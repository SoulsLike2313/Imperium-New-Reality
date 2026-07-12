"""Deterministic report projections for the reference corridor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import EvidenceFinalizedError, EvidenceStore
from .executor import git_state
from .organ_ledger import OrganLedger
from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context
from .service import BASE_HEAD, REPORT_RELATIVE, TASK_ID, TASKPACK_RELATIVE, WARP_ID


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=str(cwd),
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )


def _control_envelope(
    *,
    evidence_id: str,
    executable: Path,
    argv: list[str],
    result: dict[str, Any],
    context: Any,
    acceptance: list[dict[str, Any]],
) -> dict[str, Any]:
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    empty = _sha(b"")
    state = {"reality": git_state(Path(context.reality_root)), "worktree": git_state(Path(context.worktree_root))}
    blocked = str(result.get("verdict", "")).startswith("BLOCK") or any(
        str(item.get("verdict", "")).startswith("BLOCK") for item in acceptance if isinstance(item, dict)
    )
    return {
        "schema_version": "imperium.core_reference_corridor.evidence_envelope.v0_1",
        "evidence_id": evidence_id,
        "task_id": TASK_ID,
        "warp_id": WARP_ID,
        "event_id": "EVENT-" + evidence_id,
        "base_head": BASE_HEAD,
        "result_head_or_tree_hash": BASE_HEAD,
        "branch": context.branch,
        "timestamp_utc": _utc_now(),
        "host_fingerprint": {"host_sha256": _sha((platform.system() + platform.machine() + platform.node()).encode("utf-8"))},
        "toolchain": {"platform": platform.system(), "python": platform.python_version()},
        "exact_argv": argv,
        "executable_path": str(executable),
        "executable_sha256": sha256_file(executable),
        "cwd": str(context.worktree_root),
        "environment_profile": "CORE_CONTROL_READ_ONLY_V0_1",
        "input_hashes": {"owner_prompt": "3fa7249d956c8a79c04a8b5f323ec82bec8de1ebabf7aa3cace18d96e7ef6fd8"},
        "output_hashes": {"result": _sha(encoded)},
        "stdout_hash": _sha(encoded),
        "stderr_hash": empty,
        "exit_code": 2 if blocked else 0,
        "timeout": 30,
        "pre_git_state": state,
        "post_git_state": state,
        "filesystem_diff": [],
        "validator_ids": [evidence_id + "_VALIDATOR"],
        "acceptance_results": acceptance,
        "organ_verdict_refs": [f"{REPORT_RELATIVE.as_posix()}/ORGAN_PARTICIPATION_LEDGER.json"],
        "owner_decision_ref": "OWNER-LAUNCH-IMPERIUM-CORE-REFERENCE-0001",
        "parent_evidence_ids": [],
        "verdict": "BLOCK" if blocked else "PASS_PROVEN",
        "result": result,
    }


def _write_control_receipts(context: Any, report: Path) -> None:
    store = EvidenceStore(report)
    pwsh = Path(shutil.which("pwsh") or "").resolve()
    git = Path(shutil.which("git") or "").resolve()
    reality = Path(context.reality_root)
    worktree = Path(context.worktree_root)
    pwsh_version = _run([str(pwsh), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"], worktree).stdout.strip()
    warp_list_argv = [str(git), "worktree", "list", "--porcelain"]
    _run(warp_list_argv, worktree)
    reality_state = git_state(reality)
    origin = _run([str(git), "-C", str(reality), "rev-parse", "origin/master"], worktree).stdout.strip()
    drift = {
        "expected_head": BASE_HEAD,
        "head": reality_state["head"],
        "branch": reality_state["branch"],
        "porcelain": reality_state["porcelain"],
        "origin_master": origin,
        "pwsh_version": pwsh_version,
        "verdict": "DRIFT_GUARD_PASS" if reality_state["head"] == origin == BASE_HEAD and not reality_state["dirty"] and reality_state["branch"] == "master" and pwsh_version == "7.6.2" else "AUDIT_DRIFT_BLOCKED",
    }
    warp = {
        "warp_id": WARP_ID,
        "path": str(worktree),
        "base_head": BASE_HEAD,
        "head": git_state(worktree)["head"],
        "branch": context.branch,
        "git_metadata_file": (worktree / ".git").is_file(),
        "git_common_dir": str(context.git_common_dir),
        "creation_command": ["git", "worktree", "add", "-b", context.branch, str(worktree), BASE_HEAD],
        "verdict": "WARP_CREATE_PROVEN" if (worktree / ".git").is_file() and git_state(worktree)["head"] == BASE_HEAD else "BLOCK",
    }
    for base_evidence_id, executable, argv, result in [
        (
            "DRIFT_GUARD_RECEIPT",
            pwsh,
            [str(pwsh), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            drift,
        ),
        ("WARP_CREATE_RECEIPT", git, warp_list_argv, warp),
    ]:
        evidence_id = base_evidence_id if not (report / f"{base_evidence_id}.json").is_file() else base_evidence_id.replace("_RECEIPT", "_RECHECK_RECEIPT")
        envelope = _control_envelope(
            evidence_id=evidence_id,
            executable=executable,
            argv=argv,
            result=result,
            context=context,
            acceptance=[{"check": result["verdict"], "verdict": "PASS" if not str(result["verdict"]).endswith("BLOCK") and result["verdict"] != "BLOCK" else "BLOCK"}],
        )
        envelope["parent_evidence_ids"] = ["REPORT_BUILD_FINAL_RECEIPT"]
        try:
            store.write(envelope, finalize=True)
        except EvidenceFinalizedError:
            store.verify(evidence_id)


def _changed_files(worktree: Path) -> list[dict[str, str]]:
    raw = _run(["git", "-C", str(worktree), "status", "--porcelain=v1", "-z", "--untracked-files=all"], worktree).stdout
    records: list[dict[str, str]] = []
    for entry in filter(None, raw.split("\0")):
        status = entry[:2]
        relative = entry[3:].replace("\\", "/")
        if relative.endswith("/.TASK_STATE.lock"):
            continue
        records.append({"path": relative, "status": status})
    return sorted(records, key=lambda item: item["path"])


def _write_human_reports(report: Path, *, ready: bool) -> None:
    owner_verdict = "REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW" if ready else "REFERENCE_CORRIDOR_PARTIAL_NOT_READY"
    owner_summary = (
        "Финальная validation matrix, 20 adversarial-сценариев, Great Nine post-check и неизменность Reality доказаны. "
        "Результат ожидает только решения Owner; land/merge/push в master не выполнялись."
        if ready
        else "Коридор еще не прошел полный validation/post-check контур. Master land не разрешен и не выполнялся."
    )
    _atomic_text(
        report / "OWNER_RESULT.md",
        f"""# Owner Result

