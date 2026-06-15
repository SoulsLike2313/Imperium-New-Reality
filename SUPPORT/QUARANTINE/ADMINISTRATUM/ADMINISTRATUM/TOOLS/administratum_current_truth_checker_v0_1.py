from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-ADMINISTRATUM-REGISTRATION-CARDS-CURRENT-TRUTH-PC-V0_1"
EXPECTED_OFFICIO_HEAD = "892ae8a6f5452c55211da4748bed3b1d9d3f9326"
EXPECTED_NEXT_TASK = "TASK-NEWGEN-INQUISITION-PURITY-QUARANTINE-BODY-PC-V0_1"

HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
REPORT_ROOT = ADMIN_ROOT / "REPORTS" / TASK_ID
DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "current_truth_checker_receipt.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _enforce_output_path(path: Path, allow_external: bool) -> None:
    if allow_external:
        return
    resolved_report = REPORT_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_report not in resolved_path.parents and resolved_path != resolved_report:
        raise SystemExit(f"Output path must stay under {resolved_report} unless --allow-external-output is used.")


def _record(results: list[dict[str, Any]], check_id: str, status: str, detail: str) -> None:
    results.append({"check_id": check_id, "status": status, "detail": detail})


def run_checks(expected_head: str, expected_next_task: str) -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    paths = {
        "current_head": ADMIN_ROOT / "CURRENT_TRUTH" / "current_head_card_v0_1.json",
        "accepted_points": ADMIN_ROOT / "CURRENT_TRUTH" / "accepted_points_index_v0_1.json",
        "active_organs": ADMIN_ROOT / "CURRENT_TRUTH" / "active_organs_index_v0_1.json",
        "pending_tasks": ADMIN_ROOT / "CURRENT_TRUTH" / "pending_next_tasks_index_v0_1.json",
        "legacy_warn": ADMIN_ROOT / "CURRENT_TRUTH" / "legacy_warn_index_v0_1.json",
        "mechanicus_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "mechanicus_organ_card_v0_1.json",
        "officio_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "officio_agentis_organ_card_v0_1.json",
        "tui_source": ADMIN_ROOT / "TUI" / "administratum_tui_v0_1.py",
    }

    loaded: dict[str, Any] = {}
    for key, path in paths.items():
        if key == "tui_source":
            if path.exists():
                loaded[key] = path.read_text(encoding="utf-8")
                _record(results, f"file.{key}", "PASS", f"loaded: {path.as_posix()}")
            else:
                _record(results, f"file.{key}", "FAIL", f"missing: {path.as_posix()}")
            continue

        if not path.exists():
            _record(results, f"file.{key}", "FAIL", f"missing: {path.as_posix()}")
            continue
        try:
            loaded[key] = _read_json(path)
            _record(results, f"file.{key}", "PASS", f"loaded: {path.as_posix()}")
        except Exception as exc:
            _record(results, f"file.{key}", "FAIL", f"invalid json: {exc}")

    current_head = (loaded.get("current_head") or {}).get("current_head")
    if current_head == expected_head:
        _record(results, "truth.current_head_match", "PASS", f"current_head == {expected_head}")
    else:
        _record(results, "truth.current_head_match", "FAIL", f"expected {expected_head}, got {current_head}")

    points = (loaded.get("accepted_points") or {}).get("points", [])
    if isinstance(points, list):
        officio_found = any(
            isinstance(p, dict)
            and p.get("organ_id") == "OFFICIO_AGENTIS"
            and p.get("accepted_head") == EXPECTED_OFFICIO_HEAD
            for p in points
        )
        if officio_found:
            _record(results, "truth.officio_point_present", "PASS", EXPECTED_OFFICIO_HEAD)
        else:
            _record(results, "truth.officio_point_present", "FAIL", "required Officio accepted point missing")
    else:
        _record(results, "truth.points_shape", "FAIL", "accepted_points.points must be array")

    organ_ids: set[str] = set()
    for key in ("mechanicus_card", "officio_card"):
        card = loaded.get(key)
        if isinstance(card, dict):
            value = card.get("organ_id")
            if isinstance(value, str):
                organ_ids.add(value)
    if {"MECHANICUS", "OFFICIO_AGENTIS"}.issubset(organ_ids):
        _record(results, "truth.organ_cards_present", "PASS", "MECHANICUS + OFFICIO_AGENTIS cards present")
    else:
        _record(results, "truth.organ_cards_present", "FAIL", f"found={sorted(organ_ids)}")

    pending = (loaded.get("pending_tasks") or {}).get("pending_next_tasks", [])
    if isinstance(pending, list) and pending:
        first = pending[0] if isinstance(pending[0], dict) else {}
        task_id = first.get("task_id")
        if task_id == expected_next_task:
            _record(results, "truth.next_task_expected", "PASS", expected_next_task)
        else:
            _record(results, "truth.next_task_expected", "FAIL", f"expected {expected_next_task}, got {task_id}")
    else:
        _record(results, "truth.next_task_expected", "FAIL", "pending_next_tasks is empty")

    tui_source = loaded.get("tui_source", "")
    if isinstance(tui_source, str):
        has_truth_ref = "CURRENT_TRUTH" in tui_source and "REGISTRATION_CARDS" in tui_source
        if has_truth_ref:
            _record(results, "truth.tui_reads_real_paths", "PASS", "TUI references card/current-truth paths")
        else:
            _record(results, "truth.tui_reads_real_paths", "FAIL", "TUI path references missing")
    else:
        _record(results, "truth.tui_reads_real_paths", "FAIL", "TUI source not loaded")

    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "task_id": TASK_ID,
        "checker": "administratum_current_truth_checker_v0_1.py",
        "status": "PASS" if fail_count == 0 else "FAIL",
        "fail_count": fail_count,
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Administratum current truth indexes and links.")
    parser.add_argument("--expected-head", default=EXPECTED_OFFICIO_HEAD)
    parser.add_argument("--expected-next-task", default=EXPECTED_NEXT_TASK)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--allow-external-output", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    _enforce_output_path(output_path, allow_external=args.allow_external_output)
    report = run_checks(expected_head=str(args.expected_head), expected_next_task=str(args.expected_next_task))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
