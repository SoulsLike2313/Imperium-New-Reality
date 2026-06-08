#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_bridge import snapshot
ap=argparse.ArgumentParser(); ap.add_argument('--repo', default='../../..'); args=ap.parse_args()
out=Path(__file__).resolve().parents[1]/'app'/'imperium_snapshot.json'
out.write_text(json.dumps(snapshot(args.repo), indent=2), encoding='utf-8')
print(json.dumps({"status":"PASS","written":str(out)}, indent=2))
