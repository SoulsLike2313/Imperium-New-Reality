#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inquisition Hygiene Report Refiner V0.1.
Read-only by default. Refines Janitor V0.1 findings using an explicit policy:
- system zones are classified, not treated as unknown dirt;
- protected runtime registries are not TTL trash;
- detector source files may contain mojibake marker literals;
- summaries are recomputed.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

SURFACE = "INQUISITION_HYGIENE_REPORT_REFINER_V0_1"
VERSION = "0.1.0"

DEFAULT_POLICY_REL = Path("ORGANS/INQUISITION/HYGIENE_POLICY/hygiene_exception_policy_v0_1.json")


def norm_path(value: str) -> str:
    return (value or "").replace("\\", "/").strip()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_csv_dicts(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_dicts(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def normalize_row_types(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row)
    if "source_allowed" in out:
        out["source_allowed"] = as_bool(out["source_allowed"])
    if "ttl_hours" in out and out["ttl_hours"] in ("", None):
        out["ttl_hours"] = None
    if "size_bytes" in out:
        try:
            out["size_bytes"] = int(float(out["size_bytes"]))
        except Exception:
            out["size_bytes"] = 0
    return out


def policy_sets(policy: Dict[str, Any]) -> Tuple[set[str], set[str], set[str]]:
    system_folders = {norm_path(item.get("path", "")) for item in policy.get("approved_system_organ_folders", [])}
    protected_suffixes = {norm_path(item.get("path_suffix", "")) for item in policy.get("protected_local_ttl_paths", [])}
    marker_files = {norm_path(item.get("path", "")) for item in policy.get("marker_literal_allowed_files", [])}
    return system_folders, protected_suffixes, marker_files


def is_protected_ttl(path: str, suffixes: set[str]) -> bool:
    p = norm_path(path)
    return any(p.endswith(suffix) for suffix in suffixes if suffix)


def refine_row(row: Dict[str, Any], system_folders: set[str], protected_suffixes: set[str], marker_files: set[str]) -> Dict[str, Any]:
    r = normalize_row_types(row)
    p = norm_path(str(r.get("path", "")))
    risk = str(r.get("risk_type", ""))
    changed = False
    note = ""

    if risk == "UNKNOWN_ORGAN_FOLDER" and p in system_folders:
        r["severity"] = "INFO"
        r["risk_type"] = "SYSTEM_ZONE_UNREGISTERED_IN_POLICY"
        r["evidence"] = "Approved system zone exists under ORGANS; register in Data Atlas rather than quarantine."
        r["recommended_action"] = "Register as system zone in organ/folder policy and Data Atlas."
        r["cleanup_lane"] = "REGISTER_SYSTEM_ZONE"
        r["source_allowed"] = True
        r["ttl_hours"] = None
        changed = True
        note = "system_zone_policy"

    elif risk == "LOCAL_TTL_EXPIRED" and is_protected_ttl(p, protected_suffixes):
        r["severity"] = "INFO"
        r["risk_type"] = "PROTECTED_LOCAL_REGISTRY"
        r["evidence"] = "Protected local runtime registry root; not a TTL quarantine candidate."
        r["recommended_action"] = "Keep registry root; TTL may apply to selected child run directories only."
        r["cleanup_lane"] = "PROTECTED_NO_TTL"
        r["source_allowed"] = True
        r["ttl_hours"] = None
        changed = True
        note = "protected_ttl_registry"

    elif risk == "ENCODING_MOJIBAKE" and p in marker_files:
        r["severity"] = "INFO"
        r["risk_type"] = "ENCODING_MARKER_LITERAL_ALLOWED"
        r["evidence"] = "Detector source contains mojibake markers as literal patterns."
        r["recommended_action"] = "Keep detector literals; guard true mojibake in other files."
        r["cleanup_lane"] = "SOURCE_ALLOWED_MONITOR"
        r["source_allowed"] = True
        r["ttl_hours"] = None
        changed = True
        note = "detector_literal_allowed"

    r["refined"] = "true" if changed else "false"
    r["refine_note"] = note
    return r


def counts(rows: Iterable[Dict[str, Any]], key: str) -> Dict[str, int]:
    c = Counter(str(r.get(key, "")) for r in rows)
    c.pop("", None)
    return dict(c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--report-root", required=True)
    ap.add_argument("--policy", default="")
    args = ap.parse_args()

    repo = Path(args.repo_root)
    report_root = Path(args.report_root)
    policy_path = Path(args.policy) if args.policy else repo / DEFAULT_POLICY_REL
    policy = load_json(policy_path)
    system_folders, protected_suffixes, marker_files = policy_sets(policy)

    machine_path = report_root / "MACHINE_REPORT.json"
    if not machine_path.exists():
        raise SystemExit(f"MACHINE_REPORT.json not found: {machine_path}")

    machine = load_json(machine_path)
    raw_findings = machine.get("findings_sample") or []
    findings_csv = read_csv_dicts(report_root / "findings.csv")
    cleanup_csv = read_csv_dicts(report_root / "cleanup_plan.csv")
    ttl_csv = read_csv_dicts(report_root / "ttl_candidates.csv")

    findings_src = findings_csv if findings_csv else raw_findings
    refined_findings = [refine_row(r, system_folders, protected_suffixes, marker_files) for r in findings_src]
    refined_cleanup = [refine_row(r, system_folders, protected_suffixes, marker_files) for r in cleanup_csv] if cleanup_csv else [
        r for r in refined_findings if str(r.get("cleanup_lane", ""))
    ]
    refined_ttl = [refine_row(r, system_folders, protected_suffixes, marker_files) for r in ttl_csv]
    refined_ttl = [r for r in refined_ttl if r.get("cleanup_lane") == "TTL_48_QUARANTINE"]

    refined_summary = {
        "findings_total": len(refined_findings),
        "source_findings_total": sum(1 for r in refined_findings if not norm_path(str(r.get("path",""))).startswith("E:/")),
        "local_ttl_candidates_total": len(refined_ttl),
        "critical_total": sum(1 for r in refined_findings if r.get("severity") == "CRITICAL"),
        "warning_total": sum(1 for r in refined_findings if r.get("severity") == "WARNING"),
        "info_total": sum(1 for r in refined_findings if r.get("severity") == "INFO"),
        "risk_types_detected": len(counts(refined_findings, "risk_type")),
        "cleanup_lanes_detected": len(counts(refined_findings, "cleanup_lane")),
        "refined_total": sum(1 for r in refined_findings if r.get("refined") == "true"),
    }

    refined = {
        "status": "PASS_WITH_REFINED_FINDINGS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo),
        "input_report_root": str(report_root),
        "policy_path": str(policy_path),
        "summary": refined_summary,
        "risk_counts": counts(refined_findings, "risk_type"),
        "severity_counts": counts(refined_findings, "severity"),
        "cleanup_lane_counts": counts(refined_findings, "cleanup_lane"),
        "findings_sample": refined_findings[:80],
        "notes_ru": [
            "SYSTEM_ZONE не удаляется: регистрируется в Data Atlas.",
            "Protected registry не TTL-мусор.",
            "Detector literal mojibake в коде Инквизиции не считается реальным mojibake.",
            "Source archive/evidence lanes остаются owner-reviewed, без автоудаления."
        ],
    }

    write_json(report_root / "MACHINE_REPORT_REFINED.json", refined)
    write_csv_dicts(report_root / "findings_refined.csv", refined_findings)
    write_csv_dicts(report_root / "cleanup_plan_refined.csv", refined_cleanup)
    write_csv_dicts(report_root / "ttl_candidates_refined.csv", refined_ttl)

    risk_rows = [{"risk_type": k, "count": v} for k, v in sorted(refined["risk_counts"].items(), key=lambda x: (-x[1], x[0]))]
    write_csv_dicts(report_root / "risk_counts_refined.csv", risk_rows)

    md = [
        "# Inquisition Hygiene Refined Report V0.1",
        "",
        f"Status: **{refined['status']}**",
        f"Generated: `{refined['generated_at_utc']}`",
        f"Input: `{report_root}`",
        "",
        "## Summary",
        "",
    ]
    for k, v in refined_summary.items():
        md.append(f"- {k}: `{v}`")
    md += ["", "## Risk counts", ""]
    for k, v in risk_rows:
        md.append(f"- {k}: `{v}`")
    md += ["", "## Notes", ""]
    for n in refined["notes_ru"]:
        md.append(f"- {n}")
    (report_root / "OWNER_READABLE_REFINED_RU.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(refined, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
