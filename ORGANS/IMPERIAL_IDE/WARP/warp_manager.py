#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

SURFACE = "IMPERIUM_WARP_STAGE_LOOP_POLISH_V0_8_1"
REQUIRED_ROOT_FILES = [
    "MANIFEST.json",
    "TASK_SPEC.md",
    "ACCEPTANCE_GATES.md",
    "OUTPUT_REQUIREMENTS.md",
    "TASK_ROUTE_MANIFEST_TEMPLATE.json",
    "TASK_START_ACK_TEMPLATE.json",
    "README.md",
]
ORGANS = [
    "DOCTRINARIUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]
VOLATILE_PATTERNS = [
    ".git",
    "node_modules",
    "playwright-report",
    "test-results",
    "_H_PATCH_BACKUPS",
    "H_PATCH_*",
    "H-TASK-*",
    "*.zip",
    "__pycache__",
]
FORBIDDEN_GENERATED_NAMES = {
    "node_modules",
    "playwright-report",
    "test-results",
    "_H_PATCH_BACKUPS",
    "__pycache__",
}
STAGES = [
    "task_admitted",
    "work_started",
    "implementation",
    "validation",
    "report_bundle",
    "owner_review",
    "promotion_ready",
]
GATE_REQUIREMENTS = {
    "task_admitted": ["astronomicon_admission_receipt"],
    "work_started": ["work_started_receipt"],
    "implementation": ["implementation_evidence"],
    "validation": ["inquisition_findings"],
    "report_bundle": ["report_bundle_path"],
    "owner_review": ["owner_review_note"],
    "promotion_ready": ["promotion_preview"],
}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(data, ensure_ascii=True) + "\n")


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def legacy_registry_path(repo: Path) -> Path:
    return repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "warp_registry.json"


def legacy_active_path(repo: Path) -> Path:
    return repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "active_task.json"


def local_handoff_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_LOCAL_HANDOFF")
    if configured:
        return Path(configured).resolve()
    return (Path(repo.anchor) / "IMPERIUM_LOCAL_HANDOFF").resolve()


def runtime_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_WARP_RUNTIME_ROOT")
    if configured:
        return Path(configured).resolve()
    return local_handoff_root(repo) / "WARP_RUNS"


def runtime_registry_dir(repo: Path) -> Path:
    return runtime_root(repo) / "_registry"


def registry_path(repo: Path) -> Path:
    return runtime_registry_dir(repo) / "warp_registry.json"


def active_path(repo: Path) -> Path:
    return runtime_registry_dir(repo) / "active_task.json"


def admission_receipts_path(repo: Path) -> Path:
    return runtime_registry_dir(repo) / "admission_receipts.jsonl"


def default_warp_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_WARP_ROOT")
    if configured:
        return Path(configured).resolve()
    return (Path(repo.anchor) / "IMPERIUM_WARPS").resolve()


def marker_for(repo: Path) -> dict:
    return read_json(repo / ".imperium_warp.json", {})


def main_repo_from(repo: Path) -> Path:
    marker = marker_for(repo)
    if marker.get("main_source"):
        return Path(marker["main_source"]).resolve()
    if str(repo).endswith("_H"):
        return Path(str(repo)[:-2]).resolve()
    return repo.resolve()


