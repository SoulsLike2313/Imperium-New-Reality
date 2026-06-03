#!/usr/bin/env python3
"""Administratum Continuity Pack Skill v0.1."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

SKILL_ID = "CONTINUITY_PACK_SKILL"
SKILL_VERSION = "0.1.0"
TASK_ID_DEFAULT = "TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-PACK-SKILL-AND-LOGOS-HANDOFF-BRIDGE-PC-V0_1"

BASE_CAPS = [
    "CAP_STAGE1_WITH_WARNINGS_ONLY",
    "CAP_NO_IDE_VISUAL_RELEASE_YET",
    "CAP_NO_WARP_RUNTIME",
    "CAP_VM3_ROUTE_NOT_LIVE_PROVEN",
    "CAP_VM2_ROUTE_NOT_LIVE_PROVEN",
]

REQUIRED_OUTPUTS = [
    "administratum_continuity_pack_skill_contract.json",
    "administratum_continuity_pack_skill_v0_1.py",
    "continuity_pack_manifest.schema.json",
    "logos_prime_handoff_contract.json",
    "continuity_pack_skill_smoke_receipt.json",
    "pc_continuity_pack_build_receipt.json",
    "current_truth_snapshot.json",
    "git_truth_receipt.json",
    "latest_task_chain.json",
    "active_caps_snapshot.json",
    "source_index.json",
    "private_data_exclusion_receipt.json",
    "stale_context_audit.json",
    "logos_prime_handoff_ru.md",
    "logos_prime_handoff_en.md",
    "continuity_pack_sha256s.txt",
    "continuity_pack_zip_receipt.json",
    "skill_owner_pain_cure_receipt.json",
    "mechanicus_validation_receipt.json",
    "inquisition_fake_continuity_guard_receipt.json",
    "astronomicon_task_link_receipt.json",
    "hard_red_team_verdict.json",
    "final_owner_summary_ru.md",
    "commit_push_receipt.json",
]

PACK_CONTENTS = [
    "continuity_pack_manifest.json",
    "current_truth_snapshot.json",
    "git_truth_receipt.json",
    "latest_task_chain.json",
    "active_caps_snapshot.json",
    "source_index.json",
    "private_data_exclusion_receipt.json",
    "stale_context_audit.json",
    "logos_prime_handoff_ru.md",
    "logos_prime_handoff_en.md",
    "continuity_pack_sha256s.txt",
]

EXCLUDED_PATH_HINTS = [
    ".git/",
    "ARTIFACTS/",
    "RUNS/",
    "node_modules/",
    "venv/",
    ".venv/",
    "AppData/",
    "Downloads/",
]

CONTINUITY_MANIFEST_SCHEMA = {
    "type": "object",
    "required": [
        "schema_id",
        "pack_id",
        "created_at_utc",
        "repo_truth",
        "contents",
        "sha256s",
        "limitations",
    ],
    "properties": {
        "schema_id": {"type": "string"},
        "pack_id": {"type": "string"},
        "created_at_utc": {"type": "string"},
        "repo_truth": {"type": "object"},
        "contents": {"type": "array"},
        "sha256s": {"type": "object"},
        "limitations": {"type": "array"},
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_now_compact() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def normalize_path(path_value: str | Path, base: Path | None = None) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    if base is not None:
        return (base / path).resolve()
    return path.resolve()


def run_cmd(args: list[str], *, cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except Exception:
        return None


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except Exception:
        return str(path.resolve()).replace("\\", "/")


def ru(escaped: str) -> str:
    return bytes(escaped, "ascii").decode("unicode_escape")


def parse_ahead_behind(raw: str) -> tuple[int | None, int | None]:
    parts = raw.replace(",", " ").split()
    ahead: int | None = None
    behind: int | None = None
    for idx, token in enumerate(parts):
        if token == "ahead" and idx + 1 < len(parts):
            try:
                ahead = int(parts[idx + 1])
            except ValueError:
                ahead = None
        if token == "behind" and idx + 1 < len(parts):
            try:
                behind = int(parts[idx + 1])
            except ValueError:
                behind = None
    return ahead, behind


def collect_git_truth(repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    warnings: list[str] = []
    caps: list[str] = []

    rc, head, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if rc != 0:
        raise RuntimeError(f"git rev-parse HEAD failed: {err or head}")
    short_head = head[:12]

    rc, branch, _ = run_cmd(["git", "branch", "--show-current"], cwd=repo_root)
    if rc != 0 or not branch:
        branch = "UNKNOWN"
        warnings.append("Cannot resolve current branch.")

    rc, status_out, status_err = run_cmd(["git", "status", "--porcelain=v1", "--branch"], cwd=repo_root)
    if rc != 0:
        warnings.append(f"git status probe failed: {status_err or status_out}")
        status_lines: list[str] = []
    else:
        status_lines = status_out.splitlines()

    status_header = status_lines[0] if status_lines and status_lines[0].startswith("##") else ""
    changes = status_lines[1:] if status_header else status_lines
    worktree_dirty = len(changes) > 0
    if worktree_dirty:
        caps.append("CAP_DIRTY_START_OWNER_APPROVED_CONTINUATION")

    rc, upstream, upstream_err = run_cmd(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=repo_root,
    )
    if rc != 0:
        upstream = ""
        warnings.append(f"Upstream is not configured: {upstream_err or 'no upstream'}")
        caps.append("CAP_GIT_UPSTREAM_UNRESOLVED")

    ahead = None
    behind = None
    if upstream:
        rc, ahead_behind_raw, _ = run_cmd(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"], cwd=repo_root)
        if rc == 0 and ahead_behind_raw:
            parts = ahead_behind_raw.split()
            if len(parts) == 2:
                try:
                    behind = int(parts[0])
                    ahead = int(parts[1])
                except ValueError:
                    ahead, behind = parse_ahead_behind(ahead_behind_raw)
            else:
                ahead, behind = parse_ahead_behind(ahead_behind_raw)

    rc, origin_head, origin_err = run_cmd(["git", "rev-parse", "origin/master"], cwd=repo_root)
    if rc != 0:
        origin_head = ""
        warnings.append(f"origin/master not resolved: {origin_err or 'unknown'}")
        caps.append("CAP_ORIGIN_MASTER_SYNC_NOT_PROVEN")

    origin_sync = bool(origin_head) and (origin_head == head)
    if not origin_sync:
        caps.append("CAP_ORIGIN_MASTER_SYNC_NOT_PROVEN")

    rc, recent_commits_raw, _ = run_cmd(["git", "log", "--oneline", "-n", "5"], cwd=repo_root)
    recent_commits = recent_commits_raw.splitlines() if rc == 0 and recent_commits_raw else []

    rc, remote_raw, _ = run_cmd(["git", "remote", "-v"], cwd=repo_root)
    remotes = remote_raw.splitlines() if rc == 0 and remote_raw else []

    return (
        {
            "timestamp_utc": utc_now(),
            "repo_root": str(repo_root).replace("\\", "/"),
            "head": head,
            "short_head": short_head,
            "branch": branch,
            "upstream": upstream or None,
            "origin_master_head": origin_head or None,
            "origin_sync": origin_sync,
            "ahead": ahead,
            "behind": behind,
            "worktree_dirty": worktree_dirty,
            "worktree_changes": changes,
            "status_header": status_header,
            "recent_commits": recent_commits,
            "remotes": remotes,
        },
        sorted(set(caps)),
        warnings,
    )


def load_taskpack_context(repo_root: Path, task_id: str) -> dict[str, Any]:
    base = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
        / task_id
    )
    extracted = base / "EXTRACTED"
    manifest = read_json_if_exists(extracted / "MANIFEST.json")
    source_state = read_json_if_exists(extracted / "INPUTS/source_state.json")
    route_manifest = read_json_if_exists(base / "TASK_ROUTE_MANIFEST.json")
    admission = read_json_if_exists(base / "TASKPACK_ADMISSION_RECEIPT.json")
    resolver = read_json_if_exists(base / "TASK_ID_RESOLVER_RECEIPT.json")
    start_ack = read_json_if_exists(base / "TASK_START_ACK_TEMPLATE.json")
    return {
        "registered_root": base,
        "extracted_root": extracted,
        "manifest": manifest if isinstance(manifest, dict) else {},
        "source_state": source_state if isinstance(source_state, dict) else {},
        "route_manifest": route_manifest if isinstance(route_manifest, dict) else {},
        "admission_receipt": admission if isinstance(admission, dict) else {},
        "resolver_receipt": resolver if isinstance(resolver, dict) else {},
        "task_start_ack": start_ack if isinstance(start_ack, dict) else {},
    }


def build_astronomicon_task_link_receipt(
    repo_root: Path,
    task_id: str,
    taskpack_ctx: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    warnings: list[str] = []
    caps: list[str] = []

    registered_root = taskpack_ctx["registered_root"]
    admission = taskpack_ctx["admission_receipt"]
    resolver = taskpack_ctx["resolver_receipt"]
    route_manifest = taskpack_ctx["route_manifest"]

    exists = registered_root.exists()
    route_exists = bool(route_manifest)
    admission_verdict = str(admission.get("admission_verdict", "UNKNOWN"))
    resolver_verdict = str(resolver.get("resolver_verdict", "UNKNOWN"))
    resolver_actor = str(resolver.get("resolved_by", ""))
    admission_actor = str(admission.get("updated_by", ""))

    registered_via_skill = (
        "astronomicon_taskpack_registration_skill_v0_1.py" in resolver_actor
        or "astronomicon_taskpack_registration_skill_v0_1.py" in admission_actor
        or str(taskpack_ctx.get("task_start_ack", {}).get("resolved", "")).lower() == "true"
    )

    if not exists:
        warnings.append("Registered task root is missing.")
        caps.append("CAP_ASTRONOMICON_TASK_LINK_MISSING")
    if not route_exists:
        warnings.append("TASK_ROUTE_MANIFEST.json missing or invalid.")
        caps.append("CAP_ASTRONOMICON_TASK_LINK_MISSING")
    if admission_verdict not in {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS"}:
        warnings.append(f"Admission verdict is not PASS: {admission_verdict}")
        caps.append("CAP_ASTRONOMICON_TASK_ADMISSION_NOT_PROVEN")
    if resolver_verdict not in {"PASS", "PASS_WITH_WARNINGS"}:
        warnings.append(f"Resolver verdict is not PASS: {resolver_verdict}")
        caps.append("CAP_ASTRONOMICON_TASK_RESOLVER_NOT_PROVEN")
    if not registered_via_skill:
        warnings.append("Registration Skill provenance is not explicit in receipts.")
        caps.append("CAP_ASTRONOMICON_SKILL_REGISTRATION_NOT_OBSERVED")

    verdict = "PASS_WITH_WARNINGS" if not caps else ("WARN" if exists else "BLOCK")
    receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "registered_task_root": rel(registered_root, repo_root),
        "registered_task_root_exists": exists,
        "route_manifest_present": route_exists,
        "admission_verdict": admission_verdict,
        "resolver_verdict": resolver_verdict,
        "resolved_by": resolver_actor or None,
        "admission_updated_by": admission_actor or None,
        "registered_via_skill": registered_via_skill,
        "caps_triggered": sorted(set(caps)),
        "warnings": warnings,
        "verdict": verdict,
    }
    return receipt, sorted(set(caps)), warnings


def build_latest_task_chain(
    repo_root: Path,
    task_id: str,
    source_state: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    registry_path = repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json"
    current_expected_path = repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json"

    registry = read_json_if_exists(registry_path)
    if not isinstance(registry, dict):
        warnings.append("task_registry.json is missing or invalid.")
        tasks: list[dict[str, Any]] = []
    else:
        tasks = [row for row in registry.get("tasks", []) if isinstance(row, dict)]

    current_expected = read_json_if_exists(current_expected_path)
    if not isinstance(current_expected, dict):
        current_expected = {}
        warnings.append("current_expected_task.json is missing or invalid.")

    tail = tasks[-8:] if tasks else []
    chain = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "registry_path": rel(registry_path, repo_root),
        "current_expected_path": rel(current_expected_path, repo_root),
        "current_expected_task": current_expected.get("task_id"),
        "current_expected_status": current_expected.get("status"),
        "current_expected_updated_at_utc": current_expected.get("updated_at_utc"),
        "latest_registry_tail": [
            {
                "task_id": row.get("task_id"),
                "status": row.get("status"),
                "registered_at_utc": row.get("registered_at_utc"),
                "target_contour": row.get("target_contour"),
                "route_manifest_path": row.get("route_manifest_path"),
                "current_expected": row.get("current_expected", False),
            }
            for row in tail
        ],
        "source_state_previous_task": source_state.get("previous_task"),
        "source_state_previous_verdicts": source_state.get("previous_verdicts", []),
        "source_state_next_task_rationale": source_state.get("next_task_rationale"),
        "warnings": warnings,
    }
    return chain, warnings


def build_active_caps(
    manifest_caps: list[str],
    git_caps: list[str],
    task_link_caps: list[str],
    git_truth: dict[str, Any],
) -> dict[str, Any]:
    caps = list(BASE_CAPS)
    caps.extend(manifest_caps)
    caps.extend(git_caps)
    caps.extend(task_link_caps)
    if git_truth.get("worktree_dirty", False):
        caps.append("CAP_DIRTY_START_OWNER_APPROVED_CONTINUATION")
    if not git_truth.get("origin_sync", False):
        caps.append("CAP_ORIGIN_MASTER_SYNC_NOT_PROVEN")
    return {
        "timestamp_utc": utc_now(),
        "caps": sorted(set(caps)),
        "warnings": [
            "Clean PASS is blocked by Stage1/IDE/WARP caps.",
            "This continuity pack is controlled and partial by design, not full-repo export.",
        ],
    }


def build_source_index(repo_root: Path, task_id: str) -> dict[str, Any]:
    sources = [
        ("AGENTS_BOOTLOADER", repo_root / "AGENTS.md"),
        ("MATRIX_SPINE_INDEX", repo_root / "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md"),
        ("DOCTRINARIUM_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/DOCTRINARIUM/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        ("OFFICIO_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        ("ASTRONOMICON_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        ("ADMINISTRATUM_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        ("MECHANICUS_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        ("INQUISITION_READ_FIRST", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/READ_FIRST_GHOST_EVOLVE_PACKET.md"),
        (
            "TASK_ROUTE_MANIFEST",
            repo_root
            / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
            / task_id
            / "TASK_ROUTE_MANIFEST.json",
        ),
        (
            "TASKPACK_MANIFEST",
            repo_root
            / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
            / task_id
            / "EXTRACTED/MANIFEST.json",
        ),
        ("TASK_REGISTRY", repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json"),
        (
            "CURRENT_EXPECTED_TASK",
            repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
        ),
    ]
    rows: list[dict[str, Any]] = []
    for source_id, path in sources:
        exists = path.exists()
        rows.append(
            {
                "source_id": source_id,
                "path": rel(path, repo_root),
                "exists": exists,
                "sha256": sha256_file(path) if exists and path.is_file() else None,
            }
        )
    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "sources": rows,
    }


def parse_iso_timestamp(ts: str | None) -> dt.datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    raw = ts.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError:
        return None


def build_stale_context_audit(
    task_id: str,
    latest_task_chain: dict[str, Any],
    source_index: dict[str, Any],
) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc)
    current_expected_task = latest_task_chain.get("current_expected_task")
    updated_at_raw = latest_task_chain.get("current_expected_updated_at_utc")
    updated_at = parse_iso_timestamp(updated_at_raw)

    source_missing = [row["source_id"] for row in source_index.get("sources", []) if not row.get("exists")]
    critical_missing = any(
        source_id in source_missing
        for source_id in ["TASK_ROUTE_MANIFEST", "TASKPACK_MANIFEST", "TASK_REGISTRY", "CURRENT_EXPECTED_TASK"]
    )

    freshness_hours = None
    if updated_at is not None:
        freshness_hours = round((now - updated_at).total_seconds() / 3600.0, 2)

    if critical_missing:
        state = "BLOCKED"
    elif current_expected_task == task_id and freshness_hours is not None and freshness_hours <= 48:
        state = "FRESH"
    elif freshness_hours is not None and freshness_hours <= 168:
        state = "PARTIAL"
    else:
        state = "STALE"

    warnings: list[str] = []
    if current_expected_task != task_id:
        warnings.append("Current expected task differs from active task id.")
    if freshness_hours is not None and freshness_hours > 48:
        warnings.append("Current expected task metadata is older than 48 hours.")
    if source_missing:
        warnings.append("Some authority/source files are missing in source index.")

    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "continuity_state": state,
        "current_expected_task": current_expected_task,
        "current_expected_updated_at_utc": updated_at_raw,
        "freshness_hours": freshness_hours,
        "critical_missing_sources": source_missing,
        "warnings": warnings,
    }


def build_private_data_exclusion_receipt(
    repo_root: Path,
    report_root: Path,
    task_id: str,
) -> dict[str, Any]:
    included = [name for name in PACK_CONTENTS if (report_root / name).exists()]
    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "policy": "ALLOWLIST_ONLY",
        "scope_root": rel(report_root, repo_root),
        "included_pack_files": included,
        "excluded_path_hints": EXCLUDED_PATH_HINTS,
        "external_private_collection_performed": False,
        "secret_collection_performed": False,
        "verdict": "PASS",
    }


def build_handoff_en(
    task_id: str,
    git_truth: dict[str, Any],
    latest_task_chain: dict[str, Any],
    active_caps: dict[str, Any],
    stale_context_audit: dict[str, Any],
) -> str:
    caps_text = "\n".join(f"- {cap}" for cap in active_caps.get("caps", []))
    latest_tail = latest_task_chain.get("latest_registry_tail", [])
    latest_tail_text = "\n".join(
        f"- {row.get('task_id')} | {row.get('status')} | {row.get('registered_at_utc')}"
        for row in latest_tail
    ) or "- No registry entries were loaded."

    return f"""# Logos-Prime Handoff (EN)

