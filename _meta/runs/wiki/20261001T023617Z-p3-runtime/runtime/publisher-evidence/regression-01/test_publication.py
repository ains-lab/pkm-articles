"""Synthetic filesystem publisher tests; no real paper reads/model calls."""
import copy
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RUN = '_meta/runs/wiki/20261001T023617Z-p3-runtime'
POLICY = 'pkm-html-pdf-text-knowledge/v3'
CONTRACT = 'pkm-contracts/v3'
PROMPT = 'wiki-compile/v3'
SCOPE = 'P3 main-text complete'
MODEL = dict(provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh', fallback_allowed=False)
ROUTE = dict(base_url='http://10.10.1.244:2455/v1', api_mode='codex_responses')
STATE = '_meta/state/compilation.json'
NOW = datetime(2026, 10, 1, 3, tzinfo=timezone.utc)
VID = '2610.00001v1'
legacy_path = ROOT / '_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py'
g = types.ModuleType('publication_test_generic')
g.__file__ = str(legacy_path)
exec(compile(legacy_path.read_bytes(), str(legacy_path), 'exec'), g.__dict__)


class Fixture:
    def __init__(self, fmt='html'):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-publication-', dir=HERE)
        self.root = Path(self.tmp.name)
        self.fs = g.Files(self.root)
        self.guard_calls = 0
        for folder in ('entities', 'concepts', 'comparisons', 'queries', '_meta/locks'):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        schema = g.decode((ROOT / '_meta/automation-contracts.schema.json').read_bytes())
        self.put('_meta/automation-contracts.schema.json', g.encoded(schema))
        self.put('SCHEMA.md', (ROOT / 'SCHEMA.md').read_bytes())
        self.put('concepts/synthetic.md', b'---\nstatus: draft\n---\nSynthetic concept.\n')
        self.put('index.md', b'# Index\n\n> Last updated: 2026-10-01 | Total pages: 1\n\n## Entities\n\n## Concepts\n\n- [[concepts/synthetic]]\n\n## Raw Sources\n\nSynthetic source.\n')
        self.put('log.md', b'# Log\n\nPrior history must remain.\n')
        source = f'raw/articles/4cff5b4f10ec/arxiv-{VID}/source.{fmt}'
        raw = b'<html><body><p id="S1">Synthetic controlled experiment supports a bounded result.</p></body></html>' if fmt == 'html' else b'%PDF-1.4\nSynthetic bytes; publisher does not parse PDF.\n%%EOF\n'
        self.put(source, raw)
        meta_path = source.rsplit('.', 1)[0] + '.json'
        meta = dict(schema=f'arxiv-{fmt}-source/v1', version_id=VID, source_format=fmt,
                    **{fmt+'_file': 'source.'+fmt, fmt+'_sha256': g.sha(raw), fmt+'_bytes': len(raw)})
        self.put(meta_path, g.encoded(meta))
        self.prefix = f'{RUN}/items/{VID}/attempt1'
        approval = RUN + '/approval.json'
        self.put(approval, g.encoded(dict(synthetic=True, approved=True)))
        self.put('_meta/automation.json', g.encoded(dict(enabled=True, policy_revision=POLICY)))
        self.put('_meta/prompts/wiki-compile.md', b'Synthetic prompt only.\n')
        self.put(self.prefix+'-reservation.json', g.encoded(dict(synthetic=True, version_id=VID)))
        item = dict(source='arxiv', version_id=VID, format=fmt, source_path=source,
                    source_sha256=g.sha(raw), source_bytes=len(raw), metadata_path=meta_path,
                    metadata_sha256=g.sha(g.encoded(meta)), collected_at=NOW.isoformat(),
                    status='reading', reason='Synthetic authorized reading', requested_scope=SCOPE,
                    read_scope=[], unread_scope=[], resume_at=None, work_key=None,
                    output_refs=[], receipt_ref=None, failure_count=0, human_review=None)
        self.state = dict(schema='pkm-compilation-state/v1', policy_revision=POLICY, contract_revision=CONTRACT,
                          initialized_at=NOW.isoformat(), enabled=True, safety_block=False, safety_block_reason=None,
                          items=[item], transactions=[], receipts=[], cost_events=[], last_run=None)
        g.schema_validate(schema, self.state, 'compilation')
        self.put(STATE, g.encoded(self.state))
        paths = ['SCHEMA.md', '_meta/automation-contracts.schema.json', approval, '_meta/automation.json',
                 '_meta/prompts/wiki-compile.md', source, meta_path, 'concepts/synthetic.md']
        snapshots = {p: g.sha(self.fs.read(p)) for p in paths}
        self.ctx = dict(root=self.root, fs=self.fs, run=RUN, item=copy.deepcopy(item), metadata=meta,
                        auto=dict(enabled=True), schema=schema, synthetic=True, snapshots=snapshots,
                        approval_ref=approval, approval_sha256=snapshots[approval],
                        policy_sha256=snapshots['_meta/automation.json'], prompt_sha256=snapshots['_meta/prompts/wiki-compile.md'],
                        prompt='Synthetic prompt only.', model=MODEL, route=ROUTE, requested_scope=SCOPE,
                        wiki=[dict(path='concepts/synthetic.md', sha256=snapshots['concepts/synthetic.md'],
                                   text=self.fs.read('concepts/synthetic.md').decode())],
                        artifact_prefix=self.prefix, guard=self.guard)
        anchor = 'S1' if fmt == 'html' else 'page=1'
        claim = dict(id='C01', kind='author_report', statement='A bounded result is reported.',
                     conditions='Synthetic controlled experiment', anchor=anchor,
                     quote='Synthetic controlled experiment supports a bounded result.')
        document = dict(title='Synthetic paper', summary='A bounded synthetic result.', version_id=VID,
                        main_text_complete=True, read_scope=[anchor], unread_scope=['Figures not reviewed'],
                        limitations=['No independent reproduction'], claims=[claim],
                        markdown_body=f'# Synthetic paper\n\nVersion {VID}; text reviewed, figures unread.\n\nC01: A bounded result is reported. ^[{source}#{anchor}]\n\n[[concepts/synthetic]]\n')
        result = dict(schema='pkm-p3-content-result/v1', document=document, version_id=VID,
                      **{k:item[k] for k in ('source_path','source_sha256','source_bytes','metadata_path','metadata_sha256')},
                      policy_revision=POLICY, contract_revision=CONTRACT, policy_sha256=self.ctx['policy_sha256'],
                      prompt_revision=PROMPT, prompt_sha256=self.ctx['prompt_sha256'], approval_ref=approval,
                      approval_sha256=self.ctx['approval_sha256'], requested_scope=SCOPE, **MODEL,
                      response_model=MODEL['model'], route=ROUTE, completed=True,
                      consumed_wiki=[dict(path='concepts/synthetic.md', sha256=snapshots['concepts/synthetic.md'])], cost_policy='no_cost_cap',
                      response_status='completed', error=None, cost_usd=None)
        report = dict(schema='pkm-p3-verification/v1', passed=True, checks=[dict(name='synthetic evidence',ok=True)], document=document, result_sha256=g.sha(g.encoded(result)))
        review = dict(schema='pkm-p3-agent-review/v1', actor='agent', passed=True, human_review_ref=None,
                      version_id=VID, result_sha256=g.sha(g.encoded(result)), report_sha256=g.sha(g.encoded(report)),
                      source_sha256=item['source_sha256'], requested_scope=SCOPE, model=MODEL, route=ROUTE,
                      claim_ids=['C01'], claims=[dict(id='C01', quote_sha256=g.sha(claim['quote'].encode()),
                      verdict='supported', rationale='Synthetic test-only reviewer finding, not a live model result.')],
                      response_model=MODEL['model'], response_status='completed', body_verdict='supported', body_supported=True,
                      body_rationale='Synthetic test-only whole body finding.', main_text_complete=True,
                      coverage_rationale='Synthetic source coverage reviewed.')
        self.bundle = dict(status='ready_to_publish', result=result, report=report, review=review, artifacts={})
        self.persist()

    def guard(self):
        self.guard_calls += 1
        g.check_snapshots(self.fs, self.ctx['snapshots'])

    def put(self, path, raw):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)

    def persist(self):
        for key, suffix in [('result','result'), ('report','report'), ('review','review')]:
            raw = g.encoded(self.bundle[key])
            path = self.prefix + '-' + suffix + '.json'
            self.put(path, raw)
            self.bundle['artifacts'][key] = dict(path=path, sha256=g.sha(raw))

    def rebind(self):
        self.bundle['report']['result_sha256'] = g.sha(g.encoded(self.bundle['result']))
        self.bundle['review']['result_sha256'] = self.bundle['report']['result_sha256']
        self.bundle['review']['report_sha256'] = g.sha(g.encoded(self.bundle['report']))
        self.persist()

    def close(self):
        self.tmp.cleanup()


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def publisher(self):
        self.assertTrue((HERE / 'publication.py').is_file(), 'P3 publisher implementation is missing')
        return importlib.import_module('publication')

    def test_interrupted_page_recovers_without_overwriting_later_log(self):
        p = self.publisher()
        def crash(stage):
            if stage == 'after_page':
                raise RuntimeError('synthetic crash')
        with self.assertRaisesRegex(RuntimeError, 'synthetic crash'):
            p.publish(self.f.ctx, self.f.bundle, now=NOW, hook=crash)
        self.assertTrue((self.f.root / f'entities/arxiv-{VID}.md').is_file())
        self.f.put('log.md', self.f.fs.read('log.md') + b'\nUnrelated later event.\n')
        self.f.put('index.md', self.f.fs.read('index.md').replace(b'Synthetic source.', b'Unrelated raw count update.'))
        result = p.publish(self.f.ctx, self.f.bundle, now=NOW)
        self.assertEqual(result['status'], 'published_draft')
        self.assertIn(b'Unrelated later event.', self.f.fs.read('log.md'))
        self.assertIn(b'Unrelated raw count update.', self.f.fs.read('index.md'))
        self.assertEqual(self.f.fs.read('log.md').count(b'<!-- publication-event:'), 1)

    def test_review_requires_all_supported_claims_and_body(self):
        p = self.publisher()
        mutations = [lambda r: r.update(claims=[]),
                     lambda r: r['claims'][0].update(verdict='uncertain'),
                     lambda r: r['claims'][0].update(quote_sha256='0'*64),
                     lambda r: r.update(claim_ids=['C02']),
                     lambda r: r.update(body_supported=False),
                     lambda r: r.update(body_verdict='unsupported'),
                     lambda r: r.update(body_rationale=''),
                     lambda r: r.update(report_sha256='0'*64),
                     lambda r: r.update(response_model='other-model')]
        for n, mutate in enumerate(mutations):
            with self.subTest(case=n):
                f = Fixture()
                try:
                    mutate(f.bundle['review'])
                    f.persist()
                    with self.assertRaises(ValueError):
                        p.publish(f.ctx,f.bundle,now=NOW)
                    self.assertFalse((f.root / f'entities/arxiv-{VID}.md').exists())
                finally:
                    f.close()

    def test_result_binding_rejects_selfconsistent_foreign_evidence(self):
        p = self.publisher()
        changes = dict(schema='wrong', source_path='raw/other.html', source_sha256='0'*64,
                       metadata_sha256='0'*64, policy_sha256='0'*64, prompt_sha256='0'*64,
                       approval_sha256='0'*64, approval_ref='other.json', requested_scope='P2 main-text complete',
                       policy_revision='pkm-html-knowledge/v2', contract_revision='pkm-contracts/v2',
                       prompt_revision='wrong', provider='other', model='other', reasoning_effort='low',
                       fallback_allowed=True, route={}, completed=False, response_status='incomplete',
                       error='failed', cost_policy='cap', consumed_wiki=[])
        for key, value in changes.items():
            with self.subTest(field=key):
                f = Fixture()
                try:
                    f.bundle['result'][key] = value
                    f.rebind()
                    with self.assertRaises(ValueError):
                        p.publish(f.ctx,f.bundle,now=NOW)
                    self.assertFalse((f.root / f'entities/arxiv-{VID}.md').exists())
                finally:
                    f.close()

    def test_collector_priority_skips_without_creating_artifacts(self):
        before = {str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        result = self.publisher().publish(self.f.ctx,self.f.bundle,now=NOW.replace(hour=15))
        self.assertEqual(result['status'],'skipped_busy')
        after = {str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_document_rejects_frontmatter_unbound_links_or_claims(self):
        p = self.publisher()
        changes = [lambda d: d.update(markdown_body='---\nstatus: reviewed\n---\n'+d['markdown_body']),
                   lambda d: d.update(markdown_body=d['markdown_body']+'\n[[entities/nonexistent]]'),
                   lambda d: d.update(markdown_body=d['markdown_body']+'\n[[concepts/nonexistent]]'),
                   lambda d: d.update(markdown_body=d['markdown_body']+'\n[other](https://evil.invalid)'),
                   lambda d: d['claims'][0].update(anchor='page=0'),
                   lambda d: d['claims'][0].update(quote='x'*401),
                   lambda d: d.update(unread_scope=[]),
                   lambda d: d.update(limitations=[])]
        for n, mutate in enumerate(changes):
            with self.subTest(case=n):
                f = Fixture()
                try:
                    mutate(f.bundle['result']['document'])
                    f.bundle['review']['claims'][0]['quote_sha256'] = g.sha(f.bundle['result']['document']['claims'][0]['quote'].encode())
                    f.rebind()
                    with self.assertRaises(ValueError):
                        p.publish(f.ctx,f.bundle,now=NOW)
                    self.assertFalse((f.root / f'entities/arxiv-{VID}.md').exists())
                finally:
                    f.close()

    def test_pdf_bundle_publishes_without_pdf_parsing(self):
        f = Fixture('pdf')
        try:
            result = self.publisher().publish(f.ctx,f.bundle,now=NOW)
            self.assertEqual(result['status'],'published_draft')
            self.assertIn(b'source.pdf#page=1',f.fs.read(f'entities/arxiv-{VID}.md'))
        finally:
            f.close()

    def test_each_crash_stage_recovers_exactly_once(self):
        for stage in ('after_basis','after_journal','after_page','after_index','after_log','after_receipt','after_state'):
            with self.subTest(stage=stage):
                f = Fixture()
                try:
                    def crash(current):
                        if current == stage:
                            raise RuntimeError(stage)
                    with self.assertRaisesRegex(RuntimeError,stage):
                        self.publisher().publish(f.ctx,f.bundle,now=NOW,hook=crash)
                    result = self.publisher().publish(f.ctx,f.bundle,now=NOW)
                    self.assertEqual(result['status'],'published_draft')
                    before = {str(p.relative_to(f.root)):p.read_bytes() for p in f.root.rglob('*') if p.is_file()}
                    self.assertEqual(self.publisher().publish(f.ctx,f.bundle,now=NOW)['status'],'noop')
                    after = {str(p.relative_to(f.root)):p.read_bytes() for p in f.root.rglob('*') if p.is_file()}
                    self.assertEqual(before,after)
                    self.assertEqual(f.fs.read('log.md').count(b'<!-- publication-event:'),1)
                    self.assertEqual(len(g.decode(f.fs.read(STATE))['cost_events']),1)
                finally:
                    f.close()

    def test_noop_preserves_later_unrelated_state_index_log(self):
        p = self.publisher()
        p.publish(self.f.ctx,self.f.bundle,now=NOW)
        state = g.decode(self.f.fs.read(STATE))
        other = copy.deepcopy(self.f.state['items'][0])
        other.update(version_id='2610.00002v1', failure_count=1, status='retryable_failed')
        state['items'].append(other)
        state['last_run'] = '_meta/runs/wiki/later-run'
        self.f.put(STATE,g.encoded(state))
        self.f.put('concepts/later.md',b'Synthetic unrelated knowledge.\n')
        index = self.f.fs.read('index.md').replace(b'Total pages: 2',b'Total pages: 3')
        index = index.replace(b'## Concepts\n',b'## Concepts\n\n- [[concepts/later]]\n')
        self.f.put('index.md',index)
        self.f.put('log.md',self.f.fs.read('log.md')+b'\nLater unrelated event.\n')
        before = {str(x.relative_to(self.f.root)):x.read_bytes() for x in self.f.root.rglob('*') if x.is_file()}
        self.assertEqual(p.publish(self.f.ctx,self.f.bundle,now=NOW)['status'],'noop')
        after = {str(x.relative_to(self.f.root)):x.read_bytes() for x in self.f.root.rglob('*') if x.is_file()}
        self.assertEqual(before,after)

    def test_rehashed_journal_tampering_cannot_reconstruct(self):
        changes = [lambda p: p['targets'][0].update(path='entities/injected.md'),
                   lambda p: p['targets'][0].update(after_image='Injected reviewed output'),
                   lambda p: p['receipt'].update(human_review_ref='invented'),
                   lambda p: p['state_after']['items'][0].update(reason='tampered'),
                   lambda p: p['index'].update(after_header='Last updated: 2026-10-01 | Total pages: 999'),
                   lambda p: p.update(role='pilot'),
                   lambda p: p['log'].update(event='forged event')]
        for n,mutate in enumerate(changes):
            with self.subTest(case=n):
                f = Fixture()
                try:
                    def crash(stage):
                        if stage == 'after_journal':
                            raise RuntimeError('stop')
                    with self.assertRaises(RuntimeError):
                        self.publisher().publish(f.ctx,f.bundle,now=NOW,hook=crash)
                    path = f.prefix+'-publish-journal.json'
                    journal = g.read_journal(f.fs,path)
                    mutate(journal)
                    g.write_journal(f.fs,journal,f.fs.read(path))
                    before = {str(x.relative_to(f.root)):x.read_bytes() for x in f.root.rglob('*') if x.is_file()}
                    with self.assertRaisesRegex(ValueError,'reconstruction'):
                        self.publisher().publish(f.ctx,f.bundle,now=NOW)
                    after = {str(x.relative_to(f.root)):x.read_bytes() for x in f.root.rglob('*') if x.is_file()}
                    self.assertEqual(before,after)
                finally:
                    f.close()

    def test_edited_outputs_or_state_are_never_noop(self):
        for target in ('page','receipt','state','index','log'):
            with self.subTest(target=target):
                f = Fixture()
                try:
                    answer = self.publisher().publish(f.ctx,f.bundle,now=NOW)
                    if target == 'page':
                        f.put(f'entities/arxiv-{VID}.md',b'User edit, reviewed.\n')
                    elif target == 'receipt':
                        f.put(answer['receipt_ref'],b'{}\n')
                    elif target == 'state':
                        state = g.decode(f.fs.read(STATE))
                        state['items'][0]['failure_count'] += 1
                        f.put(STATE,g.encoded(state))
                    elif target == 'index':
                        f.put('index.md',f.fs.read('index.md').replace(f'[[entities/arxiv-{VID}]]'.encode(),b'Edited'))
                    else:
                        f.put('log.md',f.fs.read('log.md')+f'<!-- publication-event:{g.read_journal(f.fs,answer["journal_path"])["transaction_id"]} -->'.encode())
                    before = {str(x.relative_to(f.root)):x.read_bytes() for x in f.root.rglob('*') if x.is_file()}
                    with self.assertRaises(ValueError):
                        self.publisher().publish(f.ctx,f.bundle,now=NOW)
                    after = {str(x.relative_to(f.root)):x.read_bytes() for x in f.root.rglob('*') if x.is_file()}
                    self.assertEqual(before,after)
                finally:
                    f.close()

    def test_snapshot_drift_and_descriptor_drift_refuse_before_writes(self):
        for target in ('source','metadata','policy','approval','wiki','descriptor'):
            with self.subTest(target=target):
                f = Fixture()
                try:
                    paths = dict(source=f.ctx['item']['source_path'],metadata=f.ctx['item']['metadata_path'],
                                 policy='_meta/automation.json',approval=f.ctx['approval_ref'],wiki='concepts/synthetic.md',
                                 descriptor=f.prefix+'-review.json')
                    path = paths[target]
                    f.put(path,f.fs.read(path)+b'\n')
                    with self.assertRaises(ValueError):
                        self.publisher().publish(f.ctx,f.bundle,now=NOW)
                    self.assertFalse((f.root / (f.prefix+'-publication-basis.json')).exists())
                    self.assertFalse((f.root / f'entities/arxiv-{VID}.md').exists())
                finally:
                    f.close()

    def test_busy_lock_is_not_stolen(self):
        lock = self.f.root / g.LOCK
        lock.mkdir()
        (lock / 'owner.json').write_bytes(b'other owner')
        result = self.publisher().publish(self.f.ctx,self.f.bundle,now=NOW)
        self.assertEqual(result['status'],'skipped_busy')
        self.assertEqual((lock / 'owner.json').read_bytes(),b'other owner')

    def test_lock_ownership_is_checked_at_each_stage(self):
        def change(stage):
            if stage == 'after_page':
                self.f.put(g.LOCK+'/owner.json',b'successor owner')
        with self.assertRaisesRegex(ValueError,'owner changed'):
            self.publisher().publish(self.f.ctx,self.f.bundle,now=NOW,hook=change)
        self.assertEqual(self.f.fs.read(g.LOCK+'/owner.json'),b'successor owner')
        self.assertNotIn(b'<!-- publication-event:',self.f.fs.read('log.md'))

    def test_other_unknown_journal_blocks(self):
        self.f.put('_meta/runs/wiki/foreign/journal.json',b'{}\n')
        with self.assertRaisesRegex(ValueError,'unrecognized journal'):
            self.publisher().publish(self.f.ctx,self.f.bundle,now=NOW)
        self.assertFalse((self.f.root / f'entities/arxiv-{VID}.md').exists())

    def test_existing_page_not_overwritten(self):
        path = f'entities/arxiv-{VID}.md'
        self.f.put(path,b'User reviewed existing content.\n')
        with self.assertRaisesRegex(ValueError,'never overwrite'):
            self.publisher().publish(self.f.ctx,self.f.bundle,now=NOW)
        self.assertEqual(self.f.fs.read(path),b'User reviewed existing content.\n')

    def test_html_publishes_enabled_draft_with_real_helpers(self):
        p = self.publisher()
        before_log = self.f.fs.read('log.md')
        answer = p.publish(self.f.ctx, self.f.bundle, now=NOW)
        self.assertEqual(answer['status'], 'published_draft')
        page = self.f.fs.read(f'entities/arxiv-{VID}.md').decode()
        self.assertIn('status: "draft"', page)
        self.assertIn('last_reviewed: null', page)
        state = g.decode(self.f.fs.read(STATE))
        g.schema_validate(self.f.ctx['schema'], state, 'compilation')
        self.assertTrue(state['enabled'])
        self.assertEqual(state['items'][0]['status'], 'published_draft')
        self.assertEqual(state['cost_events'][-1]['role'], 'daily_compile')
        self.assertIsNone(state['cost_events'][-1]['charged_usd'])
        self.assertEqual(state['cost_events'][-1]['status'], 'unknown')
        self.assertEqual(self.f.fs.read('log.md')[:len(before_log)], before_log)
        receipt = g.decode(self.f.fs.read(answer['receipt_ref']))
        self.assertEqual(receipt['output_refs'], answer['output_refs'])
        self.assertIsNone(receipt['human_review_ref'])
        self.assertGreater(self.f.guard_calls, 0)
        self.assertEqual(g.read_journal(self.f.fs, answer['journal_path'])['status'], 'committed')
        self.assertFalse((self.f.root / g.LOCK).exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