def repo_head(repo: Path) -> str:
    result = git(repo, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def repo_branch(repo: Path) -> str:
    result = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_registry(repo: Path) -> dict:
    runtime = read_json(registry_path(repo), {})
    if runtime:
        return runtime
    legacy = read_json(legacy_registry_path(repo), {})
    if legacy:
        legacy["state_origin"] = "LEGACY_SOURCE_SEED_READ_ONLY"
        legacy["runtime_registry_path"] = str(registry_path(repo))
    return legacy


def load_active_task(repo: Path) -> dict:
    return read_json(active_path(repo), {})


def run_dir(repo: Path, warp_id: str) -> Path:
    return runtime_root(repo) / warp_id


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def safe_remove_existing(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing WARP path: {path}")


def create_with_copy(main: Path, path: Path) -> dict:
    safe_remove_existing(path)
    ignore = shutil.ignore_patterns(*VOLATILE_PATTERNS)
    shutil.copytree(main, path, ignore=ignore)
    return {
        "strategy": "copytree_no_git_metadata",
        "returncode": 0,
        "stdout": "copytree completed",
        "stderr": "",
    }


def cmd_create(args) -> None:
    repo = Path(args.repo_root).resolve()
    main = main_repo_from(repo)
    root = Path(args.warp_root).resolve() if args.warp_root else default_warp_root(repo)
    root.mkdir(parents=True, exist_ok=True)
    warp_id = args.warp_id or f"WARP-{stamp()}"
    path = root / warp_id
    result = create_with_copy(main, path)
    marker = {
        "warp_id": warp_id,
        "created_at_utc": now_utc(),
        "main_source": str(main),
        "base_head": repo_head(main),
        "branch": "copy-contour",
        "strategy": result["strategy"],
        "task_required": True,
    }
    write_json(path / ".imperium_warp.json", marker)
    data = {
        "mode": "WARP_CREATED",
        "warp_id": warp_id,
        "path": str(path),
        "created_at_utc": marker["created_at_utc"],
        "main_source": str(main),
        "base_head": marker["base_head"],
        "branch": marker["branch"],
        "strategy": marker["strategy"],
        "active_task_required": True,
        "current_stage": "task_intake",
        "stage_progress": {"done": 0, "total": len(STAGES)},
        "last_action": "create",
        "runtime_registry_path": str(registry_path(repo)),
    }
    write_json(registry_path(repo), data)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "warp": data, "create_result": result}, indent=2))


def task_template_files(task_id: str) -> dict[str, str]:
    manifest = {
        "task_id": task_id,
        "task_title": "Fill this title",
        "owner_language": "RU",
        "taskpack_internal_language": "EN",
        "organs": ORGANS,
        "route": {
            "target_contour": "PC",
            "requires_astronomicon_admission": True,
            "requires_taskpack_before_work": True,
        },
    }
    return {
        "MANIFEST.json": json.dumps(manifest, indent=2),
        "TASK_SPEC.md": f"# TASK SPEC\n\nTask id: {task_id}\n\n## Objective\nFill objective here.\n",
        "ACCEPTANCE_GATES.md": "# ACCEPTANCE GATES\n\n- Taskpack admitted.\n- Work occurs in WARP.\n- Evidence passes.\n",
        "OUTPUT_REQUIREMENTS.md": "# OUTPUT REQUIREMENTS\n\n- Evidence bundle required.\n- No commit or push without policy permission.\n",
        "TASK_ROUTE_MANIFEST_TEMPLATE.json": json.dumps({"task_id": task_id, "route": "PC", "organs": ORGANS}, indent=2),
        "TASK_START_ACK_TEMPLATE.json": json.dumps({"task_id": task_id, "start_ack": "start task", "requires_active_registry": True}, indent=2),
        "README.md": "# Astronomicon Taskpack\n\nKeep required files at ZIP root.\n",
    }


def cmd_export_template(args) -> None:
    repo = Path(args.repo_root).resolve()
    outdir = Path(args.out_dir).resolve() if args.out_dir else local_handoff_root(repo) / "TASK_FORMS"
    outdir.mkdir(parents=True, exist_ok=True)
    task_id = args.task_id or f"TASK-FILL-ME-{stamp()}"
    zip_path = outdir / f"{task_id}_ASTRONOMICON_FORM.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in task_template_files(task_id).items():
            archive.writestr(name, content)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "task_template_zip": str(zip_path), "repo_mutation": False}, indent=2))


def cmd_activate_task(args) -> None:
    repo = Path(args.repo_root).resolve()
    if not args.task_id:
        print(json.dumps({"status": "BLOCKED", "surface": SURFACE, "reason": "MISSING_TASK_ID"}, indent=2))
        return
    warnings = [item for item in (args.warnings or []) if item]
    receipt = {
        "event": "TASK_ADMITTED",
        "recorded_at_utc": now_utc(),
        "task_id": args.task_id,
        "registered_path": args.registered_path,
        "admission_verdict": args.admission_verdict,
        "caps": args.caps,
        "warnings": warnings,
        "receipt_path": args.receipt_path,
    }
    data = {
        "id": args.task_id,
        "status": "ACTIVE_TASK_REGISTERED",
        "registered_path": args.registered_path,
        "admission_verdict": args.admission_verdict,
        "caps": args.caps,
        "warnings": warnings,
        "receipt_path": args.receipt_path,
        "activated_at_utc": receipt["recorded_at_utc"],
        "next_action": "Start Work in the selected WARP.",
        "runtime_state_path": str(active_path(repo)),
    }
    write_json(active_path(repo), data)
    append_jsonl(admission_receipts_path(repo), receipt)
    registry = load_registry(repo)
    registry.update(
        {
            "active_task_id": args.task_id,
            "active_task_required": True,
            "current_stage": "task_admitted",
            "last_action": "activate-task",
            "runtime_registry_path": str(registry_path(repo)),
        }
    )
    write_json(registry_path(repo), registry)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "active_task": data, "warp": registry}, indent=2))


