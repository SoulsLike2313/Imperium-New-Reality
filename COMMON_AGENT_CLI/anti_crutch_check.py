#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BLOCKED_PREFIX = "BLOCKED_"
WARN_PREFIX = "WARN_"
DEBT_PREFIX = "DEBT_"


@dataclass
class Rules:
    domain_to_verdict: dict[str, str]
    domain_keywords: dict[str, list[str]]
    canonical_markers: list[str]
    workaround_markers: list[str]
    temporary_debt_markers: list[str]
    bypass_markers: list[str]


@dataclass
class AnalysisResult:
    source: str
    verdicts: list[str]
    primary_verdict: str
    domains: list[str]
    canonical_hits: list[str]
    workaround_hits: list[str]
    temporary_debt_hits: list[str]
    bypass_hits: list[str]
    notes: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rules_path() -> Path:
    return Path(__file__).resolve().parents[1] / "TASK_CONTROL" / "ANTI_CRUTCH_PROTOCOL" / "anti_crutch_rules.json"


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return payload


def load_rules() -> Rules:
    payload = read_json(rules_path())
    return Rules(
        domain_to_verdict={str(k): str(v) for k, v in payload.get("domain_to_verdict", {}).items()},
        domain_keywords={
            str(k): [str(item).lower() for item in v] for k, v in payload.get("domain_keywords", {}).items() if isinstance(v, list)
        },
        canonical_markers=[str(item).lower() for item in payload.get("canonical_markers", []) if isinstance(item, str)],
        workaround_markers=[str(item).lower() for item in payload.get("workaround_markers", []) if isinstance(item, str)],
        temporary_debt_markers=[str(item).lower() for item in payload.get("temporary_debt_markers", []) if isinstance(item, str)],
        bypass_markers=[str(item).lower() for item in payload.get("bypass_markers", []) if isinstance(item, str)],
    )


def marker_hits(text_lower: str, markers: list[str]) -> list[str]:
    hits: list[str] = []
    for marker in markers:
        matched = False
        negation_pattern = re.compile(rf"\b(no|not)\b[^\n]{{0,40}}{re.escape(marker)}")
        for line in text_lower.splitlines():
            if marker not in line:
                continue
            if negation_pattern.search(line):
                continue
            matched = True
            break
        if matched:
            hits.append(marker)
    return hits


def detect_domains(text_lower: str, rules: Rules) -> list[str]:
    domains: list[str] = []
    for domain, keywords in rules.domain_keywords.items():
        domain_hit = False
        for keyword in keywords:
            if " " in keyword:
                if keyword in text_lower:
                    domain_hit = True
                    break
            else:
                if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                    domain_hit = True
                    break
        if domain_hit:
            domains.append(domain)
    return sorted(set(domains))


def detect_rule_signal(text_lower: str) -> bool:
    rule_terms = [
        "rule",
        "law",
        "must",
        "protocol",
        "compliance",
        "policy",
        "contract",
    ]
    return any(term in text_lower for term in rule_terms)


def primary_verdict(verdicts: list[str]) -> str:
    if not verdicts:
        return "NO_CRUTCH_FOUND"
    blocked = sorted([item for item in verdicts if item.startswith(BLOCKED_PREFIX)])
    if blocked:
        return blocked[0]
    warns = sorted([item for item in verdicts if item.startswith(WARN_PREFIX)])
    if warns:
        return warns[0]
    debts = sorted([item for item in verdicts if item.startswith(DEBT_PREFIX)])
    if debts:
        return debts[0]
    return sorted(verdicts)[0]


def analyze_text(source: str, text: str, rules: Rules) -> AnalysisResult:
    text_lower = text.lower()
    domains = detect_domains(text_lower, rules)
    canonical_hits = marker_hits(text_lower, rules.canonical_markers)
    workaround_hits = marker_hits(text_lower, rules.workaround_markers)
    temporary_debt_hits = marker_hits(text_lower, rules.temporary_debt_markers)
    bypass_hits = marker_hits(text_lower, rules.bypass_markers)

    verdicts: list[str] = []
    notes: list[str] = []

    if workaround_hits:
        verdicts.append("WARN_TASKPACK_ONLY_WORKAROUND")
        notes.append("taskpack/prompt-only workaround markers detected")
    if temporary_debt_hits:
        verdicts.append("WARN_TEMPORARY_WORKAROUND_ACCEPTED_WITH_DEBT")
        notes.append("temporary workaround debt markers detected")
    if bypass_hits:
        verdicts.append("BLOCKED_CANONICAL_AUTHORITY_BYPASSED")
        notes.append("bypass markers detected")

    rule_signal = detect_rule_signal(text_lower)

    if (workaround_hits or temporary_debt_hits or bypass_hits) and not domains and rule_signal:
        verdicts.append("BLOCKED_ORGAN_AUTHORITY_MISSING")
        notes.append("rule signal present but canonical owner domain could not be assigned")

    if (workaround_hits or temporary_debt_hits or bypass_hits) and domains:
        for domain in domains:
            debt_code = rules.domain_to_verdict.get(domain)
            if debt_code:
                verdicts.append(debt_code)

    if not verdicts:
        verdicts.append("NO_CRUTCH_FOUND")
        if canonical_hits:
            notes.append("canonical markers detected")
        else:
            notes.append("no anti-crutch violation markers detected")

    verdicts = sorted(set(verdicts))
    return AnalysisResult(
        source=source,
        verdicts=verdicts,
        primary_verdict=primary_verdict(verdicts),
        domains=domains,
        canonical_hits=sorted(set(canonical_hits)),
        workaround_hits=sorted(set(workaround_hits)),
        temporary_debt_hits=sorted(set(temporary_debt_hits)),
        bypass_hits=sorted(set(bypass_hits)),
        notes=notes,
    )


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_path_text(path: Path) -> str:
    if path.suffix.lower() == ".json":
        payload = read_json(path)
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return load_text_file(path)


