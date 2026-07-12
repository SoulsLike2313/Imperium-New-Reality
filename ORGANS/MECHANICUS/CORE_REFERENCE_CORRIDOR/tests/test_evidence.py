from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.evidence import (
    EvidenceError,
    EvidenceFinalizedError,
    EvidenceStore,
    EvidenceTamperError,
    REQUIRED_PROOF_FIELDS,
)


def _digest(value: bytes = b"") -> str:
    return hashlib.sha256(value).hexdigest()


def _envelope(evidence_id: str = "ev-0001") -> dict[str, object]:
    return {
        "schema_version": "imperium.evidence_envelope.v1",
        "evidence_id": evidence_id,
        "task_id": "TASK-0001",
        "warp_id": "WARP-0001",
        "event_id": "EVENT-0001",
        "base_head": "a" * 40,
        "result_head_or_tree_hash": "b" * 40,
        "branch": "detached",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "host_fingerprint": {"host_sha256": _digest(b"host")},
        "toolchain": {"python": "3"},
        "exact_argv": ["python", "diagnostic.py"],
        "executable_path": "C:/Python/python.exe",
        "executable_sha256": _digest(b"python"),
        "cwd": "E:/IMPERIUM_WARPS/WARP-0001",
        "environment_profile": "CORRIDOR_MINIMAL",
        "input_hashes": {"input.json": _digest(b"input")},
        "output_hashes": {"output.json": _digest(b"output")},
        "stdout_hash": _digest(b"stdout"),
        "stderr_hash": _digest(),
        "exit_code": 0,
        "timeout": 30,
        "pre_git_state": {"head": "a" * 40, "dirty": False},
        "post_git_state": {"head": "b" * 40, "dirty": True},
        "filesystem_diff": [{"path": "output.json", "status": "A"}],
        "validator_ids": ["validator.safe-execution.v1"],
        "acceptance_results": [{"gate": "diagnostic", "verdict": "PASS_PROVEN"}],
        "organ_verdict_refs": ["organ-ledger:MECHANICUS:postcheck"],
        "owner_decision_ref": "owner-decision:launch-0001",
        "parent_evidence_ids": [],
    }


def test_finalized_json_markdown_pair_and_sealed_index(tmp_path):
    store = EvidenceStore(tmp_path)
    store.write(_envelope(), finalize=False)
    finalized = store.finalize("ev-0001")

    assert finalized["state"] == "FINALIZED"
    markdown = (tmp_path / "ev-0001.md").read_text(encoding="utf-8")
    assert all(f"`{field}`" in markdown for field in REQUIRED_PROOF_FIELDS)

    index = store.finalize_index()
    assert index["state"] == "FINALIZED"
    assert store.verify_all(require_finalized_index=True)["evidence_count"] == 1
    with pytest.raises(EvidenceFinalizedError):
        store.write(_envelope("ev-0002"), finalize=True)


def test_finalized_payload_tampering_is_detected(tmp_path):
    store = EvidenceStore(tmp_path)
    store.write(_envelope(), finalize=True)
    path = tmp_path / "ev-0001.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["exit_code"] = 99
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(EvidenceTamperError, match="hash mismatch"):
        store.verify("ev-0001")


def test_missing_proof_tuple_field_is_blocked(tmp_path):
    store = EvidenceStore(tmp_path)
    envelope = _envelope()
    del envelope["filesystem_diff"]

    with pytest.raises(EvidenceError, match="missing proof tuple fields"):
        store.write(envelope)


def test_index_tampering_is_detected_before_lookup(tmp_path):
    store = EvidenceStore(tmp_path)
    store.write(_envelope(), finalize=True)
    index_path = tmp_path / "EVIDENCE_INDEX.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["entries"]["ev-0001"]["state"] = "DRAFT"
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with pytest.raises(EvidenceTamperError, match="index hash mismatch"):
        store.verify("ev-0001")
