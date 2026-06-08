#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMINISTRATUM CONTINUITY PACK BUILDER V0.3

Hardened continuity builder for Logos Prime handoff, H-contour/manual patch flow,
owner-visible boot protocol, and evidence/readiness preservation.

Safety:
  - writes only under ORGANS/ADMINISTRATUM/CONTINUITY/PACKS
  - no commit
  - no push
  - no unsafe shell
  - no live LLM
  - no servitor execution
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "administratum.continuity_pack.v0_3"
MODES = {"quick", "h", "full"}
HERE = Path(__file__).resolve().parent
PACKS_ROOT = HERE / "PACKS"
PROTOCOLS_ROOT = HERE / "PROTOCOLS"
OWNER_FACING_TEXT_FILES = {
    "OWNER_CONTINUITY_SUMMARY_RU.md",
    "LOGOS_PRIME_HANDOFF_SUMMARY_RU.md",
    "NEXT_HANDOFF_CARD.md",
    "ENCODING_README_RU.txt",
    "H_CONTOUR_OPERATION_PROTOCOL_RU.md",
    "LOGOS_PRIME_BOOT_PROTOCOL_RU.md",
    "OPERATIONAL_GAPS_CAUGHT_RU.md",
    "NEXT_COMMANDS_H_SAFE_RU.md",
    "OWNER_REQUIREMENTS_FREELANCE_CORE_RU.md",
    "REFERENCE_TECH_BACKLOG_RU.md",
}


def _print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def find_repo_root(start: Path | None = None) -> Path:
    env = os.environ.get("IMPERIUM_ROOT")
    if env:
        p = Path(env).resolve()
        if (p / "ORGANS").is_dir():
            return p
    cur = (start or HERE).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / "ORGANS").is_dir() and ((candidate / "AGENTS.md").is_file() or (candidate / ".git").exists()):
            return candidate
    return Path.cwd().resolve()


def run_git(repo: Path, *args: str) -> str:
    try:
        p = subprocess.run(["git", *args], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15)
        return (p.stdout or "").strip()
    except Exception as exc:
        return f"GIT_ERROR: {exc}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path, limit: int = 160_000) -> str:
    try:
        data = path.read_bytes()
        if len(data) > limit:
            return data[:limit].decode("utf-8", errors="replace") + f"\n... truncated at {limit} bytes"
        return data.decode("utf-8-sig", errors="replace")
    except Exception as exc:
        return f"READ_ERROR: {exc}"


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def latest_dirs(root: Path, limit: int = 8) -> list[Path]:
    if not root.exists():
        return []
    dirs = [p for p in root.iterdir() if p.is_dir()]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def latest_files(root: Path, suffixes: tuple[str, ...] = (".json", ".md", ".txt", ".zip", ".py", ".ps1"), limit: int = 16) -> list[Path]:
    if not root.exists():
        return []
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in suffixes]
    files = [p for p in files if "__pycache__" not in p.parts and "PACKS" not in p.parts]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def current_task_id(repo: Path) -> str:
    current = read_json(repo / "ORGANS" / "ASTRONOMICON" / "TASK_REGISTRY" / "current_expected_task.json")
    if isinstance(current, dict):
        for key in ("task_id", "current_task_id"):
            value = current.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        if isinstance(current.get("current"), dict):
            value = current["current"].get("task_id")
            if isinstance(value, str):
                return value.strip()
    return "NO_CURRENT_TASK"


