"""Real daily/content/publication integration with synthetic papers/fake model."""
import copy
from contextlib import redirect_stdout
import io
import json
import unittest
from typing import Any
from unittest.mock import patch

import p3_common as C
import daily
from test_daily import Fixture, RUN, APPROVAL
from test_content import Fixture as ContentFixture, UNREAD, response, review_payload

class Model:
    def __init__(self):self.calls=[];self.closed=0
    def __call__(self,**kwargs):
        owner=self
        assert kwargs['max_retries']==0
        class Client:
            def __init__(self):self.responses=self
            def create(self,**request):
                owner.calls.append(request)
                payload=json.loads(request['input'][0]['content'][0]['text'])
                if 'document' in payload:return response(review_payload(payload['document']))
                anchors=payload['telemetry']['read_scope']
                anchor=anchors[0]
                quote='Alpha evidence.' if 'html' in payload['source'] else payload['source']['pages'][0]['text'].strip()
                doc=dict(title=payload['title'],summary='합성 텍스트 근거와 한계를 정리한다.',version_id=payload['version_id'],
                    main_text_complete=True,read_scope=anchors,unread_scope=list(UNREAD),limitations=['독립 실험 재현 미수행.'],
                    claims=[dict(id='C01',kind='author_report',statement='합성 근거를 보고한다.',conditions='합성 시험 자료에 한정.',anchor=anchor,quote=quote)],
                    markdown_body=f"# 합성 노트\n버전 {payload['version_id']}; 읽은 범위: {', '.join(anchors)}\nC01 합성 근거 보고. ^[{payload['source_path']}#{anchor}]\n"+'\n'.join(UNREAD)+'\n')
                return response(doc)
            def close(self):owner.closed+=1
        return Client()

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.addCleanup(self.f.close)
    def test_two_formats_generate_review_publish_and_next_run_noop(self):
        self.f.source('2610.00001v1')
        self.f.source('2610.00002v1',fmt='pdf')
        source_fixture=ContentFixture();self.addCleanup(source_fixture.close)
        pdf=source_fixture.use_pdf(('Alpha evidence.','Beta evidence.'))
        source_ctx: Any=source_fixture.ctx
        data=source_ctx['fs'].read(source_ctx['item']['source_path'])
        base='raw/articles/4cff5b4f10ec/arxiv-2610.00002v1/'
        self.f.put(base+'source.pdf',data)
        meta=C.decode(self.f.fs.read(base+'source.json'))
        meta.update(pdf_sha256=C.sha(data),pdf_bytes=len(data))
        self.f.put(base+'source.json',C.encoded(meta))
        originals={str(p.relative_to(self.f.root)):C.sha(p.read_bytes()) for p in (self.f.root/'raw').rglob('*') if p.is_file()}
        model=Model()
        kwargs: Any=self.f.kw()
        out=daily.run_daily(**kwargs,client_factory=model,pdf_module=pdf)
        self.assertEqual(out['status'],'committed')
        self.assertEqual(len(model.calls),4)
        self.assertEqual(model.closed,4)
        state=C.decode(self.f.fs.read(C.STATE))
        self.assertEqual([i['status'] for i in state['items']],['published_auto_verified','published_auto_verified'])
        self.assertEqual(len(state['transactions']),2)
        self.assertEqual(self.f.fs.read('log.md').count(b'<!-- publication-event:'),2)
        for p,h in originals.items():self.assertEqual(C.sha(self.f.fs.read(p)),h)
        second='_meta/runs/wiki/synthetic-next'
        # Manual approval changes its run but not policy/work identity.
        self.f.approval.update(run=second,edit_freeze={'mode':'run','run':second})
        self.f.put(APPROVAL,C.encoded(self.f.approval))
        watched={p:C.sha(self.f.fs.read(p)) for p in ('index.md','log.md',C.STATE)}
        kwargs=dict(self.f.kw(),run=second)
        no=daily.run_daily(**kwargs,client_factory=model,pdf_module=pdf)
        self.assertEqual(no['status'],'noop')
        self.assertEqual(len(model.calls),4)
        self.assertEqual(watched,{p:C.sha(self.f.fs.read(p)) for p in watched})

    def test_daily_recovery_after_each_publication_interruption_without_model(self):
        import publication
        for stage in ('after_basis','after_journal','after_page','after_index','after_log','after_receipt','after_state'):
            with self.subTest(stage=stage):
                f=Fixture();self.addCleanup(f.close);f.source('2610.00001v1')
                model=Model();original=publication.publish
                def crash(current):
                    if stage==current:raise RuntimeError(stage)
                def interrupted(ctx,bundle,**kwargs):return original(ctx,bundle,hook=crash,**kwargs)
                kw: Any=f.kw()
                with patch.object(publication,'publish',interrupted):
                    interrupted_report=daily.run_daily(**kw,client_factory=model)
                self.assertEqual(interrupted_report['status'],'unknown')
                self.assertEqual(C.decode(f.fs.read(RUN+'/daily-report.json')),interrupted_report)
                prefix=RUN+'/items/2610.00001v1/attempt1'
                self.assertIsNone(f.fs.read(prefix+'-outcome.json',True))
                self.assertIsNotNone(f.fs.read(prefix+'-publication-basis.json',True))
                if stage!='after_basis':
                    self.assertIsNotNone(f.fs.read(prefix+'-publish-journal.json',True))
                result=daily.recover_publication(**kw,version_id='2610.00001v1',attempt=1)
                self.assertEqual(result['status'],'published_auto_verified')
                self.assertEqual(len(model.calls),2)
                self.assertEqual(daily.recover_publication(**kw,version_id='2610.00001v1',attempt=1)['status'],'noop')
                self.assertEqual(f.fs.read('log.md').count(b'<!-- publication-event:'),1)

    def test_deadline_after_generation_blocks_publication_without_replaying_model(self):
        import content
        self.f.source('2610.00001v1');model=Model();elapsed=[0.0]
        def generate(ctx,**kwargs):
            bundle=content.process(ctx,**kwargs);elapsed[0]=3000.0;return bundle
        kw: Any=self.f.kw()
        result=daily.run_daily(**kw,processor=generate,client_factory=model,clock=lambda:elapsed[0])
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(C.decode(self.f.fs.read(RUN+'/daily-report.json')),result)
        prefix=RUN+'/items/2610.00001v1/attempt1'
        self.assertEqual(C.decode(self.f.fs.read(prefix+'-outcome.json'))['status'],'unknown')
        self.assertEqual(C.decode(self.f.fs.read(C.STATE))['items'][0]['status'],'blocked_conflict')
        self.assertFalse((self.f.root/daily.RUN_LOCK).exists())
        self.assertEqual(len(model.calls),2)
        self.assertFalse((self.f.root/'entities/arxiv-2610.00001v1.md').exists())
        self.assertFalse(list(self.f.root.glob('**/*-publish-journal.json')))

    def test_cli_reports_real_disabled_gate_without_creating_isolated_run(self):
        run='_meta/runs/wiki/synthetic-cli-disabled-probe'
        target=self.f.root/run
        self.f.approval.update(run=run,edit_freeze={'mode':'run','run':run})
        self.f.auto['phase_authorizations']['P3']=False;self.f.sync()
        before={str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        self.assertFalse(target.exists())
        model=Model();real_run_daily=daily.run_daily
        def isolated_run(**kwargs):
            # Inject only the synthetic context; execute the real authority gate.
            isolated_kwargs: Any=dict(self.f.kw(),**kwargs)
            return real_run_daily(**isolated_kwargs,client_factory=model)
        argv=['--run',run,'--approval-ref',APPROVAL]
        output=io.StringIO()
        with patch.object(daily,'run_daily',side_effect=isolated_run) as invoked,redirect_stdout(output):
            code=daily.main(argv)
        invoked.assert_called_once_with(run=run,approval_ref=APPROVAL)
        self.assertEqual(code,2)
        result=json.loads(output.getvalue())
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(result['error']['message'],'p3_execution_not_authorized')
        self.assertFalse(target.exists())
        self.assertEqual(model.calls,[])
        after={str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        # The same isolated CLI reaches a real no-op when P3 is authorized.
        self.f.auto['phase_authorizations']['P3']=True;self.f.sync()
        output=io.StringIO()
        with patch.object(daily,'run_daily',side_effect=isolated_run),redirect_stdout(output):
            code=daily.main(argv)
        self.assertEqual(code,0)
        self.assertEqual(json.loads(output.getvalue())['status'],'noop')
        self.assertEqual(model.calls,[])

    def test_later_success_does_not_hide_earlier_partial(self):
        import content
        self.f.source('2610.00001v1');self.f.source('2610.00002v1')
        def process(ctx,**kwargs):
            if ctx['item']['version_id']=='2610.00001v1':
                return dict(status='partial',report={'document':dict(read_scope=['S1'],unread_scope=['S2'],resume_at='S2')})
            return content.process(ctx,**kwargs)
        kw: Any=self.f.kw()
        result=daily.run_daily(**kw,processor=process,client_factory=Model())
        self.assertEqual([x['status'] for x in result['outcomes']],['partial','published_auto_verified'])
        self.assertEqual(result['status'],'partial')

    def test_partial_pdf_telemetry_reaches_daily_state_without_model(self):
        self.f.source('2610.00001v1',fmt='pdf')
        source_fixture=ContentFixture();self.addCleanup(source_fixture.close)
        pdf=source_fixture.use_pdf(('Alpha evidence.',''))
        source_ctx: Any=source_fixture.ctx
        data=source_ctx['fs'].read(source_ctx['item']['source_path'])
        base='raw/articles/4cff5b4f10ec/arxiv-2610.00001v1/'
        self.f.put(base+'source.pdf',data)
        meta=C.decode(self.f.fs.read(base+'source.json'))
        meta.update(pdf_sha256=C.sha(data),pdf_bytes=len(data))
        self.f.put(base+'source.json',C.encoded(meta))
        model=Model();kw: Any=self.f.kw()
        result=daily.run_daily(**kw,client_factory=model,pdf_module=pdf)
        self.assertEqual(result['status'],'partial')
        self.assertEqual(model.calls,[])
        item=C.decode(self.f.fs.read(C.STATE))['items'][0]
        self.assertEqual(item['read_scope'],['page=1'])
        self.assertIn('page=2: 빈 텍스트, 미독',item['unread_scope'])
        self.assertEqual(item['resume_at'],'page=2')

if __name__=='__main__':unittest.main(verbosity=2)
