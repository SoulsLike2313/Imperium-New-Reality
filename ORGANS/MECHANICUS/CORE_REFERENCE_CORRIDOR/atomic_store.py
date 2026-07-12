"""Small stdlib-only atomic persistence and inter-process locking helpers."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from .errors import AtomicStoreError, LockTimeoutError


_LOCKS_GUARD = threading.Lock()
_PROCESS_LOCKS: dict[str, threading.Lock] = {}


def _process_lock(path: Path) -> threading.Lock:
    key = os.path.normcase(str(path.resolve()))
    with _LOCKS_GUARD:
        return _PROCESS_LOCKS.setdefault(key, threading.Lock())


def _fsync_directory(directory: Path) -> None:
    """Durably record a rename where the platform supports directory fsync."""

    flags = getattr(os, "O_RDONLY", 0)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        descriptor = os.open(directory, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def atomic_write_text(path: Path | str, value: str) -> None:
    """Replace ``path`` with fully flushed UTF-8 text from the same directory."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        _fsync_directory(target.parent)
    except (OSError, UnicodeError) as exc:
        raise AtomicStoreError(f"Atomic replacement failed for {target}: {exc}") from exc
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def atomic_write_json(path: Path | str, value: Any) -> None:
    """Serialize strict JSON and atomically replace ``path``."""

    try:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        ) + "\n"
    except (TypeError, ValueError) as exc:
        raise AtomicStoreError(f"Value is not strict JSON: {exc}") from exc
    atomic_write_text(path, payload)


def read_json_object(path: Path | str) -> dict[str, Any]:
    """Read a JSON object, rejecting absent, malformed, or non-object content."""

    target = Path(path)
    try:
        with target.open("r", encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtomicStoreError(f"Cannot read valid JSON from {target}: {exc}") from exc
    if not isinstance(value, dict):
        raise AtomicStoreError(f"JSON root must be an object: {target}")
    return value


class FileLock:
    """Advisory lock effective across threads and operating-system processes."""

    def __init__(self, path: Path | str, timeout_seconds: float = 5.0) -> None:
        if timeout_seconds < 0:
            raise ValueError("timeout_seconds must not be negative")
        self.path = Path(path)
        self.timeout_seconds = timeout_seconds
        self._thread_lock = _process_lock(self.path)
        self._stream: Any | None = None
        self._thread_acquired = False

    def acquire(self) -> "FileLock":
        deadline = time.monotonic() + self.timeout_seconds
        if not self._thread_lock.acquire(timeout=self.timeout_seconds):
            raise LockTimeoutError(f"Timed out waiting for task lock: {self.path}")
        self._thread_acquired = True
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._stream = self.path.open("a+b")
            self._stream.seek(0, os.SEEK_END)
            if self._stream.tell() == 0:
                self._stream.write(b"\0")
                self._stream.flush()
                os.fsync(self._stream.fileno())
            while True:
                self._stream.seek(0)
                try:
                    self._lock_os()
                    return self
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise LockTimeoutError(
                            f"Timed out waiting for task lock: {self.path}"
                        ) from exc
                    time.sleep(min(0.025, max(0.0, deadline - time.monotonic())))
        except BaseException:
            self._cleanup_after_failed_acquire()
            raise

    def _lock_os(self) -> None:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self._stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(self._stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_os(self) -> None:
        if os.name == "nt":
            import msvcrt

            self._stream.seek(0)
            msvcrt.locking(self._stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(self._stream.fileno(), fcntl.LOCK_UN)

    def _cleanup_after_failed_acquire(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        if self._thread_acquired:
            self._thread_lock.release()
            self._thread_acquired = False

    def release(self) -> None:
        try:
            if self._stream is not None:
                self._unlock_os()
        finally:
            if self._stream is not None:
                self._stream.close()
                self._stream = None
            if self._thread_acquired:
                self._thread_lock.release()
                self._thread_acquired = False

    def __enter__(self) -> "FileLock":
        return self.acquire()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.release()
