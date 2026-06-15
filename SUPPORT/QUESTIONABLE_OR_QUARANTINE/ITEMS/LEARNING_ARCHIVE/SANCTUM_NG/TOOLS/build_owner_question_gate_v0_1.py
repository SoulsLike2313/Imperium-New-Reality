#!/usr/bin/env python3
"""Build foundation-only Owner Question Gate state for Sanctum NG."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "1e99ed0b20ede645b6201011e446ab541d9ffb0c"
MODE = "FOUNDATION_READ_ONLY_OWNER_QUESTION_GATE"
NEXT_REQUIRED_STEP = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM2-OR-VM3-V0_1"

REGISTRY_REL = "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_REGISTRY_V0_1.json"
STATUS_RULES_REL = "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_STATUS_RULES_V0_1.json"
PRIORITY_RULES_REL = "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_PRIORITY_RULES_V0_1.json"
SAMPLE_SET_REL = "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_SAMPLE_SET_V0_1.json"
QUESTION_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question.schema.json"
EVENT_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question_event.schema.json"
STATE_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question_gate_state.schema.json"
OUTPUT_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/owner_question_gate_state.generated.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def normalize_question(item: dict[str, Any], task_id: str) -> dict[str, Any]:
    out = dict(item)
    out["question_id"] = str(item.get("question_id", "")).strip()
    out["task_id"] = str(item.get("task_id", task_id)).strip() or task_id
    out["source"] = str(item.get("source", "SERVITOR")).strip()
    out["source_ref"] = str(item.get("source_ref", "FOUNDATION_SAMPLE")).strip() or "FOUNDATION_SAMPLE"
    out["question_text_ru"] = str(item.get("question_text_ru", "")).strip()
    out["question_text_en_optional"] = str(item.get("question_text_en_optional", "")).strip()
    out["why_needed_ru"] = str(item.get("why_needed_ru", "")).strip()
    out["decision_type"] = str(item.get("decision_type", "CLARIFICATION")).strip()
    out["blocking_level"] = str(item.get("blocking_level", "WARN_ONLY")).strip()
    out["status"] = str(item.get("status", "FOUNDATION_SAMPLE")).strip()
    out["owner_answer_required"] = bool(item.get("owner_answer_required", True))
    allowed_answers = item.get("allowed_answers", [])
    evidence_refs = item.get("evidence_refs", [])
    out["allowed_answers"] = [str(v) for v in allowed_answers if str(v).strip()] if isinstance(allowed_answers, list) else []
    out["evidence_refs"] = [str(v) for v in evidence_refs if str(v).strip()] if isinstance(evidence_refs, list) else []
    out["created_at_utc"] = str(item.get("created_at_utc", "")).strip() or utc_now()
    out["updated_at_utc"] = str(item.get("updated_at_utc", "")).strip() or out["created_at_utc"]
    return out


def derive_gate_status(questions: list[dict[str, Any]]) -> str:
    for question in questions:
        if (
            question.get("status") == "OPEN"
            and question.get("blocking_level") == "BLOCKING"
            and bool(question.get("owner_answer_required"))
        ):
            return "BLOCKING_OWNER_DECISION_REQUIRED"

    for question in questions:
        if question.get("status") == "STALE":
            return "WARN_OWNER_REVIEW_RECOMMENDED"
        if question.get("status") == "OPEN" and question.get("blocking_level") == "WARN_ONLY":
            return "WARN_OWNER_REVIEW_RECOMMENDED"

    return "FOUNDATION_SAMPLE_ONLY"


def build_summary(questions: list[dict[str, Any]]) -> dict[str, Any]:
    status_counter = Counter(str(q.get("status", "UNKNOWN")) for q in questions)
    blocking_counter = Counter(str(q.get("blocking_level", "WARN_ONLY")) for q in questions)
    owner_required_count = sum(1 for q in questions if bool(q.get("owner_answer_required")))

    return {
        "total_questions": len(questions),
        "open_count": status_counter.get("OPEN", 0),
        "blocking_count": blocking_counter.get("BLOCKING", 0),
        "deferred_count": status_counter.get("DEFERRED", 0),
        "warn_only_count": blocking_counter.get("WARN_ONLY", 0),
        "answered_count": status_counter.get("ANSWERED", 0),
        "stale_count": status_counter.get("STALE", 0),
        "foundation_sample_count": status_counter.get("FOUNDATION_SAMPLE", 0),
        "owner_answer_required_count": owner_required_count,
        "derived_gate_status": derive_gate_status(questions),
    }


def build_events(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for idx, question in enumerate(questions, start=1):
        event = {
            "event_id": f"OWNER_Q_EVT-{idx:03d}",
            "timestamp_utc": str(question.get("created_at_utc", utc_now())),
            "event_type": "QUESTION_REGISTERED",
            "question_id": str(question.get("question_id", "")),
            "status_after": str(question.get("status", "FOUNDATION_SAMPLE")),
            "blocking_level": str(question.get("blocking_level", "WARN_ONLY")),
            "owner_answer_required": bool(question.get("owner_answer_required", True)),
            "source": str(question.get("source", "SERVITOR")),
            "summary": f"Question registered: {str(question.get('question_id', 'UNKNOWN'))}",
            "evidence_refs": list(question.get("evidence_refs", [])),
            "notes": [
                "FOUNDATION_ONLY",
                "NOT_LIVE_OWNER_CHANNEL",
            ],
        }
        events.append(event)
    return events


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = (
        default_repo_root
        / "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-V0_1"
    )
    parser = argparse.ArgumentParser(description="Build Owner Question Gate foundation state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_repo_root / OUTPUT_REL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    required_starting_head = str(args.required_starting_head)
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    warnings: list[str] = []

    registry = load_json(repo_root / REGISTRY_REL) or {}
    status_rules = load_json(repo_root / STATUS_RULES_REL) or {}
    priority_rules = load_json(repo_root / PRIORITY_RULES_REL) or {}
    sample_set = load_json(repo_root / SAMPLE_SET_REL) or {}

    raw_questions = sample_set.get("questions", [])
    questions: list[dict[str, Any]] = []
    if isinstance(raw_questions, list):
        for raw in raw_questions:
            if isinstance(raw, dict):
                questions.append(normalize_question(raw, task_id))

    if not questions:
        warnings.append("NO_SAMPLE_QUESTIONS_FOUND")

    git_head = run_git(repo_root, "rev-parse", "HEAD")
    git_branch = run_git(repo_root, "branch", "--show-current")
    git_status = run_git(repo_root, "status", "--short")
    if git_head != required_starting_head:
        warnings.append("HEAD_MISMATCH_FROM_REQUIRED_START")

    summary = build_summary(questions)
    events = build_events(questions)

    status_semantics = status_rules.get("status_semantics", {})
    derived_status_rules = status_rules.get("derived_status_rules", {})
    priority_rule_map = priority_rules.get("blocking_level_rules", {})

    state: dict[str, Any] = {
        "schema_id": "OWNER_QUESTION_GATE_STATE_V0_1",
        "task_id": task_id,
        "mode": MODE,
        "generated_at_utc": utc_now(),
        "git": {
            "head": git_head,
            "branch": git_branch,
            "worktree_dirty": bool(git_status),
            "required_starting_head": required_starting_head,
            "head_matches_required_start": git_head == required_starting_head,
        },
        "truth_flags": {
            "read_only": True,
            "foundation_only": True,
            "live_owner_channel": False,
            "owner_answer_write_path": False,
            "production_ready": False,
        },
        "registry": {
            "registry_path": REGISTRY_REL,
            "status_rules_path": STATUS_RULES_REL,
            "priority_rules_path": PRIORITY_RULES_REL,
            "sample_set_path": SAMPLE_SET_REL,
            "question_schema_path": QUESTION_SCHEMA_REL,
            "event_schema_path": EVENT_SCHEMA_REL,
            "state_schema_path": STATE_SCHEMA_REL,
        },
        "summary": summary,
        "questions": questions,
        "events": events,
        "status_semantics": status_semantics,
        "derived_status_rules": derived_status_rules,
        "priority_rules": priority_rule_map,
        "warnings": warnings,
        "limitations": [
            "Foundation-only records; no live owner answer write path.",
            "Question feed is file-backed and read-only in Sanctum NG.",
            "No autonomous owner decision inference in V0.1.",
        ],
        "forbidden_claims": registry.get(
            "forbidden_claims",
            [
                "LIVE_OWNER_ANSWER_CHANNEL_ACTIVE",
                "AUTONOMOUS_OWNER_DECISION_INFERENCE",
                "PRODUCTION_READY_OWNER_ESCALATION",
            ],
        ),
        "boundary_note": "FOUNDATION_ONLY / NOT LIVE OWNER CHANNEL",
        "next_required_step": NEXT_REQUIRED_STEP,
    }

    write_json(output_path, state)

    build_report = {
        "schema_id": "OWNER_QUESTION_GATE_BUILD_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "status": "PASS" if not warnings else "WARN",
        "question_count": len(questions),
        "summary": summary,
        "output_state_path": output_path.relative_to(repo_root).as_posix(),
        "warnings": warnings,
        "no_live_claim": "Owner Question Gate is read-only foundation state.",
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    write_json(report_dir / "OWNER_QUESTION_GATE_BUILD_REPORT.json", build_report)

    print(f"owner_question_gate_state_written={output_path}")
    print(f"owner_question_count={len(questions)}")
    print(f"derived_gate_status={summary.get('derived_gate_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
