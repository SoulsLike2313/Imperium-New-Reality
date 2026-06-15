#!/usr/bin/env python3
"""Astronomicon Taskpack Registration Skill v0.1."""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    tools_dir = Path(__file__).resolve().parents[2] / "TOOLS"
    if str(tools_dir) not in sys.path:
        sys.path.append(str(tools_dir))

from astronomicon_task_entry_lib_v0_1 import register_taskpack, resolve_task_id, utc_now, write_json  # noqa: E402

STEP_NAME = "ASTRONOMICON TASKPACK REGISTRATION SKILL TUI CONTOUR ROUTER AND VM LAUNCH CARD"
PASS_ADMISSION = {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS"}
PASS_RESOLVER = {"PASS", "PASS_WITH_WARNINGS"}
VALID_CONTOURS = {"PC", "VM3", "VM2"}


def normalize_path(path_value: str | Path, base: Path | None = None) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    if base is not None:
        return (base / path).resolve()
    return path.resolve()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(args: list[str], *, cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def load_taskpack_manifest(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        candidates = [name for name in zf.namelist() if name.replace("\\", "/").endswith("/MANIFEST.json")]
        if "MANIFEST.json" in zf.namelist():
            candidates.insert(0, "MANIFEST.json")
        if not candidates:
            raise ValueError("MANIFEST.json not found in ZIP.")
        for member in candidates:
            try:
                payload = json.loads(zf.read(member).decode("utf-8"))
            except Exception:
                continue
            if isinstance(payload, dict) and str(payload.get("task_id", "")).strip():
                return payload
        raise ValueError("MANIFEST.json found, but no valid task_id present.")


def build_launch_card(task_id: str, registered_task_path: str, taskpack_path: str) -> str:
    lines = [
        "IMPERIUM TASK LAUNCH CARD",
        "",
        "STEP:",
        STEP_NAME,
        "",
        "TASK_ID:",
        task_id,
        "",
        "REGISTERED TASK PATH:",
        registered_task_path,
        "",
        "TASKPACK:",
        taskpack_path,
        "",
        "CHAT MESSAGE TO SERVITOR:",
        "start task",
        "",
        "COPY ONLY THIS INTO SERVITOR CHAT:",
        "start task",
    ]
    return "\n".join(lines)


def default_route_config_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json"
    )


def load_route_config(route_config_path: Path) -> dict[str, Any]:
    if not route_config_path.exists():
        return {}
    payload = load_json(route_config_path)
    if not isinstance(payload, dict):
        return {}
    return payload


def read_remote_json(ssh_alias: str, remote_path: str) -> tuple[dict[str, Any] | None, str]:
    rc, stdout, stderr = run_cmd(["ssh", ssh_alias, f"cat {shlex.quote(remote_path)}"])
    if rc != 0:
        return None, f"Cannot read remote JSON {remote_path}: {stderr or stdout}"
    try:
        payload = json.loads(stdout)
    except Exception as exc:
        return None, f"Remote JSON decode failed for {remote_path}: {exc}"
    if not isinstance(payload, dict):
        return None, f"Remote JSON root is not an object: {remote_path}"
    return payload, ""


def shell_q(value: str) -> str:
    return shlex.quote(value)


def print_launch_card(card_text: str) -> None:
    print("")
    print("=" * 60)
    print(card_text)
    print("=" * 60)


def pc_registration(repo_root: Path, zip_path: Path, *, print_card: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    intake = register_taskpack(repo_root=repo_root, source_zip_path=zip_path, actor=Path(__file__).name)
    task_id = str(intake.get("task_id", "")).strip()

    if intake.get("admission_verdict") in PASS_ADMISSION and task_id:
        resolver = resolve_task_id(
            repo_root=repo_root,
            task_id=task_id,
            actor=Path(__file__).name,
            write_receipt=True,
        )
    else:
        resolver = {
            "timestamp_utc": utc_now(),
            "task_id": task_id,
            "resolver_verdict": "BLOCK",
            "caps_triggered": ["CAP_REGISTERED_TASK_NOT_RESOLVABLE"],
            "warnings": ["Resolver not executed because admission failed."],
        }

    registered_path = str(intake.get("registered_task_path", ""))
    taskpack_path = str(intake.get("source_zip_path", str(zip_path).replace("\\", "/")))
    launch_card = build_launch_card(task_id or "UNKNOWN_TASK_ID", registered_path or "N/A", taskpack_path)

    launch_state = "LOCAL_PRINTED"
    terminal_opened_or_explained = True
    if print_card:
        print_launch_card(launch_card)

    admission_ok = intake.get("admission_verdict") in PASS_ADMISSION
    resolver_ok = resolver.get("resolver_verdict") in PASS_RESOLVER
    if admission_ok and resolver_ok:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "BLOCK"

    contour_receipt = {
        "timestamp_utc": utc_now(),
        "contour": "PC",
        "task_id": task_id,
        "zip_path": str(zip_path).replace("\\", "/"),
        "route_mode": "LIVE",
        "intake_verdict": intake.get("admission_verdict", "ADMISSION_BLOCK"),
        "resolver_verdict": resolver.get("resolver_verdict", "BLOCK"),
        "launch_card_state": launch_state,
        "verdict": verdict,
        "registered_task_path": registered_path,
        "taskpack_path": taskpack_path,
        "intake_receipt": intake,
        "resolver_receipt": resolver,
        "launch_card": launch_card,
    }
    vm_launch_card_receipt = {
        "timestamp_utc": utc_now(),
        "contour": "PC",
        "task_id": task_id,
        "terminal_attempted": True,
        "terminal_opened_or_explained": terminal_opened_or_explained,
        "copy_message": "start task",
        "verdict": verdict,
        "launch_card_state": launch_state,
    }
    return contour_receipt, vm_launch_card_receipt


def remote_registration(
    contour: str,
    repo_root: Path,
    zip_path: Path,
    *,
    route_config: dict[str, Any],
    live_remote: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_taskpack_manifest(zip_path)
    task_id = str(manifest.get("task_id", "")).strip()
    task_title = str(manifest.get("task_title", STEP_NAME)).strip() or STEP_NAME

    contours = route_config.get("contours", {}) if isinstance(route_config, dict) else {}
    contour_cfg = contours.get(contour) if isinstance(contours, dict) else None
    notes: list[str] = []

    if not isinstance(contour_cfg, dict) or not contour_cfg.get("enabled", False):
        notes.append("Route missing or disabled in contour config.")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "ROUTE_MISSING",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "WARN_ROUTE_MISSING",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "WARN_ROUTE_MISSING",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    ssh_alias = str(contour_cfg.get("ssh_alias", "")).strip()
    remote_repo_root = str(contour_cfg.get("remote_repo_root", "")).strip()
    remote_python = str(contour_cfg.get("remote_python", "python3")).strip() or "python3"
    remote_inbox_dir = str(contour_cfg.get("remote_inbox_dir", "")).strip()
    terminal_launch_command = str(contour_cfg.get("terminal_launch_command", "")).strip()

    if not ssh_alias or not remote_repo_root or not remote_inbox_dir:
        notes.append("Route config is present but missing required fields.")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_CONFIG_INVALID",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_CONFIG_INVALID",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    remote_zip_path = f"{remote_inbox_dir.rstrip('/')}/{zip_path.name}"
    intake_receipt_path = f"{remote_inbox_dir.rstrip('/')}/astronomicon_{contour.lower()}_intake_receipt.json"
    resolver_receipt_path = f"{remote_inbox_dir.rstrip('/')}/astronomicon_{contour.lower()}_resolver_receipt.json"

    if not live_remote:
        preview = {
            "copy_zip": f"scp {zip_path} {ssh_alias}:{remote_zip_path}",
            "intake": (
                f"ssh {ssh_alias} \"cd {remote_repo_root} && {remote_python} "
                "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py "
                f"--repo-root . --zip-path {remote_zip_path} --receipt-out {intake_receipt_path}\""
            ),
            "resolver": (
                f"ssh {ssh_alias} \"cd {remote_repo_root} && {remote_python} "
                "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py "
                f"--repo-root . --task-id {task_id} --receipt-out {resolver_receipt_path}\""
            ),
        }
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "DRY_RUN",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "WARN_DRY_RUN_ONLY",
            "command_preview": preview,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "WARN_DRY_RUN_ONLY",
            "warnings": ["Route available in config but executed in dry-run mode."],
        }
        return contour_receipt, vm_receipt

    if shutil.which("ssh") is None or shutil.which("scp") is None:
        notes.append("ssh/scp executables are not available on this machine.")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_REMOTE_TOOLING_MISSING",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_REMOTE_TOOLING_MISSING",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    status_cmd = f"cd {shell_q(remote_repo_root)} && git status --porcelain"
    rc, stdout, stderr = run_cmd(["ssh", ssh_alias, status_cmd])
    if rc != 0:
        notes.append(f"Remote git status failed: {stderr or stdout}")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_REMOTE_STATUS_FAILED",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_REMOTE_STATUS_FAILED",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt
    if stdout.strip():
        notes.append("Remote worktree is dirty; refusing remote sync and registration.")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_REMOTE_DIRTY_WORKTREE",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_REMOTE_DIRTY_WORKTREE",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    sync_cmd = f"cd {shell_q(remote_repo_root)} && git fetch origin && git checkout master && git pull --ff-only origin master"
    rc, stdout, stderr = run_cmd(["ssh", ssh_alias, sync_cmd])
    if rc != 0:
        notes.append(f"Remote sync failed: {stderr or stdout}")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_REMOTE_SYNC_FAILED",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_REMOTE_SYNC_FAILED",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    rc, stdout, stderr = run_cmd(["scp", str(zip_path), f"{ssh_alias}:{remote_zip_path}"])
    if rc != 0:
        notes.append(f"SCP transfer failed: {stderr or stdout}")
        contour_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "zip_path": str(zip_path).replace("\\", "/"),
            "route_mode": "BLOCKED",
            "intake_verdict": "NOT_RUN",
            "resolver_verdict": "NOT_RUN",
            "launch_card_state": "LIMITATION_RECEIPT",
            "verdict": "BLOCK_REMOTE_TRANSFER_FAILED",
            "warnings": notes,
        }
        vm_receipt = {
            "timestamp_utc": utc_now(),
            "contour": contour,
            "task_id": task_id,
            "terminal_attempted": False,
            "terminal_opened_or_explained": True,
            "copy_message": "start task",
            "verdict": "BLOCK_REMOTE_TRANSFER_FAILED",
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    intake_cmd = (
        f"cd {shell_q(remote_repo_root)} && "
        f"{shell_q(remote_python)} "
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py "
        f"--repo-root . --zip-path {shell_q(remote_zip_path)} --receipt-out {shell_q(intake_receipt_path)}"
    )
    run_cmd(["ssh", ssh_alias, intake_cmd])
    intake_payload, intake_err = read_remote_json(ssh_alias, intake_receipt_path)
    if intake_payload is None:
        notes.append(intake_err)
        intake_payload = {"admission_verdict": "ADMISSION_BLOCK"}

    resolver_cmd = (
        f"cd {shell_q(remote_repo_root)} && "
        f"{shell_q(remote_python)} "
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py "
        f"--repo-root . --task-id {shell_q(task_id)} --receipt-out {shell_q(resolver_receipt_path)}"
    )
    run_cmd(["ssh", ssh_alias, resolver_cmd])
    resolver_payload, resolver_err = read_remote_json(ssh_alias, resolver_receipt_path)
    if resolver_payload is None:
        notes.append(resolver_err)
        resolver_payload = {"resolver_verdict": "BLOCK"}

    intake_verdict = str(intake_payload.get("admission_verdict", "ADMISSION_BLOCK"))
    resolver_verdict = str(resolver_payload.get("resolver_verdict", "BLOCK"))
    remote_registered_path = str(intake_payload.get("registered_task_path", f"{remote_repo_root}/TASK_INBOX/REGISTERED"))
    launch_card = build_launch_card(task_id, remote_registered_path, remote_zip_path).replace(STEP_NAME, task_title)

    terminal_attempted = False
    terminal_opened_or_explained = True
    launch_state = "LIMITATION_RECEIPT"
    if terminal_launch_command:
        expanded = terminal_launch_command
        expanded = expanded.replace("{TASK_ID}", task_id)
        expanded = expanded.replace("{START_MESSAGE}", "start task")
        expanded = expanded.replace("{STEP_NAME}", STEP_NAME)
        expanded = expanded.replace("{REGISTERED_TASK_PATH}", remote_registered_path)
        expanded = expanded.replace("{TASKPACK_PATH}", remote_zip_path)
        terminal_attempted = True
        rc, stdout, stderr = run_cmd(["ssh", ssh_alias, expanded])
        if rc == 0:
            launch_state = "TERMINAL_OPENED"
            terminal_opened_or_explained = True
        else:
            notes.append(f"Terminal launch command failed: {stderr or stdout}")
            terminal_opened_or_explained = True
            launch_state = "LIMITATION_RECEIPT"

    admission_ok = intake_verdict in PASS_ADMISSION
    resolver_ok = resolver_verdict in PASS_RESOLVER
    if admission_ok and resolver_ok:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "BLOCK"

    contour_receipt = {
        "timestamp_utc": utc_now(),
        "contour": contour,
        "task_id": task_id,
        "zip_path": str(zip_path).replace("\\", "/"),
        "route_mode": "LIVE",
        "intake_verdict": intake_verdict,
        "resolver_verdict": resolver_verdict,
        "launch_card_state": launch_state,
        "verdict": verdict,
        "warnings": notes,
        "remote_zip_path": remote_zip_path,
        "remote_repo_root": remote_repo_root,
        "remote_intake_receipt_path": intake_receipt_path,
        "remote_resolver_receipt_path": resolver_receipt_path,
        "intake_receipt": intake_payload,
        "resolver_receipt": resolver_payload,
        "launch_card": launch_card,
    }
    vm_receipt = {
        "timestamp_utc": utc_now(),
        "contour": contour,
        "task_id": task_id,
        "terminal_attempted": terminal_attempted,
        "terminal_opened_or_explained": terminal_opened_or_explained,
        "copy_message": "start task",
        "verdict": verdict,
        "launch_card_state": launch_state,
        "warnings": notes,
    }
    return contour_receipt, vm_receipt


def execute_registration(
    *,
    repo_root: Path,
    zip_path: Path,
    contour: str,
    route_config_path: Path,
    live_remote: bool,
    print_card: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contour_upper = contour.upper()
    if contour_upper not in VALID_CONTOURS:
        raise ValueError(f"Unsupported contour: {contour}")
    if contour_upper == "PC":
        return pc_registration(repo_root, zip_path, print_card=print_card)
    route_config = load_route_config(route_config_path)
    return remote_registration(
        contour_upper,
        repo_root,
        zip_path,
        route_config=route_config,
        live_remote=live_remote,
    )


def interactive_loop(repo_root: Path) -> int:
    while True:
        print("")
        print("== ASTRONOMICON TASKPACK REGISTRATION SKILL V0.1 ==")
        print("1) Register on PC")
        print("2) Register on VM3")
        print("3) Register on VM2")
        print("4) Exit")
        choice = input("Select: ").strip()
        if choice == "4":
            return 0
        if choice not in {"1", "2", "3"}:
            print("Unknown option.")
            continue
        zip_input = input("Taskpack ZIP path: ").strip()
        if not zip_input:
            print("ZIP path is required.")
            continue
        contour = {"1": "PC", "2": "VM3", "3": "VM2"}[choice]
        live_remote = False
        if contour in {"VM3", "VM2"}:
            live_answer = input("Execute remote route live? (yes/no): ").strip().lower()
            live_remote = live_answer in {"y", "yes"}
        route_config_path = default_route_config_path(repo_root)
        contour_receipt, vm_receipt = execute_registration(
            repo_root=repo_root,
            zip_path=normalize_path(zip_input, repo_root),
            contour=contour,
            route_config_path=route_config_path,
            live_remote=live_remote,
            print_card=True,
        )
        print("")
        print(json.dumps(contour_receipt, ensure_ascii=False, indent=2))
        print(json.dumps(vm_receipt, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Astronomicon Taskpack Registration Skill v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--zip-path", default="", help="Taskpack ZIP path.")
    parser.add_argument("--contour", default="PC", help="Target contour: PC | VM3 | VM2")
    parser.add_argument("--route-config", default="", help="Route config JSON path.")
    parser.add_argument("--live-remote", action="store_true", help="Execute VM route live.")
    parser.add_argument("--interactive", action="store_true", help="Run interactive menu.")
    parser.add_argument("--contour-receipt-out", default="", help="Write contour receipt JSON.")
    parser.add_argument("--vm-launch-card-receipt-out", default="", help="Write launch-card receipt JSON.")
    parser.add_argument("--print-launch-card", action="store_true", help="Print launch card in direct mode.")
    args = parser.parse_args()

    repo_root = normalize_path(args.repo_root)
    if args.interactive or not args.zip_path:
        return interactive_loop(repo_root)

    zip_path = normalize_path(args.zip_path, repo_root)
    route_config_path = (
        normalize_path(args.route_config, repo_root)
        if args.route_config
        else default_route_config_path(repo_root)
    )
    contour_receipt, vm_receipt = execute_registration(
        repo_root=repo_root,
        zip_path=zip_path,
        contour=args.contour,
        route_config_path=route_config_path,
        live_remote=args.live_remote,
        print_card=args.print_launch_card,
    )

    if args.contour_receipt_out:
        write_json(normalize_path(args.contour_receipt_out, repo_root), contour_receipt)
    if args.vm_launch_card_receipt_out:
        write_json(normalize_path(args.vm_launch_card_receipt_out, repo_root), vm_receipt)

    print(json.dumps(contour_receipt, ensure_ascii=False, indent=2))
    if contour_receipt.get("verdict") in {"PASS", "PASS_WITH_WARNINGS", "WARN_DRY_RUN_ONLY", "WARN_ROUTE_MISSING"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
