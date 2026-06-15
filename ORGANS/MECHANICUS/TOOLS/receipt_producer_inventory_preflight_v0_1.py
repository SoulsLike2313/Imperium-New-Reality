#!/usr/bin/env python3
"""Build receipt producer inventory and legacy field preflight report."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DANGEROUS_FIELDS = [
    "final_head",
    "closure_head",
    "commit_hash",
    "remote_head",
    "head",
    "finalization_head",
    "review_target",
    "PASS",
    "clean_pass",
]

REQUIRED_CLASSIFICATIONS = [
    "MIGRATED_TO_EXTERNAL_FINALIZATION",
    "LEGACY_SELF_HEAD_RISK",
    "LEGACY_AMBIGUOUS_HEADS",
    "LEGACY_FINAL_HEAD_FIELD_RISK",
    "LEGACY_REPLAY_STATE_AMBIGUOUS",
    "LEGACY_CAP_CLOSURE_AMBIGUOUS",
    "TEMPLATE_ONLY_NEEDS_UPDATE",
    "REVIEW_PACK_PRODUCER",
    "TASKPACK_PRODUCER",
    "NOT_APPLICABLE",
    "UNKNOWN_REQUIRES_REVIEW",
]

SAFE_NEW_SEMANTIC_MARKERS = {
    "receipt_subject_head",
    "receipt_content_head",
    "external_delivery_head",
    "remote_head_after_push",
    "self_head_paradox_handled",
}

REPLAY_ALLOWED_STATES = {
    "SEPARATE_REPLAY_RUNNER_FOR_TARGET",
    "INQUISITOR_REPLAY_FOR_TARGET",
    "SPECULUM_REPLAY_FOR_TARGET",
    "EXTERNAL_REPLAY_ACCEPTED",
    "PRIOR_REPLAY_EXISTS",
    "STALE_REPLAY_ONLY",
    "NONE",
}

SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh", ".cmd", ".bat", ".js", ".ts"}
TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".py",
    ".ps1",
    ".sh",
    ".cmd",
    ".bat",
    ".js",
    ".ts",
}

OUTPUT_NAME_REGEX = re.compile(
    r"([A-Za-z0-9_./-]*(?:receipt|verdict|finalization|handoff|summary|taxonomy_manifest|adjudication|closeout|report|inventory|matrix)[A-Za-z0-9_./-]*\.(?:json|md|zip))",
    flags=re.IGNORECASE,
)

LINE_HINT_REGEX = re.compile(
    r"(receipt|verdict|finalization|handoff|summary|clean_pass|final_head|closure_head|replay_state)",
    flags=re.IGNORECASE,
)

FIELD_REGEX_MAP = {
    "final_head": re.compile(r"\bfinal_head\b", flags=re.IGNORECASE),
    "closure_head": re.compile(r"\bclosure_head\b", flags=re.IGNORECASE),
    "commit_hash": re.compile(r"\bcommit_hash\b", flags=re.IGNORECASE),
    "remote_head": re.compile(r"\bremote_head\b", flags=re.IGNORECASE),
    "head": re.compile(r"\bhead\b", flags=re.IGNORECASE),
    "finalization_head": re.compile(r"\bfinalization_head\b", flags=re.IGNORECASE),
    "review_target": re.compile(r"\breview_target\b", flags=re.IGNORECASE),
    "PASS": re.compile(r"\bPASS\b"),
    "clean_pass": re.compile(r"\bclean_pass\b", flags=re.IGNORECASE),
}

CAPS_FOR_CLASSIFICATION = {
    "CAP_RECEIPT_PRODUCER_INVENTORY_MISSING",
    "CAP_LEGACY_RECEIPT_PRODUCERS_UNCLASSIFIED",
    "CAP_MIGRATION_PRIORITY_MATRIX_MISSING",
    "CAP_LEGACY_FIELD_CHECKER_MISSING",
    "CAP_STAGE_0_CLOSEOUT_UNPROVEN",
    "CAP_P0_PRODUCER_RISK_UNRESOLVED",
    "CAP_MASS_MIGRATION_ATTEMPTED_TOO_EARLY",
    "CAP_WARP_CLAIMED_WITHOUT_UNLOCK",
    "CAP_NO_EFFICIENCY_DELTA",
}

IGNORED_DIR_PARTS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    "site-packages",
}


@dataclass
class ProducerEvidence:
    search_reason: str
    excerpt_or_line_hint: str
    related_files: list[str]


@dataclass
class ProducerItem:
    producer_id: str
    path: str
    producer_type: str
    owner_organ: str
    outputs_created: list[str]
    dangerous_fields_found: list[str]
    current_classification: str
    risk_level: str
    migration_priority: str
    recommended_migration_target: str
    evidence: ProducerEvidence
    notes: str
    legacy_field_checker_status: str
    risk_score: int

    def to_inventory_dict(self) -> dict[str, Any]:
        return {
            "producer_id": self.producer_id,
            "path": self.path,
            "producer_type": self.producer_type,
            "owner_organ": self.owner_organ,
            "outputs_created": self.outputs_created,
            "dangerous_fields_found": self.dangerous_fields_found,
            "current_classification": self.current_classification,
            "risk_level": self.risk_level,
            "migration_priority": self.migration_priority,
            "recommended_migration_target": self.recommended_migration_target,
            "evidence": {
                "search_reason": self.evidence.search_reason,
                "excerpt_or_line_hint": self.evidence.excerpt_or_line_hint,
                "related_files": self.evidence.related_files,
            },
            "notes": self.notes,
            "legacy_field_checker_status": self.legacy_field_checker_status,
            "risk_score": self.risk_score,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build receipt producer inventory preflight.")
    parser.add_argument("--repo-root", required=True, help="Absolute repository root.")
    parser.add_argument("--scan-root", default="IMPERIUM_NEW_GENERATION", help="Scan root relative to repo root.")
    parser.add_argument("--report-root", required=True, help="Output directory for required reports.")
    parser.add_argument("--task-id", required=True, help="Task ID.")
    parser.add_argument("--max-bytes", type=int, default=1_500_000, help="Max text file bytes to parse.")
    return parser.parse_args()


def _safe_text_read(path: Path, max_bytes: int) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _is_ignored_path(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return any(part in lowered for part in IGNORED_DIR_PARTS)


def _normalize(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _owner_organ_from_path(rel_path: str) -> str:
    upper = rel_path.upper()
    organ_markers = [
        "DOCTRINARIUM",
        "OFFICIO_AGENTIS",
        "ASTRONOMICON",
        "ADMINISTRATUM",
        "MECHANICUS",
        "INQUISITION",
        "STRATEGIUM",
        "SCHOLA_IMPERIALIS",
    ]
    for marker in organ_markers:
        if f"/{marker}/" in upper:
            return marker
    for marker in organ_markers:
        if marker in upper:
            return marker
    return "UNKNOWN"


def _producer_type(rel_path: str) -> str:
    upper = rel_path.upper()
    suffix = Path(rel_path).suffix.lower()
    name = Path(rel_path).name.upper()
    if "INPUT_REVIEW_ZIPS" in upper or "REVIEW" in name:
        return "REVIEW_PACK"
    if "TASKPACK" in upper or name in {"TASK_SPEC.MD", "OUTPUT_REQUIREMENTS.MD", "ACCEPTANCE_GATES.MD", "MANIFEST.JSON"}:
        return "TASKPACK_PATTERN"
    if "TEMPLATE" in upper:
        return "TEMPLATE"
    if "RUNNER" in name:
        return "RUNNER"
    if "CHECKER" in name or "VALIDATOR" in name:
        return "CHECKER"
    if suffix in SCRIPT_EXTENSIONS:
        return "SCRIPT"
    if "REPORTS/" in rel_path and suffix in {".json", ".md"}:
        return "AGENT_OUTPUT_CONVENTION"
    return "UNKNOWN"


def _extract_outputs(text: str) -> list[str]:
    outputs = sorted({match.group(1).replace("\\", "/") for match in OUTPUT_NAME_REGEX.finditer(text)})
    return outputs[:25]


def _dangerous_fields(text: str) -> list[str]:
    found: list[str] = []
    for field, regex in FIELD_REGEX_MAP.items():
        if regex.search(text):
            found.append(field)
    return found


def _line_hint(text: str) -> str:
    if not text:
        return "binary_or_too_large"
    for index, line in enumerate(text.splitlines(), start=1):
        if LINE_HINT_REGEX.search(line):
            clipped = line.strip()
            if len(clipped) > 160:
                clipped = clipped[:157] + "..."
            return f"line {index}: {clipped}"
    return "no_signal_line_found"


def _legacy_field_status(text: str, dangerous: list[str]) -> str:
    if not dangerous:
        return "NOT_APPLICABLE"

    lower = text.lower()
    safe_marker_hits = sum(1 for marker in SAFE_NEW_SEMANTIC_MARKERS if marker in lower)
    has_final_head = "final_head" in dangerous
    has_clean_pass = "clean_pass" in dangerous or "PASS" in dangerous
    has_replay = "replay" in lower
    has_allowed_replay_state = any(state.lower() in lower for state in REPLAY_ALLOWED_STATES)

    if safe_marker_hits >= 3 and not has_final_head:
        return "SAFE_NEW_SEMANTICS"
    if has_final_head and has_clean_pass and safe_marker_hits < 2:
        return "LIKELY_SELF_HEAD_RISK"
    if has_replay and not has_allowed_replay_state:
        return "AMBIGUOUS_LEGACY_FIELD"
    if safe_marker_hits >= 2:
        return "SAFE_NEW_SEMANTICS"
    if has_final_head:
        return "AMBIGUOUS_LEGACY_FIELD"
    return "MANUAL_REVIEW"


def _classification(
    producer_type: str,
    text: str,
    dangerous: list[str],
    legacy_status: str,
    rel_path: str,
    outputs: list[str],
) -> str:
    lower = text.lower()
    has_safe_markers = sum(1 for marker in SAFE_NEW_SEMANTIC_MARKERS if marker in lower) >= 2
    has_final_head = "final_head" in dangerous
    has_replay = "replay" in lower
    has_closure = "closure_head" in dangerous or "cap_closure" in lower
    has_review_pack_context = producer_type == "REVIEW_PACK"
    has_taskpack_context = producer_type == "TASKPACK_PATTERN"
    output_blob = " ".join(outputs).lower()

    if producer_type == "AGENT_OUTPUT_CONVENTION":
        if "external_finalization_receipt" in output_blob:
            return "MIGRATED_TO_EXTERNAL_FINALIZATION"
        if any(token in output_blob for token in ("closure_receipt", "final_receipt", "commit_push_receipt", "receipt_index")):
            return "TEMPLATE_ONLY_NEEDS_UPDATE"
        if any(token in output_blob for token in ("verdict", "handoff", "final_owner_summary", "adjudication", "head_taxonomy_manifest")):
            return "REVIEW_PACK_PRODUCER"
        if any(token in output_blob for token in ("receipt", "report")):
            return "TEMPLATE_ONLY_NEEDS_UPDATE"
        return "UNKNOWN_REQUIRES_REVIEW"

    if has_safe_markers and "external_finalization" in lower:
        return "MIGRATED_TO_EXTERNAL_FINALIZATION"
    if legacy_status == "LIKELY_SELF_HEAD_RISK":
        return "LEGACY_SELF_HEAD_RISK"
    if has_final_head and not has_safe_markers:
        return "LEGACY_FINAL_HEAD_FIELD_RISK"
    if ("head" in dangerous and len(dangerous) >= 3) and not has_safe_markers:
        return "LEGACY_AMBIGUOUS_HEADS"
    if has_replay and "replay_state" in lower and not any(state.lower() in lower for state in REPLAY_ALLOWED_STATES):
        return "LEGACY_REPLAY_STATE_AMBIGUOUS"
    if has_closure and "evidence_for_state" not in lower:
        return "LEGACY_CAP_CLOSURE_AMBIGUOUS"
    if producer_type == "TEMPLATE":
        return "TEMPLATE_ONLY_NEEDS_UPDATE"
    if has_review_pack_context:
        return "REVIEW_PACK_PRODUCER"
    if has_taskpack_context:
        return "TASKPACK_PRODUCER"
    if not dangerous and not outputs and producer_type == "UNKNOWN":
        return "NOT_APPLICABLE"
    return "UNKNOWN_REQUIRES_REVIEW"


def _risk_and_priority(classification: str, dangerous: list[str]) -> tuple[str, str, int]:
    if classification in {"LEGACY_SELF_HEAD_RISK", "LEGACY_AMBIGUOUS_HEADS", "LEGACY_FINAL_HEAD_FIELD_RISK"}:
        return "P0", "P0_BLOCKS_STAGE_1", 95
    if classification in {
        "LEGACY_REPLAY_STATE_AMBIGUOUS",
        "LEGACY_CAP_CLOSURE_AMBIGUOUS",
        "UNKNOWN_REQUIRES_REVIEW",
    }:
        return "P1", "P1_MIGRATE_BEFORE_REAL_USE_PILOT", 80
    if classification in {"TEMPLATE_ONLY_NEEDS_UPDATE", "REVIEW_PACK_PRODUCER", "TASKPACK_PRODUCER"}:
        score = 62 if dangerous else 50
        return "P2", "P2_MIGRATE_BEFORE_IDE_RELEASE", score
    if classification == "MIGRATED_TO_EXTERNAL_FINALIZATION":
        return "P3", "P3_LEGACY_ARCHIVE_OR_LOW_RISK", 20
    if classification == "NOT_APPLICABLE":
        return "NONE", "NOT_APPLICABLE", 0
    return "P1", "P1_MIGRATE_BEFORE_REAL_USE_PILOT", 70


def _recommended_target(classification: str) -> str:
    mapping = {
        "MIGRATED_TO_EXTERNAL_FINALIZATION": "Keep current external finalization semantics and enforce checker coverage.",
        "LEGACY_SELF_HEAD_RISK": "Replace same-commit final_head logic with external_finalization_receipt fields and subject/finalization split.",
        "LEGACY_AMBIGUOUS_HEADS": "Normalize to receipt_subject_head + receipt_content_head + remote_head_after_push contract.",
        "LEGACY_FINAL_HEAD_FIELD_RISK": "Remove standalone final_head as proof source and adopt self_head_paradox_handled rule.",
        "LEGACY_REPLAY_STATE_AMBIGUOUS": "Adopt INDEPENDENT_REPLAY_STATE_TAXONOMY states and require target/replay head parity metadata.",
        "LEGACY_CAP_CLOSURE_AMBIGUOUS": "Adopt CAP_CLOSURE_SEMANTICS contract with evidence_for_state and closure_head discipline.",
        "TEMPLATE_ONLY_NEEDS_UPDATE": "Update template placeholders to external finalization naming and cap taxonomy.",
        "REVIEW_PACK_PRODUCER": "Wire legacy field checker into review-pack generation before next review loop.",
        "TASKPACK_PRODUCER": "Add explicit output semantics and producer migration hints into taskpack specs.",
        "NOT_APPLICABLE": "No action required.",
        "UNKNOWN_REQUIRES_REVIEW": "Manual Inquisition + Mechanicus review required before Stage 1.",
    }
    return mapping.get(classification, "Manual review required.")


def _should_include_file(rel_path: str, suffix: str) -> bool:
    upper = rel_path.upper()
    name = Path(rel_path).name.upper()
    taskpack_core_names = {
        "MANIFEST.JSON",
        "TASK_SPEC.MD",
        "OUTPUT_REQUIREMENTS.MD",
        "ACCEPTANCE_GATES.MD",
        "000_START_TASK_READ_ORDER.MD",
        "00_START_MESSAGE_FOR_SERVITOR.TXT",
    }
    if suffix in SCRIPT_EXTENSIONS:
        return True
    if "TEMPLATES/" in upper:
        return True
    if "TASKPACK" in upper and name in taskpack_core_names:
        return True
    if name in {"TASK_SPEC.MD", "OUTPUT_REQUIREMENTS.MD", "ACCEPTANCE_GATES.MD", "MANIFEST.JSON"}:
        return True
    if "CONTRACTS/" in upper and any(token in name for token in ("RECEIPT", "FINALIZATION", "REPLAY", "CLOSURE")):
        return True
    return False


def _build_from_real_files(repo_root: Path, scan_root: Path, max_bytes: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in scan_root.rglob("*"):
        if not path.is_file():
            continue
        if _is_ignored_path(path):
            continue
        suffix = path.suffix.lower()
        if suffix and suffix not in TEXT_EXTENSIONS:
            continue
        rel = _normalize(path, repo_root)
        if not _should_include_file(rel, suffix):
            continue
        text = _safe_text_read(path, max_bytes)
        dangerous = _dangerous_fields(text)
        outputs = _extract_outputs(text)
        producer_type = _producer_type(rel)
        lower = text.lower()
        has_signal_keywords = any(
            token in lower
            for token in (
                "receipt",
                "verdict",
                "finalization",
                "handoff",
                "closeout",
                "report",
                "clean_pass",
                "replay",
                "head_taxonomy",
                "adjudication",
            )
        )
        if not (dangerous or outputs or has_signal_keywords or producer_type == "TASKPACK_PATTERN"):
            continue
        if not dangerous and not outputs and producer_type in {"UNKNOWN", "AGENT_OUTPUT_CONVENTION", "TEMPLATE"}:
            continue
        records.append(
            {
                "rel_path": rel,
                "text": text,
                "dangerous": dangerous,
                "outputs": outputs,
                "producer_type": producer_type,
            }
        )
    return records


def _build_convention_records(repo_root: Path, scan_root: Path) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    canonical_keep = {
        "external_finalization_receipt.json",
        "commit_push_receipt.json",
        "final_owner_summary_ru.md",
        "next_pipeline_handoff.json",
        "hard_red_team_verdict.json",
        "head_taxonomy_manifest.json",
        "combined_review_adjudication_receipt.json",
        "closure_receipt.json",
        "receipt_index.json",
    }
    for path in scan_root.rglob("*"):
        if not path.is_file():
            continue
        if _is_ignored_path(path):
            continue
        name = path.name.lower()
        if not (name.endswith(".json") or name.endswith(".md") or name.endswith(".zip")):
            continue
        if not any(
            token in name
            for token in (
                "receipt",
                "verdict",
                "finalization",
                "handoff",
                "summary",
                "taxonomy_manifest",
                "adjudication",
                "closeout",
            )
        ):
            continue
        rel = _normalize(path, repo_root)
        buckets[name].append(rel)

    records: list[dict[str, Any]] = []
    for basename, paths in sorted(buckets.items()):
        if len(paths) < 2 and basename not in canonical_keep:
            continue
        sample = sorted(paths)[0]
        text = f"observed {len(paths)} occurrences for {basename}"
        dangerous = [field for field in DANGEROUS_FIELDS if field in basename]
        records.append(
            {
                "rel_path": sample,
                "text": text,
                "dangerous": dangerous,
                "outputs": [basename],
                "producer_type": "AGENT_OUTPUT_CONVENTION",
                "related_files": sorted(paths)[:10],
            }
        )
    return records


def _dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        key = record["rel_path"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _to_items(records: list[dict[str, Any]]) -> list[ProducerItem]:
    items: list[ProducerItem] = []
    for index, record in enumerate(sorted(records, key=lambda r: r["rel_path"]), start=1):
        rel_path = record["rel_path"]
        text = record.get("text", "")
        dangerous = sorted(set(record.get("dangerous", [])))
        outputs = sorted(set(record.get("outputs", [])))
        legacy_status = _legacy_field_status(text, dangerous)
        classification = _classification(
            record.get("producer_type", "UNKNOWN"),
            text,
            dangerous,
            legacy_status,
            rel_path,
            outputs,
        )
        risk_level, migration_priority, risk_score = _risk_and_priority(classification, dangerous)
        related = record.get("related_files", [])
        line_hint = _line_hint(text)
        search_reason = f"type={record.get('producer_type','UNKNOWN')} dangerous={len(dangerous)} outputs={len(outputs)}"
        notes = "legacy_fields_detected" if dangerous else "producer_signal_without_legacy_fields"
        items.append(
            ProducerItem(
                producer_id=f"RP-{index:04d}",
                path=rel_path,
                producer_type=record.get("producer_type", "UNKNOWN"),
                owner_organ=_owner_organ_from_path(rel_path),
                outputs_created=outputs,
                dangerous_fields_found=dangerous,
                current_classification=classification,
                risk_level=risk_level,
                migration_priority=migration_priority,
                recommended_migration_target=_recommended_target(classification),
                evidence=ProducerEvidence(
                    search_reason=search_reason,
                    excerpt_or_line_hint=line_hint,
                    related_files=related,
                ),
                notes=notes,
                legacy_field_checker_status=legacy_status,
                risk_score=risk_score,
            )
        )
    return items


def _inventory_summary(items: list[ProducerItem], task_id: str, scan_root: str) -> dict[str, Any]:
    classification_counts = {key: 0 for key in REQUIRED_CLASSIFICATIONS}
    legacy_status_counts = Counter(item.legacy_field_checker_status for item in items)
    risk_counts = Counter(item.risk_level for item in items)
    owner_counts = Counter(item.owner_organ for item in items)
    producer_type_counts = Counter(item.producer_type for item in items)
    for item in items:
        classification_counts[item.current_classification] = classification_counts.get(item.current_classification, 0) + 1

    p0_paths = [item.path for item in items if item.risk_level == "P0"]
    unresolved_unknown = [item.path for item in items if item.current_classification == "UNKNOWN_REQUIRES_REVIEW"]
    blocking_caps: list[str] = []
    if not items:
        blocking_caps.append("CAP_RECEIPT_PRODUCER_INVENTORY_MISSING")
    if not p0_paths:
        # no-op; this cap is for unresolved P0 classification, not for zero count
        pass
    if unresolved_unknown:
        blocking_caps.append("CAP_LEGACY_RECEIPT_PRODUCERS_UNCLASSIFIED")
    if p0_paths:
        blocking_caps.append("CAP_P0_PRODUCER_RISK_UNRESOLVED")

    summary = {
        "schema_id": "receipt_producer_inventory_v0_1",
        "task_id": task_id,
        "scan_root": scan_root,
        "producer_total": len(items),
        "classification_counts": classification_counts,
        "legacy_field_checker_status_counts": dict(legacy_status_counts),
        "risk_level_counts": dict(risk_counts),
        "owner_organ_counts": dict(owner_counts),
        "producer_type_counts": dict(producer_type_counts),
        "p0_candidate_paths": p0_paths[:200],
        "unknown_requires_review_paths": unresolved_unknown[:200],
        "caps_triggered": [cap for cap in blocking_caps if cap in CAPS_FOR_CLASSIFICATION],
    }
    return summary


def _priority_matrix(items: list[ProducerItem], task_id: str) -> dict[str, Any]:
    sorted_items = sorted(items, key=lambda item: (-item.risk_score, item.path))
    records: list[dict[str, Any]] = []
    for rank, item in enumerate(sorted_items, start=1):
        if item.migration_priority == "NOT_APPLICABLE":
            continue
        records.append(
            {
                "rank": rank,
                "producer_id": item.producer_id,
                "path": item.path,
                "owner_organ": item.owner_organ,
                "classification": item.current_classification,
                "risk_level": item.risk_level,
                "risk_score": item.risk_score,
                "migration_priority": item.migration_priority,
                "recommended_migration_target": item.recommended_migration_target,
                "dangerous_fields_found": item.dangerous_fields_found,
                "legacy_field_checker_status": item.legacy_field_checker_status,
            }
        )

    p0 = [r for r in records if r["risk_level"] == "P0"]
    p1 = [r for r in records if r["risk_level"] == "P1"]
    p2 = [r for r in records if r["risk_level"] == "P2"]
    p3 = [r for r in records if r["risk_level"] == "P3"]

    return {
        "schema_id": "receipt_producer_migration_priority_matrix_v0_1",
        "task_id": task_id,
        "priority_groups": {
            "P0_BLOCKS_STAGE_1": p0,
            "P1_MIGRATE_BEFORE_REAL_USE_PILOT": p1,
            "P2_MIGRATE_BEFORE_IDE_RELEASE": p2,
            "P3_LOW_RISK_OR_ALREADY_MIGRATED": p3,
        },
        "records": records,
    }


def _build_legacy_field_scan(items: list[ProducerItem], scan_root: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for item in items:
        if not item.dangerous_fields_found:
            rows.append(
                {
                    "path": item.path,
                    "field_or_text": "",
                    "classification": "NOT_APPLICABLE",
                    "owner_organ": item.owner_organ,
                    "risk_level": item.risk_level,
                    "reason": "No dangerous fields detected in this producer candidate.",
                }
            )
            continue
        for field in item.dangerous_fields_found:
            rows.append(
                {
                    "path": item.path,
                    "field_or_text": field,
                    "classification": item.legacy_field_checker_status,
                    "owner_organ": item.owner_organ,
                    "risk_level": item.risk_level,
                    "reason": item.evidence.excerpt_or_line_hint,
                }
            )

    summary = Counter(row["classification"] for row in rows)
    return {
        "scan_id": "legacy_receipt_field_scan_v0_1",
        "scanned_root": scan_root,
        "dangerous_fields": DANGEROUS_FIELDS,
        "results": rows,
        "summary": dict(summary),
    }


def _json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_inventory_md(path: Path, summary: dict[str, Any], items: list[ProducerItem]) -> None:
    lines: list[str] = []
    lines.append("# Receipt Producer Inventory")
    lines.append("")
    lines.append(f"- producer_total: {summary['producer_total']}")
    lines.append(f"- p0_candidates: {len(summary['p0_candidate_paths'])}")
    lines.append(f"- unknown_requires_review: {len(summary['unknown_requires_review_paths'])}")
    lines.append(f"- caps_triggered: {', '.join(summary['caps_triggered']) if summary['caps_triggered'] else 'none'}")
    lines.append("")
    lines.append("## Classification Counts")
    for key in REQUIRED_CLASSIFICATIONS:
        lines.append(f"- {key}: {summary['classification_counts'].get(key, 0)}")
    lines.append("")
    lines.append("## Top Risk Producers")
    lines.append("| producer_id | risk | classification | owner | path |")
    lines.append("|---|---|---|---|---|")
    top = sorted(items, key=lambda item: (-item.risk_score, item.path))[:120]
    for item in top:
        lines.append(
            f"| {item.producer_id} | {item.risk_level} ({item.risk_score}) | {item.current_classification} | {item.owner_organ} | `{item.path}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_priority_md(path: Path, matrix: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Receipt Producer Migration Priority Matrix")
    lines.append("")
    for group_name, rows in matrix["priority_groups"].items():
        lines.append(f"## {group_name}")
        lines.append(f"- count: {len(rows)}")
        lines.append("| rank | producer_id | risk | classification | owner | path |")
        lines.append("|---|---|---|---|---|---|")
        for row in rows[:120]:
            lines.append(
                f"| {row['rank']} | {row['producer_id']} | {row['risk_level']} ({row['risk_score']}) | {row['classification']} | {row['owner_organ']} | `{row['path']}` |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_legacy_md(path: Path, scan: dict[str, Any]) -> None:
    summary = scan["summary"]
    rows = scan["results"]
    lines: list[str] = []
    lines.append("# Legacy Receipt Field Checker Report")
    lines.append("")
    lines.append(f"- scan_id: {scan['scan_id']}")
    lines.append(f"- scanned_root: {scan['scanned_root']}")
    lines.append(f"- dangerous_fields: {', '.join(scan['dangerous_fields'])}")
    lines.append("")
    lines.append("## Classification Summary")
    for key in ["SAFE_NEW_SEMANTICS", "AMBIGUOUS_LEGACY_FIELD", "LIKELY_SELF_HEAD_RISK", "MANUAL_REVIEW", "NOT_APPLICABLE"]:
        lines.append(f"- {key}: {summary.get(key, 0)}")
    lines.append("")
    lines.append("## Top Non-Safe Findings")
    lines.append("| classification | risk | owner | field | path | reason |")
    lines.append("|---|---|---|---|---|---|")
    non_safe = [
        row
        for row in rows
        if row["classification"] in {"AMBIGUOUS_LEGACY_FIELD", "LIKELY_SELF_HEAD_RISK", "MANUAL_REVIEW"}
    ][:220]
    for row in non_safe:
        reason = row["reason"].replace("|", "/")
        lines.append(
            f"| {row['classification']} | {row['risk_level']} | {row['owner_organ']} | {row['field_or_text'] or '-'} | `{row['path']}` | {reason} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    scan_root = (repo_root / args.scan_root).resolve()
    report_root = Path(args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    file_records = _build_from_real_files(repo_root, scan_root, args.max_bytes)
    convention_records = _build_convention_records(repo_root, scan_root)
    items = _to_items(_dedupe(file_records + convention_records))

    summary = _inventory_summary(items, args.task_id, args.scan_root)
    inventory_json = {
        "schema_id": "receipt_producer_inventory_v0_1",
        "task_id": args.task_id,
        "scan_root": args.scan_root,
        "summary": summary,
        "items": [item.to_inventory_dict() for item in items],
    }
    matrix_json = _priority_matrix(items, args.task_id)
    legacy_scan = _build_legacy_field_scan(items, args.scan_root)

    _json_dump(report_root / "receipt_producer_inventory.json", inventory_json)
    _json_dump(report_root / "receipt_producer_migration_priority_matrix.json", matrix_json)
    _json_dump(report_root / "legacy_receipt_field_scan_result.json", legacy_scan)

    _write_inventory_md(report_root / "receipt_producer_inventory.md", summary, items)
    _write_priority_md(report_root / "receipt_producer_migration_priority_matrix.md", matrix_json)
    _write_legacy_md(report_root / "legacy_receipt_field_checker_report.md", legacy_scan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
