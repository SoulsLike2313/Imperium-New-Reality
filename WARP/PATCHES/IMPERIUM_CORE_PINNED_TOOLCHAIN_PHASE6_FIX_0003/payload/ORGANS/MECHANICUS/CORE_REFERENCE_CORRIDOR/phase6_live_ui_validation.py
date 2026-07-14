"""Measured two-stage validation for the live Thin IDE diagnostic corridor."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from .evidence import EvidenceStore
from .live_ui_evidence import load_live_index, live_evidence_root, summarize_live_evidence, verify_action_document
from .registry import sha256_file
from .root_resolver import resolve_repository_context
from .tauri_surface_inventory import build_inventory
from .ui_snapshot import build_ui_snapshot

EXPECTED_BASE = "281c3a7c8463de7fb64473929fe0ed975f99f595"
EXPECTED_IMPLEMENTATION_HEAD = "8f34f78f6dc36b82989ac51e2e2baedba26872de"
TASK_ID = "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001"
WARP_ID = "WARP-CORE-REFERENCE-0001"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    rendered = json.dumps(dict(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git failed")
    return completed.stdout.strip()


def _raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _root_index_state(report: Path) -> dict[str, Any]:
    path = report / "EVIDENCE_INDEX.json"
    index = _load(path)
    entries = index.get("entries", {})
    if not isinstance(entries, dict):
        raise RuntimeError("root evidence index entries are invalid")
    return {
        "raw_sha256": _raw_sha256(path),
        "content_sha256": index.get("content_sha256"),
        "state": index.get("state"),
        "evidence_ids": sorted(entries),
    }


def _snapshot_field(snapshot: Mapping[str, Any], panel_id: str, card_id: str, label: str) -> Any:
    for panel in snapshot.get("panels", []):
        if not isinstance(panel, Mapping) or panel.get("id") != panel_id:
            continue
        for card in panel.get("cards", []):
            if not isinstance(card, Mapping) or card.get("id") != card_id:
                continue
            for field in card.get("fields", []):
                if isinstance(field, Mapping) and field.get("label") == label:
                    return field.get("value")
    return None


def capture_baseline(repo: Path, reality: Path, report: Path, output: Path) -> dict[str, Any]:
    live_index = load_live_index(report)
    if live_index.get("entries"):
        raise RuntimeError("Phase 6 first proof requires an empty live UI evidence stream")
    service_source = (repo / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/service.py").read_text(encoding="utf-8")
    if "return self.execute_demo()" not in service_source:
        raise RuntimeError("canonical typed-executor route token was removed")
    inventory = build_inventory(repo)
    if inventory.get("surface_verdict") != "LEGACY_MUTATION_SURFACE_CLOSED":
        raise RuntimeError("Phase 3 mutation surface is not closed")
    baseline = {
        "schema_version": "imperium.phase6_live_ui_baseline.v2",
        "captured_at_utc": _utc_now(),
        "implementation_head": _git(repo, "rev-parse", "HEAD"),
        "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "reality_head": _git(reality, "rev-parse", "HEAD"),
        "reality_status": _git(reality, "status", "--porcelain=v1").splitlines(),
        "root_evidence_index": _root_index_state(report),
        "capability_registry_sha256": _raw_sha256(report / "CAPABILITY_REGISTRY.json"),
        "live_evidence_ids": sorted(live_index.get("entries", {})),
        "phase3_surface_verdict": inventory.get("surface_verdict"),
    }
    if baseline["implementation_head"] != EXPECTED_IMPLEMENTATION_HEAD:
        raise RuntimeError("unexpected implementation HEAD")
    if baseline["reality_head"] != EXPECTED_BASE or baseline["reality_status"]:
        raise RuntimeError("Reality is not at the clean authoritative base")
    _atomic_json(output, baseline)
    return baseline


def verify_after(repo: Path, reality: Path, report: Path, baseline_path: Path, receipt_path: Path, proof_path: Path) -> dict[str, Any]:
    baseline = _load(baseline_path)
    if _git(repo, "rev-parse", "HEAD") != baseline["implementation_head"]:
        raise RuntimeError("implementation HEAD changed after baseline")
    if _git(reality, "rev-parse", "HEAD") != baseline["reality_head"] or _git(reality, "status", "--porcelain=v1"):
        raise RuntimeError("Reality changed during live UI proof")
    if _root_index_state(report) != baseline["root_evidence_index"]:
        raise RuntimeError("finalized root evidence index changed during live UI action")

    live_index = load_live_index(report)
    before = set(baseline.get("live_evidence_ids", []))
    after = set(live_index.get("entries", {}))
    new_ids = sorted(after - before)
    if len(new_ids) != 1:
        raise RuntimeError(f"expected exactly one new live UI evidence, got {new_ids}")
    evidence_id = new_ids[0]
    store = EvidenceStore(live_evidence_root(report))
    verification = store.verify(evidence_id, require_finalized=True)
    evidence_path = live_evidence_root(report) / f"{evidence_id}.json"
    evidence = _load(evidence_path)
    correlation = verify_action_document(evidence)
    if evidence.get("task_id") != TASK_ID or evidence.get("warp_id") != WARP_ID or evidence.get("base_head") != EXPECTED_BASE:
        raise RuntimeError("live UI evidence binding mismatch")
    if evidence.get("exit_code") != 0 or evidence.get("verdict") not in {"PASS", "PASS_PROVEN"}:
        raise RuntimeError("diagnostic execution did not pass")
    executable = Path(str(evidence.get("executable_path", "")))
    if not executable.is_file() or sha256_file(executable) != evidence.get("executable_sha256"):
        raise RuntimeError("executable identity no longer matches evidence")
    argv = evidence.get("exact_argv", [])
    if not isinstance(argv, list) or "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.diagnostic_tool" not in argv:
        raise RuntimeError("evidence argv is not the admitted diagnostic")
    registry = _load(report / "CAPABILITY_REGISTRY.json")
    diagnostic = next((item for item in registry.get("capabilities", []) if item.get("capability_id") == "CORE_DIAGNOSTIC"), None)
    if not isinstance(diagnostic, dict) or diagnostic.get("last_validation", {}).get("evidence_id") != evidence_id:
        raise RuntimeError("capability registry was not correlated to the live evidence")
    capability_by_id = {item.get("capability_id"): item for item in registry.get("capabilities", []) if isinstance(item, dict)}
    result_toolchain = evidence.get("result", {}).get("toolchain", {})
    for capability_id, key in (("CORE_GIT", "git"), ("CORE_PWSH", "pwsh")):
        capability = capability_by_id.get(capability_id)
        observed = result_toolchain.get(key) if isinstance(result_toolchain, dict) else None
        if not isinstance(capability, dict) or capability.get("admission_state") != "ACTIVE":
            raise RuntimeError(f"{capability_id} is not actively admitted")
        if not isinstance(observed, dict):
            raise RuntimeError(f"live diagnostic omitted {key} toolchain proof")
        observed_path = Path(str(observed.get("executable", ""))).resolve()
        capability_path = Path(str(capability.get("executable_path", ""))).resolve()
        if observed_path != capability_path:
            raise RuntimeError(f"live diagnostic {key} path differs from registry")
        if observed.get("sha256") != capability.get("executable_sha256"):
            raise RuntimeError(f"live diagnostic {key} hash differs from registry")
        if observed.get("path_resolution_used") is not False:
            raise RuntimeError(f"live diagnostic {key} used PATH resolution")

    inventory = build_inventory(repo)
    if inventory.get("surface_verdict") != "LEGACY_MUTATION_SURFACE_CLOSED":
        raise RuntimeError("Phase 3 regressed after live UI implementation")
    context = resolve_repository_context(repo)
    snapshot = build_ui_snapshot(context, report)
    summary = summarize_live_evidence(report)
    if summary.get("verdict") != "PASS_PROVEN":
        raise RuntimeError("live evidence summary is not proven")
    live_count = int(_snapshot_field(snapshot, "evidence", "evidence_index", "live_ui_count"))
    snapshot_evidence = _snapshot_field(snapshot, "evidence", "evidence_index", "latest_ui_evidence")
    snapshot_request = _snapshot_field(snapshot, "execution_trace", "trace_summary", "latest_ui_request")
    if live_count != len(after) or snapshot_evidence != evidence_id or snapshot_request != correlation["action_request_id"]:
        raise RuntimeError("backend snapshot does not reflect persisted live evidence")

    receipt = {
        "schema_version": "imperium.phase6_live_ui_action_receipt.v2",
        "phase": 6,
        "verdict": "LIVE_UI_CORRIDOR_PROVEN",
        "implementation_head": baseline["implementation_head"],
        "base_head": EXPECTED_BASE,
        "task_id": TASK_ID,
        "warp_id": WARP_ID,
        "action_id": "run_core_diagnostic",
        "action_request_id": correlation["action_request_id"],
        "evidence_id": evidence_id,
        "event_id": correlation["event_id"],
        "evidence_proof_sha256": verification["proof_sha256"],
        "exact_argv": argv,
        "executable_path": evidence.get("executable_path"),
        "executable_sha256": evidence.get("executable_sha256"),
        "root_index_unchanged": True,
        "capability_registry_before_sha256": baseline["capability_registry_sha256"],
        "capability_registry_after_sha256": _raw_sha256(report / "CAPABILITY_REGISTRY.json"),
        "capability_last_validation_correlated": True,
        "pinned_git": result_toolchain.get("git"),
        "pinned_pwsh": result_toolchain.get("pwsh"),
        "path_resolution_used": False,
        "live_count_before": len(before),
        "live_count_after": len(after),
        "snapshot_live_count": live_count,
        "phase3_surface_verdict": inventory["surface_verdict"],
        "reality_head_before": baseline["reality_head"],
        "reality_head_after": _git(reality, "rev-parse", "HEAD"),
        "reality_unchanged": True,
        "verified_at_utc": _utc_now(),
        "evidence_path": str(evidence_path),
    }
    _atomic_json(receipt_path, receipt)
    proof_path.write_text(
        "# Phase 6 — Live UI Corridor Proof\n\n"
        f"Verdict: `{receipt['verdict']}`\n\n"
        f"- Canonical action: `Run Diagnostic`\n"
        f"- Action request: `{receipt['action_request_id']}`\n"
        f"- Evidence: `{receipt['evidence_id']}`\n"
        f"- Event: `{receipt['event_id']}`\n"
        f"- Live count: `{receipt['live_count_before']} -> {receipt['live_count_after']}`\n"
        f"- Root sealed index unchanged: `{receipt['root_index_unchanged']}`\n"
        f"- Phase 3 surface: `{receipt['phase3_surface_verdict']}`\n"
        f"- Reality unchanged: `{receipt['reality_unchanged']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "verify"), required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--reality", required=True)
    parser.add_argument("--corridor-report", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--hardening-report")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    reality = Path(args.reality).resolve()
    report = Path(args.corridor_report).resolve()
    baseline = Path(args.baseline).resolve()
    if args.mode == "baseline":
        result = capture_baseline(repo, reality, report, baseline)
        print(json.dumps({"verdict": "LIVE_UI_BASELINE_CAPTURED", "baseline": str(baseline), "live_count": len(result["live_evidence_ids"])}, sort_keys=True))
        return 0
    if not args.hardening_report:
        raise RuntimeError("--hardening-report is required for verify")
    hardening = Path(args.hardening_report).resolve()
    result = verify_after(repo, reality, report, baseline, hardening / "LIVE_UI_ACTION_RECEIPT.json", hardening / "LIVE_UI_CORRIDOR_PROOF.md")
    print(json.dumps({"verdict": result["verdict"], "receipt": str(hardening / "LIVE_UI_ACTION_RECEIPT.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
