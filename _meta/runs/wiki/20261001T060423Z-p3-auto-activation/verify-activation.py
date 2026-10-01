
import sys,json,re,hashlib,importlib
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from collections import Counter
r=Path.cwd(); op=Path('_meta/runs/wiki/20261001T060423Z-p3-auto-activation')
sys.path.insert(0,str(r/op/'runtime'))
daily=importlib.import_module('daily'); C=importlib.import_module('p3_common')
from cron.jobs import get_job
P=C.helper('publish'); fs=P.Files(r)
baseline=C.decode(fs.read(str(op/'baseline.json')))
P.check_snapshots(fs,baseline['protected_hashes'])
assert all(fs.read(p)==(op/'policy-staged'/p).read_bytes() for p in baseline['policy_before_hashes'])
a_ref=str(op/'scheduled/execution-approval.json'); a=C.decode(fs.read(a_ref))
P.check_snapshots(fs,a['snapshots']); daily.runtime_manifest(fs,a,False); daily.scope_approval(fs,a)
scope=C.decode(fs.read(a['scope_approval_ref'])); assert C.sha(fs.read(scope['source_approval_ref']))==scope['source_approval_sha256']
s=C.decode(fs.read(C.STATE)); schema=C.decode(fs.read(C.DOCS[-1])); auto=C.decode(fs.read('_meta/automation.json'))
for name,data in [('automation',auto),('compilation',s),('feedback',C.decode(fs.read('_meta/state/feedback.json'))),('research_review',C.decode(fs.read('_meta/state/research-review.json')))]: P.schema_validate(schema,data,name)
assert s['enabled'] is True and s['safety_block'] is False
assert all(t['status']=='committed' for t in s['transactions'])
P.reject_other_unresolved(fs,''); daily.reject_dangling_reservations({'fs':fs},s['items'])
assert not any((r/'_meta/locks'/n).exists() for n in ('daily-run.lock','collection.lock'))
metadata=[C.decode(fs.read(str(p))) for p in Path('raw/articles/4cff5b4f10ec').glob('arxiv-*/source.json')]
source_ids={m['version_id'] for m in metadata}; state_ids={i['version_id'] for i in s['items']}
assert len(source_ids)==len(metadata)==len(s['items']) and source_ids==state_ids
published=[i for i in s['items'] if i['status'] in C.PUBLISHED_STATUSES]; refs={}
for item in published:
 keep=a['preserved_publications'][item['version_id']]
 assert keep==dict(work_key=item['work_key'],receipt_sha256=C.sha(fs.read(item['receipt_ref'])),output_refs=item['output_refs'])
 for ref in item['output_refs']: assert C.sha(fs.read(ref['path']))==ref['sha256']; refs[ref['path']]=ref['sha256']
index=fs.read('index.md').decode(); assert all(index.count('[['+p[:-3]+']]')==1 for p in refs)
page_count=re.search(r'Total pages: (\d+)',index)
assert page_count is not None and int(page_count.group(1))==len(refs)
actual_pages={str(p) for base in ('entities','concepts','comparisons','queries') for p in Path(base).rglob('*.md')}
assert actual_pages==set(refs)
log=fs.read('log.md'); assert C.sha(log[:baseline['log_prefix_bytes']])==baseline['log_prefix_sha256']
retry=C.decode(fs.read(str(op/'retry-approval.json')))
for i in retry['items']:P.check_snapshots(fs,i['prior_evidence_sha256'])
j=get_job('4839be6a1db1'); registration=C.decode(fs.read(str(op/'registration-active.json')))
assert isinstance(j,dict)
expected=dict(id='4839be6a1db1',enabled=True,model=C.MODEL['model'],provider=C.MODEL['provider'],reasoning_effort=C.MODEL['reasoning_effort'],workdir=str(r),skills=['llm-wiki'],deliver='local',failure_deliver='local',no_agent=False,attach_to_session=False,monitor_script=None,monitor_url=None,prompt=fs.read(C.PROMPT).decode().strip())
for record in (j,registration['job']):
 assert isinstance(record,dict)
 assert all(record.get(k)==v for k,v in expected.items())
 assert record['schedule']['kind']=='cron' and record['schedule']['expr']=='0 17 * * *'
 assert not any(record.get(k) for k in ('script','monitor','context_from','continuity','base_url'))
