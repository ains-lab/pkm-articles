"""Bounded manual P2 compiler; importing never reads sources or credentials."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time
from urllib.parse import urlsplit

PROVIDER, MODEL, EFFORT = 'codex-lb', 'gpt-6-astra', 'xhigh'
POLICY, CONTRACT, PROMPT_REV = 'pkm-html-knowledge/v2', 'pkm-contracts/v2', 'wiki-compile/v2'
PILOT = ('2609.30830v1', '2609.31358v1')
PROMPT = '_meta/prompts/wiki-compile.md'
DOCS = ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/STATE-CONTRACTS.md',
        '_meta/COMPILATION.md', '_meta/automation-contracts.schema.json')
OLD_RUNS = ('20260929T083140Z-p2-resume', '20260930T082000Z-p2-nonstream')


class Rejected(Exception):
    """Only locally defined, nonsecret category codes may be surfaced."""


def require(ok, code):
    if not ok:
        raise Rejected(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def safe_path(root, relative):
    require(isinstance(relative, str) and relative and not relative.startswith('/') and
            all(p not in ('', '.', '..') for p in relative.split('/')), 'invalid_path')
    path = root / relative
    for part in (path, *path.parents):
        require(not part.is_symlink(), 'symlink')
    require(path.is_relative_to(root), 'path_escape')
    return path


def parent_fd(path):
    """Open each parent directory without following symlinks, including races."""
    require(path.is_absolute() and '..' not in path.parts, 'invalid_path')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_bytes(root, relative):
    path = safe_path(root, relative)
    fd = parent_fd(path)
    try:
        child = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(child, 'rb') as f:
            require(stat.S_ISREG(os.fstat(f.fileno()).st_mode), 'not_regular_file')
            return f.read()
    finally:
        os.close(fd)


def read_json(root, relative):
    data = read_bytes(root, relative)
    return json.loads(data), digest(data)


def exclusive_json(path, obj):
    data = (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    fd = parent_fd(path)
    try:
        child = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(child, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.fsync(fd)
    finally:
        os.close(fd)


def mkdir_no_links(path, exist_ok=False):
    fd = parent_fd(path)
    try:
        try:
            os.mkdir(path.name, mode=0o700, dir_fd=fd)
        except FileExistsError:
            if not exist_ok:
                raise
            child = os.open(path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(child)
        os.fsync(fd)
    finally:
        os.close(fd)


def check_run_scope(root, run_path, approval_sha, instructions):
    marker = safe_path(root, str((run_path / '.compile-scope.json').relative_to(root)))
    scope = dict(schema='pkm-p2-compile-scope/v1', approval_sha256=approval_sha)
    if marker.exists():
        old, _ = read_json(root, str(marker.relative_to(root)))
        require(old == scope, 'run_scope_changed')
    else:
        allowed = {'approval.json', '.compile-reservation-lock'}
        if Path(instructions).parent == run_path.relative_to(root):
            allowed.add(Path(instructions).name)
        require({p.name for p in run_path.iterdir()} <= allowed, 'run_not_fresh')
    return marker, scope


def check_attempt_available(root, run_path, vid, attempt):
    item_path = safe_path(root, str((run_path / vid).relative_to(root)))
    names = set()
    if item_path.exists():
        for p in item_path.iterdir():
            require(not p.is_symlink(), 'symlink')
            for suffix in ('-reserved', '-record.json', '-result.json', '-model-output.md'):
                if p.name.endswith(suffix):
                    names.add(p.name[:-len(suffix)])
    require(attempt not in names, 'attempt_exists')
    require(len(names) < 2, 'attempt_limit')
    return item_path


def preflight(root, run, vid, attempt, instructions, timeout):
    require(isinstance(vid, str) and re.fullmatch(r'\d{4}\.\d{4,5}v[1-9]\d*', vid), 'invalid_id')
    require(vid in PILOT, 'outside_p2')
    require(isinstance(attempt, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,47}', attempt), 'invalid_attempt')
    require(type(timeout) in (int, float) and math.isfinite(timeout) and 0 < timeout <= 2700, 'invalid_timeout')
    root = Path(root)
    require(root.is_absolute() and '..' not in root.parts and root.is_dir(), 'invalid_root')
    require(all(not p.is_symlink() for p in (root, *root.parents)), 'symlink')
    require(isinstance(run, str) and re.fullmatch(r'_meta/runs/wiki/[A-Za-z0-9][A-Za-z0-9_-]{0,95}', run), 'invalid_run')
    require(Path(run).name not in OLD_RUNS, 'old_run_forbidden')
    run_path = safe_path(root, run)
    source = f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html'
    metadata = source.replace('source.html', 'source.json')
    for p in (*DOCS, PROMPT, source, metadata, instructions, run + '/approval.json',
              '_meta/automation.json', '_meta/state/compilation.json'):
        safe_path(root, p)
    # Actual governing files, not just copied revision strings in a request.
    docs = {p: read_bytes(root, p) for p in DOCS}
    for p, data in docs.items():
        text = data.decode('utf-8')
        versions = set(re.findall(r'pkm-html-knowledge/v\d+', text))
        if p == '_meta/COMPILATION.md' and not versions and 'policy v2' in text:
            versions = {POLICY}
        require(versions == {POLICY}, 'policy_document_mismatch')
        contracts = set(re.findall(r'pkm-contracts/v\d+', text))
        require(not contracts or contracts == {CONTRACT}, 'contract_document_mismatch')
        if p in ('AGENTS.md', 'SCHEMA.md'):
            require(not any(denial in text for denial in (
                'P2–P6 실행/등록/활성화 승인은 없다', 'P2-P6 execution not approved',
                '단계·자료·비용 게이트를 통과', '계측·강제 차단 검증 전 호출')), 'active_policy_denial')
    schema_doc = json.loads(docs['_meta/automation-contracts.schema.json'])
    require(isinstance(schema_doc, dict), 'invalid_contract_schema')
    policy, policy_sha = read_json(root, '_meta/automation.json')
    require(policy['schema'] == 'pkm-automation/v1' and policy['wiki_root'] == str(root) and
            policy['policy_revision'] == POLICY and policy['contract_revision'] == CONTRACT,
            'policy_mismatch')
    require(policy['phase_authorizations']['P2'] is True and policy['enabled'] is False, 'p2_not_authorized')
    require(policy['pilot_candidates'] == list(PILOT), 'p2_scope_mismatch')
    require(policy['model'] == dict(provider=PROVIDER, model=MODEL, reasoning_effort=EFFORT,
                                   fallback_allowed=False), 'model_pin_mismatch')
    transfer = policy['transfer']
    require(transfer['local_html_text'] is True and all(transfer[k] is False for k in
            ('pdf_content', 'images', 'external_assets', 'automatic_chat_capture',
             'secrets_or_sensitive_personal_data', 'external_novelty_search')), 'transfer_policy')
    require(policy['limits']['attempts_per_item_per_run_including_initial'] == 2, 'attempt_limit_mismatch')
    require(policy['budget']['cost_policy'] == 'no_cost_cap' and
            policy['budget']['unknown_cost_action'] == 'record_unknown_continue', 'cost_policy_mismatch')
    job = policy['jobs']['daily_compile']
    require(job['enabled'] is False and job['prompt_path'] == PROMPT and
            job['prompt_revision'] == PROMPT_REV, 'prompt_pin_mismatch')
    prompt = read_bytes(root, PROMPT)
    for family, expected in [('pkm-html-knowledge', POLICY), ('pkm-contracts', CONTRACT), ('wiki-compile', PROMPT_REV)]:
        require(set(re.findall(f'{family}/v\\d+', prompt.decode())) == {expected}, 'prompt_document_mismatch')
    require(set(re.findall(r'wiki-compile/v\d+', docs['_meta/automation-contracts.schema.json'].decode())) ==
            {PROMPT_REV}, 'schema_prompt_mismatch')
    state, _ = read_json(root, '_meta/state/compilation.json')
    require(state['schema'] == 'pkm-compilation-state/v1' and state['policy_revision'] == POLICY and
            state['contract_revision'] == CONTRACT and state['safety_block'] is False, 'safety_block_or_state')
    require(all(t.get('status') in ('committed', 'rolled_back') for t in state['transactions']), 'unresolved_transaction')
    items = [x for x in state['items'] if x['version_id'] == vid]
    require(len(items) == 1, 'missing_or_duplicate_item')
    item = items[0]
    require(item['format'] == 'html' and item['source'] == 'arxiv' and item['source_path'] == source and
            item['metadata_path'] == metadata and type(item['failure_count']) is int and
            0 <= item['failure_count'] < 3 and item['status'] in
            ('blocked_approval', 'queued', 'partial', 'retryable_failed'), 'item_policy')
    approval, approval_sha = read_json(root, run + '/approval.json')
    require(approval['schema'] == 'pkm-p2-run-approval/v1' and approval['actor'] == 'user' and
            approval['approved'] is True and approval['phase'] == 'P2' and
            approval['scope'] == 'manual-html-direct-compile' and approval['run_id'] == Path(run).name and
            approval['wiki_root'] == str(root) and approval['fresh_run'] is True and
            approval['operator_reviewed_prior_attempts'] is True and approval['version_ids'] == list(PILOT) and
            approval['max_attempts_per_item'] == 2 and isinstance(approval['confirmation'], str) and
            bool(approval['confirmation'].strip()), 'run_not_approved')
    require(all(approval[k] == v for k, v in dict(provider=PROVIDER, model=MODEL, reasoning_effort=EFFORT,
            policy_revision=POLICY, policy_sha256=policy_sha, prompt_revision=PROMPT_REV,
            prompt_sha256=digest(prompt), instructions_path=instructions).items()), 'approval_pin_mismatch')
    require(approval['document_sha256'] == {p: digest(b) for p, b in docs.items()}, 'approval_document_drift')
    instr = read_bytes(root, instructions)
    require(digest(instr) == approval['instructions_sha256'], 'instructions_drift')
    route = approval['approved_route']
    require(set(route) == {'base_url', 'api_mode'} and route['api_mode'] in ('responses', 'codex_responses'), 'route_mode')
    url = urlsplit(route['base_url'])
    require(url.scheme in ('https', 'http') and bool(url.hostname) and not url.username and not url.password and
            not url.query and not url.fragment, 'unsafe_route')
    meta, metadata_sha = read_json(root, metadata)
    require(meta['schema'] == 'arxiv-html-source/v1' and meta['source'] == 'arxiv' and
            meta['version_id'] == vid and meta['owning_cron_id'] == '4cff5b4f10ec' and
            meta['html_file'] == 'source.html' and meta['source_url'] == f'https://arxiv.org/html/{vid}' and
            meta['final_url'] == meta['source_url'] and meta['http_status'] == 200 and
            meta['preprocessing'] is False and meta['offline_assets_bundled'] is False and
            meta['charset'].lower() == 'utf-8', 'metadata_policy')
    expected = {k: item[k] for k in ('source_sha256', 'source_bytes', 'metadata_sha256')}
    require(approval['sources'][vid] == expected and metadata_sha == item['metadata_sha256'] and
            meta['html_sha256'] == item['source_sha256'] and meta['html_bytes'] == item['source_bytes'] and
            type(item['source_bytes']) is int and item['source_bytes'] > 0, 'source_metadata_drift')
    check_run_scope(root, run_path, approval_sha, instructions)
    check_attempt_available(root, run_path, vid, attempt)
    # No source bytes are read until every authorization/document/metadata gate passed.
    body = read_bytes(root, source)
    require(digest(body) == item['source_sha256'] and len(body) == item['source_bytes'], 'source_integrity')
    html = body.decode('utf-8')  # STRICT, byte-faithful; no HTML stripping or normalization.
    record = dict(vid=vid, run_id=Path(run).name, attempt=attempt, provider=PROVIDER, model=MODEL,
        reasoning_effort=EFFORT, policy_revision=POLICY, policy_sha256=policy_sha,
        prompt_revision=PROMPT_REV, prompt_sha256=digest(prompt), instructions_sha256=digest(instr),
        source_path=source, metadata_path=metadata, **expected,
        approval_ref=run + '/approval.json', approval_sha256=approval_sha,
        route_base_url=route['base_url'], api_mode=route['api_mode'], http_timeout_s=timeout)
    return root, run_path, record, instr.decode('utf-8'), html


def reserve(root, run_path, record, instructions):
    """An immutable scope and exclusive attempt consume a slot even after a crash."""
    lock = safe_path(root, str((run_path / '.compile-reservation-lock').relative_to(root)))
    mkdir_no_links(lock)  # No stale-lock stealing, no retries.
    try:
        marker, scope = check_run_scope(root, run_path, record['approval_sha256'], instructions)
        if not marker.exists():
            exclusive_json(marker, scope)
        item_path = check_attempt_available(root, run_path, record['vid'], record['attempt'])
        mkdir_no_links(item_path, exist_ok=True)
        mkdir_no_links(item_path / (record['attempt'] + '-reserved'))
        exclusive_json(item_path / (record['attempt'] + '-record.json'),
                       dict(record, schema='pkm-p2-attempt/v4', started_at=utcnow(), outcome='unknown',
                            response_model=None, response_status=None, incomplete_details=None,
                            usage=None, cost_usd=None, cost_status='unobserved_not_zero'))
        return item_path / (record['attempt'] + '-result.json')
    finally:
        lock.rmdir()


def runtime_client(*, approved_route, timeout, max_retries):
    # Only reached after complete local preflight and durable exclusive reservation.
    from hermes_cli.runtime_provider import resolve_runtime_provider
    from openai import OpenAI
    rt = resolve_runtime_provider(requested=PROVIDER, target_model=MODEL)
    require(rt.get('requested_provider') == PROVIDER and rt.get('provider') == 'custom' and
            rt.get('model') == MODEL and rt.get('base_url') == approved_route['base_url'] and
            rt.get('api_mode') == approved_route['api_mode'] and not rt.get('request_overrides'), 'runtime_route_mismatch')
    return OpenAI(api_key=rt['api_key'], base_url=rt['base_url'], default_headers=rt.get('extra_headers') or {},
                  max_retries=max_retries, timeout=timeout)


def value(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def safe_error(exc):
    # Never stringify an SDK exception: messages/bodies/headers can include secrets.
    typ = type(exc).__name__
    known = {'TimeoutError', 'ConnectionError', 'OSError', 'ValueError', 'RuntimeError',
             'APIError', 'APIStatusError', 'APIConnectionError', 'APITimeoutError', 'KeyboardInterrupt'}
    status = value(exc, 'status_code')
    return dict(type=typ if typ in known else 'Exception',
                status=status if type(status) is int and 100 <= status <= 599 else None,
                code='local_rejection' if isinstance(exc, Rejected) else 'request_failed')


def usage_metadata(response):
    usage = value(response, 'usage')
    if usage is None:
        return None
    out = {}
    for key in ('input_tokens', 'output_tokens', 'total_tokens'):
        n = value(usage, key)
        if type(n) is int and n >= 0:
            out[key] = n
    for key, inner in [('input_tokens_details', 'cached_tokens'), ('output_tokens_details', 'reasoning_tokens')]:
        n = value(value(usage, key), inner)
        if type(n) is int and n >= 0:
            out[key] = {inner: n}
    return out


def compile_one(*, root, run, vid, attempt, instructions, timeout=2400, stream=True, client_factory=None):
    root, run_path, record, instr, html = preflight(root, run, vid, attempt, instructions, timeout)
    record['transport'] = 'http-stream' if stream else 'http-nonstream'
    result_path = reserve(root, run_path, record, instructions)
    t0 = time.monotonic()
    client = None
    response_stream = None
    response = None
    error = None
    event_count = 0
    first_event_s = None
    try:
        factory = client_factory or runtime_client
        client = factory(approved_route=dict(base_url=record['route_base_url'], api_mode=record['api_mode']),
                         timeout=timeout, max_retries=0)
        if time.monotonic() - t0 >= timeout:
            raise TimeoutError()
        created = client.responses.create(model=MODEL, instructions=instr,
            input=[{'role': 'user', 'content': [{'type': 'input_text', 'text': html}]}],
            reasoning={'effort': EFFORT}, store=False, stream=stream, tools=[])
        if not stream:
            response = created
        else:
            response_stream = created
            iterator = iter(response_stream)
            terminal_seen = False
            while True:
                if time.monotonic() - t0 >= timeout:
                    raise TimeoutError()
                try:
                    event = next(iterator)
                except StopIteration:
                    break
                if time.monotonic() - t0 >= timeout:
                    raise TimeoutError()
                event_count += 1
                if first_event_s is None:
                    first_event_s = round(time.monotonic() - t0, 3)
                event_type = value(event, 'type')
                if event_type in ('response.completed', 'response.failed', 'response.incomplete', 'error'):
                    if terminal_seen or event_type != 'response.completed':
                        error = dict(type='InvalidResponse', status=None, code='stream_terminal_error')
                    terminal_seen = True
                    response = value(event, 'response')
        if time.monotonic() - t0 >= timeout:
            raise TimeoutError()
    except (Exception, KeyboardInterrupt) as exc:
        error = safe_error(exc)
    finally:
        if response_stream is not None:
            try:
                response_stream.close()
            except (Exception, KeyboardInterrupt) as exc:
                error = error or safe_error(exc)
        if client is not None:
            try:
                client.close()
            except (Exception, KeyboardInterrupt) as exc:
                error = error or safe_error(exc)
    status = value(response, 'status')
    actual_model = value(response, 'model')
    incomplete = value(response, 'incomplete_details')
    response_error = value(response, 'error')
    incomplete_reason = value(incomplete, 'reason')
    safe_incomplete = (None if incomplete is None else
        {'reason': incomplete_reason} if incomplete_reason in ('max_output_tokens', 'content_filter') else
        {'present': True})
    completed = (error is None and status == 'completed' and actual_model == MODEL and
                 incomplete is None and response_error is None and isinstance(value(response, 'output_text'), str)
                 and bool(value(response, 'output_text').strip()))
    if not completed and error is None:
        error = dict(type='InvalidResponse', status=None, code='response_rejected')
    cost = value(response, 'cost_usd')
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
        cost = None
    out = dict(record, schema='pkm-p2-attempt-result/v4', finished_at=utcnow(), completed=completed,
        error=error, elapsed_seconds=round(time.monotonic() - t0, 3),
        event_count=event_count, first_event_s=first_event_s,
        response_status=status if status in ('completed', 'incomplete', 'failed', 'cancelled', 'in_progress', 'queued') else None,
        response_model=actual_model if isinstance(actual_model, str) and re.fullmatch(r'[A-Za-z0-9_.:/-]{1,100}', actual_model) else None,
        incomplete_details=safe_incomplete,
        response_error=None if response_error is None else {'present': True},
        text=value(response, 'output_text') if completed else '', usage=usage_metadata(response),
        cost_usd=cost, cost_status='unobserved_not_zero' if cost is None else 'observed')
    exclusive_json(safe_path(root, str(result_path.relative_to(root))), out)
    return out


def main(argv=None, *, stream=True, client_factory=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vid')
    parser.add_argument('label', nargs='?')
    parser.add_argument('--root', required=True)
    parser.add_argument('--run', required=True)
    parser.add_argument('--attempt')
    parser.add_argument('--instructions', required=True)
    parser.add_argument('--timeout', type=float, default=2400)
    args = parser.parse_args(argv)
    if args.attempt and args.label:
        parser.error('use LABEL or --attempt, not both')
    if not (args.attempt or args.label):
        parser.error('LABEL or --attempt is required')
    try:
        out = compile_one(root=args.root, run=args.run, vid=args.vid, attempt=args.attempt or args.label,
            instructions=args.instructions, timeout=args.timeout, stream=stream, client_factory=client_factory)
        print(json.dumps(dict(completed=out['completed'], response_status=out['response_status'], error=out['error'])))
        return 0 if out['completed'] else 1
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps(dict(completed=False, error=safe_error(exc),
                              rejection=str(exc) if isinstance(exc, Rejected) else 'preflight_or_storage_failure')))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
