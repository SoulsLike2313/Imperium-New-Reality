from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1"
REPO_ROOT = Path(__file__).resolve().parents[3]
ARSENAL_ROOT = REPO_ROOT / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "ARSENAL"
REPORT_ROOT = (
    REPO_ROOT
    / "IMPERIUM_NEW_GENERATION"
    / "MECHANICUS"
    / "REPORTS"
    / TASK_ID
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_cards() -> list[tuple[dict[str, Any], Path]]:
    cards: list[tuple[dict[str, Any], Path]] = []
    for path in sorted((ARSENAL_ROOT / "CATEGORIES").rglob("*.json")):
        try:
            payload = load_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if {"capability_id", "name", "category", "status"}.issubset(payload.keys()):
            cards.append((payload, path))
    return cards


def canon_evidence_ok(card: dict[str, Any]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    evidence_paths = card.get("canon_evidence_paths", [])
    if isinstance(evidence_paths, list) and evidence_paths:
        for rel in evidence_paths:
            if not isinstance(rel, str):
                missing.append("<non-string-evidence-path>")
                continue
            if not (REPO_ROOT / rel).exists():
                missing.append(rel)
        return (len(missing) == 0, missing)

    promoted_by = str(card.get("promoted_by_receipt", ""))
    if promoted_by.endswith(".json"):
        candidate_paths = [
            REPO_ROOT / promoted_by,
            ARSENAL_ROOT / "RECEIPTS" / promoted_by,
        ]
        if any(path.exists() for path in candidate_paths):
            return (True, [])
        return (False, [promoted_by])
    return (False, ["missing_canon_evidence_paths"])


def main() -> int:
    violations: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    schema_path = ARSENAL_ROOT / "SCHEMAS" / "capability_card_schema_v0_1.json"
    schema = load_json(schema_path) if schema_path.exists() else {}
    required_fields = list(schema.get("required", []))
    allowed_categories = set(schema.get("properties", {}).get("category", {}).get("enum", []))
    allowed_statuses = set(schema.get("properties", {}).get("status", {}).get("enum", []))

    category_targets_path = REPORT_ROOT / "DOSSIER_SOURCE" / "CATEGORY_TARGETS.json"
    category_targets = load_json(category_targets_path) if category_targets_path.exists() else {}
    minimum_total_cards = int(category_targets.get("minimum_total_cards", 80))
    category_minimums: dict[str, int] = {
        cat: int(cfg.get("minimum_cards", 0))
        for cat, cfg in dict(category_targets.get("categories", {})).items()
    }

    cards = collect_cards()
    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    canonical_cards = 0
    fake_canon_count = 0
    llm_cloud_canon_count = 0
    bad_card_paths: list[str] = []

    for card, card_path in cards:
        cap = str(card.get("capability_id", "UNKNOWN"))
        status = str(card.get("status", "UNKNOWN"))
        category = str(card.get("category", "UNKNOWN"))

        status_counts[status] += 1
        category_counts[category] += 1

        missing_fields = [field for field in required_fields if field not in card]
        if missing_fields:
            violations.append(f"missing_fields:{cap}:{','.join(missing_fields)}")
            bad_card_paths.append(card_path.relative_to(REPO_ROOT).as_posix())

        if allowed_categories and category not in allowed_categories:
            violations.append(f"unknown_category:{cap}:{category}")
            bad_card_paths.append(card_path.relative_to(REPO_ROOT).as_posix())

        if allowed_statuses and status not in allowed_statuses:
            violations.append(f"unknown_status:{cap}:{status}")
            bad_card_paths.append(card_path.relative_to(REPO_ROOT).as_posix())

        if status == "CANON":
            canonical_cards += 1
            ok, missing = canon_evidence_ok(card)
            if not ok:
                fake_canon_count += 1
                violations.append(f"fake_canon:{cap}:{';'.join(missing)}")
            if bool(card.get("install_required", False)):
                violations.append(f"canon_requires_install:{cap}")

        if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"} and status == "CANON":
            llm_cloud_canon_count += 1
            violations.append(f"llm_cloud_canon_forbidden:{cap}")

    if len(cards) < minimum_total_cards:
        violations.append(f"total_cards_below_minimum:{len(cards)}<{minimum_total_cards}")
    else:
        info.append(f"total_cards_ok:{len(cards)}")

    for category, minimum in sorted(category_minimums.items()):
        count = int(category_counts.get(category, 0))
        if count < minimum:
            violations.append(f"category_below_minimum:{category}:{count}<{minimum}")

    # Verify folder discipline for capability-folder cards.
    folder_card_paths = list((ARSENAL_ROOT / "CATEGORIES").glob("*/*/capability_card.json"))
    if not folder_card_paths:
        violations.append("no_capability_folders_detected")
    else:
        required_files = ["README.md", "validation_plan.md", "usage_contract.md", "risks.md"]
        for card_path in folder_card_paths:
            cap_dir = card_path.parent
            for filename in required_files:
                if not (cap_dir / filename).is_file():
                    violations.append(f"missing_capability_doc:{cap_dir.relative_to(REPO_ROOT).as_posix()}/{filename}")

    required_reports = [
        "FINAL_REPORT.md",
        "mass_intake_manifest.json",
        "category_coverage_report.json",
        "fake_canon_detection_report.json",
        "next_validation_queue.json",
        "servitor_capability_scope_seed_report.json",
        "owner_questions_report.json",
        "llm_reserved_policy_report.json",
        "closure_receipt.json",
    ]
    missing_reports = [name for name in required_reports if not (REPORT_ROOT / name).is_file()]
    if missing_reports:
        warnings.append(f"missing_reports_pre_close:{','.join(missing_reports)}")

    batch_registry = ARSENAL_ROOT / "REGISTRY" / "mass_intake_candidate_batches_v0_1.json"
    if not batch_registry.is_file():
        violations.append("missing_batch_registry")

    # Runtime junk scan.
    junk_dirs = {"__pycache__", ".cache", "node_modules"}
    junk_exts = {".log", ".pid", ".tmp", ".pyc", ".pyo"}
    junk_hits: list[str] = []
    for root in [ARSENAL_ROOT, REPORT_ROOT]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if path.is_dir() and path.name in junk_dirs:
                junk_hits.append(rel + "/")
            if path.is_file() and path.suffix.lower() in junk_exts:
                junk_hits.append(rel)
    if junk_hits:
        violations.append(f"runtime_junk_found:{len(junk_hits)}")
        warnings.extend([f"junk:{entry}" for entry in junk_hits[:50]])

    truth_start_path = REPORT_ROOT / "truth_check_start.json"
    if truth_start_path.exists():
        try:
            truth_start = load_json(truth_start_path)
            dirty_entries = list(truth_start.get("preexisting_dirty_paths", []))
            if dirty_entries:
                warnings.append(f"preexisting_dirty_start_detected:{len(dirty_entries)}")
        except Exception as exc:
            warnings.append(f"truth_start_unreadable:{exc}")

    verdict = "PASS"
    if violations:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    report_payload = {
        "task_id": TASK_ID,
        "checker": "check_mechanicus_arsenal_mass_intake_v0_1.py",
        "checked_at_utc": now_utc(),
        "verdict": verdict,
        "summary": {
            "total_cards": len(cards),
            "status_counts": {
                "CANDIDATE": int(status_counts.get("CANDIDATE", 0)),
                "SANDBOX": int(status_counts.get("SANDBOX", 0)),
                "CANON": int(status_counts.get("CANON", 0)),
                "QUARANTINE": int(status_counts.get("QUARANTINE", 0)),
                "REJECTED": int(status_counts.get("REJECTED", 0)),
            },
            "canonical_cards": canonical_cards,
            "fake_canon_count": fake_canon_count,
            "llm_cloud_canon_count": llm_cloud_canon_count,
            "category_count": len(category_counts),
            "violations_count": len(violations),
            "warnings_count": len(warnings),
        },
        "coverage": {
            "minimum_total_cards": minimum_total_cards,
            "category_counts": dict(sorted(category_counts.items())),
            "category_minimums": dict(sorted(category_minimums.items())),
        },
        "violations": violations,
        "warnings": warnings,
        "info": info,
        "bad_card_paths_sample": bad_card_paths[:50],
    }

    write_path = REPORT_ROOT / "arsenal_mass_intake_check_report.json"
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