def initial_stage_ledger(registry: dict, active: dict, created_at: str) -> dict:
    rows = []
    for stage_id in STAGES:
        status = "PASS" if stage_id == "task_admitted" else "ACTIVE" if stage_id == "work_started" else "PENDING"
        rows.append(
            {
                "stage_id": stage_id,
                "status": status,
                "updated_at_utc": created_at if status != "PENDING" else None,
                "evidence": ["astronomicon_admission_receipt"] if stage_id == "task_admitted" else ["work_started_receipt"] if stage_id == "work_started" else [],
            }
        )
    return {
        "status": "PASS",
        "surface": SURFACE,
        "warp_id": registry["warp_id"],
        "task_id": active["id"],
        "current_stage": "work_started",
        "created_at_utc": created_at,
        "updated_at_utc": created_at,
        "gate_requirements": GATE_REQUIREMENTS,
        "stages": rows,
        "events": [
            {"event": "task_admitted", "status": "PASS", "at_utc": active.get("activated_at_utc", created_at)},
            {"event": "work_started", "status": "PASS", "at_utc": created_at},
        ],
    }


def initial_stage_gates(registry: dict, active: dict, created_at: str) -> dict:
    return {
        "status": "PASS_WITH_PENDING_GATES",
        "surface": "ASTRONOMICON_WARP_STAGE_GATES_V0_8_1",
        "warp_id": registry["warp_id"],
        "task_id": active["id"],
        "updated_at_utc": created_at,
        "gates": [
            {"stage_id": stage, "required_evidence": [], "verdict": "PASS" if stage in {"task_admitted", "work_started"} else "PENDING"}
            for stage in STAGES
        ],
    }


def initial_inquisition_findings(repo: Path, registry: dict, active: dict, created_at: str) -> dict:
    warp_path = Path(registry["path"]).resolve()
    return {
        "status": "PASS",
        "surface": "INQUISITION_WARP_RUNTIME_V0_8_1",
        "warp_id": registry["warp_id"],
        "task_id": active["id"],
        "generated_at_utc": created_at,
        "checks": {
            "warp_path_exists": warp_path.exists(),
            "warp_path_allowlisted": path_is_within(warp_path, default_warp_root(repo)),
            "runtime_path_allowlisted": path_is_within(run_dir(repo, registry["warp_id"]), runtime_root(repo)),
            "commit_push_not_exposed": True,
        },
        "findings": [],
    }


def seed_run_state(repo: Path, registry: dict, active: dict) -> Path:
    created_at = now_utc()
    destination = run_dir(repo, registry["warp_id"])
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "stage_ledger.json", initial_stage_ledger(registry, active, created_at))
    write_json(destination / "astronomicon_stage_gates.json", initial_stage_gates(registry, active, created_at))
    write_json(destination / "inquisition_findings.json", initial_inquisition_findings(repo, registry, active, created_at))
    receipts = destination / "administratum_receipts.jsonl"
    if receipts.exists():
        receipts.unlink()
    append_jsonl(
        receipts,
        {
            "event": "TASK_ADMITTED",
            "status": active.get("admission_verdict", "PASS"),
            "at_utc": active.get("activated_at_utc", created_at),
            "task_id": active["id"],
            "receipt_path": active.get("receipt_path", ""),
        },
    )
    append_jsonl(
        receipts,
        {
            "event": "WORK_STARTED",
            "status": "PASS",
            "at_utc": created_at,
            "task_id": active["id"],
            "warp_id": registry["warp_id"],
            "warp_path": registry["path"],
        },
    )
    return destination


def blocked(reason: str, message: str, **details) -> None:
    payload = {"status": "BLOCKED", "surface": SURFACE, "reason": reason, "message": message}
    payload.update(details)
    print(json.dumps(payload, indent=2))


