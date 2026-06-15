#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inquisition Evidence Sealer Contract Gate V0.1.

Read-only gate for the Evidence Vault sealer output-root contract.
It prevents the specific destructive-mode failure where a sealer final report is
written under the buffer that --delete-buffer-after-seal is about to remove.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

SURFACE = "INQUISITION_EVIDENCE_SEALER_CONTRACT_GATE_V0_1"
VERSION = "0.1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_id(value: str) -> str:
    keep = []
    for ch in value:
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("._-") or "UNNAMED_PATCH"


def norm_abs(path: Path) -> str:
    try:
        return os.path.normcase(os.path.abspath(str(path)))
    except Exception:
        return os.path.normcase(str(path))


def path_is_inside(child: Path, parent: Path) -> bool:
    child_s = norm_abs(child)
    parent_s = norm_abs(parent)
    try:
        return os.path.commonpath([child_s, parent_s]) == parent_s
    except Exception:
        return False


def resolve_buffer(vault_root: Path, patch_id: str, buffer_path: str = "") -> Path:
    return Path(buffer_path) if buffer_path else vault_root / "buffer" / "active" / patch_id


def pack_root_for(vault_root: Path, patch_id: str) -> Path:
    now = datetime.now(timezone.utc)
    return vault_root / "packs" / f"{now.year:04d}" / f"{now.month:02d}" / safe_id(patch_id)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def contract_gate(args: argparse.Namespace) -> Dict[str, Any]:
    vault_root = Path(args.vault_root)
    buffer_path = resolve_buffer(vault_root, args.patch_id, args.buffer_path)
    pack_root = Path(args.pack_root) if args.pack_root else pack_root_for(vault_root, args.patch_id)

    if args.out_root:
        out_root = Path(args.out_root)
        output_root_policy = "EXPLICIT_OPERATOR_ROOT"
    elif args.delete_buffer_after_seal:
        out_root = pack_root / "SEALER_REPORT"
        output_root_policy = "DEFAULT_TO_SEALED_PACK_REPORT_ROOT"
    else:
        out_root = vault_root / "reports"
        output_root_policy = "DEFAULT_TO_VAULT_REPORTS"

    out_inside_buffer = path_is_inside(out_root, buffer_path)
    out_inside_pack = path_is_inside(out_root, pack_root)
    out_inside_logs = path_is_inside(out_root, vault_root / "logs" / "sealer")
    out_inside_reports = path_is_inside(out_root, vault_root / "reports")

    if args.delete_buffer_after_seal and out_inside_buffer:
        status = "BLOCK_UNSAFE_SEALER_REPORT_ROOT"
        severity = "CRITICAL"
        blocking = True
        recommendation = "Use default report root, sealed pack folder, or $VAULT/logs/sealer; never write final sealer report into a buffer that will be deleted."
    elif args.delete_buffer_after_seal and not (out_inside_pack or out_inside_logs or out_inside_reports):
        status = "WARN_NON_CANONICAL_SEALER_REPORT_ROOT"
        severity = "WARNING"
        blocking = False
        recommendation = "Prefer sealed pack report root or $VAULT/logs/sealer for canonical proof retention."
    else:
        status = "PASS_OUTPUT_ROOT_CONTRACT"
        severity = "INFO"
        blocking = False
        recommendation = "Continue."

    return {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "contract_gate",
        "blocking_gate": blocking,
        "severity": severity,
        "patch_id": args.patch_id,
        "delete_buffer_after_seal": bool(args.delete_buffer_after_seal),
        "explicit_out_root": bool(args.out_root),
        "output_root_policy": output_root_policy,
        "buffer_path": str(buffer_path),
        "pack_root": str(pack_root),
        "resolved_output_root": str(out_root),
        "checks": {
            "output_root_inside_buffer": out_inside_buffer,
            "output_root_inside_pack_root": out_inside_pack,
            "output_root_inside_vault_logs": out_inside_logs,
            "output_root_inside_vault_reports": out_inside_reports,
        },
        "recommended_next_action": recommendation,
    }


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def health_gate(args: argparse.Namespace) -> Dict[str, Any]:
    vault_root = Path(args.vault_root)
    pack_root = Path(args.pack_root) if args.pack_root else pack_root_for(vault_root, args.patch_id)
    pack_path = pack_root / "EVIDENCE_PACK.zip"
    manifest_path = pack_root / "EVIDENCE_MANIFEST.json"
    machine_index_path = pack_root / "MACHINE_INDEX.json"
    owner_summary_path = pack_root / "OWNER_SUMMARY_RU.md"
    sha_path = pack_root / "SHA256SUMS.txt"
    sealer_report_root = pack_root / "SEALER_REPORT"

    manifest = load_json(manifest_path) if manifest_path.exists() else None
    expected_sha = (manifest or {}).get("pack_sha256") or (manifest or {}).get("sha256")
    actual_sha = sha256_file(pack_path) if pack_path.exists() else ""
    sha_matches = bool(expected_sha and actual_sha and expected_sha == actual_sha)

    required = {
        "pack_exists": pack_path.exists(),
        "manifest_exists": manifest_path.exists(),
        "machine_index_exists": machine_index_path.exists(),
        "owner_summary_exists": owner_summary_path.exists(),
        "sha256sums_exists": sha_path.exists(),
        "sha256_matches_manifest": sha_matches,
        "raw_buffer_deleted": bool((manifest or {}).get("raw_buffer_deleted")),
        "sealer_report_root_exists": sealer_report_root.exists(),
    }
    missing = [k for k, v in required.items() if not v and k != "raw_buffer_deleted" and k != "sealer_report_root_exists"]
    if missing:
        status = "FAIL_SEALED_PACK_HEALTH"
        severity = "CRITICAL"
        blocking = True
    elif not required["raw_buffer_deleted"]:
        status = "PASS_WITH_BUFFER_RETAINED"
        severity = "WARNING"
        blocking = False
    else:
        status = "PASS_SEALED_PACK_HEALTH"
        severity = "INFO"
        blocking = False

    return {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "mode": "sealed_pack_health",
        "blocking_gate": blocking,
        "severity": severity,
        "patch_id": args.patch_id,
        "pack_root": str(pack_root),
        "health": required,
        "missing_or_invalid": missing,
        "manifest_digest": {
            "evidence_pack_id": (manifest or {}).get("evidence_pack_id"),
            "retention_class": (manifest or {}).get("retention_class"),
            "storage_zone": (manifest or {}).get("storage_zone"),
            "contents": (manifest or {}).get("contents"),
        },
        "recommended_next_action": "Repair missing sidecars before treating this evidence pack as canonical." if missing else "Continue.",
    }


