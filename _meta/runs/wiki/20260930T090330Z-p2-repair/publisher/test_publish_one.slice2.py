"""Synthetic temporary-directory tests: no live publication or model calls.

REQUEST CONTRACT (all paths Wiki-root-relative, never symlinks):
--run _meta/runs/wiki/<run-id>, --attempt <name>-result.json (basename).
The request is <run>/<VID>/<name>-publication-request.json. Required exact keys:
 schema='pkm-publication-request/v1', version_id, requested_scope='P2 main-text complete',
 result={path,sha256}, approval={path,sha256}, policy={path,sha256,revision},
 prompt={path,sha256,revision}, source={path,sha256,metadata_path,metadata_sha256},
 output_path='entities/arxiv-<VID>.md', agent_review={path,sha256},
 consumed_wiki_refs=[{path,sha256,revision}].
The agent_review is a separate locally authored artifact, NOT a model boolean:
 schema='pkm-agent-evidence-review/v1', actor='agent', reviewer, reviewed_at,
 version_id, result_sha256, source_sha256, requested_scope, read_scope, unread_scope,
 evidence_scope=[original claim anchors], reviewed_claim_ids=[ALL claim IDs],
 claims=[{id,anchor,quote_sha256,verdict:'supported',rationale:nonempty string}].
The orchestrating agent must perform actual semantic checks before writing this
artifact/request. The publisher checks bindings, coverage and rationale presence;
it does not prove the rationale true. Pages remain draft/unreviewed, never human
reviewed. All fixtures below are explicit approved SYNTHETIC TEST ONLY metadata.
"""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from jsonschema import Draft202012Validator, FormatChecker
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRIPT = HERE / 'publish-one.py'
VID = '2609.31358v1'
RUN = '_meta/runs/wiki/synthetic-publisher'
NOW = datetime(2026, 9, 30, 3, tzinfo=timezone.utc)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def load_publisher():
    spec = importlib.util.spec_from_file_location('p2_publisher', SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fixture:
    def __init__(self, root):
        self.root = root
        self.vid = VID
        self.run = RUN
        self.attempt = 'attempt-result.json'
        for p in ['entities', 'concepts', 'comparisons', 'queries', '_meta/locks']:
            (root / p).mkdir(parents=True)
        for p in ['SCHEMA.md', '_meta/automation-contracts.schema.json',
                  '_meta/automation.json', '_meta/prompts/wiki-compile.md',
                  '_meta/AUTOMATION.md', '_meta/STATE-CONTRACTS.md', 'AGENTS.md']:
            self.put(p, (ROOT / p).read_bytes())
        # Root pin is intentionally live-root metadata; --root selects an isolated
        # test filesystem, without relaxing the real contract's const constraint.
        self.policy = self.get('_meta/automation.json')
        self.put('index.md', '# SYNTHETIC\n\n> Last updated: 2026-09-01 | Total pages: 99\n\n'
                 '## Entities — 논문별 요약·분석 / 모델·도구\n\n아직 작성된 페이지가 없다.\n\n'
                 '## Concepts — 개념\n\nUNRELATED CONCEPT CONTENT\n\n## Raw Sources\n\nRAW UNCHANGED\n')
        self.put('log.md', '# SYNTHETIC LOG ONLY\n')
        approval = json.loads((HERE / 'approval.json').read_text())
        approval['run_id'] = Path(RUN).name
        approval['confirmation'] = 'SYNTHETIC TEST ONLY: authorized draft publication and edit freeze'
        self.put(RUN + '/approval.json', approval)
        waiver = self.policy['approval_amendment_ref']
        self.put(waiver, json.loads((ROOT / waiver).read_text()))
        self.state = dict(schema='pkm-compilation-state/v1',
                          policy_revision=self.policy['policy_revision'],
                          contract_revision=self.policy['contract_revision'],
                          initialized_at=NOW.isoformat(), enabled=False, safety_block=False,
                          safety_block_reason=None, items=[], transactions=[], receipts=[],
                          cost_events=[], last_run=None)
        self.add_item(VID)

    def put(self, path, data):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            p.write_bytes(data)
        else:
            p.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False), encoding='utf8')

    def get(self, path):
        return json.loads((self.root / path).read_text())

    def ref(self, path, **extra):
        return dict(path=path, sha256=digest((self.root / path).read_bytes()), **extra)

    def add_item(self, vid):
        self.vid = vid
        self.source = f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html'
        self.metadata = self.source.replace('source.html', 'source.json')
        html = '<html><body><article>' + ''.join(
            f'<section id="S{i}"><h2>Synthetic section {i}</h2><p>SYNTHETIC evidence {i}.</p></section>'
            for i in range(1, 9)) + '</article></body></html>'
        self.put(self.source, html)
        sh = digest(html.encode())
        self.put(self.metadata, dict(schema='arxiv-html-source/v1', version_id=vid,
                 title='SYNTHETIC TEST ONLY', source='arxiv', owning_cron_id='4cff5b4f10ec',
                 html_file='source.html', html_sha256=sh, html_bytes=len(html.encode()),
                 source_url=f'https://arxiv.org/html/{vid}', final_url=f'https://arxiv.org/html/{vid}',
                 http_status=200, preprocessing=False, wiki_compiled=False))
        item = dict(source='arxiv', version_id=vid, format='html', source_path=self.source,
                    source_sha256=sh, source_bytes=len(html.encode()), metadata_path=self.metadata,
                    metadata_sha256=self.ref(self.metadata)['sha256'], collected_at=NOW.isoformat(),
                    status='ready_to_publish', reason='SYNTHETIC review fixture',
                    requested_scope='P2 main-text complete', read_scope=[], unread_scope=[],
                    resume_at=None, work_key=None, output_refs=[], receipt_ref=None,
                    failure_count=0, human_review=None)
        if (self.root / '_meta/state/compilation.json').exists():
            self.state = self.get('_meta/state/compilation.json')
        self.state['items'].append(item)
        self.put('_meta/state/compilation.json', self.state)
        self.doc = dict(title='SYNTHETIC: "quoted" \\ title', version_id=vid, main_text_complete=True,
                        read_scope=[f'S{i}' for i in range(1, 9)],
                        unread_scope=['figures unreviewed', 'equations unreviewed', 'appendices unreviewed'],
                        claims=[dict(id=f'C{i:02}', kind='author_report', anchor=f'S{i}',
                                     quote=f'SYNTHETIC evidence {i}.', statement=f'Synthetic claim {i}')
                                for i in range(1, 9)],
                        markdown_body='\n'.join(['# SYNTHETIC TEST ONLY', '## Method', '## Evaluation', '## Conclusion'] +
                                      [f'C{i:02}: SYNTHETIC evidence {i}.' for i in range(1, 9)] +
                                      ['SYNTHETIC explanatory line.'] * 85))
        self.result_path = f'{RUN}/{vid}/{self.attempt}'
        prompt = '_meta/prompts/wiki-compile.md'
        self.result = dict(completed=True, error=None, response_status='completed',
                           provider='codex-lb', model='gpt-6-astra', response_model='gpt-6-astra',
                           reasoning_effort='xhigh', source_sha256=sh, source_bytes=item['source_bytes'],
                           metadata_sha256=item['metadata_sha256'], policy_revision=self.policy['policy_revision'],
                           policy_sha256=self.ref('_meta/automation.json')['sha256'],
                           prompt_revision=self.policy['jobs']['daily_compile']['prompt_revision'],
                           prompt_sha256=self.ref(prompt)['sha256'], instructions_sha256='a' * 64,
                           approval_ref=RUN + '/approval.json', approval_sha256=self.ref(RUN + '/approval.json')['sha256'],
                           route_base_url='https://synthetic.invalid/v1', api_mode='responses',
                           cost_usd=None, cost_status='unobserved_not_zero', text=json.dumps(self.doc, ensure_ascii=False))
        self.prepare_request()

    def prepare_request(self):
        self.put(self.result_path, self.result)
        review_path = f'{RUN}/{self.vid}/attempt-agent-review.json'
        review = dict(schema='pkm-agent-evidence-review/v1', actor='agent',
                      reviewer='synthetic fixture author; NOT real semantic evidence', reviewed_at=NOW.isoformat(),
                      version_id=self.vid, result_sha256=self.ref(self.result_path)['sha256'],
                      source_sha256=self.result['source_sha256'], requested_scope='P2 main-text complete',
                      read_scope=self.doc['read_scope'], unread_scope=self.doc['unread_scope'],
                      evidence_scope=[c['anchor'] for c in self.doc['claims']],
                      reviewed_claim_ids=[c['id'] for c in self.doc['claims']],
                      claims=[dict(id=c['id'], anchor=c['anchor'], quote_sha256=digest(c['quote'].encode()),
                                   verdict='supported', rationale='SYNTHETIC: exact local claim/evidence fixture matches.')
                              for c in self.doc['claims']])
        self.put(review_path, review)
        self.request_path = f'{RUN}/{self.vid}/attempt-publication-request.json'
        request = dict(schema='pkm-publication-request/v1', version_id=self.vid,
                       requested_scope='P2 main-text complete', result=self.ref(self.result_path),
                       approval=self.ref(RUN + '/approval.json'),
                       policy=self.ref('_meta/automation.json', revision=self.policy['policy_revision']),
                       prompt=self.ref('_meta/prompts/wiki-compile.md', revision=self.result['prompt_revision']),
                       source=self.ref(self.source, metadata_path=self.metadata, metadata_sha256=self.ref(self.metadata)['sha256']),
                       output_path=f'entities/arxiv-{self.vid}.md', agent_review=self.ref(review_path),
                       consumed_wiki_refs=[])
        self.put(self.request_path, request)

    def tree(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}


