from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
OUTPUT_ROOT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
)
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"

PROMOTION_WHITELIST = {
    "UTILITIES_RIPGREP",
    "SEARCH_INDEXING_RIPGREP_SEARCH",
    "UTILITIES_FD",
    "UTILITIES_JQ",
    "UTILITIES_YQ",
    "UTILITIES_ARCHIVE_MANIFEST_GENERATOR",
    "UTILITIES_SHA256_HASHING",
    "SEARCH_INDEXING_RECEIPT_PATH_INDEX",
    "SEARCH_INDEXING_REPORT_PATH_INDEX",
    "SEARCH_INDEXING_TAG_INDEX_MODEL",
    "SEARCH_INDEXING_SIMPLE_INVERTED_INDEX",
    "TOOLS_SCOPE_REVIEW_TOOL",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path_hint,
            text=True,
        ).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return path_hint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tool decision matrix and apply bounded candidate->sandbox promotions.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=OUTPUT_ROOT_DEFAULT)
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--detection-results", default="tool_detection_results.json")
    return parser.parse_args()


def determine_action(row: dict[str, Any]) -> str:
    status = str(row.get("current_status", "NO_CARD"))
    present = bool(row.get("present"))
    verdict = str(row.get("detection_verdict", "UNKNOWN"))
    approval_required = bool(row.get("owner_approval_required"))
    install_cmd = str(row.get("proposed_install_command", "")).strip()

    if verdict == "FAIL":
        return "QUARANTINE_REVIEW"
    if present:
        if status == "CANDIDATE":
            if str(row.get("tool_id", "")) in PROMOTION_WHITELIST:
                return "INSTALL_OR_VALIDATE_NOW"
            return "KEEP_CANDIDATE"
        if status in {"SANDBOX", "CANON"}:
            return "VALIDATE_IF_PRESENT"
        return "KEEP_CANDIDATE"

    if verdict == "MISSING":
        if approval_required and install_cmd:
            return "OWNER_APPROVAL_REQUIRED"
        if install_cmd:
            return "DEFER"
        return "KEEP_CANDIDATE"

    return "DEFER"