def cmd_start_work(args) -> None:
    repo = Path(args.repo_root).resolve()
    active = load_active_task(repo)
    registry = load_registry(repo)
    if not active.get("id"):
        blocked("NO_ACTIVE_ASTRONOMICON_TASKPACK", "Register or select an active taskpack before work.")
        return
    if not registry.get("warp_id") or not registry.get("path"):
        blocked("NO_WARP_SELECTED", "Create or select a WARP before starting work.")
        return
    warp_path = Path(registry["path"]).resolve()
    if not warp_path.exists():
        blocked("WARP_PATH_MISSING", "The selected WARP path does not exist.", warp_path=str(warp_path))
        return
    if not path_is_within(warp_path, default_warp_root(repo)):
        blocked("WARP_PATH_OUTSIDE_ALLOWLIST", "The selected WARP is outside IMPERIUM_WARPS.", warp_path=str(warp_path))
        return
    destination = seed_run_state(repo, registry, active)
    marker = marker_for(warp_path)
    registry.update(
        {
            "mode": "WORK_ACTIVE",
            "active_task_id": active["id"],
            "current_stage": "work_started",
            "started_at_utc": now_utc(),
            "last_action": "start-work",
            "runtime_path": str(destination),
            "runtime_registry_path": str(registry_path(repo)),
            "stage_progress": {"done": 2, "total": len(STAGES)},
            "branch": marker.get("branch") or repo_branch(warp_path),
            "base_head": marker.get("base_head") or registry.get("base_head") or repo_head(warp_path),
            "strategy": marker.get("strategy") or registry.get("strategy", "unknown"),
        }
    )
    write_json(registry_path(repo), registry)
    print(
        json.dumps(
            {
                "status": "PASS",
                "surface": SURFACE,
                "warp": registry,
                "stage_ledger": str(destination / "stage_ledger.json"),
                "created_runtime_files": [
                    str(destination / "stage_ledger.json"),
                    str(destination / "administratum_receipts.jsonl"),
                    str(destination / "astronomicon_stage_gates.json"),
                    str(destination / "inquisition_findings.json"),
                ],
            },
            indent=2,
        )
    )


def untracked_files(path: Path) -> set[str]:
    result = git(path, "ls-files", "--others", "--exclude-standard", "-z")
    if result.returncode != 0:
        return set()
    files = set()
    for item in result.stdout.split("\0"):
        if item:
            files.add(str((path / item).resolve()))
    return files


def scan_forbidden(path: Path) -> list[str]:
    findings = []
    if not path.exists():
        return findings
    untracked = untracked_files(path) if (path / ".git").exists() else set()
    for item in path.rglob("*"):
        relative_parts = item.relative_to(path).parts
        if ".git" in relative_parts:
            continue
        if any(part in FORBIDDEN_GENERATED_NAMES for part in relative_parts):
            findings.append(str(item))
        elif item.is_file() and str(item.resolve()) in untracked and (
            item.suffix.lower() == ".zip"
            or fnmatch.fnmatch(item.name, "H_PATCH_*")
            or fnmatch.fnmatch(item.name, "H-TASK-*")
            or item.name.endswith("_ASTRONOMICON_FORM.zip")
        ):
            findings.append(str(item))
        if len(findings) >= 100:
            break
    return findings


def copy_contour_strategy(registry: dict, marker: dict, warp_path: Path) -> bool:
    strategy = marker.get("strategy") or registry.get("strategy") or ""
    return strategy == "copytree_no_git_metadata" or not (warp_path / ".git").exists()


def inquisition_snapshot(repo: Path, registry: dict) -> dict:
    warp_path = Path(registry.get("path", "")).resolve() if registry.get("path") else repo
    marker = marker_for(warp_path)
    is_copy_contour = copy_contour_strategy(registry, marker, warp_path)
    status_lines = [] if is_copy_contour else git(warp_path, "status", "--short").stdout.splitlines()
    diff_stat = "" if is_copy_contour else git(warp_path, "diff", "--stat").stdout.strip()
    forbidden = scan_forbidden(warp_path)
    base_head = marker.get("base_head") or registry.get("base_head")
    current_head = "copy-contour-no-git-metadata" if is_copy_contour else repo_head(warp_path)
    warnings = []
    if is_copy_contour:
        warnings.append("COPY_CONTOUR_HEAD_UNAVAILABLE: no .git metadata; promote via patch/diff bundle only.")
    checks = {
        "warp_selected": bool(registry.get("warp_id")),
        "warp_path_exists": warp_path.exists(),
        "warp_path_allowlisted": path_is_within(warp_path, default_warp_root(repo)),
        "runtime_path_allowlisted": path_is_within(run_dir(repo, registry.get("warp_id", "NO_WARP")), runtime_root(repo)),
        "forbidden_generated_files_absent": not forbidden,
        "no_commit_since_warp_base": True if is_copy_contour else bool(base_head and current_head == base_head),
        "commit_push_not_exposed": True,
    }
    passed = all(value is True for value in checks.values())
    status = "PASS_WITH_WARNINGS" if passed and warnings else "PASS" if passed else "FAIL"
    return {
        "status": status,
        "surface": "INQUISITION_WARP_RUNTIME_V0_8_1",
        "generated_at_utc": now_utc(),
        "warp_id": registry.get("warp_id"),
        "warp_path": str(warp_path),
        "strategy": marker.get("strategy") or registry.get("strategy", "unknown"),
        "promotion_route": "PATCH_OR_DIFF_BUNDLE_REQUIRED" if is_copy_contour else "GIT_WORKTREE_CHERRY_PICK_AVAILABLE",
        "checks": checks,
        "warnings": warnings,
        "dirty_count": len(status_lines),
        "dirty_scope": status_lines[:100],
        "forbidden_generated_files": forbidden,
        "diff_stat": diff_stat,
        "base_head": base_head,
        "current_head": current_head,
        "commit_push_performed": False,
    }



