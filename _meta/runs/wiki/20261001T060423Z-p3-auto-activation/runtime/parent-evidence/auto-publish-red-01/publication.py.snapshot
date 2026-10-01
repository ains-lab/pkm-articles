"""P3 single-note transactional publication; no CLI, parser, or model calls.

The parent owns the daily generation lock and authority guard. This module owns
only the brief collection lock and entity/index/log/receipt/compilation commit.
"""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

import p3_common as c


def _text(value, limit=40000):
    return isinstance(value,str) and 0 < len(value.strip()) <= limit


def _document_contract(ctx, doc):
    """Repeat bounded output/link checks without re-parsing source or models."""
    g, v = c.helper('publish'), c.helper('verify')
    g.exact_keys(doc,'title summary version_id main_text_complete read_scope unread_scope limitations claims markdown_body','document')
    for key,limit in [('title',1000),('summary',2000),('markdown_body',40000)]:
        c.require(_text(doc[key],limit), 'empty/oversize document '+key)
    for key in ('read_scope','unread_scope','limitations'):
        c.require(isinstance(doc[key],list) and 1 <= len(doc[key]) <= 1000 and
                  all(_text(x,1000) for x in doc[key]), 'missing document '+key)
    body = doc['markdown_body']
    c.require(not re.match(r'\A\s*(?:---|\+\+\+)\s*(?:\n|$)',body) and
              not re.search(r'<[^>]*>|!\[|`|https?://|data:|file:|(?m:^[ ]{0,3}~{3})|(?m:^\s*\[[^]\n]+\]:)',body), 'unsafe document markup/link')
    visible = v.visible_markdown(body)
    claims = doc['claims']
    c.require(isinstance(claims,list) and 1 <= len(claims) <= 100, 'missing/oversize claims')
    for claim in claims:
        g.exact_keys(claim,'id kind statement conditions anchor quote','claim')
        c.require(re.fullmatch(r'C[0-9]+',claim['id']) is not None and claim['kind'] in ('author_report','analyst_interpretation') and
                  all(_text(claim[k],limit) for k,limit in [('statement',2000),('conditions',2000),('anchor',400),('quote',400)]), 'invalid claim')
        anchor = claim['anchor']
        c.require(anchor in doc['read_scope'] and ('#' not in anchor) and
                  (ctx['item']['format'] != 'pdf' or re.fullmatch(r'page=[1-9][0-9]*',anchor) is not None), 'claim scope/anchor')
        cite = ctx['item']['source_path']+'#'+anchor
        c.require(any(re.search(r'\b'+re.escape(claim['id'])+r'\b',line) and cite in v.citation_targets(line)
                      for line in visible.splitlines()), 'claim citation missing')
    c.require(set(re.findall(r'\bC[0-9]+\b',visible)) == {x['id'] for x in claims}, 'body claim set conflict')
    allowed = {w['path']:w for w in ctx['wiki'] if w['path'].startswith('concepts/')}
    for target in re.findall(r'\[\[([^\[\]\n]+)\]\]',visible):
        name,mark,anchor = target.split('|',1)[0].partition('#')
        path = name if name.endswith('.md') else name+'.md'
        c.require(path in allowed, 'only existing consumed concept links permitted')
        ctx['fs'].parts(path)
        c.require(c.sha(ctx['fs'].read(path)) == allowed[path]['sha256'], 'consumed concept changed')
        if mark:
            c.require(bool(anchor) and v.markdown_anchor_exists(allowed[path]['text'],anchor), 'concept anchor missing')
    remainder = re.sub(r'\[\[[^\[\]\n]+\]\]','',visible)
    c.require('[[' not in remainder and ']]' not in remainder, 'malformed wikilink')
    for line in visible.splitlines():
        for target in v.citation_targets(line):
            path,mark,anchor = target.partition('#')
            c.require(path == ctx['item']['source_path'] and mark and anchor in doc['read_scope'], 'unbound source citation')


