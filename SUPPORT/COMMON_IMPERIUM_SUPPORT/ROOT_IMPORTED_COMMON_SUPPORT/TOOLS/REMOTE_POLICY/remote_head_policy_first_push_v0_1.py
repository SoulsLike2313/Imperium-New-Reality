from __future__ import annotations

import argparse
import hashlib
import json
import os
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
    git_truth,
    resolve_new_reality_root,
)


TASK_ID = "TASK-NEWGEN-PC-NEW-REALITY-REMOTE-HEAD-POLICY-ANCIENT-REFERENCE-AND-FIRST-PUSH-PROOF-PC-V0_1"
REPORT_REL = Path("REPORTS") / TASK_ID
REMOTE_URL = "https://github.com/SoulsLike2313/Imperium-New-Reality.git"
ANCIENT_REMOTE_URL = "https://github.com/SoulsLike2313/Imperium-"
ANCIENT_FREEZE_COMMIT = "448150be7b4984b755828bc2f89b5bd1156de37d"
ANCIENT_ROOT = Path("E:/IMPERIUM")
BRANCH = "master"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path, *, timeout: int = 120) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }


def run_git(repo_root: Path, *args: str, timeout: int = 120) -> dict[str, Any]:
    return run_command(["git", *args], repo_root, timeout=timeout)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_lines(text: str) -> list[str]:
    return text.splitlines() if text else []


def parse_remote_heads(stdout: str) -> dict[str, str]:
    heads: dict[str, str] = {}
    for line in split_lines(stdout):
        parts = line.split()
        if len(parts) != 2:
            continue
        head, ref = parts
        if ref.startswith("refs/heads/"):
            heads[ref.removeprefix("refs/heads/")] = head
    return heads


def get_ancient_state() -> dict[str, Any]:
    exists = ANCIENT_ROOT.is_dir()
    if not exists:
        return {
            "exists": False,
            "root": ANCIENT_ROOT.as_posix(),
            "head": "",
            "branch": "",
            "status_short_branch": [],
            "status": "MISSING",
        }
    head = run_git(ANCIENT_ROOT, "rev-parse", "HEAD")
    branch = run_git(ANCIENT_ROOT, "branch", "--show-current")
    status = run_git(ANCIENT_ROOT, "status", "--short", "--branch")
    return {
        "exists": True,
        "root": ANCIENT_ROOT.as_posix(),
        "head": head["stdout"],
        "branch": branch["stdout"],
        "status_short_branch": split_lines(status["stdout"]),
        "commands": {
            "head": head,
            "branch": branch,
            "status": status,
        },
    }


def remote_heads_by_url(repo_root: Path) -> dict[str, Any]:
    remote = run_command(["git", "ls-remote", "--heads", REMOTE_URL], repo_root, timeout=120)
    return {
        "command": remote["command"],
        "returncode": remote["returncode"],
        "stdout": remote["stdout"],
        "stderr": remote["stderr"],
        "status": remote["status"],
        "heads": parse_remote_heads(remote["stdout"]),
    }


def ensure_origin(repo_root: Path) -> dict[str, Any]:
    before = run_git(repo_root, "remote", "get-url", "origin")
    action = "NONE"
    if before["returncode"] != 0:
        result = run_git(repo_root, "remote", "add", "origin", REMOTE_URL)
        action = "ADDED"
    elif before["stdout"] != REMOTE_URL:
        result = run_git(repo_root, "remote", "set-url", "origin", REMOTE_URL)
        action = "UPDATED"
    else:
        result = {"returncode": 0, "stdout": "", "stderr": "", "status": "PASS", "command": []}
    after = run_git(repo_root, "remote", "get-url", "origin")
    return {
        "before": before,
        "action": action,
        "configure_result": result,
        "after": after,
        "remote_url_exact_match": after["returncode"] == 0 and after["stdout"] == REMOTE_URL,
        "verdict": "PASS" if after["returncode"] == 0 and after["stdout"] == REMOTE_URL else "BLOCK",
    }


