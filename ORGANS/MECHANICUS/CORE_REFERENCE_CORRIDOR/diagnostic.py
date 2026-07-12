"""Read-only Core diagnostic used by the admitted demo capability."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .root_resolver import resolve_repository_context


class DiagnosticError(RuntimeError):
    pass


def _run(argv: list[str], cwd: Path, timeout: float = 8.0) -> str:
    completed = subprocess.run(
        argv,
        cwd=str(cwd),
        check=False,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise DiagnosticError(f"command failed ({completed.returncode}): {argv!r}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _git(root: Path, *args: str) -> str:
    return _run(["git", "-C", str(root), *args], root)


def _load_canon(worktree_root: Path) -> dict[str, Any]:
    relative = Path("ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json")
    source = worktree_root / relative
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiagnosticError(f"Great Nine source unavailable: {source}: {exc}") from exc
    organs = [item.get("canonical_id") for item in data.get("great_nine", []) if item.get("canonical_id")]
    missing = [organ for organ in organs if not (worktree_root / "ORGANS" / organ).is_dir()]
    return {
        "source": relative.as_posix(),
        "source_status": data.get("status", "UNKNOWN"),
        "organ_ids": organs,
        "organ_count": len(organs),
        "missing_organ_paths": missing,
        "throne": data.get("crown_organ", {}),
        "constitution_conflict": "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
    }


def collect_diagnostic(start: Path | str = ".") -> dict[str, Any]:
    context = resolve_repository_context(start)
    worktree = Path(context.worktree_root)
    reality = Path(context.reality_root)
    pwsh = shutil.which("pwsh")
    if not pwsh:
        raise DiagnosticError("pwsh executable not found")
    pwsh_path = Path(pwsh).resolve()
    pwsh_version = _run(
        [str(pwsh_path), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"],
        worktree,
    )
    worktree_status = _git(worktree, "status", "--porcelain=v1").splitlines()
    reality_status = _git(reality, "status", "--porcelain=v1").splitlines()
    origin_master = _git(reality, "rev-parse", "origin/master")
    reality_head = _git(reality, "rev-parse", "HEAD")
    return {
        "schema_version": "imperium.core_reference_corridor.diagnostic.v0_1",
        "verdict": "PASS_PROVEN" if not reality_status else "BLOCK",
        "resolution": context.as_dict(),
        "git": {
            "worktree_root": str(worktree),
            "worktree_head": _git(worktree, "rev-parse", "HEAD"),
            "worktree_branch": _git(worktree, "rev-parse", "--abbrev-ref", "HEAD"),
            "worktree_dirty": bool(worktree_status),
            "worktree_status": worktree_status,
            "reality_root": str(reality),
            "reality_head": reality_head,
            "reality_branch": _git(reality, "rev-parse", "--abbrev-ref", "HEAD"),
            "reality_dirty": bool(reality_status),
            "reality_status": reality_status,
            "origin_master": origin_master,
            "reality_matches_origin_master": reality_head == origin_master,
        },
        "powershell": {
            "executable": str(pwsh_path),
            "version": pwsh_version,
            "exact_required_version": "7.6.2",
            "exact_version_match": pwsh_version == "7.6.2",
        },
        "canon": _load_canon(worktree),
        "truth_boundary": "Diagnostic proves current host/repository facts only; it does not prove complete Core v1.",
    }