def _bound(ctx, bundle):
    fs = ctx['fs']
    c.require(Path(ctx['root']) == fs.root, 'context root mismatch')
    if ctx['synthetic']:
        c.synthetic_root(fs.root)
    else:
        c.require(fs.root == c.ROOT, 'production root mismatch')
    c.require(callable(ctx['guard']), 'authority guard required')
    ctx['guard']()
    c.require(bundle['status'] == 'ready_to_publish', 'bundle is not publishable')
    g = c.helper('publish')
    snapshots = dict(ctx['snapshots'])
    c.require(not {c.STATE, 'index.md', 'log.md'} & snapshots.keys(), 'mutable input snapshots forbidden')
    values = {}
    for name, suffix in [('result','result'), ('report','report'), ('review','review')]:
        ref = bundle['artifacts'][name]
        g.exact_keys(ref, 'path sha256', 'evidence descriptor')
        c.require(ref['path'] == ctx['artifact_prefix']+'-'+suffix+'.json', 'artifact path mismatch')
        raw = fs.read(ref['path'])
        c.require(c.sha(raw) == ref['sha256'] and c.decode(raw) == bundle[name], 'artifact descriptor mismatch')
        snapshots[ref['path']] = ref['sha256']
        values[name] = c.decode(raw)
    r, report, review = (values[k] for k in ('result','report','review'))
    item = ctx['item']
    c.require(c.canonical(ctx['model']) == c.canonical(c.MODEL) and ctx['route'] == c.ROUTE and
              ctx['requested_scope'] == c.SCOPE, 'context model/route/scope')
    c.require(re.fullmatch(r'[0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*',item['version_id']) is not None and
              re.fullmatch(r'_meta/runs/wiki/[A-Za-z0-9_-]+',ctx['run']) is not None, 'run/version identity')
    c.require(re.fullmatch(re.escape(ctx['run'])+'/items/'+re.escape(item['version_id'])+r'/attempt[12]',
                          ctx['artifact_prefix']) is not None, 'artifact prefix identity')
    expected = dict(schema='pkm-p3-content-result/v1', **c.MODEL, route=c.ROUTE,
                    policy_revision=c.POLICY, contract_revision=c.CONTRACT, prompt_revision=c.PROMPT_REV,
                    completed=True, response_status='completed', response_model=c.MODEL['model'], error=None,
                    cost_policy='no_cost_cap', requested_scope=c.SCOPE,
                    consumed_wiki=[dict(path=w['path'],sha256=w['sha256']) for w in ctx['wiki']])
    expected.update({k:ctx[k] for k in ('approval_ref','approval_sha256','policy_sha256','prompt_sha256')})
    expected.update({k:item[k] for k in ('version_id','source_path','source_sha256','source_bytes','metadata_path','metadata_sha256')})
    for key,value in expected.items():
        c.require(key in r and c.canonical(r[key]) == c.canonical(value), 'result binding: '+key)
    required = {ctx['approval_ref']:ctx['approval_sha256'], '_meta/automation.json':ctx['policy_sha256'],
                '_meta/prompts/wiki-compile.md':ctx['prompt_sha256'], item['source_path']:item['source_sha256'],
                item['metadata_path']:item['metadata_sha256']}
    required.update({w['path']:w['sha256'] for w in ctx['wiki']})
    c.require(all(snapshots.get(p) == value for p,value in required.items()) and
              {'SCHEMA.md','_meta/automation-contracts.schema.json'} <= snapshots.keys(), 'required snapshot bindings')
    c.require(c.decode(fs.read('_meta/automation-contracts.schema.json')) == ctx['schema'], 'schema context mismatch')
    meta = c.decode(fs.read(item['metadata_path']))
    fmt = item['format']
    c.require(fmt in ('html','pdf') and item['source_path'] == f'raw/articles/4cff5b4f10ec/arxiv-{item["version_id"]}/source.{fmt}' and
              item['metadata_path'] == item['source_path'].rsplit('.',1)[0]+'.json', 'source path identity')
    c.require(meta == ctx['metadata'] and meta.get('schema') == f'arxiv-{fmt}-source/v1' and
              meta.get('version_id') == item['version_id'] and meta.get(fmt+'_file') == 'source.'+fmt and
              meta.get(fmt+'_sha256') == item['source_sha256'] and meta.get(fmt+'_bytes') == item['source_bytes'] and
              len(fs.read(item['source_path'])) == item['source_bytes'], 'source metadata identity')
    doc = r['document']
    _document_contract(ctx,doc)
    c.require(doc == report['document'] and doc['main_text_complete'] is True and
              doc['version_id'] == ctx['item']['version_id'], 'document mismatch/incomplete')
    c.require(report['passed'] is True and report['checks'] and
              all(x['ok'] is True for x in report['checks']), 'mechanical checks failed')
    c.require(review['passed'] is True and review['human_review_ref'] is None, 'agent review failed')
    c.require(report.get('schema') == 'pkm-p3-verification/v1' and
              report.get('result_sha256') == bundle['artifacts']['result']['sha256'], 'mechanical report binding')
    c.require(review.get('schema') == 'pkm-p3-agent-review/v1' and
              review.get('result_sha256') == bundle['artifacts']['result']['sha256'] and
              review.get('report_sha256') == bundle['artifacts']['report']['sha256'], 'semantic review binding')
    c.require(review.get('response_model') == c.MODEL['model'] and review.get('response_status') == 'completed',
              'semantic review model/completion')
    c.require(review.get('body_supported') is True and review.get('body_verdict') == 'supported' and
              review.get('main_text_complete') is True and _text(review.get('body_rationale'),1200) and
              _text(review.get('coverage_rationale'),1200), 'unsupported/unreviewed body')
    claims = doc['claims']
    c.require(isinstance(claims,list) and claims and all(isinstance(x,dict) for x in claims), 'claims missing')
    ids = [x['id'] for x in claims]
    c.require(len(set(ids)) == len(ids) and review.get('claim_ids') == ids, 'all-claims review required')
    checked = review.get('claims')
    c.require(isinstance(checked,list) and len(checked) == len(claims), 'all-claims review required')
    expected = {x['id']:x for x in claims}
    seen = set()
    for record in checked:
        g.exact_keys(record,'id verdict rationale quote_sha256','semantic claim')
        ident = record['id']
        c.require(isinstance(ident,str) and ident in expected and ident not in seen, 'semantic claim identity')
        seen.add(ident)
        c.require(record['quote_sha256'] == c.sha(expected[ident]['quote'].encode()) and
                  record['verdict'] == 'supported' and _text(record['rationale'],1200), 'unsupported/unreviewed claim')
    g.check_snapshots(fs, snapshots)
    return dict(snapshots=snapshots, result=r, report=report, review=review, document=doc, schema=ctx['schema'])


