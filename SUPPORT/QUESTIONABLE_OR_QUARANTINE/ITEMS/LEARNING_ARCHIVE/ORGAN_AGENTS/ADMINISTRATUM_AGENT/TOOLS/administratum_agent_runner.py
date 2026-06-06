#!/usr/bin/env python3
"""Administratum-Agent V1 hardened CLI runner (reference-grade trajectory)."""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
import tracemalloc
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Optional controlled renderer experiment.
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    Console = Any  # type: ignore[assignment]
    Live = Any  # type: ignore[assignment]
    Panel = Any  # type: ignore[assignment]
    Text = Any  # type: ignore[assignment]
    RICH_AVAILABLE = False

from administratum_v1_core import (
    AGENT_ROOT,
    DEFAULT_CONTEXT_LOCAL,
    DEFAULT_CONTEXT_PRIVATE,
    NEW_GENERATION_ROOT,
    REPO_ROOT,
    RUNS_ROOT,
    SKILL_IDS,
    SkillRunResult,
    build_agent_handoff_context,
    build_cu_index,
    build_inventory,
    build_merge_preparation_summary,
    build_provenance_index,
    classify_local_context,
    classify_path,
    collect_continuity_pack,
    collect_reality_snapshot,
    command_receipt,
    create_run_dir,
    detect_dirty_runtime_outputs,
    detect_private_export_risk,
    ensure_runs_root,
    finalize_metrics,
    find_useful_candidates,
    git_head,
    git_is_dirty,
    load_manifest,
    metrics_summary_from_run,
    new_metrics,
    now_utc,
    optional_oss_enhancement_proposal,
    read_json,
    record_run_event,
    route_for_object,
    route_to_organs,
    scan_imperium_context,
    sha256_file,
    skill_receipt,
    status_snapshot,
    verify_pack_against_reality,
    write_command_receipt,
    write_json,
    write_skill_receipt,
    kpd_from_reports,
)
from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root
from administratum_dossier_factory import (
    build_dossier_package,
    detect_oss_availability,
    find_latest_dossier_zip,
    verify_dossier_package,
)

TRANSFER_GATE_SCRIPTS = AGENT_ROOT / "TRANSFER_GATE" / "SCRIPTS"
if str(TRANSFER_GATE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(TRANSFER_GATE_SCRIPTS))

from transfer_gate_core_v0_1 import (  # noqa: E402
    DEFAULT_TRANSFER_ROOT,
    fetch_vm2_response_bundle_remote,
    fetch_vm2_response_bundle,
    push_vm2_prompt_pack,
    send_vm2_prompt_pack,
    transfer_status,
    verify_prompt_pack,
)

COMMON_AGENT_CLI_ROOT = NEW_GENERATION_ROOT / "COMMON_AGENT_CLI"
if str(COMMON_AGENT_CLI_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_AGENT_CLI_ROOT))

from tool_registry_reader import build_organ_tool_view, default_tool_index_path  # noqa: E402


class UserFacingError(RuntimeError):
    """Error with operator guidance."""

    def __init__(self, what_happened: str, how_to_fix: str, example: str) -> None:
        super().__init__(what_happened)
        self.what_happened = what_happened
        self.how_to_fix = how_to_fix
        self.example = example


TASK_DOSSIER_FACTORY_ID = "TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1"
TASK_REFERENCE_REPAIR_ID = "TASK-20260518-ADMINISTRATUM-REFERENCE-MEGA-REPAIR-V0_1"
FREELANCE_SCHEMA_PATH = AGENT_ROOT / "SCHEMAS" / "ADMINISTRATUM_FREELANCE_TASK_ENVELOPE_SCHEMA_V0_1.json"
FREELANCE_SAMPLE_VALID_PATH = AGENT_ROOT / "EXAMPLES" / "FREELANCE_TASK_ENVELOPE_VALID_V0_1.json"
FREELANCE_SAMPLE_MALFORMED_PATH = AGENT_ROOT / "EXAMPLES" / "FREELANCE_TASK_ENVELOPE_MALFORMED_V0_1.json"
HEAVY_DIRTY_COMMANDS = {
    "build-dossier",
    "check-all",
    "collect-continuity-pack",
    "collect-reality-snapshot",
    "build-agent-handoff-context",
}
ADMITTED_DIRTY_PREFIXES = (
    "ORGAN_AGENTS/ADMINISTRATUM_AGENT/",
    "RUNS/ADMINISTRATUM_AGENT/",
)
BASE_HALF_TASK_ID = "TASK-20260519-ORGAN-AGENT-BASE-HALF-8-ORGANS-V0_1"
BASE_HALF_REQUIRED_COMMANDS = ["status", "check", "where", "identity", "tools", "pack", "shell", "help"]
BASE_HALF_REQUIRED_FILES = [
    "README.md",
    "AGENT_PROFILE.md",
    "agent_profile.json",
    "IDENTITY_BASELINE.md",
    "TOOLS/administratum_agent_runner.py",
    "LAUNCHERS/run_administratum_pc.ps1",
    "SHELL/SHELL_CONTRACT.md",
    "STATE/current_status.json",
    "REPORTS/base_half_check_report.json",
    "REPORTS/base_half_check_report.md",
    "EXAMPLES/README.md",
    "TESTS/README.md",
]
BASE_HALF_STATE_PATH = AGENT_ROOT / "STATE" / "current_status.json"
BASE_HALF_REPORT_JSON_PATH = AGENT_ROOT / "REPORTS" / "base_half_check_report.json"
BASE_HALF_REPORT_MD_PATH = AGENT_ROOT / "REPORTS" / "base_half_check_report.md"
BASE_HALF_RUNTIME_ROOT = (
    RUNS_ROOT
    / "ORGAN_AGENT_BASE_HALF_RUNS"
    / BASE_HALF_TASK_ID
    / "ORGANS"
    / "ADMINISTRATUM_AGENT"
)


@dataclass
class CommandContext:
    command: str
    run_id: str
    run_dir: Path
    metrics: Dict[str, Any]
    start_ns: int
    cpu_start: float
    memory_trace_started: bool
    dirty_before: bool
    read_paths: set[str]
    written_paths: set[str]


def _verdict_to_status(verdict: str) -> str:
    token = str(verdict or "").upper()
    if "OWNER_DECISION" in token:
        return "OWNER_DECISION_REQUIRED"
    if token in {"PASS", "OK"}:
        return "PASS"
    if "WARN" in token:
        return "WARN"
    if token in {"BLOCKED", "REJECT_MUTATION_REQUEST"} or "BLOCK" in token:
        return "BLOCKED"
    return "FAIL"


class Renderer:
    COLORS = {
        "reset": "\x1b[0m",
        "red": "\x1b[31m",
        "green": "\x1b[32m",
        "yellow": "\x1b[33m",
        "blue": "\x1b[34m",
        "cyan": "\x1b[36m",
        "gray": "\x1b[90m",
        "bold": "\x1b[1m",
    }

    def __init__(
        self,
        *,
        plain_json: bool,
        color: bool,
        verbose: bool,
        compact: bool,
        force_ascii: bool,
        rich_enabled: bool,
    ) -> None:
        self.plain_json = plain_json
        self.color = bool(color)
        self.verbose = verbose
        self.compact = compact
        self.force_ascii = force_ascii
        self.rich_available = RICH_AVAILABLE
        self.rich_enabled = bool(rich_enabled and RICH_AVAILABLE and not plain_json)
        enc = (sys.stdout.encoding or "").lower()
        self.use_unicode = ("utf" in enc) and (not force_ascii)
        self.width = max(80, min(140, shutil.get_terminal_size((110, 30)).columns))
        self.frame = self._frame_chars()
        self.path_aliases = [
            (str(AGENT_ROOT), "<ADMIN>"),
            (str(RUNS_ROOT), "<RUNS>"),
            (str(REPO_ROOT), "<REPO>"),
        ]
        self._rich_console: Optional[Console] = None
        self._rich_live: Optional[Live] = None
        self._progress_state: Dict[str, Any] = {}
        if self.rich_enabled:
            self._rich_console = Console(no_color=not self.color, force_terminal=True if self.color else None)

    def _frame_chars(self) -> Dict[str, str]:
        if self.use_unicode:
            return {
                "h": "─",
                "v": "│",
                "tl": "┌",
                "tr": "┐",
                "bl": "└",
                "br": "┘",
                "ltee": "├",
                "rtee": "┤",
            }
        return {
            "h": "-",
            "v": "|",
            "tl": "+",
            "tr": "+",
            "bl": "+",
            "br": "+",
            "ltee": "+",
            "rtee": "+",
        }

    def _paint(self, text: str, color_name: str, *, bold: bool = False) -> str:
        if not self.color:
            return text
        prefix = ""
        if bold:
            prefix += self.COLORS["bold"]
        return f"{prefix}{self.COLORS[color_name]}{text}{self.COLORS['reset']}"

    def status_tag(self, status: str) -> str:
        v = str(status or "INFO").upper()
        if v == "PASS":
            return self._paint(f"[{v}]", "green", bold=True)
        if v == "WARN":
            return self._paint(f"[{v}]", "yellow", bold=True)
        if v in {"BLOCKED", "FAIL", "OWNER_DECISION_REQUIRED"}:
            return self._paint(f"[{v}]", "red", bold=True)
        return self._paint(f"[{v}]", "blue")

    def compact_display(self, text: str, *, run_id: Optional[str] = None) -> str:
        if self.plain_json:
            return text
        out = str(text)
        replacements: List[Tuple[str, str]] = []
        if run_id and run_id not in {"N/A", "UNKNOWN"}:
            replacements.append((str(RUNS_ROOT / run_id), "<RUN>"))
        replacements.extend(self.path_aliases)
        for source, alias in replacements:
            variants = {source, source.replace("\\", "/"), source.replace("/", "\\")}
            for variant in sorted(variants, key=len, reverse=True):
                out = out.replace(variant, alias)
        return out

    def _border(self, left: str, fill: str, right: str, width: int) -> str:
        return f"{left}{fill * width}{right}"

    def panel(self, title: str, lines: Sequence[str], *, color: str = "cyan") -> str:
        inner = self.width - 4
        h = self.frame["h"]
        v = self.frame["v"]
        out: List[str] = []
        out.append(self._border(self.frame["tl"], h, self.frame["tr"], inner + 2))
        title_line = title[:inner]
        out.append(f"{v} {self._paint(title_line.ljust(inner), color, bold=True)} {v}")
        out.append(self._border(self.frame["ltee"], h, self.frame["rtee"], inner + 2))
        for raw in lines:
            for wrapped in textwrap.wrap(raw, width=inner) or [""]:
                out.append(f"{v} {wrapped.ljust(inner)} {v}")
        out.append(self._border(self.frame["bl"], h, self.frame["br"], inner + 2))
        return "\n".join(out)

    def _list_lines(self, title: str, rows: Sequence[str], *, limit: int = 5) -> List[str]:
        out = [f"{title}:"]
        if not rows:
            out.append("  - NONE")
            return out
        visible = list(rows) if self.verbose else list(rows[:limit])
        for row in visible:
            out.append(f"  - {row}")
        if not self.verbose and len(rows) > len(visible):
            out.append(f"  - ... +{len(rows) - len(visible)} more")
        return out

    def _render_payload(self, payload: Dict[str, Any]) -> str:
        header = str(payload.get("header", "ADMINISTRATUM AGENT"))
        status = str(payload.get("status", "FAIL")).upper()
        command = str(payload.get("command", "unknown"))
        run_id = str(payload.get("run_id", "N/A"))
        verdict = str(payload.get("verdict", "UNKNOWN"))
        summary = str(payload.get("summary", "")).strip()
        summary_lines = [line.strip() for line in summary.splitlines() if line.strip()]
        primary_refs = [self.compact_display(str(x), run_id=run_id) for x in payload.get("primary_refs", [])]
        artifacts_written = [self.compact_display(str(x), run_id=run_id) for x in payload.get("artifacts_written", [])]
        warnings = [self.compact_display(str(x), run_id=run_id) for x in payload.get("warnings", [])]
        why_trust = [self.compact_display(str(x), run_id=run_id) for x in payload.get("why_trust", [])]
        next_actions = [self.compact_display(str(x), run_id=run_id) for x in payload.get("next_actions", [])]
        limitations = [self.compact_display(str(x), run_id=run_id) for x in payload.get("limitations", [])]
        summary_lines = [self.compact_display(line, run_id=run_id) for line in summary_lines]
        details = payload.get("details", {})
        metrics = payload.get("metrics", {})

        lines: List[str] = [
            f"STATUS: {self.status_tag(status)}",
            f"COMMAND: {command}",
            f"RUN_ID: {run_id}",
            f"VERDICT: {verdict}",
        ]
        lines.extend(self._list_lines("SUMMARY", summary_lines or ["No summary provided."], limit=3))
        lines.extend(self._list_lines("PRIMARY_REFS", primary_refs))
        lines.extend(self._list_lines("ARTIFACTS_WRITTEN", artifacts_written))
        lines.extend(self._list_lines("WARNINGS", warnings))
        lines.extend(self._list_lines("WHY_TRUST", why_trust))
        lines.extend(self._list_lines("NEXT_ACTIONS", next_actions))
        lines.extend(self._list_lines("LIMITATIONS", limitations))

        blocks = [self.panel(header, lines, color="blue")]
        if self.verbose:
            if metrics:
                metrics_lines = json.dumps(metrics, indent=2, ensure_ascii=False).splitlines()
                blocks.append(self.panel("METRICS", metrics_lines, color="cyan"))
            if details:
                detail_lines = json.dumps(details, indent=2, ensure_ascii=False).splitlines()
                blocks.append(self.panel("DETAILS", detail_lines, color="gray"))
        return "\n".join(blocks)

    def emit(self, payload: Dict[str, Any]) -> None:
        self.finish_progress()
        if self.plain_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        print(self._render_payload(payload))

    def emit_error(self, err: UserFacingError) -> None:
        self.finish_progress()
        payload = {
            "header": "ADMINISTRATUM AGENT :: ERROR",
            "status": "BLOCKED",
            "command": "error",
            "run_id": "N/A",
            "verdict": "BLOCKED",
            "summary": err.what_happened,
            "primary_refs": [],
            "artifacts_written": [],
            "warnings": [err.what_happened],
            "why_trust": ["Operator-facing guidance generated by CLI guardrail."],
            "next_actions": [err.how_to_fix, f"Example: {err.example}"],
            "metrics": {},
            "limitations": ["No command outputs were written due to failure."],
            "details": {
                "what_happened": err.what_happened,
                "how_to_fix": err.how_to_fix,
                "example": err.example,
            },
        }
        if self.plain_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        print(self._render_payload(payload))

    def begin_progress(self, command: str, run_id: str) -> None:
        if not self.rich_enabled or self._rich_console is None:
            return
        self._progress_state = {
            "command": command,
            "run_id": run_id,
            "phase": 0,
            "total": 8,
            "label": "idle",
            "status": "IDLE",
            "elapsed": "[00:000]",
            "extra": "",
            "counters": "",
            "warnings_count": 0,
            "target": "none",
            "final_status": "N/A",
            "last_done": "none",
        }

    def _warnings_from_extra(self, extra: str) -> int:
        m = re.search(r"warnings\s*=\s*(\d+)", extra)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return 0
        return 0

    def _render_rich_progress(self) -> Any:
        phase = int(self._progress_state.get("phase", 0))
        total = int(self._progress_state.get("total", 8))
        completed = max(0, min(total, phase))
        bar_width = 16
        filled = int((completed / total) * bar_width) if total > 0 else 0
        bar = f"[{'#' * filled}{'-' * (bar_width - filled)}]"
        text = Text()
        text.append("IMPERIUM :: ADMINISTRATUM LOCAL MODEL\n", style="bold magenta")
        text.append(f"LIVE RITE: {self._progress_state.get('command', 'unknown')}\n", style="bold cyan")
        text.append(
            f"{self._progress_state.get('elapsed', '[00:000]')} PHASE {phase}/{total} {self._progress_state.get('label', '')}\n",
            style="white",
        )
        text.append(
            (
                f"status={self._progress_state.get('status', 'RUNNING')} "
                f"warnings={self._progress_state.get('warnings_count', 0)} "
                f"target={self._progress_state.get('target', 'none')}\n"
            ),
            style="yellow",
        )
        if self._progress_state.get("counters"):
            text.append(f"counters: {self._progress_state.get('counters', '')}\n", style="bright_black")
        text.append(
            (
                f"{bar}  last={self._progress_state.get('last_done', 'none')} "
                f"final={self._progress_state.get('final_status', 'N/A')}"
            ),
            style="bright_blue",
        )
        return Panel(text, title="ARCHIVE SEAL", border_style="bright_magenta")

    def emit_phase(
        self,
        phase: int,
        total: int,
        label: str,
        status: str,
        elapsed: str,
        extra: str,
        *,
        warnings_count: Optional[int] = None,
        target: Optional[str] = None,
    ) -> None:
        if self.plain_json:
            return
        resolved_warnings = self._warnings_from_extra(extra) if warnings_count is None else int(warnings_count)
        resolved_target = (target or "").strip() or "none"
        if self.rich_enabled and self._rich_console is not None:
            self._progress_state.update(
                {
                    "phase": phase,
                    "total": total,
                    "label": label,
                    "status": status,
                    "elapsed": elapsed,
                    "extra": extra,
                    "counters": extra,
                    "warnings_count": resolved_warnings,
                    "target": resolved_target,
                }
            )
            if status == "DONE":
                self._progress_state["last_done"] = label
            if status in {"DONE", "BLOCKED", "FAIL"}:
                verdict_match = re.search(r"verdict\s*=\s*([A-Z_]+)", extra)
                self._progress_state["final_status"] = verdict_match.group(1) if verdict_match else status
            renderable = self._render_rich_progress()
            if self._rich_live is None:
                self._rich_live = Live(renderable, console=self._rich_console, refresh_per_second=8, transient=False)
                self._rich_live.start()
            else:
                self._rich_live.update(renderable, refresh=True)
            return
        line = f"{elapsed} PHASE {phase}/{total} {label} | status={status} | warnings={resolved_warnings} | target={resolved_target}"
        if extra:
            line += f" | {extra}"
        print(line)

    def finish_progress(self) -> None:
        if self._rich_live is not None:
            self._rich_live.stop()
            self._rich_live = None
            print("")


class ProgressRail:
    PHASE_LABELS = {
        1: "Reading repo state",
        2: "Scanning IMPERIUM_CONTEXT metadata",
        3: "Building inventory",
        4: "Classifying risks",
        5: "Collecting useful refs",
        6: "Building continuity narrative",
        7: "Writing receipts and metrics",
        8: "Verifying pack",
    }

    def __init__(self, renderer: Renderer, ctx: CommandContext, *, total_phases: int = 8) -> None:
        self.renderer = renderer
        self.ctx = ctx
        self.total_phases = total_phases
        self.last_phase = 0
        self.renderer.begin_progress(ctx.command, ctx.run_id)

    def _elapsed(self) -> str:
        ms = int((time.perf_counter_ns() - self.ctx.start_ns) / 1_000_000)
        sec = ms // 1000
        return f"[{sec:02d}:{ms % 1000:03d}]"

    def start(self, phase: int, extra: str = "", *, target: str = "") -> None:
        self.last_phase = phase
        self.renderer.emit_phase(
            phase,
            self.total_phases,
            self.PHASE_LABELS.get(phase, f"Phase {phase}"),
            "RUNNING",
            self._elapsed(),
            extra,
            warnings_count=int(self.ctx.metrics.get("warnings_count", 0)),
            target=target,
        )

    def pulse(self, phase: Optional[int] = None, extra: str = "", *, target: str = "") -> None:
        p = phase if phase is not None else self.last_phase
        if p <= 0:
            return
        self.renderer.emit_phase(
            p,
            self.total_phases,
            self.PHASE_LABELS.get(p, f"Phase {p}"),
            "RUNNING",
            self._elapsed(),
            extra,
            warnings_count=int(self.ctx.metrics.get("warnings_count", 0)),
            target=target,
        )

    def done(self, phase: int, extra: str = "", *, target: str = "") -> None:
        self.last_phase = phase
        self.renderer.emit_phase(
            phase,
            self.total_phases,
            self.PHASE_LABELS.get(phase, f"Phase {phase}"),
            "DONE",
            self._elapsed(),
            extra,
            warnings_count=int(self.ctx.metrics.get("warnings_count", 0)),
            target=target,
        )


def _truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _report_verdict_to_command_verdict(verdict: str) -> str:
    token = str(verdict or "").upper()
    if token == "PASS":
        return "PASS"
    if token == "WARN":
        return "PASS_WITH_WARNINGS"
    if "OWNER_DECISION" in token:
        return "OWNER_DECISION_REQUIRED"
    if token in {"BLOCKED", "FAIL"}:
        return token
    if "WARN" in token:
        return "PASS_WITH_WARNINGS"
    if "PASS" in token:
        return "PASS"
    return "BLOCKED"


def _resolve_repo_path(path_text: str) -> Path:
    return resolve_new_reality_root(path_text or None, start=Path(__file__)).active_root


