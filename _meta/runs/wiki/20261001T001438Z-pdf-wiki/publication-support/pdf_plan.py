"""Read-only v3 plan builder. No CLI, model, PDF parser, or automatic publisher."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import stat
import types

ROOT = Path('/home/ainsdev/wiki/pkm-articles')
RUN = '_meta/runs/wiki/20261001T001438Z-pdf-wiki'
VERSIONS = ('2609.30614v1', '2609.30824v1')
POLICY, CONTRACT, PROMPT = 'pkm-html-pdf-text-knowledge/v3', 'pkm-contracts/v3', 'wiki-compile/v3'
SCOPE = 'manual PDF embedded-text complete'
STATE = '_meta/state/compilation.json'
DOCS = ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/COMPILATION.md',
        '_meta/STATE-CONTRACTS.md', '_meta/automation-contracts.schema.json')
MODEL = dict(provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh')
ROUTE = dict(base_url='http://10.10.1.244:2455/v1', api_mode='codex_responses')

def require(ok, message):
    if not ok:
        raise ValueError(message)

# Safe code-only import; no legacy entrypoint, changed constant, or pycache.
_helper = ROOT / '_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py'
require(all(not p.is_symlink() for p in (_helper, *_helper.parents)), 'helper symlink')
with os.fdopen(os.open(_helper, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as _stream:
    _st = os.fstat(_stream.fileno())
    require(stat.S_ISREG(_st.st_mode) and _st.st_nlink == 1, 'unsafe helper')
    generic = types.ModuleType('_pdf_transaction_helpers')
    generic.__file__ = str(_helper)
    exec(compile(_stream.read(), str(_helper), 'exec'), generic.__dict__)
Files, collection_lock = generic.Files, generic.collection_lock
index_parts, page_count, schema_validate = generic.index_parts, generic.page_count, generic.schema_validate
write_journal, classify, check_snapshots = generic.write_journal, generic.classify, generic.check_snapshots
apply_plan, verify_committed = generic.apply_plan, generic.verify_committed
sha, canonical, encoded, decode = generic.sha, generic.canonical, generic.encoded, generic.decode

def _bound(fs, vid, run, result, report, review, now):
    require(fs.root == ROOT and run == RUN and vid in VERSIONS, 'root/run/version scope')
    require(now.tzinfo is not None, 'timezone required')
    r = result['value']
    require(r.get('attempt') in ('attempt1','attempt2'), 'attempt scope')
    require(result['path'] == f'{run}/runtime/{vid}/{r["attempt"]}-result.json' and
        report['path'] == f'{run}/reviews/{vid}-{r["attempt"]}-verification.json' and
        review['path'] == f'{run}/reviews/{vid}-{r["attempt"]}-agent-review.json', 'artifact paths')
    for descriptor in (result, report, review):
        raw = fs.read(descriptor['path'])
        require(sha(raw) == descriptor['sha256'] and decode(raw) == descriptor['value'], 'artifact hash/value mismatch')
    r, m, v = result['value'], report['value'], review['value']
    require(m.get('schema') == 'pkm-pdf-text-verification/v1' and m.get('version_id') == vid and
        m.get('passed') is True and m.get('checks') and all(c.get('ok') is True for c in m['checks']) and
        m.get('semantic_review') == m.get('publication') == 'not_performed', 'mechanical report failed')
    doc = decode(r['text'])
    require(canonical(doc) == canonical(m['document']) and doc['version_id'] == vid and
        doc['main_text_complete'] is True and all(isinstance(doc[k], str) and doc[k].strip() for k in
        ('title','summary','markdown_body')) and doc['read_scope'] and doc['unread_scope'] and doc['claims'], 'document binding/scope')
    require(v.get('schema') == 'pkm-pdf-agent-evidence-review/v1' and v.get('actor') == 'agent' and
        v.get('passed') is True and v['human_review_ref'] is None and isinstance(v.get('reviewer'),str) and
        v['reviewer'].strip(), 'agent-only passed review required')
    reviewed = datetime.fromisoformat(v['reviewed_at'])
    require(reviewed.tzinfo is not None and reviewed <= now, 'review timestamp')
    expected = dict(version_id=vid, result_sha256=result['sha256'], mechanical_report_sha256=report['sha256'],
        source_sha256=r['source_sha256'], approval_sha256=r['approval_sha256'], policy_sha256=r['policy_sha256'],
        prompt_sha256=r['prompt_sha256'], requested_scope=SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope'])
    require(set(v) == set(expected) | {'schema','actor','reviewer','reviewed_at','passed','human_review_ref',
        'evidence_scope','reviewed_claim_ids','claims'}, 'unknown/missing review fields')
    require(all(v.get(k) == val for k,val in expected.items()), 'review binding mismatch')
    claims = doc['claims']
    ids = [c['id'] for c in claims]
    require(len(set(ids)) == len(ids) and v['reviewed_claim_ids'] == ids and
        set(v['evidence_scope']) == {c['anchor'] for c in claims} and len(v['claims']) == len(claims), 'all-claims review required')
    for claim, checked in zip(claims, v['claims']):
        require(set(checked) == {'id','anchor','quote_sha256','verdict','rationale'} and
            checked['id'] == claim['id'] and checked['anchor'] == claim['anchor'] and
            checked['quote_sha256'] == sha(claim['quote'].encode()) and checked['verdict'] == 'supported' and
            isinstance(checked['rationale'],str) and checked['rationale'].strip(), 'unsupported/unreviewed claim')
    snapshots = dict(report['preflight']['snapshots'])
    a = decode(fs.read(run+'/execution-approval.json'))
    pins = dict(**MODEL, policy_revision=POLICY, contract_revision=CONTRACT, prompt_revision=PROMPT, approved_route=ROUTE)
    require(all(r.get(k) == val == a.get(k) for k,val in pins.items()) and r.get('response_model') == MODEL['model'] and
        r.get('schema') == 'pkm-pdf-text-attempt-result/v1' and r.get('completed') is True and
        r.get('response_status') == 'completed' and all(r.get(k) is None for k in ('error','response_error','incomplete_details')), 'result/model pin')
    require(a.get('schema') == 'pkm-pdf-text-run-approval/v1' and a.get('approved') is True and
        a.get('wiki_root') == str(ROOT) and a.get('run_id') == Path(RUN).name and a.get('version_ids') == list(VERSIONS) and
        a.get('publication_edit_freeze_confirmed') is True and a.get('validated_publication_authorized') is True, 'publication authority')
    bindings = 'policy_sha256 prompt_sha256 document_sha256 instructions_path instructions_sha256 sources wiki_inputs scope_approval_sha256'.split()
    require(all(canonical(r[k]) == canonical(a[k]) for k in bindings) and set(r['document_sha256']) == set(DOCS) and
        r['instructions_path'] == run+'/runtime/instructions.md' and set(r['sources']) == set(VERSIONS), 'approval bindings')
    required = dict(r['document_sha256'], **{'_meta/automation.json':r['policy_sha256'],
        '_meta/prompts/wiki-compile.md':r['prompt_sha256'], r['instructions_path']:r['instructions_sha256'],
        run+'/scope-approval.json':r['scope_approval_sha256'], run+'/execution-approval.json':r['approval_sha256']})
    for version, source in r['sources'].items():
        require(source['source_path'] == f'raw/articles/4cff5b4f10ec/arxiv-{version}/source.pdf' and
            source['metadata_path'] == source['source_path'].replace('.pdf','.json'), 'source paths')
        required[source['metadata_path']] = source['metadata_sha256']
    required.update({x['path']:x['sha256'] for x in r['wiki_inputs']})
    require(set(snapshots) == set(required) | {STATE} and all(snapshots[k] == val for k,val in required.items()), 'preflight hashes')
    record = report['preflight']['record']
    require(set(bindings) | set(pins) | {'source_sha256','source_bytes','metadata_sha256','version_id','vid','run_id','approval_ref','approval_sha256'} <= set(record) and
        all(canonical(r[k]) == canonical(val) for k,val in record.items()) and r['version_id'] == r['vid'] == vid and
        r['run_id'] == Path(run).name and r['approval_ref'] == run+'/execution-approval.json' and
        all(r[k] == val for k,val in r['sources'][vid].items()), 'preflight record binding')
    observed = datetime.fromisoformat(report['observed_at'])
    require(report['observers'] == ['manual_pdf.preflight','manual_pdf.verify_result'] and observed.tzinfo is not None and
        observed <= now and datetime.fromisoformat(r['finished_at']) <= observed, 'parent observation')
    snapshots.pop(STATE)
    for descriptor in (result, report, review):
        snapshots[descriptor['path']] = descriptor['sha256']
    for source in result['value']['sources'].values():
        snapshots[source['source_path']] = source['source_sha256']
    check_snapshots(fs, snapshots)
    return dict(schema=decode(fs.read(DOCS[-1])), snapshots=snapshots)

def _assemble(vid, run, result, report, review, now, context, before_state, before_index, log, count) -> dict:
    r, doc = result['value'], report['value']['document']
    state = decode(before_state)
    schema_validate(context['schema'], state, 'compilation')
    require(state['enabled'] is False and state['safety_block'] is False and
        all(t['status'] == 'committed' for t in state['transactions']), 'state safety/unresolved transaction')
    require(len({i['version_id'] for i in state['items']}) == len(state['items']), 'duplicate state item')
    for version in VERSIONS:
        selected = [i for i in state['items'] if i['version_id'] == version]
        require(len(selected) == 1, 'state item missing')
        s = selected[0]
        require(s['source'] == 'arxiv' and s['format'] == 'pdf' and s['human_review'] is None and
            s['status'] in (('queued',) if version == vid else ('queued','published_draft')) and
            all(s[k] == val for k,val in r['sources'][version].items()), 'state item binding/transition')
    item = next(i for i in state['items'] if i['version_id'] == vid)
    require(not item['output_refs'] and item['receipt_ref'] is None and item['work_key'] is None, 'existing output state')
    require(len({e['event_id'] for e in state['cost_events']}) == len(state['cost_events']), 'duplicate cost event')
    work = dict(source='arxiv', version_id=vid, source_sha256=r['source_sha256'], policy_revision=POLICY,
                policy_sha256=r['policy_sha256'], prompt_revision=PROMPT, prompt_sha256=r['prompt_sha256'], requested_scope=SCOPE)
    key = sha(canonical(work))
    tx = 'pdf3-' + sha(canonical([run, {k:result[k] for k in ('path','sha256')}, key]))[:32]
    base = run+'/publications/'+vid+'-'+r['attempt']
    journal, receipt_path, structural = base+'-publish-journal.json', base+'-receipt.json', base+'-verification.json'
    output = f'entities/arxiv-{vid}.md'
    today = now.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    fm = dict(title=doc['title'], summary=doc['summary'], created=today, updated=today, last_reviewed=None,
        type='entity', status='draft', tags=['paper'], sources=[r['source_path']], confidence='medium',
        contested=False, contradictions=[], schema='pkm-knowledge-page/v1', revision='1', transaction_id=tx,
        policy_revision=POLICY, prompt_revision=PROMPT, generation_ref=result['path'],
        read_scope=doc['read_scope'], unread_scope=doc['unread_scope'], review_state='unreviewed',
        source_hashes={r['source_path']:r['source_sha256']}, agent_review_ref=review['path'])
    page = '---\n'+''.join(k+': '+json.dumps(v, ensure_ascii=False, allow_nan=False)+'\n' for k,v in fm.items())+'---\n\n'+doc['markdown_body']
    start, end, header = index_parts(before_index)
    link = '[['+output[:-3]+']]'
    require(link not in before_index, 'existing index entry')
    title = ' '.join(doc['title'].split()).replace('[', '&#91;').replace(']', '&#93;')
    old_section = before_index[start:end]
    new_section = re.sub(r'^아직 작성된 페이지가 없다\.\n?', '', old_section, flags=re.M).rstrip()+'\n\n'+f'- {link} — {title} (draft/unreviewed, PDF text)\n\n'
    new_header = f'Last updated: {today} | Total pages: {count}'
    after_index = (before_index[:start]+new_section+before_index[end:]).replace(header.group(), new_header, 1)
    event = (f'\n## [{today}] create | PDF text draft — arXiv {vid}\n\n<!-- publication-event:{tx} -->\n'
        f'- Page: `{output}`; run: `{run}`; work_key: `{key}`.\n'
        f'- Source SHA-256: `{r["source_sha256"]}`; agent review: `{review["path"]}`; mechanical checks: `{report["path"]}`.\n'
        '- Draft/unreviewed; no human review, visual inspection or experimental reproduction claimed.\n')
    refs = [dict(path=output, sha256=sha(page.encode()), revision='1')]
    receipt = dict(schema='pkm-publication-receipt/v1', transaction_id=tx, run_id=Path(run).name,
        work_key=key, actual_input_hashes=context['snapshots'], output_refs=refs, committed_at=now.isoformat(),
        read_scope=doc['read_scope'], unread_scope=doc['unread_scope'], evidence_check_ref=review['path'],
        structural_check_ref=report['path'], human_review_ref=None,
        model_route=dict(**{k:r[k] for k in MODEL}, response_model=r['response_model'],
                         **r['approved_route'], instructions_sha256=r['instructions_sha256']),
        budget_usage_ref=result['path'], cost_usd=r.get('cost_usd'))
    item.update(status='published_draft', reason='Bound mechanical and agent evidence review; human unreviewed',
        requested_scope=SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope'], resume_at=None,
        work_key=key, output_refs=refs, receipt_ref=receipt_path, human_review=None)
    state['transactions'].append(dict(transaction_id=tx, journal_path=journal, status='committed'))
    state['receipts'].append(receipt_path)
    charged = r.get('cost_usd')
    state['cost_events'].append(dict(event_id=tx, run_id=Path(run).name, role='pilot', scope_id=vid,
        created_at=now.isoformat(), kst_day=today, status='unknown' if charged is None else 'settled',
        reserved_usd=None, charged_usd=charged, usage_receipt=result['path']))
    state['last_run'] = run
    schema_validate(context['schema'], state, 'compilation')
    values = [(output, None, page.encode()), ('index.md', before_index.encode(), after_index.encode()),
              ('log.md', log, log+event.encode()), (receipt_path, None, encoded(receipt)), (STATE, before_state, encoded(state))]
    targets = [dict(path=p, before_hash=None if b is None else sha(b), after_hash=sha(a), order=n, stage='planned')
               for n,(p,b,a) in enumerate(values, 1)]
    targets[0].update(before_image=None, after_image=page, before_image_ref=None,
                      after_image_ref=journal+'#/plan/targets/0/after_image')
    return dict(schema='pkm-publication-journal/v1', transaction_id=tx, run_id=Path(run).name, role='pilot',
        started_at=now.isoformat(), approval_refs=[dict(path=r['approval_ref'],sha256=r['approval_sha256']),
            dict(path=RUN+'/scope-approval.json',sha256=r['scope_approval_sha256'])], input_hashes=context['snapshots'],
        targets=targets, log_event_id=tx, status='prepared', work_key=key, journal_path=journal, receipt=receipt,
        state_after=state, structural_path=structural, structural_report=report['value'],
        index=dict(before_section=old_section, after_section=new_section, before_header=header.group(), after_header=new_header),
        log=dict(prefix_bytes=len(log), prefix_sha256=sha(log), event=event),
        before_state=before_state.decode(), before_index=before_index, page_count=count)

def build_plan(fs, vid, run, result, report, review, now):
    """Return a five-target plan, writing nothing; caller owns all live gates/lock."""
    context = _bound(fs, vid, run, result, report, review, now)
    before = fs.read(STATE)
    require(sha(before) == report['preflight']['snapshots'][STATE], 'preflight state drift')
    output = f'entities/arxiv-{vid}.md'
    require(fs.read(output, True) is None, 'existing output; never overwrite')
    plan = _assemble(vid, run, result, report, review, now, context, before,
                     fs.read('index.md').decode(), fs.read('log.md'), page_count(fs, output))
    for path in (plan['journal_path'], plan['structural_path'], plan['targets'][3]['path']):
        require(fs.read(path, True) is None, 'existing publication artifact')
    return plan

def validate_plan(fs, plan, vid, run, result, report, review, now):
    """Validate deterministic intent + current targets; return generic helper context."""
    context = _bound(fs, vid, run, result, report, review, now)
    require(plan['status'] in ('prepared','committed'), 'unknown journal status')
    started = datetime.fromisoformat(plan['started_at'])
    require(started.tzinfo is not None and started <= now, 'journal timestamp')
    before = plan['before_state'].encode()
    require(sha(before) == report['preflight']['snapshots'][STATE], 'journal before-state binding')
    log = fs.read('log.md')[:plan['log']['prefix_bytes']]
    expected = _assemble(vid, run, result, report, review, started, context, before,
                         plan['before_index'], log, plan['page_count'])
    expected['status'] = plan['status']
    if plan['status'] == 'committed':
        for target in expected['targets']:
            target['stage'] = 'verified'
    require(canonical(plan) == canonical(expected), 'journal plan conflict')
    schema_validate(context['schema'], decode(fs.read(STATE)), 'compilation')
    if plan['status'] == 'committed':
        verify_committed(fs, plan, context, vid)
    else:
        require(plan['page_count'] == page_count(fs, plan['targets'][0]['path']), 'page count drift')
        classify(fs, plan)
    return context
