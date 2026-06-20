#!/usr/bin/env python3
"""inq_patterns.py -- single source of truth for Inquisition signatures and thresholds.

Loads and validates:
  - SIGNATURES.json (8 secret patterns + 7 PI categories)
  - REDACTION_PATTERNS.json (6 redaction targets)
  - THRESHOLDS.json (all 18 thresholds)

Used by every other inq_*.py tool. Never inline a pattern -- always load via these helpers.

CLI:
  inq_patterns.py --validate          # validate all 3 config JSONs
  inq_patterns.py --dump signatures   # dump SIGNATURES.json
  inq_patterns.py --dump redaction    # dump REDACTION_PATTERNS.json
  inq_patterns.py --dump thresholds   # dump THRESHOLDS.json
  inq_patterns.py --list-thresholds   # human listing of threshold keys+values
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CONFIG_RELATIVE = Path("ORGANS/INQUISITION/CONFIG")


def _candidate_starts() -> List[Path]:
    here = Path(__file__).resolve()
    return [here.parent, Path.cwd()]


def _find_config_dir(start: Optional[Path] = None) -> Path:
    """Walk up from start (or this file / cwd) until ORGANS/INQUISITION/CONFIG/ is found.

    Honors pack-internal layout (files/ORGANS/...) as well as canonical layout (ORGANS/...).
    """
    starts: List[Path] = [start] if start is not None else []
    starts.extend(_candidate_starts())
    for s in starts:
        if s is None:
            continue
        cur = s if s.is_dir() else s.parent
        for cand in [cur, *cur.parents]:
            for prefix in ("", "files"):
                t = (cand / prefix / CONFIG_RELATIVE) if prefix else (cand / CONFIG_RELATIVE)
                if (t / "SIGNATURES.json").is_file():
                    return t.resolve()
    raise FileNotFoundError(
        f"could not locate {CONFIG_RELATIVE} (searched from {[str(s) for s in starts]})"
    )


def load_signatures(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    cd = config_dir or _find_config_dir()
    with (cd / "SIGNATURES.json").open(encoding="utf-8") as f:
        d = json.load(f)
    validate_signatures(d)
    return d


def load_redaction(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    cd = config_dir or _find_config_dir()
    with (cd / "REDACTION_PATTERNS.json").open(encoding="utf-8") as f:
        d = json.load(f)
    validate_redaction(d)
    return d


def load_thresholds(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    cd = config_dir or _find_config_dir()
    with (cd / "THRESHOLDS.json").open(encoding="utf-8") as f:
        d = json.load(f)
    validate_thresholds(d)
    return d


def validate_signatures(d: Dict[str, Any]) -> None:
    if d.get("schema_version") != "inq.signatures.v0_1":
        raise ValueError(f"unexpected signatures schema_version: {d.get('schema_version')!r}")
    if "secrets" not in d or not isinstance(d["secrets"], dict):
        raise ValueError("signatures: missing/invalid 'secrets'")
    if "pi_categories" not in d or not isinstance(d["pi_categories"], dict):
        raise ValueError("signatures: missing/invalid 'pi_categories'")
    for name, spec in d["secrets"].items():
        if "regex" not in spec:
            raise ValueError(f"secrets.{name}: missing 'regex'")
        try:
            re.compile(spec["regex"])
        except re.error as e:
            raise ValueError(f"secrets.{name}: invalid regex: {e}")
    for cat, spec in d["pi_categories"].items():
        if "patterns" not in spec or not isinstance(spec["patterns"], list):
            raise ValueError(f"pi_categories.{cat}: missing/invalid 'patterns'")
        if "weight" not in spec:
            raise ValueError(f"pi_categories.{cat}: missing 'weight'")
        for i, pat in enumerate(spec["patterns"]):
            try:
                re.compile(pat)
            except re.error as e:
                raise ValueError(f"pi_categories.{cat}.patterns[{i}]: invalid regex: {e}")


def validate_redaction(d: Dict[str, Any]) -> None:
    if d.get("schema_version") != "inq.redaction.v0_1":
        raise ValueError(f"unexpected redaction schema_version: {d.get('schema_version')!r}")
    if "targets" not in d or not isinstance(d["targets"], dict):
        raise ValueError("redaction: missing 'targets'")


def validate_thresholds(d: Dict[str, Any]) -> None:
    if d.get("schema_version") != "inq.thresholds.v0_1":
        raise ValueError(f"unexpected thresholds schema_version: {d.get('schema_version')!r}")
    required = {
        "secrets_entropy_code", "secrets_entropy_text",
        "pi_score_block_llm", "pi_score_block_owner",
        "trust_baseline_llm", "trust_baseline_owner",
        "trust_delta_ok", "trust_delta_block", "trust_min_permit",
        "probation_cycles",
        "ban_burst_consec", "ban_burst_weekly", "ban_duration",
        "purge_requires_core_ready", "fail_closed_default",
        "anomaly_first_author",
    }
    missing = required - set(d.get("thresholds", {}).keys())
    if missing:
        raise ValueError(f"thresholds: missing required keys: {sorted(missing)}")


def get_threshold(key: str, config_dir: Optional[Path] = None) -> Any:
    d = load_thresholds(config_dir)
    if key not in d["thresholds"]:
        raise KeyError(f"unknown threshold: {key}")
    return d["thresholds"][key]


def compile_secret_patterns(
    sigs: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, "re.Pattern[str]", Dict[str, Any]]]:
    d = sigs if sigs is not None else load_signatures()
    out: List[Tuple[str, re.Pattern[str], Dict[str, Any]]] = []
    for name, spec in d["secrets"].items():
        out.append((name, re.compile(spec["regex"]), spec))
    return out


def compile_pi_patterns(
    sigs: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, int, List["re.Pattern[str]"]]]:
    d = sigs if sigs is not None else load_signatures()
    out: List[Tuple[str, int, List[re.Pattern[str]]]] = []
    for cat, spec in d["pi_categories"].items():
        compiled = [re.compile(p) for p in spec["patterns"]]
        out.append((cat, int(spec["weight"]), compiled))
    return out


def _ensure_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _cli() -> int:
    args = sys.argv[1:]
    try:
        if "--validate" in args:
            load_signatures()
            load_redaction()
            load_thresholds()
            print(json.dumps({"ok": True, "schema_versions": {
                "signatures": "inq.signatures.v0_1",
                "redaction": "inq.redaction.v0_1",
                "thresholds": "inq.thresholds.v0_1",
            }}))
            return 0
        if "--dump" in args:
            i = args.index("--dump")
            if i + 1 >= len(args):
                print(json.dumps({"error": "missing key for --dump"}))
                return 4
            key = args[i + 1]
            if key == "signatures":
                d = load_signatures()
            elif key == "redaction":
                d = load_redaction()
            elif key == "thresholds":
                d = load_thresholds()
            else:
                print(json.dumps({"error": f"unknown dump key: {key}"}))
                return 4
            print(json.dumps(d, ensure_ascii=False, indent=2))
            return 0
        if "--list-thresholds" in args:
            d = load_thresholds()
            for k, v in d["thresholds"].items():
                val = v.get("value") if isinstance(v, dict) else v
                ov = v.get("overridable") if isinstance(v, dict) else None
                tag = "" if ov is None else f"  [overridable={ov}]"
                print(f"{k} = {val}{tag}")
            return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}))
        return 4
    sys.stderr.write(
        "[inq_patterns] usage: --validate | --dump (signatures|redaction|thresholds) | --list-thresholds\n"
    )
    return 0


if __name__ == "__main__":
    _ensure_utf8()
    sys.exit(_cli())
