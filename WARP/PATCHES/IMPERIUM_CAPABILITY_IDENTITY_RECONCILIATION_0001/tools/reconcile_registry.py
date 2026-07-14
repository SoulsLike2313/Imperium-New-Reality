from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone

EXPECTED = {
    "CORE_REPORT_BUILDER": {
        "registered": "6b1841f51a0562a5fa687a7fe8f1582484d9bb75e1374cefb426c86a19ab22ec",
        "actual": "8815c245531ead3e33d624394cf1d227b5e432b7aae5755555ad2f9b50a0d5a7",
    },
    "CORE_VALIDATION_SUITE": {
        "registered": "a587454054384c1f44e003a1963b3fb8b94e0231d60231fa3653b1061287c985",
        "actual": "a9e25ea01a0325bf2ac09b606d74a85a58e1f7f068be3c7ca8143ba7e98a1dc2",
    },
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def canonical_digest(value: dict) -> str:
    clone = dict(value)
    clone.pop("registry_digest", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

def atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)

def identity_rows(registry: dict) -> list[dict]:
    rows = []
    for item in registry.get("capabilities", []):
        if item.get("admission_state") != "ACTIVE":
            continue
        adapter = Path(str(item.get("adapter_path", "")))
        executable = Path(str(item.get("executable_path", "")))
        actual_adapter = sha256_file(adapter) if adapter.is_file() else "MISSING"
        actual_executable = sha256_file(executable) if executable.is_file() else "MISSING"
        rows.append({
            "capability_id": item.get("capability_id"),
            "adapter_path": str(adapter),
            "executable_path": str(executable),
            "registered_adapter_sha256": item.get("adapter_sha256"),
            "actual_adapter_sha256": actual_adapter,
            "registered_executable_sha256": item.get("executable_sha256"),
            "actual_executable_sha256": actual_executable,
            "adapter_match": actual_adapter == item.get("adapter_sha256"),
            "executable_match": actual_executable == item.get("executable_sha256"),
        })
    return rows

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--registry", required=True)
    p.add_argument("--receipt", required=True)
    args = p.parse_args()

    registry_path = Path(args.registry).resolve()
    receipt_path = Path(args.receipt).resolve()
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    before_digest = registry.get("registry_digest")
    measured_before_digest = canonical_digest(registry)
    if before_digest != measured_before_digest:
        raise SystemExit("BLOCK_REGISTRY_DIGEST_MISMATCH_BEFORE")

    rows_before = identity_rows(registry)
    mismatches = sorted(
        row["capability_id"]
        for row in rows_before
        if not row["adapter_match"] or not row["executable_match"]
    )
    if mismatches != sorted(EXPECTED):
        raise SystemExit(f"BLOCK_UNEXPECTED_IDENTITY_MISMATCHES: {mismatches}")

    by_id = {item.get("capability_id"): item for item in registry.get("capabilities", [])}
    changes = []
    for capability_id, expectation in EXPECTED.items():
        item = by_id.get(capability_id)
        if not isinstance(item, dict):
            raise SystemExit(f"BLOCK_CAPABILITY_MISSING: {capability_id}")
        if item.get("adapter_sha256") != expectation["registered"]:
            raise SystemExit(f"BLOCK_REGISTERED_HASH_DRIFT: {capability_id}")
        adapter = Path(str(item.get("adapter_path", "")))
        if not adapter.is_file():
            raise SystemExit(f"BLOCK_ADAPTER_MISSING: {capability_id}")
        actual = sha256_file(adapter)
        if actual != expectation["actual"]:
            raise SystemExit(f"BLOCK_ACTUAL_HASH_UNEXPECTED: {capability_id}:{actual}")
        item["adapter_sha256"] = actual
        changes.append({
            "capability_id": capability_id,
            "adapter_path": str(adapter),
            "old_adapter_sha256": expectation["registered"],
            "new_adapter_sha256": actual,
        })

    registry["registry_digest"] = canonical_digest(registry)
    atomic_write(registry_path, registry)

    reloaded = json.loads(registry_path.read_text(encoding="utf-8"))
    if reloaded.get("registry_digest") != canonical_digest(reloaded):
        raise SystemExit("BLOCK_REGISTRY_DIGEST_MISMATCH_AFTER")
    rows_after = identity_rows(reloaded)
    remaining = [
        row for row in rows_after
        if not row["adapter_match"] or not row["executable_match"]
    ]
    if remaining:
        raise SystemExit("BLOCK_ACTIVE_CAPABILITY_IDENTITY_REMAINS")

    receipt = {
        "schema_version": "imperium.capability_identity_reconciliation_receipt.v1",
        "patch_id": "IMPERIUM_CAPABILITY_IDENTITY_RECONCILIATION_0001",
        "verdict": "CAPABILITY_IDENTITY_RECONCILED",
        "reconciled_at_utc": utc_now(),
        "registry_path": str(registry_path),
        "registry_digest_before": before_digest,
        "registry_digest_after": reloaded["registry_digest"],
        "changes": changes,
        "active_capabilities_after": rows_after,
        "remaining_mismatches": [],
        "claim": "Only the two pre-measured stale adapter identities were changed.",
    }
    atomic_write(receipt_path, receipt)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "registry_digest_after": receipt["registry_digest_after"],
        "reconciled": [c["capability_id"] for c in changes],
        "receipt": str(receipt_path),
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
