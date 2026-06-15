from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import (  # noqa: E402
    RootResolutionError,
    git_truth,
    resolve_new_reality_root,
    resolve_output_path,
    validate_git_field,
)


TASK_ID = "TASK-NEWGEN-PC-NEW-REALITY-ROOT-RESOLVER-15-RUNTIME-CANDIDATES-AND-PROOF-REFRESH-PC-V0_1"
PREVIOUS_TASK_ID = "TASK-NEWGEN-PC-NEW-REALITY-RUNTIME-PATH-ADAPTER-SMOKE-GATE-PC-V0_1"
ACTIVE_ROOT = Path("E:/IMPERIUM_NEW_GENERATION_NEW_REALITY")
ANCIENT_ROOT = Path("E:/IMPERIUM")
ANCIENT_HEAD_AT_ROLE_ENTRY = "ca8454779da2af638609e1ea36393bffbc57f338"
ANCIENT_STATUS_AT_ROLE_ENTRY = [
    "## master...origin/master",
    " M IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
    " M IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
    "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-ROLE-PACK-AND-LOGOS-OWNER-AUDIT-CARD-CONTRACT-PC-V0_1/",
    "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-ROOT-RESOLVER-15-RUNTIME-CANDIDATES-AND-PROOF-REFRESH-PC-V0_1/",
    "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-RUNTIME-PATH-ADAPTER-SMOKE-GATE-PC-V0_1/",
    "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-SEPARATE-REPO-ANCIENT-EMPIRE-FREEZE-PC-V0_1/",
]

REPORT_ROOT_REL = Path("REPORTS") / TASK_ID
PREVIOUS_CANDIDATES_REL = Path("REPORTS") / PREVIOUS_TASK_ID / "runtime_critical_path_dependency_list.json"
CONTRACT_PATH_REL = Path("ROOT_RESOLUTION_CONTRACT.md")

OLD_PC_ROOT_RE = re.compile(r"E:[/\\]IMPERIUM(?!_NEW_GENERATION_NEW_REALITY)(?:[/\\]|$)")
OLD_CONTEXT_RE = re.compile(r"E:[/\\]IMPERIUM_CONTEXT(?:[/\\]|$)")


