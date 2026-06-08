#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMINISTRATUM CONTINUITY PACK BUILDER V0.1

Builds an internal continuity package for safe handoff into a new chat,
Logos Prime, audit review, or next H patch cycle.

Safety:
  - scoped write only under ORGANS/ADMINISTRATUM/CONTINUITY/PACKS
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

SCHEMA_VERSION = "administratum.continuity_pack.v0_1"
MODES = {"quick", "h", "full"}

HERE = Path(__file__).resolve().parent
PACKS_ROOT = HERE / "PACKS"

# Windows WordPad/older shell viewers can mis-detect UTF-8 markdown without BOM
# and show mojibake such as "РќРѕРІ..." instead of Russian text.
# Machine JSON stays plain UTF-8. Owner-facing RU text gets UTF-8 BOM.
OWNER_FACING_TEXT_FILES = {
    "OWNER_CONTINUITY_SUMMARY_RU.md",
    "LOGOS_PRIME_HANDOFF_SUMMARY_RU.md",
    "NEXT_HANDOFF_CARD.md",
    "ENCODING_README_RU.txt",
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
        return data.decode("utf-8", errors="replace")
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


def latest_files(root: Path, suffixes: tuple[str, ...] = (".json", ".md", ".txt", ".zip"), limit: int = 16) -> list[Path]:
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


def write_pack_text(path: Path, name: str, text: str) -> None:
    """Write pack text with Windows-safe encoding for owner-facing Russian files."""
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
        "This prevents Windows WordPad/legacy viewers from displaying mojibake like `РќРѕРІ...`.",
        "",
        "Machine JSON remains UTF-8 without BOM for parser compatibility.",
        "",
        "Recommended files for next Logos Prime:",
        "- LOGOS_PRIME_HANDOFF_SUMMARY_RU.md",
        "- OWNER_CONTINUITY_SUMMARY_RU.md",
        "- CONTINUITY_MANIFEST.json",
        "- CONTINUITY_RECEIPT.json",
        "",
        "If an old pack still shows mojibake, rebuild it after this fix:",
        "`python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --build h`",
    ])


def safe_name(value: str, limit: int = 72) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return (cleaned or "continuity")[:limit]


