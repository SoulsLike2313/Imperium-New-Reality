from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    Columns = None  # type: ignore[assignment]
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]


BASE_COMMANDS: dict[str, dict[str, str]] = {
    "status": {"description": "Show organ health, git truth, and mode", "action_type": "read_only"},
    "identity": {"description": "Show organ identity summary", "action_type": "read_only"},
    "gates": {"description": "Show organ gate catalog preview", "action_type": "read_only"},
    "query": {"description": "Run organ query tool in bounded mode", "action_type": "read_only"},
    "evidence": {"description": "Show evidence refs and report files", "action_type": "read_only"},
    "help": {"description": "Show command reference", "action_type": "read_only"},
    "clear": {"description": "Clear shell frame", "action_type": "shell_control"},
    "exit": {"description": "Exit shell", "action_type": "shell_control"},
}


@dataclass
class ShellResult:
    status: str
    summary: str
    payload: dict[str, Any] | list[Any] | str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "summary": self.summary, "payload": self.payload}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_status(value: str) -> str:
    upper = value.strip().upper()
    if upper in {"OK", "PASS", "READY"}:
        return "OK"
    if upper in {"WARN", "WARNING", "PARTIAL"}:
        return "WARN"
    if upper in {"BLOCK", "BLOCKED", "FAIL", "FAILED", "ERROR"}:
        return "BLOCK"
    return "WARN"


def safe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def safe_read_text(path: Path, max_lines: int = 28) -> str:
    if not path.exists() or not path.is_file():
        return f"MISSING: {path}"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    compact = [line.rstrip() for line in lines if line.strip()]
    if not compact:
        return f"EMPTY: {path}"
    if len(compact) > max_lines:
        clipped = compact[:max_lines]
        clipped.append("... [truncated]")
        compact = clipped
    return "\n".join(compact)


def clip_text(text: str, max_chars: int = 3200) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 16] + "\n...[truncated]"


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / ".git").exists():
            return parent
    return start


