#!/usr/bin/env python3
"""Build Operator Cockpit L1 generated state and compact build report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import uuid
import zipfile
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-OPERATOR-COCKPIT-L1-OWNER-POWER-PC-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_text(repo_root: Path, *args: str, fallback: str = "UNKNOWN") -> str:
    rc, out, _err = run_command(["git", *args], repo_root)
    if rc != 0 or not out:
        return fallback
    return out.splitlines()[0].strip()


def git_status_entries(repo_root: Path) -> list[dict[str, str]]:
    rc, out, _err = run_command(["git", "status", "--porcelain"], repo_root)
    if rc != 0 or not out:
        return []
    rows: list[dict[str, str]] = []
    for raw_line in out.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        status = line[0:2].strip() or "?"
        path = line[3:].strip() if len(line) > 3 else ""
        rows.append({"status": status, "path": path})
    return rows


def rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def build_small_continuity_pack(
    repo_root: Path,
    task_id: str,
    continuity_dir: Path,
    state_path: Path,
    screenshot_dir: Path,
) -> dict[str, Any]:
    request_id = f"CONTINUITY-PACK-REQ-{utc_now().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:8].upper()}"
    result_id = request_id.replace("REQ", "RESULT", 1)
    request_path = continuity_dir / "requests" / f"{request_id}.json"
    result_path = continuity_dir / "results" / f"{result_id}.json"
    pack_name = f"CONTINUITY_PACK_SMALL_{task_id}.zip"
    pack_path = continuity_dir / "packs" / pack_name
    manifest_path = continuity_dir / "packs" / f"{pack_name}.manifest.json"
    start_here_path = continuity_dir / "packs" / "START_HERE_NEXT_CHAT.md"

    request_payload = {
        "schema_id": "CONTINUITY_PACK_REQUEST_V0_1",
        "task_id": task_id,
        "request_id": request_id,
        "requested_at_utc": utc_now(),
        "mode": "small",
        "requester": "OPERATOR_COCKPIT_L1_BUILDER",
        "claim_boundary": "LOCAL_FILE_BUNDLE_ONLY",
    }
    write_json(request_path, request_payload)

    pack_inputs = [
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.css",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.css",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.js",
        state_path,
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/owner_question_gate_state.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json",
    ]

    screenshot_files = sorted(screenshot_dir.glob("*.png")) if screenshot_dir.exists() else []
    pack_inputs.extend(screenshot_files[:8])
    pack_inputs = [path for path in pack_inputs if path.exists()]

    manifest_payload = {
        "schema_id": "CONTINUITY_PACK_SMALL_MANIFEST_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "mode": "small",
        "input_count": len(pack_inputs),
        "files": [rel(path, repo_root) for path in pack_inputs],
    }
    write_json(manifest_path, manifest_payload)

    start_here_lines = [
        f"# Continuity Pack / {task_id}",
        "",
        "- Scope: operator cockpit L1 stable/candidate owner overview slice.",
        "- Stable URL (static): http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html",
        "- Candidate URL (static): http://127.0.0.1:8765/IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html",
        "- Launch helper: IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/TOOLS/launch_operator_cockpit.ps1",
        "- Launch URL (action server): http://127.0.0.1:8787/operator_cockpit_l1.html",
        "- Claim boundary: no production orchestration / no autonomous execution.",
        "",
        "## Key Artifacts",
        f"- Generated state: `{rel(state_path, repo_root)}`",
        f"- Manifest: `{rel(manifest_path, repo_root)}`",
        "",
        "## Next Chat Start Prompt",
        "Continue from current operator cockpit L1 state.",
        "Do not claim production readiness.",
    ]
    start_here_path.parent.mkdir(parents=True, exist_ok=True)
    start_here_path.write_text("\n".join(start_here_lines) + "\n", encoding="utf-8")

    pack_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pack_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for source in pack_inputs:
            zf.write(source, arcname=rel(source, repo_root))
        zf.write(manifest_path, arcname=rel(manifest_path, repo_root))
        zf.write(start_here_path, arcname=rel(start_here_path, repo_root))

    result_payload = {
        "schema_id": "CONTINUITY_PACK_RESULT_V0_1",
        "task_id": task_id,
        "result_id": result_id,
        "request_id": request_id,
        "generated_at_utc": utc_now(),
        "status": "PASS",
        "mode": "small",
        "pack_ref": rel(pack_path, repo_root),
        "manifest_ref": rel(manifest_path, repo_root),
        "start_here_ref": rel(start_here_path, repo_root),
        "input_count": len(pack_inputs),
        "claim_boundary": "LOCAL_FILE_BUNDLE_ONLY",
        "limitations": [
            "Small continuity pack only.",
            "No direct browser-side build action is claimed.",
        ],
    }
    write_json(result_path, result_payload)

    return {
        "request_ref": rel(request_path, repo_root),
        "result_ref": rel(result_path, repo_root),
        "pack_ref": rel(pack_path, repo_root),
        "manifest_ref": rel(manifest_path, repo_root),
        "start_here_ref": rel(start_here_path, repo_root),
    }


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    default_state_path = default_repo_root / f"{BASE_REL}/DATA/operator_cockpit_l1_state.generated.json"
    parser = argparse.ArgumentParser(description="Build operator cockpit L1 generated state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output-state", type=Path, default=default_state_path)
    parser.add_argument("--output-report", type=Path, default=default_report_dir / "operator_cockpit_l1_report.json")
    parser.add_argument("--build-small-continuity-pack", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_state = args.output_state.resolve()
    output_report = args.output_report.resolve()

    report_dir.mkdir(parents=True, exist_ok=True)
    output_state.parent.mkdir(parents=True, exist_ok=True)

    sanctum_state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
    session_state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json"
    owner_gate_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/owner_question_gate_state.generated.json"
    transfer_view_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
    action_registry_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json"
    schema_path = repo_root / f"{BASE_REL}/CONTRACTS/operator_cockpit_l1_state.schema.json"
    screenshot_dir = report_dir / "SCREENSHOTS"

    sanctum_state = load_json(sanctum_state_path) or {}
    session_state = load_json(session_state_path) or {}
    owner_state = load_json(owner_gate_path) or {}
    transfer_state = load_json(transfer_view_path) or {}
    action_registry = load_json(action_registry_path) or {}

    action_map: dict[str, dict[str, Any]] = {}
    for item in action_registry.get("actions", []):
        if isinstance(item, dict):
            key = str(item.get("action_id", "")).strip()
            if key:
                action_map[key] = item

    head = git_text(repo_root, "rev-parse", "HEAD")
    branch = git_text(repo_root, "branch", "--show-current")
    remote_master_line = git_text(repo_root, "ls-remote", "origin", "refs/heads/master", fallback="")
    remote_master_head = remote_master_line.split()[0] if remote_master_line else "UNKNOWN"
    status_entries = git_status_entries(repo_root)
    worktree = "DIRTY" if status_entries else "CLEAN"
    master_synced = head != "UNKNOWN" and remote_master_head != "UNKNOWN" and head == remote_master_head

    changed_paths = [entry["path"] for entry in status_entries if entry.get("path")]

    owner_summary = owner_state.get("summary", {}) if isinstance(owner_state.get("summary"), dict) else {}
    owner_blocking = int(owner_summary.get("blocking_count", 0) or 0)
    owner_open = int(owner_summary.get("open_count", 0) or 0)
    session_status = str(session_state.get("session_status", "UNKNOWN"))
    next_step = str(session_state.get("next_required_step", "UNKNOWN"))

    transfer_truth_labels = transfer_state.get("truth_labels", [])
    labels_set = {str(item) for item in transfer_truth_labels} if isinstance(transfer_truth_labels, list) else set()
    vm2_vm3 = "PROVED_BOUNDED_ROUTE_ONLY" if "TRANSFER_ROUTE_PROOF_BIDIRECTIONAL_VM2_VM3" in labels_set else "UNKNOWN"
    vm3_vm2 = "PROVED_BOUNDED_ROUTE_ONLY" if vm2_vm3 == "PROVED_BOUNDED_ROUTE_ONLY" else "UNKNOWN"
    pc_vm2 = "NOT_PROVEN"
    pc_vm3 = "NOT_PROVEN"
    for card in transfer_state.get("contour_cards", []):
        if not isinstance(card, dict):
            continue
        contour_id = str(card.get("contour_id", "")).upper()
        route_status = str(card.get("route_config_status", "UNKNOWN"))
        if contour_id == "VM2":
            pc_vm2 = route_status
        if contour_id == "VM3":
            pc_vm3 = route_status

    evidence_refs: list[str] = []
    for block in (
        sanctum_state.get("limitations", []),
        session_state.get("source_reports", []),
        transfer_state.get("source_refs", []),
    ):
        if isinstance(block, list):
            for item in block:
                if isinstance(item, str) and item not in evidence_refs:
                    evidence_refs.append(item)
                if isinstance(item, dict):
                    ref = item.get("path")
                    if isinstance(ref, str) and ref not in evidence_refs:
                        evidence_refs.append(ref)

    confidence_score = 0
    if vm2_vm3 == "PROVED_BOUNDED_ROUTE_ONLY":
        confidence_score += 2
    if len(evidence_refs) >= 8:
        confidence_score += 1
    if owner_blocking == 0:
        confidence_score += 1
    if worktree == "CLEAN":
        confidence_score += 1
    if confidence_score >= 4:
        evidence_confidence = "HIGH"
    elif confidence_score >= 2:
        evidence_confidence = "MEDIUM"
    else:
        evidence_confidence = "LOW"

    if owner_blocking > 0:
        current_blocker = f"owner_questions_blocking={owner_blocking}"
    elif worktree == "DIRTY":
        current_blocker = "worktree_dirty_in_progress"
    else:
        current_blocker = "foundation_only_limitations"

    action_specs = [
        {
            "control_id": "refresh_truth",
            "label": "Refresh Truth",
            "backend_action_id": "REFRESH_TRUTH_STATE",
            "preferred_status": "WIRED",
            "reason": "Mapped to bounded local refresh action server route.",
        },
        {
            "control_id": "validate_truth",
            "label": "Validate Truth",
            "backend_action_id": "VALIDATE_TRUTH_STATE",
            "preferred_status": "WIRED",
            "reason": "Mapped to bounded local validator action server route.",
        },
        {
            "control_id": "build_continuity_pack",
            "label": "Build Continuity Pack",
            "backend_action_id": None,
            "preferred_status": "PREVIEW_ONLY",
            "reason": "Small pack is generated by CLI builder; browser button is preview-only in L1.",
        },
        {
            "control_id": "open_evidence",
            "label": "Open Evidence",
            "backend_action_id": None,
            "preferred_status": "PREVIEW_ONLY",
            "reason": "Use evidence refs panel paths; no backend call required.",
        },
        {
            "control_id": "show_diff",
            "label": "Show Diff",
            "backend_action_id": None,
            "preferred_status": "PREVIEW_ONLY",
            "reason": "Diff summary is rendered from git status in L1 read-only mode.",
        },
        {
            "control_id": "open_dev_preview",
            "label": "Open Dev Preview",
            "backend_action_id": None,
            "preferred_status": "PREVIEW_ONLY",
            "reason": "Opens cockpit URL only; no runtime orchestration claim.",
        },
        {
            "control_id": "send_taskpack_vm2_vm3",
            "label": "Send Taskpack to VM2/VM3",
            "backend_action_id": "DRY_RUN_TASKPACK_SEND",
            "preferred_status": "DRY_RUN_ONLY",
            "reason": "Bounded dry-run route only with request/result receipts.",
        },
        {
            "control_id": "fetch_report_bundle",
            "label": "Fetch Report Bundle",
            "backend_action_id": "DRY_RUN_REPORT_FETCH",
            "preferred_status": "DRY_RUN_ONLY",
            "reason": "Bounded dry-run fetch route only with request/result receipts.",
        },
        {
            "control_id": "owner_decision_answer",
            "label": "Owner Decision / Answer Question",
            "backend_action_id": None,
            "preferred_status": "BLOCKED",
            "reason": "Write path is not admitted in this read-only L1 slice.",
        },
    ]

    actions: list[dict[str, Any]] = []
    for spec in action_specs:
        backend_action_id = spec["backend_action_id"]
        status = spec["preferred_status"]
        backend = action_map.get(backend_action_id) if isinstance(backend_action_id, str) else None
        if backend_action_id and not isinstance(backend, dict):
            status = "BLOCKED"
        receipt_mode = "NOT_ACTIVE_PREVIEW_ONLY"
        if status in {"WIRED", "DRY_RUN_ONLY"}:
            receipt_mode = "SERVER_API_REQUEST_RESULT_RECEIPT"
        if status == "BLOCKED":
            receipt_mode = "BLOCKED_NO_BACKEND"
        actions.append(
            {
                "control_id": spec["control_id"],
                "label": spec["label"],
                "status": status,
                "backend_action_id": backend_action_id,
                "request_result_receipt_mode": receipt_mode,
                "reason": spec["reason"],
                "evidence_refs": [action_registry_path.relative_to(repo_root).as_posix()],
            }
        )

    continuity_dir = output_state.parent / "continuity"
    continuity_result = {
        "request_ref": None,
        "result_ref": None,
        "pack_ref": None,
        "manifest_ref": None,
        "start_here_ref": None,
    }
    if args.build_small_continuity_pack:
        continuity_result = build_small_continuity_pack(
            repo_root=repo_root,
            task_id=str(args.task_id),
            continuity_dir=continuity_dir,
            state_path=output_state,
            screenshot_dir=screenshot_dir,
        )

    report_refs = [
        rel(report_dir / "GATE_ACK.md", repo_root),
        rel(report_dir / "operator_cockpit_l1_report.json", repo_root),
    ]
    validator_refs = [
        rel(report_dir / "operator_cockpit_l1_validator_report.json", repo_root),
        rel(report_dir / "operator_cockpit_l1_smoke_report.json", repo_root),
    ]
    screenshot_refs = [rel(path, repo_root) for path in sorted(screenshot_dir.glob("*.png"))]

    state = {
        "schema_id": "OPERATOR_COCKPIT_L1_STATE_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "claim_boundary": "READ_ONLY_OWNER_COCKPIT_L1",
        "repo": {
            "head": head,
            "branch": branch,
            "worktree": worktree,
            "remote_master_head": remote_master_head,
            "master_synced": master_synced,
            "changed_files": status_entries[:40],
        },
        "five_second_truth": {
            "active_task": str(args.task_id),
            "who_is_working": "PC Servitor / Logos bounded execution",
            "contour": "PC",
            "current_blocker": current_blocker,
            "next_action": next_step,
            "repo_clean": "YES" if worktree == "CLEAN" else "NO",
            "evidence_confidence": evidence_confidence,
        },
        "focus_gateway": {
            "external_inputs": [
                "Cloud LLMs",
                "Local LLMs",
                "Internet / OSINT / Deep research",
                "Utilities / OSS / Databases",
            ],
            "imperium_core": "IMPERIUM focus and dispersion-control core",
            "workers": [
                "Logos + Servitor",
                "PC / VM2 / VM3 bounded contours",
                "Local helper agents",
            ],
            "assistance_block": "Future Imperium Assistance (foundation-only in L1)",
            "digital_outputs": [
                "Application",
                "Game",
                "Prompt",
                "Presentation",
                "Music",
                "Video",
                "Table",
                "Any digital deliverable",
            ],
        },
        "panels": {
            "operator_overview": {
                "status": "PROVED",
                "source_refs": [rel(output_state, repo_root)],
            },
            "task_session": {
                "status": session_status,
                "source_refs": [
                    rel(session_state_path, repo_root),
                    rel(sanctum_state_path, repo_root),
                ],
                "summary": {
                    "session_mode": str(session_state.get("mode", "UNKNOWN")),
                    "session_status": session_status,
                    "owner_open_questions": owner_open,
                    "owner_blocking_questions": owner_blocking,
                },
            },
            "owner_questions_organ_dialogue": {
                "status": str(owner_summary.get("derived_gate_status", "FOUNDATION_ONLY")),
                "source_refs": [
                    rel(owner_gate_path, repo_root),
                    rel(session_state_path, repo_root),
                ],
                "summary": {
                    "owner_question_total": int(owner_summary.get("total_questions", 0) or 0),
                    "organ_request_count": int(
                        (session_state.get("organ_dialogue", {}) or {}).get("request_count", 0) or 0
                    ),
                    "organ_response_count": int(
                        (session_state.get("organ_dialogue", {}) or {}).get("response_count", 0) or 0
                    ),
                },
            },
            "development_preview": {
                "status": "PREVIEW_ONLY",
                "source_refs": [rel(output_state, repo_root)],
            },
            "continuity_pack": {
                "status": "PREVIEW_ONLY",
                "source_refs": [rel(output_state, repo_root)],
            },
        },
        "transfer_routes": {
            "pc_vm2": pc_vm2,
            "pc_vm3": pc_vm3,
            "vm2_vm3": vm2_vm3,
            "vm3_vm2": vm3_vm2,
            "route_proof_commit": "f00053012c5f4110a4a75423be8236fce1a5baa4",
            "source_refs": [
                rel(transfer_view_path, repo_root),
                "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-BIDIRECTIONAL-ROUTE-PROOF-VM2-V0_1",
            ],
        },
        "evidence_diff": {
            "changed_files_count": len(changed_paths),
            "changed_files": changed_paths[:40],
            "report_refs": report_refs,
            "validator_refs": validator_refs,
            "screenshot_refs": screenshot_refs,
            "source_refs": [
                rel(sanctum_state_path, repo_root),
                rel(session_state_path, repo_root),
                rel(owner_gate_path, repo_root),
                rel(transfer_view_path, repo_root),
            ],
        },
        "continuity": {
            "small_mode": "PREVIEW_ONLY",
            "latest_pack_ref": continuity_result["pack_ref"],
            "latest_manifest_ref": continuity_result["manifest_ref"],
            "latest_start_here_ref": continuity_result["start_here_ref"],
            "latest_request_ref": continuity_result["request_ref"],
            "latest_result_ref": continuity_result["result_ref"],
            "reason": "Stateful small pack is generated via CLI builder in this L1 slice.",
        },
        "development_preview": {
            "status": "PREVIEW_ONLY",
            "preview_url": "http://127.0.0.1:8787/operator_cockpit_l1.html",
            "reason": "Live WIRED action controls require local action server mode.",
            "screenshot_refs": screenshot_refs,
        },
        "actions": actions,
        "limitations": [
            "PASS scope is read-only owner overview slice.",
            "No production orchestration claim.",
            "No live autonomous execution claim.",
            "Owner decision write path remains blocked in this slice.",
            "Continuity pack button is preview-only in browser; CLI build is available.",
        ],
        "forbidden_claims": [
            "live execution",
            "production orchestration",
            "final luxury visual quality",
            "full organ intelligence",
            "autonomous multi-contour operation",
        ],
        "source_refs": [
            rel(schema_path, repo_root),
            rel(sanctum_state_path, repo_root),
            rel(session_state_path, repo_root),
            rel(owner_gate_path, repo_root),
            rel(transfer_view_path, repo_root),
            rel(action_registry_path, repo_root),
        ],
    }

    write_json(output_state, state)

    build_report = {
        "schema_id": "OPERATOR_COCKPIT_L1_BUILD_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": "PASS",
        "generated_state_ref": rel(output_state, repo_root),
        "report_ref": rel(output_report, repo_root),
        "summary": {
            "worktree": worktree,
            "master_synced": master_synced,
            "changed_files_count": len(changed_paths),
            "evidence_confidence": evidence_confidence,
            "route_truth_vm2_vm3": vm2_vm3,
            "route_truth_vm3_vm2": vm3_vm2,
        },
        "continuity_pack": continuity_result,
        "claim_boundary": "READ_ONLY_OWNER_COCKPIT_L1",
        "notes": [
            "Generated state is bounded to existing NewGen artifacts and git truth.",
            "No fake-green: route and action claims remain scoped.",
        ],
    }
    write_json(output_report, build_report)

    print(f"operator_cockpit_state={rel(output_state, repo_root)}")
    print(f"operator_cockpit_build_report={rel(output_report, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
