"""Semantic checkpoint persistence and honest task-state restoration."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
import uuid


SEMANTIC_CHECKPOINTS = (
    "TASK_REGISTERED",
    "SPEC_APPROVED",
    "STRATEGY_SELECTED",
    "WARP_CREATED",
    "EXECUTION_STARTED",
    "MATERIAL_CHANGE",
    "ERROR_DETECTED",
    "VALIDATION_COMPLETED",
    "OWNER_REVIEW",
    "ROLLBACK",
    "FINAL_RESULT",
)

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class CheckpointError(RuntimeError):
    """Checkpoint is invalid, stale, tampered, or outside restore scope."""


class CheckpointTamperError(CheckpointError):
    """Checkpoint bytes disagree with the hash index."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: Any) -> bytes:
    try:
        rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CheckpointError(f"checkpoint is not canonical JSON: {exc}") from exc
    return (rendered + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _inside(path: Path, roots: Sequence[Path]) -> bool:
    resolved = path.resolve()
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False


class CheckpointStore:
    """Store immutable semantic snapshots and restore only complete task state."""

    def __init__(
        self,
        root: str | Path,
        *,
        index_name: str = "CHECKPOINT_INDEX.json",
        allowed_restore_roots: Sequence[str | Path] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / index_name
        roots = allowed_restore_roots if allowed_restore_roots is not None else (self.root,)
        self.allowed_restore_roots = tuple(Path(item).resolve() for item in roots)
        if not self.allowed_restore_roots:
            raise CheckpointError("at least one allowed_restore_root is required")
        if not self.index_path.exists():
            self._write_index(
                {
                    "schema_version": "imperium.checkpoint_index.v1",
                    "entries": {},
                    "updated_at_utc": _utc_now(),
                }
            )

    @staticmethod
    def _index_hash(index: Mapping[str, Any]) -> str:
        core = {key: value for key, value in index.items() if key != "content_sha256"}
        return _sha256(_canonical_bytes(core))

    def _write_index(self, index: Mapping[str, Any]) -> dict[str, Any]:
        materialized = dict(index)
        materialized["content_sha256"] = self._index_hash(materialized)
        _atomic_write(self.index_path, _canonical_bytes(materialized))
        return materialized

    def _load_index(self) -> dict[str, Any]:
        try:
            index = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointTamperError(f"checkpoint index cannot be read: {exc}") from exc
        if index.get("schema_version") != "imperium.checkpoint_index.v1" or not isinstance(index.get("entries"), dict):
            raise CheckpointTamperError("checkpoint index schema is invalid")
        if index.get("content_sha256") != self._index_hash(index):
            raise CheckpointTamperError("checkpoint index hash mismatch")
        return index

    def _path(self, checkpoint_id: str) -> Path:
        if not _ID_RE.fullmatch(checkpoint_id) or checkpoint_id == "CHECKPOINT_INDEX":
            raise CheckpointError("unsafe checkpoint_id")
        return self.root / f"{checkpoint_id}.json"

    def create(
        self,
        checkpoint_id: str,
        *,
        semantic_state: str,
        task_id: str,
        task_state: Mapping[str, Any],
        git_state: Mapping[str, Any],
        evidence_refs: Sequence[str],
        parent_checkpoint_id: str | None = None,
        dependencies: Mapping[str, Any] | Sequence[Any] | None = None,
    ) -> dict[str, Any]:
        if semantic_state not in SEMANTIC_CHECKPOINTS:
            raise CheckpointError(f"unsupported semantic checkpoint: {semantic_state}")
        if not isinstance(task_state, Mapping) or not isinstance(git_state, Mapping):
            raise CheckpointError("task_state and git_state must be objects")
        if task_state.get("task_id") not in (None, task_id):
            raise CheckpointError("task_state belongs to a different task")
        if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)) or not all(
            isinstance(item, str) for item in evidence_refs
        ):
            raise CheckpointError("evidence_refs must be an array of strings")
        path = self._path(checkpoint_id)
        index = self._load_index()
        if checkpoint_id in index["entries"] or path.exists():
            raise CheckpointError("checkpoint ids are immutable and cannot be overwritten")
        state_copy = json.loads(_canonical_bytes(dict(task_state)))
        document = {
            "schema_version": "imperium.semantic_checkpoint.v1",
            "checkpoint_id": checkpoint_id,
            "semantic_state": semantic_state,
            "task_id": task_id,
            "timestamp_utc": _utc_now(),
            "task_state": state_copy,
            "task_state_sha256": _sha256(_canonical_bytes(state_copy)),
            "git_state": json.loads(_canonical_bytes(dict(git_state))),
            "evidence_refs": list(evidence_refs),
            "parent_checkpoint_id": parent_checkpoint_id,
            "dependencies": dependencies if dependencies is not None else {},
            "restore_contract": {
                "full_task_state": "IMPLEMENTED",
                "git_state": "REFERENCE_ONLY",
                "partial": "NOT_IMPLEMENTED_BLOCK",
            },
        }
        checkpoint_bytes = _canonical_bytes(document)
        _atomic_write(path, checkpoint_bytes)
        index["entries"][checkpoint_id] = {
            "path": path.name,
            "semantic_state": semantic_state,
            "task_id": task_id,
            "checkpoint_sha256": _sha256(checkpoint_bytes),
            "task_state_sha256": document["task_state_sha256"],
            "timestamp_utc": document["timestamp_utc"],
        }
        index["updated_at_utc"] = _utc_now()
        self._write_index(index)
        return dict(index["entries"][checkpoint_id])

    def load(self, checkpoint_id: str) -> dict[str, Any]:
        path = self._path(checkpoint_id)
        index = self._load_index()
        try:
            entry = index["entries"][checkpoint_id]
            raw = path.read_bytes()
        except (KeyError, OSError) as exc:
            raise CheckpointError(f"checkpoint is missing: {checkpoint_id}") from exc
        if _sha256(raw) != entry.get("checkpoint_sha256"):
            raise CheckpointTamperError("checkpoint file hash mismatch")
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CheckpointTamperError("checkpoint JSON is invalid") from exc
        if document.get("checkpoint_id") != checkpoint_id or document.get("semantic_state") not in SEMANTIC_CHECKPOINTS:
            raise CheckpointTamperError("checkpoint identity or semantic state is invalid")
        state = document.get("task_state")
        if not isinstance(state, dict) or _sha256(_canonical_bytes(state)) != document.get("task_state_sha256"):
            raise CheckpointTamperError("checkpoint task-state hash mismatch")
        if document["task_state_sha256"] != entry.get("task_state_sha256"):
            raise CheckpointTamperError("checkpoint task-state hash disagrees with index")
        return document

    def restore(
        self,
        checkpoint_id: str,
        target_state_path: str | Path,
        *,
        mode: str = "FULL",
        expected_task_id: str | None = None,
        expected_current_state_version: int | None = None,
        requested_keys: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        checkpoint = self.load(checkpoint_id)
        normalized_mode = mode.upper()
        target = Path(target_state_path).resolve()
        if normalized_mode == "PARTIAL":
            return {
                "schema_version": "imperium.checkpoint_restore_receipt.v1",
                "verdict": "BLOCK",
                "status": "NOT_IMPLEMENTED",
                "reason_code": "PARTIAL_RESTORE_NOT_IMPLEMENTED",
                "checkpoint_id": checkpoint_id,
                "requested_keys": list(requested_keys or ()),
                "target_mutated": False,
                "timestamp_utc": _utc_now(),
            }
        if normalized_mode != "FULL":
            raise CheckpointError("restore mode must be FULL or PARTIAL")
        if not _inside(target, self.allowed_restore_roots):
            raise CheckpointError("restore target is outside allowed_restore_roots")
        if expected_task_id is not None and checkpoint["task_id"] != expected_task_id:
            raise CheckpointError("checkpoint task_id does not match expected_task_id")
        current: dict[str, Any] | None = None
        if target.exists():
            try:
                current = json.loads(target.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise CheckpointError(f"current task state cannot be read: {exc}") from exc
            if current.get("task_id") not in (None, checkpoint["task_id"]):
                raise CheckpointError("refusing to restore over a different task")
            if expected_current_state_version is not None and current.get("state_version") != expected_current_state_version:
                raise CheckpointError("current task state version is stale")
        elif expected_current_state_version is not None:
            raise CheckpointError("expected current task state does not exist")
        before_hash = _sha256(_canonical_bytes(current)) if current is not None else None
        state_bytes = _canonical_bytes(checkpoint["task_state"])
        _atomic_write(target, state_bytes)
        restored = json.loads(target.read_text(encoding="utf-8"))
        after_hash = _sha256(_canonical_bytes(restored))
        if after_hash != checkpoint["task_state_sha256"]:
            raise CheckpointError("full task-state restore verification failed")
        return {
            "schema_version": "imperium.checkpoint_restore_receipt.v1",
            "verdict": "PASS_PROVEN",
            "status": "FULL_TASK_STATE_RESTORED",
            "checkpoint_id": checkpoint_id,
            "task_id": checkpoint["task_id"],
            "target_state_path": str(target),
            "before_sha256": before_hash,
            "after_sha256": after_hash,
            "git_state_restore": "REFERENCE_ONLY_NOT_MUTATED",
            "git_state_ref": checkpoint["git_state"],
            "target_mutated": True,
            "timestamp_utc": _utc_now(),
        }

    def index_snapshot(self) -> dict[str, Any]:
        return self._load_index()
