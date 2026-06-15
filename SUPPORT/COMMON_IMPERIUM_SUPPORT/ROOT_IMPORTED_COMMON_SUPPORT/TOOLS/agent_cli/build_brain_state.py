#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ledger_path = ROOT / "LEDGER" / "brain_event_ledger.jsonl"
    out_path = ROOT / "REPORTS" / "BRAIN_STATE_SNAPSHOT_V0_1.json"

    event_types = Counter()
    agents = Counter()

    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            event_types[item.get("event_type", "UNKNOWN")] += 1
            agents[item.get("agent", "UNKNOWN")] += 1

    snapshot = {
        "ledger_path": str(ledger_path),
        "event_type_counts": dict(event_types),
        "agent_event_counts": dict(agents),
    }
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"BRAIN_STATE_JSON {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
