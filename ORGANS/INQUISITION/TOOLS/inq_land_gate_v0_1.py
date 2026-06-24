#!/usr/bin/env python3
"""INQUISITION Land Gate v0_1 - hard pre-land BLOCK for the WARP land flow.

The Imperium already owns the LAW of clean shape
(_CORE_GOVERNANCE/TOOLS/core_active_root_allowlist_checker_v0_1.py and
REQUIRED_9_ORGANS_V0_1.json). It simply was never ENFORCED at land time, so a
pack could introduce rogue top-level roots or land on a stale base. This gate
wires that law in as a mandatory pre-push blocker.

Gates:
  G1 BASE_FRESHNESS  : local HEAD must equal origin/master HEAD, and the pack's
                       declared base must equal the live HEAD. Stale => DENY.
  G2 ROOT_TAXONOMY   : every target path must resolve under an allowed active
                       root (ORGANS/<known organ> | SUPPORT) or a technical hold.
                       A new rogue top-level root or unknown organ => DENY.
  G3 PROVENANCE_BASE : the manifest's declared base must equal the real parent
                       sha the land will sit on. A provenance lie => DENY.

Emits an imperium.kernel_write_guard.v0_1-style verdict receipt.
Exit 0 = ALLOW, 1 = DENY, 4 = INPUT_INVALID.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = "imperium.kernel_write_guard.v0_1"
GATE_VERSION = "inq.land_gate.v0_1"

ALLOWED_ROOT_DIRS = {"ORGANS", "SUPPORT"}
TECHNICAL_ROOT_HOLDS = {".gitignore", "AGENTS.md", "REPORTS"}
REQUIRED_ORGANS = {
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM", "INQUISITION",
    "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS", "STRATEGIUM",
}
# Extra organ homes that legitimately live under ORGANS/ in the canon snapshot.
KNOWN_EXTRA_ORGANS = {"_CORE_GOVERNANCE", "_POST_WORK_RING", "IMPERIAL_IDE", "SPECULUM"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def norm(p: str) -> str:
    return p.replace(chr(92), "/").strip().lstrip("./")


def known_organs(repo_root: Optional[Path]) -> set:
    organs = set(REQUIRED_ORGANS) | set(KNOWN_EXTRA_ORGANS)
    if repo_root is not None:
        od = repo_root / "ORGANS"
        if od.is_dir():
            for c in od.iterdir():
                if c.is_dir():
                    organs.add(c.name)
    return organs


def git_head(repo_root: Path, ref: str) -> Optional[str]:
    try:
        out = subprocess.run(["git", "-C", str(repo_root), "rev-parse", ref],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def declared_base(manifest: dict) -> str:
    return str(manifest.get("expected_reality_head") or manifest.get("base") or "").strip()


def gate_base_freshness(manifest: dict, live_head: Optional[str], origin_head: Optional[str]) -> list:
    reasons = []
    declared = declared_base(manifest)
    if not declared:
        reasons.append("G1_NO_DECLARED_BASE: manifest declares no base/expected_reality_head")
    if live_head and origin_head and live_head != origin_head:
        reasons.append(
            "G1_BASE_STALE: local HEAD %s != origin/master %s (fetch+rebase before land)"
            % (live_head[:12], origin_head[:12]))
    if declared and live_head and declared != live_head:
        reasons.append(
            "G1_DECLARED_BASE_MISMATCH: manifest base %s != live HEAD %s"
            % (declared[:12], live_head[:12]))
    return reasons


def gate_root_taxonomy(manifest: dict, repo_root: Optional[Path]) -> list:
    reasons = []
    organs = known_organs(repo_root)
    integ = manifest.get("integration", {})
    mp = integ.get("map", {}) if isinstance(integ, dict) else {}
    targets = [norm(v) for v in mp.values()]
    if not targets:
        reasons.append("G2_NO_TARGETS: integration.map is empty; nothing to validate")
    allowed_roots = sorted(ALLOWED_ROOT_DIRS | TECHNICAL_ROOT_HOLDS)
    for t in targets:
        parts = [s for s in t.split("/") if s]
        if not parts:
            reasons.append("G2_EMPTY_TARGET: %r" % t)
            continue
        root = parts[0]
        if root in TECHNICAL_ROOT_HOLDS:
            continue
        if root not in ALLOWED_ROOT_DIRS:
            reasons.append(
                "G2_ROGUE_ROOT: target %r introduces non-canonical top-level root %r; allowed roots: %s"
                % (t, root, allowed_roots))
            continue
        if root == "ORGANS":
            if len(parts) < 2:
                reasons.append("G2_ORGAN_MISSING: %r under ORGANS/ has no organ segment" % t)
                continue
            organ = parts[1]
            if organ not in organs:
                reasons.append(
                    "G2_UNKNOWN_ORGAN: target %r resolves to unknown organ %r (not in canon organ set)"
                    % (t, organ))
    return reasons


def gate_provenance_base(manifest: dict, parent_sha: Optional[str]) -> list:
    reasons = []
    declared = declared_base(manifest)
    if parent_sha and declared and parent_sha != declared:
        reasons.append(
            "G3_PROVENANCE_LIE: declared base %s != actual parent %s"
            % (declared[:12], parent_sha[:12]))
    return reasons


def evaluate(manifest: dict, repo_root: Optional[Path], live_head: Optional[str],
             origin_head: Optional[str], parent_sha: Optional[str], mode: str = "ENFORCED") -> dict:
    deny = []
    deny += gate_base_freshness(manifest, live_head, origin_head)
    deny += gate_root_taxonomy(manifest, repo_root)
    deny += gate_provenance_base(manifest, parent_sha)
    verdict = "ALLOW" if not deny else ("DENY" if mode == "ENFORCED" else "ALLOW_WITH_BYPASS")
    integ = manifest.get("integration", {})
    mp = integ.get("map", {}) if isinstance(integ, dict) else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "gate_version": GATE_VERSION,
        "mode": mode,
        "task_id": manifest.get("task_id"),
        "verdict": verdict,
        "changed_paths": sorted(norm(v) for v in mp.values()),
        "deny_reasons": deny,
        "declared_base": declared_base(manifest),
        "live_head": live_head,
        "origin_head": origin_head,
        "parent_sha": parent_sha,
        "verified_at": utc_now(),
        "verifier": GATE_VERSION,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="INQUISITION pre-land gate v0_1")
    p.add_argument("--manifest", required=True, help="path to pack TASK_MANIFEST.json")
    p.add_argument("--repo-root", default=None, help="repo root for organ discovery / live git")
    p.add_argument("--live-head", default=None, help="override local HEAD sha (else read via git)")
    p.add_argument("--origin-head", default=None, help="override origin/master sha (else read via git)")
    p.add_argument("--parent-sha", default=None, help="actual parent the land will sit on (defaults to live head)")
    p.add_argument("--mode", default="ENFORCED", choices=["ENFORCED", "OBSERVER"])
    p.add_argument("--out", default="", help="optional path to write the verdict receipt")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    mpath = Path(args.manifest)
    if not mpath.exists():
        print(json.dumps({"verdict": "INVALID", "deny_reasons": ["manifest not found: %s" % args.manifest]}))
        return 4
    # tolerate UTF-8 BOM that some Windows editors / Set-Content -Encoding UTF8 emit
    manifest = json.loads(mpath.read_text(encoding="utf-8-sig"))
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    live_head = args.live_head
    origin_head = args.origin_head
    if repo_root is not None and live_head is None:
        live_head = git_head(repo_root, "HEAD")
    if repo_root is not None and origin_head is None:
        origin_head = git_head(repo_root, "origin/master")
    parent_sha = args.parent_sha if args.parent_sha is not None else live_head
    receipt = evaluate(manifest, repo_root, live_head, origin_head, parent_sha, args.mode)
    text = json.dumps(receipt, ensure_ascii=True, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + chr(10), encoding="utf-8")
    print(text)
    return 0 if receipt["verdict"] in ("ALLOW", "ALLOW_WITH_BYPASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
