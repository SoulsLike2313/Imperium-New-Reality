#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_ORGANS = [
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]

ALLOWED_SOURCE_TYPES = [
    "LIVE_AGENT_RESPONSE",
    "STATIC_FILE",
    "SAMPLE_PACKET",
    "FOUNDATION_STUB",
    "MISSING_IMPLEMENTATION_WARN",
]

DEFAULT_FORBIDDEN_PATHS = [
    "ORGANS/**",
    "SANCTUM/**",
    "IMPERIUM_TEST_VERSION/**",
    ".git/**",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect and merge 8-organ scoping packets in foundation mode."
    )
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument(
        "--task-id",
        default="TASK-20260521-NEWGEN-8-ORGAN-SCOPING-CORRIDOR-PC-V0_1",
    )
    parser.add_argument(
        "--formation-record",
        default="IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/EXAMPLES/SAMPLE_TASK_FORMATION_RECORD_V0_1.json",
    )
    parser.add_argument(
        "--task-kernel",
        default="IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json",
    )
    parser.add_argument(
        "--packet-set",
        default="",
        help="Optional explicit packet set path. If empty, uses task-kernel ref or default sample.",
    )
    parser.add_argument("--out-dir", required=True)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON object expected: {path.as_posix()}")
    return data


def to_posix_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.resolve().as_posix()


