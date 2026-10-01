"""Policy repair regressions; metadata only, no paper reads or model calls."""
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[4]


def load(path):
    return json.loads((ROOT / path).read_text())


class PolicyAlignmentTests(unittest.TestCase):
    def test_all_four_contract_instances(self):
        schema = load('_meta/automation-contracts.schema.json')
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for path in ('_meta/automation.json', '_meta/state/compilation.json',
                     '_meta/state/feedback.json', '_meta/state/research-review.json'):
            with self.subTest(path=path):
                errors = list(validator.iter_errors(load(path)))
                self.assertFalse(errors, '\n'.join(error.message for error in errors))

    def test_active_document_revisions(self):
        for path in ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md',
                     '_meta/STATE-CONTRACTS.md', '_meta/QUERY-FEEDBACK.md',
                     '_meta/RESEARCH-REVIEW.md', '_meta/RESEARCH-PROFILE.md'):
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                self.assertIn('pkm-html-knowledge/v2', text)
                self.assertIn('pkm-contracts/v2', text)
                self.assertNotIn('pkm-html-knowledge/v1', text)
                self.assertNotIn('pkm-contracts/v1', text)

    def test_prompt_revisions_match_both_schema_and_files(self):
        auto = load('_meta/automation.json')
        schema = load('_meta/automation-contracts.schema.json')
        jobs = schema['$defs']['automation']['properties']['jobs']['properties']
        for name, job in auto['jobs'].items():
            with self.subTest(name=name):
                title = (ROOT / job['prompt_path']).read_text().splitlines()[0]
                match = re.search(r'(?:wiki-compile|research-review)/v\d+', title)
                assert match is not None, title
                actual = match.group(0)
                self.assertEqual(job['prompt_revision'], actual)
                self.assertEqual(jobs[name]['properties']['prompt_revision']['const'], actual)

    def test_cost_never_blocks_compilation(self):
        budget = load('_meta/automation.json')['budget']
        self.assertEqual(budget['cost_policy'], 'no_cost_cap')
        for key in ('pilot_total', 'daily_compile_per_run', 'daily_compile_per_kst_day',
                    'research_review_per_run'):
            self.assertIsNone(budget[key])
        self.assertEqual(budget['unknown_cost_action'], 'record_unknown_continue')
        self.assertFalse(budget['accounting_required_for_execution'])
        self.assertFalse(budget['hard_stop_required_for_execution'])
        agents = (ROOT / 'AGENTS.md').read_text()
        self.assertIn('no_cost_cap', agents)
        self.assertNotIn('실제 계측·강제 차단 검증 전 호출', agents)
        self.assertNotIn('파일럿 전체 US$5', agents)
        automation = (ROOT / '_meta/AUTOMATION.md').read_text()
        self.assertNotIn('비용/문맥 한도에 닿으면', automation)
        self.assertNotIn('이미지/자산/PDF 요청·미검증 예산', automation)

    def test_unreserved_cost_events_accept_unknown_and_observed_costs(self):
        schema = load('_meta/automation-contracts.schema.json')
        for definition in ('compilation', 'research_review'):
            event_schema = schema['$defs'][definition]['properties']['cost_events']['items']
            validator = Draft202012Validator(event_schema, format_checker=FormatChecker())
            for charged in (None, 25.0):
                event = dict(event_id='synthetic-cost-event', run_id='synthetic-test',
                             role='pilot', scope_id='synthetic',
                             created_at='2026-09-30T09:00:00+00:00', kst_day='2026-09-30',
                             status='unknown' if charged is None else 'settled',
                             reserved_usd=None, charged_usd=charged,
                             usage_receipt='_meta/runs/wiki/synthetic-test/usage.json')
                with self.subTest(definition=definition, charged=charged):
                    self.assertFalse(list(validator.iter_errors(event)))

    def test_scope_and_schedule_remain_restricted(self):
        auto = load('_meta/automation.json')
        self.assertFalse(auto['enabled'])
        self.assertTrue(auto['phase_authorizations']['P2'])
        for phase in ('P3', 'P4', 'P5', 'P6'):
            self.assertFalse(auto['phase_authorizations'][phase])
        self.assertFalse(auto['registration_authorized'])
        self.assertFalse(auto['activation_authorized'])
        self.assertEqual(auto['model'], {'provider': 'codex-lb', 'model': 'gpt-6-astra',
                                        'reasoning_effort': 'xhigh', 'fallback_allowed': False})
        for field in ('pdf_content', 'images', 'external_assets', 'automatic_chat_capture',
                      'secrets_or_sensitive_personal_data', 'external_novelty_search'):
            self.assertFalse(auto['transfer'][field])
        for job in auto['jobs'].values():
            self.assertFalse(job['enabled'])
            self.assertIsNone(job['cron_id'])
        self.assertEqual(auto['pilot_candidates'], ['2609.30830v1', '2609.31358v1'])

    def test_nonpilot_states_are_only_version_migrated(self):
        before = ROOT / '_meta/runs/wiki/20260930T090330Z-p2-repair/before'
        for rel in ('_meta/state/feedback.json', '_meta/state/research-review.json'):
            original = json.loads((before / rel).read_text())
            actual = load(rel)
            original['policy_revision'] = 'pkm-html-knowledge/v2'
            original['contract_revision'] = 'pkm-contracts/v2'
            self.assertEqual(actual, original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
