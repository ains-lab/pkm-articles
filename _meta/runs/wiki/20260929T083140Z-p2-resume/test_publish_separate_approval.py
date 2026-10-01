"""Synthetic delayed-publication approvals; no live paper/provider writes."""
from datetime import datetime, timezone
import copy
import importlib.util
from pathlib import Path
from typing import Any
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NOW = datetime(2026, 9, 30, 3, tzinfo=timezone.utc)


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), HERE / name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DelayedApprovalTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='p2-delayed-SYNTHETIC-')
        self.addCleanup(temp.cleanup)
        self.f = f = load('test_publish_one.py').Fixture(Path(temp.name))
        self.p = load('publish-one.py')
        f.put('_meta/COMPILATION.md', (ROOT / '_meta/COMPILATION.md').read_bytes())
        instructions = f.run + '/instructions.txt'
        f.put(instructions, 'SYNTHETIC generation instructions only')
        approval = f.get(f.run + '/approval.json')
        approval.update(schema='pkm-p2-run-approval/v1', actor='user', approved=True,
            phase='P2', scope='manual-html-direct-compile', wiki_root=str(f.root),
            fresh_run=True, operator_reviewed_prior_attempts=True,
            version_ids=f.policy['pilot_candidates'], max_attempts_per_item=2,
            approved_route=dict(base_url=f.result['route_base_url'], api_mode=f.result['api_mode']),
            policy_revision=f.result['policy_revision'], policy_sha256=f.result['policy_sha256'],
            prompt_revision=f.result['prompt_revision'], prompt_sha256=f.result['prompt_sha256'],
            instructions_path=instructions, instructions_sha256=f.ref(instructions)['sha256'],
            document_sha256={p: f.ref(p)['sha256'] for p in load('compile-one.py').DOCS},
            sources={f.vid: {k: f.result[k] for k in ('source_sha256', 'source_bytes', 'metadata_sha256')}},
            publication_edit_freeze_confirmed=False, validated_draft_publication_authorized=False)
        f.put(f.run + '/approval.json', approval)
        f.result.update(approval_sha256=f.ref(f.run + '/approval.json')['sha256'],
                        instructions_sha256=f.ref(instructions)['sha256'])
        f.prepare_request()
        req = f.get(f.request_path)
        self.approval_path = f.run + '/publication-approval.json'
        self.authorization = dict(schema='pkm-p2-publication-approval/v1', actor='user', approved=True,
            phase='P2', scope='publish-validated-staged-drafts', wiki_root=str(f.root),
            run_id=Path(f.run).name, version_ids=[f.vid], confirmed_at=NOW.isoformat(),
            user_request='SYNTHETIC: publish existing draft', confirmation='SYNTHETIC: edit freeze and publication confirmed',
            confirmation_scope='SYNTHETIC: selected reviewed result only; no generation',
            publication_edit_freeze_confirmed=True, validated_draft_publication_authorized=True,
            generation_approval=req['approval'],
            bindings={f.vid: {k: req[k] for k in ('result', 'agent_review', 'source', 'output_path')}})
        f.put(self.approval_path, self.authorization)
        req.update(schema='pkm-publication-request/v2', publication_approval=f.ref(self.approval_path))
        f.put(f.request_path, req)

    def test_delayed_approval_publishes_without_rewriting_generation(self):
        f = self.f
        protected = {p: (f.root / p).read_bytes() for p in
                     (f.run + '/approval.json', f.result_path, f.source, f.metadata)}
        result = self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)
        self.assertEqual(result['status'], 'published_draft')
        for path, original in protected.items():
            self.assertEqual((f.root / path).read_bytes(), original)
        state = f.get('_meta/state/compilation.json')
        receipt = f.get(state['receipts'][0])
        journal = f.get(state['transactions'][0]['journal_path'])['plan']
        self.assertEqual(journal['approval_refs'], [f.ref(f.run + '/approval.json'), f.ref(self.approval_path)])
        self.assertEqual(receipt['actual_input_hashes'][self.approval_path], f.ref(self.approval_path)['sha256'])
        after = f.tree()
        self.assertEqual(self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)['status'], 'noop')
        self.assertEqual(f.tree(), after)

    def test_missing_later_approval_remains_blocked(self):
        f = self.f
        req = f.get(f.request_path)
        req.pop('publication_approval')
        req['schema'] = 'pkm-publication-request/v1'
        f.put(f.request_path, req)
        before = f.tree()
        with self.assertRaisesRegex(ValueError, 'publication approval/freeze missing'):
            self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)
        self.assertEqual(f.tree(), before)

    def test_invalid_later_authorities_are_rejected_before_writes(self):
        f = self.f
        cases = [
            (('publication_edit_freeze_confirmed',), False),
            (('validated_draft_publication_authorized',), False),
            (('approved',), 1), (('actor',), 'agent'), (('phase',), 'P3'),
            (('scope',), 'manual-html-direct-compile'),
            (('wiki_root',), '/tmp/wrong-root'), (('run_id',), 'another-run'),
            (('version_ids',), ['2609.30830v1']),
            (('confirmed_at',), '2026-09-30T03:00:00'),
            (('confirmation',), ' '), (('unknown_field',), True),
            (('generation_approval', 'sha256'), '0' * 64),
            (('bindings', f.vid, 'result', 'sha256'), '0' * 64),
            (('bindings', f.vid, 'agent_review', 'sha256'), '0' * 64),
            (('bindings', f.vid, 'source', 'sha256'), '0' * 64),
            (('bindings', f.vid, 'output_path'), 'entities/wrong.md'),
        ]
        for path, value in cases:
            with self.subTest(path=path):
                authority = copy.deepcopy(self.authorization)
                target: Any = authority
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                f.put(self.approval_path, authority)
                req = f.get(f.request_path)
                req['publication_approval'] = f.ref(self.approval_path)
                f.put(f.request_path, req)
                before = f.tree()
                with self.assertRaises(ValueError):
                    self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)
                self.assertEqual(f.tree(), before)

    def test_generation_bytes_cannot_be_reapproved_after_tampering(self):
        f = self.f
        original = f.get(f.run + '/approval.json')
        original['publication_edit_freeze_confirmed'] = True
        f.put(f.run + '/approval.json', original)
        req = f.get(f.request_path)
        req['approval'] = f.ref(f.run + '/approval.json')
        authority = copy.deepcopy(self.authorization)
        authority['generation_approval'] = req['approval']
        f.put(self.approval_path, authority)
        req['publication_approval'] = f.ref(self.approval_path)
        f.put(f.request_path, req)
        before = f.tree()
        with self.assertRaisesRegex(ValueError, 'result binding conflict: approval_sha256'):
            self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)
        self.assertEqual(f.tree(), before)

    def test_later_approval_is_rechecked_under_lock(self):
        f = self.f
        before = {p: (f.root / p).read_bytes() for p in ('index.md', 'log.md', '_meta/state/compilation.json')}
        def hook(stage):
            if stage == 'before_lock':
                authority = copy.deepcopy(self.authorization)
                authority['validated_draft_publication_authorized'] = False
                f.put(self.approval_path, authority)
        with self.assertRaisesRegex(ValueError, 'reference hash conflict'):
            self.p.publish(f.root, f.vid, f.run, f.attempt, _hook=hook, _now=NOW)
        for path, original in before.items():
            self.assertEqual((f.root / path).read_bytes(), original)
        self.assertEqual(list((f.root / 'entities').glob('*.md')), [])
        self.assertFalse((f.root / '_meta/locks/collection.lock').exists())

    def test_separate_approval_recovers_a_partial_transaction(self):
        f = self.f
        def hook(stage):
            if stage == 'after_page':
                raise RuntimeError('SYNTHETIC interruption')
        with self.assertRaisesRegex(RuntimeError, 'SYNTHETIC interruption'):
            self.p.publish(f.root, f.vid, f.run, f.attempt, _hook=hook, _now=NOW)
        result = self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)
        self.assertEqual(result['status'], 'published_draft')
        self.assertEqual((f.root / 'log.md').read_text().count('<!-- publication-event:'), 1)
        self.assertEqual(self.p.publish(f.root, f.vid, f.run, f.attempt, _now=NOW)['status'], 'noop')


if __name__ == '__main__':
    unittest.main(verbosity=2)
