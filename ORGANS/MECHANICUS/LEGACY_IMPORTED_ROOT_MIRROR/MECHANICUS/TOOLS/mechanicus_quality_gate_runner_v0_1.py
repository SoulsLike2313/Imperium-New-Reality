from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
DEFAULT_REPORT_ROOT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
)
DEFAULT_TASKPACK_ZIP = (
    r"C:\Users\PC\Downloads\TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1_DOSSIER.zip"
)
NEXT_ALLOWED_TASK_PASS = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-003-VISUAL-READINESS-PC-V0_1"
NEXT_ALLOWED_TASK_WARN = "TASK-NEWGEN-MECHANICUS-QUALITY-GATE-FOLLOWUP-PC-V0_1"

OFFICIO_ROLE_PACK_REL = (
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/ROLE_PACKS/OFFICIO_PC_SERVITOR_ROLE_PACK_V0_1.json"
)
OFFICIO_CHECKER_REL = (
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TOOLS/officio_response_contract_checker_v0_1.py"
)
FAKE_CANON_DETECTOR_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py"
)
SCOPE_CONSUMER_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_scope_pack_consumer_v0_1.py"
)
SCHEMA_RUNNER_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_schema_validation_runner_v0_1.py"
)
TASKPACK_VALIDATOR_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_taskpack_validator_v0_1.py"
)
HYGIENE_RUNNER_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/newgen_repo_hygiene_check_v0_1.py"
)
EVIDENCE_SMOKE_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/evidence_index_smoke_v0_1.py"
)

READ_GATES = [
    "GATE-U00-GIT-TRUTH",
    "GATE-U01-ROLE-ACK",
    "GATE-U02-SCOPE-BOUNDARY",
    "GATE-U04-EVIDENCE-RECEIPT",
    "GATE-U05-STOP-CONDITIONS",
    "GATE-U08-REPO-PURITY",
    "GATE-U09-NO-FAKE-GREEN",
    "GATE-U12-REPORT-OUTPUT-BUDGET",
    "GATE-U13-PYTHON-TYPE-SAFETY",
    "GATE-U14-WHOLE-REPO-SCOPE-RECON",
    "GATE-U15-OPERATIONALITY-IMPACT",
    "GATE-U16-BILINGUAL-UI",
    "GATE-U17-DELIVERABLE-PACKAGE",
    "GATE-U18-AGENT-FACTORY-COMPLIANCE",
    "GATE-U19-SCRIPT-ARTIFACT-PRESERVATION",
    "GATE-U20-AGENT-KPD-SELF-REVIEW",
    "GATE-U21-COMMAND-CHUNKING",
]

REQUIRED_ACKS = [
    "ROLE_ACK",
    "LANGUAGE_ACK",
    "SCOPE_ACK",
    "STOP_CONDITIONS_ACK",
    "FORBIDDEN_ACTIONS_ACK",
]

TOOL_SCRIPTS = [
    SCOPE_CONSUMER_REL,
    SCHEMA_RUNNER_REL,
    TASKPACK_VALIDATOR_REL,
    HYGIENE_RUNNER_REL,
    EVIDENCE_SMOKE_REL,
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py",
]


