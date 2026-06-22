#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doctrinarium_integrity_validator_v0_1.py
========================================
Validates the structural integrity of the DOCTRINARIUM organ:

- Hash-locks all known charters, LAWS, and matrices.
- Cross-checks ORGAN_CARD.json validators / owned_matrices / owned_laws /
  owned_schemas / owned_tools against actual files on disk.
- Verifies each LAW has a YAML frontmatter and a Forbidden Claims section.
- Verifies ENTRY_PROTOCOL §2 mandatory read list resolves to existing files
  (advisory in v0_1).
- Verifies KERNEL_BOUNDARY_CONTRACT §2 patterns are non-empty and parseable.

NO_LLM_IN_PIPELINE: pure stdlib, deterministic.

Usage:
    python3 doctrinarium_integrity_validator_v0_1.py --repo-root .

Exit codes:
    0  overall PASS or WARN (informational)
    1  overall FAIL
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path


SCHEMA_VERSION = "imperium.doctrinarium_integrity.v0_1"
TOOL_NAME = "doctrinarium_integrity_validator_v0_1"

ORGAN_ROOT = "ORGANS/DOCTRINARIUM"
ORGAN_CARD = f"{ORGAN_ROOT}/ORGAN_CARD.json"
CHARTER_RU = "DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md"
CHARTER_EN = "DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md"
LAWS_DIR = f"{ORGAN_ROOT}/LAWS"
KERNEL_BOUNDARY_LAW = f"{LAWS_DIR}/KERNEL_BOUNDARY_CONTRACT.md"
ENTRY_PROTOCOL_LAW = f"{LAWS_DIR}/ENTRY_PROTOCOL_FOR_LLM.md"

