from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-20260519-WARN-DEBT-RICH-SHELL-HARDENING-8-ORGANS-V0_1"
DEFAULT_REPORT_DIR = (
    Path("IMPERIUM_NEW_GENERATION")
    / "REPORTS"
    / "TASK-20260519-WARN-DEBT-RICH-SHELL-HARDENING-8-ORGANS-V0_1"
)
DEFAULT_MD = "EIGHT_ORGAN_SWEEP_REPORT.md"
DEFAULT_JSON = "eight_organ_sweep_report.json"
DEFAULT_CSV = "EIGHT_ORGAN_WARN_ERROR_BLOCKER_MATRIX.csv"
DEFAULT_LOG_DIR = "SWEEP_LOGS"


@dataclass
class OrganSpec:
    organ: str
    runner: str
    domain_mode: str
    commands: list[tuple[str, list[str]]]
    domain_alias_map: dict[str, str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_abs_path(path: Path, repo_root: Path) -> Path:
    return path if path.is_absolute() else (repo_root / path)


def try_parse_json(stdout: str) -> dict[str, Any] | None:
    raw = stdout.strip()
    if not raw:
        return None
    try:
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def infer_severity(returncode: int, stdout: str, stderr: str, parsed: dict[str, Any] | None) -> str:
    joined = f"{stdout}\n{stderr}".upper()
    if returncode != 0:
        if "BLOCKED" in joined:
            return "BLOCKER"
        return "ERROR"
    if parsed is not None:
        for key in ("verdict", "status", "decision"):
            value = str(parsed.get(key, "")).upper()
            if value.startswith("BLOCKED"):
                return "BLOCKER"
            if value.startswith("FAIL"):
                return "ERROR"
        warnings = parsed.get("warnings")
        if isinstance(warnings, list) and warnings:
            return "WARN"
        visual_status = str(parsed.get("visual_status", "")).upper()
        if visual_status.startswith("WARN"):
            return "WARN"
    if "FAIL_RESPONSE_CONTRACT" in joined:
        return "ERROR"
    if "WARN" in joined:
        return "WARN"
    return "PASS"


def run_cmd(
    args: list[str],
    repo_root: Path,
    log_path: Path,
    command_env: dict[str, str] | None,
) -> dict[str, Any]:
    env = os.environ.copy()
    if command_env:
        env.update(command_env)
    completed = subprocess.run(
        args,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    out = completed.stdout or ""
    err = completed.stderr or ""
    parsed = try_parse_json(out)
    severity = infer_severity(completed.returncode, out, err, parsed)

    payload = {
        "cmd": args,
        "returncode": completed.returncode,
        "severity": severity,
        "stdout": out,
        "stderr": err,
        "json": parsed,
        "timestamp_utc": utc_now(),
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return payload


def forbidden_scope_check(repo_root: Path, forbidden_markers: list[str]) -> dict[str, Any]:
    completed = subprocess.run(["git", "diff", "--name-only"], cwd=repo_root, capture_output=True, text=True)
    diff_paths = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    hits: list[str] = []
    up_markers = [marker.upper() for marker in forbidden_markers]
    for diff_path in diff_paths:
        up_path = diff_path.upper()
        if any(marker in up_path for marker in up_markers):
            hits.append(diff_path)
    return {
        "diff_paths": diff_paths,
        "forbidden_scope_markers": forbidden_markers,
        "forbidden_hits": hits,
        "ok": len(hits) == 0,
    }


def build_sweep_specs(repo_root: Path, report_dir: Path, officio_runtime_root: Path | None) -> list[OrganSpec]:
    py = sys.executable
    specs: list[OrganSpec] = []

    simple_organs: list[tuple[str, str, list[str]]] = [
        ("INQUISITION_AGENT", "inquisition_agent_runner.py", ["fake-green-check", "scope-drift-check", "hygiene-scan"]),
        ("MECHANICUS_AGENT", "mechanicus_agent_runner.py", ["tool-list", "validator-check", "capability-map"]),
        ("ASTRONOMICON_AGENT", "astronomicon_agent_runner.py", ["task-route", "stage-map-outline", "ready-for-agent-check"]),
        ("STRATEGIUM_AGENT", "strategium_agent_runner.py", ["priority-matrix", "campaign-plan-outline", "freeze-list"]),
        ("SCHOLA_IMPERIALIS_AGENT", "schola_imperialis_agent_runner.py", ["lesson-register", "training-pack-outline", "skill-map"]),
        ("DOCTRINARIUM_AGENT", "doctrinarium_agent_runner.py", ["law-list", "doctrine-check", "violation-report"]),
    ]

    for organ, runner, domain_commands in simple_organs:
        runner_path = f"IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/{organ}/TOOLS/{runner}"
        commands: list[tuple[str, list[str]]] = [
            ("help", [py, runner_path, "help"]),
            ("shell-smoke", [py, runner_path, "shell", "--once", "help"]),
            ("status", [py, runner_path, "status"]),
            ("check", [py, runner_path, "check"]),
            ("identity", [py, runner_path, "identity"]),
        ]
        for cmd in domain_commands:
            commands.append((cmd, [py, runner_path, cmd]))
        specs.append(
            OrganSpec(
                organ=organ,
                runner=runner_path,
                domain_mode="direct",
                commands=commands,
                domain_alias_map={},
            )
        )

    admin_runner = "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py"
    specs.append(
        OrganSpec(
            organ="ADMINISTRATUM_AGENT",
            runner=admin_runner,
            domain_mode="equivalent_aliases",
            domain_alias_map={
                "address-summary": "where",
                "chronicle-summary": "recent --limit 5",
                "continuity-outline": "pack",
            },
            commands=[
                ("help", [py, admin_runner, "--plain-json", "help"]),
                ("shell-smoke", [py, admin_runner, "--plain-json", "shell", "--once", "/help"]),
                ("status", [py, admin_runner, "--plain-json", "status"]),
                ("check", [py, admin_runner, "--plain-json", "check"]),
                ("identity", [py, admin_runner, "--plain-json", "identity"]),
                ("address-summary", [py, admin_runner, "--plain-json", "where"]),
                ("chronicle-summary", [py, admin_runner, "--plain-json", "recent", "--limit", "5"]),
                ("continuity-outline", [py, admin_runner, "--plain-json", "pack"]),
            ],
        )
    )

    commands_file = report_dir / "officio_shell_commands.txt"
    commands_file.write_text("/help\n/exit\n", encoding="utf-8")
    officio_runner = "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py"
    officio_commands: list[tuple[str, list[str]]] = [
        ("help", [py, officio_runner, "--help"]),
        (
            "shell-smoke",
            [
                py,
                officio_runner,
                "shell",
                "--commands-file",
                str(commands_file),
                "--non-interactive",
            ],
        ),
        ("status", [py, officio_runner, "status"]),
        ("check", [py, officio_runner, "check-all"]),
        ("identity", [py, officio_runner, "role-get", "--agent", "SERVITOR_PRIME"]),
        ("role-pack-check", [py, officio_runner, "pack-build-role", "--agent", "SERVITOR_PRIME"]),
        (
            "settings-contract-check",
            [py, officio_runner, "settings-get", "--agent", "SERVITOR_PRIME", "--mode", "EXECUTOR"],
        ),
        ("response-contract-check", [py, officio_runner, "check-all"]),
    ]

    officio_aliases = {
        "role-pack-check": "pack-build-role --agent SERVITOR_PRIME",
        "settings-contract-check": "settings-get --agent SERVITOR_PRIME --mode EXECUTOR",
        "response-contract-check": "check-all",
    }
    specs.append(
        OrganSpec(
            organ="OFFICIO_AGENTIS_AGENT",
            runner=officio_runner,
            domain_mode="equivalent_aliases",
            commands=officio_commands,
            domain_alias_map=officio_aliases,
        )
    )

    if officio_runtime_root is not None:
        os.environ["OFFICIO_RUNTIME_ROOT"] = str(officio_runtime_root)

    return specs


def write_csv_matrix(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["organ", "command", "severity", "returncode", "log_path"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown_report(
    md_path: Path,
    payload: dict[str, Any],
    csv_path: Path,
) -> None:
    lines: list[str] = [
        "# Eight Organ Sweep Report",
        "",
        f"- task_id: `{payload['task_id']}`",
        f"- generated_at_utc: `{payload['generated_at_utc']}`",
        f"- overall_verdict: `{payload['overall_verdict']}`",
        f"- report_dir: `{payload['report_dir']}`",
        f"- matrix_csv: `{csv_path}`",
        "",
        "## Organs",
    ]

    for organ_row in payload["organs"]:
        lines.append(f"### {organ_row['organ']}")
        lines.append(f"- runner: `{organ_row['runner']}`")
        lines.append(f"- domain_mode: `{organ_row['domain_mode']}`")
        if organ_row["domain_alias_map"]:
            lines.append("- domain_alias_map:")
            for src, dst in organ_row["domain_alias_map"].items():
                lines.append(f"  - `{src}` -> `{dst}`")
        for result in organ_row["results"]:
            lines.append(f"- {result['command']}: `{result['severity']}` (rc={result['returncode']})")
            lines.append(f"  log: `{result['log_path']}`")
        lines.append("")

    scope = payload["forbidden_scope_check"]
    lines.extend(
        [
            "## Forbidden Scope Check",
            f"- markers: `{', '.join(scope['forbidden_scope_markers'])}`",
            f"- forbidden_hits: `{len(scope['forbidden_hits'])}`",
        ]
    )
    if scope["forbidden_hits"]:
        for hit in scope["forbidden_hits"]:
            lines.append(f"- {hit}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## WARN ERROR BLOCKER Summary",
            f"- WARN: `{len(payload['warnings'])}`",
            f"- ERROR: `{len(payload['errors'])}`",
            f"- BLOCKER: `{len(payload['blockers'])}`",
        ]
    )
    for row in payload["warnings"]:
        lines.append(f"- WARN `{row['organ']}` `{row['command']}` -> `{row['log_path']}`")
    for row in payload["errors"]:
        lines.append(f"- ERROR `{row['organ']}` `{row['command']}` -> `{row['log_path']}`")
    for row in payload["blockers"]:
        lines.append(f"- BLOCKER `{row['organ']}` `{row['command']}` -> `{row['log_path']}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run unified eight-organ sweep and emit MD/JSON/CSV reports.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    parser.add_argument("--md-name", default=DEFAULT_MD)
    parser.add_argument("--json-name", default=DEFAULT_JSON)
    parser.add_argument("--csv-name", default=DEFAULT_CSV)
    parser.add_argument("--log-dir-name", default=DEFAULT_LOG_DIR)
    parser.add_argument(
        "--forbidden-scope-markers",
        default="THRONE,CUSTODES",
        help="Comma-separated forbidden scope markers.",
    )
    parser.add_argument(
        "--officio-runtime-root",
        default="",
        help="Optional runtime root for Officio runner outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]

    report_dir = ensure_abs_path(Path(args.report_dir), repo_root)
    report_dir.mkdir(parents=True, exist_ok=True)
    log_dir = report_dir / args.log_dir_name
    md_path = report_dir / args.md_name
    json_path = report_dir / args.json_name
    csv_path = report_dir / args.csv_name

    officio_runtime_root = None
    if args.officio_runtime_root.strip():
        officio_runtime_root = ensure_abs_path(Path(args.officio_runtime_root.strip()), repo_root)
    else:
        officio_runtime_root = report_dir / "OFFICIO_RUNTIME"
    officio_runtime_root.mkdir(parents=True, exist_ok=True)
    organ_runtime_root = report_dir / "ORGAN_RUNTIME"
    organ_runtime_root.mkdir(parents=True, exist_ok=True)

    specs = build_sweep_specs(repo_root, report_dir, officio_runtime_root)

    matrix_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    organ_rows: list[dict[str, Any]] = []

    for spec in specs:
        command_rows: list[dict[str, Any]] = []
        for command_name, cmd_args in spec.commands:
            log_name = f"{spec.organ.lower()}__{command_name.replace(' ', '_').replace('/', '_')}.json"
            log_path = log_dir / log_name
            command_env = {"IMPERIUM_ORGAN_RUNTIME_ROOT": str(organ_runtime_root)}
            if spec.organ == "OFFICIO_AGENTIS_AGENT":
                command_env["OFFICIO_RUNTIME_ROOT"] = str(officio_runtime_root)
            result = run_cmd(cmd_args, repo_root, log_path, command_env)
            row = {
                "organ": spec.organ,
                "command": command_name,
                "severity": result["severity"],
                "returncode": result["returncode"],
                "log_path": str(log_path),
            }
            matrix_rows.append(row)
            command_rows.append({k: row[k] for k in ("command", "severity", "returncode", "log_path")})
            if row["severity"] == "WARN":
                warnings.append(row)
            elif row["severity"] == "ERROR":
                errors.append(row)
            elif row["severity"] == "BLOCKER":
                blockers.append(row)

        organ_rows.append(
            {
                "organ": spec.organ,
                "runner": spec.runner,
                "domain_mode": spec.domain_mode,
                "domain_alias_map": spec.domain_alias_map,
                "results": command_rows,
            }
        )

    forbidden_markers = [item.strip() for item in str(args.forbidden_scope_markers).split(",") if item.strip()]
    scope_check = forbidden_scope_check(repo_root, forbidden_markers)

    overall_verdict = "PASS_BACKEND_OPERATIONAL"
    if blockers:
        overall_verdict = "BLOCKED_SWEEP_RUNNER_FAILED"
    elif errors:
        overall_verdict = "PASS_BACKEND_OPERATIONAL_WITH_WARNINGS"
    elif warnings:
        overall_verdict = "PASS_BACKEND_OPERATIONAL_WITH_WARNINGS"

    payload = {
        "schema_version": "EIGHT_ORGAN_SWEEP_REPORT_V0_1",
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "overall_verdict": overall_verdict,
        "report_dir": str(report_dir),
        "log_dir": str(log_dir),
        "officio_runtime_root": str(officio_runtime_root),
        "organ_runtime_root": str(organ_runtime_root),
        "organs": organ_rows,
        "forbidden_scope_check": scope_check,
        "warnings": warnings,
        "errors": errors,
        "blockers": blockers,
        "counts": {
            "organs": len(organ_rows),
            "commands": len(matrix_rows),
            "warnings": len(warnings),
            "errors": len(errors),
            "blockers": len(blockers),
        },
    }

    write_csv_matrix(csv_path, matrix_rows)
    json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(md_path, payload, csv_path)

    print(f"SWEEP_MD: {md_path}")
    print(f"SWEEP_JSON: {json_path}")
    print(f"SWEEP_CSV: {csv_path}")
    print(f"OVERALL_VERDICT: {overall_verdict}")

    return 0 if overall_verdict != "BLOCKED_SWEEP_RUNNER_FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