def load_stage_state(repo: Path) -> tuple[dict, dict, Path, dict]:
    registry = load_registry(repo)
    active = load_active_task(repo)
    if not active.get("id"):
        raise ValueError("NO_ACTIVE_ASTRONOMICON_TASKPACK")
    if not registry.get("warp_id"):
        raise ValueError("NO_WARP_SELECTED")
    destination = run_dir(repo, registry["warp_id"])
    ledger = read_json(destination / "stage_ledger.json", {})
    if not ledger:
        destination = seed_run_state(repo, registry, active)
        ledger = read_json(destination / "stage_ledger.json", {})
    ledger.setdefault("gate_requirements", GATE_REQUIREMENTS)
    return registry, active, destination, ledger


def current_stage_from(ledger: dict, registry: dict) -> str:
    return ledger.get("current_stage") or registry.get("current_stage") or "work_started"


def normalize_stage_id(stage_id: str, ledger: dict, registry: dict) -> str:
    if stage_id:
        return stage_id
    current = current_stage_from(ledger, registry)
    if current in {"task_intake", "task_admitted", "work_started"}:
        for item in ledger.get("stages", []):
            if item.get("status") in {"PENDING", "BLOCKED"}:
                return item.get("stage_id", "implementation")
    return current


def stage_row(ledger: dict, stage_id: str) -> dict:
    for item in ledger.setdefault("stages", []):
        if item.get("stage_id") == stage_id:
            return item
    row = {"stage_id": stage_id, "status": "PENDING", "updated_at_utc": None, "evidence": []}
    ledger.setdefault("stages", []).append(row)
    return row


def update_progress(registry: dict, ledger: dict) -> None:
    done = sum(1 for item in ledger.get("stages", []) if item.get("status") == "PASS")
    registry["stage_progress"] = {"done": done, "total": len(STAGES)}
    registry["current_stage"] = ledger.get("current_stage", registry.get("current_stage", "work_started"))


def write_stage_bundle(repo: Path, registry: dict, destination: Path, ledger: dict, receipt: dict | None = None) -> None:
    ledger["updated_at_utc"] = now_utc()
    ledger["gate_requirements"] = GATE_REQUIREMENTS
    write_json(destination / "stage_ledger.json", ledger)
    if receipt:
        append_jsonl(destination / "administratum_receipts.jsonl", receipt)
    update_progress(registry, ledger)
    write_json(registry_path(repo), registry)


