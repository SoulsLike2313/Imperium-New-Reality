from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.pinned_tools import (
    GIT_HASH_ENV,
    GIT_PATH_ENV,
    REQUIRED_ENV,
    PinnedToolError,
    git_argv,
    pinned_git_executable,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _host_git() -> Path:
    found = shutil.which("git") or shutil.which("git.exe")
    assert found
    return Path(found).resolve()


def test_explicit_pinned_git_is_absolute_and_hash_verified(monkeypatch: pytest.MonkeyPatch) -> None:
    git = _host_git()
    monkeypatch.setenv(REQUIRED_ENV, "1")
    monkeypatch.setenv(GIT_PATH_ENV, str(git))
    monkeypatch.setenv(GIT_HASH_ENV, _sha(git))

    assert pinned_git_executable() == git
    assert git_argv("--version")[0] == str(git)


def test_required_mode_rejects_missing_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(REQUIRED_ENV, "1")
    monkeypatch.delenv(GIT_PATH_ENV, raising=False)
    monkeypatch.delenv(GIT_HASH_ENV, raising=False)

    with pytest.raises(PinnedToolError, match="GIT_ADMISSION_ENV_MISSING"):
        pinned_git_executable()


def test_hash_mismatch_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    git = _host_git()
    monkeypatch.setenv(REQUIRED_ENV, "1")
    monkeypatch.setenv(GIT_PATH_ENV, str(git))
    monkeypatch.setenv(GIT_HASH_ENV, "0" * 64)

    with pytest.raises(PinnedToolError, match="GIT_EXECUTABLE_HASH_MISMATCH"):
        pinned_git_executable()


def test_non_bridge_invocation_may_resolve_host_git_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(REQUIRED_ENV, raising=False)
    monkeypatch.delenv(GIT_PATH_ENV, raising=False)
    monkeypatch.delenv(GIT_HASH_ENV, raising=False)

    assert pinned_git_executable().is_file()
