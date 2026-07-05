#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, traceback
from pathlib import Path
TOOL_ID='mechanicus_task_tool_composition_planner.v0_4_strict_build_lane_aware'
LANE_READOUT=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json')
TOOLCHAIN=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json')
INVENTORY=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json')
BUILD=Path('ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json')
DEFAULT_OUT='ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json'
DEMANDS=[
 {'demand_id':'python_validator_or_scanner','keywords':['validator','scan','scanner','census','receipt','report','json','matrix','валидатор','скан','отчет','отчёт','матриц'],'preferred_lanes':['python','json_evidence','markdown_docs'],'required_validators':['python py_compile','json parse','receipt shape'],'typical_tools':['python','Mechanicus inventory scanner','language validation dispatch']},
 {'demand_id':'warp_runner_or_windows_operator','keywords':['pwsh','powershell','runner','run_','warp','patch pack','task pack','таск пак','патч пак'],'preferred_lanes':['powershell','python','json_evidence'],'required_validators':['pwsh version','runner receipt','no direct master mutation'],'typical_tools':['pwsh','WARP runner','git']},
 {'demand_id':'tauri_app_or_cockpit','keywords':['tauri','cockpit','app','webview','frontend','ui','ux','приложение','кокпит','интерфейс'],'preferred_lanes':['node_frontend','css_ui','rust','json_evidence'],'required_validators':['npm build','cargo check','runtime FPS proof','UX proof receipt'],'typical_tools':['node','npm','rustc','cargo','Tauri app shell']},
 {'demand_id':'rust_backend_or_compiled_gate','keywords':['rust','cargo','compiled','tauri backend','strict gate','безопасность','строгий','компил'],'preferred_lanes':['rust','json_evidence'],'required_validators':['cargo check','cargo fmt','cargo clippy future'],'typical_tools':['rustc','cargo']},
 {'demand_id':'visual_ui_polish','keywords':['css','style','animation','ornament','gothic','metal','fps','visual','reference','готика','орнамент','анимация','визуал','реф'],'preferred_lanes':['css_ui','node_frontend','json_evidence'],'required_validators':['CSS structural scan','FPS proof','reference fidelity report','no CSS monolith'],'typical_tools':['CSS lane','Tauri app','FPS watchdog']},
 {'demand_id':'game_engine_or_procedural_world','keywords':['game','engine','godot','bevy','unity','unreal','игра','движок','процедур'],'preferred_lanes':['node_frontend','rust','css_ui','go_future','cpp_future'],'required_validators':['engine capability proof','runtime performance proof','asset pipeline proof'],'typical_tools':['game engine candidate','runtime profiler','asset pipeline']},
 {'demand_id':'external_repo_product_work','keywords':['external repo','внешний репозиторий','продукт','рынок','script','скрипт','repo analysis','репо'],'preferred_lanes':['python','powershell','json_evidence','markdown_docs'],'required_validators':['repo scan','language lane selection','task-specific tool admission'],'typical_tools':['python','git','pwsh','Mechanicus tool inventory']}]
DEFAULT_STATES={'python':'LANE_READY_BASELINE','powershell':'LANE_READY_BASELINE','rust':'LANE_READY_BASELINE','node_frontend':'LANE_READY_BASELINE','css_ui':'LANE_READY_BASELINE','json_evidence':'LANE_READY_BASELINE','markdown_docs':'LANE_READY_BASELINE','toml_config':'LANE_READY_BASELINE','go_future':'LANE_FUTURE_CAPABILITY','cpp_future':'LANE_FUTURE_CAPABILITY'}
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load(p):
    try:
        return json.loads(p.read_text(encoding='utf-8-sig')) if p.is_file() else {}
    except Exception as e: return {'_load_error':str(e)}
def write(p,d):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
def read_task(repo, task_text, task_file, patch_id):
    if task_text: return 'inline_task_text', task_text
    if task_file:
        p=repo/task_file; return task_file, p.read_text(encoding='utf-8',errors='replace') if p.is_file() else ''
    if patch_id:
        for rel in [f'WARP/PATCHES/{patch_id}/PATCH_PACK.md',f'WARP/PATCHES/{patch_id}/TASK_PACK.md']:
            p=repo/rel
            if p.is_file(): return rel,p.read_text(encoding='utf-8',errors='replace')
        return f'WARP/PATCHES/{patch_id}',''
    return 'empty_task',''
