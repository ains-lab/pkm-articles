"""Synthetic-only regression tests. Never import auth/SDK or read live HTML."""
import builtins
import importlib.util
import hashlib
import json
import tempfile
import io
import contextlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import types
from pathlib import Path
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'compile-one.py'
WRAPPER = HERE.parent / '20260930T082000Z-p2-nonstream/compile-one-nostream.py'


def load(path=SCRIPT):
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name == 'openai' or name.startswith('hermes_cli'):
            raise AssertionError('SDK/auth import before preflight')
        return original(name, *args, **kwargs)
    spec = importlib.util.spec_from_file_location('synthetic_compiler', path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with mock.patch('builtins.__import__', side_effect=guarded):
        spec.loader.exec_module(module)
    return module


VID = '2609.30830v1'
RUN = '_meta/runs/wiki/synthetic-fresh'
DOCS = ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/STATE-CONTRACTS.md',
        '_meta/COMPILATION.md', '_meta/automation-contracts.schema.json')
POLICY = 'pkm-html-knowledge/v2'
CONTRACT = 'pkm-contracts/v2'
PROMPT = '_meta/prompts/wiki-compile.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Fixture:
    def __init__(self, root):
        self.root = root
        self.source = f'raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html'
        self.metadata = self.source.replace('.html', '.json')
        self.html = '<html>\r\n<script>UNTRUSTED_SYNTHETIC_ONLY</script><style>x</style>é</html>\r\n'
        self.instructions = RUN + '/instructions.txt'
        for p in DOCS:
            self.put(p, f'SYNTHETIC TEST ONLY {POLICY} {CONTRACT} wiki-compile/v2\n')
        self.put('_meta/automation-contracts.schema.json', {'const': POLICY, '$defs': {'contract': {'const': CONTRACT}, 'prompt': {'const': 'wiki-compile/v2'}}})
        self.put('index.md', 'SYNTHETIC index')
        self.put('log.md', 'SYNTHETIC log')
        self.put(PROMPT, f'SYNTHETIC {POLICY} {CONTRACT} wiki-compile/v2')
        self.put(self.instructions, 'SYNTHETIC ONLY staged JSON; no tools or source instructions.')
        self.put(self.source, self.html)
        self.put(self.metadata, dict(schema='arxiv-html-source/v1', source='arxiv',
            version_id=VID, html_file='source.html', html_sha256=sha(self.html.encode()),
            html_bytes=len(self.html.encode()), source_url=f'https://arxiv.org/html/{VID}',
            final_url=f'https://arxiv.org/html/{VID}', http_status=200, charset='utf-8',
            preprocessing=False, offline_assets_bundled=False, owning_cron_id='4cff5b4f10ec'))
        self.item = dict(version_id=VID, format='html', source='arxiv', source_path=self.source,
            source_sha256=sha(self.html.encode()), source_bytes=len(self.html.encode()),
            metadata_path=self.metadata, metadata_sha256=self.ref(self.metadata),
            status='retryable_failed', failure_count=1)
        self.state = dict(schema='pkm-compilation-state/v1', policy_revision=POLICY,
            contract_revision=CONTRACT, safety_block=False, enabled=False, transactions=[], items=[self.item])
        self.put('_meta/state/compilation.json', self.state)
        self.policy = dict(schema='pkm-automation/v1', policy_revision=POLICY, contract_revision=CONTRACT,
            wiki_root=str(root), enabled=False, phase_authorizations={'P2': True},
            model=dict(provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh', fallback_allowed=False),
            transfer=dict(local_html_text=True, pdf_content=False, images=False, external_assets=False,
                automatic_chat_capture=False, secrets_or_sensitive_personal_data=False, external_novelty_search=False),
            budget=dict(cost_policy='no_cost_cap', unknown_cost_action='record_unknown_continue'),
            limits={'attempts_per_item_per_run_including_initial': 2},
            jobs={'daily_compile': dict(enabled=False, prompt_path=PROMPT, prompt_revision='wiki-compile/v2')},
            pilot_candidates=[VID, '2609.31358v1'])
        self.put('_meta/automation.json', self.policy)
        self.approval = dict(schema='pkm-p2-run-approval/v1', actor='user', approved=True,
            phase='P2', scope='manual-html-direct-compile', run_id=Path(RUN).name, wiki_root=str(root),
            fresh_run=True, operator_reviewed_prior_attempts=True, version_ids=[VID, '2609.31358v1'],
            provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh', max_attempts_per_item=2,
            approved_route={'base_url': 'https://synthetic.invalid/v1', 'api_mode': 'responses'},
            policy_revision=POLICY, policy_sha256=self.ref('_meta/automation.json'),
            prompt_revision='wiki-compile/v2', prompt_sha256=self.ref(PROMPT),
            instructions_path=self.instructions, instructions_sha256=self.ref(self.instructions),
            document_sha256={p: self.ref(p) for p in DOCS},
            sources={VID: {k: self.item[k] for k in ('source_sha256', 'source_bytes', 'metadata_sha256')}},
            confirmation='SYNTHETIC ONLY explicit manual run approval')
        self.save_approval()

    def put(self, p, value):
        path = self.root / p
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else
            (value if isinstance(value, str) else json.dumps(value)).encode())

    def ref(self, p):
        return sha((self.root / p).read_bytes())

    def save_approval(self):
        self.put(RUN + '/approval.json', self.approval)

    def args(self, attempt='attempt1'):
        return [VID, attempt, '--root', str(self.root), '--run', RUN,
                '--instructions', self.instructions, '--timeout', '10']

    def result(self, attempt='attempt1'):
        return json.loads((self.root / RUN / VID / f'{attempt}-result.json').read_text())


