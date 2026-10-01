"""Daily P3 orchestration tests use synthetic roots and no network."""
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from typing import Any

import p3_common as C
HERE = Path(__file__).parent
NOW = datetime(2026, 10, 1, 2, 50, tzinfo=timezone.utc)
RUN = '_meta/runs/wiki/synthetic-daily'
APPROVAL = RUN+'/execution-approval.json'

def load() -> Any:
    path = HERE/'daily.py'
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location('p3_daily_tested', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class Fixture:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-', dir=HERE)
        self.root = Path(self.tmp.name)
        self.fs = C.helper('publish').Files(self.root)
        self.auto = json.loads((C.ROOT/'_meta/automation.json').read_text())
        self.auto['wiki_root'] = str(self.root)
        self.auto['phase_authorizations']['P3'] = True
        self.schema = json.loads((C.ROOT/'_meta/automation-contracts.schema.json').read_text())
        self.schema['$defs']['automation']['properties']['wiki_root']['const'] = str(self.root)
        self.state = dict(schema='pkm-compilation-state/v1', policy_revision=C.POLICY,
            contract_revision=C.CONTRACT, initialized_at=NOW.isoformat(), enabled=False,
            safety_block=False, safety_block_reason=None, items=[], transactions=[], receipts=[], cost_events=[], last_run=None)
        self.approval: dict[str,Any] = dict(schema='pkm-p3-execution-approval/v1', actor='user', approved=True,
            user_request='SYNTHETIC TEST ONLY: P3 processing and draft publication', phase='P3',
            wiki_root=str(self.root), mode='manual', run=RUN, source_scope='current_and_future_collected',
            formats=['html','pdf'], collector_id='4cff5b4f10ec', model=C.MODEL, route=C.ROUTE,
            validated_publication_authorized=True, edit_freeze={'mode':'run','run':RUN},
            cost_policy='no_cost_cap', snapshots={})
        for d in ['entities','concepts','comparisons','queries','_meta/locks', RUN, 'raw/articles/4cff5b4f10ec']:
            C.ensure_dirs(self.fs, d)
        for name in C.DOCS:
            self.put(name, C.encoded(self.schema) if name.endswith('.json') else (C.POLICY+'\n').encode())
        self.put(C.PROMPT, (C.PROMPT_REV+'\n'+C.POLICY+'\n').encode())
        self.put('index.md', b'# Index\n\n> Last updated: 2026-10-01 | Total pages: 0\n\n## Entities\n\n## Concepts\n\n## Comparisons\n\n## Queries\n')
        self.put('log.md', b'# Synthetic log\n')
        self.sync()
    def put(self, path, data):
        C.ensure_dirs(self.fs, str(Path(path).parent)) if '/' in path else None
        target = self.root/path
        target.write_bytes(data)
    def sync(self):
        self.put('_meta/automation.json', C.encoded(self.auto))
        self.put(C.STATE, C.encoded(self.state))
        self.approval['snapshots'] = {p:C.sha(self.fs.read(p)) for p in (*C.DOCS,C.PROMPT,'_meta/automation.json')}
        self.put(APPROVAL,C.encoded(self.approval))
    def source(self, vid, collected='2026-09-28T10:00:00+00:00', fmt='html'):
        data = b'<html><body><article id="S1"><p>Alpha evidence.</p></article></body></html>' if fmt=='html' else b'%PDF-1.7\nsynthetic placeholder for metadata-only tests\n%%EOF'
        base = f'raw/articles/4cff5b4f10ec/arxiv-{vid}'
        source=base+'/source.'+fmt
        meta=dict(schema='arxiv-'+fmt+'-source/v1',source='arxiv',version_id=vid,title='Synthetic '+vid,
            owning_cron_id='4cff5b4f10ec',source_url=f'https://arxiv.org/{fmt}/{vid}',final_url=f'https://arxiv.org/{fmt}/{vid}',
            collected_at=collected,http_status=200,preprocessing=False,offline_assets_bundled=False,wiki_compiled=False,
            capture_method='http_response_body_no_rewrite', **{fmt+'_file':'source.'+fmt,fmt+'_sha256':C.sha(data),fmt+'_bytes':len(data)})
        if fmt=='pdf':meta['source_format']='pdf'
        self.put(source,data);self.put(base+'/source.json',C.encoded(meta))
        return vid
    def kw(self):
        return dict(root=self.root,run=RUN,approval_ref=APPROVAL,synthetic=True,now=NOW)
    def close(self):self.tmp.cleanup()

class DailyTests(unittest.TestCase):
    def setUp(self):
        self.m=load()
        self.assertIsNotNone(self.m,'P3 daily orchestrator missing')
        self.f=Fixture();self.addCleanup(self.f.close)
    def test_preflight_binds_authority_and_refuses_live_disabled(self):
        ctx=self.m.preflight(**self.f.kw())
        self.assertEqual(ctx['approval_sha256'],C.sha(self.f.fs.read(APPROVAL)))
        self.assertEqual(ctx['model'],C.MODEL)
        self.f.auto['phase_authorizations']['P3']=False;self.f.sync()
        with self.assertRaisesRegex(ValueError,'p3_execution_not_authorized'):
            self.m.preflight(**self.f.kw())
        with self.assertRaisesRegex(ValueError,'p3_execution_not_authorized'):
            self.m.preflight(root=C.ROOT,run=RUN,approval_ref=APPROVAL,now=NOW)
        self.assertFalse((C.ROOT/RUN).exists())

    def test_inventory_selects_oldest_five_and_reserves_durably(self):
        self.assertTrue(callable(getattr(self.m,'inventory',None)), 'inventory not implemented')
        for n in range(6):
            self.f.source(f'2609.{30100+n}v1', f'2026-09-28T10:00:0{5-n}+00:00')
        ctx=self.m.preflight(**self.f.kw())
        items=self.m.inventory(ctx)
        self.assertEqual(len(items),6)
        self.assertEqual(self.m.select(items,5)[0]['version_id'],'2609.30105v1')
        self.assertEqual(len(self.m.select(items,5)),5)
        with self.m.run_lock(ctx) as owned:
            self.assertTrue(callable(owned))
            with self.m.run_lock(ctx) as other:
                self.assertFalse(other)
            prepared=self.m.reserve(ctx,items[0],1)
            self.assertTrue((self.f.root/(prepared['artifact_prefix']+'-reservation.json')).is_file())
            state=C.decode(self.f.fs.read(C.STATE))
            self.assertEqual(state['items'][0]['status'],'reading')
            self.assertEqual(prepared['item']['status'],'reading')
            with self.assertRaisesRegex(ValueError,'attempt_exists'):
                self.m.reserve(ctx,items[0],1)
        self.assertFalse((self.f.root/'_meta/locks/daily-run.lock').exists())

    def test_runner_bounds_retry_and_retains_unknown_without_retry(self):
        self.assertTrue(callable(getattr(self.m,'run_daily',None)), 'daily run missing')
        self.f.source('2609.30100v1')
        calls=[]
        def fail(ctx,**kwargs):
            calls.append(ctx['artifact_prefix'])
            self.assertTrue((self.f.root/(ctx['artifact_prefix']+'-reservation.json')).exists())
            return {'status':'retryable_failed'}
        out=self.m.run_daily(**self.f.kw(),processor=fail)
        self.assertEqual(len(calls),2)
        self.assertEqual(out['status'],'retryable_failed')
        state=C.decode(self.f.fs.read(C.STATE))
        self.assertEqual(state['items'][0]['failure_count'],2)
        self.assertFalse(state['safety_block'])
        self.assertEqual(list((self.f.root/'entities').iterdir()),[])
        self.assertIsNone(state['cost_events'][0]['charged_usd'])
        self.assertFalse((self.f.root/'_meta/locks/daily-run.lock').exists())

    def test_runner_unknown_is_not_retried(self):
        self.assertTrue(callable(getattr(self.m,'run_daily',None)), 'daily run missing')
        self.f.source('2609.30100v1')
        calls=[]
        def unknown(ctx,**kwargs):
            calls.append(1)
            return {'status':'unknown'}
        out=self.m.run_daily(**self.f.kw(),processor=unknown)
        self.assertEqual(len(calls),1)
        self.assertEqual(out['status'],'unknown')
        state=C.decode(self.f.fs.read(C.STATE))
        self.assertEqual(state['items'][0]['status'],'blocked_conflict')
        self.assertEqual(state['items'][0]['failure_count'],0)

    def test_scheduled_gate_checks_live_projection_and_freeze(self):
        a=self.f.auto
        a.update(enabled=True,registration_authorized=True,activation_authorized=True,activation_blockers=[])
        a['jobs']['daily_compile'].update(enabled=True,cron_id='synthetic-job',registration_status='active',registration_readback=RUN+'/registration.json')
        self.f.state['enabled']=True
        self.f.approval.update(mode='scheduled',run=None,cron_id='synthetic-job',
            edit_freeze={'mode':'daily_window','timezone':'Asia/Seoul','start':'02:00','end':'02:45'})
        job=dict(id='synthetic-job',enabled=True,model='gpt-6-astra',provider='codex-lb',reasoning_effort='xhigh',
            workdir=str(self.f.root),skills=['llm-wiki'],deliver='local',failure_deliver='local',no_agent=False,
            attach_to_session=False,monitor_script=None,monitor_url=None,
            schedule={'kind':'cron','expr':'0 17 * * *','display':'0 17 * * *'},prompt=self.f.fs.read(C.PROMPT).decode().strip(),
            next_run_at='2026-10-02T17:00:00+00:00')
        self.f.put(RUN+'/registration.json',C.encoded({'schema':'pkm-p3-registration/v1','job':job}))
        self.f.sync()
        self.f.approval['snapshots'][RUN+'/registration.json']=C.sha(self.f.fs.read(RUN+'/registration.json'))
        self.f.put(APPROVAL,C.encoded(self.f.approval))
        kw=dict(self.f.kw(),now=datetime(2026,10,1,17,10,tzinfo=timezone.utc),scheduler_observer=lambda _:job)
        ctx=self.m.preflight(**kw)
        self.assertEqual(ctx['approval']['mode'],'scheduled')
        bad=dict(job,reasoning_effort='high')
        with self.assertRaisesRegex(ValueError,'scheduler_projection'):
            self.m.preflight(**dict(kw,scheduler_observer=lambda _:bad))
        with self.assertRaisesRegex(ValueError,'edit_freeze_window'):
            self.m.preflight(**dict(kw,now=NOW))
        for key,value in [('monitor_script','unapproved.sh'),('monitor_url','https://invalid.example/data'),
                          ('attach_to_session',True),('attach_to_session',None)]:
            with self.subTest(runtime_field=key,value=value):
                bad=dict(job,**{key:value})
                with self.assertRaisesRegex(ValueError,'scheduler_projection'):
                    self.m.preflight(**dict(kw,scheduler_observer=lambda _:bad))

    def test_partial_and_three_failures_block_further_processing(self):
        vid=self.f.source('2609.30100v1')
        items=self.m.inventory(self.m.preflight(**self.f.kw()))
        items[0]['failure_count']=2
        self.f.state['items']=items;self.f.sync()
        calls=[]
        def fail(ctx,**kw):
            calls.append(1)
            return dict(status='retryable_failed')
        self.m.run_daily(**self.f.kw(),processor=fail)
        self.assertEqual(len(calls),1)
        state=C.decode(self.f.fs.read(C.STATE))
        self.assertTrue(state['safety_block'])
        self.assertEqual(state['items'][0]['failure_count'],3)

    def test_empty_inventory_is_verified_noop(self):
        out=self.m.run_daily(**self.f.kw(),processor=lambda *a,**k:self.fail('no model on empty'))
        self.assertEqual(out['status'],'noop')

    def test_reserved_unknown_from_prior_run_blocks_new_run(self):
        self.f.source('2609.30100v1')
        ctx=self.m.preflight(**self.f.kw())
        with self.m.run_lock(ctx):
            item=self.m.inventory(ctx)[0]
            prepared=self.m.reserve(ctx,item,1)
        called=[]
        with self.assertRaisesRegex(ValueError,'unresolved_reading'):
            self.m.run_daily(**self.f.kw(),processor=lambda *a,**k:called.append(1))
        self.assertFalse(called)

    def test_preserved_completed_source_noop_checks_receipt_and_output(self):
        self.assertTrue(callable(getattr(self.m,'published_context',None)), 'published context missing')
        vid=self.f.source('2609.30100v1')
        item=self.m.inventory(self.m.preflight(**self.f.kw()))[0]
        path=f'entities/arxiv-{vid}.md'
        page=b'---\nstatus: draft\n---\nSynthetic committed note.\n'
        self.f.put(path,page)
        refs=[dict(path=path,sha256=C.sha(page),revision='1')]
        receipt_path=RUN+'/old-receipt.json';journal_path=RUN+'/old-publish-journal.json'
        work='a'*64
        receipt=dict(schema='pkm-publication-receipt/v1',transaction_id='old-tx',work_key=work,
            output_refs=refs,actual_input_hashes={item['source_path']:item['source_sha256']})
        self.f.put(receipt_path,C.encoded(receipt))
        plan=dict(schema='pkm-publication-journal/v1',journal_path=journal_path,status='committed',
            transaction_id='old-tx',targets=[dict(path=path,after_hash=C.sha(page)),dict(path=receipt_path,after_hash=C.sha(C.encoded(receipt)))],
            log=dict(prefix_bytes=len(b'# Synthetic log\n'),prefix_sha256=C.sha(b'# Synthetic log\n'),event='old event\n'))
        self.f.put(journal_path,C.encoded(dict(plan=plan,plan_sha256=C.sha(C.canonical(plan)))))
        self.f.put('log.md',b'# Synthetic log\nold event\n')
        self.f.put('index.md',f'# Index\n\n> Last updated: 2026-10-01 | Total pages: 1\n\n## Entities\n\n- [[entities/arxiv-{vid}]]\n\n## Concepts\n'.encode())
        item.update(status='published_draft',requested_scope='prior manual scope',work_key=work,read_scope=['S1'],output_refs=refs,receipt_ref=receipt_path)
        self.f.state['items']=[item];self.f.state['receipts']=[receipt_path]
        self.f.state['transactions']=[dict(transaction_id='old-tx',journal_path=journal_path,status='committed')]
        self.f.approval['preserved_publications']={vid:dict(work_key=work,receipt_sha256=C.sha(C.encoded(receipt)),output_refs=refs)}
        self.f.sync()
        out=self.m.run_daily(**self.f.kw(),processor=lambda *a,**k:self.fail('completed must skip'))
        self.assertEqual(out['status'],'noop')
        ctx=self.m.preflight(**self.f.kw())
        wiki=self.m.published_context(ctx,[item])
        self.assertEqual(wiki[0]['path'],path)
        self.f.put(path,page+b'user edit')
        with self.assertRaisesRegex(ValueError,'published_output_changed'):
            self.m.published_context(ctx,[item])

    def test_dangling_reservation_before_state_write_is_not_replayed(self):
        self.f.source('2609.30100v1')
        prefix=RUN+'/items/2609.30100v1/attempt1'
        self.f.put(prefix+'-reservation.json',C.encoded(dict(schema='pkm-p3-reservation/v1',version_id='2609.30100v1',status='unknown')))
        other='_meta/runs/wiki/synthetic-next'
        self.f.approval.update(run=other,edit_freeze={'mode':'run','run':other});self.f.sync()
        with self.assertRaisesRegex(ValueError,'unresolved_reservation'):
            self.m.run_daily(**dict(self.f.kw(),run=other),processor=lambda *a,**k:self.fail('must not call'))

    def test_authority_and_integrity_negatives(self):
        for key,val in [('model',dict(C.MODEL,model='other')),('pdf_reading',dict(C.PDF_READING,ocr=True))]:
            with self.subTest(key=key):
                original=copy.deepcopy(self.f.auto[key]);self.f.auto[key]=val;self.f.sync()
                with self.assertRaises(ValueError):self.m.preflight(**self.f.kw())
                self.f.auto[key]=original;self.f.sync()
        vid=self.f.source('2609.30100v1')
        self.f.put(f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html',b'altered')
        with self.assertRaisesRegex(ValueError,'source_integrity'):
            self.m.inventory(self.m.preflight(**self.f.kw()))

    def test_context_deadline_is_checked_between_inventory_sources(self):
        self.f.source('2609.30100v1');self.f.source('2609.30101v1')
        clock_state=[0.0]
        original=self.f.fs.read
        def reader(path,*a,**kw):
            value=original(path,*a,**kw)
            if path.endswith('arxiv-2609.30100v1/source.html'):clock_state[0]=100.0
            if path.endswith('arxiv-2609.30101v1/source.html'):self.fail('second source read after deadline')
            return value
        ctx=self.m.preflight(**self.f.kw());ctx['fs'].read=reader
        ctx['deadline']=10.0;ctx['clock']=lambda:clock_state[0]
        with self.assertRaises(TimeoutError):self.m.inventory(ctx)

if __name__=='__main__': unittest.main(verbosity=2)
