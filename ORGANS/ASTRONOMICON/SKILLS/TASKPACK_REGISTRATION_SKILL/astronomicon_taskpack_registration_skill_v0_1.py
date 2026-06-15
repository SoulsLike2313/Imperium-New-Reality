#!/usr/bin/env python3
"""Astronomicon Taskpack Registration Skill v0.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import tempfile
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
CURRENT_ROUTE_CONFIG_REL = "ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json"
LEGACY_ROUTE_CONFIG_REL = (
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json"
)
ROOT_MARKERS = ("AGENTS.md", "ORGANS/ASTRONOMICON", "ORGANS/ASTRONOMICON/TOOLS")


def normalize_path(path_value: str | Path, base: Path | None = None) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    if base is not None:
        return (base / path).resolve()
    return path.resolve()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def run_cmd(args: list[str], *, cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def is_repo_root(candidate: Path) -> bool:
    return all((candidate / marker).exists() for marker in ROOT_MARKERS[:2])


def walk_up_repo_root(start: Path) -> tuple[Path | None, list[str]]:
    searched: list[str] = []
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        searched.append(str(candidate).replace("\\", "/"))
        if is_repo_root(candidate):
            return candidate, searched
    return None, searched


def resolve_repo_root(repo_root_arg: str | Path | None = None) -> tuple[Path, dict[str, Any]]:
    searched: list[str] = []
    if repo_root_arg:
        explicit = normalize_path(repo_root_arg)
        searched.append(str(explicit).replace("\\", "/"))
        if is_repo_root(explicit):
            return explicit, {
                "repo_root_source": "explicit_arg",
                "searched_paths": searched,
                "warnings": [],
            }
        raise ValueError("Explicit --repo-root is not a New Reality root. Searched: " + ", ".join(searched))

    rc, stdout, _stderr = run_cmd(["git", "rev-parse", "--show-toplevel"])
    if rc == 0 and stdout:
        git_root = normalize_path(stdout)
        searched.append(str(git_root).replace("\\", "/"))
        if is_repo_root(git_root):
            return git_root, {
                "repo_root_source": "git_rev_parse",
                "searched_paths": searched,
                "warnings": [],
            }

    script_root, script_searched = walk_up_repo_root(Path(__file__).resolve())
    searched.extend(script_searched)
    if script_root is not None:
        return script_root, {
            "repo_root_source": "script_walk_up",
            "searched_paths": searched,
            "warnings": [],
        }

    raise ValueError("Cannot resolve New Reality repo root. Searched: " + ", ".join(searched))


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
    return repo_root / CURRENT_ROUTE_CONFIG_REL


def legacy_route_config_path(repo_root: Path) -> Path:
    return repo_root / LEGACY_ROUTE_CONFIG_REL


def discover_route_config(repo_root: Path, explicit_route_config: str | Path | None = None) -> dict[str, Any]:
    warnings: list[str] = []
    searched: list[str] = []
    env_path = os.environ.get("ASTRONOMICON_ROUTE_CONFIG", "").strip()
    candidates: list[tuple[str, Path]] = []
    if explicit_route_config:
        candidates.append(("explicit_arg", normalize_path(explicit_route_config, repo_root)))
    if env_path:
        candidates.append(("env_ASTRONOMICON_ROUTE_CONFIG", normalize_path(env_path, repo_root)))
    candidates.append(("current_root_operator_config", default_route_config_path(repo_root)))
    candidates.append(("legacy_old_prefix_fallback", legacy_route_config_path(repo_root)))

    for source, path in candidates:
        searched.append(str(path).replace("\\", "/"))
        if path.exists():
            if source == "legacy_old_prefix_fallback":
                warnings.append("LEGACY_ROUTE_CONFIG_PATH_WARN: old-prefix route config was selected as fallback.")
            return {
                "route_config_path": str(path).replace("\\", "/"),
                "route_config_source": source,
                "route_config_exists": True,
                "route_config_sha256": compute_sha256(path),
                "searched_paths": searched,
                "warnings": warnings,
            }

    return {
        "route_config_path": str(default_route_config_path(repo_root)).replace("\\", "/"),
        "route_config_source": "missing_default_current_root",
        "route_config_exists": False,
        "route_config_sha256": "",
        "searched_paths": searched,
        "warnings": warnings + ["Route config missing; PC contour does not require it."],
    }


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


def ascii_safe(value: str) -> str:
    return value.encode("ascii", "ignore").decode("ascii").strip()


def slugify(value: str, fallback: str = "HANDY-MANUAL-PATCH") -> str:
    safe = ascii_safe(value).upper()
    safe = re.sub(r"[^A-Z0-9]+", "-", safe).strip("-")
    safe = re.sub(r"-+", "-", safe)
    return safe or fallback


def split_csv_lines(value: str) -> list[str]:
    items: list[str] = []
    for part in re.split(r"[,;\n]+", value or ""):
        item = part.strip().replace("\\", "/")
        if item:
            items.append(item)
    return items


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_handy_taskpack(
    *,
    repo_root: Path,
    title: str,
    intent: str,
    h_repo_root: str,
    files_to_read: list[str],
    files_to_patch: list[str],
    output_zip: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    title_ascii = ascii_safe(title) or "Imperium H manual patch"
    intent_ascii = ascii_safe(intent) or "Manual chat-driven patch in Imperium H contour."
    stem = slugify(title_ascii)
    task_id = f"H-TASK-NEWREALITY-{stem}-PC-V0_1"
    h_repo = ascii_safe(h_repo_root) or "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H"
    if output_zip:
        zip_path = normalize_path(output_zip, repo_root)
    else:
        downloads = Path.home() / "Downloads"
        zip_path = downloads / f"{task_id}.zip"

    created_at = utc_now()
    manifest = {
        "schema_version": "astronomicon.taskpack.v0_1",
        "taskpack_id": task_id,
        "task_id": task_id,
        "title": title_ascii,
        "task_class": "HANDY_IMPERIUM_H",
        "created_from_contour": "PC",
        "target_contour": "IMPERIUM_H",
        "execution_mode": "MANUAL_CHAT_PATCH_ZIP",
        "author_identity": "IMPERIUM_H <imperium_h@local>",
        "base_repo_expected": h_repo,
        "merge_policy": "OWNER_ACCEPTANCE_THEN_CHERRY_PICK_TO_MAIN",
        "patch_delivery": "ZIP_WITH_APPLY_AND_ROLLBACK",
        "manual_test_required": True,
        "commit_policy": "PATCH_DOES_NOT_COMMIT; OWNER_COMMITS_IN_H_AFTER_MANUAL_ACCEPTANCE",
        "created_at_utc": created_at,
        "intent": intent_ascii,
        "files_to_read": files_to_read,
        "files_to_patch": files_to_patch,
        "allowed_write_scope": files_to_patch or ["ORGANS/IMPERIAL_IDE/**"],
        "forbidden_actions": [
            "direct_mainline_mutation",
            "auto_commit",
            "auto_push",
            "delete_without_owner_approval",
            "enable_real_servitor_execution",
            "enable_live_llm_backend",
            "enable_unsafe_shell",
            "remote_vm_route",
        ],
    }

    required_organs = [
        "DOCTRINARIUM",
        "OFFICIO_AGENTIS",
        "ASTRONOMICON",
        "ADMINISTRATUM",
        "MECHANICUS",
        "INQUISITION",
        "STRATEGIUM",
        "SCHOLA_IMPERIALIS",
    ]
    organ_route = {
        "DOCTRINARIUM": "manual task doctrine, candidate/canon vocabulary, and no-overclaim rules",
        "OFFICIO_AGENTIS": "owner-facing handoff text and H workflow summaries",
        "ASTRONOMICON": "local PC admission, route receipt, and launch card evidence",
        "ADMINISTRATUM": "manual patch evidence, receipts, and continuity ledger",
        "MECHANICUS": "patch scope, validators, and no unsafe execution policy",
        "INQUISITION": "manual acceptance gate, no fake-green closure, and rollback proof",
        "STRATEGIUM": "operator workflow and next patch plan",
        "SCHOLA_IMPERIALIS": "operator training notes and H workflow lessons",
    }
    language_policy = {
        "taskpack_internal_files": "ENGLISH_UTF8_NO_BOM_NO_CYRILLIC",
        "canonical_repo_artifacts": "ENGLISH_UTF8_NO_BOM",
        "owner_facing_russian_runtime_output": {
            "allowed": True,
            "language": "RUSSIAN",
            "encoding": "UTF8_NO_BOM",
            "authority": "OFFICIO_AGENTIS",
            "required_route": "OFFICIO_AGENTIS_OWNER_FACING_FINAL_RESPONSE",
            "allowed_files": [
                "README_RU.md",
                "REPORTS/<task_id>/FINAL_OWNER_SUMMARY_RU.md",
            ],
            "not_allowed_in_taskpack_root_files": True,
        },
        "cyrillic_in_taskpack": {
            "allowed": False,
            "scope": "MANIFEST.json, TASK_SPEC.md, ACCEPTANCE_GATES.md, OUTPUT_REQUIREMENTS.md, TASK_ROUTE_MANIFEST_TEMPLATE.json, TASK_START_ACK_TEMPLATE.json, README.md",
            "owner_facing_russian_runtime_exception": {
                "allowed": True,
                "authority": "OFFICIO_AGENTIS",
                "scope": "runtime owner-facing files only",
            },
        },
        "localization_exception": {
            "allowed": True,
            "authority": "OFFICIO_AGENTIS",
            "scope": "owner-facing runtime files only after Officio role entry",
            "allowed_language": "RUSSIAN",
            "allowed_encoding": "UTF8_NO_BOM",
            "forbidden_scope": "taskpack internal root files",
        },
    }
    manifest["organs"] = required_organs
    manifest["required_organs"] = required_organs
    manifest["organ_route"] = organ_route
    manifest["route_manifest_template"] = "TASK_ROUTE_MANIFEST_TEMPLATE.json"
    manifest["task_start_ack_template"] = "TASK_START_ACK_TEMPLATE.json"
    manifest["language_and_encoding_policy"] = language_policy

    task_spec = f"""# TASK SPEC\n\n## Task ID\n\n{task_id}\n\n## Class\n\nHANDY_IMPERIUM_H manual chat-driven patch task.\n\n## Title\n\n{title_ascii}\n\n## Intent\n\n{intent_ascii}\n\n## Target\n\nWork only in Imperium H contour: {h_repo}\n\n## Workflow\n\n1. Gather evidence ZIP from the H contour.\n2. Review files in chat.\n3. Produce PATCH-H ZIP with APPLY_PATCH.ps1 and ROLLBACK_PATCH.ps1.\n4. Apply patch in H contour only.\n5. Owner manually tests.\n6. If accepted, Owner commits with IMPERIUM_H author identity.\n7. Mainline receives the work only by reviewed cherry-pick.\n\n## Files to read\n\n{chr(10).join('- ' + x for x in files_to_read) if files_to_read else '- To be declared in evidence ZIP.'}\n\n## Files to patch\n\n{chr(10).join('- ' + x for x in files_to_patch) if files_to_patch else '- To be declared before patching.'}\n"""
    acceptance = """# ACCEPTANCE GATES\n\n- H repo author is IMPERIUM_H <imperium_h@local>.\n- Patch is delivered as ZIP.\n- APPLY_PATCH.ps1 checks it is running inside an _H repo.\n- Patch does not commit automatically.\n- Rollback path exists.\n- Owner manually verifies the result.\n- Only accepted changes may be committed in H.\n- Mainline receives changes only by reviewed cherry-pick.\n- No real execution, live LLM, unsafe shell, VM route, or destructive cleanup is enabled.\n"""
    output_requirements = """# OUTPUT REQUIREMENTS\n\nExpected chat-side artifact:\n\n- PATCH-H-*.zip\n- PATCH_MANIFEST.json\n- README_RU.md\n- APPLY_PATCH.ps1\n- ROLLBACK_PATCH.ps1\n- PATCH_FILES/\n\nExpected H-side verification:\n\n- git diff --stat\n- manual TUI/GUI smoke as appropriate\n- optional H commit by Owner after acceptance\n"""
    route_template = {
        "schema_version": "astronomicon.task_route_manifest_template.v0_1",
        "task_id": task_id,
        "route_mode": "HANDY_MANUAL_CHAT_PATCH_ZIP",
        "target_contour": "IMPERIUM_H",
        "base_repo_expected": h_repo,
        "organs": required_organs,
        "required_organs": required_organs,
        "organ_route": organ_route,
        "files_to_read": files_to_read,
        "files_to_patch": files_to_patch,
        "allowed_write_scope": manifest["allowed_write_scope"],
        "forbidden_actions": manifest["forbidden_actions"],
        "language_and_encoding_policy": language_policy,
        "merge_policy": "OWNER_ACCEPTANCE_THEN_CHERRY_PICK_TO_MAIN",
    }
    start_ack = {
        "schema_version": "astronomicon.task_start_ack_template.v0_1",
        "task_id": task_id,
        "copy_message_to_chat": "start H task",
        "required_ack_fields": [
            "task_id",
            "h_repo_root",
            "h_branch",
            "git_author",
            "files_to_read",
            "files_to_patch",
            "patch_zip_expected",
            "rollback_plan",
            "manual_test_plan",
        ],
    }

    with tempfile.TemporaryDirectory(prefix="imperium_h_taskpack_") as tmp_name:
        tmp = Path(tmp_name)
        write_text(tmp / "MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        write_text(tmp / "TASK_SPEC.md", task_spec)
        write_text(tmp / "ACCEPTANCE_GATES.md", acceptance)
        write_text(tmp / "OUTPUT_REQUIREMENTS.md", output_requirements)
        write_text(tmp / "TASK_ROUTE_MANIFEST_TEMPLATE.json", json.dumps(route_template, ensure_ascii=False, indent=2) + "\n")
        write_text(tmp / "TASK_START_ACK_TEMPLATE.json", json.dumps(start_ack, ensure_ascii=False, indent=2) + "\n")
        write_text(tmp / "README.md", "Imperium H handy taskpack for manual chat-driven patch workflow.\n")
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in tmp.rglob("*"):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(tmp).as_posix())
    manifest["zip_path"] = str(zip_path).replace("\\", "/")
    manifest["zip_sha256"] = compute_sha256(zip_path)
    return zip_path, manifest


