from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root, resolve_output_path  # noqa: E402


TASK_ID = "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
REPORT_PATH = Path(
    "AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
    "/block_registry_check_receipt.json"
)
BLOCK_DIR = Path("AGENT_IDE/BLOCK_FOUNDATION")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Block foundation registry checker for Agent IDE V0.2.")
    parser.add_argument("--repo-root", default="", help="Optional New Reality repo root override.")
    parser.add_argument("--receipt-out", default=str(REPORT_PATH))
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
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

    out = resolve_output_path(args.receipt_out, repo_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
