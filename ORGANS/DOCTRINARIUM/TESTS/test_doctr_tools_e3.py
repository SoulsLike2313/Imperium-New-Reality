#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_doctr_tools_e3.py -- E3 self-tests for DOCTR-TOOLS-0001.
NO_LLM_IN_PIPELINE: pure stdlib + subprocess.

Runner contract: each test prints E3_MARKER_<name>__PASS or __FAIL.
main() exits 0 if all PASS, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

LAW_FILES = [
    "ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md",
    "ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md",
    "ORGANS/DOCTRINARIUM/LAWS/ENTRY_PROTOCOL_FOR_LLM.md",
    "ORGANS/DOCTRINARIUM/LAWS/EMPEROR_SEAL_PLACEHOLDER.md",
    "ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md",
]
KPD = "ORGANS/DOCTRINARIUM/MATRICES/KPD_METRIC_SPEC.md"
ORGAN_CARD = "ORGANS/DOCTRINARIUM/ORGAN_CARD.json"
ORGAN_CONTRACT = "ORGANS/DOCTRINARIUM/ORGAN_CONTRACT.md"
INVENTORY = "ORGANS/DOCTRINARIUM/TASK_PARTICIPATION/ORGAN_TOOL_AND_RECEIPT_INVENTORY.json"
TOOL_BOOT = "ORGANS/_CORE_GOVERNANCE/TOOLS/imperium_first_boot_v0_1.py"
TOOL_GUARD = "ORGANS/_CORE_GOVERNANCE/TOOLS/kernel_write_guard_v0_1.py"
TOOL_INT = "ORGANS/DOCTRINARIUM/TOOLS/doctrinarium_integrity_validator_v0_1.py"
SCHEMAS = [
    "ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.canon_admission.v0_1.schema.json",
    "ORGANS/_CORE_GOVERNANCE/SCHEMAS/imperium.kernel_write_guard.v0_1.schema.json",
    "ORGANS/DOCTRINARIUM/SCHEMAS/imperium.doctrinarium_integrity.v0_1.schema.json",
]

results: list[tuple[str, bool, str]] = []