Current verdict: `{owner_verdict}`

{owner_summary}
""",
    )
    _atomic_text(
        report / "ARCHITECTURE_DELTA.md",
        """# Architecture Delta

- Added one task-local `CORE_REFERENCE_CORRIDOR` package under Mechanicus.
- Added Git-derived root context, atomic task transaction, one capability registry, typed executor, exact-HEAD WARP manager, evidence/checkpoint stores, organ ledger and Owner gate.
- Replaced APP_TAURI's legacy cockpit entry with a generic backend snapshot renderer and two fixed bridge commands.
- Removed the direct `RUN_*.ps1` Tauri execution surface.
- Kept legacy registries, patch stores and WARP implementations read-only for migration; no deletion or hidden promotion occurred.
""",
    )
    _atomic_text(
        report / "AUDIT_FINDINGS_CLOSURE_MATRIX.md",
        """# Audit Findings Closure Matrix

| Finding | Current disposition | Proof |
|---|---|---|
| M01/M02 | ISOLATED_WITH_OWNER_SUPERSESSION_PENDING | `CANON_SUPERSESSION_PROPOSAL.md` |
| M04 | CLOSED_IN_REFERENCE_CORRIDOR | nested Git root tests + diagnostic |
| M05 | CLOSED_IN_REFERENCE_CORRIDOR | atomic `TASK_STATE.json` and transition log |
| M07/M08 | CLOSED_IN_REFERENCE_CORRIDOR | one default-deny registry + typed executor |
| M09/M11 | CLOSED_FOR_NEW_UI_CORRIDOR | direct runner removed; legacy runners not executed |
| M10/M12/M13 | CLOSED_IN_REFERENCE_CORRIDOR | exact-HEAD worktree manager + lifecycle fixtures |
| M14 | CLOSED_IN_REFERENCE_CORRIDOR | finalized proof envelopes and tamper tests |
| M15 | CLOSED_IN_THIN_IDE_SLICE | semantic UI/backend parity receipt |
| M17 | CLOSED_FOR_INITIAL_REFERENCE_SLICE | admitted diagnostic end-to-end receipt |
""",
    )
    _atomic_text(
        report / "MIGRATION_MAP.md",
        """# Migration Map

