#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ORGANS = [
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "DOCTRINARIUM",
    "MECHANICUS",
    "INQUISITION",
    "CUSTODES",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "OFFICIO_AGENTIS",
    "THRONE",
]

MECHANICUS_PREFLIGHT = Path("ORGANS/MECHANICUS/VALIDATORS/validate_patch_pack_technical_preflight.py")
INQUISITION_SCOPE = Path("ORGANS/INQUISITION/VALIDATORS/validate_patch_pack_scope_fake_green.py")
ASTRONOMICON_SMOKE = Path("ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py")

OPERATOR_RECEIPT_DIR = Path("SUPPORT/LAUNCHER/RECEIPTS")
OPERATOR_REPORT_DIR = Path("SUPPORT/LAUNCHER/REPORTS")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_") or "UNKNOWN"

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def run_py(repo: Path, script: Path, args: List[str]) -> Tuple[int, str, str]:
    if not (repo / script).is_file():
        return 2, "", f"missing script: {script.as_posix()}"
    p = subprocess.run([sys.executable, str(repo / script)] + args, cwd=str(repo), capture_output=True, text=True, timeout=240)
    return p.returncode, p.stdout, p.stderr

def print_status(repo: Path):
    print("IMPERIUM TERMINAL LAUNCHER V0.2")
    print(f"Repo: {repo}")
    print(f"HEAD: {git_head(repo)}")
    receipt = load_json(repo / "ORGANS/THRONE/RECEIPTS/organ_assembly_stage_scoring_receipt.json")
    if receipt:
        s = receipt.get("scores", {})
        print("Stage scoring:")
        for k in ["profile_baseline_score","duty_defined_score","assembly_target_defined_score","organ_truth_maturity_score","organ_assembled_score","red_team_score","blue_team_score"]:
            print(f"  {k}: {s.get(k)}")
    else:
        print("Stage scoring receipt: missing")

def print_organs(repo: Path):
    summary = load_json(repo / "ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.json")
    scores: Dict[str, Any] = {}
    if summary:
        for row in summary.get("organs", []):
            scores[row.get("organ_id")] = row
    print("ORGANS")
    for o in ORGANS:
        row = scores.get(o, {})
        print(f"- {o}: maturity={row.get('organ_truth_maturity_score','?')} assembled={row.get('stage_scores',{}).get('organ_assembled_score','?')}")

def organ_view(repo: Path, organ: str, mode: str):
    organ = organ.upper().replace("-", "_")
    if organ not in ORGANS:
        print(f"Unknown organ: {organ}", file=sys.stderr)
        sys.exit(2)
    root = repo / "ORGANS" / organ
    print(f"ORGAN {organ}")
    print(f"path: {root}")
    if mode == "status":
        for rel in ["CONTRACTS/ORGAN_DUTY_CONTRACT_V0_1.json","ASSEMBLY/ORGAN_ASSEMBLY_TARGET_V0_1.json"]:
            print(f"{rel}: {'OK' if (root/rel).is_file() else 'MISSING'}")
    elif mode == "assembly":
        data = load_json(root / "ASSEMBLY/ORGAN_ASSEMBLY_TARGET_V0_1.json")
        if not data:
            print("assembly target missing")
            return
        for k, v in data.get("assembly_gates", {}).items():
            print(f"- {k}: {v.get('proof_state')}")
    elif mode == "receipts":
        d = root / "RECEIPTS"
        if not d.is_dir():
            print("receipts dir missing")
            return
        for f in sorted(d.glob("*.json"))[-20:]:
            print(f"- {f.relative_to(repo)}")
    else:
        print(f"Unknown organ mode: {mode}", file=sys.stderr)
        sys.exit(2)

def patch_list(repo: Path):
    d = repo / "WARP/PATCHES"
    print("PATCHES")
    if not d.is_dir():
        return
    for p in sorted([x for x in d.iterdir() if x.is_dir()])[-80:]:
        print(f"- {p.name}")

def patch_inspect(repo: Path, patch_id: str):
    d = repo / "WARP/PATCHES" / patch_id
    if not d.is_dir():
        print(f"Patch not found: {patch_id}", file=sys.stderr)
        sys.exit(2)
    print(f"PATCH {patch_id}")
    for rel in ["PATCH_PACK.md","PATCH_PACK_MANIFEST_V0_1.json","PATCH_FILE_MANIFEST_SHA256.json"]:
        if (d / rel).exists():
            print(f"- {rel}")
    for r in sorted(d.glob("RUN_*.ps1")):
        print(f"- {r.name}")
    pp = d / "PATCH_PACK.md"
    if pp.exists():
        print("\n--- PATCH_PACK.md head ---")
        print("\n".join(pp.read_text(encoding="utf-8", errors="replace").splitlines()[:80]))

def intake_dry_run(repo: Path, text: str, task_id: str | None):
    tool = repo / "ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py"
    if not tool.is_file():
        print("Astronomicon dry-run tool missing", file=sys.stderr)
        sys.exit(2)
    cmd = [sys.executable, str(tool), "--repo-root", str(repo), "--text", text]
    if task_id:
        cmd += ["--task-id", task_id]
    p = subprocess.run(cmd, text=True)
    sys.exit(p.returncode)

