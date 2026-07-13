"""Evidence-derived Great Nine and Throne participation ledger."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .organ_verdict import (
    Verdict,
    VerdictContext,
    enforce_throne_guard,
    evaluate_organ,
)
from .registry import atomic_write_json


GREAT_NINE = [
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "DOCTRINARIUM",
    "MECHANICUS",
    "INQUISITION",
    "CUSTODES",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "OFFICIO_AGENTIS",
]
THRONE = "THRONE"
ALLOWED_VERDICTS = {item.value for item in Verdict} | {"NOT_APPLICABLE_PROVEN"}


CHECKS = {
    "ASTRONOMICON": ["taskpack_digest_admitted", "task_route_resolved"],
    "ADMINISTRATUM": ["task_state_addressable", "evidence_index_addressable"],
    "DOCTRINARIUM": ["forbidden_claims_carried", "canon_conflict_disclosed"],
    "MECHANICUS": ["single_registry_valid", "typed_executor_validated"],
    "INQUISITION": ["negative_matrix_localized", "master_unchanged"],
    "CUSTODES": ["great_nine_complete", "ledger_rows_schema_complete"],
    "STRATEGIUM": ["strategy_selected", "cost_time_pause_contract_present"],
    "SCHOLA_IMPERIALIS": ["known_gaps_captured", "learning_proposals_owner_gated"],
    "OFFICIO_AGENTIS": ["owner_language_ru", "final_response_contract_loaded"],
    "THRONE": ["great_nine_evidence_referenced", "owner_sovereignty_preserved", "land_not_executed"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _boundary(organ_id: str) -> str:
    if organ_id == THRONE:
        return "Analyzes evidence and risk; cannot accept the result or authorize land for the Owner."
    return "Deterministic contract checks only; no simulated cognition or autonomous authority."


def _claims_and_declared_refs(value: Any, organ_id: str) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    if isinstance(value, Mapping):
        raw_claims = value.get("claims", value)
        claims = {
            check_id: claim
            for check_id, claim in raw_claims.items()
            if check_id in CHECKS[organ_id] and isinstance(claim, Mapping)
        }
        refs = [
            str(claim["evidence_ref"])
            for claim in claims.values()
            if isinstance(claim.get("evidence_ref"), str)
        ]
        return claims, sorted(set(refs))
    if isinstance(value, list):
        return {}, sorted({str(item) for item in value if isinstance(item, str) and item})
    return {}, []


def _record(
    organ_id: str,
    phase: str,
    task_state: dict[str, Any],
    claims: Mapping[str, Mapping[str, Any]],
    declared_refs: list[str],
    context: VerdictContext,
    warnings: list[str],
    declared_not_proven: list[str],
    accepted_debt: list[str],
) -> dict[str, Any]:
    truth = evaluate_organ(
        organ_id,
        CHECKS[organ_id],
        claims,
        context,
        accepted_debt=accepted_debt,
    )
    if declared_not_proven:
        truth["not_proven"].extend(
            {"check_id": "declared_boundary", "reasons": [str(item)]}
            for item in declared_not_proven
        )
        if truth["verdict"] != Verdict.BLOCK.value:
            truth["verdict"] = Verdict.NOT_PROVEN.value
            truth["confidence"] = min(0.99, truth["confidence"])
    checks_executed = sorted(
        check_id
        for check_id, claim in claims.items()
        if isinstance(claim.get("validator_execution"), Mapping)
    )
    validator_runs = [
        dict(result["validator_execution"])
        for result in truth["check_results"]
        if isinstance(result.get("validator_execution"), Mapping)
    ]
    primary_run = validator_runs[0] if validator_runs else {}
    measured_checks = [
        dict(result["measured_check"])
        if isinstance(result.get("measured_check"), Mapping)
        else {
            "check_id": result["check_id"],
            "expected": None,
            "observed": None,
            "evidence_id": result.get("evidence_ref"),
            "verdict": result["verdict"],
        }
        for result in truth["check_results"]
    ]
    failed_checks = [
        result["check_id"]
        for result in truth["check_results"]
        if result["verdict"] == Verdict.BLOCK.value
    ]
    run_exit_codes = [run.get("exit_code") for run in validator_runs]
    record: dict[str, Any] = {
        "organ_id": organ_id,
        "phase": phase,
        "assigned_depth": task_state.get("organ_depth_plan", {}).get(organ_id, "STANDARD"),
        "input_refs": [task_state.get("task_id", ""), task_state.get("base_head", "")],
        "required_checks": CHECKS[organ_id],
        "checks_executed": checks_executed,
        "validator_id": primary_run.get("validator_id"),
        "validator_version": primary_run.get("validator_version"),
        "validator_executable_path": primary_run.get("validator_executable_path"),
        "validator_sha256": primary_run.get("validator_sha256"),
        "exact_argv": primary_run.get("exact_argv", []),
        "started_at_utc": primary_run.get("started_at_utc"),
        "finished_at_utc": primary_run.get("finished_at_utc"),
        "exit_code": (
            next((code for code in run_exit_codes if code not in {0, None}), 0)
            if run_exit_codes else None
        ),
        "validator_runs": validator_runs,
        "measured_checks": measured_checks,
        "failed_checks": failed_checks,
        "verdict": truth["verdict"],
        "confidence": truth["confidence"],
        "confidence_basis": truth["confidence_basis"],
        "check_results": truth["check_results"],
        "proven": truth["proven"],
        "evidence_refs": truth["evidence_refs"],
        "declared_evidence_refs": declared_refs,
        "warnings": [str(item) for item in warnings],
        "not_proven": truth["not_proven"],
        "accepted_debt": truth["accepted_debt"],
        "blocking_evidence": truth["blocking_evidence"],
        "boundary_statement": _boundary(organ_id),
        "timestamp_utc": utc_now(),
    }
    if organ_id == THRONE:
        record["risk_statement"] = {
            "evidence": truth["evidence_refs"],
            "causal_chain": [
                "Constitution names an older organ set",
                "runtime follows later explicit Owner canon",
                "land without supersession would preserve authority ambiguity",
            ],
            "affected_scope": ["governance", "organ routing", "future land"],
            "probability": "HIGH_UNTIL_SUPERSESSION",
            "severity": "HIGH",
            "expected_consequences": "Conflicting organ routes and false claims of conflict-free canon.",
        }
    return record


def _validate_record(item: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    required_fields = {
        "organ_id", "phase", "assigned_depth", "input_refs", "required_checks", "checks_executed",
        "validator_id", "validator_version", "validator_executable_path", "validator_sha256",
        "exact_argv", "started_at_utc", "finished_at_utc", "exit_code", "validator_runs",
        "measured_checks", "failed_checks",
        "verdict", "confidence", "confidence_basis", "check_results", "proven", "evidence_refs",
        "declared_evidence_refs", "warnings", "not_proven", "accepted_debt", "blocking_evidence",
        "boundary_statement", "timestamp_utc",
    }
    missing = sorted(required_fields - set(item))
    if missing:
        errors.append(f"record {index}: missing {','.join(missing)}")
        return errors
    organ_id = item.get("organ_id")
    if organ_id not in CHECKS:
        errors.append(f"record {index}: invalid organ")
        return errors
    verdict = item.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"record {index}: invalid verdict")
    confidence = item.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        errors.append(f"record {index}: invalid confidence")
    if verdict == Verdict.PASS_WITH_DEBT.value and (not item.get("accepted_debt") or confidence >= 1):
        errors.append(f"record {index}: debt verdict must list debt and confidence below 1")
    if verdict == Verdict.NOT_APPLICABLE_PROVEN.value:
        applicability = item.get("applicability_validation")
        if not isinstance(applicability, Mapping) or applicability.get("verdict") != Verdict.PASS_PROVEN.value:
            errors.append(f"record {index}: NOT_APPLICABLE_PROVEN lacks applicability validator proof")
    if confidence == 1.0 and (item.get("not_proven") or item.get("accepted_debt")):
        errors.append(f"record {index}: confidence 1.0 carries unresolved truth")
    results = item.get("check_results")
    if not isinstance(results, list):
        errors.append(f"record {index}: check_results is not a list")
        return errors
    result_ids = [result.get("check_id") for result in results if isinstance(result, Mapping)]
    if sorted(result_ids) != sorted(CHECKS[organ_id]):
        errors.append(f"record {index}: required check result set mismatch")
    if verdict == Verdict.PASS_PROVEN.value:
        if confidence != 1.0 or item.get("not_proven") or item.get("accepted_debt") or item.get("blocking_evidence"):
            errors.append(f"record {index}: PASS_PROVEN carries unresolved truth")
        for result in results:
            if not isinstance(result, Mapping) or result.get("verdict") != Verdict.PASS_PROVEN.value:
                errors.append(f"record {index}: PASS_PROVEN has non-pass check")
                break
            execution = result.get("validator_execution")
            if not result.get("evidence_ref") or not result.get("evidence_sha256") or not isinstance(execution, Mapping):
                errors.append(f"record {index}: PASS_PROVEN check lacks evidence/validator proof")
                break
            if execution.get("exit_code") != 0:
                errors.append(f"record {index}: PASS_PROVEN validator was not green")
                break
        if not item.get("validator_id") or not item.get("validator_version") or not item.get("validator_runs"):
            errors.append(f"record {index}: PASS_PROVEN has no organ-specific validator runs")
    return errors


def validate_ledger(
    ledger: dict[str, Any],
    *,
    require_phases: tuple[str, ...] = ("PREFLIGHT", "POSTCHECK"),
) -> list[str]:
    errors: list[str] = []
    records = ledger.get("records", [])
    if not isinstance(records, list):
        return ["records is not a list"]
    for phase in require_phases:
        ids = [item.get("organ_id") for item in records if isinstance(item, Mapping) and item.get("phase") == phase]
        for organ_id in [*GREAT_NINE, THRONE]:
            if ids.count(organ_id) != 1:
                errors.append(f"{phase}: participation count for {organ_id} is {ids.count(organ_id)}")
    for index, item in enumerate(records):
        if not isinstance(item, Mapping):
            errors.append(f"record {index}: not an object")
            continue
        errors.extend(_validate_record(item, index))
    for phase in require_phases:
        phase_records = [item for item in records if isinstance(item, Mapping) and item.get("phase") == phase]
        throne = next((item for item in phase_records if item.get("organ_id") == THRONE), None)
        critical_blocks = [
            (item.get("organ_id"), result.get("check_id"))
            for item in phase_records
            if item.get("organ_id") != THRONE
            for result in item.get("check_results", [])
            if isinstance(result, Mapping) and result.get("critical") is True and result.get("verdict") == Verdict.BLOCK.value
        ]
        if critical_blocks and throne and str(throne.get("verdict", "")).startswith("PASS"):
            errors.append(f"{phase}: Throne PASS over critical organ BLOCK {critical_blocks}")
        critical_unknowns = [
            (item.get("organ_id"), result.get("check_id"))
            for item in phase_records
            if item.get("organ_id") != THRONE
            for result in item.get("check_results", [])
            if isinstance(result, Mapping)
            and result.get("critical") is True
            and result.get("verdict") == Verdict.NOT_PROVEN.value
        ]
        if critical_unknowns and throne and throne.get("verdict") == Verdict.PASS_PROVEN.value:
            errors.append(f"{phase}: Throne PASS_PROVEN over critical organ NOT_PROVEN {critical_unknowns}")
    return errors


class OrganLedger:
    def __init__(
        self,
        path: Path | str,
        task_id: str,
        *,
        evidence_root: Path | str | None = None,
        validator_root: Path | str | None = None,
    ):
        self.path = Path(path).resolve()
        self.evidence_root = Path(evidence_root).resolve() if evidence_root is not None else None
        self.validator_root = Path(validator_root).resolve() if validator_root is not None else None
        self.data: dict[str, Any] = {
            "schema_version": "imperium.core_reference_corridor.organ_ledger.v0_2",
            "task_id": task_id,
            "operational_canon_source": "ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json",
            "great_nine": GREAT_NINE,
            "crown_organ": THRONE,
            "constitution_conflict": "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
            "records": [],
            "overall_verdict": Verdict.NOT_PROVEN.value,
        }

    def load(self) -> dict[str, Any]:
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def _context(self, task_state: dict[str, Any]) -> VerdictContext:
        warp = task_state.get("warp", {}) if isinstance(task_state.get("warp"), Mapping) else {}
        inferred_root = Path(str(warp.get("path", self.path.parent))).resolve()
        return VerdictContext(
            task_id=str(task_state.get("task_id", self.data.get("task_id", ""))),
            warp_id=str(warp.get("warp_id", task_state.get("warp_id", ""))),
            base_head=str(task_state.get("base_head", "")),
            evidence_root=self.evidence_root or inferred_root,
            validator_root=self.validator_root or inferred_root,
        )

    def record_phase(
        self,
        phase: str,
        task_state: dict[str, Any],
        evidence_by_organ: dict[str, Any],
        *,
        checks_by_organ: dict[str, bool] | None = None,
        warnings_by_organ: dict[str, list[str]] | None = None,
        not_proven_by_organ: dict[str, list[str]] | None = None,
        accepted_debt_by_organ: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        if phase not in {"PREFLIGHT", "POSTCHECK"}:
            raise ValueError("phase must be PREFLIGHT or POSTCHECK")
        del checks_by_organ  # legacy booleans are intentionally not accepted as proof
        warnings_by_organ = warnings_by_organ or {}
        not_proven_by_organ = not_proven_by_organ or {}
        accepted_debt_by_organ = accepted_debt_by_organ or {}
        context = self._context(task_state)
        self.data["schema_version"] = "imperium.core_reference_corridor.organ_ledger.v0_2"
        self.data["records"] = [item for item in self.data.get("records", []) if item.get("phase") != phase]
        phase_records: list[dict[str, Any]] = []
        for organ_id in GREAT_NINE:
            claims, refs = _claims_and_declared_refs(evidence_by_organ.get(organ_id), organ_id)
            phase_records.append(
                _record(
                    organ_id, phase, task_state, claims, refs, context,
                    warnings_by_organ.get(organ_id, []),
                    not_proven_by_organ.get(organ_id, []),
                    accepted_debt_by_organ.get(organ_id, []),
                )
            )
        throne_claims, throne_refs = _claims_and_declared_refs(evidence_by_organ.get(THRONE), THRONE)
        throne = _record(
            THRONE, phase, task_state, throne_claims, throne_refs, context,
            warnings_by_organ.get(THRONE, []),
            not_proven_by_organ.get(THRONE, []),
            accepted_debt_by_organ.get(THRONE, []),
        )
        phase_records.append(enforce_throne_guard(throne, phase_records))
        self.data["records"].extend(phase_records)
        phases = {item["phase"] for item in self.data["records"]}
        required = ("PREFLIGHT", "POSTCHECK") if phases == {"PREFLIGHT", "POSTCHECK"} else tuple(sorted(phases))
        errors = validate_ledger(self.data, require_phases=required)
        verdicts = [item["verdict"] for item in self.data["records"]]
        if errors or Verdict.BLOCK.value in verdicts:
            overall = Verdict.BLOCK.value
        elif Verdict.NOT_PROVEN.value in verdicts:
            overall = Verdict.NOT_PROVEN.value
        elif Verdict.PASS_WITH_DEBT.value in verdicts:
            overall = Verdict.PASS_WITH_DEBT.value
        else:
            overall = Verdict.PASS_PROVEN.value
        self.data["overall_verdict"] = overall
        self.data["validation_errors"] = errors
        self.data["updated_at_utc"] = utc_now()
        atomic_write_json(self.path, self.data)
        return self.data

    def post_work_ring(self) -> dict[str, Any]:
        post = {
            item["organ_id"]: item
            for item in self.data.get("records", [])
            if item.get("phase") == "POSTCHECK" and item.get("organ_id") in GREAT_NINE
        }
        ledger_errors = validate_ledger(self.data)
        rows = []
        for organ_id in GREAT_NINE:
            record = post.get(organ_id)
            if not record or ledger_errors:
                status, refs = "BLOCK", []
            else:
                status = (
                    "IMPLEMENTED" if record["verdict"] == Verdict.PASS_PROVEN.value
                    else "IMPLEMENTED_WITH_WARNINGS" if record["verdict"] == Verdict.PASS_WITH_DEBT.value
                    else "BLOCK"
                )
                refs = record.get("evidence_refs", [])
            rows.append(
                {
                    "organ_id": organ_id,
                    "task_id": self.data["task_id"],
                    "status": status,
                    "owned_checks": CHECKS[organ_id],
                    "evidence_paths": refs,
                    "learned_rules": [],
                }
            )
        return {
            "schema_version": "post_work.organ_ring.v0_2",
            "task_id": self.data["task_id"],
            "created_at_utc": utc_now(),
            "required_organs_source": "ORGANS/_POST_WORK_RING/REQUIRED_9_ORGANS_V0_1.json",
            "organ_receipts": rows,
            "ledger_validation_errors": ledger_errors,
            "ring_verdict": "POST_WORK_ORGAN_RING_PASS" if all(row["status"] != "BLOCK" for row in rows) else "POST_WORK_ORGAN_RING_BLOCK",
        }
