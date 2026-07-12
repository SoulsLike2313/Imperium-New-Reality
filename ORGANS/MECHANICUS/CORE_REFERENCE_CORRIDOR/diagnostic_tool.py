"""Fixed-argument process entrypoint for CORE_DIAGNOSTIC."""

from __future__ import annotations

import argparse
import json
import sys

from .diagnostic import collect_diagnostic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        result = collect_diagnostic(".")
    except Exception as exc:  # fixed process boundary converts failures to a typed result
        print(json.dumps({"verdict": "BLOCK", "error_code": "DIAGNOSTIC_FAILED", "message": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result.get("verdict") == "PASS_PROVEN" else 2


if __name__ == "__main__":
    sys.exit(main())

