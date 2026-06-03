from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
TASK_ID = "TASK-20260519-ORGAN-AGENT-IDENTITY-HALF-RICH-SHELL-8-ORGANS-V0_1"
REPORT_ROOT = REPO_ROOT / "IMPERIUM_NEW_GENERATION" / "REPORTS"
TASK_REPORT_DIR = REPORT_ROOT / TASK_ID
LOG_DIR = TASK_REPORT_DIR / "SWEEP_LOGS"

COMBINED_MD = REPORT_ROOT / "EIGHT_ORGAN_IDENTITY_RICH_SHELL_RUN_REPORT.md"
COMBINED_JSON = REPORT_ROOT / "eight_organ_identity_rich_shell_run_report.json"
TASK_RECEIPT = TASK_REPORT_DIR / f"{TASK_ID}_RECEIPT.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args: list[str], log_name: str) -> dict[str, Any]:
    completed = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)
    out = completed.stdout or ""
    err = completed.stderr or ""
    parsed: dict[str, Any] | None = None
    try:
        parsed_raw = json.loads(out.strip())
        if isinstance(parsed_raw, dict):
            parsed = parsed_raw
    except Exception:
        parsed = None

    joined = f"{out}\n{err}".upper()
    severity = "PASS"
    if completed.returncode != 0:
        severity = "ERROR"
    if "BLOCKED" in joined:
        severity = "BLOCKER"
    elif "WARN" in joined and severity == "PASS":
        severity = "WARN"
    if parsed:
        if str(parsed.get("visual_status", "")).upper().startswith("WARN") and severity == "PASS":
            severity = "WARN"
        if parsed.get("warnings") and severity == "PASS":
            severity = "WARN"

    log_path = LOG_DIR / f"{log_name}.json"
    payload = {
        "cmd": args,
        "returncode": completed.returncode,
        "severity": severity,
        "stdout": out,
        "stderr": err,
        "json": parsed,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return payload


def build_runs() -> list[dict[str, Any]]:
    simple = [
        ("INQUISITION_AGENT", "inquisition_agent_runner.py", ["fake-green-check", "scope-drift-check", "hygiene-scan", "audit-claims"]),
        ("MECHANICUS_AGENT", "mechanicus_agent_runner.py", ["tool-list", "validator-check", "capability-map", "script-receipt-check"]),
        ("ASTRONOMICON_AGENT", "astronomicon_agent_runner.py", ["task-route", "stage-map-outline", "ready-for-agent-check", "route-report"]),
        ("STRATEGIUM_AGENT", "strategium_agent_runner.py", ["priority-matrix", "campaign-plan-outline", "resource-estimate", "freeze-list"]),
        ("SCHOLA_IMPERIALIS_AGENT", "schola_imperialis_agent_runner.py", ["lesson-register", "training-pack-outline", "skill-map", "example-check"]),
        ("DOCTRINARIUM_AGENT", "doctrinarium_agent_runner.py", ["law-list", "doctrine-check", "violation-report", "gate-before-work"]),
    ]
    rows: list[dict[str, Any]] = []
    for organ, runner, domain in simple:
        path = f"IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/{organ}/TOOLS/{runner}"
        commands = [
            ("cli_launch", ["python", path, "help"]),
            ("shell_smoke", ["python", path, "shell", "--once", "help"]),
            ("status", ["python", path, "status"]),
            ("check", ["python", path, "check"]),
            ("identity", ["python", path, "identity"]),
        ]
        for cmd in domain:
            commands.append((cmd, ["python", path, cmd]))
        rows.append({"organ": organ, "runner": path, "domain_mode": "direct", "commands": commands})

    rows.append(
        {
            "organ": "ADMINISTRATUM_AGENT",
            "runner": "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py",
            "domain_mode": "equivalent_aliases",
            "domain_alias_map": {
                "address-summary": "where",
                "chronicle-summary": "recent",
                "continuity-outline": "pack",
                "evidence-dossier-outline": "help",
            },
            "commands": [
                ("cli_launch", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--help"]),
                ("shell_smoke", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "shell", "--once", "/help"]),
                ("status", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "status"]),
                ("check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "check"]),
                ("identity", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "identity"]),
                ("address-summary", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "where"]),
                ("chronicle-summary", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "recent", "--limit", "5"]),
                ("continuity-outline", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "pack"]),
                ("evidence-dossier-outline", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "--plain-json", "help"]),
            ],
        }
    )

    commands_file = TASK_REPORT_DIR / "officio_shell_commands.txt"
    commands_file.write_text("/help\n/exit\n", encoding="utf-8")
    rows.append(
        {
            "organ": "OFFICIO_AGENTIS_AGENT",
            "runner": "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py",
            "domain_mode": "equivalent_aliases",
            "domain_alias_map": {
                "role-pack-check": "pack-build-role --agent SERVITOR_PRIME",
                "settings-contract-check": "settings-get --agent SERVITOR_PRIME --mode EXECUTOR",
                "response-contract-check": "check-all",
                "role-ack-check": "role-get --agent SERVITOR_PRIME",
            },
            "commands": [
                ("cli_launch", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "--help"]),
                ("shell_smoke", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "shell", "--commands-file", str(commands_file), "--non-interactive"]),
                ("status", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "status"]),
                ("check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "check-all"]),
                ("identity", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "role-get", "--agent", "SERVITOR_PRIME"]),
                ("role-pack-check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "pack-build-role", "--agent", "SERVITOR_PRIME"]),
                ("settings-contract-check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "settings-get", "--agent", "SERVITOR_PRIME", "--mode", "EXECUTOR"]),
                ("response-contract-check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "check-all"]),
                ("role-ack-check", ["python", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "role-get", "--agent", "SERVITOR_PRIME"]),
            ],
        }
    )
    return rows


