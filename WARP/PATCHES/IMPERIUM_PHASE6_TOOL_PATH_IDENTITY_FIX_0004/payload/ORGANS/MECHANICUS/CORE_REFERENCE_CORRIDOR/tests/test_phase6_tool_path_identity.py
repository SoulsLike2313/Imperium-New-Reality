from __future__ import annotations

from pathlib import Path

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation import (
    _same_executable_identity,
    _windows_path_identity,
)


def test_phase6_windows_extended_length_prefix_is_same_identity() -> None:
    ordinary = r"C:\Program Files\Git\cmd\git.exe"
    extended = r"\\?\C:\Program Files\Git\cmd\git.exe"
    assert _windows_path_identity(ordinary) == _windows_path_identity(extended)
    assert _same_executable_identity(ordinary, extended)


def test_phase6_windows_case_and_separator_spelling_is_same_identity() -> None:
    left = r"C:\Program Files\Git\cmd\git.exe"
    right = r"c:/PROGRAM FILES/Git/cmd/git.exe"
    assert _same_executable_identity(left, right)


def test_phase6_different_executables_are_not_same_identity() -> None:
    git = r"C:\Program Files\Git\cmd\git.exe"
    pwsh = r"C:\Program Files\PowerShell\7\pwsh.exe"
    assert not _same_executable_identity(git, pwsh)


def test_phase6_samefile_proves_real_file_identity(tmp_path: Path) -> None:
    executable = tmp_path / "tool.exe"
    executable.write_bytes(b"identity")
    assert _same_executable_identity(executable, executable)
