from __future__ import annotations

from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR import phase6_live_ui_validation as validation


def _prepare_repo(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    repo = tmp_path / "repo"
    reality = tmp_path / "reality"
    report = tmp_path / "report"
    output = tmp_path / "baseline.json"
    (repo / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR").mkdir(parents=True)
    (repo / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/service.py").write_text(
        "return self.execute_demo()\n",
        encoding="utf-8",
    )
    reality.mkdir()
    report.mkdir()
    (report / "CAPABILITY_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    return repo, reality, report, output


def test_phase6_baseline_accepts_existing_historical_live_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, reality, report, output = _prepare_repo(tmp_path)

    monkeypatch.setattr(
        validation,
        "load_live_index",
        lambda _report: {"entries": {"UI_DIAGNOSTIC_ATTEMPT_01": {}}},
    )
    monkeypatch.setattr(
        validation,
        "build_inventory",
        lambda _repo: {"surface_verdict": "LEGACY_MUTATION_SURFACE_CLOSED"},
    )
    monkeypatch.setattr(
        validation,
        "_root_index_state",
        lambda _report: {"state": "FINALIZED", "evidence_ids": []},
    )
    monkeypatch.setattr(validation, "_raw_sha256", lambda _path: "a" * 64)

    def fake_git(root: Path, *args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return (
                "281c3a7c8463de7fb64473929fe0ed975f99f595"
                if root == reality
                else "committed-phase6-head"
            )
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return "servitor/imperium-core-reference-corridor-0001"
        if args[0] == "status":
            return ""
        raise AssertionError(args)

    monkeypatch.setattr(validation, "_git", fake_git)

    baseline = validation.capture_baseline(repo, reality, report, output)

    assert baseline["schema_version"] == "imperium.phase6_live_ui_baseline.v3"
    assert baseline["implementation_head"] == "committed-phase6-head"
    assert baseline["implementation_tracked_status"] == []
    assert baseline["live_evidence_ids"] == ["UI_DIAGNOSTIC_ATTEMPT_01"]


def test_phase6_baseline_rejects_tracked_dirty_implementation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, reality, report, output = _prepare_repo(tmp_path)

    monkeypatch.setattr(validation, "load_live_index", lambda _report: {"entries": {}})
    monkeypatch.setattr(
        validation,
        "build_inventory",
        lambda _repo: {"surface_verdict": "LEGACY_MUTATION_SURFACE_CLOSED"},
    )
    monkeypatch.setattr(
        validation,
        "_root_index_state",
        lambda _report: {"state": "FINALIZED", "evidence_ids": []},
    )
    monkeypatch.setattr(validation, "_raw_sha256", lambda _path: "b" * 64)

    def fake_git(root: Path, *args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return (
                "281c3a7c8463de7fb64473929fe0ed975f99f595"
                if root == reality
                else "committed-phase6-head"
            )
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return "servitor/imperium-core-reference-corridor-0001"
        if args == ("status", "--porcelain=v1", "--untracked-files=no") and root == repo:
            return " M tracked.py"
        if args == ("status", "--porcelain=v1") and root == reality:
            return ""
        raise AssertionError((root, args))

    monkeypatch.setattr(validation, "_git", fake_git)

    with pytest.raises(RuntimeError, match="tracked worktree is dirty"):
        validation.capture_baseline(repo, reality, report, output)


def test_phase6_verify_still_requires_same_head_as_captured_baseline() -> None:
    source = Path(validation.__file__).read_text(encoding="utf-8")
    assert 'if _git(repo, "rev-parse", "HEAD") != baseline["implementation_head"]:' in source
    assert 'raise RuntimeError("implementation HEAD changed after baseline")' in source
