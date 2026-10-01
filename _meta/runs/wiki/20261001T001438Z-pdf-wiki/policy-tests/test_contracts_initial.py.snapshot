"""Synthetic policy-only tests. Never read source bodies or call a provider."""
import copy
import json
import os
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

RUN = Path(__file__).resolve().parent.parent
ROOT = RUN.parents[3]
SCHEMA_PATH = Path(os.environ.get('POLICY_SCHEMA', str(RUN / 'policy-staging/_meta/automation-contracts.schema.json')))
POLICY = 'pkm-html-pdf-text-knowledge/v3'
CONTRACT = 'pkm-contracts/v3'
PDF_READING = {
    'mode': 'embedded_text_only', 'library': 'pypdf', 'environment': '.venv-pdf-reader',
    'pdf_binary_transfer': False, 'images': False, 'ocr': False, 'external_assets': False,
    'persistent_extraction': False, 'page_citation': 'physical_1_based',
}

def request(fmt='pdf'):
    return {
        'schema': 'pkm-compile-request/v3', 'policy_revision': POLICY,
        'contract_revision': CONTRACT, 'provider': 'codex-lb',
        'model': 'gpt-6-astra', 'reasoning_effort': 'xhigh',
        'fallback_allowed': False, 'source_format': fmt,
        'source_path': 'raw/articles/synthetic/arxiv-2601.00001v1/source.' + fmt,
        'source_sha256': 'a' * 64, 'source_approval_id': 'synthetic-approval-not-real',
        'phase_execution_approved': True,
        'phase_approval_ref': '_meta/runs/wiki/synthetic/approval.json',
        'images': False, 'external_assets': False, 'pdf_analysis': fmt == 'pdf',
        'input_mode': 'embedded_text_only' if fmt == 'pdf' else 'html_direct_text',
        'pdf_reading': copy.deepcopy(PDF_READING) if fmt == 'pdf' else None,
        'ocr': False, 'pdf_binary_transfer': False, 'persistent_extraction': False,
        'cost_policy': 'no_cost_cap',
        'cost_waiver_ref': '_meta/runs/wiki/20260929T064035Z-p2-cost-waiver/approval.json',
    }

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def accepts(self, value):
        errors = list(self.validator.iter_errors(value))
        self.assertFalse(errors, '\n'.join(str(e)[:600] for e in errors))

    def rejects(self, value):
        self.assertTrue(list(self.validator.iter_errors(value)), 'Forbidden shape was accepted')

    def test_approved_v3_pdf_text_request(self):
        self.accepts(request())

if __name__ == '__main__':
    unittest.main(verbosity=2)