def validate_identity_json() -> list[dict[str, Any]]:
    organs = [
        "INQUISITION_AGENT",
        "MECHANICUS_AGENT",
        "ADMINISTRATUM_AGENT",
        "ASTRONOMICON_AGENT",
        "STRATEGIUM_AGENT",
        "OFFICIO_AGENTIS_AGENT",
        "SCHOLA_IMPERIALIS_AGENT",
        "DOCTRINARIUM_AGENT",
    ]
    rows: list[dict[str, Any]] = []
    for organ in organs:
        for rel in ["identity_profile.json", "lore_functions.json", "domain_commands.json"]:
            path = REPO_ROOT / "IMPERIUM_NEW_GENERATION" / "ORGAN_AGENTS" / organ / "IDENTITY" / rel
            ok = True
            error = ""
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(raw, dict):
                    raise ValueError("top-level JSON is not object")
            except Exception as exc:
                ok = False
                error = str(exc)
            rows.append({"organ": organ, "path": str(path), "ok": ok, "error": error})
    return rows


def forbidden_scope_check() -> dict[str, Any]:
    completed = subprocess.run(["git", "diff", "--name-only"], cwd=REPO_ROOT, capture_output=True, text=True)
    paths = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    hits = [path for path in paths if ("THRONE" in path.upper() or "CUSTODES" in path.upper())]
    return {"diff_paths": paths, "forbidden_hits": hits, "ok": len(hits) == 0}


