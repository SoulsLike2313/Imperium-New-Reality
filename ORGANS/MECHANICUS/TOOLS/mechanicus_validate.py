import sys

from mechanicus_cli import main


if __name__ == "__main__":
    raise SystemExit(main(["validate-json", *sys.argv[1:]]))
