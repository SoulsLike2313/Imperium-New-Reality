from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1"

SOURCE_GLOBS: tuple[str, ...] = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/**/*.md",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/**/*.json",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/**/capability_card.json",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS/**/*.json",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/**/*.json",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/**/*.md",
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/ROLE_PACKS/**/*.json",
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/CONTRACTS/**/*.md",
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/TEMPLATES/**/*.md",
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/REPORTS/**/*.json",
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/REPORTS/**/*.md",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Mechanicus evidence index outputs and emit handoff reports.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output-root",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1",
    )
    parser.add_argument(
        "--report-root",
        default=(
            "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
            "TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1"
        ),
    )
    parser.add_argument("--min-records", type=int, default=50)
    parser.add_argument("--py-compile-status", default="UNKNOWN")
    parser.add_argument("--ruff-status", default="UNKNOWN")
    parser.add_argument("--mypy-status", default="WARN")
    parser.add_argument("--json-parse-status", default="UNKNOWN")
    parser.add_argument("--query-smoke-status", default="UNKNOWN")
    return parser.parse_args()


def normalize_status(value: str) -> str:
    upper = value.strip().upper()
    if upper in {"PASS", "PASS_WITH_WARNINGS", "WARN", "FAIL", "BLOCKED", "UNKNOWN"}:
        return upper
    return "UNKNOWN"


