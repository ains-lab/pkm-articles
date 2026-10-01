"""Staged automatic-publication contract; synthetic files/fake models only."""
import copy
from contextlib import redirect_stdout
import io
import json

import types
import unittest
from typing import Any
from unittest.mock import patch

import p3_common as C
import publication
import daily
from test_publication import Fixture as PublicationFixture, NOW, VID
from test_daily import Fixture as DailyFixture, APPROVAL, RUN
from test_integration import Model
from test_content import Fixture as ContentFixture

AUTO = 'published_auto_verified'
LEGACY = 'published_draft'


def allow_auto_schema(schema):
    """Future contract amendment in synthetic fixtures, never the live schema."""
    item = schema['$defs']['compilation']['properties']['items']['items']
    if AUTO not in item['properties']['status']['enum']:
        item['properties']['status']['enum'].append(AUTO)
    item['allOf'][0]['if']['properties']['status'] = {'enum': [LEGACY, AUTO]}
    return schema


class AutoPublicationFixture(PublicationFixture):
    ctx: Any
    bundle: Any
    state: Any

    def __init__(self, fmt='html'):
        super().__init__(fmt)
        allow_auto_schema(self.ctx['schema'])
        path = '_meta/automation-contracts.schema.json'
        self.put(path, C.encoded(self.ctx['schema']))
        self.ctx['snapshots'][path] = C.sha(self.fs.read(path))


class AutoDailyFixture(DailyFixture):
    def __init__(self):
        super().__init__()
        allow_auto_schema(self.schema)
        self.put('_meta/automation-contracts.schema.json', C.encoded(self.schema))
        self.sync()

    def kw(self) -> Any:
        return super().kw()