class FakeClient:
    def __init__(self, response=None):
        self.responses = self
        self.response = response or SimpleNamespace(status='completed', model='gpt-6-astra',
            incomplete_details=None, error=None, output_text='SYNTHETIC RESULT',
            usage=SimpleNamespace(input_tokens=100, output_tokens=20, total_tokens=120), cost_usd=None)
        self.calls = []
        self.closed = False

    def create(self, **kw):
        self.calls.append(kw)
        return self.response

    def close(self):
        self.closed = True


class FakeStream:
    def __init__(self, events, failure=None):
        self.events = events
        self.failure = failure
        self.closed = False

    def __iter__(self):
        yield from self.events
        if self.failure:
            raise self.failure

    def close(self):
        self.closed = True


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fx = Fixture(Path(self.tmp.name))
        self.client = FakeClient()
        self.factory = mock.Mock(return_value=self.client)

    def test_nonstream_direct_html_success_and_complete_provenance(self):
        rc = load(WRAPPER).main(self.fx.args(), client_factory=self.factory)
        self.assertEqual(rc, 0)
        out = self.fx.result()
        self.assertTrue(out['completed'])
        self.assertIsNone(out['cost_usd'])
        self.assertEqual(out['usage']['total_tokens'], 120)
        for key in ('provider', 'model', 'reasoning_effort', 'policy_revision', 'policy_sha256',
                    'prompt_revision', 'prompt_sha256', 'instructions_sha256', 'source_sha256',
                    'source_bytes', 'metadata_sha256', 'approval_ref', 'approval_sha256',
                    'route_base_url', 'api_mode', 'response_model', 'response_status', 'incomplete_details'):
            self.assertIn(key, out)
        self.assertEqual(out['provider'], 'codex-lb')
        self.assertEqual(out['source_sha256'], sha(self.fx.html.encode()))
        call, = self.client.calls
        self.assertEqual(call['input'][0]['content'][0]['text'], self.fx.html)
        self.assertFalse(call['stream'])
        self.assertEqual(call['tools'], [])
        self.assertTrue(self.client.closed)
        self.assertEqual(self.factory.call_args.kwargs['max_retries'], 0)

    def test_stream_completed_success(self):
        stream = FakeStream([SimpleNamespace(type='response.completed', response=self.client.response)])
        self.client.response = stream
        self.assertEqual(load().main(self.fx.args(), client_factory=self.factory), 0)
        self.assertTrue(self.fx.result()['completed'])
        self.assertTrue(self.client.calls[0]['stream'])
        self.assertTrue(stream.closed)
        self.assertTrue(self.client.closed)

    def test_stream_exception_after_completion_is_failure_no_fallback(self):
        stream = FakeStream([SimpleNamespace(type='response.completed', response=self.client.response)],
                            RuntimeError('SYNTHETIC_SECRET_DO_NOT_RECORD'))
        self.client.response = stream
        self.assertEqual(load().main(self.fx.args(), client_factory=self.factory), 1)
        self.assertFalse(self.fx.result()['completed'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(self.fx.result()))
        self.assertEqual(len(self.client.calls), 1)
        self.assertTrue(stream.closed)
        self.assertTrue(self.client.closed)

    def test_both_modes_reject_incomplete_wrong_model_and_error(self):
        for streaming in (False, True):
            for change in ({'status': 'incomplete'}, {'model': 'wrong-model'},
                           {'incomplete_details': {}}, {'error': {'message': 'SYNTHETIC_SECRET'}},
                           {'status': None}):
                with self.subTest(streaming=streaming, change=change), tempfile.TemporaryDirectory() as tmp:
                    fx = Fixture(Path(tmp))
                    response = FakeClient().response
                    for key, val in change.items():
                        setattr(response, key, val)
                    client = FakeClient(FakeStream([SimpleNamespace(type='response.completed', response=response)])
                                        if streaming else response)
                    rc = load().main(fx.args(), stream=streaming, client_factory=lambda **kw: client)
                    self.assertEqual(rc, 1)
                    self.assertEqual(len(client.calls), 1)
                    self.assertFalse(fx.result()['completed'])
                    self.assertNotIn('SYNTHETIC_SECRET', json.dumps(fx.result()))
                    self.assertTrue(client.closed)

    def test_stream_error_event_cannot_be_overridden(self):
        stream = FakeStream([SimpleNamespace(type='error', message='SYNTHETIC_SECRET'),
                             SimpleNamespace(type='response.completed', response=self.client.response)])
        self.client.response = stream
        self.assertEqual(load().main(self.fx.args(), client_factory=self.factory), 1)
        self.assertFalse(self.fx.result()['completed'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(self.fx.result()))
        self.assertTrue(stream.closed)

    def test_unknown_and_positive_cost_never_gate(self):
        for cost in (None, 999999):
            with self.subTest(cost=cost), tempfile.TemporaryDirectory() as tmp:
                fx = Fixture(Path(tmp))
                client = FakeClient()
                client.response.cost_usd = cost
                self.assertEqual(load().main(fx.args(), stream=False, client_factory=lambda **kw: client), 0)
                self.assertEqual(fx.result()['cost_usd'], cost)

    def test_exception_has_safe_failure_record_and_no_retry(self):
        self.client.create = mock.Mock(side_effect=RuntimeError('SYNTHETIC_SECRET credential'))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = load().main(self.fx.args(), stream=False, client_factory=self.factory)
        self.assertEqual(rc, 1)
        self.assertEqual(self.client.create.call_count, 1)
        self.assertTrue(self.client.closed)
        self.assertIsNone(self.fx.result()['cost_usd'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(self.fx.result()) + buf.getvalue())

    def reject_without_body_or_client(self, mutate=None, args=None):
        if mutate:
            mutate()
        module = load()
        original = module.read_bytes
        reads = []
        def guarded(root, relative):
            reads.append(relative)
            self.assertFalse(relative.endswith('source.html'), 'read source before safety checks')
            return original(root, relative)
        with mock.patch.object(module, 'read_bytes', side_effect=guarded):
            rc = module.main(args or self.fx.args(), stream=False, client_factory=self.factory)
        self.assertEqual(rc, 2)
        self.assertFalse(any(p.endswith('source.html') for p in reads))
        self.factory.assert_not_called()
        self.assertFalse((self.fx.root / RUN / '.compile-scope.json').exists())

    def test_protected_agents_inconsistency_blocks_before_body_and_client(self):
        self.fx.put('AGENTS.md', 'pkm-html-knowledge/v1\nP2 execution not approved; cost gate')
        self.fx.approval['document_sha256']['AGENTS.md'] = self.fx.ref('AGENTS.md')
        self.fx.save_approval()  # Even freshly hashing the inconsistent document must not approve it.
        self.reject_without_body_or_client()

    def test_live_root_blocked_without_source_auth_or_writes(self):
        module = load()
        root = HERE.parents[3]
        reads = []
        original = module.read_bytes
        def guard(root, relative):
            reads.append(relative)
            self.assertFalse(relative.endswith('source.html'))
            return original(root, relative)
        args = [VID, 'attempt1', '--root', str(root), '--run', '_meta/runs/wiki/nonexistent-synthetic-no-create',
                '--instructions', '_meta/runs/wiki/20260929T083140Z-p2-resume/compile-instructions.txt']
        with mock.patch.object(module, 'read_bytes', side_effect=guard):
            self.assertEqual(module.main(args, client_factory=self.factory), 2)
        self.assertIn('AGENTS.md', reads)
        self.assertFalse(any(p.endswith('source.html') for p in reads))
        self.factory.assert_not_called()
        self.assertFalse((root / '_meta/runs/wiki/nonexistent-synthetic-no-create').exists())

    def test_out_of_scope_and_malformed_id(self):
        for vid in ('2609.30824v1', '../2609.30830v1', '2609.30830v1 ', '2609.30830'):
            with self.subTest(vid=vid):
                self.reject_without_body_or_client(args=[vid, *self.fx.args()[1:]])

    def test_symlink_and_path_escape(self):
        source = self.fx.root / self.fx.source
        source.unlink()
        source.symlink_to(self.fx.root / 'AGENTS.md')
        self.reject_without_body_or_client()
        args = self.fx.args()
        args[args.index('--run') + 1] = '_meta/runs/wiki/../escape'
        self.reject_without_body_or_client(args=args)

    def test_p2_safety_model_prompt_and_approval_drifts(self):
        cases = [('policy', 'phase_authorizations', {'P2': False}),
                 ('policy', 'model', {'provider': 'fallback'}),
                 ('state', 'safety_block', True),
                 ('state', 'transactions', [{'status': 'prepared'}]),
                 ('approval', 'model', 'wrong'), ('approval', 'run_id', 'old'),
                 ('approval', 'policy_sha256', '0' * 64),
                 ('approval', 'instructions_sha256', '0' * 64),
                 ('approval', 'approved_route', {'base_url': 'https://host/v1', 'api_mode': 'chat_completions'})]
        for owner, key, val in cases:
            with self.subTest(owner=owner, key=key), tempfile.TemporaryDirectory() as tmp:
                old = self.fx
                self.fx = Fixture(Path(tmp))
                data = getattr(self.fx, owner)
                data[key] = val
                path = {'policy': '_meta/automation.json', 'state': '_meta/state/compilation.json',
                        'approval': RUN + '/approval.json'}[owner]
                self.fx.put(path, data)
                self.reject_without_body_or_client()
                self.fx = old

    def test_metadata_drift_blocks_before_source(self):
        self.fx.put(self.fx.metadata, {'schema': 'arxiv-pdf-source/v1'})
        self.reject_without_body_or_client()

    def test_source_hash_and_length_drift_no_client(self):
        self.fx.put(self.fx.source, 'SYNTHETIC CHANGED')
        self.assertEqual(load().main(self.fx.args(), stream=False, client_factory=self.factory), 2)
        self.factory.assert_not_called()

    def test_attempt_immutability_and_two_attempt_limit(self):
        module = load()
        self.assertEqual(module.main(self.fx.args(), stream=False, client_factory=self.factory), 0)
        item = self.fx.root / RUN / VID
        before = {p.name: p.read_bytes() for p in item.iterdir() if p.is_file()}
        self.assertEqual(module.main(self.fx.args(), stream=False, client_factory=self.factory), 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in item.iterdir() if p.is_file()})
        self.assertEqual(module.main(self.fx.args('attempt2'), stream=False, client_factory=self.factory), 0)
        self.assertEqual(module.main(self.fx.args('attempt3'), stream=False, client_factory=self.factory), 2)
        self.assertEqual(self.factory.call_count, 2)

    def test_start_only_unknown_attempt_counts_and_is_not_rewritten(self):
        module = load()
        context = module.preflight(self.fx.root, RUN, VID, 'unknown', self.fx.instructions, 10)
        result_path = module.reserve(context[0], context[1], context[2], self.fx.instructions)
        record_path = result_path.with_name('unknown-record.json')
        before = record_path.read_bytes()
        self.assertFalse(result_path.exists())
        self.assertEqual(module.main(self.fx.args('unknown'), stream=False, client_factory=self.factory), 2)
        self.assertEqual(module.main(self.fx.args('second'), stream=False, client_factory=self.factory), 0)
        self.assertEqual(module.main(self.fx.args('third'), stream=False, client_factory=self.factory), 2)
        self.assertEqual(record_path.read_bytes(), before)
        self.assertFalse(result_path.exists())

    def test_atomic_concurrent_attempt_reservation(self):
        module = load()
        context = module.preflight(self.fx.root, RUN, VID, 'same', self.fx.instructions, 10)
        def worker(_):
            try:
                module.reserve(context[0], context[1], context[2], self.fx.instructions)
                return True
            except (OSError, module.Rejected):
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(worker, range(8)))
        self.assertEqual(sum(outcomes), 1)

    def test_cli_requires_run_and_returns_nonzero(self):
        for path in (SCRIPT, WRAPPER):
            p = subprocess.run([sys.executable, '-B', str(path), VID, 'attempt1'], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('--run', p.stderr)

    def test_v2_label_cannot_override_active_agents_denial(self):
        self.fx.put('AGENTS.md', 'pkm-html-knowledge/v2\nP2–P6 실행/등록/활성화 승인은 없다.\n')
        self.fx.approval['document_sha256']['AGENTS.md'] = self.fx.ref('AGENTS.md')
        self.fx.save_approval()
        self.reject_without_body_or_client()

    def test_actual_compilation_document_version_spelling_is_supported(self):
        self.fx.put('_meta/COMPILATION.md', (HERE.parents[3] / '_meta/COMPILATION.md').read_bytes())
        self.fx.approval['document_sha256']['_meta/COMPILATION.md'] = self.fx.ref('_meta/COMPILATION.md')
        self.fx.save_approval()
        self.assertEqual(load().main(self.fx.args(), stream=False, client_factory=self.factory), 0)

    def test_nonfresh_run_rejected_before_source(self):
        self.fx.put(RUN + '/' + VID + '/old-result.json', {'completed': False})
        self.reject_without_body_or_client()

    def test_runtime_route_and_resolved_model_are_pinned_without_real_imports(self):
        module = load()
        route = self.fx.approval['approved_route']
        for change in ({'model': 'wrong'}, {'provider': 'openrouter'},
                       {'base_url': 'https://wrong.invalid/v1'}, {'api_mode': 'chat_completions'},
                       {'request_overrides': {'extra_body': {'model': 'wrong'}}}):
            with self.subTest(change=change):
                runtime = dict(requested_provider='codex-lb', provider='custom', model='gpt-6-astra', api_key=object(),
                               api_mode=route['api_mode'], base_url=route['base_url'])
                runtime.update(change)
                sdk = types.ModuleType('openai')
                sdk.OpenAI = mock.Mock()
                resolver = types.ModuleType('hermes_cli.runtime_provider')
                resolver.resolve_runtime_provider = mock.Mock(return_value=runtime)
                with mock.patch.dict(sys.modules, {'openai': sdk, 'hermes_cli': types.ModuleType('hermes_cli'),
                                                   'hermes_cli.runtime_provider': resolver}):
                    with self.assertRaises(module.Rejected):
                        module.runtime_client(approved_route=route, timeout=10, max_retries=0)
                    sdk.OpenAI.assert_not_called()

    def test_timeout_after_nonstream_response_preserves_failure(self):
        module = load()
        clock = [0]
        def create(**kw):
            clock[0] = 11
            return self.client.response
        self.client.create = create
        with mock.patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
            self.assertEqual(module.main(self.fx.args(), stream=False, client_factory=self.factory), 1)
        self.assertTrue(self.client.closed)
        self.assertEqual(self.fx.result()['error']['type'], 'TimeoutError')

    def test_existing_attempt_is_rejected_before_source_reread(self):
        module = load()
        self.assertEqual(module.main(self.fx.args(), stream=False, client_factory=self.factory), 0)
        reads = []
        original = module.read_bytes
        def guarded(root, relative):
            reads.append(relative)
            return original(root, relative)
        with mock.patch.object(module, 'read_bytes', side_effect=guarded):
            self.assertEqual(module.main(self.fx.args(), stream=False, client_factory=self.factory), 2)
        self.assertFalse(any(p.endswith('source.html') for p in reads))
        self.assertEqual(self.factory.call_count, 1)

    def test_exclusive_writer_rejects_parent_symlink(self):
        module = load()
        target = self.fx.root / 'external-synthetic'
        target.mkdir()
        linked = self.fx.root / 'linked'
        linked.symlink_to(target, target_is_directory=True)
        with self.assertRaises((OSError, module.Rejected)):
            module.exclusive_json(linked / 'result.json', {'synthetic': True})
        self.assertFalse((target / 'result.json').exists())

    def test_start_record_includes_unknown_response_and_usage(self):
        self.assertEqual(load().main(self.fx.args(), stream=False, client_factory=self.factory), 0)
        start = json.loads((self.fx.root / RUN / VID / 'attempt1-record.json').read_text())
        for key in ('response_model', 'response_status', 'incomplete_details', 'usage', 'cost_usd'):
            self.assertIn(key, start)
            self.assertIsNone(start[key])
        self.assertEqual(start['outcome'], 'unknown')

    def test_incomplete_reason_is_bounded_but_retained(self):
        self.client.response.status = 'incomplete'
        self.client.response.incomplete_details = {'reason': 'max_output_tokens', 'message': 'SYNTHETIC_SECRET'}
        self.assertEqual(load().main(self.fx.args(), stream=False, client_factory=self.factory), 1)
        self.assertEqual(self.fx.result()['incomplete_details'], {'reason': 'max_output_tokens'})
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(self.fx.result()))

    def test_deadline_expired_in_factory_makes_no_request(self):
        module = load()
        clock = [0]
        def factory(**kw):
            clock[0] = 11
            return self.client
        with mock.patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
            rc = module.main(self.fx.args(), stream=False, client_factory=factory)
        self.assertEqual(rc, 1)
        self.assertEqual(self.client.calls, [])
        self.assertTrue(self.client.closed)
        self.assertFalse(self.fx.result()['completed'])

    def test_mocked_compiler_result_passes_real_sibling_verifier(self):
        quote = 'Synthetic evidence supports a bounded claim.'
        html = '<html><body><section id="S1">' + quote + '</section></body></html>'
        self.fx.put(self.fx.source, html)
        metadata = json.loads((self.fx.root / self.fx.metadata).read_text())
        metadata.update(html_sha256=sha(html.encode()), html_bytes=len(html.encode()))
        self.fx.put(self.fx.metadata, metadata)
        self.fx.item.update(source_sha256=metadata['html_sha256'], source_bytes=metadata['html_bytes'],
                            metadata_sha256=self.fx.ref(self.fx.metadata))
        self.fx.put('_meta/state/compilation.json', self.fx.state)
        self.fx.approval['sources'][VID] = {k: self.fx.item[k] for k in
                                          ('source_sha256', 'source_bytes', 'metadata_sha256')}
        self.fx.save_approval()
        claims = [dict(id=f'C{i:02d}', kind='author_report', statement=f'Synthetic bounded claim {i}.',
                       conditions='Synthetic fixture only.', anchor='S1', quote=quote) for i in range(1, 9)]
        lines = ['## Synthetic analysis']
        for claim in claims:
            lines += [f"### {claim['id']}",
                      f"{claim['id']}: {claim['statement']} [evidence]({self.fx.source}#S1)",
                      'SYNTHETIC test only; no scientific finding.'] + ['Bounded fixture explanation.'] * 9
        doc = dict(title='Synthetic integration', version_id=VID, main_text_complete=True,
                   read_scope=['S1'], unread_scope=['Figures not reviewed', 'Equations not reviewed', 'Appendix not reviewed'],
                   limitations=['Synthetic evidence only; no scientific validation.'], claims=claims,
                   markdown_body='\n'.join(lines))
        self.client.response.output_text = json.dumps(doc)
        self.assertEqual(load(WRAPPER).main(self.fx.args(), client_factory=self.factory), 0)
        verifier = load(HERE / 'verify-one.py')
        report = verifier.verify_result(self.fx.root, VID, self.fx.result())
        self.assertTrue(report['passed'], report)
        self.assertEqual(report['document'], doc)


class ImportTests(unittest.TestCase):
    def test_both_entrypoints_import_without_execution(self):
        for script in (SCRIPT, WRAPPER):
            with self.subTest(script=script.name):
                module = load(script)
                self.assertTrue(callable(module.main))


if __name__ == '__main__':
    unittest.main()
