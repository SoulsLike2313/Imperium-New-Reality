#!/usr/bin/env python3
"""Validate bounded PC->VM3 transfer route proof evidence and runner behavior."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE"
RUNNER_REL = f"{BASE_REL}/TOOLS/transfer_action_runner_v0_1.py"
VIEW_STATE_REL = f"{BASE_REL}/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
LEDGER_REL = f"{BASE_REL}/DATA/ledgers/transfer_action_runner_ledger.jsonl"

ROUTE_VERDICT = "PASS_FOR_ONE_CONFIRMED_BOUNDED_PC_TO_VM3_TRANSFER_ROUTE_ONLY"
ROUTE_ACTION = "SEND_TASKPACK_ZIP"
ROUTE_SOURCE = "PC"
ROUTE_TARGET = "VM3"
EVIDENCE_NAME = "PC_TO_VM3_DELIVERY_EVIDENCE.json"
FORBIDDEN_FIELDS = {"command", "shell", "exec", "powershell", "bash", "cmd", "arbitrary_command", "remote_command"}
REQUIRED_EVIDENCE_FIELDS = [
    "route",
    "task_id",
    "local_zip_sha256",
    "remote_zip_sha256",
    "remote_zip_size_bytes",
    "remote_zip_path",
    "remote_unpacked_path",
    "remote_host_alias",
    "remote_repo_path",
    "action_type",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_kv(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        line = line.strip()
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


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(payload, dict):
        return None, "not_json_object"
    return payload, None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for row in path.read_text(encoding="utf-8").splitlines():
        line = row.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    pass_detail: str,
    fail_detail: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": pass_detail})
        return
    checks.append({"check_id": check_id, "status": fail_level, "details": fail_detail})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_detail}")
    else:
        blockers.append(f"{check_id}:{fail_detail}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_output = default_report_dir / "transfer_route_proof_validator_report.json"
    default_evidence = (
        default_repo_root
        / "INBOX"
        / "VM3_TASKPACKS"
        / TASK_ID_DEFAULT
        / EVIDENCE_NAME
    )

    parser = argparse.ArgumentParser(description="Validate bounded PC->VM3 route proof.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--evidence-file", type=Path, default=default_evidence)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()
    evidence_path = args.evidence_file.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    required_files = [
        repo_root / RUNNER_REL,
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_request.schema.json",
        repo_root / f"{BASE_REL}/CONTRACTS/transfer_action_result.schema.json",
        repo_root / f"{BASE_REL}/TOOLS/smoke_transfer_action_runner_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "core_files_exist",
        all(path.exists() for path in required_files),
        "runner/contracts/ui files exist",
        "one or more required files are missing",
    )

    evidence, evidence_err = load_json(evidence_path)
    add_check(
        checks,
        warnings,
        blockers,
        "delivery_evidence_parse",
        evidence is not None,
        "delivery evidence parses",
        f"delivery evidence parse failed ({evidence_err})",
    )

    zip_path = Path("")
    unpacked_path = Path("")
    zip_hash = None
    zip_size = None

    if evidence is not None:
        missing_fields = [field for field in REQUIRED_EVIDENCE_FIELDS if field not in evidence]
        add_check(
            checks,
            warnings,
            blockers,
            "delivery_evidence_required_fields",
            len(missing_fields) == 0,
            "delivery evidence contains required fields",
            f"missing fields: {missing_fields}",
        )

        add_check(
            checks,
            warnings,
            blockers,
            "delivery_evidence_route",
            str(evidence.get("route", "")) == "PC_TO_VM3",
            "delivery evidence route is PC_TO_VM3",
            f"unexpected route: {evidence.get('route')}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "delivery_evidence_action",
            str(evidence.get("action_type", "")) == ROUTE_ACTION,
            "delivery evidence action is SEND_TASKPACK_ZIP",
            f"unexpected action_type: {evidence.get('action_type')}",
        )

        zip_path = Path(str(evidence.get("remote_zip_path", ""))).resolve()
        zip_exists = zip_path.exists() and zip_path.is_file()
        add_check(
            checks,
            warnings,
            blockers,
            "delivery_zip_exists",
            zip_exists,
            "delivery ZIP exists",
            f"delivery ZIP missing: {zip_path.as_posix()}",
        )

        if zip_exists:
            zip_hash = sha256_file(zip_path)
            zip_size = zip_path.stat().st_size

        expected_hash = str(evidence.get("remote_zip_sha256", "")).lower()
        add_check(
            checks,
            warnings,
            blockers,
            "delivery_zip_sha256_matches",
            bool(zip_hash) and zip_hash.lower() == expected_hash,
            "delivery ZIP sha256 matches evidence",
            f"zip hash mismatch actual={zip_hash} expected={expected_hash}",
        )

        expected_size = evidence.get("remote_zip_size_bytes")
        add_check(
            checks,
            warnings,
            blockers,
            "delivery_zip_size_matches",
            isinstance(expected_size, int) and zip_size == expected_size,
            "delivery ZIP size matches evidence",
            f"zip size mismatch actual={zip_size} expected={expected_size}",
        )

        unpacked_path = Path(str(evidence.get("remote_unpacked_path", ""))).resolve()
        if not unpacked_path.exists() or not unpacked_path.is_dir():
            derived_unpacked = (
                repo_root
                / "INBOX"
                / "VM3_TASKPACKS"
                / str(args.task_id)
                / f"TASKPACK_{args.task_id}"
            ).resolve()
            unpacked_ok = derived_unpacked.exists() and derived_unpacked.is_dir()
            add_check(
                checks,
                warnings,
                blockers,
                "unpacked_taskpack_exists",
                unpacked_ok,
                "unpacked taskpack exists (derived path)",
                f"unpacked taskpack missing: declared={unpacked_path.as_posix()} derived={derived_unpacked.as_posix()}",
                fail_level="WARN" if unpacked_ok else "BLOCK",
            )
            if unpacked_ok:
                unpacked_path = derived_unpacked
        else:
            add_check(
                checks,
                warnings,
                blockers,
                "unpacked_taskpack_exists",
                True,
                "unpacked taskpack exists",
                "unpacked taskpack missing",
            )

        add_check(
            checks,
            warnings,
            blockers,
            "remote_repo_path_matches",
            Path(str(evidence.get("remote_repo_path", ""))).resolve() == repo_root,
            "remote repo path matches current repo",
            f"remote repo path mismatch: {evidence.get('remote_repo_path')}",
        )

    report_dir.mkdir(parents=True, exist_ok=True)
    runner_report_path = report_dir / "transfer_route_proof_action_report.json"
    confirmed_cmd = [
        "python3",
        str(repo_root / RUNNER_REL),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--action-id",
        ROUTE_ACTION,
        "--mode",
        "DRY_RUN",
        "--route-proof-mode",
        "--delivery-evidence-file",
        str(evidence_path),
        "--report-dir",
        str(report_dir),
        "--output-report",
        str(runner_report_path),
    ]
    confirmed_run = run_cmd(confirmed_cmd, repo_root)
    confirmed_status = str(confirmed_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "runner_route_proof_confirmed",
        confirmed_run["returncode"] == 0 and confirmed_status == "PASS",
        "runner produced PASS for bounded route-proof",
        f"runner did not confirm route-proof returncode={confirmed_run['returncode']} status={confirmed_status}",
    )

    request_ref = str(confirmed_run.get("parsed", {}).get("transfer_action_request_ref", ""))
    result_ref = str(confirmed_run.get("parsed", {}).get("transfer_action_result_ref", ""))
    view_ref = str(confirmed_run.get("parsed", {}).get("transfer_console_view_state", VIEW_STATE_REL))

    request_payload, request_err = load_json(repo_root / request_ref) if request_ref else (None, "missing_ref")
    result_payload, result_err = load_json(repo_root / result_ref) if result_ref else (None, "missing_ref")
    view_payload, view_err = load_json(repo_root / view_ref)

    add_check(
        checks,
        warnings,
        blockers,
        "request_record_exists",
        request_payload is not None,
        "request record exists",
        f"request record missing/invalid ({request_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "result_record_exists",
        result_payload is not None,
        "result record exists",
        f"result record missing/invalid ({result_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "view_state_exists",
        view_payload is not None,
        "view state exists",
        f"view state missing/invalid ({view_err})",
    )

    if request_payload is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "request_action_allowlisted",
            str(request_payload.get("action_type", "")) == ROUTE_ACTION,
            "request action type is allowlisted",
            f"request action_type is not {ROUTE_ACTION}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "request_route_fixed_pc_to_vm3",
            str(request_payload.get("source_contour", "")) == ROUTE_SOURCE
            and str(request_payload.get("target_contour", "")) == ROUTE_TARGET,
            "request route fixed to PC -> VM3",
            f"request route mismatch: {request_payload.get('source_contour')}->{request_payload.get('target_contour')}",
        )
        request_forbidden = sorted(field for field in request_payload if field in FORBIDDEN_FIELDS)
        add_check(
            checks,
            warnings,
            blockers,
            "request_no_arbitrary_shell_fields",
            len(request_forbidden) == 0,
            "request has no arbitrary shell fields",
            f"forbidden fields in request: {request_forbidden}",
        )

    if result_payload is not None:
        result_forbidden = sorted(field for field in result_payload if field in FORBIDDEN_FIELDS)
        add_check(
            checks,
            warnings,
            blockers,
            "result_no_arbitrary_shell_fields",
            len(result_forbidden) == 0,
            "result has no arbitrary shell fields",
            f"forbidden fields in result: {result_forbidden}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "result_status_confirmed",
            str(result_payload.get("status", "")) == "CONFIRMED",
            "result status is CONFIRMED",
            f"result status is not CONFIRMED: {result_payload.get('status')}",
        )

        refs = result_payload.get("evidence_refs", [])
        refs_list = refs if isinstance(refs, list) else []
        add_check(
            checks,
            warnings,
            blockers,
            "result_has_evidence_refs",
            len(refs_list) >= 3,
            "result contains evidence refs",
            f"result evidence refs too small: {len(refs_list)}",
        )

        expected_ref_fragments = [
            str(evidence_path).replace(str(repo_root) + "/", ""),
            zip_path.as_posix() if zip_path else "",
            unpacked_path.as_posix() if unpacked_path else "",
        ]
        joined_refs = "\n".join(str(item) for item in refs_list)
        all_refs_present = all(fragment and fragment in joined_refs for fragment in expected_ref_fragments)
        add_check(
            checks,
            warnings,
            blockers,
            "result_evidence_refs_resolve",
            all_refs_present,
            "result evidence refs include evidence file, ZIP, and unpacked path",
            "result evidence refs do not include all required proof paths",
        )

        limitations = result_payload.get("limitations", [])
        limitation_list = limitations if isinstance(limitations, list) else []
        verdict_present = any(str(item) == f"verdict:{ROUTE_VERDICT}" for item in limitation_list)
        add_check(
            checks,
            warnings,
            blockers,
            "result_contains_route_verdict",
            verdict_present,
            "result limitations contain route verdict marker",
            f"result limitations missing verdict marker for {ROUTE_VERDICT}",
        )

        sha = result_payload.get("sha256_before_after", {})
        before_hash = str(sha.get("before", "")) if isinstance(sha, dict) else ""
        after_hash = str(sha.get("after", "")) if isinstance(sha, dict) else ""
        add_check(
            checks,
            warnings,
            blockers,
            "result_sha_before_after_matches_zip",
            bool(zip_hash) and before_hash == zip_hash and after_hash == zip_hash,
            "result before/after sha256 matches delivered ZIP hash",
            f"sha mismatch before={before_hash} after={after_hash} expected={zip_hash}",
        )

    ledger_rows = load_jsonl(repo_root / LEDGER_REL)
    ledger_match = any(
        str(item.get("request_ref", "")) == request_ref
        and str(item.get("result_ref", "")) == result_ref
        and str(item.get("action_id", "")) == ROUTE_ACTION
        and str(item.get("result_status", "")) == "CONFIRMED"
        for item in ledger_rows
    )
    add_check(
        checks,
        warnings,
        blockers,
        "ledger_record_exists",
        ledger_match,
        "ledger contains CONFIRMED route-proof entry",
        "ledger missing CONFIRMED route-proof entry",
    )

    if view_payload is not None:
        runner_state = view_payload.get("action_runner_state", {}) if isinstance(view_payload, dict) else {}
        last_action = runner_state.get("last_action", {}) if isinstance(runner_state, dict) else {}

        add_check(
            checks,
            warnings,
            blockers,
            "view_state_route_proof_status",
            str(last_action.get("route_proof_status", "")) == "CONFIRMED",
            "view state exposes route_proof_status=CONFIRMED",
            f"view state route_proof_status is {last_action.get('route_proof_status')}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "view_state_route_proof_verdict",
            str(last_action.get("route_proof_verdict", "")) == ROUTE_VERDICT,
            "view state exposes bounded route-proof verdict",
            f"view state verdict mismatch: {last_action.get('route_proof_verdict')}",
        )

        contours = view_payload.get("contour_cards", []) if isinstance(view_payload, dict) else []
        contour_map = {
            str(item.get("contour_id", "")): str(item.get("status", ""))
            for item in contours
            if isinstance(item, dict)
        }
        add_check(
            checks,
            warnings,
            blockers,
            "view_state_vm2_not_claimed",
            contour_map.get("VM2") in {"NOT_PROVEN", "UNKNOWN", "OFFLINE", "NOT_CONFIGURED"},
            "VM2 is not claimed as proven",
            f"VM2 status unexpectedly claimed: {contour_map.get('VM2')}",
        )

        routes = view_payload.get("transfer_routes", []) if isinstance(view_payload, dict) else []
        route_ok = any(
            isinstance(item, dict)
            and str(item.get("route_id", "")) == "PC_TO_VM3"
            and str(item.get("route_status", "")) == "CONFIRMED"
            for item in routes
        )
        add_check(
            checks,
            warnings,
            blockers,
            "view_state_route_card_confirmed",
            route_ok,
            "view state contains confirmed PC_TO_VM3 route card",
            "view state missing confirmed PC_TO_VM3 route card",
        )

    invalid_route_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            ROUTE_ACTION,
            "--source-contour",
            "VM2",
            "--target-contour",
            ROUTE_TARGET,
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
        ],
        repo_root,
    )
    invalid_route_status = str(invalid_route_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "reject_vm2_route_in_route_proof_mode",
        invalid_route_run["returncode"] != 0 and invalid_route_status == "BLOCK",
        "runner rejects VM2 route in route-proof mode",
        f"VM2 route not rejected returncode={invalid_route_run['returncode']} status={invalid_route_status}",
    )

    invalid_action_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            "DRY_RUN_TRANSFER",
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
        ],
        repo_root,
    )
    invalid_action_status = str(invalid_action_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "reject_non_allowlisted_action_in_route_proof_mode",
        invalid_action_run["returncode"] != 0 and invalid_action_status == "BLOCK",
        "runner rejects non-allowlisted action in route-proof mode",
        f"non-allowlisted action not rejected returncode={invalid_action_run['returncode']} status={invalid_action_status}",
    )

    forbidden_request_path = report_dir / "validator_forbidden_field_request.json"
    forbidden_request_payload = {
        "schema_id": "TRANSFER_ACTION_REQUEST_V0_1",
        "request_id": "VALIDATOR-FORBIDDEN-FIELD",
        "task_id": str(args.task_id),
        "action_type": ROUTE_ACTION,
        "source_contour": ROUTE_SOURCE,
        "target_contour": ROUTE_TARGET,
        "artifact_type": "taskpack_zip",
        "artifact_name": f"TASKPACK_{args.task_id}.zip",
        "source_path": f"INBOX/VM3_TASKPACKS/{args.task_id}/TASKPACK_{args.task_id}.zip",
        "target_path": f"/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM3_TASKPACKS/{args.task_id}/TASKPACK_{args.task_id}.zip",
        "mode": "DRY_RUN",
        "owner_approval_required": True,
        "owner_approved": False,
        "rollback_plan": "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK/ACTION_ROLLBACK_POLICY_V0_1.json",
        "allowed_command_profile": "DRY_RUN_ONLY",
        "created_at_utc": utc_now(),
        "status": "REQUESTED",
        "claim_boundary": "FOUNDATION_ONLY",
        "route_proof_mode": True,
        "delivery_evidence_file": str(evidence_path),
        "cmd": "echo forbidden",
    }
    forbidden_request_path.write_text(
        json.dumps(forbidden_request_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    forbidden_field_run = run_cmd(
        [
            "python3",
            str(repo_root / RUNNER_REL),
            "--repo-root",
            str(repo_root),
            "--task-id",
            str(args.task_id),
            "--action-id",
            ROUTE_ACTION,
            "--request-file",
            str(forbidden_request_path),
            "--route-proof-mode",
            "--delivery-evidence-file",
            str(evidence_path),
            "--report-dir",
            str(report_dir),
        ],
        repo_root,
    )
    forbidden_status = str(forbidden_field_run.get("parsed", {}).get("transfer_action_runner_status", ""))
    add_check(
        checks,
        warnings,
        blockers,
        "reject_arbitrary_shell_fields",
        forbidden_field_run["returncode"] != 0 and forbidden_status == "BLOCK",
        "runner rejects request with arbitrary shell field",
        f"forbidden field request not rejected returncode={forbidden_field_run['returncode']} status={forbidden_status}",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "TRANSFER_ROUTE_PROOF_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "allowed_final_verdict": ROUTE_VERDICT,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "runner_runs": {
            "confirmed": confirmed_run,
            "invalid_route": invalid_route_run,
            "invalid_action": invalid_action_run,
            "forbidden_field": forbidden_field_run,
        },
        "refs": {
            "request_ref": request_ref,
            "result_ref": result_ref,
            "view_ref": view_ref,
            "evidence_file": evidence_path.as_posix(),
        },
        "claim_boundary": "FOUNDATION_ONLY",
        "not_proven": [
            "VM2 transfer route proof",
            "VM3 to PC report fetch proof",
            "production remote orchestration",
            "arbitrary shell execution",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"transfer_route_proof_validator_verdict={verdict}")
    print(f"transfer_route_proof_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
