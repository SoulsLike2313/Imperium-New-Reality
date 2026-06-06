#!/usr/bin/env python3
"""Smoke-check bidirectional VM2<->VM3 bounded route-proof flow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-BIDIRECTIONAL-ROUTE-PROOF-VM2-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
REPORT_DIR_REL = f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
SUMMARY_REL = f"{REPORT_DIR_REL}/bidirectional_route_probe_report.json"
OUTPUT_REL = f"{REPORT_DIR_REL}/bidirectional_route_proof_smoke_report.json"
BUILDER_REL = f"{BASE_REL}/TOOLS/build_bidirectional_route_proof_vm2_vm3_v0_1.py"
VALIDATOR_REL = f"{BASE_REL}/TOOLS/validate_bidirectional_route_proof_vm2_vm3_v0_1.py"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in stdout.splitlines():
        line = raw.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_cmd(cmd: list[str], repo_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "parsed": parse_kv(proc.stdout.strip()),
    }


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def add_step(
    steps: list[dict[str, Any]],
    warnings: list[str],
    blockers: list[str],
    step: str,
    ok: bool,
    details: Any,
    fail_id: str,
    warn: bool = False,
) -> None:
    if ok:
        steps.append({"step": step, "status": "PASS", "details": details})
        return

    status = "WARN" if warn else "BLOCK"
    steps.append({"step": step, "status": status, "details": details})
    if warn:
        warnings.append(fail_id)
    else:
        blockers.append(fail_id)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]

    parser = argparse.ArgumentParser(description="Smoke-check bidirectional VM2/VM3 route-proof flow.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_repo_root / REPORT_DIR_REL)
    parser.add_argument("--summary", type=Path, default=default_repo_root / SUMMARY_REL)
    parser.add_argument("--output", type=Path, default=default_repo_root / OUTPUT_REL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    summary_path = args.summary.resolve()
    output_path = args.output.resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    build_run = run_cmd(
        [
            "python3",
            str(repo_root / BUILDER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--report-dir",
            str(report_dir),
            "--output-report",
            str(summary_path),
        ],
        repo_root,
    )
    builder_verdict = str(build_run.get("parsed", {}).get("bidirectional_builder_verdict", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "builder_completed",
        build_run["returncode"] == 0 and builder_verdict in {"PASS", "WARN"},
        build_run,
        "builder_failed",
    )

    validator_path = report_dir / "bidirectional_route_proof_validator_report.json"
    validate_run = run_cmd(
        [
            "python3",
            str(repo_root / VALIDATOR_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--summary",
            str(summary_path),
            "--output",
            str(validator_path),
        ],
        repo_root,
    )
    validator_verdict = str(validate_run.get("parsed", {}).get("bidirectional_route_proof_validator_verdict", ""))
    add_step(
        steps,
        warnings,
        blockers,
        "validator_completed",
        validate_run["returncode"] == 0 and validator_verdict in {"PASS", "WARN"},
        validate_run,
        "validator_failed",
    )

    summary = load_json(summary_path)
    add_step(
        steps,
        warnings,
        blockers,
        "summary_present_after_build",
        summary is not None,
        {"summary_path": summary_path.as_posix()},
        "summary_missing_after_build",
    )

    if summary is not None:
        routes = summary.get("routes", [])
        route_map: dict[str, str] = {}
        if isinstance(routes, list):
            for item in routes:
                if isinstance(item, dict):
                    route_map[str(item.get("route", ""))] = str(item.get("status", ""))

        vm2_to_vm3 = route_map.get("VM2_TO_VM3", "UNKNOWN")
        vm3_to_vm2 = route_map.get("VM3_TO_VM2", "UNKNOWN")

        add_step(
            steps,
            warnings,
            blockers,
            "vm2_to_vm3_proved",
            vm2_to_vm3 == "PROVED",
            {"VM2_TO_VM3": vm2_to_vm3},
            "vm2_to_vm3_not_proved",
            warn=vm2_to_vm3 not in {"UNKNOWN", ""},
        )
        add_step(
            steps,
            warnings,
            blockers,
            "vm3_to_vm2_proved",
            vm3_to_vm2 == "PROVED",
            {"VM3_TO_VM2": vm3_to_vm2},
            "vm3_to_vm2_not_proved",
            warn=vm3_to_vm2 not in {"UNKNOWN", ""},
        )

        both_proved = vm2_to_vm3 == "PROVED" and vm3_to_vm2 == "PROVED"
        expected_full_claim = "PASS_FOR_TWO_CONFIRMED_BOUNDED_VM2_VM3_TRANSFER_ROUTES_ONLY"
        claim = str(summary.get("verdict_claim", ""))

        add_step(
            steps,
            warnings,
            blockers,
            "verdict_claim_honest",
            (both_proved and claim == expected_full_claim)
            or ((not both_proved) and claim in {"WARN_PARTIAL_BIDIRECTIONAL_ROUTE_PROOF", "BLOCK_ROUTE_PROOF_FAILED"}),
            {"claim": claim, "both_proved": both_proved},
            "verdict_claim_not_honest",
            warn=not both_proved,
        )

        add_step(
            steps,
            warnings,
            blockers,
            "no_fake_green_when_partial",
            both_proved or validator_verdict == "WARN",
            {"both_proved": both_proved, "validator_verdict": validator_verdict},
            "partial_state_not_reflected_as_warn",
            warn=not both_proved,
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "BIDIRECTIONAL_ROUTE_PROOF_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "allowed_final_verdict": "PASS/WARN/BLOCK_FOR_SCOPED_VM2_VM3_BOUNDED_ROUTE_PROOF_ONLY",
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "runner_runs": {
            "builder": build_run,
            "validator": validate_run,
        },
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "production orchestration",
            "arbitrary remote shell",
            "global all-contour transfer readiness",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"bidirectional_route_proof_smoke_verdict={verdict}")
    print(f"bidirectional_route_proof_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