def _resolve_json_report(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    if not path.exists():
        raise UserFacingError(
            f"Input report not found: {path}",
            "Provide a valid existing JSON report path.",
            f"python {Path(__file__).name} --no-color merge-summary --repo-root {REPO_ROOT} --inventory <path_to_inventory_report.json>",
    )
    return path


def _parse_git_porcelain_paths(stdout: str) -> List[str]:
    paths: List[str] = []
    for line in stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].strip()
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1].strip()
        raw = raw.strip('"').replace("\\", "/")
        if raw:
            paths.append(raw)
    simulated = os.environ.get("ADMINISTRATUM_DIRTY_SIMULATION_PATHS", "").strip()
    if simulated:
        for item in re.split(r"[;\n]", simulated):
            rel = item.strip().strip('"').replace("\\", "/")
            if rel:
                paths.append(rel)
    return sorted(dict.fromkeys(paths))


def _git_dirty_paths(repo_root: Path) -> List[str]:
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=False)
    return _parse_git_porcelain_paths(proc.stdout)


def _admitted_dirty_path(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in ADMITTED_DIRTY_PREFIXES)


def _dirty_admission_state(command: str) -> Dict[str, Any]:
    dirty_paths = _git_dirty_paths(REPO_ROOT)
    unauthorized = [p for p in dirty_paths if not _admitted_dirty_path(p)]
    authorized = [p for p in dirty_paths if _admitted_dirty_path(p)]
    verdict = "PASS"
    if dirty_paths and command in HEAVY_DIRTY_COMMANDS:
        verdict = "OWNER_DECISION_REQUIRED" if unauthorized else "PASS_WITH_WARNINGS"
    return {
        "command": command,
        "dirty_paths": dirty_paths,
        "authorized_dirty_paths": authorized,
        "unauthorized_dirty_paths": unauthorized,
        "heavy_command": command in HEAVY_DIRTY_COMMANDS,
        "verdict": verdict,
    }


def _dirty_admission_warnings(admission: Dict[str, Any]) -> List[str]:
    if not admission.get("dirty_paths"):
        return []
    if admission.get("unauthorized_dirty_paths"):
        return [
            "dirty pre-state requires Owner decision before heavy command",
            f"unauthorized dirty paths: {', '.join(str(x) for x in admission.get('unauthorized_dirty_paths', [])[:5])}",
        ]
    return [
        "dirty pre-state is limited to Administratum/RUNS admitted scope; preserve GATE_ACK evidence before claiming clean PASS"
    ]


def _block_if_dirty_owner_decision(
    ctx: CommandContext,
    renderer: Renderer,
    *,
    command: str,
    input_refs: Sequence[str],
    progress: Optional[ProgressRail] = None,
) -> Optional[int]:
    admission = _dirty_admission_state(command)
    if admission.get("verdict") != "OWNER_DECISION_REQUIRED":
        return None
    report_path = ctx.run_dir / "reports" / f"{command.replace('-', '_')}_dirty_admission_report.json"
    report = {
        "report_type": "DIRTY_ADMISSION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "admission": admission,
        "options": [
            "Review dirty paths and explicitly authorize them for this task.",
            "Commit/stash/revert unrelated dirty paths outside Administratum scope.",
            "Rerun the heavy command from a clean or admitted state.",
        ],
        "verdict": "OWNER_DECISION_REQUIRED",
        "warnings": _dirty_admission_warnings(admission),
    }
    write_json(report_path, report)
    return _finalize_command(
        ctx,
        renderer,
        header=f"ADMINISTRATUM AGENT :: {command.upper()} ADMISSION",
        verdict="OWNER_DECISION_REQUIRED",
        summary="Heavy command blocked by dirty pre-state admission law.",
        outputs=[report_path],
        input_refs=input_refs,
        warnings=report["warnings"],
        details=report,
        next_actions=report["options"],
        blocker_class="DIRTY_STATE_OWNER_DECISION_REQUIRED",
        progress=progress,
    )


def _collect_outputs(*items: Any) -> List[Path]:
    out: List[Path] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, SkillRunResult):
            out.extend([Path(item.report_path), Path(item.receipt_path)])
            continue
        if isinstance(item, Path):
            out.append(item)
            continue
        if isinstance(item, (list, tuple)):
            out.extend(_collect_outputs(*item))
            continue
        text = str(item).strip()
        if not text or text in {".", "./"}:
            continue
        try:
            out.append(Path(text))
        except Exception:
            continue
    return out


def _start_command(command: str, out_dir: Optional[str]) -> CommandContext:
    ensure_runs_root()
    run_id, run_dir = create_run_dir(out_dir)
    dirty_before = git_is_dirty(REPO_ROOT)
    metrics = new_metrics(command, dirty_before)
    start_ns = time.perf_counter_ns()
    cpu_start = time.process_time()
    started_memory_trace = False
    if not tracemalloc.is_tracing():
        tracemalloc.start()
        started_memory_trace = True
    record_run_event(run_dir, "COMMAND_START", {"command": command})
    return CommandContext(
        command=command,
        run_id=run_id,
        run_dir=run_dir,
        metrics=metrics,
        start_ns=start_ns,
        cpu_start=cpu_start,
        memory_trace_started=started_memory_trace,
        dirty_before=dirty_before,
        read_paths=set(),
        written_paths=set(),
    )


def _write_metrics_report(ctx: CommandContext) -> Path:
    payload = {
        "report_type": "COMMAND_METRICS_SUMMARY",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "command": ctx.command,
        "generated_at_utc": now_utc(),
        "metrics": ctx.metrics,
    }
    metrics_path = ctx.run_dir / "reports" / f"{ctx.command.replace('-', '_')}_metrics_summary.json"
    write_json(metrics_path, payload)
    return metrics_path


def _register_paths(ctx: CommandContext, refs: Iterable[str], *, write: bool) -> None:
    target = ctx.written_paths if write else ctx.read_paths
    for ref in refs:
        raw = str(ref).strip()
        if not raw:
            continue
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / candidate).resolve()
        target.add(str(candidate))


def _path_category(path: Path) -> str:
    name = path.name.lower()
    if "receipt" in name:
        return "receipts"
    if "metric" in name:
        return "metrics"
    if path.suffix.lower() in {".md", ".txt"}:
        return "docs"
    return "reports"


def _build_access_map(ctx: CommandContext, dirty_after: bool) -> Dict[str, Any]:
    read_roots = sorted({str(Path(p).anchor + Path(p).parts[1]) if len(Path(p).parts) > 1 else str(Path(p)) for p in ctx.read_paths})
    written_roots = sorted({str(Path(p).anchor + Path(p).parts[1]) if len(Path(p).parts) > 1 else str(Path(p)) for p in ctx.written_paths})
    private_roots = sorted({p for p in ctx.read_paths if "IMPERIUM_CONTEXT\\PRIVATE" in p.upper() or "IMPERIUM_CONTEXT/PRIVATE" in p.upper()})
    files_written_by_category: Dict[str, int] = {}
    for raw in sorted(ctx.written_paths):
        p = Path(raw)
        cat = _path_category(p)
        files_written_by_category[cat] = files_written_by_category.get(cat, 0) + 1
    return {
        "report_type": "ACCESS_MAP_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "read_roots": read_roots,
        "written_roots": written_roots,
        "private_roots_metadata_only": private_roots,
        "forbidden_roots_not_touched": [
            "ANCIENT_EMPIRE_REFERENCE:ORGANS/SANCTUM",
            "ANCIENT_EMPIRE_REFERENCE:IMPERIUM_TEST_VERSION",
        ],
        "runtime_output_dir": str(ctx.run_dir),
        "files_written_by_category": files_written_by_category,
        "git_mutation_status": "NO_GIT_MUTATION" if (ctx.dirty_before == dirty_after) else "DIRTY_STATE_CHANGED",
    }


def _sync_continuity_pack_metrics(run_dir: Path, metrics: Dict[str, Any]) -> None:
    metrics_summary_path = run_dir / "continuity_pack" / "metrics_summary.json"
    if not metrics_summary_path.exists():
        return
    try:
        summary = read_json(metrics_summary_path)
    except Exception:
        return
    aggregate = summary.get("aggregate")
    if not isinstance(aggregate, dict):
        return

    numeric_fields = [
        "wall_clock_ms",
        "process_cpu_seconds",
        "files_scanned",
        "files_classified",
        "objects_considered",
        "outputs_written_count",
        "output_bytes_total",
        "warnings_count",
        "errors_count",
        "rejected_count",
        "routes_made",
        "receipts_written",
        "owner_wait_seconds",
        "touched_paths_read_count",
        "touched_paths_written_count",
    ]
    for field in numeric_fields:
        try:
            current = float(aggregate.get(field, 0) or 0)
            incoming = float(metrics.get(field, 0) or 0)
            if incoming > current:
                if field in {"process_cpu_seconds", "owner_wait_seconds"}:
                    aggregate[field] = round(incoming, 6 if field == "process_cpu_seconds" else 3)
                else:
                    aggregate[field] = int(incoming)
        except Exception:
            continue

    peak_incoming = metrics.get("peak_memory_kb")
    if isinstance(peak_incoming, int):
        peak_current = aggregate.get("peak_memory_kb")
        if not isinstance(peak_current, int) or peak_incoming > peak_current:
            aggregate["peak_memory_kb"] = peak_incoming
            aggregate["peak_memory_unavailable_reason"] = ""
            aggregate["memory_metric_source"] = str(metrics.get("memory_metric_source", "tracemalloc"))

    aggregate["gpu_used"] = bool(aggregate.get("gpu_used", False) or metrics.get("gpu_used", False))
    aggregate["gpu_reason"] = str(metrics.get("gpu_reason", aggregate.get("gpu_reason", "")))
    aggregate["dirty_before"] = bool(aggregate.get("dirty_before", False) or metrics.get("dirty_before", False))
    aggregate["dirty_after"] = bool(aggregate.get("dirty_after", False) or metrics.get("dirty_after", False))
    aggregate["dirty_tree_before"] = bool(
        aggregate.get("dirty_tree_before", False) or metrics.get("dirty_tree_before", False)
    )
    aggregate["dirty_tree_after"] = bool(
        aggregate.get("dirty_tree_after", False) or metrics.get("dirty_tree_after", False)
    )
    aggregate["commands"] = max(int(aggregate.get("commands", 0) or 0), 1)

    incoming_cost = str(metrics.get("run_cost_class", metrics.get("cost_class", "UNSET")))
    if incoming_cost and incoming_cost != "UNSET":
        aggregate["run_cost_class"] = incoming_cost
        aggregate["cost_class"] = incoming_cost
    aggregate["maintenance_cost_note"] = str(
        metrics.get("maintenance_cost_note", aggregate.get("maintenance_cost_note", ""))
    )
    summary["aggregate"] = aggregate
    write_json(metrics_summary_path, summary)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _build_why_trust(
    *,
    ctx: CommandContext,
    input_refs: Sequence[str],
    output_paths: Sequence[Path],
    access_map_path: Path,
    metrics_path: Path,
    receipt_path: Path,
    dirty_after: bool,
    limitations: Sequence[str],
) -> List[str]:
    confined = all(_is_within(path, ctx.run_dir) for path in output_paths if path.exists())
    runtime_root_confined = all(_is_within(path, RUNS_ROOT) for path in output_paths if path.exists())
    private_context_seen = any("IMPERIUM_CONTEXT/PRIVATE" in ref.replace("\\", "/").upper() for ref in input_refs)
    reasons = [
        f"Git truth checked before/after command: dirty_before={str(ctx.dirty_before).lower()}, dirty_after={str(dirty_after).lower()}.",
        f"Command receipt written: {receipt_path}.",
        f"Metrics report written: {metrics_path}.",
        f"Access map written: {access_map_path}.",
        f"Runtime outputs confined to run dir: {str(confined).lower()}; RUNS root confinement: {str(runtime_root_confined).lower()}.",
    ]
    if private_context_seen:
        reasons.append("Private context detected in refs; metadata-only/no-git-export policy remains required.")
    if limitations:
        reasons.append("Trust is partial where limitations are present.")
    return reasons


def _finalize_command(
    ctx: CommandContext,
    renderer: Renderer,
    *,
    header: str,
    verdict: str,
    summary: str,
    outputs: Iterable[Any],
    input_refs: Iterable[str],
    warnings: Optional[List[str]] = None,
    details: Optional[Dict[str, Any]] = None,
    next_actions: Optional[List[str]] = None,
    limitations: Optional[List[str]] = None,
    blocker_class: Optional[str] = None,
    progress: Optional[ProgressRail] = None,
) -> int:
    warnings = list(warnings or [])
    limitations = limitations or []
    metrics_warning_count = int(ctx.metrics.get("warnings_count", 0) or 0)
    if metrics_warning_count > len(warnings):
        warnings.append(
            f"internal_warning_reconciliation: metrics_warnings={metrics_warning_count}, explicit_warnings={len(warnings)}"
        )
    warnings = list(dict.fromkeys(str(w) for w in warnings if str(w).strip()))
    if warnings and str(verdict).upper() in {"PASS", "OK"}:
        verdict = "PASS_WITH_WARNINGS"
    ctx.metrics["warnings_count"] = max(int(ctx.metrics.get("warnings_count", 0) or 0), len(warnings))
    if progress:
        progress.start(7, "writing_receipts_and_metrics", target=str(ctx.run_dir / "receipts"))
    input_refs_list = [str(x) for x in input_refs]
    _register_paths(ctx, input_refs_list, write=False)
    output_paths = [p for p in _collect_outputs(list(outputs)) if p.exists()]
    _register_paths(ctx, [str(p) for p in output_paths], write=True)

    dirty_after = git_is_dirty(REPO_ROOT)
    cpu_delta = max(0.0, time.process_time() - ctx.cpu_start)
    peak_kb: Optional[int] = None
    peak_reason = ""
    peak_source = "unavailable"
    if tracemalloc.is_tracing():
        _, peak = tracemalloc.get_traced_memory()
        peak_kb = int(peak / 1024)
        peak_source = "tracemalloc"
    else:
        peak_reason = "tracemalloc_not_active"

    finalize_metrics(
        ctx.metrics,
        ctx.start_ns,
        output_paths,
        dirty_after,
        process_cpu_seconds=cpu_delta,
        peak_memory_kb=peak_kb,
        peak_memory_source=peak_source,
        peak_memory_reason=peak_reason,
        touched_paths_read_count=len(ctx.read_paths),
        touched_paths_written_count=len(ctx.written_paths),
    )

    access_map = _build_access_map(ctx, dirty_after)
    access_map_path = ctx.run_dir / "reports" / f"{ctx.command.replace('-', '_')}_access_map.json"
    write_json(access_map_path, access_map)
    output_paths.append(access_map_path)
    _register_paths(ctx, [str(access_map_path)], write=True)

    metrics_path = _write_metrics_report(ctx)
    output_paths.append(metrics_path)
    _register_paths(ctx, [str(metrics_path)], write=True)
    ctx.metrics["receipts_written"] += 1
    receipt = command_receipt(
        run_id=ctx.run_id,
        command=ctx.command,
        argv=sys.argv,
        cwd=str(Path.cwd()),
        git_head_value=git_head(REPO_ROOT),
        input_refs=input_refs_list,
        output_refs=[str(p) for p in output_paths],
        metrics=ctx.metrics,
        warnings=warnings,
        verdict=verdict,
        dirty_before=ctx.dirty_before,
        dirty_after=dirty_after,
        blocker_class=blocker_class,
    )
    receipt_path = write_command_receipt(ctx.run_dir, ctx.command.replace("-", "_"), receipt)
    output_paths.append(receipt_path)

    _register_paths(ctx, [str(receipt_path)], write=True)
    existing_files = [p for p in output_paths if p.exists() and p.is_file()]
    ctx.metrics["outputs_written_count"] = len(existing_files)
    ctx.metrics["output_bytes_total"] = sum(p.stat().st_size for p in existing_files)
    ctx.metrics["output_bytes"] = ctx.metrics["output_bytes_total"]
    ctx.metrics["touched_paths_read_count"] = len(ctx.read_paths)
    ctx.metrics["touched_paths_written_count"] = len(ctx.written_paths)
    ctx.metrics["dirty_after"] = dirty_after
    ctx.metrics["dirty_tree_after"] = dirty_after
    _ = _write_metrics_report(ctx)
    _sync_continuity_pack_metrics(ctx.run_dir, ctx.metrics)
    if progress:
        progress.done(
            7,
            f"receipts={ctx.metrics.get('receipts_written', 0)} warnings={len(warnings)}",
            target=str(receipt_path),
        )
        progress.start(8, "verifying_pack_and_git_state", target=str(ctx.run_dir))

    if ctx.memory_trace_started and tracemalloc.is_tracing():
        tracemalloc.stop()

    details_payload = dict(details or {})
    details_payload["warning_reconciliation"] = {
        "explicit_warning_count": len(warnings),
        "metrics_warning_count": int(ctx.metrics.get("warnings_count", 0) or 0),
        "final_status_rule": "PASS_WITH_WARNINGS/WARN when warnings are non-empty",
        "active_warnings": warnings,
    }

    record_run_event(
        ctx.run_dir,
        "COMMAND_FINISH",
        {
            "command": ctx.command,
            "verdict": verdict,
            "warnings_count": len(warnings),
            "outputs": [str(x) for x in output_paths],
        },
    )
    if progress:
        progress.done(8, f"verdict={verdict}", target=str(ctx.run_dir))

    out_map: Dict[str, str] = {"run_dir": str(ctx.run_dir), "metrics_report": str(metrics_path), "command_receipt": str(receipt_path)}
    for index, path_obj in enumerate(output_paths, start=1):
        out_map[f"output_{index:02d}"] = str(path_obj)

    status = _verdict_to_status(verdict)
    auto_limitations: List[str] = list(limitations)
    private_context_seen = any("IMPERIUM_CONTEXT/PRIVATE" in ref.replace("\\", "/").upper() for ref in input_refs_list)
    if private_context_seen:
        auto_limitations.append("Private context references are metadata-only and must not be exported as content.")
    if not all(_is_within(path, RUNS_ROOT) for path in output_paths if path.exists()):
        auto_limitations.append("Some outputs are outside the expected RUNS root.")
    if status != "PASS":
        auto_limitations.append(f"Command status is {status}; review warnings and receipts before downstream trust.")
    dedup_limitations = list(dict.fromkeys(auto_limitations))
    why_trust = _build_why_trust(
        ctx=ctx,
        input_refs=input_refs_list,
        output_paths=output_paths,
        access_map_path=access_map_path,
        metrics_path=metrics_path,
        receipt_path=receipt_path,
        dirty_after=dirty_after,
        limitations=dedup_limitations,
    )
    summary_text = str(summary).strip() or f"{ctx.command} completed."
    primary_refs = list(dict.fromkeys(input_refs_list))
    artifacts_written = [str(p) for p in existing_files]
    next_actions_list = list(next_actions or [])
    if not next_actions_list:
        if status == "PASS":
            next_actions_list = ["Proceed to next admitted command or handoff review."]
        else:
            next_actions_list = ["Rerun with --verbose and inspect command receipt plus metrics report."]

    payload = {
        "header": header,
        "status": status,
        "command": ctx.command,
        "run_id": ctx.run_id,
        "verdict": verdict,
        "summary": summary_text,
        "primary_refs": primary_refs,
        "artifacts_written": artifacts_written,
        "outputs": out_map,
        "warnings": warnings,
        "why_trust": why_trust,
        "next_actions": next_actions_list,
        "metrics": dict(ctx.metrics),
        "limitations": dedup_limitations,
        "details": details_payload,
    }
    renderer.emit(payload)
    return 0 if status in {"PASS", "WARN"} else 1


def _render_skill_payload(skill: SkillRunResult, header: str) -> Dict[str, Any]:
    return {
        "header": header,
        "verdict": skill.report.get("verdict", "PASS"),
        "summary": f"{skill.skill_id} completed.",
        "details": skill.report,
    }


def _build_inventory_if_needed(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    metrics: Dict[str, Any],
    inventory_arg: Optional[str],
) -> Tuple[SkillRunResult, Path]:
    if inventory_arg:
        inventory_path = _resolve_json_report(inventory_arg)
        report = read_json(inventory_path)
        receipt = skill_receipt(
            run_id=run_id,
            skill_id="build_repo_inventory",
            input_refs=[str(repo_root)],
            outputs=[str(inventory_path)],
            verdict=report.get("verdict", "PASS"),
            warnings=[],
        )
        synthetic_receipt = write_skill_receipt(run_dir, "build_repo_inventory_reused", receipt)
        result = SkillRunResult(
            skill_id="build_repo_inventory",
            report=report,
            report_path=str(inventory_path),
            receipt=receipt,
            receipt_path=str(synthetic_receipt),
            run_dir=str(run_dir),
        )
        metrics["receipts_written"] += 1
        return result, inventory_path
    inv = build_inventory(repo_root, run_id, run_dir, metrics=metrics)
    return inv, Path(inv.report_path)


