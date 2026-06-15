from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1"
MAX_EXCERPT_CHARS = 480
MAX_SUMMARY_CHARS = 240
MAX_TITLE_CHARS = 160

SOURCE_GLOBS: tuple[str, ...] = (
    "MECHANICUS/REPORTS/**/*.md",
    "MECHANICUS/REPORTS/**/*.json",
    "MECHANICUS/ARSENAL/CATEGORIES/**/capability_card.json",
    "MECHANICUS/ARSENAL/RECEIPTS/**/*.json",
    "MECHANICUS/ARSENAL/SCOPE_PACKS/**/*.json",
    "MECHANICUS/ARSENAL/SCOPE_PACKS/**/*.md",
    "OFFICIO_AGENTIS/ROLE_PACKS/**/*.json",
    "OFFICIO_AGENTIS/CONTRACTS/**/*.md",
    "OFFICIO_AGENTIS/TEMPLATES/**/*.md",
    "OFFICIO_AGENTIS/REPORTS/**/*.json",
    "OFFICIO_AGENTIS/REPORTS/**/*.md",
)

SOURCE_TYPE_EXAMPLES: dict[str, str] = {
    "FINAL_REPORT": "Final task report markdown.",
    "CLOSURE_RECEIPT": "Task closure receipt JSON.",
    "ADMINISTRATUM_EVIDENCE_MAP": "Evidence handoff map for Administratum.",
    "INQUISITION_REPORT": "Inquisition safety or hygiene report.",
    "MECHANICUS_SCOPE_PACK": "Mechanicus scope pack markdown/json.",
    "CAPABILITY_CARD": "Capability card JSON.",
    "VALIDATION_RECEIPT": "Validation or generic receipt JSON.",
    "INSTALL_RECEIPT": "Install receipt JSON.",
    "ROLE_PACK": "Officio role pack JSON.",
    "CONTRACT": "Contract markdown file.",
    "TEMPLATE": "Template markdown file.",
    "TOOL_REPORT": "Tool-generated report JSON/MD.",
    "UNKNOWN_JSON": "JSON not matched by a specific type rule.",
    "UNKNOWN_MD": "Markdown not matched by a specific type rule.",
}

TASK_ID_PATTERN = re.compile(r"TASK-[A-Z0-9]+(?:[-_][A-Z0-9]+)*")
COMMIT_PATTERN = re.compile(r"\b[0-9a-f]{7,40}\b")
VERDICT_PATTERN = re.compile(r"\b(PASS_WITH_WARNINGS|PASS|WARN|WARNING|FAIL|BLOCKED)\b")


@dataclass(frozen=True)
class PatternSpec:
    pattern_id: str
    label: str
    regex: str
    severity: str


PATTERN_SPECS: tuple[PatternSpec, ...] = (
    PatternSpec(
        pattern_id="fake_canon_count",
        label="Fake canon references",
        regex=r"fake[_\s-]?canon[_\s-]?count|fake\s+canon",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="PASS_WITH_WARNINGS",
        label="PASS_WITH_WARNINGS verdicts",
        regex=r"PASS_WITH_WARNINGS",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="hygiene",
        label="Hygiene findings",
        regex=r"hygiene",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="runtime_junk",
        label="Runtime junk mentions",
        regex=r"runtime[_\s-]?junk",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="pycache",
        label="Pycache artifact mention",
        regex=r"__pycache__|pycache",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="pyc",
        label="PYC artifact mention",
        regex=r"\.pyc\b",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="missing_ACK",
        label="Missing ACK mention",
        regex=r"missing\s+ack|ack[_\s-]?violation",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="language_violation",
        label="Language violation mention",
        regex=r"language[_\s-]?violation|OFFICIO_LANGUAGE_VIOLATION_WARN",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="NO_SCHEMA_AVAILABLE",
        label="No schema available markers",
        regex=r"NO_SCHEMA_AVAILABLE",
        severity="warning",
    ),
    PatternSpec(
        pattern_id="BLOCKED",
        label="BLOCKED verdict mentions",
        regex=r"\bBLOCKED\b",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="FAIL",
        label="FAIL verdict mentions",
        regex=r"\bFAIL\b",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="install_performed",
        label="Install performed mention",
        regex=r"install(ed|_performed)|pip\s+install|npm\s+install",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="visual_prototype",
        label="Visual prototype mention",
        regex=r"visual\s+prototype",
        severity="critical",
    ),
    PatternSpec(
        pattern_id="LLM_cloud",
        label="LLM/cloud mention",
        regex=r"\bLLM\b|cloud",
        severity="critical",
    ),
)