def gate_stage(repo: Path, registry: dict, destination: Path, ledger: dict, stage_id: str) -> dict:
    row = stage_row(ledger, stage_id)
    evidence = set(row.get("evidence", []))
    required = GATE_REQUIREMENTS.get(stage_id, [])
    blockers = []
    for item in required:
        if item not in evidence:
            if item == "inquisition_findings" and (destination / "inquisition_findings.json").exists():
                row.setdefault("evidence", []).append(item)
                continue
            blockers.append(f"missing:{item}")
    if stage_id == "promotion_ready":
        preview = build_promotion_preview(repo, registry)
        if preview.get("blocked"):
            blockers.extend(preview.get("blockers", []))
    verdict = "PASS" if not blockers else "BLOCKED"
    row["gate_verdict"] = verdict
    row["blockers"] = blockers
    row["updated_at_utc"] = now_utc()
    gates = read_json(destination / "astronomicon_stage_gates.json", {"gates": []})
    gates.update({"status": "PASS" if verdict == "PASS" else "BLOCKED", "surface": "ASTRONOMICON_WARP_STAGE_GATES_V0_8_1", "updated_at_utc": now_utc(), "current_stage": stage_id})
    existing = {item.get("stage_id"): item for item in gates.get("gates", [])}
    existing[stage_id] = {"stage_id": stage_id, "required_evidence": required, "verdict": verdict, "blockers": blockers, "updated_at_utc": now_utc()}
    gates["gates"] = [existing.get(stage, {"stage_id": stage, "required_evidence": GATE_REQUIREMENTS.get(stage, []), "verdict": "PENDING"}) for stage in STAGES]
    write_json(destination / "astronomicon_stage_gates.json", gates)
    return {"stage_id": stage_id, "verdict": verdict, "required_evidence": required, "blockers": blockers, "gates_path": str(destination / "astronomicon_stage_gates.json")}


def cmd_stage_start(args) -> None:
    repo = Path(args.repo_root).resolve()
    try:
        registry, active, destination, ledger = load_stage_state(repo)
    except ValueError as exc:
        reason = str(exc)
        blocked(reason, "Stage control requires active WARP and admitted taskpack.")
        return
    stage_id = normalize_stage_id(getattr(args, "stage_id", ""), ledger, registry)
    row = stage_row(ledger, stage_id)
    row.update({"status": "ACTIVE", "started_at_utc": now_utc(), "updated_at_utc": now_utc()})
    ledger["current_stage"] = stage_id
    ledger.setdefault("events", []).append({"event": "stage_started", "stage_id": stage_id, "status": "ACTIVE", "at_utc": now_utc()})
    receipt = {"event": "STAGE_STARTED", "status": "PASS", "at_utc": now_utc(), "stage_id": stage_id, "task_id": active.get("id"), "warp_id": registry.get("warp_id")}
    write_stage_bundle(repo, registry, destination, ledger, receipt)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "stage": row, "stage_ledger": str(destination / "stage_ledger.json")}, indent=2))


def cmd_stage_evidence(args) -> None:
    repo = Path(args.repo_root).resolve()
    try:
        registry, active, destination, ledger = load_stage_state(repo)
    except ValueError as exc:
        blocked(str(exc), "Stage evidence requires active WARP and admitted taskpack.")
        return
    stage_id = normalize_stage_id(getattr(args, "stage_id", ""), ledger, registry)
    row = stage_row(ledger, stage_id)
    evidence = row.setdefault("evidence", [])
    marker = args.evidence or (GATE_REQUIREMENTS.get(stage_id, ["operator_evidence"])[0] if GATE_REQUIREMENTS.get(stage_id) else "operator_evidence")
    if marker not in evidence:
        evidence.append(marker)
    if args.artifact and args.artifact not in evidence:
        evidence.append(args.artifact)
    row["status"] = "ACTIVE" if row.get("status") in {"PENDING", "BLOCKED"} else row.get("status", "ACTIVE")
    row["note"] = args.note or "Operator evidence marker from Web Sanctum."
    row["updated_at_utc"] = now_utc()
    receipt = {"event": "STAGE_EVIDENCE_SUBMITTED", "status": "PASS", "at_utc": now_utc(), "stage_id": stage_id, "evidence": evidence, "note": row.get("note", "")}
    write_stage_bundle(repo, registry, destination, ledger, receipt)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "stage": row, "receipt": receipt}, indent=2))


def cmd_stage_gate(args) -> None:
    repo = Path(args.repo_root).resolve()
    try:
        registry, active, destination, ledger = load_stage_state(repo)
    except ValueError as exc:
        blocked(str(exc), "Stage gate requires active WARP and admitted taskpack.")
        return
    stage_id = normalize_stage_id(getattr(args, "stage_id", ""), ledger, registry)
    gate = gate_stage(repo, registry, destination, ledger, stage_id)
    receipt = {"event": "STAGE_GATE_RUN", "status": gate["verdict"], "at_utc": now_utc(), "stage_id": stage_id, "blockers": gate.get("blockers", [])}
    write_stage_bundle(repo, registry, destination, ledger, receipt)
    print(json.dumps({"status": "PASS" if gate["verdict"] == "PASS" else "BLOCKED", "surface": SURFACE, "gate": gate}, indent=2))