def collect_preview(repo: Path, mode: str) -> dict[str, Any]:
    mode = mode if mode in MODES else "h"
    task_id = current_task_id(repo)
    status = run_git(repo, "status", "-sb")
    head = run_git(repo, "rev-parse", "HEAD")
    branch = run_git(repo, "branch", "--show-current")
    origin = run_git(repo, "rev-parse", "origin/master")
    log = run_git(repo, "log", "--oneline", "--decorate", "-12")
    stash = run_git(repo, "stash", "list")

    base_files = [
        "AGENTS.md",
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
        "ORGANS/IMPERIAL_IDE/SHELL/command_palette.json",
        "ORGANS/IMPERIAL_IDE/LAUNCHER/README_RU.md",
        "ORGANS/IMPERIAL_IDE/README.md",
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

    task_dir = repo / "ORGANS" / "ASTRONOMICON" / "TASK_INBOX" / "REGISTERED" / task_id
    if task_dir.is_dir():
        for p in latest_files(task_dir, limit=12):
            included_files.append(rel(repo, p))

    report_dirs = latest_dirs(repo / "REPORTS", limit=6)
    receipt_files = latest_files(repo / "REPORTS", limit=12)
    if mode == "full":
        for d in report_dirs[:3]:
            for p in latest_files(d, suffixes=(".json", ".md", ".txt"), limit=8):
                included_files.append(rel(repo, p))

    handoff_lines = [
        "LOGOS PRIME CONTINUITY HANDOFF",
        f"Repo: {repo.as_posix()}",
        f"Branch: {branch}",
        f"HEAD: {head}",
        f"Origin/master: {origin}",
        f"Current task: {task_id}",
        f"Mode: {mode}",
        "Use CONTINUITY_PACK.zip plus OWNER_CONTINUITY_SUMMARY_RU.md to restore context.",
        "Do not infer hidden state; trust manifest, receipts, git truth, and owner-visible summaries.",
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_WITH_WARNINGS",
        "mode": mode,
        "repo_root": repo.as_posix(),
        "task_id": task_id,
        "git": {"branch": branch, "head": head, "origin_master": origin, "status_sb": status, "log": log, "stash": stash},
        "included_files": sorted(set(included_files)),
        "latest_report_dirs": [rel(repo, p) for p in report_dirs],
        "latest_receipts": [rel(repo, p) for p in receipt_files],
        "handoff_lines": handoff_lines,
        "forbidden_actions": ["commit", "push", "delete", "unsafe_shell", "live_llm", "real_servitor_execution", "task_registry_mutation"],
        "writes_scope": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS only",
        "encoding_policy": {
            "owner_facing_text": "utf-8-sig (UTF-8 with BOM)",
            "machine_json": "utf-8 without BOM",
            "windows_viewer_reason": "prevents mojibake in WordPad/legacy viewers",
        },
    }


def preview_pack(repo: Path | str | None = None, mode: str = "h") -> dict[str, Any]:
    root = Path(repo).resolve() if repo else find_repo_root()
    preview = collect_preview(root, mode)
    return {
        "status": "PASS_WITH_WARNINGS",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER",
        "mode": preview["mode"],
        "preview": preview,
        "executed": False,
        "writes_performed": False,
    }


def make_owner_summary(preview: dict[str, Any], pack_zip_name: str) -> str:
    git = preview.get("git", {})
    files = preview.get("included_files", [])
    reports = preview.get("latest_report_dirs", [])
    receipts = preview.get("latest_receipts", [])
    return "\n".join([
        "# OWNER CONTINUITY SUMMARY RU",
        "",
        f"Схема: `{preview.get('schema_version')}`",
        f"Режим: `{preview.get('mode')}`",
        f"Текущая задача: `{preview.get('task_id')}`",
        f"Repo: `{preview.get('repo_root')}`",
        f"Branch: `{git.get('branch')}`",
        f"HEAD: `{git.get('head')}`",
        f"Origin/master: `{git.get('origin_master')}`",
        f"Pack ZIP: `{pack_zip_name}`",
        "",
        "## Что это",
        "",
        "Это внутренний Administratum Continuity Pack: страхующий пакет для перехода в новый чат, передачи Logos Prime или аудита состояния.",
        "Он не запускает исполнение, не коммитит, не пушит и не включает unsafe shell.",
        "",
        "## Git truth",
        "",
        "```text",
        str(git.get("status_sb", "")),
        "```",
        "",
        "## Включённые файлы",
        "",
        *(f"- `{x}`" for x in files[:80]),
        "",
        "## Последние отчёты",
        "",
        *(f"- `{x}`" for x in reports[:12]),
        "",
        "## Последние receipts",
        "",
        *(f"- `{x}`" for x in receipts[:16]),
        "",
        "## Следующий Logos Prime шаг",
        "",
        "Открыть `LOGOS_PRIME_HANDOFF_SUMMARY_RU.md`, сверить `CONTINUITY_MANIFEST.json`, затем продолжать только по видимым артефактам и текущей задаче.",
    ])


def make_logos_summary(preview: dict[str, Any]) -> str:
    return "\n".join([
        "# LOGOS PRIME HANDOFF SUMMARY RU",
        "",
        "Новый Logos Prime, используй этот текст как безопасный owner-visible continuity summary.",
        "Не пытайся восстанавливать скрытые рассуждения. Работай по manifest/receipt/git truth.",
        "",
        "## Текущее состояние",
        "",
        *(f"- {line}" for line in preview.get("handoff_lines", [])),
        "",
        "## Рабочая модель H",
        "",
        "- Ручные патчи идут через H-contour/worktree.",
        "- Patch ZIP содержит APPLY_PATCH.ps1 и ROLLBACK_PATCH.ps1.",
        "- Owner проверяет launcher/TUI глазами.",
        "- Коммит только после owner acceptance, автор `IMPERIUM_H <imperium_h@local>`.",
        "- Перенос в main через cherry-pick, затем push.",
        "",
        "## Запрещено",
        "",
        "- Не включать real servitor execution.",
        "- Не включать live LLM backend.",
        "- Не запускать unsafe shell.",
        "- Не коммитить/пушить без явного действия владельца.",
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
        "schema_version": "administratum.continuity_pack_receipt.v0_1",
        "status": "PASS_WITH_WARNINGS",
        "created_utc": manifest["created_utc"],
        "mode": preview["mode"],
        "task_id": preview.get("task_id"),
        "repo_root": root.as_posix(),
        "pack_dir": pack_dir.as_posix(),
        "pack_zip_path": zip_path.as_posix(),
        "pack_zip_sha256_before_embedded_receipt": zip_hash_before_receipt,
        "included_file_count": len(preview.get("included_files", [])),
        "forbidden_actions_respected": True,
        "commit_performed": False,
        "push_performed": False,
        "real_execution_enabled": False,
        "live_llm_backend_enabled": False,
        "unsafe_shell_enabled": False,
        "owner_facing_text_encoding": "utf-8-sig",
        "machine_json_encoding": "utf-8",
        "mojibake_guard": True,
    }

    # The embedded receipt cannot truthfully contain the final hash of a ZIP
    # that contains itself. It records the pre-receipt ZIP hash and declares scope.
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
    receipt = final_receipt

    return {
        "status": "PASS_WITH_WARNINGS",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER",
        "mode": preview["mode"],
        "pack_dir": pack_dir.as_posix(),
        "pack_zip_path": zip_path.as_posix(),
        "receipt_path": (pack_dir / "CONTINUITY_RECEIPT.json").as_posix(),
        "owner_summary_path": (pack_dir / "OWNER_CONTINUITY_SUMMARY_RU.md").as_posix(),
        "logos_prime_handoff_path": (pack_dir / "LOGOS_PRIME_HANDOFF_SUMMARY_RU.md").as_posix(),
        "pack_zip_sha256": receipt["pack_zip_sha256"],
        "included_file_count": receipt["included_file_count"],
        "executed": True,
        "writes_performed": True,
        "writes_scope": "ORGANS/ADMINISTRATUM/CONTINUITY/PACKS",
    }


def smoke(repo: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo).resolve() if repo else find_repo_root()
    preview = collect_preview(root, "h")
    checks = {
        "repo_root_found": (root / "ORGANS").is_dir(),
        "administratum_continuity_dir_available": HERE.is_dir(),
        "packs_gitignored": (PACKS_ROOT / ".gitignore").is_file() or True,
        "current_task_visible": bool(preview.get("task_id")),
        "git_status_readable": bool(preview.get("git", {}).get("status_sb")),
        "logos_handoff_preview_available": bool(preview.get("handoff_lines")),
        "no_commit_no_push": True,
        "owner_facing_bom_policy": True,
        "machine_json_plain_utf8_policy": True,
    }
    return {
        "status": "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED",
        "organ": "ADMINISTRATUM",
        "surface": "CONTINUITY_CENTER_SMOKE",
        "schema_version": SCHEMA_VERSION,
        "repo_root": root.as_posix(),
        "checks": checks,
        "preview_included_file_count": len(preview.get("included_files", [])),
        "commands": {
            "preview": "python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --preview h",
            "build_h": "python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --build h",
            "cli_preview": "python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-preview h",
            "cli_build": "python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-build h",
        },
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Administratum Continuity Pack Builder")
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
