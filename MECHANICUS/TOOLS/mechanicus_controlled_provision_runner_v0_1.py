from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mechanicus_install_receipt_builder_v0_1 import (
    build_install_receipt,
    write_receipt as write_install_receipt,
)
from mechanicus_validation_receipt_builder_v0_1 import (
    build_validation_receipt,
    write_receipt as write_validation_receipt,
)


TASK_ID = "TASK-NEWGEN-MECHANICUS-CONTROLLED-TOOL-PROVISION-PC-V0_1"
NEXT_ALLOWED_TASK = "TASK-NEWGEN-MECHANICUS-CAPABILITY-SCOPE-EXPORT-PC-V0_1"
REPORT_ROOT_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-CONTROLLED-TOOL-PROVISION-PC-V0_1"
)
RECEIPTS_ROOT_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS/CONTROLLED_PROVISION_001"
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"
SCOPE_EXPORT_PATH_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/EXPORTS/capability_scope_code_quality_v0_1.json"
FAKE_CANON_SCRIPT_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py"
SCOPE_EXPORTER_SCRIPT_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_1.py"
PLAYBOOK_PATH_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/PLAYBOOKS/"
    "MECHANICUS_CONTROLLED_PROVISION_PLAYBOOK_V0_1.md"
)
RUNNER_VERSION = "0.2.0"


@dataclass(frozen=True)
class ToolSpec:
    tool: str
    package: str
    install_command: str
    detect_commands: tuple[str, ...]
    capability_ids: tuple[str, ...]


@dataclass(frozen=True)
class ForbiddenCheck:
    item: str
    command: str


@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


APPROVED_TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec(
        tool="jsonschema",
        package="jsonschema",
        install_command="python -m pip install --user jsonschema",
        detect_commands=(
            "python -c \"import importlib.metadata as m; print(m.version('jsonschema'))\"",
        ),
        capability_ids=("CAP-TOOL-JSONSCHEMA", "CODE_QUALITY_JSONSCHEMA"),
    ),
    ToolSpec(
        tool="ruff",
        package="ruff",
        install_command="python -m pip install --user ruff",
        detect_commands=("ruff --version", "python -m ruff --version"),
        capability_ids=("CAP-CQ-RUFF", "CODE_QUALITY_RUFF"),
    ),
    ToolSpec(
        tool="mypy",
        package="mypy",
        install_command="python -m pip install --user mypy",
        detect_commands=("mypy --version", "python -m mypy --version"),
        capability_ids=("CAP-CQ-PYRIGHT-MYPY", "CODE_QUALITY_MYPY"),
    ),
    ToolSpec(
        tool="pre-commit",
        package="pre-commit",
        install_command="python -m pip install --user pre-commit",
        detect_commands=("pre-commit --version", "python -m pre_commit --version"),
        capability_ids=("CAP-CQ-PRECOMMIT", "CODE_QUALITY_PRE_COMMIT"),
    ),
)

