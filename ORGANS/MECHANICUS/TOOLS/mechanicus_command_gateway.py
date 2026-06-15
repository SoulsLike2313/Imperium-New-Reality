import sys

from mechanicus_cli import main


if __name__ == "__main__":
    tool_id = sys.argv[1] if len(sys.argv) > 1 else "MECHANICUS_DOCTOR"
    raise SystemExit(main(["dry-run-tool", tool_id]))