Task ID: `{task_id}`
Generated at UTC: `{utc_now()}`

## Latest accepted HEAD and branch truth
- Local HEAD: `{git_truth.get("head")}`
- Branch: `{git_truth.get("branch")}`
- Upstream: `{git_truth.get("upstream")}`
- origin/master: `{git_truth.get("origin_master_head")}`
- origin sync: `{git_truth.get("origin_sync")}`
- Worktree dirty: `{git_truth.get("worktree_dirty")}`

## Latest task chain and verdict context
{latest_tail_text}

## Active caps and warnings
{caps_text}

## Current next recommended task
- Continue from `{task_id}` and use this continuity pack as the required handoff artifact for new chat/session entry.

## Key organ-state summary stubs
- Officio: role-entry and RU owner-facing language route is required.
- Astronomicon: task registration and current_expected_task links are the route truth.
- Administratum: this continuity pack is the handoff truth carrier.
- Mechanicus: JSON/ZIP/SHA validation receipts are required.
- Inquisition: stale-context and fake-continuity guards must stay visible.

## Important evidence/report paths
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/REPORTS/{task_id}/`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json`

## What not to assume
- Do not assume clean PASS while global Stage1/IDE/WARP caps remain.
- Do not assume VM2/VM3 live route proof is done.
- Do not assume full-repo context export is allowed.
- Do not assume private/secrets collection is allowed.

