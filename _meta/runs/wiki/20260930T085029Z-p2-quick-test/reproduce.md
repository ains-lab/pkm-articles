# P2 격리 테스트 재현

실제 기존 verify-one.py/publish-one.py를 임시 폴더에서 합성 입력으로 실행한다. 원문은 해시·길이 검증만 하며 모델 호출·운영 게시는 없다. 아래 코드는 수집기/파서가 아니라 이번 시험의 재현 기록이다. 첫 실행의 PDF 파일명 정렬 오탐은 initial-test-report.json에 보존했다.

실행 환경: `/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B`, 작업 위치 `/home/ainsdev/wiki/pkm-articles`.

```python

import json, hashlib, re, sys, subprocess, tempfile, os, collections, time
from pathlib import Path
from datetime import datetime, timezone
from jsonschema import Draft202012Validator, FormatChecker
root=Path('/home/ainsdev/wiki/pkm-articles')
start=time.monotonic()
report={'schema':'pkm-p2-quick-test/v1','started_at':datetime.now(timezone.utc).isoformat(),'model_calls':0,'paper_text_sent':False,'fixtures_are_synthetic':True,'checks':[],'blockers':[]}
def check(name,ok,details=None):
    report['checks'].append({'name':name,'passed':bool(ok),'details':details})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
protected=list((root/'raw').rglob('source.*'))+[root/p for p in ['AGENTS.md','SCHEMA.md','index.md','log.md','_meta/topics.json','_meta/state/4cff5b4f10ec.json','_meta/state/compilation.json','_meta/automation.json','_meta/automation-contracts.schema.json']]
before={str(p.relative_to(root)):sha(p) for p in protected}
report['protected_hashes_before']=before
schema=json.loads((root/'_meta/automation-contracts.schema.json').read_text())
Draft202012Validator.check_schema(schema)
v=Draft202012Validator(schema,format_checker=FormatChecker())
for name in ['_meta/automation.json','_meta/state/compilation.json','_meta/state/feedback.json','_meta/state/research-review.json']:
    errs=list(v.iter_errors(json.loads((root/name).read_text())))
    check('schema:'+name,not errs,[str(e.message)[:200] for e in errs])
auto=json.loads((root/'_meta/automation.json').read_text())
state=json.loads((root/'_meta/state/compilation.json').read_text())
report['ledger_status_counts']=dict(collections.Counter(i['status'] for i in state['items']))
report['pilot_items']=[{k:i[k] for k in ['version_id','status','reason','failure_count']} for i in state['items'] if i['version_id'] in auto['pilot_candidates']]
check('P2_manual_authorization_flag',auto['phase_authorizations']['P2'])
check('automatic_execution_disabled',auto['enabled'] is False and all(j['enabled'] is False and j['cron_id'] is None for j in auto['jobs'].values()))
versions=[]; inventory=[]
for mpath in sorted((root/'raw/articles/4cff5b4f10ec').glob('arxiv-*/source.json')):
    m=json.loads(mpath.read_text()); fmt='html' if 'html_sha256' in m else 'pdf'; p=mpath.parent/('source.'+fmt)
    ok=(not p.is_symlink() and not mpath.is_symlink() and sha(p)==m[fmt+'_sha256'] and p.stat().st_size==m[fmt+'_bytes'] and mpath.parent.name=='arxiv-'+m['version_id'] and sorted(q.name for q in mpath.parent.iterdir())==sorted(['source.'+fmt,'source.json']))
    inventory.append({'version_id':m['version_id'],'format':fmt,'passed':ok}); versions.append(m['version_id'])
check('all_source_packages_integrity',all(i['passed'] for i in inventory) and len(versions)==len(set(versions)),inventory)
report['source_counts']=dict(collections.Counter(i['format'] for i in inventory))
report['source_total']=len(inventory)
for item in state['items']:
    check('ledger_source:'+item['version_id'],sha(root/item['source_path'])==item['source_sha256'] and (root/item['source_path']).stat().st_size==item['source_bytes'] and sha(root/item['metadata_path'])==item['metadata_sha256'])
pages=[p for d in ['entities','concepts','comparisons','queries'] for p in (root/d).glob('*.md')]
report['knowledge_pages']=len(pages)
check('index_page_count',int(re.search(r'Total pages: (\d+)',(root/'index.md').read_text()).group(1))==len(pages))
report['unledgered_sources']=sorted(set(versions)-{i['version_id'] for i in state['items']})
agents=(root/'AGENTS.md').read_text(); sc=(root/'SCHEMA.md').read_text()
check('policy_revision_consistency',auto['policy_revision'] in agents and auto['policy_revision'] in sc,{'automation':auto['policy_revision'],'agents_has_v1':'pkm-html-knowledge/v1' in agents,'schema_has_v1':'pkm-html-knowledge/v1' in sc})
report['blockers'].append('AGENTS.md and SCHEMA.md retain v1 approval/budget rules while automation configuration is v2 no_cost_cap; accounting/hard_stop unverified')
for job in ['daily_compile','research_review']:
    configured=auto['jobs'][job]['prompt_revision']; actual=(root/auto['jobs'][job]['prompt_path']).read_text().splitlines()[0]
    check('prompt_revision:'+job,configured in actual,{'configured':configured,'actual_heading':actual})
report['blockers'].append('Configured/schema prompt revisions remain v1 while actual prompt headings are v2')
prior=root/'_meta/runs/wiki/20260930T082000Z-p2-nonstream/2609.31358v1'
report['prior_nonstream_artifacts']=sorted(p.name for p in prior.iterdir())
report['prior_nonstream_outcome']='unknown: attempt start exists, no result; server cancellation and failure cause not observed'
runrel=Path('_meta/runs/wiki/20260929T083140Z-p2-resume')
vid='2609.31358v1'
# Isolated synthetic input, never promoted to real raw or knowledge paths.
fixture_source='<html><body>'+''.join(f'<p id="C{i:02}">SYNTHETIC evidence {i:02}.</p>' for i in range(1,9))+'</body></html>'
fixture_doc={'title':'SYNTHETIC TEST ONLY','version_id':vid,'main_text_complete':False,'read_scope':['C01'],'unread_scope':['그림 미검토','수식 미검토','부록 미검토'],'claims':[{'id':f'C{i:02}','kind':'author_report','anchor':f'C{i:02}','quote':f'SYNTHETIC evidence {i:02}.'} for i in range(1,9)],'markdown_body':'\n'.join(['C01 SYNTHETIC TEST ONLY']+['SYNTHETIC filler for structural test']*89)}
fixture_result={'completed':True,'error':None,'response_status':'incomplete','response_model':'gpt-6-astra','cost_usd':None,'cost_status':'unobserved_not_zero','source_sha256':hashlib.sha256(fixture_source.encode()).hexdigest(),'text':json.dumps(fixture_doc,ensure_ascii=False)}
def put(r,p,value):
    q=r/p; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(json.dumps(value,ensure_ascii=False) if not isinstance(value,str) else value)
script=root/runrel/'verify-one.py'; publisher=root/runrel/'publish-one.py'
report['scripts_tested']={str(p.relative_to(root)):sha(p) for p in [script,publisher]}
with tempfile.TemporaryDirectory(prefix='p2-isolated-') as td:
    r=Path(td)
    put(r,Path(f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html'),fixture_source)
    put(r,runrel/vid/'attempt-result.json',fixture_result)
    proc=subprocess.run([sys.executable,'-B',str(script),vid],cwd=r,capture_output=True,text=True,timeout=15)
    vr=json.loads((r/runrel/vid/'verify-report.json').read_text())
    check('reject_incomplete_response_and_partial_paper',not vr['passed'],{'exit_code':proc.returncode,'validator_passed':vr['passed'],'synthetic_response_status':'incomplete','synthetic_main_text_complete':False})
    put(r,Path(f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.json'),{'title':'SYNTHETIC TEST ONLY','abstract':'SYNTHETIC TEST ONLY.'})
    put(r,Path('_meta/automation.json'),auto)
    put(r,Path('_meta/state/compilation.json'),state)
    put(r,Path('index.md'),(root/'index.md').read_text())
    put(r,Path('log.md'),'# SYNTHETIC TEST LOG ONLY\n')
    (r/'entities').mkdir()
    # Simulate collector's directory lock. Busy must be a controlled skip.
    lock=r/'_meta/locks/collection.lock'; lock.mkdir(parents=True)
    p=subprocess.run([sys.executable,'-B',str(publisher),vid],cwd=r,capture_output=True,text=True,timeout=15)
    check('publisher_handles_collector_directory_lock', 'skipped_busy' in (p.stdout+p.stderr),{'exit_code':p.returncode,'error':p.stderr.splitlines()[-1:]})
    lock.rmdir() # Only our empty synthetic fixture lock, never a real lock.
    p=subprocess.run([sys.executable,'-B',str(publisher),vid],cwd=r,capture_output=True,text=True,timeout=15)
    newstate=json.loads((r/'_meta/state/compilation.json').read_text())
    item=next(i for i in newstate['items'] if i['version_id']==vid)
    idx=(r/'index.md').read_text(); errs=list(v.iter_errors(newstate))
    check('publisher_completes_consistent_publication',p.returncode==0 and f'[[entities/arxiv-{vid}]]' in idx and not errs,{'exit_code':p.returncode,'error':p.stderr.splitlines()[-1:],'page_exists':(r/f'entities/arxiv-{vid}.md').exists(),'index_entry_present':f'[[entities/arxiv-{vid}]]' in idx,'item_status':item['status'],'receipt_exists':(r/runrel/vid/'publish-record.json').exists(),'lock_left_as_file':lock.is_file()})
    check('publisher_state_satisfies_contract',not errs,{'errors':[e.message[:250] for e in errs]})
    for target in ['status','work_key','output_refs']:
        props=schema['$defs']['compilation']['properties']['items']['items']['properties'] if 'compilation' in schema['$defs'] else None
        if props:
            validator=Draft202012Validator({'$schema':schema['$schema'],'$defs':schema['$defs'],**props[target]})
            ee=list(validator.iter_errors(item[target])); report.setdefault('publisher_field_errors',{})[target]=[e.message for e in ee]
report['blockers']+=['Existing verifier accepts synthetic incomplete/partial response','Existing publisher is incompatible with directory lock and produces invalid partial publication in isolated fixture']
check('protected_files_unchanged',before=={str(p.relative_to(root)):sha(p) for p in protected})
report['ended_at']=datetime.now(timezone.utc).isoformat(); report['elapsed_seconds']=round(time.monotonic()-start,3)
report['result']='blocked_policy_and_publisher_regressions'
report['summary']={'checks':len(report['checks']),'passed':sum(c['passed'] for c in report['checks']),'failed':sum(not c['passed'] for c in report['checks'])}
print(json.dumps(report,ensure_ascii=False))

```
