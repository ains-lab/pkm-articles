"""Outcome durability under collection contention; never real model/state IO."""
from contextlib import ExitStack
from contextlib import redirect_stdout
from unittest.mock import patch
import io
import unittest
from typing import Any
import daily
import p3_common as C
from test_daily import Fixture, RUN, NOW

class ContentionTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.addCleanup(self.f.close)
        self.f.source('2610.00001v1')
    def test_reservation_busy_is_reported_without_model_or_reading_state(self):
        P=C.helper('publish');kw: Any=self.f.kw()
        with P.collection_lock(self.f.fs,'synthetic-collector','busy',NOW) as owns:
            self.assertTrue(owns)
            result=daily.run_daily(**kw,processor=lambda *a,**k:self.fail('must not invoke'))
            self.assertEqual(result['status'],'skipped_busy')
            self.assertEqual(C.decode(self.f.fs.read(C.STATE))['items'],[])
            self.assertFalse(list(self.f.root.glob('**/*-reservation.json')))
            owns()

    def test_known_unknown_outcome_survives_busy_and_reconciles_without_replay(self):
        kw: Any=self.f.kw();locks=ExitStack();self.addCleanup(locks.close);calls=[]
        def processor(ctx,**kwargs):
            calls.append(1)
            locks.enter_context(C.helper('publish').collection_lock(ctx['fs'],'synthetic-collector','busy',NOW))
            return dict(status='unknown')
        result=daily.run_daily(**kw,processor=processor)
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(result['state_reconciliation'],'pending')
        prefix=RUN+'/items/2610.00001v1/attempt1'
        self.assertEqual(C.decode(self.f.fs.read(prefix+'-outcome.json'))['status'],'unknown')
        self.assertEqual(C.decode(self.f.fs.read(C.STATE))['items'][0]['status'],'reading')
        locks.close()
        result=daily.reconcile_outcomes(**kw)
        self.assertEqual(result['status'],'reconciled')
        state=self.f.fs.read(C.STATE)
        self.assertEqual(C.decode(state)['items'][0]['status'],'blocked_conflict')
        self.assertEqual(len(C.decode(state)['cost_events']),1)
        self.assertEqual(daily.reconcile_outcomes(**kw)['status'],'noop')
        self.assertEqual(self.f.fs.read(C.STATE),state)
        self.assertEqual(calls,[1])

    def test_reconciliation_cli_dispatches_without_regeneration(self):
        args=['--run',RUN,'--approval-ref',RUN+'/execution-approval.json','--reconcile-outcomes']
        with patch.object(daily,'reconcile_outcomes',return_value={'status':'reconciled','reconciled':1}) as call,redirect_stdout(io.StringIO()):
            self.assertEqual(daily.main(args),0)
        call.assert_called_once_with(run=RUN,approval_ref=RUN+'/execution-approval.json')

    def test_reconciliation_refuses_drift_and_recovers_state_write_interruption_once(self):
        kw: Any=self.f.kw();ctx=daily.preflight(**kw)
        with daily.run_lock(ctx):
            item=daily.inventory(ctx)[0];prepared=daily.reserve(ctx,item,1)
            original=ctx['fs'].write
            def crash(path,*a,**k):
                if path==C.STATE:raise RuntimeError('state write interrupted')
                return original(path,*a,**k)
            with patch.object(ctx['fs'],'write',crash),self.assertRaisesRegex(RuntimeError,'state write interrupted'):
                daily.record_outcome(prepared,dict(status='retryable_failed'))
        state=self.f.fs.read(C.STATE)
        source=item['source_path'];before=self.f.fs.read(source)
        self.f.put(source,before+b'drift')
        with self.assertRaises(ValueError):daily.reconcile_outcomes(**kw)
        self.assertEqual(self.f.fs.read(C.STATE),state)
        self.f.put(source,before)
        self.assertEqual(daily.reconcile_outcomes(**kw)['status'],'reconciled')
        state=self.f.fs.read(C.STATE)
        self.assertEqual(C.decode(state)['items'][0]['failure_count'],1)
        self.assertEqual(daily.reconcile_outcomes(**kw)['status'],'noop')
        self.assertEqual(self.f.fs.read(C.STATE),state)

if __name__=='__main__':unittest.main(verbosity=2)