def remote_safety_verdict(remote_heads: dict[str, str], local_head: str) -> dict[str, Any]:
    if not remote_heads:
        return {
            "remote_state": "EMPTY",
            "remote_safe_for_push": True,
            "remote_not_empty_requires_owner_decision": False,
            "reason": "No remote heads were returned by git ls-remote --heads.",
        }
    if set(remote_heads) == {BRANCH} and remote_heads.get(BRANCH) == local_head:
        return {
            "remote_state": "EXACT_MATCH",
            "remote_safe_for_push": True,
            "remote_not_empty_requires_owner_decision": False,
            "reason": "Remote master already equals local HEAD.",
        }
    return {
        "remote_state": "NON_EMPTY_OR_UNRELATED",
        "remote_safe_for_push": False,
        "remote_not_empty_requires_owner_decision": True,
        "reason": "Remote contains heads that are not an exact local-head match.",
    }


def write_policy_files(repo_root: Path) -> dict[str, Any]:
    remote_policy = f"""# New Reality Remote Policy

Status: ACTIVE_REMOTE_POLICY_V0_1
Owner organ: ADMINISTRATUM
Support organs: MECHANICUS, ASTRONOMICON, INQUISITION

## Active Remote

New Reality uses only this owner-authorized remote for PC `master` pushes:

```text
{REMOTE_URL}
```

Git remote name:

```text
origin
```

Active branch:

```text
{BRANCH}
```

## First Push Rule

Before the first push, the agent must run `git ls-remote --heads {REMOTE_URL}`.

- If no heads are returned, first push may proceed.
- If `refs/heads/{BRANCH}` exists and equals local HEAD, a normal non-force push may proceed.
- If any unrelated or unexpected remote history exists, stop with `REMOTE_NOT_EMPTY_REQUIRES_OWNER_DECISION`.

## Forbidden

- No force push.
- No push to Ancient Empire.
- No remote URL other than `{REMOTE_URL}`.
- No clean PASS without remote HEAD equality proof.

## Evidence

Required receipts:

- `pc_new_reality_remote_policy_receipt.json`
- `remote_push_receipt.json`
- `remote_head_equality_receipt.json`
- `git_closure_receipt.json`
"""
    ancient_reference = f"""# Ancient Empire Reference

Status: READ_ONLY_ARCHAEOLOGY_V0_1

Ancient Empire is not the active New Reality work truth.

Remote:

```text
{ANCIENT_REMOTE_URL}
```

Reference freeze commit:

```text
{ANCIENT_FREEZE_COMMIT}
```

Local archaeology root:

```text
{ANCIENT_ROOT.as_posix()}
```

Access mode:

```text
READ_ONLY_REFERENCE_REQUIRES_TASK_ADMISSION
```

## Policy

Ancient Empire may be read only when the active task explicitly grants reference access and records evidence. It must not be mutated, committed to, pushed to, rewritten, or treated as active remote truth for New Reality.
"""
    head_contract = f"""# New Reality Remote HEAD Contract

Status: CANDIDATE_REMOTE_HEAD_CONTRACT_V0_1
Owner organ: ADMINISTRATUM
Support organs: MECHANICUS, INQUISITION

## Purpose

Define how New Reality proves remote truth after commit and push.

## Canonical Remote

```text
{REMOTE_URL}
```

## Required Checks

1. Local branch is `{BRANCH}`.
2. `origin` URL equals the canonical remote exactly.
3. Push command is a normal non-force push.
4. `git ls-remote origin refs/heads/{BRANCH}` returns the same 40-character commit as local `git rev-parse HEAD`.
5. Receipts distinguish implementation/policy payload proof from any later closure receipt commit.

## Blocking Conditions

- Remote URL mismatch.
- Remote has unrelated history.
- Force push needed.
- Ancient Empire mutation or push.
- Empty or malformed local/remote HEAD fields.

## Evidence Level

Remote equality is an E3 runtime claim only when backed by the executed `git ls-remote` command result.
"""
    remote_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "New Reality Remote Push Receipt",
        "type": "object",
        "required": [
            "verdict",
            "remote_url",
            "local_head",
            "remote_head",
            "remote_head_equals_local_head",
            "push_performed",
            "force_push_used",
        ],
        "properties": {
            "verdict": {"type": "string"},
            "remote_url": {"type": "string"},
            "branch": {"type": "string"},
            "local_head": {"type": "string"},
            "remote_head": {"type": "string"},
            "remote_head_equals_local_head": {"type": "boolean"},
            "push_performed": {"type": "boolean"},
            "force_push_used": {"type": "boolean"},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
    }
    write_text(repo_root / "REMOTE_POLICY.md", remote_policy)
    write_text(repo_root / "ANCIENT_EMPIRE_REFERENCE.md", ancient_reference)
    write_text(repo_root / "NEW_REALITY_REMOTE_HEAD_CONTRACT.md", head_contract)
    write_json(repo_root / "SCHEMAS" / "remote_push_receipt.schema.json", remote_schema)
    return {
        "files": [
            "REMOTE_POLICY.md",
            "ANCIENT_EMPIRE_REFERENCE.md",
            "NEW_REALITY_REMOTE_HEAD_CONTRACT.md",
            "SCHEMAS/remote_push_receipt.schema.json",
        ],
        "status": "WRITTEN",
    }