def _identity(ctx, evidence):
    item, r = ctx['item'], evidence['result']
    work = dict(source='arxiv', version_id=item['version_id'], source_sha256=item['source_sha256'],
                policy_revision=c.POLICY, policy_sha256=ctx['policy_sha256'], prompt_revision=c.PROMPT_REV,
                prompt_sha256=ctx['prompt_sha256'], requested_scope=c.SCOPE)
    key = c.sha(c.canonical(work))
    result_ref = dict(path=ctx['artifact_prefix']+'-result.json', sha256=c.sha(c.encoded(r)))
    tx = 'p3-' + c.sha(c.canonical([ctx['run'], result_ref, key]))[:32]
    return key, tx


def _assemble(ctx, evidence, basis):
    g = c.helper('publish')
    before = basis['before_state'].encode()
    state = c.decode(before)
    g.schema_validate(ctx['schema'], state, 'compilation')
    c.require(state['safety_block'] is False, 'compilation safety block')
    c.require(all(t['status'] == 'committed' for t in state['transactions']), 'other unresolved transaction')
    c.require(len({i['version_id'] for i in state['items']}) == len(state['items']), 'duplicate state item')
    vid = ctx['item']['version_id']
    selected = [i for i in state['items'] if i['version_id'] == vid]
    c.require(len(selected) == 1, 'missing state item')
    item = selected[0]
    c.require(item['status'] in ('reading','ready_to_publish') and item['human_review'] is None,
              'invalid publication transition/reviewed item')
    for key in ('source','version_id','format','source_path','source_sha256','source_bytes','metadata_path','metadata_sha256'):
        c.require(item[key] == ctx['item'][key], 'state source conflict: '+key)
    c.require(not item['output_refs'] and item['receipt_ref'] is None, 'existing output state')
    work, tx = _identity(ctx, evidence)
    c.require(item['work_key'] in (None, work), 'state work key conflict')
    prefix = ctx['artifact_prefix']
    journal, receipt_path = prefix+'-publish-journal.json', prefix+'-receipt.json'
    structural = prefix+'-publish-verification.json'
    doc, r = evidence['document'], evidence['result']
    output = f'entities/arxiv-{vid}.md'
    now = datetime.fromisoformat(basis['started_at'])
    today = now.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    fm = dict(title=doc['title'], summary=doc['summary'], created=today, updated=today,
              last_reviewed=None, type='entity', status='draft', tags=['paper'], sources=[item['source_path']],
              confidence='medium', contested=False, contradictions=[], schema='pkm-knowledge-page/v1',
              revision='1', transaction_id=tx, policy_revision=c.POLICY, prompt_revision=c.PROMPT_REV,
              generation_ref=prefix+'-result.json', read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
              review_state='unreviewed', source_hashes={item['source_path']:item['source_sha256']},
              agent_review_ref=prefix+'-review.json')
    page = '---\n'+''.join(k+': '+json.dumps(v, ensure_ascii=False, allow_nan=False)+'\n' for k,v in fm.items())+'---\n\n'+doc['markdown_body'].rstrip()+'\n'
    before_index = basis['before_index']
    start, end, header = g.index_parts(before_index)
    link = '[['+output[:-3]+']]'
    c.require(link not in before_index, 'existing index entry')
    title = ' '.join(doc['title'].split()).replace('[', '&#91;').replace(']', '&#93;')
    old_section = before_index[start:end]
    entry = f'- {link} — {title} (draft/unreviewed, P3 {item["format"]} text)\n'
    new_section = re.sub(r'^아직 작성된 페이지가 없다\.\n?', '', old_section, flags=re.M).rstrip()+'\n\n'+entry+'\n'
    new_header = f'Last updated: {today} | Total pages: {basis["page_count"]}'
    after_index = (before_index[:start]+new_section+before_index[end:]).replace(header.group(), new_header, 1)
    log = basis['before_log'].encode()
    event = (f'\n## [{today}] create | P3 draft — arXiv {vid}\n\n<!-- publication-event:{tx} -->\n'
             f'- Page: `{output}`; run: `{ctx["run"]}`; work_key: `{work}`.\n'
             f'- Source SHA-256: `{item["source_sha256"]}`; agent review: `{prefix}-review.json`; mechanical checks: `{prefix}-report.json`.\n'
             '- Draft/unreviewed; no human review, visual inspection or experimental reproduction claimed.\n')
    refs = [dict(path=output, sha256=c.sha(page.encode()), revision='1')]
    receipt = dict(schema='pkm-publication-receipt/v1', transaction_id=tx, run_id=Path(ctx['run']).name,
                   work_key=work, actual_input_hashes=evidence['snapshots'], output_refs=refs,
                   committed_at=now.isoformat(), read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
                   evidence_check_ref=prefix+'-review.json', structural_check_ref=prefix+'-report.json',
                   human_review_ref=None, model_route=dict(**ctx['model'], approved_route=ctx['route'], response_model=r['response_model']),
                   budget_usage_ref=prefix+'-result.json', cost_usd=r.get('cost_usd'))
    item.update(status='published_draft', reason='Bound mechanical and semantic agent review; human unreviewed',
                requested_scope=c.SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
                resume_at=None, work_key=work, output_refs=refs, receipt_ref=receipt_path, human_review=None)
    c.require(len({e['event_id'] for e in state['cost_events']}) == len(state['cost_events']), 'duplicate cost event')
    state['transactions'].append(dict(transaction_id=tx, journal_path=journal, status='committed'))
    state['receipts'].append(receipt_path)
    charged = r.get('cost_usd')
    state['cost_events'].append(dict(event_id=tx, run_id=Path(ctx['run']).name, role='daily_compile', scope_id=vid,
                                    created_at=now.isoformat(), kst_day=today, status='unknown' if charged is None else 'settled',
                                    reserved_usd=None, charged_usd=charged, usage_receipt=prefix+'-result.json'))
    state['last_run'] = ctx['run']
    g.schema_validate(ctx['schema'], state, 'compilation')
    values = [(output,None,page.encode()), ('index.md',before_index.encode(),after_index.encode()),
              ('log.md',log,log+event.encode()), (receipt_path,None,c.encoded(receipt)), (c.STATE,before,c.encoded(state))]
    targets = [dict(path=p,before_hash=None if b is None else c.sha(b),after_hash=c.sha(a),order=n,stage='planned')
               for n,(p,b,a) in enumerate(values,1)]
    targets[0].update(before_image=None,after_image=page,before_image_ref=None,
                      after_image_ref=journal+'#/plan/targets/0/after_image')
    return dict(schema='pkm-publication-journal/v1',transaction_id=tx,run_id=Path(ctx['run']).name,role='daily_compile',
                started_at=now.isoformat(),approval_refs=[dict(path=ctx['approval_ref'],sha256=ctx['approval_sha256'])],
                input_hashes=evidence['snapshots'],targets=targets,log_event_id=tx,status='prepared',work_key=work,
                journal_path=journal,receipt=receipt,state_after=state,structural_path=structural,structural_report=evidence['report'],
                index=dict(before_section=old_section,after_section=new_section,before_header=header.group(),after_header=new_header),
                log=dict(prefix_bytes=len(log),prefix_sha256=c.sha(log),event=event))


