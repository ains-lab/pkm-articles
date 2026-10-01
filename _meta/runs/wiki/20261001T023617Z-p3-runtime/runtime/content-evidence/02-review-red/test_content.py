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


if __name__ == '__main__':
    unittest.main()
