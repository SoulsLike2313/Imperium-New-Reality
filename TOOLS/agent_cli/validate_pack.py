#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

REQUIRED = {
    "question": ["question_id", "task_id", "target_agent", "action", "payload"],
    "answer": ["answer_id", "question_id", "agent", "action", "verdict"],
    "task": ["task_id", "title", "requested_route"],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", required=True)
    parser.add_argument("--type", required=True, choices=sorted(REQUIRED))
    args = parser.parse_args()

    data = json.loads(Path(args.pack).read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED[args.type] if k not in data]
    if missing:
        print("VALIDATION FAIL")
        print("MISSING", ",".join(missing))
        return 1

    print("VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