def handy_registration_interactive(repo_root: Path) -> None:
    print("")
    print("== IMPERIUM_H HANDY TASK REGISTRATION ==")
    print("This creates a local H taskpack for manual chat-driven patch work.")
    title = input("H task title: ").strip() or "Imperium H manual patch"
    intent = input("Intent / goal: ").strip() or title
    default_h_repo = str(repo_root).replace("\\", "/")
    if not default_h_repo.endswith("_H"):
        default_h_repo = default_h_repo + "_H"
    h_repo = input(f"H repo root [{default_h_repo}]: ").strip() or default_h_repo
    read_raw = input("Files to read (comma separated): ").strip()
    patch_raw = input("Files to patch (comma separated): ").strip()
    out_raw = input("Output ZIP path (blank=Downloads): ").strip()
    zip_path, manifest = make_handy_taskpack(
        repo_root=repo_root,
        title=title,
        intent=intent,
        h_repo_root=h_repo,
        files_to_read=split_csv_lines(read_raw),
        files_to_patch=split_csv_lines(patch_raw),
        output_zip=out_raw or None,
    )
    print("")
    print("HANDY taskpack created:")
    print(str(zip_path).replace("\\", "/"))
    print("SHA256:", manifest.get("zip_sha256"))
    print("")
    answer = input("Register this HANDY taskpack on PC now? (yes/no): ").strip().lower()
    if answer not in {"y", "yes"}:
        print(json.dumps({"status": "HANDY_TASKPACK_CREATED_NOT_REGISTERED", "task_id": manifest["task_id"], "zip_path": manifest["zip_path"]}, ensure_ascii=False, indent=2))
        return
    contour_receipt, vm_receipt = pc_registration(repo_root, zip_path, print_card=True)
    contour_receipt["handy_taskpack_manifest"] = manifest
    vm_receipt["handy_taskpack"] = True
    print(json.dumps(contour_receipt, ensure_ascii=False, indent=2))
    print(json.dumps(vm_receipt, ensure_ascii=False, indent=2))


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
    route_config_discovery: dict[str, Any],
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py "
                f"--repo-root . --zip-path {remote_zip_path} --receipt-out {intake_receipt_path}\""
            ),
            "resolver": (
                f"ssh {ssh_alias} \"cd {remote_repo_root} && {remote_python} "
                "ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py "
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
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
            "route_config_discovery": route_config_discovery,
            "warnings": notes,
        }
        return contour_receipt, vm_receipt

    intake_cmd = (
        f"cd {shell_q(remote_repo_root)} && "
        f"{shell_q(remote_python)} "
        "ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py "
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
        "ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py "
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
        "route_config_discovery": route_config_discovery,
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
        "route_config_discovery": route_config_discovery,
    }
    return contour_receipt, vm_receipt


