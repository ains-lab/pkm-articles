"""Preparation/read-only and synthetic boundary checks; NOT a P3 executor.

No network/provider initialization, live paper text reads, production state writes,
Cron registration, or policy relaxation. Existing P2 rejection is a P3 blocker,
not evidence that a daily end-to-end path succeeds.
"""
import copy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRIPTS = ROOT / '_meta/runs/wiki/20260929T083140Z-p2-resume'


def load_module(name):
    spec = importlib.util.spec_from_file_location('readiness_' + name.replace('.', '_'), SCRIPTS / name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    return json.loads(path.read_text())


class PreparationTests(unittest.TestCase):
    def test_preparation_is_not_execution_or_registration_permission(self):
        approval = read_json(HERE / 'approval.json')
        self.assertTrue(approval['preparation_approved'])
        for key in ('new_paper_generation_authorized', 'cron_registration_authorized',
                    'cron_activation_authorized', 'p2_human_content_review_completed'):
            self.assertFalse(approval[key])
        policy = read_json(ROOT / '_meta/automation.json')
        self.assertFalse(policy['enabled'])
        self.assertFalse(policy['phase_authorizations']['P3'])
        self.assertFalse(policy['registration_authorized'])
        self.assertFalse(policy['activation_authorized'])
        for job in policy['jobs'].values():
            self.assertFalse(job['enabled'])
            self.assertIsNone(job['cron_id'])

    def test_prepared_state_matches_existing_schema(self):
        schema = read_json(ROOT / '_meta/automation-contracts.schema.json')
        state = read_json(HERE / 'prepared-compilation-state.json')
        validator = Draft202012Validator(
            {'$defs': schema['$defs'], '$ref': '#/$defs/compilation'},
            format_checker=FormatChecker())
        validator.validate(state)

    def test_only_missing_metadata_items_are_appended(self):
        old = read_json(HERE / 'before/_meta/state/compilation.json')
        new = read_json(HERE / 'prepared-compilation-state.json')
        self.assertEqual(new['items'][:len(old['items'])], old['items'])
        self.assertEqual({k: v for k, v in old.items() if k != 'items'},
                         {k: v for k, v in new.items() if k != 'items'})
        self.assertEqual(len(new['items']), 20)
        added = new['items'][len(old['items']):]
        self.assertEqual(len(added), 10)
        for item in added:
            self.assertEqual(item['status'], 'blocked_approval')
            self.assertEqual(item['format'], 'html')
            self.assertEqual(item['read_scope'], [])
            self.assertEqual(item['unread_scope'], [])
            self.assertEqual(item['output_refs'], [])
            self.assertIsNone(item['work_key'])
            self.assertIsNone(item['receipt_ref'])
            self.assertEqual(item['failure_count'], 0)

    def test_inventory_ids_metadata_and_order_are_exact(self):
        inventory = read_json(HERE / 'preflight.json')['source_inventory']
        state = read_json(HERE / 'prepared-compilation-state.json')
        queue = read_json(HERE / 'backlog.json')
        self.assertEqual({x['version_id'] for x in state['items']},
                         {x['version_id'] for x in inventory})
        self.assertEqual(len({x['version_id'] for x in state['items']}), 20)
        expected = sorted((x for x in state['items'] if x['status'] == 'blocked_approval'),
                          key=lambda x: (datetime.fromisoformat(x['collected_at']), x['version_id']))
        self.assertEqual([x['version_id'] for x in queue['items']],
                         [x['version_id'] for x in expected])
        self.assertEqual(len(expected), 16)
        self.assertEqual(queue['selection_limit'], 5)
        self.assertFalse(queue['execution_authorized'])
        metadata = {x['version_id']: x for x in inventory}
        for item in state['items']:
            for key in ('source_path', 'source_sha256', 'source_bytes', 'metadata_path',
                        'metadata_sha256', 'collected_at', 'format'):
                self.assertEqual(item[key], metadata[item['version_id']][key])

    def test_pdfs_remain_unread_and_published_sources_are_not_queued(self):
        state = read_json(HERE / 'prepared-compilation-state.json')
        queue_ids = {x['version_id'] for x in read_json(HERE / 'backlog.json')['items']}
        pdfs = [x for x in state['items'] if x['format'] == 'pdf']
        published = [x for x in state['items'] if x['status'] == 'published_draft']
        self.assertEqual(len(pdfs), 2)
        self.assertEqual(len(published), 2)
        for item in pdfs:
            self.assertEqual(item['status'], 'blocked_policy')
            self.assertEqual(item['read_scope'], [])
            self.assertEqual(item['output_refs'], [])
        self.assertFalse(queue_ids & {x['version_id'] for x in pdfs + published})

    def test_real_compiler_refuses_nonpilot_before_read_or_client(self):
        compiler = load_module('compile-one.py')
        with tempfile.TemporaryDirectory(prefix='p3-synthetic-boundary-') as td:
            with mock.patch.object(compiler, 'read_bytes', side_effect=AssertionError('unexpected read')) as reader:
                factory = mock.Mock(side_effect=AssertionError('unexpected provider'))
                with self.assertRaisesRegex(compiler.Rejected, '^outside_p2$'):
                    compiler.compile_one(root=Path(td), run='_meta/runs/wiki/synthetic-p3',
                        vid='2609.30217v1', attempt='attempt1', instructions='instructions.txt',
                        stream=False, client_factory=factory)
                reader.assert_not_called()
                factory.assert_not_called()
                self.assertEqual(list(Path(td).iterdir()), [])

    def test_real_compiler_rejects_malformed_id_without_repair(self):
        compiler = load_module('compile-one.py')
        with mock.patch.object(compiler, 'read_bytes', side_effect=AssertionError('unexpected read')) as reader:
            with self.assertRaisesRegex(compiler.Rejected, '^invalid_id$'):
                compiler.preflight(ROOT, '_meta/runs/wiki/synthetic-p3', '2609.30217v01',
                                   'attempt1', 'instructions.txt', 10)
            reader.assert_not_called()

    def test_valid_p2_positive_control_reaches_only_fake_sdk(self):
        tests = load_module('test_compile_one.py')
        compiler = tests.load()
        with tempfile.TemporaryDirectory(prefix='p3-p2-positive-') as td:
            fixture = tests.Fixture(Path(td))
            client = tests.FakeClient()
            answer = compiler.compile_one(root=fixture.root, run=tests.RUN, vid=tests.VID,
                attempt='attempt1', instructions=fixture.instructions, timeout=10,
                stream=False, client_factory=lambda **kwargs: client)
            self.assertTrue(answer['completed'])
            self.assertEqual(len(client.calls), 1)
            self.assertTrue(client.closed)

    def test_enabled_daily_shape_does_not_bypass_p2_guard(self):
        tests = load_module('test_compile_one.py')
        compiler = tests.load()
        with tempfile.TemporaryDirectory(prefix='p3-p2-enabled-') as td:
            fixture = tests.Fixture(Path(td))
            fixture.policy['enabled'] = True
            fixture.policy['phase_authorizations']['P3'] = True
            fixture.put('_meta/automation.json', fixture.policy)
            factory = mock.Mock(side_effect=AssertionError('unexpected provider'))
            with self.assertRaisesRegex(compiler.Rejected, '^p2_not_authorized$'):
                compiler.compile_one(root=fixture.root, run=tests.RUN, vid=tests.VID,
                    attempt='attempt1', instructions=fixture.instructions, timeout=10,
                    stream=False, client_factory=factory)
            factory.assert_not_called()

    def test_request_schema_rejects_forbidden_inputs_but_is_not_authority(self):
        schema = read_json(ROOT / '_meta/automation-contracts.schema.json')
        definition = schema['$defs']['compile_request']
        validator = Draft202012Validator(definition, format_checker=FormatChecker())
        candidate = {k: v['const'] for k, v in definition['properties'].items() if 'const' in v}
        candidate.update(source_path='raw/SYNTHETIC-ONLY/source.html', source_sha256='0' * 64,
                         phase_approval_ref='_meta/runs/wiki/SYNTHETIC-NOT-AN-APPROVAL/approval.json')
        validator.validate(candidate)
        for key, invalid in [('source_format', 'pdf'), ('images', True), ('external_assets', True),
                             ('pdf_analysis', True), ('provider', 'unapproved'),
                             ('phase_execution_approved', False), ('reasoning_effort', 'high')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(candidate)
                changed[key] = invalid
                self.assertTrue(list(validator.iter_errors(changed)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