def _mark(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"E3_MARKER_{name}__{status}"
    if not ok and detail:
        line += f" :: {detail}"
    print(line)
    results.append((name, ok, detail))


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _read_json(rel: str) -> dict:
    return json.loads(_read(rel))


# ----- structural tests --------------------------------------------------

def t01_laws_frontmatter() -> None:
    bad = [r for r in LAW_FILES if not re.search(r"law_id:\s*DOCTR\.LAW\.", _read(r))]
    _mark("01_laws_frontmatter_law_id", not bad, ";".join(bad))


def t02_laws_forbidden_claims() -> None:
    bad = [r for r in LAW_FILES if ("Forbidden claims" not in _read(r) and "Forbidden Claims" not in _read(r))]
    _mark("02_laws_forbidden_claims_section", not bad, ";".join(bad))


def t03_kernel_pattern_block() -> None:
    text = _read("ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md")
    ok = "KERNEL_PATTERNS" in text and "ORGANS/_CORE_GOVERNANCE/CONSTITUTION/**" in text
    _mark("03_kernel_boundary_patterns_present", ok)


def t04_pipeline_seven_stages() -> None:
    text = _read("ORGANS/DOCTRINARIUM/LAWS/CANONICAL_PIPELINE.md")
    stages = ["INTAKE", "CHARTER", "BOUNDARY", "WRITE", "VERIFY", "ARCHIVE", "RECEIPT"]
    missing = [s for s in stages if s not in text]
    _mark("04_pipeline_seven_stages", not missing, ";".join(missing))


def t05_entry_protocol_mentions_boot_tool() -> None:
    text = _read("ORGANS/DOCTRINARIUM/LAWS/ENTRY_PROTOCOL_FOR_LLM.md")
    _mark("05_entry_protocol_mentions_boot_tool", "imperium_first_boot_v0_1.py" in text)


def t06_seal_placeholder_alpha() -> None:
    text = _read("ORGANS/DOCTRINARIUM/LAWS/EMPEROR_SEAL_PLACEHOLDER.md")
    ok = "PLACEHOLDER" in text and "DOCTR-EMPEROR-SEAL-0001" in text and "OBSERVER" in text
    _mark("06_emperor_seal_placeholder_alpha", ok)


def t07_role_registry_seven_roles() -> None:
    text = _read("ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md")
    roles = ["OWNER_MANUAL", "THRONE", "LOGOS_PRIME", "SPECULUM", "SERVITOR_PRIME", "ROGUE_TRADER", "FREE_ARCHITECT"]
    missing = [r for r in roles if r not in text]
    _mark("07_role_registry_seven_roles", not missing, ";".join(missing))


def t08_kpd_six_components() -> None:
    text = _read(KPD)
    comps = ["FTP", "FGCR", "TTT", "RI", "KPE", "RC"]
    missing = [c for c in comps if c not in text]
    _mark("08_kpd_six_components", not missing, ";".join(missing))


def t09_organ_card_v1_shape() -> None:
    d = _read_json(ORGAN_CARD)
    ok = (
        d.get("organ_id") == "DOCTRINARIUM"
        and len(d.get("owned_laws", [])) == 5
        and len(d.get("owned_schemas", [])) >= 1
        and len(d.get("owned_tools", [])) >= 1
        and len(d.get("validators", [])) >= 3
    )
    _mark("09_organ_card_v1_shape", ok)


def t10_organ_contract_v1_markers() -> None:
    text = _read(ORGAN_CONTRACT)
    ok = "V1.0" in text and "DOCTR-TOOLS-0001" in text and "NO_LLM_IN_PIPELINE" in text
    _mark("10_organ_contract_v1_markers", ok)


def t11_inventory_v02_bump() -> None:
    d = _read_json(INVENTORY)
    paths = d.get("local_script_first", [])
    ok = (
        d.get("schema_version") == "imperium.organ_tool_inventory.v0_2"
        and any("doctrinarium_integrity_validator_v0_1" in p for p in paths)
        and any("kernel_write_guard_v0_1" in p for p in paths)
        and any("imperium_first_boot_v0_1" in p for p in paths)
    )
    _mark("11_inventory_v02_schema_bump", ok)


def t12_schemas_parse() -> None:
    bad: list[str] = []
    for rel in SCHEMAS:
        try:
            data = _read_json(rel)
            if not data.get("$schema") or not data.get("$id"):
                bad.append(rel)
        except Exception as exc:
            bad.append(f"{rel}:{exc}")
    _mark("12_schemas_valid_draft7", not bad, ";".join(bad))


def t13_gitignore_patch_present() -> None:
    # PASS if either:
    #   (a) pre-apply (sandbox / pack root): payload _root_patches source present, OR
    #   (b) post-apply (live repo): .gitignore at repo root carries the marker.
    src = REPO_ROOT / "_root_patches" / "gitignore_append.txt"
    if src.exists() and "_HARNESS/_RUNS/" in src.read_text(encoding="utf-8"):
        _mark("13_gitignore_patch_present", True); return
    gi = REPO_ROOT / ".gitignore"
    if gi.exists():
        text = gi.read_text(encoding="utf-8")
        if "IMPERIUM hygiene additions (DOCTR-TOOLS-0001)" in text and "_HARNESS/_RUNS/" in text:
            _mark("13_gitignore_patch_present", True); return
    _mark("13_gitignore_patch_present", False)


# ----- integration tests (tools end-to-end) ------------------------------

def _fixture_repo(tmp: Path) -> Path:
    """Build a minimal repo skeleton sufficient for tool invocations."""
    root = tmp / "fixture"
    root.mkdir(parents=True, exist_ok=True)
    # mirror payload tree
    for rel in LAW_FILES + [KPD, ORGAN_CARD, ORGAN_CONTRACT, INVENTORY, TOOL_BOOT, TOOL_GUARD, TOOL_INT] + SCHEMAS:
        src = REPO_ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    # minimal mandatory-read-list stubs for first_boot + integrity validator
    stubs = {
        "ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md": "# stub constitution\n",
        "ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md": "# stub passport\n",
        "ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json": "{\"v\":\"stub\"}\n",
        "ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json": "{\"v\":\"stub\"}\n",
        "DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md": "# stub charter ru\n",
        "DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md": "# stub charter en\n",
    }
    for rel, content in stubs.items():
        fp = root / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
    return root


def t14_first_boot_happy_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        out = root / "out_acks"
        cmd = [
            sys.executable, str(root / TOOL_BOOT),
            "--repo-root", str(root),
            "--role", "LOGOS_PRIME",
            "--session-id", "test_session",
            "--scope", "DOCTR-TOOLS-0001",
            "--auto-ack",
            "--output-dir", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0 and any(out.iterdir()) if out.exists() else False
        if ok:
            receipt = json.loads(next(out.iterdir()).read_text(encoding="utf-8"))
            ok = receipt.get("schema_version") == "imperium.entry_attestation.v0_1" and receipt.get("declared_role") == "LOGOS_PRIME"
        _mark("14_first_boot_happy_path", ok, r.stderr[:200])


def t15_first_boot_rejects_bad_role() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        cmd = [
            sys.executable, str(root / TOOL_BOOT),
            "--repo-root", str(root),
            "--role", "NOT_A_REAL_ROLE",
            "--session-id", "x", "--auto-ack",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        _mark("15_first_boot_rejects_bad_role", r.returncode == 3)


def t16_kernel_guard_allow_for_payload_paths() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        changed = root / "changed.txt"
        changed.write_text(
            "ORGANS/DOCTRINARIUM/LAWS/ROLE_REGISTRY.md\n"
            "ORGANS/DOCTRINARIUM/TOOLS/doctrinarium_integrity_validator_v0_1.py\n"
            "ORGANS/DOCTRINARIUM/MATRICES/KPD_METRIC_SPEC.md\n",
            encoding="utf-8",
        )
        out = root / "out_guard"
        cmd = [
            sys.executable, str(root / TOOL_GUARD),
            "--repo-root", str(root),
            "--changed-paths", str(changed),
            "--task-id", "DOCTR-TOOLS-0001",
            "--actor-role", "LOGOS_PRIME",
            "--output-dir", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        if ok and out.exists():
            receipt = json.loads(next(out.iterdir()).read_text(encoding="utf-8"))
            ok = receipt.get("verdict") == "ALLOW" and not receipt.get("kernel_paths_touched")
        _mark("16_kernel_guard_allow_payload", ok, r.stderr[:200])


def t17_kernel_guard_deny_kernel_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        changed = root / "changed.txt"
        changed.write_text("ORGANS/_CORE_GOVERNANCE/CONSTITUTION/CONSTITUTION_OF_THE_IMPERIUM.md\n", encoding="utf-8")
        out = root / "out_guard_kernel"
        cmd = [
            sys.executable, str(root / TOOL_GUARD),
            "--repo-root", str(root),
            "--changed-paths", str(changed),
            "--actor-role", "LOGOS_PRIME",
            "--output-dir", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        # OBSERVER mode default: exit 0 even on DENY
        ok = r.returncode == 0
        if ok and out.exists():
            receipt = json.loads(next(out.iterdir()).read_text(encoding="utf-8"))
            ok = receipt.get("verdict") == "DENY" and len(receipt.get("kernel_paths_touched", [])) >= 1 and receipt.get("mode") == "OBSERVER"
        _mark("17_kernel_guard_deny_kernel_no_bypass", ok, r.stderr[:200])


def t18_kernel_guard_allow_with_bypass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        changed = root / "changed.txt"
        changed.write_text("ORGANS/_CORE_GOVERNANCE/EMPEROR/PASSPORT_OF_THE_EMPEROR.md\n", encoding="utf-8")
        out = root / "out_guard_bypass"
        cmd = [
            sys.executable, str(root / TOOL_GUARD),
            "--repo-root", str(root),
            "--changed-paths", str(changed),
            "--actor-role", "OWNER_MANUAL",
            "--bypass", "owner_manual",
            "--output-dir", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        if ok and out.exists():
            receipt = json.loads(next(out.iterdir()).read_text(encoding="utf-8"))
            ok = receipt.get("verdict") == "ALLOW_WITH_BYPASS"
        _mark("18_kernel_guard_allow_with_bypass", ok, r.stderr[:200])


def t19_integrity_validator_pass_on_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        out = root / "out_int"
        cmd = [
            sys.executable, str(root / TOOL_INT),
            "--repo-root", str(root),
            "--output-dir", str(out),
            "--quiet",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 0
        if ok and out.exists():
            receipt = json.loads(next(out.iterdir()).read_text(encoding="utf-8"))
            ok = receipt.get("overall") in ("PASS", "WARN")
        _mark("19_integrity_validator_pass_fixture", ok, r.stderr[:200])


def t20_integrity_validator_fails_on_missing_law() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture_repo(Path(tmp))
        # Sabotage: remove KERNEL_BOUNDARY_CONTRACT.md
        (root / "ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md").unlink()
        out = root / "out_int_fail"
        cmd = [
            sys.executable, str(root / TOOL_INT),
            "--repo-root", str(root),
            "--output-dir", str(out),
            "--quiet",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = r.returncode == 1
        _mark("20_integrity_validator_fails_missing_law", ok)


def main() -> int:
    tests = [
        t01_laws_frontmatter, t02_laws_forbidden_claims, t03_kernel_pattern_block,
        t04_pipeline_seven_stages, t05_entry_protocol_mentions_boot_tool,
        t06_seal_placeholder_alpha, t07_role_registry_seven_roles,
        t08_kpd_six_components, t09_organ_card_v1_shape, t10_organ_contract_v1_markers,
        t11_inventory_v02_bump, t12_schemas_parse, t13_gitignore_patch_present,
        t14_first_boot_happy_path, t15_first_boot_rejects_bad_role,
        t16_kernel_guard_allow_for_payload_paths, t17_kernel_guard_deny_kernel_path,
        t18_kernel_guard_allow_with_bypass,
        t19_integrity_validator_pass_on_fixture,
        t20_integrity_validator_fails_on_missing_law,
    ]
    for fn in tests:
        try:
            fn()
        except Exception as exc:
            _mark(fn.__name__, False, f"exception: {exc}")
    failed = [n for n, ok, _ in results if not ok]
    print(f"E3_SUMMARY total={len(results)} passed={len(results)-len(failed)} failed={len(failed)}")
    if failed:
        print("E3_FAILED: " + ", ".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
