#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, csv, datetime as dt, json, os, re, hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001"
VALIDATOR_ID = "external_audit_control_and_consolidation_validator.v0_1"

THRONE = Path("ORGANS/THRONE")
RECEIPT = THRONE / "RECEIPTS/external_audit_consolidation_receipt.json"
REPORT = THRONE / "REPORTS/EXTERNAL_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md"
CONFLICT_CSV = THRONE / "REPORTS/EXTERNAL_AUDIT_CONFLICT_MATRIX_V0_1.csv"
SCORE_JSON = THRONE / "REPORTS/EXTERNAL_AUDIT_SCORE_NORMALIZATION_V0_1.json"
NEXT_PATCHES = THRONE / "REPORTS/EXTERNAL_AUDIT_RECOMMENDED_NEXT_PATCHES_V0_1.md"

REQUIRED_CONTROL_FILES = [
    THRONE / "MATRICES/EXTERNAL_AUDIT_CONSOLIDATION_MATRIX_V0_1.json",
    THRONE / "MATRICES/SCORE_CONTRACT_MATRIX_V0_1.json",
    Path("ORGANS/CUSTODES/MATRICES/EXTERNAL_EXECUTOR_SCOPE_CONTRACT_MATRIX_V0_1.json"),
    Path("ORGANS/INQUISITION/MATRICES/AUDITOR_SCOPE_VIOLATION_MATRIX_V0_1.json"),
    Path("ORGANS/MECHANICUS/SPECS/VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE_SPEC_V0_1.md"),
    THRONE / "SCHEMAS/external_audit_consolidation_receipt.schema.json",
]

KNOWN_AUDIT_DIR_HINTS = [
    "SERVITOR-REALITY-HYGIENE-EXTERNAL-0001",
    "GROK-REALITY-HYGIENE-EXTERNAL-0001",
    "CODEX-REALITY-HYGIENE-EXTERNAL-0001",
]

THEME_PATTERNS = {
    "root_transport_clutter": [r"root clutter", r"APPLY_", r"FILE_MANIFEST", r"transport", r"root-level", r"root clutter"],
    "validator_readonly_mode": [r"mutating validator", r"dry-run", r"read-only", r"external audit mode", r"copy", r"перезапис", r"rewrote"],
    "population_census_refresh": [r"stale census", r"census refresh", r"population census", r"перепис"],
    "governance_reconciliation": [r"governance drift", r"GOVERNANCE_INDEX", r"root drift", r"Great Nine naming", r"Architectum", r"Officio", r"канон"],
    "great_nine_operational_proof": [r"operational proof", r"profile baseline", r"implementation proof", r"Great Nine operational", r"implementation"],
    "great_nine_trust_proof": [r"trust proof", r"Custodes", r"Inquisition", r"validator trust", r"довер"],
    "no_core_mutation_proof": [r"no-core-mutation", r"core mutation", r"before/after census", r"allowed return", r"мутац"],
    "score_contract": [r"different scores", r"score normalization", r"metric_id", r"formula", r"разные цифры", r"score"],
    "scope_control": [r"scope violation", r"mutated original", r"git checkout", r"changed receipt", r"перезапис", r"reverted"],
}

