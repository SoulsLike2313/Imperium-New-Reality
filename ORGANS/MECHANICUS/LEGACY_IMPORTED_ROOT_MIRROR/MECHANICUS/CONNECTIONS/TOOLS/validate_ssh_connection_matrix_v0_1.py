#!/usr/bin/env python3
"""Validate Mechanicus SSH connection matrix foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-MECHANICUS-SSH-MATRIX-AND-ACTION-ROLLBACK-CONTRACT-VM2-V0_1"
MATRIX_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.json"
MATRIX_DIR_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS"

REQUIRED_CONNECTION_IDS = {
    "PC_LOCAL_REPO",
    "VM2_SSH_LOOPBACK_ALIAS",
    "VM3_SSH_ALIAS",
    "THRONE_CORE_FUTURE_CONTOUR",
}

FORBIDDEN_KEY_MARKERS = [
    "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
    "-----BEGIN " + "RSA PRIVATE KEY-----",
    "-----BEGIN " + "PRIVATE KEY-----",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = (
        default_repo_root
        / "IMPERIUM_NEW_GENERATION/REPORTS"
        / TASK_ID_DEFAULT
    )

    parser = argparse.ArgumentParser(description="Validate SSH connection matrix artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "SSH_MATRIX_VALIDATOR_REPORT.json")
    return parser.parse_args()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(payload, dict):
        return None, "not_json_object"
    return payload, None


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    ok_details: str,
    fail_details: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": ok_details})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": fail_details})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_details}")
    else:
        blockers.append(f"{check_id}:{fail_details}")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_path = args.output.resolve()
    task_id = str(args.task_id)

    matrix_dir = repo_root / MATRIX_DIR_REL
    matrix_path = repo_root / MATRIX_REL

    required_paths = [
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.md",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_CONNECTION_MATRIX_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SSH_ALIAS_POLICY_V0_1.md",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/COMMAND_SHORTCUTS_CATALOG_V0_1.md",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SCHEMAS/ssh_connection_matrix_v0_1.schema.json",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/SAMPLES/ssh_connection_matrix_sample_v0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/TOOLS/validate_ssh_connection_matrix_v0_1.py",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    add_check(
        checks,
        warnings,
        blockers,
        "matrix_files_exist",
        all(path.exists() for path in required_paths),
        "matrix foundation files exist",
        "one or more matrix foundation files are missing",
    )

    matrix, matrix_err = load_json(matrix_path)
    add_check(
        checks,
        warnings,
        blockers,
        "matrix_json_parse",
        matrix is not None,
        "matrix json parses",
        f"matrix json parse failed ({matrix_err})",
    )

    connections: list[dict[str, Any]] = []
    if matrix is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "schema_id_ok",
            matrix.get("schema_id") == "SSH_CONNECTION_MATRIX_V0_1",
            "schema id is SSH_CONNECTION_MATRIX_V0_1",
            "schema id mismatch",
        )

        add_check(
            checks,
            warnings,
            blockers,
            "private_key_material_disallowed",
            matrix.get("private_key_material_allowed_in_repo") is False,
            "private key material is explicitly disallowed",
            "private_key_material_allowed_in_repo is not false",
        )

        raw_connections = matrix.get("connections", [])
        if isinstance(raw_connections, list):
            connections = [item for item in raw_connections if isinstance(item, dict)]

        connection_ids = {str(item.get("connection_id")) for item in connections}
        missing_ids = sorted(REQUIRED_CONNECTION_IDS - connection_ids)
        add_check(
            checks,
            warnings,
            blockers,
            "required_connection_ids",
            not missing_ids,
            "all required connection ids are present",
            f"missing required connection ids: {missing_ids}",
        )

        by_id = {str(item.get("connection_id")): item for item in connections}

        vm2 = by_id.get("VM2_SSH_LOOPBACK_ALIAS", {})
        vm2_ok = (
            vm2.get("alias") == "imperium-vm2"
            and vm2.get("route") == "127.0.0.1:2223"
            and vm2.get("user") == "vboxuser2"
            and vm2.get("repo_path") == "/home/vboxuser2/IMPERIUM_WORK/Imperium-"
        )
        add_check(
            checks,
            warnings,
            blockers,
            "vm2_required_route_fields",
            vm2_ok,
            "vm2 alias, route, user, repo path match required values",
            "vm2 alias/route/user/repo_path mismatch",
        )

        vm2_key_ref = str(vm2.get("key_reference_path", ""))
        add_check(
            checks,
            warnings,
            blockers,
            "vm2_key_reference_path",
            vm2_key_ref == "%USERPROFILE%\\.ssh\\imperium_pc_to_vm2_ed25519_20260418",
            "vm2 key reference path is the expected local reference",
            "vm2 key reference path missing or mismatched",
        )

        vm3 = by_id.get("VM3_SSH_ALIAS", {})
        vm3_ok = (
            vm3.get("alias") == "imperium-vm3"
            and vm3.get("status") == "REGISTERED_OFFLINE_NOT_VERIFIED"
            and vm3.get("repo_path") == "/home/vboxuser3/IMPERIUM_WORK/Imperium-"
        )
        add_check(
            checks,
            warnings,
            blockers,
            "vm3_offline_registration",
            vm3_ok,
            "vm3 is registered as offline/not verified",
            "vm3 registration does not match required offline status",
        )

        throne = by_id.get("THRONE_CORE_FUTURE_CONTOUR", {})
        throne_ok = throne.get("status") == "OFFLINE_OR_NOT_CONFIGURED"
        add_check(
            checks,
            warnings,
            blockers,
            "throne_placeholder_registration",
            throne_ok,
            "throne/core placeholder is registered as offline or not configured",
            "throne/core placeholder status mismatch",
        )

        offline_ids = ["VM3_SSH_ALIAS", "THRONE_CORE_FUTURE_CONTOUR"]
        offline_marked_live = [
            cid
            for cid in offline_ids
            if by_id.get(cid, {}).get("live_verified") is True
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "offline_not_marked_live",
            not offline_marked_live,
            "offline contours are not marked live",
            f"offline contours marked live: {offline_marked_live}",
        )

    marker_hits: list[str] = []
    for path in matrix_dir.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for marker in FORBIDDEN_KEY_MARKERS:
            if marker in text:
                marker_hits.append(f"{path.relative_to(repo_root).as_posix()}::{marker}")

    add_check(
        checks,
        warnings,
        blockers,
        "no_private_key_markers",
        not marker_hits,
        "no private key markers detected under connections folder",
        f"private key markers detected: {marker_hits}",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "SSH_MATRIX_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "matrix_json": MATRIX_REL,
            "matrix_dir": MATRIX_DIR_REL,
        },
        "no_fake_green_note": "PASS means documentation matrix safety checks passed; live connectivity is not claimed.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"ssh_matrix_validator_verdict={verdict}")
    print(f"ssh_matrix_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
