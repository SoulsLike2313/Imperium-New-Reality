from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.errors import RepositoryResolutionError
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.root_resolver import (
    resolve_repository_context,
)


def _git(*arguments: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )
    return completed.stdout.strip()


def _linked_worktree(tmp_path: Path) -> tuple[Path, Path, str]:
    reality = tmp_path / "reality"
    warp = tmp_path / "warp"
    _git("init", "--initial-branch=master", str(reality))
    (reality / "tracked.txt").write_text("truth\n", encoding="utf-8")
    _git("add", "tracked.txt", cwd=reality)
    _git(
        "-c",
        "user.name=Corridor Test",
        "-c",
        "user.email=corridor@example.invalid",
        "commit",
        "-m",
        "fixture",
        cwd=reality,
    )
    head = _git("rev-parse", "HEAD", cwd=reality)
    _git("worktree", "add", "-b", "fixture/warp", str(warp), head, cwd=reality)
    return reality.resolve(), warp.resolve(), head


def test_resolves_linked_worktree_and_reality_from_nested_cwd(tmp_path: Path) -> None:
    reality, warp, head = _linked_worktree(tmp_path)
    nested = warp / "a" / "deep" / "cwd"
    nested.mkdir(parents=True)

    context = resolve_repository_context(nested)

    assert context.worktree_root == warp
    assert context.reality_root == reality
    assert context.git_common_dir == reality / ".git"
    assert context.head == head
    assert context.branch == "fixture/warp"
    assert context.resolution_method == "git_rev_parse_worktree_and_common_dir"
    assert context.as_dict()["worktree_root"] == str(warp)


def test_fails_closed_outside_git(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()

    with pytest.raises(RepositoryResolutionError, match="Git rejected"):
        resolve_repository_context(outside)


def test_windows_long_path_boundary_is_localized_without_root_guessing(tmp_path: Path) -> None:
    reality, warp, head = _linked_worktree(tmp_path)
    nested = warp
    component = "long_boundary_component_12345"
    while len(str(nested)) < 285:
        nested = nested / component
    nested.mkdir(parents=True)

    assert len(str(nested)) >= 285
    if os.name == "nt":
        with pytest.raises(RepositoryResolutionError, match="Filename too long"):
            resolve_repository_context(nested)
        assert _git("rev-parse", "HEAD", cwd=reality) == head
        assert _git("status", "--porcelain=v1", cwd=reality) == ""
    else:
        context = resolve_repository_context(nested)
        assert context.worktree_root == warp
        assert context.reality_root == reality
        assert context.head == head
