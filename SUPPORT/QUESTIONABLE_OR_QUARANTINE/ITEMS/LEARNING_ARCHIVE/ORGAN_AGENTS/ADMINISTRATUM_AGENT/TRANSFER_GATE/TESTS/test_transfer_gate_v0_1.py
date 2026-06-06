#!/usr/bin/env python3
"""Synthetic end-to-end test for Administratum Transfer Gate V0.1."""
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
    fetch_vm2_response_bundle,
    send_vm2_prompt_pack,
    sha256_bytes,
    transfer_status,
    verify_prompt_pack,
)


TASK_ID = "TASK-SYNTHETIC-TRANSFER-GATE-V0_1"
RESPONSE_NAME = f"{TASK_ID}__VM2_RESPONSE_BUNDLE.zip"


def _sha_text_map(payloads: Dict[str, bytes]) -> str:
    lines = []
    for name in sorted(payloads):
        lines.append(f"{sha256_bytes(payloads[name])}  {name}")
    return "\n".join(lines) + "\n"


def build_prompt_pack(path: Path, *, bad_hash: bool = False) -> None:
    task_pack = {
        "task_id": TASK_ID,
        "required_starting_head": "b8e46c1fd04901c983df7761248702897ee2c289",
        "target_actor": "VM2_SERVITOR",
        "creation_gate": {
            "owner_trigger_phrase_exact": "Пиши промт",
            "trigger_phrase_verified_by_logos": True,
        },
    }
    payloads: Dict[str, bytes] = {
        "TASK_PACK.md": b"# Synthetic task pack\n",
        "task_pack.json": json.dumps(task_pack, ensure_ascii=False, indent=2).encode("utf-8"),
        "START_PROMPT.txt": b"You are VM2 Servitor for IMPERIUM.\n",
    }
    manifest = {
        "pack_type": "IMPERIUM_LOGOS_PROMPT_PACK",
        "schema_version": "0.1",
        "task_id": TASK_ID,
        "required_starting_head": task_pack["required_starting_head"],
        "target_actor": "VM2_SERVITOR",
        "files": [
            {"path": name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
            for name, data in sorted(payloads.items())
        ],
        "manifest_self_hash_mode": "MANIFEST.json self-hash omitted",
    }
    payloads["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    sums = _sha_text_map(payloads)
    if bad_hash:
        sums = sums.replace(sums[:64], "0" * 64, 1)
    payloads["SHA256SUMS.txt"] = sums.encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zip_obj:
        for name, data in payloads.items():
            zip_obj.writestr(name, data)


def build_response_bundle(path: Path, *, correlation_id: str) -> None:
    final_report = {
        "task_id": TASK_ID,
        "correlation_id": correlation_id,
        "verdict": "SYNTHETIC_PASS",
    }
    payloads: Dict[str, bytes] = {
        "FINAL_REPORT.md": b"# Synthetic response\n\n- verdict: SYNTHETIC_PASS\n",
        "final_report.json": json.dumps(final_report, ensure_ascii=False, indent=2).encode("utf-8"),
    }
    manifest = {
        "bundle_type": "IMPERIUM_VM2_RESPONSE_BUNDLE",
        "schema_version": "0.1",
        "task_id": TASK_ID,
        "files": [
            {"path": name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
            for name, data in sorted(payloads.items())
        ],
    }
    payloads["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    payloads["SHA256SUMS.txt"] = _sha_text_map(payloads).encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zip_obj:
        for name, data in payloads.items():
            zip_obj.writestr(name, data)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="administratum_transfer_gate_") as tmp:
        root = Path(tmp)
        runtime_root = root / "transfer_root"
        pack = root / "synthetic_prompt_pack.zip"
        bad_pack = root / "bad_prompt_pack.zip"
        build_prompt_pack(pack)
        build_prompt_pack(bad_pack, bad_hash=True)

        verify = verify_prompt_pack(pack, runtime_root)
        assert verify["verdict"] == "PASS", verify

        sent = send_vm2_prompt_pack(
            pack,
            step_name="Synthetic Transfer Gate Test",
            source_head="b8e46c1fd04901c983df7761248702897ee2c289",
            runtime_root=runtime_root,
        )
        assert sent["verdict"] == "SIGNED_FOR_MANUAL_VM2_TRANSFER", sent
        assert Path(sent["received_zip"]).exists(), sent
        assert Path(sent["receipt_path"]).exists(), sent

        bad_sent = send_vm2_prompt_pack(
            bad_pack,
            step_name="Synthetic Invalid Pack Test",
            source_head="b8e46c1fd04901c983df7761248702897ee2c289",
            runtime_root=runtime_root,
        )
        assert bad_sent["verdict"] == "BLOCKED_INVALID_PROMPT_PACK", bad_sent
        assert Path(bad_sent["quarantine_path"]).exists(), bad_sent

        response_dir = runtime_root / "OUTBOX" / "VM2_TO_PC" / TASK_ID
        response_dir.mkdir(parents=True, exist_ok=True)
        response_zip = response_dir / RESPONSE_NAME
        build_response_bundle(response_zip, correlation_id=str(sent["correlation_id"]))

        fetched = fetch_vm2_response_bundle(
            task_id=TASK_ID,
            expected_filename=RESPONSE_NAME,
            correlation_id=str(sent["correlation_id"]),
            runtime_root=runtime_root,
        )
        assert fetched["verdict"] == "FETCHED_VERIFIED", fetched

        mismatch = fetch_vm2_response_bundle(
            task_id=TASK_ID,
            expected_filename=RESPONSE_NAME,
            correlation_id="CORR-WRONG",
            runtime_root=runtime_root,
        )
        assert mismatch["verdict"] == "BLOCKED_RESPONSE_MISMATCH", mismatch
        assert Path(mismatch["quarantine_path"]).exists(), mismatch

        status = transfer_status(runtime_root)
        assert status["ledger_entries"] >= 4, status

        print(
            json.dumps(
                {
                    "test": "transfer_gate_v0_1_synthetic_e2e",
                    "verdict": "PASS",
                    "runtime_root": str(runtime_root),
                    "transfer_id": sent["transfer_id"],
                    "correlation_id": sent["correlation_id"],
                    "ledger_entries": status["ledger_entries"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
