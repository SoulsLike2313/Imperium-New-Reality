from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.evidence import EvidenceStore
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.live_ui_evidence import (
    create_action_context,
    load_live_index,
    summarize_live_evidence,
)
import ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.ui_snapshot as ui_snapshot


def _envelope(evidence_id: str, event_id: str, request_id: str) -> dict:
    zero = hashlib.sha256(b"").hexdigest()
    return {
        "schema_version": "imperium.evidence.v1",
        "evidence_id": evidence_id,
        "task_id": "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001",
        "warp_id": "WARP-CORE-REFERENCE-0001",
        "event_id": event_id,
        "base_head": "2" * 40,
        "result_head_or_tree_hash": "3" * 40,
        "branch": "feature",
        "timestamp_utc": "2026-07-13T00:00:00Z",
        "host_fingerprint": "fixture",
        "toolchain": {"python": "3.12"},
        "exact_argv": ["python.exe", "-m", "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.diagnostic_tool"],
        "executable_path": str(Path(__file__).resolve()),
        "executable_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cwd": str(Path.cwd()),
        "environment_profile": "TEST",
        "input_hashes": {},
        "output_hashes": {},
        "stdout_hash": zero,
        "stderr_hash": zero,
        "exit_code": 0,
        "timeout": 10,
        "pre_git_state": {},
        "post_git_state": {},
        "filesystem_diff": {},
        "validator_ids": ["FIXTURE"],
        "acceptance_results": {"verdict": "PASS_PROVEN"},
        "organ_verdict_refs": [],
        "owner_decision_ref": None,
        "parent_evidence_ids": [],
        "verdict": "PASS_PROVEN",
        "action_request_id": request_id,
        "ui_action_id": "run_core_diagnostic",
        "ui_dispatch": "CORRIDOR_UI_ACTION_CANONICAL_ROUTE",
    }


def test_phase6_01_action_context_is_unique_and_rejects_unsafe_id() -> None:
    first = create_action_context()
    second = create_action_context()
    assert first != second
    assert first["evidence_id"].startswith("UI_DIAGNOSTIC_")
    with pytest.raises(ValueError, match="action_request_id"):
        create_action_context({"action_request_id": "../unsafe"})


def test_phase6_02_absent_live_index_is_read_only(tmp_path: Path) -> None:
    report = tmp_path / "report"
    index = load_live_index(report)
    assert index["state"] == "ABSENT"
    assert not report.exists()


def test_phase6_03_canonical_store_and_summary_correlate(tmp_path: Path) -> None:
    report = tmp_path / "report"
    identity = create_action_context({"action_request_id": "ui-fixture-0001"})
    store = EvidenceStore(report / "live_ui_evidence")
    store.write(_envelope(identity["evidence_id"], identity["event_id"], identity["action_request_id"]), finalize=True)
    assert store.verify(identity["evidence_id"])["verdict"] == "PASS_PROVEN"
    summary = summarize_live_evidence(report)
    assert summary["verdict"] == "PASS_PROVEN"
    assert summary["count"] == 1
    assert summary["latest_action_request_id"] == "ui-fixture-0001"


def test_phase6_04_snapshot_reads_live_stream_without_new_writer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = tmp_path / "report"
    report.mkdir()
    (report / "TASK_STATE.json").write_text(json.dumps({"task_id": "T", "base_head": "2" * 40, "warp": {"path": str(tmp_path), "state": "ACTIVE"}}), encoding="utf-8")
    (report / "CAPABILITY_REGISTRY.json").write_text(json.dumps({"default_policy": "DENY", "capabilities": [], "ui_actions": []}), encoding="utf-8")
    (report / "EVIDENCE_INDEX.json").write_text(json.dumps({"state": "FINALIZED", "entries": {}, "content_sha256": "fixture"}), encoding="utf-8")
    identity = create_action_context({"action_request_id": "ui-fixture-0002"})
    EvidenceStore(report / "live_ui_evidence").write(_envelope(identity["evidence_id"], identity["event_id"], identity["action_request_id"]), finalize=True)
    monkeypatch.setattr(ui_snapshot, "build_real_diff", lambda *args: {"verdict": "PASS_PROVEN", "files": [], "errors": []})
    context = SimpleNamespace(worktree_root=str(tmp_path), reality_root=str(tmp_path))
    snapshot = ui_snapshot.build_ui_snapshot(context, report)
    evidence_panel = next(panel for panel in snapshot["panels"] if panel["id"] == "evidence")
    fields = {field["label"]: field["value"] for field in evidence_panel["cards"][0]["fields"]}
    assert fields["live_ui_count"] == "1"
    assert fields["latest_ui_request"] == "ui-fixture-0002"


def test_phase6_05_phase3_exact_route_token_is_preserved() -> None:
    service_path = Path(__file__).resolve().parents[1] / "service.py"
    source = service_path.read_text(encoding="utf-8")
    assert "self.registry.action(action_id)" in source
    assert "execute_capability(" in source
    assert "return self.execute_demo()" in source
    assert "self._pending_ui_action_context = create_action_context(payload)" in source
