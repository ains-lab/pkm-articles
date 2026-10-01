"""Synthetic request-contract regressions, not evidence of real model compliance."""
import unittest
from typing import Any, cast

from test_content import FakeFactory, Fixture, HTML, VID, document, load_content, review_payload


class ContentContractTests(unittest.TestCase):
    def setUp(self):
        self.content = load_content()
        self.fixture = Fixture()
        self.addCleanup(self.fixture.close)
        self.ctx = cast(dict[str, Any], self.fixture.ctx)

    def generate(self, doc=None, **kwargs):
        fake = FakeFactory(doc=doc)
        bundle = cast(dict[str, Any], self.content.process(self.fixture.ctx, client_factory=fake, **kwargs))
        return fake, bundle

    def instructions(self, fake):
        return ' '.join(fake.calls[0]['instructions'].split())

    def test_visible_scope_contract_requires_exact_version_and_every_scope_token(self):
        # A parent anchor does not visibly disclose a separately declared child.
        doc: dict[str, Any] = document()
        doc['read_scope'].append('paper')
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual([x['check'] for x in bundle['report']['checks'] if not x['ok']],
                         ['version_scope_visible'])
        self.assertEqual(bundle['result']['document'], doc)
        self.assertIn(VID, doc['markdown_body'])
        self.assertEqual(bundle['review']['body_verdict'], 'not_reviewed')
        self.assertEqual(len(fake.calls), 1)
        instructions = self.instructions(fake)
        self.assertIn('Copy the exact supplied version_id into markdown_body as visible text', instructions)
        self.assertIn('Show every read_scope token verbatim in visible markdown_body', instructions)
        self.assertIn('JSON fields alone do not satisfy visible disclosure', instructions)

    def test_claim_scope_contract_requires_exact_claim_anchor_membership(self):
        doc: dict[str, Any] = document()
        doc['read_scope'] = ['paper']
        doc['markdown_body'] += '\n읽은 범위: paper\n'
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual([x['check'] for x in bundle['report']['checks'] if not x['ok']],
                         ['claim_scope_observed'])
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(len(fake.calls), 1)
        instructions = self.instructions(fake)
        self.assertIn('Every claim anchor must be an exact member of read_scope', instructions)
        self.assertIn('A parent section anchor does not substitute for a cited child anchor', instructions)
        self.assertIn('read_scope must contain unique observed nonempty-text locations', instructions)

    def test_repeated_claim_contract_requires_same_line_citation_every_time(self):
        doc: dict[str, Any] = document()
        doc['markdown_body'] += '\nC01 관련 해석도 통제된 사례에 한한다.\n'
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual([x['check'] for x in bundle['report']['checks'] if not x['ok']],
                         ['claims_cited'])
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(bundle['review']['body_verdict'], 'not_reviewed')
        self.assertEqual(len(fake.calls), 1)
        instructions = self.instructions(fake)
        self.assertIn('Every occurrence of a claim ID, including repeated mentions', instructions)
        self.assertIn('must have its matching ^[SOURCE_PATH#ANCHOR] on that same visible line', instructions)
        self.assertIn('Do not escape citation punctuation', instructions)
        self.assertIn('Claim IDs must be unique C followed by digits', instructions)
        self.assertIn('the visible body must contain all and only those claim IDs', instructions)

    def test_pdf_contract_requires_all_observed_physical_text_pages(self):
        pdf = self.fixture.use_pdf()
        doc = document(self.ctx['item']['source_path'], 'page=1')
        fake, bundle = self.generate(doc, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual([x['check'] for x in bundle['report']['checks'] if not x['ok']],
                         ['pdf_read_scope_complete'])
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(len(fake.calls), 1)
        instructions = self.instructions(fake)
        self.assertIn('For PDF, read_scope must equal telemetry.read_scope as a set', instructions)
        self.assertIn('include every physical 1-based page=N token, not only cited pages', instructions)

    def test_generation_contract_states_closed_bounded_schema(self):
        doc: dict[str, Any] = document()
        doc['source_dump'] = 'SYNTHETIC_DUMP_MUST_NOT_PERSIST'
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertIsNone(bundle['result']['document'])
        self.assertEqual(len(fake.calls), 1)
        for descriptor in bundle['artifacts'].values():
            self.assertNotIn(b'SYNTHETIC_DUMP_MUST_NOT_PERSIST', self.ctx['fs'].read(descriptor['path']))
        instructions = self.instructions(fake)
        for requirement in (
                'Use exactly the listed document and claim fields; no extra fields or source dumps',
                'All string fields must be nonempty',
                'title<=1000, summary<=2000, version_id<=40, markdown_body<=40000',
                'read_scope, unread_scope and limitations each contain 1..1000 strings of <=1000 chars',
                'claims contains 1..100 objects',
                'id<=16, kind<=40, statement<=2000, conditions<=2000, anchor<=400, quote<=400'):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, instructions)

    # Supplemental coverage of unchanged validators, not new RED evidence.
    def test_json_version_without_exact_body_version_stays_blocked(self):
        # Neutral synthetic path prevents the ID in a citation from masking omission.
        source = 'raw/articles/4cff5b4f10ec/synthetic-source/source.html'
        self.fixture.write(source, HTML)
        self.ctx['item']['source_path'] = source
        doc: dict[str, Any] = document(source)
        doc['markdown_body'] = doc['markdown_body'].replace(VID, 'v1')
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual([x['check'] for x in bundle['report']['checks'] if not x['ok']],
                         ['version_scope_visible'])
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(len(fake.calls), 1)

    def test_compliant_body_is_not_rewritten_and_reaches_independent_review(self):
        doc: dict[str, Any] = document()
        doc['read_scope'].append('paper')
        doc['markdown_body'] += '\n읽은 범위: paper\n' + doc['markdown_body'].splitlines()[2] + '\n'
        fake, bundle = self.generate(doc)
        self.assertEqual(bundle['status'], 'ready_to_publish')
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(len(fake.calls), 2)
        self.assertIn('independent semantic reviewer', fake.calls[1]['instructions'])
        self.assertIsNone(bundle['review']['human_review_ref'])

    def test_mechanically_compliant_body_still_requires_semantic_support(self):
        doc = document()
        decision = review_payload(doc)
        decision['body_verdict'] = 'unsupported'
        fake = FakeFactory(doc=doc, review=decision)
        bundle = cast(dict[str, Any], self.content.process(self.ctx, client_factory=fake))
        self.assertTrue(bundle['report']['passed'])
        self.assertFalse(bundle['review']['passed'])
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual(bundle['result']['document'], doc)
        self.assertEqual(len(fake.calls), 2)


if __name__ == '__main__':
    unittest.main()
