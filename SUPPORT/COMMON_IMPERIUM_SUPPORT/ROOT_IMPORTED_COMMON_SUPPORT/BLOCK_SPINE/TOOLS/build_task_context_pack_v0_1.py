#!/usr/bin/env python3
"""Build a compact task context pack from route manifest and organ digests."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
from typing import Dict, List, Sequence


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_route_manifest(repo_root: pathlib.Path, task_id: str, explicit: str | None) -> pathlib.Path:
    if explicit:
        path = (repo_root / explicit).resolve() if not explicit.startswith("/") else pathlib.Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f"Route manifest not found: {path}")
        return path

    path = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
        / task_id
        / "TASK_ROUTE_MANIFEST.json"
    )
    if path.is_file():
        return path

    candidates = sorted(
        (repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED").glob(
            "*/TASK_ROUTE_MANIFEST.json"
        )
    )
    for candidate in candidates:
        try:
            if load_json(candidate).get("task_id") == task_id:
                return candidate
        except Exception:
            continue

    raise FileNotFoundError("Unable to locate TASK_ROUTE_MANIFEST.json for provided task_id")


def extract_organs(route_manifest: dict) -> List[str]:
    organs = route_manifest.get("required_organs") or []
    if organs:
        return organs

    discovered = []
    for entry in route_manifest.get("read_order", []):
        m = re.search(r"ORGANS/([A-Z_]+)/", entry)
        if m:
            discovered.append(m.group(1))

    # keep unique and stable order
    seen = set()
    result = []
    for organ in discovered:
        if organ not in seen:
            seen.add(organ)
            result.append(organ)
    return result


def parse_output_requirements(md_path: pathlib.Path) -> tuple[list[str], list[str]]:
    if not md_path.is_file():
        return [], []

    expected_outputs: list[str] = []
    required_receipts: list[str] = []

    lines = md_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("- "):
            continue
        item = line[2:].strip().strip("`")
        if not item:
            continue
        expected_outputs.append(item)
        lower = item.lower()
        if "receipt" in lower or "ledger" in lower or "verdict" in lower:
            required_receipts.append(item)

    return expected_outputs, required_receipts


def unique(items: Sequence[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def read_text_len(path: pathlib.Path) -> int:
    if not path.is_file():
        return 0
    try:
        return len(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return len(path.read_bytes())


def build_context_pack(repo_root: pathlib.Path, task_id: str, route_manifest_path: pathlib.Path) -> dict:
    route = load_json(route_manifest_path)
    required_organs = extract_organs(route)

    mandatory_context = [
        "AGENTS.md",
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md",
    ]
    optional_context: list[str] = []
    protected_zones: Dict[str, List[str]] = {}
    warnings: list[str] = []

    read_order = route.get("read_order", [])
    mandatory_context.extend(read_order)

    for organ in required_organs:
        digest = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/BLOCK/CONTEXT_DIGEST_V0_1.md"
        compact = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/BLOCK/READ_FIRST_COMPACT.md"
        passport_json = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_V0_1.json"
        passport_md = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_V0_1.md"

        mandatory_context.extend([digest, compact, passport_json])
        optional_context.extend([passport_md, f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/REPORTS/"])

        passport_path = repo_root / passport_json
        if passport_path.is_file():
            try:
                protected_zones[organ] = load_json(passport_path).get("protected_zones", [])
            except Exception:
                protected_zones[organ] = []
                warnings.append(f"Failed to parse passport json for {organ}")
        else:
            protected_zones[organ] = []
            warnings.append(f"Missing passport json for {organ}")

    taskpack_root = route_manifest_path.parent / "EXTRACTED"
    output_req_md = taskpack_root / "OUTPUT_REQUIREMENTS.md"
    expected_outputs, required_receipts = parse_output_requirements(output_req_md)

    mandatory_context = unique(mandatory_context)
    optional_context = unique(optional_context)

    existing_mandatory_files = [p for p in mandatory_context if (repo_root / p).is_file()]
    estimated_file_count = len(existing_mandatory_files)
    estimated_character_count = sum(read_text_len(repo_root / p) for p in existing_mandatory_files)

    for path in mandatory_context:
        if not (repo_root / path).exists():
            warnings.append(f"Missing mandatory path: {path}")

    allowed_tools_placeholder = [
        {
            "tool_name": "LOCAL_SCRIPT_FIRST",
            "status": "REQUIRED",
            "notes": "Prefer local scripts and replayable validators before agent-only reasoning.",
        },
        {
            "tool_name": "LOCAL_MANUAL_COMMAND",
            "status": "ALLOWED",
            "notes": "Use explicit command receipts when script-first is unavailable.",
        },
        {
            "tool_name": "EXTERNAL_RESEARCH",
            "status": "FORBIDDEN_IN_THIS_TASK",
            "notes": "Task scope is local block-spine foundation only.",
        },
    ]

    return {
        "schema_version": "0.1",
        "task_id": task_id,
        "target_contour": route.get("target_contour", "VM3"),
        "route_manifest_path": str(route_manifest_path.relative_to(repo_root)),
        "required_organs": required_organs,
        "mandatory_context": mandatory_context,
        "optional_context": optional_context,
        "protected_zones": protected_zones,
        "allowed_tools_placeholder": allowed_tools_placeholder,
        "expected_outputs": expected_outputs,
        "required_receipts": unique(required_receipts),
        "route_read_order": read_order,
        "estimated_file_count": estimated_file_count,
        "estimated_character_count": estimated_character_count,
        "generation_receipt": {
            "generated_at_utc": utc_now(),
            "generator": "build_task_context_pack_v0_1.py",
            "warnings": warnings,
        },
    }


def write_outputs(output_dir: pathlib.Path, context_pack: dict) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pack_path = output_dir / "task_context_pack_v0_1.json"
    report_path = output_dir / "context_pack_builder_report.md"
    receipt_path = output_dir / "context_pack_builder_receipt.json"

    pack_path.write_text(json.dumps(context_pack, indent=2) + "\n", encoding="utf-8")

    report = []
    report.append("# Context Pack Builder Report")
    report.append("")
    report.append(f"Task ID: `{context_pack['task_id']}`")
    report.append(f"Target contour: `{context_pack['target_contour']}`")
    report.append(f"Route manifest: `{context_pack['route_manifest_path']}`")
    report.append("")
    report.append("## Metrics")
    report.append("")
    report.append(f"- mandatory_context_count: {len(context_pack['mandatory_context'])}")
    report.append(f"- optional_context_count: {len(context_pack['optional_context'])}")
    report.append(f"- estimated_file_count: {context_pack['estimated_file_count']}")
    report.append(f"- estimated_character_count: {context_pack['estimated_character_count']}")
    report.append("")
    report.append("## Required organs")
    report.append("")
    for organ in context_pack["required_organs"]:
        report.append(f"- {organ}")
    report.append("")
    report.append("## Warnings")
    report.append("")
    warnings = context_pack["generation_receipt"]["warnings"]
    if warnings:
        for warning in warnings:
            report.append(f"- {warning}")
    else:
        report.append("- none")

    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    receipt = {
        "generated_at_utc": utc_now(),
        "task_id": context_pack["task_id"],
        "context_pack_path": str(pack_path),
        "report_path": str(report_path),
        "mandatory_context_count": len(context_pack["mandatory_context"]),
        "optional_context_count": len(context_pack["optional_context"]),
        "estimated_file_count": context_pack["estimated_file_count"],
        "estimated_character_count": context_pack["estimated_character_count"],
        "warnings": warnings,
        "verdict": "PASS_WITH_WARNINGS" if warnings else "PASS",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return pack_path, report_path, receipt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build task context pack")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--route-manifest", default=None)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    repo_root = pathlib.Path(args.repo_root).resolve()
    route_manifest_path = find_route_manifest(repo_root, args.task_id, args.route_manifest)
    context_pack = build_context_pack(repo_root, args.task_id, route_manifest_path)
    write_outputs(pathlib.Path(args.output_dir), context_pack)


if __name__ == "__main__":
    main()
