#!/usr/bin/env python3
"""Build NewGen Visual Brain Task Corridor V0.1 generated state."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-VISUAL-BRAIN-TASK-CORRIDOR-PC-V0_1"
INPUT_DEFAULTS = {
    "transition": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1/TASK_STATE_TRANSITION_PROPOSAL.generated.json",
    "evidence_index": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1/EVIDENCE_REPLAY_INDEX.generated.json",
    "scope_merge": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-8-ORGAN-SCOPING-CORRIDOR-PC-V0_1/ORGAN_SCOPE_MERGE_RECORD.generated.json",
    "servitor_session": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/SERVITOR_EXECUTION_SESSION.generated.json",
    "run_record": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/RUN_RECORD_001.generated.json",
    "rerun_decision": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/RERUN_DECISION_RECORD.generated.json",
    "formation_record": "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/EXAMPLES/SAMPLE_TASK_FORMATION_RECORD_V0_1.json",
    "task_kernel": "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json",
}

ORGANS = [
    ("OFFICIO_AGENTIS", "officio_agentis", "Officio Agentis"),
    ("DOCTRINARIUM", "doctrinarium", "Doctrinarium"),
    ("ADMINISTRATUM", "administratum", "Administratum"),
    ("MECHANICUS", "mechanicus", "Mechanicus"),
    ("INQUISITION", "inquisition", "Inquisition"),
    ("STRATEGIUM", "strategium", "Strategium"),
    ("SCHOLA_IMPERIALIS", "schola_imperialis", "Schola Imperialis"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Visual Brain Task Corridor V0.1 state.")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument(
        "--out-path",
        default="IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/TASK_CORRIDOR_V0_1/data/visual_brain_task_corridor_state.generated.json",
    )
    parser.add_argument("--transition-path", default=INPUT_DEFAULTS["transition"])
    parser.add_argument("--evidence-index-path", default=INPUT_DEFAULTS["evidence_index"])
    parser.add_argument("--scope-merge-path", default=INPUT_DEFAULTS["scope_merge"])
    parser.add_argument("--servitor-session-path", default=INPUT_DEFAULTS["servitor_session"])
    parser.add_argument("--run-record-path", default=INPUT_DEFAULTS["run_record"])
    parser.add_argument("--rerun-decision-path", default=INPUT_DEFAULTS["rerun_decision"])
    parser.add_argument("--formation-record-path", default=INPUT_DEFAULTS["formation_record"])
    parser.add_argument("--task-kernel-path", default=INPUT_DEFAULTS["task_kernel"])
    return parser.parse_args()


def read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    if not path.exists():
        return None, "MISSING"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, "READ_ERROR"
    if isinstance(data, dict):
        return data, "READ"
    return None, "READ_ERROR"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def to_repo_posix(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return path.resolve().as_posix()


def evidence_lookup(evidence_index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    items = evidence_index.get("evidence_items")
    if not isinstance(items, list):
        return result
    for item in items:
        if isinstance(item, dict):
            key = str(item.get("kind", "")).strip()
            if key:
                result[key] = item
    return result


def proved_status(evidence_ref: str, fallback_status: str) -> str:
    if evidence_ref.strip():
        return "PROVED_BY_RECEIPT"
    return fallback_status


def make_warnings(source_records: list[dict[str, str]]) -> list[str]:
    warnings = [
        "READ_ONLY_LAB",
        "FOUNDATION_ONLY",
        "NO LIVE BACKEND",
        "NO LIVE AUTONOMOUS ORGAN DIALOGUE PROVEN",
        "GREEN REQUIRES RECEIPT",
    ]
    for record in source_records:
        if record["status"] != "READ":
            warnings.append(f"MISSING_INPUT_WARN:{record['source_id']}")
    return sorted(set(warnings))


def build_nodes(
    source_data: dict[str, dict[str, Any] | None],
    source_status: dict[str, str],
    evidence_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    task_kernel_evid = evidence_map.get("TASK_KERNEL", {})
    scope_evid = evidence_map.get("ORGAN_SCOPE_MERGE_RECORD", {})
    session_evid = evidence_map.get("SERVITOR_SESSION", {})
    run_evid = evidence_map.get("RUN_RECORD", {})
    rerun_evid = evidence_map.get("RERUN_DECISION", {})

    owner_evidence_id = str(task_kernel_evid.get("evidence_id", "")).strip()
    owner_status = "FOUNDATION_ONLY"
    if source_status["task_kernel"] == "READ":
        owner_status = proved_status(owner_evidence_id, "FOUNDATION_ONLY")
    elif source_status["task_kernel"] != "READ":
        owner_status = "MISSING_INPUT_WARN"

    nodes.append(
        {
            "node_id": "owner_intent",
            "label": "Owner Intent",
            "kind": "OWNER",
            "status": owner_status,
            "evidence_ref": owner_evidence_id,
            "notes": ["Owner intent is derived from task kernel/formation receipts."],
        }
    )

    formation_id = ""
    formation = source_data.get("formation_record")
    if isinstance(formation, dict):
        formation_id = str(formation.get("formation_id", "")).strip()
    astro_status = "FOUNDATION_ONLY"
    if source_status["formation_record"] != "READ":
        astro_status = "MISSING_INPUT_WARN"
    nodes.append(
        {
            "node_id": "astronomicon",
            "label": "Astronomicon Formation",
            "kind": "ORGAN",
            "status": astro_status,
            "evidence_ref": formation_id,
            "notes": ["Formation record is foundation sample unless upgraded by live receipts."],
        }
    )

    scope_status = source_status["scope_merge"]
    scope_data = source_data.get("scope_merge") or {}
    packet_sources = scope_data.get("packet_sources")
    packet_map: dict[str, str] = {}
    if isinstance(packet_sources, list):
        for item in packet_sources:
            if isinstance(item, dict):
                packet_map[str(item.get("organ_id", "")).upper()] = str(item.get("source_type", ""))

    for organ_id, node_id, label in ORGANS:
        source_type = packet_map.get(organ_id, "")
        organ_status = "FOUNDATION_ONLY"
        if scope_status != "READ":
            organ_status = "MISSING_INPUT_WARN"
        elif source_type == "LIVE_AGENT_RESPONSE":
            organ_status = "PARTIAL"
        evidence_ref = str(scope_evid.get("evidence_id", "")).strip()
        nodes.append(
            {
                "node_id": node_id,
                "label": label,
                "kind": "ORGAN",
                "status": organ_status,
                "evidence_ref": evidence_ref,
                "notes": [f"Scope source_type={source_type or 'UNKNOWN'}."],
            }
        )

    session_status = source_status["servitor_session"]
    run_status = source_status["run_record"]
    rerun_status = source_status["rerun_decision"]
    servitor_node_status = "FOUNDATION_ONLY"
    if session_status != "READ" or run_status != "READ":
        servitor_node_status = "MISSING_INPUT_WARN"
    else:
        servitor_node_status = proved_status(str(session_evid.get("evidence_id", "")), "FOUNDATION_ONLY")
    nodes.append(
        {
            "node_id": "servitor_core",
            "label": "Servitor Execution Core",
            "kind": "SERVITOR",
            "status": servitor_node_status,
            "evidence_ref": str(session_evid.get("evidence_id", "")).strip(),
            "notes": ["Run/rerun records are deterministic foundation records."],
        }
    )

    binder_status = "FOUNDATION_ONLY"
    if source_status["transition"] != "READ" or source_status["evidence_index"] != "READ":
        binder_status = "MISSING_INPUT_WARN"
    else:
        binder_status = proved_status(str(run_evid.get("evidence_id", "")), "FOUNDATION_ONLY")
    nodes.append(
        {
            "node_id": "evidence_binder",
            "label": "Evidence Binder",
            "kind": "BINDER",
            "status": binder_status,
            "evidence_ref": str(run_evid.get("evidence_id", "")).strip(),
            "notes": ["State transition and replay index are bound here."],
        }
    )

    verdict_status = "PARTIAL"
    transition = source_data.get("transition")
    if isinstance(transition, dict):
        proposed = str(transition.get("proposed_task_state", ""))
        if proposed in {"BLOCKED_NEEDS_OWNER"}:
            verdict_status = "BLOCKED"
        elif proposed in {"PASSED_STRICT"}:
            verdict_status = "PROVED_BY_RECEIPT" if rerun_status == "READ" else "PARTIAL"
    if rerun_status != "READ":
        verdict_status = "MISSING_INPUT_WARN"
    nodes.append(
        {
            "node_id": "owner_verdict_gate",
            "label": "Owner Verdict Gate",
            "kind": "OWNER_GATE",
            "status": verdict_status,
            "evidence_ref": str(rerun_evid.get("evidence_id", "")).strip(),
            "notes": ["Owner acceptance remains external to V0.1 static corridor lab."],
        }
    )
    return nodes


def build_edges(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids = {str(node["node_id"]): node for node in nodes}

    def edge_status(source_id: str, target_id: str) -> str:
        source = ids[source_id]
        target = ids[target_id]
        if "MISSING_INPUT_WARN" in {source["status"], target["status"]}:
            return "MISSING_INPUT_WARN"
        if "BLOCKED" in {source["status"], target["status"]}:
            return "BLOCKED"
        if "PROVED_BY_RECEIPT" in {source["status"], target["status"]}:
            return "PROVED_BY_RECEIPT"
        return "FOUNDATION_ONLY"

    line = [
        ("owner_intent", "astronomicon"),
        ("astronomicon", "officio_agentis"),
        ("astronomicon", "doctrinarium"),
        ("astronomicon", "administratum"),
        ("astronomicon", "mechanicus"),
        ("astronomicon", "inquisition"),
        ("astronomicon", "strategium"),
        ("astronomicon", "schola_imperialis"),
        ("officio_agentis", "servitor_core"),
        ("doctrinarium", "servitor_core"),
        ("administratum", "servitor_core"),
        ("mechanicus", "servitor_core"),
        ("inquisition", "servitor_core"),
        ("strategium", "servitor_core"),
        ("schola_imperialis", "servitor_core"),
        ("servitor_core", "evidence_binder"),
        ("evidence_binder", "owner_verdict_gate"),
    ]
    edges: list[dict[str, Any]] = []
    for idx, (src, dst) in enumerate(line, start=1):
        source_evidence = str(ids[src].get("evidence_ref", "")).strip()
        target_evidence = str(ids[dst].get("evidence_ref", "")).strip()
        edges.append(
            {
                "edge_id": f"edge-{idx:03d}",
                "from": src,
                "to": dst,
                "status": edge_status(src, dst),
                "evidence_ref": source_evidence or target_evidence,
            }
        )
    return edges


def build_run_rail(
    source_data: dict[str, dict[str, Any] | None],
    source_status: dict[str, str],
    evidence_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    run_record = source_data.get("run_record") or {}
    rerun = source_data.get("rerun_decision") or {}
    session = source_data.get("servitor_session") or {}

    session_label = str(session.get("status", "MISSING"))
    run_label = str(run_record.get("status", "MISSING"))
    rerun_label = str(rerun.get("decision", "MISSING"))

    def status_for(key: str, status_text: str) -> str:
        if source_status[key] != "READ":
            return "MISSING_INPUT_WARN"
        if status_text in {"PASSED_WITH_EVIDENCE", "READY_FOR_RUN"}:
            return "PROVED_BY_RECEIPT"
        if status_text in {"BLOCKED", "FAILED_CLASSIFIED"}:
            return "BLOCKED"
        return "PARTIAL"

    return [
        {
            "step_id": "session",
            "label": "Servitor Session",
            "status": status_for("servitor_session", session_label),
            "evidence_ref": str(evidence_map.get("SERVITOR_SESSION", {}).get("evidence_id", "")).strip(),
            "details": session_label,
        },
        {
            "step_id": "run",
            "label": "Run Record",
            "status": status_for("run_record", run_label),
            "evidence_ref": str(evidence_map.get("RUN_RECORD", {}).get("evidence_id", "")).strip(),
            "details": run_label,
        },
        {
            "step_id": "rerun",
            "label": "Rerun Decision",
            "status": status_for("rerun_decision", rerun_label),
            "evidence_ref": str(evidence_map.get("RERUN_DECISION", {}).get("evidence_id", "")).strip(),
            "details": rerun_label,
        },
    ]


def build_evidence_constellation(
    source_data: dict[str, dict[str, Any] | None],
    nodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_index = source_data.get("evidence_index") or {}
    items = evidence_index.get("evidence_items")
    node_map: dict[str, list[str]] = {}
    for node in nodes:
        evidence_ref = str(node.get("evidence_ref", "")).strip()
        if evidence_ref:
            node_map.setdefault(evidence_ref, []).append(str(node["node_id"]))

    if isinstance(items, list) and items:
        output: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            evid = str(item.get("evidence_id", "")).strip()
            output.append(
                {
                    "evidence_id": evid or "EVID-UNKNOWN",
                    "kind": str(item.get("kind", "UNKNOWN")),
                    "status": str(item.get("status", "WARN")),
                    "path_or_note": str(item.get("path_or_note", "")),
                    "linked_nodes": sorted(set(node_map.get(evid, []))),
                }
            )
        if output:
            return output

    fallback: list[dict[str, Any]] = []
    for idx, node in enumerate(nodes, start=1):
        evidence_ref = str(node.get("evidence_ref", "")).strip()
        if not evidence_ref:
            continue
        fallback.append(
            {
                "evidence_id": evidence_ref,
                "kind": "NODE_REFERENCE",
                "status": "WARN",
                "path_or_note": f"fallback:{node['node_id']}",
                "linked_nodes": [str(node["node_id"])],
            }
        )
    if not fallback:
        fallback.append(
            {
                "evidence_id": "EVID-MISSING",
                "kind": "MISSING_INPUT_WARN",
                "status": "MISSING",
                "path_or_note": "No evidence sources were readable.",
                "linked_nodes": [],
            }
        )
    return fallback


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_path = (repo_root / args.out_path).resolve()

    path_map = {
        "transition": (repo_root / args.transition_path).resolve(),
        "evidence_index": (repo_root / args.evidence_index_path).resolve(),
        "scope_merge": (repo_root / args.scope_merge_path).resolve(),
        "servitor_session": (repo_root / args.servitor_session_path).resolve(),
        "run_record": (repo_root / args.run_record_path).resolve(),
        "rerun_decision": (repo_root / args.rerun_decision_path).resolve(),
        "formation_record": (repo_root / args.formation_record_path).resolve(),
        "task_kernel": (repo_root / args.task_kernel_path).resolve(),
    }

    source_data: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    source_records: list[dict[str, str]] = []
    for source_id, path in path_map.items():
        data, status = read_json(path)
        source_data[source_id] = data
        source_status[source_id] = status
        source_records.append(
            {
                "source_id": source_id,
                "path": to_repo_posix(path, repo_root),
                "status": status,
            }
        )

    transition = source_data.get("transition") or {}
    evidence_index = source_data.get("evidence_index") or {}
    task_id = str(transition.get("task_id", args.task_id))
    visual_state_id = f"VB-{args.task_id}-STATE"

    evidence_map = evidence_lookup(evidence_index)
    nodes = build_nodes(source_data, source_status, evidence_map)
    edges = build_edges(nodes)
    run_rail = build_run_rail(source_data, source_status, evidence_map)
    evidence_constellation = build_evidence_constellation(source_data, nodes)

    visual_state = {
        "schema_version": "0.1",
        "visual_state_id": visual_state_id,
        "mode": "READ_ONLY_LAB",
        "foundation_only": True,
        "production_ready": False,
        "live_autonomous_organ_dialogue_proven": False,
        "task_ref": {
            "task_id": args.task_id,
            "source_task_id": task_id,
            "state_ref": to_repo_posix(path_map["transition"], repo_root),
            "evidence_ref": to_repo_posix(path_map["evidence_index"], repo_root),
        },
        "nodes": nodes,
        "edges": edges,
        "run_rail": run_rail,
        "evidence_constellation": evidence_constellation,
        "warnings": make_warnings(source_records),
        "forbidden_claims": [
            "production orchestration is ready",
            "live autonomous execution is proven",
            "live organ dialogue is proven",
            "full visual brain readiness is proven",
        ],
        "source_records": source_records,
        "created_at_utc": utc_now(),
    }

    write_json(out_path, visual_state)
    print(out_path.as_posix())
    print(f"nodes={len(nodes)}")
    print(f"evidence={len(evidence_constellation)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
