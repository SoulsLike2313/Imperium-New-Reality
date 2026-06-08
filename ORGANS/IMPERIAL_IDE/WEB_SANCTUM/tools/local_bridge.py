#!/usr/bin/env python3
import argparse, json, os, subprocess, sys, time, zipfile, shutil
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

SURFACE = "WEB_SANCTUM_OPERATIONAL_SPINE_AND_WARP_V0_5"
VERSION = "0.5.0"

class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def run(cmd, cwd, timeout=120):
    p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, shell=False)
    return {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}

def git(repo, *args):
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

def snapshot(repo):
    repo = Path(repo).resolve()
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    head = git(repo, "rev-parse", "HEAD") or "unknown"
    dirty = git(repo, "status", "--short")
    is_h = str(repo).endswith("_H") or branch.startswith("h/")
    reg = repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "warp_registry.json"
    warp = {"mode":"NO_WARP_SELECTED","path":"","active_task_required":True,"stage_progress":{"done":0,"total":0}}
    if reg.exists():
        try: warp.update(json.loads(reg.read_text(encoding="utf-8")))
        except Exception: pass
    active = repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "active_task.json"
    task = {"id":"NO_ACTIVE_TASK","status":"WAITING_FOR_ASTRONOMICON_TASKPACK","next_action":"Create WARP or register taskpack through Astronomicon."}
    if active.exists():
        try: task.update(json.loads(active.read_text(encoding="utf-8")))
        except Exception: pass
    return {
        "status":"PASS_WITH_WARNINGS" if dirty else "PASS",
        "surface":SURFACE,
        "version":VERSION,
        "generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contour":{"current_contour":"H_CONTOUR" if is_h else "MAIN_OR_UNKNOWN","repo_root":str(repo).replace('\\','/'),"branch":branch,"head":head,"dirty_count":len([x for x in dirty.splitlines() if x.strip()]),"main_repo_candidate":str(repo).replace('_H','').replace('\\','/'),"h_repo_candidate":str(repo).replace('\\','/') if is_h else str(repo).replace('\\','/')+"_H"},
        "task":task,
        "warp":warp,
        "departments":["FREELANCE","TRADING"],
        "organs":["DOCTRINARIUM","OFFICIO_AGENTIS","ASTRONOMICON","ADMINISTRATUM","MECHANICUS","INQUISITION","STRATEGIUM","SCHOLA_IMPERIALIS"],
        "safety":{"real_execution_enabled":False,"live_llm_backend_enabled":False,"unsafe_shell_enabled":False,"trading_execution_enabled":False}
    }

def find_repo_root(start):
    p = Path(start).resolve()
    for x in [p, *p.parents]:
        if (x/"ORGANS").exists(): return x
    return p

def warp_tool(repo, *args):
    script = Path(repo)/"ORGANS"/"IMPERIAL_IDE"/"WARP"/"warp_manager.py"
    return run([sys.executable, str(script), "--repo-root", str(repo), *args], repo)

def report_tool(repo, *args):
    script = Path(repo)/"ORGANS"/"ADMINISTRATUM"/"REPORTS"/"final_report_bundle_builder_v0_1.py"
    return run([sys.executable, str(script), "--repo-root", str(repo), *args], repo)

def mech_tool(repo, *args):
    script = Path(repo)/"ORGANS"/"MECHANICUS"/"TOOL_REGISTRY"/"mechanicus_tool_registry_v0_1.py"
    return run([sys.executable, str(script), "--repo-root", str(repo), *args], repo)

class Handler(SimpleHTTPRequestHandler):
    repo_root = None
    actions = False
    def end_json(self, data, status=200):
        raw=json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status); self.send_header('content-type','application/json; charset=utf-8'); self.send_header('content-length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path.startswith('/api/health'):
            self.end_json({"status":"PASS","surface":SURFACE,"version":VERSION,"actions_enabled":self.actions,"repo_root":str(self.repo_root)})
        elif self.path.startswith('/api/snapshot'):
            self.end_json(snapshot(self.repo_root))
        else:
            return super().do_GET()
    def do_POST(self):
        if not self.path.startswith('/api/action'): self.end_json({"status":"FAIL","error":"unknown endpoint"},404); return
        n=int(self.headers.get('content-length','0') or 0); body=self.rfile.read(n).decode('utf-8') if n else '{}'
        try: req=json.loads(body)
        except Exception: req={}
        action=req.get('action','')
        if not self.actions:
            self.end_json({"status":"BLOCKED","message":"Actions disabled; command copied only.","action":action,"actions_enabled":False}); return
        repo=Path(self.repo_root)
        allowed = {
            "refresh_snapshot": lambda: {"status":"PASS","snapshot":snapshot(repo)},
            "create_warp": lambda: warp_tool(repo,"create"),
            "start_work": lambda: warp_tool(repo,"start-work"),
            "export_task_template": lambda: warp_tool(repo,"export-task-template"),
            "validate_warp": lambda: warp_tool(repo,"validate"),
            "build_report_bundle": lambda: report_tool(repo,"build"),
            "mechanicus_register_tool": lambda: mech_tool(repo,"register-sample"),
            "mechanicus_list_tools": lambda: mech_tool(repo,"list"),
            "run_playwright": lambda: run(["npm","run","test:pw"], repo/"ORGANS"/"IMPERIAL_IDE"/"WEB_SANCTUM", timeout=300),
            "run_playwright_screenshots": lambda: run(["npm","run","test:pw:screenshots"], repo/"ORGANS"/"IMPERIAL_IDE"/"WEB_SANCTUM", timeout=300),
            "open_repo": lambda: run(["explorer", str(repo)], repo),
            "open_reports": lambda: run(["explorer", str(repo/"ORGANS"/"IMPERIAL_IDE"/"STATION"/"reports")], repo),
            "open_tui": lambda: run([sys.executable, str(repo/"ORGANS"/"IMPERIAL_IDE"/"WORKBENCH"/"TUI"/"imperial_tui.py")], repo),
            "open_tk": lambda: run([sys.executable, str(repo/"ORGANS"/"IMPERIAL_IDE"/"LAUNCHER"/"imperial_launcher.py")], repo),
        }
        if action == "register_taskpack_pc":
            zip_path=req.get('zip_path','')
            if not zip_path or not zip_path.lower().endswith('.zip'):
                self.end_json({"status":"BLOCKED","message":"Provide a .zip taskpack path."}); return
            skill=repo/"ORGANS"/"ASTRONOMICON"/"SKILLS"/"TASKPACK_REGISTRATION_SKILL"/"astronomicon_taskpack_registration_skill_v0_1.py"
            self.end_json(run([sys.executable, str(skill), "--zip-path", zip_path, "--contour", "PC"], repo, timeout=180)); return
        if action not in allowed:
            self.end_json({"status":"BLOCKED","message":"Action not allowlisted","action":action},403); return
        self.end_json(allowed[action]())

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='../../..'); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=8790); ap.add_argument('--actions',action='store_true')
    args=ap.parse_args(); repo=find_repo_root(args.repo_root); app_dir=Path(__file__).resolve().parents[1]/'app'
    Handler.repo_root=repo; Handler.actions=args.actions; os.chdir(app_dir)
    print(f"WEB SANCTUM {SURFACE} serving {app_dir}"); print(f"repo: {repo}"); print(f"actions: {'ENABLED allowlisted only' if args.actions else 'DISABLED static/read-only'}"); print(f"http://{args.host}:{args.port}/")
    with ThreadingServer((args.host,args.port),Handler) as httpd: httpd.serve_forever()
if __name__=='__main__': main()
