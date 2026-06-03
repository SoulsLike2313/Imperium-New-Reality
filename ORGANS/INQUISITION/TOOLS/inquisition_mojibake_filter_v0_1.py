#!/usr/bin/env python3
"""Global language/encoding guard for canonical IMPERIUM artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TEXT_EXTENSIONS = {
    ".md",
    ".json",
    ".txt",
    ".py",
    ".ps1",
    ".yaml",
    ".yml",
    ".csv",
    ".toml",
    ".sh",
    ".js",
    ".html",
    ".css",
    ".ts",
}

BOM_CHECK_EXTENSIONS = {".json", ".md", ".txt", ".py", ".ps1", ".yaml", ".yml", ".csv"}

BINARY_SKIP_EXTENSIONS = {
    ".pdf",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".bmp",
    ".mp4",
    ".mov",
    ".avi",
    ".wav",
    ".mp3",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".pyc",
}

LOCALIZATION_MARKERS = {"locales", "i18n", "translations", "localization"}

CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
REPLACEMENT_RE = re.compile(r"\ufffd")

MOJIBAKE_SIGNATURES = [
    ("MOJIBAKE_UTF8_LATIN1_C3", re.compile(r"\u00c3[\u0080-\u00bf]")),
    ("MOJIBAKE_UTF8_LATIN1_C2", re.compile(r"\u00c2[\u0080-\u00bf]")),
    ("MOJIBAKE_CP1252_QUOTES", re.compile(r"\u00e2\u0080[\u0098-\u009f]")),
    ("MOJIBAKE_D0_D1_SEQUENCE", re.compile(r"[\u00d0\u00d1][\u0080-\u00bf]")),
]

CAP_BY_HIT_TYPE = {
    "UTF8_BOM": "CAP_UTF8_BOM_NOT_DETECTED",
    "CYRILLIC_IN_CANONICAL_ARTIFACT": "CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC",
    "TASKPACK_ROOT_CYRILLIC": "CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT",
    "REPLACEMENT_CHARACTER": "CAP_REPLACEMENT_CHARACTER_NOT_DETECTED",
    "MOJIBAKE_SIGNATURE": "CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED",
    "MIXED_ENCODING_PATTERN": "CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED",
    "UTF8_DECODE_ERROR": "CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED",
}

STRICT_BLOCK_CLASSIFICATIONS = {"BLOCK"}
WARN_CLASSIFICATIONS = {"LEGACY_TO_REMEDIATE", "ALLOWED_RUNTIME_OWNER_OUTPUT", "ALLOWED_LOCALIZATION"}

DEFAULT_SCAN_ROOTS = [
    "AGENTS.md",
    "IMPERIUM_NEW_GENERATION/ORGANS",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE",
    "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/REPORTS",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_repo_root(repo_root: str | Path) -> Path:
    return Path(repo_root).expanduser().resolve()


def normalize_path(repo_root: Path, path_value: str | Path) -> Path:
    candidate = Path(path_value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (repo_root / candidate).resolve()


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def has_utf8_bom(raw: bytes) -> bool:
    return raw.startswith(b"\xef\xbb\xbf")


def looks_binary(raw: bytes) -> bool:
    if not raw:
        return False
    if b"\x00" in raw:
        return True
    sample = raw[:4096]
    non_text = 0
    for byte in sample:
        if byte in (9, 10, 13):
            continue
        if 32 <= byte <= 126:
            continue
        if 160 <= byte <= 255:
            continue
        non_text += 1
    return (non_text / max(1, len(sample))) > 0.30


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def is_localization_path(relative_path: str) -> bool:
    parts = [part.lower() for part in relative_path.split("/") if part]
    return any(marker in parts for marker in LOCALIZATION_MARKERS)


def is_runtime_owner_ru_file(relative_path: str) -> bool:
    lowered = relative_path.lower()
    return lowered.endswith("/final_owner_summary_ru.md") or lowered.endswith("_ru.md")


def path_owner_organ(relative_path: str) -> str:
    parts = relative_path.split("/")
    if len(parts) >= 4 and parts[0] == "IMPERIUM_NEW_GENERATION" and parts[1] == "ORGANS":
        return parts[2]
    if relative_path.startswith("IMPERIUM_NEW_GENERATION/MATRIX_SPINE/"):
        return "DOCTRINARIUM"
    if relative_path == "AGENTS.md":
        return "OFFICIO_AGENTIS"
    return "ADMINISTRATUM"


def _matches_prefix(relative_path: str, prefix: str) -> bool:
    normalized_path = relative_path.strip("/")
    normalized_prefix = prefix.strip("/")
    return normalized_path == normalized_prefix or normalized_path.startswith(normalized_prefix + "/")


def classify_path(relative_path: str, current_task_id: str, strict_prefixes: list[str]) -> str:
    if is_localization_path(relative_path):
        return "ALLOWED_LOCALIZATION"
    if is_runtime_owner_ru_file(relative_path):
        return "ALLOWED_RUNTIME_OWNER_OUTPUT"
    if strict_prefixes:
        if not any(_matches_prefix(relative_path, prefix) for prefix in strict_prefixes):
            return "LEGACY_TO_REMEDIATE"
    task_inbox_marker = "/TASK_INBOX/REGISTERED/"
    reports_marker = "/REPORTS/"
    with_root = "/" + relative_path
    if task_inbox_marker in with_root and current_task_id and f"/{current_task_id}/" not in with_root:
        return "LEGACY_TO_REMEDIATE"
    if reports_marker in with_root and current_task_id and f"/{current_task_id}/" not in with_root:
        return "LEGACY_TO_REMEDIATE"
    return "BLOCK"


def classify_severity(classification: str) -> str:
    if classification in WARN_CLASSIFICATIONS:
        return "WARN"
    return "BLOCK"


def build_scan_roots(repo_root: Path, scan_roots: list[str]) -> list[Path]:
    if scan_roots:
        roots = [normalize_path(repo_root, value) for value in scan_roots]
    else:
        roots = [normalize_path(repo_root, value) for value in DEFAULT_SCAN_ROOTS]
    context_spine = repo_root / "IMPERIUM_NEW_GENERATION/CONTEXT_SPINE"
    if context_spine.exists():
        roots.append(context_spine.resolve())
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = to_posix(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def iter_files_from_roots(repo_root: Path, roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            key = to_posix(root.resolve())
            if key not in seen:
                files.append(root.resolve())
                seen.add(key)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            key = to_posix(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            files.append(path.resolve())
    return sorted(files, key=lambda item: to_posix(item))


def stable_snippet_hash(text: str, hit_type: str) -> str:
    digest = hashlib.sha256((hit_type + "\n" + text).encode("utf-8", errors="replace")).hexdigest()
    return digest[:24]


def detect_line_hits(
    *,
    line: str,
    line_number: int,
    relative_path: str,
    owner_organ: str,
    current_task_id: str,
    strict_prefixes: list[str],
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    classification = classify_path(relative_path, current_task_id, strict_prefixes)
    severity = classify_severity(classification)

    if CYRILLIC_RE.search(line):
        hit_type = (
            "TASKPACK_ROOT_CYRILLIC"
            if "/TASK_INBOX/REGISTERED/" in ("/" + relative_path) and "/EXTRACTED/" in ("/" + relative_path)
            else "CYRILLIC_IN_CANONICAL_ARTIFACT"
        )
        hits.append(
            {
                "path": relative_path,
                "line": line_number,
                "hit_type": hit_type,
                "signature_id": "CYRILLIC_RE",
                "snippet_hash": stable_snippet_hash(line, hit_type),
                "owner_organ": owner_organ,
                "severity": severity,
                "classification": classification,
            }
        )

    if REPLACEMENT_RE.search(line):
        hit_type = "REPLACEMENT_CHARACTER"
        hits.append(
            {
                "path": relative_path,
                "line": line_number,
                "hit_type": hit_type,
                "signature_id": "REPLACEMENT_UFFFD",
                "snippet_hash": stable_snippet_hash(line, hit_type),
                "owner_organ": owner_organ,
                "severity": severity,
                "classification": classification,
            }
        )

    for signature_id, pattern in MOJIBAKE_SIGNATURES:
        if pattern.search(line):
            hit_type = "MOJIBAKE_SIGNATURE"
            hits.append(
                {
                    "path": relative_path,
                    "line": line_number,
                    "hit_type": hit_type,
                    "signature_id": signature_id,
                    "snippet_hash": stable_snippet_hash(line, signature_id),
                    "owner_organ": owner_organ,
                    "severity": severity,
                    "classification": classification,
                }
            )

    return hits


def detect_file_hits(
    *,
    repo_root: Path,
    file_path: Path,
    current_task_id: str,
    strict_prefixes: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    relative_path = to_posix(file_path.relative_to(repo_root))
    suffix = file_path.suffix.lower()

    if "/_language_encoding_fixture_sandbox_" in ("/" + relative_path):
        return [], {"path": relative_path, "reason": "FIXTURE_SANDBOX_EXCLUDED"}

    if is_localization_path(relative_path):
        return [], {"path": relative_path, "reason": "LOCALIZATION_PATH_EXCLUDED"}

    if suffix in BINARY_SKIP_EXTENSIONS:
        return [], {"path": relative_path, "reason": f"BINARY_EXTENSION_EXCLUDED:{suffix}"}

    raw = file_path.read_bytes()
    if looks_binary(raw):
        return [], {"path": relative_path, "reason": "BINARY_CONTENT_EXCLUDED"}

    if suffix not in TEXT_EXTENSIONS:
        return [], None

    owner_organ = path_owner_organ(relative_path)
    classification = classify_path(relative_path, current_task_id, strict_prefixes)
    severity = classify_severity(classification)
    hits: list[dict[str, Any]] = []

    if suffix in BOM_CHECK_EXTENSIONS and has_utf8_bom(raw):
        hit_type = "UTF8_BOM"
        hits.append(
            {
                "path": relative_path,
                "line": 1,
                "hit_type": hit_type,
                "signature_id": "UTF8_BOM",
                "snippet_hash": stable_snippet_hash(relative_path, hit_type),
                "owner_organ": owner_organ,
                "severity": severity,
                "classification": classification,
            }
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        hit_type = "UTF8_DECODE_ERROR"
        hits.append(
            {
                "path": relative_path,
                "line": None,
                "hit_type": hit_type,
                "signature_id": "UTF8_DECODE_ERROR",
                "snippet_hash": stable_snippet_hash(relative_path, hit_type),
                "owner_organ": owner_organ,
                "severity": severity,
                "classification": classification,
            }
        )
        return hits, None

    for index, line in enumerate(text.splitlines(), start=1):
        hits.extend(
            detect_line_hits(
                line=line,
                line_number=index,
                relative_path=relative_path,
                owner_organ=owner_organ,
                current_task_id=current_task_id,
                strict_prefixes=strict_prefixes,
            )
        )

    if len(hits) >= 2 and any(hit["hit_type"] == "MOJIBAKE_SIGNATURE" for hit in hits):
        hit_type = "MIXED_ENCODING_PATTERN"
        hits.append(
            {
                "path": relative_path,
                "line": None,
                "hit_type": hit_type,
                "signature_id": "MIXED_PATTERN_HEURISTIC",
                "snippet_hash": stable_snippet_hash(relative_path, hit_type),
                "owner_organ": owner_organ,
                "severity": severity,
                "classification": classification,
            }
        )
    return hits, None


def summarize_hits(hits: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_classification: dict[str, int] = {}
    for hit in hits:
        by_type[hit["hit_type"]] = by_type.get(hit["hit_type"], 0) + 1
        by_severity[hit["severity"]] = by_severity.get(hit["severity"], 0) + 1
        by_classification[hit["classification"]] = by_classification.get(hit["classification"], 0) + 1
    return {
        "total_hits": len(hits),
        "by_hit_type": dict(sorted(by_type.items())),
        "by_severity": dict(sorted(by_severity.items())),
        "by_classification": dict(sorted(by_classification.items())),
    }


def caps_from_hits(hits: list[dict[str, Any]]) -> list[str]:
    caps: set[str] = set()
    for hit in hits:
        cap = CAP_BY_HIT_TYPE.get(hit["hit_type"])
        if cap:
            caps.add(cap)
    return sorted(caps)


def decide_verdict(hits: list[dict[str, Any]]) -> str:
    has_block = any(hit["severity"] == "BLOCK" for hit in hits)
    has_warn = any(hit["severity"] == "WARN" for hit in hits)
    if has_block:
        return "BLOCK"
    if has_warn:
        return "WARN"
    return "PASS"


def build_markdown_report(report: dict[str, Any]) -> list[str]:
    summary = report["summary"]
    lines = [
        "# Inquisition Mojibake Filter Report",
        "",
        f"Task ID: `{report.get('task_id', '')}`",
        f"Timestamp (UTC): `{report['timestamp_utc']}`",
        f"Verdict: `{report['verdict']}`",
        "",
        "## Scope",
        "",
        f"- Repo root: `{report['repo_root']}`",
        f"- Scan roots: `{', '.join(report['scan_roots'])}`",
        f"- Current task context: `{report.get('current_task_id', '')}`",
        "",
        "## Summary",
        "",
        f"- Total files scanned: `{report['files_scanned']}`",
        f"- Excluded paths: `{len(report['excluded_paths'])}`",
        f"- Total hits: `{summary['total_hits']}`",
        f"- Caps triggered: `{', '.join(report['caps_triggered']) if report['caps_triggered'] else 'none'}`",
        "",
        "### Hits by Type",
    ]
    for hit_type, count in summary["by_hit_type"].items():
        lines.append(f"- `{hit_type}`: `{count}`")
    if not summary["by_hit_type"]:
        lines.append("- none")

    lines.extend(["", "### Hits by Severity"])
    for severity, count in summary["by_severity"].items():
        lines.append(f"- `{severity}`: `{count}`")
    if not summary["by_severity"]:
        lines.append("- none")

    lines.extend(["", "### Hits by Classification"])
    for cls, count in summary["by_classification"].items():
        lines.append(f"- `{cls}`: `{count}`")
    if not summary["by_classification"]:
        lines.append("- none")

    lines.extend(["", "## Sample Hits (first 20)"])
    for hit in report["hits"][:20]:
        lines.append(
            "- "
            + f"`{hit['severity']}` `{hit['hit_type']}` "
            + f"`{hit['path']}` line `{hit['line']}` "
            + f"classification `{hit['classification']}`"
        )
    if not report["hits"]:
        lines.append("- none")
    return lines


def run_filter(
    *,
    repo_root: str | Path = ".",
    task_id: str = "",
    current_task_id: str = "",
    scan_roots: list[str] | None = None,
    strict_prefixes: list[str] | None = None,
    max_hits: int = 5000,
) -> dict[str, Any]:
    repo = normalize_repo_root(repo_root)
    root_paths = build_scan_roots(repo, scan_roots or [])
    files = iter_files_from_roots(repo, root_paths)

    all_hits: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    warnings: list[str] = []

    strict_prefix_list = [prefix.strip().replace("\\", "/") for prefix in (strict_prefixes or []) if prefix.strip()]

    for file_path in files:
        try:
            hits, excluded_item = detect_file_hits(
                repo_root=repo,
                file_path=file_path,
                current_task_id=current_task_id,
                strict_prefixes=strict_prefix_list,
            )
        except Exception as exc:  # defensive capture; do not hide filter failure
            warnings.append(f"Scanner error on {to_posix(file_path)}: {exc}")
            continue
        if excluded_item:
            excluded.append(excluded_item)
        if hits:
            all_hits.extend(hits)
            if len(all_hits) >= max_hits:
                warnings.append(f"Hit collection truncated at max_hits={max_hits}.")
                all_hits = all_hits[:max_hits]
                break

    summary = summarize_hits(all_hits)
    verdict = decide_verdict(all_hits)
    caps = caps_from_hits(all_hits)
    report = {
        "schema_version": "0.1",
        "scan_id": f"INQUISITION_MOJIBAKE_FILTER_{utc_now()}",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": to_posix(repo),
        "scan_roots": [to_posix(path) for path in root_paths if path.exists()],
        "current_task_id": current_task_id,
        "strict_prefixes": strict_prefix_list,
        "files_scanned": len(files),
        "excluded_paths": excluded,
        "hits": all_hits,
        "summary": summary,
        "caps_triggered": caps,
        "warnings": warnings,
        "verdict": verdict,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inquisition global mojibake/encoding filter.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--task-id", default="", help="Task ID for report metadata.")
    parser.add_argument("--current-task-id", default="", help="Current task ID for legacy classification.")
    parser.add_argument(
        "--scan-root",
        action="append",
        default=[],
        help="Optional scan root (repeatable). Relative paths are resolved from repo root.",
    )
    parser.add_argument("--report-json", default="", help="Optional output JSON report path.")
    parser.add_argument("--report-md", default="", help="Optional output markdown report path.")
    parser.add_argument(
        "--strict-prefix",
        action="append",
        default=[],
        help="Paths that must be treated as strict canonical scope; outside becomes legacy warning.",
    )
    parser.add_argument("--max-hits", type=int, default=5000, help="Maximum number of hits to collect.")
    args = parser.parse_args()

    report = run_filter(
        repo_root=args.repo_root,
        task_id=args.task_id,
        current_task_id=args.current_task_id,
        scan_roots=list(args.scan_root or []),
        strict_prefixes=list(args.strict_prefix or []),
        max_hits=max(100, args.max_hits),
    )

    if args.report_json:
        report_json_path = normalize_path(normalize_repo_root(args.repo_root), args.report_json)
        write_json(report_json_path, report)
    if args.report_md:
        report_md_path = normalize_path(normalize_repo_root(args.repo_root), args.report_md)
        write_markdown(report_md_path, build_markdown_report(report))

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("verdict") == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
