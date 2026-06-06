#!/usr/bin/env python3
"""Heuristic checker for Officio role/language/response contract violations."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ACK_TOKENS_REQUIRED = [
    "ROLE_ACK",
    "LANGUAGE_ACK",
    "SCOPE_ACK",
    "STOP_CONDITIONS_ACK",
]

FORBIDDEN_ACTION_PATTERNS = [
    re.compile(r"\bsilent install\b", re.IGNORECASE),
    re.compile(r"\bi installed packages silently\b", re.IGNORECASE),
    re.compile(r"\bactivated (llm|cloud)\b", re.IGNORECASE),
    re.compile(r"\bllm/cloud activation\b", re.IGNORECASE),
    re.compile(r"\bvisual prototype\b", re.IGNORECASE),
    re.compile(r"\bя .*установ(ил|ила).*(тихо|молча)\b", re.IGNORECASE),
    re.compile(r"\bактивировал(а)?\s+(llm|cloud)\b", re.IGNORECASE),
]

TECHNICAL_HINT_PATTERNS = [
    re.compile(r"^\s*```"),
    re.compile(r"^\s*`[^`]+`"),
    re.compile(r"^\s*(python|git|npm|pip|ruff|mypy|pytest)\b", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9_]+\.json\b"),
    re.compile(r"[A-Za-z0-9_]+\.py\b"),
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/[A-Za-z0-9._/-]+"),
    re.compile(r"^\s*(ROLE_ACK|LANGUAGE_ACK|SCOPE_ACK|STOP_CONDITIONS_ACK|FORBIDDEN_ACTIONS_ACK)\b", re.IGNORECASE),
]

PART_MARKERS = [
    re.compile(r"^\s*1\.\s+", re.MULTILINE),
    re.compile(r"^\s*2\.\s+", re.MULTILINE),
    re.compile(r"^\s*3\.\s+", re.MULTILINE),
    re.compile(r"^\s*4\.\s+", re.MULTILINE),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[А-Яа-яЁё]", text))


def has_latin(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text))


def is_technical_line(line: str, in_code_block: bool) -> bool:
    if in_code_block:
        return True
    stripped = line.strip()
    if not stripped:
        return False
    for pattern in TECHNICAL_HINT_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def is_ack_line(text: str) -> bool:
    return bool(
        re.match(
            r"^\s*(ROLE_ACK|LANGUAGE_ACK|SCOPE_ACK|STOP_CONDITIONS_ACK|FORBIDDEN_ACTIONS_ACK)\b",
            text,
            flags=re.IGNORECASE,
        )
    )


def split_lines_with_code_state(text: str) -> List[Tuple[str, bool]]:
    lines_with_state: List[Tuple[str, bool]] = []
    in_code_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            lines_with_state.append((line, True))
            in_code_block = not in_code_block
            continue
        lines_with_state.append((line, in_code_block))
    return lines_with_state


def find_missing_acks(text: str) -> List[str]:
    upper_text = text.upper()
    missing: List[str] = []
    for token in ACK_TOKENS_REQUIRED:
        if token not in upper_text:
            missing.append(token)
    return missing


def has_4_part_structure(text: str) -> bool:
    return all(pattern.search(text) for pattern in PART_MARKERS)


def has_russian_owner_summary(text: str) -> bool:
    lines = text.splitlines()
    summary_started = False
    summary_lines: List[str] = []

    for line in lines:
        if re.match(r"^\s*4\.\s+", line):
            summary_started = True
            summary_lines.append(line)
            continue
        if summary_started and re.match(r"^\s*[1-3]\.\s+", line):
            break
        if summary_started:
            summary_lines.append(line)

    return has_cyrillic("\n".join(summary_lines))


def detect_language_profile(text: str) -> Dict[str, int]:
    owner_ru = 0
    owner_en = 0
    technical_en = 0
    technical_signal_en = 0
    mixed_lines = 0

    for line, in_code_block in split_lines_with_code_state(text):
        stripped = line.strip()
        if not stripped:
            continue
        line_has_cyr = has_cyrillic(stripped)
        line_has_lat = has_latin(stripped)
        technical = is_technical_line(stripped, in_code_block)
        if technical and line_has_lat:
            technical_en += 1
            if not is_ack_line(stripped):
                technical_signal_en += 1
            continue
        if line_has_cyr and line_has_lat:
            mixed_lines += 1
            owner_ru += 1
            continue
        if line_has_cyr:
            owner_ru += 1
            continue
        if line_has_lat:
            owner_en += 1

    return {
        "owner_ru_lines": owner_ru,
        "owner_en_lines": owner_en,
        "technical_en_lines": technical_en,
        "technical_signal_en_lines": technical_signal_en,
        "mixed_lines": mixed_lines,
    }


def detect_forbidden_admission(text: str) -> List[str]:
    found: List[str] = []
    for pattern in FORBIDDEN_ACTION_PATTERNS:
        if pattern.search(text):
            found.append(pattern.pattern)
    return found


def evaluate_text(path: Path, text: str) -> Dict[str, object]:
    violations: List[str] = []
    warnings: List[str] = []

    missing_acks = find_missing_acks(text)
    if missing_acks:
        violations.append(f"MISSING_ACK:{','.join(missing_acks)}")

    if not has_4_part_structure(text):
        violations.append("FINAL_RESPONSE_NOT_4_PART")

    if not has_russian_owner_summary(text):
        violations.append("MISSING_RUSSIAN_OWNER_SUMMARY")

    language_metrics = detect_language_profile(text)
    owner_en = language_metrics["owner_en_lines"]
    owner_ru = language_metrics["owner_ru_lines"]
    technical_signal_en = language_metrics["technical_signal_en_lines"]

    if owner_en >= 3 and owner_en > owner_ru:
        violations.append("LONG_ENGLISH_OWNER_COMMENTARY")
    elif owner_en > 0 and owner_en <= owner_ru:
        warnings.append("MINOR_OWNER_ENGLISH_DRIFT")

    if technical_signal_en >= 2 and owner_ru > 0 and owner_en == 0:
        warnings.append("TECHNICAL_ENGLISH_ALLOWED")

    forbidden = detect_forbidden_admission(text)
    if forbidden:
        violations.append("FORBIDDEN_ACTION_ADMISSION")

    if violations:
        status = "FAIL"
        recommendation = "Исправить FAIL-нарушения: ACK, RU-summary, 4-part формат, запретные признания."
    elif warnings:
        status = "WARN"
        recommendation = "Сократить дрейф и оставить Owner-facing комментарии на русском."
    else:
        status = "PASS"
        recommendation = "Контракт соблюден."

    limitations = [
        "Heuristic checker: language ratio and technical block detection are approximate.",
        "Does not perform deep semantic understanding of intent.",
    ]

    return {
        "file": str(path),
        "status": status,
        "violations": violations + warnings,
        "detected_violations": {
            "fail": violations,
            "warn": warnings,
        },
        "recommended_correction": recommendation,
        "limitations": limitations,
        "metrics": language_metrics,
        "forbidden_matches": forbidden,
    }


def evaluate_paths(paths: Sequence[Path]) -> Dict[str, object]:
    items: List[Dict[str, object]] = []
    pass_count = 0
    warn_count = 0
    fail_count = 0

    for path in paths:
        text = path.read_text(encoding="utf-8")
        item = evaluate_text(path, text)
        items.append(item)
        status = str(item["status"])
        if status == "PASS":
            pass_count += 1
        elif status == "WARN":
            warn_count += 1
        else:
            fail_count += 1

    overall = "PASS"
    if fail_count > 0:
        overall = "FAIL"
    elif warn_count > 0:
        overall = "WARN"

    return {
        "status": overall,
        "generated_at_utc": utc_now(),
        "required_acks": ACK_TOKENS_REQUIRED,
        "items": items,
        "summary": {
            "pass": pass_count,
            "warn": warn_count,
            "fail": fail_count,
            "total": len(items),
        },
    }


def collect_input_paths(input_arg: str) -> List[Path]:
    target = Path(input_arg)
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.rglob("*.md") if path.is_file())
    raise RuntimeError(f"Input path does not exist: {input_arg}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Officio response contract compliance for markdown files.")
    parser.add_argument("--input", required=True, help="Input file or directory.")
    parser.add_argument("--output", help="Optional report output JSON path.")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = collect_input_paths(args.input)
    report = evaluate_paths(paths)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.compact:
            data = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
        else:
            data = json.dumps(report, ensure_ascii=False, indent=2)
        output_path.write_text(data + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