def cmd_stage_close(args) -> None:
    repo = Path(args.repo_root).resolve()
    try:
        registry, active, destination, ledger = load_stage_state(repo)
    except ValueError as exc:
        blocked(str(exc), "Stage close requires active WARP and admitted taskpack.")
        return
    stage_id = normalize_stage_id(getattr(args, "stage_id", ""), ledger, registry)
    gate = gate_stage(repo, registry, destination, ledger, stage_id)
    row = stage_row(ledger, stage_id)
    if gate["verdict"] != "PASS":
        row["status"] = "BLOCKED"
        write_stage_bundle(repo, registry, destination, ledger, {"event": "STAGE_CLOSE_BLOCKED", "status": "BLOCKED", "at_utc": now_utc(), "stage_id": stage_id, "blockers": gate.get("blockers", [])})
        print(json.dumps({"status": "BLOCKED", "surface": SURFACE, "reason": "STAGE_GATE_BLOCKED", "gate": gate}, indent=2))
        return
    row["status"] = "PASS"
    row["closed_at_utc"] = now_utc()
    idx = STAGES.index(stage_id) if stage_id in STAGES else -1
    next_stage = STAGES[idx + 1] if idx >= 0 and idx + 1 < len(STAGES) else "promotion_ready"
    if next_stage != stage_id:
        ledger["current_stage"] = next_stage
        next_row = stage_row(ledger, next_stage)
        if next_row.get("status") == "PENDING":
            next_row["status"] = "ACTIVE"
            next_row["started_at_utc"] = now_utc()
    receipt = {"event": "STAGE_CLOSED", "status": "PASS", "at_utc": now_utc(), "stage_id": stage_id, "next_stage": next_stage}
    write_stage_bundle(repo, registry, destination, ledger, receipt)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "closed_stage": stage_id, "next_stage": next_stage, "stage_ledger": str(destination / "stage_ledger.json")}, indent=2))


def classify_dirty_line(line: str) -> str:
    value = line.strip()
    lower = value.lower()
    if any(part in lower for part in ["node_modules", "playwright-report", "test-results", "_h_patch_backups", "__pycache__"]):
        return "FORBIDDEN"
    if value.endswith(".zip") or "h_patch_" in lower or "h-task-" in lower:
        return "GENERATED_TEMPORARY"
    if any(part in lower for part in ["organs/imperial_ide/web_sanctum", "organs/imperial_ide/warp", "organs/administratum", "organs/mechanicus", "organs/inquisition", "organs/strategium"]):
        return "ALLOWED_SOURCE_CHANGE"
    return "UNKNOWN"


def build_promotion_preview(repo: Path, registry: dict) -> dict:
    warp_path = Path(registry.get("path", "")).resolve() if registry.get("path") else repo
    marker = marker_for(warp_path)
    is_copy_contour = copy_contour_strategy(registry, marker, warp_path)
    status_lines = [] if is_copy_contour else git(warp_path, "status", "--short").stdout.splitlines()
    diff_stat = "" if is_copy_contour else git(warp_path, "diff", "--stat").stdout.strip()
    classified = [{"path": line.strip(), "class": classify_dirty_line(line)} for line in status_lines if line.strip()]
    blockers = [item["path"] for item in classified if item["class"] in {"FORBIDDEN", "GENERATED_TEMPORARY", "UNKNOWN"}]
    allowed = [item["path"] for item in classified if item["class"] == "ALLOWED_SOURCE_CHANGE"]
    forbidden = scan_forbidden(warp_path)
    blockers.extend([f"forbidden_generated:{item}" for item in forbidden[:100]])
    warnings = []
    if is_copy_contour:
        warnings.append("COPY_CONTOUR_PROMOTION_ROUTE: build a patch/diff bundle; do not cherry-pick this WARP.")
    status = "BLOCKED" if blockers else "PASS_WITH_WARNINGS" if (allowed or warnings) else "PASS"
    return {
        "status": status,
        "surface": "PROMOTION_PREVIEW_NO_COMMIT_V0_8_1",
        "generated_at_utc": now_utc(),
        "warp_path": str(warp_path),
        "strategy": marker.get("strategy") or registry.get("strategy", "unknown"),
        "promotion_route": "PATCH_OR_DIFF_BUNDLE_REQUIRED" if is_copy_contour else "GIT_WORKTREE_CHERRY_PICK_AVAILABLE",
        "cherry_pick_available": not is_copy_contour,
        "blocked": bool(blockers),
        "blockers": blockers[:100],
        "warnings": warnings,
        "allowed_source_changes": allowed[:100],
        "classified_dirty_scope": classified[:200],
        "diff_stat": diff_stat,
        "commit_push_performed": False,
        "suggested_commit_message": "IMPERIUM_H: add WARP full stage loop and promotion preview v0.8.1",
        "next_required_action": "Run validation, build report bundle, owner review, then promote manually if accepted.",
    }