class EntrypointTests(unittest.TestCase):
    def test_help_is_an_import_safe_cli_not_publication(self):
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, '-B', str(SCRIPT), '--help'],
                               cwd=td, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            for arg in ['--root', '--run', '--attempt']:
                self.assertIn(arg, p.stdout)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_import_does_not_read_arguments_or_publish(self):
        code = ('import importlib.util; '
                f's=importlib.util.spec_from_file_location("p", {str(SCRIPT)!r}); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                'assert callable(m.main)')
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, '-B', '-c', code], cwd=td,
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(list(Path(td).iterdir()), [])


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix='p2-publisher-SYNTHETIC-')
        self.addCleanup(self.td.cleanup)
        self.f = Fixture(Path(self.td.name))
        self.p = load_publisher()
        self.verifications = []
        # Structural verifier is a sibling maintained independently. These tests
        # isolate publisher transactions; a separate integration test uses the real sibling.
        def verifier(root, vid, result):
            self.verifications.append((Path(root) / '_meta/locks/collection.lock').is_dir())
            doc = json.loads(result['text'])
            ok = result['completed'] is True and result['response_status'] == 'completed' and doc['main_text_complete'] is True
            return dict(passed=ok, checks=[dict(check='synthetic-interface', ok=ok)], document=doc)
        self.mock = mock.patch.object(self.p, '_verify_result', verifier, create=True)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def publish(self, **kw):
        return self.p.publish(self.f.root, self.f.vid, self.f.run, self.f.attempt, _now=NOW, **kw)

    def test_happy_path_schema_actual_count_yaml_and_verifier_under_lock(self):
        result = self.publish()
        self.assertEqual(result['status'], 'published_draft')
        state = self.f.get('_meta/state/compilation.json')
        Draft202012Validator(self.f.get('_meta/automation-contracts.schema.json'), format_checker=FormatChecker()).validate(state)
        item = state['items'][0]
        self.assertEqual(item['status'], 'published_draft')
        self.assertEqual(set(item['output_refs'][0]), {'path', 'sha256', 'revision'})
        self.assertIsInstance(item['output_refs'][0]['revision'], str)
        page = (self.f.root / item['output_refs'][0]['path']).read_bytes()
        fm = yaml.safe_load(page.decode().split('---\n')[1])
        self.assertEqual(fm['title'], self.f.doc['title'])
        self.assertEqual(fm['status'], 'draft')
        self.assertEqual(fm['review_state'], 'unreviewed')
        self.assertIsNone(fm['last_reviewed'])
        self.assertEqual(fm['tags'], ['paper', 'llm-security', 'agent-security'])
        self.assertEqual(item['output_refs'][0]['sha256'], digest(page))
        idx = (self.f.root / 'index.md').read_text()
        self.assertIn('Total pages: 1', idx)
        self.assertIn(f'[[entities/arxiv-{VID}]]', idx)
        self.assertIn('RAW UNCHANGED', idx)
        self.assertTrue(any(self.verifications), self.verifications)
        self.assertFalse((self.f.root / '_meta/locks/collection.lock').exists())
        request = self.f.get(self.f.request_path)
        wk = dict(source='arxiv', version_id=VID, source_sha256=self.f.result['source_sha256'],
                  policy_revision=request['policy']['revision'], policy_sha256=request['policy']['sha256'],
                  prompt_revision=request['prompt']['revision'], prompt_sha256=request['prompt']['sha256'],
                  requested_scope=request['requested_scope'])
        self.assertEqual(item['work_key'], digest(json.dumps(wk, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()))
        receipt = self.f.get(item['receipt_ref'])
        self.assertEqual(receipt['work_key'], item['work_key'])
        self.assertIsNone(receipt['human_review_ref'])


if __name__ == '__main__':
    unittest.main()
