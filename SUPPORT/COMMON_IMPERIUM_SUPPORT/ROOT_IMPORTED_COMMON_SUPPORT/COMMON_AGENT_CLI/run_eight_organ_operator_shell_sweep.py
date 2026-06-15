from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-20260519-RICH-SHELL-OPERATOR-REPAIR-8-ORGANS-VM2-V0_1"
DEFAULT_REPORT_DIR = (
    Path("IMPERIUM_NEW_GENERATION")
    / "REPORTS"
    / "TASK-20260519-RICH-SHELL-OPERATOR-REPAIR-8-ORGANS-VM2-V0_1"
)


@dataclass
class OrganCase:
    organ: str
    runner: str
    kind: str  # base | administratum | officio


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_abs(path: Path, repo_root: Path) -> Path:
    return path if path.is_absolute() else (repo_root / path)


def parse_json_strict(text: str) -> dict[str, Any] | None:
    raw = text.strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def parse_labeled_paths(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value.startswith("/") or re.match(r"^[A-Za-z]:\\", value):
            out[key] = value
    return out


def read_json_if_exists(path: str) -> dict[str, Any] | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def run_command(
    cmd: list[str],
    repo_root: Path,
    log_path: Path,
    env: dict[str, str],
    stdin_text: str | None = None,
) -> dict[str, Any]:
    completed = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        input=stdin_text,
        env=env,
    )
    payload = {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timestamp_utc": utc_now(),
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return payload


def operator_zone_proof(text: str) -> dict[str, bool]:
    up = text.upper()
    top = ("TOP STATUS BAR" in up) or ("WELCOME" in up)
    left = ("LEFT WORK ZONE" in up) or ("STATUS" in up)
    right = ("RIGHT COMMAND ZONE" in up) or ("AVAILABLE RITES" in up)
    bottom = ("BOTTOM EVENT BAR" in up) or ("RECENT ACTIVITY" in up)
    return {
        "top_status_bar": top,
        "left_work_zone": left,
        "right_command_zone": right,
        "bottom_event_bar": bottom,
        "all_required_zones": top and left and right and bottom,
    }


def infer_renderer(
    status_stdout: str,
    shell_stdout: str,
    officio_renderer_diag_path: str | None,
) -> tuple[str, bool | None, dict[str, Any] | None]:
    status_json = parse_json_strict(status_stdout)
    if status_json:
        renderer_status = status_json.get("renderer_status")
        if isinstance(renderer_status, dict):
            renderer = str(renderer_status.get("renderer", "unknown"))
            rich_available = renderer_status.get("rich_renderer_available")
            if isinstance(rich_available, bool):
                return renderer, rich_available, status_json
        rich_available = status_json.get("rich_renderer_available")
        if isinstance(rich_available, bool):
            return ("rich" if rich_available else "ansi_fallback"), rich_available, status_json

    up = shell_stdout.upper()
    if "RENDERER: RICH" in up:
        return "rich", True, status_json
    if "RENDERER: ANSI_FALLBACK" in up:
        return "ansi_fallback", False, status_json
    # Administratum rich shell uses rounded box-drawing frames from Rich (╭╰),
    # while stdlib fallback uses square frames (┌└).
    if ("╭" in shell_stdout and "╰" in shell_stdout) and ("WELCOME" in up):
        return "rich", True, status_json
    if ("┌" in shell_stdout and "└" in shell_stdout) and ("WELCOME" in up):
        return "ansi_fallback", False, status_json

    if officio_renderer_diag_path:
        diag = read_json_if_exists(officio_renderer_diag_path)
        if diag:
            renderer = str(diag.get("renderer", "unknown"))
            rich_installed = diag.get("rich_installed")
            rich_available = bool(rich_installed) if isinstance(rich_installed, bool) else None
            return renderer, rich_available, diag

    return "unknown", None, status_json


def visual_status_for(
    boot_rc: int,
    help_rc: int,
    status_rc: int,
    identity_rc: int,
    zones: dict[str, bool],
    renderer: str,
) -> str:
    if boot_rc != 0 or help_rc != 0 or status_rc != 0 or identity_rc != 0:
        return "BLOCKED_SHELL_NOT_IMPLEMENTED"
    if zones.get("all_required_zones"):
        if renderer == "rich":
            return "PASS_RICH_OPERATOR_SHELL"
        return "WARN_PLAIN_FALLBACK"
    return "WARN_COMPACT_OPERATOR_SHELL"


def build_cases() -> list[OrganCase]:
    return [
        OrganCase("INQUISITION_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/INQUISITION_AGENT/TOOLS/inquisition_agent_runner.py", "base"),
        OrganCase("MECHANICUS_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/TOOLS/mechanicus_agent_runner.py", "base"),
        OrganCase("ADMINISTRATUM_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py", "administratum"),
        OrganCase("ASTRONOMICON_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ASTRONOMICON_AGENT/TOOLS/astronomicon_agent_runner.py", "base"),
        OrganCase("STRATEGIUM_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/STRATEGIUM_AGENT/TOOLS/strategium_agent_runner.py", "base"),
        OrganCase("OFFICIO_AGENTIS_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py", "officio"),
        OrganCase("SCHOLA_IMPERIALIS_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/SCHOLA_IMPERIALIS_AGENT/TOOLS/schola_imperialis_agent_runner.py", "base"),
        OrganCase("DOCTRINARIUM_AGENT", "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/DOCTRINARIUM_AGENT/TOOLS/doctrinarium_agent_runner.py", "base"),
    ]


def command_sets(case: OrganCase, report_dir: Path) -> dict[str, Any]:
    py = sys.executable
    if case.kind == "base":
        return {
            "boot": {"cmd": [py, case.runner, "shell"], "stdin": "exit\n"},
            "once_help": {"cmd": [py, case.runner, "shell", "--once", "help"]},
            "once_status": {"cmd": [py, case.runner, "shell", "--once", "status"]},
            "once_identity": {"cmd": [py, case.runner, "shell", "--once", "identity"]},
            "status": {"cmd": [py, case.runner, "status"]},
        }
    if case.kind == "administratum":
        return {
            "boot": {"cmd": [py, case.runner, "--rich", "shell"], "stdin": "/exit\n"},
            "once_help": {"cmd": [py, case.runner, "--rich", "shell", "--once", "/help"]},
            "once_status": {"cmd": [py, case.runner, "--rich", "shell", "--once", "/status"]},
            "once_identity": {"cmd": [py, case.runner, "--rich", "shell", "--once", "/identity"]},
            "status": {"cmd": [py, case.runner, "--rich", "status"]},
        }

    commands_file = report_dir / f"{case.organ.lower()}_shell_commands.txt"
    commands_file.write_text("/help\n/exit\n", encoding="utf-8")
    return {
        "boot": {
            "cmd": [
                py,
                case.runner,
                "shell",
                "--commands-file",
                str(commands_file),
                "--non-interactive",
            ]
        },
        "once_help": {"cmd": [py, case.runner, "shell", "--once", "/help", "--non-interactive"]},
        "once_status": {"cmd": [py, case.runner, "shell", "--once", "/status", "--non-interactive"]},
        "once_identity": {"cmd": [py, case.runner, "shell", "--once", "/identity", "--non-interactive"]},
        "status": {"cmd": [py, case.runner, "status"]},
    }


def write_matrix_md(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Eight Organ Operator Shell Matrix",
        "",
        "| Organ | Help RC | Status RC | Identity RC | Zones | Renderer | Visual Status |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        zones = row["zone_proof"]
        zone_label = "PASS" if zones.get("all_required_zones") else "COMPACT"
        lines.append(
            f"| {row['organ']} | {row['help_rc']} | {row['status_rc']} | {row['identity_rc']} | {zone_label} | {row['renderer']} | {row['visual_status']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_register_md(path: Path, register: dict[str, list[dict[str, Any]]]) -> None:
    lines = [
        "# WARN ERROR BLOCKER Register",
        "",
        f"- WARN: `{len(register['WARN'])}`",
        f"- ERROR: `{len(register['ERROR'])}`",
        f"- BLOCKER: `{len(register['BLOCKER'])}`",
        "",
    ]
    for level in ("WARN", "ERROR", "BLOCKER"):
        lines.append(f"## {level}")
        if not register[level]:
            lines.append("- none")
        else:
            for item in register[level]:
                lines.append(f"- {item['organ']}: {item['reason']} ({item.get('ref', 'n/a')})")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect operator-shell evidence for eight organs.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    report_dir = ensure_abs(Path(args.report_dir), repo_root)
    log_dir = report_dir / "SWEEP_LOGS"
    transcript_dir = report_dir / "SHELL_TRANSCRIPTS"
    renderer_dir = report_dir / "RENDERER_DIAGNOSTICS"
    officio_runtime = report_dir / "OFFICIO_RUNTIME"
    organ_runtime = report_dir / "ORGAN_RUNTIME"

    for p in (report_dir, log_dir, transcript_dir, renderer_dir, officio_runtime, organ_runtime):
        p.mkdir(parents=True, exist_ok=True)

    env_base = os.environ.copy()
    env_base["IMPERIUM_ORGAN_RUNTIME_ROOT"] = str(organ_runtime)

    matrix_rows: list[dict[str, Any]] = []
    register: dict[str, list[dict[str, Any]]] = {"WARN": [], "ERROR": [], "BLOCKER": []}

    for case in build_cases():
        commands = command_sets(case, report_dir)
        env = dict(env_base)
        if case.kind == "officio":
            env["OFFICIO_RUNTIME_ROOT"] = str(officio_runtime)

        boot = run_command(
            commands["boot"]["cmd"],
            repo_root,
            log_dir / f"{case.organ.lower()}__shell_boot.json",
            env,
            commands["boot"].get("stdin"),
        )
        once_help = run_command(
            commands["once_help"]["cmd"],
            repo_root,
            log_dir / f"{case.organ.lower()}__shell_once_help.json",
            env,
        )
        once_status = run_command(
            commands["once_status"]["cmd"],
            repo_root,
            log_dir / f"{case.organ.lower()}__shell_once_status.json",
            env,
        )
        once_identity = run_command(
            commands["once_identity"]["cmd"],
            repo_root,
            log_dir / f"{case.organ.lower()}__shell_once_identity.json",
            env,
        )
        status_cmd = run_command(
            commands["status"]["cmd"],
            repo_root,
            log_dir / f"{case.organ.lower()}__status.json",
            env,
        )

        (transcript_dir / f"{case.organ}_shell_operator_boot.txt").write_text(boot["stdout"] + "\n" + boot["stderr"], encoding="utf-8")
        (transcript_dir / f"{case.organ}_shell_once_help.txt").write_text(once_help["stdout"] + "\n" + once_help["stderr"], encoding="utf-8")
        (transcript_dir / f"{case.organ}_shell_once_status.txt").write_text(once_status["stdout"] + "\n" + once_status["stderr"], encoding="utf-8")
        (transcript_dir / f"{case.organ}_shell_once_identity.txt").write_text(once_identity["stdout"] + "\n" + once_identity["stderr"], encoding="utf-8")

        zones = operator_zone_proof(boot["stdout"])

        officio_renderer_diag_path = None
        if case.kind == "officio":
            labels = parse_labeled_paths(once_help["stdout"])
            officio_renderer_diag_path = labels.get("RENDERER_DIAGNOSTIC")

        renderer, rich_available, status_payload = infer_renderer(
            status_stdout=status_cmd["stdout"],
            shell_stdout=boot["stdout"],
            officio_renderer_diag_path=officio_renderer_diag_path,
        )

        visual_status = visual_status_for(
            boot_rc=int(boot["returncode"]),
            help_rc=int(once_help["returncode"]),
            status_rc=int(once_status["returncode"]),
            identity_rc=int(once_identity["returncode"]),
            zones=zones,
            renderer=renderer,
        )

        diag_payload = {
            "schema_version": "OPERATOR_SHELL_RENDERER_DIAGNOSTIC_V0_1",
            "task_id": args.task_id,
            "organ": case.organ,
            "runner": case.runner,
            "timestamp_utc": utc_now(),
            "renderer": renderer,
            "rich_renderer_available": rich_available,
            "zone_proof": zones,
            "help_rc": int(once_help["returncode"]),
            "status_rc": int(once_status["returncode"]),
            "identity_rc": int(once_identity["returncode"]),
            "boot_rc": int(boot["returncode"]),
            "visual_status": visual_status,
            "status_payload_excerpt": status_payload,
            "officio_renderer_diagnostic_source": officio_renderer_diag_path,
        }
        diag_path = renderer_dir / f"{case.organ}_renderer_diagnostic.json"
        diag_path.write_text(json.dumps(diag_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

        row = {
            "organ": case.organ,
            "runner": case.runner,
            "help_rc": int(once_help["returncode"]),
            "status_rc": int(once_status["returncode"]),
            "identity_rc": int(once_identity["returncode"]),
            "zone_proof": zones,
            "renderer": renderer,
            "renderer_diagnostic": str(diag_path),
            "visual_status": visual_status,
            "transcripts": {
                "boot": str(transcript_dir / f"{case.organ}_shell_operator_boot.txt"),
                "help": str(transcript_dir / f"{case.organ}_shell_once_help.txt"),
                "status": str(transcript_dir / f"{case.organ}_shell_once_status.txt"),
                "identity": str(transcript_dir / f"{case.organ}_shell_once_identity.txt"),
            },
            "logs": {
                "boot": str(log_dir / f"{case.organ.lower()}__shell_boot.json"),
                "help": str(log_dir / f"{case.organ.lower()}__shell_once_help.json"),
                "status": str(log_dir / f"{case.organ.lower()}__shell_once_status.json"),
                "identity": str(log_dir / f"{case.organ.lower()}__shell_once_identity.json"),
                "status_cmd": str(log_dir / f"{case.organ.lower()}__status.json"),
            },
        }
        matrix_rows.append(row)

        if visual_status == "BLOCKED_SHELL_NOT_IMPLEMENTED":
            register["BLOCKER"].append({"organ": case.organ, "reason": visual_status, "ref": str(diag_path)})
        elif visual_status != "PASS_RICH_OPERATOR_SHELL":
            register["WARN"].append({"organ": case.organ, "reason": visual_status, "ref": str(diag_path)})

        if row["help_rc"] != 0 or row["status_rc"] != 0 or row["identity_rc"] != 0:
            register["ERROR"].append(
                {
                    "organ": case.organ,
                    "reason": f"non_zero_rc help={row['help_rc']} status={row['status_rc']} identity={row['identity_rc']}",
                    "ref": str(diag_path),
                }
            )

    matrix_json = {
        "schema_version": "EIGHT_ORGAN_OPERATOR_SHELL_MATRIX_V0_1",
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "organs": matrix_rows,
        "counts": {
            "organs": len(matrix_rows),
            "warn": len(register["WARN"]),
            "error": len(register["ERROR"]),
            "blocker": len(register["BLOCKER"]),
        },
    }

    (report_dir / "eight_organ_operator_shell_matrix.json").write_text(
        json.dumps(matrix_json, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    write_matrix_md(report_dir / "EIGHT_ORGAN_OPERATOR_SHELL_MATRIX.md", matrix_rows)

    register_json = {
        "schema_version": "WARN_ERROR_BLOCKER_REGISTER_V0_1",
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "register": register,
        "counts": {
            "warn": len(register["WARN"]),
            "error": len(register["ERROR"]),
            "blocker": len(register["BLOCKER"]),
        },
    }
    (report_dir / "WARN_ERROR_BLOCKER_REGISTER.json").write_text(
        json.dumps(register_json, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    write_register_md(report_dir / "WARN_ERROR_BLOCKER_REGISTER.md", register)

    verdict = "PASS_RICH_OPERATOR_SHELL_8_ORGANS"
    if register["BLOCKER"]:
        verdict = "BLOCKED_SHELL_NOT_IMPLEMENTED"
    elif register["ERROR"] or register["WARN"]:
        verdict = "PASS_OPERATOR_SHELL_WITH_WARNINGS"

    print(f"MATRIX_JSON: {report_dir / 'eight_organ_operator_shell_matrix.json'}")
    print(f"MATRIX_MD: {report_dir / 'EIGHT_ORGAN_OPERATOR_SHELL_MATRIX.md'}")
    print(f"REGISTER_JSON: {report_dir / 'WARN_ERROR_BLOCKER_REGISTER.json'}")
    print(f"REGISTER_MD: {report_dir / 'WARN_ERROR_BLOCKER_REGISTER.md'}")
    print(f"VERDICT: {verdict}")

    return 0 if verdict != "BLOCKED_SHELL_NOT_IMPLEMENTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