def cmd_promotion_preview(args) -> None:
    repo = Path(args.repo_root).resolve()
    registry = load_registry(repo)
    if not registry.get("warp_id"):
        blocked("NO_WARP_SELECTED", "Promotion preview requires a selected WARP.")
        return
    preview = build_promotion_preview(repo, registry)
    destination = run_dir(repo, registry["warp_id"])
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "promotion_preview.json", preview)
    print(json.dumps({"status": "PASS", "surface": SURFACE, "promotion_preview": preview, "receipt": str(destination / "promotion_preview.json")}, indent=2))

def cmd_validate(args) -> None:
    repo = Path(args.repo_root).resolve()
    registry = load_registry(repo)
    active = load_active_task(repo)
    if not active.get("id"):
        blocked("NO_ACTIVE_ASTRONOMICON_TASKPACK", "Validation requires an active runtime task.")
        return
    if not registry.get("warp_id"):
        blocked("NO_WARP_SELECTED", "Validation requires a selected WARP.")
        return
    findings = inquisition_snapshot(repo, registry)
    destination = run_dir(repo, registry["warp_id"])
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "inquisition_findings.json", findings)
    print(json.dumps({"status": findings["status"], "surface": SURFACE, "inquisition": findings, "receipt": str(destination / "inquisition_findings.json")}, indent=2))


def cmd_status(args) -> None:
    repo = Path(args.repo_root).resolve()
    registry = load_registry(repo)
    active = load_active_task(repo)
    destination = run_dir(repo, registry["warp_id"]) if registry.get("warp_id") else None
    ledger = read_json(destination / "stage_ledger.json", {}) if destination else {}
    print(
        json.dumps(
            {
                "status": "PASS",
                "surface": SURFACE,
                "registry": registry or {"mode": "NO_WARP_SELECTED", "active_task_required": True},
                "active_task": active,
                "stage_ledger": ledger,
                "runtime_paths": {
                    "runtime_root": str(runtime_root(repo)),
                    "registry": str(registry_path(repo)),
                    "active_task": str(active_path(repo)),
                    "run_dir": str(destination) if destination else "",
                    "promotion_preview": str(destination / "promotion_preview.json") if destination else "",
                },
            },
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="cmd")
    create = sub.add_parser("create")
    create.add_argument("--warp-root", default="")
    create.add_argument("--warp-id", default="")
    sub.add_parser("start-work")
    sub.add_parser("status")
    sub.add_parser("validate")
    stage_start = sub.add_parser("stage-start")
    stage_start.add_argument("--stage-id", default="")
    stage_evidence = sub.add_parser("stage-evidence")
    stage_evidence.add_argument("--stage-id", default="")
    stage_evidence.add_argument("--evidence", default="")
    stage_evidence.add_argument("--artifact", default="")
    stage_evidence.add_argument("--note", default="")
    stage_gate = sub.add_parser("stage-gate")
    stage_gate.add_argument("--stage-id", default="")
    stage_close = sub.add_parser("stage-close")
    stage_close.add_argument("--stage-id", default="")
    sub.add_parser("promotion-preview")
    export = sub.add_parser("export-task-template")
    export.add_argument("--task-id", default="")
    export.add_argument("--out-dir", default="")
    activate = sub.add_parser("activate-task")
    activate.add_argument("--task-id", required=True)
    activate.add_argument("--registered-path", default="")
    activate.add_argument("--admission-verdict", default="")
    activate.add_argument("--caps", default="")
    activate.add_argument("--warnings", action="append", default=[])
    activate.add_argument("--receipt-path", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    handlers = {
        "create": cmd_create,
        "start-work": cmd_start_work,
        "status": cmd_status,
        "validate": cmd_validate,
        "stage-start": cmd_stage_start,
        "stage-evidence": cmd_stage_evidence,
        "stage-gate": cmd_stage_gate,
        "stage-close": cmd_stage_close,
        "promotion-preview": cmd_promotion_preview,
        "export-task-template": cmd_export_template,
        "activate-task": cmd_activate_task,
    }
    handler = handlers.get(args.cmd)
    if not handler:
        build_parser().print_help()
        return 2
    handler(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
