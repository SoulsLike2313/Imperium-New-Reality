#!/usr/bin/env python3
"""INQ-TOOLS-0001 E3 test matrix (T1-T10) -- aligned to real CLI signatures."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _force_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _discover_pack_root() -> Path:
    env = os.environ.get("PACK_ROOT")
    if env:
        p = Path(env).resolve()
        if p.is_dir():
            return p
    start = Path(__file__).resolve()
    for cand in [start.parent] + list(start.parents):
        if (cand / "_HARNESS").is_dir() and (cand / "ORGANS").is_dir():
            return cand
    raise RuntimeError("PACK_ROOT not found from %s" % start)


ROOT: Path = _discover_pack_root()
TOOLS: Path = ROOT / "ORGANS" / "INQUISITION" / "TOOLS"
CFG: Path = ROOT / "ORGANS" / "INQUISITION" / "CONFIG"
TRUST_FILE: Path = ROOT / "ORGANS" / "INQUISITION" / "TRUST" / "authors.json"
BANS_FILE: Path = ROOT / "ORGANS" / "INQUISITION" / "BAN_LIST" / "bans.jsonl"
FX: Path = ROOT / "_HARNESS" / "_FIXTURES" / "INQ"
RUNNER: Path = ROOT / "_HARNESS" / "RUNNER" / "e3_runner.py"
PY = sys.executable


def _run_tool(tool: str, *args: str) -> Dict[str, Any]:
    cmd = [PY, str(TOOLS / tool), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45)
    last_line = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout.strip() else ""
    try:
        verdict = json.loads(last_line) if last_line else {}
    except json.JSONDecodeError:
        verdict = {"_parse_error": last_line[:200]}
    return {"rc": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "verdict": verdict}


def _new_tmp_pack(name: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"inq_t_{name}_"))


def _copy_fx(fx_relpath: str, dst: Path) -> Path:
    src = FX / fx_relpath
    out = dst / src.name
    shutil.copy(src, out)
    return out


FAILS: List[Tuple[str, str]] = []


def _assert(cond: bool, tag: str, detail: str) -> None:
    if not cond:
        FAILS.append((tag, detail))
        print(f"[FAIL] {tag}: {detail}")
    else:
        print(f"[ ok ] {tag}")


def T0_runner_path_invariance() -> None:
    # INV-1: tmp dir without markers -> RuntimeError, never IndexError
    tmp = _new_tmp_pack("empty")
    try:
        proc = subprocess.run(
            [PY, "-c", f"import sys; sys.path.insert(0, r'{RUNNER.parent}'); import e3_runner; print(e3_runner.find_pack_root(start=__import__('pathlib').Path(r'{tmp}')))"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, cwd=str(tmp),
        )
        combined = proc.stderr + proc.stdout
        if "IndexError" in proc.stderr:
            _assert(False, "T0.INV-1", f"REGRESSION: IndexError leaked: {proc.stderr[:200]}")
        elif "PACK_ROOT not found" in combined:
            _assert(True, "T0.INV-1", "RuntimeError raised cleanly")
        else:
            # Could have resolved via Path.cwd() fallback into a parent tree -- acceptable.
            _assert(proc.returncode == 0, "T0.INV-1", f"unexpected: rc={proc.returncode} out={proc.stdout[:160]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # INV-2 + INV-3
    for label, start in (("INV-2_root", ROOT), ("INV-3_runner_dir", RUNNER.parent)):
        proc = subprocess.run(
            [PY, "-c", f"import sys; sys.path.insert(0, r'{RUNNER.parent}'); import e3_runner; print(e3_runner.find_pack_root(start=__import__('pathlib').Path(r'{start}')))"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        _assert(
            proc.returncode == 0 and str(ROOT) in proc.stdout,
            f"T0.{label}",
            f"rc={proc.returncode} out={proc.stdout.strip()[:160]} err={proc.stderr.strip()[:160]}",
        )


def T1_health_smoke() -> None:
    r = _run_tool("inquisition.py", "--health")
    v = r["verdict"]
    _assert(r["rc"] == 0, "T1.rc", f"rc={r['rc']} stderr={r['stderr'][:200]}")
    _assert(isinstance(v.get("tools"), list) and len(v["tools"]) >= 10, "T1.tools_count", f"tools={len(v.get('tools',[]))}")
    _assert(all(t.get("syntax_ok") is True for t in v.get("tools", [])), "T1.syntax_ok_all", "some tool failed syntax check")
    _assert(v.get("overall") in ("OK", "HEALTHY", "PASS", True), "T1.overall_ok", f"overall={v.get('overall')}")


def _secrets_block_case(fx_rel: str, expected_kind: str, tag_prefix: str) -> None:
    pd = _new_tmp_pack(tag_prefix)
    try:
        _copy_fx(fx_rel, pd)
        r = _run_tool(
            "inq_secrets.py",
            "--pack-dir", str(pd),
            "--task-id", f"TEST-{tag_prefix}",
            "--author", "NOTION_OPUS",
            "--stage", "H1_POST_ADMIT",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
        )
        v = r["verdict"]
        _assert(r["rc"] == 1, f"{tag_prefix}.rc", f"rc={r['rc']}")
        _assert(v.get("verdict") == "BLOCK_SECRETS", f"{tag_prefix}.verdict", f"verdict={v.get('verdict')}")
        kinds = {f.get("category", f.get("pattern", f.get("kind"))) for f in v.get("findings", [])}
        _assert(expected_kind in kinds, f"{tag_prefix}.kind", f"expected {expected_kind} in {sorted(kinds)}")
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T2_secrets_openai() -> None:
    _secrets_block_case("per_tool/05_secrets_openai_key.json", "openai_anthropic", "T2")


def T3_secrets_aws_compound() -> None:
    _secrets_block_case("per_tool/06_secrets_aws_session_token.json", "aws_access_keys", "T3")


def T4_secrets_entropy() -> None:
    _secrets_block_case("per_tool/07_secrets_entropy_only.json", "generic_high_entropy", "T4")


def T5_pi_ignore_previous() -> None:
    pd = _new_tmp_pack("T5")
    try:
        _copy_fx("base/03_pi_ignore_previous.json", pd)
        r = _run_tool(
            "inq_pi_scan.py",
            "--pack-dir", str(pd),
            "--task-id", "TEST-T5",
            "--author", "NOTION_OPUS",
            "--stage", "H1_POST_ADMIT",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
        )
        v = r["verdict"]
        _assert(r["rc"] == 1, "T5.rc", f"rc={r['rc']}")
        _assert(v.get("verdict") == "BLOCK_PI", "T5.verdict", f"verdict={v.get('verdict')}")
        kinds = {f.get("category") for f in v.get("findings", [])}
        _assert("ignore_directives" in kinds, "T5.kind", f"kinds={sorted(kinds)}")
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T6_trust_probe_ok() -> None:
    pd = _new_tmp_pack("T6")
    try:
        r = _run_tool(
            "inq_trust.py",
            "--pack-dir", str(pd),
            "--trust-file", str(TRUST_FILE),
            "--task-id", "TEST-T6",
            "--author", "NOTION_OPUS",
            "--stage", "H2_PRE_PERMIT",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
        )
        v = r["verdict"]
        _assert(
            r["rc"] in (0,) and v.get("verdict") in ("OK", "HINT_TRUST_LOW", "HINT_PROBATION"),
            "T6.verdict",
            f"verdict={v.get('verdict')} rc={r['rc']} stderr={r['stderr'][:160]}",
        )
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T7_ban_probe_ok() -> None:
    pd = _new_tmp_pack("T7")
    try:
        r = _run_tool(
            "inq_ban.py",
            "--pack-dir", str(pd),
            "--bans-file", str(BANS_FILE),
            "--task-id", "TEST-T7",
            "--author", "NOTION_OPUS",
            "--stage", "H2_PRE_PERMIT",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
        )
        v = r["verdict"]
        _assert(
            r["rc"] in (0,) and v.get("verdict") in ("OK", "BLOCK_BAN", "HINT_PROBATION"),
            "T7.verdict",
            f"verdict={v.get('verdict')} rc={r['rc']} stderr={r['stderr'][:160]}",
        )
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T8_redact_password() -> None:
    pd = _new_tmp_pack("T8")
    try:
        _copy_fx("per_tool/10_redact_password.json", pd)
        r = _run_tool(
            "inq_redact.py",
            "--pack-dir", str(pd),
            "--task-id", "TEST-T8",
            "--author", "NOTION_OPUS",
            "--stage", "H4_PRE_APPLY",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
        )
        v = r["verdict"]
        _assert(v.get("verdict") == "HINT_REDACT_TARGETS", "T8.verdict", f"verdict={v.get('verdict')}")
        _assert(len(v.get("findings", [])) >= 2, "T8.findings", f"findings={len(v.get('findings',[]))}")
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def _make_event(task_id: str, reason: str) -> Dict[str, Any]:
    return {
        "schema_version": "inq.verdict.v0_1",
        "verdict": "OK",
        "stage": "H6_ON_DEMAND",
        "tool": "inq_trust",
        "task_id": task_id,
        "author": "NOTION_OPUS",
        "issued_utc": "2026-06-20T00:00:00Z",
        "exit_code": 0,
        "findings": [],
        "reasons": [reason],
    }


def _find_audit_log(pd: Path) -> Optional[Path]:
    cands = list(pd.rglob("audit_*.jsonl"))
    return cands[0] if cands else None


def T9_audit_chain_immutable() -> None:
    pd = _new_tmp_pack("T9")
    try:
        ev1 = pd / "ev1.json"
        ev1.write_text(json.dumps(_make_event("T9-E1", "t9 entry 1")), encoding="utf-8")
        r1 = _run_tool(
            "inq_audit.py",
            "--pack-dir", str(pd),
            "--append", "--verdict", str(ev1),
            "--task-id", "T9-1",
            "--author", "OWNER_MANUAL",
            "--stage", "H5_POST_LAND",
            "--reports-dir", str(pd / "_R"),
        )
        _assert(r1["rc"] == 0, "T9.append1.rc", f"rc={r1['rc']} stderr={r1['stderr'][:200]}")

        ev2 = pd / "ev2.json"
        ev2.write_text(json.dumps(_make_event("T9-E2", "t9 entry 2")), encoding="utf-8")
        r2 = _run_tool(
            "inq_audit.py",
            "--pack-dir", str(pd),
            "--append", "--verdict", str(ev2),
            "--task-id", "T9-2",
            "--author", "OWNER_MANUAL",
            "--stage", "H5_POST_LAND",
            "--reports-dir", str(pd / "_R"),
        )
        _assert(r2["rc"] == 0, "T9.append2.rc", f"rc={r2['rc']}")

        audit_log = _find_audit_log(pd)
        _assert(audit_log is not None, "T9.audit_log_present", f"no audit_*.jsonl found under {pd}")
        if not audit_log:
            return

        r3 = _run_tool(
            "inq_audit.py",
            "--pack-dir", str(pd),
            "--verify-chain",
            "--task-id", "T9-V",
            "--author", "OWNER_MANUAL",
            "--stage", "H6_ON_DEMAND",
            "--reports-dir", str(pd / "_R"),
        )
        v3 = r3["verdict"]
        chain_clean_ok = (r3["rc"] == 0) and (
            v3.get("chain_ok") is True
            or v3.get("verdict") in ("OK",)
            or (isinstance(v3.get("chain"), dict) and v3["chain"].get("ok") is True)
        )
        _assert(chain_clean_ok, "T9.verify_clean", f"verdict={v3} rc={r3['rc']}")

        # tamper line 1
        lines = audit_log.read_text(encoding="utf-8").splitlines()
        if len(lines) >= 2:
            first = json.loads(lines[0])
            first["reasons"] = ["TAMPERED"]
            lines[0] = json.dumps(first, ensure_ascii=False)
            audit_log.write_text("\n".join(lines) + "\n", encoding="utf-8")
            r4 = _run_tool(
                "inq_audit.py",
                "--pack-dir", str(pd),
                "--verify-chain",
                "--task-id", "T9-T",
                "--author", "OWNER_MANUAL",
                "--stage", "H6_ON_DEMAND",
                "--reports-dir", str(pd / "_R"),
            )
            v4 = r4["verdict"]
            tampered_detected = (
                v4.get("chain_ok") is False
                or (isinstance(v4.get("chain"), dict) and v4["chain"].get("ok") is False)
                or v4.get("verdict") in ("BLOCK_AUDIT", "FAIL_CLOSED")
                or r4["rc"] != 0
            )
            _assert(tampered_detected, "T9.tamper_detected", f"verdict={v4} rc={r4['rc']}")
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T9b_audit_crlf_roundtrip() -> None:
    """Regression: a CRLF-line-ending audit log (Windows-flavour) MUST verify clean.

    Pre-fix, inq_audit wrote with text-mode 'a' (Windows -> CRLF on disk) but read
    chain via mixed binary/text paths, producing a chain-hash mismatch at line 2.
    This test hand-crafts a CRLF audit log with a correct chain and asserts that
    --verify-chain reports it intact regardless of host platform.
    """
    pd = _new_tmp_pack("T9b")
    try:
        audit_root = pd / "_INQUISITION" / "AUDIT"
        audit_root.mkdir(parents=True)
        log = audit_root / "audit_2026-06.jsonl"
        e1 = _make_event("T9b-E1", "crlf entry 1")
        e1["_chain_prev_sha256"] = "GENESIS"
        line1 = json.dumps(e1, ensure_ascii=False)
        import hashlib as _hl
        h1 = _hl.sha256(line1.encode("utf-8")).hexdigest()
        e2 = _make_event("T9b-E2", "crlf entry 2")
        e2["_chain_prev_sha256"] = h1
        line2 = json.dumps(e2, ensure_ascii=False)
        # Write with explicit CRLF endings to simulate Windows text-mode output.
        log.write_bytes(line1.encode("utf-8") + b"\r\n" + line2.encode("utf-8") + b"\r\n")

        r = _run_tool(
            "inq_audit.py",
            "--pack-dir", str(pd),
            "--audit-root", str(audit_root),
            "--verify-chain",
            "--task-id", "T9b-V",
            "--author", "OWNER_MANUAL",
            "--stage", "H6_ON_DEMAND",
            "--reports-dir", str(pd / "_R"),
        )
        v = r["verdict"]
        ok = (r["rc"] == 0) and (v.get("verdict") in ("OK", "NOOP"))
        findings = v.get("findings", []) or []
        first = findings[0] if findings else {}
        _assert(
            ok and first.get("ok") is True and first.get("lines_checked") == 2,
            "T9b.crlf_chain_intact",
            f"verdict={v.get('verdict')} rc={r['rc']} findings={findings}",
        )
    finally:
        shutil.rmtree(pd, ignore_errors=True)


def T10_force_inq_logged() -> None:
    pd = _new_tmp_pack("T10")
    try:
        _copy_fx("per_tool/05_secrets_openai_key.json", pd)
        r = _run_tool(
            "inq_secrets.py",
            "--pack-dir", str(pd),
            "--task-id", "TEST-T10",
            "--author", "OWNER_MANUAL",
            "--stage", "H1_POST_ADMIT",
            "--reports-dir", str(pd / "_R"),
            "--config-dir", str(CFG),
            "--force-inq",
        )
        v = r["verdict"]
        verdict = v.get("verdict", "")
        is_overridden = ("OVERRID" in verdict.upper()) or verdict.startswith("HINT_")
        _assert(is_overridden, "T10.overridden", f"verdict={verdict}")
        reasons_txt = " ".join(v.get("reasons", []))
        _assert("override" in reasons_txt.lower() or "force" in reasons_txt.lower(), "T10.reason_mentions_override", f"reasons={reasons_txt[:200]}")
    finally:
        shutil.rmtree(pd, ignore_errors=True)


TESTS = [
    ("T0", T0_runner_path_invariance),
    ("T1", T1_health_smoke),
    ("T2", T2_secrets_openai),
    ("T3", T3_secrets_aws_compound),
    ("T4", T4_secrets_entropy),
    ("T5", T5_pi_ignore_previous),
    ("T6", T6_trust_probe_ok),
    ("T7", T7_ban_probe_ok),
    ("T8", T8_redact_password),
    ("T9", T9_audit_chain_immutable),
    ("T9b", T9b_audit_crlf_roundtrip),
    ("T10", T10_force_inq_logged),
]


def main() -> int:
    _force_utf8()
    print(f"PACK_ROOT={ROOT}")
    print(f"PY={PY}")
    print(f"TOOLS={TOOLS}")
    for name, fn in TESTS:
        print(f"\n--- {name} ---")
        try:
            fn()
        except Exception as e:
            FAILS.append((name, f"EXCEPTION: {type(e).__name__}: {e}"))
            print(f"[FAIL] {name}: EXCEPTION: {type(e).__name__}: {e}")
    print("\n=== SUMMARY ===")
    if FAILS:
        print(f"FAILED: {len(FAILS)} assertion(s)")
        for tag, det in FAILS:
            print(f"  - {tag}: {det}")
        print(json.dumps({"schema_version": "inq.test_summary.v0_1", "suite": "test_inq_tools_e3", "passed": False, "failures": [{"tag": t, "detail": d} for t, d in FAILS]}, ensure_ascii=False))
        return 1
    print("ALL PASSED")
    print(json.dumps({"schema_version": "inq.test_summary.v0_1", "suite": "test_inq_tools_e3", "passed": True, "tests": len(TESTS)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