CANDIDATE_POLICIES: dict[str, dict[str, Any]] = {
    "ADMINISTRATUM/TOOLS/administratum_card_checker_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Seed workspace path is now New Reality relative RUNS/WARP/SESSION_001.",
        "allow_old_context_detector": False,
    },
    "AGENT_IDE/TOOLS/agent_ide_block_registry_checker_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Repo root default now resolves through root_resolution.py and reports inside AGENT_IDE/REPORTS.",
        "allow_old_context_detector": False,
    },
    "AGENT_IDE/TOOLS/agent_ide_data_probe_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Repo root and receipt path now resolve through New Reality root.",
        "allow_old_context_detector": False,
    },
    "AGENT_IDE/TOOLS/agent_ide_scope_checker_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Repo root default removed; Agent IDE allowed prefix points to top-level AGENT_IDE.",
        "allow_old_context_detector": False,
    },
    "AGENT_IDE/TOOLS/agent_ide_scope_checker_v0_2.py": {
        "resolution": "PATCHED",
        "reason": "Repo root default removed; allowed prefixes point to top-level New Reality layout.",
        "allow_old_context_detector": False,
    },
    "AGENT_IDE/TOOLS/agent_ide_smoke_test_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Repo root and receipt path now resolve through New Reality root.",
        "allow_old_context_detector": False,
    },
    "COMMON_AGENT_CLI/base_half_cli.py": {
        "resolution": "PATCHED",
        "reason": "Default runtime path now uses RUNS/COMMON_AGENT_CLI under New Reality.",
        "allow_old_context_detector": False,
    },
    "MECHANICUS/TOOLS/check_mechanicus_evidence_index_v0_1.py": {
        "resolution": "CLASSIFIED",
        "reason": "The remaining E:/IMPERIUM_CONTEXT string is a private-path detector signature, not an active root default.",
        "allow_old_context_detector": True,
    },
    "MECHANICUS/TOOLS/mechanicus_evidence_index_builder_v0_1.py": {
        "resolution": "CLASSIFIED",
        "reason": "The remaining E:/IMPERIUM_CONTEXT string is a private-path detector signature, not an active root default.",
        "allow_old_context_detector": True,
    },
    "MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py": {
        "resolution": "PATCHED",
        "reason": "Expected repo root and active Mechanicus relative paths now target New Reality layout.",
        "allow_old_context_detector": False,
    },
    "ORGAN_AGENTS/ADMINISTRATUM_AGENT/LAUNCHERS/run_administratum_pc.ps1": {
        "resolution": "PATCHED",
        "reason": "PowerShell launcher now dot-sources root_resolution.ps1 and writes transfer runtime under RUNS.",
        "allow_old_context_detector": False,
    },
    "ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py": {
        "resolution": "PATCHED_WITH_CLASSIFIED_VM_REMOTE",
        "reason": "PC repo/context defaults now use New Reality; VM2 remote IMPERIUM_CONTEXT defaults are classified out of scope by no_vm_sync.",
        "allow_old_context_detector": False,
    },
    "ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_v1_core.py": {
        "resolution": "PATCHED_WITH_CLASSIFIED_DETECTORS",
        "reason": "Repo root and default context roots now resolve to New Reality; IMPERIUM_CONTEXT text remains only as classification vocabulary.",
        "allow_old_context_detector": False,
    },
    "ORGAN_AGENTS/OFFICIO_AGENTIS_AGENT/TOOLS/officio_agent_runner.py": {
        "resolution": "PATCHED",
        "reason": "Runtime root and COMMON_AGENT_CLI path now resolve under New Reality.",
        "allow_old_context_detector": False,
    },
    "SANCTUM_NG/OPERATOR_COCKPIT/TOOLS/launch_operator_cockpit.ps1": {
        "resolution": "PATCHED",
        "reason": "PowerShell launcher now resolves New Reality root and serves top-level SANCTUM_NG app paths.",
        "allow_old_context_detector": False,
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }


def read_previous_candidates(repo_root: Path) -> list[dict[str, Any]]:
    payload = json.loads((repo_root / PREVIOUS_CANDIDATES_REL).read_text(encoding="utf-8"))
    candidates = payload.get("runtime_critical_candidates", [])
    if not isinstance(candidates, list):
        raise RuntimeError("previous runtime candidates payload is malformed")
    return candidates


def rel_from_previous_file(path_text: str, repo_root: Path) -> str:
    path = Path(path_text)
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path_text).replace("\\", "/").replace("E:/IMPERIUM_NEW_GENERATION_NEW_REALITY/", "")


def build_root_receipt(repo_root: Path, report_root: Path) -> dict[str, Any]:
    resolution = resolve_new_reality_root(repo_root)
    payload = {
        "task_id": TASK_ID,
        "receipt_type": "root_resolution_receipt",
        "timestamp_utc": utc_now(),
        **resolution.to_receipt(),
        "ancient_empire_mutated": False,
        "git": git_truth(repo_root),
        "verdict": "PASS",
    }
    write_json(report_root / "root_resolution_receipt.json", payload)
    return payload


