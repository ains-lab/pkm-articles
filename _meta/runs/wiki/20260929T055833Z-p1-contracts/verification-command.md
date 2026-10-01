# P1 readonly verification command

Observed contract/inventory checks only; synthetic request fixtures are not real execution evidence. Run from the Wiki root.

```bash
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -c 'from pathlib import Path
import json, hashlib, os, re, copy, subprocess
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from jsonschema import Draft202012Validator, FormatChecker
r=Path.cwd(); run=r/'"'"'_meta/runs/wiki/20260929T055833Z-p1-contracts'"'"'
b=json.loads((run/'"'"'preflight.json'"'"').read_text())
sha=lambda data: hashlib.sha256(data).hexdigest()
schema=json.loads((r/'"'"'_meta/automation-contracts.schema.json'"'"').read_text())
Draft202012Validator.check_schema(schema)
v=Draft202012Validator(schema,format_checker=FormatChecker())
paths=['"'"'_meta/automation.json'"'"','"'"'_meta/state/compilation.json'"'"','"'"'_meta/state/feedback.json'"'"','"'"'_meta/state/research-review.json'"'"']
a,c,f,w=[json.loads((r/p).read_text()) for p in paths]
for x in [a,c,f,w]: v.validate(x)
fixture={'"'"'schema'"'"':'"'"'pkm-compile-request/v1'"'"','"'"'policy_revision'"'"':'"'"'pkm-html-knowledge/v1'"'"','"'"'contract_revision'"'"':'"'"'pkm-contracts/v1'"'"','"'"'provider'"'"':'"'"'codex-lb'"'"','"'"'model'"'"':'"'"'gpt-6-astra'"'"','"'"'reasoning_effort'"'"':'"'"'xhigh'"'"','"'"'source_format'"'"':'"'"'html'"'"','"'"'source_path'"'"':'"'"'fixtures/not-a-real-paper/source.html'"'"','"'"'source_sha256'"'"':'"'"'0'"'"'*64,'"'"'source_approval_id'"'"':'"'"'p1-proposed-values-2026-09-29'"'"','"'"'phase_execution_approved'"'"':True,'"'"'phase_approval_ref'"'"':'"'"'fixtures/not-a-real-approval.json'"'"','"'"'images'"'"':False,'"'"'external_assets'"'"':False,'"'"'pdf_analysis'"'"':False,'"'"'accounting_verified'"'"':True,'"'"'hard_stop_verified'"'"':True,'"'"'budget_receipt'"'"':'"'"'fixtures/not-a-real-budget.json'"'"'}
v.validate(fixture)
cases=[]
for key,value in [('"'"'provider'"'"','"'"'unapproved-provider'"'"'),('"'"'model'"'"','"'"'unapproved-model'"'"'),('"'"'reasoning_effort'"'"','"'"'low'"'"'),('"'"'source_format'"'"','"'"'pdf'"'"'),('"'"'images'"'"',True),('"'"'external_assets'"'"',True),('"'"'pdf_analysis'"'"',True),('"'"'phase_execution_approved'"'"',False),('"'"'accounting_verified'"'"',False),('"'"'hard_stop_verified'"'"',False),('"'"'source_approval_id'"'"','"'"'unknown'"'"'),('"'"'policy_revision'"'"','"'"'unknown/v99'"'"'),('"'"'contract_revision'"'"','"'"'unknown/v99'"'"'),('"'"'source_path'"'"','"'"'../outside.html'"'"'),('"'"'source_sha256'"'"','"'"'not-a-hash'"'"')]:
 x=copy.deepcopy(fixture); x[key]=value
 assert not v.is_valid(x),key
 cases.append({'"'"'case'"'"':'"'"'request:'"'"'+key,'"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
x=copy.deepcopy(fixture); del x['"'"'phase_approval_ref'"'"']; assert not v.is_valid(x)
cases.append({'"'"'case'"'"':'"'"'missing_approval_ref'"'"','"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
for path in paths:
 x=json.loads((r/path).read_text()); x['"'"'schema'"'"']='"'"'unknown/v99'"'"'; assert not v.is_valid(x)
 cases.append({'"'"'case'"'"':'"'"'unknown_schema:'"'"'+path,'"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
x=copy.deepcopy(a); x['"'"'enabled'"'"']=True; assert not v.is_valid(x)
cases.append({'"'"'case'"'"':'"'"'activation_without_approvals_and_budget_proof'"'"','"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
x=copy.deepcopy(c); pdf=next(i for i in x['"'"'items'"'"'] if i['"'"'format'"'"']=='"'"'pdf'"'"'); pdf['"'"'status'"'"']='"'"'queued'"'"'; assert not v.is_valid(x)
cases.append({'"'"'case'"'"':'"'"'pdf_policy_bypass'"'"','"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
x=copy.deepcopy(c); html=next(i for i in x['"'"'items'"'"'] if i['"'"'format'"'"']=='"'"'html'"'"'); html['"'"'status'"'"']='"'"'published_draft'"'"'; assert not v.is_valid(x)
cases.append({'"'"'case'"'"':'"'"'publication_without_read_scope_output_receipt'"'"','"'"'expected'"'"':'"'"'reject'"'"','"'"'observed'"'"':'"'"'reject'"'"'})
changed=[p for p,h in b['"'"'protected_files'"'"'].items() if not (r/p).is_file() or sha((r/p).read_bytes())!=h]
assert not changed,changed
ids={i['"'"'version_id'"'"'] for i in b['"'"'inventory'"'"']}; assert len(ids)==len(c['"'"'items'"'"'])==10
assert {i['"'"'version_id'"'"'] for i in c['"'"'items'"'"']}==ids
for i in c['"'"'items'"'"']:
 p=r/i['"'"'source_path'"'"']; meta=json.loads((r/i['"'"'metadata_path'"'"']).read_text()); data=p.read_bytes()
 assert sha(data)==i['"'"'source_sha256'"'"']==meta[i['"'"'format'"'"']+'"'"'_sha256'"'"']
 assert len(data)==i['"'"'source_bytes'"'"']==meta[i['"'"'format'"'"']+'"'"'_bytes'"'"']
 assert sha((r/i['"'"'metadata_path'"'"']).read_bytes())==i['"'"'metadata_sha256'"'"']
 assert i['"'"'version_id'"'"']==meta['"'"'version_id'"'"'] and p.parent.name=='"'"'arxiv-'"'"'+i['"'"'version_id'"'"']
 assert set(x.name for x in p.parent.iterdir())=={'"'"'source.'"'"'+i['"'"'format'"'"'],'"'"'source.json'"'"'}
 assert not i['"'"'read_scope'"'"'] and not i['"'"'output_refs'"'"'] and i['"'"'receipt_ref'"'"'] is None
 assert i['"'"'status'"'"']==('"'"'blocked_policy'"'"' if i['"'"'format'"'"']=='"'"'pdf'"'"' else '"'"'blocked_approval'"'"')
rawidx=(r/'"'"'raw/articles/4cff5b4f10ec/index.md'"'"').read_text(); rows=re.findall(r'"'"'^\| (\d{4}\.\d{4,5}v\d+) \|'"'"',rawidx,re.M)
assert len(rows)==len(set(rows))==10 and set(rows)==ids
state=json.loads((r/'"'"'_meta/state/4cff5b4f10ec.json'"'"').read_text()); assert state['"'"'pending'"'"']==[]
assert {x['"'"'version_id'"'"'] for x in state['"'"'html_unavailable'"'"']}=={i['"'"'version_id'"'"'] for i in c['"'"'items'"'"'] if i['"'"'format'"'"']=='"'"'pdf'"'"'}
assert all(x['"'"'local_fulltext_preserved'"'"'] and x['"'"'pdf_fallback_status'"'"']=='"'"'captured'"'"' for x in state['"'"'html_unavailable'"'"'])
home=Path(os.environ.get('"'"'HERMES_HOME'"'"',str(Path.home()/'"'"'.hermes'"'"')))
j=json.loads((home/'"'"'cron/jobs.json'"'"').read_text()); jobs=j if isinstance(j,list) else j['"'"'jobs'"'"']; collector=next(x for x in jobs if x['"'"'id'"'"']=='"'"'4cff5b4f10ec'"'"')
assert sha(json.dumps(collector,sort_keys=True,separators=('"'"','"'"','"'"':'"'"')).encode())==b['"'"'collector_record_sha256'"'"']
assert sorted(x['"'"'id'"'"'] for x in jobs)==b['"'"'job_ids'"'"']
assert not a['"'"'enabled'"'"'] and not a['"'"'registration_authorized'"'"'] and not a['"'"'activation_authorized'"'"']
assert a['"'"'phase_authorizations'"'"']=={'"'"'P1'"'"':True,'"'"'P2'"'"':False,'"'"'P3'"'"':False,'"'"'P4'"'"':False,'"'"'P5'"'"':False,'"'"'P6'"'"':False}
assert all(x['"'"'cron_id'"'"'] is None and x['"'"'enabled'"'"'] is False and x['"'"'registration_status'"'"']=='"'"'not_registered'"'"' for x in a['"'"'jobs'"'"'].values())
assert not any(x['"'"'enabled'"'"'] for x in [c,f,w]); assert w['"'"'anchor_utc'"'"'] is None
assert not f['"'"'events'"'"'] and not w['"'"'ideas'"'"'] and not w['"'"'windows'"'"'] and not c['"'"'receipts'"'"'] and not c['"'"'transactions'"'"']
assert c['"'"'cost_events'"'"']==w['"'"'cost_events'"'"']==[]
assert a['"'"'model'"'"']=={'"'"'provider'"'"':'"'"'codex-lb'"'"','"'"'model'"'"':'"'"'gpt-6-astra'"'"','"'"'reasoning_effort'"'"':'"'"'xhigh'"'"','"'"'fallback_allowed'"'"':False}
assert a['"'"'budget'"'"']['"'"'pilot_total'"'"']==5 and a['"'"'budget'"'"']['"'"'daily_compile_per_run'"'"']==5 and a['"'"'budget'"'"']['"'"'daily_compile_per_kst_day'"'"']==10 and a['"'"'budget'"'"']['"'"'research_review_per_run'"'"']==5
assert not a['"'"'budget'"'"']['"'"'accounting_verified'"'"'] and not a['"'"'budget'"'"']['"'"'hard_stop_verified'"'"']
for job in a['"'"'jobs'"'"'].values():
 text=(r/job['"'"'prompt_path'"'"']).read_text()
 for expected in [job['"'"'prompt_revision'"'"'],a['"'"'policy_revision'"'"'],a['"'"'contract_revision'"'"'],'"'"'codex-lb'"'"','"'"'gpt-6-astra'"'"','"'"'xhigh'"'"','"'"'collection.lock'"'"']:
  assert expected in text,(job['"'"'prompt_path'"'"'],expected)
knowledge=[p for d in ['"'"'entities'"'"','"'"'concepts'"'"','"'"'comparisons'"'"','"'"'queries'"'"'] for p in (r/d).rglob('"'"'*.md'"'"')]
assert len(knowledge)==0
idx=(r/'"'"'index.md'"'"').read_text(); assert re.search(r'"'"'Total pages:\s*0\b'"'"',idx)
old=(run/'"'"'before/log.md'"'"').read_bytes(); assert (r/'"'"'log.md'"'"').read_bytes().startswith(old)
# P1 adds only an explanatory suffix to the collector contract.
assert (r/'"'"'_meta/COLLECTION.md'"'"').read_text().startswith((run/'"'"'before/_meta/COLLECTION.md'"'"').read_text())
mdpaths=[p for p in b['"'"'new_paths'"'"']+list(b['"'"'edit_before'"'"']) if p.endswith('"'"'.md'"'"') and p!='"'"'log.md'"'"']
links=[]
for rel in mdpaths:
 text=(r/rel).read_text()
 for target in re.findall(r'"'"'(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)'"'"',text):
  if re.match(r'"'"'^[a-z]+://'"'"',target) or target.startswith('"'"'#'"'"'): continue
  dest=((r/rel).parent/target.split('"'"'#'"'"')[0]).resolve()
  assert dest.is_relative_to(r) and dest.exists(),(rel,target)
  links.append((rel,target))
assert not (r/'"'"'_meta/locks/collection.lock'"'"').exists()
result=subprocess.run(['"'"'git'"'"','"'"'diff'"'"','"'"'--check'"'"'],capture_output=True,text=True); assert result.returncode==0,result.stdout+result.stderr
local=datetime(2026,10,1,2,tzinfo=ZoneInfo('"'"'Asia/Seoul'"'"')).astimezone(timezone.utc); assert local.hour==17
print(json.dumps({'"'"'schema'"'"':'"'"'pkm-p1-verification/v1'"'"','"'"'recorded_at'"'"':datetime.now(timezone.utc).isoformat(),'"'"'contract_instances_valid'"'"':len(paths),'"'"'synthetic_positive_control'"'"':'"'"'shape_only_not_real_approval_or_execution'"'"','"'"'rejection_cases'"'"':cases,'"'"'rejections_passed'"'"':len(cases),'"'"'protected_files_unchanged'"'"':len(b['"'"'protected_files'"'"']),'"'"'original_and_metadata_files_unchanged'"'"':len(c['"'"'items'"'"'])*2,'"'"'versions'"'"':len(ids),'"'"'html'"'"':sum(i['"'"'format'"'"']=='"'"'html'"'"' for i in c['"'"'items'"'"']),'"'"'pdf'"'"':sum(i['"'"'format'"'"']=='"'"'pdf'"'"' for i in c['"'"'items'"'"']),'"'"'knowledge_pages'"'"':len(knowledge),'"'"'collector_record_unchanged'"'"':True,'"'"'job_id_set_unchanged'"'"':True,'"'"'new_jobs_registered'"'"':0,'"'"'log_prefix_preserved'"'"':True,'"'"'local_links_checked'"'"':len(links),'"'"'collection_behavior_text_preserved'"'"':True,'"'"'git_diff_check'"'"':'"'"'pass'"'"','"'"'lock_released'"'"':True,'"'"'runtime_model_budget_publication_recovery'"'"':'"'"'not_tested_P2_or_later'"'"'},ensure_ascii=False))
'
```