def _verify_committed(ctx, plan):
    fs, g = ctx['fs'], c.helper('publish')
    targets = plan['targets']
    c.require(fs.read(targets[0]['path'], True) == targets[0]['after_image'].encode(), 'committed page conflict')
    c.require(fs.read(targets[3]['path'], True) == c.encoded(plan['receipt']), 'committed receipt conflict')
    c.require(fs.read(plan['structural_path'], True) == c.encoded(plan['structural_report']), 'committed verification conflict')
    state = c.decode(fs.read(c.STATE))
    g.schema_validate(ctx['schema'], state, 'compilation')
    c.require(state['safety_block'] is False, 'committed safety block')
    vid = ctx['item']['version_id']
    current = [i for i in state['items'] if i['version_id'] == vid]
    expected = [i for i in plan['state_after']['items'] if i['version_id'] == vid]
    c.require(len(current) == 1 and current == expected, 'committed item conflict')
    tx = dict(transaction_id=plan['transaction_id'],journal_path=plan['journal_path'],status='committed')
    c.require(state['transactions'].count(tx) == 1 and state['receipts'].count(targets[3]['path']) == 1, 'committed state transaction conflict')
    cost = [e for e in state['cost_events'] if e['event_id'] == plan['transaction_id']]
    c.require(cost == [plan['state_after']['cost_events'][-1]], 'committed cost event conflict')
    index = fs.read('index.md').decode()
    start,end,header = g.index_parts(index)
    link = '[['+targets[0]['path'][:-3]+']]'
    c.require(index.count(link) == 1 and link in index[start:end], 'committed index entry conflict')
    c.require(int(header.group().split('Total pages: ')[1]) == g.page_count(fs,targets[0]['path']), 'committed page count conflict')
    log = fs.read('log.md')
    spec = plan['log']
    marker = ('<!-- publication-event:'+plan['transaction_id']+' -->').encode()
    c.require(c.sha(log[:spec['prefix_bytes']]) == spec['prefix_sha256'] and log.count(spec['event'].encode()) == 1 and
              log.count(marker) == 1, 'committed log conflict')


