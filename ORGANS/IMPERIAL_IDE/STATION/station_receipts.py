from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_receipt(receipt_type: str, status: str, **fields: Any) -> dict[str, Any]:
    return {
        "schema_version": "imperial_ide.station_receipt.v0_2",
        "receipt_type": receipt_type,
        "status": status,
        "timestamp_utc": utc_now(),
        **fields,
    }


def write_receipt(path: Path, receipt: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()
