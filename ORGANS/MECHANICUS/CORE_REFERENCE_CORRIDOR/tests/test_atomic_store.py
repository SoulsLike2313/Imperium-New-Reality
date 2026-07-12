from __future__ import annotations

from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.atomic_store import (
    FileLock,
    atomic_write_json,
    read_json_object,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.errors import LockTimeoutError


def test_atomic_json_replaces_complete_document(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    atomic_write_json(target, {"state_version": 1, "value": "old"})
    atomic_write_json(target, {"state_version": 2, "value": "new"})

    assert read_json_object(target) == {"state_version": 2, "value": "new"}
    assert list(tmp_path.glob("*.tmp")) == []


def test_file_lock_denies_concurrent_holder(tmp_path: Path) -> None:
    path = tmp_path / "state.lock"

    with FileLock(path, timeout_seconds=1):
        with pytest.raises(LockTimeoutError):
            FileLock(path, timeout_seconds=0.02).acquire()