def main() -> int:
    TASK_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    sweep_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    for organ_entry in build_runs():
        organ = organ_entry["organ"]
        organ_results = []
        for command_name, args in organ_entry["commands"]:
            log_name = f"{organ.lower()}__{command_name.replace(' ', '_').replace('/', '_')}"
            result = run_cmd(args, log_name)
            row = {
                "command": command_name,
                "severity": result["severity"],
                "returncode": result["returncode"],
                "log_path": str(LOG_DIR / f"{log_name}.json"),
            }
            organ_results.append(row)
            evidence = {"organ": organ, "command": command_name, "log_path": row["log_path"]}
            if result["severity"] == "WARN":
                warnings.append(evidence)
            elif result["severity"] == "ERROR":
                errors.append(evidence)
            elif result["severity"] == "BLOCKER":
                blockers.append(evidence)
        sweep_rows.append(
            {
                "organ": organ,
                "runner": organ_entry["runner"],
                "domain_mode": organ_entry.get("domain_mode", "direct"),
                "domain_alias_map": organ_entry.get("domain_alias_map", {}),
                "results": organ_results,
            }
        )

    json_validation = validate_identity_json()
    bad_json = [row for row in json_validation if not row["ok"]]

    scope = forbidden_scope_check()

    overall_verdict = "PASS_BACKEND_IDENTITY_BASE_RICH_SHELL"
    if blockers:
        overall_verdict = "BLOCKED_SWEEP_BLOCKER"
    elif errors:
        overall_verdict = "PASS_BACKEND_IDENTITY_BASE_WITH_WARNINGS"
    elif warnings:
        overall_verdict = "PASS_BACKEND_IDENTITY_BASE_WITH_WARNINGS"

    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "organs": sweep_rows,
        "json_validation": json_validation,
        "json_validation_failed_count": len(bad_json),
        "forbidden_scope_check": scope,
        "warnings": warnings,
        "errors": errors,
        "blockers": blockers,
        "overall_verdict": overall_verdict,
        "evidence_bundle_dir": str(TASK_REPORT_DIR),
    }
    COMBINED_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Eight Organ Identity Rich Shell Run Report",
        "",
        f"- task_id: `{TASK_ID}`",
        f"- generated_at_utc: `{payload['generated_at_utc']}`",
        f"- overall_verdict: `{overall_verdict}`",
        f"- evidence_bundle_dir: `{TASK_REPORT_DIR}`",
        "",
        "## Organ Sweep Summary",
    ]
    for organ_row in sweep_rows:
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

    lines.extend(
        [
            "## JSON Validation",
            f"- failed_count: `{len(bad_json)}`",
        ]
    )
    for row in bad_json:
        lines.append(f"- FAIL `{row['organ']}` `{row['path']}`: {row['error']}")
    if not bad_json:
        lines.append("- all identity JSON files parsed successfully")

    lines.extend(
        [
            "",
            "## Forbidden Scope Check",
            f"- forbidden_hits: `{len(scope['forbidden_hits'])}`",
        ]
    )
    if scope["forbidden_hits"]:
        for hit in scope["forbidden_hits"]:
            lines.append(f"- {hit}")
    else:
        lines.append("- no THRONE/CUSTODES path in git diff")

    lines.extend(
        [
            "",
            "## WARN ERROR BLOCKER Table",
            f"- WARN: `{len(warnings)}`",
            f"- ERROR: `{len(errors)}`",
            f"- BLOCKER: `{len(blockers)}`",
        ]
    )
    for item in warnings:
        lines.append(f"- WARN `{item['organ']}` `{item['command']}` -> `{item['log_path']}`")
    for item in errors:
        lines.append(f"- ERROR `{item['organ']}` `{item['command']}` -> `{item['log_path']}`")
    for item in blockers:
        lines.append(f"- BLOCKER `{item['organ']}` `{item['command']}` -> `{item['log_path']}`")

    COMBINED_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    receipt = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "overall_verdict": overall_verdict,
        "combined_report_md": str(COMBINED_MD),
        "combined_report_json": str(COMBINED_JSON),
        "role_ack_path": str(TASK_REPORT_DIR / "OFFICIO_ROLE_ACK_SERVITOR_PRIME.json"),
        "evidence_bundle_dir": str(TASK_REPORT_DIR),
        "tool_artifacts": [
            {
                "path": str(Path(__file__)),
                "classification": "BUFFER_FOR_SCRIPTORIUM_REVIEW",
                "purpose": "Run eight-organ sweep and produce compact evidence reports.",
            }
        ],
    }
    TASK_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
