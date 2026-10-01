"""Metadata-only migration and adversarial v3 request tests; no PDF/provider IO."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker
import test_contracts as core
from test_contracts import request, PDF_READING, POLICY, CONTRACT, RUN

STAGE = RUN / 'policy-staging'
BEFORE = RUN / 'before'
TARGETS = {'2609.30614v1', '2609.30824v1'}
INSTANCE_PATHS = ['_meta/automation.json', '_meta/state/compilation.json',
                  '_meta/state/feedback.json', '_meta/state/research-review.json']


def load(base, rel):
    return json.loads((base / rel).read_text())


class Matrix(core.Contracts):
    def test_v3_html_request(self):
        self.accepts(request('html'))

    def test_pdf_published_state_shape_requires_real_evidence_semantically(self):
        # Explicit synthetic metadata, not an actual successful paper run.
        state = load(STAGE, '_meta/state/compilation.json')
        item = next(i for i in state['items'] if i['format'] == 'pdf')
        item.update(status='published_draft', reason='SYNTHETIC_SCHEMA_TEST_NOT_A_RUN',
                    requested_scope='synthetic page 1 text, partial', read_scope=['physical page 1'],
                    unread_scope=['images unread; synthetic remaining scope'], work_key='b' * 64,
                    output_refs=[{'path': 'entities/synthetic.md', 'sha256': 'c' * 64, 'revision': '1'}],
                    receipt_ref='_meta/runs/wiki/synthetic/receipt.json')
        self.accepts(state)
        for key, missing in [('receipt_ref', None), ('read_scope', []),
                             ('output_refs', []), ('work_key', None)]:
            with self.subTest(key=key):
                invalid = copy.deepcopy(state)
                next(i for i in invalid['items'] if i['format'] == 'pdf')[key] = missing
                self.rejects(invalid)

    def test_migration_exact_item_and_history_preservation(self):
        old = load(BEFORE, '_meta/state/compilation.json')
        new = load(STAGE, '_meta/state/compilation.json')
        expected = copy.deepcopy(old)
        expected.update(policy_revision=POLICY, contract_revision=CONTRACT)
        modified = []
        for item in expected['items']:
            if item['version_id'] in TARGETS:
                self.assertEqual(item['format'], 'pdf')
                item.update(status='blocked_approval', reason='pdf_text_policy_eligible_pending_execution_gate')
                modified.append(item['version_id'])
        self.assertEqual(set(modified), TARGETS)
        self.assertEqual(new, expected)
        for item in new['items']:
            if item['version_id'] in TARGETS:
                self.assertEqual(item['read_scope'], [])
                self.assertEqual(item['unread_scope'], [])
                self.assertEqual(item['output_refs'], [])
                self.assertIsNone(item['requested_scope'])
                self.assertIsNone(item['receipt_ref'])
                self.assertIsNone(item['work_key'])
                self.assertFalse(any('page' in k or 'attempt' in k for k in item))

    def test_feedback_research_only_outer_revisions_migrated(self):
        for rel in INSTANCE_PATHS[2:]:
            expected = load(BEFORE, rel)
            expected.update(policy_revision=POLICY, contract_revision=CONTRACT)
            self.assertEqual(load(STAGE, rel), expected)

    def test_policy_invariants(self):
        new = load(STAGE, '_meta/automation.json')
        old = load(BEFORE, '_meta/automation.json')
        self.assertFalse(new['enabled'])
        self.assertFalse(new['registration_authorized'])
        self.assertFalse(new['activation_authorized'])
        self.assertEqual(new['pdf_reading'], PDF_READING)
        self.assertTrue(new['transfer']['pdf_content'])
        self.assertEqual(new['budget'], old['budget'])
        self.assertEqual(new['model'], old['model'])
        self.assertEqual(new['collector'], old['collector'])
        self.assertEqual(new['approval'], old['approval'])
        self.assertEqual(new['approval_amendment_ref'], old['approval_amendment_ref'])
        for phase in ['P3', 'P4', 'P5', 'P6']:
            self.assertIs(new['phase_authorizations'][phase], False)
        for name, job in new['jobs'].items():
            self.assertIs(job['enabled'], False)
            self.assertIsNone(job['cron_id'])
            self.assertIsNone(job['registration_readback'])
            self.assertEqual(job['registration_status'], 'not_registered')
            expected = copy.deepcopy(old['jobs'][name])
            expected['prompt_revision'] = 'wiki-compile/v3' if name == 'daily_compile' else 'research-review/v3'
            self.assertEqual(job, expected)
        self.assertIsNone(load(STAGE, '_meta/state/research-review.json')['anchor_utc'])

    def test_frozen_v2_instances_remain_valid_on_frozen_schema(self):
        schema = load(BEFORE, '_meta/automation-contracts.schema.json')
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for rel in INSTANCE_PATHS:
            validator.validate(load(BEFORE, rel))

    def test_pdf_reading_const_schema_exact(self):
        self.assertEqual(self.schema['$defs']['pdf_reading']['const'], PDF_READING)

    def test_no_index_log_staged(self):
        self.assertFalse((STAGE / 'index.md').exists())
        self.assertFalse((STAGE / 'log.md').exists())

    def test_prompt_revisions(self):
        for stem in ['wiki-compile', 'research-review']:
            text = (STAGE / '_meta/prompts' / (stem + '.md')).read_text()
            self.assertIn(stem + '/v3', text)
            self.assertIn(POLICY, text)
            self.assertIn(CONTRACT, text)
            self.assertIn('collect-only', text)
            self.assertIn('legacy P2-v2', text)

    def test_docs_cover_pdf_boundaries(self):
        for rel in ['SCHEMA.md', 'README.md', '_meta/AUTOMATION.md', '_meta/COMPILATION.md',
                    '_meta/STATE-CONTRACTS.md', '_meta/P3-PREPARATION.md',
                    '_meta/prompts/wiki-compile.md', '_meta/prompts/research-review.md']:
            text = (STAGE / rel).read_text()
            for required in [POLICY, CONTRACT, 'embedded_text_only', 'source.pdf#page=N',
                             '1-based', 'blocked_approval', 'pdf_text_policy_eligible_pending_execution_gate',
                             'collect-only', 'no_cost_cap', 'legacy P2-v2']:
                self.assertIn(required, text, (rel, required))


def add_case(name, fn):
    fn.__name__ = 'test_' + name
    setattr(Matrix, fn.__name__, fn)


for rel in INSTANCE_PATHS:
    def positive(self, path=rel):
        self.accepts(load(STAGE, path))
    add_case('instance_' + Path(rel).stem, positive)

for fmt in ['html', 'pdf']:
    changes = {
        'bad_provider': ('provider', 'other'), 'bad_model': ('model', 'other'),
        'bad_reasoning': ('reasoning_effort', 'low'), 'fallback': ('fallback_allowed', True),
        'no_execution_approval': ('phase_execution_approved', False),
        'bad_policy': ('policy_revision', 'pkm-html-knowledge/v2'),
        'bad_contract': ('contract_revision', 'pkm-contracts/v2'),
        'images': ('images', True), 'assets': ('external_assets', True),
        'ocr': ('ocr', True), 'binary': ('pdf_binary_transfer', True),
        'persist': ('persistent_extraction', True), 'empty_approval': ('source_approval_id', ''),
        'wrong_analysis': ('pdf_analysis', fmt != 'pdf'),
        'absolute_path': ('source_path', '/tmp/source.' + fmt),
        'traversal': ('source_path', 'raw/articles/../source.' + fmt),
        'url_input': ('source_path', 'https://arxiv.org/pdf/2601.00001v1'),
        'wrong_extension': ('source_path', 'raw/articles/synthetic/source.' + ('html' if fmt == 'pdf' else 'pdf')),
        'bad_hash': ('source_sha256', 'not-a-hash'),
        'bad_mode': ('input_mode', 'multimodal'),
        'file_payload': ('input_file', {'filename': 'source.pdf', 'file_data': 'SYNTHETIC_NOT_REAL'}),
        'image_payload': ('input_image', 'SYNTHETIC_NOT_REAL'),
        'text_dump': ('persistent_text_path', '_meta/synthetic.txt'),
        'raw_body': ('pdf_bytes', 'SYNTHETIC_NOT_REAL'),
    }
    for label, (key, value) in changes.items():
        def negative(self, fmt=fmt, key=key, value=value):
            obj = request(fmt); obj[key] = value
            self.rejects(obj)
        add_case(fmt + '_' + label, negative)
    for key in request(fmt):
        def absent(self, fmt=fmt, key=key):
            obj = request(fmt); del obj[key]
            self.rejects(obj)
        add_case(fmt + '_missing_' + key, absent)

for key, value in PDF_READING.items():
    for action in ['missing', 'wrong']:
        def contract_shape(self, key=key, value=value, action=action):
            obj = request()
            if action == 'missing':
                del obj['pdf_reading'][key]
            else:
                obj['pdf_reading'][key] = True if value is False else 'FORBIDDEN'
            self.rejects(obj)
            auto = load(STAGE, '_meta/automation.json')
            auto['pdf_reading'] = obj['pdf_reading']
            self.rejects(auto)
        add_case('pdf_reading_' + action + '_' + key, contract_shape)

for label, value in [('null', None), ('empty', {}), ('extra', {**PDF_READING, 'unknown': False})]:
    def malformed(self, value=value):
        obj = request(); obj['pdf_reading'] = value
        self.rejects(obj)
    add_case('pdf_reading_' + label, malformed)

def html_pdf_shape(self):
    obj = request('html'); obj['pdf_reading'] = copy.deepcopy(PDF_READING)
    self.rejects(obj)
add_case('html_cannot_acquire_pdf_reading', html_pdf_shape)

if __name__ == '__main__':
    unittest.main(verbosity=2)
