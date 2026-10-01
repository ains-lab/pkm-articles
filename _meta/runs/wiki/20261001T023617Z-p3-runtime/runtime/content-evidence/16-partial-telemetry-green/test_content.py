"""Synthetic-only executable contract tests for P3 content; no network/credentials."""
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RUN = str(HERE.parent.relative_to(ROOT))
VID = '9910.00001v1'
SOURCE = f'raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html'
QUOTE = 'The synthetic method succeeded in two controlled cases.'
UNREAD = ['모든 그림·이미지 및 이미지 전용 내용: 미검토',
          '수식·레이아웃·표 구조: 텍스트 추출 모호성, 시각 검증 미수행']
HTML = ('<!doctype html><html><head><title>Synthetic evidence</title></head><body>'
        '<article id="paper"><section id="S1"><h1>Synthetic evidence</h1><p>' + QUOTE +
        '</p><p>Only controlled cases were tested. SOURCE_ONLY_TAIL_NEVER_PERSIST.</p>'
        '</section></article></body></html>').encode()


def load_content():
    if not (HERE / 'content.py').is_file():
        raise AssertionError('P3 content.process implementation is missing')
    import content
    return content


def document(source=SOURCE, anchor='S1'):
    return dict(title='Synthetic evidence', summary='통제된 합성 사례의 결과와 한계.',
        version_id=VID, main_text_complete=True, read_scope=[anchor],
        unread_scope=list(UNREAD), limitations=['합성 사례이며 일반화와 재현은 미검증.'],
        claims=[dict(id='C01', kind='author_report', statement='두 통제 사례에서 성공했다고 보고한다.',
                     conditions='통제된 합성 사례에 한함.', anchor=anchor, quote=QUOTE)],
        markdown_body=f'# Synthetic evidence\n버전: {VID}; 읽은 범위: {anchor}\n'
            f'C01 저자 보고: 두 통제 사례에서 성공. 조건: 통제된 합성 사례. ^[{source}#{anchor}]\n'
            + '\n'.join(UNREAD) + '\n한계: 일반화와 재현은 미검증.\n')


def review_payload(doc):
    import p3_common as common
    return dict(claims=[dict(id=c['id'], verdict='supported', rationale='원문은 통제된 두 사례만 보고하며 조건이 보존됨.',
                            quote_sha256=common.sha(c['quote'].encode())) for c in doc['claims']],
        body_verdict='supported', body_rationale='본문 전체가 원문과 조건을 보존하고 시각적 미검토를 명시함.',
        main_text_complete=True, coverage_rationale='제공된 전체 텍스트와 읽기 범위를 대조함.')


def response(payload):
    return types.SimpleNamespace(status='completed', model='gpt-6-astra',
        incomplete_details=None, error=None, output_text=json.dumps(payload, ensure_ascii=False),
        usage=None, cost_usd=None)


class FakeFactory:
    def __init__(self, doc=None, review=None):
        self.doc = doc if doc is not None else document()
        self.review = review
        self.calls, self.factories, self.closed = [], [], []

    def __call__(self, **kwargs):
        self.factories.append(kwargs)
        owner = self
        number = len(self.factories)
        class Client:
            def __init__(self):
                self.responses = self
            def create(self, **request):
                owner.calls.append(request)
                answer = owner.doc if len(owner.calls) == 1 else (owner.review or review_payload(owner.doc))
                if isinstance(answer, BaseException):
                    raise answer
                return answer if hasattr(answer, 'output_text') else response(answer)
            def close(self):
                owner.closed.append(number)
        return Client()