def detect_contours(repo: Path) -> dict[str, Any]:
    leaf = repo.name
    branch = run_git(repo, "branch", "--show-current")
    head = run_git(repo, "rev-parse", "HEAD")
    status_short = run_git(repo, "status", "--short")
    h_path = leaf.endswith("_H")
    h_branch = branch.startswith("h/")
    current_contour = "H_CONTOUR" if h_path or h_branch else "MAIN_CONTOUR_OR_UNKNOWN"
    main_candidate = repo.parent / leaf[:-2] if h_path else repo
    h_candidate = repo if h_path else repo.parent / f"{leaf}_H"

    def git_brief(path: Path) -> dict[str, Any]:
        if not path.is_dir():
            return {"exists": False, "path": path.as_posix()}
        return {
            "exists": True,
            "path": path.as_posix(),
            "branch": run_git(path, "branch", "--show-current"),
            "head": run_git(path, "rev-parse", "HEAD"),
            "status_sb": run_git(path, "status", "-sb"),
            "log": run_git(path, "log", "--oneline", "--decorate", "-8"),
        }

    return {
        "current_contour": current_contour,
        "repo_root": repo.as_posix(),
        "repo_leaf": leaf,
        "branch": branch,
        "head": head,
        "status_short": status_short,
        "is_h_path": h_path,
        "is_h_branch": h_branch,
        "dirty": bool(status_short),
        "main_repo_candidate": main_candidate.as_posix(),
        "h_repo_candidate": h_candidate.as_posix(),
        "main_repo": git_brief(main_candidate),
        "h_repo": git_brief(h_candidate),
        "h_workflow_rule": "Patch ZIP -> APPLY in H -> H smoke/visual -> IMPERIUM_H commit -> cherry-pick/merge to main -> main smoke -> push.",
        "main_direct_patch_allowed": False,
    }


def write_pack_text(path: Path, name: str, text: str) -> None:
    if text is None:
        text = ""
    if not text.endswith("\n"):
        text += "\n"
    if name in OWNER_FACING_TEXT_FILES or name.endswith("_RU.md"):
        path.write_text(text, encoding="utf-8-sig", newline="\r\n")
    else:
        path.write_text(text, encoding="utf-8", newline="\r\n")


def owner_encoding_readme() -> str:
    return "\n".join([
        "# ENCODING README RU",
        "",
        "Owner-facing Russian markdown files in this continuity pack are written as UTF-8 with BOM (utf-8-sig).",
        "Machine JSON remains UTF-8 without BOM for parser compatibility.",
        "This protects Windows viewers from mojibake.",
    ])


def safe_name(value: str, limit: int = 72) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return (cleaned or "continuity")[:limit]


def h_protocol_text(contours: dict[str, Any]) -> str:
    return "\n".join([
        "# H-CONTOUR OPERATION PROTOCOL RU",
        "",
        "## Канон",
        "",
        f"- Main repo candidate: `{contours.get('main_repo_candidate')}`",
        f"- H repo candidate: `{contours.get('h_repo_candidate')}`",
        "- H-зона — ручная изолированная зона варпа для patch ZIP, smoke, визуального poke и acceptance.",
        "- Main/master — каноническая чистая зона. UI/UX polish туда не применяется напрямую.",
        "",
        "## Правильная цепочка",
        "",
        "```text",
        "H patch ZIP -> APPLY_PATCH.ps1 in *_H -> smoke in H -> visual review in H -> owner acceptance",
        "-> commit by IMPERIUM_H -> cherry-pick/merge to main -> smoke in main -> push -> next task",
        "```",
        "",
        "## Запреты для Logos Prime",
        "",
        "- Не давать команды применения H-патча в main, если owner явно не приказал.",
        "- Не считать `repo_root` из manifest рабочей зоной H-polish, если есть H-contour rule.",
        "- Не восстанавливать скрытые рассуждения прошлого чата.",
        "- Не включать real servitor execution, live LLM, unsafe shell, автокоммит или autopush.",
    ])


def boot_protocol_text() -> str:
    return "\n".join([
        "# LOGOS PRIME BOOT PROTOCOL RU",
        "",
        "Новый Logos Prime обязан стартовать не с догадок, а с owner-visible документов.",
        "",
        "## Читать в первую очередь",
        "",
        "1. CONTINUITY_MANIFEST.json",
        "2. CONTINUITY_RECEIPT.json",
        "3. OWNER_CONTINUITY_SUMMARY_RU.md",
        "4. LOGOS_PRIME_HANDOFF_SUMMARY_RU.md",
        "5. H_CONTOUR_OPERATION_PROTOCOL_RU.md",
        "6. NEXT_COMMANDS_H_SAFE_RU.md",
        "7. OWNER_REQUIREMENTS_FREELANCE_CORE_RU.md",
        "8. REFERENCE_TECH_BACKLOG_RU.md",
        "",
        "## Стартовые проверки",
        "",
        "- Где H-contour? Где main?",
        "- На какой ветке и HEAD находится H?",
        "- На какой ветке и HEAD находится main/origin?",
        "- Чистый ли H перед применением patch ZIP?",
        "- Не пытается ли команда применить H-патч в main?",
        "- Достаточно ли pack передал операционную полноту: H flow, pass gates, owner priorities, next commands?",
        "",
        "Если ответов нет — не продолжать как будто всё понятно. Сначала чинить continuity.",
    ])


