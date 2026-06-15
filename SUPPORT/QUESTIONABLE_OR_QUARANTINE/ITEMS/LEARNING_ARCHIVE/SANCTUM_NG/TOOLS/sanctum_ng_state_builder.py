#!/usr/bin/env python3
"""Build Sanctum NG read-only truth state from canonical phase registry."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "573169b9830ecb0322202e33a3e12ca2fc5e3556"
MODE = "READ_ONLY_FOUNDATION"
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_PHASE_REGISTRY_V0_1.json"
OFFICIO_DRAFT_REL = "IMPERIUM_NEW_GENERATION/AUTHORITY_DRAFTS/OFFICIO_LIVE_COMMUNICATION_ENFORCEMENT_V0_1.md"
OFFICIO_GATE_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/officio_live_communication_gate_v0_1.schema.json"
CURRENT_TRUTH_REL = "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json"
REPORT_STATUS_INDEX_REL = "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json"
EVIDENCE_SOURCE_MAP_REL = "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_SOURCE_MAP_V0_1.json"
EVIDENCE_MAP_UNIFIED_REL = "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_MAP_UNIFIED_V0_1.json"
EVIDENCE_FRESHNESS_INDEX_REL = "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_FRESHNESS_INDEX_V0_1.json"
PARTIAL_ACCEPTANCE_MAP_REL = "IMPERIUM_NEW_GENERATION/TRUTH/PARTIAL_ACCEPTANCE_MAP_V0_1.json"
ACCEPTANCE_DECISION_RULES_REL = "IMPERIUM_NEW_GENERATION/TRUTH/ACCEPTANCE_DECISION_RULES_V0_1.json"
ACCEPTANCE_DECISION_SAMPLES_REL = "IMPERIUM_NEW_GENERATION/TRUTH/ACCEPTANCE_DECISION_SAMPLES_V0_1.json"


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def get_git_truth(repo_root: Path, required_starting_head: str) -> dict[str, Any]:
    head = run_git(repo_root, "rev-parse", "HEAD")
    branch = run_git(repo_root, "branch", "--show-current")
    status_short = run_git(repo_root, "status", "--short")
    return {
        "head": head,
        "branch": branch,
        "worktree_dirty": bool(status_short),
        "required_starting_head": required_starting_head,
        "head_matches_required_start": head == required_starting_head,
    }


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    return value


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def registry_refs(entry: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in ["architecture_refs", "contract_refs", "report_refs", "validator_refs", "evidence_refs"]:
        values = entry.get(key, [])
        if isinstance(values, list):
            refs.extend(str(value) for value in values if str(value).strip())
    return unique(refs)


def map_status(registry_status: str, has_evidence_refs: bool) -> str:
    status = registry_status.strip().upper()
    if status == "PROVED_BY_RECEIPT":
        return "PROVED" if has_evidence_refs else "WARN"
    if status in {"FOUNDATION", "PARTIAL", "WARN", "MISSING"}:
        return status
    return "WARN"


def build_communication_gate(repo_root: Path, task_id: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    report_dir_rel = f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}"
    officio_ack_rel = f"{report_dir_rel}/OFFICIO_ROLE_ACK_OR_WARN.json"
    live_report_json_rel = f"{report_dir_rel}/OFFICIO_LIVE_LANGUAGE_REPAIR_REPORT.json"

    authority_sources = [
        OFFICIO_DRAFT_REL,
        OFFICIO_GATE_SCHEMA_REL,
        officio_ack_rel,
    ]

    missing_authority = [rel for rel in authority_sources if not (repo_root / rel).exists()]
    if missing_authority:
        warnings.append("COMMUNICATION_GATE_MISSING_AUTHORITY_REFS")

    live_report = load_json(repo_root / live_report_json_rel) or {}
    violations = live_report.get("violations", [])
    self_corrections = live_report.get("self_corrections", [])
    if not isinstance(violations, list):
        violations = []
    if not isinstance(self_corrections, list):
        self_corrections = []

    if missing_authority:
        status = "WARN_MISSING_AUTHORITY"
        known_limitation = "Communication authority artifacts are incomplete in bounded scope."
    else:
        status = "WARN_FOUNDATION_ONLY"
        known_limitation = "Live language compliance is foundation-level receipt discipline, not runtime hard-block enforcement."

    gate = {
        "LIVE_LANGUAGE_COMPLIANCE": "RUSSIAN_OWNER_PROGRESS_REQUIRED",
        "FINAL_REPORT_LANGUAGE": "RUSSIAN_REQUIRED",
        "TECHNICAL_ARTIFACT_LANGUAGE": "ENGLISH_ALLOWED",
        "AUTHORITY_SOURCE": authority_sources,
        "STATUS": status,
        "KNOWN_LIMITATION": known_limitation,
        "VIOLATIONS": [str(item) for item in violations],
        "SELF_CORRECTIONS": [str(item) for item in self_corrections],
    }
    return gate, warnings


def build_phases_from_registry(repo_root: Path, registry: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    phases: list[dict[str, Any]] = []

    raw_phases = registry.get("phases", [])
    if not isinstance(raw_phases, list):
        return [], ["PHASE_REGISTRY_INVALID_SHAPE"]

    sorted_entries = sorted(
        [entry for entry in raw_phases if isinstance(entry, dict)],
        key=lambda item: int(item.get("display_order", 999)),
    )

    for entry in sorted_entries:
        phase_no = int(entry.get("display_order", 0))
        phase_name = str(entry.get("title", f"Phase {phase_no}")).strip() or f"Phase {phase_no}"
        phase_id = str(entry.get("phase_id", f"PHASE_{phase_no:02d}")).strip()
        source_commit = str(entry.get("source_commit", "UNKNOWN")).strip() or "UNKNOWN"

        refs = registry_refs(entry)
        existing_refs: list[str] = []
        missing_refs: list[str] = []
        for rel in refs:
            if (repo_root / rel).exists():
                existing_refs.append(rel)
            else:
                missing_refs.append(rel)

        base_status = map_status(str(entry.get("status", "WARN")), bool(entry.get("evidence_refs", [])))
        status = base_status
        if not existing_refs:
            status = "MISSING"
        elif missing_refs and status in {"PROVED", "FOUNDATION"}:
            status = "PARTIAL"

        if status in {"WARN", "MISSING", "PARTIAL"}:
            warnings.append(f"PHASE_{phase_no}_{status}")

        evidence_refs = [f"FILE:{path}" for path in existing_refs]
        evidence_refs.append(f"REGISTRY:{phase_id}")

        report_paths = [path for path in existing_refs if "/REPORTS/" in path]
        known_warnings = entry.get("known_warnings", [])
        if not isinstance(known_warnings, list):
            known_warnings = []

        limitations = [
            f"Registry phase id: {phase_id}",
            f"Registry source commit: {source_commit}",
        ]
        limitations.extend(str(item) for item in known_warnings)
        if missing_refs:
            limitations.append("Missing expected artifacts: " + ", ".join(missing_refs))

        summary = f"{phase_name} foundation mapping from canonical Sanctum NG phase registry."

        phases.append(
            {
                "phase_no": phase_no,
                "name": phase_name,
                "status": status,
                "summary": summary,
                "evidence_refs": evidence_refs,
                "paths": existing_refs,
                "report_paths": report_paths,
                "limitations": limitations,
            }
        )

    return phases, warnings


def build_current_truth_index(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    current_truth_path = repo_root / CURRENT_TRUTH_REL

    index: dict[str, Any] = {
        "current_truth_root_path": CURRENT_TRUTH_REL,
        "report_status_index_path": REPORT_STATUS_INDEX_REL,
        "evidence_source_map_path": EVIDENCE_SOURCE_MAP_REL,
        "evidence_map_unified_path": EVIDENCE_MAP_UNIFIED_REL,
        "evidence_freshness_index_path": EVIDENCE_FRESHNESS_INDEX_REL,
        "partial_acceptance_map_path": PARTIAL_ACCEPTANCE_MAP_REL,
        "acceptance_decision_rules_path": ACCEPTANCE_DECISION_RULES_REL,
        "acceptance_decision_samples_path": ACCEPTANCE_DECISION_SAMPLES_REL,
        "acceptance_layer_status": "UNKNOWN",
        "status": "UNKNOWN",
        "last_sync_utc": "UNKNOWN",
        "known_limitations": [
            "Read-only truth reference layer only.",
            "No live backend synchronization claim.",
        ],
    }

    current_truth = load_json(current_truth_path)
    if current_truth is None:
        warnings.append("CURRENT_TRUTH_ROOT_MISSING_OR_INVALID")
        index["status"] = "MISSING"
        return index, warnings

    index["report_status_index_path"] = str(current_truth.get("report_status_index_path", REPORT_STATUS_INDEX_REL))
    index["evidence_source_map_path"] = str(current_truth.get("evidence_source_map_path", EVIDENCE_SOURCE_MAP_REL))
    index["evidence_map_unified_path"] = str(current_truth.get("evidence_map_unified_path", EVIDENCE_MAP_UNIFIED_REL))
    index["evidence_freshness_index_path"] = str(
        current_truth.get("evidence_freshness_index_path", EVIDENCE_FRESHNESS_INDEX_REL)
    )
    index["partial_acceptance_map_path"] = str(
        current_truth.get("partial_acceptance_map_path", PARTIAL_ACCEPTANCE_MAP_REL)
    )
    index["acceptance_decision_rules_path"] = str(
        current_truth.get("acceptance_decision_rules_path", ACCEPTANCE_DECISION_RULES_REL)
    )
    index["acceptance_decision_samples_path"] = str(
        current_truth.get("acceptance_decision_samples_path", ACCEPTANCE_DECISION_SAMPLES_REL)
    )
    index["last_sync_utc"] = str(current_truth.get("generated_at_utc", "UNKNOWN"))

    unification = current_truth.get("evidence_unification", {})
    if isinstance(unification, dict):
        index["status"] = str(unification.get("status", "FOUNDATION_ONLY"))
        known_limitations = unification.get("known_limitations", [])
        if isinstance(known_limitations, list) and known_limitations:
            index["known_limitations"] = [str(item) for item in known_limitations]
    else:
        index["status"] = "FOUNDATION_ONLY"

    partial_layer = current_truth.get("partial_acceptance_layer", {})
    if isinstance(partial_layer, dict):
        index["acceptance_layer_status"] = str(partial_layer.get("status", "FOUNDATION_ONLY"))
        partial_limitations = partial_layer.get("known_limitations", [])
        if isinstance(partial_limitations, list):
            index["known_limitations"] = unique(index["known_limitations"] + [str(item) for item in partial_limitations])
    else:
        index["acceptance_layer_status"] = "MISSING"

    missing_refs = []
    for key in [
        "current_truth_root_path",
        "report_status_index_path",
        "evidence_source_map_path",
        "evidence_map_unified_path",
        "evidence_freshness_index_path",
        "partial_acceptance_map_path",
        "acceptance_decision_rules_path",
        "acceptance_decision_samples_path",
    ]:
        rel_path = str(index.get(key, "")).strip()
        if not rel_path or not (repo_root / rel_path).exists():
            missing_refs.append(key)

    if missing_refs:
        index["status"] = "PARTIAL"
        warnings.append("CURRENT_TRUTH_INDEX_MISSING_REFS_" + "_".join(missing_refs))

    return index, warnings


def build_state(repo_root: Path, task_id: str, required_starting_head: str) -> dict[str, Any]:
    warnings: list[str] = []
    registry_path = repo_root / REGISTRY_REL
    registry = load_json(registry_path)

    if registry is None:
        phases = [
            {
                "phase_no": phase_no,
                "name": f"Phase {phase_no}",
                "status": "MISSING",
                "summary": "Phase registry is missing or invalid.",
                "evidence_refs": ["REGISTRY:MISSING"],
                "paths": [],
                "report_paths": [],
                "limitations": ["Registry not found or invalid JSON."],
            }
            for phase_no in range(1, 11)
        ]
        warnings.append("PHASE_REGISTRY_MISSING_OR_INVALID")
        registry_loaded = False
        registry_source_commit = "UNKNOWN"
    else:
        phases, phase_warnings = build_phases_from_registry(repo_root, registry)
        warnings.extend(phase_warnings)
        registry_loaded = True
        registry_source_commit = str(registry.get("source_commit", "UNKNOWN"))

    phase_numbers = {int(phase["phase_no"]) for phase in phases if isinstance(phase.get("phase_no"), int)}
    for expected in range(1, 11):
        if expected not in phase_numbers:
            warnings.append(f"PHASE_{expected}_MISSING_FROM_REGISTRY")
            phases.append(
                {
                    "phase_no": expected,
                    "name": f"Phase {expected}",
                    "status": "MISSING",
                    "summary": "Missing from canonical phase registry.",
                    "evidence_refs": [f"REGISTRY:PHASE_{expected:02d}_MISSING"],
                    "paths": [],
                    "report_paths": [],
                    "limitations": ["Registry entry missing."],
                }
            )

    phases = sorted(phases, key=lambda item: int(item.get("phase_no", 999)))
    communication_gate, communication_warnings = build_communication_gate(repo_root, task_id)
    warnings.extend(communication_warnings)
    current_truth_index, truth_index_warnings = build_current_truth_index(repo_root)
    warnings.extend(truth_index_warnings)

    git_truth = get_git_truth(repo_root, required_starting_head)

    state = {
        "schema_id": "SANCTUM_NG_STATE_V0_1",
        "task_id": task_id,
        "mode": MODE,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git": git_truth,
        "truth_flags": {
            "read_only": True,
            "foundation_only": True,
            "production_ready": False,
            "live_backend": False,
            "autonomous_execution": False,
        },
        "phase_registry": {
            "path": REGISTRY_REL,
            "loaded": registry_loaded,
            "phase_count": len(phases),
            "source_commit": registry_source_commit,
        },
        "communication_gate": communication_gate,
        "pipeline_shape": [
            {
                "phase_no": item["phase_no"],
                "name": item["name"],
                "status": item["status"],
            }
            for item in phases
        ],
        "phases": phases,
        "warnings": unique(warnings),
        "limitations": [
            "Truth shell reflects bounded local artifacts and foundation phase evidence only.",
            "No live backend bridge is wired from browser local file mode.",
            "No autonomous organ dialogue or production readiness is claimed.",
            "Communication language compliance is exposed as foundation gate truth, not runtime hard-block automation.",
        ],
        "forbidden_claims": [
            "LIVE_BACKEND_READY",
            "AUTONOMOUS_EXECUTION_READY",
            "PRODUCTION_READY",
            "LIVE_ORGAN_DIALOGUE",
        ],
        "actions": {
            "REFRESH_TRUTH_STATE": "WIRED",
            "VALIDATE_TRUTH_STATE": "WIRED",
            "READ_PHASE_REGISTRY": "WIRED",
            "READ_ACTION_REGISTRY": "WIRED",
            "READ_LATEST_REPORT_SUMMARY": "WIRED",
            "CHECK_CONTOUR_STATUS": "WIRED",
            "REGISTER_TASKPACK_SEND": "WIRED",
            "REGISTER_REPORT_BUNDLE_FETCH": "WIRED",
            "DRY_RUN_TASKPACK_SEND": "WIRED",
            "DRY_RUN_REPORT_FETCH": "WIRED",
            "REFRESH_TRANSFER_CONSOLE_VIEW": "WIRED",
            "SEND_TASKPACK_ZIP": "WIRED",
            "FETCH_REPORT_BUNDLE_ZIP": "WIRED",
            "REGISTER_TRANSFER_RESULT": "WIRED",
            "VALIDATE_TRANSFER_REQUEST": "WIRED",
            "DRY_RUN_TRANSFER": "WIRED",
        },
        "current_truth_index": current_truth_index,
    }

    return state


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_output = default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

    parser = argparse.ArgumentParser(description="Build Sanctum NG read-only state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output.resolve()

    state = build_state(repo_root, str(args.task_id), str(args.required_starting_head))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"state_written={relpath(output, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
