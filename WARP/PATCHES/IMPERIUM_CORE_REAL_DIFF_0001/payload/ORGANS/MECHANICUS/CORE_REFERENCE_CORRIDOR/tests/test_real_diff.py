from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.real_diff import PASS_VERDICT, build_real_diff
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.ui_snapshot import build_ui_snapshot


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _repo(path: Path) -> Path:
    path.mkdir(parents=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "imperium@test.invalid")
    _git(path, "config", "user.name", "Imperium Test")
    (path / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-q", "-m", "seed")
    return path


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _clean_reality(tmp_path: Path) -> Path:
    return _repo(tmp_path / "reality")


def test_clean_committed_branch_has_nonzero_diff(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    (worktree / "seed.txt").write_text("seed\nchanged\n", encoding="utf-8")
    (worktree / "added.txt").write_text("new\n", encoding="utf-8")
    result_head = _commit(worktree, "change")

    result = build_real_diff(worktree, reality, base)

    assert result["verdict"] == PASS_VERDICT
    assert result["result_head"] == result_head
    assert result["files_changed"] == 2
    assert result["insertions"] >= 2
    assert result["worktree_dirty_count"] == 0
    assert result["patch_available"] is True


def test_identical_commits_have_zero_committed_diff(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")

    result = build_real_diff(worktree, reality, base)

    assert result["verdict"] == PASS_VERDICT
    assert result["files_changed"] == 0
    assert result["patch_available"] is False
    assert result["worktree_dirty_count"] == 0


def test_dirty_warp_is_reported_separately_from_committed_range(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    (worktree / "committed.txt").write_text("committed\n", encoding="utf-8")
    _commit(worktree, "committed")
    (worktree / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")

    result = build_real_diff(worktree, reality, base)

    assert result["verdict"] == PASS_VERDICT
    assert result["files_changed"] == 1
    assert result["worktree_dirty_count"] == 1
    assert any("uncommitted.txt" in item for item in result["worktree_status"])


def test_binary_file_is_measured_without_fake_line_counts(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    (worktree / "binary.bin").write_bytes(b"\x00\x01\x02\xff")
    _commit(worktree, "binary")

    result = build_real_diff(worktree, reality, base)
    binary = next(item for item in result["files"] if item["path"] == "binary.bin")

    assert result["verdict"] == PASS_VERDICT
    assert binary["binary"] is True
    assert binary["insertions"] == 0
    assert binary["deletions"] == 0


def test_rename_preserves_old_and_new_paths(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    (worktree / "rename-source.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    _commit(worktree, "rename source")
    base = _git(worktree, "rev-parse", "HEAD")
    _git(worktree, "mv", "rename-source.txt", "rename-target.txt")
    _commit(worktree, "rename")

    result = build_real_diff(worktree, reality, base)
    renamed = next(item for item in result["files"] if item["status"] == "R")

    assert renamed["old_path"] == "rename-source.txt"
    assert renamed["path"] == "rename-target.txt"
    assert result["renamed_files"] == 1


def test_invalid_base_head_fails_closed(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)

    result = build_real_diff(worktree, reality, "not-a-commit")

    assert result["verdict"] == "BLOCK_REAL_DIFF_MEASUREMENT_FAILED"
    assert result["committed_range_proven"] is False


def test_non_ancestor_base_is_blocked(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    _git(worktree, "checkout", "--orphan", "unrelated")
    for child in worktree.iterdir():
        if child.name != ".git":
            if child.is_file():
                child.unlink()
    (worktree / "other.txt").write_text("other\n", encoding="utf-8")
    _commit(worktree, "unrelated")

    result = build_real_diff(worktree, reality, base)

    assert result["verdict"] == "BLOCK_REAL_DIFF_MEASUREMENT_FAILED" or result["verdict"] == "BLOCK_BASE_NOT_ANCESTOR"
    assert result["committed_range_proven"] is False


def test_dirty_reality_blocks_even_when_range_is_measured(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    (worktree / "change.txt").write_text("change\n", encoding="utf-8")
    _commit(worktree, "change")
    (reality / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = build_real_diff(worktree, reality, base)

    assert result["verdict"] == "BLOCK_REALITY_DIRTY"
    assert result["committed_range_proven"] is True
    assert result["reality_dirty_count"] == 1


def test_ui_snapshot_exposes_real_range_files_patch_and_boundary(tmp_path: Path):
    worktree = _repo(tmp_path / "worktree")
    reality = _clean_reality(tmp_path)
    base = _git(worktree, "rev-parse", "HEAD")
    (worktree / "feature.txt").write_text("feature\n", encoding="utf-8")
    _commit(worktree, "feature")

    report = tmp_path / "report"
    report.mkdir()
    (report / "TASK_STATE.json").write_text(
        json.dumps({"task_id": "TEST", "task_type": "TEST", "base_head": base, "current_state": "OWNER_ACCEPT_OR_REJECT", "state_version": 1}),
        encoding="utf-8",
    )
    (report / "KNOWN_GAPS.md").write_text("# Known Gaps\n- test gap\n", encoding="utf-8")
    context = SimpleNamespace(worktree_root=worktree, reality_root=reality)

    snapshot = build_ui_snapshot(context, report)
    diff_panel = next(panel for panel in snapshot["panels"] if panel["id"] == "diff")
    cards = {card["id"]: card for card in diff_panel["cards"]}

    assert diff_panel["status"] == PASS_VERDICT
    assert set(cards) == {"git_range", "git_changed_files", "git_patch_preview", "git_boundary"}
    range_fields = {field["label"]: field["value"] for field in cards["git_range"]["fields"]}
    assert range_fields["files_changed"] == "1"
    assert range_fields["base_head"] == base