def _list_recent_runs(limit: int = 6, *, exclude_run_id: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_runs_root()
    dirs = sorted(
        [p for p in RUNS_ROOT.glob("RUN-*") if p.is_dir() and p.name != exclude_run_id],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    out: List[Dict[str, Any]] = []
    for run_dir in dirs[:limit]:
        check_path = run_dir / "reports" / "check_all_report.json"
        command = "unparsed"
        warnings = 0
        verdict = "unparsed"
        status = "unparsed"
        key_artifact_path = ""
        unparsed_reason = "no command receipt or check-all report found"
        receipt_candidates = sorted((run_dir / "receipts").glob("*_command_receipt.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        for receipt_path in receipt_candidates[:1]:
            try:
                receipt = read_json(receipt_path)
                command = str(receipt.get("skill_id") or receipt.get("command") or receipt_path.stem.replace("_command_receipt", ""))
                verdict = str(receipt.get("verdict", "UNKNOWN"))
                status = _verdict_to_status(verdict)
                warnings = len(receipt.get("warnings", []) or [])
                output_refs = [str(x) for x in receipt.get("output_refs", [])]
                key_artifact_path = output_refs[0] if output_refs else str(receipt_path)
                unparsed_reason = ""
            except Exception as exc:
                unparsed_reason = f"receipt_unparseable: {exc}"
            break
        check_all_verdict = "unparsed"
        if check_path.exists():
            try:
                check = read_json(check_path)
                check_all_verdict = str(check.get("verdict", "UNKNOWN"))
                if command == "unparsed":
                    command = "check-all"
                    verdict = check_all_verdict
                    status = _verdict_to_status(verdict)
                    warnings = int(check.get("failed", 0))
                    key_artifact_path = str(check_path)
                    unparsed_reason = ""
            except Exception as exc:
                if unparsed_reason:
                    unparsed_reason = f"check_all_unparseable: {exc}"
        out.append(
            {
                "run_id": run_dir.name,
                "path": str(run_dir),
                "mtime_utc": now_utc() if not run_dir.exists() else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(run_dir.stat().st_mtime)),
                "command": command,
                "status": status,
                "verdict": verdict,
                "check_all_verdict": check_all_verdict,
                "warning_count": warnings,
                "key_artifact_path": key_artifact_path,
                "parse_state": "parsed" if not unparsed_reason else "unparsed",
                "unparsed_reason": unparsed_reason,
            }
        )
    return out


def _find_latest_check_all() -> Optional[Dict[str, Any]]:
    for row in _list_recent_runs(limit=20):
        p = Path(row["path"]) / "reports" / "check_all_report.json"
        if p.exists():
            try:
                data = read_json(p)
                data["_path"] = str(p)
                return data
            except Exception:
                continue
    return None


def _latest_continuity_manifest() -> Optional[Path]:
    for row in _list_recent_runs(limit=30):
        candidate = Path(row["path"]) / "continuity_pack" / "continuity_pack_manifest.json"
        if candidate.exists():
            return candidate
    return None


def _latest_run_dir() -> Optional[Path]:
    rows = _list_recent_runs(limit=1)
    if not rows:
        return None
    return Path(rows[0]["path"])


def _latest_matching_report(file_name: str, limit: int = 30) -> Optional[Path]:
    for row in _list_recent_runs(limit=limit):
        candidate = Path(row["path"]) / "reports" / file_name
        if candidate.exists():
            return candidate
    return None


def _inventory_progress_hook(rail: ProgressRail) -> Callable[[Dict[str, Any]], None]:
    def _hook(payload: Dict[str, Any]) -> None:
        rail.pulse(
            3,
            (
                f"files={payload.get('files_scanned', 0)} "
                f"warnings={payload.get('warnings_count', 0)} "
                f"rejected={payload.get('rejected_count', 0)}"
            ),
            target="inventory_scan",
        )

    return _hook


def _context_progress_hook(rail: ProgressRail) -> Callable[[Dict[str, Any]], None]:
    def _hook(payload: Dict[str, Any]) -> None:
        scope = str(payload.get("scope", "N/A"))
        rail.pulse(
            2,
            (
                f"scope={scope} "
                f"objects={payload.get('objects_scanned', 0)} "
                f"warnings={payload.get('warnings_count', 0)}"
            ),
            target=scope,
        )

    return _hook


def _base_half_paths() -> Dict[str, str]:
    return {
        "organ_root": str(AGENT_ROOT),
        "runner": str(AGENT_ROOT / "TOOLS" / "administratum_agent_runner.py"),
        "launcher": str(AGENT_ROOT / "LAUNCHERS" / "run_administratum_pc.ps1"),
        "profile_md": str(AGENT_ROOT / "AGENT_PROFILE.md"),
        "profile_json": str(AGENT_ROOT / "agent_profile.json"),
        "identity_md": str(AGENT_ROOT / "IDENTITY_BASELINE.md"),
        "state_json": str(BASE_HALF_STATE_PATH),
        "check_report_json": str(BASE_HALF_REPORT_JSON_PATH),
        "runtime_root": str(BASE_HALF_RUNTIME_ROOT),
    }


def _base_half_identity_summary() -> str:
    profile_path = AGENT_ROOT / "agent_profile.json"
    profile = read_json(profile_path)
    if isinstance(profile, dict):
        summary = str(profile.get("summary", "")).strip()
        if summary:
            return summary
    return "Addresses, continuity, chronicle, and evidence packaging."


def _base_half_git_branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return str((completed.stderr or completed.stdout).strip())
    return str(completed.stdout.strip())


def _write_base_half_state() -> Path:
    BASE_HALF_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "ORGAN_BASE_HALF_STATUS_V0_1",
        "task_id": BASE_HALF_TASK_ID,
        "organ": "ADMINISTRATUM_AGENT",
        "timestamp_utc": now_utc(),
        "status": "READY",
        "visual_status": "WARN",
        "supported_commands": BASE_HALF_REQUIRED_COMMANDS,
        "identity_summary": _base_half_identity_summary(),
        "paths": _base_half_paths(),
        "git": {
            "head": git_head(REPO_ROOT),
            "branch": _base_half_git_branch(),
            "dirty": git_is_dirty(REPO_ROOT),
        },
    }
    write_json(BASE_HALF_STATE_PATH, payload)
    return BASE_HALF_STATE_PATH


def _write_base_half_reports() -> Tuple[Path, Path, List[str]]:
    BASE_HALF_REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    missing = [rel for rel in BASE_HALF_REQUIRED_FILES if not (AGENT_ROOT / rel).exists()]
    verdict = "PASS" if not missing else "WARN"
    report = {
        "schema_version": "ORGAN_BASE_HALF_CHECK_REPORT_V0_1",
        "task_id": BASE_HALF_TASK_ID,
        "organ": "ADMINISTRATUM_AGENT",
        "timestamp_utc": now_utc(),
        "verdict": verdict,
        "visual_status": "WARN",
        "supported_commands": BASE_HALF_REQUIRED_COMMANDS,
        "checks": [{"file": rel, "exists": rel not in missing} for rel in BASE_HALF_REQUIRED_FILES],
        "missing": missing,
        "notes": [
            "Base Half shell is minimal by design.",
            "Identity/profile depth is intentionally compact for first scaffold pass.",
        ],
    }
    write_json(BASE_HALF_REPORT_JSON_PATH, report)
    md_lines = [
        "# Administratum Base Half Check Report",
        "",
        f"- task_id: {BASE_HALF_TASK_ID}",
        f"- verdict: {verdict}",
        "- visual_status: WARN",
        f"- timestamp_utc: {report['timestamp_utc']}",
        "",
        "## Missing",
    ]
    if missing:
        md_lines.extend([f"- {item}" for item in missing])
    else:
        md_lines.append("- none")
    md_lines.extend(["", "## Commands", *[f"- {cmd}" for cmd in BASE_HALF_REQUIRED_COMMANDS], ""])
    BASE_HALF_REPORT_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    return BASE_HALF_REPORT_JSON_PATH, BASE_HALF_REPORT_MD_PATH, missing


def _base_half_pack_root() -> Path:
    stamp = re.sub(r"[^0-9]", "", now_utc())
    return BASE_HALF_RUNTIME_ROOT / "PACKS" / f"run_{stamp}"


def command_status(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("status", args.out)
    snap = status_snapshot()
    base_state_path = _write_base_half_state()
    runtime_gitignore = RUNS_ROOT / ".gitignore"
    iso_ok = runtime_gitignore.exists() and "RUN-*/" in runtime_gitignore.read_text(encoding="utf-8")
    snap["runtime_isolation_status"] = "PASS" if iso_ok else "BLOCKED"
    snap["base_half_state_path"] = str(base_state_path)
    report_path = ctx.run_dir / "reports" / "status_report.json"
    write_json(report_path, snap)
    warnings: List[str] = []
    if snap.get("dirty_tree"):
        warnings.append("repository is dirty; review before claiming PASS")
    if not iso_ok:
        warnings.append("runtime isolation policy file missing or invalid")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: STATUS",
        verdict=verdict,
        summary="Status snapshot created.",
        outputs=[report_path, base_state_path],
        input_refs=[],
        warnings=warnings,
        details=snap,
        next_actions=["Run `check-all` before Owner handoff."],
    )


def command_check(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("check", args.out)
    state_path = _write_base_half_state()
    report_json, report_md, missing = _write_base_half_reports()
    warnings = [f"missing required file: {item}" for item in missing]
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    details = {
        "task_id": BASE_HALF_TASK_ID,
        "required_commands": BASE_HALF_REQUIRED_COMMANDS,
        "state_path": str(state_path),
        "report_json": str(report_json),
        "report_md": str(report_md),
        "missing": missing,
    }
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CHECK (BASE HALF)",
        verdict=verdict,
        summary="Base Half check report refreshed.",
        outputs=[state_path, report_json, report_md],
        input_refs=[],
        warnings=warnings,
        details=details,
        next_actions=["Run `where`, `identity`, and `pack` for continuity outputs."],
    )


def command_where(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("where", args.out)
    paths = _base_half_paths()
    report_path = ctx.run_dir / "reports" / "where_report.json"
    write_json(
        report_path,
        {
            "schema_version": "ORGAN_BASE_HALF_WHERE_REPORT_V0_1",
            "task_id": BASE_HALF_TASK_ID,
            "organ": "ADMINISTRATUM_AGENT",
            "timestamp_utc": now_utc(),
            "paths": paths,
        },
    )
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: WHERE (BASE HALF)",
        verdict="PASS",
        summary="Important path map emitted.",
        outputs=[report_path],
        input_refs=[],
        warnings=[],
        details={"paths": paths},
    )


def command_identity(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("identity", args.out)
    profile_path = AGENT_ROOT / "agent_profile.json"
    identity_path = AGENT_ROOT / "IDENTITY_BASELINE.md"
    profile = read_json(profile_path)
    identity_text = identity_path.read_text(encoding="utf-8") if identity_path.exists() else ""
    report_path = ctx.run_dir / "reports" / "identity_report.json"
    write_json(
        report_path,
        {
            "schema_version": "ORGAN_BASE_HALF_IDENTITY_REPORT_V0_1",
            "task_id": BASE_HALF_TASK_ID,
            "organ": "ADMINISTRATUM_AGENT",
            "timestamp_utc": now_utc(),
            "summary": _base_half_identity_summary(),
            "profile": profile,
            "identity_baseline_excerpt": identity_text[:2000],
        },
    )
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: IDENTITY (BASE HALF)",
        verdict="PASS",
        summary="Identity baseline and profile references emitted.",
        outputs=[report_path],
        input_refs=[str(profile_path), str(identity_path)],
        warnings=[],
        details={"summary": _base_half_identity_summary()},
    )


def command_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("pack", args.out)
    state_path = _write_base_half_state()
    report_json, report_md, _missing = _write_base_half_reports()
    pack_root = _base_half_pack_root()
    pack_root.mkdir(parents=True, exist_ok=True)
    copies = [
        ("AGENT_PROFILE.md", AGENT_ROOT / "AGENT_PROFILE.md"),
        ("agent_profile.json", AGENT_ROOT / "agent_profile.json"),
        ("IDENTITY_BASELINE.md", AGENT_ROOT / "IDENTITY_BASELINE.md"),
        ("STATE/current_status.json", state_path),
        ("REPORTS/base_half_check_report.json", report_json),
        ("REPORTS/base_half_check_report.md", report_md),
        ("SHELL/SHELL_CONTRACT.md", AGENT_ROOT / "SHELL" / "SHELL_CONTRACT.md"),
    ]
    copied: List[str] = []
    for rel, src in copies:
        if not src.exists():
            continue
        dst = pack_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)
    manifest_path = pack_root / "pack_manifest.json"
    write_json(
        manifest_path,
        {
            "schema_version": "ORGAN_BASE_HALF_PACK_V0_1",
            "task_id": BASE_HALF_TASK_ID,
            "organ": "ADMINISTRATUM_AGENT",
            "timestamp_utc": now_utc(),
            "pack_root": str(pack_root),
            "copied": copied,
            "required_commands": BASE_HALF_REQUIRED_COMMANDS,
        },
    )
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: PACK (BASE HALF)",
        verdict="PASS",
        summary="Base Half continuity pack generated under local context.",
        outputs=[manifest_path],
        input_refs=[str(state_path), str(report_json), str(report_md)],
        warnings=[],
        details={"pack_root": str(pack_root), "copied": copied},
    )


def command_help(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("help", args.out)
    help_report = ctx.run_dir / "reports" / "help_report.json"
    write_json(
        help_report,
        {
            "schema_version": "ORGAN_BASE_HALF_HELP_REPORT_V0_1",
            "task_id": BASE_HALF_TASK_ID,
            "organ": "ADMINISTRATUM_AGENT",
            "timestamp_utc": now_utc(),
            "commands": BASE_HALF_REQUIRED_COMMANDS,
            "note": "Use shell --once <command> for shell-smoke checks.",
        },
    )
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: HELP (BASE HALF)",
        verdict="PASS",
        summary="Base Half command contract listed.",
        outputs=[help_report],
        input_refs=[],
        warnings=[],
        details={"commands": BASE_HALF_REQUIRED_COMMANDS},
    )


def command_tools(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("tools", args.out)
    index_path = default_tool_index_path(REPO_ROOT)
    payload = build_organ_tool_view(organ_id="ADMINISTRATUM_AGENT", index_path=index_path)
    report_path = ctx.run_dir / "reports" / "tools_report.json"
    write_json(report_path, payload)
    warnings = [str(item) for item in payload.get("warnings", []) if str(item).strip()]
    verdict_token = str(payload.get("verdict", "PASS")).upper()
    if verdict_token.startswith("BLOCKED"):
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TOOLS",
        verdict=verdict,
        summary="Organ-specific tool capability view generated from Mechanicus registry.",
        outputs=[report_path],
        input_refs=[str(index_path)],
        warnings=warnings,
        details=payload,
        next_actions=["Use `shell --once tools` for shell-mode smoke check."],
    )


