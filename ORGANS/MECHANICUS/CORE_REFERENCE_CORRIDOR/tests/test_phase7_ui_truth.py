from __future__ import annotations

from types import SimpleNamespace
import json
from pathlib import Path

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR import ui_snapshot


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _organ_panel(snapshot: dict) -> dict:
    return next(panel for panel in snapshot["panels"] if panel["id"] == "great_nine_throne")


def _field(card: dict, label: str) -> str:
    return next(field["value"] for field in card["fields"] if field["label"] == label)


def _fixture(tmp_path: Path) -> tuple[SimpleNamespace, Path]:
    report = tmp_path / "report"
    report.mkdir()
    _write(
        report / "TASK_STATE.json",
        {
            "task_id": "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001",
            "base_head": "a" * 40,
            "warp": {"path": str(tmp_path / "warp"), "state": "READY_FOR_REVIEW"},
        },
    )
    _write(
        report / "CAPABILITY_REGISTRY.json",
        {"default_policy": "DENY", "capabilities": [], "ui_actions": []},
    )
    organs = [
        "ASTRONOMICON",
        "ADMINISTRATUM",
        "DOCTRINARIUM",
        "MECHANICUS",
        "INQUISITION",
        "CUSTODES",
        "STRATEGIUM",
        "SCHOLA_IMPERIALIS",
        "OFFICIO_AGENTIS",
        "THRONE",
    ]
    _write(
        report / "ORGAN_PARTICIPATION_LEDGER.json",
        {
            "overall_verdict": "PASS_WITH_DEBT",
            "records": [
                {
                    "organ_id": organ,
                    "phase": "POSTCHECK",
                    "verdict": "PASS_PROVEN",
                    "confidence": 1.0,
                    "evidence_refs": ["historical.json"],
                }
                for organ in organs
            ],
        },
    )
    _write(report / "EVIDENCE_INDEX.json", {"entries": {}, "state": "FINALIZED"})
    _write(report / "CHECKPOINT_INDEX.json", {"entries": {}})
    (report / "KNOWN_GAPS.md").write_text("# Known Gaps\n- debt\n", encoding="utf-8")
    context = SimpleNamespace(worktree_root=tmp_path / "warp", reality_root=tmp_path / "reality")
    return context, report


def test_ui_snapshot_fails_closed_when_current_claim_authority_is_absent(
    tmp_path: Path, monkeypatch
) -> None:
    context, report = _fixture(tmp_path)
    monkeypatch.setattr(ui_snapshot, "summarize_live_evidence", lambda _report: {"count": 0, "verdict": "PASS_PROVEN"})
    monkeypatch.setattr(
        ui_snapshot,
        "build_real_diff",
        lambda *_args, **_kwargs: {
            "verdict": "REAL_DIFF_REVIEW_PROVEN",
            "files": [],
            "worktree_status": [],
            "reality_status": [],
        },
    )
    snapshot = ui_snapshot.build_ui_snapshot(context, report)
    panel = _organ_panel(snapshot)
    assert panel["status"] == "NOT_PROVEN"
    assert len(panel["cards"]) == 10
    assert all(_field(card, "verdict") == "NOT_PROVEN" for card in panel["cards"])
    assert all(_field(card, "historical_verdict") == "PASS_PROVEN" for card in panel["cards"])


def test_ui_snapshot_uses_phase7_current_claim_authority(
    tmp_path: Path, monkeypatch
) -> None:
    context, report = _fixture(tmp_path)
    _write(
        report / "CURRENT_CLAIM_STATUS.json",
        {
            "organ_ring_verdict": "NOT_PROVEN",
            "organs": {
                organ: {
                    "phase": "PHASE7_CURRENT_TRUTH",
                    "verdict": "NOT_PROVEN",
                    "confidence": 0,
                    "evidence_refs": [],
                    "claim_state": "HISTORICAL_NOT_PROMOTED",
                }
                for organ in [
                    "ASTRONOMICON",
                    "ADMINISTRATUM",
                    "DOCTRINARIUM",
                    "MECHANICUS",
                    "INQUISITION",
                    "CUSTODES",
                    "STRATEGIUM",
                    "SCHOLA_IMPERIALIS",
                    "OFFICIO_AGENTIS",
                    "THRONE",
                ]
            },
        },
    )
    monkeypatch.setattr(ui_snapshot, "summarize_live_evidence", lambda _report: {"count": 0, "verdict": "PASS_PROVEN"})
    monkeypatch.setattr(
        ui_snapshot,
        "build_real_diff",
        lambda *_args, **_kwargs: {
            "verdict": "REAL_DIFF_REVIEW_PROVEN",
            "files": [],
            "worktree_status": [],
            "reality_status": [],
        },
    )
    snapshot = ui_snapshot.build_ui_snapshot(context, report)
    panel = _organ_panel(snapshot)
    assert panel["status"] == "NOT_PROVEN"
    assert all(_field(card, "claim_state") == "HISTORICAL_NOT_PROMOTED" for card in panel["cards"])
