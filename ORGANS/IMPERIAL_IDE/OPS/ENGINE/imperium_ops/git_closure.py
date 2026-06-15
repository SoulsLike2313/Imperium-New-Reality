"""git_closure - the remote-closure step of a task, kept honest and gated.

status / diff / scope-check / secret-check are always safe to run. commit and
push only happen when the repo is a real git repo AND the safety gate allows
ACTION_PUSH; otherwise the closure is simulated and an honest receipt explains
why nothing was pushed.
"""
from __future__ import annotations

import os
import re
import subprocess
from typing import Dict, List

from . import receipts
from . import safety_gate

_SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key"),
    re.compile(r"(?i)secret"),
    re.compile(r"(?i)password"),
    re.compile(r"(?i)token\s*[=:]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

_LOCAL_CONFIG_HINTS = [".env", "local.settings", "id_rsa", ".pem", "credentials"]


def _git(repo_root: str, args: List[str]) -> Dict:
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root, *args],
            capture_output=True, text=True, timeout=30,
        )
        return {"rc": proc.returncode, "out": proc.stdout.strip(), "err": proc.stderr.strip()}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"rc": 127, "out": "", "err": str(exc)}


def is_git_repo(repo_root: str) -> bool:
    return _git(repo_root, ["rev-parse", "--is-inside-work-tree"]).get("out") == "true"


def git_status(repo_root: str) -> Dict:
    """Branch / HEAD / dirty state. Safe; returns not_a_git_repo if absent."""
    if not is_git_repo(repo_root):
        return {"git": "not_a_git_repo", "repo_root": repo_root}
    branch = _git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]).get("out")
    head = _git(repo_root, ["rev-parse", "HEAD"]).get("out")
    porcelain = _git(repo_root, ["status", "--porcelain"]).get("out")
    dirty = [ln for ln in porcelain.splitlines() if ln.strip()]
    return {
        "git": "ok",
        "branch": branch,
        "head": head,
        "dirty": bool(dirty),
        "dirty_count": len(dirty),
    }


def diff_summary(repo_root: str) -> List[str]:
    if not is_git_repo(repo_root):
        return []
    out = _git(repo_root, ["status", "--porcelain"]).get("out")
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def scope_check(changed_paths: List[str], allowed_scope: List[str]) -> List[str]:
    """Return paths that fall outside the allowed write scope."""
    out_of_scope: List[str] = []
    for raw in changed_paths:
        path = raw.split(" ", 1)[-1].strip() if " " in raw else raw
        if not any(path.startswith(scope.rstrip("/")) for scope in allowed_scope):
            out_of_scope.append(path)
    return out_of_scope


def secret_check(repo_root: str, changed_paths: List[str]) -> List[str]:
    """Return paths that look like they contain secrets or local configs."""
    flagged: List[str] = []
    for raw in changed_paths:
        path = raw.split(" ", 1)[-1].strip() if " " in raw else raw
        if any(hint in path for hint in _LOCAL_CONFIG_HINTS):
            flagged.append(path)
            continue
        full = os.path.join(repo_root, path)
        if os.path.isfile(full):
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read(20000)
                if any(p.search(text) for p in _SECRET_PATTERNS):
                    flagged.append(path)
            except OSError:
                pass
    return flagged


def closure(repo_root: str, intent, state, message: str, dry_run: bool = True) -> dict:
    """Attempt remote closure; emit a git_commit_push_receipt. Honest by design."""
    changed = diff_summary(repo_root)
    allowed = getattr(intent, "allowed_write_scope", []) or ["ORGANS/IMPERIAL_IDE/OPS/STAGING/"]
    out_of_scope = scope_check(changed, allowed)
    secrets = secret_check(repo_root, changed)

    gate = safety_gate.check(safety_gate.ACTION_PUSH, state)
    can_close = (
        is_git_repo(repo_root)
        and gate.allowed
        and not out_of_scope
        and not secrets
        and not dry_run
    )

    commit = ""
    pushed = False
    reasons: List[str] = list(gate.reasons)
    if out_of_scope:
        reasons.append(f"out-of-scope paths: {out_of_scope}")
    if secrets:
        reasons.append(f"secret/local-config paths: {secrets}")
    if dry_run:
        reasons.append("dry-run: closure simulated")

    if can_close:
        _git(repo_root, ["add", "-A"])
        c = _git(repo_root, ["commit", "-m", message])
        commit = _git(repo_root, ["rev-parse", "HEAD"]).get("out") if c["rc"] == 0 else ""
        p = _git(repo_root, ["push"])
        pushed = p["rc"] == 0

    branch = _git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]).get("out") if is_git_repo(repo_root) else ""
    return receipts.make_receipt(
        "git_commit_push_receipt",
        task_id=getattr(intent, "task_id", ""),
        branch=branch,
        commit=commit,
        pushed=pushed,
        in_scope=not out_of_scope,
        secrets_detected=bool(secrets),
        reasons=reasons,
        dry_run=dry_run,
    )
