"""Authoritative one-task transaction store for the reference corridor."""

from __future__ import annotations

import copy
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .atomic_store import FileLock, atomic_write_json, atomic_write_text, read_json_object
from .constants import (
    ALLOWED_STATE_TRANSITIONS,
    INITIAL_STATE_VERSION,
    LOCK_FILENAME,
    OWNER_GATE_REQUIREMENTS,
    PENDING_TRANSACTION_FILENAME,
    PENDING_TRANSACTION_SCHEMA,
    REQUIRED_TASK_FIELDS,
    STATE_FILENAME,
    TASK_STATE_ROUTE,
    TASK_STATE_SCHEMA,
    TRANSITION_EVENT_SCHEMA,
    TRANSITION_LOG_FILENAME,
)
from .errors import (
    AtomicStoreError,
    ConcurrentUpdateError,
    CorruptStateError,
    GateDeniedError,
    InvalidTransitionError,
    StaleBaseError,
    TaskAlreadyExistsError,
    TaskNotFoundError,
    TaskStoreError,
    TaskValidationError,
)


_GIT_OBJECT_RE = re.compile(r"^[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?$")
_DECISION_KEY_RE = re.compile(r"[^A-Z0-9]+")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _json_clone(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise TaskValidationError(f"Task data is not strict JSON: {exc}") from exc


def _normalize_decision(value: str) -> str:
    return _DECISION_KEY_RE.sub("_", value.strip().upper()).strip("_")


def _decision_record(
    owner_decision: str | Mapping[str, Any] | None,
    gate_evidence: Mapping[str, Any] | None,
) -> tuple[str | None, dict[str, Any] | None]:
    if owner_decision is None:
        return None, None
    if isinstance(owner_decision, str):
        raw_decision = owner_decision
        record: dict[str, Any] = {"decision": raw_decision}
    elif isinstance(owner_decision, Mapping):
        record = _json_clone(dict(owner_decision))
        raw_decision = next(
            (
                record[key]
                for key in ("decision", "action", "decision_type")
                if isinstance(record.get(key), str) and record[key].strip()
            ),
            "",
        )
        if not raw_decision:
            raise TaskValidationError(
                "owner_decision object needs decision, action, or decision_type"
            )
    else:
        raise TaskValidationError("owner_decision must be a string or JSON object")
    normalized = _normalize_decision(raw_decision)
    if not normalized:
        raise TaskValidationError("owner_decision cannot be empty")
    record["decision"] = normalized
    record.setdefault("recorded_at_utc", _utc_now())
    if gate_evidence is not None:
        if not isinstance(gate_evidence, Mapping) or not gate_evidence:
            raise TaskValidationError("gate_evidence must be a non-empty JSON object")
        record["gate_evidence"] = _json_clone(dict(gate_evidence))
    return normalized, record


class TaskStore:
    """Persist exactly one versioned task and its recoverable transition log."""

    def __init__(
        self,
        root: Path | str,
        *,
        expected_base_head: str | None = None,
        lock_timeout_seconds: float = 5.0,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        self.state_path = self.root / STATE_FILENAME
        self.transition_log_path = self.root / TRANSITION_LOG_FILENAME
        self.pending_path = self.root / PENDING_TRANSACTION_FILENAME
        self.lock_path = self.root / LOCK_FILENAME
        self.expected_base_head = (
            self._validated_head(expected_base_head, "expected_base_head")
            if expected_base_head is not None
            else None
        )
        self.lock_timeout_seconds = lock_timeout_seconds

    def create(self, task: Mapping[str, Any]) -> dict[str, Any]:
        """Create the corridor's only current task at ``OWNER_INTENT``."""

        if not isinstance(task, Mapping):
            raise TaskValidationError("task must be a JSON object")
        state = _json_clone(dict(task))
        state.setdefault("schema_version", TASK_STATE_SCHEMA)
        self._validate_task(state)
        if state["current_state"] != TASK_STATE_ROUTE[0]:
            raise TaskValidationError(
                f"A new task must start at {TASK_STATE_ROUTE[0]}, got {state['current_state']}"
            )
        if state["state_version"] != INITIAL_STATE_VERSION:
            raise TaskValidationError(
                f"A new task must start at state_version {INITIAL_STATE_VERSION}"
            )
        self._assert_base(state["base_head"], self.expected_base_head)
        state["base_head"] = state["base_head"].lower()

        with self._lock():
            self._recover_locked()
            if self.state_path.exists():
                raise TaskAlreadyExistsError(
                    f"A current task already exists at {self.state_path}"
                )
            event = self._event(
                transaction_id=uuid.uuid4().hex,
                task_id=state["task_id"],
                base_head=state["base_head"],
                from_state=None,
                to_state=state["current_state"],
                version_before=0,
                version_after=state["state_version"],
                owner_decision=None,
                gate_evidence=None,
            )
            self._commit_locked(state, event)
            return copy.deepcopy(state)

    def load(self) -> dict[str, Any]:
        """Load current state after recovering any durable pending commit."""

        with self._lock():
            self._recover_locked()
            return copy.deepcopy(self._read_state_locked())

    def load_transition_log(self) -> list[dict[str, Any]]:
        """Return the complete transition log after recovery."""

        with self._lock():
            self._recover_locked()
            return copy.deepcopy(self._read_events_locked())

    def allowed_targets(self, current_state: str | None = None) -> tuple[str, ...]:
        """Expose canonical next states for backend/UI parity checks."""

        if current_state is None:
            current_state = self.load()["current_state"]
        if current_state not in ALLOWED_STATE_TRANSITIONS:
            raise InvalidTransitionError(f"Unknown current state: {current_state}")
        return tuple(sorted(ALLOWED_STATE_TRANSITIONS[current_state]))

    def transition(
        self,
        target_state: str,
        *,
        expected_version: int,
        expected_base_head: str | None = None,
        owner_decision: str | Mapping[str, Any] | None = None,
        gate_evidence: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Atomically advance one allowed edge with base/version/gate checks."""

        if not isinstance(expected_version, int) or isinstance(expected_version, bool):
            raise TaskValidationError("expected_version must be an integer")
        supplied_base = expected_base_head or self.expected_base_head
        if supplied_base is None:
            raise StaleBaseError(
                "Transition needs expected_base_head on the call or TaskStore"
            )
        supplied_base = self._validated_head(supplied_base, "expected_base_head")
        decision, decision_record = _decision_record(owner_decision, gate_evidence)

        with self._lock():
            self._recover_locked()
            current = self._read_state_locked()
            if current["state_version"] != expected_version:
                raise ConcurrentUpdateError(
                    "Expected state_version "
                    f"{expected_version}, found {current['state_version']}"
                )
            self._assert_base(current["base_head"], supplied_base)
            self._validate_edge(current["current_state"], target_state, decision)

            updated = copy.deepcopy(current)
            updated["current_state"] = target_state
            updated["state_version"] = current["state_version"] + 1
            updated["updated_at_utc"] = _utc_now()
            if decision_record is not None:
                updated["owner_decisions"].append(decision_record)
            self._validate_task(updated)

            transaction_id = uuid.uuid4().hex
            event = self._event(
                transaction_id=transaction_id,
                task_id=current["task_id"],
                base_head=current["base_head"],
                from_state=current["current_state"],
                to_state=target_state,
                version_before=current["state_version"],
                version_after=updated["state_version"],
                owner_decision=decision_record,
                gate_evidence=gate_evidence,
            )
            self._commit_locked(updated, event)
            return copy.deepcopy(updated)

    def _lock(self) -> FileLock:
        return FileLock(self.lock_path, self.lock_timeout_seconds)

    @staticmethod
    def _validated_head(value: str, field: str) -> str:
        if not isinstance(value, str) or not _GIT_OBJECT_RE.fullmatch(value):
            raise TaskValidationError(f"{field} must be a 40- or 64-hex Git object id")
        return value.lower()

    @staticmethod
    def _assert_base(stored: str, expected: str | None) -> None:
        if expected is not None and stored.casefold() != expected.casefold():
            raise StaleBaseError(f"Task base {stored} does not match expected {expected}")

    @staticmethod
    def _validate_edge(source: str, target: str, decision: str | None) -> None:
        allowed = ALLOWED_STATE_TRANSITIONS.get(source)
        if allowed is None or target not in allowed:
            raise InvalidTransitionError(
                f"Transition {source} -> {target} is not in the owner route"
            )
        required = OWNER_GATE_REQUIREMENTS.get((source, target))
        if required is not None and decision not in required:
            choices = ", ".join(sorted(required))
            raise GateDeniedError(
                f"Transition {source} -> {target} requires one of: {choices}"
            )

    def _validate_task(self, state: Mapping[str, Any]) -> None:
        missing = sorted(REQUIRED_TASK_FIELDS.difference(state))
        if missing:
            raise TaskValidationError("Missing required task fields: " + ", ".join(missing))
        if state.get("schema_version") != TASK_STATE_SCHEMA:
            raise TaskValidationError(f"Unsupported task schema: {state.get('schema_version')}")
        for field in ("task_id", "task_type", "branch", "created_by"):
            if not isinstance(state[field], str) or not state[field].strip():
                raise TaskValidationError(f"{field} must be a non-empty string")
        self._validated_head(state["base_head"], "base_head")
        if state["current_state"] not in TASK_STATE_ROUTE:
            raise TaskValidationError(f"Unknown current_state: {state['current_state']}")
        if (
            not isinstance(state["state_version"], int)
            or isinstance(state["state_version"], bool)
            or state["state_version"] < INITIAL_STATE_VERSION
        ):
            raise TaskValidationError("state_version must be a positive integer")
        for field in (
            "allowed_read_roots",
            "allowed_write_roots",
            "acceptance_tests",
            "owner_decisions",
        ):
            if not isinstance(state[field], list):
                raise TaskValidationError(f"{field} must be a JSON array")
        if not all(isinstance(item, str) and item for item in state["allowed_read_roots"]):
            raise TaskValidationError("allowed_read_roots entries must be non-empty strings")
        if not all(isinstance(item, str) and item for item in state["allowed_write_roots"]):
            raise TaskValidationError("allowed_write_roots entries must be non-empty strings")
        created_at = state["created_at_utc"]
        if not isinstance(created_at, str):
            raise TaskValidationError("created_at_utc must be an ISO-8601 string")
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise TaskValidationError("created_at_utc must be an ISO-8601 timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            raise TaskValidationError("created_at_utc must identify UTC")
        _json_clone(dict(state))

    def _read_state_locked(self) -> dict[str, Any]:
        if not self.state_path.is_file():
            raise TaskNotFoundError(f"No current task at {self.state_path}")
        try:
            state = read_json_object(self.state_path)
            self._validate_task(state)
        except (AtomicStoreError, TaskValidationError) as exc:
            raise CorruptStateError(f"Invalid task state at {self.state_path}: {exc}") from exc
        return state

    def _read_events_locked(self) -> list[dict[str, Any]]:
        if not self.transition_log_path.exists():
            return []
        try:
            lines = self.transition_log_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise CorruptStateError(f"Cannot read transition log: {exc}") from exc
        events: list[dict[str, Any]] = []
        seen: set[str] = set()
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CorruptStateError(
                    f"Invalid transition log JSON at line {line_number}: {exc}"
                ) from exc
            if not isinstance(event, dict) or not isinstance(event.get("transaction_id"), str):
                raise CorruptStateError(
                    f"Invalid transition event at line {line_number}"
                )
            if event["transaction_id"] in seen:
                raise CorruptStateError(
                    f"Duplicate transition transaction_id: {event['transaction_id']}"
                )
            seen.add(event["transaction_id"])
            events.append(event)
        return events

    def _write_events_locked(self, events: list[dict[str, Any]]) -> None:
        payload = "".join(
            json.dumps(event, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
            for event in events
        )
        atomic_write_text(self.transition_log_path, payload)

    def _upsert_event_locked(self, event: dict[str, Any]) -> None:
        events = self._read_events_locked()
        for existing in events:
            if existing["transaction_id"] == event["transaction_id"]:
                if existing != event:
                    raise CorruptStateError(
                        f"Transition id collision: {event['transaction_id']}"
                    )
                return
        events.append(event)
        self._write_events_locked(events)

    def _commit_locked(self, state: dict[str, Any], event: dict[str, Any]) -> None:
        transaction = {
            "schema_version": PENDING_TRANSACTION_SCHEMA,
            "transaction_id": event["transaction_id"],
            "state": state,
            "event": event,
        }
        try:
            atomic_write_json(self.pending_path, transaction)
            atomic_write_json(self.state_path, state)
            self._upsert_event_locked(event)
            self._remove_pending_locked()
        except (AtomicStoreError, OSError) as exc:
            raise TaskStoreError(
                f"Task commit interrupted; durable recovery marker retained: {exc}",
                code="TASK_COMMIT_RECOVERY_REQUIRED",
            ) from exc

    def _remove_pending_locked(self) -> None:
        self.pending_path.unlink(missing_ok=True)

    def _recover_locked(self) -> None:
        if not self.pending_path.exists():
            return
        try:
            pending = read_json_object(self.pending_path)
        except AtomicStoreError as exc:
            raise CorruptStateError(f"Pending transaction is unreadable: {exc}") from exc
        if pending.get("schema_version") != PENDING_TRANSACTION_SCHEMA:
            raise CorruptStateError("Pending transaction has an unsupported schema")
        state = pending.get("state")
        event = pending.get("event")
        if not isinstance(state, dict) or not isinstance(event, dict):
            raise CorruptStateError("Pending transaction lacks state or event object")
        if pending.get("transaction_id") != event.get("transaction_id"):
            raise CorruptStateError("Pending transaction id does not match its event")
        try:
            self._validate_task(state)
        except TaskValidationError as exc:
            raise CorruptStateError(f"Pending state is invalid: {exc}") from exc

        if self.state_path.exists():
            current = self._read_state_locked()
            current_version = current["state_version"]
            pending_version = state["state_version"]
            if current["task_id"] != state["task_id"]:
                raise CorruptStateError("Pending transaction belongs to another task")
            if current_version > pending_version:
                raise CorruptStateError("Pending transaction is older than current state")
            if current_version == pending_version and current != state:
                raise CorruptStateError("Pending and current states disagree at one version")
            if current_version < pending_version - 1:
                raise CorruptStateError("Pending transaction skips one or more state versions")
        try:
            atomic_write_json(self.state_path, state)
            self._upsert_event_locked(event)
            self._remove_pending_locked()
        except (AtomicStoreError, OSError) as exc:
            raise TaskStoreError(
                f"Pending transaction recovery failed: {exc}",
                code="TASK_RECOVERY_BLOCKED",
            ) from exc

    @staticmethod
    def _event(
        *,
        transaction_id: str,
        task_id: str,
        base_head: str,
        from_state: str | None,
        to_state: str,
        version_before: int,
        version_after: int,
        owner_decision: Mapping[str, Any] | None,
        gate_evidence: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": TRANSITION_EVENT_SCHEMA,
            "event_id": f"TASK-STATE-{transaction_id}",
            "transaction_id": transaction_id,
            "task_id": task_id,
            "base_head": base_head,
            "from_state": from_state,
            "to_state": to_state,
            "state_version_before": version_before,
            "state_version_after": version_after,
            "timestamp_utc": _utc_now(),
            "owner_decision": _json_clone(owner_decision),
            "gate_evidence": _json_clone(gate_evidence),
        }