def _publication_basis(ctx, evidence, now):
    """Keep prior mutable inputs outside the untrusted recovery journal.

    Exclusive-create, safe descriptor readback, and the cooperative edit freeze
    make this an immutable transaction input (not a substitute for signatures).
    """
    fs, g = ctx['fs'], c.helper('publish')
    path = ctx['artifact_prefix']+'-publication-basis.json'
    raw = fs.read(path, True)
    if raw is None:
        basis = dict(schema='pkm-p3-publication-basis/v1', started_at=now.isoformat(),
                     input_hashes=evidence['snapshots'], before_state=fs.read(c.STATE).decode(),
                     before_index=fs.read('index.md').decode(), before_log=fs.read('log.md').decode(),
                     page_count=g.page_count(fs,f'entities/arxiv-{ctx["item"]["version_id"]}.md'))
        raw = c.encoded(basis)
        fs.write(path,raw,None)
    basis = c.decode(raw)
    g.exact_keys(basis, 'schema started_at input_hashes before_state before_index before_log page_count', 'publication basis')
    c.require(basis['schema'] == 'pkm-p3-publication-basis/v1' and basis['input_hashes'] == evidence['snapshots'],
              'publication basis input mismatch')
    started = datetime.fromisoformat(basis['started_at'])
    c.require(started.tzinfo is not None and started.utcoffset() == timedelta(0) and started <= now, 'publication basis time')
    c.require(type(basis['page_count']) is int and basis['page_count'] > 0, 'publication basis count')
    evidence['snapshots'] = dict(evidence['snapshots'], **{path:c.sha(raw)})
    return basis


