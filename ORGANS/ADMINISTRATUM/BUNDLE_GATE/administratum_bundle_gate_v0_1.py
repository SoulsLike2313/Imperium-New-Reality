#!/usr/bin/env python3
"""Administratum task report bundle composition gate v0.1."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-PC-ADMINISTRATUM-TASK-REPORT-BUNDLE-GATE-MATRIX-AND-PACKAGER-PC-V0_1"
MATRIX_VERSION = "0.1"
PASS = "BUNDLE_COMPOSITION_PASS"
BLOCK = "BUNDLE_COMPOSITION_BLOCK"
ADJACENT_MANIFEST = "adjacent_receipts_manifest.json"
COMPOSITION_RECEIPT = "administratum_bundle_composition_receipt.json"
MISSING_REQUEST = "missing_items_request.json"


@dataclass(frozen=True)
class MatrixClass:
    class_id: str
    required: bool
    description: str
    patterns: tuple[str, ...]
    adjacent_allowed: bool = False
    directory_name_task_id: bool = False
    produced_by_gate: bool = False


MATRIX_CLASSES: tuple[MatrixClass, ...] = (
    MatrixClass(
        "task_identity_and_report_metadata",
        True,
        "Task identity and task report metadata.",
        (
            "TASK_FOCUS_PACKET.json",
            "TASK_RECEIPT.json",
            "task_metadata.json",
            "GATE_ACK.md",
            "FINAL_REPORT.md",
            "README.md",
        ),
        directory_name_task_id=True,
    ),
    MatrixClass(
        "commit_chain_identifiers",
        True,
        "Commit chain or commit identifiers.",
        (
            "git_closure_receipt.json",
            "commit_chain_receipt.json",
            "final_closure_proof_receipt.json",
            "remote_tree_bundle_closure_receipt.json",
            "bundle_contract_receipt.json",
        ),
        adjacent_allowed=True,
    ),
    MatrixClass(
        "git_closure_and_remote_closure_proof",
        True,
        "Git closure and remote closure proof.",
        (
            "git_closure_receipt.json",
            "remote_closure_receipt.json",
            "final_remote_closure_receipt.json",
            "remote_tree_bundle_closure_receipt.json",
        ),
        adjacent_allowed=True,
    ),
    MatrixClass(
        "worktree_clean_or_explicit_cap_receipt",
        True,
        "Clean worktree proof or explicit cap receipt.",
        (
            "git_closure_receipt.json",
            "final_closure_proof_receipt.json",
            "cap_closure_receipt.json",
            "CAP_CLOSURE_RECEIPT.json",
            "servitor_control_chain_receipt.json",
        ),
        adjacent_allowed=True,
    ),
    MatrixClass(
        "scope_lock_no_ancient_mutation_receipt",
        True,
        "Scope lock or no Ancient Empire mutation receipt.",
        (
            "no_ancient_mutation_receipt.json",
            "ancient_readonly_guard_receipt.json",
            "scope_lock_receipt.json",
        ),
    ),
    MatrixClass(
        "claim_ledger",
        True,
        "Claim ledger.",
        ("CLAIM_LEDGER.json", "claim_ledger.json"),
    ),
    MatrixClass(
        "capability_split_receipt",
        True,
        "Capability split receipt.",
        ("CAPABILITY_SPLIT_RECEIPT.json", "capability_split_receipt.json"),
    ),
    MatrixClass(
        "red_team_verdict",
        True,
        "Red team verdict.",
        ("RED_TEAM_VERDICT.json", "red_team_report.md", "red_team_verdict.json"),
    ),
    MatrixClass(
        "final_owner_summary_boundary",
        True,
        "Final owner summary boundary or Officio localization reference.",
        (
            "final_owner_summary_ru.md",
            "OFFICIO_LOCALIZATION_REFERENCE.json",
            "OFFICIO_LOCALIZATION_REFERENCE.md",
            "OWNER_RESPONSE_BOUNDARY.md",
            "FINAL_REPORT.md",
            "*summary*.json",
            "*summary*.md",
        ),
    ),
    MatrixClass(
        "bundle_manifest_and_file_inventory",
        True,
        "Bundle manifest or file inventory.",
        (
            "bundle_file_inventory.json",
            "bundle_manifest.json",
            "evidence_index.json",
            "active_reports_manifest.json",
        ),
        adjacent_allowed=True,
    ),
    MatrixClass(
        "sha256_sums",
        True,
        "SHA256 sums.",
        ("sha256sums.txt", "SHA256SUMS.txt", "*.sha256"),
        adjacent_allowed=True,
    ),
    MatrixClass(
        "adjacent_receipts_manifest",
        True,
        "Adjacent receipts manifest for self-reference-limited proof files.",
        (ADJACENT_MANIFEST,),
    ),
    MatrixClass(
        "administratum_composition_receipt",
        True,
        "Administratum composition receipt.",
        (COMPOSITION_RECEIPT,),
        adjacent_allowed=True,
        produced_by_gate=True,
    ),
    MatrixClass(
        "screenshots_assets",
        False,
        "Screenshots or assets.",
        ("screenshots/*", "assets/*", "*.png", "*.jpg", "*.jpeg", "*.webp"),
    ),
    MatrixClass(
        "web_research_dossier",
        False,
        "Web research dossier.",
        ("web_research_dossier.*", "source_index.*", "*SOURCE_INDEX*"),
    ),
    MatrixClass(
        "inquisition_review",
        False,
        "Inquisition review.",
        ("INQUISITION_REVIEW.*", "*inquisition*review*", "*fake_green*"),
    ),
    MatrixClass(
        "speculum_review",
        False,
        "Speculum review.",
        ("SPECULUM_REVIEW.*", "*speculum*review*"),
    ),
    MatrixClass(
        "mechanicus_tool_receipts",
        False,
        "Mechanicus tool or candidate receipts.",
        ("MECHANICUS_*.json", "*mechanicus*.json", "validation_run_receipt.json"),
    ),
    MatrixClass(
        "performance_cost_kpd_receipts",
        False,
        "Performance, cost, or KPD receipts.",
        ("*performance*.json", "*cost*.json", "*KPD*.json", "*kpd*.json"),
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def find_repo_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if all((candidate / marker).is_file() for marker in ("AGENTS.md", "EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md")):
            return candidate
    raise RuntimeError("New Reality root markers not found from path: " + str(start))


def ensure_under(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve()
    resolved = candidate.resolve()
    if resolved == resolved_root or resolved_root in resolved.parents:
        return resolved
    raise RuntimeError(f"refusing path outside New Reality root: {resolved}")


def load_adjacent_manifest(report_dir: Path) -> dict[str, Any]:
    path = report_dir / ADJACENT_MANIFEST
    if not path.is_file():
        return {"adjacent_files": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "adjacent_files": [],
            "manifest_parse_error": str(exc),
        }
    if not isinstance(payload, dict):
        return {"adjacent_files": [], "manifest_parse_error": "manifest root is not an object"}
    payload.setdefault("adjacent_files", [])
    return payload


def glob_matches(report_dir: Path, patterns: tuple[str, ...]) -> list[str]:
    matches: set[str] = set()
    for pattern in patterns:
        for path in report_dir.glob(pattern):
            if path.is_file():
                matches.add(path.relative_to(report_dir).as_posix())
    return sorted(matches)


def adjacent_matches(report_dir: Path, manifest: dict[str, Any], class_id: str) -> list[str]:
    matches: list[str] = []
    for entry in manifest.get("adjacent_files", []):
        if not isinstance(entry, dict):
            continue
        class_ids = entry.get("class_ids", [])
        rel_path = str(entry.get("path", ""))
        if class_id not in class_ids or not rel_path:
            continue
        if (report_dir / rel_path).is_file():
            matches.append(rel_path.replace("\\", "/"))
    return sorted(set(matches))


def evaluate_report(
    report_dir: Path,
    *,
    task_id: str,
    receipt_path: Path | None = None,
) -> dict[str, Any]:
    repo_root = find_repo_root(report_dir)
    report_dir = ensure_under(repo_root, report_dir)
    manifest = load_adjacent_manifest(report_dir)
    class_results: list[dict[str, Any]] = []
    missing_required: list[str] = []

    for item in MATRIX_CLASSES:
        actual = glob_matches(report_dir, item.patterns)
        if item.directory_name_task_id and report_dir.name.startswith("TASK-"):
            actual.append(f"{report_dir.name}/")
        if item.produced_by_gate and receipt_path is not None:
            if ensure_under(repo_root, receipt_path).parent == report_dir:
                actual.append(receipt_path.name)
        adjacent = adjacent_matches(report_dir, manifest, item.class_id) if item.adjacent_allowed else []
        present = bool(actual or adjacent)
        if item.required and not present:
            missing_required.append(item.class_id)
        class_results.append(
            {
                "class_id": item.class_id,
                "required": item.required,
                "present": present,
                "actual_matches": sorted(set(actual)),
                "adjacent_matches": adjacent,
                "description": item.description,
            }
        )

    verdict = PASS if not missing_required else BLOCK
    return {
        "verdict": verdict,
        "task_id": task_id,
        "matrix_version": MATRIX_VERSION,
        "checked_path": to_posix(report_dir),
        "missing_required_items": missing_required,
        "bundle_created": False,
        "timestamp_utc": utc_now(),
        "required_class_count": sum(1 for item in MATRIX_CLASSES if item.required),
        "present_required_class_count": sum(
            1 for row in class_results if row["required"] and row["present"]
        ),
        "class_results": class_results,
        "adjacent_manifest_path": to_posix(report_dir / ADJACENT_MANIFEST),
        "adjacent_manifest_parse_error": manifest.get("manifest_parse_error", ""),
        "notes": "V0.1 composition check only; no semantic truth admission is claimed.",
    }


def build_missing_request(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": BLOCK,
        "task_id": result["task_id"],
        "matrix_version": MATRIX_VERSION,
        "checked_path": result["checked_path"],
        "missing_required_items": result["missing_required_items"],
        "required_action": "Add missing report bundle file classes and resubmit to Administratum.",
        "timestamp_utc": utc_now(),
    }


def write_gate_outputs(
    result: dict[str, Any],
    *,
    receipt_path: Path,
    missing_request_path: Path,
    bundle_created: bool = False,
    bundle_path: Path | None = None,
    bundle_sha256: str = "",
) -> dict[str, Any]:
    receipt = dict(result)
    receipt["bundle_created"] = bundle_created
    if bundle_path is not None:
        receipt["bundle_path"] = to_posix(bundle_path)
    if bundle_sha256:
        receipt["bundle_sha256"] = bundle_sha256
    write_json(receipt_path, receipt)
    if receipt["verdict"] == BLOCK:
        missing = build_missing_request(receipt)
        write_json(missing_request_path, missing)
        receipt["missing_items_request_path"] = to_posix(missing_request_path)
    return receipt


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Administratum bundle composition gate v0.1.")
    parser.add_argument("--report-dir", required=True, help="Task report directory to check.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT, help="Task ID for receipts.")
    parser.add_argument(
        "--receipt-out",
        default="",
        help="Composition receipt path. Defaults to report-dir/administratum_bundle_composition_receipt.json.",
    )
    parser.add_argument(
        "--missing-out",
        default="",
        help="Missing items request path. Defaults to report-dir/missing_items_request.json.",
    )
    parser.add_argument("--bundle-created", action="store_true", help="Mark receipt as bundle-created.")
    parser.add_argument("--bundle-path", default="", help="Bundle path to record.")
    parser.add_argument("--bundle-sha256", default="", help="Bundle SHA256 to record.")
    parser.add_argument(
        "--allow-block-exit-zero",
        action="store_true",
        help="Return exit code 0 even when the gate blocks.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report_dir = Path(args.report_dir)
    repo_root = find_repo_root(report_dir)
    report_dir = ensure_under(repo_root, report_dir)
    receipt_path = ensure_under(
        repo_root,
        Path(args.receipt_out) if args.receipt_out else report_dir / COMPOSITION_RECEIPT,
    )
    missing_path = ensure_under(
        repo_root,
        Path(args.missing_out) if args.missing_out else report_dir / MISSING_REQUEST,
    )
    bundle_path = ensure_under(repo_root, Path(args.bundle_path)) if args.bundle_path else None
    result = evaluate_report(report_dir, task_id=args.task_id, receipt_path=receipt_path)
    receipt = write_gate_outputs(
        result,
        receipt_path=receipt_path,
        missing_request_path=missing_path,
        bundle_created=args.bundle_created,
        bundle_path=bundle_path,
        bundle_sha256=args.bundle_sha256,
    )
    print(json.dumps(receipt, ensure_ascii=True, indent=2))
    if receipt["verdict"] == BLOCK and not args.allow_block_exit_zero:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