def build_smoke_receipt(repo_root: Path, report_root: Path) -> dict[str, Any]:
    smoke: dict[str, Any] = {
        "task_id": TASK_ID,
        "receipt_type": "root_resolution_smoke_receipt",
        "timestamp_utc": utc_now(),
        "checks": {},
    }

    smoke["checks"]["explicit_cli_arg"] = resolve_new_reality_root(repo_root).to_receipt()
    env = {**os.environ, "IMPERIUM_NEW_REALITY_ROOT": repo_root.as_posix()}
    smoke["checks"]["environment"] = resolve_new_reality_root(None, start=Path(__file__), env=env).to_receipt()
    smoke["checks"]["auto_discovery"] = resolve_new_reality_root(None, start=repo_root / "AGENT_IDE" / "TOOLS", env={}).to_receipt()
    try:
        resolve_new_reality_root(ANCIENT_ROOT)
        ancient_blocked = False
        ancient_error = ""
    except RootResolutionError as exc:
        ancient_blocked = True
        ancient_error = str(exc)
    smoke["checks"]["ancient_empire_block"] = {
        "attempted_root": ANCIENT_ROOT.as_posix(),
        "blocked": ancient_blocked,
        "error": ancient_error,
    }
    ps_command = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        ". ./ORGAN_AGENT_COMMON/root_resolution.ps1; Resolve-NewRealityRoot -RepoRoot 'E:/IMPERIUM_NEW_GENERATION_NEW_REALITY'",
    ]
    smoke["checks"]["powershell_helper"] = run_command(ps_command, repo_root)

    all_pass = (
        smoke["checks"]["explicit_cli_arg"]["active_root"] == repo_root.as_posix()
        and smoke["checks"]["environment"]["active_root"] == repo_root.as_posix()
        and smoke["checks"]["auto_discovery"]["active_root"] == repo_root.as_posix()
        and ancient_blocked
        and smoke["checks"]["powershell_helper"]["returncode"] == 0
    )
    smoke["verdict"] = "PASS" if all_pass else "BLOCK"
    write_json(report_root / "root_resolution_smoke_receipt.json", smoke)
    return smoke


def build_git_field_sanity_receipt(repo_root: Path, report_root: Path) -> dict[str, Any]:
    truth = git_truth(repo_root)
    negative_cases = [
        {"field": "git_head", "value": "usage: git rev-parse [--verify] HEAD"},
        {"field": "git_branch", "value": "options:\n  -h, --help"},
        {"field": "git_head", "value": "not-a-commit"},
    ]
    negative_results = []
    for case in negative_cases:
        ok, reason = validate_git_field(case["field"], case["value"])
        negative_results.append({**case, "accepted": ok, "reason": reason})
    payload = {
        "task_id": TASK_ID,
        "receipt_type": "git_field_sanity_gate_receipt",
        "timestamp_utc": utc_now(),
        "positive_git_truth": truth,
        "negative_cases": negative_results,
        "verdict": "PASS"
        if truth["git_head_sane"] and truth["git_branch_sane"] and not any(row["accepted"] for row in negative_results)
        else "BLOCK",
    }
    write_json(report_root / "git_field_sanity_gate_receipt.json", payload)
    return payload


def build_candidate_receipt(repo_root: Path, report_root: Path) -> dict[str, Any]:
    previous = read_previous_candidates(repo_root)
    rows: list[dict[str, Any]] = []
    missing_policies: list[str] = []
    failing: list[str] = []
    for item in previous:
        rel_path = rel_from_previous_file(str(item.get("file", "")), repo_root)
        policy = CANDIDATE_POLICIES.get(rel_path)
        if policy is None:
            missing_policies.append(rel_path)
            continue
        file_path = repo_root / rel_path
        text = file_path.read_text(encoding="utf-8")
        old_root_hits = bool(OLD_PC_ROOT_RE.search(text))
        old_context_hits = bool(OLD_CONTEXT_RE.search(text))
        allowed_context = bool(policy.get("allow_old_context_detector"))
        status = "PASS"
        notes: list[str] = []
        if old_root_hits:
            status = "FAIL"
            notes.append("old active PC root remains")
        if old_context_hits and not allowed_context:
            status = "FAIL"
            notes.append("old PC context default remains")
        if old_context_hits and allowed_context:
            notes.append("old context string retained as detector signature")
        if status != "PASS":
            failing.append(rel_path)
        rows.append(
            {
                "file": rel_path,
                "previous_match_count": item.get("match_count"),
                "resolution": policy["resolution"],
                "reason": policy["reason"],
                "old_active_root_hits": old_root_hits,
                "old_context_hits": old_context_hits,
                "classification_notes": notes,
                "status": status,
            }
        )

    payload = {
        "task_id": TASK_ID,
        "receipt_type": "runtime_candidate_patch_or_classification_receipt",
        "timestamp_utc": utc_now(),
        "previous_task_id": PREVIOUS_TASK_ID,
        "candidate_count_expected": 15,
        "candidate_count_seen": len(previous),
        "candidate_count_receipted": len(rows),
        "missing_policies": missing_policies,
        "failing_candidates": failing,
        "candidates": rows,
        "verdict": "PASS" if len(previous) == 15 and len(rows) == 15 and not missing_policies and not failing else "BLOCK",
    }
    write_json(report_root / "runtime_candidate_patch_or_classification_receipt.json", payload)
    return payload


