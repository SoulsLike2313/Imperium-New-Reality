"""Read-only correlation helpers for canonical live UI evidence.

No function in this module writes repository state. Persistence remains owned by
`CorridorService.execute_demo()` through the existing admitted typed-executor
route and the canonical `EvidenceStore`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping
import uuid

_REQUEST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _index_hash(index: Mapping[str, Any]) -> str:
    core = {key: value for key, value in index.items() if key != "content_sha256"}
    return hashlib.sha256(_canonical_bytes(core)).hexdigest()


def live_evidence_root(report_root: Path | str) -> Path:
    return Path(report_root).resolve() / "live_ui_evidence"


def create_action_context(payload: Mapping[str, Any] | None = None) -> dict[str, str]:
    """Create server-owned unique correlation IDs; never trust an unsafe ID."""
    payload = payload or {}
    candidate = payload.get("action_request_id")
    token = uuid.uuid4().hex
    if candidate is None:
        request_id = f"ui-{token}"
    elif not isinstance(candidate, str) or not _REQUEST_RE.fullmatch(candidate):
        raise ValueError("action_request_id is invalid")
    else:
        request_id = candidate
    return {
        "action_request_id": request_id,
        "evidence_id": f"UI_DIAGNOSTIC_{token}",
        "event_id": f"EVENT-UI-DIAGNOSTIC-{token}",
    }


def load_live_index(report_root: Path | str) -> dict[str, Any]:
    """Read and hash-check the optional live index without creating it."""
    root = live_evidence_root(report_root)
    path = root / "EVIDENCE_INDEX.json"
    if not path.is_file():
        return {
            "schema_version": "imperium.evidence_index.v1",
            "state": "ABSENT",
            "entries": {},
            "content_sha256": None,
        }
    try:
        index = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"live evidence index cannot be read: {exc}") from exc
    if index.get("schema_version") != "imperium.evidence_index.v1" or not isinstance(index.get("entries"), dict):
        raise ValueError("live evidence index schema is invalid")
    if index.get("content_sha256") != _index_hash(index):
        raise ValueError("live evidence index hash mismatch")
    return index


def verify_action_document(document: Mapping[str, Any]) -> dict[str, str]:
    if document.get("ui_action_id") != "run_core_diagnostic":
        raise ValueError("unexpected UI action")
    if document.get("ui_dispatch") != "CORRIDOR_UI_ACTION_CANONICAL_ROUTE":
        raise ValueError("canonical UI dispatch marker is missing")
    request_id = str(document.get("action_request_id", ""))
    if not _REQUEST_RE.fullmatch(request_id):
        raise ValueError("invalid action_request_id")
    evidence_id = str(document.get("evidence_id", ""))
    event_id = str(document.get("event_id", ""))
    if not re.fullmatch(r"UI_DIAGNOSTIC_[0-9a-f]{32}", evidence_id):
        raise ValueError("invalid UI evidence_id")
    if not re.fullmatch(r"EVENT-UI-DIAGNOSTIC-[0-9a-f]{32}", event_id):
        raise ValueError("invalid UI event_id")
    argv = document.get("exact_argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        raise ValueError("exact argv missing")
    executable = Path(str(document.get("executable_path", "")))
    if not executable.is_absolute():
        raise ValueError("executable path is not absolute")
    if not _HEX64.fullmatch(str(document.get("executable_sha256", ""))):
        raise ValueError("executable sha256 missing")
    return {
        "action_request_id": request_id,
        "evidence_id": evidence_id,
        "event_id": event_id,
    }


def summarize_live_evidence(report_root: Path | str) -> dict[str, Any]:
    """Return a fail-visible, read-only summary for the Thin IDE snapshot."""
    try:
        index = load_live_index(report_root)
    except ValueError as exc:
        return {
            "verdict": "BLOCK_LIVE_EVIDENCE_INVALID",
            "state": "BLOCK",
            "count": 0,
            "index_hash": "INVALID",
            "latest_evidence_id": None,
            "latest_event_id": None,
            "latest_action_request_id": None,
            "error": str(exc),
        }
    entries = index.get("entries", {})
    if not entries:
        return {
            "verdict": "NOT_PROVEN",
            "state": index.get("state", "ABSENT"),
            "count": 0,
            "index_hash": index.get("content_sha256"),
            "latest_evidence_id": None,
            "latest_event_id": None,
            "latest_action_request_id": None,
            "error": None,
        }
    latest_id = max(entries, key=lambda key: (str(entries[key].get("indexed_at_utc", "")), key))
    path = live_evidence_root(report_root) / str(entries[latest_id].get("json_path", f"{latest_id}.json"))
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        correlation = verify_action_document(document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "verdict": "BLOCK_LIVE_EVIDENCE_INVALID",
            "state": "BLOCK",
            "count": len(entries),
            "index_hash": index.get("content_sha256"),
            "latest_evidence_id": latest_id,
            "latest_event_id": None,
            "latest_action_request_id": None,
            "error": str(exc),
        }
    return {
        "verdict": "PASS_PROVEN",
        "state": index.get("state", "NOT_PROVEN"),
        "count": len(entries),
        "index_hash": index.get("content_sha256"),
        "latest_evidence_id": correlation["evidence_id"],
        "latest_event_id": correlation["event_id"],
        "latest_action_request_id": correlation["action_request_id"],
        "error": None,
    }