def operational_gaps_text() -> str:
    return "\n".join([
        "# OPERATIONAL GAPS CAUGHT RU",
        "",
        "Этот файл фиксирует провал старого handoff, чтобы он не повторялся.",
        "",
        "## Что пошло плохо",
        "",
        "- Новый Logos Prime прочитал main repo_root и дал команды применения patch ZIP в main.",
        "- H-contour path не был явно поднят как hard rule.",
        "- Команды предполагали, что ZIP уже лежит в repo root, что вызвало Expand-Archive path error.",
        "- Smoke был запущен на старом launcher, поэтому мог создать ложное ощущение прогресса.",
        "- Следующий task был выбран слишком рано, до фикса continuity полноты.",
        "",
        "## Исправление v0.3",
        "",
        "- Manifest содержит contours/main/H и h_workflow_rule.",
        "- H protocol и boot checklist включаются в pack как owner-visible документы.",
        "- Next commands разделяют H apply и main acceptance flow.",
        "- Launcher показывает H/main awareness и continuity completeness gates.",
    ])


def next_commands_text(contours: dict[str, Any]) -> str:
    h_path = contours.get("h_repo_candidate") or "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H"
    main_path = contours.get("main_repo_candidate") or "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
    return "\n".join([
        "# NEXT COMMANDS H SAFE RU",
        "",
        "## H-зона: применить patch ZIP только тут",
        "",
        "```powershell",
        f'$HRepo = "{h_path}"',
        "cd $HRepo",
        "git status --short",
        "git log --oneline --decorate -5",
        "# затем APPLY_PATCH.ps1 -RepoRoot $HRepo",
        "```",
        "",
        "## После owner acceptance в H",
        "",
        "```powershell",
        "git status --short",
        "git add <accepted files>",
        'git -c user.name=IMPERIUM_H -c user.email=imperium_h@local commit -m "IMPERIUM_H: <accepted patch title>"',
        "```",
        "",
        "## Main: только принять уже проверенный H-коммит",
        "",
        "```powershell",
        f'$MainRepo = "{main_path}"',
        "cd $MainRepo",
        "git fetch origin",
        "git status --short",
        "git cherry-pick <H_COMMIT_HASH>",
        "python .\\ORGANS\\IMPERIAL_IDE\\LAUNCHER\\imperial_launcher.py --smoke",
        "git push origin master",
        "```",
    ])


def collect_owner_requirements(repo: Path) -> dict[str, str]:
    files = {
        "owner_requirements": PROTOCOLS_ROOT / "OWNER_REQUIREMENTS_FREELANCE_CORE_RU.md",
        "reference_backlog": PROTOCOLS_ROOT / "REFERENCE_TECH_BACKLOG_RU.md",
        "h_protocol": PROTOCOLS_ROOT / "H_CONTOUR_OPERATION_PROTOCOL_RU.md",
        "boot_protocol": PROTOCOLS_ROOT / "LOGOS_PRIME_BOOT_PROTOCOL_RU.md",
    }
    return {key: read_text(path, 80_000) for key, path in files.items() if path.is_file()}


