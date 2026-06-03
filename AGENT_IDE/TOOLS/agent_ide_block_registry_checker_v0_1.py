from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


TASK_ID = "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
REPORT_PATH = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
    "/block_registry_check_receipt.json"
)
BLOCK_DIR = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/BLOCK_FOUNDATION")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Block foundation registry checker for Agent IDE V0.2.")
    parser.add_argument("--repo-root", default="E:/IMPERIUM")
    parser.add_argument("--receipt-out", default=str(REPORT_PATH))
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    block_dir = repo_root / BLOCK_DIR
    required = [
        "block_schema_v0_1.json",
        "block_registry_seed_v0_1.json",
        "layout_manifest_schema_v0_1.json",
        "theme_tokens_v0_1.json",
        "material_registry_v0_1.json",
        "animation_registry_v0_1.json",
    ]

    missing = [name for name in required if not (block_dir / name).exists()]
    warnings: List[str] = []
    status = "PASS"

    registry_payload: Dict[str, Any] = {}
    if not missing:
        registry_payload = _read_json(block_dir / "block_registry_seed_v0_1.json")
        blocks = registry_payload.get("blocks", [])
        if not isinstance(blocks, list) or not blocks:
            status = "FAIL"
            warnings.append("Block registry seed has no blocks.")
        for idx, block in enumerate(blocks):
            for required_key in (
                "block_id",
                "name",
                "level",
                "data_sources",
                "display_contract",
                "skin_material_ref",
                "animation_policy_ref",
                "safety_level",
                "projection_visibility",
            ):
                if required_key not in block:
                    status = "FAIL"
                    warnings.append(f"Missing key {required_key} in block index {idx}.")
    else:
        status = "FAIL"
        warnings.append("Missing required block foundation files.")

    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "missing_files": missing,
        "warnings": warnings,
        "block_count": len(registry_payload.get("blocks", [])) if registry_payload else 0,
        "block_levels": sorted(
            {str(item.get("level", "UNKNOWN")) for item in registry_payload.get("blocks", [])}
        )
        if registry_payload
        else [],
    }

    out = Path(args.receipt_out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
