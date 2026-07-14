"""Phase 7 claim reconciliation for the Core Reference Corridor.

This module does not upgrade historical claims. It derives a current claim
authority from primary receipts, current bytes and explicit debt boundaries.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable, Mapping

from .organ_ledger import GREAT_NINE, THRONE
from .pinned_tools import git_argv
from .registry import CapabilityRegistry
from .root_resolver import resolve_repository_context
from .ui_contract import validate_ui_contract
from .ui_snapshot import build_ui_snapshot

BASE_HEAD = "281c3a7c8463de7fb64473929fe0ed975f99f595"
TASK_ID = "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001"
WARP_ID = "WARP-CORE-REFERENCE-0001"
PASS_WITH_DEBT = "REFERENCE_CORRIDOR_PASS_WITH_DEBT"
PASS_PROVEN = "REFERENCE_CORRIDOR_PASS_PROVEN"
NOT_READY = "REFERENCE_CORRIDOR_NOT_READY"
BLOCKED = "REFERENCE_CORRIDOR_BLOCKED"

PHASE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "phase": 1,
        "path": "ORGAN_VERDICT_TRUTH.json",
        "expected": {"ORGAN_TRUTH_HARDENING_PASS"},
    },
    {
        "phase": 2,
        "path": "NEGATIVE_PROOF_TRUTH.json",
        "expected": {
            "NEGATIVE_PROOF_HARDENING_PASS",
            "NEGATIVE_PROOF_HARDENING_PASS_PROVEN",
        },
    },
    {
        "phase": 3,
        "path": "PHASE_3_VALIDATION_RECEIPT.json",
        "expected": {"LEGACY_MUTATION_SURFACE_CLOSED"},
    },
    {
        "phase": 4,
        "path": "PHASE_4_CHECKPOINT.json",
        "expected": {"RUST_PYTHON_BRIDGE_HARDENING_PASS"},
    },
    {
        "phase": 5,
        "path": "REAL_DIFF_RECEIPT.json",
        "expected": {"REAL_DIFF_REVIEW_PROVEN"},
    },
    {
        "phase": 6,
        "path": "LIVE_UI_ACTION_RECEIPT.json",
        "expected": {"LIVE_UI_CORRIDOR_PROVEN"},
    },
)

REQUIRED_DEBTS: tuple[dict[str, str], ...] = (
    {
        "debt_id": "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
        "severity": "HIGH_FOR_LAND",
        "blocking_scope": "LAND_ONLY",
    },
    {
        "debt_id": "ACTUAL_ORGANS_NOT_CURRENTLY_REVALIDATED",
        "severity": "HIGH_FOR_ORGAN_MATURITY_CLAIMS",
        "blocking_scope": "ORGAN_OPERATIONAL_CLAIMS",
    },
    {
        "debt_id": "LIVE_UI_NONBLOCKING_ACTION_DEFERRED",
        "severity": "UX_DEBT",
        "blocking_scope": "NON_BLOCKING_FOR_PHASE7",
    },
    {
        "debt_id": "LEGACY_PRIVATE_RUST_SOURCE_DEBT",
        "severity": "LOW",
        "blocking_scope": "NON_BLOCKING",
    },
    {
        "debt_id": "PARTIAL_CHECKPOINT_RESTORE_NOT_IMPLEMENTED",
        "severity": "MEDIUM",
        "blocking_scope": "PARTIAL_RESTORE",
    },
    {
        "debt_id": "SCAFFOLD_EXTENSIONS_NOT_OPERATIONAL",
        "severity": "EXPECTED_SCOPE_BOUNDARY",
        "blocking_scope": "EXTENSION_CLAIMS",
    },
    {
        "debt_id": "ADMINISTRATUM_MINIMAL_LEDGER_ADAPTER",
        "severity": "EXPECTED_SCOPE_BOUNDARY",
        "blocking_scope": "FULL_ADMINISTRATUM_CLAIMS",
    },
    {
        "debt_id": "OWNER_ACCEPTANCE_AND_LAND_PENDING",
        "severity": "OWNER_GATE",
        "blocking_scope": "LAND",
    },
    {
        "debt_id": "REFERENCE_CORRIDOR_SCOPE_ONLY",
        "severity": "CLAIM_BOUNDARY",
        "blocking_scope": "CORE_V1_COMPLETENESS_CLAIMS",
    },
)


class Phase7Error(RuntimeError):
    """A current truth claim cannot be proved."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Phase7Error(f"JSON_UNAVAILABLE: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Phase7Error(f"JSON_NOT_OBJECT: {path}")
    return value


def atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    rendered = json.dumps(dict(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_git(root: Path, *arguments: str) -> str:
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
        raise Phase7Error(
            f"GIT_FAILED: {' '.join(arguments)}: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout.strip()


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        git_argv("-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant),
        shell=False,
        capture_output=True,
        timeout=30,
        check=False,
    )
    return completed.returncode == 0


def extract_verdict(value: Mapping[str, Any]) -> str:
    for key in ("PHASE_VERDICT", "phase_verdict", "verdict"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    return "NOT_PROVEN"


def measure_phases(repo: Path, hardening: Path, current_head: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in PHASE_SPECS:
        path = hardening / str(spec["path"])
        row: dict[str, Any] = {
            "phase": spec["phase"],
            "path": str(path),
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
            "expected_verdicts": sorted(spec["expected"]),
            "observed_verdict": "NOT_PROVEN",
            "verdict": "NOT_PROVEN",
            "errors": [],
        }
        if not path.is_file():
            row["errors"].append("RECEIPT_MISSING")
            rows.append(row)
            continue
        value = load_json(path)
        observed = extract_verdict(value)
        row["schema_version"] = value.get("schema_version")
        row["observed_verdict"] = observed
        if observed not in spec["expected"]:
            row["errors"].append("PHASE_VERDICT_MISMATCH")
            row["verdict"] = "BLOCK"
        else:
            row["verdict"] = "PASS_PROVEN"

        implementation_head = value.get("implementation_head")
        if isinstance(implementation_head, str) and len(implementation_head) == 40:
            row["implementation_head"] = implementation_head
            row["implementation_head_is_ancestor"] = is_ancestor(
                repo, implementation_head, current_head
            )
            if not row["implementation_head_is_ancestor"]:
                row["errors"].append("IMPLEMENTATION_HEAD_NOT_ANCESTOR")
                row["verdict"] = "BLOCK"
        rows.append(row)
    return rows


def latest_organ_rows(ledger: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in ledger.get("records", []):
        if isinstance(row, dict) and isinstance(row.get("organ_id"), str):
            latest[row["organ_id"]] = row
    return latest


def current_organ_status(ledger: Mapping[str, Any]) -> dict[str, Any]:
    latest = latest_organ_rows(ledger)
    result: dict[str, Any] = {}
    for organ_id in [*GREAT_NINE, THRONE]:
        historical = latest.get(organ_id, {})
        result[organ_id] = {
            "phase": "PHASE7_CURRENT_TRUTH",
            "verdict": "NOT_PROVEN",
            "confidence": 0,
            "evidence_refs": [],
            "claim_state": "HISTORICAL_NOT_PROMOTED",
            "historical_phase": historical.get("phase", "NONE"),
            "historical_verdict": historical.get("verdict", "NONE"),
            "historical_confidence": historical.get("confidence", 0),
            "reason": (
                "Phase 1 proves the verdict mechanism; no current organ-specific "
                "operational evidence was supplied for promotion."
            ),
        }
    return result


def phase_map(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        str(row["phase"]): {
            "verdict": row["verdict"],
            "observed_verdict": row["observed_verdict"],
            "receipt_path": row["path"],
            "receipt_sha256": row["sha256"],
        }
        for row in rows
    }


def calculate_campaign_verdict(
    phase_rows: Iterable[Mapping[str, Any]],
    *,
    blockers: Iterable[str],
    debts: Iterable[Mapping[str, Any]],
) -> str:
    blockers = list(blockers)
    rows = list(phase_rows)
    if blockers or any(row.get("verdict") == "BLOCK" for row in rows):
        return BLOCKED
    if not rows or any(row.get("verdict") != "PASS_PROVEN" for row in rows):
        return NOT_READY
    return PASS_WITH_DEBT if list(debts) else PASS_PROVEN


def render_matrix_markdown(matrix: Mapping[str, Any]) -> str:
    lines = [
        "# Phase 7 — Claim / Evidence Matrix",
        "",
        f"Current verdict: `{matrix['campaign_verdict']}`",
        "",
        "| Claim | Classification | Measured truth |",
        "|---|---|---|",
    ]
    for row in matrix["claims"]:
        lines.append(
            f"| `{row['claim_id']}` | `{row['classification']}` | "
            f"{row['measured_truth']} |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- This verdict covers the Reference Corridor campaign only.",
            "- It does not claim Core v1 completion.",
            "- Historical organ PASS rows are not current operational proof.",
            "- No land, merge or master push is authorized.",
            "",
        ]
    )
    return "\n".join(lines)


def reconcile(
    *,
    repo: Path,
    reality: Path,
    corridor_report: Path,
    hardening_report: Path,
    output_root: Path,
    mode: str,
) -> dict[str, Any]:
    context = resolve_repository_context(repo)
    if Path(context.worktree_root) != repo.resolve():
        raise Phase7Error("WORKTREE_CONTEXT_MISMATCH")
    if Path(context.reality_root) != reality.resolve():
        raise Phase7Error("REALITY_CONTEXT_MISMATCH")

    current_head = run_git(repo, "rev-parse", "HEAD").lower()
    branch = run_git(repo, "branch", "--show-current")
    tracked_status = run_git(
        repo, "status", "--porcelain=v1", "--untracked-files=no"
    ).splitlines()
    reality_head = run_git(reality, "rev-parse", "HEAD").lower()
    reality_status = run_git(reality, "status", "--porcelain=v1").splitlines()

    blockers: list[str] = []
    if reality_head != BASE_HEAD or reality_status:
        blockers.append("REALITY_NOT_CLEAN_AUTHORITATIVE_BASE")
    if mode == "final" and tracked_status:
        blockers.append("IMPLEMENTATION_TRACKED_WORKTREE_DIRTY")

    phase_rows = measure_phases(repo, hardening_report, current_head)
    registry_path = corridor_report / "CAPABILITY_REGISTRY.json"
    registry = CapabilityRegistry(registry_path).load(verify_files=True)
    ledger = load_json(corridor_report / "ORGAN_PARTICIPATION_LEDGER.json")
    organs = current_organ_status(ledger)

    runtime_transition = load_json(
        hardening_report / "PHASE6_REGISTRY_RUNTIME_TRANSITION_RECEIPT.json"
    )
    live_receipt = load_json(hardening_report / "LIVE_UI_ACTION_RECEIPT.json")
    if runtime_transition.get("verdict") != "EXACT_RUNTIME_REGISTRY_TRANSITION_PROVEN":
        blockers.append("PHASE6_RUNTIME_TRANSITION_NOT_PROVEN")
    if runtime_transition.get("new_evidence_id") != live_receipt.get("evidence_id"):
        blockers.append("PHASE6_EVIDENCE_TRANSITION_MISMATCH")

    debts = [dict(item) for item in REQUIRED_DEBTS]
    campaign_verdict = calculate_campaign_verdict(
        phase_rows, blockers=blockers, debts=debts
    )

    superseded = [
        {
            "path": str(corridor_report / "OWNER_RESULT.md"),
            "claim": "REFERENCE_CORRIDOR_READY_FOR_OWNER_REVIEW",
            "classification": "HISTORICAL_SUPERSEDED",
            "reason": "Predates truth-hardening Phases 1–7.",
        },
        {
            "path": str(corridor_report / "OWNER_REVIEW_READY_RECEIPT.json"),
            "claim": "OWNER_REVIEW_READY",
            "classification": "HISTORICAL_SUPERSEDED",
            "reason": "Preserved as history; not current Phase 7 authority.",
        },
        {
            "path": str(corridor_report / "ORGAN_PARTICIPATION_LEDGER.json"),
            "claim": "HISTORICAL_POSTCHECK_PASS_PROVEN",
            "classification": "HISTORICAL_NOT_PROMOTED",
            "reason": "Current organ-specific operational evidence is absent.",
        },
    ]

    claim_status = {
        "schema_version": "imperium.phase7.current_claim_status.v1",
        "authority": "PHASE7_CURRENT_CLAIM_AUTHORITY",
        "generated_at_utc": utc_now(),
        "mode": mode,
        "task_id": TASK_ID,
        "warp_id": WARP_ID,
        "base_head": BASE_HEAD,
        "implementation_head": current_head,
        "branch": branch,
        "campaign_verdict": campaign_verdict,
        "phase_status": phase_map(phase_rows),
        "organ_ring_verdict": "NOT_PROVEN",
        "organs": organs,
        "debts": debts,
        "blockers": blockers,
        "superseded_claims": superseded,
        "scope_boundary": {
            "reference_corridor_only": True,
            "core_v1_complete": False,
            "all_organs_operational": False,
            "owner_acceptance_inferred": False,
            "land_authorized": False,
            "master_mutated": False,
        },
    }

    claims: list[dict[str, Any]] = []
    for row in phase_rows:
        claims.append(
            {
                "claim_id": f"PHASE_{row['phase']}",
                "classification": row["verdict"],
                "measured_truth": (
                    f"{row['observed_verdict']} from {Path(row['path']).name}; "
                    f"sha256={row['sha256']}"
                ),
            }
        )
    claims.extend(
        [
            {
                "claim_id": "GREAT_NINE_AND_THRONE_OPERATIONAL",
                "classification": "NOT_PROVEN",
                "measured_truth": (
                    "Historical ledger rows exist, but current organ-specific "
                    "operational evidence was not supplied."
                ),
            },
            {
                "claim_id": "LIVE_UI_NONBLOCKING",
                "classification": "PASS_WITH_DEBT",
                "measured_truth": (
                    "Execution and evidence are proven; synchronous UI responsiveness "
                    "is deferred accepted debt."
                ),
            },
            {
                "claim_id": "CORE_V1_COMPLETE",
                "classification": "NOT_CLAIMED",
                "measured_truth": "Phase 7 covers only the Reference Corridor campaign.",
            },
            {
                "claim_id": "LAND_AUTHORIZED",
                "classification": "NOT_PROVEN",
                "measured_truth": "Owner land decision has not been recorded.",
            },
        ]
    )

    matrix = {
        "schema_version": "imperium.phase7.claim_evidence_matrix.v1",
        "generated_at_utc": utc_now(),
        "implementation_head": current_head,
        "campaign_verdict": campaign_verdict,
        "claims": claims,
        "superseded_claims": superseded,
        "debts": debts,
        "blockers": blockers,
    }
    issue_registry = {
        "schema_version": "imperium.phase7.issue_registry.v1",
        "generated_at_utc": utc_now(),
        "implementation_head": current_head,
        "issues": debts,
        "blocking_issue_count": len(blockers),
        "campaign_verdict": campaign_verdict,
    }

    output_root.mkdir(parents=True, exist_ok=True)
    atomic_json(output_root / "CURRENT_CLAIM_STATUS.json", claim_status)
    atomic_json(output_root / "CLAIM_EVIDENCE_MATRIX.json", matrix)
    (output_root / "CLAIM_EVIDENCE_MATRIX.md").write_text(
        render_matrix_markdown(matrix), encoding="utf-8", newline="\n"
    )
    atomic_json(output_root / "ISSUE_REGISTRY.json", issue_registry)

    # Validate the actual UI projection. If output_root is the report root, the
    # newly written claim authority is consumed. Otherwise the UI must still
    # fail closed when no current authority exists.
    snapshot = build_ui_snapshot(context, corridor_report)
    ui_errors = validate_ui_contract(snapshot, registry)
    if ui_errors:
        blockers.extend(f"UI_CONTRACT:{error}" for error in ui_errors)

    organ_panel = next(
        (panel for panel in snapshot.get("panels", []) if panel.get("id") == "great_nine_throne"),
        None,
    )
    if not isinstance(organ_panel, dict) or organ_panel.get("status") != "NOT_PROVEN":
        blockers.append("UI_ORGAN_PANEL_NOT_FAIL_CLOSED")
    else:
        for card in organ_panel.get("cards", []):
            fields = {
                field.get("label"): field.get("value")
                for field in card.get("fields", [])
                if isinstance(field, dict)
            }
            if fields.get("verdict") != "NOT_PROVEN":
                blockers.append(f"UI_ORGAN_CARD_OVERCLAIM:{card.get('id')}")

    if blockers and campaign_verdict != BLOCKED:
        campaign_verdict = BLOCKED
        claim_status["campaign_verdict"] = campaign_verdict
        claim_status["blockers"] = blockers
        matrix["campaign_verdict"] = campaign_verdict
        matrix["blockers"] = blockers
        issue_registry["campaign_verdict"] = campaign_verdict
        issue_registry["blocking_issue_count"] = len(blockers)
        atomic_json(output_root / "CURRENT_CLAIM_STATUS.json", claim_status)
        atomic_json(output_root / "CLAIM_EVIDENCE_MATRIX.json", matrix)
        atomic_json(output_root / "ISSUE_REGISTRY.json", issue_registry)

    receipt = {
        "schema_version": "imperium.phase7.claim_reconciliation_receipt.v1",
        "phase": 7,
        "verdict": campaign_verdict,
        "generated_at_utc": utc_now(),
        "mode": mode,
        "task_id": TASK_ID,
        "warp_id": WARP_ID,
        "base_head": BASE_HEAD,
        "implementation_head": current_head,
        "branch": branch,
        "tracked_status": tracked_status,
        "reality_head": reality_head,
        "reality_status": reality_status,
        "phase_rows": phase_rows,
        "capability_registry": {
            "path": str(registry_path),
            "sha256": sha256_file(registry_path),
            "digest": registry.get("registry_digest"),
            "default_policy": registry.get("default_policy"),
        },
        "organ_ring_current_verdict": "NOT_PROVEN",
        "historical_organ_rows_promoted": False,
        "ui_contract_errors": ui_errors,
        "ui_organ_panel_status": organ_panel.get("status") if isinstance(organ_panel, dict) else "MISSING",
        "debt_count": len(debts),
        "blockers": blockers,
        "scope_boundary": claim_status["scope_boundary"],
        "artifacts": {
            "current_claim_status": str(output_root / "CURRENT_CLAIM_STATUS.json"),
            "claim_evidence_matrix": str(output_root / "CLAIM_EVIDENCE_MATRIX.json"),
            "issue_registry": str(output_root / "ISSUE_REGISTRY.json"),
        },
    }
    atomic_json(output_root / "PHASE7_CLAIM_RECONCILIATION_RECEIPT.json", receipt)
    (output_root / "PHASE7_CLAIM_RECONCILIATION_RECEIPT.md").write_text(
        "# Phase 7 — Claim Reconciliation\n\n"
        f"Verdict: `{campaign_verdict}`\n\n"
        f"- Implementation HEAD: `{current_head}`\n"
        f"- Reality unchanged: `{not reality_status and reality_head == BASE_HEAD}`\n"
        f"- Phases measured: `{len(phase_rows)}`\n"
        f"- Current organ ring: `NOT_PROVEN`\n"
        f"- Historical organ PASS promoted: `False`\n"
        f"- Debts: `{len(debts)}`\n"
        f"- Blockers: `{len(blockers)}`\n"
        f"- Land authorized: `False`\n",
        encoding="utf-8",
        newline="\n",
    )
    (output_root / "OWNER_RESULT_RECONCILED.md").write_text(
        "# Owner Result — Phase 7 Current Truth\n\n"
        f"Current verdict: `{campaign_verdict}`\n\n"
        "The Reference Corridor is ready for Owner audit and remediation with "
        "explicit debt. This is not a claim that Core v1 is complete or that "
        "all Great Nine organs and Throne are operationally mature.\n\n"
        "No land, merge or master push is authorized by this result.\n",
        encoding="utf-8",
        newline="\n",
    )

    if campaign_verdict == BLOCKED:
        raise Phase7Error("PHASE7_RECONCILIATION_BLOCKED: " + ", ".join(blockers))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--reality", required=True)
    parser.add_argument("--corridor-report", required=True)
    parser.add_argument("--hardening-report", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--mode", choices=("provisional", "final"), required=True)
    args = parser.parse_args()
    result = reconcile(
        repo=Path(args.repo).resolve(),
        reality=Path(args.reality).resolve(),
        corridor_report=Path(args.corridor_report).resolve(),
        hardening_report=Path(args.hardening_report).resolve(),
        output_root=Path(args.output_root).resolve(),
        mode=args.mode,
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "implementation_head": result["implementation_head"],
                "receipt": result["artifacts"]["current_claim_status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
