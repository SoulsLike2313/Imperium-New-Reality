from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MARKER_FILES = ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")
ENV_ROOT = "IMPERIUM_NEW_REALITY_ROOT"
CANONICAL_NEW_REALITY_ROOT = Path("E:/IMPERIUM_NEW_GENERATION_NEW_REALITY")
ANCIENT_EMPIRE_ROOT = Path("E:/IMPERIUM")
HELP_USAGE_TOKENS = (
    "usage:",
    "options:",
    "show this help",
    "fatal:",
    "error:",
    "git ",
    "powershell",
    "parameter",
)
GIT_HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
GIT_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")


@dataclass(frozen=True)
class RootResolution:
    active_root: Path
    resolution_method: str
    epoch_manifest_found: bool
    scope_lock_found: bool
    agents_md_found: bool

    def to_receipt(self) -> dict[str, Any]:
        return {
            "active_root": self.active_root.as_posix(),
            "resolution_method": self.resolution_method,
            "epoch_manifest_found": self.epoch_manifest_found,
            "scope_lock_found": self.scope_lock_found,
            "agents_md_found": self.agents_md_found,
        }


class RootResolutionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def _same_path(left: Path, right: Path) -> bool:
    return _resolved(left) == _resolved(right)


def is_ancient_empire_root(path: Path) -> bool:
    return _same_path(path, ANCIENT_EMPIRE_ROOT)


def is_under(path: Path, root: Path) -> bool:
    resolved_path = _resolved(path)
    resolved_root = _resolved(root)
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def _marker_state(candidate: Path) -> dict[str, bool]:
    return {
        "epoch_manifest_found": (candidate / "EPOCH_MANIFEST.json").is_file(),
        "scope_lock_found": (candidate / "NEW_REALITY_SCOPE_LOCK.md").is_file(),
        "agents_md_found": (candidate / "AGENTS.md").is_file(),
    }


def _load_epoch_manifest(candidate: Path) -> dict[str, Any]:
    path = candidate / "EPOCH_MANIFEST.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RootResolutionError(f"invalid epoch manifest at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RootResolutionError(f"invalid epoch manifest payload at {path}: expected object")
    return payload


def validate_new_reality_root(candidate: Path) -> RootResolution:
    root = _resolved(candidate)
    if is_ancient_empire_root(root):
        raise RootResolutionError(f"Ancient Empire root is not an active New Reality root: {root}")
    if not is_under(root, CANONICAL_NEW_REALITY_ROOT):
        raise RootResolutionError(f"root is outside New Reality boundary: {root}")

    markers = _marker_state(root)
    missing = [name for name, found in zip(MARKER_FILES, markers.values()) if not found]
    if missing:
        raise RootResolutionError(f"root is missing required marker files: {', '.join(missing)}")

    epoch_manifest = _load_epoch_manifest(root)
    if str(epoch_manifest.get("epoch", "")).upper() != "NEW_REALITY":
        raise RootResolutionError("epoch manifest does not declare NEW_REALITY")
    active_root = str(epoch_manifest.get("active_root", "")).strip()
    if active_root and not _same_path(Path(active_root), root):
        raise RootResolutionError(f"epoch manifest active_root mismatch: {active_root} != {root}")

    return RootResolution(
        active_root=root,
        resolution_method="validated",
        epoch_manifest_found=markers["epoch_manifest_found"],
        scope_lock_found=markers["scope_lock_found"],
        agents_md_found=markers["agents_md_found"],
    )


def discover_new_reality_root(start: Path | None = None) -> RootResolution:
    cursor = _resolved(start or Path.cwd())
    if cursor.is_file():
        cursor = cursor.parent
    errors: list[str] = []
    for candidate in (cursor, *cursor.parents):
        if all((candidate / marker).is_file() for marker in MARKER_FILES):
            try:
                found = validate_new_reality_root(candidate)
                return RootResolution(**{**found.to_receipt(), "active_root": found.active_root, "resolution_method": "auto_discovery"})
            except RootResolutionError as exc:
                errors.append(str(exc))
    suffix = f"; checked candidates failed: {' | '.join(errors)}" if errors else ""
    raise RootResolutionError(f"could not discover New Reality root from {cursor}{suffix}")


