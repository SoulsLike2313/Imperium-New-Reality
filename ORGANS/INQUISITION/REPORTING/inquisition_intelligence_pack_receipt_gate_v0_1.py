#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inquisition gate for Imperium Intelligence Pack final digest sidecar receipt."""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

SURFACE = "INQUISITION_INTELLIGENCE_PACK_RECEIPT_GATE_V0_1"
VERSION = "0.1.0"
CONTRACT_ID = "mechanicus.intelligence_pack.final_digest_contract.v0_8_9_4"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def default_sidecars(pack: Path, receipt_root: Optional[Path] = None) -> Dict[str, Path]:
    root = receipt_root if receipt_root else pack.parent
    base = root / pack.stem
    return {
        "manifest": base.with_suffix(".INTELLIGENCE_PACK_MANIFEST.json"),
        "sha256sums": base.with_suffix(".FINAL_SHA256SUMS.txt"),
        "machine_receipt": base.with_suffix(".MACHINE_RECEIPT.json"),
        "owner_summary": base.with_suffix(".OWNER_SUMMARY_RU.md"),
    }


def read_embedded_manifest(pack: Path) -> Tuple[Optional[Dict[str, object]], Optional[str], Optional[str]]:
    try:
        with zipfile.ZipFile(pack, "r") as zf:
            data = zf.read("MANIFEST.json")
        h = hashlib.sha256(data).hexdigest()
        return json.loads(data.decode("utf-8")), h, None
    except Exception as exc:
        return None, None, str(exc)