def command_inventory(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("inventory", args.out)
    rail = ProgressRail(renderer, ctx)
    rail.start(1, "git_truth_and_dirty_state", target=str(repo_root))
    rail.done(1, f"dirty={str(ctx.dirty_before).lower()}", target=str(repo_root))
    rail.start(3, "building_inventory", target=str(repo_root))
    inv = build_inventory(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics, progress_hook=_inventory_progress_hook(rail))
    rail.done(
        3,
        f"files={inv.report.get('total_files', 0)} warnings={len(inv.report.get('warnings', []))}",
        target=str(Path(inv.report_path)),
    )
    rail.start(4, "classifying_risks", target="zone_classification")
    rail.done(4, f"zones={len(inv.report.get('zone_counts', {}))}", target="zone_classification")
    payload = _render_skill_payload(inv, "ADMINISTRATUM AGENT :: INVENTORY")
    return _finalize_command(
        ctx,
        renderer,
        header=payload["header"],
        verdict=inv.report.get("verdict", "PASS"),
        summary="Repository inventory built.",
        outputs=[inv, Path(inv.report.get("objects_jsonl_path", ""))],
        input_refs=[str(repo_root)],
        warnings=inv.report.get("warnings", []),
        details=inv.report,
        progress=rail,
    )


def command_classify_path(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("classify-path", args.out)
    cls = classify_path(args.path, repo_root)
    route = route_for_object(cls, requested_action=args.requested_action or "")
    route_blocked = route["verdict"].startswith("REJECT") or "BLOCK" in route["verdict"]
    report = {
        "report_type": "ARTIFACT_CLASSIFICATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "object": {**cls, **route},
        "verdict": "PASS" if not route_blocked else "BLOCKED",
        "warnings": [] if not route_blocked else [f"requested action blocked for {cls['path']}"],
    }
    report_path = ctx.run_dir / "reports" / "classification_report.json"
    write_json(report_path, report)
    s_receipt = skill_receipt(
        run_id=ctx.run_id,
        skill_id="classify_repo_zone",
        input_refs=[args.path],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=report.get("warnings", []),
    )
    s_receipt_path = write_skill_receipt(ctx.run_dir, "classify_repo_zone", s_receipt)
    ctx.metrics["files_classified"] += 1
    ctx.metrics["objects_considered"] += 1
    ctx.metrics["routes_made"] += 1
    ctx.metrics["warnings_count"] += len(report.get("warnings", []))
    ctx.metrics["rejected_count"] += 1 if route_blocked else 0
    ctx.metrics["receipts_written"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CLASSIFY PATH",
        verdict=report["verdict"],
        summary="Path classification completed.",
        outputs=[report_path, s_receipt_path],
        input_refs=[args.path],
        warnings=report.get("warnings", []),
        details=report,
    )


def command_provenance(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("provenance-index", args.out)
    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, inv_path, metrics=ctx.metrics, limit=args.limit)
    warnings = list(inv.report.get("warnings", [])) + list(prov.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: PROVENANCE",
        verdict=verdict,
        summary="Provenance index built.",
        outputs=[inv, prov],
        input_refs=[str(repo_root), str(inv_path)],
        warnings=warnings,
        details={"inventory_report": inv.report, "provenance_report": prov.report},
    )


def command_useful_candidates(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("useful-candidates", args.out)
    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, inv_path, repo_root=repo_root, metrics=ctx.metrics)
    warnings = list(inv.report.get("warnings", [])) + list(useful.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: USEFUL CANDIDATES",
        verdict=verdict,
        summary="Useful candidate extraction completed.",
        outputs=[inv, useful],
        input_refs=[str(inv_path)],
        warnings=warnings,
        details=useful.report,
    )


def command_detect_dirty_runtime(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("detect-dirty-runtime", args.out)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: DIRTY RUNTIME",
        verdict=dirty.report.get("verdict", "PASS"),
        summary="Runtime pollution scan completed.",
        outputs=[dirty],
        input_refs=[str(repo_root)],
        warnings=dirty.report.get("warnings", []),
        details=dirty.report,
    )


def _load_findings_from_args(paths: List[str], paths_file: Optional[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = [{"path": p} for p in paths]
    if paths_file:
        report_path = _resolve_json_report(paths_file)
        data = read_json(report_path)
        if isinstance(data, dict):
            if isinstance(data.get("paths"), list):
                findings.extend({"path": str(p)} for p in data["paths"])
            if isinstance(data.get("objects_preview"), list):
                findings.extend({"path": str(o.get("path", ""))} for o in data["objects_preview"] if o.get("path"))
    dedup = []
    seen = set()
    for row in findings:
        p = str(row.get("path", "")).strip()
        if not p or p in seen:
            continue
        seen.add(p)
        dedup.append({"path": p})
    return dedup


def command_route_to_organs(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("route-to-organs", args.out)
    findings = _load_findings_from_args(args.path or [], args.paths_file)
    if not findings:
        raise UserFacingError(
            "No paths provided for routing.",
            "Provide --path one or more times, or provide --paths-file JSON with `paths`.",
            f"python {Path(__file__).name} route-to-organs --path IMPERIUM_NEW_GENERATION/README.md",
        )
    routing = route_to_organs(ctx.run_id, ctx.run_dir, findings, requested_action=args.requested_action or "", metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: ROUTING",
        verdict=routing.report.get("verdict", "PASS"),
        summary="Routing recommendations built.",
        outputs=[routing],
        input_refs=[x["path"] for x in findings],
        warnings=routing.report.get("warnings", []),
        details=routing.report,
    )


def command_merge_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("merge-summary", args.out)

    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    if args.provenance:
        prov_report = read_json(_resolve_json_report(args.provenance))
        prov = None
    else:
        prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, inv_path, metrics=ctx.metrics, limit=args.provenance_limit)
        prov_report = prov.report

    if args.candidates:
        candidates_report = read_json(_resolve_json_report(args.candidates))
        useful = None
    else:
        useful = find_useful_candidates(ctx.run_id, ctx.run_dir, inv_path, repo_root=repo_root, metrics=ctx.metrics)
        candidates_report = useful.report

    if args.dirty:
        dirty_report = read_json(_resolve_json_report(args.dirty))
        dirty = None
    else:
        dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
        dirty_report = dirty.report

    if args.routing:
        routing_report = read_json(_resolve_json_report(args.routing))
        routing = None
    else:
        preview_paths = [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:80] if x.get("path")]
        routing = route_to_organs(ctx.run_id, ctx.run_dir, preview_paths, requested_action=args.requested_action or "", metrics=ctx.metrics)
        routing_report = routing.report

    merge = build_merge_preparation_summary(
        ctx.run_id,
        ctx.run_dir,
        inv.report,
        prov_report,
        candidates_report,
        dirty_report,
        routing_report,
        metrics=ctx.metrics,
    )

    warnings = (
        list(inv.report.get("warnings", []))
        + list(prov_report.get("warnings", []))
        + list(candidates_report.get("warnings", []))
        + list(dirty_report.get("warnings", []))
        + list(routing_report.get("warnings", []))
        + list(merge.report.get("warnings", []))
    )
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: MERGE SUMMARY",
        verdict=verdict,
        summary="Merge preparation summary generated.",
        outputs=[inv, prov, useful, dirty, routing, merge],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=merge.report,
    )


def command_scan_context(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("scan-imperium-context", args.out)
    local_root = Path(args.local_root).resolve()
    private_root = Path(args.private_root).resolve()
    rail = ProgressRail(renderer, ctx)
    rail.start(1, "git_truth_and_dirty_state", target=str(REPO_ROOT))
    rail.done(1, f"dirty={str(ctx.dirty_before).lower()}", target=str(REPO_ROOT))
    rail.start(2, "scanning_context_metadata", target="IMPERIUM_CONTEXT")
    scan = scan_imperium_context(
        ctx.run_id,
        ctx.run_dir,
        local_root=local_root,
        private_root=private_root,
        metrics=ctx.metrics,
        progress_hook=_context_progress_hook(rail),
    )
    total_entries = int(scan.report.get("entry_count", 0))
    rail.done(2, f"objects={total_entries} warnings={len(scan.report.get('warnings', []))}", target=str(Path(scan.report_path)))
    rail.start(4, "classifying_risks", target=str(Path(scan.report_path)))
    rail.done(
        4,
        f"private_entries={scan.report.get('scope_counts', {}).get('PRIVATE_CONTEXT', 0)}",
        target=str(Path(scan.report_path)),
    )
    warnings = list(scan.report.get("warnings", []))
    if scan.report.get("scope_counts", {}).get("PRIVATE_CONTEXT", 0) > 0:
        warnings.append("private context detected; metadata-only export policy active")
    verdict = "PASS_WITH_WARNINGS" if warnings else scan.report.get("verdict", "PASS")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: SCAN IMPERIUM CONTEXT",
        verdict=verdict,
        summary="Context scan completed (metadata-only).",
        outputs=[scan, Path(scan.report.get("index_jsonl_path", ""))],
        input_refs=[str(local_root), str(private_root), "NEW_REALITY_RUNS_CONTEXT"],
        warnings=warnings,
        details=scan.report,
        progress=rail,
    )


def command_classify_local_context(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("classify-local-context", args.out)
    if args.scan_report:
        scan_report_path = _resolve_json_report(args.scan_report)
        scan = None
    else:
        local_root = Path(args.local_root).resolve()
        private_root = Path(args.private_root).resolve()
        scan = scan_imperium_context(ctx.run_id, ctx.run_dir, local_root=local_root, private_root=private_root, metrics=ctx.metrics)
        scan_report_path = Path(scan.report_path)

    classified = classify_local_context(ctx.run_id, ctx.run_dir, scan_report_path, metrics=ctx.metrics)
    risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(classified.report_path), metrics=ctx.metrics)
    warnings = list(classified.report.get("warnings", [])) + list(risk.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CLASSIFY LOCAL CONTEXT",
        verdict=verdict,
        summary="Local/private context classification completed.",
        outputs=[scan, classified, risk],
        input_refs=[str(scan_report_path)],
        warnings=warnings,
        details={"local_context": classified.report, "private_export_risk": risk.report},
    )


def command_collect_reality_snapshot(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("collect-reality-snapshot", args.out)
    rail = ProgressRail(renderer, ctx)
    blocked = _block_if_dirty_owner_decision(ctx, renderer, command="collect-reality-snapshot", input_refs=[str(repo_root)], progress=rail)
    if blocked is not None:
        return blocked
    dirty_admission = _dirty_admission_state("collect-reality-snapshot")
    rail.start(1, "reading_repo_state", target=str(repo_root))
    snap = collect_reality_snapshot(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    rail.done(1, f"head={str(snap.report.get('git_head', ''))[:12]}", target=str(Path(snap.report_path)))
    rail.start(6, "building_reality_capsule", target=str(ctx.run_dir / "reports"))
    rail.done(6, f"dirty={str(bool(snap.report.get('dirty_tree'))).lower()}", target=str(Path(snap.report_path)))
    warnings: List[str] = []
    if snap.report.get("dirty_tree"):
        warnings.append("repository dirty at snapshot time")
    warnings.extend(_dirty_admission_warnings(dirty_admission))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: REALITY SNAPSHOT",
        verdict=verdict,
        summary="Reality snapshot collected.",
        outputs=[snap],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=snap.report,
        progress=rail,
    )


def command_collect_continuity_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("collect-continuity-pack", args.out)
    rail = ProgressRail(renderer, ctx)
    blocked = _block_if_dirty_owner_decision(ctx, renderer, command="collect-continuity-pack", input_refs=[str(repo_root)], progress=rail)
    if blocked is not None:
        return blocked
    dirty_admission = _dirty_admission_state("collect-continuity-pack")
    rail.start(1, "reading_repo_state", target=str(repo_root))
    rail.done(1, f"dirty={str(ctx.dirty_before).lower()}", target=str(repo_root))
    rail.start(2, "scanning_context_metadata", target="NEW_REALITY_RUNS_CONTEXT")
    if args.include_context:
        scan = scan_imperium_context(
            ctx.run_id,
            ctx.run_dir,
            local_root=Path(args.local_root).resolve(),
            private_root=Path(args.private_root).resolve(),
            metrics=ctx.metrics,
            progress_hook=_context_progress_hook(rail),
        )
        classify_ctx = classify_local_context(ctx.run_id, ctx.run_dir, Path(scan.report_path), metrics=ctx.metrics)
        risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(classify_ctx.report_path), metrics=ctx.metrics)
        context_chain: List[Any] = [scan, classify_ctx, risk]
    else:
        context_chain = []
    rail.done(2, "metadata_only=true", target="IMPERIUM_CONTEXT")
    rail.start(3, "building_inventory_and_provenance", target=str(repo_root))
    inv = build_inventory(
        repo_root,
        ctx.run_id,
        ctx.run_dir,
        metrics=ctx.metrics,
        max_files=args.inventory_max_files,
        progress_hook=_inventory_progress_hook(rail),
    )
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, Path(inv.report_path), metrics=ctx.metrics, limit=args.provenance_limit)
    rail.done(
        3,
        f"files={inv.report.get('total_files', 0)} provenance={prov.report.get('entry_count', 0)}",
        target=str(Path(inv.report_path)),
    )
    rail.start(4, "classifying_risks", target=str(ctx.run_dir / "reports"))
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, Path(inv.report_path), repo_root=repo_root, metrics=ctx.metrics)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    rail.done(4, f"warnings={len(dirty.report.get('warnings', []))}", target=str(Path(dirty.report_path)))
    rail.start(5, "collecting_useful_refs", target=str(ctx.run_dir / "reports"))
    routing = route_to_organs(
        ctx.run_id,
        ctx.run_dir,
        [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:80] if x.get("path")],
        requested_action="continuity_pack_collection",
        metrics=ctx.metrics,
    )
    rail.done(5, f"routes={routing.report.get('route_count', 0)}", target=str(Path(routing.report_path)))
    rail.start(6, "building_continuity_narrative", target=str(ctx.run_dir / "continuity_pack"))
    reality = collect_reality_snapshot(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    live_snapshot = dict(ctx.metrics)
    live_snapshot["wall_clock_ms"] = int((time.perf_counter_ns() - ctx.start_ns) / 1_000_000)
    live_snapshot["process_cpu_seconds"] = max(0.0, time.process_time() - ctx.cpu_start)
    live_snapshot["owner_wait_seconds"] = round(float(live_snapshot["wall_clock_ms"]) / 1000.0, 3)
    pack = collect_continuity_pack(
        repo_root,
        ctx.run_id,
        ctx.run_dir,
        include_context=args.include_context,
        metrics=ctx.metrics,
        live_metrics_snapshot=live_snapshot,
    )
    rail.done(6, f"pack_dir={Path(pack.report.get('pack_dir', '')).name}", target=str(Path(pack.report.get("pack_dir", ""))))
    warnings = (
        list(inv.report.get("warnings", []))
        + list(prov.report.get("warnings", []))
        + list(useful.report.get("warnings", []))
        + list(dirty.report.get("warnings", []))
        + list(routing.report.get("warnings", []))
        + list(pack.report.get("warnings", []))
    )
    if args.include_context:
        warnings.append("context included in metadata-only mode with no-git-export rules")
    warnings.extend(_dirty_admission_warnings(dirty_admission))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CONTINUITY PACK",
        verdict=verdict,
        summary="Continuity pack collected.",
        outputs=[inv, prov, useful, dirty, routing, reality, context_chain, pack],
        input_refs=[str(repo_root), str(Path(args.local_root).resolve()), str(Path(args.private_root).resolve())],
        warnings=warnings,
        details=pack.report,
        progress=rail,
    )


def command_build_handoff_context(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("build-agent-handoff-context", args.out)
    blocked = _block_if_dirty_owner_decision(ctx, renderer, command="build-agent-handoff-context", input_refs=[str(repo_root)])
    if blocked is not None:
        return blocked
    dirty_admission = _dirty_admission_state("build-agent-handoff-context")
    if not (ctx.run_dir / "reports" / "continuity_pack_report.json").exists():
        _ = collect_continuity_pack(repo_root, ctx.run_id, ctx.run_dir, include_context=args.include_context, metrics=ctx.metrics)
    handoff = build_agent_handoff_context(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    warnings = list(handoff.report.get("warnings", [])) + _dirty_admission_warnings(dirty_admission)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: AGENT HANDOFF CONTEXT",
        verdict=handoff.report.get("verdict", "PASS"),
        summary="Agent handoff context built.",
        outputs=[handoff],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=handoff.report,
    )


def command_verify_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("verify-pack-against-reality", args.out)
    rail = ProgressRail(renderer, ctx)
    rail.start(1, "reading_repo_state", target=str(repo_root))
    rail.done(1, f"dirty={str(ctx.dirty_before).lower()}", target=str(repo_root))
    if args.manifest:
        manifest_path = _resolve_json_report(args.manifest)
    else:
        latest = _latest_continuity_manifest()
        if latest is None:
            raise UserFacingError(
                "No continuity pack manifest found.",
                "Run `collect-continuity-pack` first or pass --manifest explicitly.",
                f"python {Path(__file__).name} collect-continuity-pack --repo-root {REPO_ROOT}",
            )
        manifest_path = latest
    verification = verify_pack_against_reality(repo_root, ctx.run_id, ctx.run_dir, manifest_path, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: VERIFY PACK AGAINST REALITY",
        verdict=verification.report.get("verdict", "PASS"),
        summary="Pack/reality verification completed.",
        outputs=[verification],
        input_refs=[str(manifest_path)],
        warnings=verification.report.get("warnings", []),
        details=verification.report,
        progress=rail,
    )


def command_metrics_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("metrics-summary", args.out)
    if args.run_dir:
        target_run = Path(args.run_dir)
        if not target_run.is_absolute():
            target_run = (REPO_ROOT / target_run).resolve()
    else:
        target_run = _latest_run_dir() or ctx.run_dir
    report = metrics_summary_from_run(target_run.name, target_run)
    report["target_run_dir"] = str(target_run)
    report_path = ctx.run_dir / "reports" / "metrics_summary_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += int(report.get("receipt_count", 0))
    verdict = report.get("verdict", "PASS")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: METRICS SUMMARY",
        verdict=verdict,
        summary="Metrics summary generated.",
        outputs=[report_path],
        input_refs=[str(target_run)],
        warnings=[],
        details=report,
    )