def resolve_new_reality_root(
    repo_root: str | Path | None = None,
    *,
    start: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> RootResolution:
    active_env = env if env is not None else os.environ

    if repo_root:
        resolved = validate_new_reality_root(Path(repo_root))
        return RootResolution(**{**resolved.to_receipt(), "active_root": resolved.active_root, "resolution_method": "explicit_cli_arg"})

    env_value = str(active_env.get(ENV_ROOT, "")).strip()
    if env_value:
        resolved = validate_new_reality_root(Path(env_value))
        return RootResolution(**{**resolved.to_receipt(), "active_root": resolved.active_root, "resolution_method": "environment"})

    return discover_new_reality_root(Path(start) if start else None)


def resolve_repo_path(repo_root: str | Path | None = None, *, start: str | Path | None = None) -> Path:
    return resolve_new_reality_root(repo_root, start=start).active_root


def default_runs_path(*parts: str, repo_root: str | Path | None = None, start: str | Path | None = None) -> Path:
    root = resolve_repo_path(repo_root, start=start)
    return root.joinpath("RUNS", *parts)


def resolve_output_path(value: str | Path, repo_root: Path) -> Path:
    path = Path(value)
    resolved = _resolved(path if path.is_absolute() else repo_root / path)
    if not is_under(resolved, repo_root):
        raise RootResolutionError(f"output path escapes New Reality root: {resolved}")
    return resolved


def git_value(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    value = completed.stdout.strip() if completed.returncode == 0 else (completed.stderr or completed.stdout).strip()
    return value


def validate_git_field(field_name: str, value: str) -> tuple[bool, str]:
    text = str(value or "").strip()
    lowered = text.lower()
    if not text:
        return False, f"{field_name} is empty"
    if "\n" in text or "\r" in text:
        return False, f"{field_name} is not single-line"
    if any(token in lowered for token in HELP_USAGE_TOKENS):
        return False, f"{field_name} contains help/error/usage text"
    if field_name in {"git_head", "head"} and not GIT_HEAD_RE.fullmatch(text):
        return False, f"{field_name} is not a 40-character hex commit id"
    if field_name in {"git_branch", "branch"} and not GIT_BRANCH_RE.fullmatch(text):
        return False, f"{field_name} contains unsupported branch characters"
    return True, "PASS"


def git_truth(repo_root: Path) -> dict[str, Any]:
    head = git_value(repo_root, "rev-parse", "HEAD")
    branch = git_value(repo_root, "branch", "--show-current")
    status = git_value(repo_root, "status", "--short")
    head_ok, head_reason = validate_git_field("git_head", head)
    branch_ok, branch_reason = validate_git_field("git_branch", branch)
    return {
        "git_head": head,
        "git_branch": branch,
        "git_status_short": status,
        "git_head_sane": head_ok,
        "git_branch_sane": branch_ok,
        "git_head_reason": head_reason,
        "git_branch_reason": branch_reason,
        "verdict": "PASS" if head_ok and branch_ok else "BLOCK",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve and validate the New Reality root.")
    parser.add_argument("--repo-root", default="", help="Optional explicit New Reality root.")
    parser.add_argument("--start", default="", help="Optional start path for upward discovery.")
    parser.add_argument("--receipt-out", default="", help="Optional JSON receipt output path.")
    args = parser.parse_args()

    try:
        resolution = resolve_new_reality_root(args.repo_root or None, start=args.start or None)
        truth = git_truth(resolution.active_root)
        payload = {
            "receipt_type": "root_resolution_receipt",
            "timestamp_utc": utc_now(),
            **resolution.to_receipt(),
            "git": truth,
            "verdict": "PASS" if truth["verdict"] == "PASS" else "BLOCK",
        }
        exit_code = 0 if payload["verdict"] == "PASS" else 1
    except Exception as exc:
        payload = {
            "receipt_type": "root_resolution_receipt",
            "timestamp_utc": utc_now(),
            "active_root": None,
            "error": str(exc),
            "verdict": "BLOCK",
        }
        exit_code = 1

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.receipt_out:
        output_path = Path(args.receipt_out).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