def states(readout):
    s=dict(DEFAULT_STATES)
    for l in readout.get('lanes',[]) or []:
        if isinstance(l,dict) and l.get('lane_id') and l.get('state'): s[str(l['lane_id'])]=str(l['state'])
    return s
def classify(text):
    low=' '+(text or '').lower().replace('\n',' ')+' '; out=[]
    for d in DEMANDS:
        hits=[kw for kw in d['keywords'] if kw.lower() in low]
        if hits: out.append({**d,'score':min(100,20+len(hits)*14),'matched_keywords':hits})
    out.sort(key=lambda x:x['score'], reverse=True)
    return out or [{'demand_id':'unknown_or_low_signal_task','score':25,'matched_keywords':[],'preferred_lanes':['python','json_evidence','markdown_docs'],'required_validators':['Owner clarification','Mechanicus research/readout'],'typical_tools':['python','Mechanicus planner']}]
def build_bonus(build,did):
    if build.get('verdict')!='PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION': return 0
    return 12 if did in {'tauri_app_or_cockpit','rust_backend_or_compiled_gate','visual_ui_polish','warp_runner_or_windows_operator','python_validator_or_scanner'} else 4
def score(d,st,build):
    pref=d.get('preferred_lanes',[]); rows=[]; ready=debt=future=missing=0
    for lane in pref:
        state=st.get(lane,'LANE_UNKNOWN'); rows.append({'lane_id':lane,'state':state})
        if state=='LANE_READY_BASELINE': ready+=1
        elif state=='LANE_MEASURED_WITH_DEBT': debt+=1
        elif state=='LANE_FUTURE_CAPABILITY': future+=1
        else: missing+=1
    total=max(1,len(pref)); bonus=build_bonus(build,d.get('demand_id'))
    dims={'requirement_fit':min(100,d.get('score',0)+20),'availability_and_admission':max(0,int((ready/total)*100)-debt*10-future*20-missing*25),'cleanliness_validation_coverage':max(0,min(100,50+ready*10-debt*12-future*18-missing*20+bonus)),'reliability_and_receipts':max(0,min(100,55+ready*8-debt*10-future*16-missing*20+bonus)),'cost_and_runtime_weight':60 if d.get('demand_id') in {'game_engine_or_procedural_world','tauri_app_or_cockpit','visual_ui_polish'} else 82,'maintainability_no_monolith':82 if len(pref)<=4 else 65,'strict_build_bonus':bonus}
    if future or missing: dims['cost_and_runtime_weight']=max(20,dims['cost_and_runtime_weight']-20)
    val=(dims['requirement_fit']*25+dims['availability_and_admission']*20+dims['cleanliness_validation_coverage']*20+dims['reliability_and_receipts']*15+dims['cost_and_runtime_weight']*10+dims['maintainability_no_monolith']*10)/100
    verdict='RECOMMENDED_PRIMARY_STACK' if val>=85 else 'ACCEPTABLE_WITH_DEBT' if val>=70 else 'POSSIBLE_REWORK_REQUIRED' if val>=50 else 'NOT_RECOMMENDED_OR_CAPABILITY_MISSING'
    return {'demand_id':d.get('demand_id'),'score_0_to_100':round(val,2),'verdict':verdict,'preferred_lanes':pref,'lane_states':rows,'dimensions':dims,'required_validators':d.get('required_validators',[]),'typical_tools':d.get('typical_tools',[])}
def tool_ok(toolchain,name):
    return any(isinstance(r,dict) and r.get('name')==name and r.get('ok') for r in toolchain.get('results',[]) or [])
def has_engine(inv):
    text=' '.join((str(r.get('name',''))+' '+str(r.get('path_or_command',''))).lower() for r in inv.get('records',[]) or [] if isinstance(r,dict))
    return any(x in text for x in ['godot','bevy','unity','unreal','game engine'])