def to_token(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned.upper() if cleaned else "UNSPECIFIED"


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({v for v in values if isinstance(v, str) and v.strip()})


def normalize_list_field(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def detect_contour(formation_record: dict[str, Any]) -> str:
    start_block = formation_record.get("servitor_start_block")
    if isinstance(start_block, list):
        for line in start_block:
            if not isinstance(line, str):
                continue
            u = line.upper()
            if "PC" in u:
                return "PC"
            if "VM2" in u:
                return "VM2"
            if "VM3" in u:
                return "VM3"
    return "UNKNOWN"


def resolve_packet_set_path(
    repo_root: Path,
    explicit_packet_set: str,
    task_kernel: dict[str, Any],
) -> Path:
    if explicit_packet_set.strip():
        return (repo_root / explicit_packet_set).resolve()

    ref = str(task_kernel.get("organ_packet_set_ref", "")).strip()
    if ref:
        candidate = (repo_root / ref).resolve()
        if candidate.exists():
            return candidate

    return (
        repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/EXAMPLES/SAMPLE_TASK_8_ORGAN_PACKET_SET_V0_1.json"
    ).resolve()


def build_scope_request(
    task_id: str,
    contour: str,
    formation_path_rel: str,
    task_kernel_path_rel: str,
    packet_set_path_rel: str,
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "request_id": f"SCOPE-REQ-{to_token(task_id)}",
        "task_id": task_id,
        "source": {
            "contour": contour,
            "formation_record_path": formation_path_rel,
            "task_kernel_path": task_kernel_path_rel,
            "collector_mode": "FOUNDATION_V0_1",
        },
        "required_organs": REQUIRED_ORGANS,
        "scope_prompt": (
            "Collect and merge 8-organ task scope in deterministic foundation mode. "
            "Use static/sample/stub packets only; do not claim live autonomous agent communication."
        ),
        "input_artifacts": [
            formation_path_rel,
            task_kernel_path_rel,
            packet_set_path_rel,
        ],
        "truth_policy": {
            "no_fake_live_agent_claims": True,
            "stub_label_required": True,
            "allowed_source_types": ALLOWED_SOURCE_TYPES,
        },
    }


def choose_packet_source_type(packet: dict[str, Any], set_live_status: str) -> str:
    if packet.get("live_status") == "LIVE" and set_live_status == "LIVE":
        return "LIVE_AGENT_RESPONSE"
    if set_live_status in {"EXAMPLE_ONLY", "NOT_IMPLEMENTED"}:
        return "SAMPLE_PACKET"
    if set_live_status == "STUB":
        return "FOUNDATION_STUB"
    return "STATIC_FILE"


def normalize_packet(
    organ_id: str,
    task_id: str,
    packet: dict[str, Any] | None,
    source_path_rel: str,
    set_live_status: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    if packet is None:
        normalized = {
            "organ_id": organ_id,
            "task_id": task_id,
            "source_type": "FOUNDATION_STUB",
            "packet_status": "MISSING_AUTHORITY",
            "live_status": "NOT_IMPLEMENTED",
            "scope_advice": [
                f"{organ_id}: no packet source file detected for this task. Foundation stub generated."
            ],
            "required_checks": [
                "Owner decision on live adapter implementation",
                "No fake live-agent claim guard",
            ],
            "evidence_required": [
                "Foundation stub packet receipt",
                "Validator report",
            ],
            "owner_questions": [
                f"Should {organ_id} receive a dedicated live adapter in next corridor task?"
            ],
            "warnings": [
                "MISSING_IMPLEMENTATION_WARN",
                "FOUNDATION_STUB",
            ],
        }
        source = {
            "organ_id": organ_id,
            "source_type": "FOUNDATION_STUB",
            "path_or_note": "No matching packet found; deterministic foundation stub created.",
        }
        return normalized, source

    source_type = choose_packet_source_type(packet, set_live_status)
    normalized = {
        "organ_id": organ_id,
        "task_id": task_id,
        "source_type": source_type,
        "packet_status": str(packet.get("packet_status", "EXAMPLE_ONLY")),
        "live_status": str(packet.get("live_status", "EXAMPLE_ONLY")),
        "scope_advice": normalize_list_field(packet.get("scope_advice")),
        "required_checks": normalize_list_field(packet.get("required_checks")),
        "evidence_required": normalize_list_field(packet.get("evidence_required")),
        "owner_questions": normalize_list_field(packet.get("questions_for_owner")),
        "warnings": [],
    }
    if source_type != "LIVE_AGENT_RESPONSE":
        normalized["warnings"].append("NOT_LIVE_AGENT")
    if source_type in {"SAMPLE_PACKET", "FOUNDATION_STUB"}:
        normalized["warnings"].append("FOUNDATION_ONLY_SOURCE")

    source = {
        "organ_id": organ_id,
        "source_type": source_type,
        "path_or_note": source_path_rel,
    }
    return normalized, source


def collect_packets(
    task_id: str,
    packet_set: dict[str, Any],
    packet_set_path_rel: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    packet_map: dict[str, dict[str, Any]] = {}
    raw_packets = packet_set.get("packets")
    if isinstance(raw_packets, list):
        for item in raw_packets:
            if isinstance(item, dict):
                organ = str(item.get("organ_id", ""))
                if organ and organ not in packet_map:
                    packet_map[organ] = item

    set_live_status = str(packet_set.get("set_live_status", "EXAMPLE_ONLY"))
    normalized_packets: list[dict[str, Any]] = []
    packet_sources: list[dict[str, str]] = []

    for organ in REQUIRED_ORGANS:
        normalized, source = normalize_packet(
            organ_id=organ,
            task_id=task_id,
            packet=packet_map.get(organ),
            source_path_rel=packet_set_path_rel,
            set_live_status=set_live_status,
        )
        normalized_packets.append(normalized)
        packet_sources.append(source)

    return normalized_packets, packet_sources


def merge_scope(
    task_id: str,
    formation_record: dict[str, Any],
    task_kernel: dict[str, Any],
    normalized_packets: list[dict[str, Any]],
    packet_sources: list[dict[str, str]],
) -> dict[str, Any]:
    allowed_paths = unique_sorted(
        normalize_list_field(formation_record.get("allowed_paths"))
        + normalize_list_field(task_kernel.get("allowed_paths"))
    )
    forbidden_paths = unique_sorted(
        normalize_list_field(formation_record.get("forbidden_paths"))
        + normalize_list_field(task_kernel.get("forbidden_paths"))
        + DEFAULT_FORBIDDEN_PATHS
    )

    required_checks: list[str] = [
        "GATE_ACK before edits",
        "Schema parse checks",
        "8-organ coverage checks",
        "No fake live-agent claims",
    ]
    evidence_required: list[str] = [
        "OFFICIO_ROLE_ACK_OR_WARN.json",
        "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        "STEP_PROOF_RECORDS.jsonl",
        "VALIDATOR_REPORT.json",
        "FINAL_RECEIPT.json",
    ]
    owner_questions: list[str] = []
    warnings: list[str] = []

    for packet in normalized_packets:
        required_checks.extend(normalize_list_field(packet.get("required_checks")))
        evidence_required.extend(normalize_list_field(packet.get("evidence_required")))
        owner_questions.extend(normalize_list_field(packet.get("owner_questions")))
        warnings.extend(normalize_list_field(packet.get("warnings")))

    required_checks = unique_sorted(required_checks)
    evidence_required = unique_sorted(evidence_required)
    owner_questions = unique_sorted(owner_questions)
    warnings = unique_sorted(warnings)

    conflicts: list[str] = []
    forbidden_set = set(forbidden_paths)
    for path in allowed_paths:
        if path in forbidden_set:
            conflicts.append(f"Path is both allowed and forbidden: {path}")

    covered_organs = {str(item.get("organ_id", "")) for item in normalized_packets}
    missing_organs = sorted(set(REQUIRED_ORGANS).difference(covered_organs))

    has_stub = any(
        source.get("source_type") in {"FOUNDATION_STUB", "MISSING_IMPLEMENTATION_WARN"}
        for source in packet_sources
    )
    has_non_live = any(
        source.get("source_type") != "LIVE_AGENT_RESPONSE" for source in packet_sources
    )

    readiness = "READY"
    if missing_organs:
        readiness = "BLOCKED"
    elif has_stub or has_non_live:
        readiness = "FOUNDATION_ONLY"
    elif warnings:
        readiness = "READY_WITH_WARNINGS"

    truth_limitations = [
        "Foundation-only scoping corridor output.",
        "Packet sources are static/sample/stub unless explicit live receipts exist.",
        "No production live autonomous multi-organ claim.",
    ]

    if has_non_live and "NOT_LIVE_AGENT" not in warnings:
        warnings.append("NOT_LIVE_AGENT")
        warnings = unique_sorted(warnings)

    self_verdict = "STRONG"
    if missing_organs or conflicts:
        self_verdict = "FAILED"
    elif warnings:
        self_verdict = "STRONG"
    elif readiness == "READY":
        self_verdict = "PROVED"

    return {
        "schema_version": "0.1",
        "merge_id": f"SCOPE-MERGE-{to_token(task_id)}",
        "task_id": task_id,
        "packet_sources": packet_sources,
        "organ_coverage": {
            "required_count": 8,
            "covered_count": len(covered_organs.intersection(set(REQUIRED_ORGANS))),
            "missing_organs": missing_organs,
        },
        "merged_scope": {
            "allowed_paths": allowed_paths,
            "forbidden_paths": forbidden_paths,
            "required_checks": required_checks,
            "evidence_required": evidence_required,
            "owner_questions": owner_questions,
            "next_stage_recommendation": (
                "Proceed to guarded per-organ adapter planning with receipt-backed live-source policy."
                if readiness != "BLOCKED"
                else "Resolve missing organ coverage before progression."
            ),
        },
        "conflicts": conflicts,
        "warnings": warnings,
        "readiness": readiness,
        "truth_limitations": truth_limitations,
        "self_verdict": self_verdict,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    formation_path = (repo_root / args.formation_record).resolve()
    task_kernel_path = (repo_root / args.task_kernel).resolve()
    formation_record = read_json(formation_path)
    task_kernel = read_json(task_kernel_path)

    derived_task_id = str(
        formation_record.get("task_id")
        or task_kernel.get("task_id")
        or args.task_id
    ).strip()
    task_id = derived_task_id if derived_task_id else args.task_id

    packet_set_path = resolve_packet_set_path(repo_root, args.packet_set, task_kernel)
    packet_set = read_json(packet_set_path)

    formation_rel = to_posix_relative(formation_path, repo_root)
    task_kernel_rel = to_posix_relative(task_kernel_path, repo_root)
    packet_set_rel = to_posix_relative(packet_set_path, repo_root)

    scope_request = build_scope_request(
        task_id=task_id,
        contour=detect_contour(formation_record),
        formation_path_rel=formation_rel,
        task_kernel_path_rel=task_kernel_rel,
        packet_set_path_rel=packet_set_rel,
    )

    normalized_packets, packet_sources = collect_packets(
        task_id=task_id,
        packet_set=packet_set,
        packet_set_path_rel=packet_set_rel,
    )

    merge_record = merge_scope(
        task_id=task_id,
        formation_record=formation_record,
        task_kernel=task_kernel,
        normalized_packets=normalized_packets,
        packet_sources=packet_sources,
    )

    packets_generated = {
        "schema_version": "0.1",
        "task_id": task_id,
        "set_live_status": "FOUNDATION_STUB",
        "required_organs": REQUIRED_ORGANS,
        "packet_sources": packet_sources,
        "packets": normalized_packets,
        "truth_note": "Generated in foundation mode; no live autonomous organ agent communication claimed.",
    }

    scope_request_path = out_dir / "SCOPE_REQUEST.generated.json"
    packets_path = out_dir / "ORGAN_PACKETS.generated.json"
    merge_path = out_dir / "ORGAN_SCOPE_MERGE_RECORD.generated.json"

    scope_request_path.write_text(
        json.dumps(scope_request, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    packets_path.write_text(
        json.dumps(packets_generated, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    merge_path.write_text(
        json.dumps(merge_record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(scope_request_path.as_posix())
    print(packets_path.as_posix())
    print(merge_path.as_posix())
    print(f"readiness={merge_record['readiness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