class Fixture:
    def __init__(self):
        import p3_common as c
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-content-', dir=HERE)
        self.root = Path(self.temp.name)
        self.c = c
        self.reads, self.guards = [], []
        self.source = SOURCE
        self.write(SOURCE, HTML)
        meta_path = SOURCE.replace('source.html', 'source.json')
        metadata = dict(schema='arxiv-html-source/v1', source='arxiv', version_id=VID,
            title='Synthetic evidence', html_file='source.html', html_sha256=c.sha(HTML),
            html_bytes=len(HTML), charset='utf-8')
        self.write(meta_path, c.encoded(metadata))
        prefix = f'{RUN}/items/{VID}/attempt1'
        self.write(prefix + '-reservation.json', c.encoded({'synthetic': True}))
        fs = c.helper('publish').Files(self.root)
        original_read = fs.read
        def read(path, missing=False):
            self.reads.append(path)
            return original_read(path, missing)
        fs.read = read
        self.ctx = dict(root=self.root, fs=fs, run=RUN,
            item=dict(version_id=VID, format='html', source='arxiv', source_path=SOURCE,
                source_sha256=c.sha(HTML), source_bytes=len(HTML), metadata_path=meta_path,
                metadata_sha256=c.sha(c.encoded(metadata)), status='reading'),
            metadata=metadata, synthetic=True, auto={}, schema={}, snapshots={},
            approval_ref=RUN+'/approval.json', approval_sha256='a'*64,
            policy_sha256='b'*64, prompt_sha256=c.sha(b'Synthetic trusted compile prompt'),
            prompt='Synthetic trusted compile prompt', model=copy.deepcopy(c.MODEL),
            route=copy.deepcopy(c.ROUTE), requested_scope=c.SCOPE, wiki=[], artifact_prefix=prefix,
            guard=lambda: self.guards.append(len(self.reads)))

    def write(self, path, data):
        full = self.root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)

    def use_pdf(self, texts=(QUOTE, 'Second synthetic page. PDF_TAIL_NEVER_PERSIST.')):
        site = ROOT / '.venv-pdf-reader/lib/python3.12/site-packages'
        sys.path.insert(0, str(site))
        import pypdf
        from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
        writer = pypdf.PdfWriter()
        for text in texts:
            page = writer.add_blank_page(width=612, height=792)
            if text:
                font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                    NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
                page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):
                    DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
                stream = DecodedStreamObject()
                escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                stream.set_data(f'BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET'.encode('ascii'))
                page[NameObject('/Contents')] = writer._add_object(stream)
        out = io.BytesIO(); writer.write(out); writer.close()
        data = out.getvalue()
        source = SOURCE.replace('source.html', 'source.pdf')
        self.write(source, data)
        item = self.ctx['item']
        item.update(format='pdf', source_path=source, source_sha256=self.c.sha(data), source_bytes=len(data))
        metadata = dict(schema='arxiv-pdf-source/v1', source='arxiv', version_id=VID,
            title='Synthetic evidence', pdf_file='source.pdf', pdf_sha256=self.c.sha(data), pdf_bytes=len(data))
        self.ctx['metadata'] = metadata
        self.write(item['metadata_path'], self.c.encoded(metadata))
        item['metadata_sha256'] = self.c.sha(self.c.encoded(metadata))
        return pypdf

    def close(self):
        self.temp.cleanup()


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.content = load_content()
        self.fixture = Fixture()
        self.addCleanup(self.fixture.close)
        self.ctx = self.fixture.ctx

    def test_html_generation_separate_review_and_bound_artifacts(self):
        f = FakeFactory()
        bundle = self.content.process(self.ctx, client_factory=f)
        self.assertEqual(bundle['status'], 'ready_to_publish')
        self.assertTrue(bundle['report']['passed'])
        self.assertTrue(bundle['review']['passed'])
        self.assertEqual(bundle['result']['document'], bundle['report']['document'])
        self.assertEqual(len(f.factories), 2)
        self.assertEqual(f.closed, [1, 2])
        self.assertEqual(len(f.calls), 2)
        for factory in f.factories:
            self.assertEqual(factory['approved_route'], self.ctx['route'])
            self.assertEqual(factory['max_retries'], 0)
        for request in f.calls:
            self.assertEqual(request['model'], 'gpt-6-astra')
            self.assertEqual(request['reasoning'], {'effort': 'xhigh'})
            self.assertIs(request['store'], False)
            self.assertIs(request['stream'], False)
            self.assertEqual(request['tools'], [])
        self.assertIn('independent', f.calls[1]['instructions'].lower())
        self.assertIn('markdown_body', json.dumps(f.calls[1]['input']))
        self.assertIn('SOURCE_ONLY_TAIL_NEVER_PERSIST', json.dumps(f.calls[1]['input']))
        self.assertIsNone(bundle['result']['cost_usd'])
        self.assertIsNone(bundle['review']['human_review_ref'])
        self.assertEqual(bundle['review']['claim_ids'], ['C01'])
        self.assertGreaterEqual(len(self.fixture.guards), 5)
        self.assertEqual(self.fixture.guards[0], 0)
        for name, descriptor in bundle['artifacts'].items():
            data = self.ctx['fs'].read(descriptor['path'])
            self.assertEqual(self.fixture.c.sha(data), descriptor['sha256'])
            self.assertEqual(json.loads(data), bundle[name])
            self.assertNotIn(b'SOURCE_ONLY_TAIL_NEVER_PERSIST', data)
        self.assertEqual(bundle['review']['result_sha256'], bundle['artifacts']['result']['sha256'])
        self.assertEqual(bundle['review']['report_sha256'], bundle['artifacts']['report']['sha256'])

    def test_semantic_review_requires_all_claims_and_body(self):
        review = review_payload(document())
        review['claims'] = []
        f = FakeFactory(review=review)
        bundle = self.content.process(self.ctx, client_factory=f)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertFalse(bundle['review']['passed'])
        self.assertFalse(bundle['review']['body_supported'])
        self.assertEqual(len(f.calls), 2)

    def test_mechanical_contract_rejects_uncited_unbounded_or_untrusted_documents(self):
        cases = {}
        d = document(); d['claims'][0]['quote'] = 'x' * 401; cases['long_quote'] = d
        d = document(); d['claims'][0]['conditions'] = ''; cases['missing_conditions'] = d
        d = document(); d['claims'].append(copy.deepcopy(d['claims'][0])); cases['duplicate_id'] = d
        d = document(); d['claims'][0]['kind'] = 'human_verified'; cases['authority_kind'] = d
        d = document(); d['markdown_body'] = '<!-- '+d['markdown_body']+' -->'; cases['hidden_citation'] = d
        d = document(); d['markdown_body'] += '\n[[concepts/fabricated]]'; cases['fabricated_link'] = d
        d = document(); d['markdown_body'] += '\n[leak](https://outside.invalid)'; cases['external_link'] = d
        d = document(); d['markdown_body'] = '---\nstatus: reviewed\n---\n'+d['markdown_body']; cases['frontmatter'] = d
        d = document(); d['unread_scope'] = ['none']; cases['missing_visual_disclosure'] = d
        d = document(); d['read_scope'] = ['fabricated']; cases['fabricated_scope'] = d
        d = document(); d['full_extract'] = 'SOURCE_ONLY_TAIL_NEVER_PERSIST' * 1000; cases['extra_dump'] = d
        for name, doc in cases.items():
            with self.subTest(name=name):
                fixture = Fixture()
                try:
                    fake = FakeFactory(doc=doc)
                    bundle = self.content.process(fixture.ctx, client_factory=fake)
                    self.assertEqual(bundle['status'], 'blocked_review')
                    self.assertFalse(bundle['report']['passed'])
                    self.assertEqual(len(fake.calls), 1)
                    for descriptor in bundle['artifacts'].values():
                        self.assertNotIn(b'SOURCE_ONLY_TAIL_NEVER_PERSIST', fixture.ctx['fs'].read(descriptor['path']))
                finally:
                    fixture.close()

    def test_pdf_embedded_text_physical_pages_and_text_only_requests(self):
        pdf = self.fixture.use_pdf()
        doc = document(source=self.ctx['item']['source_path'], anchor='page=1')
        doc['read_scope'] = ['page=1', 'page=2']
        doc['markdown_body'] += '\n읽은 범위: page=1, page=2\n'
        f = FakeFactory(doc=doc)
        bundle = self.content.process(self.ctx, client_factory=f, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'ready_to_publish')
        telemetry = bundle['result']['telemetry']
        self.assertEqual(telemetry['page_count'], 2)
        self.assertEqual(telemetry['read_scope'], ['page=1', 'page=2'])
        self.assertEqual(telemetry['blank_pages'], [])
        self.assertEqual(telemetry['pypdf_version'], '6.19.0')
        self.assertEqual([p['extracted_chars'] for p in telemetry['pages']], [len(QUOTE), len('Second synthetic page. PDF_TAIL_NEVER_PERSIST.')])
        for request in f.calls:
            for block in request['input'][0]['content']:
                self.assertEqual(block['type'], 'input_text')
                self.assertNotIn('%PDF-', block['text'])
                self.assertIn('PDF_TAIL_NEVER_PERSIST', block['text'])
        for desc in bundle['artifacts'].values():
            self.assertNotIn(b'PDF_TAIL_NEVER_PERSIST', self.ctx['fs'].read(desc['path']))

    def test_every_claim_line_requires_unescaped_citation(self):
        cases = {}
        d = document(); d['markdown_body'] += '\nC01 다시 인용 없는 주장.\n'; cases['repeat_uncited'] = d
        d = document(); d['markdown_body'] = d['markdown_body'].replace('^[', r'\^['); cases['escaped_caret'] = d
        d = document(); d['markdown_body'] = d['markdown_body'].replace('^[', '^' + r'\['); cases['escaped_bracket'] = d
        for name, doc in cases.items():
            with self.subTest(name=name):
                fixture = Fixture()
                try:
                    fake = FakeFactory(doc=doc)
                    bundle = self.content.process(fixture.ctx, client_factory=fake)
                    self.assertEqual(bundle['status'], 'blocked_review')
                    self.assertEqual(len(fake.calls), 1)
                finally:
                    fixture.close()

    def test_malformed_reference_and_unresolved_links_are_rejected(self):
        cases = ['[reference][ref]', '[collapsed][]', '[shortcut]', '[bad](missing',
                 '^[' + SOURCE + '#S1', '[bad](<missing>)', '[bad](missing "title")',
                 '[bad](mailto:test@example.invalid)', '[[concepts/known]']
        for link in cases:
            with self.subTest(link=link):
                fixture = Fixture()
                try:
                    doc = document(); doc['markdown_body'] += '\n' + link
                    fake = FakeFactory(doc=doc)
                    bundle = self.content.process(fixture.ctx, client_factory=fake)
                    self.assertEqual(bundle['status'], 'blocked_review')
                    self.assertEqual(len(fake.calls), 1)
                finally:
                    fixture.close()

    def test_allowed_inline_source_and_committed_wiki_links(self):
        self.ctx['wiki'] = [dict(path='concepts/known.md', text='# Known\n', sha256='a'*64)]
        doc = document()
        doc['markdown_body'] = doc['markdown_body'].replace(f'^[{SOURCE}#S1]', f'[근거]({SOURCE}#S1)')
        doc['markdown_body'] += '\n[[concepts/known#known|관련 개념]]\n'
        bundle = self.content.process(self.ctx, client_factory=FakeFactory(doc=doc))
        self.assertEqual(bundle['status'], 'ready_to_publish')

    def test_bom_cannot_hide_frontmatter(self):
        for prefix in ('\ufeff---\nstatus: reviewed\n---\n', '\ufeff+++\nstatus = "reviewed"\n+++\n'):
            with self.subTest(prefix=prefix):
                fixture = Fixture()
                try:
                    doc = document(); doc['markdown_body'] = prefix + doc['markdown_body']
                    fake = FakeFactory(doc=doc)
                    bundle = self.content.process(fixture.ctx, client_factory=fake)
                    self.assertEqual(bundle['status'], 'blocked_review')
                    self.assertEqual(len(fake.calls), 1)
                finally:
                    fixture.close()

    def test_pdf_subset_cannot_claim_main_text_complete(self):
        pdf = self.fixture.use_pdf()
        fake = FakeFactory(doc=document(self.ctx['item']['source_path'], 'page=1'))
        bundle = self.content.process(self.ctx, client_factory=fake, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'blocked_review')
        self.assertEqual(bundle['result']['telemetry']['read_scope'], ['page=1', 'page=2'])
        self.assertIn({'check': 'pdf_read_scope_complete', 'ok': False}, bundle['report']['checks'])
        self.assertEqual(len(fake.calls), 1)

    def test_blank_pdf_is_partial_without_model_requests(self):
        pdf = self.fixture.use_pdf((QUOTE, ''))
        f = FakeFactory(doc=document(self.ctx['item']['source_path'], 'page=1'))
        bundle = self.content.process(self.ctx, client_factory=f, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'partial')
        self.assertEqual(f.factories, [])
        self.assertFalse(bundle['result']['completed'])
        self.assertFalse(bundle['report']['passed'])
        self.assertFalse(bundle['review']['passed'])
        self.assertEqual(bundle['result']['telemetry']['page_count'], 2)
        self.assertEqual(bundle['result']['telemetry']['blank_pages'], [2])
        self.assertEqual(bundle['result']['telemetry']['read_scope'], ['page=1'])
        self.assertIn('page=2: 빈 텍스트, 미독', bundle['result']['telemetry']['required_unread_scope'])

    def test_request_failures_are_bounded_durable_and_never_forge_review(self):
        for stage, error, status in [('generation', ConnectionError('SOURCE_SECRET_NEVER_LOG'), 'unknown'),
                                     ('generation', ConnectionResetError('SOURCE_SECRET_NEVER_LOG'), 'unknown'),
                                     ('review', ConnectionError('SOURCE_SECRET_NEVER_LOG'), 'unknown'),
                                     ('review', TimeoutError('SOURCE_SECRET_NEVER_LOG'), 'unknown')]:
            with self.subTest(stage=stage):
                fixture = Fixture()
                try:
                    f = FakeFactory(doc=error) if stage == 'generation' else FakeFactory(review=error)
                    bundle = self.content.process(fixture.ctx, client_factory=f)
                    self.assertEqual(bundle['status'], status)
                    self.assertFalse(bundle['review']['passed'])
                    self.assertEqual(len(f.closed), 1 if stage == 'generation' else 2)
                    self.assertEqual(len(f.calls), len(f.closed))
                    self.assertIsNone(bundle['result']['cost_usd'])
                    for desc in bundle['artifacts'].values():
                        data = fixture.ctx['fs'].read(desc['path'])
                        self.assertNotIn(b'SOURCE_SECRET_NEVER_LOG', data)
                        self.assertNotIn(b'SOURCE_ONLY_TAIL_NEVER_PERSIST', data)
                finally:
                    fixture.close()

    def test_factory_failure_is_precall_and_route_rejection_never_retryable(self):
        legacy = self.fixture.c.helper('compile')
        cases = [(ConnectionError('SOURCE_SECRET_NEVER_LOG'), 'retryable_failed'),
                 (TimeoutError('SOURCE_SECRET_NEVER_LOG'), 'retryable_failed'),
                 (legacy.Rejected('runtime_route_mismatch'), 'blocked_policy')]
        for error, expected in cases:
            with self.subTest(error=type(error).__name__):
                fixture = Fixture()
                try:
                    calls = []
                    def factory(**kwargs):
                        calls.append(kwargs)
                        raise error
                    bundle = self.content.process(fixture.ctx, client_factory=factory)
                    self.assertEqual(bundle['status'], expected)
                    self.assertEqual(len(calls), 1)
                    self.assertFalse(bundle['result']['completed'])
                    self.assertFalse(bundle['review']['passed'])
                    self.assertNotIn('SOURCE_SECRET_NEVER_LOG', json.dumps(bundle))
                finally:
                    fixture.close()

    def test_repeated_attempt_rejected_before_second_source_read_or_client(self):
        first = FakeFactory()
        self.content.process(self.ctx, client_factory=first)
        count_before = self.fixture.reads.count(SOURCE)
        second = FakeFactory()
        with self.assertRaises(ValueError):
            self.content.process(self.ctx, client_factory=second)
        self.assertEqual(second.calls, [])
        self.assertEqual(second.factories, [])
        self.assertEqual(self.fixture.reads.count(SOURCE), count_before)

    def test_expiry_during_result_encoding_stops_before_write(self):
        now = [0.0]
        c = self.fixture.c
        original = c.encoded
        def encode(value):
            data = original(value)
            if isinstance(value, dict) and value.get('schema') == 'pkm-p3-content-result/v1':
                now[0] = 11.0
            return data
        f = FakeFactory()
        with patch.object(c, 'encoded', side_effect=encode):
            with self.assertRaises(TimeoutError):
                self.content.process(self.ctx, client_factory=f, deadline=10.0, clock=lambda: now[0])
        self.assertEqual(len(f.calls), 1)
        self.assertIsNone(self.ctx['fs'].read(self.ctx['artifact_prefix']+'-result.json', missing=True))

    def test_pdf_midread_failure_preserves_observed_and_unread_telemetry(self):
        self.fixture.use_pdf((QUOTE, 'Second.', 'Third.'))
        calls = []
        closed = []
        class Page:
            def __init__(self, number):
                self.number = number
            def extract_text(self):
                calls.append(self.number)
                if self.number == 2:
                    raise ValueError('SOURCE_SECRET_NEVER_LOG')
                return QUOTE
        class Reader:
            is_encrypted = False
            pages = [Page(1), Page(2), Page(3)]
            def __init__(self, *args, **kwargs):
                pass
            def close(self):
                closed.append(True)
        pdf = types.SimpleNamespace(PdfReader=Reader, __version__='synthetic-fault')
        fake = FakeFactory()
        bundle = self.content.process(self.ctx, client_factory=fake, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'partial')
        self.assertEqual(calls, [1, 2])
        self.assertEqual(closed, [True])
        self.assertEqual(fake.factories, [])
        telemetry = bundle['result']['telemetry']
        self.assertEqual(telemetry['page_count'], 3)
        self.assertEqual(telemetry['requested_pages'], [1, 2, 3])
        self.assertEqual(telemetry['read_scope'], ['page=1'])
        self.assertEqual(telemetry['unread_pages'], [2, 3])
        self.assertEqual([p['extracted_chars'] for p in telemetry['pages']], [len(QUOTE)])
        self.assertFalse(telemetry['main_text_complete_eligible'])
        for n in (2, 3):
            self.assertIn(f'page={n}: 텍스트 읽기 실패 또는 미시도, 미독', telemetry['required_unread_scope'])
        saved = json.loads(self.ctx['fs'].read(bundle['artifacts']['result']['path']))
        self.assertEqual(saved['telemetry'], telemetry)
        self.assertNotIn('SOURCE_SECRET_NEVER_LOG', json.dumps(bundle))
        self.assertNotIn(QUOTE, json.dumps(saved))

    def test_corrupt_pdf_is_partial_with_unknown_page_count_no_model(self):
        pdf = self.fixture.use_pdf()
        data = b'%PDF-1.7\nsynthetic-corrupt\n%%EOF\n'
        item = self.ctx['item']
        self.fixture.write(item['source_path'], data)
        item.update(source_sha256=self.fixture.c.sha(data), source_bytes=len(data))
        f = FakeFactory()
        bundle = self.content.process(self.ctx, client_factory=f, pdf_module=pdf)
        self.assertEqual(bundle['status'], 'partial')
        self.assertEqual(len(f.calls), 0)
        self.assertIsNone(bundle['result']['telemetry']['page_count'])
        self.assertEqual(bundle['result']['telemetry']['read_scope'], [])
        self.assertIsNotNone(bundle['result']['telemetry']['error'])
        self.assertFalse(bundle['result']['telemetry']['main_text_complete_eligible'])


if __name__ == '__main__':
    unittest.main()
