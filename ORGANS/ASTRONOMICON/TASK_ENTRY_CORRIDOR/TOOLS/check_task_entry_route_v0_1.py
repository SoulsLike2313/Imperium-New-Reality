#!/usr/bin/env python3
"""Synthetic Stage1 checker for Astronomicon task-entry route and eight-organ reachability."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1"
REQUIRED_ORGANS = [
    "DOCTRINARIUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]
REQUIRED_ORGAN_PACKET_FILES = [
    "READ_FIRST_TASK_PARTICIPATION.md",
    "TASK_PARTICIPATION_CONTRACT.json",
    "ORGAN_TASK_INPUTS_OUTPUTS.json",
    "ORGAN_MATRIX_RESPONSIBILITIES.json",
    "ORGAN_TOOL_AND_RECEIPT_INVENTORY.json",
    "ORGAN_IDE_DISPLAY_MODEL.json",
    "KNOWN_GAPS_AND_NEXT_HOOKS.md",
]
REQUIRED_CORRIDOR_FILES = [
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ENTRY_CORRIDOR_CONTRACT.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ENTRY_CORRIDOR_CONTRACT.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_ADMISSION_CONTRACT.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ID_RESOLVER_CONTRACT.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/TASK_INBOX_README.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/SYNTHETIC_STAGE1_TASKPACK_REFERENCE.json",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/TASK_ID_REGISTRY_STAGE1.json",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def check_organs(repo_root: Path) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    organs_ack: dict[str, Any] = {}
    missing_organs: list[str] = []
    details: list[dict[str, Any]] = []
    for organ in REQUIRED_ORGANS:
        read_first = repo_root / "IMPERIUM_NEW_GENERATION" / "ORGANS" / organ / "READ_FIRST_GHOST_EVOLVE_PACKET.md"
        part_base = repo_root / "IMPERIUM_NEW_GENERATION" / "ORGANS" / organ / "TASK_PARTICIPATION"
        missing_files: list[str] = []
        for rel_name in REQUIRED_ORGAN_PACKET_FILES:
            if not (part_base / rel_name).exists():
                missing_files.append(str(part_base / rel_name))

        status = "ACTIVE_FOR_STAGE1" if not missing_files and read_first.exists() else "MISSING_REQUIRED_FILES"
        if status != "ACTIVE_FOR_STAGE1":
            missing_organs.append(organ)

        organs_ack[organ] = {
            "read_first_found": read_first.exists(),
            "participation_contract_found": (part_base / "TASK_PARTICIPATION_CONTRACT.json").exists(),
            "status": status,
            "missing_files_count": len(missing_files),
        }
        details.append({"organ": organ, "status": status, "missing_files": missing_files})
    return organs_ack, missing_organs, details


def check_corridor(repo_root: Path) -> tuple[list[str], list[str]]:
    missing_corridor: list[str] = []
    existing_corridor: list[str] = []
    for rel in REQUIRED_CORRIDOR_FILES:
        full = repo_root / rel
        if full.exists():
            existing_corridor.append(rel)
        else:
            missing_corridor.append(rel)
    return existing_corridor, missing_corridor


def check_taskpack_pointer(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    pointer_path = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/SYNTHETIC_STAGE1_TASKPACK_REFERENCE.json"
    )
    pointer = read_json(pointer_path)
    taskpack_path = Path(pointer["taskpack_path"])
    extracted = repo_root / pointer["extracted_reference"]
    read_order = extracted / "000_START_TASK_READ_ORDER.md"
    if not taskpack_path.exists():
        warnings.append(f"Taskpack zip path not found: {taskpack_path}")
    if not extracted.exists():
        warnings.append(f"Extracted taskpack path not found: {extracted}")
    if not read_order.exists():
        warnings.append(f"Taskpack read-order file not found: {read_order}")
    return pointer, warnings


def check_route_manifest(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    route_path = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json"
    )
    route = read_json(route_path)
    route_issues: list[str] = []
    route_organs = set(route.get("required_organs", []))
    missing = [org for org in REQUIRED_ORGANS if org not in route_organs]
    if missing:
        route_issues.append("Missing required organs in route manifest: " + ", ".join(missing))
    if route.get("task_id") != TASK_ID:
        route_issues.append("Route task_id mismatch.")
    return route, route_issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--report-root",
        default=(
            "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/"
            "TASK-NEWGEN-EIGHT-ORGAN-MOBILIZATION-AND-ASTRONOMICON-TASK-ENTRY-FORM-PC-V0_1"
        ),
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    organs_ack, missing_organs, organ_details = check_organs(repo_root)
    existing_corridor, missing_corridor = check_corridor(repo_root)
    pointer, pointer_warnings = check_taskpack_pointer(repo_root)
    route, route_issues = check_route_manifest(repo_root)

    caps = ["CAP_STAGE1_WITH_WARNINGS_ONLY"]
    if missing_organs:
        caps.append("CAP_ORGAN_SKIPPED")
        caps.append("CAP_ORGAN_FILE_DECORATIVE_NOT_USED")
    if missing_corridor:
        caps.append("CAP_ASTRONOMICON_TASK_ENTRY_MISSING")
        if any("TASK_ID_RESOLVER_CONTRACT.json" in rel for rel in missing_corridor):
            caps.append("CAP_TASK_ID_RESOLVER_MISSING")
    if pointer_warnings or route_issues:
        caps.append("CAP_SYNTHETIC_TASK_ENTRY_PROOF_MISSING")

    block_conditions = bool(missing_organs or missing_corridor or route_issues)
    verdict = "BLOCK" if block_conditions else "PASS_WITH_WARNINGS"

    ack = {
        "task_id": TASK_ID,
        "entry_mode": "ASTRONOMICON_TASK_ID_PLUS_START_TASK",
        "all_organs_checked": len(missing_organs) == 0,
        "organs": organs_ack,
        "missing_organs": missing_organs,
        "caps_triggered": caps,
        "verdict": verdict,
    }
    write_json(report_root / "all_organ_entry_ack_fixture.json", ack)

    checker_receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": now,
        "checker": "check_task_entry_route_v0_1.py",
        "required_organs": REQUIRED_ORGANS,
        "organ_details": organ_details,
        "existing_corridor_files": existing_corridor,
        "missing_corridor_files": missing_corridor,
        "taskpack_pointer": pointer,
        "taskpack_pointer_warnings": pointer_warnings,
        "route_manifest_task_id": route.get("task_id"),
        "route_manifest_issues": route_issues,
        "caps_triggered": caps,
        "final_verdict": verdict,
        "clean_pass_allowed": False,
    }
    write_json(report_root / "synthetic_task_entry_checker_receipt.json", checker_receipt)

    md = "# Synthetic Task Entry Proof Report\n\n"
    md += f"Task: `{TASK_ID}`\n"
    md += f"Timestamp: `{now}`\n\n"
    md += f"Verdict: `{verdict}`\n\n"
    md += "## Checks\n"
    md += f"- Required organs checked: `{len(REQUIRED_ORGANS)}`\n"
    md += f"- Missing organs: `{len(missing_organs)}`\n"
    md += f"- Missing corridor files: `{len(missing_corridor)}`\n"
    md += f"- Taskpack pointer warnings: `{len(pointer_warnings)}`\n"
    md += f"- Route manifest issues: `{len(route_issues)}`\n\n"
    md += "## Caps\n"
    for cap in caps:
        md += f"- `{cap}`\n"
    md += "\n## Organ details\n"
    for row in organ_details:
        md += f"- `{row['organ']}`: `{row['status']}`\n"
        if row["missing_files"]:
            for path in row["missing_files"]:
                md += f"  - missing: `{path}`\n"
    if pointer_warnings:
        md += "\n## Pointer warnings\n"
        for warn in pointer_warnings:
            md += f"- {warn}\n"
    if route_issues:
        md += "\n## Route issues\n"
        for issue in route_issues:
            md += f"- {issue}\n"
    write_text(report_root / "synthetic_task_entry_proof_report.md", md)

    print(f"checker_verdict={verdict}")
    return 1 if verdict == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