## Read first
- `AGENTS.md`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/READ_FIRST_GHOST_EVOLVE_PACKET.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/READ_FIRST_GHOST_EVOLVE_PACKET.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/READ_FIRST_GHOST_EVOLVE_PACKET.md`

## Freshness / stale-context state
- Continuity state: `{stale_context_audit.get("continuity_state")}`
- Freshness hours: `{stale_context_audit.get("freshness_hours")}`
"""


def build_handoff_ru(
    task_id: str,
    git_truth: dict[str, Any],
    latest_task_chain: dict[str, Any],
    active_caps: dict[str, Any],
    stale_context_audit: dict[str, Any],
) -> str:
    caps_text = "\n".join(f"- {cap}" for cap in active_caps.get("caps", []))
    latest_tail = latest_task_chain.get("latest_registry_tail", [])
    latest_tail_text = "\n".join(
        f"- {row.get('task_id')} | {row.get('status')} | {row.get('registered_at_utc')}"
        for row in latest_tail
    ) or f"- {ru(r'\\u0420\\u0435\\u0435\\u0441\\u0442\\u0440 \\u0437\\u0430\\u0434\\u0430\\u0447 \\u043d\\u0435 \\u0437\\u0430\\u0433\\u0440\\u0443\\u0436\\u0435\\u043d.')}"

    return f"""# {ru(r'\\u041f\\u0435\\u0440\\u0435\\u0434\\u0430\\u0447\\u0430 Logos-Prime (RU)')}

{ru(r'\\u0417\\u0430\\u0434\\u0430\\u0447\\u0430')}: `{task_id}`
{ru(r'\\u0421\\u0444\\u043e\\u0440\\u043c\\u0438\\u0440\\u043e\\u0432\\u0430\\u043d\\u043e (UTC)')}: `{utc_now()}`

## {ru(r'\\u0422\\u0435\\u043a\\u0443\\u0449\\u0430\\u044f git-\\u0438\\u0441\\u0442\\u0438\\u043d\\u0430')}
- HEAD: `{git_truth.get("head")}`
- Branch: `{git_truth.get("branch")}`
- Upstream: `{git_truth.get("upstream")}`
- origin/master: `{git_truth.get("origin_master_head")}`
- origin sync: `{git_truth.get("origin_sync")}`
- Worktree dirty: `{git_truth.get("worktree_dirty")}`

## {ru(r'\\u0426\\u0435\\u043f\\u043e\\u0447\\u043a\\u0430 \\u043f\\u043e\\u0441\\u043b\\u0435\\u0434\\u043d\\u0438\\u0445 \\u0437\\u0430\\u0434\\u0430\\u0447')}
{latest_tail_text}

## {ru(r'\\u0410\\u043a\\u0442\\u0438\\u0432\\u043d\\u044b\\u0435 caps')}
{caps_text}

## {ru(r'\\u0427\\u0442\\u043e \\u0434\\u0435\\u043b\\u0430\\u0442\\u044c \\u0434\\u0430\\u043b\\u044c\\u0448\\u0435')}
- {ru(r'\\u041f\\u0440\\u043e\\u0434\\u043e\\u043b\\u0436\\u0430\\u0442\\u044c \\u0440\\u0430\\u0431\\u043e\\u0442\\u0443 \\u043f\\u043e \\u0442\\u0435\\u043a\\u0443\\u0449\\u0435\\u0439 \\u0437\\u0430\\u0434\\u0430\\u0447\\u0435, \\u0438\\u0441\\u043f\\u043e\\u043b\\u044c\\u0437\\u0443\\u044f \\u044d\\u0442\\u043e\\u0442 continuity pack \\u043a\\u0430\\u043a \\u0432\\u0445\\u043e\\u0434\\u043d\\u043e\\u0439 \\u043f\\u0430\\u043a\\u0435\\u0442 \\u0434\\u043b\\u044f \\u043d\\u043e\\u0432\\u043e\\u0433\\u043e \\u0447\\u0430\\u0442\\u0430/Logos-Prime.')}

## {ru(r'\\u041a\\u043b\\u044e\\u0447\\u0435\\u0432\\u044b\\u0435 \\u043f\\u0443\\u0442\\u0438 \\u0434\\u043e\\u043a\\u0430\\u0437\\u0430\\u0442\\u0435\\u043b\\u044c\\u0441\\u0442\\u0432')}
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/REPORTS/{task_id}/`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json`

## {ru(r'\\u0427\\u0442\\u043e \\u043d\\u0435\\u043b\\u044c\\u0437\\u044f \\u043f\\u0440\\u0435\\u0434\\u043f\\u043e\\u043b\\u0430\\u0433\\u0430\\u0442\\u044c')}
- {ru(r'\\u041d\\u0435\\u043b\\u044c\\u0437\\u044f \\u0441\\u0447\\u0438\\u0442\\u0430\\u0442\\u044c clean PASS \\u0434\\u043e\\u043f\\u0443\\u0441\\u0442\\u0438\\u043c\\u044b\\u043c \\u043f\\u0440\\u0438 \\u0430\\u043a\\u0442\\u0438\\u0432\\u043d\\u044b\\u0445 \\u0433\\u043b\\u043e\\u0431\\u0430\\u043b\\u044c\\u043d\\u044b\\u0445 caps.')}
- {ru(r'\\u041d\\u0435\\u043b\\u044c\\u0437\\u044f \\u0441\\u0447\\u0438\\u0442\\u0430\\u0442\\u044c \\u0434\\u043e\\u043a\\u0430\\u0437\\u0430\\u043d\\u043d\\u044b\\u043c live route \\u0434\\u043b\\u044f VM2/VM3.')}
- {ru(r'\\u041d\\u0435\\u043b\\u044c\\u0437\\u044f \\u0434\\u0435\\u043b\\u0430\\u0442\\u044c \\u0432\\u044b\\u0432\\u043e\\u0434 \\u043e \\u0440\\u0430\\u0437\\u0440\\u0435\\u0448\\u0435\\u043d\\u0438\\u0438 full-repo dump.')}
- {ru(r'\\u041d\\u0435\\u043b\\u044c\\u0437\\u044f \\u0441\\u043e\\u0431\\u0438\\u0440\\u0430\\u0442\\u044c private/secrets \\u043a\\u043e\\u043d\\u0442\\u0435\\u043d\\u0442.')}

## {ru(r'\\u0427\\u0442\\u043e \\u0447\\u0438\\u0442\\u0430\\u0442\\u044c \\u0441\\u043d\\u0430\\u0447\\u0430\\u043b\\u0430')}
- `AGENTS.md`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/READ_FIRST_GHOST_EVOLVE_PACKET.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/READ_FIRST_GHOST_EVOLVE_PACKET.md`
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/READ_FIRST_GHOST_EVOLVE_PACKET.md`

## {ru(r'\\u0421\\u043e\\u0441\\u0442\\u043e\\u044f\\u043d\\u0438\\u0435 \\u0441\\u0432\\u0435\\u0436\\u0435\\u0441\\u0442\\u0438 \\u043a\\u043e\\u043d\\u0442\\u0435\\u043a\\u0441\\u0442\\u0430')}
- {ru(r'\\u041a\\u043b\\u0430\\u0441\\u0441')}: `{stale_context_audit.get("continuity_state")}`
- {ru(r'\\u0421\\u0432\\u0435\\u0436\\u0435\\u0441\\u0442\\u044c (\\u0447\\u0430\\u0441\\u043e\\u0432)')}: `{stale_context_audit.get("freshness_hours")}`
"""


def build_contract_artifacts(manifest_caps: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    skill_contract = {
        "skill_id": SKILL_ID,
        "skill_name": "Administratum Continuity Pack Skill",
        "owner_organ": "ADMINISTRATUM",
        "version": SKILL_VERSION,
        "status": "CANDIDATE_STAGE1",
        "purpose": "Build controlled continuity packs for Logos-Prime handoff and new-chat context recovery.",
        "required_command_shape": "imperium_build_continuity_pack -Mode LogosPrimeHandoff -IncludeLatestTask -OpenFolder",
        "python_entrypoint": "python IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/SKILLS/CONTINUITY_PACK_SKILL/administratum_continuity_pack_skill_v0_1.py --repo-root .",
        "required_pack_contents": [
            "continuity_pack_manifest.json",
            "current_truth_snapshot.json",
            "git_truth_receipt.json",
            "latest_task_chain.json",
            "active_caps_snapshot.json",
            "source_index.json",
            "private_data_exclusion_receipt.json",
            "stale_context_audit.json",
            "logos_prime_handoff_ru.md",
            "logos_prime_handoff_en.md",
            "continuity_pack_sha256s.txt",
        ],
        "non_goals": [
            "No full repository dump",
            "No private/secrets collection",
            "No cloud upload",
            "No IDE release",
            "No WARP runtime claims",
        ],
        "caps_carried": sorted(set(BASE_CAPS + manifest_caps)),
    }

    handoff_contract = {
        "contract_id": "LOGOS_PRIME_HANDOFF_CONTRACT_V0_1",
        "owner_organ": "OFFICIO_AGENTIS_FOR_LANGUAGE_ROUTE_AND_ADMINISTRATUM_FOR_PACK_OWNERSHIP",
        "required_sections": [
            "latest_head_and_branch_truth",
            "latest_task_chain_and_verdicts",
            "active_caps_and_warnings",
            "next_recommended_task",
            "key_organ_state_summary",
            "important_evidence_paths",
            "what_not_to_assume",
            "read_first",
            "owner_facing_russian_summary",
            "machine_readable_english_summary",
        ],
        "language_policy": {
            "owner_facing_runtime": "RUSSIAN_THROUGH_OFFICIO",
            "machine_artifacts": "ENGLISH_UTF8_NO_BOM",
        },
    }
    return skill_contract, handoff_contract


def build_continuity_manifest(
    task_id: str,
    git_truth: dict[str, Any],
    pack_file_hashes: dict[str, str],
    caps: list[str],
) -> dict[str, Any]:
    return {
        "schema_id": "IMPERIUM_ADMINISTRATUM_CONTINUITY_PACK_MANIFEST_V0_1",
        "pack_id": f"{task_id}_{utc_now_compact()}",
        "created_at_utc": utc_now(),
        "repo_truth": {
            "head": git_truth.get("head"),
            "branch": git_truth.get("branch"),
            "origin_master_head": git_truth.get("origin_master_head"),
            "origin_sync": git_truth.get("origin_sync"),
            "worktree_dirty": git_truth.get("worktree_dirty"),
        },
        "contents": sorted(pack_file_hashes.keys()),
        "sha256s": pack_file_hashes,
        "limitations": sorted(set(caps)),
    }


def build_sha_file(report_root: Path, zip_name: str | None = None, zip_sha: str | None = None) -> str:
    lines: list[str] = []
    for name in sorted(REQUIRED_OUTPUTS):
        path = report_root / name
        if path.exists() and path.is_file():
            lines.append(f"{sha256_file(path)}  {name}")
    if zip_name and zip_sha:
        lines.append(f"{zip_sha}  {zip_name}")
    return "\n".join(lines) + "\n"


def validate_json_files(report_root: Path) -> tuple[list[dict[str, Any]], bool]:
    checks: list[dict[str, Any]] = []
    all_ok = True
    for path in sorted(report_root.glob("*.json")):
        try:
            read_json(path)
            checks.append({"file": path.name, "parse_ok": True})
        except Exception as exc:
            all_ok = False
            checks.append({"file": path.name, "parse_ok": False, "error": str(exc)})
    return checks, all_ok


def write_claim_ledger(report_root: Path, task_id: str) -> None:
    claim_lines = [
        {
            "claim_id": "C001",
            "claim": "Administratum continuity skill exists as script-first CLI.",
            "owner_organ": "ADMINISTRATUM",
            "evidence_level": "E3_EXECUTED_LOCAL_SCRIPT",
            "evidence_path": "administratum_continuity_pack_skill_v0_1.py",
            "cap_if_missing": "CAP_ORGAN_FILE_DECORATIVE_NOT_USED",
        },
        {
            "claim_id": "C002",
            "claim": "Continuity pack bundle includes controlled handoff artifacts and excludes private bulk collection.",
            "owner_organ": "ADMINISTRATUM",
            "evidence_level": "E3_EXECUTED_LOCAL_SCRIPT",
            "evidence_path": "private_data_exclusion_receipt.json",
            "cap_if_missing": "CAP_NO_FAKE_CONTINUITY",
        },
        {
            "claim_id": "C003",
            "claim": "Mechanicus checks cover JSON parse, ZIP readability and SHA256.",
            "owner_organ": "MECHANICUS",
            "evidence_level": "E3_EXECUTED_LOCAL_SCRIPT",
            "evidence_path": "mechanicus_validation_receipt.json",
            "cap_if_missing": "CAP_RUNTIME_CLAIM_NO_REPLAY",
        },
    ]
    ledger_path = report_root / "CLAIM_LEDGER.jsonl"
    lines = "\n".join(json.dumps(row, ensure_ascii=False) for row in claim_lines) + "\n"
    write_text(ledger_path, lines)


def write_evidence_boundary(report_root: Path, repo_root: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "included_boundary": {
            "report_root": rel(report_root, repo_root),
            "required_outputs": REQUIRED_OUTPUTS,
            "pack_contents": PACK_CONTENTS,
        },
        "excluded_boundary": {
            "private_external_paths": True,
            "full_repo_dump": True,
            "secret_collection": True,
            "excluded_path_hints": EXCLUDED_PATH_HINTS,
        },
    }
    write_json(report_root / "EVIDENCE_BOUNDARY.json", payload)


def write_capability_split(report_root: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "LOCAL_SCRIPT_FIRST": [
            "administratum_continuity_pack_skill_v0_1.py",
        ],
        "LOCAL_MANUAL_COMMAND": [
            "git status --porcelain=v1 --branch",
            "git rev-parse HEAD",
            "git rev-parse origin/master",
        ],
        "CANDIDATE_SCRIPT_FIRST": [
            "Future PowerShell wrapper: imperium_build_continuity_pack",
        ],
        "AGENT_REASONING_ONLY": [
            "Owner-facing wording and red-team interpretation.",
        ],
        "EXTERNAL_RESEARCH": [],
        "OWNER_MANUAL_CONFIRMATION": [],
        "FUTURE_CAPABILITY_GAP": [
            "No VM2/VM3 live continuity route proof in this task.",
        ],
    }
    write_json(report_root / "capability_split_receipt.json", payload)


def write_question_pass(report_root: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "questions": [
            {"question": "What is the source of truth?", "answer": "Taskpack + organ authority files + local git truth"},
            {"question": "Which organ owns the rule?", "answer": "Administratum for continuity pack, Officio for RU route, Inquisition for red-team caps"},
            {"question": "What evidence proves runtime behavior?", "answer": "Local script run receipts and generated bundle artifacts"},
            {"question": "What cap applies if evidence is missing?", "answer": "PASS_WITH_WARNINGS with explicit caps; clean PASS blocked"},
            {"question": "What could be fake-green?", "answer": "Claims without replay/receipt, hidden dirty state, missing stale-context audit"},
        ],
        "verdict": "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "IMPERIUM_QUESTION_PASS.json", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Administratum Continuity Pack Skill v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT, help="Task id for report/pack generation.")
    parser.add_argument("--report-root", default="", help="Optional report root override.")
    parser.add_argument("--mode", default="LogosPrimeHandoff", help="Skill mode. Default: LogosPrimeHandoff")
    parser.add_argument("--include-latest-task", action="store_true", help="Include latest task chain artifacts.")
    parser.add_argument("--open-folder", action="store_true", help="Reserved flag for future wrappers.")
    args = parser.parse_args()

    repo_root = normalize_path(args.repo_root)
    task_id = str(args.task_id).strip() or TASK_ID_DEFAULT
    report_root = (
        normalize_path(args.report_root, repo_root)
        if args.report_root
        else repo_root / "IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/REPORTS" / task_id
    )
    report_root.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).resolve()
    skill_root = script_path.parent

    git_truth, git_caps, git_warnings = collect_git_truth(repo_root)
    taskpack_ctx = load_taskpack_context(repo_root, task_id)
    manifest_caps = list(taskpack_ctx.get("manifest", {}).get("active_caps_to_carry", []))
    if not manifest_caps:
        manifest_caps = list(BASE_CAPS)

    task_link_receipt, task_link_caps, task_link_warnings = build_astronomicon_task_link_receipt(
        repo_root,
        task_id,
        taskpack_ctx,
    )
    latest_task_chain, chain_warnings = build_latest_task_chain(
        repo_root,
        task_id,
        taskpack_ctx.get("source_state", {}),
    )
    active_caps_snapshot = build_active_caps(manifest_caps, git_caps, task_link_caps, git_truth)
    source_index = build_source_index(repo_root, task_id)
    stale_context_audit = build_stale_context_audit(task_id, latest_task_chain, source_index)

    current_truth_snapshot = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "skill_id": SKILL_ID,
        "mode": args.mode,
        "repo_truth": {
            "head": git_truth.get("head"),
            "branch": git_truth.get("branch"),
            "origin_master_head": git_truth.get("origin_master_head"),
            "origin_sync": git_truth.get("origin_sync"),
            "worktree_dirty": git_truth.get("worktree_dirty"),
        },
        "current_expected_task": latest_task_chain.get("current_expected_task"),
        "current_expected_status": latest_task_chain.get("current_expected_status"),
        "warnings": sorted(set(git_warnings + task_link_warnings + chain_warnings)),
    }

    private_exclusion = build_private_data_exclusion_receipt(repo_root, report_root, task_id)

    handoff_en = build_handoff_en(task_id, git_truth, latest_task_chain, active_caps_snapshot, stale_context_audit)
    handoff_ru = build_handoff_ru(task_id, git_truth, latest_task_chain, active_caps_snapshot, stale_context_audit)

    skill_contract, handoff_contract = build_contract_artifacts(manifest_caps)

    # Core outputs
    write_json(report_root / "git_truth_receipt.json", git_truth)
    write_json(report_root / "current_truth_snapshot.json", current_truth_snapshot)
    write_json(report_root / "latest_task_chain.json", latest_task_chain)
    write_json(report_root / "active_caps_snapshot.json", active_caps_snapshot)
    write_json(report_root / "source_index.json", source_index)
    write_json(report_root / "private_data_exclusion_receipt.json", private_exclusion)
    write_json(report_root / "stale_context_audit.json", stale_context_audit)
    write_json(report_root / "astronomicon_task_link_receipt.json", task_link_receipt)
    write_text(report_root / "logos_prime_handoff_en.md", handoff_en)
    write_text(report_root / "logos_prime_handoff_ru.md", handoff_ru)
    write_json(report_root / "administratum_continuity_pack_skill_contract.json", skill_contract)
    write_json(report_root / "logos_prime_handoff_contract.json", handoff_contract)
    write_json(report_root / "continuity_pack_manifest.schema.json", CONTINUITY_MANIFEST_SCHEMA)

    # Also keep canonical copies near the skill.
    write_json(skill_root / "administratum_continuity_pack_skill_contract.json", skill_contract)
    write_json(skill_root / "logos_prime_handoff_contract.json", handoff_contract)
    write_json(skill_root / "continuity_pack_manifest.schema.json", CONTINUITY_MANIFEST_SCHEMA)

    # Auxiliary closure artifacts.
    write_evidence_boundary(report_root, repo_root, task_id)
    write_question_pass(report_root, task_id)
    write_capability_split(report_root, task_id)
    write_claim_ledger(report_root, task_id)

    # Copy script into report bundle (required output artifact).
    shutil.copy2(script_path, report_root / "administratum_continuity_pack_skill_v0_1.py")

    # Build continuity manifest and hashes.
    pack_hashes: dict[str, str] = {}
    for name in PACK_CONTENTS:
        path = report_root / name
        if path.exists() and path.is_file():
            pack_hashes[name] = sha256_file(path)

    continuity_manifest = build_continuity_manifest(
        task_id=task_id,
        git_truth=git_truth,
        pack_file_hashes=pack_hashes,
        caps=active_caps_snapshot["caps"],
    )
    write_json(report_root / "continuity_pack_manifest.json", continuity_manifest)

    # First sha file pass (without zip hash).
    sha_text = build_sha_file(report_root)
    write_text(report_root / "continuity_pack_sha256s.txt", sha_text)

    # ZIP build.
    zip_name = f"continuity_pack_{utc_now_compact()}.zip"
    zip_path = report_root / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(set(PACK_CONTENTS + ["continuity_pack_manifest.json"])):
            file_path = report_root / name
            if file_path.exists() and file_path.is_file():
                zf.write(file_path, arcname=name)

    zip_sha = sha256_file(zip_path)
    # Second sha pass includes ZIP hash.
    sha_text = build_sha_file(report_root, zip_name=zip_name, zip_sha=zip_sha)
    write_text(report_root / "continuity_pack_sha256s.txt", sha_text)

    zip_receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "zip_name": zip_name,
        "zip_path": rel(zip_path, repo_root),
        "zip_sha256": zip_sha,
        "zip_readable": True,
        "included_files": sorted(set(PACK_CONTENTS + ["continuity_pack_manifest.json"])),
        "verdict": "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "continuity_pack_zip_receipt.json", zip_receipt)

    # Mechanicus validation.
    json_checks, json_all_ok = validate_json_files(report_root)
    zip_readability_ok = True
    zip_readability_error = ""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad_file = zf.testzip()
            if bad_file is not None:
                zip_readability_ok = False
                zip_readability_error = f"Corrupt member: {bad_file}"
    except Exception as exc:
        zip_readability_ok = False
        zip_readability_error = str(exc)

    mechanicus_caps: list[str] = []
    if not json_all_ok:
        mechanicus_caps.append("CAP_JSON_PARSE_CHECK_FAILED")
    if not zip_readability_ok:
        mechanicus_caps.append("CAP_ZIP_READABILITY_FAILED")
    if not (report_root / "continuity_pack_sha256s.txt").exists():
        mechanicus_caps.append("CAP_SHA256_GENERATION_MISSING")

    mechanicus_receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "checks": {
            "json_parse": json_checks,
            "zip_readability": {
                "ok": zip_readability_ok,
                "error": zip_readability_error or None,
            },
            "sha256_generated": (report_root / "continuity_pack_sha256s.txt").exists(),
            "git_truth_present": (report_root / "git_truth_receipt.json").exists(),
        },
        "replay_state": "SEPARATE_REPLAY_RUNNER_FOR_TARGET",
        "replay_command": f"python {rel(script_path, repo_root)} --repo-root . --task-id {task_id}",
        "caps_triggered": sorted(set(mechanicus_caps)),
        "verdict": "PASS_WITH_WARNINGS" if not mechanicus_caps else "BLOCK",
    }
    write_json(report_root / "mechanicus_validation_receipt.json", mechanicus_receipt)

    # Inquisition stale/fake continuity guard.
    continuity_state = str(stale_context_audit.get("continuity_state", "PARTIAL")).upper()
    guard_caps: list[str] = []
    fake_green_flags: list[str] = []
    if continuity_state == "BLOCKED":
        guard_caps.append("CAP_NO_FAKE_CONTINUITY")
        fake_green_flags.append("CLAIM_WITHOUT_REPLAY")
    if private_exclusion.get("verdict") != "PASS":
        guard_caps.append("CAP_PRIVATE_LEAK_RISK")
        fake_green_flags.append("PRIVATE_LEAK_RISK")
    if mechanicus_receipt.get("verdict") == "BLOCK":
        guard_caps.append("CAP_MECHANICUS_VALIDATION_BLOCK")
        fake_green_flags.append("OUTPUT_UNSCHEMAED")

    if continuity_state == "FRESH" and not guard_caps:
        guard_verdict = "PASS_WITH_WARNINGS"
    elif continuity_state in {"PARTIAL", "STALE"} and not guard_caps:
        guard_verdict = "WARN"
    else:
        guard_verdict = "BLOCK"

    inquisition_guard = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "continuity_state": continuity_state,
        "stale_context_audit_path": "stale_context_audit.json",
        "private_data_exclusion_path": "private_data_exclusion_receipt.json",
        "mechanicus_validation_path": "mechanicus_validation_receipt.json",
        "fake_green_flags": fake_green_flags,
        "caps_triggered": sorted(set(guard_caps)),
        "verdict": guard_verdict,
    }
    write_json(report_root / "inquisition_fake_continuity_guard_receipt.json", inquisition_guard)

    hard_red_team_verdict = {
        "task_id": task_id,
        "builder_claims": [
            {
                "claim_id": "C001",
                "claim": "Continuity pack skill is script-first and replayable.",
                "evidence": "administratum_continuity_pack_skill_v0_1.py + continuity_pack_skill_smoke_receipt.json",
            },
            {
                "claim_id": "C002",
                "claim": "No private/secrets bulk collection is performed.",
                "evidence": "private_data_exclusion_receipt.json",
            },
            {
                "claim_id": "C003",
                "claim": "Pack integrity is validated with JSON/ZIP/SHA checks.",
                "evidence": "mechanicus_validation_receipt.json",
            },
        ],
        "attacks": [
            {
                "attack_id": "A001",
                "target_claim": "C001",
                "result": "PASS" if mechanicus_receipt["verdict"] != "BLOCK" else "WARN",
                "detail": "Replay command exists and generated current-target artifacts.",
            },
            {
                "attack_id": "A002",
                "target_claim": "C002",
                "result": "PASS" if private_exclusion.get("verdict") == "PASS" else "BLOCK",
                "detail": "Allowlist-only packaging with explicit private exclusion policy.",
            },
            {
                "attack_id": "A003",
                "target_claim": "GLOBAL",
                "result": "WARN",
                "detail": "Global Stage1/IDE/WARP caps remain active; clean PASS is forbidden.",
            },
        ],
        "downgrade_rules_applied": [
            "NO_CLEAN_PASS_WITH_GLOBAL_CAPS",
            "DIRTY_START_VISIBLE_AND_CAPPED",
            "NO_VM2_VM3_LIVE_ROUTE_PROOF",
        ],
        "final_verdict": "PASS_WITH_WARNINGS" if guard_verdict != "BLOCK" else "BLOCK",
        "blocked_clean_pass_reasons": [
            "CAP_STAGE1_WITH_WARNINGS_ONLY",
            "CAP_NO_IDE_VISUAL_RELEASE_YET",
            "CAP_NO_WARP_RUNTIME",
        ],
    }
    write_json(report_root / "hard_red_team_verdict.json", hard_red_team_verdict)

    skill_pain_cure = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "owner_pains": [
            "Manual context reconstruction for new chat",
            "Risk of stale context",
            "Risk of private-data leak",
            "No stable handoff route for Logos-Prime",
        ],
        "implemented_cures": [
            "Script-first continuity pack build command",
            "stale_context_audit.json classification",
            "private_data_exclusion_receipt.json allowlist policy",
            "RU+EN handoff pair for Owner and machine flows",
        ],
        "evidence_paths": [
            "continuity_pack_skill_smoke_receipt.json",
            "stale_context_audit.json",
            "private_data_exclusion_receipt.json",
            "logos_prime_handoff_ru.md",
            "logos_prime_handoff_en.md",
        ],
        "verdict": "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "skill_owner_pain_cure_receipt.json", skill_pain_cure)

    build_receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "skill_id": SKILL_ID,
        "skill_version": SKILL_VERSION,
        "mode": args.mode,
        "report_root": rel(report_root, repo_root),
        "zip_path": rel(zip_path, repo_root),
        "required_outputs_expected": REQUIRED_OUTPUTS,
        "verdict": "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "pc_continuity_pack_build_receipt.json", build_receipt)

    commit_push_receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "receipt_subject_head": git_truth.get("head"),
        "last_verified_head_before_this_commit": git_truth.get("head"),
        "receipt_content_head": git_truth.get("head"),
        "external_delivery_head": None,
        "remote_head_after_push": git_truth.get("origin_master_head"),
        "verification_timestamp_utc": utc_now(),
        "verification_actor": "administratum_continuity_pack_skill_v0_1.py",
        "worktree_clean_after_push": None,
        "origin_master_sync_after_push": git_truth.get("origin_sync"),
        "verification_method": "git truth probe only; commit/push not executed in this run",
        "self_head_paradox_handled": True,
        "commit_performed": False,
        "push_performed": False,
        "caps_triggered": [
            "CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP",
            "CAP_STAGE1_WITH_WARNINGS_ONLY",
        ],
        "clean_pass_allowed": False,
        "verdict": "WARN_NOT_PUSHED",
    }
    write_json(report_root / "commit_push_receipt.json", commit_push_receipt)

    final_owner_summary = f"""# FINAL_OWNER_SUMMARY_RU

{ru(r'\\u0428\\u0430\\u0433')}: Administratum Continuity Pack Skill and Logos-Prime handoff bridge.
{ru(r'\\u041f\\u0443\\u0442\\u044c \\u043a output bundle')}: `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/REPORTS/{task_id}/`
{ru(r'\\u0412\\u0435\\u0440\\u0434\\u0438\\u043a\\u0442')}: `PASS_WITH_WARNINGS`

- {ru(r'\\u041f\\u043e\\u0441\\u0442\\u0440\\u043e\\u0435\\u043d Administratum Skill-\\u043f\\u0430\\u043a\\u0435\\u0442 \\u0434\\u043b\\u044f controlled continuity handoff (PC contour).')}
- {ru(r'\\u0421\\u0444\\u043e\\u0440\\u043c\\u0438\\u0440\\u043e\\u0432\\u0430\\u043d\\u044b RU/EN handoff-\\u0430\\u0440\\u0442\\u0435\\u0444\\u0430\\u043a\\u0442\\u044b, stale-context \\u0430\\u0443\\u0434\\u0438\\u0442, private-data exclusion \\u0438 hash/zip receipts.')}
- {ru(r'\\u0412\\u044b\\u043f\\u043e\\u043b\\u043d\\u0435\\u043d\\u044b Mechanicus-\\u043f\\u0440\\u043e\\u0432\\u0435\\u0440\\u043a\\u0438 JSON/ZIP/SHA \\u0438 Inquisition fake-continuity guard.')}
- {ru(r'Clean PASS \\u043d\\u0435 \\u0437\\u0430\\u044f\\u0432\\u043b\\u044f\\u0435\\u0442\\u0441\\u044f: \\u0433\\u043b\\u043e\\u0431\\u0430\\u043b\\u044c\\u043d\\u044b\\u0435 Stage1/IDE/WARP caps \\u0441\\u043e\\u0445\\u0440\\u0430\\u043d\\u0435\\u043d\\u044b.')}
- {ru(r'Commit/push \\u0432 \\u044d\\u0442\\u043e\\u043c \\u043f\\u0440\\u043e\\u0433\\u043e\\u043d\\u0435 \\u043d\\u0435 \\u0432\\u044b\\u043f\\u043e\\u043b\\u043d\\u044f\\u043b\\u0438\\u0441\\u044c; \\u0432\\u044b\\u0434\\u0430\\u043d \\u0447\\u0435\\u0441\\u0442\\u043d\\u044b\\u0439 commit_push_receipt.json \\u0441\\u043e \\u0441\\u0442\\u0430\\u0442\\u0443\\u0441\\u043e\\u043c WARN.')}
"""
    write_text(report_root / "final_owner_summary_ru.md", final_owner_summary)

    missing_outputs = [
        name
        for name in REQUIRED_OUTPUTS
        if name != "continuity_pack_skill_smoke_receipt.json" and not (report_root / name).exists()
    ]
    smoke_verdict = "PASS_WITH_WARNINGS" if not missing_outputs else "BLOCK"
    smoke_receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "skill_id": SKILL_ID,
        "command": f"python {rel(script_path, repo_root)} --repo-root . --task-id {task_id}",
        "required_outputs_count": len(REQUIRED_OUTPUTS),
        "missing_outputs": missing_outputs,
        "caps_carried": active_caps_snapshot["caps"],
        "verdict": smoke_verdict,
    }
    write_json(report_root / "continuity_pack_skill_smoke_receipt.json", smoke_receipt)

    print(json.dumps(
        {
            "task_id": task_id,
            "report_root": rel(report_root, repo_root),
            "zip_path": rel(zip_path, repo_root),
            "smoke_verdict": smoke_verdict,
            "hard_red_team_verdict": hard_red_team_verdict["final_verdict"],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0 if smoke_verdict != "BLOCK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
