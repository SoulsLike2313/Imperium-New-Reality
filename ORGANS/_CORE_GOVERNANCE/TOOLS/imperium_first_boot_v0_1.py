#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imperium_first_boot_v0_1.py
===========================
ENTRY_PROTOCOL_FOR_LLM attestation tool.

Reads the canonical mandatory file list, computes sha256 of each, and writes
an attestation receipt to _HARNESS/_RUNS/<UTC>/ENTRY_ACKS/<role>_<sid>.json.

NO_LLM_IN_PIPELINE: this tool is pure stdlib. It does not import any LLM,
network, or non-deterministic dependency.

Usage:
    python3 imperium_first_boot_v0_1.py \
        --role LOGOS_PRIME --session-id 2026-06-22T19:00Z \
        --scope DOCTR-TOOLS-0001 --auto-ack

Exit codes:
    0  attestation written successfully
    2  mandatory file missing from repo
    3  declared_role not present in ROLE_REGISTRY
    4  ack flags missing and not interactive
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path


SCHEMA_VERSION = "imperium.entry_attestation.v0_1"
TOOL_NAME = "imperium_first_boot_v0_1"

# Mandatory read list mirrors ENTRY_PROTOCOL_FOR_LLM.md §2.
# Repo-relative POSIX paths.
MANDATORY_READ_LIST = [
    "ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md",
    "ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md",
    "ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json",
    "ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json",
    "DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md",
    "ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md",
    "ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md",
    "ORGANS/DOCTRINARIUM/LAWS/EMPEROR_SEAL_PLACEHOLDER.md",
    "ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md",
]

ROLE_REGISTRY_PATH = "ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md"

# Known role identifiers extractable from ROLE_REGISTRY.md §1.
# Hard-coded fallback list; §2 mandates the validator also parse the file.
KNOWN_ROLES = {
    "OWNER_MANUAL",
    "THRONE",
    "LOGOS_PRIME",
    "SPECULUM",
    "SERVITOR_PRIME",
    "ROGUE_TRADER",
    "FREE_ARCHITECT",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_digest(repo_root: Path, paths: list[str]) -> str:
    """Deterministic digest over the mandatory read set."""
    h = hashlib.sha256()
    for rel in sorted(paths):
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        fp = repo_root / rel
        if fp.exists() and fp.is_file():
            h.update(sha256_file(fp).encode("ascii"))
        else:
            h.update(b"MISSING")
        h.update(b"\n")
    return h.hexdigest()


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_run_dir_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_role_registry_actives(repo_root: Path) -> set[str]:
    """Extract role names from ROLE_REGISTRY.md table. Returns empty set on
    parse failure (validator falls back to KNOWN_ROLES)."""
    fp = repo_root / ROLE_REGISTRY_PATH
    if not fp.exists():
        return set()
    roles: set[str] = set()
    try:
        text = fp.read_text(encoding="utf-8")
    except OSError:
        return set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.split("|")]
        if len(cells) < 3:
            continue
        candidate = cells[1]
        if candidate and candidate.replace("_", "").isalnum() and candidate.isupper():
            roles.add(candidate)
    return roles


def build_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Imperium entry-protocol attestation.")
    p.add_argument("--repo-root", default=".", help="Path to repository root (default: cwd).")
    p.add_argument("--role", required=True, help="Declared actor role.")
    p.add_argument("--session-id", required=True, help="Session identifier.")
    p.add_argument("--scope", default="broad", help="Task or organ scope (default: broad).")
    p.add_argument("--auto-ack", action="store_true", help="Accept the three acknowledgements without prompting.")
    p.add_argument("--output-dir", default=None, help="Override receipt output directory.")
    return p.parse_args(argv)


def interactive_acks() -> dict[str, bool]:
    acks: dict[str, bool] = {}
    prompts = [
        ("no_llm_in_pipeline",     "Acknowledge NO_LLM_IN_PIPELINE? [y/N]: "),
        ("kernel_writes_need_seal","Acknowledge kernel writes require EMPEROR_SEAL (or declared bypass)? [y/N]: "),
        ("forbidden_claims_known", "Acknowledge forbidden-claims list is read and understood? [y/N]: "),
    ]
    for key, prompt in prompts:
        try:
            ans = input(prompt).strip().lower()
        except EOFError:
            return acks
        acks[key] = ans.startswith("y")
    return acks


def main(argv: list[str] | None = None) -> int:
    args = build_args(argv)
    repo_root = Path(args.repo_root).resolve()

    missing: list[str] = []
    hashes: dict[str, str] = {}
    for rel in MANDATORY_READ_LIST:
        fp = repo_root / rel
        if not fp.exists() or not fp.is_file():
            missing.append(rel)
            continue
        hashes[rel] = sha256_file(fp)

    parsed_roles = parse_role_registry_actives(repo_root)
    role_universe = parsed_roles if parsed_roles else KNOWN_ROLES

    if missing:
        sys.stderr.write("[first_boot] missing mandatory files:\n")
        for rel in missing:
            sys.stderr.write(f"  - {rel}\n")
        sys.stderr.write("Refusing to write attestation.\n")
        return 2

    if args.role not in role_universe:
        sys.stderr.write(f"[first_boot] declared role '{args.role}' not in role universe {sorted(role_universe)}\n")
        return 3

    if args.auto_ack:
        acks = {
            "no_llm_in_pipeline":      True,
            "kernel_writes_need_seal": True,
            "forbidden_claims_known":  True,
        }
    else:
        if not sys.stdin.isatty():
            sys.stderr.write("[first_boot] non-interactive run requires --auto-ack\n")
            return 4
        acks = interactive_acks()
        if not all(acks.values()):
            sys.stderr.write("[first_boot] one or more acks declined; refusing to write attestation.\n")
            return 4

    receipt = {
        "schema_version":   SCHEMA_VERSION,
        "actor":            f"{args.role}:{args.session_id}",
        "read_files":       list(MANDATORY_READ_LIST),
        "read_shas":        hashes,
        "snapshot_digest":  snapshot_digest(repo_root, MANDATORY_READ_LIST),
        "declared_role":    args.role,
        "declared_scope":   args.scope,
        "attested_at":      utc_now_iso(),
        "acks":             acks,
        "tool":             TOOL_NAME,
    }

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = repo_root / "_HARNESS" / "_RUNS" / utc_run_dir_stamp() / "ENTRY_ACKS"
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_sid = args.session_id.replace(":", "-").replace("/", "-")
    out_path = out_dir / f"{args.role}_{safe_sid}.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sys.stdout.write(f"[first_boot] attestation written: {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
