#!/usr/bin/env python3
import argparse,json,time
from pathlib import Path
SURFACE='MECHANICUS_TOOL_REGISTRY_V0_1'
def reg_path(repo): return Path(repo)/'ORGANS'/'MECHANICUS'/'TOOL_REGISTRY'/'tool_registry.json'
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return {'tools':[]}
def save(p,data): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('cmd',nargs='?',default='list'); args=ap.parse_args(); p=reg_path(args.repo_root); data=load(p)
    if args.cmd=='register-sample':
        data['tools'].append({'id':'web_sanctum_bridge','safety':'ALLOWLISTED_ACTIONS_ONLY','registered_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'arbitrary_shell':False}); save(p,data)
    print(json.dumps({'status':'PASS','surface':SURFACE,'registry':data},indent=2))
if __name__=='__main__': main()
