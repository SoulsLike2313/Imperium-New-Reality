from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mechanicus_validation_receipt_builder_v0_1 import (
    build_validation_receipt,
    write_receipt,
)


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
OUTPUT_ROOT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1"
)
RECEIPTS_ROOT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS/TOOL_EXPANSION_BATCH_001"


@dataclass
class CommandOutcome:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def run_command(repo_root: Path, command: str) -> CommandOutcome:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        command,
        shell=True,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    return CommandOutcome(
        command=command,
        exit_code=int(proc.returncode),
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def short_text(value: str, limit: int = 800) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def merge_stdout(outcomes: list[CommandOutcome]) -> str:
    parts = [f"$ {item.command}\n{item.stdout}".strip() for item in outcomes if item.stdout.strip()]
    return "\n\n".join(parts)


def merge_stderr(outcomes: list[CommandOutcome]) -> str:
    parts = [f"$ {item.command}\n{item.stderr}".strip() for item in outcomes if item.stderr.strip()]
    return "\n\n".join(parts)


def classify_missing(outcomes: list[CommandOutcome]) -> bool:
    markers = (
        "not recognized",
        "not found",
        "modulenotfounderror",
        "no module named",
        "cannot find",
        "no such file",
    )
    combined = "\n".join([item.stderr.lower() for item in outcomes] + [item.stdout.lower() for item in outcomes])
    return any(marker in combined for marker in markers)


def detect_verdict(outcomes: list[CommandOutcome]) -> str:
    if any(item.exit_code == 0 for item in outcomes):
        if any(item.exit_code != 0 for item in outcomes):
            return "PASS_WITH_WARNINGS"
        return "PASS"
    if classify_missing(outcomes):
        return "MISSING"
    return "FAIL"


def receipt_name(tool_id: str) -> str:
    return tool_id.lower().replace("_", "-").replace(" ", "-") + "_validation_receipt.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run controlled detection checks for Mechanicus tool expansion candidates.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=OUTPUT_ROOT_DEFAULT)
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--receipts-root", default=RECEIPTS_ROOT_DEFAULT)
    parser.add_argument("--candidate-matrix", default="tool_candidate_matrix_v0_1.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    output_root = (repo_root / args.output_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    receipts_root = (repo_root / args.receipts_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)
    receipts_root.mkdir(parents=True, exist_ok=True)

    matrix_path = Path(args.candidate_matrix)
    if not matrix_path.is_absolute():
        matrix_path = output_root / matrix_path
    matrix_payload = load_json(matrix_path)
    candidates = matrix_payload.get("candidates", [])
    if not isinstance(candidates, list):
        raise RuntimeError("Candidate matrix has invalid `candidates` field.")

    result_rows: list[dict[str, Any]] = []
    receipts_index: list[dict[str, Any]] = []
    verdict_counter: Counter[str] = Counter()

    for row in candidates:
        if not isinstance(row, dict):
            continue
        tool_id = str(row.get("tool_id", "")).strip()
        commands = row.get("detection_commands", [])
        if not tool_id or not isinstance(commands, list) or not commands:
            continue

        outcomes = [run_command(repo_root, str(command)) for command in commands]
        verdict = detect_verdict(outcomes)
        present = verdict in {"PASS", "PASS_WITH_WARNINGS"}
        verdict_counter[verdict] += 1

        row_out = dict(row)
        row_out["present"] = bool(present)
        row_out["detection_verdict"] = verdict
        row_out["command_outcomes"] = [
            {
                "command": item.command,
                "exit_code": item.exit_code,
                "stdout_excerpt": short_text(item.stdout),
                "stderr_excerpt": short_text(item.stderr),
            }
            for item in outcomes
        ]

        rec_name = receipt_name(tool_id)
        rec_path = receipts_root / rec_name
        rec_rel = rec_path.relative_to(repo_root).as_posix()
        row_out["validation_receipt"] = rec_rel

        recommendation = "KEEP_CANDIDATE"
        if present and row_out.get("current_status") == "CANDIDATE":
            recommendation = "PROMOTE_SANDBOX"
        elif present and row_out.get("current_status") in {"SANDBOX", "CANON"}:
            recommendation = "KEEP_STATUS"
        elif verdict == "MISSING":
            recommendation = "KEEP_CANDIDATE"
        elif verdict == "FAIL":
            recommendation = "QUARANTINE_REVIEW"
        row_out["status_recommendation"] = recommendation

        receipt_payload = build_validation_receipt(
            task_id=args.task_id,
            capability_id=tool_id,
            validator="mechanicus_tool_detection_runner_v0_1.py",
            check_name=f"tool_detection:{tool_id}",
            command_or_check=" || ".join(commands),
            exit_code=max(item.exit_code for item in outcomes),
            stdout_text=merge_stdout(outcomes),
            stderr_text=merge_stderr(outcomes),
            side_effects=["read-only detection commands", "validation receipt created"],
            network_used=False,
            files_created_or_modified=[rec_rel],
            validation_verdict=verdict,
            promotion_recommendation=recommendation,
            evidence_paths=[rec_rel],
            warnings=(
                ["partial_detection_fallback"]
                if verdict == "PASS_WITH_WARNINGS"
                else ["tool_missing_or_not_in_path"]
                if verdict == "MISSING"
                else []
            ),
        )
        write_receipt(rec_path, receipt_payload)

        receipts_index.append(
            {
                "tool_id": tool_id,
                "receipt_path": rec_rel,
                "detection_verdict": verdict,
            }
        )
        result_rows.append(row_out)

    detection_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "runner": "mechanicus_tool_detection_runner_v0_1.py",
        "results": result_rows,
        "summary": {
            "candidate_count": len(result_rows),
            "present_count": sum(1 for row in result_rows if bool(row.get("present"))),
            "missing_count": sum(1 for row in result_rows if row.get("detection_verdict") == "MISSING"),
            "fail_count": sum(1 for row in result_rows if row.get("detection_verdict") == "FAIL"),
            "verdict_counts": dict(verdict_counter),
        },
    }
    write_json(output_root / "tool_detection_results.json", detection_payload)
    write_json(
        report_root / "tool_detection_report.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_tool_detection_runner_v0_1.py",
            "summary": detection_payload["summary"],
            "warnings": (
                ["some_candidates_missing"]
                if detection_payload["summary"]["missing_count"] > 0
                else []
            ),
            "verdict": (
                "PASS_WITH_WARNINGS"
                if detection_payload["summary"]["fail_count"] == 0
                and detection_payload["summary"]["missing_count"] > 0
                else "PASS"
                if detection_payload["summary"]["fail_count"] == 0
                else "FAIL"
            ),
            "raw_dump_status": "COMPACT_ONLY",
        },
    )
    write_json(
        report_root / "tool_validation_receipts_index.json",
        {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "receipts_root": receipts_root.relative_to(repo_root).as_posix(),
            "receipts": receipts_index,
        },
    )

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "candidate_count": len(result_rows),
                "present_count": detection_payload["summary"]["present_count"],
                "missing_count": detection_payload["summary"]["missing_count"],
                "fail_count": detection_payload["summary"]["fail_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if detection_payload["summary"]["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