next_kst=datetime.fromisoformat(j['next_run_at']).astimezone(ZoneInfo('Asia/Seoul')); assert next_kst.strftime('%H:%M')=='02:00'
before=C.decode(fs.read(str(op/'cron-before.json')))
keys=('id','name','prompt','skills','skill','model','provider','base_url','script','no_agent','context_from','schedule','repeat','enabled','state','deliver','failure_deliver','origin','enabled_toolsets','workdir','attach_to_session','reasoning_effort','monitor_script','monitor_url','continuity')
unchanged=[]; runtime_counter_changes=[]
for ident,b in before.items():
 if ident==j['id']:continue
 live=get_job(ident); assert isinstance(live,dict)
 assert all(live.get(k)==b.get(k) for k in keys if k!='repeat'),ident
 assert {k:v for k,v in live['repeat'].items() if k!='completed'}=={k:v for k,v in b['repeat'].items() if k!='completed'},ident
 if live['repeat']['completed']!=b['repeat']['completed']:runtime_counter_changes.append(dict(id=ident,field='repeat.completed',before=b['repeat']['completed'],after=live['repeat']['completed']))
 unchanged.append(ident)
checks={'source_body_reads':0,'network_attempts':0}
def audit(event,args):
 if event in ('socket.connect','socket.bind','socket.getaddrinfo'):
  checks['network_attempts']+=1; raise AssertionError('probe network forbidden')
 if event=='open' and isinstance(args[0],(str,bytes)):
  p=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).absolute()
  if p.is_relative_to(r/'raw') and p.name in ('source.html','source.pdf'):
   checks['source_body_reads']+=1; raise AssertionError('probe source body forbidden')
sys.addaudithook(audit)
probe='_meta/runs/wiki/20261001T065900Z-p3-outside-window-probe'
try:daily.preflight(run=probe,approval_ref=a_ref)
except ValueError as e:assert str(e)=='edit_freeze_window'; refused=str(e)
else:raise AssertionError('outside-window preflight unexpectedly passed')
assert not (r/probe).exists()
print(json.dumps(dict(schema='pkm-p3-activation-verification/v1',observed_at=datetime.now(timezone.utc).isoformat(),status='activation_verified_first_fire_pending',enabled=True,next_run_kst=next_kst.isoformat(),compiler_id=j['id'],first_fire_observed=False,protected_hashes_verified=len(baseline['protected_hashes']),policy_files_match_staged=True,approved_runtime_and_scope_bound=True,unrelated_job_config_unchanged=unchanged,unrelated_job_runtime_counter_changes=runtime_counter_changes,source_count=len(source_ids),source_formats=dict(Counter('pdf' if 'pdf_file' in m else 'html' for m in metadata)),state_counts=dict(Counter(i['status'] for i in s['items'])),knowledge_pages=len(refs),eligible_count=sum(i['status'] in ('blocked_approval','queued','partial','retryable_failed') and i['human_review'] is None and i['failure_count']<3 for i in s['items']),next_selected=[i['version_id'] for i in daily.select(s['items'],5)],versions=[dict(version_id=i['version_id'],format=i['format'],status=i['status']) for i in sorted(s['items'],key=lambda x:x['version_id'])],retry_failures_preserved=True,outside_window_probe=dict(refused=refused,run_created=False,**checks),full_wiki_lint_scheduled=False,unit_integration_test_receipt=str(op/'runtime/parent-evidence/parent-final-full-02/counts.json')),ensure_ascii=False))
