"""Synthetic SDK boundary -> real producer/verifier/publisher integration.

No network, auth imports or live paper reads. The copied schema root is rebound
ONLY inside TemporaryDirectory because a real compiler pins its exact root.
"""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / '_meta/runs/wiki/20260929T083140Z-p2-resume'


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), SCRIPTS / name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CrossComponentTests(unittest.TestCase):
    def test_explicit_response_error_cannot_pass_the_verifier(self):
        with tempfile.TemporaryDirectory(prefix='p2-chain-SYNTHETIC-') as td:
            f = load('test_publish_one.py').Fixture(Path(td))
            result = dict(f.result, response_error={'present': True})
            self.assertFalse(load('verify-one.py').verify_result(f.root, f.vid, result)['passed'])

    def test_generated_result_reaches_verified_publication_and_noop(self):
        for cost, publication_authorized in ((None, True), (25.0, True), (None, False)):
            with self.subTest(cost=cost, publication_authorized=publication_authorized), tempfile.TemporaryDirectory(prefix='p2-chain-SYNTHETIC-') as td:
                fixture_module = load('test_publish_one.py')
                compiler = load('compile-one.py')
                verifier = load('verify-one.py')
                publisher = load('publish-one.py')
                f = fixture_module.Fixture(Path(td))
                req = f.get(f.request_path)
                review_path = req['agent_review']['path']
                review = f.get(review_path)
                # Replace fixture-only fake result with output of the real producer.
                for path in (f.result_path, f.request_path, review_path):
                    (f.root / path).unlink()
                (f.root / f.run / f.vid).rmdir()
                f.put('_meta/COMPILATION.md', (ROOT / '_meta/COMPILATION.md').read_bytes())
                f.policy['wiki_root'] = str(f.root)
                f.put('_meta/automation.json', f.policy)
                schema = f.get('_meta/automation-contracts.schema.json')
                schema['$defs']['automation']['properties']['wiki_root']['const'] = str(f.root)
                f.put('_meta/automation-contracts.schema.json', schema)
                metadata = f.get(f.metadata)
                metadata.update(offline_assets_bundled=False, charset='utf-8')
                f.put(f.metadata, metadata)
                state = f.get('_meta/state/compilation.json')
                item = state['items'][0]
                item.update(status='queued', metadata_sha256=f.ref(f.metadata)['sha256'])
                f.put('_meta/state/compilation.json', state)
                instructions = f.run + '/instructions.txt'
                f.put(instructions, (SCRIPTS / 'compile-instructions.txt').read_bytes())
                approval = f.get(f.run + '/approval.json')
                approval.update(schema='pkm-p2-run-approval/v1', actor='user', approved=True,
                    phase='P2', scope='manual-html-direct-compile', wiki_root=str(f.root),
                    fresh_run=True, operator_reviewed_prior_attempts=True,
                    version_ids=f.policy['pilot_candidates'], max_attempts_per_item=2,
                    approved_route={'base_url': 'https://synthetic.invalid/v1', 'api_mode': 'responses'},
                    policy_revision=f.policy['policy_revision'], policy_sha256=f.ref('_meta/automation.json')['sha256'],
                    prompt_revision='wiki-compile/v2', prompt_sha256=f.ref('_meta/prompts/wiki-compile.md')['sha256'],
                    instructions_path=instructions, instructions_sha256=f.ref(instructions)['sha256'],
                    document_sha256={p: f.ref(p)['sha256'] for p in compiler.DOCS},
                    sources={f.vid: {k: item[k] for k in ('source_sha256', 'source_bytes', 'metadata_sha256')}})
                approval.pop('versions', None)
                approval['validated_draft_publication_authorized'] = publication_authorized
                f.put(f.run + '/approval.json', approval)
                calls = []
                closed = []
                class SyntheticClient:
                    def __init__(self):
                        self.responses = self
                    def create(self, **kw):
                        calls.append(kw)
                        return SimpleNamespace(status='completed', model='gpt-6-astra',
                            error=None, incomplete_details=None, output_text=json.dumps(f.doc),
                            usage=None, cost_usd=cost)
                    def close(self):
                        closed.append(True)
                result = compiler.compile_one(root=f.root, run=f.run, vid=f.vid,
                    attempt='attempt', instructions=instructions, stream=False,
                    client_factory=lambda **kw: SyntheticClient())
                self.assertTrue(result['completed'])
                self.assertEqual(len(calls), 1)
                self.assertEqual(closed, [True])
                self.assertEqual(calls[0]['input'][0]['content'][0]['text'], (f.root / f.source).read_text())
                checked = verifier.verify_result(f.root, f.vid, result)
                self.assertTrue(checked['passed'], checked['checks'])
                result_hash = f.ref(f.result_path)['sha256']
                # Authored synthetic review: each claim is supported by the matching
                # explicit synthetic section, not a real model-review claim.
                review.update(result_sha256=result_hash)
                f.put(review_path, review)
                req.update(result=f.ref(f.result_path), approval=f.ref(f.run + '/approval.json'),
                    policy=f.ref('_meta/automation.json', revision='pkm-html-knowledge/v2'),
                    source=f.ref(f.source, metadata_path=f.metadata, metadata_sha256=f.ref(f.metadata)['sha256']),
                    agent_review=f.ref(review_path))
                f.put(f.request_path, req)
                now = datetime(2026, 9, 30, 3, tzinfo=timezone.utc)
                if not publication_authorized:
                    before = f.tree()
                    with self.assertRaisesRegex(ValueError, 'publication approval/freeze missing'):
                        publisher.publish(f.root, f.vid, f.run, f.attempt, _now=now)
                    self.assertEqual(f.tree(), before)
                    continue
                published = publisher.publish(f.root, f.vid, f.run, f.attempt, _now=now)
                self.assertEqual(published['status'], 'published_draft')
                after = f.tree()
                self.assertEqual(publisher.publish(f.root, f.vid, f.run, f.attempt, _now=now)['status'], 'noop')
                self.assertEqual(f.tree(), after)
                self.assertEqual(f.ref(f.result_path)['sha256'], result_hash)
                final = f.get('_meta/state/compilation.json')
                self.assertEqual(final['items'][0]['status'], 'published_draft')
                self.assertEqual(final['cost_events'][0]['charged_usd'], cost)
                self.assertEqual((f.root / 'log.md').read_text().count('<!-- publication-event:'), 1)
                self.assertFalse((f.root / '_meta/locks/collection.lock').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