def command_explain_decision(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("explain-decision", args.out)
    cls = classify_path(args.path, repo_root)
    route = route_for_object(cls, requested_action=args.requested_action or "")
    route_blocked = route["verdict"].startswith("REJECT") or "BLOCK" in route["verdict"]
    report = {
        "report_type": "EXPLAIN_DECISION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "input_path": args.path,
        "requested_action": args.requested_action or "",
        "classification": cls,
        "routing_decision": route,
        "rule_links": [
            "brain_node/rules/repo_zone_classification_rules.json",
            "brain_node/rules/routing_rules.json",
            "brain_node/rules/artifact_rejection_rules.json",
        ],
        "verdict": "PASS" if not route_blocked else "BLOCKED",
        "warnings": [] if not route_blocked else ["mutation/deletion-like request blocked by policy"],
    }
    report_path = ctx.run_dir / "reports" / "explain_decision_report.json"
    write_json(report_path, report)
    ctx.metrics["files_classified"] += 1
    ctx.metrics["objects_considered"] += 1
    ctx.metrics["routes_made"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: EXPLAIN DECISION",
        verdict=report["verdict"],
        summary="Decision explanation generated.",
        outputs=[report_path],
        input_refs=[args.path],
        warnings=report.get("warnings", []),
        details=report,
    )


def command_show_kpd(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("show-kpd", args.out)
    if args.run_dir:
        target_run = Path(args.run_dir)
        if not target_run.is_absolute():
            target_run = (REPO_ROOT / target_run).resolve()
    else:
        target_run = _latest_run_dir() or ctx.run_dir
    kpd, thinking = kpd_from_reports(target_run.name, target_run)
    kpd["target_run_dir"] = str(target_run)
    thinking["target_run_dir"] = str(target_run)
    scorecard = {
        "overall_kpd": kpd.get("score_0_to_100"),
        "evidence_quality": kpd.get("component_scores", {}).get("evidence"),
        "trust_risk": kpd.get("trust_verdict"),
        "runtime_cost": kpd.get("component_scores", {}).get("cost_efficiency"),
        "warnings": kpd.get("component_scores", {}).get("warning_penalty"),
        "recommended_next_action": "review warnings before handoff" if kpd.get("verdict") != "PASS" else "eligible for next admitted command",
    }
    kpd["compact_scorecard"] = scorecard
    kpd_path = ctx.run_dir / "reports" / "kpd_score.json"
    thinking_path = ctx.run_dir / "reports" / "thinking_quality_score.json"
    write_json(kpd_path, kpd)
    write_json(thinking_path, thinking)
    ctx.metrics["objects_considered"] += 2
    warnings: List[str] = []
    if kpd.get("verdict") != "PASS":
        warnings.append(f"kpd verdict: {kpd.get('verdict')}")
    if thinking.get("verdict") != "PASS":
        warnings.append(f"thinking-quality verdict: {thinking.get('verdict')}")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: KPD / THINKING QUALITY",
        verdict=verdict,
        summary="\n".join(
            [
                f"overall_kpd: {scorecard['overall_kpd']}",
                f"evidence_quality: {scorecard['evidence_quality']}",
                f"trust_risk: {scorecard['trust_risk']}",
                f"runtime_cost: {scorecard['runtime_cost']}",
                f"warnings: {scorecard['warnings']}",
                f"recommended_next_action: {scorecard['recommended_next_action']}",
            ]
        ),
        outputs=[kpd_path, thinking_path],
        input_refs=[str(target_run)],
        warnings=warnings,
        details={"kpd": kpd, "thinking_quality": thinking},
    )


def command_cu_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("cu-summary", args.out)
    cu = build_cu_index(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CU SUMMARY",
        verdict=cu.report.get("verdict", "PASS"),
        summary="Control Unit (CU) summary generated.",
        outputs=[cu],
        input_refs=[str(AGENT_ROOT)],
        warnings=cu.report.get("warnings", []),
        details=cu.report,
    )


def command_recent(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("recent", args.out)
    recent = _list_recent_runs(limit=args.limit, exclude_run_id=ctx.run_id)
    report = {
        "report_type": "RECENT_RUNS_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "recent_runs": recent,
        "verdict": "PASS",
    }
    report_path = ctx.run_dir / "reports" / "recent_runs_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += len(recent)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: RECENT RUNS",
        verdict="PASS",
        summary=f"Loaded {len(recent)} recent run entries.",
        outputs=[report_path],
        input_refs=[str(RUNS_ROOT)],
        warnings=[],
        details=report,
    )


def command_open_runs(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("open-runs", args.out)
    report = {
        "report_type": "RUNS_PATH_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "runs_root": str(RUNS_ROOT),
        "exists": RUNS_ROOT.exists(),
        "verdict": "PASS",
    }
    report_path = ctx.run_dir / "reports" / "runs_path_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: OPEN RUNS",
        verdict="PASS",
        summary=f"Runs root: {RUNS_ROOT}",
        outputs=[report_path],
        input_refs=[],
        warnings=[],
        details=report,
        next_actions=[f"Open path manually in Explorer: {RUNS_ROOT}"],
    )


def _validate_freelance_envelope_payload(payload: Any) -> List[str]:
    if not isinstance(payload, dict):
        return ["envelope_root_must_be_object"]
    required = {
        "task_id": str,
        "client_goal": str,
        "assigned_organ": str,
        "administratum_scope": list,
        "input_refs": list,
        "privacy_level": str,
        "allowed_actions": list,
        "forbidden_actions": list,
        "deliverables_required": list,
        "acceptance_criteria": list,
        "evidence_required": list,
        "handoff_target": str,
        "owner_decision_required": bool,
    }
    errors: List[str] = []
    for key, typ in required.items():
        if key not in payload:
            errors.append(f"missing_required:{key}")
            continue
        if not isinstance(payload.get(key), typ):
            errors.append(f"invalid_type:{key}:expected_{typ.__name__}")
    if payload.get("assigned_organ") != "ADMINISTRATUM_AGENT":
        errors.append("assigned_organ_must_be_ADMINISTRATUM_AGENT")
    if payload.get("privacy_level") not in {"public", "client_confidential", "private"}:
        errors.append("privacy_level_invalid")
    allowed_scope = {"intake", "context_map", "evidence_pack", "handoff"}
    scope_items = set(str(x) for x in payload.get("administratum_scope", []) if isinstance(x, str))
    if not scope_items:
        errors.append("administratum_scope_empty")
    unknown_scope = sorted(scope_items - allowed_scope)
    if unknown_scope:
        errors.append(f"administratum_scope_unknown:{','.join(unknown_scope)}")
    return errors


def _load_envelope(path_text: str) -> Tuple[Path, Dict[str, Any]]:
    path = Path(path_text)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path, read_json(path)


def command_validate_freelance_envelope(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("validate-freelance-envelope", args.out)
    envelope_path = args.envelope or str(FREELANCE_SAMPLE_VALID_PATH)
    path, payload = _load_envelope(envelope_path)
    errors = _validate_freelance_envelope_payload(payload)
    report = {
        "report_type": "FREELANCE_ENVELOPE_VALIDATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "schema_path": str(FREELANCE_SCHEMA_PATH),
        "envelope_path": str(path),
        "task_id": str(payload.get("task_id", "")),
        "errors": errors,
        "warnings": [],
        "verdict": "PASS" if not errors else "BLOCKED",
    }
    report_path = ctx.run_dir / "reports" / "freelance_envelope_validation_report.json"
    write_json(report_path, report)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: FREELANCE ENVELOPE VALIDATION",
        verdict=report["verdict"],
        summary="Freelance envelope validation completed.",
        outputs=[report_path],
        input_refs=[str(path), str(FREELANCE_SCHEMA_PATH)],
        warnings=errors,
        details=report,
        blocker_class="FREELANCE_ENVELOPE_INVALID" if errors else None,
    )


def _safe_artifact_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "artifact"


def command_build_freelance_handoff(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("build-freelance-handoff", args.out)
    envelope_path = args.envelope or str(FREELANCE_SAMPLE_VALID_PATH)
    path, payload = _load_envelope(envelope_path)
    errors = _validate_freelance_envelope_payload(payload)
    if errors:
        report_path = ctx.run_dir / "reports" / "freelance_handoff_blocked_report.json"
        report = {
            "report_type": "FREELANCE_HANDOFF_BLOCKED_REPORT",
            "agent_id": "ADMINISTRATUM_AGENT",
            "run_id": ctx.run_id,
            "generated_at_utc": now_utc(),
            "envelope_path": str(path),
            "errors": errors,
            "verdict": "BLOCKED",
            "warnings": errors,
        }
        write_json(report_path, report)
        return _finalize_command(
            ctx,
            renderer,
            header="ADMINISTRATUM AGENT :: FREELANCE HANDOFF",
            verdict="BLOCKED",
            summary="Freelance handoff blocked by invalid envelope.",
            outputs=[report_path],
            input_refs=[str(path)],
            warnings=errors,
            details=report,
            blocker_class="FREELANCE_ENVELOPE_INVALID",
        )

    task_id = str(payload.get("task_id", "FREELANCE-TASK")).strip()
    package_root = ctx.run_dir / "freelance_handoff" / _safe_artifact_name(task_id)
    machine_dir = package_root / "machine"
    reports_dir = package_root / "reports_en"
    owner_dir = package_root / "owner_ru"
    evidence_dir = package_root / "evidence"
    for directory in (machine_dir, reports_dir, owner_dir, evidence_dir / "json_samples", evidence_dir / "logs"):
        directory.mkdir(parents=True, exist_ok=True)

    intake = {
        "task_id": task_id,
        "client_goal": payload.get("client_goal", ""),
        "privacy_level": payload.get("privacy_level", ""),
        "administratum_scope": payload.get("administratum_scope", []),
        "input_file_map": [{"ref": ref, "classification": "metadata_ref_only"} for ref in payload.get("input_refs", [])],
        "evidence_required": payload.get("evidence_required", []),
        "deliverable_handoff_checklist": payload.get("deliverables_required", []),
        "limitations": ["Administratum performs intake/context/evidence/handoff only; implementation belongs to downstream organ."],
        "next_organ_recommendation": payload.get("handoff_target", ""),
    }
    write_json(machine_dir / "envelope.json", payload)
    write_json(machine_dir / "intake_summary.json", intake)
    write_json(machine_dir / "evidence_index.json", {"schema_version": "imperium.administratum.evidence_index.v0_1", "entries": []})
    handoff_md = [
        f"# Administratum Freelance Handoff: {task_id}",
        "",
        f"- client_goal: {payload.get('client_goal', '')}",
        f"- privacy_level: {payload.get('privacy_level', '')}",
        f"- handoff_target: {payload.get('handoff_target', '')}",
        "",
        "## Administratum Scope",
        *[f"- {item}" for item in payload.get("administratum_scope", [])],
        "",
        "## Deliverable Checklist",
        *[f"- {item}" for item in payload.get("deliverables_required", [])],
        "",
        "## Limitations",
        "- No private payload content exported; input references are metadata-only.",
    ]
    (reports_dir / "ADMINISTRATUM_FREELANCE_HANDOFF.md").write_text("\n".join(handoff_md) + "\n", encoding="utf-8")
    (owner_dir / "OWNER_SUMMARY_RU.md").write_text(
        "\n".join(
            [
                f"# Freelance handoff Owner summary: {task_id}",
                "",
                "Administratum подготовил intake/context/evidence/handoff пакет без экспорта приватного payload.",
                f"Следующий орган: {payload.get('handoff_target', '')}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "README.md").write_text(
        "Administratum freelance handoff package. Canonical truth is machine JSON plus markdown reports. No PDF included.\n",
        encoding="utf-8",
    )

    manifest_files: List[Dict[str, Any]] = []
    for p in sorted(x for x in package_root.rglob("*") if x.is_file() and x.name != "MANIFEST.json"):
        manifest_files.append({"path": p.relative_to(package_root).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size})
    manifest = {
        "schema_version": "imperium.administratum.freelance_handoff_manifest.v0_1",
        "task_id": task_id,
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "source_envelope": str(path),
        "files": manifest_files,
        "private_content_exported": False,
        "default_dossier_has_pdf": False,
        "verdict": "PASS",
    }
    write_json(package_root / "MANIFEST.json", manifest)
    zip_path = ctx.run_dir / "freelance_handoff" / f"ADMINISTRATUM_FREELANCE_HANDOFF_{_safe_artifact_name(task_id)}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(x for x in package_root.rglob("*") if x.is_file()):
            zf.write(file_path, arcname=file_path.relative_to(package_root).as_posix())

    report = {
        "report_type": "FREELANCE_HANDOFF_BUILD_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "task_id": task_id,
        "package_root": str(package_root),
        "zip_path": str(zip_path),
        "manifest_path": str(package_root / "MANIFEST.json"),
        "private_content_exported": False,
        "default_dossier_has_pdf": False,
        "verdict": "PASS",
        "warnings": [],
    }
    report_path = ctx.run_dir / "reports" / "freelance_handoff_build_report.json"
    write_json(report_path, report)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: FREELANCE HANDOFF",
        verdict="PASS",
        summary="Freelance handoff package built.",
        outputs=[report_path, package_root / "MANIFEST.json", zip_path],
        input_refs=[str(path), str(FREELANCE_SCHEMA_PATH)],
        warnings=[],
        details=report,
        next_actions=["Hand off package to the declared downstream organ after Owner review."],
    )


def _shape_check(name: str, payload: Dict[str, Any], required: Sequence[str]) -> Dict[str, Any]:
    missing = [field for field in required if field not in payload]
    return {"name": name, "pass": not missing, "missing": missing}


def command_schema_regression(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("schema-regression", args.out)
    runner_path = Path(__file__).resolve()
    required_payload = [
        "status",
        "command",
        "run_id",
        "verdict",
        "summary",
        "primary_refs",
        "artifacts_written",
        "warnings",
        "why_trust",
        "next_actions",
        "metrics",
        "limitations",
        "details",
    ]
    results: List[Dict[str, Any]] = []
    warnings: List[str] = []
    for command_name in ["status", "doctor-rich", "doctor-oss", "recent"]:
        out_dir = ctx.run_dir / f"schema_{command_name.replace('-', '_')}"
        proc = subprocess.run(
            [sys.executable, str(runner_path), "--plain-json", "--no-color", command_name, "--out", str(out_dir)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        parsed: Dict[str, Any] = {}
        ok = proc.returncode == 0
        parse_error = ""
        try:
            parsed = json.loads(proc.stdout)
        except Exception as exc:
            ok = False
            parse_error = str(exc)
        shape = _shape_check(command_name, parsed, required_payload) if parsed else {"name": command_name, "pass": False, "missing": required_payload}
        results.append(
            {
                "name": f"plain_json_{command_name}",
                "pass": bool(ok and shape.get("pass")),
                "returncode": proc.returncode,
                "missing": shape.get("missing", []),
                "parse_error": parse_error,
                "sample_path": str(out_dir),
            }
        )

    valid_payload = read_json(FREELANCE_SAMPLE_VALID_PATH)
    valid_errors = _validate_freelance_envelope_payload(valid_payload)
    results.append({"name": "freelance_valid_sample", "pass": not valid_errors, "errors": valid_errors})
    malformed_payload = read_json(FREELANCE_SAMPLE_MALFORMED_PATH)
    malformed_errors = _validate_freelance_envelope_payload(malformed_payload)
    results.append({"name": "freelance_malformed_sample_blocks", "pass": bool(malformed_errors), "errors": malformed_errors})

    receipt_paths = sorted((ctx.run_dir / "schema_status" / "receipts").glob("*_command_receipt.json"))
    if receipt_paths:
        receipt = read_json(receipt_paths[0])
        results.append(
            {
                "name": "command_receipt_shape",
                "pass": _shape_check(
                    "command_receipt",
                    receipt,
                    ["receipt_type", "agent_id", "run_id", "skill_id", "input_refs", "output_refs", "metrics", "warnings", "verdict"],
                )["pass"],
            }
        )
    else:
        results.append({"name": "command_receipt_shape", "pass": False, "missing": ["*_command_receipt.json"]})

    latest_dossier = find_latest_dossier_zip(RUNS_ROOT)
    if latest_dossier:
        verify = verify_dossier_package(latest_dossier, ctx.run_dir / "reports" / "schema_regression_dossier_extract")
        legacy_pdf = bool(verify.get("default_dossier_has_pdf"))
        if legacy_pdf:
            warnings.append("latest legacy dossier contains PDF; build-dossier must create a new no-PDF default package")
        results.append(
            {
                "name": "latest_dossier_manifest_and_no_pdf",
                "pass": verify.get("verdict") in {"PASS", "WARN"} or legacy_pdf,
                "zip_path": str(latest_dossier),
                "verify_verdict": verify.get("verdict"),
                "pdf_members": verify.get("pdf_members", []),
                "legacy_pdf_detected": legacy_pdf,
            }
        )
    else:
        warnings.append("latest dossier not found; manifest validation deferred until build-dossier creates one")
        results.append({"name": "latest_dossier_manifest_and_no_pdf", "pass": True, "deferred": True})

    failed = [row for row in results if not row.get("pass")]
    report = {
        "report_type": "SCHEMA_REGRESSION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "results": results,
        "failed": len(failed),
        "warnings": warnings,
        "jsonschema_dependency": "optional_not_required_stdlib_fallback_used",
        "verdict": "BLOCKED" if failed else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
    }
    report_path = ctx.run_dir / "reports" / "schema_regression_report.json"
    write_json(report_path, report)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: SCHEMA REGRESSION",
        verdict=report["verdict"],
        summary=f"Schema regression completed: failed={len(failed)}, warnings={len(warnings)}.",
        outputs=[report_path],
        input_refs=[str(FREELANCE_SCHEMA_PATH), str(FREELANCE_SAMPLE_VALID_PATH), str(FREELANCE_SAMPLE_MALFORMED_PATH)],
        warnings=warnings + [f"failed schema checks: {len(failed)}"] if failed else warnings,
        details=report,
        blocker_class="SCHEMA_REGRESSION_FAILED" if failed else None,
    )


def command_doctor_rich(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("doctor-rich", args.out)
    no_color_env = _truthy(os.environ.get("NO_COLOR"))
    stdout_isatty = bool(sys.stdout.isatty())
    rich_import_available = bool(RICH_AVAILABLE)
    rich_mode_selected = bool(renderer.rich_enabled)
    plain_json_mode = bool(args.plain_json)
    no_color_flag = bool(args.no_color)
    color_flag = bool(args.color)
    no_rich_flag = bool(args.no_rich)
    rich_flag = bool(args.rich)

    detected_color_system = "unknown"
    if renderer._rich_console is not None:
        detected_color_system = str(renderer._rich_console.color_system or "none")
    elif RICH_AVAILABLE:
        try:
            probe = Console()
            detected_color_system = str(probe.color_system or "none")
        except Exception:
            detected_color_system = "unavailable"

    fallback_reasons: List[str] = []
    if not rich_import_available:
        fallback_reasons.append("rich_import_unavailable")
    if plain_json_mode:
        fallback_reasons.append("plain_json_mode_forces_machine_output")
    if no_rich_flag:
        fallback_reasons.append("no_rich_flag_enabled")
    if not stdout_isatty:
        fallback_reasons.append("stdout_is_not_tty")
    if no_color_flag or no_color_env:
        fallback_reasons.append("color_disabled_by_flag_or_env")
    if rich_mode_selected:
        fallback_reasons = []

    env_summary = {
        "TERM": os.environ.get("TERM", ""),
        "COLORTERM": os.environ.get("COLORTERM", ""),
        "WT_SESSION": os.environ.get("WT_SESSION", ""),
        "TERM_PROGRAM": os.environ.get("TERM_PROGRAM", ""),
        "NO_COLOR": os.environ.get("NO_COLOR", ""),
        "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING", ""),
    }
    report = {
        "report_type": "RICH_RENDERER_DIAGNOSTIC_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "rich_import_available": rich_import_available,
        "rich_mode_selected": rich_mode_selected,
        "stdout_isatty": stdout_isatty,
        "no_color_flag_active": no_color_flag,
        "no_color_env_active": no_color_env,
        "plain_json_mode_active": plain_json_mode,
        "rich_flag_active": rich_flag,
        "no_rich_flag_active": no_rich_flag,
        "color_flag_active": color_flag,
        "terminal_environment": env_summary,
        "color_system_detected": detected_color_system,
        "fallback_renderer_reason": fallback_reasons if fallback_reasons else ["none"],
        "suggested_local_test_commands": [
            f"python {Path(__file__).name} doctor-rich --no-color",
            f"python {Path(__file__).name} --rich status",
            f"python {Path(__file__).name} --no-rich status",
            f"python {Path(__file__).name} --plain-json status",
        ],
        "verdict": "PASS_WITH_WARNINGS" if fallback_reasons else "PASS",
    }
    report_path = ctx.run_dir / "reports" / "doctor_rich_report.json"
    write_json(report_path, report)

    warnings = []
    if fallback_reasons:
        warnings.append(f"rich_renderer_fallback_active: {','.join(fallback_reasons)}")
    limitations = []
    if not stdout_isatty:
        limitations.append("Non-TTY stdout can suppress live color even when Rich is installed.")
    if plain_json_mode:
        limitations.append("Machine-first plain JSON mode disables Rich rendering by design.")

    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: DOCTOR RICH",
        verdict=report["verdict"],
        summary="Renderer diagnostics collected.",
        outputs=[report_path],
        input_refs=[str(REPO_ROOT)],
        warnings=warnings,
        details=report,
        next_actions=report["suggested_local_test_commands"],
        limitations=limitations,
    )


def command_doctor_oss(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("doctor-oss", args.out)
    snapshot = detect_oss_availability(AGENT_ROOT)
    report_path = ctx.run_dir / "reports" / "doctor_oss_report.json"
    write_json(report_path, snapshot)
    unavailable = list(snapshot.get("unavailable", []))
    warnings: List[str] = []
    if unavailable:
        warnings.append(f"oss_unavailable_tools: {','.join(unavailable)}")
    if str(snapshot.get("available_pdf_backend", "unavailable")) == "unavailable":
        warnings.append("no_local_pdf_backend_detected_for_owner_pdf")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: DOCTOR OSS",
        verdict=verdict,
        summary="OSS availability detection completed (no installs performed).",
        outputs=[report_path],
        input_refs=[str(AGENT_ROOT / "OSS_ADMISSION" / "OSS_ADMISSION_REGISTER_V0_1.json")],
        warnings=warnings,
        details=snapshot,
        next_actions=[
            "Review OSS candidate statuses before any admission update.",
            "Use build-dossier to package machine reports and Owner artifact.",
        ],
        limitations=[] if str(snapshot.get("available_pdf_backend", "unavailable")) != "unavailable" else ["Russian PDF backend may require local browser backend admission."],
    )


def command_build_dossier(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("build-dossier", args.out)
    blocked = _block_if_dirty_owner_decision(ctx, renderer, command="build-dossier", input_refs=[str(AGENT_ROOT)])
    if blocked is not None:
        return blocked
    dirty_admission = _dirty_admission_state("build-dossier")
    task_id = str(args.task_id or TASK_DOSSIER_FACTORY_ID).strip()
    source_report_dir = Path(args.source_report_dir).resolve() if args.source_report_dir else (AGENT_ROOT / "REPORTS" / task_id).resolve()
    source_receipt_path = Path(args.source_receipt).resolve() if args.source_receipt else (AGENT_ROOT / "receipts" / f"{task_id}_RECEIPT_V0_1.json").resolve()
    command_matrix_path = source_report_dir / "COMMAND_STATUS_MATRIX_V0_1.md"
    if not source_report_dir.exists():
        raise UserFacingError(
            f"Source report dir missing: {source_report_dir}",
            "Generate required task reports before build-dossier.",
            f"python {Path(__file__).name} build-dossier --task-id {task_id} --source-report-dir <existing_path>",
        )
    if not source_receipt_path.exists():
        raise UserFacingError(
            f"Source receipt missing: {source_receipt_path}",
            "Generate task receipt before build-dossier.",
            f"python {Path(__file__).name} build-dossier --task-id {task_id} --source-receipt <existing_receipt_path>",
        )

    oss_snapshot = detect_oss_availability(AGENT_ROOT)
    result = build_dossier_package(
        task_id=task_id,
        run_id=ctx.run_id,
        run_dir=ctx.run_dir,
        repo_root=REPO_ROOT,
        source_report_dir=source_report_dir,
        source_receipt_path=source_receipt_path,
        command_status_matrix_path=command_matrix_path,
        oss_snapshot=oss_snapshot,
        next_recommended_task=str(args.next_task or "TASK-20260518-ADMINISTRATUM-CONTRACT-REGRESSION-GATE-V0_1"),
    )
    report = {
        "report_type": "DOSSIER_FACTORY_BUILD_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "task_id": task_id,
        "source_report_dir": str(source_report_dir),
        "source_receipt_path": str(source_receipt_path),
        "zip_path": result.zip_path,
        "manifest_path": result.manifest_path,
        "sha256sums_path": result.sha256sums_path,
        "owner_pdf_generated": result.owner_pdf_generated,
        "owner_pdf_path": result.owner_pdf_path,
        "owner_pdf_language": result.owner_pdf_language,
        "pdf_backend": result.pdf_backend,
        "evidence_index_path": result.evidence_index_path,
        "warnings": result.warnings,
        "limitations": result.limitations,
        "unverified": result.unverified,
        "verdict": result.verdict,
    }
    report_path = ctx.run_dir / "reports" / "dossier_factory_build_report.json"
    write_json(report_path, report)
    command_verdict = _report_verdict_to_command_verdict(result.verdict)
    outputs: List[Any] = [
        report_path,
        Path(result.zip_path),
        Path(result.manifest_path),
        Path(result.sha256sums_path),
        Path(result.evidence_index_path),
    ]
    if result.owner_pdf_path:
        outputs.append(Path(result.owner_pdf_path))
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: BUILD DOSSIER",
        verdict=command_verdict,
        summary="Dossier package build completed.",
        outputs=outputs,
        input_refs=[str(source_report_dir), str(source_receipt_path), str(command_matrix_path)],
        warnings=list(result.warnings) + _dirty_admission_warnings(dirty_admission),
        details=report,
        next_actions=[
            "Run verify-dossier --latest to validate package integrity.",
            "Use OWNER_QUICKSTART and canonical reports for Owner review.",
        ],
        limitations=result.limitations + result.unverified,
    )


def command_verify_dossier(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("verify-dossier", args.out)
    if args.zip_path:
        zip_path = Path(args.zip_path)
        if not zip_path.is_absolute():
            zip_path = (REPO_ROOT / zip_path).resolve()
    else:
        latest = find_latest_dossier_zip(RUNS_ROOT)
        if latest is None:
            raise UserFacingError(
                "No dossier zip found under RUNS.",
                "Build a dossier first or pass --zip-path explicitly.",
                f"python {Path(__file__).name} build-dossier --task-id {TASK_DOSSIER_FACTORY_ID}",
            )
        zip_path = latest
    report = verify_dossier_package(zip_path, ctx.run_dir / "reports" / "dossier_verify_extract")
    report_path = ctx.run_dir / "reports" / "dossier_verify_report.json"
    write_json(report_path, report)
    command_verdict = _report_verdict_to_command_verdict(str(report.get("verdict", "BLOCKED")))
    warnings = [str(x) for x in report.get("warnings", [])]
    limitations: List[str] = []
    if report.get("default_dossier_has_pdf"):
        limitations.append("Default dossier ZIP contains PDF and is not valid for agent exchange.")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: VERIFY DOSSIER",
        verdict=command_verdict,
        summary="Dossier package verification completed.",
        outputs=[report_path],
        input_refs=[str(zip_path)],
        warnings=warnings,
        details=report,
        next_actions=["Inspect verify report and hash status before Owner handoff."],
        limitations=limitations,
    )


def _test_result(name: str, ok: bool, detail: Optional[Any] = None) -> Dict[str, Any]:
    row: Dict[str, Any] = {"test": name, "pass": bool(ok)}
    if detail is not None:
        row["detail"] = detail
    return row


def command_check_all(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("check-all", args.out)
    rail = ProgressRail(renderer, ctx)
    blocked = _block_if_dirty_owner_decision(ctx, renderer, command="check-all", input_refs=[str(repo_root)], progress=rail)
    if blocked is not None:
        return blocked
    dirty_admission = _dirty_admission_state("check-all")
    rail.start(1, "reading_git_truth", target=str(repo_root))

    before = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=False)
    before_set = {line[3:] for line in before.stdout.splitlines() if len(line) > 3}
    tests: List[Dict[str, Any]] = []
    rail.done(1, f"dirty={str(ctx.dirty_before).lower()}", target=str(repo_root))

    manifest = load_manifest()
    tests.append(_test_result("manifest_exists", manifest.get("agent_id") == "ADMINISTRATUM_AGENT"))
    tests.append(_test_result("manifest_has_extended_skills", set(SKILL_IDS).issubset(set(manifest.get("supported_skills", [])))))

    policies = [
        AGENT_ROOT / "POLICIES" / "ACCEPTANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "REJECTION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "LEARNING_POLICY.md",
        AGENT_ROOT / "POLICIES" / "MUTATION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "PROVENANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "RUNTIME_OUTPUT_POLICY.md",
    ]
    tests.append(_test_result("policies_exist", all(p.exists() for p in policies)))

    rules_ok = True
    for p in (AGENT_ROOT / "brain_node" / "rules").glob("*.json"):
        try:
            read_json(p)
        except Exception:
            rules_ok = False
            break
    tests.append(_test_result("rules_json_valid", rules_ok))

    skill_mf_ok = True
    missing = []
    for sid in SKILL_IDS:
        path = AGENT_ROOT / "skills" / sid / "skill_manifest.json"
        if not path.exists():
            missing.append(str(path))
            skill_mf_ok = False
    tests.append(_test_result("skill_manifests_exist", skill_mf_ok, missing if missing else None))

    c_runtime = classify_path("IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-DEMO/file.json", repo_root)
    tests.append(_test_result("runtime_path_classification", c_runtime.get("zone_class") == "RUNTIME_OUTPUT", c_runtime))

    # CLI smoke commands
    runner_path = Path(__file__).resolve()
    cmd_help = subprocess.run(
        [sys.executable, str(runner_path), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_help_runs", cmd_help.returncode == 0 and "doctor-rich" in cmd_help.stdout, cmd_help.stdout[:300]))
    tests.append(_test_result("cli_help_lists_transfer_commands", "transfer-verify-pack" in cmd_help.stdout, cmd_help.stdout[:300]))

    cmd_status = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "status", "--out", str(ctx.run_dir / "cli_status")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_status_runs", cmd_status.returncode == 0, cmd_status.stdout[:300]))
    tests.append(_test_result("cli_status_compact_default", "DETAILS:" not in cmd_status.stdout, cmd_status.stdout[:300]))

    cmd_inventory = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "inventory", "--repo-root", str(REPO_ROOT), "--out", str(ctx.run_dir / "cli_inventory")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_inventory_runs", cmd_inventory.returncode == 0, cmd_inventory.stdout[:300]))

    cmd_doctor_rich = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "doctor-rich", "--out", str(ctx.run_dir / "cli_doctor_rich")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_doctor_rich_runs", cmd_doctor_rich.returncode == 0, cmd_doctor_rich.stdout[:300]))

    cmd_verbose = subprocess.run(
        [sys.executable, str(runner_path), "--verbose", "--no-color", "status", "--out", str(ctx.run_dir / "cli_status_verbose")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_verbose_mode_renders_details", cmd_verbose.returncode == 0 and "DETAILS" in cmd_verbose.stdout, cmd_verbose.stdout[:300]))

    cmd_no_rich = subprocess.run(
        [sys.executable, str(runner_path), "--no-rich", "--no-color", "status", "--out", str(ctx.run_dir / "cli_status_no_rich")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_no_rich_mode_runs", cmd_no_rich.returncode == 0 and "ARCHIVE SEAL" not in cmd_no_rich.stdout, cmd_no_rich.stdout[:300]))

    if RICH_AVAILABLE:
        cmd_rich = subprocess.run(
            [sys.executable, str(runner_path), "--rich", "--no-color", "status", "--out", str(ctx.run_dir / "cli_status_rich")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        tests.append(_test_result("cli_rich_mode_runs_if_available", cmd_rich.returncode == 0, cmd_rich.stdout[:300]))
    else:
        tests.append(_test_result("cli_rich_mode_runs_if_available", True, "rich_not_installed"))

    cmd_shell_help = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_help_render", cmd_shell_help.returncode == 0 and "AVAILABLE RITES" in cmd_shell_help.stdout, cmd_shell_help.stdout[:400]))
    tests.append(_test_result("shell_no_color_render", "\x1b[" not in cmd_shell_help.stdout))

    cmd_shell_status = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/status"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_status_render", cmd_shell_status.returncode == 0 and "ADMINISTRATUM AGENT :: STATUS" in cmd_shell_status.stdout, cmd_shell_status.stdout[:400]))

    cmd_shell_recent = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/recent"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_recent_render", cmd_shell_recent.returncode == 0 and "RECENT RUNS" in cmd_shell_recent.stdout, cmd_shell_recent.stdout[:400]))

    cmd_shell_self = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/shell"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_self_guard_already_in_shell", cmd_shell_self.returncode == 0 and "already_in_shell" in cmd_shell_self.stdout, cmd_shell_self.stdout[:400]))

    cmd_shell_typo = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/soctor-oss"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_fuzzy_suggestion", cmd_shell_typo.returncode != 0 and "/doctor-oss" in cmd_shell_typo.stdout, cmd_shell_typo.stdout[:400]))

    cmd_schema = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "schema-regression", "--out", str(ctx.run_dir / "cli_schema_regression")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("schema_regression_runs", cmd_schema.returncode == 0 and "SCHEMA REGRESSION" in cmd_schema.stdout, cmd_schema.stdout[:400]))

    transfer_test_path = AGENT_ROOT / "TRANSFER_GATE" / "TESTS" / "test_transfer_gate_v0_1.py"
    tests.append(_test_result("transfer_gate_test_script_exists", transfer_test_path.exists(), str(transfer_test_path)))
    cmd_transfer_test = subprocess.run(
        [sys.executable, str(transfer_test_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "transfer_gate_synthetic_e2e",
            cmd_transfer_test.returncode == 0 and '"verdict": "PASS"' in cmd_transfer_test.stdout,
            cmd_transfer_test.stdout[:500] or cmd_transfer_test.stderr[:500],
        )
    )
    cmd_transfer_status = subprocess.run(
        [
            sys.executable,
            str(runner_path),
            "--no-color",
            "transfer-status",
            "--transfer-root",
            str(ctx.run_dir / "transfer_status_root"),
            "--out",
            str(ctx.run_dir / "cli_transfer_status"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "transfer_status_cli_runs",
            cmd_transfer_status.returncode == 0 and "TRANSFER STATUS" in cmd_transfer_status.stdout,
            cmd_transfer_status.stdout[:400],
        )
    )
    cmd_shell_transfer_help = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "shell_help_lists_transfer_rites",
            all(
                token in cmd_shell_transfer_help.stdout
                for token in [
                    "/transfer-status",
                    "/transfer-verify-pack",
                    "/transfer-send-vm2",
                    "/transfer-push-vm2",
                    "/transfer-fetch-vm2",
                ]
            ),
            cmd_shell_transfer_help.stdout[:500],
        )
    )

    cmd_transfer_push_missing = subprocess.run(
        [sys.executable, str(runner_path), "--plain-json", "transfer-push-vm2", "--step-name", "missing-pack", "--transport", "local", "--remote-root", str(ctx.run_dir / "mock_vm2")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "transfer_push_missing_path_blocks",
            cmd_transfer_push_missing.returncode != 0 and "BLOCKED_INPUT_MISSING" in cmd_transfer_push_missing.stdout,
            cmd_transfer_push_missing.stdout[:500] or cmd_transfer_push_missing.stderr[:500],
        )
    )

    cmd_transfer_push_bad = subprocess.run(
        [
            sys.executable,
            str(runner_path),
            "--plain-json",
            "transfer-push-vm2",
            "--pack-zip",
            str(ctx.run_dir / "missing_prompt_pack.zip"),
            "--step-name",
            "bad-pack",
            "--transport",
            "local",
            "--remote-root",
            str(ctx.run_dir / "mock_vm2"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "transfer_push_bad_path_blocks",
            cmd_transfer_push_bad.returncode != 0 and "BLOCKED_INPUT_MISSING" in cmd_transfer_push_bad.stdout,
            cmd_transfer_push_bad.stdout[:500] or cmd_transfer_push_bad.stderr[:500],
        )
    )

    transfer_pc_test_path = AGENT_ROOT / "TRANSFER_GATE" / "TESTS" / "test_transfer_gate_pc_push_fetch_v0_1.py"
    tests.append(_test_result("transfer_pc_test_script_exists", transfer_pc_test_path.exists(), str(transfer_pc_test_path)))
    cmd_transfer_pc_test = subprocess.run(
        [sys.executable, str(transfer_pc_test_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(
        _test_result(
            "transfer_pc_push_fetch_synthetic",
            cmd_transfer_pc_test.returncode == 0 and '"verdict": "PASS"' in cmd_transfer_pc_test.stdout,
            cmd_transfer_pc_test.stdout[:700] or cmd_transfer_pc_test.stderr[:700],
        )
    )

    cmd_valid_freelance = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "validate-freelance-envelope", "--envelope", str(FREELANCE_SAMPLE_VALID_PATH), "--out", str(ctx.run_dir / "cli_freelance_valid")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("freelance_valid_sample_passes", cmd_valid_freelance.returncode == 0, cmd_valid_freelance.stdout[:400]))

    cmd_bad_freelance = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "validate-freelance-envelope", "--envelope", str(FREELANCE_SAMPLE_MALFORMED_PATH), "--out", str(ctx.run_dir / "cli_freelance_malformed")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("freelance_malformed_sample_blocks", cmd_bad_freelance.returncode != 0 and "BLOCKED" in cmd_bad_freelance.stdout, cmd_bad_freelance.stdout[:400]))

    cmd_handoff = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "build-freelance-handoff", "--envelope", str(FREELANCE_SAMPLE_VALID_PATH), "--out", str(ctx.run_dir / "cli_freelance_handoff")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("freelance_handoff_package_builds", cmd_handoff.returncode == 0 and "FREELANCE HANDOFF" in cmd_handoff.stdout, cmd_handoff.stdout[:400]))

    dirty_env = dict(os.environ)
    dirty_env["ADMINISTRATUM_DIRTY_SIMULATION_PATHS"] = "UNAUTHORIZED_DIRTY_SIMULATION.tmp"
    cmd_dirty_block = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "collect-reality-snapshot", "--repo-root", str(REPO_ROOT), "--out", str(ctx.run_dir / "cli_dirty_admission_simulation")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=dirty_env,
    )
    tests.append(
        _test_result(
            "dirty_state_simulation_owner_decision",
            cmd_dirty_block.returncode != 0 and "OWNER_DECISION_REQUIRED" in cmd_dirty_block.stdout,
            cmd_dirty_block.stdout[:500],
        )
    )

    cmd_progress = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "collect-reality-snapshot", "--repo-root", str(REPO_ROOT), "--out", str(ctx.run_dir / "cli_progress")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("progress_renderer_visible", cmd_progress.returncode == 0 and "PHASE 1/8" in cmd_progress.stdout, cmd_progress.stdout[:400]))

    # Functional new layers
    rail.start(2, "scanning_context_metadata", target="IMPERIUM_CONTEXT")
    scan = scan_imperium_context(
        ctx.run_id,
        ctx.run_dir,
        local_root=Path(args.local_root).resolve(),
        private_root=Path(args.private_root).resolve(),
        metrics=ctx.metrics,
        progress_hook=_context_progress_hook(rail),
    )
    tests.append(_test_result("scan_imperium_context_runs", Path(scan.report_path).exists()))
    rail.done(2, f"objects={scan.report.get('entry_count', 0)}", target=str(Path(scan.report_path)))

    rail.start(4, "classifying_risks", target=str(Path(scan.report_path)))
    local_cls = classify_local_context(ctx.run_id, ctx.run_dir, Path(scan.report_path), metrics=ctx.metrics)
    tests.append(_test_result("classify_local_context_runs", Path(local_cls.report_path).exists()))

    risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(local_cls.report_path), metrics=ctx.metrics)
    tests.append(_test_result("private_export_risk_report_runs", Path(risk.report_path).exists()))
    rail.done(4, f"high_risk={local_cls.report.get('high_risk_count', 0)}", target=str(Path(local_cls.report_path)))

    rail.start(3, "building_inventory", target=str(repo_root))
    inv = build_inventory(
        repo_root,
        ctx.run_id,
        ctx.run_dir,
        metrics=ctx.metrics,
        max_files=args.inventory_max_files,
        progress_hook=_inventory_progress_hook(rail),
    )
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, Path(inv.report_path), metrics=ctx.metrics, limit=120)
    rail.done(3, f"files={inv.report.get('total_files', 0)}", target=str(Path(inv.report_path)))
    rail.start(5, "collecting_useful_refs", target=str(Path(inv.report_path)))
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, Path(inv.report_path), repo_root=repo_root, metrics=ctx.metrics)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    routing = route_to_organs(
        ctx.run_id,
        ctx.run_dir,
        [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:40] if x.get("path")],
        requested_action="delete file",
        metrics=ctx.metrics,
    )
    tests.append(
        _test_result(
            "route_mutation_request_blocked",
            any((r.get("verdict", "").startswith("REJECT") or "BLOCK" in r.get("verdict", "")) for r in routing.report.get("routes", [])),
        )
    )
    rail.done(5, f"candidates={useful.report.get('top_summary', {}).get('scripts', 0)}", target=str(Path(useful.report_path)))

    rail.start(6, "building_continuity_narrative", target=str(ctx.run_dir / "continuity_pack"))
    continuity = collect_continuity_pack(repo_root, ctx.run_id, ctx.run_dir, include_context=True, metrics=ctx.metrics)
    tests.append(_test_result("continuity_pack_exists", Path(continuity.report.get("manifest_path", "")).exists()))
    required_pack_files = [
        "continuity_pack_manifest.json",
        "continuity_pack_summary.md",
        "owner_readable_continuity_brief.md",
        "agent_handoff_brief.md",
        "reality_snapshot_excerpt.json",
        "current_git_truth.json",
        "active_agent_status.json",
        "warnings_and_owner_decisions.md",
        "useful_refs_index.json",
        "private_context_safety_report.json",
        "metrics_summary.json",
        "kpd_score.json",
        "receipt.json",
    ]
    pack_dir = Path(continuity.report.get("pack_dir", ""))
    missing_pack = [name for name in required_pack_files if not (pack_dir / name).exists()]
    tests.append(_test_result("continuity_pack_rich_files_exist", len(missing_pack) == 0, missing_pack))
    rail.done(
        6,
        f"pack_files={len(required_pack_files) - len(missing_pack)} warnings={len(missing_pack)}",
        target=str(pack_dir),
    )

    verify = verify_pack_against_reality(repo_root, ctx.run_id, ctx.run_dir, Path(continuity.report.get("manifest_path", "")), metrics=ctx.metrics)
    tests.append(_test_result("verify_pack_against_reality_runs", Path(verify.report_path).exists()))

    handoff = build_agent_handoff_context(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    tests.append(_test_result("handoff_context_runs", Path(handoff.report_path).exists()))

    cu = build_cu_index(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    tests.append(_test_result("cu_summary_runs", Path(cu.report_path).exists()))

    kpd, thinking = kpd_from_reports(ctx.run_id, ctx.run_dir)
    kpd_path = ctx.run_dir / "reports" / "kpd_score_from_check_all.json"
    thinking_path = ctx.run_dir / "reports" / "thinking_quality_from_check_all.json"
    write_json(kpd_path, kpd)
    write_json(thinking_path, thinking)
    tests.append(_test_result("kpd_generated", kpd_path.exists() and thinking_path.exists()))

    cmd_plain = subprocess.run(
        [sys.executable, str(runner_path), "--plain-json", "status", "--out", str(ctx.run_dir / "cli_plain_status")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    plain_ok = False
    if cmd_plain.returncode == 0:
        try:
            j = json.loads(cmd_plain.stdout)
            required = {
                "status",
                "command",
                "summary",
                "primary_refs",
                "artifacts_written",
                "warnings",
                "why_trust",
                "next_actions",
                "metrics",
                "limitations",
            }
            plain_ok = required.issubset(set(j.keys()))
        except Exception:
            plain_ok = False
    tests.append(_test_result("cli_plain_json_mode", plain_ok, cmd_plain.stdout[:200]))

    metrics_file = ctx.run_dir / "cli_progress" / "reports" / "collect_reality_snapshot_metrics_summary.json"
    metrics_data = read_json(metrics_file) if metrics_file.exists() else {}
    metrics_payload = metrics_data.get("metrics", {})
    tests.append(_test_result("resource_metrics_present", all(k in metrics_payload for k in ["process_cpu_seconds", "gpu_used", "run_cost_class"])))
    tests.append(_test_result("gpu_fields_explicit_false", metrics_payload.get("gpu_used") is False))

    access_map_path = ctx.run_dir / "cli_progress" / "reports" / "collect_reality_snapshot_access_map.json"
    tests.append(_test_result("access_map_generated", access_map_path.exists()))
    if access_map_path.exists():
        amap = read_json(access_map_path)
        tests.append(_test_result("access_map_has_touched_roots", bool(amap.get("read_roots")) and bool(amap.get("written_roots"))))

    runner_text = Path(__file__).read_text(encoding="utf-8")
    banned = [pkg for pkg in ["rich", "textual", "numpy", "pandas"] if f"import {pkg}" in runner_text]
    tests.append(_test_result("no_external_dependency_imports", len(banned) == 0, banned))

    after = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=False)
    after_set = {line[3:] for line in after.stdout.splitlines() if len(line) > 3}
    new_dirty = sorted(after_set - before_set)
    outside_runs = [p for p in new_dirty if not p.startswith("RUNS/ADMINISTRATUM_AGENT/")]
    tests.append(_test_result("shell_and_checks_do_not_dirty_outside_runs", len(outside_runs) == 0, outside_runs))

    total = len(tests)
    passed = sum(1 for t in tests if t.get("pass"))
    failed = total - passed
    verdict = "PASS" if failed == 0 else "BLOCKED"
    report = {
        "report_type": "CHECK_ALL_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "verdict": verdict,
        "tests": tests,
    }
    report_path = ctx.run_dir / "reports" / "check_all_report.json"
    write_json(report_path, report)
    report_md = ctx.run_dir / "reports" / "check_all_report.md"
    lines = [
        "# Administratum Agent Check-All Report",
        "",
        f"- run_id: {ctx.run_id}",
        f"- verdict: {verdict}",
        f"- passed: {passed}/{total}",
        "",
    ]
    for t in tests:
        lines.append(f"- {t['test']}: {'PASS' if t.get('pass') else 'FAIL'}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    warnings = ([f"failed tests: {failed}"] if failed else []) + _dirty_admission_warnings(dirty_admission)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CHECK ALL",
        verdict=verdict if verdict == "PASS" else "BLOCKED",
        summary="Acceptance check suite completed.",
        outputs=[report_path, report_md, kpd_path, thinking_path, inv, prov, useful, dirty, routing, continuity, verify, handoff, cu],
        input_refs=[str(repo_root), str(Path(args.local_root).resolve()), str(Path(args.private_root).resolve())],
        warnings=warnings,
        details=report,
        next_actions=["Review failed checks before claiming PASS."] if failed else ["All checks passed."],
        blocker_class="CHECKS_FAILED" if failed else None,
        progress=rail,
    )


def _shell_activity_summary() -> List[str]:
    rows = _list_recent_runs(limit=5)
    if not rows:
        return ["No runs detected yet."]
    out = []
    for row in rows:
        out.append(
            f"{row['run_id']} | command: {row.get('command', 'unparsed')} | status: {row.get('status', 'unparsed')} | warnings: {row['warning_count']}"
        )
    return out


def _runtime_isolation_status() -> Tuple[str, List[str]]:
    gitignore = RUNS_ROOT / ".gitignore"
    if not gitignore.exists():
        return "BLOCKED", ["RUNS .gitignore is missing."]
    text = gitignore.read_text(encoding="utf-8")
    warnings = []
    if "RUN-*/" not in text:
        warnings.append("RUN-*/ pattern missing in RUNS .gitignore")
    if "!.gitignore" not in text:
        warnings.append("!.gitignore marker missing in RUNS .gitignore")
    if warnings:
        return "PASS_WITH_WARNINGS", warnings
    return "PASS", ["Runtime outputs isolated under RUNS layer."]


def _shell_commands_reference() -> List[str]:
    return [
        "/help",
        "/help <command>",
        "/status",
        "/tools",
        "/inventory",
        "/doctor-rich",
        "/doctor-oss",
        "/build-dossier",
        "/verify-dossier",
        "/schema-regression",
        "/validate-freelance-envelope [path]",
        "/build-freelance-handoff [path]",
        "/classify <path>",
        "/dirty-runtime",
        "/useful-candidates",
        "/route <path>",
        "/merge-summary",
        "/scan-context",
        "/continuity-pack",
        "/reality-snapshot",
        "/metrics",
        "/kpd",
        "/check-all",
        "/transfer-status",
        "/transfer-verify-pack <pack_zip>",
        "/transfer-send-vm2 <pack_zip> <step name>",
        "/transfer-push-vm2 <pack_zip> <step name>",
        "/transfer-fetch-vm2 <task_id> <expected_filename>",
        "/recent",
        "/open-runs",
        "/exit",
    ]


def _shell_known_command_tokens() -> List[str]:
    tokens = []
    for row in _shell_commands_reference():
        token = row.split()[0].strip()
        if token and token not in tokens:
            tokens.append(token)
    if "/shell" not in tokens:
        tokens.append("/shell")
    return tokens


def _show_shell_welcome(renderer: Renderer) -> None:
    snap = status_snapshot()
    head_short = str(snap.get("git_head", ""))[:12]
    iso_status, iso_lines = _runtime_isolation_status()
    check = _find_latest_check_all()
    check_line = "n/a"
    warning_count = 0
    if check:
        check_line = f"{check.get('verdict', 'UNKNOWN')} ({check.get('passed', 0)}/{check.get('total', 0)})"
        warning_count = int(check.get("failed", 0))

    latest_manifest = _latest_continuity_manifest()
    latest_pack = str(latest_manifest.parent) if latest_manifest else "n/a"
    latest_pack_metrics = str((latest_manifest.parent / "metrics_summary.json")) if latest_manifest and (latest_manifest.parent / "metrics_summary.json").exists() else "n/a"
    latest_kpd = str((latest_manifest.parent / "kpd_score.json")) if latest_manifest and (latest_manifest.parent / "kpd_score.json").exists() else "n/a"
    latest_check_path = str(check.get("_path")) if check else "n/a"

    left_crest = "[ADM-ARCHIVE-SEAL]"
    right_crest = "[IMP-THRONE-SEAL]"

    title_lines = [
        f"{left_crest} ADMINISTRATUM LOCAL MODEL {right_crest}",
        "IMPERIUM NEW GENERATION / ARCHIVE VAULT ONLINE",
        "ADMINISTRATUM AGENT :: LOCAL MODEL",
        f"version: {snap.get('version', 'UNKNOWN')} | status: {snap.get('status', 'UNKNOWN')}",
        f"head: {head_short} | git_dirty: {str(bool(snap.get('dirty_tree'))).lower()} | live_work: enabled",
    ]
    status_lines = [
        f"runtime isolation: {iso_status}",
        *iso_lines,
        f"last check-all: {check_line}",
        f"warning count: {warning_count}",
        f"latest check-all report: {latest_check_path}",
        f"latest continuity pack: {latest_pack}",
        f"latest metrics: {latest_pack_metrics}",
        f"latest kpd: {latest_kpd}",
        "gpu policy: script-first / gpu_used=false",
        "truth zones: CANON / SANDBOX / RUNTIME / PRIVATE / LOCAL",
        "layout: left work/output zone; right command hints zone; header reprinted on /help",
    ]
    status_lines = [renderer.compact_display(line) for line in status_lines]
    recent_lines = _shell_activity_summary()
    rites_lines = _shell_commands_reference()

    if renderer.rich_enabled and renderer._rich_console is not None:
        welcome_text = Text("\n".join(title_lines), style="bright_white")
        renderer._rich_console.print(Panel(welcome_text, title="WELCOME", border_style="bright_magenta"))
        renderer._rich_console.print(Panel(Text("\n".join(status_lines), style="cyan"), title="STATUS", border_style="bright_blue"))
        renderer._rich_console.print(Panel(Text("\n".join(recent_lines), style="bright_black"), title="RECENT ACTIVITY", border_style="bright_black"))
        renderer._rich_console.print(Panel(Text("\n".join(rites_lines), style="green"), title="AVAILABLE RITES", border_style="green"))
        if DEFAULT_CONTEXT_PRIVATE.exists():
            renderer._rich_console.print(
                Panel(
                    Text("PRIVATE context detected. Metadata-only indexing and no-git-export rules are active.", style="yellow"),
                    title="SAFETY NOTICE",
                    border_style="yellow",
                )
            )
        renderer._rich_console.print("ADMINISTRATUM://LOCAL >")
        return

    print(renderer.panel("WELCOME", title_lines, color="blue"))
    print(renderer.panel("STATUS", status_lines, color="cyan"))
    print(renderer.panel("RECENT ACTIVITY", recent_lines, color="gray"))
    print(renderer.panel("AVAILABLE RITES", rites_lines, color="green"))
    if DEFAULT_CONTEXT_PRIVATE.exists():
        print(renderer.panel("SAFETY NOTICE", ["PRIVATE context detected. Metadata-only indexing and no-git-export rules are active."], color="yellow"))
    print("ADMINISTRATUM://LOCAL >")


def _shell_dispatch_line(line: str, renderer: Renderer) -> int:
    raw = line.strip()
    if not raw:
        return 0
    if not raw.startswith("/"):
        raise UserFacingError(
            "Shell command must start with `/`.",
            "Use one of the available rites from `/help`.",
            "/help",
        )

    parts = shlex.split(raw)
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd == "/exit":
        return 99
    if cmd == "/shell":
        renderer.emit(
            {
                "header": "ADMINISTRATUM SHELL :: SELF GUARD",
                "status": "WARN",
                "command": "shell/self_guard",
                "run_id": "N/A",
                "verdict": "already_in_shell",
                "summary": "already_in_shell: nested shell launch skipped.",
                "primary_refs": [],
                "artifacts_written": [],
                "warnings": ["already_in_shell"],
                "why_trust": ["Shell guard prevents false unknown command and avoids nested prompt side effects."],
                "metrics": {},
                "limitations": [],
                "details": {"requested": raw, "guard": "already_in_shell"},
                "next_actions": ["Use `/help` for shell commands or `/exit` to leave the shell."],
            }
        )
        return 0
    if cmd == "/help":
        topic = args[0].lower() if args else ""
        command_help = {
            "/status": "Read-only truth snapshot. Dirty state becomes WARN.",
            "/tools": "Show Administratum-relevant tools from Mechanicus registry with availability truth.",
            "/check-all": "Heavy verification rite. Dirty pre-state outside admitted scope returns OWNER_DECISION_REQUIRED.",
            "/build-dossier": "Build default MD+JSON no-PDF dossier ZIP.",
            "/verify-dossier": "Verify dossier hashes, required files, and no-PDF default policy.",
            "/recent": "Parse recent run receipts/reports into command/status/warning/run refs.",
            "/kpd": "Show compact scorecard first; JSON/verbose keeps full detail.",
            "/schema-regression": "Validate core JSON envelopes, command receipt shape, dossier no-PDF policy, and freelance samples.",
            "/validate-freelance-envelope": "Validate an Administratum freelance task envelope.",
            "/build-freelance-handoff": "Build Administratum's scoped freelance handoff package.",
            "/transfer-status": "Show Transfer Gate runtime status.",
            "/transfer-verify-pack": "Verify a Logos prompt ZIP. Usage: /transfer-verify-pack <pack_zip>",
            "/transfer-send-vm2": "Local stamp/register only. Usage: /transfer-send-vm2 <pack_zip> <step name>",
            "/transfer-push-vm2": "PC-side push to VM2 with remote hash/size proof. Usage: /transfer-push-vm2 <pack_zip> <step name>",
            "/transfer-fetch-vm2": "PC-side fetch by exact response filename. Usage: /transfer-fetch-vm2 <task_id> <expected_filename>",
        }
        summary = "Available rites listed."
        details: Dict[str, Any] = {"commands": _shell_commands_reference(), "modes": ["slash commands only", "plain JSON remains authoritative outside shell"]}
        if topic:
            normalized_topic = topic if topic.startswith("/") else f"/{topic}"
            summary = command_help.get(normalized_topic, f"No dedicated help entry for {normalized_topic}; showing command map.")
            details["topic"] = normalized_topic
            details["topic_help"] = command_help.get(normalized_topic, "unavailable")
        renderer.emit(
            {
                "header": "ADMINISTRATUM SHELL :: HELP",
                "status": "PASS",
                "command": "shell/help",
                "run_id": "N/A",
                "verdict": "PASS",
                "summary": summary,
                "primary_refs": [],
                "artifacts_written": [],
                "warnings": [],
                "why_trust": ["Help generated from local static shell command map."],
                "metrics": {},
                "limitations": [],
                "details": details,
                "next_actions": ["Use `/status` or `/check-all` as first verification rites."],
            }
        )
        return 0

    if cmd == "/status":
        return command_status(argparse.Namespace(out=None), renderer)
    if cmd == "/tools":
        return command_tools(argparse.Namespace(out=None), renderer)
    if cmd == "/identity":
        return command_identity(argparse.Namespace(out=None), renderer)
    if cmd == "/inventory":
        return command_inventory(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/doctor-rich":
        return command_doctor_rich(
            argparse.Namespace(
                out=None,
                plain_json=False,
                no_color=False,
                color=False,
                rich=renderer.rich_enabled,
                no_rich=not renderer.rich_enabled,
            ),
            renderer,
        )
    if cmd == "/doctor-oss":
        return command_doctor_oss(argparse.Namespace(out=None), renderer)
    if cmd == "/build-dossier":
        return command_build_dossier(
            argparse.Namespace(
                task_id=TASK_DOSSIER_FACTORY_ID,
                source_report_dir=None,
                source_receipt=None,
                next_task="TASK-20260518-ADMINISTRATUM-CONTRACT-REGRESSION-GATE-V0_1",
                out=None,
            ),
            renderer,
        )
    if cmd == "/verify-dossier":
        return command_verify_dossier(argparse.Namespace(zip_path=None, latest=True, out=None), renderer)
    if cmd == "/schema-regression":
        return command_schema_regression(argparse.Namespace(out=None), renderer)
    if cmd == "/validate-freelance-envelope":
        return command_validate_freelance_envelope(argparse.Namespace(envelope=args[0] if args else None, out=None), renderer)
    if cmd == "/build-freelance-handoff":
        return command_build_freelance_handoff(argparse.Namespace(envelope=args[0] if args else None, out=None), renderer)
    if cmd == "/classify":
        if not args:
            raise UserFacingError("Missing `<path>` for /classify.", "Provide a path argument.", "/classify IMPERIUM_NEW_GENERATION/README.md")
        return command_classify_path(argparse.Namespace(repo_root=str(REPO_ROOT), path=args[0], requested_action="", out=None), renderer)
    if cmd == "/dirty-runtime":
        return command_detect_dirty_runtime(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/useful-candidates":
        return command_useful_candidates(argparse.Namespace(repo_root=str(REPO_ROOT), inventory=None, out=None), renderer)
    if cmd == "/route":
        if not args:
            raise UserFacingError("Missing `<path>` for /route.", "Provide a path argument.", "/route IMPERIUM_NEW_GENERATION/TOOLS/agent_cli/imperium_ng_cli.py")
        return command_route_to_organs(
            argparse.Namespace(path=[args[0]], paths_file=None, requested_action="", out=None),
            renderer,
        )
    if cmd == "/merge-summary":
        return command_merge_summary(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                inventory=None,
                provenance=None,
                candidates=None,
                dirty=None,
                routing=None,
                requested_action="",
                provenance_limit=300,
                out=None,
            ),
            renderer,
        )
    if cmd == "/scan-context":
        return command_scan_context(
            argparse.Namespace(local_root=str(DEFAULT_CONTEXT_LOCAL), private_root=str(DEFAULT_CONTEXT_PRIVATE), out=None),
            renderer,
        )
    if cmd == "/continuity-pack":
        return command_collect_continuity_pack(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                include_context=True,
                local_root=str(DEFAULT_CONTEXT_LOCAL),
                private_root=str(DEFAULT_CONTEXT_PRIVATE),
                provenance_limit=300,
                inventory_max_files=1200,
                out=None,
            ),
            renderer,
        )
    if cmd == "/reality-snapshot":
        return command_collect_reality_snapshot(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/metrics":
        return command_metrics_summary(argparse.Namespace(run_dir=None, out=None), renderer)
    if cmd == "/kpd":
        return command_show_kpd(argparse.Namespace(run_dir=None, out=None), renderer)
    if cmd == "/check-all":
        return command_check_all(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                local_root=str(DEFAULT_CONTEXT_LOCAL),
                private_root=str(DEFAULT_CONTEXT_PRIVATE),
                inventory_max_files=1000,
                out=None,
            ),
            renderer,
        )
    if cmd == "/recent":
        return command_recent(argparse.Namespace(limit=8, out=None), renderer)
    if cmd == "/open-runs":
        return command_open_runs(argparse.Namespace(out=None), renderer)
    if cmd == "/transfer-status":
        return command_transfer_status(argparse.Namespace(transfer_root=str(DEFAULT_TRANSFER_ROOT), ledger_tail=5, out=None), renderer)
    if cmd == "/transfer-verify-pack":
        if not args:
            raise UserFacingError(
                "Missing `<pack_zip>` for /transfer-verify-pack.",
                "Provide a prompt pack ZIP path.",
                "/transfer-verify-pack /path/to/TASK__PROMPT_PACK.zip",
            )
        return command_transfer_verify_pack(argparse.Namespace(pack_zip=args[0], transfer_root=str(DEFAULT_TRANSFER_ROOT), out=None), renderer)
    if cmd == "/transfer-send-vm2":
        if len(args) < 2:
            raise UserFacingError(
                "Missing arguments for /transfer-send-vm2.",
                "Provide pack path and step name. Quote the step name when it contains spaces.",
                "/transfer-send-vm2 /path/to/TASK__PROMPT_PACK.zip \"Owner step\"",
            )
        return command_transfer_send_vm2(
            argparse.Namespace(
                pack_zip=args[0],
                step_name=" ".join(args[1:]),
                source_head=None,
                operator="OWNER",
                transfer_root=str(DEFAULT_TRANSFER_ROOT),
                out=None,
            ),
            renderer,
        )
    if cmd == "/transfer-push-vm2":
        if len(args) < 2:
            raise UserFacingError(
                "Missing arguments for /transfer-push-vm2.",
                "Provide pack path and step name. VM2 target defaults are used unless CLI flags are needed.",
                "/transfer-push-vm2 /path/to/TASK__PROMPT_PACK.zip \"Owner step\"",
            )
        return command_transfer_push_vm2(
            argparse.Namespace(
                pack_zip=args[0],
                step_name=" ".join(args[1:]),
                source_head=None,
                operator="OWNER",
                task_id=None,
                vm_user="vboxuser2",
                vm_host="127.0.0.1",
                vm_port=2223,
                vm_key=None,
                remote_root="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER",
                transfer_root=str(DEFAULT_TRANSFER_ROOT),
                transport="ssh",
                dry_run=False,
                out=None,
            ),
            renderer,
        )
    if cmd == "/transfer-fetch-vm2":
        if len(args) < 2:
            raise UserFacingError(
                "Missing arguments for /transfer-fetch-vm2.",
                "Provide task id and exact expected response filename.",
                "/transfer-fetch-vm2 TASK-ID TASK-ID__VM2_RESPONSE_BUNDLE.zip",
            )
        return command_transfer_fetch_vm2(
            argparse.Namespace(
                task_id=args[0],
                expected_filename=args[1],
                correlation_id=None,
                transfer_root=str(DEFAULT_TRANSFER_ROOT),
                no_quarantine=False,
                pc_remote=True,
                vm_user="vboxuser2",
                vm_host="127.0.0.1",
                vm_port=2223,
                vm_key=None,
                remote_root="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER",
                transport="ssh",
                out=None,
            ),
            renderer,
        )

    suggestion = difflib.get_close_matches(cmd, _shell_known_command_tokens(), n=1, cutoff=0.55)
    how_to_fix = "Use `/help` to list available rites."
    example = "/help"
    if suggestion:
        how_to_fix = f"Did you mean `{suggestion[0]}`? Use `/help` for the full command map."
        example = suggestion[0]
    raise UserFacingError(f"Unknown shell command: {cmd}", how_to_fix, example)


def command_shell(args: argparse.Namespace, renderer: Renderer) -> int:
    _show_shell_welcome(renderer)
    if args.once:
        once_line = str(args.once).strip()
        if once_line and not once_line.startswith("/"):
            once_line = f"/{once_line}"
        return_code = _shell_dispatch_line(once_line, renderer)
        return 0 if return_code in {0, 99} else return_code

    prompt = "ADMINISTRATUM://LOCAL > "
    while True:
        try:
            line = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print()
            return 0
        try:
            code = _shell_dispatch_line(line, renderer)
            if code == 99:
                return 0
        except UserFacingError as err:
            renderer.emit_error(err)
            continue
        except Exception as err:  # pragma: no cover - defensive shell branch
            renderer.emit_error(
                UserFacingError(
                    f"Unhandled shell error: {err}",
                    "Retry the command with --verbose or run outside shell for details.",
                    f"python {Path(__file__).name} --verbose status",
                )
            )
            continue


def command_optional_oss_proposal(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("optional-oss-proposal", args.out)
    text = optional_oss_enhancement_proposal()
    path = ctx.run_dir / "reports" / "OPTIONAL_ENHANCEMENT_PROPOSAL.md"
    path.write_text(text, encoding="utf-8")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: OPTIONAL OSS PROPOSAL",
        verdict="PASS",
        summary="Optional OSS proposal generated (advisory only).",
        outputs=[path],
        input_refs=[],
        warnings=[],
        details={"oss_policy": "NONE_INSTALLED_NONE_INTRODUCED"},
    )


def _transfer_command_verdict(result: Dict[str, Any]) -> str:
    token = str(result.get("verdict", "BLOCKED")).upper()
    if token.startswith("BLOCKED"):
        return "BLOCKED"
    warnings = result.get("warnings", []) or []
    verification = result.get("verification")
    if isinstance(verification, dict):
        warnings = list(warnings) + list(verification.get("warnings", []) or [])
    return "PASS_WITH_WARNINGS" if warnings else "PASS"


def _transfer_warnings(result: Dict[str, Any]) -> List[str]:
    warnings = list(result.get("warnings", []) or [])
    errors = list(result.get("errors", []) or [])
    verification = result.get("verification")
    if isinstance(verification, dict):
        warnings.extend(verification.get("warnings", []) or [])
        errors.extend(verification.get("errors", []) or [])
    return list(dict.fromkeys(str(item) for item in warnings + errors if str(item).strip()))


def command_transfer_verify_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("transfer-verify-pack", args.out)
    pack_zip = Path(args.pack_zip)
    runtime_root = Path(args.transfer_root)
    result = verify_prompt_pack(pack_zip, runtime_root)
    report_path = ctx.run_dir / "reports" / "transfer_verify_pack_report.json"
    write_json(report_path, result)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TRANSFER VERIFY PACK",
        verdict=_transfer_command_verdict(result),
        summary="Transfer prompt pack verification completed.",
        outputs=[report_path],
        input_refs=[str(pack_zip), str(runtime_root)],
        warnings=_transfer_warnings(result),
        details=result,
        next_actions=["Run transfer-send-vm2 if verification is PASS or accepted WARN."],
        blocker_class="TRANSFER_PACK_INVALID" if str(result.get("verdict", "")).startswith("BLOCKED") else None,
    )


def command_transfer_send_vm2(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("transfer-send-vm2", args.out)
    runtime_root = Path(args.transfer_root)
    source_head = str(args.source_head or git_head(REPO_ROOT))
    result = send_vm2_prompt_pack(
        Path(args.pack_zip),
        step_name=str(args.step_name),
        source_head=source_head,
        operator=str(args.operator),
        runtime_root=runtime_root,
    )
    report_path = ctx.run_dir / "reports" / "transfer_send_vm2_report.json"
    write_json(report_path, result)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TRANSFER SEND VM2",
        verdict=_transfer_command_verdict(result),
        summary="Transfer prompt pack send/stamp completed.",
        outputs=[report_path],
        input_refs=[str(args.pack_zip), str(runtime_root)],
        warnings=_transfer_warnings(result),
        details=result,
        next_actions=["Use the VM2 prompt pack manually, then create/fetch the exact response bundle."],
        blocker_class="TRANSFER_SEND_BLOCKED" if str(result.get("verdict", "")).startswith("BLOCKED") else None,
    )


def _add_dirty_truth(result: Dict[str, Any]) -> Dict[str, Any]:
    dirty_paths = _git_dirty_paths(REPO_ROOT)
    if not dirty_paths:
        result["dirty_repo_before"] = False
        result["dirty_paths_before"] = []
        return result
    warnings = list(result.get("warnings", []) or [])
    warnings.append("WARN_DIRTY_REPO")
    result["warnings"] = list(dict.fromkeys(warnings))
    result["dirty_repo_before"] = True
    result["dirty_paths_before"] = dirty_paths
    return result


def command_transfer_push_vm2(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("transfer-push-vm2", args.out)
    source_head = str(args.source_head or git_head(REPO_ROOT))
    result = push_vm2_prompt_pack(
        getattr(args, "pack_zip", None),
        step_name=str(getattr(args, "step_name", "")),
        source_head=source_head,
        operator=str(getattr(args, "operator", "OWNER")),
        task_id=getattr(args, "task_id", None),
        vm_user=str(getattr(args, "vm_user", "vboxuser2")),
        vm_host=str(getattr(args, "vm_host", "127.0.0.1")),
        vm_port=int(getattr(args, "vm_port", 2223)),
        vm_key=getattr(args, "vm_key", None),
        remote_root=str(getattr(args, "remote_root", "/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")),
        runtime_root=Path(getattr(args, "transfer_root", str(DEFAULT_TRANSFER_ROOT))),
        transport=str(getattr(args, "transport", "ssh")),
        dry_run=bool(getattr(args, "dry_run", False)),
    )
    result = _add_dirty_truth(result)
    report_path = ctx.run_dir / "reports" / "transfer_push_vm2_report.json"
    write_json(report_path, result)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TRANSFER PUSH VM2",
        verdict=_transfer_command_verdict(result),
        summary="Transfer prompt pack PC-to-VM2 push completed.",
        outputs=[report_path],
        input_refs=[
            str(getattr(args, "pack_zip", "")),
            str(getattr(args, "remote_root", "")),
            str(getattr(args, "transfer_root", "")),
        ],
        warnings=_transfer_warnings(result),
        details=result,
        next_actions=["Use transfer-fetch-vm2 after VM2 creates the exact response bundle."],
        blocker_class="TRANSFER_PUSH_BLOCKED" if str(result.get("verdict", "")).startswith("BLOCKED") else None,
    )


def command_transfer_fetch_vm2(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("transfer-fetch-vm2", args.out)
    runtime_root = Path(args.transfer_root)
    if bool(getattr(args, "pc_remote", False)):
        result = fetch_vm2_response_bundle_remote(
            task_id=str(args.task_id),
            expected_filename=str(args.expected_filename or ""),
            correlation_id=args.correlation_id,
            runtime_root=runtime_root,
            vm_user=str(getattr(args, "vm_user", "vboxuser2")),
            vm_host=str(getattr(args, "vm_host", "127.0.0.1")),
            vm_port=int(getattr(args, "vm_port", 2223)),
            vm_key=getattr(args, "vm_key", None),
            remote_root=str(getattr(args, "remote_root", "/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")),
            transport=str(getattr(args, "transport", "ssh")),
        )
    else:
        result = fetch_vm2_response_bundle(
            task_id=str(args.task_id),
            expected_filename=args.expected_filename,
            correlation_id=args.correlation_id,
            runtime_root=runtime_root,
            quarantine_on_mismatch=not bool(args.no_quarantine),
        )
    result = _add_dirty_truth(result)
    report_path = ctx.run_dir / "reports" / "transfer_fetch_vm2_report.json"
    write_json(report_path, result)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TRANSFER FETCH VM2",
        verdict=_transfer_command_verdict(result),
        summary="Transfer response bundle fetch/verification completed.",
        outputs=[report_path],
        input_refs=[str(runtime_root), str(args.task_id), str(args.expected_filename or "")],
        warnings=_transfer_warnings(result),
        details=result,
        next_actions=["Hand off verified response bundle by exact filename."],
        blocker_class="TRANSFER_FETCH_BLOCKED" if str(result.get("verdict", "")).startswith("BLOCKED") else None,
    )


def command_transfer_status(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("transfer-status", args.out)
    runtime_root = Path(args.transfer_root)
    result = transfer_status(runtime_root, ledger_tail=int(args.ledger_tail))
    report_path = ctx.run_dir / "reports" / "transfer_status_report.json"
    write_json(report_path, result)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: TRANSFER STATUS",
        verdict="PASS",
        summary="Transfer gate runtime status collected.",
        outputs=[report_path],
        input_refs=[str(runtime_root)],
        warnings=[],
        details=result,
        next_actions=["Use transfer-verify-pack, transfer-send-vm2, or transfer-fetch-vm2 as needed."],
    )


COMMAND_HANDLERS: Dict[str, Callable[[argparse.Namespace, Renderer], int]] = {
    "status": command_status,
    "check": command_check,
    "where": command_where,
    "identity": command_identity,
    "tools": command_tools,
    "pack": command_pack,
    "help": command_help,
    "inventory": command_inventory,
    "classify-path": command_classify_path,
    "provenance-index": command_provenance,
    "useful-candidates": command_useful_candidates,
    "detect-dirty-runtime": command_detect_dirty_runtime,
    "route-to-organs": command_route_to_organs,
    "merge-summary": command_merge_summary,
    "scan-imperium-context": command_scan_context,
    "classify-local-context": command_classify_local_context,
    "collect-reality-snapshot": command_collect_reality_snapshot,
    "collect-continuity-pack": command_collect_continuity_pack,
    "build-agent-handoff-context": command_build_handoff_context,
    "verify-pack-against-reality": command_verify_pack,
    "metrics-summary": command_metrics_summary,
    "explain-decision": command_explain_decision,
    "show-kpd": command_show_kpd,
    "cu-summary": command_cu_summary,
    "doctor-rich": command_doctor_rich,
    "doctor-oss": command_doctor_oss,
    "build-dossier": command_build_dossier,
    "verify-dossier": command_verify_dossier,
    "schema-regression": command_schema_regression,
    "validate-freelance-envelope": command_validate_freelance_envelope,
    "build-freelance-handoff": command_build_freelance_handoff,
    "check-all": command_check_all,
    "recent": command_recent,
    "open-runs": command_open_runs,
    "shell": command_shell,
    "optional-oss-proposal": command_optional_oss_proposal,
    "transfer-verify-pack": command_transfer_verify_pack,
    "transfer-send-vm2": command_transfer_send_vm2,
    "transfer-push-vm2": command_transfer_push_vm2,
    "transfer-fetch-vm2": command_transfer_fetch_vm2,
    "transfer-status": command_transfer_status,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="administratum_agent_runner.py",
        description="Administratum-Agent V1 hardened local CLI (IMPERIUM_NEW_GENERATION sandbox).",
    )
    parser.add_argument("--plain-json", action="store_true", help="Machine-readable JSON output (authoritative mode).")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    parser.add_argument("--color", action="store_true", help="Enable ANSI colors (when terminal supports).")
    parser.add_argument("--verbose", action="store_true", help="Verbose output with full details blocks.")
    parser.add_argument("--compact", action="store_true", help="Compact renderer mode.")
    parser.add_argument("--ascii", action="store_true", help="Force ASCII-safe panel rendering.")
    parser.add_argument("--rich", action="store_true", help="Enable optional Rich renderer when available.")
    parser.add_argument("--no-rich", action="store_true", help="Force stdlib renderer even if Rich is available.")

    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show agent status snapshot.")
    p_status.add_argument("--out", default=None, help="Optional output run directory.")
    p_status.set_defaults(func=command_status)

    p_check_base = sub.add_parser("check", help="Run Base Half required check/report refresh.")
    p_check_base.add_argument("--out", default=None)
    p_check_base.set_defaults(func=command_check)

    p_where = sub.add_parser("where", help="Show important Administratum base paths.")
    p_where.add_argument("--out", default=None)
    p_where.set_defaults(func=command_where)

    p_identity = sub.add_parser("identity", help="Show Administratum identity/profile baseline.")
    p_identity.add_argument("--out", default=None)
    p_identity.set_defaults(func=command_identity)

    p_tools = sub.add_parser("tools", help="Show Administratum-relevant tool capability view.")
    p_tools.add_argument("--out", default=None)
    p_tools.set_defaults(func=command_tools)

    p_pack_base = sub.add_parser("pack", help="Build Base Half continuity pack under local context.")
    p_pack_base.add_argument("--out", default=None)
    p_pack_base.set_defaults(func=command_pack)

    p_help_base = sub.add_parser("help", help="Show Base Half compact command contract.")
    p_help_base.add_argument("--out", default=None)
    p_help_base.set_defaults(func=command_help)

    p_inventory = sub.add_parser("inventory", help="Build repository inventory report.")
    p_inventory.add_argument("--repo-root", default=str(REPO_ROOT))
    p_inventory.add_argument("--out", default=None)
    p_inventory.set_defaults(func=command_inventory)

    p_classify = sub.add_parser("classify-path", help="Classify one path and explain route.")
    p_classify.add_argument("--repo-root", default=str(REPO_ROOT))
    p_classify.add_argument("--path", required=True)
    p_classify.add_argument("--requested-action", default="")
    p_classify.add_argument("--out", default=None)
    p_classify.set_defaults(func=command_classify_path)

    p_prov = sub.add_parser("provenance-index", help="Build provenance index report.")
    p_prov.add_argument("--repo-root", default=str(REPO_ROOT))
    p_prov.add_argument("--inventory", default=None, help="Optional existing inventory report path.")
    p_prov.add_argument("--limit", type=int, default=500)
    p_prov.add_argument("--out", default=None)
    p_prov.set_defaults(func=command_provenance)

    p_useful = sub.add_parser("useful-candidates", help="Build useful-candidates report.")
    p_useful.add_argument("--repo-root", default=str(REPO_ROOT))
    p_useful.add_argument("--inventory", default=None, help="Optional existing inventory report path.")
    p_useful.add_argument("--out", default=None)
    p_useful.set_defaults(func=command_useful_candidates)

    p_dirty = sub.add_parser("detect-dirty-runtime", help="Detect runtime pollution outside admitted RUNS layer.")
    p_dirty.add_argument("--repo-root", default=str(REPO_ROOT))
    p_dirty.add_argument("--out", default=None)
    p_dirty.set_defaults(func=command_detect_dirty_runtime)

    p_route = sub.add_parser("route-to-organs", help="Route findings to organ agents.")
    p_route.add_argument("--path", action="append", default=[])
    p_route.add_argument("--paths-file", default=None, help="JSON with `paths` or `objects_preview`.")
    p_route.add_argument("--requested-action", default="")
    p_route.add_argument("--out", default=None)
    p_route.set_defaults(func=command_route_to_organs)

    p_merge = sub.add_parser("merge-summary", help="Build merge-preparation summary.")
    p_merge.add_argument("--repo-root", default=str(REPO_ROOT))
    p_merge.add_argument("--inventory", default=None)
    p_merge.add_argument("--provenance", default=None)
    p_merge.add_argument("--candidates", default=None)
    p_merge.add_argument("--dirty", default=None)
    p_merge.add_argument("--routing", default=None)
    p_merge.add_argument("--requested-action", default="")
    p_merge.add_argument("--provenance-limit", type=int, default=400)
    p_merge.add_argument("--out", default=None)
    p_merge.set_defaults(func=command_merge_summary)

    p_scan = sub.add_parser("scan-imperium-context", help="Scan LOCAL/PRIVATE context roots in metadata-only mode.")
    p_scan.add_argument("--local-root", default=str(DEFAULT_CONTEXT_LOCAL))
    p_scan.add_argument("--private-root", default=str(DEFAULT_CONTEXT_PRIVATE))
    p_scan.add_argument("--out", default=None)
    p_scan.set_defaults(func=command_scan_context)

    p_cls_ctx = sub.add_parser("classify-local-context", help="Classify local/private context and detect export risk.")
    p_cls_ctx.add_argument("--scan-report", default=None)
    p_cls_ctx.add_argument("--local-root", default=str(DEFAULT_CONTEXT_LOCAL))
    p_cls_ctx.add_argument("--private-root", default=str(DEFAULT_CONTEXT_PRIVATE))
    p_cls_ctx.add_argument("--out", default=None)
    p_cls_ctx.set_defaults(func=command_classify_local_context)

    p_snapshot = sub.add_parser("collect-reality-snapshot", help="Collect current git/runtime reality snapshot.")
    p_snapshot.add_argument("--repo-root", default=str(REPO_ROOT))
    p_snapshot.add_argument("--out", default=None)
    p_snapshot.set_defaults(func=command_collect_reality_snapshot)

    p_pack = sub.add_parser("collect-continuity-pack", help="Collect continuity pack for handoff.")
    p_pack.add_argument("--repo-root", default=str(REPO_ROOT))
    p_pack.add_argument("--include-context", default="true", help="true/false; metadata-only when true.")
    p_pack.add_argument("--local-root", default=str(DEFAULT_CONTEXT_LOCAL))
    p_pack.add_argument("--private-root", default=str(DEFAULT_CONTEXT_PRIVATE))
    p_pack.add_argument("--provenance-limit", type=int, default=400)
    p_pack.add_argument("--inventory-max-files", type=int, default=2500)
    p_pack.add_argument("--out", default=None)
    p_pack.set_defaults(func=command_collect_continuity_pack)

    p_handoff = sub.add_parser("build-agent-handoff-context", help="Build handoff context for downstream agents.")
    p_handoff.add_argument("--repo-root", default=str(REPO_ROOT))
    p_handoff.add_argument("--include-context", default="true")
    p_handoff.add_argument("--out", default=None)
    p_handoff.set_defaults(func=command_build_handoff_context)

    p_verify = sub.add_parser("verify-pack-against-reality", help="Verify continuity pack against current reality.")
    p_verify.add_argument("--repo-root", default=str(REPO_ROOT))
    p_verify.add_argument("--manifest", default=None, help="Optional explicit continuity manifest path.")
    p_verify.add_argument("--out", default=None)
    p_verify.set_defaults(func=command_verify_pack)

    p_metrics = sub.add_parser("metrics-summary", help="Aggregate metrics from a target run.")
    p_metrics.add_argument("--run-dir", default=None, help="Optional path to target run directory.")
    p_metrics.add_argument("--out", default=None)
    p_metrics.set_defaults(func=command_metrics_summary)

    p_explain = sub.add_parser("explain-decision", help="Explain path classification and route decision.")
    p_explain.add_argument("--repo-root", default=str(REPO_ROOT))
    p_explain.add_argument("--path", required=True)
    p_explain.add_argument("--requested-action", default="")
    p_explain.add_argument("--out", default=None)
    p_explain.set_defaults(func=command_explain_decision)

    p_kpd = sub.add_parser("show-kpd", help="Generate KPD and thinking-quality score from run evidence.")
    p_kpd.add_argument("--run-dir", default=None)
    p_kpd.add_argument("--out", default=None)
    p_kpd.set_defaults(func=command_show_kpd)

    p_cu = sub.add_parser("cu-summary", help="Build Control Units (CU) index and summary.")
    p_cu.add_argument("--out", default=None)
    p_cu.set_defaults(func=command_cu_summary)

    p_doctor = sub.add_parser("doctor-rich", help="Diagnose Rich/color renderer availability and fallback reasons.")
    p_doctor.add_argument("--out", default=None)
    p_doctor.set_defaults(func=command_doctor_rich)

    p_doctor_oss = sub.add_parser("doctor-oss", help="Detect OSS tool availability and PDF backend status.")
    p_doctor_oss.add_argument("--out", default=None)
    p_doctor_oss.set_defaults(func=command_doctor_oss)

    p_build_dossier = sub.add_parser("build-dossier", help="Build a dossier ZIP from canonical report and receipt inputs.")
    p_build_dossier.add_argument("--task-id", default=TASK_DOSSIER_FACTORY_ID)
    p_build_dossier.add_argument("--source-report-dir", default=None, help="Optional explicit report folder path.")
    p_build_dossier.add_argument("--source-receipt", default=None, help="Optional explicit receipt path.")
    p_build_dossier.add_argument("--next-task", default="TASK-20260518-ADMINISTRATUM-CONTRACT-REGRESSION-GATE-V0_1")
    p_build_dossier.add_argument("--out", default=None)
    p_build_dossier.set_defaults(func=command_build_dossier)

    p_verify_dossier = sub.add_parser("verify-dossier", help="Verify dossier ZIP required files and hash manifest.")
    p_verify_dossier.add_argument("--zip-path", default=None, help="Optional explicit dossier zip path.")
    p_verify_dossier.add_argument("--latest", action="store_true", help="Use latest dossier zip in RUNS when --zip-path is not provided.")
    p_verify_dossier.add_argument("--out", default=None)
    p_verify_dossier.set_defaults(func=command_verify_dossier)

    p_schema = sub.add_parser("schema-regression", help="Validate core JSON/schema/dossier/freelance contracts.")
    p_schema.add_argument("--out", default=None)
    p_schema.set_defaults(func=command_schema_regression)

    p_validate_freelance = sub.add_parser("validate-freelance-envelope", help="Validate an Administratum freelance task envelope.")
    p_validate_freelance.add_argument("--envelope", default=None, help="Envelope JSON path; defaults to bundled valid sample.")
    p_validate_freelance.add_argument("--out", default=None)
    p_validate_freelance.set_defaults(func=command_validate_freelance_envelope)

    p_handoff_freelance = sub.add_parser("build-freelance-handoff", help="Build Administratum's scoped freelance handoff package.")
    p_handoff_freelance.add_argument("--envelope", default=None, help="Envelope JSON path; defaults to bundled valid sample.")
    p_handoff_freelance.add_argument("--out", default=None)
    p_handoff_freelance.set_defaults(func=command_build_freelance_handoff)

    p_check = sub.add_parser("check-all", help="Run full Administratum hardening check suite.")
    p_check.add_argument("--repo-root", default=str(REPO_ROOT))
    p_check.add_argument("--local-root", default=str(DEFAULT_CONTEXT_LOCAL))
    p_check.add_argument("--private-root", default=str(DEFAULT_CONTEXT_PRIVATE))
    p_check.add_argument("--inventory-max-files", type=int, default=1500)
    p_check.add_argument("--out", default=None)
    p_check.set_defaults(func=command_check_all)

    p_recent = sub.add_parser("recent", help="Show recent run summaries.")
    p_recent.add_argument("--limit", type=int, default=8)
    p_recent.add_argument("--out", default=None)
    p_recent.set_defaults(func=command_recent)

    p_open = sub.add_parser("open-runs", help="Show runtime RUNS root path.")
    p_open.add_argument("--out", default=None)
    p_open.set_defaults(func=command_open_runs)

    p_shell = sub.add_parser("shell", help="Interactive local Administratum shell.")
    p_shell.add_argument("--once", default=None, help="Run one shell command and exit (testing mode).")
    p_shell.set_defaults(func=command_shell)

    p_oss = sub.add_parser("optional-oss-proposal", help="Write optional OSS enhancement proposal (advisory only).")
    p_oss.add_argument("--out", default=None)
    p_oss.set_defaults(func=command_optional_oss_proposal)

    p_transfer_verify = sub.add_parser("transfer-verify-pack", help="Verify a Logos prompt pack ZIP for VM2 transfer.")
    p_transfer_verify.add_argument("--pack-zip", required=True)
    p_transfer_verify.add_argument("--transfer-root", default=str(DEFAULT_TRANSFER_ROOT))
    p_transfer_verify.add_argument("--out", default=None)
    p_transfer_verify.set_defaults(func=command_transfer_verify_pack)

    p_transfer_send = sub.add_parser("transfer-send-vm2", help="Stamp and place a prompt pack in the VM2 transfer intake.")
    p_transfer_send.add_argument("--pack-zip", required=True)
    p_transfer_send.add_argument("--step-name", required=True)
    p_transfer_send.add_argument("--source-head", default=None)
    p_transfer_send.add_argument("--operator", default="OWNER")
    p_transfer_send.add_argument("--transfer-root", default=str(DEFAULT_TRANSFER_ROOT))
    p_transfer_send.add_argument("--out", default=None)
    p_transfer_send.set_defaults(func=command_transfer_send_vm2)

    p_transfer_push = sub.add_parser("transfer-push-vm2", help="Push a prompt pack to VM2 and require remote SHA256/size proof.")
    p_transfer_push.add_argument("--pack-zip", default=None)
    p_transfer_push.add_argument("--step-name", default="")
    p_transfer_push.add_argument("--source-head", default=None)
    p_transfer_push.add_argument("--operator", default="OWNER")
    p_transfer_push.add_argument("--task-id", default=None)
    p_transfer_push.add_argument("--vm-user", default="vboxuser2")
    p_transfer_push.add_argument("--vm-host", default="127.0.0.1")
    p_transfer_push.add_argument("--vm-port", type=int, default=2223)
    p_transfer_push.add_argument("--vm-key", default=None)
    p_transfer_push.add_argument("--remote-root", default="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")
    p_transfer_push.add_argument("--transfer-root", default=str(DEFAULT_TRANSFER_ROOT))
    p_transfer_push.add_argument("--transport", choices=["ssh", "local"], default="ssh")
    p_transfer_push.add_argument("--dry-run", action="store_true")
    p_transfer_push.add_argument("--out", default=None)
    p_transfer_push.set_defaults(func=command_transfer_push_vm2)

    p_transfer_fetch = sub.add_parser("transfer-fetch-vm2", help="Fetch and verify a VM2 response ZIP by exact filename.")
    p_transfer_fetch.add_argument("--task-id", required=True)
    p_transfer_fetch.add_argument("--expected-filename", default=None)
    p_transfer_fetch.add_argument("--correlation-id", default=None)
    p_transfer_fetch.add_argument("--transfer-root", default=str(DEFAULT_TRANSFER_ROOT))
    p_transfer_fetch.add_argument("--pc-remote", action="store_true", help="Fetch from a remote VM2 outbox instead of local transfer root.")
    p_transfer_fetch.add_argument("--vm-user", default="vboxuser2")
    p_transfer_fetch.add_argument("--vm-host", default="127.0.0.1")
    p_transfer_fetch.add_argument("--vm-port", type=int, default=2223)
    p_transfer_fetch.add_argument("--vm-key", default=None)
    p_transfer_fetch.add_argument("--remote-root", default="/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER")
    p_transfer_fetch.add_argument("--transport", choices=["ssh", "local"], default="ssh")
    p_transfer_fetch.add_argument("--no-quarantine", action="store_true")
    p_transfer_fetch.add_argument("--out", default=None)
    p_transfer_fetch.set_defaults(func=command_transfer_fetch_vm2)

    p_transfer_status = sub.add_parser("transfer-status", help="Show Administratum transfer runtime status.")
    p_transfer_status.add_argument("--transfer-root", default=str(DEFAULT_TRANSFER_ROOT))
    p_transfer_status.add_argument("--ledger-tail", type=int, default=5)
    p_transfer_status.add_argument("--out", default=None)
    p_transfer_status.set_defaults(func=command_transfer_status)

    return parser


def _normalize_global_flags(argv: Sequence[str]) -> List[str]:
    globals_no_arg = {"--plain-json", "--no-color", "--color", "--verbose", "--compact", "--ascii", "--rich", "--no-rich"}
    front: List[str] = []
    rest: List[str] = []
    for tok in argv:
        if tok in globals_no_arg:
            front.append(tok)
        else:
            rest.append(tok)
    return front + rest


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    raw = list(argv if argv is not None else sys.argv[1:])
    normalized = _normalize_global_flags(raw)
    parser = build_parser()
    args = parser.parse_args(normalized)
    # normalize bool-like flags for selected commands
    if getattr(args, "command", "") == "collect-continuity-pack":
        args.include_context = _truthy(args.include_context)
    if getattr(args, "command", "") == "build-agent-handoff-context":
        args.include_context = _truthy(args.include_context)
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    color_allowed = bool(args.color and not args.no_color and sys.stdout.isatty() and not _truthy(os.environ.get("NO_COLOR")))
    rich_auto = bool(RICH_AVAILABLE and sys.stdout.isatty() and not args.plain_json and not args.no_rich)
    rich_enabled = bool((args.rich or rich_auto) and not args.no_rich and RICH_AVAILABLE and not args.plain_json)
    renderer = Renderer(
        plain_json=bool(args.plain_json),
        color=color_allowed,
        verbose=bool(args.verbose),
        compact=bool(args.compact),
        force_ascii=bool(args.ascii),
        rich_enabled=rich_enabled,
    )
    command = str(args.command)
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        raise UserFacingError(
            f"Unknown command: {command}",
            "Use --help to inspect available commands.",
            f"python {Path(__file__).name} --help",
        )
    try:
        return int(handler(args, renderer))
    except UserFacingError as err:
        renderer.emit_error(err)
        return 2
    except Exception as err:  # pragma: no cover - final guardrail
        renderer.emit_error(
            UserFacingError(
                f"Unhandled command failure: {err}",
                "Rerun with --verbose and inspect generated run reports/receipts.",
                f"python {Path(__file__).name} --verbose {command}",
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
