from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
MAX_DOCS = 200
MAX_SNIPPET_CHARS = 300
MAX_QUERY_RESULTS = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def short_text(value: str, limit: int = MAX_SNIPPET_CHARS) -> str:
    text = value.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def collect_documents(report_root: Path) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for path in sorted(report_root.glob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".md"}:
            continue
        text = read_text_safe(path)
        snippet = short_text(text)
        docs.append(
            {
                "doc_id": hashlib.sha256(path.as_posix().encode("utf-8")).hexdigest()[:16],
                "path": path.as_posix(),
                "title": path.name,
                "snippet": snippet,
                "content": text[:3000],
            }
        )
        if len(docs) >= MAX_DOCS:
            break
    return docs


def run_smoke_index(report_root: Path, db_path: Path) -> dict[str, Any]:
    documents = collect_documents(report_root)
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    warnings: list[str] = []
    query_results: list[dict[str, str]] = []
    fts_enabled = False

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE docs (
                doc_id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL,
                snippet TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO docs(doc_id, path, title, snippet, content) VALUES(:doc_id, :path, :title, :snippet, :content)",
            documents,
        )

        try:
            conn.execute("CREATE VIRTUAL TABLE docs_fts USING fts5(doc_id, path, title, content)")
            conn.executemany(
                "INSERT INTO docs_fts(doc_id, path, title, content) VALUES(:doc_id, :path, :title, :content)",
                documents,
            )
            fts_enabled = True
            cursor = conn.execute(
                """
                SELECT path, title
                FROM docs_fts
                WHERE docs_fts MATCH ?
                LIMIT ?
                """,
                ("gate OR verdict OR fake", MAX_QUERY_RESULTS),
            )
            query_results = [{"path": row[0], "title": row[1]} for row in cursor.fetchall()]
        except sqlite3.OperationalError as exc:
            warnings.append(f"fts5_unavailable:{exc}")
            cursor = conn.execute(
                """
                SELECT path, title
                FROM docs
                WHERE lower(content) LIKE '%gate%'
                   OR lower(content) LIKE '%verdict%'
                   OR lower(content) LIKE '%fake%'
                LIMIT ?
                """,
                (MAX_QUERY_RESULTS,),
            )
            query_results = [{"path": row[0], "title": row[1]} for row in cursor.fetchall()]
        except Exception as exc:
            errors.append(f"fts_query_failed:{exc}")

    verdict = "PASS"
    if not documents:
        verdict = "FAIL"
        errors.append("no_documents_indexed")
    elif errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    return {
        "generated_at_utc": utc_now(),
        "checker": "evidence_index_smoke_v0_1.py",
        "db_path": db_path.as_posix(),
        "summary": {
            "documents_indexed": len(documents),
            "fts_enabled": fts_enabled,
            "query_result_count": len(query_results),
        },
        "query_results_sample": query_results[:MAX_QUERY_RESULTS],
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create tiny SQLite/FTS evidence smoke index for report artifacts.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--report-root", required=True)
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_root = Path(args.report_root).resolve()
    db_path = Path(args.db_path).resolve()
    output = Path(args.output).resolve()

    payload = run_smoke_index(report_root=report_root, db_path=db_path)
    payload["task_id"] = args.task_id
    write_json(output, payload)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": payload["verdict"],
                "documents_indexed": payload["summary"]["documents_indexed"],
                "fts_enabled": payload["summary"]["fts_enabled"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if payload["verdict"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