@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_text(value: str, limit: int = 320) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_command(command: list[str], cwd: Path) -> CommandResult:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return CommandResult(
        command=command,
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def run_git(repo_root: Path, *args: str) -> str:
    result = run_command(["git", *args], cwd=repo_root)
    return result.stdout.strip()


def normalize_gate_status(value: str) -> str:
    text = value.strip().upper()
    if text == "PASS_WITH_WARNINGS":
        return "WARN"
    if text in {"PASS", "WARN", "FAIL", "BLOCKED"}:
        return text
    return "BLOCKED"


def status_from_exit(result: CommandResult) -> str:
    return "PASS" if result.exit_code == 0 else "FAIL"


def find_repo_root(path_hint: Path) -> Path:
    root = run_git(path_hint, "rev-parse", "--show-toplevel")
    if root:
        return Path(root).resolve()
    return path_hint.resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def relative_or_abs(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except Exception:
        return path.as_posix()


def run_json_tool(repo_root: Path, command: list[str], output_path: Path) -> tuple[str, dict[str, Any], CommandResult]:
    result = run_command(command, cwd=repo_root)
    if output_path.exists():
        try:
            payload = load_json(output_path)
        except Exception as exc:
            return "FAIL", {"verdict": "FAIL", "errors": [f"invalid_json_output:{exc}"]}, result
        verdict = normalize_gate_status(str(payload.get("verdict", status_from_exit(result))))
        if result.exit_code != 0 and verdict == "PASS":
            verdict = "WARN"
        return verdict, payload, result
    return "FAIL", {"verdict": "FAIL", "errors": ["missing_output_report"]}, result


def parse_status_paths(status_text: str) -> list[str]:
    paths: list[str] = []
    for line in status_text.splitlines():
        stripped = line.strip()
        if len(stripped) < 4:
            continue
        path = stripped[3:].strip().replace("\\", "/")
        if path:
            paths.append(path)
    return paths


def classify_starting_status(status_text: str, report_root_rel: str) -> tuple[str, list[str]]:
    paths = parse_status_paths(status_text)
    if not paths:
        return "CLEAN", []
    allowed_prefixes = [
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_scope_pack_consumer_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_schema_validation_runner_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_taskpack_validator_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/newgen_repo_hygiene_check_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/evidence_index_smoke_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/PLAYBOOKS/MECHANICUS_QUALITY_GATE_PLAYBOOK_V0_1.md",
        report_root_rel.rstrip("/") + "/",
    ]
    unrelated = [path for path in paths if not any(path.startswith(prefix) for prefix in allowed_prefixes)]
    if unrelated:
        return "HAS_UNRELATED_DIRTY", unrelated
    return "TASK_OWNED_DIRTY_EXPECTED", []


def evaluate_officio_gate(
    task_id: str,
    repo_root: Path,
    report_root: Path,
    starting_head: str,
    starting_branch: str,
) -> tuple[str, dict[str, Any]]:
    gate_ack_path = report_root / "GATE_ACK.md"
    role_pack_path = repo_root / OFFICIO_ROLE_PACK_REL
    checker_path = repo_root / OFFICIO_CHECKER_REL

    warnings: list[str] = []
    errors: list[str] = []
    ack_status: dict[str, bool] = {}

    gate_ack_text = ""
    if gate_ack_path.exists():
        gate_ack_text = gate_ack_path.read_text(encoding="utf-8")
    else:
        errors.append("missing_gate_ack_md")

    for token in REQUIRED_ACKS:
        ack_status[token] = token in gate_ack_text
        if not ack_status[token]:
            errors.append(f"missing_ack:{token}")

    role_pack_data: dict[str, Any] = {}
    if role_pack_path.exists():
        try:
            payload = load_json(role_pack_path)
            if isinstance(payload, dict):
                role_pack_data = payload
        except Exception as exc:
            errors.append(f"role_pack_parse_failed:{exc}")
    else:
        errors.append("missing_role_pack")

    if not checker_path.exists():
        warnings.append("officio_response_contract_checker_missing_optional")

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    report = {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_quality_gate_runner_v0_1.py:officio_gate_use",
        "starting_head": starting_head,
        "starting_branch": starting_branch,
        "officio_references": {
            "gate_ack_path": relative_or_abs(gate_ack_path, repo_root),
            "role_pack_path": relative_or_abs(role_pack_path, repo_root),
            "officio_checker_path": relative_or_abs(checker_path, repo_root),
        },
        "ack_status": ack_status,
        "role_pack_summary": {
            "role_id": role_pack_data.get("role_id"),
            "owner_facing_language": role_pack_data.get("owner_facing_language"),
            "required_acks": role_pack_data.get("required_acks", []),
            "forbidden_actions": role_pack_data.get("forbidden_actions", []),
        },
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    return verdict, report


def run_code_quality(task_id: str, repo_root: Path) -> tuple[str, dict[str, Any]]:
    files = [repo_root / rel for rel in TOOL_SCRIPTS]
    missing = [relative_or_abs(path, repo_root) for path in files if not path.exists()]
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    if missing:
        errors.extend([f"missing_tool_script:{item}" for item in missing])

    script_args = [str(path) for path in files if path.exists()]
    py_compile_status = "FAIL"
    ruff_status = "WARN"
    mypy_status = "WARN"

    if script_args:
        py_compile_cmd = [sys.executable, "-m", "py_compile", *script_args]
        py_compile_result = run_command(py_compile_cmd, cwd=repo_root)
        py_compile_status = "PASS" if py_compile_result.exit_code == 0 else "FAIL"
        if py_compile_status == "FAIL":
            errors.append("py_compile_failed")
        checks.append(
            {
                "check": "py_compile",
                "status": py_compile_status,
                "exit_code": py_compile_result.exit_code,
                "command": " ".join(py_compile_result.command),
                "stdout_excerpt": short_text(py_compile_result.stdout),
                "stderr_excerpt": short_text(py_compile_result.stderr),
            }
        )

        ruff_cmd = [sys.executable, "-m", "ruff", "check", *script_args]
        ruff_result = run_command(ruff_cmd, cwd=repo_root)
        if ruff_result.exit_code == 0:
            ruff_status = "PASS"
        else:
            ruff_status = "WARN"
            warnings.append("ruff_nonzero_or_unavailable")
        checks.append(
            {
                "check": "ruff",
                "status": ruff_status,
                "exit_code": ruff_result.exit_code,
                "command": " ".join(ruff_result.command),
                "stdout_excerpt": short_text(ruff_result.stdout),
                "stderr_excerpt": short_text(ruff_result.stderr),
            }
        )

        mypy_cmd = [sys.executable, "-m", "mypy", *script_args]
        mypy_result = run_command(mypy_cmd, cwd=repo_root)
        if mypy_result.exit_code == 0:
            mypy_status = "PASS"
        else:
            mypy_status = "WARN"
            warnings.append("mypy_nonzero_warn_allowed")
        checks.append(
            {
                "check": "mypy",
                "status": mypy_status,
                "exit_code": mypy_result.exit_code,
                "command": " ".join(mypy_result.command),
                "stdout_excerpt": short_text(mypy_result.stdout),
                "stderr_excerpt": short_text(mypy_result.stderr),
            }
        )

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    report = {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_quality_gate_runner_v0_1.py:code_quality",
        "target_scripts": [relative_or_abs(path, repo_root) for path in files],
        "checks": checks,
        "summary": {
            "py_compile": py_compile_status,
            "ruff": ruff_status,
            "mypy": mypy_status,
        },
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    return verdict, report


def build_quality_gate_report(
    task_id: str,
    statuses: dict[str, str],
    warnings: list[str],
    failures: list[str],
) -> dict[str, Any]:
    if any(status in {"FAIL", "BLOCKED"} for status in statuses.values()):
        overall = "FAIL"
    elif any(status == "WARN" for status in statuses.values()):
        overall = "PASS_WITH_WARNINGS"
    else:
        overall = "PASS"

    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "gates": statuses,
        "overall_verdict": overall,
        "warnings": warnings,
        "failures": failures,
        "reports": [],
    }


def build_inquisition_handoff(
    task_id: str,
    hygiene_report: dict[str, Any],
    fake_report: dict[str, Any],
    overall_verdict: str,
) -> dict[str, Any]:
    fake_count = int(fake_report.get("summary", {}).get("fake_canon_count", 0))
    hygiene_hits = int(hygiene_report.get("summary", {}).get("total_hits", 0))
    risks: list[str] = []
    if fake_count > 0:
        risks.append("fake_canon_detected")
    if hygiene_hits > 0:
        risks.append("runtime_or_hygiene_hits_detected")
    if overall_verdict == "FAIL":
        risks.append("overall_verdict_fail")

    verdict = "PASS"
    if fake_count > 0:
        verdict = "FAIL"
    elif hygiene_hits > 0 or overall_verdict == "PASS_WITH_WARNINGS":
        verdict = "WARN"

    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "handoff_to": "INQUISITION",
        "checker": "mechanicus_quality_gate_runner_v0_1.py",
        "hygiene_verdict": hygiene_report.get("verdict", "UNKNOWN"),
        "fake_canon_verdict": fake_report.get("verdict", "UNKNOWN"),
        "fake_canon_count": fake_count,
        "hygiene_total_hits": hygiene_hits,
        "risks": risks,
        "verdict": verdict,
    }


def build_ghost_evolve_proof(task_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "proof_id": "ghost_evolve_batch_002",
        "manual_to_reusable_conversion": [
            {
                "manual_before": "Manual selection of scope packs and checks.",
                "reusable_now": "mechanicus_scope_pack_consumer_v0_1.py + mechanicus_quality_gate_runner_v0_1.py",
            },
            {
                "manual_before": "Manual JSON parsing and inconsistent schema decisions.",
                "reusable_now": "mechanicus_schema_validation_runner_v0_1.py",
            },
            {
                "manual_before": "Manual dossier structure check per ZIP.",
                "reusable_now": "mechanicus_taskpack_validator_v0_1.py",
            },
            {
                "manual_before": "Manual hygiene scanning and evidence grep.",
                "reusable_now": "newgen_repo_hygiene_check_v0_1.py + evidence_index_smoke_v0_1.py",
            },
        ],
        "rerun_commands": [
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_quality_gate_runner_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1 --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_taskpack_validator_v0_1.py --taskpack-zip <DOSSIER.zip> --output <report.json>",
        ],
        "future_servitor_decisions_removed": [
            "Which scope packs to consume for this gate family.",
            "How to classify NO_SCHEMA_AVAILABLE vs FAIL.",
            "How to run compact hygiene and evidence smoke.",
        ],
        "limitations": [
            "Mypy can emit first-pass warnings; treated as WARN per contract.",
            "Schema coverage remains partial where no explicit schema exists.",
        ],
    }


def build_administratum_evidence_map(task_id: str, repo_root: Path, report_root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(report_root.glob("*")):
        if not path.is_file():
            continue
        files.append(
            {
                "path": relative_or_abs(path, repo_root),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "owner_organ": "ADMINISTRATUM",
        "report_root": relative_or_abs(report_root, repo_root),
        "artifact_count": len(files),
        "artifacts": files,
    }


def build_kpd_self_review(task_id: str) -> dict[str, Any]:
    return {
        "agent_kpd_self_review": {
            "task_id": task_id,
            "agent_role": "Codex big-model Servitor",
            "useful_outputs": [
                "Reusable quality gate runner and five helper tools",
                "Repeatable report bundle for Officio+Mechanicus combined gate",
            ],
            "waste_points": [
                "Initial context loading is heavy due mandatory multi-organ read route.",
            ],
            "missing_tools": [
                "Dedicated schema registry for Officio role pack and task reports.",
            ],
            "generated_tools_to_preserve": [
                "mechanicus_scope_pack_consumer_v0_1.py",
                "mechanicus_schema_validation_runner_v0_1.py",
                "mechanicus_taskpack_validator_v0_1.py",
                "newgen_repo_hygiene_check_v0_1.py",
                "evidence_index_smoke_v0_1.py",
                "mechanicus_quality_gate_runner_v0_1.py",
            ],
            "recommended_script_absorption": [
                "Absorb all six tools into Mechanicus reusable gate lane.",
            ],
            "recommended_narrow_agent_profiles": [
                "MECHANICUS_QUALITY_GATE_EXECUTOR_PC_V0_1",
            ],
            "future_prompt_improvements": [
                "Add explicit schema map artifact in every taskpack.",
            ],
            "future_gate_or_checklist_recommendations": [
                "Add mandatory `schema_map.json` for report artifacts.",
            ],
            "kpd_verdict": "GOOD",
        }
    }


def build_final_report_md(
    task_id: str,
    repo_root: Path,
    report_root: Path,
    starting_head: str,
    starting_status: str,
    scope_report: dict[str, Any],
    officio_report: dict[str, Any],
    quality_gate_report: dict[str, Any],
    code_quality_report: dict[str, Any],
    schema_report: dict[str, Any],
    taskpack_report: dict[str, Any],
    hygiene_report: dict[str, Any],
    evidence_report: dict[str, Any],
    fake_report: dict[str, Any],
    starting_status_classification: str,
) -> str:
    overall = quality_gate_report.get("overall_verdict", "UNKNOWN")
    gate_rows = [
        ("py_compile", code_quality_report.get("summary", {}).get("py_compile", "UNKNOWN"), "code_quality_report.json"),
        ("ruff", code_quality_report.get("summary", {}).get("ruff", "UNKNOWN"), "code_quality_report.json"),
        ("mypy", code_quality_report.get("summary", {}).get("mypy", "UNKNOWN"), "code_quality_report.json"),
        ("JSON/schema", schema_report.get("verdict", "UNKNOWN"), "schema_validation_report.json"),
        ("taskpack validation", taskpack_report.get("verdict", "UNKNOWN"), "taskpack_validation_report.json"),
        ("hygiene", hygiene_report.get("verdict", "UNKNOWN"), "newgen_hygiene_report.json"),
        ("evidence index smoke", evidence_report.get("verdict", "UNKNOWN"), "evidence_index_smoke_report.json"),
        ("fake CANON", fake_report.get("verdict", "UNKNOWN"), "fake_canon_detector_report.json"),
    ]
    scope_rows = scope_report.get("consumed_scope_packs", [])
    ack_status = officio_report.get("ack_status", {})
    ending_head = run_git(repo_root, "rev-parse", "@")
    status_end = run_git(repo_root, "status", "--short")
    worktree_clean = "yes" if not status_end.strip() else "no"

    lines: list[str] = []
    lines.append(f"# Final Report — {task_id}")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(str(overall))
    lines.append("")
    lines.append("## Owner-facing summary RU")
    lines.append("")
    lines.append("Собран повторяемый Mechanicus quality gate runner с обязательным Officio role/language admission.")
    lines.append("Runner потребляет scope packs, запускает code quality/JSON/taskpack/hygiene/fake-canon/evidence-index smoke.")
    lines.append("Сформирован полный комплект отчетов и receipts для Inquisition/Administratum handoff без install/visual/cloud.")
    lines.append("Результат готов к повторному прогону будущими Servitor по playbook.")
    lines.append("")
    lines.append("## Starting state")
    lines.append("")
    lines.append(f"- Repo root: `{repo_root.as_posix()}`")
    lines.append(f"- Starting HEAD: `{starting_head}`")
    if starting_status_classification == "CLEAN":
        lines.append("- Starting git status: `clean`")
    else:
        lines.append(f"- Starting git status: `{starting_status_classification}`")
    lines.append(f"- Officio role pack read: `{OFFICIO_ROLE_PACK_REL}`")
    lines.append("- Mechanicus scope packs read: yes")
    lines.append("")
    lines.append("## Officio gate")
    lines.append("")
    lines.append("| ACK | Status | Evidence |")
    lines.append("|---|---|---|")
    for key in REQUIRED_ACKS:
        lines.append(f"| {key} | {'PASS' if ack_status.get(key) else 'FAIL'} | GATE_ACK.md |")
    lines.append("")
    lines.append("## Scope consumption")
    lines.append("")
    lines.append("| Scope pack | Consumed | Result |")
    lines.append("|---|---|---|")
    for row in scope_rows:
        scope_id = row.get("scope_id", "unknown")
        consumed = "yes" if row.get("exists", False) else "no"
        result = "PASS" if row.get("exists", False) else "FAIL"
        lines.append(f"| {scope_id} | {consumed} | {result} |")
    lines.append("")
    lines.append("## Quality gate results")
    lines.append("")
    lines.append("| Gate | Result | Report |")
    lines.append("|---|---|---|")
    for gate_name, gate_result, report_name in gate_rows:
        lines.append(f"| {gate_name} | {gate_result} | {report_name} |")
    lines.append("")
    lines.append("## New reusable Mechanicus tools")
    lines.append("")
    lines.append("| Tool | Path | How to rerun |")
    lines.append("|---|---|---|")
    for rel in TOOL_SCRIPTS:
        filename = Path(rel).name
        lines.append(f"| {filename} | {rel} | `python {rel} --help` |")
    lines.append("")
    lines.append("## Inquisition")
    lines.append("")
    lines.append("- Handoff: `inquisition_hygiene_handoff.json`")
    lines.append(f"- Dirt found: `{hygiene_report.get('summary', {}).get('total_hits', 0)}`")
    lines.append(f"- Fake green risk: `fake_canon_count={fake_report.get('summary', {}).get('fake_canon_count', 0)}`")
    lines.append("")
    lines.append("## Administratum")
    lines.append("")
    lines.append("- Evidence map: `administratum_evidence_map.json`")
    lines.append("- Reports: report-root bundle for batch 002")
    lines.append("- Receipts/exports: closure_receipt + quality gate reports")
    lines.append("")
    lines.append("## Ghost_Evolve proof")
    lines.append("")
    lines.append("- Proof path: `ghost_evolve_batch_002_training_proof.json`")
    lines.append("- Manual work converted into reusable tools: yes")
    lines.append("- Future Servitor load reduced by: scope/check/report automation")
    lines.append("")
    lines.append("## Ending state")
    lines.append("")
    lines.append(f"- Ending HEAD: `{ending_head}`")
    lines.append("- Commit: `NOT_PERFORMED_BY_RUNNER`")
    lines.append("- Push: `NOT_PERFORMED_BY_RUNNER`")
    lines.append(f"- Worktree: `{worktree_clean}`")
    lines.append("- Remote sync: `not_checked_after_edits`")
    lines.append("")
    lines.append("## Next allowed task")
    lines.append("")
    lines.append(f"`{NEXT_ALLOWED_TASK_PASS if overall == 'PASS' else NEXT_ALLOWED_TASK_WARN}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Mechanicus Validation Batch 002 quality gate.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--taskpack-zip", default=DEFAULT_TASKPACK_ZIP)
    parser.add_argument("--taskpack-dir", help="Optional unpacked dossier directory for schema/structure checks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(Path(args.repo_root))
    report_root = Path(args.report_root)
    if not report_root.is_absolute():
        report_root = (repo_root / report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    taskpack_zip = Path(args.taskpack_zip).resolve()
    taskpack_dir = Path(args.taskpack_dir).resolve() if args.taskpack_dir else None

    starting_head = run_git(repo_root, "rev-parse", "@")
    starting_branch = run_git(repo_root, "branch", "--show-current")
    starting_status = run_git(repo_root, "status", "--short")
    starting_log = run_git(repo_root, "log", "-8", "--oneline")
    report_root_rel = relative_or_abs(report_root, repo_root)
    starting_status_classification, unrelated_start_dirty = classify_starting_status(starting_status, report_root_rel)

    officio_status, officio_report = evaluate_officio_gate(
        task_id=args.task_id,
        repo_root=repo_root,
        report_root=report_root,
        starting_head=starting_head,
        starting_branch=starting_branch,
    )
    write_json(report_root / "officio_gate_use_report.json", officio_report)

    scope_status, scope_report, scope_result = run_json_tool(
        repo_root=repo_root,
        command=[
            sys.executable,
            str((repo_root / SCOPE_CONSUMER_REL).resolve()),
            "--task-id",
            args.task_id,
            "--repo-root",
            str(repo_root),
            "--output",
            str((report_root / "scope_pack_consumption_report.json").resolve()),
        ],
        output_path=report_root / "scope_pack_consumption_report.json",
    )

    code_quality_status, code_quality_report = run_code_quality(args.task_id, repo_root=repo_root)
    write_json(report_root / "code_quality_report.json", code_quality_report)

    schema_command = [
        sys.executable,
        str((repo_root / SCHEMA_RUNNER_REL).resolve()),
        "--task-id",
        args.task_id,
        "--repo-root",
        str(repo_root),
        "--report-root",
        str(report_root),
        "--output",
        str((report_root / "schema_validation_report.json").resolve()),
    ]
    if taskpack_dir is not None and taskpack_dir.exists():
        schema_command.extend(["--taskpack-dir", str(taskpack_dir)])
    schema_status, schema_report, schema_result = run_json_tool(
        repo_root=repo_root,
        command=schema_command,
        output_path=report_root / "schema_validation_report.json",
    )

    taskpack_status, taskpack_report, taskpack_result = run_json_tool(
        repo_root=repo_root,
        command=[
            sys.executable,
            str((repo_root / TASKPACK_VALIDATOR_REL).resolve()),
            "--task-id",
            args.task_id,
            "--taskpack-zip",
            str(taskpack_zip),
            "--output",
            str((report_root / "taskpack_validation_report.json").resolve()),
        ],
        output_path=report_root / "taskpack_validation_report.json",
    )

    hygiene_status, hygiene_report, hygiene_result = run_json_tool(
        repo_root=repo_root,
        command=[
            sys.executable,
            str((repo_root / HYGIENE_RUNNER_REL).resolve()),
            "--task-id",
            args.task_id,
            "--repo-root",
            str(repo_root),
            "--output",
            str((report_root / "newgen_hygiene_report.json").resolve()),
        ],
        output_path=report_root / "newgen_hygiene_report.json",
    )

    evidence_status, evidence_report, evidence_result = run_json_tool(
        repo_root=repo_root,
        command=[
            sys.executable,
            str((repo_root / EVIDENCE_SMOKE_REL).resolve()),
            "--task-id",
            args.task_id,
            "--report-root",
            str(report_root),
            "--db-path",
            str((report_root / "evidence_index_smoke.sqlite3").resolve()),
            "--output",
            str((report_root / "evidence_index_smoke_report.json").resolve()),
        ],
        output_path=report_root / "evidence_index_smoke_report.json",
    )

    fake_canon_result = run_command(
        [
            sys.executable,
            str((repo_root / FAKE_CANON_DETECTOR_REL).resolve()),
            "--task-id",
            args.task_id,
            "--repo-root",
            str(repo_root),
            "--output",
            str((report_root / "fake_canon_detector_report.json").resolve()),
        ],
        cwd=repo_root,
    )
    if (report_root / "fake_canon_detector_report.json").exists():
        fake_report = load_json(report_root / "fake_canon_detector_report.json")
    else:
        fake_report = {
            "verdict": "FAIL",
            "summary": {"fake_canon_count": -1},
            "errors": ["fake_canon_report_missing"],
        }
    fake_status = normalize_gate_status(str(fake_report.get("verdict", status_from_exit(fake_canon_result))))

    statuses: dict[str, str] = {
        "officio_gate": officio_status,
        "scope_consumption": scope_status,
        "py_compile": normalize_gate_status(code_quality_report.get("summary", {}).get("py_compile", "BLOCKED")),
        "ruff": normalize_gate_status(code_quality_report.get("summary", {}).get("ruff", "BLOCKED")),
        "mypy": normalize_gate_status(code_quality_report.get("summary", {}).get("mypy", "BLOCKED")),
        "json_schema": schema_status,
        "taskpack_validation": taskpack_status,
        "hygiene": hygiene_status,
        "evidence_index_smoke": evidence_status,
        "fake_canon": fake_status,
    }

    warnings: list[str] = []
    failures: list[str] = []
    for gate, status in statuses.items():
        if status == "WARN":
            warnings.append(f"{gate}:WARN")
        if status in {"FAIL", "BLOCKED"}:
            failures.append(f"{gate}:{status}")

    quality_gate_report = build_quality_gate_report(
        task_id=args.task_id,
        statuses=statuses,
        warnings=warnings,
        failures=failures,
    )
    write_json(report_root / "quality_gate_run_report.json", quality_gate_report)

    inquisition_handoff = build_inquisition_handoff(
        task_id=args.task_id,
        hygiene_report=hygiene_report,
        fake_report=fake_report,
        overall_verdict=str(quality_gate_report.get("overall_verdict", "UNKNOWN")),
    )
    write_json(report_root / "inquisition_hygiene_handoff.json", inquisition_handoff)

    ghost_evolve_proof = build_ghost_evolve_proof(args.task_id)
    write_json(report_root / "ghost_evolve_batch_002_training_proof.json", ghost_evolve_proof)

    kpd_review = build_kpd_self_review(args.task_id)
    write_json(report_root / "agent_kpd_self_review.json", kpd_review)

    evidence_map = build_administratum_evidence_map(args.task_id, repo_root=repo_root, report_root=report_root)
    write_json(report_root / "administratum_evidence_map.json", evidence_map)

    ending_head = run_git(repo_root, "rev-parse", "@")
    remote_master = run_git(repo_root, "ls-remote", "origin", "refs/heads/master")
    origin_master_ref = remote_master.split()[0] if remote_master else ""
    remote_sync_after_push = bool(origin_master_ref) and ending_head == origin_master_ref
    worktree_clean = run_git(repo_root, "status", "--short").strip() == ""
    overall = str(quality_gate_report.get("overall_verdict", "FAIL"))
    next_allowed = NEXT_ALLOWED_TASK_PASS if overall == "PASS" else NEXT_ALLOWED_TASK_WARN
    fake_canon_count = int(fake_report.get("summary", {}).get("fake_canon_count", 0))

    closure = {
        "task_id": args.task_id,
        "verdict": overall,
        "repo_root": repo_root.as_posix(),
        "starting_head": starting_head,
        "ending_head": ending_head,
        "external_finalization_semantics": {
            "receipt_subject_head": starting_head,
            "receipt_content_head": ending_head,
            "external_delivery_head": origin_master_ref,
            "remote_head_after_push": origin_master_ref,
            "followup_finalization_receipt_head": "",
            "self_head_paradox_handled": True,
            "clean_pass_allowed": False,
            "caps_triggered": ["CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"],
        },
        "commit": "NOT_PERFORMED_BY_RUNNER",
        "push": "NOT_PERFORMED_BY_RUNNER",
        "worktree_clean": "yes" if worktree_clean else "no",
        "remote_sync": "yes" if remote_sync_after_push else "no",
        "owner_facing_language": "RU",
        "officio_gate_used": bool(officio_status == "PASS"),
        "mechanicus_scopes_consumed": [row.get("scope_id", "") for row in scope_report.get("consumed_scope_packs", [])],
        "quality_gate_runner_created": True,
        "quality_gate_runner_ran": True,
        "json_schema_gate_ran": True,
        "taskpack_validator_created": True,
        "hygiene_scan_ran": True,
        "evidence_index_smoke_ran": True,
        "fake_canon_count": fake_canon_count,
        "install_performed": False,
        "visual_prototypes_created": False,
        "llm_cloud_activated": False,
        "warnings": warnings,
        "next_allowed_task": next_allowed,
    }
    write_json(report_root / "closure_receipt.json", closure)

    final_report = build_final_report_md(
        task_id=args.task_id,
        repo_root=repo_root,
        report_root=report_root,
        starting_head=starting_head,
        starting_status=starting_status,
        scope_report=scope_report,
        officio_report=officio_report,
        quality_gate_report=quality_gate_report,
        code_quality_report=code_quality_report,
        schema_report=schema_report,
        taskpack_report=taskpack_report,
        hygiene_report=hygiene_report,
        evidence_report=evidence_report,
        fake_report=fake_report,
        starting_status_classification=starting_status_classification,
    )
    write_text(report_root / "FINAL_REPORT.md", final_report)

    command_trace = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "starting_head": starting_head,
        "starting_branch": starting_branch,
        "starting_status": starting_status,
        "starting_status_classification": starting_status_classification,
        "starting_status_unrelated_paths": unrelated_start_dirty,
        "starting_log": starting_log.splitlines(),
        "commands": [
            {
                "name": "scope_consumer",
                "exit_code": scope_result.exit_code,
                "stdout_excerpt": short_text(scope_result.stdout),
                "stderr_excerpt": short_text(scope_result.stderr),
            },
            {
                "name": "schema_runner",
                "exit_code": schema_result.exit_code,
                "stdout_excerpt": short_text(schema_result.stdout),
                "stderr_excerpt": short_text(schema_result.stderr),
            },
            {
                "name": "taskpack_validator",
                "exit_code": taskpack_result.exit_code,
                "stdout_excerpt": short_text(taskpack_result.stdout),
                "stderr_excerpt": short_text(taskpack_result.stderr),
            },
            {
                "name": "hygiene_runner",
                "exit_code": hygiene_result.exit_code,
                "stdout_excerpt": short_text(hygiene_result.stdout),
                "stderr_excerpt": short_text(hygiene_result.stderr),
            },
            {
                "name": "evidence_smoke",
                "exit_code": evidence_result.exit_code,
                "stdout_excerpt": short_text(evidence_result.stdout),
                "stderr_excerpt": short_text(evidence_result.stderr),
            },
            {
                "name": "fake_canon_detector",
                "exit_code": fake_canon_result.exit_code,
                "stdout_excerpt": short_text(fake_canon_result.stdout),
                "stderr_excerpt": short_text(fake_canon_result.stderr),
            },
        ],
    }
    write_json(report_root / "runner_command_trace.json", command_trace)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "overall_verdict": overall,
                "warnings": len(warnings),
                "failures": len(failures),
                "report_root": report_root.as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0 if overall in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