def bytes_at(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def legacy_publisher():
    """Execute unchanged old publisher only inside a synthetic root."""
    path = C.ROOT/'_meta/runs/wiki/20261001T023617Z-p3-runtime/runtime/publication.py'
    source = path.read_bytes()
    assert C.sha(source) == 'c660378062b7ad6fad28772c1a5d2bd6aba78bdd1314dd579ea11d11d5b68435'
    module = types.ModuleType('frozen_legacy_publication')
    module.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


class AutoPublicationTests(unittest.TestCase):
    def test_page_displays_automatic_verification_not_human_review(self):
        f = AutoPublicationFixture()
        self.addCleanup(f.close)
        publication.publish(f.ctx, f.bundle, now=NOW)
        page = f.fs.read(f'entities/arxiv-{VID}.md').decode()
        self.assertIn('자동 검증 완료', page)
        self.assertIn('인간 검토·도표 시각 검토·실험 재현을 뜻하지 않습니다.', page)
        self.assertIn(f.bundle['result']['document']['markdown_body'].rstrip(), page)

    def test_legacy_prepared_journal_is_not_applied_or_rewritten(self):
        f = AutoPublicationFixture()
        self.addCleanup(f.close)
        def crash(stage):
            if stage == 'after_journal':
                raise RuntimeError('legacy interruption')
        with self.assertRaisesRegex(RuntimeError, 'legacy interruption'):
            legacy_publisher().publish(f.ctx, f.bundle, now=NOW, hook=crash)
        before = bytes_at(f.root)
        with self.assertRaisesRegex(ValueError, 'reconstruction'):
            publication.publish(f.ctx, f.bundle, now=NOW)
        self.assertEqual(bytes_at(f.root), before)

    def test_both_terminal_statuses_require_bound_published_outputs(self):
        f = AutoPublicationFixture()
        self.addCleanup(f.close)
        publication.publish(f.ctx, f.bundle, now=NOW)
        state = C.decode(f.fs.read(C.STATE))
        for status in (AUTO, LEGACY):
            for field, value in [('work_key', None), ('read_scope', []),
                                 ('output_refs', []), ('receipt_ref', None)]:
                with self.subTest(status=status, missing=field):
                    invalid = copy.deepcopy(state)
                    invalid['items'][0].update(status=status, **{field: value})
                    with self.assertRaisesRegex(ValueError, 'schema compilation'):
                        C.helper('publish').schema_validate(f.ctx['schema'], invalid, 'compilation')

    def test_terminal_state_does_not_bypass_receipt_page_or_log_checks(self):
        for status in (AUTO, LEGACY):
            for target in ('page', 'receipt', 'journal', 'index', 'log'):
                with self.subTest(status=status, target=target):
                    f = AutoPublicationFixture()
                    self.addCleanup(f.close)
                    publisher = publication if status == AUTO else legacy_publisher()
                    result = publisher.publish(f.ctx, f.bundle, now=NOW)
                    state = C.decode(f.fs.read(C.STATE))
                    ctx = dict(f.ctx, approval={})
                    self.assertEqual(len(daily.published_context(ctx, state['items'])), 1)
                    paths = dict(page=f'entities/arxiv-{VID}.md', receipt=result['receipt_ref'],
                                 journal=result['journal_path'], index='index.md', log='log.md')
                    path = paths[target]
                    f.put(path, b'User-edited protected bytes.\n')
                    before = bytes_at(f.root)
                    with self.assertRaises(ValueError):
                        daily.published_context(ctx, state['items'])
                    with self.assertRaises(ValueError):
                        publication.publish(f.ctx, f.bundle, now=NOW)
                    self.assertEqual(bytes_at(f.root), before)

    def test_auto_publication_still_rejects_incomplete_or_unreviewed_evidence(self):
        changes = [lambda f: f.bundle['report'].update(passed=False),
                   lambda f: f.bundle['report']['checks'][0].update(ok=False),
                   lambda f: f.bundle['review'].update(passed=False),
                   lambda f: f.bundle['review'].update(human_review_ref='invented'),
                   lambda f: f.bundle['review'].update(claims=[]),
                   lambda f: f.bundle['review'].update(body_supported=False),
                   lambda f: f.bundle['review'].update(response_model='other'),
                   lambda f: f.bundle['result']['document'].update(main_text_complete=False),
                   lambda f: f.bundle['result'].update(model='other'),
                   lambda f: f.bundle['result'].update(route={}),
                   lambda f: f.bundle['result'].update(fallback_allowed=True)]
        for n, change in enumerate(changes):
            with self.subTest(case=n):
                f = AutoPublicationFixture()
                self.addCleanup(f.close)
                change(f)
                f.rebind()
                before = bytes_at(f.root)
                with self.assertRaises(ValueError):
                    publication.publish(f.ctx, f.bundle, now=NOW)
                self.assertEqual(bytes_at(f.root), before)

    def test_existing_and_human_reviewed_items_remain_protected(self):
        for reviewed in (False, True):
            with self.subTest(reviewed=reviewed):
                f = AutoPublicationFixture()
                self.addCleanup(f.close)
                if reviewed:
                    item = f.state['items'][0]
                    item['human_review'] = dict(actor='user', reviewed_at=NOW.isoformat(),
                        page_sha256='a'*64, scope='synthetic human review', evidence_ref='review.json')
                    f.put(C.STATE, C.encoded(f.state))
                else:
                    f.put(f'entities/arxiv-{VID}.md', b'User-owned existing note.\n')
                before_state = f.fs.read(C.STATE)
                with self.assertRaisesRegex(ValueError, 'reviewed item|never overwrite'):
                    publication.publish(f.ctx, f.bundle, now=NOW)
                self.assertEqual(f.fs.read(C.STATE), before_state)
                if not reviewed:
                    self.assertEqual(f.fs.read(f'entities/arxiv-{VID}.md'), b'User-owned existing note.\n')

    def test_legacy_committed_noop_preserves_every_byte(self):
        f = AutoPublicationFixture()
        self.addCleanup(f.close)
        self.assertEqual(legacy_publisher().publish(f.ctx, f.bundle, now=NOW)['status'], LEGACY)
        before = bytes_at(f.root)
        result = publication.publish(f.ctx, f.bundle, now=NOW)
        self.assertEqual(result['status'], 'noop')
        self.assertEqual(bytes_at(f.root), before)
        self.assertEqual(C.decode(f.fs.read(C.STATE))['items'][0]['status'], LEGACY)

    def test_new_html_and_pdf_publication_is_compiled_auto_verified(self):
        for fmt in ('html', 'pdf'):
            with self.subTest(format=fmt):
                f = AutoPublicationFixture(fmt)
                self.addCleanup(f.close)
                before_log = f.fs.read('log.md')
                result = publication.publish(f.ctx, f.bundle, now=NOW)
                page = f.fs.read(f'entities/arxiv-{VID}.md').decode()
                self.assertIn('status: "compiled"', page)
                self.assertIn('review_state: "auto_verified"', page)
                self.assertIn('last_reviewed: null', page)
                self.assertEqual(result['status'], AUTO)
                state = C.decode(f.fs.read(C.STATE))
                item = state['items'][0]
                self.assertEqual(item['status'], AUTO)
                self.assertIsNone(item['human_review'])
                receipt = C.decode(f.fs.read(result['receipt_ref']))
                self.assertIsNone(receipt['human_review_ref'])
                self.assertIsNone(f.bundle['review']['human_review_ref'])
                self.assertEqual(receipt['output_refs'][0]['sha256'], C.sha(page.encode()))
                self.assertEqual(receipt['evidence_check_ref'], f.prefix+'-review.json')
                self.assertEqual(receipt['structural_check_ref'], f.prefix+'-report.json')
                C.helper('publish').schema_validate(f.ctx['schema'], state, 'compilation')
                for text in (f.fs.read('index.md').decode(), f.fs.read('log.md').decode()):
                    self.assertIn('자동 검증 완료', text)
                    self.assertNotIn('draft/unreviewed', text.lower())
                self.assertTrue(f.fs.read('log.md').startswith(before_log))
                self.assertIn('no human review, visual inspection or experimental reproduction claimed',
                              f.fs.read('log.md').decode())
                before = bytes_at(f.root)
                self.assertEqual(publication.publish(f.ctx, f.bundle, now=NOW)['status'], 'noop')
                self.assertEqual(bytes_at(f.root), before)


class AutoDailyTests(unittest.TestCase):
    def test_two_formats_generate_independent_reviews_and_auto_publish(self):
        f = AutoDailyFixture()
        self.addCleanup(f.close)
        f.source(VID)
        pdf_vid = f.source('2610.00002v1', fmt='pdf')
        source = ContentFixture()
        self.addCleanup(source.close)
        pdf = source.use_pdf(('Alpha evidence.', 'Beta evidence.'))
        source_ctx: Any = source.ctx
        data = source_ctx['fs'].read(source_ctx['item']['source_path'])
        base = f'raw/articles/4cff5b4f10ec/arxiv-{pdf_vid}/'
        f.put(base+'source.pdf', data)
        meta = C.decode(f.fs.read(base+'source.json'))
        meta.update(pdf_sha256=C.sha(data), pdf_bytes=len(data))
        f.put(base+'source.json', C.encoded(meta))
        originals = bytes_at(f.root/'raw')
        model = Model()
        result = daily.run_daily(**f.kw(), client_factory=model, pdf_module=pdf)
        self.assertEqual(result['status'], 'committed')
        self.assertEqual([r['status'] for r in result['outcomes']], [AUTO, AUTO])
        self.assertEqual(len(model.calls), 4)
        self.assertEqual(model.closed, 4)
        self.assertEqual(bytes_at(f.root/'raw'), originals)
        self.assertIn(b'source.pdf#page=1', f.fs.read(f'entities/arxiv-{pdf_vid}.md'))
        state = C.decode(f.fs.read(C.STATE))
        self.assertEqual([i['status'] for i in state['items']], [AUTO, AUTO])
        self.assertEqual(len(state['transactions']), 2)

    def test_auto_verified_recovery_after_every_wal_interruption(self):
        for stage in ('after_basis', 'after_journal', 'after_page', 'after_index',
                      'after_log', 'after_receipt', 'after_state'):
            with self.subTest(stage=stage):
                f = AutoDailyFixture()
                self.addCleanup(f.close)
                f.source(VID)
                model = Model()
                original = publication.publish
                def crash(current):
                    if current == stage:
                        raise RuntimeError(stage)
                def interrupted(ctx, bundle, **kwargs):
                    return original(ctx, bundle, hook=crash, **kwargs)
                with patch.object(publication, 'publish', interrupted):
                    interrupted_report = daily.run_daily(**f.kw(), client_factory=model)
                self.assertEqual(interrupted_report['status'], 'unknown')
                self.assertEqual(C.decode(f.fs.read(RUN+'/daily-report.json')), interrupted_report)
                prefix = f'{RUN}/items/{VID}/attempt1'
                self.assertIsNone(f.fs.read(prefix+'-outcome.json', True))
                self.assertIsNotNone(f.fs.read(prefix+'-publication-basis.json', True))
                if stage != 'after_basis':
                    self.assertIsNotNone(f.fs.read(prefix+'-publish-journal.json', True))
                self.assertEqual(len(model.calls), 2)
                result = daily.recover_publication(**f.kw(), version_id=VID, attempt=1)
                self.assertEqual(result['status'], AUTO)
                before = bytes_at(f.root)
                result = daily.recover_publication(**f.kw(), version_id=VID, attempt=1)
                self.assertEqual(result['status'], 'noop')
                self.assertEqual(bytes_at(f.root), before)
                self.assertEqual(len(model.calls), 2)
                self.assertEqual(model.closed, 2)
                self.assertEqual(f.fs.read('log.md').count(b'<!-- publication-event:'), 1)
                self.assertEqual(len(C.decode(f.fs.read(C.STATE))['cost_events']), 1)
                self.assertFalse((f.root/daily.RUN_LOCK).exists())
                self.assertFalse((f.root/C.helper('publish').LOCK).exists())

    def test_mixed_old_and_auto_publications_remain_noop_and_unreservable(self):
        f = AutoDailyFixture()
        self.addCleanup(f.close)
        old_vid = f.source(VID)
        model = Model()
        with patch.object(publication, 'publish', legacy_publisher().publish):
            self.assertEqual(daily.run_daily(**f.kw(), client_factory=model)['status'], 'committed')
        old_state = C.decode(f.fs.read(C.STATE))
        old_files = bytes_at(f.root)
        new_vid = f.source('2610.00002v1')
        next_run = '_meta/runs/wiki/synthetic-mixed-next'
        f.approval.update(run=next_run, edit_freeze={'mode': 'run', 'run': next_run})
        f.put(APPROVAL, C.encoded(f.approval))
        result = daily.run_daily(**dict(f.kw(), run=next_run), client_factory=model)
        self.assertEqual(result['status'], 'committed')
        self.assertEqual(result['selected'], [new_vid])
        state = C.decode(f.fs.read(C.STATE))
        self.assertEqual({i['version_id']: i['status'] for i in state['items']}, {old_vid: LEGACY, new_vid: AUTO})
        self.assertEqual(state['items'][0], old_state['items'][0])
        for path, data in old_files.items():
            if path.endswith(('-receipt.json', '-publish-journal.json', '-publication-basis.json')) or path.startswith('entities/'):
                self.assertEqual(f.fs.read(path), data, path)
        third = '_meta/runs/wiki/synthetic-mixed-final'
        f.approval.update(run=third, edit_freeze={'mode': 'run', 'run': third})
        f.put(APPROVAL, C.encoded(f.approval))
        self.assertEqual(daily.run_daily(**dict(f.kw(), run=third), client_factory=model)['status'], 'noop')
        self.assertEqual(len(model.calls), 4)
        ctx = daily.preflight(**dict(f.kw(), run=third))
        self.assertEqual(daily.select(state['items'], 5), [])
        with daily.run_lock(ctx):
            for item in state['items']:
                with self.assertRaisesRegex(ValueError, 'item_not_reservable'):
                    daily.reserve(ctx, item, 1)

    def test_recovery_cli_accepts_both_published_terminal_statuses(self):
        for status in (AUTO, LEGACY):
            with self.subTest(status=status):
                output = io.StringIO()
                # Fixed production root cannot be used by this synthetic CLI test.
                with patch.object(daily, 'recover_publication', return_value={'status': status}) as recover:
                    with redirect_stdout(output):
                        code = daily.main(['--run', '_meta/runs/wiki/synthetic-cli',
                            '--approval-ref', APPROVAL, '--recover-version', VID, '--attempt', '1'])
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(output.getvalue())['status'], status)
                recover.assert_called_once_with(run='_meta/runs/wiki/synthetic-cli',
                    approval_ref=APPROVAL, version_id=VID, attempt=1)

    def test_daily_commits_auto_verified_then_noops_without_second_model(self):
        f = AutoDailyFixture()
        self.addCleanup(f.close)
        f.source(VID)
        model = Model()
        result = daily.run_daily(**f.kw(), client_factory=model)
        self.assertEqual(result['status'], 'committed')
        self.assertEqual([entry['status'] for entry in result['outcomes']], [AUTO])
        self.assertEqual(len(model.calls), 2)
        self.assertEqual(model.closed, 2)
        state = C.decode(f.fs.read(C.STATE))
        self.assertEqual(state['items'][0]['status'], AUTO)
        preserved = {path: raw for path, raw in bytes_at(f.root).items()
                     if path != APPROVAL}
        next_run = '_meta/runs/wiki/synthetic-auto-next'
        f.approval.update(run=next_run, edit_freeze={'mode': 'run', 'run': next_run})
        f.put(APPROVAL, C.encoded(f.approval))
        result = daily.run_daily(**dict(f.kw(), run=next_run), client_factory=model)
        self.assertEqual(result['status'], 'noop')
        self.assertEqual(result['selected'], [])
        self.assertEqual(len(model.calls), 2)
        for path, raw in preserved.items():
            self.assertEqual(f.fs.read(path), raw, path)
        ctx = daily.preflight(**dict(f.kw(), run=next_run))
        wiki = daily.published_context(ctx, state['items'])
        self.assertEqual([w['path'] for w in wiki], [f'entities/arxiv-{VID}.md'])
        f.put(f'entities/arxiv-{VID}.md', wiki[0]['text'].encode()+b'User edit')
        with self.assertRaisesRegex(ValueError, 'published_output_changed'):
            daily.published_context(ctx, state['items'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