def apply_card_promotion(repo_root: Path, row: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    card_rel = str(row.get("current_capability_card", "")).strip()
    if not card_rel:
        return None
    card_path = repo_root / card_rel
    if not card_path.exists():
        return None

    payload = load_json(card_path)
    old_status = str(payload.get("status", "CANDIDATE"))
    if old_status != "CANDIDATE":
        return None

    payload["status"] = "SANDBOX"
    payload["promoted_by_receipt"] = str(row.get("validation_receipt", "")).strip() or "NOT_PROMOTED"
    payload["last_reviewed_utc"] = utc_now()
    payload["next_review_reason"] = (
        f"Promoted by {task_id} after controlled detection evidence; "
        "CANON remains forbidden in this task."
    )
    expected = payload.get("expected_receipts")
    receipt_name = Path(str(row.get("validation_receipt", ""))).name
    if isinstance(expected, list):
        if receipt_name and receipt_name not in expected:
            expected.append(receipt_name)
    else:
        payload["expected_receipts"] = [receipt_name] if receipt_name else []

    write_json(card_path, payload)
    return {
        "capability_id": str(row.get("tool_id", "")),
        "card_path": card_rel,
        "old_status": old_status,
        "new_status": "SANDBOX",
        "evidence_receipt": str(row.get("validation_receipt", "")),
    }


def rebuild_registry(repo_root: Path, task_id: str) -> dict[str, Any]:
    registry_path = repo_root / REGISTRY_REL
    registry = load_json(registry_path)
    cards = registry.get("cards", [])
    if not isinstance(cards, list):
        raise RuntimeError("Registry cards field must be a list.")

    status_counter: Counter[str] = Counter()
    rebuilt: list[dict[str, Any]] = []
    for row in cards:
        if not isinstance(row, dict):
            continue
        card_rel = str(row.get("card_path", "")).strip()
        if not card_rel:
            continue
        card_path = repo_root / card_rel
        if not card_path.exists():
            continue
        card_payload = load_json(card_path)
        cap = str(card_payload.get("capability_id", "")).strip()
        if not cap:
            continue
        status = str(card_payload.get("status", "")).strip()
        rebuilt.append(
            {
                "capability_id": cap,
                "name": str(card_payload.get("name", "")).strip(),
                "category": str(card_payload.get("category", "")).strip(),
                "status": status,
                "card_path": card_rel.replace("\\", "/"),
                "owner_organ": str(card_payload.get("owner_organ", "")).strip(),
                "source_type": str(card_payload.get("source_type", "")).strip(),
                "install_required": bool(card_payload.get("install_required", False)),
            }
        )
        status_counter[status] += 1

    registry["generated_at_utc"] = utc_now()
    registry["task_id"] = task_id
    registry["cards"] = rebuilt
    registry["card_count"] = len(rebuilt)
    registry["status_counts"] = {
        "CANDIDATE": int(status_counter.get("CANDIDATE", 0)),
        "SANDBOX": int(status_counter.get("SANDBOX", 0)),
        "CANON": int(status_counter.get("CANON", 0)),
        "QUARANTINE": int(status_counter.get("QUARANTINE", 0)),
        "REJECTED": int(status_counter.get("REJECTED", 0)),
    }
    write_json(registry_path, registry)
    return registry


def build_decision_markdown(task_id: str, rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# Tool Decision Matrix RU — {task_id}",
        "",
        "| Tool ID | Группа | Present | Текущий статус | Decision | Риск | Плюсы | Минусы |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        plus = "; ".join(str(item) for item in row.get("plus", []))
        minus = "; ".join(str(item) for item in row.get("minus", []))
        lines.append(
            "| {tool_id} | {group} | {present} | {status} | {decision} | {risk} | {plus} | {minus} |".format(
                tool_id=str(row.get("tool_id", "")),
                group=str(row.get("candidate_group", "")),
                present="yes" if bool(row.get("present")) else "no",
                status=str(row.get("current_status", "")),
                decision=str(row.get("recommended_action", "")),
                risk=str(row.get("risk_level", "")),
                plus=plus.replace("|", "/"),
                minus=minus.replace("|", "/"),
            )
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    output_root = (repo_root / args.output_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    detection_path = Path(args.detection_results)
    if not detection_path.is_absolute():
        detection_path = output_root / detection_path
    detection_payload = load_json(detection_path)
    rows = detection_payload.get("results", [])
    if not isinstance(rows, list):
        raise RuntimeError("Detection results payload has invalid `results` field.")

    decision_rows: list[dict[str, Any]] = []
    approval_queue: list[dict[str, Any]] = []
    status_changes: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()

    for raw in rows:
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        action = determine_action(row)
        row["recommended_action"] = action
        action_counts[action] += 1

        if action == "INSTALL_OR_VALIDATE_NOW" and str(row.get("current_status", "")) == "CANDIDATE" and bool(row.get("present")):
            change = apply_card_promotion(repo_root, row, args.task_id)
            if change:
                status_changes.append(change)
                row["status_recommendation"] = "PROMOTE_SANDBOX"
            else:
                row["status_recommendation"] = "KEEP_CANDIDATE"
        elif action == "OWNER_APPROVAL_REQUIRED":
            row["status_recommendation"] = "KEEP_CANDIDATE"
            approval_queue.append(
                {
                    "tool_id": str(row.get("tool_id", "")),
                    "name": str(row.get("name", "")),
                    "category": str(row.get("category", "")),
                    "risk_level": str(row.get("risk_level", "")),
                    "install_command": str(row.get("proposed_install_command", "")),
                    "install_scope": "local_user",
                    "network_use": True,
                    "expected_side_effects": ["package install into user environment"],
                    "rollback_uninstall_note": "Uninstall with package manager command for the same tool.",
                    "why_it_matters": "; ".join(str(item) for item in row.get("plus", [])),
                    "recommended_decision": "DEFER",
                    "owner_options": [
                        "APPROVE_INSTALL_THIS_TOOL",
                        "DEFER",
                        "QUARANTINE_REVIEW",
                        "REJECT",
                        "APPROVE_DETECTION_ONLY",
                    ],
                }
            )
        elif action in {"QUARANTINE_REVIEW", "DEFER"}:
            row["status_recommendation"] = action
        else:
            row["status_recommendation"] = "KEEP_STATUS"

        decision_rows.append(row)

    registry_payload = rebuild_registry(repo_root, args.task_id)

    decision_md = build_decision_markdown(args.task_id, decision_rows)
    write_text(output_root / "tool_decision_matrix_RU.md", decision_md)
    write_json(
        output_root / "owner_install_approval_queue.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "queue": approval_queue,
            "summary": {"count": len(approval_queue)},
        },
    )

    write_json(
        report_root / "tool_decision_matrix_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_tool_expansion_decision_builder_v0_1.py",
            "summary": {
                "decision_count": len(decision_rows),
                "action_counts": dict(action_counts),
                "status_changes": len(status_changes),
            },
            "verdict": "PASS_WITH_WARNINGS" if len(approval_queue) > 0 else "PASS",
            "raw_dump_status": "COMPACT_ONLY",
        },
    )
    write_json(
        report_root / "owner_approval_queue_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_tool_expansion_decision_builder_v0_1.py",
            "owner_approval_required_count": len(approval_queue),
            "queued_tools": [item["tool_id"] for item in approval_queue],
            "verdict": "PASS",
            "raw_dump_status": "COMPACT_ONLY",
        },
    )
    write_json(
        report_root / "capability_status_change_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "status_changes": status_changes,
            "summary": {
                "promoted_to_sandbox_count": len(status_changes),
                "promoted_capability_ids": [row["capability_id"] for row in status_changes],
            },
            "raw_dump_status": "COMPACT_ONLY",
        },
    )
    write_json(
        output_root / "tool_decision_matrix_v0_1.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "decisions": decision_rows,
            "summary": {
                "decision_count": len(decision_rows),
                "action_counts": dict(action_counts),
                "status_changes": len(status_changes),
                "owner_approval_required": len(approval_queue),
            },
        },
    )
    write_json(
        report_root / "registry_sync_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "registry_path": REGISTRY_REL,
            "status_counts": registry_payload.get("status_counts", {}),
            "card_count": registry_payload.get("card_count", 0),
            "verdict": "PASS",
            "raw_dump_status": "COMPACT_ONLY",
        },
    )

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "decision_count": len(decision_rows),
                "promoted_to_sandbox": len(status_changes),
                "owner_approval_required": len(approval_queue),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