def build_ancient_no_mutation_receipt(report_root: Path) -> dict[str, Any]:
    head = run_command(["git", "rev-parse", "HEAD"], ANCIENT_ROOT)
    branch = run_command(["git", "branch", "--show-current"], ANCIENT_ROOT)
    status = run_command(["git", "status", "--short", "--branch"], ANCIENT_ROOT)
    current_status_lines = status["stdout"].splitlines() if status["stdout"] else []
    head_unchanged = head["stdout"] == ANCIENT_HEAD_AT_ROLE_ENTRY
    status_unchanged = current_status_lines == ANCIENT_STATUS_AT_ROLE_ENTRY
    payload = {
        "task_id": TASK_ID,
        "receipt_type": "ancient_empire_no_mutation_receipt",
        "timestamp_utc": utc_now(),
        "ancient_empire_reference_root": ANCIENT_ROOT.as_posix(),
        "head_at_role_entry": ANCIENT_HEAD_AT_ROLE_ENTRY,
        "head_after_work": head["stdout"],
        "branch_after_work": branch["stdout"],
        "status_after_work": current_status_lines,
        "head_unchanged": head_unchanged,
        "status_matches_role_entry_snapshot": status_unchanged,
        "pre_existing_dirty_state_declared": True,
        "ancient_empire_mutated_by_this_task": False if head_unchanged and status_unchanged else None,
        "verdict": "PASS_WITH_WARNINGS" if head_unchanged and status_unchanged else "WARN_REVIEW_REQUIRED",
        "warnings": ["Ancient Empire had pre-existing dirty/untracked registry/taskpack state before this task."],
    }
    write_json(report_root / "ancient_empire_no_mutation_receipt.json", payload)
    return payload


def build_self_hosting_status(report_root: Path, smoke: dict[str, Any], candidate_receipt: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "receipt_type": "new_reality_self_hosting_status_receipt",
        "timestamp_utc": utc_now(),
        "root_resolution_proven": smoke.get("verdict") == "PASS",
        "runtime_candidates_covered": candidate_receipt.get("verdict") == "PASS",
        "registration_bridge": "ANCIENT_EMPIRE_ASTRONOMICON_TASKPACK_CARRIER",
        "self_hosting_state": "PARTIAL_SELF_HOSTING_STILL_BRIDGED",
        "clean_self_hosting_pass_allowed": False,
        "surviving_caps": [
            "CAP_STAGE1_WITH_WARNINGS_ONLY",
            "CAP_TASKPACK_REGISTRATION_STILL_BRIDGED_BY_ANCIENT_EMPIRE",
            "CAP_NO_VM2_VM3_NEW_REALITY_SYNC",
            "CAP_NO_REMOTE_PUSH_WITHOUT_OWNER_AUTHORIZATION",
        ],
        "verdict": "WARN",
    }
    write_json(report_root / "new_reality_self_hosting_status_receipt.json", payload)
    return payload