PATTERN_REGEX: dict[str, re.Pattern[str]] = {
    spec.pattern_id: re.compile(spec.regex, re.IGNORECASE) for spec in PATTERN_SPECS
}

SQL_SCHEMA_V0_1 = """-- Evidence Index Schema V0.1
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evidence_records (
    record_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    source_type TEXT NOT NULL,
    organ TEXT NOT NULL,
    task_id TEXT,
    commit_hash TEXT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT NOT NULL,
    tags TEXT NOT NULL,
    created_at_utc TEXT,
    indexed_at_utc TEXT NOT NULL,
    content_excerpt TEXT NOT NULL,
    sha256 TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(
    record_id UNINDEXED,
    title,
    summary,
    content_excerpt,
    tags,
    source_path
);

CREATE TABLE IF NOT EXISTS task_index (
    task_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    PRIMARY KEY (task_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS commit_index (
    commit_hash TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    PRIMARY KEY (commit_hash, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS capability_index (
    capability_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT NOT NULL,
    PRIMARY KEY (capability_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receipt_index (
    receipt_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    verdict TEXT NOT NULL,
    PRIMARY KEY (receipt_name, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS warning_error_index (
    pattern_id TEXT NOT NULL,
    pattern_label TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    match_count INTEGER NOT NULL,
    severity TEXT NOT NULL,
    PRIMARY KEY (pattern_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS source_file_index (
    source_path TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    organ TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    file_mtime_utc TEXT NOT NULL,
    sha256 TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_records_source_type ON evidence_records(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_records_organ ON evidence_records(organ);
CREATE INDEX IF NOT EXISTS idx_evidence_records_verdict ON evidence_records(verdict);
CREATE INDEX IF NOT EXISTS idx_task_index_task_id ON task_index(task_id);
CREATE INDEX IF NOT EXISTS idx_commit_index_commit_hash ON commit_index(commit_hash);
CREATE INDEX IF NOT EXISTS idx_warning_error_pattern_id ON warning_error_index(pattern_id);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_text(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "...<truncated>"


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def json_load_safe(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def collect_source_files(newgen_root: Path) -> list[Path]:
    files: set[Path] = set()
    for pattern in SOURCE_GLOBS:
        for path in newgen_root.glob(pattern):
            if path.is_file():
                files.add(path.resolve())
    return sorted(files)


def detect_source_type(source_path: str, parsed_json: Any | None) -> str:
    lower = source_path.lower()
    name = Path(source_path).name.lower()
    if name == "final_report.md":
        return "FINAL_REPORT"
    if name == "closure_receipt.json":
        return "CLOSURE_RECEIPT"
    if name == "administratum_evidence_map.json":
        return "ADMINISTRATUM_EVIDENCE_MAP"
    if "inquisition" in name and name.endswith(".json"):
        return "INQUISITION_REPORT"
    if "arsenal/categories/" in lower and name == "capability_card.json":
        return "CAPABILITY_CARD"
    if "arsenal/scope_packs/" in lower:
        return "MECHANICUS_SCOPE_PACK"
    if "officio_agentis/role_packs/" in lower:
        return "ROLE_PACK"
    if "officio_agentis/contracts/" in lower:
        return "CONTRACT"
    if "officio_agentis/templates/" in lower:
        return "TEMPLATE"
    if "receipt" in name and name.endswith(".json"):
        if "install" in name:
            return "INSTALL_RECEIPT"
        return "VALIDATION_RECEIPT"
    if name.endswith("_report.json"):
        return "TOOL_REPORT"
    if name.endswith(".json"):
        if (
            isinstance(parsed_json, dict)
            and "verdict" in parsed_json
            and "generated_at_utc" in parsed_json
        ):
            return "TOOL_REPORT"
        return "UNKNOWN_JSON"
    if name.endswith(".md"):
        return "UNKNOWN_MD"
    return "UNKNOWN_JSON"


def detect_organ(source_path: str, source_type: str) -> str:
    if source_type == "ADMINISTRATUM_EVIDENCE_MAP":
        return "ADMINISTRATUM"
    if source_type == "INQUISITION_REPORT":
        return "INQUISITION"
    if source_path.startswith("IMPERIUM_NEW_GENERATION/MECHANICUS/"):
        return "MECHANICUS"
    if source_path.startswith("IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/"):
        return "OFFICIO_AGENTIS"
    return "UNKNOWN"


def find_task_ids(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for match in TASK_ID_PATTERN.findall(text):
        if match not in seen:
            seen.add(match)
            out.append(match)
    return out


def find_commit_hashes(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for match in COMMIT_PATTERN.findall(text):
        if match not in seen:
            seen.add(match)
            out.append(match)
    return out


def extract_verdict_and_status(text: str, parsed_json: Any | None) -> tuple[str, str]:
    verdict = "UNKNOWN"
    status = "UNKNOWN"
    if isinstance(parsed_json, dict):
        for verdict_key in ("overall_verdict", "verdict"):
            value = parsed_json.get(verdict_key)
            if isinstance(value, str) and value.strip():
                verdict = value.strip()
                break
        for status_key in ("status", "checker_status"):
            value = parsed_json.get(status_key)
            if isinstance(value, str) and value.strip():
                status = value.strip()
                break
    if verdict == "UNKNOWN":
        match = VERDICT_PATTERN.search(text)
        if match:
            verdict = match.group(1)
    if status == "UNKNOWN":
        upper = verdict.upper()
        if upper in {"PASS", "PASS_WITH_WARNINGS", "WARN", "WARNING", "FAIL", "BLOCKED"}:
            status = upper
    return verdict, status


def extract_title_summary(
    source_path: str,
    text: str,
    parsed_json: Any | None,
) -> tuple[str, str]:
    fallback_title = Path(source_path).name
    fallback_summary = short_text(text, MAX_SUMMARY_CHARS)

    if isinstance(parsed_json, dict):
        for title_key in ("title", "task_id", "scope_id", "role_id", "name"):
            value = parsed_json.get(title_key)
            if isinstance(value, str) and value.strip():
                fallback_title = value.strip()
                break
        for summary_key in ("summary", "mission", "purpose", "description"):
            value = parsed_json.get(summary_key)
            if isinstance(value, str) and value.strip():
                fallback_summary = short_text(value, MAX_SUMMARY_CHARS)
                break
    else:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            first_line = lines[0].lstrip("# ").strip()
            if first_line:
                fallback_title = first_line
            if len(lines) > 1:
                fallback_summary = short_text(lines[1], MAX_SUMMARY_CHARS)

    return short_text(fallback_title, MAX_TITLE_CHARS), fallback_summary


def extract_created_at(
    path: Path,
    parsed_json: Any | None,
) -> str:
    if isinstance(parsed_json, dict):
        for key in ("generated_at_utc", "created_utc", "timestamp_utc", "created_at_utc"):
            value = parsed_json.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return mtime.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_capability_id(source_path: str, parsed_json: Any | None) -> str:
    if "CAPABILITY_CARD" not in source_path and Path(source_path).name.lower() != "capability_card.json":
        if "arsenal/categories/" not in source_path.lower():
            return ""
    if isinstance(parsed_json, dict):
        for key in ("capability_id", "id"):
            value = parsed_json.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    parent = Path(source_path).parent
    return parent.name


def detect_receipt_name(source_path: str, source_type: str) -> str:
    if source_type in {"CLOSURE_RECEIPT", "VALIDATION_RECEIPT", "INSTALL_RECEIPT"}:
        return Path(source_path).name
    if "receipt" in source_path.lower():
        return Path(source_path).name
    return ""


def detect_warning_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for spec in PATTERN_SPECS:
        pattern = PATTERN_REGEX[spec.pattern_id]
        count = len(pattern.findall(text))
        if count > 0:
            hits[spec.pattern_id] = count
    return hits


def build_tags(
    source_type: str,
    organ: str,
    verdict: str,
    status: str,
    task_ids: list[str],
    warning_hits: dict[str, int],
) -> list[str]:
    tags = [source_type, organ]
    if verdict and verdict != "UNKNOWN":
        tags.append(verdict.upper())
    if status and status != "UNKNOWN":
        tags.append(status.upper())
    tags.extend(task_ids[:4])
    tags.extend(warning_hits.keys())
    dedup: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        clean = tag.strip()
        if not clean:
            continue
        if clean in seen:
            continue
        seen.add(clean)
        dedup.append(clean)
    return dedup


def build_record(
    repo_root: Path,
    path: Path,
    indexed_at_utc: str,
) -> dict[str, Any]:
    relative = path.relative_to(repo_root).as_posix()
    raw_bytes = path.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    text = read_text_safe(path)
    parsed_json = json_load_safe(text) if path.suffix.lower() == ".json" else None

    source_type = detect_source_type(relative, parsed_json)
    organ = detect_organ(relative, source_type)
    task_ids = find_task_ids(text)
    commits = find_commit_hashes(text)
    verdict, status = extract_verdict_and_status(text, parsed_json)
    title, summary = extract_title_summary(relative, text, parsed_json)
    created_at_utc = extract_created_at(path, parsed_json)
    warning_hits = detect_warning_hits(text)
    tags = build_tags(source_type, organ, verdict, status, task_ids, warning_hits)

    main_task_id = task_ids[0] if task_ids else ""
    main_commit = commits[0] if commits else ""
    record_key = f"{relative}:{sha256}"
    record_id = hashlib.sha256(record_key.encode("utf-8")).hexdigest()[:24]

    capability_id = ""
    if source_type == "CAPABILITY_CARD":
        capability_id = detect_capability_id(relative, parsed_json)

    receipt_name = detect_receipt_name(relative, source_type)

    return {
        "record_id": record_id,
        "source_path": relative,
        "source_type": source_type,
        "organ": organ,
        "task_id": main_task_id,
        "commit_hash": main_commit,
        "title": title,
        "summary": summary,
        "status": status,
        "verdict": verdict,
        "tags": tags,
        "created_at_utc": created_at_utc,
        "indexed_at_utc": indexed_at_utc,
        "content_excerpt": short_text(text, MAX_EXCERPT_CHARS),
        "sha256": sha256,
        "task_ids": task_ids,
        "commit_hashes": commits,
        "warning_hits": warning_hits,
        "capability_id": capability_id,
        "receipt_name": receipt_name,
        "file_size_bytes": len(raw_bytes),
        "file_mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def create_database(db_path: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    warning_rows = 0
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SQL_SCHEMA_V0_1)

        for record in records:
            conn.execute(
                """
                INSERT INTO evidence_records(
                    record_id, source_path, source_type, organ, task_id, commit_hash,
                    title, summary, status, verdict, tags, created_at_utc, indexed_at_utc,
                    content_excerpt, sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["record_id"],
                    record["source_path"],
                    record["source_type"],
                    record["organ"],
                    record["task_id"],
                    record["commit_hash"],
                    record["title"],
                    record["summary"],
                    record["status"],
                    record["verdict"],
                    json.dumps(record["tags"], ensure_ascii=False),
                    record["created_at_utc"],
                    record["indexed_at_utc"],
                    record["content_excerpt"],
                    record["sha256"],
                ),
            )
            conn.execute(
                """
                INSERT INTO evidence_fts(record_id, title, summary, content_excerpt, tags, source_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record["record_id"],
                    record["title"],
                    record["summary"],
                    record["content_excerpt"],
                    " ".join(record["tags"]),
                    record["source_path"],
                ),
            )
            conn.execute(
                """
                INSERT INTO source_file_index(
                    source_path, source_type, organ, file_size_bytes, file_mtime_utc, sha256
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record["source_path"],
                    record["source_type"],
                    record["organ"],
                    record["file_size_bytes"],
                    record["file_mtime_utc"],
                    record["sha256"],
                ),
            )

            for task_id in record["task_ids"]:
                conn.execute(
                    "INSERT OR IGNORE INTO task_index(task_id, record_id, source_path) VALUES (?, ?, ?)",
                    (task_id, record["record_id"], record["source_path"]),
                )
            for commit_hash in record["commit_hashes"]:
                conn.execute(
                    "INSERT OR IGNORE INTO commit_index(commit_hash, record_id, source_path) VALUES (?, ?, ?)",
                    (commit_hash, record["record_id"], record["source_path"]),
                )
            capability_id = record["capability_id"]
            if capability_id:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO capability_index(
                        capability_id, record_id, source_path, status, verdict
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        capability_id,
                        record["record_id"],
                        record["source_path"],
                        record["status"],
                        record["verdict"],
                    ),
                )

            receipt_name = record["receipt_name"]
            if receipt_name:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO receipt_index(
                        receipt_name, record_id, source_path, verdict
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        receipt_name,
                        record["record_id"],
                        record["source_path"],
                        record["verdict"],
                    ),
                )

            for pattern_id, match_count in record["warning_hits"].items():
                spec = next(spec for spec in PATTERN_SPECS if spec.pattern_id == pattern_id)
                conn.execute(
                    """
                    INSERT OR REPLACE INTO warning_error_index(
                        pattern_id, pattern_label, record_id, source_path, match_count, severity
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        spec.pattern_id,
                        spec.label,
                        record["record_id"],
                        record["source_path"],
                        int(match_count),
                        spec.severity,
                    ),
                )
                warning_rows += 1

        fts_count = int(conn.execute("SELECT COUNT(1) FROM evidence_fts").fetchone()[0])
        task_links = int(conn.execute("SELECT COUNT(1) FROM task_index").fetchone()[0])
        commit_links = int(conn.execute("SELECT COUNT(1) FROM commit_index").fetchone()[0])
        capability_links = int(conn.execute("SELECT COUNT(1) FROM capability_index").fetchone()[0])
        receipt_links = int(conn.execute("SELECT COUNT(1) FROM receipt_index").fetchone()[0])

    return {
        "fts_count": fts_count,
        "task_links": task_links,
        "commit_links": commit_links,
        "capability_links": capability_links,
        "receipt_links": receipt_links,
        "warning_rows": warning_rows,
    }


def build_warning_seed_payload(task_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "seed_version": "v0_1",
        "patterns": [
            {
                "pattern_id": spec.pattern_id,
                "label": spec.label,
                "regex": spec.regex,
                "severity": spec.severity,
            }
            for spec in PATTERN_SPECS
        ],
    }


def build_example_queries_payload(task_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "query_examples": [
            {
                "query_id": "fake_canon_count",
                "mode": "sql_scalar",
                "sql": (
                    "SELECT COALESCE(SUM(match_count), 0) AS result "
                    "FROM warning_error_index WHERE pattern_id = 'fake_canon_count'"
                ),
            },
            {
                "query_id": "PASS_WITH_WARNINGS",
                "mode": "sql_table",
                "sql": (
                    "SELECT source_path, verdict, status "
                    "FROM evidence_records "
                    "WHERE upper(verdict) = 'PASS_WITH_WARNINGS' "
                    "ORDER BY source_path LIMIT 20"
                ),
            },
            {"query_id": "hygiene", "mode": "fts", "fts_query": "hygiene", "limit": 20},
            {"query_id": "ruff", "mode": "fts", "fts_query": "ruff", "limit": 20},
            {"query_id": "mypy", "mode": "fts", "fts_query": "mypy", "limit": 20},
            {"query_id": "jsonschema", "mode": "fts", "fts_query": "jsonschema", "limit": 20},
            {"query_id": "ROLE_ACK", "mode": "fts", "fts_query": "ROLE_ACK", "limit": 20},
            {"query_id": "LANGUAGE_ACK", "mode": "fts", "fts_query": "LANGUAGE_ACK", "limit": 20},
            {"query_id": "SANDBOX", "mode": "fts", "fts_query": "SANDBOX", "limit": 20},
            {
                "query_id": "quality gate",
                "mode": "fts",
                "fts_query": "\"quality gate\" OR quality OR gate",
                "limit": 20,
            },
            {
                "query_id": "evidence index",
                "mode": "fts",
                "fts_query": "\"evidence index\" OR evidence OR index",
                "limit": 20,
            },
            {
                "query_id": "NO_SCHEMA_AVAILABLE",
                "mode": "fts",
                "fts_query": "NO_SCHEMA_AVAILABLE",
                "limit": 20,
            },
        ],
    }


def build_playbook_payload() -> str:
    return """# EVIDENCE INDEX PLAYBOOK V0.1

## Purpose
Provide a repeatable way to rebuild and query NewGen evidence index artifacts.

## Build
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py `
  --repo-root E:\\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1
```

## Query Smoke
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_evidence_query_runner_v0_1.py `
  --repo-root E:\\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1
```

## Checker
```powershell
python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py `
  --repo-root E:\\IMPERIUM `
  --output-root IMPERIUM_NEW_GENERATION/MECHANICUS/EVIDENCE_INDEX/V0_1 `
  --report-root IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-EVIDENCE-INDEX-FOUNDATION-PC-V0_1 `
  --py-compile-status PASS `
  --ruff-status PASS `
  --mypy-status WARN `
  --json-parse-status PASS `
  --query-smoke-status PASS
```

## Guardrails
- Index only `IMPERIUM_NEW_GENERATION` scoped files from this task contract.
- Never include private/local external context paths.
- Keep reports compact (`raw_dump_status=COMPACT_ONLY`).
- Use report receipts for PASS claims.
"""


def build_readme_ru_payload() -> str:
    return """# Evidence Index Foundation V0.1 (RU)

## Что это
Первый базовый индекс доказательств NewGen для Mechanicus:
- SQLite база с FTS поиском;
- индекс по reports/receipts/cards/scope packs/role packs/contracts/templates;
- seeds по warning/error и связям task/commit.

## Что не входит
- UI/visual прототипы;
- LLM/cloud активация;
- индексация private/local external context;
- broad cleanup.

## Ключевые файлы
- `evidence_index.sqlite3`
- `evidence_index_schema_v0_1.sql`
- `evidence_index_manifest.json`
- `warning_error_patterns_v0_1.json`
- `example_queries_v0_1.json`
- `EVIDENCE_INDEX_PLAYBOOK_V0_1.md`

## Быстрый цикл
1. Запустить builder.
2. Запустить query runner.
3. Запустить checker и сверить отчеты в report-root.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build bounded NewGen SQLite/FTS evidence index for Mechanicus."
    )
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
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    newgen_root = (repo_root / "IMPERIUM_NEW_GENERATION").resolve()
    indexed_at_utc = utc_now()

    db_path = output_root / "evidence_index.sqlite3"
    schema_path = output_root / "evidence_index_schema_v0_1.sql"
    manifest_path = output_root / "evidence_index_manifest.json"
    warning_path = output_root / "warning_error_patterns_v0_1.json"
    playbook_path = output_root / "EVIDENCE_INDEX_PLAYBOOK_V0_1.md"
    query_examples_path = output_root / "example_queries_v0_1.json"
    readme_ru_path = output_root / "README_RU.md"

    build_report_path = report_root / "evidence_index_build_report.json"
    warning_seed_report_path = report_root / "warning_error_pattern_seed_report.json"
    linkage_report_path = report_root / "task_commit_linkage_seed_report.json"

    if not newgen_root.exists():
        payload = {
            "task_id": args.task_id,
            "generated_at_utc": indexed_at_utc,
            "checker": "mechanicus_evidence_index_builder_v0_1.py",
            "errors": ["missing_newgen_root"],
            "verdict": "FAIL",
            "raw_dump_status": "COMPACT_ONLY",
        }
        write_json(build_report_path, payload)
        print(json.dumps({"task_id": args.task_id, "verdict": "FAIL"}, ensure_ascii=False))
        return 1

    source_files = collect_source_files(newgen_root)
    records = [build_record(repo_root=repo_root, path=path, indexed_at_utc=indexed_at_utc) for path in source_files]

    db_stats = create_database(db_path=db_path, records=records)

    source_type_counts: dict[str, int] = {}
    organ_counts: dict[str, int] = {}
    for record in records:
        source_type = str(record["source_type"])
        organ = str(record["organ"])
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        organ_counts[organ] = organ_counts.get(organ, 0) + 1

    unique_task_ids = sorted(
        {task_id for record in records for task_id in record["task_ids"] if task_id}
    )
    unique_commits = sorted(
        {
            commit_hash
            for record in records
            for commit_hash in record["commit_hashes"]
            if commit_hash
        }
    )
    warning_totals: dict[str, int] = {}
    for record in records:
        for pattern_id, count in record["warning_hits"].items():
            warning_totals[pattern_id] = warning_totals.get(pattern_id, 0) + int(count)

    private_path_hits = [
        record["source_path"]
        for record in records
        if (
            record["source_path"].startswith("C:/")
            or record["source_path"].startswith("E:/IMPERIUM_CONTEXT")
            or "IMPERIUM_CONTEXT" in record["source_path"]
            or "/Users/" in record["source_path"]
        )
    ]

    warning_seed_payload = build_warning_seed_payload(args.task_id)
    write_json(warning_path, warning_seed_payload)
    write_json(warning_seed_report_path, warning_seed_payload)

    query_examples_payload = build_example_queries_payload(args.task_id)
    write_json(query_examples_path, query_examples_payload)
    write_text(schema_path, SQL_SCHEMA_V0_1)
    write_text(playbook_path, build_playbook_payload())
    write_text(readme_ru_path, build_readme_ru_payload())

    linkage_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_evidence_index_builder_v0_1.py",
        "summary": {
            "task_links": db_stats["task_links"],
            "commit_links": db_stats["commit_links"],
            "unique_task_ids": len(unique_task_ids),
            "unique_commits": len(unique_commits),
        },
        "task_ids_sample": unique_task_ids[:40],
        "commit_hashes_sample": unique_commits[:40],
        "verdict": "PASS",
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(linkage_report_path, linkage_payload)

    manifest_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "builder": "mechanicus_evidence_index_builder_v0_1.py",
        "db_path": db_path.relative_to(repo_root).as_posix(),
        "schema_path": schema_path.relative_to(repo_root).as_posix(),
        "source_globs": list(SOURCE_GLOBS),
        "records_indexed": len(records),
        "source_files_indexed": len(source_files),
        "source_type_counts": source_type_counts,
        "organ_counts": organ_counts,
        "task_links": db_stats["task_links"],
        "commit_links": db_stats["commit_links"],
        "capability_links": db_stats["capability_links"],
        "receipt_links": db_stats["receipt_links"],
        "warning_totals": warning_totals,
        "excluded_private_paths_confirmed": len(private_path_hits) == 0,
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(manifest_path, manifest_payload)

    verdict = "PASS"
    warnings: list[str] = []
    errors: list[str] = []
    if len(records) < 50:
        warnings.append("record_count_below_50")
    if private_path_hits:
        verdict = "FAIL"
        errors.append("private_path_indexing_detected")

    build_report_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_evidence_index_builder_v0_1.py",
        "output_root": output_root.relative_to(repo_root).as_posix(),
        "report_root": report_root.relative_to(repo_root).as_posix(),
        "summary": {
            "database_created": db_path.exists(),
            "records_indexed": len(records),
            "fts_rows": db_stats["fts_count"],
            "source_files_scanned": len(source_files),
            "source_type_count": len(source_type_counts),
            "task_link_rows": db_stats["task_links"],
            "commit_link_rows": db_stats["commit_links"],
            "warning_pattern_rows": db_stats["warning_rows"],
            "private_paths_indexed": len(private_path_hits),
        },
        "source_type_counts": source_type_counts,
        "organ_counts": organ_counts,
        "warning_totals": warning_totals,
        "source_type_examples": SOURCE_TYPE_EXAMPLES,
        "artifact_paths": {
            "db": db_path.relative_to(repo_root).as_posix(),
            "schema_sql": schema_path.relative_to(repo_root).as_posix(),
            "manifest": manifest_path.relative_to(repo_root).as_posix(),
            "warning_seed": warning_path.relative_to(repo_root).as_posix(),
            "playbook": playbook_path.relative_to(repo_root).as_posix(),
            "query_examples": query_examples_path.relative_to(repo_root).as_posix(),
            "readme_ru": readme_ru_path.relative_to(repo_root).as_posix(),
        },
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }
    write_json(build_report_path, build_report_payload)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": verdict,
                "records_indexed": len(records),
                "fts_rows": db_stats["fts_count"],
                "task_links": db_stats["task_links"],
                "commit_links": db_stats["commit_links"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
