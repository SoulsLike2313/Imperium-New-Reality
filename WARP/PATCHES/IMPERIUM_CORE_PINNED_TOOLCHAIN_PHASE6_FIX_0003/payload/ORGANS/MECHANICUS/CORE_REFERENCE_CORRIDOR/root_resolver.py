"""Git-derived repository and linked-worktree context resolution."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import RepositoryResolutionError
from .pinned_tools import git_argv


@dataclass(frozen=True, slots=True)
class RepositoryContext:
    """Resolved context for either the Reality worktree or a linked WARP."""

    worktree_root: Path
    reality_root: Path
    git_common_dir: Path
    head: str
    branch: str
    resolution_method: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation without losing field names."""

        return {
            "worktree_root": str(self.worktree_root),
            "reality_root": str(self.reality_root),
            "git_common_dir": str(self.git_common_dir),
            "head": self.head,
            "branch": self.branch,
            "resolution_method": self.resolution_method,
        }


def _git(start: Path, *arguments: str) -> str:
    try:
        argv = git_argv("-C", str(start), *arguments)
        completed = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RepositoryResolutionError(
            f"Git invocation failed for {start}: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Git error"
        raise RepositoryResolutionError(
            f"Git rejected repository resolution for {start}: {detail}"
        )
    value = completed.stdout.strip()
    if not value:
        raise RepositoryResolutionError(
            f"Git returned an empty value for arguments {arguments!r}"
        )
    return value


def _resolved_directory(start: Path | str) -> Path:
    candidate = Path(start).expanduser()
    try:
        candidate = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RepositoryResolutionError(
            f"Start path does not resolve to an existing location: {candidate}"
        ) from exc
    if candidate.is_file():
        candidate = candidate.parent
    if not candidate.is_dir():
        raise RepositoryResolutionError(f"Start path is not a directory: {candidate}")
    return candidate


def resolve_repository_context(start: Path | str = ".") -> RepositoryContext:
    """Resolve current worktree and canonical Reality via Git only.

    The common Git directory is the authority connecting an external linked
    worktree to its main Reality worktree.  A repository whose common directory
    is not a ``.git`` directory is rejected because it cannot prove that shape.
    """

    start_directory = _resolved_directory(start)
    worktree_root = Path(_git(start_directory, "rev-parse", "--show-toplevel")).resolve()
    common_dir = Path(
        _git(
            start_directory,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    if common_dir.name.casefold() != ".git":
        raise RepositoryResolutionError(
            f"Git common directory does not prove a non-bare Reality root: {common_dir}"
        )
    reality_root = common_dir.parent.resolve()

    # Re-prove that the inferred parent is itself the main worktree for this
    # common directory; a directory merely named .git is not sufficient.
    reality_toplevel = Path(
        _git(reality_root, "rev-parse", "--show-toplevel")
    ).resolve()
    reality_common = Path(
        _git(
            reality_root,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    if reality_toplevel != reality_root or reality_common != common_dir:
        raise RepositoryResolutionError(
            "Git common-directory proof does not identify a canonical Reality worktree"
        )

    head = _git(start_directory, "rev-parse", "--verify", "HEAD").lower()
    branch = _git(start_directory, "branch", "--show-current") or "DETACHED"
    return RepositoryContext(
        worktree_root=worktree_root,
        reality_root=reality_root,
        git_common_dir=common_dir,
        head=head,
        branch=branch,
        resolution_method="git_rev_parse_worktree_and_common_dir",
    )
