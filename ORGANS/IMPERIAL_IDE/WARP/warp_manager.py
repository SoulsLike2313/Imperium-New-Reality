#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path
SURFACE="IMPERIUM_WARP_MANAGER_V0_1"
REQUIRED_ROOT_FILES=["MANIFEST.json","TASK_SPEC.md","ACCEPTANCE_GATES.md","OUTPUT_REQUIREMENTS.md","TASK_ROUTE_MANIFEST_TEMPLATE.json","TASK_START_ACK_TEMPLATE.json","README.md"]
ORGANS=["DOCTRINARIUM","OFFICIO_AGENTIS","ASTRONOMICON","ADMINISTRATUM","MECHANICUS","INQUISITION","STRATEGIUM","SCHOLA_IMPERIALIS"]

def git(repo,*args):
    return subprocess.run(["git","-C",str(repo),*args],text=True,capture_output=True)

def registry_path(repo): return Path(repo)/"ORGANS"/"IMPERIAL_IDE"/"WARP"/"warp_registry.json"
def active_path(repo): return Path(repo)/"ORGANS"/"IMPERIAL_IDE"/"WARP"/"active_task.json"
def write_json(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2),encoding='utf-8')
def read_json(path,default):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return default

def default_warp_root(repo):
    return Path(str(repo).replace('_H','_WARP_ZONES')) if str(repo).endswith('_H') else Path(str(repo)+"_WARP_ZONES")

def cmd_create(args):
    repo=Path(args.repo_root).resolve(); root=Path(args.warp_root) if args.warp_root else default_warp_root(repo); root.mkdir(parents=True,exist_ok=True)
    stamp=time.strftime('%Y%m%d_%H%M%S'); path=root/f"WARP_{stamp}"
    main=str(repo).replace('_H','') if str(repo).endswith('_H') else str(repo)
    # Safe copy fallback; avoid copying volatile dirs.
    ignore=shutil.ignore_patterns('.git','node_modules','playwright-report','test-results','_H_PATCH_BACKUPS','H_PATCH_*','*.zip')
    shutil.copytree(main, path, ignore=ignore)
    data={"mode":"WARP_CREATED","path":str(path),"created_at_utc":time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),"main_source":main,"active_task_required":True,"stage_progress":{"done":0,"total":0}}
    write_json(registry_path(repo),data); print(json.dumps({"status":"PASS","surface":SURFACE,"warp":data},indent=2))

def task_template_files(task_id):
    manifest={"task_id":task_id,"task_title":"Fill this title","owner_language":"RU","taskpack_internal_language":"EN","language_and_encoding_policy":{"taskpack_internal_files":"ENGLISH_UTF8_ASCII_COMPATIBLE","canonical_repo_artifacts":"ENGLISH_UTF8_ASCII_COMPATIBLE","owner_facing_russian_runtime_output":"ROUTED_THROUGH_OFFICIO_OWNER_RU","cyrillic_in_taskpack":"FORBIDDEN_EXCEPT_OFFICIO_OWNER_RU","localization_exception":"OWNER_RU_ONLY"},"organs":ORGANS,"route":{"target_contour":"PC","requires_astronomicon_admission":True,"requires_taskpack_before_work":True}}
    return {
      "MANIFEST.json":json.dumps(manifest,indent=2),
      "TASK_SPEC.md":"# TASK SPEC\n\nTask id: %s\n\n## Objective\nFill objective here.\n\n## Scope\nFill scope.\n\n## Stages\n1. Intake\n2. Work\n3. Evidence\n4. Delivery\n"%task_id,
      "ACCEPTANCE_GATES.md":"# ACCEPTANCE GATES\n\n- Gate 1: taskpack admitted by Astronomicon.\n- Gate 2: work occurs in WARP contour.\n- Gate 3: smoke / tests / evidence pass.\n- Gate 4: owner accepts.\n",
      "OUTPUT_REQUIREMENTS.md":"# OUTPUT REQUIREMENTS\n\n- Audit/report bundle required.\n- No source mutation unless task explicitly allows it.\n- No commit or push without owner acceptance.\n",
      "TASK_ROUTE_MANIFEST_TEMPLATE.json":json.dumps({"task_id":task_id,"route":"PC","organs":ORGANS,"servitor_mode":"AUDIT_OR_WORK_AS_REQUESTED"},indent=2),
      "TASK_START_ACK_TEMPLATE.json":json.dumps({"task_id":task_id,"start_ack":"start task","requires_active_registry":True},indent=2),
      "README.md":"# Astronomicon Taskpack\n\nRoot files must stay in this ZIP root. Machine files are English/UTF-8. Owner-facing Russian text must be routed through Officio documents.\n"
    }

def cmd_export_template(args):
    repo=Path(args.repo_root).resolve(); outdir=repo/"ORGANS"/"IMPERIAL_IDE"/"WARP"/"task_templates"; outdir.mkdir(parents=True,exist_ok=True)
    task_id=args.task_id or f"TASK-FILL-ME-{time.strftime('%Y%m%d-%H%M%S')}"; zip_path=outdir/f"{task_id}_ASTRONOMICON_FORM.zip"
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in task_template_files(task_id).items(): z.writestr(name,content)
    print(json.dumps({"status":"PASS","surface":SURFACE,"task_template_zip":str(zip_path)},indent=2))

def cmd_start_work(args):
    repo=Path(args.repo_root).resolve(); active=read_json(active_path(repo),{})
    if not active.get('id'):
        print(json.dumps({"status":"BLOCKED","surface":SURFACE,"reason":"NO_ACTIVE_ASTRONOMICON_TASKPACK","message":"Register or select active taskpack before work."},indent=2)); return
    reg=read_json(registry_path(repo),{})
    reg.update({"mode":"WORK_ACTIVE","active_task_id":active.get('id'),"started_at_utc":time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}); write_json(registry_path(repo),reg)
    print(json.dumps({"status":"PASS","surface":SURFACE,"warp":reg},indent=2))

def cmd_validate(args):
    repo=Path(args.repo_root).resolve(); dirty=git(repo,'status','--short').stdout.splitlines(); reg=read_json(registry_path(repo),{})
    checks={"active_task_present":bool(read_json(active_path(repo),{}).get('id')),"warp_exists":bool(reg.get('path')),"dirty_classification_required":bool(dirty),"commit_push_gated":True}
    print(json.dumps({"status":"PASS_WITH_WARNINGS","surface":SURFACE,"checks":checks,"dirty_count":len(dirty),"dirty_preview":dirty[:80]},indent=2))

def cmd_status(args):
    repo=Path(args.repo_root).resolve(); print(json.dumps({"status":"PASS","surface":SURFACE,"registry":read_json(registry_path(repo),{}),"active_task":read_json(active_path(repo),{})},indent=2))

ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); sub=ap.add_subparsers(dest='cmd')
sub.add_parser('create').add_argument('--warp-root',default='')
sub.add_parser('start-work')
sub.add_parser('status')
sub.add_parser('validate')
et=sub.add_parser('export-task-template'); et.add_argument('--task-id',default='')
args=ap.parse_args()
if args.cmd=='create': cmd_create(args)
elif args.cmd=='start-work': cmd_start_work(args)
elif args.cmd=='status': cmd_status(args)
elif args.cmd=='validate': cmd_validate(args)
elif args.cmd=='export-task-template': cmd_export_template(args)
else: ap.print_help(); sys.exit(2)
