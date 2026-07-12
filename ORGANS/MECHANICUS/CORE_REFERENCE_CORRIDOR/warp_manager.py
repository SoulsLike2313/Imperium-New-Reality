"""Exact-HEAD external Git worktree lifecycle for the reference corridor.

The manager deliberately does not merge, commit, or push.  Land preparation is
data-only; the only ref mutation helper is restricted to an explicitly marked
disposable fixture and rolls the ref back before returning.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping, Protocol, Sequence
import uuid


LIFECYCLE_STATES = (
    "PLANNED",
    "CREATED",
    "ACTIVE",
    "EXECUTING",
    "VALIDATING",
    "READY_FOR_REVIEW",
    "REJECTED",
    "DISCARDED",
    "APPROVED_FOR_LAND",
    "LANDED",
    "DESTROYED",
    "FAILED_CONTAINED",
)

_TRANSITIONS = {
    "CREATED": {"ACTIVE", "DISCARDED", "FAILED_CONTAINED"},
    "ACTIVE": {"EXECUTING", "DISCARDED", "FAILED_CONTAINED"},
    "EXECUTING": {"VALIDATING", "FAILED_CONTAINED"},
    "VALIDATING": {"READY_FOR_REVIEW", "FAILED_CONTAINED"},
    "READY_FOR_REVIEW": {"REJECTED", "DISCARDED"},
    "REJECTED": {"DISCARDED"},
    "FAILED_CONTAINED": {"DISCARDED"},
    "DISCARDED": {"DESTROYED"},
}

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_OID_RE = re.compile(r"^[0-9a-f]{40,64}$")
DISPOSABLE_MARKER = ".corridor-disposable-git-fixture"


class WarpError(RuntimeError):
    """Base failure for a fail-closed WARP operation."""


class WarpSafetyError(WarpError):
    """The requested path, state, or authority is unsafe."""


class OwnerGateProtocol(Protocol):
    def require(
        self, action: str, task_id: str, warp_id: str | None = None, **context: Any
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class WarpRecord:
    warp_id: str
    task_id: str
    path: str
    source_repo: str
    base_head: str
    scope: tuple[str, ...]
    state: str
    created_at_utc: str
    updated_at_utc: str
    git_metadata_verified: bool = True
    history: tuple[dict[str, str], ...] = field(default_factory=tuple)
    land_plan: dict[str, Any] | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(_canonical_bytes(value))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _same_path(left: Path | str, right: Path | str) -> bool:
    return os.path.normcase(str(Path(left).resolve())) == os.path.normcase(str(Path(right).resolve()))


def _inside(path: Path, root: Path, *, allow_root: bool = False) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return allow_root or relative != Path(".")


def _run(repo: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if check and completed.returncode != 0:
        raise WarpError(
            f"git {' '.join(args)} failed ({completed.returncode}): {completed.stderr.strip()}"
        )
    return completed


def _git(repo: Path, *args: str) -> str:
    return _run(repo, args).stdout.strip()


class WarpManager:
    """Persist and enforce one allowlisted family of external worktrees."""

    def __init__(
        self,
        source_repo: str | Path,
        managed_root: str | Path,
        *,
        registry_path: str | Path | None = None,
        owner_gate: OwnerGateProtocol | None = None,
    ) -> None:
        self.source_repo = Path(source_repo).resolve()
        self.managed_root = Path(managed_root).resolve()
        self.managed_root.mkdir(parents=True, exist_ok=True)
        self.registry_path = Path(registry_path).resolve() if registry_path else self.managed_root / ".warp_registry.json"
        if not _inside(self.registry_path, self.managed_root):
            raise WarpSafetyError("registry_path must be inside managed_root")
        self.owner_gate = owner_gate
        actual_root = Path(_git(self.source_repo, "rev-parse", "--show-toplevel")).resolve()
        if not _same_path(actual_root, self.source_repo):
            raise WarpSafetyError("source_repo must be the Git top-level")
        if not self.registry_path.exists():
            self._save({"schema_version": "imperium.warp_registry.v1", "warps": {}})

    def _load(self) -> dict[str, Any]:
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WarpError(f"invalid WARP registry: {exc}") from exc
        if data.get("schema_version") != "imperium.warp_registry.v1" or not isinstance(data.get("warps"), dict):
            raise WarpError("unsupported WARP registry")
        return data

    def _save(self, data: Mapping[str, Any]) -> None:
        _atomic_json(self.registry_path, data)

    @staticmethod
    def _validate_id(value: str, label: str) -> None:
        if not _ID_RE.fullmatch(value):
            raise WarpSafetyError(f"unsafe {label}: {value!r}")

    def _target(self, warp_id: str) -> Path:
        self._validate_id(warp_id, "warp_id")
        target = (self.managed_root / warp_id).resolve()
        if target.parent != self.managed_root or not _inside(target, self.managed_root):
            raise WarpSafetyError("WARP path must be a direct child of managed_root")
        return target

    def _resolve_base(self, base_head: str) -> str:
        if not _OID_RE.fullmatch(base_head.lower()):
            raise WarpSafetyError("base_head must be a full Git object id")
        resolved = _git(self.source_repo, "rev-parse", "--verify", f"{base_head}^{{commit}}").lower()
        if resolved != base_head.lower():
            raise WarpSafetyError("base_head did not resolve exactly")
        return resolved

    def _assert_clean_exact_source(self, base_head: str) -> None:
        if _git(self.source_repo, "rev-parse", "HEAD").lower() != base_head:
            raise WarpSafetyError("source HEAD is stale relative to base_head")
        if _git(self.source_repo, "status", "--porcelain=v1"):
            raise WarpSafetyError("source repository is not clean")

    def _registered_entry(self, target: Path) -> dict[str, Any] | None:
        raw = _run(self.source_repo, ("worktree", "list", "--porcelain", "-z")).stdout
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for item in raw.split("\0"):
            if not item:
                continue
            if item.startswith("worktree "):
                current = {"path": item[9:]}
                entries.append(current)
            elif current is not None and item.startswith("HEAD "):
                current["head"] = item[5:].lower()
            elif current is not None and item == "detached":
                current["detached"] = True
        return next((entry for entry in entries if _same_path(entry["path"], target)), None)

    def _verify_worktree(self, target: Path, base_head: str, *, require_clean: bool) -> None:
        if not target.exists() or not (target / ".git").exists():
            raise WarpSafetyError("external WARP lacks Git worktree metadata")
        if not _same_path(_git(target, "rev-parse", "--show-toplevel"), target):
            raise WarpSafetyError("WARP Git top-level mismatch")
        if _git(target, "rev-parse", "HEAD").lower() != base_head:
            raise WarpSafetyError("WARP HEAD differs from exact base_head")
        if require_clean and _git(target, "status", "--porcelain=v1"):
            raise WarpSafetyError("new or registered WARP is not clean")
        entry = self._registered_entry(target)
        if entry is None or entry.get("head") != base_head or not entry.get("detached"):
            raise WarpSafetyError("WARP is not registered as detached exact-HEAD worktree")
        if _run(target, ("symbolic-ref", "-q", "HEAD"), check=False).returncode == 0:
            raise WarpSafetyError("WARP unexpectedly has an attached branch")

    def _record(self, warp_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        registry = self._load()
        try:
            return registry, registry["warps"][warp_id]
        except KeyError as exc:
            raise WarpError(f"unknown warp_id: {warp_id}") from exc

    def get(self, warp_id: str) -> WarpRecord:
        _, record = self._record(warp_id)
        normalized = dict(record)
        normalized["scope"] = tuple(normalized.get("scope", ()))
        normalized["history"] = tuple(normalized.get("history", ()))
        return WarpRecord(**normalized)

    def _authorize(self, action: str, record: Mapping[str, Any], **context: Any) -> Mapping[str, Any]:
        if self.owner_gate is None:
            raise WarpSafetyError(f"explicit Owner gate is required for {action}")
        return self.owner_gate.require(
            action=action,
            task_id=str(record["task_id"]),
            warp_id=str(record["warp_id"]),
            **context,
        )

    def create(self, warp_id: str, task_id: str, base_head: str, scope: Sequence[str] = ()) -> WarpRecord:
        self._validate_id(task_id, "task_id")
        target = self._target(warp_id)
        base = self._resolve_base(base_head)
        self._assert_clean_exact_source(base)
        registry = self._load()
        if warp_id in registry["warps"] or target.exists():
            raise WarpSafetyError("WARP id or path already exists")
        _run(self.source_repo, ("worktree", "add", "--detach", str(target), base))
        try:
            self._verify_worktree(target, base, require_clean=True)
        except Exception:
            _run(self.source_repo, ("worktree", "remove", "--force", str(target)), check=False)
            raise
        now = _utc_now()
        record = WarpRecord(
            warp_id=warp_id,
            task_id=task_id,
            path=str(target),
            source_repo=str(self.source_repo),
            base_head=base,
            scope=tuple(scope),
            state="CREATED",
            created_at_utc=now,
            updated_at_utc=now,
            history=({"state": "CREATED", "timestamp_utc": now},),
        )
        registry["warps"][warp_id] = asdict(record)
        self._save(registry)
        return record

    def register_existing(
        self,
        warp_id: str,
        task_id: str,
        path: str | Path,
        base_head: str,
        scope: Sequence[str] = (),
    ) -> WarpRecord:
        """Register only an already clean, detached, exact-base Git worktree."""
        self._validate_id(task_id, "task_id")
        expected = self._target(warp_id)
        candidate = Path(path).resolve()
        if not _same_path(candidate, expected):
            raise WarpSafetyError("existing worktree path does not match managed warp_id path")
        base = self._resolve_base(base_head)
        self._assert_clean_exact_source(base)
        self._verify_worktree(candidate, base, require_clean=True)
        registry = self._load()
        if warp_id in registry["warps"]:
            raise WarpSafetyError("WARP id is already registered")
        now = _utc_now()
        record = WarpRecord(
            warp_id=warp_id,
            task_id=task_id,
            path=str(candidate),
            source_repo=str(self.source_repo),
            base_head=base,
            scope=tuple(scope),
            state="CREATED",
            created_at_utc=now,
            updated_at_utc=now,
            history=({"state": "CREATED", "timestamp_utc": now, "mode": "REGISTER_EXISTING"},),
        )
        registry["warps"][warp_id] = asdict(record)
        self._save(registry)
        return record

    def _transition(self, warp_id: str, target_state: str) -> WarpRecord:
        registry, record = self._record(warp_id)
        current = str(record["state"])
        if target_state not in _TRANSITIONS.get(current, set()):
            raise WarpSafetyError(f"illegal WARP transition: {current} -> {target_state}")
        if current != "DESTROYED":
            self._verify_worktree(Path(record["path"]), str(record["base_head"]), require_clean=False)
        now = _utc_now()
        record["state"] = target_state
        record["updated_at_utc"] = now
        record.setdefault("history", []).append({"state": target_state, "timestamp_utc": now})
        self._save(registry)
        return self.get(warp_id)

    def activate(self, warp_id: str) -> WarpRecord:
        _, record = self._record(warp_id)
        self._authorize("LAUNCH", record)
        return self._transition(warp_id, "ACTIVE")

    def execute(self, warp_id: str) -> WarpRecord:
        return self._transition(warp_id, "EXECUTING")

    def validate(self, warp_id: str, *, passed: bool) -> WarpRecord:
        self._transition(warp_id, "VALIDATING")
        return self._transition(warp_id, "READY_FOR_REVIEW" if passed else "FAILED_CONTAINED")

    def reject(self, warp_id: str) -> WarpRecord:
        _, record = self._record(warp_id)
        self._authorize("REJECT_RESULT", record)
        return self._transition(warp_id, "REJECTED")

    def discard(self, warp_id: str) -> WarpRecord:
        _, record = self._record(warp_id)
        self._authorize("DISCARD_WARP", record)
        return self._transition(warp_id, "DISCARDED")

    def destroy(self, warp_id: str) -> WarpRecord:
        registry, record = self._record(warp_id)
        self._authorize("DESTROY_WARP", record)
        if record["state"] != "DISCARDED":
            raise WarpSafetyError("WARP must be explicitly discarded before destroy")
        target = self._target(warp_id)
        if not _same_path(target, record["path"]):
            raise WarpSafetyError("registered WARP path escaped managed root")
        self._verify_worktree(target, str(record["base_head"]), require_clean=False)
        _run(self.source_repo, ("worktree", "remove", "--force", str(target)))
        if target.exists() or self._registered_entry(target) is not None:
            raise WarpError("Git did not fully remove the managed worktree")
        now = _utc_now()
        record["state"] = "DESTROYED"
        record["updated_at_utc"] = now
        record.setdefault("history", []).append({"state": "DESTROYED", "timestamp_utc": now})
        self._save(registry)
        return self.get(warp_id)

    def prepare_land_plan(self, warp_id: str) -> dict[str, Any]:
        """Return and persist a review plan; never update a ref or working tree."""
        registry, record = self._record(warp_id)
        self._authorize("PREPARE_LAND", record)
        if record["state"] != "READY_FOR_REVIEW":
            raise WarpSafetyError("land preparation requires READY_FOR_REVIEW")
        worktree = Path(record["path"])
        changed = set(filter(None, _run(worktree, ("diff", "--name-only", "-z", record["base_head"], "--")).stdout.split("\0")))
        changed.update(filter(None, _run(worktree, ("ls-files", "--others", "--exclude-standard", "-z")).stdout.split("\0")))
        hashes: dict[str, str] = {}
        for relative in sorted(changed):
            candidate = (worktree / relative).resolve()
            if not _inside(candidate, worktree):
                raise WarpSafetyError(f"changed path escaped WARP: {relative}")
            original = worktree / relative
            if original.is_symlink():
                hashes[relative] = "SYMLINK:" + hashlib.sha256(os.readlink(original).encode("utf-8")).hexdigest()
            elif original.is_file():
                hashes[relative] = hashlib.sha256(original.read_bytes()).hexdigest()
            else:
                hashes[relative] = "DELETED"
        plan = {
            "schema_version": "imperium.land_plan.v1",
            "warp_id": warp_id,
            "task_id": record["task_id"],
            "base_head": record["base_head"],
            "result_head": _git(worktree, "rev-parse", "HEAD"),
            "working_tree_manifest_sha256": hashlib.sha256(_canonical_bytes(hashes)).hexdigest(),
            "files_to_land": sorted(changed),
            "file_hashes": hashes,
            "prepared_at_utc": _utc_now(),
            "execution_performed": False,
            "land_authorized": False,
            "required_future_gate": "OWNER_AUTHORIZE_LAND",
            "atomic_method": "compare-and-swap ref update in a separate approved land task",
            "rollback_method": "compare-and-swap ref restoration to base_head",
        }
        record["land_plan"] = plan
        record["updated_at_utc"] = plan["prepared_at_utc"]
        self._save(registry)
        return plan


def mark_disposable_fixture(repo: str | Path, disposable_root: str | Path) -> Path:
    """Mark a Git repository as eligible for destructive proof helpers."""
    repository = Path(repo).resolve()
    allowed = Path(disposable_root).resolve()
    if not _inside(repository, allowed):
        raise WarpSafetyError("disposable repository is outside disposable_root")
    if not _same_path(_git(repository, "rev-parse", "--show-toplevel"), repository):
        raise WarpSafetyError("disposable repository must be its Git top-level")
    marker = repository / DISPOSABLE_MARKER
    _atomic_json(marker, {"schema_version": "imperium.disposable_git_fixture.v1", "repo": str(repository)})
    return marker


def prove_disposable_atomic_land_rollback(
    repo: str | Path,
    *,
    disposable_root: str | Path,
    target_ref: str,
    candidate_head: str,
    expected_base: str,
) -> dict[str, Any]:
    """CAS-update and restore one ref, but only inside a marked disposable repo."""
    repository = Path(repo).resolve()
    allowed = Path(disposable_root).resolve()
    if not _inside(repository, allowed) or not (repository / DISPOSABLE_MARKER).is_file():
        raise WarpSafetyError("atomic proof requires a marked repository inside disposable_root")
    if _run(repository, ("check-ref-format", target_ref), check=False).returncode != 0:
        raise WarpSafetyError("invalid target_ref")
    base = _git(repository, "rev-parse", "--verify", f"{expected_base}^{{commit}}").lower()
    candidate = _git(repository, "rev-parse", "--verify", f"{candidate_head}^{{commit}}").lower()
    before = _git(repository, "rev-parse", "--verify", target_ref).lower()
    if before != base:
        raise WarpSafetyError("target ref is stale; compare-and-swap proof blocked")
    landed = False
    try:
        _run(repository, ("update-ref", target_ref, candidate, base))
        landed = _git(repository, "rev-parse", target_ref).lower() == candidate
        if not landed:
            raise WarpError("atomic land verification failed")
    finally:
        current = _run(repository, ("rev-parse", "--verify", target_ref), check=False).stdout.strip().lower()
        if current == candidate:
            _run(repository, ("update-ref", target_ref, base, candidate))
    after = _git(repository, "rev-parse", "--verify", target_ref).lower()
    if after != base:
        raise WarpError("disposable rollback verification failed")
    return {
        "schema_version": "imperium.atomic_land_rollback_proof.v1",
        "verdict": "PASS_PROVEN",
        "repository": str(repository),
        "target_ref": target_ref,
        "base_head": base,
        "candidate_head": candidate,
        "land_compare_and_swap_proven": landed,
        "rollback_compare_and_swap_proven": True,
        "final_ref": after,
        "commands": [
            ["git", "update-ref", target_ref, candidate, base],
            ["git", "update-ref", target_ref, base, candidate],
        ],
        "timestamp_utc": _utc_now(),
    }