REQUIRED_LAW_NAMES = [
    "KERNEL_BOUNDARY_CONTRACT.md",
    "CANONICAL_PIPELINE.md",
    "ENTRY_PROTOCOL_FOR_LLM.md",
    "EMPEROR_SEAL_PLACEHOLDER.md",
    "ROLE_REGISTRY.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_run_dir_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def check(status: str, detail: str = "", evidence: str = "") -> dict:
    return {"status": status, "detail": detail, "evidence": evidence}


def parse_frontmatter(text: str) -> dict | None:
    """Best-effort YAML frontmatter parse without external deps. Returns
    None when the file does not begin with a fenced yaml block."""
    lines = text.splitlines()
    i = 0
    # Skip the leading H1 if present.
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
    if i >= len(lines) or not lines[i].strip().startswith("```"):
        return None
    fence = lines[i].strip()
    if "yaml" not in fence.lower():
        return None
    i += 1
    block: list[str] = []
    while i < len(lines) and not lines[i].strip().startswith("```"):
        block.append(lines[i])
        i += 1
    data: dict = {}
    for ln in block:
        if ":" not in ln:
            continue
        key, _, value = ln.partition(":")
        data[key.strip()] = value.strip()
    return data


def parse_kernel_patterns(law_path: Path) -> list[str]:
    text = law_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_section = False
    in_code = False
    out: list[str] = []
    for line in lines:
        if line.startswith("## ") and "KERNEL_PATTERNS" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code and line.strip():
            out.append(line.strip())
    return out


def parse_entry_protocol_read_list(law_path: Path) -> list[str]:
    if not law_path.exists():
        return []
    text = law_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_section = False
    in_code = False
    out: list[str] = []
    for line in lines:
        if line.startswith("## ") and "Mandatory read list" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and "." in stripped:
                rest = stripped.split(".", 1)[1].strip()
                if rest:
                    out.append(rest)
    return out


def build_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Validate DOCTRINARIUM integrity.")
    p.add_argument("--repo-root", default=".", help="Repository root (default cwd).")
    p.add_argument("--output-dir", default=None, help="Override receipt output dir.")
    p.add_argument("--quiet", action="store_true", help="Suppress per-check stdout.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = build_args(argv)
    repo_root = Path(args.repo_root).resolve()

    hashes: dict[str, str] = {}
    failures: list[str] = []

    def add_hash(rel: str, required: bool = True) -> Path | None:
        fp = repo_root / rel
        if fp.exists() and fp.is_file():
            hashes[rel] = sha256_file(fp)
            return fp
        if required:
            failures.append(f"missing required file: {rel}")
        return None

    # Charters
    add_hash(CHARTER_RU)
    add_hash(CHARTER_EN)

    # LAWS
    for name in REQUIRED_LAW_NAMES:
        add_hash(f"{LAWS_DIR}/{name}")

    # ORGAN_CARD
    organ_card_path = repo_root / ORGAN_CARD
    if organ_card_path.exists():
        hashes[ORGAN_CARD] = sha256_file(organ_card_path)
        try:
            organ_card = json.loads(organ_card_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            organ_card = {}
            failures.append(f"ORGAN_CARD.json json error: {exc}")
    else:
        organ_card = {}
        failures.append("missing ORGAN_CARD.json")

    # Cross-ref: validators / owned_* exist
    validators_ok = True
    matrices_ok = True
    laws_ok = True
    schemas_ok = True
    tools_ok = True

    for kind, key, ok_ref in [
        ("validators", "validators", None),
        ("matrices",   "owned_matrices", None),
        ("laws",       "owned_laws", None),
        ("schemas",    "owned_schemas", None),
        ("tools",      "owned_tools", None),
    ]:
        items = organ_card.get(key, [])
        for rel in items:
            fp = repo_root / rel
            if not fp.exists() or not fp.is_file():
                # matrices may legitimately be pre-charter stubs in v0_1 alpha;
                # downgrade to WARN (record absence but do not fail integrity).
                if kind == "matrices":
                    matrices_ok = False
                    continue
                failures.append(f"ORGAN_CARD.{key} references missing file: {rel}")
                if kind == "validators":
                    validators_ok = False
                elif kind == "laws":
                    laws_ok = False
                elif kind == "schemas":
                    schemas_ok = False
                elif kind == "tools":
                    tools_ok = False
            else:
                hashes.setdefault(rel, sha256_file(fp))

    # Per-LAW structural checks
    laws_have_fm = True
    laws_have_fc = True
    for name in REQUIRED_LAW_NAMES:
        rel = f"{LAWS_DIR}/{name}"
        fp = repo_root / rel
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm or "law_id" not in fm:
            laws_have_fm = False
            failures.append(f"LAW missing yaml frontmatter with law_id: {rel}")
        if "Forbidden claims" not in text and "Forbidden Claims" not in text:
            laws_have_fc = False
            failures.append(f"LAW missing Forbidden Claims section: {rel}")

    # KERNEL_BOUNDARY §2 parseable
    kb_path = repo_root / KERNEL_BOUNDARY_LAW
    if kb_path.exists():
        patterns = parse_kernel_patterns(kb_path)
        kb_ok = len(patterns) > 0
        if not kb_ok:
            failures.append("KERNEL_BOUNDARY §2 patterns parsed empty")
    else:
        kb_ok = False
        patterns = []

    # ENTRY_PROTOCOL read list resolves
    ep_path = repo_root / ENTRY_PROTOCOL_LAW
    ep_unresolved: list[str] = []
    if ep_path.exists():
        read_list = parse_entry_protocol_read_list(ep_path)
        for entry in read_list:
            if entry.startswith("The charter") or entry.lower().startswith("the actor"):
                continue
            candidate = repo_root / entry
            if not candidate.exists():
                ep_unresolved.append(entry)
        ep_ok = len(ep_unresolved) == 0
    else:
        ep_ok = False
        failures.append("ENTRY_PROTOCOL_FOR_LLM.md missing")

    cross_refs = {
        "organ_card_validators_exist":        check("PASS" if validators_ok else "FAIL"),
        "organ_card_owned_matrices_exist":    check("PASS" if matrices_ok else "WARN", "", "matrices_pre_charter"),
        "laws_have_forbidden_claims_section": check("PASS" if laws_have_fc else "FAIL"),
        "laws_have_yaml_frontmatter":         check("PASS" if laws_have_fm else "FAIL"),
        "entry_protocol_read_list_resolves":  check("PASS" if ep_ok else "WARN", evidence=";".join(ep_unresolved)),
        "kernel_boundary_patterns_parseable": check("PASS" if kb_ok else "FAIL", detail=f"{len(patterns)} patterns"),
    }

    extra_checks = {
        "required_laws_present":  check("PASS" if all((LAWS_DIR + "/" + n) in hashes for n in REQUIRED_LAW_NAMES) else "FAIL"),
        "organ_card_schemas_exist": check("PASS" if schemas_ok else "FAIL"),
        "organ_card_tools_exist":   check("PASS" if tools_ok else "FAIL"),
        "organ_card_laws_exist":    check("PASS" if laws_ok else "FAIL"),
    }

    # Overall verdict
    statuses = [r["status"] for r in list(cross_refs.values()) + list(extra_checks.values())]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARN" in statuses:
        overall = "WARN"
    else:
        overall = "PASS"

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "validated_at":   utc_now_iso(),
        "validator":      TOOL_NAME,
        "organ":          "DOCTRINARIUM",
        "hashes":         hashes,
        "cross_refs":     cross_refs,
        "checks":         extra_checks,
        "overall":        overall,
        "failures":       failures,
    }

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = repo_root / "_HARNESS" / "_RUNS" / utc_run_dir_stamp() / "DOCTRINARIUM_INTEGRITY"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{utc_run_dir_stamp()}.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not args.quiet:
        sys.stdout.write(f"[doctr-integrity] overall={overall} hashes={len(hashes)} failures={len(failures)} receipt={out_path}\n")
        for fname in failures:
            sys.stdout.write(f"  - {fname}\n")

    return 0 if overall != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