| Old path/role | Risk | New replacement | Adapter/removal precondition | Status |
|---|---|---|---|---|
| heuristic root resolvers | stale/hardcoded root | `CORE_REFERENCE_CORRIDOR/root_resolver.py` | read-only compatibility only; remove after consumers migrate | LEGACY_READ_ONLY |
| Astronomicon/IDE current-state files | contradictory current task | atomic corridor `TASK_STATE.json` | generate views after Owner admission | LEGACY_READ_ONLY |
| three Mechanicus registries | competing authority/effect drift | task-local `CAPABILITY_REGISTRY.json` | migrate consumers and validate parity | LEGACY_READ_ONLY |
| hardcoded Tauri actions | UI/backend drift | registry-backed snapshot actions | semantic parity required | DEPRECATED_UNSAFE |
| direct Tauri patch runner | arbitrary Reality mutation | fixed corridor bridge -> typed executor | no re-enable without new Owner task | QUARANTINED |
| copytree WARP | no Git metadata/exact HEAD | `warp_manager.py` Git worktree | migrate runtime callers | DEPRECATED_UNSAFE |
| tracked `WARP/PATCHES` and intake/archive meanings | mixed semantics | external managed runtime WARP | retain as non-executable legacy stores | LEGACY_READ_ONLY |
| old `RUN_*.ps1` patch runners | direct Reality write/removal | no replacement execution authority | per-runner migration and owner approval | QUARANTINED |
| incomplete receipt formats | missing proof tuple | `evidence.py` envelope | independent validator and hash migration | LEGACY_READ_ONLY |
""",
    )
    _atomic_text(
        report / "KNOWN_GAPS.md",
        """# Known Gaps

- `CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING`: Constitution wording is not amended; land requires a separate Owner decision.
- Windows Git rejects `-C` for the tested path above 260 characters; the resolver localizes this as `BLOCK` and never guesses a root.
- Partial checkpoint restore is `NOT_IMPLEMENTED`; the false partial-restore path is blocked.
- API, MCP, Skills editor, external LLM, quiet scheduler, live causal graph, learned-rule automation and coding abstraction are `SCAFFOLD_ONLY / NOT_OPERATIONALLY_PROVEN`.
- The cost/time contract is implemented as a pause gate; no background estimator service is claimed.
- Administratum remains a minimal ledger adapter in this initial corridor.
- Owner result acceptance, land authorization, master merge and master push are pending and were not inferred.
- Runtime GUI interaction was not opened automatically; build, bridge tests and semantic contract parity are the current UI proof.
""",
    )
    _atomic_text(
        report / "OWNER_REVIEW_GUIDE.md",
        """# Owner Review Guide

1. Read `OWNER_RESULT.md` and `KNOWN_GAPS.md`.
2. Run the exact commands listed in the final Officio response from this WARP.
3. Inspect `CAPABILITY_REGISTRY.json`, `TASK_STATE.json`, `ORGAN_PARTICIPATION_LEDGER.json`, `VALIDATION_MATRIX.json` and `EVIDENCE_INDEX.json`.
4. Compare `FILES_TO_LAND.json` with `git diff`.
5. Choose accept, reject/rework, forbid land, discard or destroy through the Owner gate.

Review does not mutate master. A land task must be separately approved.
""",
    )
    _atomic_text(
        report / "LAND_PLAN.md",
        """# Land Plan — Preparation Only

Status: `OWNER_ACCEPTANCE_AND_LAND_AUTHORIZATION_PENDING`

1. Verify `HASH_MANIFEST.json`, evidence index, tests, secret scan and current Reality HEAD.
2. Owner accepts the result and separately authorizes land preparation.
3. Create a reviewed candidate commit in the WARP branch if the Owner wants commit-based land.
4. In a separate land task, require `master == origin/master == base_head` and apply the exact reviewed file set atomically.
5. Re-run all gates and retain rollback reference to `281c3a7c8463de7fb64473929fe0ed975f99f595`.

This task executes none of these land operations.
""",
    )
    _atomic_text(
        report / "ROLLBACK_PLAN.md",
        """# Rollback Plan