def patch_preflight(repo: Path, patch_id: str) -> int:
    code, out, err = run_py(repo, MECHANICUS_PREFLIGHT, ["--repo-root", str(repo), "--patch-id", patch_id])
    if out:
        print(out.rstrip())
    if err:
        print(err.rstrip(), file=sys.stderr)
    return code

def patch_scope(repo: Path, patch_id: str) -> int:
    code, out, err = run_py(repo, INQUISITION_SCOPE, ["--repo-root", str(repo), "--patch-id", patch_id])
    if out:
        print(out.rstrip())
    if err:
        print(err.rstrip(), file=sys.stderr)
    return code

def patch_smoke(repo: Path, patch_id: str | None = None, out_name: str | None = None) -> int:
    if out_name is None:
        out_name = f"ORGANS/ASTRONOMICON/REPORTS/OPERATOR_PATCH_SMOKE_{safe_name(patch_id or 'ALL')}.json"
    args = ["--repo-root", str(repo), "--out", out_name]
    if patch_id:
        args += ["--patch-id", patch_id]
    code, out, err = run_py(repo, ASTRONOMICON_SMOKE, args)
    if out:
        print(out.rstrip())
    if err:
        print(err.rstrip(), file=sys.stderr)
    return code

def summarize_smoke(repo: Path, mode: str = "summary") -> int:
    candidates = [
        repo / "ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_LIFECYCLE_SMOKE_ALL_SUMMARY_V0_1.json",
        repo / "ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_SMOKE_VALIDATION_SUMMARY_V0_1.json",
    ]
    data = None
    path = None
    for c in candidates:
        if c.is_file():
            data = load_json(c)
            path = c
            break
    if not data:
        print("No smoke summary found. Run: patch smoke-all", file=sys.stderr)
        return 2
    results = data.get("results", [])
    if mode == "partial":
        results = [r for r in results if r.get("smoke_verdict") != "CLOSED_BY_DECLARED_GOALS"]
    elif mode == "closed":
        results = [r for r in results if r.get("smoke_verdict") == "CLOSED_BY_DECLARED_GOALS"]
    print(f"Smoke summary: {path.relative_to(repo)}")
    print(f"patch_count: {data.get('patch_count')}")
    counts: Dict[str, int] = {}
    for r in data.get("results", []):
        counts[r.get("smoke_verdict", "UNKNOWN")] = counts.get(r.get("smoke_verdict", "UNKNOWN"), 0) + 1
    for k in sorted(counts):
        print(f"{k}: {counts[k]}")
    print("")
    for r in results[:120]:
        print(f"{r.get('patch_id')}: {r.get('smoke_verdict')} / {r.get('evidence_level')}")
    return 0