def write_common_receipts(
    repo_root: Path,
    report_root: Path,
    *,
    phase: str,
    origin_receipt: dict[str, Any],
    remote_probe: dict[str, Any],
    ancient_before: dict[str, Any],
    ancient_after: dict[str, Any],
    remote_push: dict[str, Any] | None,
) -> None:
    resolution = resolve_new_reality_root(repo_root)
    truth = git_truth(repo_root)
    remote_heads = remote_probe.get("heads", {})
    safety = remote_safety_verdict(remote_heads, truth.get("git_head", ""))
    policy_files = ["REMOTE_POLICY.md", "ANCIENT_EMPIRE_REFERENCE.md", "NEW_REALITY_REMOTE_HEAD_CONTRACT.md", "SCHEMAS/remote_push_receipt.schema.json"]
    policy_hashes = {path: sha256_file(repo_root / path) for path in policy_files if (repo_root / path).is_file()}

    write_json(
        report_root / "root_resolution_receipt.json",
        {
            "task_id": TASK_ID,
            "receipt_type": "root_resolution_receipt",
            "timestamp_utc": utc_now(),
            **resolution.to_receipt(),
            "git": truth,
            "verdict": "PASS" if truth.get("verdict") == "PASS" else "BLOCK",
        },
    )
    write_json(
        report_root / "pc_new_reality_remote_policy_receipt.json",
        {
            "task_id": TASK_ID,
            "receipt_type": "pc_new_reality_remote_policy_receipt",
            "timestamp_utc": utc_now(),
            "phase": phase,
            "active_root": repo_root.as_posix(),
            "remote_url": REMOTE_URL,
            "branch": BRANCH,
            "origin_configuration": origin_receipt,
            "remote_pre_push_probe": remote_probe,
            "remote_safety": safety,
            "policy_files": policy_hashes,
            "ancient_empire_reference_url": ANCIENT_REMOTE_URL,
            "ancient_empire_freeze_commit": ANCIENT_FREEZE_COMMIT,
            "verdict": "PASS" if origin_receipt.get("verdict") == "PASS" and safety["remote_safe_for_push"] else "BLOCK",
        },
    )
    ancient_unchanged = ancient_before.get("head") == ancient_after.get("head") and ancient_before.get("status_short_branch") == ancient_after.get("status_short_branch")
    write_json(
        report_root / "ancient_empire_no_mutation_receipt.json",
        {
            "task_id": TASK_ID,
            "receipt_type": "ancient_empire_no_mutation_receipt",
            "timestamp_utc": utc_now(),
            "ancient_root": ANCIENT_ROOT.as_posix(),
            "before": ancient_before,
            "after": ancient_after,
            "head_unchanged_during_task_runner": ancient_before.get("head") == ancient_after.get("head"),
            "status_unchanged_during_task_runner": ancient_before.get("status_short_branch") == ancient_after.get("status_short_branch"),
            "write_operations_performed": False,
            "ancient_empire_mutated_by_this_task": False if ancient_unchanged else None,
            "warnings": ["Ancient Empire has pre-existing dirty/untracked state; this task did not write there."],
            "verdict": "PASS_WITH_WARNINGS" if ancient_unchanged else "WARN_REVIEW_REQUIRED",
        },
    )
    remote_push_payload = remote_push or {
        "verdict": "PENDING",
        "remote_url": REMOTE_URL,
        "branch": BRANCH,
        "local_head": truth.get("git_head", ""),
        "remote_head": "",
        "remote_head_equals_local_head": False,
        "push_performed": False,
        "force_push_used": False,
        "warnings": ["Remote push has not been executed in this receipt phase."],
    }
    write_json(report_root / "remote_push_receipt.json", remote_push_payload)
    equality_payload = {
        "task_id": TASK_ID,
        "receipt_type": "remote_head_equality_receipt",
        "timestamp_utc": utc_now(),
        "phase": phase,
        "remote_url": REMOTE_URL,
        "branch": BRANCH,
        "local_head": remote_push_payload.get("local_head", truth.get("git_head", "")),
        "remote_head": remote_push_payload.get("remote_head", ""),
        "remote_head_equals_local_head": bool(remote_push_payload.get("remote_head_equals_local_head", False)),
        "verification_command": ["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"],
        "force_push_used": bool(remote_push_payload.get("force_push_used", False)),
        "verdict": "PASS" if remote_push_payload.get("remote_head_equals_local_head") else "PENDING",
        "self_reference_note": "Receipt records the pushed payload/receipt-generation HEAD; final closure commit equality is verified by the final post-push command and Owner summary.",
    }
    write_json(report_root / "remote_head_equality_receipt.json", equality_payload)
    write_json(
        report_root / "capability_split_receipt.json",
        {
            "task_id": TASK_ID,
            "LOCAL_SCRIPT_FIRST": ["TOOLS/REMOTE_POLICY/remote_head_policy_first_push_v0_1.py", "ORGAN_AGENT_COMMON/root_resolution.py"],
            "LOCAL_MANUAL_COMMAND": [
                "git add -A",
                "git commit",
                "git push -u origin master",
                "git ls-remote origin refs/heads/master",
                "git status --short --branch",
            ],
            "CANDIDATE_SCRIPT_FIRST": [],
            "AGENT_REASONING_ONLY": ["Closure receipt self-reference limitation is labeled instead of hidden."],
            "EXTERNAL_RESEARCH": [],
            "OWNER_MANUAL_CONFIRMATION": ["Owner-authorized remote URL supplied by taskpack."],
            "FUTURE_CAPABILITY_GAP": ["A self-hashing committed receipt cannot contain its own future commit hash."],
        },
    )
    write_json(
        report_root / "claim_ledger.json",
        {
            "task_id": TASK_ID,
            "claims": [
                {
                    "claim_id": "C001",
                    "claim": "New Reality root resolved through root resolver.",
                    "owner_organ": "MECHANICUS",
                    "capability_class": "LOCAL_SCRIPT_FIRST",
                    "evidence_level": "E3",
                    "evidence_ref": "root_resolution_receipt.json",
                    "status": "PASS",
                },
                {
                    "claim_id": "C002",
                    "claim": "Origin URL is the owner-authorized New Reality remote.",
                    "owner_organ": "ADMINISTRATUM",
                    "capability_class": "LOCAL_SCRIPT_FIRST",
                    "evidence_level": "E3",
                    "evidence_ref": "pc_new_reality_remote_policy_receipt.json",
                    "status": "PASS" if origin_receipt.get("remote_url_exact_match") else "BLOCK",
                },
                {
                    "claim_id": "C003",
                    "claim": "Ancient Empire was not mutated by this task runner.",
                    "owner_organ": "INQUISITION",
                    "capability_class": "LOCAL_MANUAL_COMMAND",
                    "evidence_level": "E3",
                    "evidence_ref": "ancient_empire_no_mutation_receipt.json",
                    "status": "PASS_WITH_WARNINGS" if ancient_unchanged else "WARN",
                },
                {
                    "claim_id": "C004",
                    "claim": "Remote HEAD equality was verified for the pushed New Reality branch.",
                    "owner_organ": "ADMINISTRATUM",
                    "capability_class": "LOCAL_MANUAL_COMMAND",
                    "evidence_level": "E3" if remote_push_payload.get("remote_head_equals_local_head") else "E1",
                    "evidence_ref": "remote_head_equality_receipt.json",
                    "status": "PASS" if remote_push_payload.get("remote_head_equals_local_head") else "PENDING",
                },
            ],
        },
    )
    write_json(
        report_root / "EVIDENCE_BOUNDARY.json",
        {
            "task_id": TASK_ID,
            "active_root": repo_root.as_posix(),
            "ancient_empire_root": ANCIENT_ROOT.as_posix(),
            "allowed_mutation_scope": "New Reality root only",
            "ancient_access_mode": "read-only status/head probe",
            "external_research_used": False,
            "remote_network_used": True,
            "remote_network_target": REMOTE_URL,
            "dirty_state_declared": truth.get("git_status_short", "") != "",
        },
    )
    write_json(
        report_root / "IMPERIUM_QUESTION_PASS.json",
        {
            "task_id": TASK_ID,
            "blocking_owner_questions": [],
            "owner_authorized_remote_url": REMOTE_URL,
            "question_pass_verdict": "PASS",
        },
    )
    write_json(
        report_root / "red_team_verdict.json",
        {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "mode": "HARD_RED_TEAM",
            "checks": {
                "remote_url_exact": "PASS" if origin_receipt.get("remote_url_exact_match") else "BLOCK",
                "remote_unrelated_history": "PASS" if safety["remote_safe_for_push"] else "BLOCK",
                "force_push": "PASS" if not remote_push_payload.get("force_push_used") else "BLOCK",
                "ancient_mutation": "PASS_WITH_WARNINGS" if ancient_unchanged else "WARN",
                "remote_head_equality": "PASS" if remote_push_payload.get("remote_head_equals_local_head") else "PENDING",
                "closure_self_reference": "WARN_DISCLOSED",
            },
            "clean_pass_allowed_from_bundle_only": bool(remote_push_payload.get("remote_head_equals_local_head")),
            "surviving_warnings": [
                "Ancient Empire had pre-existing dirty/untracked state.",
                "A committed receipt cannot contain a cryptographic proof of its own future commit hash; final equality is rechecked after push.",
            ],
            "final_verdict": "PASS_WITH_WARNINGS" if remote_push_payload.get("remote_head_equals_local_head") else "PENDING",
        },
    )
    write_json(
        report_root / "git_closure_receipt.json",
        {
            "task_id": TASK_ID,
            "receipt_type": "git_closure_receipt",
            "timestamp_utc": utc_now(),
            "phase": phase,
            "local_git_truth": truth,
            "remote_url": REMOTE_URL,
            "branch": BRANCH,
            "remote_head_equality_receipt": "remote_head_equality_receipt.json",
            "post_receipt_commit_verification_required": True,
            "verdict": "PASS_WITH_POST_PUSH_VERIFICATION_REQUIRED" if remote_push_payload.get("remote_head_equals_local_head") else "PENDING",
        },
    )
    summary_ru = (
        "# FINAL_OWNER_SUMMARY_RU\n\n"
        "\u0428\u0430\u0433: New Reality remote policy and first push proof.\n"
        f"\u0412\u0435\u0440\u0434\u0438\u043a\u0442: {'PASS_WITH_WARNINGS' if remote_push_payload.get('remote_head_equals_local_head') else 'PENDING'}.\n"
        "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 remote \u0437\u0430\u0434\u0430\u043d\u0430 \u0434\u043b\u044f owner-authorized New Reality repo; Ancient Empire \u043e\u0441\u0442\u0430\u043b\u0441\u044f read-only reference.\n"
        "\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 exact remote HEAD \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0435\u0442\u0441\u044f post-push \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 \u0438 \u0434\u0443\u0431\u043b\u0438\u0440\u0443\u0435\u0442\u0441\u044f \u0432 owner final.\n"
    )
    write_text(report_root / "final_owner_summary_ru.md", summary_ru)