def summarize_results(results: list[AnalysisResult]) -> tuple[list[str], str]:
    verdicts: list[str] = []
    for item in results:
        verdicts.extend(item.verdicts)
    unique = sorted(set(verdicts)) if verdicts else ["NO_CRUTCH_FOUND"]
    primary = primary_verdict(unique)
    return unique, primary


def collect_taskpack_entries(taskpack_path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    allowed_ext = {".md", ".txt", ".json"}

    if taskpack_path.is_dir():
        for path in sorted(taskpack_path.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in allowed_ext:
                continue
            try:
                text = load_path_text(path)
            except Exception as error:
                text = f"READ_ERROR:{error}"
            entries.append((str(path), text))
        return entries

    if taskpack_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(taskpack_path, "r") as archive:
            for name in sorted(archive.namelist()):
                suffix = Path(name).suffix.lower()
                if suffix not in allowed_ext:
                    continue
                raw = archive.read(name)
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw.decode("utf-8", errors="replace")
                if suffix == ".json":
                    try:
                        parsed = json.loads(text)
                        text = json.dumps(parsed, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                entries.append((f"{taskpack_path}!/{name}", text))
        return entries

    raise ValueError("taskpack path must be directory or .zip")


def result_to_dict(result: AnalysisResult) -> dict[str, Any]:
    return {
        "source": result.source,
        "primary_verdict": result.primary_verdict,
        "verdicts": result.verdicts,
        "domains": result.domains,
        "canonical_hits": result.canonical_hits,
        "workaround_hits": result.workaround_hits,
        "temporary_debt_hits": result.temporary_debt_hits,
        "bypass_hits": result.bypass_hits,
        "notes": result.notes,
    }


def maybe_write_json(path: str | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def exit_code_for(verdicts: list[str]) -> int:
    if any(v.startswith(BLOCKED_PREFIX) for v in verdicts):
        return 2
    if any(v.startswith(WARN_PREFIX) or v.startswith(DEBT_PREFIX) for v in verdicts):
        return 1
    return 0


def cmd_check_file(args: argparse.Namespace, rules: Rules) -> int:
    path = Path(args.path).resolve()
    text = load_path_text(path)
    result = analyze_text(str(path), text, rules)
    payload = {
        "schema_version": "ANTI_CRUTCH_CHECK_REPORT_V0_1",
        "checked_at_utc": utc_now(),
        "mode": "check-file",
        "result": result_to_dict(result),
    }
    maybe_write_json(args.json_out, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code_for(result.verdicts)


def cmd_check_text(args: argparse.Namespace, rules: Rules) -> int:
    path = Path(args.path).resolve()
    text = load_text_file(path)
    result = analyze_text(str(path), text, rules)
    payload = {
        "schema_version": "ANTI_CRUTCH_CHECK_REPORT_V0_1",
        "checked_at_utc": utc_now(),
        "mode": "check-text",
        "result": result_to_dict(result),
    }
    maybe_write_json(args.json_out, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code_for(result.verdicts)


def cmd_check_taskpack(args: argparse.Namespace, rules: Rules) -> int:
    path = Path(args.path).resolve()
    entries = collect_taskpack_entries(path)
    results: list[AnalysisResult] = [analyze_text(source, text, rules) for source, text in entries]
    combined_verdicts, combined_primary = summarize_results(results)

    payload = {
        "schema_version": "ANTI_CRUTCH_CHECK_REPORT_V0_1",
        "checked_at_utc": utc_now(),
        "mode": "check-taskpack",
        "taskpack_path": str(path),
        "file_count": len(results),
        "primary_verdict": combined_primary,
        "combined_verdicts": combined_verdicts,
        "results": [result_to_dict(item) for item in results],
    }
    maybe_write_json(args.json_out, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code_for(combined_verdicts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IMPERIUM Anti-Crutch checker V0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    p_file = sub.add_parser("check-file", help="Analyze a file and return anti-crutch verdicts.")
    p_file.add_argument("path", help="Path to source file (.md/.txt/.json).")
    p_file.add_argument("--json-out", dest="json_out", help="Optional path to write JSON report.")

    p_text = sub.add_parser("check-text", help="Analyze plain text file and return anti-crutch verdicts.")
    p_text.add_argument("path", help="Path to text file.")
    p_text.add_argument("--json-out", dest="json_out", help="Optional path to write JSON report.")

    p_taskpack = sub.add_parser("check-taskpack", help="Analyze taskpack folder/zip and aggregate anti-crutch verdicts.")
    p_taskpack.add_argument("path", help="Path to taskpack directory or .zip.")
    p_taskpack.add_argument("--json-out", dest="json_out", help="Optional path to write JSON report.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    rules = load_rules()

    if args.command == "check-file":
        return cmd_check_file(args, rules)
    if args.command == "check-text":
        return cmd_check_text(args, rules)
    if args.command == "check-taskpack":
        return cmd_check_taskpack(args, rules)

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
