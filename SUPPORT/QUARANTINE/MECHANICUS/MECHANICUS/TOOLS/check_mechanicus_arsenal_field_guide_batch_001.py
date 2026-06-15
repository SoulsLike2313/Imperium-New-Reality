from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-FIELD-GUIDE-BATCH-001-PC-V0_1"
RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_repo_root(start: Path) -> Path:
    probe = start.resolve()
    cwd = probe if probe.is_dir() else probe.parent
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, text=True).strip()
        if root:
            return Path(root)
    except Exception:
        pass
    for candidate in [probe, *probe.parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("Cannot locate repo root containing AGENTS.md")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def discover_card_ids(cards_root: Path) -> tuple[set[str], Counter]:
    ids: set[str] = set()
    category_counter: Counter = Counter()
    for path in sorted(cards_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "capability_card.json" or (path.name.startswith("CAP-") and path.suffix == ".json"):
            payload = read_json(path)
            cap_id = str(payload.get("capability_id", "")).strip()
            category = str(payload.get("category", "")).strip()
            if cap_id:
                ids.add(cap_id)
            if category:
                category_counter[category] += 1
    return ids, category_counter


def main() -> None:
    repo_root = find_repo_root(Path(__file__).resolve())
    output_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/FIELD_GUIDES/BATCH_001"
    report_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS" / TASK_ID
    cards_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES"

    required_output_files = [
        output_root / "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_RU.md",
        output_root / "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_EN.md",
        output_root / "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json",
        output_root / "SERVITOR_CAPABILITY_SCOPE_EXAMPLES.md",
        output_root / "VALIDATION_PRIORITY_QUEUE_RU.md",
        output_root / "OWNER_DECISION_POINTS_RU.md",
        output_root / "FIELD_GUIDE_COVERAGE_REPORT.json",
    ]
    required_report_files = [
        report_root / "GATE_ACK.md",
        report_root / "FINAL_REPORT.md",
        report_root / "field_guide_manifest.json",
        report_root / "field_guide_coverage_report.json",
        report_root / "servitor_scope_examples_report.json",
        report_root / "validation_priority_queue_report.json",
        report_root / "owner_decision_points_report.json",
        report_root / "llm_cloud_reserved_check_report.json",
        report_root / "closure_receipt.json",
    ]

    errors: list[str] = []
    warnings: list[str] = []

    missing_files = [str(path.relative_to(repo_root).as_posix()) for path in required_output_files + required_report_files if not path.exists()]
    if missing_files:
        errors.append(f"missing_required_files={len(missing_files)}")

    usage_map_path = output_root / "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json"
    usage_payload = read_json(usage_map_path)
    entries = usage_payload.get("entries", [])
    if not isinstance(entries, list):
        raise RuntimeError("Usage map entries must be a list")

    card_ids, category_card_counts = discover_card_ids(cards_root)
    usage_ids = [str(item.get("capability_id", "")).strip() for item in entries if isinstance(item, dict)]
    usage_id_set = set(usage_ids)

    duplicate_ids = sorted([cap_id for cap_id, count in Counter(usage_ids).items() if count > 1 and cap_id])
    missing_capability_ids = sorted(card_ids - usage_id_set)
    extra_capability_ids = sorted(usage_id_set - card_ids)

    if duplicate_ids:
        errors.append(f"duplicate_usage_map_ids={len(duplicate_ids)}")
    if missing_capability_ids:
        errors.append(f"missing_usage_map_ids={len(missing_capability_ids)}")
    if extra_capability_ids:
        errors.append(f"extra_usage_map_ids={len(extra_capability_ids)}")

    # Category guide coverage check.
    category_guides_root = output_root / "CATEGORY_GUIDES_RU"
    category_usage_counts = Counter(str(item.get("category", "")).strip() for item in entries if isinstance(item, dict))
    missing_category_guides = []
    for category in sorted(category_card_counts):
        guide_path = category_guides_root / f"{category}_FIELD_GUIDE_RU.md"
        if not guide_path.exists():
            missing_category_guides.append(category)
    if missing_category_guides:
        errors.append(f"missing_category_guides={len(missing_category_guides)}")

    # Reserved categories must not be activated.
    reserved_violations = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category", "")).strip()
        level = str(item.get("agent_use_level", "")).strip()
        status = str(item.get("status", "")).strip()
        if category in RESERVED_CATEGORIES and level not in {"OWNER_DECISION_REQUIRED", "NOT_ALLOWED"}:
            reserved_violations.append(
                {
                    "capability_id": str(item.get("capability_id", "")).strip(),
                    "category": category,
                    "status": status,
                    "agent_use_level": level,
                }
            )
    if reserved_violations:
        errors.append(f"reserved_activation_violations={len(reserved_violations)}")

    # No CANON claim without evidence or receipts.
    canon_without_evidence = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        if str(item.get("status", "")).strip() != "CANON":
            continue
        required_receipts = item.get("required_receipts", [])
        if not isinstance(required_receipts, list) or len([x for x in required_receipts if str(x).strip()]) == 0:
            canon_without_evidence.append(str(item.get("capability_id", "")).strip())
    if canon_without_evidence:
        errors.append(f"canon_without_required_receipts={len(canon_without_evidence)}")

    # Soft warning when checker is run on dirty tree (expected in local uncommitted execution).
    if (report_root / "closure_receipt.json").exists():
        closure = read_json(report_root / "closure_receipt.json")
        if closure.get("commit") == "NOT_PERFORMED":
            warnings.append("commit_not_performed_in_this_run")

    verdict = "PASS" if not errors else "FAIL"
    report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "notes": errors if errors else ["all mandatory checks passed"],
        "warnings": warnings,
        "summary": {
            "cards_discovered": len(card_ids),
            "usage_map_entries": len(usage_ids),
            "unique_usage_map_entries": len(usage_id_set),
            "category_count": len(category_card_counts),
        },
        "missing_files": missing_files,
        "missing_capability_ids": missing_capability_ids,
        "extra_capability_ids": extra_capability_ids,
        "duplicate_capability_ids": duplicate_ids,
        "missing_category_guides": missing_category_guides,
        "reserved_activation_violations": reserved_violations,
        "canon_without_required_receipts": canon_without_evidence,
        "category_card_counts": dict(category_card_counts),
        "category_usage_counts": dict(category_usage_counts),
    }

    write_json(report_root / "agent_usage_map_check_report.json", report)
    print(json.dumps({"task_id": TASK_ID, "verdict": verdict, "errors": len(errors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