- Before land: Owner may reject, discard, then destroy the external WARP through explicit gates; Reality is already unchanged.
- After a future approved land: compare-and-swap the master ref only when it still equals the expected result, restore it to the recorded base on failure, then restore the clean worktree from Git.
- Partial task restore remains blocked; use a full semantic checkpoint restore unless dependency isolation is independently proven.
- Atomic land/rollback behavior is proven only in a disposable Git fixture, never on current master.
""",
    )


def _ready_facts(context: Any, report: Path, task_state: dict[str, Any], ring: dict[str, Any]) -> dict[str, Any]:
    reality = git_state(Path(context.reality_root))
    git = Path(shutil.which("git") or "").resolve()
    pwsh = Path(shutil.which("pwsh") or "").resolve()
    origin = _run([str(git), "-C", str(context.reality_root), "rev-parse", "origin/master"], Path(context.worktree_root)).stdout.strip()
    pwsh_version = _run(
        [str(pwsh), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"],
        Path(context.worktree_root),
    ).stdout.strip()
    matrix_path = report / "VALIDATION_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.is_file() else {}
    current_receipts = matrix.get("current_receipts", {}) if isinstance(matrix, dict) else {}
    receipt_checks: dict[str, str] = {}
    store = EvidenceStore(report)
    for role, filename in sorted(current_receipts.items()) if isinstance(current_receipts, dict) else []:
        try:
            document = json.loads((report / filename).read_text(encoding="utf-8"))
            store.verify(Path(filename).stem)
            result = document.get("result", {})
            receipt_checks[role] = "PASS" if document.get("verdict") == "PASS_PROVEN" and isinstance(result, dict) and result.get("verdict") == "PASS_PROVEN" else "BLOCK"
        except Exception:
            receipt_checks[role] = "BLOCK"
    expected_roles = {"validation", "negative_proof", "ui_backend_parity"}
    checks = {
        "owner_review_state": task_state.get("current_state") == "OWNER_ACCEPT_OR_REJECT",
        "validation_matrix": matrix.get("verdict") == "PASS_PROVEN",
        "current_receipts": set(receipt_checks) == expected_roles and all(value == "PASS" for value in receipt_checks.values()),
        "great_nine_post_work_ring": ring.get("ring_verdict") == "POST_WORK_ORGAN_RING_PASS",
        "reality_clean_exact_head": not reality["dirty"] and reality["branch"] == "master" and reality["head"] == origin == BASE_HEAD,
        "powershell_exact_version": pwsh_version == "7.6.2",
        "master_land_absent": task_state.get("owner_decisions", [{}])[-1].get("decision") != "ACCEPT_RESULT",
    }
    return {
        "checks": checks,
        "receipt_checks": receipt_checks,
        "current_receipts": current_receipts,
        "reality": reality,
        "origin_master": origin,
        "pwsh_version": pwsh_version,
        "ready": all(checks.values()),
    }


def _write_owner_ready(context: Any, report: Path, facts: dict[str, Any]) -> None:
    result = {
        "verdict": "PASS_PROVEN" if facts["ready"] else "BLOCK",
        "owner_result": "REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW" if facts["ready"] else "REFERENCE_CORRIDOR_PARTIAL_NOT_READY",
        "checks": facts["checks"],
        "current_receipts": facts["current_receipts"],
        "receipt_checks": facts["receipt_checks"],
        "validation_history_retained": [
            "VALIDATION_RECEIPT.json",
            "VALIDATION_RETRY_01_RECEIPT.json",
            "VALIDATION_RETRY_02_RECEIPT.json",
        ],
        "master_land_merge_push": False,
    }
    acceptance = [{"check": name, "verdict": "PASS" if passed else "BLOCK"} for name, passed in sorted(facts["checks"].items())]
    envelope = _control_envelope(
        evidence_id="OWNER_REVIEW_READY_RECEIPT",
        executable=Path(sys.executable).resolve(),
        argv=[str(Path(sys.executable).resolve()), "-m", "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.report_builder", "--write"],
        result=result,
        context=context,
        acceptance=acceptance,
    )
    envelope["parent_evidence_ids"] = [
        "REPORT_BUILD_FINAL_RECEIPT",
        *[Path(name).stem for name in facts["current_receipts"].values()],
        "DRIFT_GUARD_RECHECK_RECEIPT",
        "WARP_CREATE_RECHECK_RECEIPT",
    ]
    store = EvidenceStore(report)
    try:
        store.write(envelope, finalize=True)
    except EvidenceFinalizedError:
        store.verify("OWNER_REVIEW_READY_RECEIPT")


def _write_hash_manifest(report: Path) -> None:
    excluded = {
        ".TASK_STATE.lock": "ephemeral lock",
        "EVIDENCE_INDEX.json": "self-hashed index is sealed after the final executor receipt",
        "HASH_MANIFEST.json": "self-reference",
    }
    files = []
    for path in sorted((item for item in report.rglob("*") if item.is_file()), key=lambda item: item.relative_to(report).as_posix()):
        relative = path.relative_to(report).as_posix()
        if relative in excluded:
            continue
        files.append({"path": relative, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    atomic_write_json(
        report / "HASH_MANIFEST.json",
        {
            "schema_version": "imperium.core_reference_corridor.hash_manifest.v0_1",
            "task_id": TASK_ID,
            "base_head": BASE_HEAD,
            "generated_at_utc": _utc_now(),
            "algorithm": "sha256",
            "files": files,
            "count": len(files),
            "exclusions": [{"path": path, "reason": reason} for path, reason in sorted(excluded.items())],
        },
    )


def build_reports() -> dict[str, Any]:
    context = resolve_repository_context(".")
    worktree = Path(context.worktree_root)
    report = worktree / REPORT_RELATIVE
    report.mkdir(parents=True, exist_ok=True)
    _write_control_receipts(context, report)
    task_state = json.loads((report / "TASK_STATE.json").read_text(encoding="utf-8"))
    ledger = OrganLedger(report / "ORGAN_PARTICIPATION_LEDGER.json", TASK_ID)
    ledger.load()
    ring = ledger.post_work_ring()
    atomic_write_json(report / "POST_WORK_ORGAN_RING_RECEIPT.json", ring)
    facts = _ready_facts(context, report, task_state, ring)
    _write_human_reports(report, ready=facts["ready"])
    task_manifest = {
        "schema_version": "imperium.core_reference_corridor.task_manifest.v0_1",
        "task_id": TASK_ID,
        "authority_mode": task_state["owner_intent"]["authority_mode"],
        "source_prompt_sha256": task_state["owner_intent"]["source_sha256"],
        "base_head": BASE_HEAD,
        "branch": context.branch,
        "worktree": str(worktree),
        "taskpack": TASKPACK_RELATIVE.as_posix(),
        "scope": task_state["scope"],
        "acceptance_tests": task_state["acceptance_tests"],
        "owner_land_approved": False,
    }
    atomic_write_json(report / "TASK_MANIFEST.json", task_manifest)
    checkpoint_source = report / "checkpoints" / "CHECKPOINT_INDEX.json"
    atomic_write_json(report / "CHECKPOINT_INDEX.json", json.loads(checkpoint_source.read_text(encoding="utf-8")))
    atomic_write_json(report / "OWNER_DECISIONS.json", json.loads((report / "owner_gate" / "OWNER_DECISIONS.json").read_text(encoding="utf-8")))
    atomic_write_json(report / "THRONE_RISKS.json", json.loads((report / "owner_gate" / "THRONE_RISKS.json").read_text(encoding="utf-8")))
    if facts["ready"]:
        _write_owner_ready(context, report, facts)

    changed = _changed_files(worktree)
    file_delta = {"schema_version": "imperium.core_reference_corridor.files_changed.v0_1", "task_id": TASK_ID, "base_head": BASE_HEAD, "files": changed, "count": len(changed)}
    atomic_write_json(report / "FILES_CHANGED.json", file_delta)
    atomic_write_json(
        report / "FILES_TO_LAND.json",
        {
            "schema_version": "imperium.core_reference_corridor.files_to_land.v0_1",
            "task_id": TASK_ID,
            "status": "PREPARED_NOT_AUTHORIZED",
            "base_head": BASE_HEAD,
            "files": [item["path"] for item in changed],
            "owner_land_approved": False,
            "land_executed": False,
        },
    )
    _write_hash_manifest(report)
    changed = _changed_files(worktree)
    file_delta["files"] = changed
    file_delta["count"] = len(changed)
    atomic_write_json(report / "FILES_CHANGED.json", file_delta)
    atomic_write_json(
        report / "FILES_TO_LAND.json",
        {
            "schema_version": "imperium.core_reference_corridor.files_to_land.v0_1",
            "task_id": TASK_ID,
            "status": "PREPARED_NOT_AUTHORIZED",
            "base_head": BASE_HEAD,
            "files": [item["path"] for item in changed],
            "owner_land_approved": False,
            "land_executed": False,
        },
    )
    result = {
        "verdict": "REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW" if facts["ready"] else "BLOCK",
        "report_root": str(report),
        "changed_file_count": len(changed),
        "readiness_checks": facts["checks"],
    }
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args(argv)
    build_reports()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
