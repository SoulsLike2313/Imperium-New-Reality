#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path
TOOL_ID='mechanicus_json_evidence_strict_lane_scanner.v0_1'
EXCLUDE={'.git','node_modules','target','dist','build','__pycache__','.venv','venv','.mypy_cache','.ruff_cache','.pytest_cache','.next','.turbo','.idea','.vscode'}
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def cls(rel:str):
    low=rel.lower()
    if rel.startswith('WARP/PATCHES/') or '/FILES_TO_LAND/' in rel: return 'PATCH_PAYLOAD_CANDIDATE'
    if rel.startswith('SUPPORT/QUARANTINE/') or '/QUARANTINE/' in rel: return 'QUARANTINE_EVIDENCE_DEBT'
    if '/FIXTURES/' in rel and any(x in low for x in ['malformed','invalid','bad_json','negative']): return 'EXPECTED_NEGATIVE_FIXTURE'
    return 'CANONICAL_EVIDENCE'
def candidate(p:Path,repo:Path):
    if not p.is_file() or p.suffix.lower() not in {'.json','.jsonl'}: return False
    try: parts=set(p.relative_to(repo).parts)
    except Exception: return False
    return not bool(parts & EXCLUDE)
def parse(p:Path):
    try:
        if p.suffix.lower()=='.jsonl':
            for i,line in enumerate(p.read_text(encoding='utf-8-sig',errors='replace').splitlines(),1):
                if line.strip(): json.loads(line)
        else: json.loads(p.read_text(encoding='utf-8-sig'))
        return None
    except Exception as e: return str(e)
def scan(repo:Path):
    files=sorted([p for p in repo.rglob('*') if candidate(p,repo)], key=lambda p:p.relative_to(repo).as_posix())
    errs=[]; counts={}; err_counts={}
    for p in files:
        rel=p.relative_to(repo).as_posix(); c=cls(rel); counts[c]=counts.get(c,0)+1; e=parse(p)
        if e:
            rec={'path':rel,'evidence_class':c,'parser_mode':'jsonl_one_json_value_per_nonempty_line' if p.suffix.lower()=='.jsonl' else 'json_parse','error':e}
            errs.append(rec); err_counts[c]=err_counts.get(c,0)+1
    canonical=[e for e in errs if e['evidence_class']=='CANONICAL_EVIDENCE']
    fixtures=[e for e in errs if e['evidence_class']=='EXPECTED_NEGATIVE_FIXTURE']
    quarantine=[e for e in errs if e['evidence_class']=='QUARANTINE_EVIDENCE_DEBT']
    patch=[e for e in errs if e['evidence_class']=='PATCH_PAYLOAD_CANDIDATE']
    clean=len(canonical)==0
    return {'tool_id':TOOL_ID,'generated_at_utc':utc(),'repo_root':str(repo),'files_checked':len(files),'parse_error_count':len(errs),'counts_by_class':counts,'counts_by_error_class':err_counts,'canonical_parse_debt_count':len(canonical),'expected_negative_fixture_count':len(fixtures),'quarantine_parse_debt_count':len(quarantine),'patch_candidate_parse_error_count':len(patch),'canonical_parse_debt':canonical,'expected_negative_fixtures':fixtures,'quarantine_parse_debt':quarantine,'patch_candidate_parse_errors':patch[:100],'json_evidence_lane_state':'LANE_READY_BASELINE' if clean else 'LANE_MEASURED_WITH_DEBT','verdict':'PASS_JSON_EVIDENCE_CANONICAL_STRICT_CLEAN_WITH_CLASSIFIED_DEBT' if clean else 'FAIL_JSON_EVIDENCE_CANONICAL_PARSE_DEBT','not_claimed':['schema correctness','semantic evidence truth','quarantine repaired','fixtures valid','receipt honesty'],'warnings':['Expected negative fixtures are classified and do not block canonical JSON readiness.','Quarantine parse debt remains visible and is not erased.','This is parse strictness only, not schema or semantic validation.']}
def write_md(path:Path,r:dict):
    def lines(xs): return '\n'.join(f"- `{x['path']}` — {x['error']}" for x in xs) or '- none'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(f"""# MECHANICUS JSON EVIDENCE STRICT LANE REPORT V0.1\n\ntool_id: `{r['tool_id']}`  \nverdict: `{r['verdict']}`  \nlane_state: `{r['json_evidence_lane_state']}`  \ngenerated_at_utc: `{r['generated_at_utc']}`\n\n## Counts\n\n- files_checked: `{r['files_checked']}`\n- parse_error_count: `{r['parse_error_count']}`\n- canonical_parse_debt_count: `{r['canonical_parse_debt_count']}`\n- expected_negative_fixture_count: `{r['expected_negative_fixture_count']}`\n- quarantine_parse_debt_count: `{r['quarantine_parse_debt_count']}`\n\n## Canonical parse debt\n\n{lines(r.get('canonical_parse_debt',[]))}\n\n## Expected negative fixtures\n\n{lines(r.get('expected_negative_fixtures',[]))}\n\n## Quarantine parse debt\n\n{lines(r.get('quarantine_parse_debt',[]))}\n\n## Boundary\n\n```text\nThis proves canonical JSON/JSONL parse cleanliness only.\nIt does not prove schema correctness, semantic truth, or receipt honesty.\n```\n""", encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',default='.'); ap.add_argument('--out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_REPORT_V0_1.json'); ap.add_argument('--md-out',default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_REPORT_V0_1.md'); a=ap.parse_args()
    repo=Path(a.repo_root).resolve(); r=scan(repo); out=repo/a.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); write_md(repo/a.md_out,r); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r['canonical_parse_debt_count']==0 else 1
if __name__=='__main__': raise SystemExit(main())