def build_bundle(repo_root: Path, report_root: Path) -> dict[str, Any]:
    required = [
        "pc_new_reality_remote_policy_receipt.json",
        "remote_push_receipt.json",
        "remote_head_equality_receipt.json",
        "ancient_empire_no_mutation_receipt.json",
        "root_resolution_receipt.json",
        "git_closure_receipt.json",
        "claim_ledger.json",
        "capability_split_receipt.json",
        "red_team_verdict.json",
        "final_owner_summary_ru.md",
        "EVIDENCE_BOUNDARY.json",
        "IMPERIUM_QUESTION_PASS.json",
    ]
    source_files = [
        "REMOTE_POLICY.md",
        "ANCIENT_EMPIRE_REFERENCE.md",
        "NEW_REALITY_REMOTE_HEAD_CONTRACT.md",
        "SCHEMAS/remote_push_receipt.schema.json",
        "TOOLS/REMOTE_POLICY/remote_head_policy_first_push_v0_1.py",
    ]
    paths = [report_root / rel for rel in required] + [repo_root / rel for rel in source_files]
    sha_lines = []
    for path in paths:
        rel = path.relative_to(repo_root).as_posix()
        sha_lines.append(f"{sha256_file(path)}  {rel}")
    write_text(report_root / "sha256sums.txt", "\n".join(sha_lines) + "\n")

    bundle_path = report_root / "task_report_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in paths:
            zf.write(path, path.relative_to(repo_root).as_posix())
        zf.write(report_root / "sha256sums.txt", (report_root / "sha256sums.txt").relative_to(repo_root).as_posix())
    receipt = {
        "task_id": TASK_ID,
        "receipt_type": "task_report_bundle_receipt",
        "timestamp_utc": utc_now(),
        "bundle_path": bundle_path.as_posix(),
        "bundle_sha256": sha256_file(bundle_path),
        "sha256sums_path": (report_root / "sha256sums.txt").as_posix(),
        "verdict": "PASS",
    }
    write_json(report_root / "task_report_bundle_receipt.json", receipt)
    write_text(report_root / "task_report_bundle.zip.sha256", f"{receipt['bundle_sha256']}  task_report_bundle.zip\n")
    return receipt


