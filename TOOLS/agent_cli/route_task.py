#!/usr/bin/env python3
import argparse
from imperium_ng_cli import cmd_route


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    raise SystemExit(cmd_route(args))
