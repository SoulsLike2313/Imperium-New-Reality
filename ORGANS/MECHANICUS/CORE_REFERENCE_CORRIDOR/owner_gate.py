"""Explicit Owner authority gates and evidence-bound Throne risk records."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
import uuid


DECISION_ACTIONS = (
    "APPROVE_LAUNCH",
    "STOP",
    "CONTINUE_FROM_CHECKPOINT",
    "ACCEPT_RISK",
    "ACCEPT_RESULT",
    "REJECT_RESULT",
    "REQUEST_REWORK",
    "ALLOW_LAND_PREPARATION",
    "FORBID_LAND",
    "DISCARD_WARP",
    "DESTROY_WARP",
    "CONTINUE_AFTER_OVERRUN",
)

GATE_POLICY = {
    "LAUNCH": ({"APPROVE_LAUNCH"}, {"STOP"}),
    "CONTINUE_FROM_CHECKPOINT": ({"CONTINUE_FROM_CHECKPOINT"}, {"STOP"}),
    "ACCEPT_RISK": ({"ACCEPT_RISK"}, {"STOP"}),
    "ACCEPT_RESULT": ({"ACCEPT_RESULT"}, {"REJECT_RESULT", "REQUEST_REWORK", "STOP"}),
    "REJECT_RESULT": ({"REJECT_RESULT"}, {"ACCEPT_RESULT"}),
    "REQUEST_REWORK": ({"REQUEST_REWORK"}, {"ACCEPT_RESULT"}),
    "PREPARE_LAND": ({"ALLOW_LAND_PREPARATION"}, {"FORBID_LAND", "REJECT_RESULT", "REQUEST_REWORK", "STOP"}),
    "DISCARD_WARP": ({"DISCARD_WARP"}, set()),
    "DESTROY_WARP": ({"DESTROY_WARP"}, set()),
    "CONTINUE_AFTER_OVERRUN": ({"CONTINUE_AFTER_OVERRUN"}, {"STOP"}),
}

THRONE_RISK_FIELDS = (
    "evidence",
    "causal_chain",
    "affected_scope",
    "probability",
    "severity",
    "expected_consequences",
)

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_WARP_BOUND_ACTIONS = {
    "ACCEPT_RESULT",
    "REJECT_RESULT",
    "REQUEST_REWORK",
    "ALLOW_LAND_PREPARATION",
    "FORBID_LAND",
    "DISCARD_WARP",
    "DESTROY_WARP",
}


class OwnerGateError(RuntimeError):
    """Decision/risk storage or contract error."""


class OwnerDecisionRequired(OwnerGateError):
    """Raised when an action lacks a current explicit Owner decision."""

    def __init__(self, message: str, receipt: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.receipt = dict(receipt)


class OwnerGateTamperError(OwnerGateError):
    """Decision or risk ledger self-hash mismatch."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: Any) -> bytes:
    try:
        rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise OwnerGateError(f"record is not canonical JSON: {exc}") from exc
    return (rendered + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(_canonical_bytes(value))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _validate_id(value: Any, label: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise OwnerGateError(f"invalid {label}")


def _validate_timestamp(value: str) -> None:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except (TypeError, ValueError) as exc:
        raise OwnerGateError("decision timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise OwnerGateError("decision timestamp must be UTC")


class OwnerGate:
    """Persist immutable decisions and make every protected transition explicit."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.decisions_path = self.root / "OWNER_DECISIONS.json"
        self.risks_path = self.root / "THRONE_RISKS.json"
        if not self.decisions_path.exists():
            self._write_ledger(
                self.decisions_path,
                {"schema_version": "imperium.owner_decisions.v1", "records": [], "updated_at_utc": _utc_now()},
            )
        if not self.risks_path.exists():
            self._write_ledger(
                self.risks_path,
                {"schema_version": "imperium.throne_risks.v1", "records": [], "updated_at_utc": _utc_now()},
            )

    @staticmethod
    def _ledger_hash(ledger: Mapping[str, Any]) -> str:
        core = {key: value for key, value in ledger.items() if key != "content_sha256"}
        return _sha256(_canonical_bytes(core))

    def _write_ledger(self, path: Path, ledger: Mapping[str, Any]) -> dict[str, Any]:
        materialized = dict(ledger)
        materialized["content_sha256"] = self._ledger_hash(materialized)
        _atomic_write(path, materialized)
        return materialized

    def _load_ledger(self, path: Path, schema: str) -> dict[str, Any]:
        try:
            ledger = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OwnerGateTamperError(f"ledger cannot be read: {path.name}: {exc}") from exc
        if ledger.get("schema_version") != schema or not isinstance(ledger.get("records"), list):
            raise OwnerGateTamperError(f"ledger schema is invalid: {path.name}")
        if ledger.get("content_sha256") != self._ledger_hash(ledger):
            raise OwnerGateTamperError(f"ledger hash mismatch: {path.name}")
        return ledger

    def record_decision(
        self,
        decision_id: str,
        *,
        task_id: str,
        action: str,
        rationale: str,
        evidence_refs: Sequence[str],
        warp_id: str | None = None,
        decided_by: str = "OWNER",
        timestamp_utc: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _validate_id(decision_id, "decision_id")
        _validate_id(task_id, "task_id")
        _validate_id(warp_id, "warp_id", optional=True)
        if action not in DECISION_ACTIONS:
            raise OwnerGateError(f"unsupported Owner decision action: {action}")
        if decided_by != "OWNER":
            raise OwnerGateError("only an explicit OWNER record can authorize a gate")
        if action in _WARP_BOUND_ACTIONS and warp_id is None:
            raise OwnerGateError(f"{action} must be bound to a warp_id")
        if not isinstance(rationale, str) or not rationale.strip():
            raise OwnerGateError("Owner decision rationale is required")
        if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)) or not all(
            isinstance(item, str) for item in evidence_refs
        ):
            raise OwnerGateError("evidence_refs must be an array of strings")
        detail_copy = dict(details or {})
        if action == "CONTINUE_FROM_CHECKPOINT" and not detail_copy.get("checkpoint_id"):
            raise OwnerGateError("continue decision requires checkpoint_id")
        if action == "ACCEPT_RISK":
            risk_id = detail_copy.get("risk_id")
            _validate_id(risk_id, "risk_id")
            risks = self._load_ledger(self.risks_path, "imperium.throne_risks.v1")
            if not any(record["risk_id"] == risk_id and record["task_id"] == task_id for record in risks["records"]):
                raise OwnerGateError("accepted Throne risk is not recorded for this task")
        timestamp = timestamp_utc or _utc_now()
        _validate_timestamp(timestamp)
        ledger = self._load_ledger(self.decisions_path, "imperium.owner_decisions.v1")
        if any(record.get("decision_id") == decision_id for record in ledger["records"]):
            raise OwnerGateError("Owner decision ids are immutable")
        record = {
            "schema_version": "imperium.owner_decision.v1",
            "decision_id": decision_id,
            "task_id": task_id,
            "warp_id": warp_id,
            "action": action,
            "decided_by": decided_by,
            "rationale": rationale.strip(),
            "evidence_refs": list(evidence_refs),
            "details": detail_copy,
            "timestamp_utc": timestamp,
            "sequence": len(ledger["records"]) + 1,
        }
        ledger["records"].append(record)
        ledger["updated_at_utc"] = _utc_now()
        self._write_ledger(self.decisions_path, ledger)
        return record

    def check(
        self,
        action: str,
        task_id: str,
        warp_id: str | None = None,
        *,
        checkpoint_id: str | None = None,
        risk_id: str | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        if action not in GATE_POLICY:
            raise OwnerGateError(f"unknown protected gate: {action}")
        _validate_id(task_id, "task_id")
        _validate_id(warp_id, "warp_id", optional=True)
        allowed_actions, blocking_actions = GATE_POLICY[action]
        relevant_actions = allowed_actions | blocking_actions
        ledger = self._load_ledger(self.decisions_path, "imperium.owner_decisions.v1")
        candidates = []
        for record in ledger["records"]:
            if record["task_id"] != task_id or record["action"] not in relevant_actions:
                continue
            if warp_id is not None and record.get("warp_id") not in (None, warp_id):
                continue
            if warp_id is None and record.get("warp_id") is not None:
                continue
            if action == "CONTINUE_FROM_CHECKPOINT" and record.get("details", {}).get("checkpoint_id") != checkpoint_id:
                continue
            if action == "ACCEPT_RISK" and record.get("details", {}).get("risk_id") != risk_id:
                continue
            candidates.append(record)
        latest = max(candidates, key=lambda item: item["sequence"], default=None)
        allowed = latest is not None and latest["action"] in allowed_actions
        return {
            "schema_version": "imperium.owner_gate_receipt.v1",
            "verdict": "ALLOW" if allowed else "BLOCK",
            "allowed": allowed,
            "gate_action": action,
            "task_id": task_id,
            "warp_id": warp_id,
            "decision_ref": latest["decision_id"] if latest else None,
            "decision_action": latest["action"] if latest else None,
            "reason": "EXPLICIT_OWNER_DECISION" if allowed else "EXPLICIT_OWNER_DECISION_REQUIRED_OR_SUPERSEDED",
            "timestamp_utc": _utc_now(),
        }

    def require(self, action: str, task_id: str, warp_id: str | None = None, **context: Any) -> dict[str, Any]:
        receipt = self.check(action, task_id, warp_id, **context)
        if not receipt["allowed"]:
            raise OwnerDecisionRequired(f"Owner decision required for {action}", receipt)
        return receipt

    def record_throne_risk(self, risk: Mapping[str, Any]) -> dict[str, Any]:
        required = ("risk_id", "task_id", *THRONE_RISK_FIELDS)
        missing = [field for field in required if field not in risk]
        if missing:
            raise OwnerGateError(f"missing Throne risk fields: {', '.join(missing)}")
        _validate_id(risk["risk_id"], "risk_id")
        _validate_id(risk["task_id"], "task_id")
        _validate_id(risk.get("warp_id"), "warp_id", optional=True)
        if not isinstance(risk["evidence"], Sequence) or isinstance(risk["evidence"], (str, bytes)) or not risk["evidence"]:
            raise OwnerGateError("Throne risk evidence must be a non-empty array")
        if not isinstance(risk["causal_chain"], Sequence) or isinstance(risk["causal_chain"], (str, bytes)) or not risk["causal_chain"]:
            raise OwnerGateError("Throne causal_chain must be a non-empty array")
        if not isinstance(risk["affected_scope"], (Mapping, list, tuple)) or not risk["affected_scope"]:
            raise OwnerGateError("Throne affected_scope must be non-empty")
        probability = risk["probability"]
        if not isinstance(probability, (int, float)) or isinstance(probability, bool) or not 0 <= probability <= 1:
            raise OwnerGateError("Throne probability must be between 0 and 1")
        if risk["severity"] not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise OwnerGateError("invalid Throne severity")
        consequences = risk["expected_consequences"]
        if not isinstance(consequences, (str, list, tuple)) or not consequences:
            raise OwnerGateError("Throne expected_consequences must be non-empty")
        record = json.loads(_canonical_bytes(dict(risk)))
        record.setdefault("schema_version", "imperium.throne_risk.v1")
        record.setdefault("warp_id", None)
        record["source"] = "THRONE"
        record["timestamp_utc"] = risk.get("timestamp_utc", _utc_now())
        ledger = self._load_ledger(self.risks_path, "imperium.throne_risks.v1")
        if any(existing.get("risk_id") == record["risk_id"] for existing in ledger["records"]):
            raise OwnerGateError("Throne risk ids are immutable")
        ledger["records"].append(record)
        ledger["updated_at_utc"] = _utc_now()
        self._write_ledger(self.risks_path, ledger)
        return record

    @staticmethod
    def validate_throne_assessment(assessment: Mapping[str, Any]) -> dict[str, Any]:
        verdict = assessment.get("verdict")
        evidence_refs = assessment.get("evidence_refs")
        if not isinstance(verdict, str):
            raise OwnerGateError("Throne assessment requires a verdict")
        if verdict.startswith("PASS") and (
            not isinstance(evidence_refs, Sequence)
            or isinstance(evidence_refs, (str, bytes))
            or not evidence_refs
            or not all(isinstance(item, str) and item for item in evidence_refs)
        ):
            raise OwnerGateError("Throne PASS requires referenced proof")
        return {"verdict": verdict, "evidence_refs": list(evidence_refs or ()), "validated": True}

    @staticmethod
    def evaluate_budget_pause(
        *,
        estimated_cost: float | None,
        actual_cost: float | None,
        estimated_seconds: float | None,
        elapsed_seconds: float | None,
    ) -> dict[str, Any]:
        reasons: list[str] = []
        if estimated_cost is not None and actual_cost is not None:
            if estimated_cost < 0 or actual_cost < 0:
                raise OwnerGateError("cost values cannot be negative")
            if estimated_cost == 0 and actual_cost > 0 or estimated_cost > 0 and actual_cost > estimated_cost * 1.5:
                reasons.append("COST_EXCEEDED_150_PERCENT")
        if estimated_seconds is not None and elapsed_seconds is not None:
            if estimated_seconds < 0 or elapsed_seconds < 0:
                raise OwnerGateError("time values cannot be negative")
            if estimated_seconds == 0 and elapsed_seconds > 0 or estimated_seconds > 0 and elapsed_seconds >= estimated_seconds * 2:
                reasons.append("TIME_REACHED_200_PERCENT")
        return {
            "schema_version": "imperium.cost_time_pause.v1",
            "verdict": "PAUSE" if reasons else "CONTINUE",
            "pause_required": bool(reasons),
            "reasons": reasons,
            "continuation_gate": "CONTINUE_AFTER_OVERRUN" if reasons else None,
            "timestamp_utc": _utc_now(),
        }

    def decision_snapshot(self) -> dict[str, Any]:
        return self._load_ledger(self.decisions_path, "imperium.owner_decisions.v1")

    def risk_snapshot(self) -> dict[str, Any]:
        return self._load_ledger(self.risks_path, "imperium.throne_risks.v1")
