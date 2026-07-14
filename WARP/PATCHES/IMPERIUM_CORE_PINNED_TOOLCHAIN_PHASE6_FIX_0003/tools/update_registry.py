from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("registry_digest", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def version(path: Path) -> str:
    completed = subprocess.run(
        [str(path), "--version"], shell=False, check=False, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=10,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"VERSION_PROBE_FAILED: {path}")
    return completed.stdout.strip() or completed.stderr.strip()


def record(capability_id: str, path: Path, operations: list[str], roots: list[str]) -> dict[str, Any]:
    path = path.resolve(strict=True)
    digest = sha256_file(path)
    return {
        "capability_id": capability_id,
        "type": "SYSTEM_EXECUTABLE",
        "adapter_id": "PINNED_EXECUTABLE_V0_1",
        "adapter_path": str(path),
        "adapter_sha256": digest,
        "executable_path": str(path),
        "executable_sha256": digest,
        "version": version(path),
        "admission_state": "ACTIVE",
        "declared_effect": "READ_ONLY",
        "actual_effect_class": "READ_ONLY",
        "allowed_operations": operations,
        "allowed_read_roots": roots,
        "allowed_write_roots": [],
        "timeout_seconds": 60,
        "environment_profile": "RUST_PYTHON_BRIDGE_MINIMAL_ENV_V2",
        "cost_model": {"unit": "local_process", "estimated_units": 1, "external_cost": 0},
        "trust_level": "HOST_PINNED_HASH_VERIFIED",
        "last_validation": "PENDING_FIRST_BRIDGE_USE",
        "quarantine_reason": "",
        "fixed_argv": [],
        "parameter_schema": {"type": "object", "additionalProperties": False},
    }


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--git", required=True)
    parser.add_argument("--pwsh", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--reality", required=True)
    args = parser.parse_args()

    registry_path = Path(args.registry).resolve()
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "imperium.core_reference_corridor.capability_registry.v0_1":
        raise RuntimeError("REGISTRY_SCHEMA_MISMATCH")
    if data.get("default_policy") != "DENY":
        raise RuntimeError("REGISTRY_DEFAULT_DENY_MISSING")
    roots = [str(Path(args.reality).resolve()), str(Path(args.worktree).resolve())]
    capabilities = [
        item for item in data.get("capabilities", [])
        if item.get("capability_id") not in {"CORE_GIT", "CORE_PWSH"}
    ]
    capabilities.extend([
        record("CORE_GIT", Path(args.git), ["repository_read", "diff_read", "status_read"], roots),
        record("CORE_PWSH", Path(args.pwsh), ["version_probe"], roots),
    ])
    data["capabilities"] = capabilities
    data["registry_digest"] = canonical_digest(data)
    atomic_write(registry_path, data)
    print(json.dumps({
        "verdict": "PINNED_TOOLCHAIN_REGISTERED",
        "git": capabilities[-2]["executable_path"],
        "git_sha256": capabilities[-2]["executable_sha256"],
        "pwsh": capabilities[-1]["executable_path"],
        "pwsh_sha256": capabilities[-1]["executable_sha256"],
        "registry_digest": data["registry_digest"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
