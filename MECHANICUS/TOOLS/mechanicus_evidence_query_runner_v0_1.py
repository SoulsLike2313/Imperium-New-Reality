from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1"
MAX_TABLE_ROWS = 20
MAX_SAMPLE_CHARS = 220


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_text(text: str, limit: int = MAX_SAMPLE_CHARS) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "...<truncated>"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_sql_scalar(conn: sqlite3.Connection, sql: str) -> dict[str, Any]:
    row = conn.execute(sql).fetchone()
    if row is None:
        return {"result": 0}
    value = row[0]
    return {"result": value}


def run_sql_table(conn: sqlite3.Connection, sql: str) -> dict[str, Any]:
    cursor = conn.execute(sql)
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = cursor.fetchmany(MAX_TABLE_ROWS)
    sample: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for index, value in enumerate(row):
            key = columns[index] if index < len(columns) else f"col_{index + 1}"
            if isinstance(value, str):
                item[key] = short_text(value)
            else:
                item[key] = value
        sample.append(item)

    total_count = len(rows)
    if sample:
        count_sql = f"SELECT COUNT(1) FROM ({sql})"
        total_count = int(conn.execute(count_sql).fetchone()[0])
    return {"count": total_count, "sample": sample}


def run_fts(conn: sqlite3.Connection, fts_query: str, limit: int) -> dict[str, Any]:
    cursor = conn.execute(
        """
        SELECT source_path, title, summary
        FROM evidence_fts
        WHERE evidence_fts MATCH ?
        LIMIT ?
        """,
        (fts_query, int(limit)),
    )
    rows = cursor.fetchall()
    sample = [
        {
            "source_path": row[0],
            "title": short_text(str(row[1])),
            "summary": short_text(str(row[2])),
        }
        for row in rows
    ]
    count = int(
        conn.execute(
            "SELECT COUNT(1) FROM evidence_fts WHERE evidence_fts MATCH ?",
            (fts_query,),
        ).fetchone()[0]
    )
    return {"count": count, "sample": sample}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evidence query examples over Mechanicus evidence index.")
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    output_root = (repo_root / args.output_root).resolve()
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    db_path = output_root / "evidence_index.sqlite3"
    query_examples_path = output_root / "example_queries_v0_1.json"
    report_path = report_root / "evidence_query_smoke_report.json"

    warnings: list[str] = []
    errors: list[str] = []
    query_results: list[dict[str, Any]] = []

    if not db_path.exists():
        payload = {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_evidence_query_runner_v0_1.py",
            "warnings": [],
            "errors": ["missing_database"],
            "verdict": "FAIL",
            "raw_dump_status": "COMPACT_ONLY",
        }
        write_json(report_path, payload)
        print(json.dumps({"task_id": args.task_id, "verdict": "FAIL"}, ensure_ascii=False))
        return 1

    if not query_examples_path.exists():
        payload = {
            "task_id": args.task_id,
            "generated_at_utc": utc_now(),
            "checker": "mechanicus_evidence_query_runner_v0_1.py",
            "warnings": [],
            "errors": ["missing_example_queries"],
            "verdict": "FAIL",
            "raw_dump_status": "COMPACT_ONLY",
        }
        write_json(report_path, payload)
        print(json.dumps({"task_id": args.task_id, "verdict": "FAIL"}, ensure_ascii=False))
        return 1

    query_payload = read_json(query_examples_path)
    examples = query_payload.get("query_examples", [])
    if not isinstance(examples, list):
        examples = []

    with sqlite3.connect(db_path) as conn:
        for item in examples:
            if not isinstance(item, dict):
                warnings.append("invalid_query_definition_non_dict")
                continue
            query_id = str(item.get("query_id", "UNKNOWN"))
            mode = str(item.get("mode", ""))
            result_row: dict[str, Any] = {"query_id": query_id, "mode": mode}
            try:
                if mode == "sql_scalar":
                    sql = str(item.get("sql", ""))
                    scalar = run_sql_scalar(conn, sql)
                    result_row["result_count"] = int(scalar.get("result", 0) or 0)
                    result_row["sample"] = [{"result": scalar.get("result")}]
                    result_row["verdict"] = "PASS"
                elif mode == "sql_table":
                    sql = str(item.get("sql", ""))
                    table = run_sql_table(conn, sql)
                    result_row["result_count"] = int(table.get("count", 0))
                    result_row["sample"] = table.get("sample", [])
                    result_row["verdict"] = "PASS"
                elif mode == "fts":
                    fts_query = str(item.get("fts_query", ""))
                    limit = int(item.get("limit", MAX_TABLE_ROWS))
                    fts_result = run_fts(conn, fts_query, limit)
                    result_row["result_count"] = int(fts_result.get("count", 0))
                    result_row["sample"] = fts_result.get("sample", [])
                    result_row["verdict"] = "PASS"
                else:
                    result_row["result_count"] = 0
                    result_row["sample"] = []
                    result_row["verdict"] = "WARN"
                    warnings.append(f"unknown_query_mode:{query_id}:{mode}")
            except Exception as exc:
                result_row["result_count"] = 0
                result_row["sample"] = []
                result_row["verdict"] = "FAIL"
                result_row["error"] = str(exc)
                errors.append(f"query_failed:{query_id}")
            query_results.append(result_row)

    failed_queries = sum(1 for row in query_results if row.get("verdict") == "FAIL")
    warn_queries = sum(1 for row in query_results if row.get("verdict") == "WARN")
    non_zero_results = sum(1 for row in query_results if int(row.get("result_count", 0)) > 0)

    verdict = "PASS"
    if failed_queries > 0:
        verdict = "FAIL"
    elif warn_queries > 0:
        verdict = "PASS_WITH_WARNINGS"

    payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_evidence_query_runner_v0_1.py",
        "db_path": db_path.relative_to(repo_root).as_posix(),
        "query_examples_path": query_examples_path.relative_to(repo_root).as_posix(),
        "summary": {
            "query_count": len(query_results),
            "failed_queries": failed_queries,
            "warn_queries": warn_queries,
            "non_zero_results": non_zero_results,
        },
        "query_results": query_results,
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(report_path, payload)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": verdict,
                "queries": len(query_results),
                "failed": failed_queries,
            },
            ensure_ascii=False,
        )
    )
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
