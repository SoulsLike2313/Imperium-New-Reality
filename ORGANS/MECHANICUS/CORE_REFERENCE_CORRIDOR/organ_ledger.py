"""Deterministic Great Nine and Throne participation ledger."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
ALLOWED_VERDICTS = {"PASS_PROVEN", "PASS_WITH_DEBT", "BLOCK", "NOT_PROVEN", "NOT_APPLICABLE_PROVEN"}


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


def _record(
    organ_id: str,
    phase: str,
    task_state: dict[str, Any],
    evidence_refs: list[str],
    checks_passed: bool,
    warnings: list[str],
    not_proven: list[str],
) -> dict[str, Any]:
    if not checks_passed:
        verdict = "BLOCK"
    elif not_proven:
        verdict = "PASS_WITH_DEBT"
    else:
        verdict = "PASS_PROVEN"
    record: dict[str, Any] = {
        "organ_id": organ_id,
        "phase": phase,
        "assigned_depth": task_state.get("organ_depth_plan", {}).get(organ_id, "STANDARD"),
        "input_refs": [task_state.get("task_id", ""), task_state.get("base_head", "")],
        "checks_executed": CHECKS[organ_id],
        "verdict": verdict,
        "confidence": 1.0 if verdict == "PASS_PROVEN" else 0.75 if verdict == "PASS_WITH_DEBT" else 0.0,
        "evidence_refs": sorted(set(evidence_refs)),
        "warnings": warnings,
        "not_proven": not_proven,
        "boundary_statement": _boundary(organ_id),
        "timestamp_utc": utc_now(),
    }
    if organ_id == THRONE:
        record["risk_statement"] = {
            "evidence": sorted(set(evidence_refs)),
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


def validate_ledger(ledger: dict[str, Any], *, require_phases: tuple[str, ...] = ("PREFLIGHT", "POSTCHECK")) -> list[str]:
    errors: list[str] = []
    records = ledger.get("records", [])
    required_fields = {
        "organ_id",
        "phase",
        "assigned_depth",
        "input_refs",
        "checks_executed",
        "verdict",
        "confidence",
        "evidence_refs",
        "warnings",
        "not_proven",
        "boundary_statement",
        "timestamp_utc",
    }
    for phase in require_phases:
        ids = [item.get("organ_id") for item in records if item.get("phase") == phase]
        for organ_id in [*GREAT_NINE, THRONE]:
            if ids.count(organ_id) != 1:
                errors.append(f"{phase}: participation count for {organ_id} is {ids.count(organ_id)}")
    for index, item in enumerate(records):
        missing = sorted(required_fields - set(item))
        if missing:
            errors.append(f"record {index}: missing {','.join(missing)}")
        if item.get("verdict") not in ALLOWED_VERDICTS:
            errors.append(f"record {index}: invalid verdict")
        if item.get("verdict") == "NOT_APPLICABLE_PROVEN" and not item.get("checks_executed"):
            errors.append(f"record {index}: unproved not-applicable")
        if item.get("organ_id") == THRONE and str(item.get("verdict", "")).startswith("PASS") and not item.get("evidence_refs"):
            errors.append(f"record {index}: Throne PASS has no evidence")
    return errors


class OrganLedger:
    def __init__(self, path: Path | str, task_id: str):
        self.path = Path(path).resolve()
        self.data: dict[str, Any] = {
            "schema_version": "imperium.core_reference_corridor.organ_ledger.v0_1",
            "task_id": task_id,
            "operational_canon_source": "ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json",
            "great_nine": GREAT_NINE,
            "crown_organ": THRONE,
            "constitution_conflict": "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
            "records": [],
            "overall_verdict": "NOT_PROVEN",
        }

    def load(self) -> dict[str, Any]:
        import json

        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def record_phase(
        self,
        phase: str,
        task_state: dict[str, Any],
        evidence_by_organ: dict[str, list[str]],
        *,
        checks_by_organ: dict[str, bool] | None = None,
        warnings_by_organ: dict[str, list[str]] | None = None,
        not_proven_by_organ: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        if phase not in {"PREFLIGHT", "POSTCHECK"}:
            raise ValueError("phase must be PREFLIGHT or POSTCHECK")
        checks_by_organ = checks_by_organ or {}
        warnings_by_organ = warnings_by_organ or {}
        not_proven_by_organ = not_proven_by_organ or {}
        self.data["records"] = [item for item in self.data["records"] if item.get("phase") != phase]
        for organ_id in [*GREAT_NINE, THRONE]:
            refs = evidence_by_organ.get(organ_id, [])
            self.data["records"].append(
                _record(
                    organ_id,
                    phase,
                    task_state,
                    refs,
                    checks_by_organ.get(organ_id, bool(refs)),
                    warnings_by_organ.get(organ_id, []),
                    not_proven_by_organ.get(organ_id, []),
                )
            )
        phases = {item["phase"] for item in self.data["records"]}
        required = ("PREFLIGHT", "POSTCHECK") if phases == {"PREFLIGHT", "POSTCHECK"} else tuple(sorted(phases))
        errors = validate_ledger(self.data, require_phases=required)
        verdicts = [item["verdict"] for item in self.data["records"]]
        self.data["overall_verdict"] = "BLOCK" if errors or "BLOCK" in verdicts else "PASS_WITH_DEBT" if "PASS_WITH_DEBT" in verdicts else "PASS_PROVEN"
        self.data["validation_errors"] = errors
        self.data["updated_at_utc"] = utc_now()
        atomic_write_json(self.path, self.data)
        return self.data

    def post_work_ring(self) -> dict[str, Any]:
        post = {item["organ_id"]: item for item in self.data["records"] if item["phase"] == "POSTCHECK" and item["organ_id"] in GREAT_NINE}
        rows = []
        for organ_id in GREAT_NINE:
            record = post.get(organ_id)
            if not record:
                status = "BLOCK"
                refs: list[str] = []
            else:
                status = "IMPLEMENTED" if record["verdict"] == "PASS_PROVEN" else "IMPLEMENTED_WITH_WARNINGS" if record["verdict"] == "PASS_WITH_DEBT" else "BLOCK"
                refs = record["evidence_refs"]
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
            "ring_verdict": "POST_WORK_ORGAN_RING_PASS" if all(row["status"] != "BLOCK" for row in rows) else "POST_WORK_ORGAN_RING_BLOCK",
        }

