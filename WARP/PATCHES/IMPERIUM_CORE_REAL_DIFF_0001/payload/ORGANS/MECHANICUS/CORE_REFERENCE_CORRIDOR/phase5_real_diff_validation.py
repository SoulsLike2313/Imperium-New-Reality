"""Phase 5 receipt builder for IMPERIUM_CORE_REAL_DIFF_0001."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.real_diff import PASS_VERDICT, build_real_diff

EXPECTED_BASE = "281c3a7c8463de7fb64473929fe0ed975f99f595"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--reality", required=True)
    parser.add_argument("--report-root", required=True)
    parser.add_argument("--targeted-pass", type=int, required=True)
    parser.add_argument("--regression-pass", type=int, required=True)
    parser.add_argument("--npm-build", required=True)
    parser.add_argument("--cargo-check", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    reality = Path(args.reality).resolve()
    report = Path(args.report_root).resolve()
    measured = build_real_diff(repo, reality, EXPECTED_BASE, patch_preview_limit=4000)
    verdict = PASS_VERDICT
    blockers: list[str] = []
    if measured.get("verdict") != PASS_VERDICT:
        blockers.append(f"real diff verdict: {measured.get('verdict')}")
    if measured.get("files_changed", 0) <= 0:
        blockers.append("expected committed range to contain changes")
    if not measured.get("patch_available"):
        blockers.append("patch is not available")
    if measured.get("reality_dirty_count") != 0:
        blockers.append("Reality is dirty")
    if args.targeted_pass < 9:
        blockers.append("targeted test count below 9")
    if args.regression_pass < 59:
        blockers.append("regression test count below pre-Phase-5 baseline")
    if args.npm_build != "PASS":
        blockers.append("npm build failed")
    if args.cargo_check != "PASS":
        blockers.append("cargo check failed")
    if blockers:
        verdict = "REAL_DIFF_REVIEW_PARTIAL_NOT_READY"

    receipt = {
        "schema_version": "imperium.phase5.real_diff.receipt.v1",
        "patch_id": "IMPERIUM_CORE_REAL_DIFF_0001",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "campaign_verdict": "TRUTH_HARDENING_PARTIAL_NOT_READY",
        "phase_6": "NOT_STARTED",
        "base_head": EXPECTED_BASE,
        "result_head_at_validation": measured.get("result_head"),
        "measured": measured,
        "tests": {
            "targeted_pass": args.targeted_pass,
            "regression_pass": args.regression_pass,
            "npm_build": args.npm_build,
            "cargo_check": args.cargo_check,
        },
        "blockers": blockers,
        "land_performed": False,
    }
    json_path = report / "REAL_DIFF_RECEIPT.json"
    md_path = report / "REAL_DIFF_PROOF.md"
    _write_atomic(json_path, json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    receipt["receipt_sha256"] = _sha(json_path)
    _write_atomic(json_path, json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    md = [
        "# Phase 5 — Real Diff Review",
        "",
        f"- Phase verdict: `{verdict}`",
        "- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`",
        "- Phase 6: `NOT_STARTED`",
        f"- Base head: `{EXPECTED_BASE}`",
        f"- Result head at validation: `{measured.get('result_head')}`",
        f"- Files changed in committed range: `{measured.get('files_changed')}`",
        f"- Insertions/deletions: `+{measured.get('insertions')} / -{measured.get('deletions')}`",
        f"- Binary files: `{measured.get('binary_files')}`",
        f"- Renames: `{measured.get('renamed_files')}`",
        f"- WARP dirty entries (Phase 5 payload not committed yet): `{measured.get('worktree_dirty_count')}`",
        f"- Reality dirty entries: `{measured.get('reality_dirty_count')}`",
        f"- Targeted tests: `{args.targeted_pass} passed`",
        f"- Full corridor regression: `{args.regression_pass} passed`",
        f"- npm build: `{args.npm_build}`",
        f"- cargo check: `{args.cargo_check}`",
        f"- Patch SHA-256: `{measured.get('patch_sha256')}`",
        "- Land: `NOT_PERFORMED`",
    ]
    if blockers:
        md += ["", "## Blockers", *[f"- {item}" for item in blockers]]
    _write_atomic(md_path, "\n".join(md) + "\n")
    print(json.dumps({"verdict": verdict, "receipt": str(json_path), "proof": str(md_path)}, ensure_ascii=False))
    return 0 if verdict == PASS_VERDICT else 1


if __name__ == "__main__":
    raise SystemExit(main())