def overall_from_statuses(statuses: dict[str, str], hard_fail: list[str]) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []
    for name, status in statuses.items():
        if status in {"FAIL", "BLOCKED"}:
            failures.append(f"{name}:{status}")
        elif status in {"WARN", "PASS_WITH_WARNINGS"}:
            warnings.append(f"{name}:{status}")
    failures.extend(hard_fail)

    if failures:
        return "FAIL", warnings, failures
    if warnings:
        return "PASS_WITH_WARNINGS", warnings, failures
    return "PASS", warnings, failures


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    output_root = (repo_root / args.output_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    db_path = output_root / "evidence_index.sqlite3"
    manifest_path = output_root / "evidence_index_manifest.json"
    coverage_report_path = report_root / "evidence_index_coverage_report.json"
    inquisition_report_path = report_root / "inquisition_evidence_safety_report.json"
    handoff_report_path = report_root / "administratum_evidence_index_handoff.json"
    ghost_report_path = report_root / "ghost_evolve_evidence_index_training_proof.json"
    quality_report_path = report_root / "quality_gate_result_report.json"

    hard_fail: list[str] = []
    warnings: list[str] = []

    if not db_path.exists():
        hard_fail.append("missing_database")
    if not manifest_path.exists():
        hard_fail.append("missing_manifest")

    record_count = 0
    fts_count = 0
    source_files_indexed = 0
    source_type_counts: dict[str, int] = {}
    organ_counts: dict[str, int] = {}
    task_links = 0
    commit_links = 0
    capability_links = 0
    receipt_links = 0
    fake_canon_count = 0
    private_hits: list[str] = []
    fts_smoke_count = 0
    indexed_paths: list[str] = []

    if not hard_fail:
        with sqlite3.connect(db_path) as conn:
            record_count = int(conn.execute("SELECT COUNT(1) FROM evidence_records").fetchone()[0])
            fts_count = int(conn.execute("SELECT COUNT(1) FROM evidence_fts").fetchone()[0])
            source_files_indexed = int(conn.execute("SELECT COUNT(1) FROM source_file_index").fetchone()[0])
            task_links = int(conn.execute("SELECT COUNT(1) FROM task_index").fetchone()[0])
            commit_links = int(conn.execute("SELECT COUNT(1) FROM commit_index").fetchone()[0])
            capability_links = int(conn.execute("SELECT COUNT(1) FROM capability_index").fetchone()[0])
            receipt_links = int(conn.execute("SELECT COUNT(1) FROM receipt_index").fetchone()[0])
            fake_canon_count = int(
                conn.execute(
                    """
                    SELECT COALESCE(SUM(match_count), 0)
                    FROM warning_error_index
                    WHERE pattern_id = 'fake_canon_count'
                    """
                ).fetchone()[0]
            )
            fts_smoke_count = int(
                conn.execute(
                    """
                    SELECT COUNT(1) FROM evidence_fts
                    WHERE evidence_fts MATCH 'evidence OR quality OR hygiene'
                    """
                ).fetchone()[0]
            )
            for row in conn.execute(
                "SELECT source_type, COUNT(1) FROM evidence_records GROUP BY source_type ORDER BY source_type"
            ):
                source_type_counts[str(row[0])] = int(row[1])
            for row in conn.execute(
                "SELECT organ, COUNT(1) FROM evidence_records GROUP BY organ ORDER BY organ"
            ):
                organ_counts[str(row[0])] = int(row[1])
            indexed_paths = [str(row[0]) for row in conn.execute("SELECT source_path FROM source_file_index")]

        private_hits = [
            path
            for path in indexed_paths
            if (
                not path.startswith("IMPERIUM_NEW_GENERATION/")
                or "IMPERIUM_CONTEXT" in path
                or path.startswith("C:/")
                or path.startswith("E:/IMPERIUM_CONTEXT")
                or "/Users/" in path
                or "\\Users\\" in path
            )
        ]

    if record_count < int(args.min_records):
        warnings.append(f"record_count_below_min:{record_count}<{args.min_records}")
    if fts_count <= 0:
        hard_fail.append("fts_empty_or_unavailable")
    if private_hits:
        hard_fail.append("private_context_indexed")

    indexed_set = set(indexed_paths)
    coverage_by_glob: list[dict[str, Any]] = []
    for pattern in SOURCE_GLOBS:
        expected_files = {
            path.relative_to(repo_root).as_posix()
            for path in repo_root.glob(pattern)
            if path.is_file()
        }
        matched = len(indexed_set & expected_files)
        expected_count = len(expected_files)
        verdict = "PASS"
        if expected_count > 0 and matched < expected_count:
            verdict = "WARN"
            warnings.append(f"partial_coverage:{pattern}:{matched}/{expected_count}")
        coverage_by_glob.append(
            {
                "pattern": pattern,
                "expected_files": expected_count,
                "matched_files": matched,
                "verdict": verdict,
            }
        )

    statuses = {
        "py_compile": normalize_status(args.py_compile_status),
        "ruff": normalize_status(args.ruff_status),
        "mypy": normalize_status(args.mypy_status),
        "json_parse": normalize_status(args.json_parse_status),
        "query_smoke": normalize_status(args.query_smoke_status),
        "sqlite_open": "PASS" if not hard_fail else "FAIL",
        "fts_smoke": "PASS" if fts_smoke_count > 0 else "FAIL",
        "private_scope_exclusion": "PASS" if not private_hits else "FAIL",
        "record_threshold": "PASS" if record_count >= int(args.min_records) else "WARN",
    }
    overall_verdict, status_warnings, status_failures = overall_from_statuses(statuses, hard_fail)
    warnings.extend(status_warnings)

    coverage_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "check_mechanicus_evidence_index_v0_1.py",
        "summary": {
            "records_indexed": record_count,
            "fts_rows": fts_count,
            "source_files_indexed": source_files_indexed,
            "task_links": task_links,
            "commit_links": commit_links,
            "capability_links": capability_links,
            "receipt_links": receipt_links,
            "private_paths_indexed": len(private_hits),
        },
        "source_type_counts": source_type_counts,
        "organ_counts": organ_counts,
        "coverage_by_glob": coverage_by_glob,
        "warnings": warnings,
        "errors": status_failures,
        "verdict": overall_verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(coverage_report_path, coverage_payload)

    inquisition_verdict = "PASS"
    inquisition_risks: list[str] = []
    if private_hits:
        inquisition_verdict = "FAIL"
        inquisition_risks.append("private_context_indexed")
    if record_count < int(args.min_records):
        inquisition_verdict = "WARN"
        inquisition_risks.append("record_count_below_target")
    if fake_canon_count > 0:
        inquisition_risks.append("fake_canon_mentions_present")

    inquisition_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "handoff_to": "INQUISITION",
        "checker": "check_mechanicus_evidence_index_v0_1.py",
        "private_context_indexed": len(private_hits) > 0,
        "private_context_samples": private_hits[:20],
        "fake_canon_count": fake_canon_count,
        "fts_smoke_count": fts_smoke_count,
        "risks": inquisition_risks,
        "verdict": inquisition_verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(inquisition_report_path, inquisition_payload)

    handoff_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "handoff_to": "ADMINISTRATUM",
        "db_path": db_path.relative_to(repo_root).as_posix() if db_path.exists() else "",
        "manifest_path": manifest_path.relative_to(repo_root).as_posix() if manifest_path.exists() else "",
        "summary": {
            "records_indexed": record_count,
            "source_files_indexed": source_files_indexed,
            "task_links": task_links,
            "commit_links": commit_links,
            "source_type_count": len(source_type_counts),
        },
        "ownership_recommendation": (
            "Administratum owns recurring evidence map snapshots; "
            "Mechanicus owns builder/query/check tooling refresh."
        ),
        "next_refresh_command": (
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/"
            "mechanicus_evidence_index_builder_v0_1.py --repo-root E:\\IMPERIUM"
        ),
        "verdict": "PASS" if db_path.exists() and manifest_path.exists() else "FAIL",
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(handoff_report_path, handoff_payload)

    ghost_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "contract": "Ghost_Evolve Evidence Index Contract V0.1",
        "manual_search_work_converted": [
            "reports/receipts lookup by task id and verdict",
            "warning/error term discovery via FTS",
            "task-to-commit linkage extraction",
            "capability and receipt path discovery",
        ],
        "rebuild_steps": [
            "run mechanicus_evidence_index_builder_v0_1.py",
            "run mechanicus_evidence_query_runner_v0_1.py",
            "run check_mechanicus_evidence_index_v0_1.py",
        ],
        "covered_categories": sorted(source_type_counts.keys()),
        "intentional_exclusions": [
            "private/local external context",
            "full-repository blind indexing",
            "binary payload content indexing",
            "LLM/cloud source ingestion",
        ],
        "future_servitor_manual_work_reduced": [
            "manual grep across every report folder",
            "manual commit hash hunting in markdown/json files",
            "manual warning/error trend extraction",
        ],
        "verdict": "PASS" if record_count > 0 else "FAIL",
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(ghost_report_path, ghost_payload)

    quality_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "check_mechanicus_evidence_index_v0_1.py",
        "gates": statuses,
        "overall_verdict": overall_verdict,
        "warnings": warnings,
        "failures": status_failures,
        "reports": [
            coverage_report_path.relative_to(repo_root).as_posix(),
            inquisition_report_path.relative_to(repo_root).as_posix(),
            handoff_report_path.relative_to(repo_root).as_posix(),
            ghost_report_path.relative_to(repo_root).as_posix(),
        ],
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(quality_report_path, quality_payload)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": overall_verdict,
                "records_indexed": record_count,
                "private_paths": len(private_hits),
                "fts_smoke_count": fts_smoke_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if overall_verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