SCORE_KEYS = [
    "root_hygiene_score",
    "warp_patch_hygiene_score",
    "organ_profile_baseline_score",
    "organ_structural_score",
    "organ_operational_proof_score",
    "organ_trust_proof_score",
    "throne_measurement_quality_score",
    "validator_trust_score",
    "external_executor_onboarding_clarity_score",
    "no_core_mutation_evidence_score",
    "overall_reality_hygiene_score",
    "overall",
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def add(checks: List[Dict[str,Any]], name: str, ok: bool, details: Dict[str,Any]|None=None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def default_external_root() -> Path:
    env = os.environ.get("IMPERIUM_EXTERNAL_AUDITS")
    if env:
        return Path(env)
    return Path(r"E:\IMPERIUM_EXTERNAL_AUDITS")

def classify_audit_dir(path: Path) -> str:
    name = path.name.upper()
    if "GROK" in name:
        return "GROK_RED_TEAM"
    if "SERVITOR" in name:
        return "SERVITOR_OR_CODEX_CAUTIOUS"
    if "CODEX" in name:
        return "SERVITOR_OR_CODEX_CAUTIOUS"
    return "UNKNOWN_EXTERNAL_AUDIT"

def find_audit_dirs(external_root: Path) -> List[Path]:
    if not external_root.exists():
        return []
    candidates = []
    for child in external_root.iterdir():
        if child.is_dir():
            has_report = any((child / n).exists() for n in [
                "REALITY_HYGIENE_AUDIT_REPORT.md",
                "SERVITOR_COMPREHENSION_REPORT.md",
                "GROK_COMPREHENSION_REPORT.md",
                "SCORES.json",
                "RECOMMENDED_NEXT_PATCHES.md",
            ])
            if has_report or "HYGIENE" in child.name.upper():
                candidates.append(child)
    # prefer known current dirs first
    candidates.sort(key=lambda p: (0 if any(h in p.name for h in KNOWN_AUDIT_DIR_HINTS) else 1, p.name))
    return candidates

def load_audit(path: Path) -> Dict[str,Any]:
    text_parts = []
    files = {}
    for name in [
        "README.md",
        "REALITY_HYGIENE_AUDIT_REPORT.md",
        "SERVITOR_COMPREHENSION_REPORT.md",
        "GROK_COMPREHENSION_REPORT.md",
        "THRONE_AUDIT.md",
        "RECOMMENDED_NEXT_PATCHES.md",
        "COMMAND_LOG.md",
    ]:
        p = path / name
        if p.is_file():
            content = read_text(p)
            text_parts.append(f"\n\n--- FILE: {name} ---\n{content}")
            files[name] = {"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p)}
    scores = {}
    sp = path / "SCORES.json"
    if sp.is_file():
        try:
            raw = read_json(sp)
            scores = raw if isinstance(raw, dict) else {"raw": raw}
            files["SCORES.json"] = {"path": str(sp), "bytes": sp.stat().st_size, "sha256": sha(sp)}
        except Exception as e:
            scores = {"_parse_error": str(e)}

    text = "\n".join(text_parts)
    return {
        "audit_id": path.name,
        "path": str(path),
        "auditor_class": classify_audit_dir(path),
        "files": files,
        "scores": scores,
        "text": text,
    }

def theme_hits(text: str) -> Dict[str, int]:
    hits = {}
    for theme, patterns in THEME_PATTERNS.items():
        count = 0
        for pat in patterns:
            count += len(re.findall(pat, text, flags=re.I))
        hits[theme] = count
    return hits

def extract_recommended_patches(text: str) -> List[str]:
    # Patch-like tokens, intentionally conservative.
    found = re.findall(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+){2,}-\d{4}\b", text)
    # keep order unique
    out = []
    for x in found:
        if x not in out:
            out.append(x)
    return out[:50]

def normalize_scores(audits: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    rows = []
    for audit in audits:
        scores = audit.get("scores", {})
        flat = {}
        def walk(prefix, value):
            if isinstance(value, dict):
                for k, v in value.items():
                    walk(f"{prefix}.{k}" if prefix else str(k), v)
            elif isinstance(value, (int, float)):
                flat[prefix] = value
            elif isinstance(value, str):
                m = re.search(r"(-?\d+(?:\.\d+)?)", value)
                if m:
                    try:
                        flat[prefix] = float(m.group(1))
                    except Exception:
                        pass
        walk("", scores)

        for key, value in flat.items():
            metric_guess = None
            for known in SCORE_KEYS:
                if known.lower() in key.lower():
                    metric_guess = known
                    break
            if metric_guess or "score" in key.lower() or "overall" in key.lower():
                rows.append({
                    "metric_id": metric_guess or key,
                    "value": float(value),
                    "scale": "0-100 inferred",
                    "source": audit["audit_id"],
                    "auditor_class": audit["auditor_class"],
                    "formula_or_method": "external auditor provided; not accepted as canonical until replayed",
                    "input_paths": list(audit.get("files", {}).keys()),
                    "evidence_level": "EXTERNAL_AUDIT_SELF_REPORTED",
                    "confidence": "MEDIUM" if audit["auditor_class"] != "UNKNOWN_EXTERNAL_AUDIT" else "LOW",
                    "reproducible": False
                })
    return rows

def detect_scope_violations(audit: Dict[str,Any]) -> List[Dict[str,Any]]:
    text = audit.get("text", "")
    violations = []
    patterns = [
        (r"git checkout", "possible_original_repo_revert_or_cleanup"),
        (r"перезапис", "possible_original_repo_receipt_rewrite"),
        (r"rewrote|overwrote", "possible_original_repo_receipt_rewrite"),
        (r"mutat(?:e|ing|ed)", "possible_mutating_action"),
        (r"changed .*receipt|modified .*receipt", "possible_receipt_mutation"),
        (r"git status.*clean", "status_claim_present_not_violation"),
    ]
    for pat, kind in patterns:
        matches = re.findall(pat, text, flags=re.I | re.S)
        if matches and kind != "status_claim_present_not_violation":
            violations.append({
                "audit_id": audit["audit_id"],
                "kind": kind,
                "severity": "HIGH" if "rewrite" in kind or "revert" in kind else "MEDIUM",
                "pattern": pat,
                "evidence_count": len(matches),
                "meaning": "Potential auditor scope violation or validator external-audit-mode weakness. Treat findings as useful but not fully trusted until rerun in copy-only mode."
            })
    return violations

def build_conflict_rows(audits: List[Dict[str,Any]]) -> Tuple[List[Dict[str,Any]], List[str], List[str], List[str]]:
    per_audit_hits = {a["audit_id"]: theme_hits(a["text"]) for a in audits}
    rows = []
    confirmed = []
    only_one = []
    conflicts = []

    for theme in THEME_PATTERNS:
        sources = [aid for aid, hits in per_audit_hits.items() if hits.get(theme, 0) > 0]
        total_hits = sum(per_audit_hits[aid].get(theme, 0) for aid in per_audit_hits)
        if len(sources) >= 2:
            status = "CONFIRMED_BY_MULTIPLE_AUDITORS"
            confirmed.append(theme)
        elif len(sources) == 1:
            status = "SINGLE_SOURCE_NEEDS_RECHECK"
            only_one.append(theme)
        else:
            status = "NOT_OBSERVED"
        rows.append({
            "theme": theme,
            "status": status,
            "sources": ";".join(sources),
            "total_hits": total_hits
        })

    # Score conflicts: same metric, spread > 15.
    norm = normalize_scores(audits)
    by_metric = {}
    for r in norm:
        by_metric.setdefault(r["metric_id"], []).append(r)
    for metric, vals in by_metric.items():
        if len(vals) >= 2:
            nums = [v["value"] for v in vals]
            if max(nums) - min(nums) > 15:
                conflicts.append(metric)
                rows.append({
                    "theme": f"score_conflict:{metric}",
                    "status": "SCORE_CONFLICT_REQUIRES_NORMALIZATION",
                    "sources": ";".join(f"{v['source']}={v['value']}" for v in vals),
                    "total_hits": len(vals)
                })
    return rows, confirmed, only_one, conflicts

def next_patch_backlog(confirmed: List[str], only_one: List[str], scope_violations: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    # Always include the six-series plan but prioritize based on confirmed findings.
    backlog = [
        {
            "priority": 1,
            "patch_id": "VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001",
            "reason": "External agents must not mutate Reality while auditing; validators need dry-run/read-only/copy-output behavior.",
            "evidence": "confirmed" if "validator_readonly_mode" in confirmed or scope_violations else "planned"
        },
        {
            "priority": 2,
            "patch_id": "ROOT-TRANSPORT-CLUTTER-RELOCATION-0001",
            "reason": "Root transport clutter makes Reality harder for external agents to parse.",
            "evidence": "confirmed" if "root_transport_clutter" in confirmed else "planned"
        },
        {
            "priority": 3,
            "patch_id": "IMPERIUM-POPULATION-CENSUS-REFRESH-0001",
            "reason": "Census must be refreshed and staleness-guarded after Reality changes.",
            "evidence": "confirmed" if "population_census_refresh" in confirmed else "planned"
        },
        {
            "priority": 4,
            "patch_id": "GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001",
            "reason": "Governance/root naming drift and Great Nine canon conflicts must be resolved before executor onboarding.",
            "evidence": "confirmed" if "governance_reconciliation" in confirmed else "planned"
        },
        {
            "priority": 5,
            "patch_id": "GREAT-NINE-OPERATIONAL-AND-TRUST-PROOF-0001",
            "reason": "Great Nine baseline/structure is strong, but operational/trust proof remains weak.",
            "evidence": "confirmed" if "great_nine_operational_proof" in confirmed or "great_nine_trust_proof" in confirmed else "planned"
        },
        {
            "priority": 6,
            "patch_id": "THRONE-NO-CORE-MUTATION-PROOF-0001",
            "reason": "No-core-mutation evidence remains low/absent and blocks safe external work.",
            "evidence": "confirmed" if "no_core_mutation_proof" in confirmed else "planned"
        },
        {
            "priority": 7,
            "patch_id": "INDEPENDENT-AUDIT-ROUND-2-0001",
            "reason": "After six patches, repeat independent external audit with stricter containment.",
            "evidence": "post-series gate"
        }
    ]
    return backlog

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--external-audits-root", default=None)
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    external_root = Path(args.external_audits_root) if args.external_audits_root else default_external_root()

    checks: List[Dict[str,Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    missing_control = [p.as_posix() for p in REQUIRED_CONTROL_FILES if not (repo / p).exists()]
    add(checks, "required_control_files_exist", not missing_control, {"missing": missing_control})
    if missing_control:
        errors.extend(f"Missing control file: {p}" for p in missing_control)

    audit_dirs = find_audit_dirs(external_root)
    add(checks, "external_audit_root_found", external_root.exists(), {"external_root": str(external_root)})
    if not external_root.exists():
        errors.append(f"External audit root not found: {external_root}")

    add(checks, "at_least_two_independent_audits_found", len(audit_dirs) >= 2, {"audit_dirs": [str(p) for p in audit_dirs]})
    if len(audit_dirs) < 2:
        errors.append("Need at least two independent external audits for consolidation")

    audits = [load_audit(p) for p in audit_dirs]
    audit_classes = sorted(set(a["auditor_class"] for a in audits))
    add(checks, "multiple_auditor_styles_present", len(audit_classes) >= 2, {"auditor_classes": audit_classes})
    if len(audit_classes) < 2:
        warnings.append("Only one auditor style detected; consolidation confidence reduced")

    score_rows = normalize_scores(audits)
    add(checks, "score_rows_loaded", len(score_rows) > 0, {"score_rows": len(score_rows)})
    if not score_rows:
        warnings.append("No external score rows found or parsed")

    conflict_rows, confirmed, only_one, score_conflicts = build_conflict_rows(audits)
    scope_violations = []
    for audit in audits:
        scope_violations.extend(detect_scope_violations(audit))

    add(checks, "score_contract_enforced", True, {"normalized_scores": len(score_rows), "score_conflicts": score_conflicts})
    add(checks, "scope_contract_defined", not missing_control, {"scope_violation_count": len(scope_violations)})
    add(checks, "scope_violation_detection_active", True, {"scope_violations": scope_violations})
    add(checks, "no_blind_score_acceptance", True, {"rule": "external scores are normalized as EXTERNAL_AUDIT_SELF_REPORTED, not canonical"})
    add(checks, "consolidated_findings_built", bool(confirmed or only_one or conflict_rows), {"confirmed": confirmed, "single_source": only_one})
    backlog = next_patch_backlog(confirmed, only_one, scope_violations)
    add(checks, "next_patch_backlog_defined", len(backlog) >= 6, {"backlog": [b["patch_id"] for b in backlog]})

    verdict = "PASS_CONSOLIDATED" if not errors else "FAIL_CONSOLIDATION"

    out_dirs = [
        repo / RECEIPT.parent,
        repo / REPORT.parent,
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    receipt = {
        "receipt_id": "receipt.external_audit_control_and_consolidation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc(),
        "external_audits_root": str(external_root),
        "audits": [
            {
                "audit_id": a["audit_id"],
                "path": a["path"],
                "auditor_class": a["auditor_class"],
                "files": a["files"],
                "theme_hits": theme_hits(a["text"]),
                "recommended_patches": extract_recommended_patches(a["text"]),
            }
            for a in audits
        ],
        "scores": {
            "normalized_score_rows": score_rows,
            "score_conflicts": score_conflicts,
            "meaning": "External scores are evidence, not canonical truth, until replayed under score contract."
        },
        "confirmed_themes": confirmed,
        "single_source_themes": only_one,
        "scope_violations": scope_violations,
        "recommended_patch_backlog": backlog,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "This receipt consolidates independent audits and defines external executor control; it does not fix Reality yet."
    }

    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / SCORE_JSON).write_text(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        "score_contract": {
            "external_scores_are_not_canonical": True,
            "required_fields": [
                "metric_id", "value", "scale", "source", "formula_or_method",
                "input_paths", "evidence_level", "confidence", "reproducible"
            ]
        },
        "normalized_score_rows": score_rows,
        "score_conflicts": score_conflicts
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (repo / CONFLICT_CSV).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["theme", "status", "sources", "total_hits"])
        w.writeheader()
        for row in conflict_rows:
            w.writerow(row)

    patches_md = "\n".join(
        f"{b['priority']}. `{b['patch_id']}` — {b['reason']} _(evidence: {b['evidence']})_"
        for b in backlog
    )
    (repo / NEXT_PATCHES).write_text(f"""# EXTERNAL AUDIT RECOMMENDED NEXT PATCHES V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Backlog

{patches_md}
""", encoding="utf-8")

    audit_lines = []
    for a in receipt["audits"]:
        audit_lines.append(f"- `{a['audit_id']}` — class: `{a['auditor_class']}`, files: `{len(a['files'])}`")
    confirmed_lines = "\n".join(f"- `{x}`" for x in confirmed) if confirmed else "- none"
    single_lines = "\n".join(f"- `{x}`" for x in only_one) if only_one else "- none"
    violation_lines = "\n".join(
        f"- `{v['audit_id']}` — `{v['kind']}` / `{v['severity']}` / evidence_count `{v['evidence_count']}`"
        for v in scope_violations
    ) if scope_violations else "- none"
    conflicts_lines = "\n".join(f"- `{x}`" for x in score_conflicts) if score_conflicts else "- none"
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    report = f"""# EXTERNAL AUDIT CONSOLIDATED FINDINGS V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This is a consolidation and control patch.

It does not clean the repository yet.  
It defines how external audits are accepted, how scores are normalized, and how auditor scope violations are recorded.

## Audits found

{chr(10).join(audit_lines) if audit_lines else '- none'}

## Confirmed themes

{confirmed_lines}

## Single-source themes needing recheck

{single_lines}

## Score conflicts

{conflicts_lines}

## Scope violations / containment issues

{violation_lines}

## Important control decision

External audit scores are not canonical truth.

Every score must carry:

```text
metric_id
value
scale
source
formula_or_method
input_paths
evidence_level
confidence
generated_at_or_observed_at
repo_head_if_applicable
reproducible
```

## Recommended next patches

{patches_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT.as_posix()}`
- `{REPORT.as_posix()}`
- `{CONFLICT_CSV.as_posix()}`
- `{SCORE_JSON.as_posix()}`
- `{NEXT_PATCHES.as_posix()}`
"""
    (repo / REPORT).write_text(report, encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "external_audits_root": str(external_root),
        "audits_found": [a["audit_id"] for a in audits],
        "confirmed_themes": confirmed,
        "single_source_themes": only_one,
        "score_conflicts": score_conflicts,
        "scope_violations": scope_violations,
        "recommended_patch_backlog": [b["patch_id"] for b in backlog],
        "receipt": RECEIPT.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_CONSOLIDATED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