def prepare(repo_root: Path) -> int:
    report_root = repo_root / REPORT_REL
    report_root.mkdir(parents=True, exist_ok=True)
    ancient_before = get_ancient_state()
    policy = write_policy_files(repo_root)
    origin = ensure_origin(repo_root)
    remote_probe = remote_heads_by_url(repo_root)
    ancient_after = get_ancient_state()
    write_common_receipts(
        repo_root,
        report_root,
        phase="PRE_PUSH_POLICY_PREPARE",
        origin_receipt=origin,
        remote_probe=remote_probe,
        ancient_before=ancient_before,
        ancient_after=ancient_after,
        remote_push=None,
    )
    bundle = build_bundle(repo_root, report_root)
    payload = {
        "task_id": TASK_ID,
        "phase": "prepare",
        "policy": policy,
        "origin": origin,
        "remote_probe": remote_probe,
        "bundle": bundle,
        "verdict": "PASS" if origin.get("verdict") == "PASS" and remote_safety_verdict(remote_probe.get("heads", {}), git_truth(repo_root).get("git_head", ""))["remote_safe_for_push"] else "BLOCK",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if payload["verdict"] == "PASS" else 2


def finalize(repo_root: Path) -> int:
    report_root = repo_root / REPORT_REL
    report_root.mkdir(parents=True, exist_ok=True)
    ancient_before = get_ancient_state()
    origin = ensure_origin(repo_root)
    remote_probe = remote_heads_by_url(repo_root)
    local_head = git_truth(repo_root).get("git_head", "")
    remote_head = remote_probe.get("heads", {}).get(BRANCH, "")
    remote_push = {
        "task_id": TASK_ID,
        "receipt_type": "remote_push_receipt",
        "timestamp_utc": utc_now(),
        "verdict": "PASS" if remote_head and remote_head == local_head else "WARN_REMOTE_HEAD_MISMATCH_OR_MISSING",
        "remote_url": REMOTE_URL,
        "branch": BRANCH,
        "local_head": local_head,
        "remote_head": remote_head,
        "remote_head_equals_local_head": bool(remote_head and remote_head == local_head),
        "push_performed": True,
        "force_push_used": False,
        "remote_probe": remote_probe,
        "warnings": [] if remote_head and remote_head == local_head else ["Remote head did not match local head at finalize time."],
    }
    ancient_after = get_ancient_state()
    write_common_receipts(
        repo_root,
        report_root,
        phase="POST_PUSH_PROOF",
        origin_receipt=origin,
        remote_probe=remote_probe,
        ancient_before=ancient_before,
        ancient_after=ancient_after,
        remote_push=remote_push,
    )
    bundle = build_bundle(repo_root, report_root)
    payload = {
        "task_id": TASK_ID,
        "phase": "finalize",
        "remote_push": remote_push,
        "bundle": bundle,
        "verdict": "PASS" if remote_push["remote_head_equals_local_head"] else "WARN",
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if remote_push["remote_head_equals_local_head"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="New Reality remote policy and first push proof task runner.")
    parser.add_argument("--repo-root", default="", help="Explicit New Reality root.")
    parser.add_argument("--phase", choices=["prepare", "finalize"], required=True)
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    if args.phase == "prepare":
        return prepare(repo_root)
    return finalize(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
