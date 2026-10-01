"""Synthetic schema regression for automated completion (no live writes)."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent

class AutomatedCompletionSchemaTests(unittest.TestCase):
    def setUp(self):
        schema = json.loads((HERE / 'policy-staged/_meta/automation-contracts.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema['$defs']['compilation'], format_checker=FormatChecker())
        self.state = dict(schema='pkm-compilation-state/v1', policy_revision='pkm-html-pdf-text-knowledge/v3',
                          contract_revision='pkm-contracts/v3', initialized_at='2026-10-01T00:00:00+00:00',
                          enabled=True, safety_block=False, safety_block_reason=None, items=[],
                          transactions=[], receipts=[], cost_events=[], last_run=None)
        self.item = dict(source='arxiv', version_id='2601.00001v1', format='html',
                         source_path='raw/articles/4cff5b4f10ec/arxiv-2601.00001v1/source.html',
                         source_sha256='a'*64, source_bytes=100,
                         metadata_path='raw/articles/4cff5b4f10ec/arxiv-2601.00001v1/source.json',
                         metadata_sha256='b'*64, collected_at='2026-10-01T00:00:00+00:00',
                         status='published_auto_verified', reason='synthetic automatic validation receipt',
                         requested_scope='P3 main-text complete', read_scope=['S1'], unread_scope=['Images not reviewed'],
                         resume_at=None, work_key='c'*64,
                         output_refs=[dict(path='entities/arxiv-2601.00001v1.md', sha256='d'*64, revision='1')],
                         receipt_ref='_meta/runs/wiki/synthetic/receipt.json', failure_count=0, human_review=None)

    def test_automatic_completion_requires_no_human_review(self):
        self.state['items'] = [self.item]
        self.validator.validate(self.state)

    def test_old_published_draft_is_still_valid(self):
        self.item['status'] = 'published_draft'
        self.state['items'] = [self.item]
        self.validator.validate(self.state)

    def test_each_completion_state_requires_publication_evidence(self):
        for status in ('published_auto_verified', 'published_draft'):
            for key, value in [('work_key', None), ('read_scope', []), ('output_refs', []), ('receipt_ref', None)]:
                with self.subTest(status=status, missing=key):
                    item = copy.deepcopy(self.item)
                    item.update(status=status)
                    item[key] = value
                    self.state['items'] = [item]
                    self.assertTrue(list(self.validator.iter_errors(self.state)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
