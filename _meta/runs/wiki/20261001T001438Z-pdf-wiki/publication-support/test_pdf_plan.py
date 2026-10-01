"""Synthetic filesystem only. Never open live PDF/result/Wiki content."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

SUPPORT = Path(__file__).parent
REPO = SUPPORT.parents[4]
RUN = '_meta/runs/wiki/20261001T001438Z-pdf-wiki'
VERSIONS = ('2609.30614v1', '2609.30824v1')
POLICY = 'pkm-html-pdf-text-knowledge/v3'
CONTRACT = 'pkm-contracts/v3'
SCOPE = 'manual PDF embedded-text complete'
STATE = '_meta/state/compilation.json'
DOCS = ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/COMPILATION.md',
        '_meta/STATE-CONTRACTS.md', '_meta/automation-contracts.schema.json')
MODEL = dict(provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh')
ROUTE = dict(base_url='http://10.10.1.244:2455/v1', api_mode='codex_responses')
NOW = datetime(2026, 10, 1, 3, tzinfo=timezone.utc)

def load(path, name):
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), mod.__dict__)
    return mod

G = load(REPO / '_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py', 'synthetic_generic')

class Fixture:
    def __init__(self, root):
        self.root = root
        for d in ('entities', 'concepts', 'comparisons', 'queries', '_meta/locks', RUN+'/publications', RUN+'/reviews'):
            (root/d).mkdir(parents=True, exist_ok=True)
        # Only live input copied is the approved schema, never data/state/papers.
        self.schema = G.decode((REPO/'_meta/automation-contracts.schema.json').read_bytes())
        for p in DOCS:
            self.put(p, G.encoded(self.schema) if p.endswith('.json') else (POLICY+'\n').encode())
        self.put('SCHEMA.md', (POLICY+'\n## 7. 태그\n`paper`\n').encode())
        self.put('_meta/automation.json', G.encoded(dict(policy_revision=POLICY, contract_revision=CONTRACT)))
        self.put('_meta/prompts/wiki-compile.md', ('wiki-compile/v3\n'+POLICY).encode())
        self.put(RUN+'/runtime/instructions.md', b'SYNTHETIC instructions, not research data')
        self.put(RUN+'/scope-approval.json', G.encoded(dict(schema='pkm-pdf-text-scope-approval/v1',
            wiki_root=str(root), run_id=Path(RUN).name, version_ids=list(VERSIONS),
            validated_publication_authorized=True, publication_edit_freeze_confirmed=True,
            cost_policy='no_cost_cap', model=dict(**MODEL, fallback_allowed=False))))
        self.sources, items = {}, []
        for vid in VERSIONS:
            source = f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.pdf'
            # Not a PDF and never parsed: a hash-only sentinel for transaction tests.
            data = ('SYNTHETIC HASH SENTINEL '+vid).encode()
            self.put(source, data)
            meta = dict(schema='arxiv-pdf-source/v1', version_id=vid, title='Synthetic '+vid,
                        pdf_sha256=G.sha(data), pdf_bytes=len(data))
            self.put(source.replace('.pdf', '.json'), G.encoded(meta))
            refs = dict(source_path=source, source_sha256=G.sha(data), source_bytes=len(data),
                        metadata_path=source.replace('.pdf', '.json'), metadata_sha256=self.hash(source.replace('.pdf', '.json')))
            self.sources[vid] = refs
            items.append(dict(source='arxiv', version_id=vid, format='pdf', **refs, collected_at=NOW.isoformat(),
                status='queued', reason='Synthetic parent gate observed', requested_scope=None, read_scope=[],
                unread_scope=[], resume_at=None, work_key=None, output_refs=[], receipt_ref=None,
                failure_count=0, human_review=None))
        self.approval = dict(schema='pkm-pdf-text-run-approval/v1', approved=True, wiki_root=str(root),
            run_id=Path(RUN).name, version_ids=list(VERSIONS), **MODEL, policy_revision=POLICY,
            contract_revision=CONTRACT, prompt_revision='wiki-compile/v3',
            policy_sha256=self.hash('_meta/automation.json'), prompt_sha256=self.hash('_meta/prompts/wiki-compile.md'),
            document_sha256={p:self.hash(p) for p in DOCS}, instructions_path=RUN+'/runtime/instructions.md',
            instructions_sha256=self.hash(RUN+'/runtime/instructions.md'), sources=self.sources, wiki_inputs=[],
            scope_approval_sha256=self.hash(RUN+'/scope-approval.json'), approved_route=ROUTE,
            publication_edit_freeze_confirmed=True, validated_publication_authorized=True, max_attempts_per_item=2)
        self.put(RUN+'/execution-approval.json', G.encoded(self.approval))
        self.state = dict(schema='pkm-compilation-state/v1', policy_revision=POLICY, contract_revision=CONTRACT,
            initialized_at=NOW.isoformat(), enabled=False, safety_block=False, safety_block_reason=None,
            items=items, transactions=[], receipts=[], cost_events=[], last_run=None)
        self.put(STATE, G.encoded(self.state))
        self.put('index.md', b'# Synthetic\n> Last updated: 2026-10-01 | Total pages: 0\n\n## Entities\n\n## Concepts\n\n')
        self.put('log.md', b'# Synthetic log\n')
        self.fs = G.Files(root)

    def put(self, path, data):
        p = self.root/path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def hash(self, path):
        return G.sha((self.root/path).read_bytes())

    def descriptor(self, path, value):
        self.put(path, G.encoded(value))
        return dict(path=path, sha256=self.hash(path), value=value)

    def inputs(self, vid):
        a = self.approval
        record = {k:copy.deepcopy(a[k]) for k in ('provider','model','reasoning_effort','policy_revision',
            'contract_revision','prompt_revision','policy_sha256','prompt_sha256','document_sha256',
            'scope_approval_sha256','instructions_path','instructions_sha256','sources','wiki_inputs','approved_route')}
        record.update(version_id=vid, vid=vid, run_id=Path(RUN).name, approval_ref=RUN+'/execution-approval.json',
            approval_sha256=self.hash(RUN+'/execution-approval.json'), http_timeout_s=2400, **a['sources'][vid])
        source = a['sources'][vid]['source_path']
        doc = dict(title='Synthetic '+vid, summary='Synthetic metadata-only contract check.', version_id=vid,
            main_text_complete=True, read_scope=['page=1'], unread_scope=['Images not reviewed'],
            limitations=['Synthetic fixture, not a paper'],
            claims=[dict(id='C01',kind='author_report',statement='Synthetic claim',conditions='Test only',
                         anchor='page=1',quote='Synthetic quote')],
            markdown_body=f'# Synthetic\nC01 합성 계약 검사 ^[{source}#page=1]\nImages not reviewed\n\n')
        result = self.descriptor(RUN+'/runtime/'+vid+'/attempt1-result.json', dict(record,
            schema='pkm-pdf-text-attempt-result/v1', attempt='attempt1', completed=True, response_status='completed',
            response_model=MODEL['model'], error=None, response_error=None, incomplete_details=None,
            text=json.dumps(doc, ensure_ascii=False), cost_usd=None, started_at=NOW.isoformat(), finished_at=NOW.isoformat()))
        report = self.descriptor(RUN+'/reviews/'+vid+'-attempt1-verification.json', dict(
            schema='pkm-pdf-text-verification/v1',version_id=vid,passed=True,
            checks=[dict(check='synthetic_parent_observation',ok=True)], document=doc,
            semantic_review='not_performed',publication='not_performed'))
        paths = list(DOCS)+['_meta/automation.json','_meta/prompts/wiki-compile.md', STATE,
            RUN+'/scope-approval.json', RUN+'/execution-approval.json', a['instructions_path']]
        paths += [x['metadata_path'] for x in self.sources.values()]
        report.update(preflight=dict(record=record, snapshots={p:self.hash(p) for p in paths}),
                      observed_at=NOW.isoformat(), observers=['manual_pdf.preflight','manual_pdf.verify_result'])
        review = self.descriptor(RUN+'/reviews/'+vid+'-attempt1-agent-review.json', dict(
            schema='pkm-pdf-agent-evidence-review/v1', actor='agent', reviewer='synthetic reviewer',
            reviewed_at=NOW.isoformat(), version_id=vid, passed=True, human_review_ref=None,
            result_sha256=result['sha256'], mechanical_report_sha256=report['sha256'],
            source_sha256=record['source_sha256'], approval_sha256=record['approval_sha256'],
            policy_sha256=record['policy_sha256'], prompt_sha256=record['prompt_sha256'],
            requested_scope=SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
            evidence_scope=['page=1'], reviewed_claim_ids=['C01'], claims=[dict(id='C01',anchor='page=1',
            quote_sha256=G.sha(b'Synthetic quote'),verdict='supported',rationale='Synthetic condition and quote agree.')]))
        return result, report, review

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-', dir=SUPPORT)
        self.addCleanup(self.tmp.cleanup)
        self.f = Fixture(Path(self.tmp.name))
        path = SUPPORT/'pdf_plan.py'
        self.assertTrue(path.exists(), 'MISSING_IMPLEMENTATION: pdf_plan.py')
        self.b = load(path, 'synthetic_pdf_plan')
        # Only our new module's ROOT is injected; generic helper guards/constants stay unchanged.
        self.patch = patch.object(self.b, 'ROOT', self.f.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def commit(self, vid, result, report, review, hook=lambda stage:None):
        p = self.b.build_plan(self.f.fs,vid,RUN,result,report,review,NOW)
        self.assertTrue(callable(getattr(self.b,'validate_plan',None)), 'MISSING_IMPLEMENTATION: validate_plan')
        with self.b.collection_lock(self.f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
            self.assertTrue(owned)
            context = self.b.validate_plan(self.f.fs,p,vid,RUN,result,report,review,NOW)
            self.b.write_journal(self.f.fs,p)
            self.b.apply_plan(self.f.fs,p,context,hook,owned)
            self.b.verify_committed(self.f.fs,p,context,vid)
        return p, context

    def test_two_success_plans_and_repeat_generic_noop(self):
        saved = []
        for vid in VERSIONS:
            inputs = self.f.inputs(vid)
            plan, context = self.commit(vid,*inputs)
            saved.append((vid,plan,context,inputs))
            self.assertEqual(plan['status'],'committed')
            self.assertEqual(plan['receipt']['cost_usd'],None)
            expected_work = dict(source='arxiv',version_id=vid,source_sha256=inputs[0]['value']['source_sha256'],
                policy_revision=POLICY,policy_sha256=inputs[0]['value']['policy_sha256'],prompt_revision='wiki-compile/v3',
                prompt_sha256=inputs[0]['value']['prompt_sha256'],requested_scope=SCOPE)
            self.assertEqual(plan['work_key'],G.sha(G.canonical(expected_work)))
            self.assertEqual(G.decode(self.f.fs.read(plan['journal_path']))['plan_sha256'],G.sha(G.canonical(plan)))
        before = {str(p):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        for _ in range(2):
            for vid,p,context,inputs in saved:
                with self.b.collection_lock(self.f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
                    self.assertTrue(owned)
                    self.b.validate_plan(self.f.fs,p,vid,RUN,*inputs,NOW)
                    self.b.verify_committed(self.f.fs,p,context,vid)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()})
        self.assertEqual(G.page_count(self.f.fs,saved[0][1]['targets'][0]['path']),2)

    def test_review_unknown_human_flag_rejected(self):
        vid = VERSIONS[0]
        result, report, review = self.f.inputs(vid)
        review['value']['human_reviewed'] = True
        review.update(self.f.descriptor(review['path'],review['value']))
        with self.assertRaises(ValueError):
            self.b.build_plan(self.f.fs,vid,RUN,result,report,review,NOW)

    def test_all_interrupted_stages_recover(self):
        for stage in ('after_page','after_index','after_log','after_receipt','after_state'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory(prefix='synthetic-',dir=SUPPORT) as root:
                f = Fixture(Path(root))
                with patch.object(self.b,'ROOT',f.root):
                    vid = VERSIONS[0]
                    inputs = f.inputs(vid)
                    p = self.b.build_plan(f.fs,vid,RUN,*inputs,NOW)
                    def stop(current):
                        if current == stage: raise RuntimeError('synthetic interruption '+stage)
                    with self.b.collection_lock(f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
                        context = self.b.validate_plan(f.fs,p,vid,RUN,*inputs,NOW)
                        self.b.write_journal(f.fs,p)
                        with self.assertRaisesRegex(RuntimeError,'synthetic interruption'):
                            self.b.apply_plan(f.fs,p,context,stop,owned)
                    # Re-read the actual persisted envelope, not the mutated in-memory plan.
                    envelope = G.decode(f.fs.read(p['journal_path']))
                    self.assertEqual(envelope['plan_sha256'],G.sha(G.canonical(envelope['plan'])))
                    p = envelope['plan']
                    with self.b.collection_lock(f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
                        context = self.b.validate_plan(f.fs,p,vid,RUN,*inputs,NOW)
                        self.b.apply_plan(f.fs,p,context,lambda _:None,owned)
                        self.b.verify_committed(f.fs,p,context,vid)
                    self.assertEqual(p['status'],'committed')
                    self.assertEqual(f.fs.read('log.md').count(p['log']['event'].encode()),1)

    def test_unexpected_target_and_input_edits_refused_before_recovery_write(self):
        for changed in ('page','index','log','receipt','state','structural','source'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory(prefix='synthetic-',dir=SUPPORT) as root:
                f = Fixture(Path(root))
                with patch.object(self.b,'ROOT',f.root):
                    vid = VERSIONS[0]
                    inputs = f.inputs(vid)
                    p = self.b.build_plan(f.fs,vid,RUN,*inputs,NOW)
                    context = self.b.validate_plan(f.fs,p,vid,RUN,*inputs,NOW)
                    self.b.write_journal(f.fs,p)
                    def stop(stage):
                        if stage == 'after_page': raise RuntimeError('synthetic interruption')
                    with self.b.collection_lock(f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
                        with self.assertRaises(RuntimeError): self.b.apply_plan(f.fs,p,context,stop,owned)
                    paths = dict(page=p['targets'][0]['path'],index='index.md',log='log.md',
                        receipt=p['targets'][3]['path'],state=STATE,structural=p['structural_path'],
                        source=inputs[0]['value']['source_path'])
                    path = paths[changed]
                    old = f.fs.read(path,True) or b''
                    if changed == 'index': new = old.replace(b'## Entities',b'## Entities\nEdited owned section')
                    elif changed == 'log': new = b'Changed prefix\n'+old
                    else: new = old+b'\n'
                    f.put(path,new)
                    before = {str(p):p.read_bytes() for p in f.root.rglob('*') if p.is_file()}
                    with self.b.collection_lock(f.fs,Path(RUN).name,p['transaction_id'],NOW) as owned:
                        with self.assertRaises((ValueError,KeyError,TypeError)):
                            context = self.b.validate_plan(f.fs,p,vid,RUN,*inputs,NOW)
                            self.b.apply_plan(f.fs,p,context,lambda _:None,owned)
                    self.assertEqual(before,{str(p):p.read_bytes() for p in f.root.rglob('*') if p.is_file()})

    def test_scope_hash_symlink_and_output_conflicts(self):
        inputs = self.f.inputs(VERSIONS[0])
        for vid,run in [('2609.30614',RUN),('2609.99999v1',RUN),(VERSIONS[0],RUN+'-other')]:
            with self.subTest(vid=vid,run=run), self.assertRaises(ValueError):
                self.b.build_plan(self.f.fs,vid,run,*inputs,NOW)
        with patch.object(self.b,'ROOT',Path('/unapproved-root')), self.assertRaises(ValueError):
            self.b.build_plan(self.f.fs,VERSIONS[0],RUN,*inputs,NOW)
        for which in range(3):
            with self.subTest(descriptor=which):
                bad = copy.deepcopy(inputs)
                bad[which]['sha256'] = '0'*64
                with self.assertRaises(ValueError): self.b.build_plan(self.f.fs,VERSIONS[0],RUN,*bad,NOW)
        source = self.f.root/inputs[0]['value']['source_path']
        original = source.read_bytes()
        source.unlink()
        source.symlink_to(self.f.root/'SCHEMA.md')
        with self.assertRaises((ValueError,OSError)): self.b.build_plan(self.f.fs,VERSIONS[0],RUN,*inputs,NOW)
        source.unlink()
        source.write_bytes(original)
        output = f'entities/arxiv-{VERSIONS[0]}.md'
        self.f.put(output,b'Existing user page')
        with self.assertRaisesRegex(ValueError,'existing output'): self.b.build_plan(self.f.fs,VERSIONS[0],RUN,*inputs,NOW)
        self.assertEqual(self.f.fs.read(output),b'Existing user page')

    def test_plan_tampering_and_unknown_status_rejected(self):
        vid = VERSIONS[0]
        inputs = self.f.inputs(vid)
        p = self.b.build_plan(self.f.fs,vid,RUN,*inputs,NOW)
        changes = [lambda p:p.update(status='unknown'),lambda p:p.update(work_key='0'*64),
            lambda p:p['targets'][0].update(path='entities/other.md'),
            lambda p:p['targets'][0].update(after_image='forged'),
            lambda p:p['state_after']['items'][1].update(reason='unrelated rewrite'),
            lambda p:p['receipt'].update(human_review_ref='claimed'),
            lambda p:p['log'].update(event='forged event'),
            lambda p:p.update(page_count=99),lambda p:p.update(before_state=p['before_state']+'\n')]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                bad = copy.deepcopy(p)
                change(bad)
                with self.assertRaises((ValueError,KeyError,TypeError)):
                    self.b.validate_plan(self.f.fs,bad,vid,RUN,*inputs,NOW)

    def test_execution_binding_and_state_rejections(self):
        cases = ('wrong_model', 'wrong_response_model', 'wrong_route', 'incomplete', 'attempt3',
            'wrong_result_path', 'missing_preflight_document', 'wrong_preflight_record', 'wrong_observer',
            'wrong_document_commitment', 'wrong_approval_commitment', 'blocked_target', 'blocked_peer',
            'unknown_status', 'human_review_item', 'duplicate_item', 'unresolved_transaction',
            'safety_block', 'automation_enabled')
        for name in cases:
            with self.subTest(name=name):
                self.f = Fixture(self.f.root)
                result, report, review = self.f.inputs(VERSIONS[0])
                r, pf = result['value'], report['preflight']
                if name == 'wrong_model':
                    r['model'] = pf['record']['model'] = 'other-model'
                elif name == 'wrong_response_model': r['response_model'] = 'other-model'
                elif name == 'wrong_route': r['approved_route'] = pf['record']['approved_route'] = {'base_url':'wrong','api_mode':'wrong'}
                elif name == 'incomplete': r['completed'] = False
                elif name == 'attempt3': r['attempt'] = 'attempt3'
                elif name == 'wrong_result_path': result['path'] = RUN+'/reviews/wrong-result.json'
                elif name == 'missing_preflight_document': pf['snapshots'].pop('AGENTS.md')
                elif name == 'wrong_preflight_record': pf['record']['source_bytes'] += 1
                elif name == 'wrong_observer': report['observers'] = ['fabricated preflight']
                elif name == 'wrong_document_commitment': r['document_sha256'] = pf['record']['document_sha256'] = {'wrong':'0'*64}
                elif name == 'wrong_approval_commitment': r['approval_sha256'] = pf['record']['approval_sha256'] = '0'*64
                elif name == 'blocked_target': self.f.state['items'][0]['status'] = 'blocked_approval'
                elif name == 'blocked_peer': self.f.state['items'][1]['status'] = 'blocked_approval'
                elif name == 'unknown_status': self.f.state['items'][0]['status'] = 'unknown'
                elif name == 'human_review_item':
                    self.f.state['items'][0]['human_review'] = dict(actor='user',reviewed_at=NOW.isoformat(),
                        page_sha256='0'*64,scope='Synthetic',evidence_ref='synthetic.json')
                elif name == 'duplicate_item': self.f.state['items'].append(copy.deepcopy(self.f.state['items'][0]))
                elif name == 'unresolved_transaction': self.f.state['transactions'].append(dict(transaction_id='x',journal_path='x.json',status='prepared'))
                elif name == 'safety_block': self.f.state['safety_block'] = True
                elif name == 'automation_enabled': self.f.state['enabled'] = True
                self.f.put(STATE,G.encoded(self.f.state))
                pf['snapshots'][STATE] = self.f.hash(STATE)
                result.update(self.f.descriptor(result['path'],r))
                review['value'].update(result_sha256=result['sha256'],approval_sha256=r['approval_sha256'])
                review.update(self.f.descriptor(review['path'],review['value']))
                with self.assertRaises((ValueError,KeyError,TypeError)):
                    self.b.build_plan(self.f.fs,VERSIONS[0],RUN,result,report,review,NOW)

    def test_semantic_review_and_mechanical_report_rejections(self):
        vid = VERSIONS[0]
        cases = {
            'missing_claim': lambda r,v: v.update(reviewed_claim_ids=[]),
            'missing_claim_detail': lambda r,v: v.update(claims=[]),
            'missing_rationale': lambda r,v: v['claims'][0].update(rationale=''),
            'unsupported_claim': lambda r,v: v['claims'][0].update(verdict='uncertain'),
            'wrong_quote_hash': lambda r,v: v['claims'][0].update(quote_sha256='0'*64),
            'review_passed_absent': lambda r,v: v.pop('passed'),
            'mechanical_passed_absent': lambda r,v: r.pop('passed'),
            'mechanical_check_failed': lambda r,v: r['checks'][0].update(ok=False),
            'report_claims_not_generated': lambda r,v: r['document'].update(summary='Modified summary'),
            'review_human_claim': lambda r,v: v.update(human_review_ref='unobserved-user-review'),
            'review_not_agent': lambda r,v: v.update(actor='user'),
            'wrong_result_binding': lambda r,v: v.update(result_sha256='0'*64),
            'wrong_source_binding': lambda r,v: v.update(source_sha256='0'*64),
            'wrong_mechanical_binding': lambda r,v: v.update(mechanical_report_sha256='0'*64),
            'wrong_read_scope': lambda r,v: v.update(read_scope=['page=2']),
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                result, report, review = self.f.inputs(vid)
                change(report['value'], review['value'])
                for d in (report, review):
                    d.update(self.f.descriptor(d['path'],d['value']))
                with self.assertRaises((ValueError,KeyError,TypeError)):
                    self.b.build_plan(self.f.fs, vid, RUN, result, report, review, NOW)

    def test_minimal_draft_plan_is_read_only(self):
        vid = VERSIONS[0]
        result, report, review = self.f.inputs(vid)
        before = {str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        plan = self.b.build_plan(self.f.fs, vid, RUN, result, report, review, NOW)
        self.assertEqual(plan['schema'], 'pkm-publication-journal/v1')
        self.assertEqual(len(plan['targets']), 5)
        self.assertTrue(plan['targets'][0]['after_image'].endswith(report['value']['document']['markdown_body']))
        self.assertIn('summary: "Synthetic metadata-only contract check."', plan['targets'][0]['after_image'])
        self.assertIn('review_state: "unreviewed"', plan['targets'][0]['after_image'])
        self.assertNotIn(STATE, plan['input_hashes'])
        self.assertEqual(plan['targets'][4]['before_hash'], self.f.hash(STATE))
        self.assertEqual(before, {str(p.relative_to(self.f.root)):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()})
        G.schema_validate(self.f.schema, plan['state_after'], 'compilation')

if __name__ == '__main__':
    unittest.main(verbosity=2)
