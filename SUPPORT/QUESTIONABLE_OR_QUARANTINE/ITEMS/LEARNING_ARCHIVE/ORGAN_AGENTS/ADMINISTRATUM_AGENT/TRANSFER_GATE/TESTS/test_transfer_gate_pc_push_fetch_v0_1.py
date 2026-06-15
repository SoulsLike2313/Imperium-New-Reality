#!/usr/bin/env python3
"""PC-side transfer push/fetch regression for Administratum Transfer Gate V0.1."""
from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "SCRIPTS"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from transfer_gate_core_v0_1 import (  # noqa: E402
    fetch_vm2_response_bundle_remote,
    push_vm2_prompt_pack,
    sha256_bytes,
    verify_prompt_pack,
)

TASK_ID = "TASK-SYNTHETIC-PC-PUSH-FETCH-V0_1"
RESPONSE_NAME = f"{TASK_ID}__VM2_RESPONSE_BUNDLE.zip"


def _sha_text_map(payloads: Dict[str, bytes]) -> str:
    return "".join(f"{sha256_bytes(payload)}  {name}\n" for name, payload in sorted(payloads.items()))


def build_prompt_pack(path: Path) -> None:
    task_pack = {
        "task_id": TASK_ID,
        "required_starting_head": "a37b1805993e7db60631e9e15c5560ad786078e0",
        "target_actor": "VM2_SERVITOR",
        "creation_gate": {
            "owner_trigger_phrase_exact": "Пиши промт",
            "trigger_phrase_verified_by_logos": True,
        },
    }
    payloads: Dict[str, bytes] = {
        "TASK_PACK.md": b"# Synthetic PC push task\n",
        "task_pack.json": json.dumps(task_pack, ensure_ascii=False, indent=2).encode("utf-8"),
        "START_PROMPT.txt": b"VM2 Servitor synthetic prompt\n",
    }
    manifest = {
        "manifest_version": "PROMPT_PACK_MANIFEST_V0_1",
        "task_id": TASK_ID,
        "files": [
            {"path": name, "sha256": sha256_bytes(payload), "size_bytes": len(payload)}
            for name, payload in sorted(payloads.items())
        ],
        "notes": ["MANIFEST.json self-size omitted."],
    }
    payloads["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    payloads["SHA256SUMS.txt"] = _sha_text_map(payloads).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zip_obj:
        for name, payload in payloads.items():
            zip_obj.writestr(name, payload)


def build_response(path: Path, correlation_id: str) -> None:
    final_report = {
        "task_id": TASK_ID,
        "correlation_id": correlation_id,
        "verdict": "SYNTHETIC_PASS",
    }
    payloads: Dict[str, bytes] = {
        "FINAL_REPORT.md": b"# Synthetic response\n",
        "final_report.json": json.dumps(final_report, ensure_ascii=False, indent=2).encode("utf-8"),
    }
    manifest = {
        "bundle_type": "IMPERIUM_VM2_RESPONSE_BUNDLE",
        "schema_version": "0.1",
        "task_id": TASK_ID,
        "files": [
            {"path": name, "sha256": sha256_bytes(payload), "size_bytes": len(payload)}
            for name, payload in sorted(payloads.items())
        ],
    }
    payloads["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    payloads["SHA256SUMS.txt"] = _sha_text_map(payloads).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zip_obj:
        for name, payload in payloads.items():
            zip_obj.writestr(name, payload)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="administratum_pc_transfer_") as tmp:
        root = Path(tmp)
        runtime_root = root / "pc_runtime"
        remote_root = root / "mock_vm2_remote"
        pack = root / "synthetic_prompt.zip"
        build_prompt_pack(pack)

        missing = push_vm2_prompt_pack(None, step_name="Missing Pack", source_head="HEAD", runtime_root=runtime_root, remote_root=str(remote_root), transport="local")
        assert missing["verdict"] == "BLOCKED_INPUT_MISSING", missing

        bad = push_vm2_prompt_pack(root / "missing.zip", step_name="Bad Pack", source_head="HEAD", runtime_root=runtime_root, remote_root=str(remote_root), transport="local")
        assert bad["verdict"] == "BLOCKED_INPUT_MISSING", bad

        verify = verify_prompt_pack(pack, runtime_root)
        assert verify["verdict"] == "PASS", verify
        assert "manifest_self_size_mismatch:MANIFEST.json" not in verify["warnings"], verify

        dry = push_vm2_prompt_pack(pack, step_name="Dry Run", source_head="HEAD", runtime_root=runtime_root, remote_root=str(remote_root), transport="local", dry_run=True)
        assert dry["verdict"] == "BLOCKED_DRY_RUN_REMOTE_NOT_VERIFIED", dry

        pushed = push_vm2_prompt_pack(pack, step_name="Synthetic PC Push", source_head="HEAD", runtime_root=runtime_root, remote_root=str(remote_root), transport="local")
        assert pushed["verdict"] == "PUSHED_TO_VM2_REMOTE_VERIFIED", pushed
        assert Path(pushed["remote_file"]).exists(), pushed
        assert pushed["remote_sha256"] == pushed["payload_sha256"], pushed
        assert pushed["remote_size_bytes"] == pushed["payload_size_bytes"], pushed

        response_dir = remote_root / "OUTBOX" / "VM2_TO_PC" / TASK_ID
        response_dir.mkdir(parents=True, exist_ok=True)
        build_response(response_dir / RESPONSE_NAME, pushed["correlation_id"])
        duplicate_dir = response_dir / "duplicate"
        duplicate_dir.mkdir()
        build_response(duplicate_dir / RESPONSE_NAME, pushed["correlation_id"])

        ambiguous = fetch_vm2_response_bundle_remote(
            task_id=TASK_ID,
            expected_filename=RESPONSE_NAME,
            correlation_id=pushed["correlation_id"],
            runtime_root=runtime_root,
            remote_root=str(remote_root),
            transport="local",
        )
        assert ambiguous["verdict"] == "BLOCKED_AMBIGUOUS_RESPONSE_BUNDLES", ambiguous
        (duplicate_dir / RESPONSE_NAME).unlink()

        fetched = fetch_vm2_response_bundle_remote(
            task_id=TASK_ID,
            expected_filename=RESPONSE_NAME,
            correlation_id=pushed["correlation_id"],
            runtime_root=runtime_root,
            remote_root=str(remote_root),
            transport="local",
        )
        assert fetched["verdict"] == "FETCHED_FROM_VM2_ACCEPTED", fetched
        assert Path(fetched["local_path"]).exists(), fetched
        assert fetched["local_sha256"] == fetched["remote_sha256"], fetched

        print(
            json.dumps(
                {
                    "test": "transfer_gate_pc_push_fetch_v0_1",
                    "verdict": "PASS",
                    "remote_root": str(remote_root),
                    "runtime_root": str(runtime_root),
                    "transfer_id": pushed["transfer_id"],
                    "correlation_id": pushed["correlation_id"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