def _validate_reconstruction(ctx, evidence, basis, plan):
    expected = _assemble(ctx,evidence,basis)
    expected['status'] = plan['status']
    if plan['status'] == 'committed':
        for target in expected['targets']:
            target['stage'] = 'verified'
    c.require(c.canonical(plan) == c.canonical(expected), 'journal deterministic reconstruction conflict')
    if plan['status'] == 'prepared':
        c.require(basis['page_count'] == c.helper('publish').page_count(ctx['fs'],plan['targets'][0]['path']), 'recovery page count drift')
        c.helper('publish').classify(ctx['fs'],plan)


def publish(ctx, bundle, *, now=None, hook=None):
    """Publish one bound draft or fail closed. Authority belongs to ctx.guard."""
    supplied_now = now
    now = supplied_now or datetime.now(timezone.utc)
    c.require(now.tzinfo is not None and now.utcoffset() == timedelta(0), 'aware UTC timestamp required')
    g, fs = c.helper('publish'), ctx['fs']
    hook = hook or (lambda stage: None)
    evidence = _bound(ctx,bundle)
    work, tx = _identity(ctx,evidence)
    prefix = ctx['artifact_prefix']
    journal_path = prefix+'-publish-journal.json'
    def priority():
        current = supplied_now or datetime.now(timezone.utc)
        kst = current.astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')
        return kst >= '23:55' or kst < '01:35'
    def busy():
        return dict(status='skipped_busy',work_key=work,output_refs=[],receipt_ref=None,journal_path=journal_path)
    if priority():
        return busy()
    hook('before_lock')
    if priority():
        return busy()
    with g.collection_lock(fs,Path(ctx['run']).name,tx,now) as owned:
        if not owned:
            return busy()
        hook('after_lock')
        owned()
        if priority():
            return busy()
        def guard():
            owned()
            c.require(not priority(), 'collector priority interrupted publication')
            ctx['guard']()
            g.check_snapshots(fs,evidence['snapshots'])
        guard()
        g.reject_other_unresolved(fs,journal_path)
        plan = g.read_journal(fs,journal_path)
        if plan is None:
            c.require(fs.read(f'entities/arxiv-{ctx["item"]["version_id"]}.md',True) is None, 'existing output; never overwrite')
        else:
            c.require(fs.read(prefix+'-publication-basis.json',True) is not None, 'missing publication basis')
        basis = _publication_basis(ctx,evidence,now)
        hook('after_basis')
        guard()
        if plan is None:
            plan = _assemble(ctx,evidence,basis)
            g.classify(fs,plan)
            guard()
            g.write_journal(fs,plan)
            hook('after_journal')
        else:
            _validate_reconstruction(ctx,evidence,basis,plan)
            if plan['status'] == 'committed':
                _verify_committed(ctx,plan)
                return dict(status='noop',work_key=work,output_refs=plan['receipt']['output_refs'],
                            receipt_ref=plan['targets'][3]['path'],journal_path=journal_path)
        g.apply_plan(fs,plan,evidence,hook,guard)
        guard()
        _verify_committed(ctx,plan)
        return dict(status='published_draft',work_key=work,output_refs=plan['receipt']['output_refs'],
                    receipt_ref=plan['targets'][3]['path'],journal_path=journal_path)