def patch_lifecycle(repo: Path, patch_id: str | None, all_mode: bool = False) -> int:
    generated = utc()
    target = patch_id if patch_id else "ALL"
    safe = safe_name(target)

    if all_mode:
        pre_args = ["--repo-root", str(repo), "--all"]
        scope_args = ["--repo-root", str(repo), "--all"]
        smoke_out = f"SUPPORT/LAUNCHER/REPORTS/PATCH_LIFECYCLE_OPERATOR_SMOKE_ALL.json"
        smoke_args = ["--repo-root", str(repo), "--out", smoke_out]
    else:
        pre_args = ["--repo-root", str(repo), "--patch-id", patch_id]
        scope_args = ["--repo-root", str(repo), "--patch-id", patch_id]
        smoke_out = f"SUPPORT/LAUNCHER/REPORTS/PATCH_LIFECYCLE_OPERATOR_SMOKE_{safe}.json"
        smoke_args = ["--repo-root", str(repo), "--patch-id", patch_id, "--out", smoke_out]

    pre_code, pre_out, pre_err = run_py(repo, MECHANICUS_PREFLIGHT, pre_args)
    scope_code, scope_out, scope_err = run_py(repo, INQUISITION_SCOPE, scope_args)
    smoke_code, smoke_out_text, smoke_err = run_py(repo, ASTRONOMICON_SMOKE, smoke_args)

    pre_receipt = load_json(repo / "ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json") or {}
    scope_receipt = load_json(repo / "ORGANS/INQUISITION/RECEIPTS/patch_pack_scope_fake_green_receipt.json") or {}
    smoke_summary = load_json(repo / smoke_out) or {}

    operator_state = "PASS_OPERATOR_LIFECYCLE_FOUNDATION" if pre_code == 0 and scope_code == 0 and smoke_code == 0 else "FAIL_OPERATOR_LIFECYCLE_FOUNDATION"
    receipt = {
        "receipt_id": "receipt.support_launcher.patch_lifecycle_operator.v0_1",
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "target_patch_id": patch_id,
        "all_mode": all_mode,
        "operator_state": operator_state,
        "pre_work": {
            "mechanicus_exit_code": pre_code,
            "mechanicus_verdict": pre_receipt.get("verdict"),
            "mechanicus_error_count": pre_receipt.get("error_count"),
        },
        "scope_gate": {
            "inquisition_exit_code": scope_code,
            "inquisition_verdict": scope_receipt.get("verdict"),
            "inquisition_error_count": scope_receipt.get("error_count"),
        },
        "post_work_smoke": {
            "astronomicon_exit_code": smoke_code,
            "smoke_patch_count": smoke_summary.get("patch_count"),
            "smoke_summary": smoke_out,
        },
        "not_claimed": [
            "patch execution",
            "Custodes trust",
            "Throne verdict",
            "full red/blue proof",
        ],
        "stdout_tail": {
            "mechanicus": pre_out[-3000:],
            "inquisition": scope_out[-3000:],
            "smoke": smoke_out_text[-3000:],
        },
        "stderr_tail": {
            "mechanicus": pre_err[-1000:],
            "inquisition": scope_err[-1000:],
            "smoke": smoke_err[-1000:],
        }
    }

    receipt_path = repo / OPERATOR_RECEIPT_DIR / f"PATCH_LIFECYCLE_OPERATOR_RECEIPT_{safe}.json"
    report_path = repo / OPERATOR_REPORT_DIR / f"PATCH_LIFECYCLE_OPERATOR_REPORT_{safe}.md"
    write_json(receipt_path, receipt)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(f"""# PATCH LIFECYCLE OPERATOR REPORT V0.1

target_patch_id: `{target}`  
operator_state: `{operator_state}`  
generated_at_utc: `{generated}`

## Before work

- Mechanicus: `{pre_receipt.get('verdict')}` exit `{pre_code}`
- Inquisition: `{scope_receipt.get('verdict')}` exit `{scope_code}`

## After work smoke

- Astronomicon smoke exit: `{smoke_code}`
- Smoke patch count: `{smoke_summary.get('patch_count')}`
- Smoke summary: `{smoke_out}`

## Not claimed

- patch execution
- Custodes trust
- Throne verdict
- full red/blue proof
""", encoding="utf-8")

    print(json.dumps({
        "operator_state": operator_state,
        "target_patch_id": patch_id,
        "all_mode": all_mode,
        "mechanicus": pre_receipt.get("verdict"),
        "inquisition": scope_receipt.get("verdict"),
        "smoke_patch_count": smoke_summary.get("patch_count"),
        "receipt": str(receipt_path.relative_to(repo)).replace("\\", "/"),
        "report": str(report_path.relative_to(repo)).replace("\\", "/"),
    }, ensure_ascii=False, indent=2))
    return 0 if operator_state.startswith("PASS") else 1

def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--repo-root", default=".")
    ns, rest = ap.parse_known_args()
    repo = Path(ns.repo_root).resolve()

    if not rest or rest[0] in ["help", "-h", "--help"]:
        print("Commands:")
        print("  status | organs")
        print("  organ <id> status|assembly|receipts")
        print("  patch list|inspect <id>")
        print("  patch preflight <id>")
        print("  patch scope <id>")
        print("  patch smoke <id>")
        print("  patch smoke-all|smoke-summary|smoke-partial|smoke-closed")
        print("  patch lifecycle <id>")
        print("  patch lifecycle-all")
        print("  intake dry-run <text> [--task-id ID]")
        return 0

    if rest[0] == "status":
        print_status(repo)
        return 0
    if rest[0] == "organs":
        print_organs(repo)
        return 0
    if rest[0] == "organ" and len(rest) >= 3:
        organ_view(repo, rest[1], rest[2])
        return 0
    if rest[0] == "patch" and len(rest) >= 2:
        cmd = rest[1]
        if cmd == "list":
            patch_list(repo)
            return 0
        if cmd == "inspect" and len(rest) >= 3:
            patch_inspect(repo, rest[2])
            return 0
        if cmd == "preflight" and len(rest) >= 3:
            return patch_preflight(repo, rest[2])
        if cmd in ["scope", "fakegreen", "fake-green"] and len(rest) >= 3:
            return patch_scope(repo, rest[2])
        if cmd == "smoke" and len(rest) >= 3:
            return patch_smoke(repo, rest[2])
        if cmd == "smoke-all":
            return patch_smoke(repo, None, "ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_OPERATOR_SMOKE_ALL_V0_1.json")
        if cmd == "smoke-summary":
            return summarize_smoke(repo, "summary")
        if cmd == "smoke-partial":
            return summarize_smoke(repo, "partial")
        if cmd == "smoke-closed":
            return summarize_smoke(repo, "closed")
        if cmd == "lifecycle" and len(rest) >= 3:
            return patch_lifecycle(repo, rest[2], all_mode=False)
        if cmd == "lifecycle-all":
            return patch_lifecycle(repo, None, all_mode=True)
        if cmd in ["run", "apply"]:
            print("Forbidden in launcher v0.2: patch execution is not implemented.", file=sys.stderr)
            return 2

    if rest[0] == "intake" and len(rest) >= 3 and rest[1] == "dry-run":
        text = rest[2]
        task_id = None
        if "--task-id" in rest:
            i = rest.index("--task-id")
            if i + 1 < len(rest):
                task_id = rest[i + 1]
        intake_dry_run(repo, text, task_id)
        return 0

    print("Unknown command. Run: help", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