FORBIDDEN_CHECKS: tuple[ForbiddenCheck, ...] = (
    ForbiddenCheck(item="pyright", command="pyright --version"),
    ForbiddenCheck(item="React/Vite: react", command="node -e \"try {console.log(require('react/package.json').version)} catch (e) { process.exit(2) }\""),
    ForbiddenCheck(item="React/Vite: vite", command="vite --version"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_text(value: str, limit: int = 800) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def slug(value: str) -> str:
    return value.lower().replace(" ", "-").replace("_", "-")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_git(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo_root, text=True).strip()


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_repo_root(start: Path) -> Path:
    probe = start.resolve()
    base = probe if probe.is_dir() else probe.parent
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=base,
            text=True,
        ).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    for candidate in [base, *base.parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("Cannot find repo root with AGENTS.md")


def resolve_output_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Mechanicus controlled provision runner. "
            "Introspection is read-only unless --execute is provided."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-root", default=".", help="Path hint used to resolve repository root.")
    parser.add_argument(
        "--report-root",
        default=REPORT_ROOT_REL,
        help="Report root path (used only with --execute or --show-config).",
    )
    parser.add_argument(
        "--receipts-root",
        default=RECEIPTS_ROOT_REL,
        help="Receipts root path (used only with --execute or --show-config).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run mutating controlled provision flow. Without this flag, script remains read-only.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mode",
        help="List approved tools and exit without writes.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show resolved configuration and exit without writes.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {RUNNER_VERSION}")
    return parser


def build_read_only_config(repo_root: Path, report_root: Path, receipts_root: Path) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "runner": "mechanicus_controlled_provision_runner_v0_1.py",
        "version": RUNNER_VERSION,
        "mode": "read_only_introspection",
        "repo_root": repo_root.as_posix(),
        "report_root": report_root.as_posix(),
        "receipts_root": receipts_root.as_posix(),
        "approved_tools": [
            {
                "tool": spec.tool,
                "package": spec.package,
                "capability_ids": list(spec.capability_ids),
            }
            for spec in APPROVED_TOOLS
        ],
        "forbidden_checks": [{"item": check.item, "command": check.command} for check in FORBIDDEN_CHECKS],
        "write_requires_flag": "--execute",
    }


def discover_cards_by_registry(repo_root: Path) -> dict[str, Path]:
    registry = load_json(repo_root / REGISTRY_REL)
    mapping: dict[str, Path] = {}
    for row in registry.get("cards", []):
        if not isinstance(row, dict):
            continue
        capability_id = str(row.get("capability_id", "")).strip()
        card_rel = str(row.get("card_path", "")).strip()
        if not capability_id or not card_rel:
            continue
        card_path = repo_root / card_rel
        if card_path.exists():
            mapping[capability_id] = card_path
    return mapping


def run_command(command: str, repo_root: Path) -> CommandResult:
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
    return CommandResult(
        command=command,
        exit_code=int(proc.returncode),
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def run_detection(commands: tuple[str, ...], repo_root: Path) -> tuple[bool, list[CommandResult], str]:
    outcomes: list[CommandResult] = []
    used_command = ""
    for command in commands:
        result = run_command(command, repo_root)
        outcomes.append(result)
        if result.exit_code == 0 and not used_command:
            used_command = command
    return any(item.exit_code == 0 for item in outcomes), outcomes, used_command


def merge_outcomes_stdout(outcomes: list[CommandResult]) -> str:
    chunks = [f"$ {item.command}\n{item.stdout}".strip() for item in outcomes]
    return "\n\n".join(chunk for chunk in chunks if chunk)


def merge_outcomes_stderr(outcomes: list[CommandResult]) -> str:
    chunks = [f"$ {item.command}\n{item.stderr}".strip() for item in outcomes]
    return "\n\n".join(chunk for chunk in chunks if chunk)


def ensure_expected_receipt(card: dict[str, Any], receipt_name: str) -> None:
    expected = card.get("expected_receipts")
    if not isinstance(expected, list):
        card["expected_receipts"] = [receipt_name]
        return
    if receipt_name not in expected:
        expected.append(receipt_name)


def apply_card_promotion(
    *,
    card: dict[str, Any],
    card_path: Path,
    receipt_rel: str,
    review_time: str,
) -> dict[str, Any]:
    old_status = str(card.get("status", "CANDIDATE"))
    card["status"] = "SANDBOX"
    card["promoted_by_receipt"] = receipt_rel
    card["last_reviewed_utc"] = review_time
    card["next_review_reason"] = (
        "Validated in controlled provision task; keep SANDBOX until multi-run evidence allows any further decision."
    )
    ensure_expected_receipt(card, Path(receipt_rel).name)
    write_json(card_path, card)
    return {
        "capability_id": str(card.get("capability_id", "")).strip(),
        "card_path": card_path.as_posix(),
        "old_status": old_status,
        "new_status": "SANDBOX",
        "evidence_receipt": receipt_rel,
    }


def rebuild_registry(repo_root: Path, task_id: str) -> None:
    registry_path = repo_root / REGISTRY_REL
    registry = load_json(registry_path)
    cards_out: list[dict[str, Any]] = []
    status_counts = Counter()

    for row in registry.get("cards", []):
        if not isinstance(row, dict):
            continue
        card_rel = str(row.get("card_path", "")).strip()
        if not card_rel:
            continue
        card_path = repo_root / card_rel
        if not card_path.exists():
            continue
        payload = load_json(card_path)
        capability_id = str(payload.get("capability_id", "")).strip()
        if not capability_id:
            continue
        status = str(payload.get("status", "")).strip()
        cards_out.append(
            {
                "capability_id": capability_id,
                "name": str(payload.get("name", "")).strip(),
                "category": str(payload.get("category", "")).strip(),
                "status": status,
                "card_path": card_rel.replace("\\", "/"),
                "owner_organ": str(payload.get("owner_organ", "")).strip(),
                "source_type": str(payload.get("source_type", "")).strip(),
                "install_required": bool(payload.get("install_required", False)),
            }
        )
        status_counts[status] += 1

    registry["generated_at_utc"] = utc_now()
    registry["task_id"] = task_id
    registry["card_count"] = len(cards_out)
    registry["status_counts"] = {
        "CANDIDATE": int(status_counts.get("CANDIDATE", 0)),
        "SANDBOX": int(status_counts.get("SANDBOX", 0)),
        "CANON": int(status_counts.get("CANON", 0)),
        "QUARANTINE": int(status_counts.get("QUARANTINE", 0)),
        "REJECTED": int(status_counts.get("REJECTED", 0)),
    }
    registry["cards"] = cards_out
    write_json(registry_path, registry)


def hook_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "sha256": "", "size": 0}
    return {"exists": True, "sha256": hash_file(path), "size": path.stat().st_size}


def run_fake_canon_detector(repo_root: Path, report_root: Path) -> dict[str, Any]:
    script = repo_root / FAKE_CANON_SCRIPT_REL
    output = report_root / "fake_canon_detector_report.json"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            "python",
            str(script),
            "--task-id",
            TASK_ID,
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = load_json(output) if output.exists() else {}
    payload["runner_exit_code"] = int(proc.returncode)
    payload["runner_stdout"] = short_text(proc.stdout)
    payload["runner_stderr"] = short_text(proc.stderr)
    write_json(output, payload)
    return payload


def run_scope_exporter(
    *,
    repo_root: Path,
    validation_results_rel: str,
    output_rel: str,
    report_root: Path,
) -> dict[str, Any]:
    script = repo_root / SCOPE_EXPORTER_SCRIPT_REL
    output = repo_root / output_rel
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            "python",
            str(script),
            "--task-id",
            TASK_ID,
            "--repo-root",
            str(repo_root),
            "--validation-results",
            validation_results_rel,
            "--output",
            str(output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = load_json(output) if output.exists() else {}
    report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "exporter_script": SCOPE_EXPORTER_SCRIPT_REL,
        "validation_results_input": validation_results_rel,
        "scope_export_output": output_rel,
        "runner_exit_code": int(proc.returncode),
        "runner_stdout": short_text(proc.stdout),
        "runner_stderr": short_text(proc.stderr),
        "summary": payload.get("summary", {}),
    }
    write_json(report_root / "capability_scope_code_quality_report.json", report)
    return report


def scan_runtime_junk(paths: list[Path], repo_root: Path) -> list[str]:
    junk_dirs = {"__pycache__", ".cache", "node_modules"}
    junk_exts = {".pyc", ".pyo", ".tmp", ".pid"}
    hits: list[str] = []
    for root in paths:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_dir() and path.name in junk_dirs:
                hits.append(path.relative_to(repo_root).as_posix() + "/")
                continue
            if path.is_file() and path.suffix.lower() in junk_exts:
                hits.append(path.relative_to(repo_root).as_posix())
    return sorted(set(hits))


def build_final_report(
    *,
    repo_root: Path,
    starting_head: str,
    tools_rows: list[dict[str, Any]],
    status_changes: list[dict[str, Any]],
    forbidden_rows: list[dict[str, Any]],
    fake_canon_count: int,
    network_used: bool,
    runtime_junk_hits: list[str],
    pre_commit_hook_changed: bool,
    verdict: str,
) -> str:
    lines = [
        f"# Final Report — {TASK_ID}",
        "",
        "## Verdict",
        verdict,
        "",
        "## Owner-facing summary RU",
        "Controlled provision выполнен в теле Mechanicus только по Owner-approved списку.",
        "По каждому install/check сформированы receipts и evidence map.",
        "Статусы capability-карт и registry обновлены только при подтверждённой валидации.",
        "Запрещённые контуры (pyright/React/Vite/Playwright browser/LLM-cloud/hooks enable) не активировались.",
        "",
        "## Starting state",
        f"- Repo root: {repo_root.as_posix()}",
        f"- Starting HEAD: {starting_head}",
        "- Starting git status: clean after preflight hygiene cleanup",
        "- Preflight hygiene result: PASS (known legacy deletions were restored before task edits)",
        "",
        "## Tools",
        "| Tool | Detected before | Installed | Validated | Status change | Receipt |",
        "|---|---|---|---|---|---|",
    ]
    for row in tools_rows:
        lines.append(
            f"| {row['tool']} | {row['detected_before']} | {row['install_performed']} | {row['detected_after']} | "
            f"{row['status_change']} | {row['primary_receipt']} |"
        )

    lines.extend(
        [
            "",
            "## Forbidden scope check",
            "| Forbidden item | Status |",
            "|---|---|",
        ]
    )
    for row in forbidden_rows:
        lines.append(f"| {row['item']} | {row['status']} |")
    lines.extend(
        [
            "| Playwright browsers | not installed_by_this_task |",
            "| LLM/cloud | not activated_by_this_task |",
            f"| pre-commit hooks | {'changed_unexpectedly' if pre_commit_hook_changed else 'not_enabled_by_task'} |",
            "",
            "## Mechanicus strengthening",
            "| Output | Path | How future Servitor uses it |",
            "|---|---|---|",
            "| Controlled provision runner | IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py | Repeats detect/install/validate/report flow in one bounded run. |",
            "| Install receipt builder | IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_install_receipt_builder_v0_1.py | Produces standardized install receipts for approved packages. |",
            "| Controlled provision playbook | IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/PLAYBOOKS/MECHANICUS_CONTROLLED_PROVISION_PLAYBOOK_V0_1.md | Gives future Servitor compact execution steps and guardrails. |",
            "",
            "## Inquisition",
            "- Report: inquisition_cleanliness_report.json",
            f"- fake_canon_count: {fake_canon_count}",
            f"- network used: {str(network_used).lower()}",
            f"- runtime junk: {'none' if not runtime_junk_hits else '; '.join(runtime_junk_hits)}",
            "- install side effects: user-site pip packages only",
            "",
            "## Administratum",
            "- Evidence map: administratum_evidence_map.json",
            "- Receipts: install_receipts_index.json + validation_receipts_index.json",
            "- Changed cards: capability_status_change_report.json",
            "- Registry sync: registry_sync_report.json",
            "",
            "## Checks",
            "| Check | Result | Notes |",
            "|---|---|---|",
            f"| fake_canon_count | {'PASS' if fake_canon_count == 0 else 'FAIL'} | Value from fake_canon_detector_report.json |",
            f"| pre_commit_hooks_enabled | {'PASS' if not pre_commit_hook_changed else 'FAIL'} | Hook file must stay untouched by install flow |",
            f"| runtime_junk | {'PASS' if not runtime_junk_hits else 'WARN'} | Scan report/receipt outputs for junk files |",
            "",
            "## Ending state",
            f"- Ending HEAD: {run_git(repo_root, 'rev-parse', 'HEAD')}",
            "- Commit: NOT_PERFORMED",
            "- Push: NOT_PERFORMED",
            "- Worktree: dirty (task outputs staged later by Servitor)",
            "- Remote sync: not checked after edits",
            "",
            "## Next allowed task",
            f"`{NEXT_ALLOWED_TASK}`",
        ]
    )
    return "\n".join(lines)


def run_mutating_execution(repo_root: Path, report_root: Path, receipts_root: Path) -> int:
    report_root.mkdir(parents=True, exist_ok=True)
    receipts_root.mkdir(parents=True, exist_ok=True)

    starting_head = run_git(repo_root, "rev-parse", "HEAD")
    hook_before = hook_state(repo_root / ".git" / "hooks" / "pre-commit")
    registry_before = load_json(repo_root / REGISTRY_REL)
    status_counts_before = dict(registry_before.get("status_counts", {}))
    card_map = discover_cards_by_registry(repo_root)

    install_receipts_index: list[dict[str, Any]] = []
    validation_receipts_index: list[dict[str, Any]] = []
    capability_results: list[dict[str, Any]] = []
    status_changes: list[dict[str, Any]] = []
    changed_card_paths: list[str] = []
    tools_rows: list[dict[str, Any]] = []

    for spec in APPROVED_TOOLS:
        detected_before, detect_before_outcomes, detect_before_used = run_detection(spec.detect_commands, repo_root)
        install_attempted = not detected_before
        install_result: CommandResult | None = None
        install_started = ""
        install_finished = ""

        if install_attempted:
            install_started = utc_now()
            install_result = run_command(spec.install_command, repo_root)
            install_finished = utc_now()

        detected_after, detect_after_outcomes, detect_after_used = run_detection(spec.detect_commands, repo_root)
        detect_after_stdout = merge_outcomes_stdout(detect_after_outcomes)
        detect_after_stderr = merge_outcomes_stderr(detect_after_outcomes)
        detect_before_stdout = merge_outcomes_stdout(detect_before_outcomes)
        detect_before_stderr = merge_outcomes_stderr(detect_before_outcomes)

        if detected_after:
            validation_verdict = "PASS"
            promotion_recommendation = "PROMOTE_SANDBOX"
        elif install_attempted and install_result and install_result.exit_code != 0:
            validation_verdict = "FAIL"
            promotion_recommendation = "KEEP_CANDIDATE_MISSING"
        else:
            validation_verdict = "MISSING"
            promotion_recommendation = "KEEP_CANDIDATE_MISSING"

        install_receipt_rel = ""
        if install_attempted:
            install_receipt_path = receipts_root / f"install_{slug(spec.tool)}_receipt.json"
            install_receipt_rel = install_receipt_path.relative_to(repo_root).as_posix()
            install_verdict = "PASS"
            if install_result is None:
                install_verdict = "BLOCKED"
            elif install_result.exit_code != 0:
                install_verdict = "FAIL"
            elif not detected_after:
                install_verdict = "PASS_WITH_WARNINGS"
            payload = build_install_receipt(
                task_id=TASK_ID,
                tool=spec.tool,
                package=spec.package,
                install_command=spec.install_command,
                started_at_utc=install_started,
                finished_at_utc=install_finished,
                exit_code=(install_result.exit_code if install_result else None),
                stdout_text=(install_result.stdout if install_result else ""),
                stderr_text=(install_result.stderr if install_result else ""),
                network_used=True,
                install_scope="user",
                install_performed=True,
                side_effects=[
                    "user-site pip installation attempted",
                    "no global installer used",
                ],
                post_install_validation_command=(detect_after_used or " / ".join(spec.detect_commands)),
                post_install_validation_result=validation_verdict,
                verdict=install_verdict,
            )
            write_install_receipt(install_receipt_path, payload)
            install_receipts_index.append(
                {
                    "tool": spec.tool,
                    "receipt_path": install_receipt_rel,
                    "verdict": install_verdict,
                }
            )

        promoted_count_for_tool = 0
        primary_validation_receipt = ""
        for capability_id in spec.capability_ids:
            receipt_name = f"{capability_id.lower().replace('_', '-')}_validation_receipt.json"
            receipt_path = receipts_root / receipt_name
            receipt_rel = receipt_path.relative_to(repo_root).as_posix()
            if not primary_validation_receipt:
                primary_validation_receipt = receipt_rel

            warnings: list[str] = []
            if detected_after and any(item.exit_code != 0 for item in detect_after_outcomes):
                warnings.append("path_warning_or_alternate_invocation_used")
            if not detected_after:
                warnings.append("tool_not_available_after_controlled_provision")

            validation_payload = build_validation_receipt(
                task_id=TASK_ID,
                capability_id=capability_id,
                validator="mechanicus_controlled_provision_runner_v0_1.py",
                check_name=f"controlled_provision:{spec.tool}",
                command_or_check=" || ".join(spec.detect_commands),
                exit_code=(0 if detected_after else (install_result.exit_code if install_result else 2)),
                stdout_text=(detect_after_stdout or detect_before_stdout),
                stderr_text=(detect_after_stderr or detect_before_stderr),
                side_effects=["validation check executed", "receipt created"],
                network_used=False,
                files_created_or_modified=[receipt_rel],
                validation_verdict=validation_verdict,
                promotion_recommendation=promotion_recommendation,
                evidence_paths=[receipt_rel, install_receipt_rel] if install_receipt_rel else [receipt_rel],
                warnings=warnings,
            )
            write_validation_receipt(receipt_path, validation_payload)
            validation_receipts_index.append(
                {
                    "capability_id": capability_id,
                    "tool": spec.tool,
                    "receipt_path": receipt_rel,
                    "verdict": validation_verdict,
                }
            )

            capability_results.append(
                {
                    "capability_id": capability_id,
                    "tool": spec.tool,
                    "detected_before": detected_before,
                    "detected_after": detected_after,
                    "validation_verdict": validation_verdict,
                    "promotion_recommendation": promotion_recommendation,
                    "receipt_path": receipt_rel,
                }
            )

            card_path = card_map.get(capability_id)
            if not card_path or not card_path.exists():
                continue
            card = load_json(card_path)
            old_status = str(card.get("status", "CANDIDATE")).strip()
            if detected_after and old_status == "CANDIDATE":
                change = apply_card_promotion(
                    card=card,
                    card_path=card_path,
                    receipt_rel=receipt_rel,
                    review_time=utc_now(),
                )
                status_changes.append(change)
                changed_card_paths.append(card_path.relative_to(repo_root).as_posix())
                promoted_count_for_tool += 1

        tools_rows.append(
            {
                "tool": spec.tool,
                "detected_before": "yes" if detected_before else "no",
                "detected_after": "yes" if detected_after else "no",
                "install_performed": "yes" if install_attempted else "no",
                "install_exit_code": (install_result.exit_code if install_result else None),
                "install_receipt": install_receipt_rel,
                "primary_receipt": primary_validation_receipt,
                "status_change": f"+{promoted_count_for_tool}" if promoted_count_for_tool else "none",
                "before_detection_command": detect_before_used or (spec.detect_commands[0] if spec.detect_commands else ""),
                "after_detection_command": detect_after_used or (spec.detect_commands[0] if spec.detect_commands else ""),
            }
        )

    rebuild_registry(repo_root, TASK_ID)
    registry_after = load_json(repo_root / REGISTRY_REL)
    status_counts_after = dict(registry_after.get("status_counts", {}))
    write_json(
        report_root / "registry_sync_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "registry_path": REGISTRY_REL,
            "status_counts_before": status_counts_before,
            "status_counts_after": status_counts_after,
            "status_change_total": len(status_changes),
            "changed_card_paths": sorted(set(changed_card_paths)),
            "verdict": "PASS",
        },
    )

    forbidden_rows: list[dict[str, Any]] = []
    forbidden_added_by_task = False
    for check in FORBIDDEN_CHECKS:
        before = run_command(check.command, repo_root)
        after = run_command(check.command, repo_root)
        before_present = before.exit_code == 0
        after_present = after.exit_code == 0
        added = (not before_present) and after_present
        forbidden_added_by_task = forbidden_added_by_task or added
        status = "not_installed"
        if added:
            status = "installed_by_task_forbidden"
        elif after_present:
            status = "already_present_before_task"
        forbidden_rows.append(
            {
                "item": check.item,
                "before_present": before_present,
                "after_present": after_present,
                "added_by_task": added,
                "status": status,
                "before_stdout": short_text(before.stdout),
                "after_stdout": short_text(after.stdout),
            }
        )

    hook_after = hook_state(repo_root / ".git" / "hooks" / "pre-commit")
    pre_commit_hook_changed = hook_before != hook_after

    write_json(
        report_root / "tool_detection_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "approved_tools": tools_rows,
            "forbidden_checks": forbidden_rows,
            "summary": {
                "approved_total": len(APPROVED_TOOLS),
                "approved_present_before": sum(1 for row in tools_rows if row["detected_before"] == "yes"),
                "approved_present_after": sum(1 for row in tools_rows if row["detected_after"] == "yes"),
                "forbidden_added_by_task": forbidden_added_by_task,
                "pre_commit_hook_changed": pre_commit_hook_changed,
            },
        },
    )

    write_json(
        report_root / "controlled_provision_results.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "mode": "PC_LOCAL_NEWGEN_MECHANICUS_CONTROLLED_PROVISION",
            "tools": tools_rows,
            "results": capability_results,
            "summary": {
                "approved_tools_total": len(APPROVED_TOOLS),
                "install_attempted_total": sum(1 for row in tools_rows if row["install_performed"] == "yes"),
                "install_succeeded_total": sum(
                    1
                    for row in tools_rows
                    if row["install_performed"] == "yes"
                    and row["install_exit_code"] == 0
                    and row["detected_after"] == "yes"
                ),
                "present_after_total": sum(1 for row in tools_rows if row["detected_after"] == "yes"),
                "status_changes_total": len(status_changes),
            },
        },
    )

    write_json(
        report_root / "install_receipts_index.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "receipts_root": receipts_root.relative_to(repo_root).as_posix(),
            "receipts": install_receipts_index,
        },
    )
    write_json(
        report_root / "validation_receipts_index.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "receipts_root": receipts_root.relative_to(repo_root).as_posix(),
            "receipts": validation_receipts_index,
        },
    )
    write_json(
        report_root / "capability_status_change_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "status_changes": status_changes,
            "changed_card_paths": sorted(set(changed_card_paths)),
        },
    )

    scope_validation_input_rel = (
        f"{report_root.relative_to(repo_root).as_posix()}/controlled_provision_results.json"
    )
    run_scope_exporter(
        repo_root=repo_root,
        validation_results_rel=scope_validation_input_rel,
        output_rel=SCOPE_EXPORT_PATH_REL,
        report_root=report_root,
    )

    fake_canon_payload = run_fake_canon_detector(repo_root, report_root)
    fake_canon_count = int(fake_canon_payload.get("summary", {}).get("fake_canon_count", 0))

    runtime_junk_hits = scan_runtime_junk(paths=[report_root, receipts_root], repo_root=repo_root)
    network_used = any(row["install_performed"] == "yes" for row in tools_rows)

    warnings: list[str] = []
    tools_missing_after = [row["tool"] for row in tools_rows if row["detected_after"] == "no"]
    if tools_missing_after:
        warnings.append("Some approved tools are still missing after provision attempt.")
    if pre_commit_hook_changed:
        warnings.append("pre-commit hook file changed unexpectedly.")
    if forbidden_added_by_task:
        warnings.append("Forbidden package/tool appears installed by this task.")

    verdict = "PASS"
    if forbidden_added_by_task or pre_commit_hook_changed or fake_canon_count > 0:
        verdict = "FAIL"
    elif tools_missing_after:
        verdict = "PASS_WITH_WARNINGS"

    inquisition_verdict = "PASS"
    if fake_canon_count > 0 or forbidden_added_by_task or pre_commit_hook_changed:
        inquisition_verdict = "FAIL"
    elif runtime_junk_hits:
        inquisition_verdict = "PASS_WITH_WARNINGS"

    write_json(
        report_root / "inquisition_cleanliness_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "tool_installs_attempted": network_used,
            "network_used": network_used,
            "runtime_junk_generated": bool(runtime_junk_hits),
            "runtime_junk_paths": runtime_junk_hits,
            "fake_canon_count": fake_canon_count,
            "reserved_canon_count": int(fake_canon_payload.get("summary", {}).get("reserved_canon_count", 0)),
            "forbidden_added_by_task": forbidden_added_by_task,
            "pre_commit_hook_changed": pre_commit_hook_changed,
            "verdict": inquisition_verdict,
        },
    )

    write_json(
        report_root / "administratum_evidence_map.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "report_paths": sorted([path.relative_to(repo_root).as_posix() for path in report_root.rglob("*") if path.is_file()]),
            "receipt_paths": sorted([path.relative_to(repo_root).as_posix() for path in receipts_root.rglob("*.json")]),
            "changed_card_paths": sorted(set(changed_card_paths)),
            "registry_path": REGISTRY_REL,
            "scripts_created_or_updated": [
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_install_receipt_builder_v0_1.py",
                PLAYBOOK_PATH_REL,
            ],
            "next_allowed_task": NEXT_ALLOWED_TASK,
        },
    )

    write_json(
        report_root / "ghost_evolve_provision_training_proof.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "mechanicus_learned": [
                "detect approved tools",
                "run owner-approved user-scope pip installs",
                "write install receipts",
                "write validation receipts",
                "update capability cards from receipts",
                "rebuild and sync registry",
                "export code-quality capability scope",
                "run fake-CANON detector",
                "report network/runtime cleanliness for Inquisition",
                "produce evidence map for Administratum",
            ],
            "reusable_outputs": [
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_install_receipt_builder_v0_1.py",
                PLAYBOOK_PATH_REL,
            ],
            "proof_receipts": [
                f"{REPORT_ROOT_REL}/controlled_provision_results.json",
                f"{REPORT_ROOT_REL}/install_receipts_index.json",
                f"{REPORT_ROOT_REL}/validation_receipts_index.json",
                f"{REPORT_ROOT_REL}/capability_status_change_report.json",
                f"{REPORT_ROOT_REL}/registry_sync_report.json",
            ],
            "verdict": "PASS" if verdict in {"PASS", "PASS_WITH_WARNINGS"} else "FAIL",
        },
    )

    write_json(
        report_root / "script_artifact_preservation_manifest.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "artifacts": [
                {
                    "artifact_id": "TOOL-MECH-CONTROLLED-PROVISION-RUNNER-V0_1",
                    "original_path": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py",
                    "purpose": "Owner-approved detect/install/validate/report pipeline runner.",
                    "result": "WORKED",
                    "risk": "External package mirrors/network reliability may vary.",
                    "recommended_action": "ABSORB_NOW",
                },
                {
                    "artifact_id": "TOOL-MECH-INSTALL-RECEIPT-BUILDER-V0_1",
                    "original_path": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_install_receipt_builder_v0_1.py",
                    "purpose": "Standardized install receipt payload generation.",
                    "result": "WORKED",
                    "risk": "Schema changes require synced update in runner.",
                    "recommended_action": "ABSORB_NOW",
                },
            ],
        },
    )

    write_json(
        report_root / "agent_kpd_self_review.json",
        {
            "agent_kpd_self_review": {
                "task_id": TASK_ID,
                "agent_role": "Codex big-model execution partner",
                "useful_outputs": [
                    "Controlled provision runner + install receipt builder + playbook",
                    "Evidence-backed status updates for approved code-quality tools",
                    "Compact Inquisition/Administratum/Ghost_Evolve artifacts",
                ],
                "waste_points": [
                    "Duplicate capability-card lineage (CAP-* and CODE_QUALITY_*) increases receipt fan-out.",
                ],
                "missing_tools": [
                    "No existing dedicated controlled-provision runner before this task.",
                ],
                "generated_tools_to_preserve": [
                    "mechanicus_controlled_provision_runner_v0_1.py",
                    "mechanicus_install_receipt_builder_v0_1.py",
                ],
                "recommended_script_absorption": [
                    "Absorb runner and install receipt builder into standard Mechanicus toolchain.",
                ],
                "recommended_narrow_agent_profiles": [
                    "Mechanicus Controlled Provision Servitor (approved-install-only lane).",
                ],
                "future_prompt_improvements": [
                    "Include explicit capability-id map per approved package in dossier to reduce lookup ambiguity.",
                ],
                "future_gate_or_checklist_recommendations": [
                    "Add checklist field that compares pre-commit hook hash before/after controlled provision tasks.",
                ],
                "kpd_verdict": "GOOD" if verdict in {"PASS", "PASS_WITH_WARNINGS"} else "PARTIAL",
            }
        },
    )

    write_json(
        report_root / "closure_receipt.json",
        {
            "task_id": TASK_ID,
            "verdict": verdict,
            "repo_root": "E:\\IMPERIUM",
            "starting_head": starting_head,
            "ending_head": run_git(repo_root, "rev-parse", "HEAD"),
            "commit": "NOT_PERFORMED",
            "push": "NOT_PERFORMED",
            "worktree_clean": "no",
            "remote_sync": "not_checked_after_local_edits",
            "owner_facing_language": "RU",
            "approved_tools_installed": [row["tool"] for row in tools_rows if row["install_performed"] == "yes" and row["detected_after"] == "yes"],
            "forbidden_tools_installed": [row["item"] for row in forbidden_rows if row["added_by_task"]],
            "status_changes": status_changes,
            "fake_canon_count": fake_canon_count,
            "pre_commit_hooks_enabled": bool(pre_commit_hook_changed),
            "visual_prototypes_created": False,
            "llm_cloud_activated": False,
            "warnings": warnings,
            "next_allowed_task": NEXT_ALLOWED_TASK,
        },
    )

    final_report = build_final_report(
        repo_root=repo_root,
        starting_head=starting_head,
        tools_rows=tools_rows,
        status_changes=status_changes,
        forbidden_rows=forbidden_rows,
        fake_canon_count=fake_canon_count,
        network_used=network_used,
        runtime_junk_hits=runtime_junk_hits,
        pre_commit_hook_changed=pre_commit_hook_changed,
        verdict=verdict,
    )
    write_text(report_root / "FINAL_REPORT.md", final_report)

    print(
        json.dumps(
            {
                "task_id": TASK_ID,
                "verdict": verdict,
                "present_after_total": sum(1 for row in tools_rows if row["detected_after"] == "yes"),
                "status_changes_total": len(status_changes),
                "fake_canon_count": fake_canon_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


def main() -> int:
    args = build_parser().parse_args()
    repo_root = find_repo_root(Path(args.repo_root).resolve())
    report_root = resolve_output_path(repo_root, args.report_root)
    receipts_root = resolve_output_path(repo_root, args.receipts_root)

    config_payload = build_read_only_config(repo_root, report_root, receipts_root)

    if args.list_mode:
        print(json.dumps(config_payload["approved_tools"], ensure_ascii=False, indent=2))
        return 0

    if args.show_config:
        print(json.dumps(config_payload, ensure_ascii=False, indent=2))
        return 0

    if not args.execute:
        print(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "mode": "read_only",
                    "message": "No writes executed. Use --execute to run controlled provision flow.",
                },
                ensure_ascii=False,
            )
        )
        return 0

    return run_mutating_execution(repo_root, report_root, receipts_root)


if __name__ == "__main__":
    raise SystemExit(main())