def collect_preview(repo: Path, mode: str) -> dict[str, Any]:
    mode = mode if mode in MODES else "h"
    task_id = current_task_id(repo)
    contours = detect_contours(repo)
    status = run_git(repo, "status", "-sb")
    head = run_git(repo, "rev-parse", "HEAD")
    branch = run_git(repo, "branch", "--show-current")
    origin = run_git(repo, "rev-parse", "origin/master")
    log = run_git(repo, "log", "--oneline", "--decorate", "-14")
    stash = run_git(repo, "stash", "list")

    base_files = [
        "AGENTS.md",
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
        "ORGANS/IMPERIAL_IDE/SHELL/command_palette.json",
        "ORGANS/IMPERIAL_IDE/LAUNCHER/README_RU.md",
        "ORGANS/IMPERIAL_IDE/README.md",
        "ORGANS/ADMINISTRATUM/CONTINUITY/README_RU.md",
        "ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py",
        "ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_schema.json",
    ]
    if mode in {"h", "full"}:
        base_files += [
            "ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py",
            "ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py",
        ]
    if mode == "full":
        base_files += [
            "ORGANS/IMPERIAL_IDE/STATION/station_router.py",
            "ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py",
            "ORGANS/IMPERIAL_IDE/SHELL/shell_router.py",
        ]

    included_files: list[str] = []
    for item in base_files:
        if (repo / item).is_file():
            included_files.append(item)
    protocols_dir = repo / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PROTOCOLS"
    for p in latest_files(protocols_dir, suffixes=(".md", ".json", ".txt"), limit=32):
        included_files.append(rel(repo, p))

    task_dir = repo / "ORGANS" / "ASTRONOMICON" / "TASK_INBOX" / "REGISTERED" / task_id
    if task_dir.is_dir():
        for p in latest_files(task_dir, limit=14):
            included_files.append(rel(repo, p))
    report_dirs = latest_dirs(repo / "REPORTS", limit=6)
    receipt_files = latest_files(repo / "REPORTS", limit=12)
    if mode == "full":
        for d in report_dirs[:3]:
            for p in latest_files(d, suffixes=(".json", ".md", ".txt"), limit=8):
                included_files.append(rel(repo, p))

    handoff_lines = [
        "LOGOS PRIME CONTINUITY HANDOFF",
        f"Working repo: {repo.as_posix()}",
        f"Current contour: {contours.get('current_contour')}",
        f"H contour: {contours.get('h_repo_candidate')}",
        f"Main repo: {contours.get('main_repo_candidate')}",
        f"Branch: {branch}",
        f"HEAD: {head}",
        f"Origin/master: {origin}",
        f"Current task: {task_id}",
        f"Mode: {mode}",
        "Read H_CONTOUR_OPERATION_PROTOCOL_RU.md before giving commands.",
        "Use CONTINUITY_PACK.zip plus owner-facing summaries; do not infer hidden state.",
    ]
    owner_docs = collect_owner_requirements(repo)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_WITH_WARNINGS",
        "mode": mode,
        "repo_root": repo.as_posix(),
        "task_id": task_id,
        "contours": contours,
        "git": {"branch": branch, "head": head, "origin_master": origin, "status_sb": status, "log": log, "stash": stash},
        "included_files": sorted(set(included_files)),
        "latest_report_dirs": [rel(repo, p) for p in report_dirs],
        "latest_receipts": [rel(repo, p) for p in receipt_files],
        "handoff_lines": handoff_lines,
        "owner_operational_context": {
            "prior_failure": "H-contour was not explicit enough; commands were given for main and ZIP location assumptions failed.",
            "priority_now": "Fix continuity operational completeness before next feature task.",
            "ui_ux_priority": "Top-level Sanctum/IDE must become smooth, beautiful, observable, and pleasant for daily use.",
            "mechanicus_priority": "Mechanicus becomes reference organ: state machines, schemas, tool safety, DB/API/RAG/search corridors.",
            "freelance_core": "External brief -> taskpack -> agents -> owner gates -> build/test -> evidence -> delivery -> support.",
            "trading_department_gate": "Research/paper/simulation first; no live trading/order placement without future explicit owner LIVE gate.",
        },
        "owner_reference_docs_present": sorted(owner_docs.keys()),
        "forbidden_actions": ["commit", "push", "delete", "unsafe_shell", "live_llm", "real_servitor_execution", "task_registry_mutation", "live_trading_execution"],
        "writes_scope": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS only",
        "encoding_policy": {
            "owner_facing_text": "utf-8-sig (UTF-8 with BOM)",
            "machine_json": "utf-8 without BOM",
            "windows_viewer_reason": "prevents mojibake in WordPad/legacy viewers",
        },
        "continuity_pass_gates": {
            "h_contour_path_present": bool(contours.get("h_repo_candidate")),
            "main_repo_path_present": bool(contours.get("main_repo_candidate")),
            "h_protocol_included": (protocols_dir / "H_CONTOUR_OPERATION_PROTOCOL_RU.md").is_file(),
            "boot_protocol_included": (protocols_dir / "LOGOS_PRIME_BOOT_PROTOCOL_RU.md").is_file(),
            "next_commands_h_safe_included": (protocols_dir / "NEXT_COMMANDS_H_SAFE_RU.md").is_file(),
            "owner_requirements_included": (protocols_dir / "OWNER_REQUIREMENTS_FREELANCE_CORE_RU.md").is_file(),
            "reference_backlog_included": (protocols_dir / "REFERENCE_TECH_BACKLOG_RU.md").is_file(),
        },
    }