def write_owner_summary(path: Path, report: Dict[str, Any]) -> None:
    lines = [
        "# Inquisition Evidence Sealer Contract Gate V0.1",
        "",
        f"Status: **{report.get('status')}**",
        f"Generated: `{report.get('generated_at_utc')}`",
        f"Mode: `{report.get('mode')}`",
        f"Blocking: `{report.get('blocking_gate')}`",
        "",
        "## Recommendation",
        "",
        f"- {report.get('recommended_next_action')}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["contract", "health"], default="contract")
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--patch-id", required=True)
    ap.add_argument("--buffer-path", default="")
    ap.add_argument("--pack-root", default="")
    ap.add_argument("--out-root", default="")
    ap.add_argument("--delete-buffer-after-seal", action="store_true")
    ap.add_argument("--out-report-root", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    report = contract_gate(args) if args.mode == "contract" else health_gate(args)
    if args.out_report_root and not args.dry_run:
        root = Path(args.out_report_root)
        run_dir = root / f"{SURFACE}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        write_json(run_dir / "MACHINE_REPORT.json", report)
        write_owner_summary(run_dir / "OWNER_READABLE_REPORT_RU.md", report)
        report["output_root"] = str(run_dir)
        write_json(run_dir / "MACHINE_REPORT.json", report)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report.get("blocking_gate") else 0


if __name__ == "__main__":
    raise SystemExit(main())