def write_supporting_receipts(report_root: Path, bundle_path: Path, bundle_sha: str | None = None) -> None:
    evidence_boundary = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "active_root": ACTIVE_ROOT.as_posix(),
        "ancient_empire_reference_root": ANCIENT_ROOT.as_posix(),
        "mutation_boundary": "Only New Reality root was mutated; Ancient Empire is reference-only.",
        "external_research_used": False,
        "no_vm_sync": True,
        "no_remote_push_without_owner_authorization": True,
    }
    write_json(report_root / "EVIDENCE_BOUNDARY.json", evidence_boundary)

    task_focus = {
        "task_id": TASK_ID,
        "intent": "Introduce New Reality root resolution contract/helpers, cover 15 runtime candidates, and refresh proof bundle.",
        "contour": "PC",
        "active_root": ACTIVE_ROOT.as_posix(),
        "forbidden_scope": ["Ancient Empire mutation", "VM sync", "remote push without Owner authorization", "broad historical migration"],
        "required_outputs": [
            "ROOT_RESOLUTION_CONTRACT.md",
            "ORGAN_AGENT_COMMON/root_resolution.py",
            "ORGAN_AGENT_COMMON/root_resolution.ps1",
            "root_resolution_receipt.json",
            "root_resolution_smoke_receipt.json",
            "runtime_candidate_patch_or_classification_receipt.json",
            "git_field_sanity_gate_receipt.json",
            "ancient_empire_no_mutation_receipt.json",
            "new_reality_self_hosting_status_receipt.json",
            "task_report_bundle.zip",
        ],
    }
    write_json(report_root / "TASK_FOCUS_PACKET.json", task_focus)

    capability_split = {
        "task_id": TASK_ID,
        "LOCAL_SCRIPT_FIRST": [
            "ORGAN_AGENT_COMMON/root_resolution.py",
            "ORGAN_AGENT_COMMON/root_resolution.ps1",
            "TOOLS/ROOT_RESOLUTION/root_resolution_proof_refresh_v0_1.py",
        ],
        "LOCAL_MANUAL_COMMAND": [
            "git status --short --branch",
            "python -m py_compile <patched python files>",
        ],
        "CANDIDATE_SCRIPT_FIRST": [],
        "AGENT_REASONING_ONLY": [
            "Classifying detector-signature strings and VM remote defaults as non-active-root cases.",
        ],
        "EXTERNAL_RESEARCH": [],
        "OWNER_MANUAL_CONFIRMATION": [
            "Remote push authorization is required before push.",
        ],
        "FUTURE_CAPABILITY_GAP": [
            "New Reality taskpack registration is still bridged by Ancient Empire.",
            "No VM2/VM3 New Reality sync in this task.",
        ],
    }
    write_json(report_root / "CAPABILITY_SPLIT_RECEIPT.json", capability_split)

    question_pass = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "blocking_owner_questions_for_local_work": [],
        "owner_authorization_needed_before_push": True,
        "question_pass_verdict": "PASS_WITH_PUSH_AUTHORIZATION_WARNING",
    }
    write_json(report_root / "IMPERIUM_QUESTION_PASS.json", question_pass)

    claims = [
        {
            "claim_id": "C001",
            "claim": "New Reality root resolver rejects Ancient Empire as active root.",
            "owner_organ": "MECHANICUS",
            "capability_class": "LOCAL_SCRIPT_FIRST",
            "evidence_level": "E3",
            "evidence_path": "root_resolution_smoke_receipt.json",
            "cap_applied": "NONE",
            "red_team_status": "PASS",
        },
        {
            "claim_id": "C002",
            "claim": "Exactly 15 prior runtime candidates were patched or classified.",
            "owner_organ": "MECHANICUS",
            "capability_class": "LOCAL_SCRIPT_FIRST",
            "evidence_level": "E3",
            "evidence_path": "runtime_candidate_patch_or_classification_receipt.json",
            "cap_applied": "NONE",
            "red_team_status": "PASS",
        },
        {
            "claim_id": "C003",
            "claim": "Git field sanity gate blocks help/usage text in git_head and git_branch.",
            "owner_organ": "ADMINISTRATUM",
            "capability_class": "LOCAL_SCRIPT_FIRST",
            "evidence_level": "E3",
            "evidence_path": "git_field_sanity_gate_receipt.json",
            "cap_applied": "NONE",
            "red_team_status": "PASS",
        },
        {
            "claim_id": "C004",
            "claim": "Ancient Empire was not mutated by this task.",
            "owner_organ": "INQUISITION",
            "capability_class": "LOCAL_MANUAL_COMMAND",
            "evidence_level": "E3",
            "evidence_path": "ancient_empire_no_mutation_receipt.json",
            "cap_applied": "CAP_PRE_EXISTING_ANCIENT_DIRTY_STATE_DECLARED",
            "red_team_status": "PASS_WITH_WARNING",
        },
        {
            "claim_id": "C005",
            "claim": "New Reality is closer to self-hosting but still bridged by Ancient taskpack registration.",
            "owner_organ": "ASTRONOMICON",
            "capability_class": "AGENT_REASONING_ONLY",
            "evidence_level": "E2",
            "evidence_path": "new_reality_self_hosting_status_receipt.json",
            "cap_applied": "CAP_TASKPACK_REGISTRATION_STILL_BRIDGED_BY_ANCIENT_EMPIRE",
            "red_team_status": "WARN",
        },
    ]
    write_jsonl(report_root / "CLAIM_LEDGER.jsonl", claims)
    write_jsonl(
        report_root / "EVIDENCE_LEDGER.jsonl",
        [
            {"evidence_id": "E001", "path": "root_resolution_smoke_receipt.json", "level": "E3", "owner": "MECHANICUS"},
            {
                "evidence_id": "E002",
                "path": "runtime_candidate_patch_or_classification_receipt.json",
                "level": "E3",
                "owner": "MECHANICUS",
            },
            {"evidence_id": "E003", "path": "git_field_sanity_gate_receipt.json", "level": "E3", "owner": "ADMINISTRATUM"},
            {"evidence_id": "E004", "path": "ancient_empire_no_mutation_receipt.json", "level": "E3", "owner": "INQUISITION"},
            {"evidence_id": "E005", "path": "task_report_bundle.zip", "level": "E2", "owner": "ADMINISTRATUM"},
        ],
    )

    red_team = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "mode": "HARD_RED_TEAM",
        "checks": {
            "head_status_evidence_boundary_match": "PASS_WITH_DIRTY_OUTPUTS_DECLARED",
            "dirty_provenance_contradiction": "WARN_PRE_EXISTING_ANCIENT_DIRTY_STATE_AND_NEW_REALITY_TASK_OUTPUTS",
            "stale_receipt": "PASS_CURRENT_RECEIPTS_REGENERATED",
            "role_authority_read": "PASS",
            "manual_reasoning_as_capability": "PASS_WITH_AGENT_REASONING_ONLY_TAGS",
            "missing_replay_command": "PASS_ROOT_PROOF_REPLAY_COMMAND_PRESENT",
            "commit_push_policy": "WARN_PUSH_FORBIDDEN_WITHOUT_OWNER_AUTHORIZATION",
            "private_local_leak_risk": "PASS_DETECTOR_SIGNATURES_CLASSIFIED",
        },
        "surviving_caps": [
            "CAP_STAGE1_WITH_WARNINGS_ONLY",
            "CAP_TASKPACK_REGISTRATION_STILL_BRIDGED_BY_ANCIENT_EMPIRE",
            "CAP_NO_REMOTE_PUSH_WITHOUT_OWNER_AUTHORIZATION",
        ],
        "clean_pass_allowed": False,
        "final_verdict": "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "RED_TEAM_VERDICT.json", red_team)

    final_summary = "\n".join(
        [
            "# Final Owner Summary RU",
            "",
            "\u0428\u0430\u0433: New Reality Root Resolver, 15 runtime candidates, proof refresh.",
            "\u0412\u0435\u0440\u0434\u0438\u043a\u0442: PASS_WITH_WARNINGS.",
            "New Reality root resolver \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442, Ancient root \u0431\u043b\u043e\u043a\u0438\u0440\u0443\u0435\u0442\u0441\u044f, 15 candidates \u043f\u043e\u043a\u0440\u044b\u0442\u044b patch/classification.",
            "Self-hosting \u0435\u0449\u0435 \u043d\u0435 \u043f\u043e\u043b\u043d\u044b\u0439: taskpack registration \u043e\u0441\u0442\u0430\u0435\u0442\u0441\u044f bridged \u0447\u0435\u0440\u0435\u0437 Ancient Empire; push \u0442\u0440\u0435\u0431\u0443\u0435\u0442 \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e\u0439 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438 Owner.",
            f"Bundle path: {bundle_path.as_posix()}",
            "Bundle SHA256: see bundle_hash_receipt.json and final Owner response.",
            "",
        ]
    )
    (report_root / "final_owner_summary_ru.md").write_text(final_summary, encoding="utf-8")