def execute_registration(
    *,
    repo_root: Path,
    zip_path: Path,
    contour: str,
    route_config_path: Path,
    route_config_discovery: dict[str, Any] | None,
    live_remote: bool,
    print_card: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contour_upper = contour.upper()
    if contour_upper not in VALID_CONTOURS:
        raise ValueError(f"Unsupported contour: {contour}")
    if contour_upper == "PC":
        contour_receipt, vm_receipt = pc_registration(repo_root, zip_path, print_card=print_card)
        contour_receipt["route_config_loaded"] = False
        contour_receipt["route_config_discovery"] = route_config_discovery or {}
        vm_receipt["route_config_loaded"] = False
        vm_receipt["route_config_discovery"] = route_config_discovery or {}
        return contour_receipt, vm_receipt
    route_config = load_route_config(route_config_path)
    return remote_registration(
        contour_upper,
        repo_root,
        zip_path,
        route_config=route_config,
        route_config_discovery=route_config_discovery or {},
        live_remote=live_remote,
    )


def discovery_smoke(repo_root: Path, route_config_discovery: dict[str, Any]) -> dict[str, Any]:
    route_template = repo_root / "ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json"
    start_ack_template = repo_root / "ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json"
    matrix_spine = (
        repo_root
        / "SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md"
    )
    return {
        "timestamp_utc": utc_now(),
        "repo_root": str(repo_root).replace("\\", "/"),
        "contour": "PC",
        "remote_route_attempted": False,
        "route_template_path": str(route_template).replace("\\", "/"),
        "route_template_exists": route_template.exists(),
        "start_ack_template_path": str(start_ack_template).replace("\\", "/"),
        "start_ack_template_exists": start_ack_template.exists(),
        "matrix_spine_path": str(matrix_spine).replace("\\", "/"),
        "matrix_spine_exists": matrix_spine.exists(),
        "route_config_loaded_for_pc": False,
        "route_config_discovery": route_config_discovery,
        "verdict": "PASS_WITH_WARNINGS" if route_template.exists() and start_ack_template.exists() else "BLOCK",
    }


def interactive_loop(repo_root: Path) -> int:
    while True:
        print("")
        print("== ASTRONOMICON TASKPACK REGISTRATION SKILL V0.1 ==")
        print("1) Register on PC")
        print("2) Register HANDY / IMPERIUM_H task on PC")
        print("3) Register on VM3")
        print("4) Register on VM2")
        print("5) Exit")
        choice = input("Select: ").strip()
        if choice == "5":
            return 0
        if choice == "2":
            handy_registration_interactive(repo_root)
            continue
        if choice not in {"1", "3", "4"}:
            print("Unknown option.")
            continue
        zip_input = input("Taskpack ZIP path: ").strip()
        if not zip_input:
            print("ZIP path is required.")
            continue
        contour = {"1": "PC", "3": "VM3", "4": "VM2"}[choice]
        live_remote = False
        if contour in {"VM3", "VM2"}:
            live_answer = input("Execute remote route live? (yes/no): ").strip().lower()
            live_remote = live_answer in {"y", "yes"}
        route_discovery = discover_route_config(repo_root)
        route_config_path = normalize_path(route_discovery["route_config_path"])
        contour_receipt, vm_receipt = execute_registration(
            repo_root=repo_root,
            zip_path=normalize_path(zip_input, repo_root),
            contour=contour,
            route_config_path=route_config_path,
            route_config_discovery=route_discovery,
            live_remote=live_remote,
            print_card=True,
        )
        print("")
        print(json.dumps(contour_receipt, ensure_ascii=False, indent=2))
        print(json.dumps(vm_receipt, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Astronomicon Taskpack Registration Skill v0.1")
    parser.add_argument("--repo-root", default="", help="Repository root.")
    parser.add_argument("--zip-path", default="", help="Taskpack ZIP path.")
    parser.add_argument("--contour", default="PC", help="Target contour: PC | VM3 | VM2")
    parser.add_argument("--route-config", default="", help="Route config JSON path.")
    parser.add_argument("--live-remote", action="store_true", help="Execute VM route live.")
    parser.add_argument("--interactive", action="store_true", help="Run interactive menu.")
    parser.add_argument("--contour-receipt-out", default="", help="Write contour receipt JSON.")
    parser.add_argument("--vm-launch-card-receipt-out", default="", help="Write launch-card receipt JSON.")
    parser.add_argument("--print-launch-card", action="store_true", help="Print launch card in direct mode.")
    parser.add_argument("--discovery-smoke", action="store_true", help="Run read-only PC discovery smoke.")
    parser.add_argument("--handy", action="store_true", help="Create/register an IMPERIUM_H handy taskpack interactively.")
    args = parser.parse_args()

    repo_root, repo_root_discovery = resolve_repo_root(args.repo_root if args.repo_root else None)
    route_discovery = discover_route_config(repo_root, args.route_config if args.route_config else None)
    route_config_path = normalize_path(route_discovery["route_config_path"])
    route_discovery["repo_root_discovery"] = repo_root_discovery

    if args.discovery_smoke:
        smoke = discovery_smoke(repo_root, route_discovery)
        print(json.dumps(smoke, ensure_ascii=False, indent=2))
        return 0 if smoke.get("verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 1

    if args.handy:
        handy_registration_interactive(repo_root)
        return 0

    if args.interactive or not args.zip_path:
        return interactive_loop(repo_root)

    zip_path = normalize_path(args.zip_path, repo_root)
    contour_receipt, vm_receipt = execute_registration(
        repo_root=repo_root,
        zip_path=zip_path,
        contour=args.contour,
        route_config_path=route_config_path,
        route_config_discovery=route_discovery,
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
