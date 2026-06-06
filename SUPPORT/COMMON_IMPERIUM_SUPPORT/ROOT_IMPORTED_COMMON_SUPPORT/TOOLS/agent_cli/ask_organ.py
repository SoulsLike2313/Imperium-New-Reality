#!/usr/bin/env python3
import argparse
from imperium_ng_cli import cmd_ask


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--question", required=True)
    args = parser.parse_args()
    raise SystemExit(cmd_ask(args))