def gaps(text, classes, toolchain, inv, build):
    low=(text or '').lower(); out=[]
    if any(c.get('demand_id')=='game_engine_or_procedural_world' for c in classes) and not has_engine(inv): out.append({'capability_id':'GAME_ENGINE_CAPABILITY_NOT_INVENTORIED','severity':'OWNER_VISIBLE_GAP','meaning':'Game/procedural engine requested or implied, but no admitted engine is inventoried.'})
    if ('go' in low or 'golang' in low) and not tool_ok(toolchain,'go_version'): out.append({'capability_id':'GO_TOOLCHAIN_MISSING','severity':'CAPABILITY_DEBT','meaning':'Go requested or implied, but go toolchain is missing.'})
    if any(x in low for x in ['c++','cpp','cmake']) and not tool_ok(toolchain,'cmake_version'): out.append({'capability_id':'CPP_CMAKE_TOOLCHAIN_MISSING','severity':'CAPABILITY_DEBT','meaning':'C++/CMake requested or implied, but CMake/compiler capability is missing.'})
    if any(x in low for x in ['strict','build','runtime','cargo check','npm build','строг']) and build.get('verdict')!='PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION': out.append({'capability_id':'STRICT_BUILD_LANE_REQUIRED','severity':'NEXT_VALIDATOR_REQUIRED','meaning':'Task asks for strict/build/runtime confidence; strict build lane has not passed.'})
    if any(x in low for x in ['reference','fidelity','реф','pixel','ui','ux']): out.append({'capability_id':'UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI','severity':'CONDITIONAL_GAP','meaning':'UI/reference work needs dedicated fidelity proof; CSS alone cannot prove target UI.'})
    return out
def make(repo, task_text, task_file, patch_id):
    src,text=read_task(repo,task_text,task_file,patch_id); readout=load(repo/LANE_READOUT); toolchain=load(repo/TOOLCHAIN); inv=load(repo/INVENTORY); build=load(repo/BUILD); st=states(readout); cls=classify(text); combos=[score(c,st,build) for c in cls]; combos.sort(key=lambda x:x['score_0_to_100'], reverse=True); rec=combos[0] if combos else None
    validators=[]
    for c in combos[:3]:
        for v in c.get('required_validators',[]):
            if v not in validators: validators.append(v)
    miss=gaps(text,cls,toolchain,inv,build); blockers=[m for m in miss if m.get('severity') in {'OWNER_VISIBLE_GAP','OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED'}]
    return {'tool_id':TOOL_ID,'generated_at_utc':utc(),'repo_root':str(repo),'task_source':src,'task_text_preview':(text or '')[:1200],'strict_build_report':BUILD.as_posix() if build else None,'task_demand_classification':cls,'candidate_combinations_with_scores':combos,'recommended_tool_stack':rec,'recommended_language_lanes':rec.get('preferred_lanes',[]) if isinstance(rec,dict) else [],'required_validators':validators,'missing_capabilities':miss,'owner_visible_blockers':blockers,'verdict':'PLAN_READY_WITH_CAPABILITY_GAPS' if miss else 'PLAN_READY','not_claimed':['task executed','runtime proof','dependencies installed','100% clean','strict build pass unless strict build receipt exists'],'warnings':['Tool composition plan is advisory and does not execute the task.','Strict build lane affects reliability score only when receipt exists.']}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--task-text'); ap.add_argument('--task-file'); ap.add_argument('--patch-id'); ap.add_argument('--out',default=DEFAULT_OUT); a=ap.parse_args(); repo=Path(a.repo_root).resolve()
    try: plan=make(repo,a.task_text,a.task_file,a.patch_id)
    except Exception as e: plan={'tool_id':TOOL_ID,'generated_at_utc':utc(),'repo_root':str(repo),'verdict':'PLAN_READY_WITH_PLANNER_EXCEPTION_DEBT','missing_capabilities':[{'capability_id':'PLANNER_EXCEPTION','severity':'REWORK_REQUIRED','meaning':repr(e)}],'exception_trace_tail':traceback.format_exc()[-4000:]}
    write(repo/a.out,plan); print(json.dumps(plan,ensure_ascii=False,indent=2,default=str)); return 0
if __name__=='__main__': raise SystemExit(main())
