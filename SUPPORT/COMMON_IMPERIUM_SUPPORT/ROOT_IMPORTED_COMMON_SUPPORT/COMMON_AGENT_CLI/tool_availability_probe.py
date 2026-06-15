from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_AVAILABLE_PC = "AVAILABLE_PC"
STATUS_AVAILABLE_VM2 = "AVAILABLE_VM2"
STATUS_AVAILABLE_BOTH = "AVAILABLE_BOTH"
STATUS_KNOWN_NOT_INSTALLED = "KNOWN_NOT_INSTALLED"
STATUS_NOT_FOUND_ON_PC = "NOT_FOUND_ON_PC"
STATUS_NOT_FOUND_ON_VM2 = "NOT_FOUND_ON_VM2"
STATUS_PC_SNAPSHOT_MISSING = "PC_SNAPSHOT_MISSING"
STATUS_VERSION_UNKNOWN = "VERSION_UNKNOWN"
STATUS_BLOCKED_NOT_ADMITTED = "BLOCKED_NOT_ADMITTED"

ALLOWED_STATUSES = {
    STATUS_AVAILABLE_PC,
    STATUS_AVAILABLE_VM2,
    STATUS_AVAILABLE_BOTH,
    STATUS_KNOWN_NOT_INSTALLED,
    STATUS_NOT_FOUND_ON_PC,
    STATUS_NOT_FOUND_ON_VM2,
    STATUS_PC_SNAPSHOT_MISSING,
    STATUS_VERSION_UNKNOWN,
    STATUS_BLOCKED_NOT_ADMITTED,
}


@dataclass
class ProbeCommand:
    tool_id: str
    command: list[str]
    fallback: list[str] | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def first_non_empty_line(text: str) -> str | None:
    for line in text.splitlines():
        candidate = line.strip()
        if candidate:
            return candidate
    return None


def parse_version(stdout: str, stderr: str) -> str | None:
    return first_non_empty_line(stdout) or first_non_empty_line(stderr)


def normalized_tool_key(tool_id: str) -> str:
    return tool_id.strip().lower().replace("_", "-")


def candidate_aliases(tool_id: str) -> set[str]:
    key = normalized_tool_key(tool_id)
    aliases = {key}
    if key == "ripgrep":
        aliases.add("rg")
    if key == "pip-audit":
        aliases.add("pip_audit")
    if key == "jsonschema":
        aliases.add("python3-jsonschema")
    return aliases


def canonical_agent_name(raw: str) -> str:
    token = raw.strip().upper()
    if token in {"ALL", "SANCTUM_LATER", "CUSTODES_LATER"}:
        return token
    if token.endswith("_AGENT"):
        return token
    mapping = {
        "INQUISITION": "INQUISITION_AGENT",
        "MECHANICUS": "MECHANICUS_AGENT",
        "ADMINISTRATUM": "ADMINISTRATUM_AGENT",
        "ASTRONOMICON": "ASTRONOMICON_AGENT",
        "STRATEGIUM": "STRATEGIUM_AGENT",
        "OFFICIO_AGENTIS": "OFFICIO_AGENTIS_AGENT",
        "SCHOLA_IMPERIALIS": "SCHOLA_IMPERIALIS_AGENT",
        "DOCTRINARIUM": "DOCTRINARIUM_AGENT",
    }
    return mapping.get(token, token)