class OrganShell:
    def __init__(self, config: Mapping[str, Any], args: argparse.Namespace) -> None:
        self.config = config
        self.args = args
        self.organ_id = str(config.get("organ_id", "UNKNOWN"))
        self.organ_slug = str(config.get("organ_slug", self.organ_id.lower()))
        self.task_id = str(args.task_id or config.get("task_id_default", "TASK-UNKNOWN"))
        self.shell_version = str(config.get("shell_version", "v1.0.0"))
        self.mission_focus = str(config.get("mission_focus", "Bounded shell execution"))
        self.theme = dict(config.get("theme", {}))

        self.organ_root = Path(str(config.get("organ_root", "."))).resolve()
        self.report_root = Path(str(config.get("report_root", "."))).resolve()
        self.query_script = Path(str(config.get("query_script", ""))).resolve()
        self.specific_commands = dict(config.get("specific_commands", {}))

        self.repo_root = find_repo_root(self.organ_root)
        self.newgen_root = self.repo_root / "IMPERIUM_NEW_GENERATION"

        self.identity_path = self.organ_root / "IDENTITY" / "organ_identity_v0_1.md"
        self.contract_path = self.organ_root / "CONTRACTS" / "servitor_contract_v0_1.md"
        self.gate_catalog_path = self.organ_root / "GATES" / "organ_gate_catalog_v0_1.json"
        self.state_path = self.organ_root / "STATE" / "current_state_v0_1.json"

        self.gate_catalog = safe_load_json(self.gate_catalog_path)
        self.state = safe_load_json(self.state_path)

        self.allowlist: dict[str, dict[str, str]] = {}
        self.allowlist.update(BASE_COMMANDS)
        for name, description in self.specific_commands.items():
            self.allowlist[str(name)] = {"description": str(description), "action_type": "read_only"}

        self.counters = {"OK": 0, "WARN": 0, "BLOCK": 0}
        self.history: list[dict[str, Any]] = []
        self.latest_summary = "Shell initialized."
        self.latest_payload: dict[str, Any] | list[Any] | str | None = None
        self.latest_command = "boot"

        self.console = Console(record=True, soft_wrap=True) if HAVE_RICH and not args.plain_json else None

    def _git_value(self, *command: str) -> str:
        try:
            proc = subprocess.run(
                list(command),
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=8,
                check=False,
            )
        except Exception as exc:
            return f"error:{exc}"
        if proc.returncode != 0:
            return f"error:{clip_text((proc.stderr or '').strip(), 160)}"
        return (proc.stdout or "").strip()

    def _run_json_script(self, command: list[str], timeout_sec: float = 24.0) -> dict[str, Any]:
        started = utc_now()
        try:
            proc = subprocess.run(
                command,
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "timed_out": True,
                "exit_code": 124,
                "stdout": clip_text(str(exc.stdout or "")),
                "stderr": clip_text(str(exc.stderr or "")),
                "parsed_json": None,
                "parse_error": "TIMEOUT",
                "command": command,
            }
        except Exception as exc:
            return {
                "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "timed_out": False,
                "exit_code": 2,
                "stdout": "",
                "stderr": str(exc),
                "parsed_json": None,
                "parse_error": "EXEC_ERROR",
                "command": command,
            }

        parsed_json: dict[str, Any] | list[Any] | None = None
        parse_error: str | None = None
        stdout = proc.stdout or ""
        stripped = stdout.strip()
        if stripped:
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, (dict, list)):
                    parsed_json = parsed
                else:
                    parse_error = "JSON_ROOT_NOT_OBJECT_OR_ARRAY"
            except json.JSONDecodeError as exc:
                parse_error = f"JSON_DECODE_ERROR: {exc.msg}"
        else:
            parse_error = "EMPTY_STDOUT"

        return {
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
            "timed_out": False,
            "exit_code": int(proc.returncode),
            "stdout": clip_text(stdout),
            "stderr": clip_text(proc.stderr or ""),
            "parsed_json": parsed_json,
            "parse_error": parse_error,
            "command": command,
        }

    def _collect_report_files(self) -> list[str]:
        if not self.report_root.exists():
            return []
        files = sorted(
            [
                p
                for p in self.report_root.rglob("*")
                if p.is_file() and p.suffix.lower() in {".json", ".md", ".txt", ".html"}
            ],
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        return [str(path.relative_to(self.repo_root)).replace("\\", "/") for path in files[:12]]

    def _command_status(self, _: str) -> ShellResult:
        git_head = self._git_value("git", "rev-parse", "--short", "HEAD")
        git_branch = self._git_value("git", "branch", "--show-current")
        git_dirty = self._git_value("git", "status", "--short")
        dirty_flag = "clean" if not git_dirty else "dirty"
        payload = {
            "organ_id": self.organ_id,
            "task_id": self.task_id,
            "mode": self._run_mode(),
            "git_head": git_head,
            "git_branch": git_branch,
            "worktree": dirty_flag,
            "responsibility": self.state.get("responsibility", ""),
            "rich_available": HAVE_RICH,
            "generated_at_utc": utc_now(),
        }
        summary = f"status={payload['worktree']} head={git_head} branch={git_branch}"
        status = "OK"
        return ShellResult(status=status, summary=summary, payload=payload)

    def _command_identity(self, _: str) -> ShellResult:
        payload = {
            "identity_path": str(self.identity_path),
            "content_excerpt": safe_read_text(self.identity_path, max_lines=18),
        }
        return ShellResult(status="OK", summary="Identity loaded.", payload=payload)

    def _command_gates(self, _: str) -> ShellResult:
        gates = self.gate_catalog.get("gates", [])
        gate_rows: list[dict[str, str]] = []
        if isinstance(gates, list):
            for gate in gates[:12]:
                if isinstance(gate, dict):
                    gate_rows.append(
                        {
                            "gate_id": str(gate.get("gate_id", "UNKNOWN")),
                            "severity": str(gate.get("severity", "UNKNOWN")),
                            "expected_verdict": str(gate.get("expected_verdict", "n/a")),
                        }
                    )
        payload = {"gate_catalog_path": str(self.gate_catalog_path), "gates": gate_rows}
        return ShellResult(status="OK", summary=f"Gates listed: {len(gate_rows)}", payload=payload)

    def _command_query(self, args: str) -> ShellResult:
        if not self.query_script.exists():
            return ShellResult(status="BLOCK", summary="Query script missing.", payload={"path": str(self.query_script)})
        command = [sys.executable, str(self.query_script), "--task-id", self.task_id]
        if args.strip():
            command.extend(["--question", args.strip()])
        else:
            command.append("--sample")
        result = self._run_json_script(command)
        payload = {
            "query_script": str(self.query_script),
            "exit_code": result.get("exit_code"),
            "parse_error": result.get("parse_error"),
            "parsed_json": result.get("parsed_json"),
            "stderr": result.get("stderr"),
        }
        verdict = None
        parsed = result.get("parsed_json")
        if isinstance(parsed, dict):
            raw_verdict = parsed.get("verdict")
            if isinstance(raw_verdict, str):
                verdict = raw_verdict
        status = "OK" if int(result.get("exit_code", 1)) == 0 else "BLOCK"
        if verdict in {"BLOCK", "OWNER_VERDICT_NEEDED"} and status != "BLOCK":
            status = "WARN"
        summary = f"query_exit={result.get('exit_code')} verdict={verdict or 'UNKNOWN'}"
        return ShellResult(status=status, summary=summary, payload=payload)

    def _command_evidence(self, _: str) -> ShellResult:
        refs = self.state.get("evidence_refs", [])
        evidence_refs = [str(item) for item in refs] if isinstance(refs, list) else []
        payload = {
            "report_root": str(self.report_root),
            "evidence_refs": evidence_refs,
            "recent_report_files": self._collect_report_files(),
        }
        status = "OK" if evidence_refs else "WARN"
        summary = f"evidence_refs={len(evidence_refs)} recent_files={len(payload['recent_report_files'])}"
        return ShellResult(status=status, summary=summary, payload=payload)

    def _command_help(self, _: str) -> ShellResult:
        rows = []
        for name in sorted(self.allowlist.keys()):
            entry = self.allowlist[name]
            rows.append(
                {
                    "name": name,
                    "description": entry.get("description", ""),
                    "action_type": entry.get("action_type", "read_only"),
                }
            )
        return ShellResult(status="OK", summary="Allowlisted commands listed.", payload={"commands": rows})

    def _command_laws(self, _: str) -> ShellResult:
        doctrine = safe_load_json(
            self.newgen_root
            / "DOCTRINARIUM"
            / "DECLARATIONS"
            / "METAOS_FOCUSING_DOCTRINE"
            / "metaos_focusing_doctrine_v0_1.json"
        )
        laws = doctrine.get("laws", [])
        gate_ids = []
        gates = self.gate_catalog.get("gates", [])
        if isinstance(gates, list):
            gate_ids = [str(item.get("gate_id", "")) for item in gates if isinstance(item, dict)]
        payload = {"doctrine_id": doctrine.get("doctrine_id"), "laws": laws, "gate_ids": gate_ids}
        return ShellResult(status="OK", summary=f"laws={len(laws) if isinstance(laws, list) else 0}", payload=payload)

    def _command_preflight(self, _: str) -> ShellResult:
        script = (
            self.newgen_root
            / "DOCTRINARIUM"
            / "GATE_SPINE"
            / "TOOLS"
            / "doctrinarium_preflight_v0_1.py"
        )
        if not script.exists():
            return ShellResult(status="BLOCK", summary="Preflight script missing.", payload={"path": str(script)})
        result = self._run_json_script([sys.executable, str(script), "--task-type", "visual_cockpit"], timeout_sec=25.0)
        parsed = result.get("parsed_json")
        status = "OK"
        if int(result.get("exit_code", 1)) != 0:
            status = "BLOCK"
        if isinstance(parsed, dict) and str(parsed.get("status", "")).upper() != "PASS":
            status = "WARN"
        summary = f"preflight_exit={result.get('exit_code')} status={parsed.get('status') if isinstance(parsed, dict) else 'UNKNOWN'}"
        payload = {
            "script": str(script),
            "exit_code": result.get("exit_code"),
            "parsed_json": parsed,
            "parse_error": result.get("parse_error"),
        }
        return ShellResult(status=status, summary=summary, payload=payload)

    def _command_role(self, _: str) -> ShellResult:
        role_contract = safe_load_json(
            self.newgen_root / "OFFICIO_AGENTIS" / "AGENT_BOOT" / "officio_role_contract_v0_1.json"
        )
        payload = {
            "role_id": role_contract.get("role_id"),
            "role_title": role_contract.get("role_title"),
            "required_verdict_pattern": role_contract.get("required_verdict_pattern"),
            "forbidden": role_contract.get("forbidden", []),
            "stop_conditions": role_contract.get("stop_conditions", []),
        }
        return ShellResult(status="OK", summary="Role contract loaded.", payload=payload)

    def _command_language(self, _: str) -> ShellResult:
        language_doc = (
            self.newgen_root
            / "OFFICIO_AGENTIS"
            / "AGENT_BOOT"
            / "owner_facing_language_contract_v0_1.md"
        )
        payload = {"path": str(language_doc), "content_excerpt": safe_read_text(language_doc, max_lines=20)}
        return ShellResult(status="OK", summary="Language contract loaded.", payload=payload)

    def _command_continuity(self, _: str) -> ShellResult:
        required = [
            "applicable_doctrinarium_gates.json",
            "officio_role_contract_ack.json",
            "taskpack_scope_ack.json",
            "organ_route_plan.json",
            "GATE_ACK.md",
        ]
        checks = []
        for name in required:
            target = self.report_root / name
            checks.append({"file": name, "exists": target.exists()})
        git_dirty = bool(self._git_value("git", "status", "--short"))
        payload = {"required_files": checks, "git_dirty": git_dirty}
        missing = [row["file"] for row in checks if not row["exists"]]
        if missing:
            return ShellResult(status="WARN", summary=f"missing continuity files: {', '.join(missing)}", payload=payload)
        return ShellResult(status="OK", summary="Continuity files present.", payload=payload)

    def _command_receipts(self, _: str) -> ShellResult:
        if not self.report_root.exists():
            return ShellResult(status="WARN", summary="Report root missing.", payload={"report_root": str(self.report_root)})
        files = sorted([p for p in self.report_root.glob("*.json") if p.is_file()])
        payload = {
            "report_root": str(self.report_root),
            "json_files": [str(path.name) for path in files],
            "count": len(files),
        }
        return ShellResult(status="OK" if files else "WARN", summary=f"receipt_files={len(files)}", payload=payload)

    def _command_route(self, _: str) -> ShellResult:
        route_path = self.report_root / "organ_route_plan.json"
        if route_path.exists():
            route_payload = safe_load_json(route_path)
            return ShellResult(status="OK", summary="Route plan loaded.", payload=route_payload)
        payload = {
            "task_id": self.task_id,
            "route": [
                "DOCTRINARIUM",
                "OFFICIO_AGENTIS",
                "ASTRONOMICON",
                "ADMINISTRATUM",
                "MECHANICUS",
                "INQUISITION",
            ],
        }
        return ShellResult(status="WARN", summary="Route plan file missing, fallback route shown.", payload=payload)

    def _command_stages(self, _: str) -> ShellResult:
        payload = {
            "task_id": self.task_id,
            "stages": [
                "admission_truth_check",
                "shell_standard_build",
                "six_organ_shell_apply",
                "smoke_and_scripted_validation",
                "receipt_and_closure",
            ],
        }
        return ShellResult(status="OK", summary="Stage template listed.", payload=payload)

    def _command_tools(self, _: str) -> ShellResult:
        registry_path = self.newgen_root / "MECHANICUS" / "TOOLS_REGISTRY" / "tool_capability_registry.json"
        registry = safe_load_json(registry_path)
        tools = registry.get("tools", [])
        payload = {
            "registry_path": str(registry_path),
            "tool_count": len(tools) if isinstance(tools, list) else 0,
            "tools": tools if isinstance(tools, list) else [],
        }
        status = "OK" if payload["tool_count"] > 0 else "WARN"
        return ShellResult(status=status, summary=f"tool_registry_count={payload['tool_count']}", payload=payload)

    def _command_capability(self, _: str) -> ShellResult:
        try:
            version = importlib.metadata.version("rich")
            payload = {"rich_available": True, "rich_version": version}
            return ShellResult(status="OK", summary=f"rich={version}", payload=payload)
        except Exception as exc:
            payload = {"rich_available": False, "error": str(exc)}
            return ShellResult(status="BLOCK", summary="Rich capability missing.", payload=payload)

    def _command_audit(self, _: str) -> ShellResult:
        checks = {
            "final_report": (self.report_root / "FINAL_REPORT.md").exists(),
            "closure_receipt": (self.report_root / "closure_receipt.json").exists(),
            "smoke_report": (self.report_root / "organ_shell_v1_smoke_report.json").exists(),
            "scripted_report": (self.report_root / "organ_shell_v1_scripted_test_report.json").exists(),
        }
        missing = [name for name, exists in checks.items() if not exists]
        status = "OK" if not missing else "WARN"
        payload = {"checks": checks, "missing": missing}
        summary = "audit ready" if not missing else f"audit missing: {', '.join(missing)}"
        return ShellResult(status=status, summary=summary, payload=payload)

    def _command_fakegreen(self, _: str) -> ShellResult:
        closure_path = self.report_root / "closure_receipt.json"
        closure = safe_load_json(closure_path)
        verdict = str(closure.get("verdict", "UNKNOWN")) if closure else "UNKNOWN"
        scoped = verdict.startswith("PASS_FOR_")
        if closure and not scoped:
            status = "BLOCK"
            summary = "Closure verdict is not scoped PASS_FOR_<SLICE>_ONLY."
        elif closure and scoped:
            status = "OK"
            summary = "Scoped verdict found."
        else:
            status = "WARN"
            summary = "Closure receipt not present yet."
        payload = {"closure_path": str(closure_path), "verdict": verdict, "scoped": scoped}
        return ShellResult(status=status, summary=summary, payload=payload)

    def _dispatch(self, name: str, arg_text: str) -> ShellResult:
        handlers = {
            "status": self._command_status,
            "identity": self._command_identity,
            "gates": self._command_gates,
            "query": self._command_query,
            "evidence": self._command_evidence,
            "help": self._command_help,
            "laws": self._command_laws,
            "preflight": self._command_preflight,
            "role": self._command_role,
            "language": self._command_language,
            "continuity": self._command_continuity,
            "receipts": self._command_receipts,
            "route": self._command_route,
            "stages": self._command_stages,
            "tools": self._command_tools,
            "capability": self._command_capability,
            "audit": self._command_audit,
            "fakegreen": self._command_fakegreen,
        }
        handler = handlers.get(name)
        if handler is None:
            return ShellResult(status="BLOCK", summary=f"Unknown or disallowed command: {name}")
        return handler(arg_text)

    def run_command(self, raw_command: str, source: str) -> tuple[ShellResult, bool]:
        parts = raw_command.strip().split(maxsplit=1)
        if not parts:
            return ShellResult(status="WARN", summary="Empty command."), False
        command = parts[0].strip().lower()
        arg_text = parts[1] if len(parts) > 1 else ""
        if command not in self.allowlist:
            result = ShellResult(status="BLOCK", summary=f"Command not allowlisted: {command}")
            self._record(command, result, source)
            return result, False
        if command == "clear":
            if self.console is not None:
                self.console.clear()
            result = ShellResult(status="OK", summary="Screen cleared.")
            self._record(command, result, source)
            return result, False
        if command == "exit":
            result = ShellResult(status="OK", summary="Exit command accepted.")
            self._record(command, result, source)
            return result, True

        result = self._dispatch(command, arg_text)
        self._record(command, result, source)
        return result, False

    def _record(self, command: str, result: ShellResult, source: str) -> None:
        status = normalize_status(result.status)
        if status not in self.counters:
            status = "WARN"
        self.counters[status] += 1
        self.latest_command = command
        self.latest_summary = result.summary
        self.latest_payload = result.payload
        self.history.append(
            {
                "command": command,
                "source": source,
                "status": status,
                "summary": result.summary,
                "payload": result.payload,
                "timestamp_utc": utc_now(),
            }
        )

    def _run_mode(self) -> str:
        if self.args.smoke:
            return "smoke"
        if self.args.scripted_test:
            return "scripted_test"
        if self.args.command:
            return "single_command"
        return "interactive"

    def _command_palette_table(self) -> Table:
        table = Table(title="COMMAND ZONE / ALLOWLIST", border_style=self.theme.get("panel", "cyan"))
        table.add_column("Command", style=self.theme.get("accent", "bold cyan"))
        table.add_column("Action")
        for name in sorted(self.allowlist.keys()):
            table.add_row(name, self.allowlist[name].get("description", ""))
        return table

    def _render_payload_excerpt(self) -> str:
        if self.latest_payload is None:
            return "No payload yet."
        try:
            dumped = json.dumps(self.latest_payload, ensure_ascii=False, indent=2)
        except Exception:
            dumped = str(self.latest_payload)
        return clip_text(dumped, 2600)

    def render(self) -> None:
        if self.console is None or not HAVE_RICH:
            return
        status_line = (
            f"HEAD {self._git_value('git', 'rev-parse', '--short', 'HEAD')} | "
            f"BRANCH {self._git_value('git', 'branch', '--show-current')} | "
            f"MODE {self._run_mode()} | TASK {self.task_id}"
        )
        header_text = (
            f"{self.organ_id} SHELL {self.shell_version}\n"
            f"{self.theme.get('identity', 'Operator Console')}\n"
            f"{status_line}"
        )
        header = Panel(
            header_text,
            title="IDENTITY HEADER",
            border_style=self.theme.get("header", "bold cyan"),
        )

        strip = Table(title="STATUS STRIP", border_style=self.theme.get("panel", "cyan"))
        strip.add_column("OK")
        strip.add_column("WARN")
        strip.add_column("BLOCK")
        strip.add_column("Last Command")
        strip.add_column("Latest Summary")
        strip.add_row(
            str(self.counters["OK"]),
            str(self.counters["WARN"]),
            str(self.counters["BLOCK"]),
            self.latest_command,
            clip_text(self.latest_summary, 140).replace("\n", " "),
        )

        work = Panel(
            self._render_payload_excerpt(),
            title=f"WORK ZONE / LAST OUTPUT ({self.latest_command})",
            border_style=self.theme.get("panel", "cyan"),
        )
        commands = self._command_palette_table()
        mission = Panel(self.mission_focus, title="MISSION FOCUS", border_style=self.theme.get("panel", "cyan"))
        evidence = Panel(
            "\n".join(self._collect_report_files()) or "No report artifacts yet.",
            title="EVIDENCE / LATEST REPORTS",
            border_style=self.theme.get("panel", "cyan"),
        )

        self.console.clear()
        self.console.print(header)
        self.console.print(strip)
        self.console.print(Columns([work, commands], equal=True, expand=True))
        self.console.print(Columns([mission, evidence], equal=True, expand=True))
        self.console.print(
            Panel(
                f"{self.organ_slug}> allowlisted command input only",
                title="PROMPT CONTRACT",
                border_style=self.theme.get("panel", "cyan"),
            )
        )

    def _export_snapshots(self) -> None:
        if self.console is None:
            return
        if self.args.snapshot_text_path:
            text_path = Path(self.args.snapshot_text_path).resolve()
            text_path.parent.mkdir(parents=True, exist_ok=True)
            self.console.save_text(str(text_path))
        if self.args.snapshot_html_path:
            html_path = Path(self.args.snapshot_html_path).resolve()
            html_path.parent.mkdir(parents=True, exist_ok=True)
            self.console.save_html(str(html_path))

    def _run_non_interactive_sequence(self, sequence: list[str], source: str) -> bool:
        blocked = False
        for command in sequence:
            result, _ = self.run_command(command, source=source)
            if normalize_status(result.status) == "BLOCK":
                blocked = True
        return blocked

    def _json_result(self, proof: str | None) -> dict[str, Any]:
        verdict = "PASS"
        if self.counters["BLOCK"] > 0:
            verdict = "BLOCK"
        elif self.counters["WARN"] > 0:
            verdict = "WARN"
        return {
            "schema_id": "newgen_organ_shell_run_v0_1",
            "organ_id": self.organ_id,
            "task_id": self.task_id,
            "mode": self._run_mode(),
            "verdict": verdict,
            "status": verdict,
            "proof": proof,
            "rich_available": HAVE_RICH,
            "responsibility": self.state.get("responsibility", ""),
            "allowlisted_commands": sorted(self.allowlist.keys()),
            "counters": self.counters,
            "history": self.history,
            "report_root": str(self.report_root),
            "generated_at_utc": utc_now(),
        }

    def run(self) -> int:
        if not HAVE_RICH:
            payload = {
                "schema_id": "newgen_organ_shell_block_v0_1",
                "organ_id": self.organ_id,
                "error": "Rich renderer is required for ORGAN_SHELL_V1",
                "rich_available": False,
                "generated_at_utc": utc_now(),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 3

        mode_count = int(bool(self.args.smoke)) + int(bool(self.args.scripted_test)) + int(bool(self.args.command))
        if mode_count > 1:
            print("BLOCK: use only one of --smoke, --scripted-test, --command.")
            return 2

        proof: str | None = None
        blocked = False

        if self.args.smoke:
            sequence = ["status", "identity", "gates"]
            sequence.extend(list(self.specific_commands.keys())[:1])
            sequence.extend(["query", "evidence"])
            blocked = self._run_non_interactive_sequence(sequence, source="smoke")
            proof = f"SMOKE_OK_{self.organ_id}_SHELL_V0_1"
        elif self.args.scripted_test:
            sequence = ["status", "identity", "gates", "query", "evidence"]
            sequence.extend(list(self.specific_commands.keys()))
            sequence.append("help")
            blocked = self._run_non_interactive_sequence(sequence, source="scripted_test")
            proof = f"SCRIPTED_TEST_OK_{self.organ_id}_SHELL_V0_1"
        elif self.args.command:
            result, _ = self.run_command(str(self.args.command), source="single_command")
            blocked = normalize_status(result.status) == "BLOCK"
        else:
            while True:
                self.render()
                prompt_style = self.theme.get("prompt", "bold cyan")
                if self.console is None:
                    break
                try:
                    raw = self.console.input(f"[{prompt_style}]{self.organ_slug}> [/]")
                except (EOFError, KeyboardInterrupt):
                    self.run_command("exit", source="interactive")
                    break
                result, should_exit = self.run_command(raw, source="interactive")
                if normalize_status(result.status) == "BLOCK":
                    blocked = True
                if should_exit:
                    break
                if self.console is not None:
                    self.render()

        if not self.args.plain_json:
            self.render()
            if proof:
                print(proof)
        self._export_snapshots()

        payload = self._json_result(proof=proof)
        if self.args.plain_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2 if blocked else 0


def parse_args(argv: Sequence[str] | None = None, default_task_id: str = "TASK-UNKNOWN") -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ORGAN_SHELL_V1 runtime.")
    parser.add_argument("--task-id", default=default_task_id)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--scripted-test", action="store_true")
    parser.add_argument("--command", default=None)
    parser.add_argument("--plain-json", action="store_true")
    parser.add_argument("--snapshot-text-path", default=None)
    parser.add_argument("--snapshot-html-path", default=None)
    return parser.parse_args(list(argv) if argv is not None else None)


def run_organ_shell(config: Mapping[str, Any], argv: Sequence[str] | None = None) -> int:
    default_task_id = str(config.get("task_id_default", "TASK-UNKNOWN"))
    args = parse_args(argv=argv, default_task_id=default_task_id)
    shell = OrganShell(config=config, args=args)
    return shell.run()