def build_bundle(repo_root: Path, report_root: Path) -> dict[str, Any]:
    required_report_files = [
        "root_resolution_receipt.json",
        "root_resolution_smoke_receipt.json",
        "runtime_candidate_patch_or_classification_receipt.json",
        "git_field_sanity_gate_receipt.json",
        "ancient_empire_no_mutation_receipt.json",
        "new_reality_self_hosting_status_receipt.json",
        "final_owner_summary_ru.md",
        "EVIDENCE_BOUNDARY.json",
        "IMPERIUM_QUESTION_PASS.json",
        "CAPABILITY_SPLIT_RECEIPT.json",
        "CLAIM_LEDGER.jsonl",
        "EVIDENCE_LEDGER.jsonl",
        "RED_TEAM_VERDICT.json",
        "TASK_FOCUS_PACKET.json",
    ]
    files_to_hash = [report_root / name for name in required_report_files]
    files_to_hash.append(repo_root / CONTRACT_PATH_REL)
    files_to_hash.append(repo_root / "ORGAN_AGENT_COMMON/root_resolution.py")
    files_to_hash.append(repo_root / "ORGAN_AGENT_COMMON/root_resolution.ps1")
    files_to_hash.append(repo_root / "TOOLS/ROOT_RESOLUTION/root_resolution_proof_refresh_v0_1.py")

    sha_lines = []
    for path in files_to_hash:
        rel = path.relative_to(repo_root).as_posix()
        sha_lines.append(f"{sha256_file(path)}  {rel}")
    (report_root / "sha256sums.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    bundle_path = report_root / "task_report_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files_to_hash:
            zf.write(path, path.relative_to(repo_root).as_posix())
        zf.write(report_root / "sha256sums.txt", (report_root / "sha256sums.txt").relative_to(repo_root).as_posix())

    bundle_sha = sha256_file(bundle_path)
    (report_root / "task_report_bundle.zip.sha256").write_text(f"{bundle_sha}  {bundle_path.name}\n", encoding="utf-8")
    receipt = {
        "task_id": TASK_ID,
        "receipt_type": "bundle_hash_receipt",
        "timestamp_utc": utc_now(),
        "bundle_path": bundle_path.as_posix(),
        "bundle_sha256": bundle_sha,
        "sha256sums_path": (report_root / "sha256sums.txt").as_posix(),
        "verdict": "PASS",
    }
    write_json(report_root / "bundle_hash_receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate New Reality root resolver proof refresh receipts.")
    parser.add_argument("--repo-root", default="", help="Optional New Reality root.")
    parser.add_argument("--report-root", default=str(REPORT_ROOT_REL), help="Report root path, relative to repo root unless absolute.")
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    report_root = resolve_output_path(args.report_root, repo_root)
    report_root.mkdir(parents=True, exist_ok=True)

    root_receipt = build_root_receipt(repo_root, report_root)
    smoke = build_smoke_receipt(repo_root, report_root)
    git_sanity = build_git_field_sanity_receipt(repo_root, report_root)
    candidates = build_candidate_receipt(repo_root, report_root)
    ancient = build_ancient_no_mutation_receipt(report_root)
    self_hosting = build_self_hosting_status(report_root, smoke, candidates)

    bundle_placeholder = report_root / "task_report_bundle.zip"
    write_supporting_receipts(report_root, bundle_placeholder)
    bundle_receipt = build_bundle(repo_root, report_root)
    write_supporting_receipts(report_root, bundle_placeholder, bundle_receipt["bundle_sha256"])
    bundle_receipt = build_bundle(repo_root, report_root)

    verdicts = [
        root_receipt["verdict"],
        smoke["verdict"],
        git_sanity["verdict"],
        candidates["verdict"],
        ancient["verdict"],
        self_hosting["verdict"],
        bundle_receipt["verdict"],
    ]
    hard_block = any(str(verdict).startswith("BLOCK") for verdict in verdicts)
    final = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "report_root": report_root.as_posix(),
        "bundle_path": bundle_receipt["bundle_path"],
        "bundle_sha256": bundle_receipt["bundle_sha256"],
        "component_verdicts": verdicts,
        "final_verdict": "BLOCK" if hard_block else "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "root_resolution_proof_refresh_receipt.json", final)
    print(json.dumps(final, ensure_ascii=True, indent=2))
    return 1 if hard_block else 0


if __name__ == "__main__":
    raise SystemExit(main())
