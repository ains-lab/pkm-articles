"""Scheduler safety regressions: isolated synthetic IO, never model/network."""
import copy
from datetime import datetime, timezone
from pathlib import Path
import unittest
from typing import Any
from unittest.mock import patch

import daily
import p3_common as C
from test_daily import Fixture, RUN, APPROVAL

VID = '2610.00001v1'
PREFIX = RUN+'/items/'+VID+'/attempt1'
OLD = '_meta/runs/wiki/20260929T083140Z-p2-resume'
DEPENDENCIES = {C.RUN+'/runtime/'+n+'.py' for n in ('daily','p3_common','content','publication')} | {
    OLD+'/'+n+'-one.py' for n in ('compile','verify','publish')}

class ScheduledFixture(Fixture):
    def __init__(self):
        super().__init__()
        self.auto.update(enabled=True,registration_authorized=True,activation_authorized=True,activation_blockers=[])
        self.auto['jobs']['daily_compile'].update(enabled=True,cron_id='synthetic-job',registration_status='active',
            registration_readback=RUN+'/registration.json')
        self.state['enabled']=True
        self.approval.update(mode='scheduled',run=None,cron_id='synthetic-job',
            edit_freeze=dict(mode='daily_window',timezone='Asia/Seoul',start='02:00',end='02:45'))
        self.job=dict(id='synthetic-job',enabled=True,model=C.MODEL['model'],provider=C.MODEL['provider'],
            reasoning_effort=C.MODEL['reasoning_effort'],workdir=str(self.root),skills=['llm-wiki'],
            deliver='local',failure_deliver='local',no_agent=False,attach_to_session=False,
            monitor_script=None,monitor_url=None,schedule=dict(kind='cron',expr='0 17 * * *'),
            prompt=self.fs.read(C.PROMPT).decode().strip(),next_run_at='2026-10-02T17:00:00+00:00')
        self.put(RUN+'/registration.json',C.encoded(dict(schema='pkm-p3-registration/v1',job=self.job)))
        for path in sorted(DEPENDENCIES):
            self.put(path,(C.ROOT/path).read_bytes())
        self.manifest_ref=RUN+'/runtime-manifest.json'
        self.manifest: dict[str,Any]=dict(schema='pkm-p3-runtime-manifest/v1',runtime_files={p:C.sha(self.fs.read(p)) for p in sorted(DEPENDENCIES)})
        self.bind()
    def bind(self):
        self.put(self.manifest_ref,C.encoded(self.manifest))
        self.approval.update(runtime_manifest_ref=self.manifest_ref,runtime_manifest_sha256=C.sha(self.fs.read(self.manifest_ref)))
        self.sync()
        self.approval['snapshots'][RUN+'/registration.json']=C.sha(self.fs.read(RUN+'/registration.json'))
        self.put(APPROVAL,C.encoded(self.approval))
    def kw(self) -> dict[str,Any]:
        return dict(super().kw(),now=datetime(2026,10,1,17,44,50,tzinfo=timezone.utc),scheduler_observer=lambda _:self.job)