def probe_commands() -> dict[str, ProbeCommand]:
    return {
        "git": ProbeCommand("git", ["git", "--version"]),
        "ripgrep": ProbeCommand("ripgrep", ["rg", "--version"]),
        "ruff": ProbeCommand("ruff", ["ruff", "--version"]),
        "pytest": ProbeCommand("pytest", ["pytest", "--version"], fallback=["python3", "-m", "pytest", "--version"]),
        "jsonschema": ProbeCommand("jsonschema", ["python3", "-m", "jsonschema", "--version"]),
        "jq": ProbeCommand("jq", ["jq", "--version"]),
        "yq": ProbeCommand("yq", ["yq", "--version"]),
        "gitleaks": ProbeCommand("gitleaks", ["gitleaks", "version"]),
        "semgrep": ProbeCommand("semgrep", ["semgrep", "--version"]),
        "bandit": ProbeCommand("bandit", ["bandit", "--version"]),
        "pip-audit": ProbeCommand("pip-audit", ["pip-audit", "--version"]),
        "uv": ProbeCommand("uv", ["uv", "--version"]),
        "duckdb": ProbeCommand("duckdb", ["duckdb", "--version"]),
        "node": ProbeCommand("node", ["node", "--version"]),
        "npm": ProbeCommand("npm", ["npm", "--version"]),
        "playwright": ProbeCommand("playwright", ["npx", "--no-install", "playwright", "--version"]),
    }


