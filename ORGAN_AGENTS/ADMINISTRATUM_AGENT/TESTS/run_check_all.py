#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'TOOLS' / 'administratum_agent_runner.py'

if __name__ == '__main__':
    cmd = [sys.executable, str(RUNNER), 'check-all', '--repo-root', str(ROOT.parents[2])]
    raise SystemExit(subprocess.call(cmd))