class ScheduledSafetyTests(unittest.TestCase):
    def setUp(self):
        self.f=ScheduledFixture();self.addCleanup(self.f.close)
        self.f.source(VID)
    def test_expired_processor_error_has_durable_unknown_not_orphan_reading(self):
        elapsed=[0.0];calls=[]
        def processor(ctx,**kw):
            calls.append(1);elapsed[0]=3000.0
            raise TimeoutError('synthetic dispatch timeout')
        result=daily.run_daily(**self.f.kw(),processor=processor,clock=lambda:elapsed[0])
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(calls,[1])
        outcome=C.decode(self.f.fs.read(PREFIX+'-outcome.json'))
        self.assertEqual(outcome['status'],'unknown')
        self.assertEqual(C.decode(self.f.fs.read(C.STATE))['items'][0]['status'],'blocked_conflict')
        self.assertEqual(C.decode(self.f.fs.read(RUN+'/daily-report.json')),result)
        self.assertFalse(list((self.f.root/'entities').iterdir()))
        self.assertFalse((self.f.root/daily.RUN_LOCK).exists())

    def test_occurrence_end_stops_real_generation_semantic_and_publication(self):
        import content
        from test_integration import Model
        for stage in ('generation','semantic','ready'):
            with self.subTest(stage=stage):
                f=ScheduledFixture();self.addCleanup(f.close);f.source(VID)
                elapsed=[0.0];model=Model();seen=[]
                def factory(**kwargs):
                    client=model(**kwargs);original=client.responses.create
                    def create(**request):
                        result=original(**request)
                        if len(model.calls)==(1 if stage=='generation' else 2) and stage!='ready':elapsed[0]=11.0
                        return result
                    client.responses.create=create
                    return client
                def processor(ctx,**kwargs):
                    seen.append(kwargs['deadline'])
                    original=ctx['fs'].read
                    def reader(path,*a,**kw):
                        if elapsed[0]>=11.0 and path.startswith('raw/'):
                            self.fail('source reread during expired terminal bookkeeping')
                        return original(path,*a,**kw)
                    ctx['fs'].read=reader
                    result=content.process(ctx,**kwargs)
                    if stage=='ready':elapsed[0]=11.0
                    return result
                result=daily.run_daily(**f.kw(),processor=processor,client_factory=factory,clock=lambda:elapsed[0])
                self.assertEqual(result['status'],'unknown')
                self.assertLessEqual(seen[0],10.0)
                self.assertEqual(len(model.calls),1 if stage=='generation' else 2)
                self.assertEqual(C.decode(f.fs.read(PREFIX+'-outcome.json'))['status'],'unknown')
                self.assertEqual(C.decode(f.fs.read(C.STATE))['items'][0]['status'],'blocked_conflict')
                self.assertFalse(list((f.root/'entities').iterdir()))
                self.assertFalse(list(f.root.glob('**/*-publish-journal.json')))

    def test_interrupted_publication_keeps_unknown_report_and_same_transaction_recovery(self):
        import publication
        from test_integration import Model
        for stage in ('after_basis','after_journal','after_page','after_index','after_log','after_receipt','after_state'):
            with self.subTest(stage=stage):
                f=ScheduledFixture();self.addCleanup(f.close);f.source(VID)
                elapsed=[0.0];model=Model();original=publication.publish
                def crash(current):
                    if current==stage:
                        elapsed[0]=11.0
                        raise TimeoutError('publication crossed occurrence end')
                def interrupted(ctx,bundle,**kw):return original(ctx,bundle,hook=crash,**kw)
                with patch.object(publication,'publish',interrupted):
                    result=daily.run_daily(**f.kw(),client_factory=model,clock=lambda:elapsed[0])
                self.assertEqual(result['status'],'unknown')
                self.assertEqual(result['outcomes'][0]['stage'],'publication')
                self.assertEqual(C.decode(f.fs.read(RUN+'/daily-report.json')),result)
                self.assertFalse((f.root/(PREFIX+'-outcome.json')).exists())
                failure=C.decode(f.fs.read(PREFIX+'-publication-unknown.json'))
                self.assertEqual(failure['status'],'unknown')
                self.assertTrue(failure['operator_recovery_required'])
                if stage!='after_basis':self.assertIn('journal',failure['publication_evidence'])
                self.assertEqual(len(model.calls),2)
                # Recovery retains the exact original result/WAL; no regeneration.
                recovered=daily.recover_publication(**f.kw(),version_id=VID,attempt=1)
                self.assertIn(recovered['status'],('published_auto_verified','noop'))
                self.assertEqual(len(model.calls),2)
                self.assertEqual(f.fs.read('log.md').count(b'<!-- publication-event:'),1)
                self.assertEqual(C.decode(f.fs.read(PREFIX+'-publication-unknown.json')),failure)

    def test_scheduled_manifest_exact_dependencies_required_before_source_or_model(self):
        for defect in ('missing_ref','missing_hash','manifest_hash','schema','missing_dependency','extra_dependency','dependency_bytes'):
            with self.subTest(defect=defect):
                f=ScheduledFixture();self.addCleanup(f.close);f.source(VID)
                if defect=='missing_ref':f.approval.pop('runtime_manifest_ref')
                elif defect=='missing_hash':f.approval.pop('runtime_manifest_sha256')
                elif defect=='manifest_hash':f.approval['runtime_manifest_sha256']='0'*64
                elif defect=='dependency_bytes':f.put(sorted(DEPENDENCIES)[0],b'changed runtime')
                else:
                    if defect=='schema':f.manifest['schema']='unapproved/v1'
                    elif defect=='missing_dependency':f.manifest['runtime_files'].pop(sorted(DEPENDENCIES)[0])
                    elif defect=='extra_dependency':f.manifest['runtime_files']['unexpected.py']='0'*64
                    f.bind()
                f.put(APPROVAL,C.encoded(f.approval))
                P=C.helper('publish');read=P.Files.read;calls=[]
                def reader(fs,path,*a,**kw):
                    if path.startswith('raw/'):self.fail('source read before manifest rejection')
                    return read(fs,path,*a,**kw)
                with patch.object(P.Files,'read',reader),self.assertRaisesRegex(ValueError,'runtime_manifest|runtime_dependency'):
                    daily.run_daily(**f.kw(),processor=lambda *a,**k:calls.append(1))
                self.assertEqual(calls,[])
                self.assertFalse((f.root/daily.RUN_LOCK).exists())

    def test_optional_scope_approval_is_hashed_user_authority_not_a_label(self):
        ref=RUN+'/scope-approval.json'
        scope=dict(schema='pkm-p3-operations-scope/v1',actor='user',approved=True,phase='P3',
            wiki_root=str(self.f.root),user_request=self.f.approval['user_request'],
            edit_freeze=self.f.approval['edit_freeze'],validated_publication_authorized=True,
            activation_authorized=True,scheduled_run_edit_freeze_authorized=True)
        for field,bad in [('schema','invented/v1'),('actor','agent'),('approved',False),('phase','P2'),
                          ('user_request','different request'),('edit_freeze',{'mode':'run','run':RUN}),
                          ('wiki_root','/wrong-root'),('activation_authorized',False),('hash','0'*64)]:
            with self.subTest(field=field):
                doc=dict(scope)
                if field!='hash':doc[field]=bad
                self.f.put(ref,C.encoded(doc))
                self.f.approval.update(scope_approval_ref=ref,scope_approval_sha256='0'*64 if field=='hash' else C.sha(self.f.fs.read(ref)))
                self.f.put(APPROVAL,C.encoded(self.f.approval))
                with self.assertRaisesRegex(ValueError,'scope_approval'):
                    daily.preflight(**self.f.kw())
        self.f.put(ref,C.encoded(scope))
        self.f.approval['scope_approval_sha256']=C.sha(self.f.fs.read(ref))
        self.f.put(APPROVAL,C.encoded(self.f.approval))
        ctx=daily.preflight(**self.f.kw())
        self.assertEqual(ctx['snapshots'][ref],self.f.approval['scope_approval_sha256'])
        self.f.put(ref,C.encoded(dict(scope,approved=False)))
        with self.assertRaises(ValueError):ctx['guard']()

    def test_committed_batch_reports_unselected_and_old_blocked_backlog_separately(self):
        from test_integration import Model
        for n in range(2,8):self.f.source(f'2610.{n:05d}v1')
        items=daily.inventory(daily.preflight(**self.f.kw()))
        items[-1].update(status='blocked_conflict',reason='prior unknown HTTP502; explicit approval required')
        self.f.state['items']=items;self.f.bind()
        model=Model()
        result=daily.run_daily(**self.f.kw(),client_factory=model,clock=lambda:0.0)
        self.assertEqual(result['status'],'committed')
        self.assertEqual(result['inventory_count'],7)
        self.assertEqual(len(result['selected']),5)
        self.assertEqual(result['remaining_count'],2)
        self.assertEqual(result['deferred'],['2610.00006v1'])
        self.assertEqual(result['blocked_count'],1)
        self.assertEqual(result['blocked'][0]['version_id'],'2610.00007v1')
        self.assertEqual(result['blocked'][0]['status'],'blocked_conflict')
        self.assertFalse(result['all_papers_done'])
        self.assertEqual(len(model.calls),10)
        self.assertEqual(C.decode(self.f.fs.read(RUN+'/daily-report.json')),result)

    def test_expired_semantic_dispatch_preserves_persisted_generation_references(self):
        from test_integration import Model
        model=Model();elapsed=[0.0]
        def factory(**kwargs):
            client=model(**kwargs);original=client.responses.create
            def create(**request):
                result=original(**request)
                if len(model.calls)==2:elapsed[0]=11.0
                return result
            client.responses.create=create
            return client
        result=daily.run_daily(**self.f.kw(),client_factory=factory,clock=lambda:elapsed[0])
        self.assertEqual(result['status'],'unknown')
        evidence=C.decode(self.f.fs.read(PREFIX+'-outcome.json'))
        self.assertEqual(set(evidence['artifacts']),{'result','report'})
        for name,ref in evidence['artifacts'].items():
            self.assertEqual(ref['path'],PREFIX+'-'+name+'.json')
            self.assertEqual(ref['sha256'],C.sha(self.f.fs.read(ref['path'])))

    def test_publication_contention_retains_operator_recovery_not_silent_reading(self):
        import content
        from contextlib import ExitStack
        from test_integration import Model
        locks=ExitStack();self.addCleanup(locks.close);model=Model()
        def processor(ctx,**kw):
            bundle=content.process(ctx,**kw)
            locks.enter_context(C.helper('publish').collection_lock(ctx['fs'],'collector','busy',ctx['now']))
            return bundle
        result=daily.run_daily(**self.f.kw(),processor=processor,client_factory=model,clock=lambda:0.0)
        self.assertEqual(result['status'],'unknown')
        self.assertTrue(result['outcomes'][0]['operator_recovery_required'])
        self.assertTrue((self.f.root/(PREFIX+'-publication-unknown.json')).exists())
        self.assertFalse((self.f.root/(PREFIX+'-outcome.json')).exists())
        self.assertEqual(len(model.calls),2)
        locks.close()
        self.assertEqual(daily.recover_publication(**self.f.kw(),version_id=VID,attempt=1)['status'],'published_auto_verified')
        self.assertEqual(len(model.calls),2)

    def test_same_transaction_recovery_cannot_outlive_its_scheduled_occurrence(self):
        import publication
        from test_integration import Model
        original=publication.publish;elapsed=[0.0]
        def crash(stage):
            if stage=='after_basis':raise RuntimeError('stop before WAL')
        with patch.object(publication,'publish',lambda ctx,bundle,**kw:original(ctx,bundle,hook=crash,**kw)):
            result=daily.run_daily(**self.f.kw(),client_factory=Model(),clock=lambda:0.0)
        self.assertEqual(result['status'],'unknown')
        def expire(stage):
            if stage=='after_basis':elapsed[0]=11.0
        with patch.object(daily.time,'monotonic',lambda:elapsed[0]),patch.object(
            publication,'publish',lambda ctx,bundle,**kw:original(ctx,bundle,hook=expire,**kw)):
            with self.assertRaises(TimeoutError):
                daily.recover_publication(**self.f.kw(),version_id=VID,attempt=1)
        self.assertFalse(list((self.f.root/'entities').iterdir()))
        self.assertFalse((self.f.root/(PREFIX+'-publish-journal.json')).exists())

    def test_terminal_cleanup_never_bypasses_changed_authority_or_ownership(self):
        for changed in ('approval','policy','runtime','owner','reservation','item','safety_block'):
            with self.subTest(changed=changed):
                f=ScheduledFixture();self.addCleanup(f.close);f.source(VID)
                elapsed=[0.0];state_after=[];calls=[]
                def processor(ctx,**kw):
                    calls.append(1)
                    if changed=='approval':f.put(APPROVAL,C.encoded(dict(f.approval,approved=False)))
                    elif changed=='policy':f.put(C.PROMPT,b'drift')
                    elif changed=='runtime':f.put(sorted(DEPENDENCIES)[0],b'drift')
                    elif changed=='owner':f.put(daily.RUN_LOCK+'/owner.json',C.encoded({'token':'foreign'}))
                    elif changed=='reservation':
                        r=C.decode(f.fs.read(PREFIX+'-reservation.json'));r['attempt']=2
                        f.put(PREFIX+'-reservation.json',C.encoded(r))
                    else:
                        state=C.decode(f.fs.read(C.STATE))
                        if changed=='item':state['items'][0]['resume_at']='foreign-attempt'
                        else:state.update(safety_block=True,safety_block_reason='operator safety stop')
                        f.put(C.STATE,C.encoded(state))
                    state_after.append(f.fs.read(C.STATE));elapsed[0]=11.0
                    raise TimeoutError('expired dispatch')
                with self.assertRaises(ValueError):
                    daily.run_daily(**f.kw(),processor=processor,clock=lambda:elapsed[0])
                self.assertEqual(calls,[1])
                self.assertEqual(f.fs.read(C.STATE),state_after[0])
                self.assertFalse((f.root/(PREFIX+'-outcome.json')).exists())
                self.assertFalse((f.root/(RUN+'/daily-report.json')).exists())

    def test_expired_outcome_survives_collection_contention_and_cannot_overwrite(self):
        from contextlib import ExitStack
        locks=ExitStack();self.addCleanup(locks.close);elapsed=[0.0];calls=[]
        def processor(ctx,**kw):
            calls.append(1)
            locks.enter_context(C.helper('publish').collection_lock(ctx['fs'],'collector','busy',ctx['now']))
            elapsed[0]=11.0
            raise TimeoutError('unknown dispatch')
        result=daily.run_daily(**self.f.kw(),processor=processor,clock=lambda:elapsed[0])
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(result['state_reconciliation'],'pending')
        self.assertEqual(result['unresolved'],[VID])
        before=self.f.fs.read(PREFIX+'-outcome.json')
        locks.close()
        self.assertEqual(daily.reconcile_outcomes(**self.f.kw())['status'],'reconciled')
        self.assertEqual(daily.reconcile_outcomes(**self.f.kw())['status'],'noop')
        self.assertEqual(self.f.fs.read(PREFIX+'-outcome.json'),before)
        with self.assertRaisesRegex(ValueError,'completed_run_use_fresh_id'):
            daily.run_daily(**self.f.kw(),processor=lambda *a,**k:self.fail('must not replay'))
        self.assertEqual(calls,[1])
        self.assertEqual(self.f.fs.read(PREFIX+'-outcome.json'),before)

    def test_runtime_guard_rehashes_all_dependencies_and_aware_next_run_can_advance(self):
        for path in sorted(DEPENDENCIES):
            with self.subTest(path=path):
                ctx=daily.preflight(**self.f.kw());before=self.f.fs.read(path)
                self.f.put(path,before+b'\n# drift\n')
                with self.assertRaisesRegex(ValueError,'runtime_dependency_changed'):ctx['guard']()
                self.f.put(path,before)
        later=dict(self.f.job,next_run_at='2026-11-03T17:00:00+00:00')
        ctx=daily.preflight(**dict(self.f.kw(),scheduler_observer=lambda _:later))
        self.assertEqual(ctx['approval']['mode'],'scheduled')
        for stamp in ('2026-11-03T17:00:00','not-a-date'):
            with self.assertRaises(ValueError):
                daily.preflight(**dict(self.f.kw(),scheduler_observer=lambda _:dict(later,next_run_at=stamp)))

    def test_expiry_at_publication_guard_leaves_next_target_untouched(self):
        import publication
        from test_integration import Model
        elapsed=[0.0];original=publication.publish
        before={p:self.f.fs.read(p) for p in ('index.md','log.md')}
        def expire(stage):
            if stage=='after_journal':elapsed[0]=11.0
        with patch.object(publication,'publish',lambda ctx,bundle,**kw:original(ctx,bundle,hook=expire,**kw)):
            result=daily.run_daily(**self.f.kw(),client_factory=Model(),clock=lambda:elapsed[0])
        self.assertEqual(result['status'],'unknown')
        self.assertTrue((self.f.root/(PREFIX+'-publish-journal.json')).exists())
        self.assertFalse(list((self.f.root/'entities').iterdir()))
        for path,data in before.items():self.assertEqual(self.f.fs.read(path),data)

if __name__=='__main__':unittest.main(verbosity=2)