def run_probe(cmd: ProbeCommand, timeout_seconds: int) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    commands = [cmd.command]
    if cmd.fallback:
        commands.append(cmd.fallback)

    for attempt in commands:
        try:
            proc = subprocess.run(
                attempt,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            attempts.append(
                {
                    "command": attempt,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "timeout": False,
                }
            )
            if proc.returncode == 0:
                version = parse_version(proc.stdout, proc.stderr)
                return {
                    "tool_id": cmd.tool_id,
                    "vm2_status": STATUS_AVAILABLE_VM2,
                    "version_vm2": version,
                    "version_vm2_status": STATUS_VERSION_UNKNOWN if version is None else STATUS_AVAILABLE_VM2,
                    "command_used": attempt,
                    "exit_code": 0,
                    "stdout_excerpt": first_non_empty_line(proc.stdout),
                    "stderr_excerpt": first_non_empty_line(proc.stderr),
                    "attempts": attempts,
                }
        except FileNotFoundError:
            attempts.append(
                {
                    "command": attempt,
                    "returncode": 127,
                    "stdout": "",
                    "stderr": "command_not_found",
                    "timeout": False,
                }
            )
        except subprocess.TimeoutExpired as err:
            attempts.append(
                {
                    "command": attempt,
                    "returncode": 124,
                    "stdout": (err.stdout or "") if isinstance(err.stdout, str) else "",
                    "stderr": (err.stderr or "") if isinstance(err.stderr, str) else "",
                    "timeout": True,
                }
            )

    last = attempts[-1] if attempts else {"command": cmd.command, "returncode": 127, "stdout": "", "stderr": "", "timeout": False}
    return {
        "tool_id": cmd.tool_id,
        "vm2_status": STATUS_NOT_FOUND_ON_VM2,
        "version_vm2": None,
        "version_vm2_status": STATUS_VERSION_UNKNOWN,
        "command_used": last["command"],
        "exit_code": int(last["returncode"]),
        "stdout_excerpt": first_non_empty_line(str(last.get("stdout", ""))),
        "stderr_excerpt": first_non_empty_line(str(last.get("stderr", ""))),
        "attempts": attempts,
    }


def parse_pc_snapshot(pc_snapshot_path: Path | None) -> tuple[dict[str, dict[str, Any]], list[str]]:
    warnings: list[str] = []
    if pc_snapshot_path is None:
        return {}, warnings
    if not pc_snapshot_path.exists():
        warnings.append("pc_snapshot_missing")
        return {}, warnings
    raw = pc_snapshot_path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    results = data.get("results", [])
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(results, list):
        warnings.append("pc_snapshot_results_invalid")
        return index, warnings
    for item in results:
        if not isinstance(item, dict):
            continue
        key = normalized_tool_key(str(item.get("tool_id", "")))
        if not key:
            continue
        index[key] = item
    return index, warnings


def pc_status_for_tool(tool_id: str, pc_index: dict[str, dict[str, Any]], pc_snapshot_present: bool) -> tuple[str, str | None, dict[str, Any] | None]:
    if not pc_snapshot_present:
        return STATUS_PC_SNAPSHOT_MISSING, None, None
    matched: dict[str, Any] | None = None
    for alias in candidate_aliases(tool_id):
        item = pc_index.get(alias)
        if item is not None:
            matched = item
            break
    if matched is None:
        return STATUS_NOT_FOUND_ON_PC, None, None

    found = False
    if isinstance(matched.get("found_on_pc"), bool):
        found = bool(matched["found_on_pc"])
    elif isinstance(matched.get("exit_code"), int):
        found = int(matched["exit_code"]) == 0
    else:
        status_text = str(matched.get("status", "")).upper()
        found = status_text.startswith("AVAILABLE") or status_text.startswith("FOUND")

    version_pc = parse_version(str(matched.get("stdout", "")), str(matched.get("stderr", "")))
    return (STATUS_AVAILABLE_PC if found else STATUS_NOT_FOUND_ON_PC), version_pc, matched


def combined_status(pc_status: str, vm2_status: str) -> str:
    if pc_status == STATUS_AVAILABLE_PC and vm2_status == STATUS_AVAILABLE_VM2:
        return STATUS_AVAILABLE_BOTH
    if pc_status == STATUS_AVAILABLE_PC and vm2_status != STATUS_AVAILABLE_VM2:
        return STATUS_AVAILABLE_PC
    if vm2_status == STATUS_AVAILABLE_VM2 and pc_status != STATUS_AVAILABLE_PC:
        return STATUS_AVAILABLE_VM2
    if pc_status == STATUS_PC_SNAPSHOT_MISSING and vm2_status == STATUS_NOT_FOUND_ON_VM2:
        return STATUS_KNOWN_NOT_INSTALLED
    if pc_status == STATUS_NOT_FOUND_ON_PC and vm2_status == STATUS_NOT_FOUND_ON_VM2:
        return STATUS_KNOWN_NOT_INSTALLED
    if pc_status == STATUS_PC_SNAPSHOT_MISSING:
        return STATUS_PC_SNAPSHOT_MISSING
    return STATUS_KNOWN_NOT_INSTALLED


def render_markdown(rows: list[dict[str, Any]], warnings: list[str], task_id: str) -> str:
    lines = [
        "# TOOL AVAILABILITY REPORT",
        "",
        f"- task_id: {task_id}",
        f"- generated_at_utc: {utc_now()}",
        "",
        "| tool_id | pc_status | vm2_status | combined_status | version_pc | version_vm2 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {tool_id} | {pc_status} | {vm2_status} | {combined_status} | {version_pc} | {version_vm2} |".format(
                tool_id=row["tool_id"],
                pc_status=row["pc_status"],
                vm2_status=row["vm2_status"],
                combined_status=row["combined_status"],
                version_pc=row.get("version_pc") or "n/a",
                version_vm2=row.get("version_vm2") or "n/a",
            )
        )
    lines.append("")
    lines.append("## Warnings")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe VM2 tool availability and merge optional PC snapshot.")
    parser.add_argument("--task-id", default="TASK-UNKNOWN")
    parser.add_argument("--candidates-json", required=True)
    parser.add_argument("--pc-probe-json", default=None)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--logs-dir", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args(argv)

    candidates_path = Path(args.candidates_json)
    candidates_data = json.loads(candidates_path.read_text(encoding="utf-8"))
    tools = candidates_data.get("tools", [])
    if not isinstance(tools, list):
        raise SystemExit("Invalid candidates JSON: .tools must be an array")

    pc_snapshot_path = Path(args.pc_probe_json) if args.pc_probe_json else None
    pc_snapshot_present = bool(pc_snapshot_path and pc_snapshot_path.exists())
    pc_index, warnings = parse_pc_snapshot(pc_snapshot_path)

    command_map = probe_commands()
    rows: list[dict[str, Any]] = []
    vm2_missing = 0
    pc_missing = 0

    logs_dir: Path | None = Path(args.logs_dir) if args.logs_dir else None
    if logs_dir is not None:
        logs_dir.mkdir(parents=True, exist_ok=True)

    for tool in tools:
        if not isinstance(tool, dict):
            continue
        tool_id = str(tool.get("tool_id", "")).strip()
        if not tool_id:
            continue
        normalized = normalized_tool_key(tool_id)
        command = command_map.get(normalized)
        if command is None:
            probe = {
                "tool_id": tool_id,
                "vm2_status": STATUS_BLOCKED_NOT_ADMITTED,
                "version_vm2": None,
                "version_vm2_status": STATUS_VERSION_UNKNOWN,
                "command_used": [],
                "exit_code": 127,
                "stdout_excerpt": None,
                "stderr_excerpt": "tool_id_not_in_probe_registry",
                "attempts": [],
            }
        else:
            probe = run_probe(command, timeout_seconds=max(1, int(args.timeout_seconds)))

        pc_status, version_pc, pc_raw = pc_status_for_tool(normalized, pc_index, pc_snapshot_present)
        combined = combined_status(pc_status=pc_status, vm2_status=str(probe["vm2_status"]))
        if pc_status == STATUS_NOT_FOUND_ON_PC:
            pc_missing += 1
        if probe["vm2_status"] == STATUS_NOT_FOUND_ON_VM2:
            vm2_missing += 1

        row = {
            "tool_id": normalized,
            "display_name": str(tool.get("tool_id", normalized)),
            "owner_organ": canonical_agent_name(str(tool.get("owner_organ", "MECHANICUS"))),
            "consumer_organs": [canonical_agent_name(str(x)) for x in tool.get("consumer_organs", []) if isinstance(x, (str, int, float))],
            "purpose": str(tool.get("purpose", "")).strip(),
            "pc_status": pc_status,
            "vm2_status": str(probe["vm2_status"]),
            "combined_status": combined,
            "version_pc": version_pc,
            "version_vm2": probe["version_vm2"],
            "version_pc_status": STATUS_VERSION_UNKNOWN if version_pc is None else STATUS_AVAILABLE_PC,
            "version_vm2_status": str(probe["version_vm2_status"]),
            "command_used": " ".join(shlex.quote(part) for part in probe["command_used"]),
            "vm2_exit_code": int(probe["exit_code"]),
            "vm2_stdout_excerpt": probe["stdout_excerpt"],
            "vm2_stderr_excerpt": probe["stderr_excerpt"],
            "pc_probe_raw": pc_raw,
            "evidence_required": [str(x) for x in tool.get("evidence_required", []) if isinstance(x, (str, int, float))],
        }
        rows.append(row)

        if logs_dir is not None:
            write_json(logs_dir / f"{normalized}_probe_attempts.json", {"tool_id": normalized, "attempts": probe["attempts"]})

    report = {
        "schema_version": "MECHANICUS_TOOL_AVAILABILITY_REPORT_V0_1",
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "candidate_source": str(candidates_path),
        "pc_snapshot_path": str(pc_snapshot_path) if pc_snapshot_path else None,
        "pc_snapshot_present": pc_snapshot_present,
        "warnings": warnings,
        "tools": rows,
        "counts": {
            "tools_total": len(rows),
            "available_both": sum(1 for row in rows if row["combined_status"] == STATUS_AVAILABLE_BOTH),
            "available_vm2_only": sum(1 for row in rows if row["combined_status"] == STATUS_AVAILABLE_VM2),
            "available_pc_only": sum(1 for row in rows if row["combined_status"] == STATUS_AVAILABLE_PC),
            "known_not_installed": sum(1 for row in rows if row["combined_status"] == STATUS_KNOWN_NOT_INSTALLED),
            "pc_not_found": pc_missing,
            "vm2_not_found": vm2_missing,
        },
        "allowed_statuses": sorted(ALLOWED_STATUSES),
    }

    out_json = Path(args.out_json)
    write_json(out_json, report)
    if args.out_md:
        out_md = Path(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(rows, warnings, args.task_id), encoding="utf-8")

    print(f"TOOL_AVAILABILITY_JSON: {out_json}")
    if args.out_md:
        print(f"TOOL_AVAILABILITY_MD: {Path(args.out_md)}")
    if logs_dir is not None:
        print(f"TOOL_AVAILABILITY_LOGS_DIR: {logs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
