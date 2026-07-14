"""Independent read-only Phase 7 disk auditor.

This module intentionally does not import phase7_claim_reconciliation. It
recomputes the decisive truth from disk, registry bytes, Git and UI projection.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from .pinned_tools import git_argv
from .root_resolver import resolve_repository_context
from .ui_contract import validate_ui_contract
from .ui_snapshot import build_ui_snapshot

BASE_HEAD = "281c3a7c8463de7fb64473929fe0ed975f99f595"
PASS_WITH_DEBT = "REFERENCE_CORRIDOR_PASS_WITH_DEBT"
GREAT_NINE = (
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "DOCTRINARIUM",
    "MECHANICUS",
    "INQUISITION",
    "CUSTODES",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "OFFICIO_AGENTIS",
)
THRONE = "THRONE"
REQUIRED_DEBT_IDS = {
    "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
    "ACTUAL_ORGANS_NOT_CURRENTLY_REVALIDATED",
    "LIVE_UI_NONBLOCKING_ACTION_DEFERRED",
    "LEGACY_PRIVATE_RUST_SOURCE_DEBT",
    "PARTIAL_CHECKPOINT_RESTORE_NOT_IMPLEMENTED",
    "SCAFFOLD_EXTENSIONS_NOT_OPERATIONAL",
    "ADMINISTRATUM_MINIMAL_LEDGER_ADAPTER",
    "OWNER_ACCEPTANCE_AND_LAND_PENDING",
    "REFERENCE_CORRIDOR_SCOPE_ONLY",
}
PHASE_EXPECTED = {
    "ORGAN_VERDICT_TRUTH.json": {"ORGAN_TRUTH_HARDENING_PASS"},
    "NEGATIVE_PROOF_TRUTH.json": {
        "NEGATIVE_PROOF_HARDENING_PASS",
        "NEGATIVE_PROOF_HARDENING_PASS_PROVEN",
    },
    "PHASE_3_VALIDATION_RECEIPT.json": {"LEGACY_MUTATION_SURFACE_CLOSED"},
    "PHASE_4_CHECKPOINT.json": {"RUST_PYTHON_BRIDGE_HARDENING_PASS"},
    "REAL_DIFF_RECEIPT.json": {"REAL_DIFF_REVIEW_PROVEN"},
    "LIVE_UI_ACTION_RECEIPT.json": {"LIVE_UI_CORRIDOR_PROVEN"},
}


class DiskAuditError(RuntimeError):
    """Independent disk truth did not support the claim."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiskAuditError(f"JSON_UNAVAILABLE:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise DiskAuditError(f"JSON_NOT_OBJECT:{path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_registry_digest(value: Mapping[str, Any]) -> str:
    clone = copy.deepcopy(dict(value))
    clone.pop("registry_digest", None)
    payload = json.dumps(
        clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        git_argv("-C", str(root), *arguments),
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        raise DiskAuditError(
            f"GIT_FAILED:{' '.join(arguments)}:"
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout.strip()


def extract_verdict(value: Mapping[str, Any]) -> str:
    for key in ("PHASE_VERDICT", "phase_verdict", "verdict"):
        item = value.get(key)
        if isinstance(item, str) and item:
            return item
    return "NOT_PROVEN"


def claim_status_errors(status: Mapping[str, Any], current_head: str) -> list[str]:
    errors: list[str] = []
    if status.get("authority") != "PHASE7_CURRENT_CLAIM_AUTHORITY":
        errors.append("CLAIM_AUTHORITY_INVALID")
    if status.get("implementation_head") != current_head:
        errors.append("CLAIM_HEAD_MISMATCH")
    if status.get("campaign_verdict") != PASS_WITH_DEBT:
        errors.append("CAMPAIGN_VERDICT_NOT_PASS_WITH_DEBT")
    if status.get("organ_ring_verdict") != "NOT_PROVEN":
        errors.append("ORGAN_RING_OVERCLAIM")
    organs = status.get("organs", {})
    if not isinstance(organs, dict) or set(organs) != {*GREAT_NINE, THRONE}:
        errors.append("ORGAN_SET_INVALID")
    else:
        for organ_id, row in organs.items():
            if not isinstance(row, dict):
                errors.append(f"ORGAN_ROW_INVALID:{organ_id}")
                continue
            if row.get("verdict") != "NOT_PROVEN":
                errors.append(f"ORGAN_CURRENT_OVERCLAIM:{organ_id}")
            if row.get("claim_state") != "HISTORICAL_NOT_PROMOTED":
                errors.append(f"ORGAN_HISTORY_BOUNDARY_MISSING:{organ_id}")
    debts = status.get("debts", [])
    debt_ids = {
        row.get("debt_id")
        for row in debts
        if isinstance(row, dict) and isinstance(row.get("debt_id"), str)
    }
    missing = sorted(REQUIRED_DEBT_IDS - debt_ids)
    if missing:
        errors.append("REQUIRED_DEBTS_MISSING:" + ",".join(missing))
    boundary = status.get("scope_boundary", {})
    if (
        not isinstance(boundary, dict)
        or boundary.get("reference_corridor_only") is not True
        or boundary.get("core_v1_complete") is not False
        or boundary.get("all_organs_operational") is not False
        or boundary.get("land_authorized") is not False
        or boundary.get("master_mutated") is not False
    ):
        errors.append("SCOPE_BOUNDARY_INVALID")
    superseded = status.get("superseded_claims", [])
    superseded_paths = {
        Path(str(row.get("path", ""))).name
        for row in superseded
        if isinstance(row, dict)
    }
    for required in (
        "OWNER_RESULT.md",
        "OWNER_REVIEW_READY_RECEIPT.json",
        "ORGAN_PARTICIPATION_LEDGER.json",
    ):
        if required not in superseded_paths:
            errors.append(f"SUPERSESSION_MISSING:{required}")
    return errors


def self_test() -> dict[str, Any]:
    organs = {
        organ_id: {
            "verdict": "NOT_PROVEN",
            "claim_state": "HISTORICAL_NOT_PROMOTED",
        }
        for organ_id in [*GREAT_NINE, THRONE]
    }
    status = {
        "authority": "PHASE7_CURRENT_CLAIM_AUTHORITY",
        "implementation_head": "a" * 40,
        "campaign_verdict": PASS_WITH_DEBT,
        "organ_ring_verdict": "NOT_PROVEN",
        "organs": organs,
        "debts": [{"debt_id": item} for item in sorted(REQUIRED_DEBT_IDS)],
        "scope_boundary": {
            "reference_corridor_only": True,
            "core_v1_complete": False,
            "all_organs_operational": False,
            "land_authorized": False,
            "master_mutated": False,
        },
        "superseded_claims": [
            {"path": "OWNER_RESULT.md"},
            {"path": "OWNER_REVIEW_READY_RECEIPT.json"},
            {"path": "ORGAN_PARTICIPATION_LEDGER.json"},
        ],
    }
    if claim_status_errors(status, "a" * 40):
        raise AssertionError("valid status rejected")

    mutations: list[tuple[str, dict[str, Any]]] = []
    promoted = copy.deepcopy(status)
    promoted["organs"]["MECHANICUS"]["verdict"] = "PASS_PROVEN"
    mutations.append(("organ_promotion", promoted))
    no_debt = copy.deepcopy(status)
    no_debt["debts"] = [
        row
        for row in no_debt["debts"]
        if row["debt_id"] != "LIVE_UI_NONBLOCKING_ACTION_DEFERRED"
    ]
    mutations.append(("debt_removal", no_debt))
    core_complete = copy.deepcopy(status)
    core_complete["scope_boundary"]["core_v1_complete"] = True
    mutations.append(("core_v1_overclaim", core_complete))
    no_supersession = copy.deepcopy(status)
    no_supersession["superseded_claims"] = []
    mutations.append(("supersession_removal", no_supersession))

    detected: list[str] = []
    for name, mutated in mutations:
        if not claim_status_errors(mutated, "a" * 40):
            raise AssertionError(f"mutation not detected: {name}")
        detected.append(name)

    registry = {"schema_version": "x", "capabilities": []}
    registry["registry_digest"] = canonical_registry_digest(registry)
    tampered = copy.deepcopy(registry)
    tampered["capabilities"].append({"capability_id": "ROGUE"})
    if canonical_registry_digest(tampered) == tampered["registry_digest"]:
        raise AssertionError("registry digest mutation not detected")
    detected.append("registry_digest_tamper")

    return {
        "verdict": "MUTATIONS_DETECTED",
        "detected": detected,
        "count": len(detected),
    }


def audit(
    *,
    repo: Path,
    reality: Path,
    corridor_report: Path,
    hardening_report: Path,
    claim_status_path: Path,
    output_path: Path,
    mode: str,
) -> dict[str, Any]:
    context = resolve_repository_context(repo)
    current_head = git(repo, "rev-parse", "HEAD").lower()
    tracked_status = git(
        repo, "status", "--porcelain=v1", "--untracked-files=no"
    ).splitlines()
    reality_head = git(reality, "rev-parse", "HEAD").lower()
    reality_status = git(reality, "status", "--porcelain=v1").splitlines()

    errors: list[str] = []
    if Path(context.worktree_root) != repo.resolve():
        errors.append("WORKTREE_CONTEXT_MISMATCH")
    if Path(context.reality_root) != reality.resolve():
        errors.append("REALITY_CONTEXT_MISMATCH")
    if reality_head != BASE_HEAD or reality_status:
        errors.append("REALITY_NOT_CLEAN_BASE")
    if mode == "final" and tracked_status:
        errors.append("TRACKED_WORKTREE_DIRTY")

    phase_receipts: list[dict[str, Any]] = []
    for filename, expected in PHASE_EXPECTED.items():
        path = hardening_report / filename
        row = {
            "path": str(path),
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
            "observed_verdict": "NOT_PROVEN",
            "verdict": "NOT_PROVEN",
        }
        if not path.is_file():
            errors.append(f"PHASE_RECEIPT_MISSING:{filename}")
        else:
            value = load_json(path)
            observed = extract_verdict(value)
            row["observed_verdict"] = observed
            row["verdict"] = "PASS_PROVEN" if observed in expected else "BLOCK"
            if observed not in expected:
                errors.append(f"PHASE_VERDICT_MISMATCH:{filename}:{observed}")
        phase_receipts.append(row)

    registry_path = corridor_report / "CAPABILITY_REGISTRY.json"
    registry = load_json(registry_path)
    if registry.get("default_policy") != "DENY":
        errors.append("REGISTRY_DEFAULT_DENY_MISSING")
    if registry.get("registry_digest") != canonical_registry_digest(registry):
        errors.append("REGISTRY_DIGEST_MISMATCH")
    capability_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for capability in registry.get("capabilities", []):
        if not isinstance(capability, dict):
            errors.append("CAPABILITY_ROW_INVALID")
            continue
        capability_id = capability.get("capability_id")
        if not isinstance(capability_id, str) or capability_id in seen:
            errors.append(f"CAPABILITY_ID_INVALID:{capability_id}")
            continue
        seen.add(capability_id)
        row = {
            "capability_id": capability_id,
            "admission_state": capability.get("admission_state"),
            "adapter_match": None,
            "executable_match": None,
        }
        if capability.get("admission_state") == "ACTIVE":
            adapter = Path(str(capability.get("adapter_path", "")))
            executable = Path(str(capability.get("executable_path", "")))
            row["adapter_match"] = (
                adapter.is_file()
                and sha256_file(adapter) == capability.get("adapter_sha256")
            )
            row["executable_match"] = (
                executable.is_file()
                and sha256_file(executable)
                == capability.get("executable_sha256")
            )
            if not row["adapter_match"]:
                errors.append(f"ADAPTER_IDENTITY_MISMATCH:{capability_id}")
            if not row["executable_match"]:
                errors.append(f"EXECUTABLE_IDENTITY_MISMATCH:{capability_id}")
        capability_rows.append(row)

    status = load_json(claim_status_path)
    errors.extend(claim_status_errors(status, current_head))

    snapshot = build_ui_snapshot(context, corridor_report)
    ui_errors = validate_ui_contract(snapshot, registry)
    errors.extend(f"UI_CONTRACT:{item}" for item in ui_errors)
    organ_panel = next(
        (panel for panel in snapshot.get("panels", []) if panel.get("id") == "great_nine_throne"),
        None,
    )
    if not isinstance(organ_panel, dict) or organ_panel.get("status") != "NOT_PROVEN":
        errors.append("UI_ORGAN_PANEL_OVERCLAIM")
    elif len(organ_panel.get("cards", [])) != 10:
        errors.append("UI_ORGAN_CARD_COUNT_INVALID")
    else:
        for card in organ_panel["cards"]:
            fields = {
                field.get("label"): field.get("value")
                for field in card.get("fields", [])
                if isinstance(field, dict)
            }
            if fields.get("verdict") != "NOT_PROVEN":
                errors.append(f"UI_ORGAN_CARD_OVERCLAIM:{card.get('id')}")

    report_gaps = (corridor_report / "KNOWN_GAPS.md").read_text(encoding="utf-8")
    hardening_gaps = (hardening_report / "KNOWN_GAPS.md").read_text(encoding="utf-8")
    for debt_id in REQUIRED_DEBT_IDS:
        if debt_id not in report_gaps and debt_id not in hardening_gaps:
            errors.append(f"KNOWN_GAP_NOT_DISCLOSED:{debt_id}")

    owner_result = (corridor_report / "OWNER_RESULT.md").read_text(encoding="utf-8")
    if "REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW" not in owner_result:
        errors.append("HISTORICAL_OWNER_RESULT_UNEXPECTEDLY_REWRITTEN")

    mutation_result = self_test()
    verdict = PASS_WITH_DEBT if not errors else "REFERENCE_CORRIDOR_BLOCKED"

    result = {
        "schema_version": "imperium.phase7.independent_disk_audit.v1",
        "generated_at_utc": utc_now(),
        "mode": mode,
        "verdict": verdict,
        "implementation_head": current_head,
        "tracked_status": tracked_status,
        "reality_head": reality_head,
        "reality_status": reality_status,
        "phase_receipts": phase_receipts,
        "capability_registry": {
            "path": str(registry_path),
            "sha256": sha256_file(registry_path),
            "digest": registry.get("registry_digest"),
            "capabilities": capability_rows,
        },
        "claim_status_path": str(claim_status_path),
        "claim_status_sha256": sha256_file(claim_status_path),
        "ui_contract_errors": ui_errors,
        "ui_organ_panel_status": (
            organ_panel.get("status") if isinstance(organ_panel, dict) else "MISSING"
        ),
        "mutation_tests": mutation_result,
        "errors": errors,
        "reality_unchanged": reality_head == BASE_HEAD and not reality_status,
        "land_authorized": False,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    output_path.with_suffix(".md").write_text(
        "# Phase 7 — Independent Disk Audit\n\n"
        f"Verdict: `{verdict}`\n\n"
        f"- Implementation HEAD: `{current_head}`\n"
        f"- Phase receipts: `{len(phase_receipts)}`\n"
        f"- Mutation tests detected: `{mutation_result['count']}`\n"
        f"- UI organ panel: `{result['ui_organ_panel_status']}`\n"
        f"- Reality unchanged: `{result['reality_unchanged']}`\n"
        f"- Errors: `{len(errors)}`\n"
        f"- Land authorized: `False`\n",
        encoding="utf-8",
        newline="\n",
    )
    if errors:
        raise DiskAuditError("INDEPENDENT_DISK_AUDIT_BLOCKED: " + ", ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--reality")
    parser.add_argument("--corridor-report")
    parser.add_argument("--hardening-report")
    parser.add_argument("--claim-status")
    parser.add_argument("--output")
    parser.add_argument("--mode", choices=("provisional", "final"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, sort_keys=True))
        return 0

    required = (
        args.repo,
        args.reality,
        args.corridor_report,
        args.hardening_report,
        args.claim_status,
        args.output,
        args.mode,
    )
    if any(item is None for item in required):
        raise RuntimeError("all audit arguments are required")

    result = audit(
        repo=Path(args.repo).resolve(),
        reality=Path(args.reality).resolve(),
        corridor_report=Path(args.corridor_report).resolve(),
        hardening_report=Path(args.hardening_report).resolve(),
        claim_status_path=Path(args.claim_status).resolve(),
        output_path=Path(args.output).resolve(),
        mode=str(args.mode),
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "implementation_head": result["implementation_head"],
                "output": str(Path(args.output).resolve()),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
