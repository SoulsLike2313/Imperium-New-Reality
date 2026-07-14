"""Fail-closed access to system executables admitted by the Rust bridge.

The bridge deliberately clears PATH. Python code must therefore never resolve
Git or PowerShell by name. Each invocation re-checks the absolute path and
SHA-256 supplied through the minimal admitted environment.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path


GIT_PATH_ENV = "IMPERIUM_GIT_EXECUTABLE"
GIT_HASH_ENV = "IMPERIUM_GIT_SHA256"
PWSH_PATH_ENV = "IMPERIUM_PWSH_EXECUTABLE"
PWSH_HASH_ENV = "IMPERIUM_PWSH_SHA256"
REQUIRED_ENV = "IMPERIUM_PINNED_TOOLCHAIN_REQUIRED"
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class PinnedToolError(RuntimeError):
    """A required executable is missing, ambiguous, or has changed identity."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_pinned(path_env: str, hash_env: str, allowed_names: set[str], label: str) -> Path:
    raw_path = os.environ.get(path_env, "").strip()
    expected_hash = os.environ.get(hash_env, "").strip()
    required = os.environ.get(REQUIRED_ENV, "").strip() == "1"
    if bool(raw_path) != bool(expected_hash):
        raise PinnedToolError(f"{label}_ADMISSION_ENV_INCOMPLETE")
    if not raw_path:
        if required:
            raise PinnedToolError(f"{label}_ADMISSION_ENV_MISSING")
        located = next((shutil.which(name) for name in allowed_names if shutil.which(name)), None)
        if not located:
            raise PinnedToolError(f"{label}_EXECUTABLE_NOT_FOUND")
        raw_path = located
        expected_hash = sha256_file(Path(located).resolve(strict=True))
    if not _SHA256.fullmatch(expected_hash):
        raise PinnedToolError(f"{label}_ADMISSION_HASH_INVALID")

    configured = Path(raw_path)
    if not configured.is_absolute():
        raise PinnedToolError(f"{label}_BARE_OR_RELATIVE_EXECUTABLE_REJECTED")
    try:
        executable = configured.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PinnedToolError(f"{label}_EXECUTABLE_UNAVAILABLE: {exc}") from exc
    if not executable.is_file():
        raise PinnedToolError(f"{label}_EXECUTABLE_NOT_FILE")
    if executable.name.casefold() not in {name.casefold() for name in allowed_names}:
        raise PinnedToolError(f"{label}_EXECUTABLE_NAME_REJECTED: {executable.name}")

    actual_hash = sha256_file(executable)
    if actual_hash.casefold() != expected_hash.casefold():
        raise PinnedToolError(f"{label}_EXECUTABLE_HASH_MISMATCH")
    return executable


def pinned_git_executable() -> Path:
    return _resolve_pinned(GIT_PATH_ENV, GIT_HASH_ENV, {"git.exe", "git"}, "GIT")


def pinned_pwsh_executable() -> Path:
    return _resolve_pinned(PWSH_PATH_ENV, PWSH_HASH_ENV, {"pwsh.exe", "pwsh"}, "PWSH")


def git_argv(*arguments: str) -> list[str]:
    return [str(pinned_git_executable()), *arguments]
