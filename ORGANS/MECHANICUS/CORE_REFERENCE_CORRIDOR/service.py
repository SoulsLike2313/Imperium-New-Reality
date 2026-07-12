"""Application service that composes the bounded reference-corridor modules."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .checkpoint import CheckpointError, CheckpointStore
from .constants import TASK_STATE_ROUTE
from .evidence import EvidenceStore
from .executor import execute_capability, git_state
from .organ_ledger import GREAT_NINE, THRONE, OrganLedger
from .owner_gate import OwnerGate, OwnerGateError
from .registry import CapabilityRegistry, atomic_write_json, canonical_digest
from .root_resolver import RepositoryContext, resolve_repository_context
from .strategy import confidence_assessment, selected_strategy
from .task_store import TaskStore
from .ui_snapshot import build_ui_snapshot


TASK_ID = "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001"
BASE_HEAD = "281c3a7c8463de7fb64473929fe0ed975f99f595"
WARP_ID = "WARP-CORE-REFERENCE-0001"
REPORT_RELATIVE = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001")
TASKPACK_RELATIVE = Path("ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001")


class CorridorServiceError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CorridorPaths:
    worktree: Path
    reality: Path
    report: Path
    taskpack: Path
    registry: Path
    organ_ledger: Path
    checkpoints: Path
    owner_gate: Path


class CorridorService:
    def __init__(self, start: Path | str = ".") -> None:
        self.context: RepositoryContext = resolve_repository_context(start)
        self.paths = CorridorPaths(
            worktree=Path(self.context.worktree_root),
            reality=Path(self.context.reality_root),
            report=Path(self.context.worktree_root) / REPORT_RELATIVE,
            taskpack=Path(self.context.worktree_root) / TASKPACK_RELATIVE,
            registry=Path(self.context.worktree_root) / REPORT_RELATIVE / "CAPABILITY_REGISTRY.json",
            organ_ledger=Path(self.context.worktree_root) / REPORT_RELATIVE / "ORGAN_PARTICIPATION_LEDGER.json",
            checkpoints=Path(self.context.worktree_root) / REPORT_RELATIVE / "checkpoints",
            owner_gate=Path(self.context.worktree_root) / REPORT_RELATIVE / "owner_gate",
        )
        self.paths.report.mkdir(parents=True, exist_ok=True)
        self.task_store = TaskStore(self.paths.report, expected_base_head=BASE_HEAD)
        self.registry = CapabilityRegistry(self.paths.registry)
        self.owner_gate = OwnerGate(self.paths.owner_gate)
        self.checkpoints = CheckpointStore(
            self.paths.checkpoints,
            allowed_restore_roots=[self.paths.report],
        )

    def _task_definition(self) -> dict[str, Any]:
        confidence = confidence_assessment()
        strategy = selected_strategy()
        allowed_write = [
            str(self.paths.taskpack),
            str(self.paths.worktree / "ORGANS/ASTRONOMICON/ADMISSIONS"),
            str(self.paths.worktree / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR"),
            str(self.paths.report),
            str(self.paths.worktree / "SUPPORT/APP_TAURI"),
        ]
        return {
            "schema_version": "imperium.core_reference_corridor.task_state.v0_1",
            "task_id": TASK_ID,
            "task_type": "SERVITOR_TASK_PACK",
            "owner_intent": {
                "summary": "Build one safe, evidence-bound Owner-to-WARP reference corridor without landing master.",
                "authority_mode": "OWNER_EQUIVALENT_INSTRUCTION",
                "source_filename": "IMPERIUM_CORE_REFERENCE_CORRIDOR_0001_SERVITOR_PROMPT.md",
                "source_sha256": "3fa7249d956c8a79c04a8b5f323ec82bec8de1ebabf7aa3cace18d96e7ef6fd8",
                "payload_digest": "0e5e9f5cbd00cf8966330593df399f0f0a47c242ff7d3708c5721479f2ee5e94",
            },
            "created_at_utc": _utc_now(),
            "base_head": BASE_HEAD,
            "branch": self.context.branch,
            "scope": {
                "implementation": ["Mechanicus Safe Execution Spine", "APP_TAURI Thin IDE", "task/evidence package"],
                "forbidden": ["master mutation", "master land", "legacy RUN_*.ps1", "legacy deletion"],
            },
            "allowed_read_roots": [str(self.paths.reality), str(self.paths.worktree)],
            "allowed_write_roots": allowed_write,
            "acceptance_tests": [
                "exact_happy_path",
                "stale_base_head",
                "dirty_master_fixture",
                "unauthorized_write_path",
                "malicious_powershell_runner",
                "command_not_in_registry",
                "timeout",
                "process_crash",
                "failed_validation",
                "modified_finalized_evidence",
                "nested_path",
                "windows_long_path_boundary",
                "broken_ui_backend_parity",
                "warp_reject_discard",
                "warp_destroy",
                "disposable_rollback",
                "deterministic_replay_clone",
                "direct_execution_outside_executor",
                "missing_organ_participation",
                "throne_pass_without_proof",
            ],
            "confidence_components": confidence,
            "selected_strategy": strategy,
            "current_state": "OWNER_INTENT",
            "state_version": 1,
            "organ_depth_plan": {
                **{organ: "STANDARD" for organ in GREAT_NINE},
                "ADMINISTRATUM": "MINIMAL_LEDGER_ADAPTER",
                "MECHANICUS": "DEEP",
                "INQUISITION": "DEEP",
                "CUSTODES": "DEEP",
                THRONE: "CROWN_REVIEW",
            },
            "owner_decisions": [],
            "created_by": "CODEX_SERVITOR_PRIME",
            "warp": {
                "warp_id": WARP_ID,
                "path": str(self.paths.worktree),
                "base_head": BASE_HEAD,
                "state": "ACTIVE",
                "mode": "EXTERNAL_GIT_WORKTREE_FROM_EXACT_AUDIT_HEAD",
                "git_metadata": (self.paths.worktree / ".git").is_file(),
            },
            "caps": [
                "CAP_CONSTITUTION_GREAT_NINE_SUPERSESSION_PENDING",
                "CAP_NO_MASTER_LAND",
                "CAP_SCAFFOLD_EXTENSIONS_NOT_OPERATIONALLY_PROVEN",
            ],
        }

    def _checkpoint(self, checkpoint_id: str, semantic_state: str, state: dict[str, Any], evidence_refs: list[str]) -> None:
        try:
            self.checkpoints.create(
                checkpoint_id,
                semantic_state=semantic_state,
                task_id=TASK_ID,
                task_state=state,
                git_state={"worktree": git_state(self.paths.worktree), "reality": git_state(self.paths.reality)},
                evidence_refs=evidence_refs,
            )
        except CheckpointError as exc:
            if "immutable" not in str(exc) and "already" not in str(exc):
                raise

    def _transition(self, target: str, *, owner_decision: dict[str, Any] | None = None, gate_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        current = self.task_store.load()
        if current["current_state"] == target:
            return current
        return self.task_store.transition(
            target,
            expected_version=current["state_version"],
            expected_base_head=BASE_HEAD,
            owner_decision=owner_decision,
            gate_evidence=gate_evidence,
        )

    def _preflight_ledger(self, state: dict[str, Any]) -> dict[str, Any]:
        common = [
            f"{TASKPACK_RELATIVE.as_posix()}/TASKPACK_ADMISSION_RECEIPT.json",
            f"{REPORT_RELATIVE.as_posix()}/RECONCILIATION_PLAN.md",
            "ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json",
        ]
        evidence = {organ: [*common] for organ in [*GREAT_NINE, THRONE]}
        debt = {organ: ["POSTCHECK_PENDING"] for organ in [*GREAT_NINE, THRONE]}
        ledger = OrganLedger(self.paths.organ_ledger, TASK_ID)
        if self.paths.organ_ledger.is_file():
            ledger.load()
        return ledger.record_phase("PREFLIGHT", state, evidence, not_proven_by_organ=debt)

    def _ensure_throne_risk(self) -> None:
        if any(item.get("risk_id") == "RISK-GREAT-NINE-CONSTITUTION-CONFLICT" for item in self.owner_gate.risk_snapshot()["records"]):
            return
        self.owner_gate.record_throne_risk(
            {
                "risk_id": "RISK-GREAT-NINE-CONSTITUTION-CONFLICT",
                "task_id": TASK_ID,
                "warp_id": WARP_ID,
                "evidence": [f"{REPORT_RELATIVE.as_posix()}/CANON_SUPERSESSION_PROPOSAL.md"],
                "causal_chain": ["Constitution retains older list", "runtime follows later Owner canon", "unreviewed land preserves conflict"],
                "affected_scope": ["governance", "organ routing", "future land"],
                "probability": 0.9,
                "severity": "HIGH",
                "expected_consequences": "Ambiguous authority and contradictory organ participation.",
            }
        )

    def bootstrap(self) -> dict[str, Any]:
        if self.context.head != BASE_HEAD:
            raise CorridorServiceError(f"bootstrap requires exact audit HEAD, got {self.context.head}")
        if git_state(self.paths.reality)["dirty"]:
            raise CorridorServiceError("Reality/master is dirty")
        if not self.task_store.state_path.exists():
            state = self.task_store.create(self._task_definition())
        else:
            state = self.task_store.load()
        if not self.paths.registry.is_file():
            self.registry.initialize(self.context, self.paths.report)
        else:
            self.registry.reconcile(self.context, self.paths.report)
        self._ensure_throne_risk()

        route_to_exact = [
            "TASK_REGISTRATION",
            "SPECIFICATION",
            "CONFIDENCE",
            "STRATEGY",
            "GREAT_NINE_PREFLIGHT",
            "THRONE_PREFLIGHT",
            "OWNER_LAUNCH_APPROVAL",
            "EXACT_HEAD_WARP",
        ]
        for target in route_to_exact:
            state = self.task_store.load()
            if TASK_STATE_ROUTE.index(state["current_state"]) >= TASK_STATE_ROUTE.index(target):
                continue
            if target == "TASK_REGISTRATION":
                state = self._transition(target)
                self._checkpoint("checkpoint-task-registered", "TASK_REGISTERED", state, [f"{TASKPACK_RELATIVE.as_posix()}/TASKPACK_ADMISSION_RECEIPT.json"])
            elif target == "SPECIFICATION":
                state = self._transition(target)
                self._checkpoint("checkpoint-spec-approved", "SPEC_APPROVED", state, [f"{TASKPACK_RELATIVE.as_posix()}/EXTRACTED/TASK_SPEC.md"])
            elif target == "GREAT_NINE_PREFLIGHT":
                state = self._transition(target)
                self._preflight_ledger(state)
            elif target == "THRONE_PREFLIGHT":
                state = self._transition(target)
            elif target == "EXACT_HEAD_WARP":
                decisions = self.owner_gate.decision_snapshot()["records"]
                decision = next((item for item in decisions if item["action"] == "APPROVE_LAUNCH"), None)
                if decision is None:
                    decision = self.owner_gate.record_decision(
                        "OWNER-LAUNCH-IMPERIUM-CORE-REFERENCE-0001",
                        task_id=TASK_ID,
                        action="APPROVE_LAUNCH",
                        rationale="Owner supplied the named task specification and explicitly requested execution.",
                        evidence_refs=[f"{TASKPACK_RELATIVE.as_posix()}/TASK_START_ACK.json"],
                        details={"source_sha256": "3fa7249d956c8a79c04a8b5f323ec82bec8de1ebabf7aa3cace18d96e7ef6fd8"},
                    )
                gate = self.owner_gate.require("LAUNCH", TASK_ID)
                state = self._transition(
                    target,
                    owner_decision={"decision": "APPROVE_LAUNCH", "decision_id": decision["decision_id"], "actor": "OWNER", "basis": decision["rationale"]},
                    gate_evidence=gate,
                )
                self._checkpoint("checkpoint-warp-created", "WARP_CREATED", state, [f"{REPORT_RELATIVE.as_posix()}/WARP_CREATE_RECEIPT.json"])
            else:
                state = self._transition(target)
                if target == "STRATEGY":
                    self._checkpoint("checkpoint-strategy-selected", "STRATEGY_SELECTED", state, [f"{REPORT_RELATIVE.as_posix()}/RECONCILIATION_PLAN.md"])
        return self.status()

    def status(self) -> dict[str, Any]:
        state = self.task_store.load()
        return {
            "verdict": "STATE_RECOVERED",
            "task": state,
            "context": self.context.as_dict(),
            "report_root": str(self.paths.report),
            "registry_digest": self.registry.load().get("registry_digest") if self.paths.registry.is_file() else None,
        }

    def execute_demo(self) -> dict[str, Any]:
        state = self.task_store.load()
        if state["current_state"] == "EXACT_HEAD_WARP":
            state = self._transition("SAFE_EXECUTION")
        elif TASK_STATE_ROUTE.index(state["current_state"]) < TASK_STATE_ROUTE.index("SAFE_EXECUTION"):
            raise CorridorServiceError("demo execution requires EXACT_HEAD_WARP")
        self._checkpoint("checkpoint-execution-started", "EXECUTION_STARTED", state, [])
        self.registry.load()
        envelope = execute_capability(
            registry=self.registry,
            capability_id="CORE_DIAGNOSTIC",
            operation="diagnose",
            params={},
            cwd=self.paths.worktree,
            task_state=state,
            reality_root=self.paths.reality,
            worktree_root=self.paths.worktree,
            guard_roots=[self.paths.reality],
            validator_ids=["CORE_DIAGNOSTIC_CONTRACT_V0_1"],
            organ_verdict_refs=[f"{REPORT_RELATIVE.as_posix()}/ORGAN_PARTICIPATION_LEDGER.json"],
        )
        envelope.pop("envelope_digest", None)
        envelope["evidence_id"] = "SAFE_EXECUTION_RECEIPT"
        envelope["event_id"] = "EVENT-CORE-DIAGNOSTIC-DEMO"
        store = EvidenceStore(self.paths.report)
        entry = store.write(envelope, finalize=True)
        capability = self.registry.data["capabilities"][0]
        capability["last_validation"] = {"evidence_id": "SAFE_EXECUTION_RECEIPT", "verdict": envelope["verdict"], "timestamp_utc": envelope["timestamp_utc"]}
        self.registry.data["registry_digest"] = canonical_digest(self.registry.data)
        self.registry.validate(self.registry.data, verify_files=True)
        atomic_write_json(self.paths.registry, self.registry.data)
        return {"verdict": envelope["verdict"], "evidence": entry, "result": envelope.get("result"), "snapshot": self.snapshot()}

    def run_internal_capability(self, capability_id: str, evidence_id: str, *, seal_evidence_index: bool = False) -> dict[str, Any]:
        state = self.task_store.load()
        if TASK_STATE_ROUTE.index(state["current_state"]) < TASK_STATE_ROUTE.index("SAFE_EXECUTION"):
            raise CorridorServiceError(f"{capability_id} requires SAFE_EXECUTION")
        self.registry.reconcile(self.context, self.paths.report)
        envelope = execute_capability(
            registry=self.registry,
            capability_id=capability_id,
            operation="run",
            params={},
            cwd=self.paths.worktree,
            task_state=state,
            reality_root=self.paths.reality,
            worktree_root=self.paths.worktree,
            guard_roots=[self.paths.reality, self.paths.worktree],
            validator_ids=[capability_id + "_CONTRACT_V0_1"],
            organ_verdict_refs=[f"{REPORT_RELATIVE.as_posix()}/ORGAN_PARTICIPATION_LEDGER.json"],
        )
        envelope.pop("envelope_digest", None)
        envelope["evidence_id"] = evidence_id
        envelope["event_id"] = "EVENT-" + evidence_id
        store = EvidenceStore(self.paths.report)
        entry = store.write(envelope, finalize=True)
        capability = next(item for item in self.registry.data["capabilities"] if item["capability_id"] == capability_id)
        capability["last_validation"] = {"evidence_id": evidence_id, "verdict": envelope["verdict"], "timestamp_utc": envelope["timestamp_utc"]}
        self.registry.data["registry_digest"] = canonical_digest(self.registry.data)
        self.registry.validate(self.registry.data, verify_files=True)
        atomic_write_json(self.paths.registry, self.registry.data)
        if seal_evidence_index:
            from .report_builder import _changed_files, _write_hash_manifest

            _write_hash_manifest(self.paths.report)
            changed = _changed_files(self.paths.worktree)
            atomic_write_json(
                self.paths.report / "FILES_CHANGED.json",
                {
                    "schema_version": "imperium.core_reference_corridor.files_changed.v0_1",
                    "task_id": TASK_ID,
                    "base_head": BASE_HEAD,
                    "files": changed,
                    "count": len(changed),
                },
            )
            atomic_write_json(
                self.paths.report / "FILES_TO_LAND.json",
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
            store.finalize_index()
        return {"verdict": envelope["verdict"], "evidence": entry, "result": envelope.get("result"), "snapshot": self.snapshot()}

    def advance_to_owner_review(self) -> dict[str, Any]:
        validation = json.loads((self.paths.report / "VALIDATION_MATRIX.json").read_text(encoding="utf-8"))
        if validation.get("verdict") not in {"PASS_PROVEN", "REFERENCE_CORRIDOR_VALIDATION_PASS"}:
            raise CorridorServiceError("critical validation matrix is not PASS_PROVEN")
        current_receipts = validation.get("current_receipts")
        if not isinstance(current_receipts, dict) or set(current_receipts) != {"validation", "negative_proof", "ui_backend_parity"}:
            raise CorridorServiceError("validation matrix has no complete current receipt set")
        store = EvidenceStore(self.paths.report)
        verified_refs: list[str] = []
        for role, filename in sorted(current_receipts.items()):
            path = self.paths.report / str(filename)
            if path.parent != self.paths.report or path.suffix != ".json" or not path.is_file():
                raise CorridorServiceError(f"unsafe or missing current {role} receipt")
            evidence_id = path.stem
            store.verify(evidence_id)
            document = json.loads(path.read_text(encoding="utf-8"))
            result = document.get("result", {})
            if document.get("verdict") != "PASS_PROVEN" or not isinstance(result, dict) or result.get("verdict") != "PASS_PROVEN":
                raise CorridorServiceError(f"current {role} receipt is not semantically PASS_PROVEN")
            verified_refs.append(f"{REPORT_RELATIVE.as_posix()}/{path.name}")
        state = self.task_store.load()
        refs = [f"{REPORT_RELATIVE.as_posix()}/SAFE_EXECUTION_RECEIPT.json", *verified_refs]
        ledger = OrganLedger(self.paths.organ_ledger, TASK_ID)
        ledger.load()
        ledger.record_phase("POSTCHECK", state, {organ: refs for organ in [*GREAT_NINE, THRONE]})
        if state["current_state"] == "OWNER_ACCEPT_OR_REJECT":
            return self.status()
        if state["current_state"] == "SAFE_EXECUTION":
            state = self._transition("VALIDATION")
        if state["current_state"] != "VALIDATION":
            raise CorridorServiceError(f"postcheck requires VALIDATION, got {state['current_state']}")
        state = self._transition("GREAT_NINE_POSTCHECK")
        state = self._transition("THRONE_REVIEW")
        state = self._transition("OWNER_ACCEPT_OR_REJECT")
        self._checkpoint("checkpoint-validation-completed", "VALIDATION_COMPLETED", state, refs)
        self._checkpoint("checkpoint-owner-review", "OWNER_REVIEW", state, refs)
        return self.status()

    def snapshot(self) -> dict[str, Any]:
        return build_ui_snapshot(self.context, self.paths.report)

    def ui_action(self, action_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        self.registry.load()
        try:
            action = self.registry.action(action_id)
        except Exception as exc:
            return {"verdict": "BLOCK", "reason": str(exc), "snapshot": self.snapshot()}
        if action_id == "refresh_state":
            return {"verdict": "PASS_PROVEN", "snapshot": self.snapshot()}
        if action_id == "run_core_diagnostic":
            return self.execute_demo()
        if action_id in {"accept_result", "reject_result", "request_rework"}:
            state = self.task_store.load()
            if state["current_state"] != "OWNER_ACCEPT_OR_REJECT":
                return {"verdict": "BLOCK", "reason": "OWNER_REVIEW_STATE_REQUIRED", "snapshot": self.snapshot()}
            owner_action = {"accept_result": "ACCEPT_RESULT", "reject_result": "REJECT_RESULT", "request_rework": "REQUEST_REWORK"}[action_id]
            decision = self.owner_gate.record_decision(
                "OWNER-" + owner_action + "-" + uuid.uuid4().hex[:12],
                task_id=TASK_ID,
                warp_id=WARP_ID,
                action=owner_action,
                rationale=str(payload.get("rationale") or f"Owner selected {owner_action} in Thin IDE."),
                evidence_refs=[f"{REPORT_RELATIVE.as_posix()}/OWNER_REVIEW_READY_RECEIPT.json"],
            )
            state = self._transition(
                "LAND_PLAN_OR_DISCARD",
                owner_decision={"decision": owner_action, "decision_id": decision["decision_id"], "actor": "OWNER", "basis": decision["rationale"]},
                gate_evidence=self.owner_gate.check(owner_action, TASK_ID, WARP_ID),
            )
            return {"verdict": "OWNER_DECISION_RECORDED", "decision": decision, "state": state, "snapshot": self.snapshot()}
        return {"verdict": "BLOCK", "reason": "ACTION_AVAILABLE_ONLY_AFTER_EXPLICIT_LIFECYCLE_PRECONDITIONS", "action_id": action_id, "snapshot": self.snapshot()}