def parse_sha256sums(path: Path, expected_filename: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[-1] == expected_filename:
                return parts[0].lower(), None
        if lines:
            parts = lines[0].split()
            if parts:
                return parts[0].lower(), f"No exact filename match for {expected_filename}; used first line."
        return None, "SHA256SUMS file is empty."
    except Exception as exc:
        return None, str(exc)


def evaluate(pack: Path, receipt_root: Optional[Path]) -> Dict[str, object]:
    findings = []
    checks: Dict[str, object] = {}
    pack = pack.resolve()
    sidecars = default_sidecars(pack, receipt_root.resolve() if receipt_root else None)
    actual_sha = sha256_file(pack) if pack.exists() else None
    actual_size = pack.stat().st_size if pack.exists() else None

    if not pack.exists():
        findings.append({"finding_id": "INTELLIGENCE_PACK_ZIP_MISSING", "severity": "CRITICAL", "count": 1, "sample": [str(pack)]})

    missing = [name for name, path in sidecars.items() if not path.exists()]
    if missing:
        findings.append({"finding_id": "INTELLIGENCE_PACK_RECEIPT_SIDECARS_MISSING", "severity": "CRITICAL", "count": len(missing), "sample": [f"{n}:{sidecars[n]}" for n in missing]})

    sums_sha = None
    sums_warning = None
    if sidecars["sha256sums"].exists():
        sums_sha, sums_warning = parse_sha256sums(sidecars["sha256sums"], pack.name)
        if sums_warning:
            findings.append({"finding_id": "INTELLIGENCE_PACK_SHA256SUMS_WEAK_MATCH", "severity": "WARNING", "count": 1, "sample": [sums_warning]})

    machine_receipt = None
    if sidecars["machine_receipt"].exists():
        try:
            machine_receipt = read_json(sidecars["machine_receipt"])
        except Exception as exc:
            findings.append({"finding_id": "INTELLIGENCE_PACK_MACHINE_RECEIPT_INVALID_JSON", "severity": "CRITICAL", "count": 1, "sample": [str(exc)]})

    sidecar_manifest = None
    if sidecars["manifest"].exists():
        try:
            sidecar_manifest = read_json(sidecars["manifest"])
        except Exception as exc:
            findings.append({"finding_id": "INTELLIGENCE_PACK_SIDECAR_MANIFEST_INVALID_JSON", "severity": "CRITICAL", "count": 1, "sample": [str(exc)]})

    embedded_manifest, embedded_manifest_sha, embedded_manifest_error = read_embedded_manifest(pack) if pack.exists() else (None, None, "pack missing")
    if embedded_manifest_error:
        findings.append({"finding_id": "INTELLIGENCE_PACK_EMBEDDED_MANIFEST_UNREADABLE", "severity": "CRITICAL", "count": 1, "sample": [embedded_manifest_error]})

    checks["pack_exists"] = pack.exists()
    checks["pack_sha256_actual"] = actual_sha
    checks["pack_size_bytes_actual"] = actual_size
    checks["sidecars_missing_total"] = len(missing)
    checks["embedded_manifest_sha256"] = embedded_manifest_sha
    checks["embedded_manifest_has_final_zip_sha256"] = bool(isinstance(embedded_manifest, dict) and embedded_manifest.get("pack_sha256"))

    def compare(label: str, expected: Optional[str]) -> None:
        if expected and actual_sha and expected.lower() != actual_sha.lower():
            findings.append({"finding_id": f"INTELLIGENCE_PACK_RECEIPT_HASH_MISMATCH_{label}", "severity": "CRITICAL", "count": 1, "sample": [f"expected={expected}", f"actual={actual_sha}"]})

    compare("SHA256SUMS", sums_sha)
    if isinstance(machine_receipt, dict):
        artifact = machine_receipt.get("artifact", {}) if isinstance(machine_receipt.get("artifact"), dict) else {}
        compare("MACHINE_RECEIPT", artifact.get("sha256"))
        if artifact.get("filename") and artifact.get("filename") != pack.name:
            findings.append({"finding_id": "INTELLIGENCE_PACK_RECEIPT_FILENAME_MISMATCH", "severity": "CRITICAL", "count": 1, "sample": [artifact.get("filename"), pack.name]})
        if machine_receipt.get("contract_id") != CONTRACT_ID:
            findings.append({"finding_id": "INTELLIGENCE_PACK_RECEIPT_CONTRACT_ID_MISMATCH", "severity": "WARNING", "count": 1, "sample": [machine_receipt.get("contract_id")]})
    if isinstance(sidecar_manifest, dict):
        compare("SIDECAR_MANIFEST", sidecar_manifest.get("pack_sha256"))
        embedded_expected = sidecar_manifest.get("embedded_manifest_sha256")
        if embedded_expected and embedded_manifest_sha and embedded_expected.lower() != embedded_manifest_sha.lower():
            findings.append({"finding_id": "INTELLIGENCE_PACK_EMBEDDED_MANIFEST_HASH_MISMATCH", "severity": "CRITICAL", "count": 1, "sample": [f"expected={embedded_expected}", f"actual={embedded_manifest_sha}"]})

    if isinstance(embedded_manifest, dict) and embedded_manifest.get("pack_sha256"):
        findings.append({"finding_id": "INTELLIGENCE_PACK_SELF_REFERENTIAL_HASH_IN_ZIP_MANIFEST", "severity": "CRITICAL", "count": 1, "sample": ["MANIFEST.json contains pack_sha256"]})
    if isinstance(embedded_manifest, dict):
        digest_contract = embedded_manifest.get("digest_contract")
        if not isinstance(digest_contract, dict) or digest_contract.get("self_referential_pack_hash_inside_zip_manifest") is not False:
            findings.append({"finding_id": "INTELLIGENCE_PACK_DIGEST_CONTRACT_MISSING_OR_WEAK", "severity": "WARNING", "count": 1, "sample": [str(digest_contract)]})

    blocking = any(f.get("severity") == "CRITICAL" for f in findings)
    return {
        "status": "FAIL_INTELLIGENCE_PACK_RECEIPT" if blocking else "PASS_INTELLIGENCE_PACK_RECEIPT",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "contract_id": CONTRACT_ID,
        "blocking_gate": blocking,
        "severity": "CRITICAL" if blocking else ("WARNING" if findings else "INFO"),
        "pack": str(pack),
        "sidecars": {k: str(v) for k, v in sidecars.items()},
        "checks": checks,
        "receipt_digest": machine_receipt,
        "sidecar_manifest_digest": sidecar_manifest,
        "findings": findings,
        "recommended_next_action_ru": "Use ZIP plus receipt sidecars as handoff only when this gate is PASS.",
    }


def write_reports(root: Path, report: Dict[str, object]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Intelligence Pack Receipt Gate", "", f"Status: {report['status']}", "", "## Checks"]
    for k, v in report.get("checks", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Findings")
    if report.get("findings"):
        for f in report.get("findings", []):
            lines.append(f"- {f.get('severity')}: {f.get('finding_id')} ({f.get('count')})")
    else:
        lines.append("- none")
    (root / "OWNER_REPORT_RU.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Check Imperium Intelligence Pack receipt sidecars")
    ap.add_argument("--pack", required=True, help="Intelligence Pack ZIP path")
    ap.add_argument("--receipt-root", default="", help="Optional root containing receipt sidecars; default is ZIP parent")
    ap.add_argument("--out-report-root", default="")
    args = ap.parse_args(argv)
    report = evaluate(Path(args.pack), Path(args.receipt_root) if args.receipt_root else None)
    if args.out_report_root:
        write_reports(Path(args.out_report_root), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