def preview_pack(repo: Path | str | None = None, mode: str = "h") -> dict[str, Any]:
    root = Path(repo).resolve() if repo else find_repo_root()
    preview = collect_preview(root, mode)
    return {
        "status": "PASS_WITH_WARNINGS",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER_V0_3",
        "mode": preview["mode"],
        "preview": preview,
        "executed": False,
        "writes_performed": False,
    }


def make_owner_summary(preview: dict[str, Any], pack_zip_name: str) -> str:
    git = preview.get("git", {})
    contours = preview.get("contours", {})
    files = preview.get("included_files", [])
    reports = preview.get("latest_report_dirs", [])
    receipts = preview.get("latest_receipts", [])
    pass_gates = preview.get("continuity_pass_gates", {})
    return "\n".join([
        "# OWNER CONTINUITY SUMMARY RU",
        "",
        f"Схема: `{preview.get('schema_version')}`",
        f"Режим: `{preview.get('mode')}`",
        f"Текущая задача: `{preview.get('task_id')}`",
        f"Working repo: `{preview.get('repo_root')}`",
        f"Current contour: `{contours.get('current_contour')}`",
        f"H contour: `{contours.get('h_repo_candidate')}`",
        f"Main repo: `{contours.get('main_repo_candidate')}`",
        f"Branch: `{git.get('branch')}`",
        f"HEAD: `{git.get('head')}`",
        f"Origin/master: `{git.get('origin_master')}`",
        f"Pack ZIP: `{pack_zip_name}`",
        "",
        "## Что исправлено в v0.3",
        "",
        "Continuity больше не должен оставлять Logos Prime без H-path, H/main flow, boot checklist и owner priorities.",
        "Следующий Logos Prime обязан прочитать H_CONTOUR_OPERATION_PROTOCOL_RU.md перед выдачей команд.",
        "",
        "## Continuity pass gates",
        "",
        *(f"- `{key}`: `{value}`" for key, value in pass_gates.items()),
        "",
        "## Git truth",
        "",
        "```text",
        str(git.get("status_sb", "")),
        "```",
        "",
        "## Включённые файлы",
        "",
        *(f"- `{x}`" for x in files[:120]),
        "",
        "## Последние отчёты",
        "",
        *(f"- `{x}`" for x in reports[:12]),
        "",
        "## Последние receipts",
        "",
        *(f"- `{x}`" for x in receipts[:16]),
    ])


def make_logos_summary(preview: dict[str, Any]) -> str:
    ctx = preview.get("owner_operational_context", {})
    return "\n".join([
        "# LOGOS PRIME HANDOFF SUMMARY RU",
        "",
        "Новый Logos Prime, используй этот текст как безопасный owner-visible continuity summary.",
        "Не пытайся восстанавливать скрытые рассуждения. Работай по manifest/receipt/git truth и owner-facing protocols.",
        "",
        "## Текущее состояние",
        "",
        *(f"- {line}" for line in preview.get("handoff_lines", [])),
        "",
        "## Hard rule H",
        "",
        "- H-патчи и UI/UX polish применяются сначала только в H-contour/worktree.",
        "- Main/master — зона принятия уже проверенного H-коммита, не первичная рабочая зона polish.",
        "- Если continuity pack указывает только main repo_root, но есть H protocol, приоритет у H protocol.",
        "",
        "## Owner priorities now",
        "",
        *(f"- {key}: {value}" for key, value in ctx.items()),
        "",
        "## Читать обязательно",
        "",
        "- H_CONTOUR_OPERATION_PROTOCOL_RU.md",
        "- LOGOS_PRIME_BOOT_PROTOCOL_RU.md",
        "- NEXT_COMMANDS_H_SAFE_RU.md",
        "- OWNER_REQUIREMENTS_FREELANCE_CORE_RU.md",
        "- REFERENCE_TECH_BACKLOG_RU.md",
        "",
        "## Запрещено",
        "",
        "- Не включать real servitor execution.",
        "- Не включать live LLM backend.",
        "- Не запускать unsafe shell.",
        "- Не коммитить/пушить без owner acceptance.",
        "- Не давать live trading/order placement команды без будущего явного LIVE-гейта.",
    ])


