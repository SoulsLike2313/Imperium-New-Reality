"""Fail-closed errors for the Core Reference Corridor foundation."""

from __future__ import annotations


class CorridorError(RuntimeError):
    """Base error carrying a stable machine-readable code."""

    code = "CORRIDOR_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.code = code or self.code
        self.message = message
        super().__init__(f"{self.code}: {message}")


class RepositoryResolutionError(CorridorError):
    code = "REPOSITORY_RESOLUTION_BLOCKED"


class AtomicStoreError(CorridorError):
    code = "ATOMIC_STORE_ERROR"


class LockTimeoutError(AtomicStoreError):
    code = "STORE_LOCK_TIMEOUT"


class TaskStoreError(CorridorError):
    code = "TASK_STORE_ERROR"


class TaskNotFoundError(TaskStoreError):
    code = "TASK_NOT_FOUND"


class TaskAlreadyExistsError(TaskStoreError):
    code = "TASK_ALREADY_EXISTS"


class TaskValidationError(TaskStoreError):
    code = "TASK_VALIDATION_BLOCKED"


class CorruptStateError(TaskStoreError):
    code = "TASK_STATE_CORRUPT"


class ConcurrentUpdateError(TaskStoreError):
    code = "TASK_VERSION_CONFLICT"


class StaleBaseError(TaskStoreError):
    code = "STALE_BASE_BLOCKED"


class InvalidTransitionError(TaskStoreError):
    code = "TASK_TRANSITION_BLOCKED"


class GateDeniedError(TaskStoreError):
    code = "OWNER_GATE_BLOCKED"
