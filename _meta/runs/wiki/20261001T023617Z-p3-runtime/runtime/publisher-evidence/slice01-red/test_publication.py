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
        anchor = source + ('#S1' if fmt == 'html' else '#page=1')
        claim = dict(id='C01', kind='author_report', statement='A bounded result is reported.',
                     conditions='Synthetic controlled experiment', anchor=anchor,
                     quote='Synthetic controlled experiment supports a bounded result.')
        document = dict(title='Synthetic paper', summary='A bounded synthetic result.', version_id=VID,
                        main_text_complete=True, read_scope=[anchor], unread_scope=['Figures not reviewed'],
                        limitations=['No independent reproduction'], claims=[claim],
                        markdown_body=f'# Synthetic paper\n\nVersion {VID}; text reviewed, figures unread.\n\nC01: A bounded result is reported. [source]({anchor})\n\n[[concepts/synthetic]]\n')
        result = dict(schema='pkm-p3-attempt-result/v1', document=document, version_id=VID,
                      **{k:item[k] for k in ('source_path','source_sha256','source_bytes','metadata_path','metadata_sha256')},
                      policy_revision=POLICY, contract_revision=CONTRACT, policy_sha256=self.ctx['policy_sha256'],
                      prompt_revision=PROMPT, prompt_sha256=self.ctx['prompt_sha256'], approval_ref=approval,
                      approval_sha256=self.ctx['approval_sha256'], requested_scope=SCOPE, **MODEL,
                      response_model=MODEL['model'], approved_route=ROUTE, completed=True,
                      response_status='completed', error=None, cost_usd=None)
        report = dict(schema='pkm-p3-verification/v1', passed=True, checks=[dict(name='synthetic evidence',ok=True)], document=document)
        review = dict(schema='pkm-p3-agent-review/v1', actor='agent', passed=True, human_review_ref=None,
                      version_id=VID, result_sha256=g.sha(g.encoded(result)), report_sha256=g.sha(g.encoded(report)),
                      source_sha256=item['source_sha256'], requested_scope=SCOPE, model=MODEL, route=ROUTE,
                      reviewed_claim_ids=['C01'], claims=[dict(id='C01', anchor=anchor, quote_sha256=g.sha(claim['quote'].encode()),
                      verdict='supported', rationale='Synthetic test-only reviewer finding, not a live model result.')],
                      body_review=dict(verdict='supported', rationale='Synthetic test-only whole body finding.',
                                       markdown_body_sha256=g.sha(document['markdown_body'].encode())))
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
        for key, suffix in [('result','result'), ('report','verification'), ('review','agent-review')]:
            raw = g.encoded(self.bundle[key])
            path = self.prefix + '-' + suffix + '.json'
            self.put(path, raw)
            self.bundle['artifacts'][key] = dict(path=path, sha256=g.sha(raw))

    def close(self):
        self.tmp.cleanup()


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def publisher(self):
        self.assertTrue((HERE / 'publication.py').is_file(), 'P3 publisher implementation is missing')
        return importlib.import_module('publication')

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