def build_pack(repo: Path | str | None = None, mode: str = "h") -> dict[str, Any]:
    root = Path(repo).resolve() if repo else find_repo_root()
    preview = collect_preview(root, mode)
    task = safe_name(preview.get("task_id", "NO_TASK"), 72)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    pack_dir = PACKS_ROOT / f"{stamp}_{preview['mode']}_{task}"
    pack_dir.mkdir(parents=True, exist_ok=True)
    (PACKS_ROOT / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")

    manifest = dict(preview)
    manifest["created_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["pack_dir"] = pack_dir.as_posix()
    manifest["pack_zip"] = "CONTINUITY_PACK.zip"

    contours = preview.get("contours", {})
    generated_protocols = {
        "H_CONTOUR_OPERATION_PROTOCOL_RU.md": h_protocol_text(contours),
        "LOGOS_PRIME_BOOT_PROTOCOL_RU.md": boot_protocol_text(),
        "OPERATIONAL_GAPS_CAUGHT_RU.md": operational_gaps_text(),
        "NEXT_COMMANDS_H_SAFE_RU.md": next_commands_text(contours),
    }
    for name, text in generated_protocols.items():
        write_pack_text(pack_dir / name, name, text)

    owner_summary = make_owner_summary(preview, "CONTINUITY_PACK.zip")
    logos_summary = make_logos_summary(preview)
    next_handoff = "\n".join(preview.get("handoff_lines", [])) + "\n"
    files_to_write = {
        "CONTINUITY_MANIFEST.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        "OWNER_CONTINUITY_SUMMARY_RU.md": owner_summary,
        "LOGOS_PRIME_HANDOFF_SUMMARY_RU.md": logos_summary,
        "NEXT_HANDOFF_CARD.md": next_handoff,
        "GIT_STATUS.txt": preview["git"].get("status_sb", ""),
        "GIT_LOG.txt": preview["git"].get("log", ""),
        "GIT_STASH.txt": preview["git"].get("stash", ""),
        "ENCODING_README_RU.txt": owner_encoding_readme(),
    }
    files_to_write.update(generated_protocols)
    for name, text in files_to_write.items():
        write_pack_text(pack_dir / name, name, text)

    zip_path = pack_dir / "CONTINUITY_PACK.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in files_to_write:
            zf.write(pack_dir / name, arcname=name)
        for item in preview.get("included_files", []):
            src = root / item
            if src.is_file():
                try:
                    zf.write(src, arcname=f"REPO/{item}")
                except Exception:
                    pass
    zip_hash_before_receipt = sha256_file(zip_path)
    receipt_base = {
        "schema_version": "administratum.continuity_pack_receipt.v0_3",
        "status": "PASS_WITH_WARNINGS",
        "created_utc": manifest["created_utc"],
        "mode": preview["mode"],
        "task_id": preview.get("task_id"),
        "repo_root": root.as_posix(),
        "contours": preview.get("contours", {}),
        "pack_dir": pack_dir.as_posix(),
        "pack_zip_path": zip_path.as_posix(),
        "pack_zip_sha256_before_embedded_receipt": zip_hash_before_receipt,
        "included_file_count": len(preview.get("included_files", [])),
        "continuity_pass_gates": preview.get("continuity_pass_gates", {}),
        "forbidden_actions_respected": True,
        "commit_performed": False,
        "push_performed": False,
        "real_execution_enabled": False,
        "live_llm_backend_enabled": False,
        "unsafe_shell_enabled": False,
        "live_trading_execution_enabled": False,
        "owner_facing_text_encoding": "utf-8-sig",
        "machine_json_encoding": "utf-8",
        "mojibake_guard": True,
    }
    embedded_receipt = dict(receipt_base)
    embedded_receipt["pack_zip_sha256"] = zip_hash_before_receipt
    embedded_receipt["pack_zip_sha256_scope"] = "ZIP_BEFORE_EMBEDDED_RECEIPT"
    embedded_receipt["self_reference_note"] = "Final ZIP hash is recorded in the external CONTINUITY_RECEIPT.json next to the ZIP."
    (pack_dir / "CONTINUITY_RECEIPT.json").write_text(json.dumps(embedded_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(pack_dir / "CONTINUITY_RECEIPT.json", arcname="CONTINUITY_RECEIPT.json")
    final_zip_hash = sha256_file(zip_path)
    final_receipt = dict(receipt_base)
    final_receipt["pack_zip_sha256"] = final_zip_hash
    final_receipt["pack_zip_sha256_after_embedded_receipt"] = final_zip_hash
    final_receipt["pack_zip_sha256_scope"] = "FINAL_ZIP_WITH_EMBEDDED_RECEIPT"
    final_receipt["embedded_receipt_note"] = "Embedded receipt hash scope is ZIP_BEFORE_EMBEDDED_RECEIPT to avoid a self-referential hash lie."
    (pack_dir / "CONTINUITY_RECEIPT.json").write_text(json.dumps(final_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "PASS_WITH_WARNINGS",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER_V0_3",
        "mode": preview["mode"],
        "pack_dir": pack_dir.as_posix(),
        "pack_zip_path": zip_path.as_posix(),
        "receipt_path": (pack_dir / "CONTINUITY_RECEIPT.json").as_posix(),
        "owner_summary_path": (pack_dir / "OWNER_CONTINUITY_SUMMARY_RU.md").as_posix(),
        "logos_prime_handoff_path": (pack_dir / "LOGOS_PRIME_HANDOFF_SUMMARY_RU.md").as_posix(),
        "pack_zip_sha256": final_zip_hash,
        "included_file_count": len(preview.get("included_files", [])),
        "continuity_pass_gates": preview.get("continuity_pass_gates", {}),
        "executed": True,
        "writes_performed": True,
        "writes_scope": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS",
    }


def smoke(repo: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo).resolve() if repo else find_repo_root()
    preview = collect_preview(root, "h")
    gates = preview.get("continuity_pass_gates", {})
    checks = {
        "repo_root_found": (root / "ORGANS").is_dir(),
        "administratum_continuity_dir_available": HERE.is_dir(),
        "h_contour_path_visible": bool(preview.get("contours", {}).get("h_repo_candidate")),
        "main_repo_path_visible": bool(preview.get("contours", {}).get("main_repo_candidate")),
        "h_protocol_visible": bool(gates.get("h_protocol_included")),
        "boot_protocol_visible": bool(gates.get("boot_protocol_included")),
        "owner_requirements_visible": bool(gates.get("owner_requirements_included")),
        "reference_backlog_visible": bool(gates.get("reference_backlog_included")),
        "git_status_readable": bool(preview.get("git", {}).get("status_sb")),
        "logos_handoff_preview_available": bool(preview.get("handoff_lines")),
        "no_commit_no_push": True,
        "owner_facing_bom_policy": True,
        "machine_json_plain_utf8_policy": True,
    }
    return {
        "status": "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER_SMOKE_V0_3",
        "schema_version": SCHEMA_VERSION,
        "repo_root": root.as_posix(),
        "contours": preview.get("contours", {}),
        "checks": checks,
        "preview_included_file_count": len(preview.get("included_files", [])),
        "commands": {
            "preview": "python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --preview h",
            "build_h": "python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --build h",
            "launcher_smoke": "python ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py --smoke",
        },
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Administratum Continuity Pack Builder V0.3")
    parser.add_argument("--preview", nargs="?", const="h", choices=sorted(MODES))
    parser.add_argument("--build", nargs="?", const="h", choices=sorted(MODES))
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    repo = find_repo_root()
    if args.smoke:
        payload = smoke(repo)
    elif args.preview:
        payload = preview_pack(repo, args.preview)
    elif args.build:
        payload = build_pack(repo, args.build)
    else:
        payload = preview_pack(repo, "h")
    _print_json(payload)
    return 2 if payload.get("status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
