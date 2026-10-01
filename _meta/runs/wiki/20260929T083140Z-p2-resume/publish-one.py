"""Fail-closed P2 draft publisher; importing this file never publishes."""
import argparse
import copy
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import uuid

POLICY = 'pkm-html-knowledge/v2'
CONTRACT = 'pkm-contracts/v2'
SCOPE = 'P2 main-text complete'
STATE = '_meta/state/compilation.json'
LOCK = '_meta/locks/collection.lock'
MODEL = {'provider': 'codex-lb', 'model': 'gpt-6-astra', 'reasoning_effort': 'xhigh'}
VID_RE = r'(?:[0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Z]{2})?/[0-9]{7})v[1-9][0-9]*'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def decode(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


class Files:
    """Root-contained dirfd operations; no symlinks or special/hardlinked files.

    Cooperative collection.lock/edit freeze is still required: atomic replace is
    not a compare-and-swap against a noncooperating editor between check/rename.
    """
    def __init__(self, root):
        require('..' not in Path(root).parts, 'unsafe root traversal')
        self.root = Path(os.path.abspath(root))
        p = Path(self.root.anchor)
        for part in self.root.parts[1:]:
            p /= part
            require(not p.is_symlink() and p.is_dir(), 'unsafe root')

    def parts(self, path):
        require(isinstance(path, str) and bool(re.fullmatch(r'[A-Za-z0-9_./%-]+', path)), 'unsafe path')
        parts = path.split('/')
        require(all(x not in ('', '.', '..') for x in parts), 'unsafe path')
        return parts

    @contextmanager
    def parent(self, path):
        parts = self.parts(path)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        fd = os.open(self.root.anchor, flags)
        try:
            for part in self.root.parts[1:]:
                nxt = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = nxt
            for part in parts[:-1]:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = nxt
            yield fd, parts[-1]
        finally:
            os.close(fd)

    def read(self, path, missing=False):
        with self.parent(path) as (fd, name):
            try:
                f = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            except FileNotFoundError:
                if missing:
                    return None
                raise
            with os.fdopen(f, 'rb') as stream:
                st = os.fstat(stream.fileno())
                require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, 'unsafe nonregular/hardlinked file')
                return stream.read()

    def write(self, path, data, before):
        """Fsync temporary bytes then no-clobber create or checked replacement."""
        require(self.read(path, missing=True) == before, 'target changed: ' + path)
        with self.parent(path) as (fd, name):
            tmp = '.publish-' + uuid.uuid4().hex
            out = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            try:
                with os.fdopen(out, 'wb') as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                require(self.read(path, missing=True) == before, 'target changed: ' + path)
                if before is None:
                    os.link(tmp, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
                    os.unlink(tmp, dir_fd=fd)
                else:
                    os.replace(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)
                os.fsync(fd)
            finally:
                try:
                    os.unlink(tmp, dir_fd=fd)
                except FileNotFoundError:
                    pass
        require(self.read(path) == data, 'write readback failed: ' + path)

    def append(self, path, data, before):
        require(self.read(path) == before, 'log changed before append')
        with self.parent(path) as (fd, name):
            out = os.open(name, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW, dir_fd=fd)
            with os.fdopen(out, 'ab') as stream:
                require(os.fstat(stream.fileno()).st_nlink == 1, 'hardlinked log')
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.fsync(fd)
        require(self.read(path) == before + data, 'log append readback failed')


@contextmanager
def collection_lock(fs, run, tx, now):
    owner = encoded(dict(role='pilot', run_id=run, transaction_id=tx,
                         acquired_at=now.isoformat(), pid=os.getpid(), token=uuid.uuid4().hex))
    with fs.parent(LOCK) as (fd, name):
        try:
            os.mkdir(name, 0o700, dir_fd=fd)
        except FileExistsError:
            yield False
            return
        os.fsync(fd)
        inode = os.stat(name, dir_fd=fd, follow_symlinks=False).st_ino
    try:
        fs.write(LOCK + '/owner.json', owner, None)
        def owns_lock():
            with fs.parent(LOCK) as (fd, name):
                st = os.stat(name, dir_fd=fd, follow_symlinks=False)
                require(st.st_ino == inode and stat.S_ISDIR(st.st_mode) and fs.read(LOCK + '/owner.json', True) == owner, 'collection.lock owner changed')
        yield owns_lock
    finally:
        # Never steal/remove a successor's lock, even when its pid happens to match.
        try:
            with fs.parent(LOCK) as (fd, name):
                st = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if st.st_ino == inode and stat.S_ISDIR(st.st_mode) and fs.read(LOCK + '/owner.json', True) == owner:
                    with fs.parent(LOCK + '/owner.json') as (lfd, lname):
                        os.unlink(lname, dir_fd=lfd)
                        os.fsync(lfd)
                    os.rmdir(name, dir_fd=fd)
                    os.fsync(fd)
        except (FileNotFoundError, NotADirectoryError):
            pass


def _verify_result(root, vid, result):
    sibling = Path(__file__).with_name('verify-one.py')
    require(not sibling.is_symlink(), 'unsafe verifier')
    spec = importlib.util.spec_from_file_location('pkm_publication_verifier', sibling)
    require(spec is not None and spec.loader is not None, 'verifier unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify_result(root, vid, result)


def schema_validate(schema, value, definition):
    from jsonschema import Draft202012Validator, FormatChecker
    # Contracts are entirely local. Never let a modified schema cause network I/O.
    def local_refs(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == '$ref':
                    require(v.startswith('#/'), 'external schema reference forbidden')
                local_refs(v)
        elif isinstance(node, list):
            for child in node:
                local_refs(child)
    local_refs(schema)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator({'$defs': schema['$defs'], '$ref': '#/$defs/' + definition},
                                    format_checker=FormatChecker())
    errors = list(validator.iter_errors(value))
    require(not errors, 'schema ' + definition + ': ' + '; '.join(e.message for e in errors)[:800])


def exact_keys(value, keys, label):
    require(isinstance(value, dict) and set(value) == set(keys.split()), 'invalid ' + label + ' keys')


def inputs(fs, vid, run, attempt):
    snapshots = {}
    def take(path):
        data = fs.read(path)
        snapshots[path] = sha(data)
        return data
    def ref(value, extra=''):
        exact_keys(value, 'path sha256 ' + extra, 'reference')
        data = take(value['path'])
        require(sha(data) == value['sha256'], 'reference hash conflict: ' + value['path'])
        return data
    result_path = f'{run}/{vid}/{attempt}'
    request_path = result_path[:-len('-result.json')] + '-publication-request.json'
    req = decode(take(request_path))
    separate_approval = isinstance(req, dict) and req.get('schema') == 'pkm-publication-request/v2'
    exact_keys(req, 'schema version_id requested_scope result approval policy prompt source output_path agent_review consumed_wiki_refs' +
               (' publication_approval' if separate_approval else ''), 'request')
    for name, extra in [('result', ''), ('approval', ''), ('policy', 'revision'), ('prompt', 'revision'), ('agent_review', '')]:
        exact_keys(req[name], 'path sha256 ' + extra, 'request ' + name)
    require(req['schema'] in ('pkm-publication-request/v1', 'pkm-publication-request/v2') and
            req['version_id'] == vid and req['requested_scope'] == SCOPE, 'invalid publication request scope')
    require(req['result']['path'] == result_path and req['output_path'] == f'entities/arxiv-{vid}.md', 'invalid output/result path')
    require(req['policy']['path'] == '_meta/automation.json' and req['prompt']['path'] == '_meta/prompts/wiki-compile.md', 'invalid policy/prompt path')
    auto = decode(ref(req['policy'], 'revision'))
    schema = decode(take('_meta/automation-contracts.schema.json'))
    schema_validate(schema, auto, 'automation')
    require(auto['phase_authorizations']['P2'] is True and auto['enabled'] is False, 'P2 manual approval required')
    require(auto['policy_revision'] == req['policy']['revision'] == POLICY and auto['contract_revision'] == CONTRACT, 'invalid policy')
    require(vid in auto['pilot_candidates'] and auto['model'] == dict(**MODEL, fallback_allowed=False), 'unapproved source/model')
    for path in ['AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/STATE-CONTRACTS.md']:
        text = take(path).decode('utf8')
        require(POLICY in text, 'policy document revision mismatch: ' + path)
    prompt = ref(req['prompt'], 'revision').decode('utf8')
    require(req['prompt']['revision'] == auto['jobs']['daily_compile']['prompt_revision'] == 'wiki-compile/v2', 'prompt revision mismatch')
    require('wiki-compile/v2' in prompt.splitlines()[0] and POLICY in prompt, 'prompt content mismatch')
    approval = decode(ref(req['approval']))
    canonical_approval = approval.get('schema') == 'pkm-p2-run-approval/v1'
    if canonical_approval:
        require(approval.get('actor') == 'user' and approval.get('approved') is True and
                approval.get('phase') == 'P2' and approval.get('scope') == 'manual-html-direct-compile' and
                approval.get('fresh_run') is True and approval.get('operator_reviewed_prior_attempts') is True,
                'invalid compile approval')
        require(approval.get('wiki_root') == str(fs.root) and
                approval.get('version_ids') == auto['pilot_candidates'] and
                vid in approval['version_ids'], 'invalid compile approval scope')
    else:
        require(approval.get('schema') == 'pkm-p2-resume-approval/v1' and vid in approval.get('versions', []), 'invalid approval')
    require(approval.get('run_id') == Path(run).name, 'fresh per-run publication approval required')
    authority = approval
    if separate_approval:
        # A later publication grant supplements, never replaces, the immutable
        # generation approval bound by the producer's original result envelope.
        require(canonical_approval and req['approval']['path'] == run + '/approval.json', 'canonical generation approval required')
        authority = decode(ref(req['publication_approval']))
        require(req['publication_approval']['path'] == run + '/publication-approval.json', 'publication approval path conflict')
        exact_keys(authority, 'schema actor approved phase scope wiki_root run_id version_ids confirmed_at user_request confirmation confirmation_scope publication_edit_freeze_confirmed validated_draft_publication_authorized generation_approval bindings', 'publication approval')
        require(authority['schema'] == 'pkm-p2-publication-approval/v1' and authority['actor'] == 'user' and
                authority['approved'] is True and authority['phase'] == 'P2' and
                authority['scope'] == 'publish-validated-staged-drafts', 'invalid separate publication authority')
        require(authority['wiki_root'] == str(fs.root) and authority['run_id'] == Path(run).name,
                'separate publication root/run conflict')
        versions = authority['version_ids']
        require(isinstance(versions, list) and versions and all(isinstance(v, str) for v in versions) and
                len(set(versions)) == len(versions) and vid in versions and
                set(versions) <= set(approval['version_ids']), 'separate publication versions conflict')
        require(authority['generation_approval'] == req['approval'], 'separate generation approval conflict')
        require(isinstance(authority['bindings'], dict) and set(authority['bindings']) == set(versions),
                'separate publication binding set conflict')
        for binding in authority['bindings'].values():
            exact_keys(binding, 'result agent_review source output_path', 'publication binding')
        require(authority['bindings'][vid] == {k: req[k] for k in ('result', 'agent_review', 'source', 'output_path')},
                'separate publication input binding conflict')
        require(isinstance(authority['confirmed_at'], str) and
                datetime.fromisoformat(authority['confirmed_at']).tzinfo is not None, 'publication confirmation timezone missing')
        require(all(isinstance(authority[k], str) and authority[k].strip() for k in
                    ('user_request', 'confirmation', 'confirmation_scope')), 'publication confirmation provenance missing')
    for flag in ['publication_edit_freeze_confirmed', 'validated_draft_publication_authorized']:
        require(authority.get(flag) is True, 'publication approval/freeze missing')
    require(authority.get('confirmation') and authority.get('confirmation_scope') and authority.get('user_request'), 'approval provenance missing')
    require(all(approval.get(k) == v for k, v in MODEL.items()) and approval.get('fallback_allowed') is False, 'approval model conflict')
    require(approval.get('pdf_images_external_assets_allowed') is False and approval.get('cost_policy') == 'no_cost_cap', 'approval scope conflict')
    # The repair cost-policy amendment is NOT live execution/publication authority.
    # Snapshot it, but derive authority only from this run's explicit approval.
    amendment = decode(take(auto['approval_amendment_ref']))
    require(amendment.get('cost_policy') == 'no_cost_cap', 'cost policy amendment conflict')
    waiver = decode(take(approval['prior_approval_ref']))
    require(waiver.get('execution_authorized') is True and waiver.get('phase') == 'P2' and waiver.get('user_quote') and vid in waiver.get('candidate_versions', []), 'execution approval missing')
    require(waiver.get('cost_policy') == 'no_cost_cap' and all(waiver.get(k) == v for k, v in MODEL.items()), 'waiver policy/model conflict')
    result = decode(ref(req['result']))
    require(all(result.get(k) == v for k, v in MODEL.items()) and result.get('response_model') == MODEL['model'], 'result model conflict')
    for k, v in dict(policy_revision=POLICY, policy_sha256=req['policy']['sha256'],
                     prompt_revision=req['prompt']['revision'], prompt_sha256=req['prompt']['sha256'],
                     approval_ref=req['approval']['path'], approval_sha256=req['approval']['sha256']).items():
        require(result.get(k) == v, 'result binding conflict: ' + k)
    require(bool(re.fullmatch('[0-9a-f]{64}', result.get('instructions_sha256', ''))) and result.get('route_base_url') and result.get('api_mode'), 'missing execution route/instructions')
    if canonical_approval:
        for key in ('policy_revision', 'policy_sha256', 'prompt_revision', 'prompt_sha256', 'instructions_sha256'):
            require(approval.get(key) == result.get(key), 'compile approval binding conflict: ' + key)
        require(approval.get('approved_route') == dict(base_url=result['route_base_url'], api_mode=result['api_mode']), 'compile route conflict')
        require(sha(take(approval['instructions_path'])) == result['instructions_sha256'], 'compile instructions conflict')
        document_hashes = approval.get('document_sha256')
        expected_documents = {'AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/STATE-CONTRACTS.md',
                              '_meta/COMPILATION.md', '_meta/automation-contracts.schema.json'}
        require(isinstance(document_hashes, dict) and set(document_hashes) == expected_documents, 'compile document set conflict')
        for path, expected in document_hashes.items():
            require(sha(take(path)) == expected, 'compile document conflict: ' + path)
        require(approval.get('sources', {}).get(vid) == {key: result.get(key) for key in
                ('source_sha256', 'source_bytes', 'metadata_sha256')}, 'compile source approval conflict')
    require(result.get('completed') is True and result.get('error') is None and result.get('response_status') == 'completed', 'incomplete response')
    source = req['source']
    exact_keys(source, 'path sha256 metadata_path metadata_sha256', 'source')
    expected_source = f'raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html'
    require(source['path'] == expected_source and source['metadata_path'] == expected_source.replace('source.html', 'source.json'), 'source path conflict')
    source_data = take(source['path'])
    metadata_data = take(source['metadata_path'])
    require(sha(source_data) == source['sha256'] == result.get('source_sha256') and len(source_data) == result.get('source_bytes'), 'source integrity conflict')
    require(sha(metadata_data) == source['metadata_sha256'] == result.get('metadata_sha256'), 'metadata integrity conflict')
    meta = decode(metadata_data)
    require(meta.get('version_id') == vid and meta.get('schema') == 'arxiv-html-source/v1' and meta.get('html_file') == 'source.html', 'source metadata invalid')
    require(meta.get('html_sha256') == source['sha256'] and meta.get('html_bytes') == len(source_data), 'metadata source mismatch')
    report = _verify_result(fs.root, vid, result)
    require(report.get('passed') is True and report.get('checks') and all(c.get('ok') is True for c in report['checks']), 'fresh structural verification failed')
    doc = report.get('document')
    require(isinstance(doc, dict) and doc.get('main_text_complete') is True and doc.get('version_id') == vid, 'invalid verified document')
    require(isinstance(doc.get('title'), str) and doc['title'].strip() and isinstance(doc.get('markdown_body'), str) and doc['markdown_body'].strip(), 'empty document')
    require(doc.get('read_scope') and isinstance(doc.get('unread_scope'), list) and doc.get('claims'), 'incomplete read/evidence scope')
    review = decode(ref(req['agent_review']))
    exact_keys(review, 'schema actor reviewer reviewed_at version_id result_sha256 source_sha256 requested_scope read_scope unread_scope evidence_scope reviewed_claim_ids claims', 'agent review')
    require(review['schema'] == 'pkm-agent-evidence-review/v1' and review['actor'] == 'agent' and isinstance(review['reviewer'], str) and review['reviewer'].strip(), 'agent semantic review required')
    require(datetime.fromisoformat(review['reviewed_at']).tzinfo is not None, 'review timezone missing')
    for key, expected in dict(version_id=vid, result_sha256=req['result']['sha256'], source_sha256=source['sha256'], requested_scope=SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope']).items():
        require(review[key] == expected, 'semantic review binding mismatch: ' + key)
    claims = doc['claims']
    ids = [c['id'] for c in claims]
    require(len(set(ids)) == len(ids) and review['reviewed_claim_ids'] == ids, 'not all claims semantically reviewed')
    require(isinstance(review['evidence_scope'], list) and set(review['evidence_scope']) == {c['anchor'] for c in claims}, 'review evidence scope mismatch')
    require(isinstance(review['claims'], list) and len(review['claims']) == len(claims), 'review claims missing')
    for claim, checked in zip(claims, review['claims']):
        exact_keys(checked, 'id anchor quote_sha256 verdict rationale', 'reviewed claim')
        require(checked['id'] == claim['id'] and checked['anchor'] == claim['anchor'] and checked['quote_sha256'] == sha(claim['quote'].encode()), 'review claim binding mismatch')
        require(checked['verdict'] == 'supported' and isinstance(checked['rationale'], str) and checked['rationale'].strip(), 'unsupported/unreviewed claim')
    require(isinstance(req['consumed_wiki_refs'], list), 'invalid consumed Wiki refs')
    import yaml
    for consumed in req['consumed_wiki_refs']:
        require(consumed['path'].split('/')[0] in ('entities', 'concepts', 'comparisons', 'queries'), 'invalid consumed page')
        raw = ref(consumed, 'revision').decode()
        front = yaml.safe_load(raw.split('---', 2)[1])
        require(str(front.get('revision')) == consumed['revision'], 'consumed revision conflict')
    return dict(request=req, request_path=request_path, result=result, document=doc,
                report=report, schema=schema, snapshots=snapshots)


def index_parts(text):
    headings = list(re.finditer(r'^##[ \t]+Entities(?:[ \t]+[^\n]*)?[ \t]*$', text, re.M))
    require(len(headings) == 1, 'ambiguous/missing Entities heading')
    start = headings[0].start()
    nxt = re.search(r'^##[ \t]+', text[headings[0].end():], re.M)
    end = headings[0].end() + nxt.start() if nxt else len(text)
    headers = list(re.finditer(r'Last updated: \d{4}-\d{2}-\d{2} \| Total pages: \d+', text))
    require(len(headers) == 1, 'ambiguous/missing index count')
    return start, end, headers[0]


def page_count(fs, output):
    paths = set()
    for directory in ['entities', 'concepts', 'comparisons', 'queries']:
        base = fs.root / directory
        require(base.is_dir() and not base.is_symlink(), 'unsafe knowledge directory')
        for parent, dirs, files in os.walk(base, followlinks=False):
            require(all(not (Path(parent) / d).is_symlink() for d in dirs), 'symlink knowledge directory')
            for name in files:
                p = Path(parent) / name
                require(not p.is_symlink(), 'symlink knowledge page')
                if name.endswith('.md'):
                    relative = p.relative_to(fs.root).as_posix()
                    fs.read(relative)
                    paths.add(relative)
    paths.add(output)
    return len(paths)


def new_plan(fs, context, vid, run, now):
    req, doc = context['request'], context['document']
    state_bytes = fs.read(STATE)
    state = decode(state_bytes)
    schema_validate(context['schema'], state, 'compilation')
    require(not state['safety_block'] and not state['enabled'], 'compilation safety block/enabled')
    selected = [i for i in state['items'] if i['version_id'] == vid]
    require(len(selected) == 1, 'missing/duplicate state item')
    item = selected[0]
    require(item['format'] == 'html' and item['human_review'] is None, 'reviewed/non-HTML item')
    for key, value in dict(source_path=req['source']['path'], source_sha256=req['source']['sha256'],
                           source_bytes=context['result']['source_bytes'], metadata_path=req['source']['metadata_path'],
                           metadata_sha256=req['source']['metadata_sha256']).items():
        require(item[key] == value, 'state input conflict: ' + key)
    require(all(t['status'] == 'committed' for t in state['transactions']), 'other unresolved transaction')
    require(item['status'] in ('ready_to_publish', 'reading', 'retryable_failed', 'partial', 'queued', 'blocked_approval'), 'invalid item transition')
    require(not item['output_refs'] and item['receipt_ref'] is None and item['work_key'] is None, 'existing output state')
    output = req['output_path']
    require(fs.read(output, True) is None, 'existing output; never overwrite')
    work = dict(source='arxiv', version_id=vid, source_sha256=req['source']['sha256'], policy_revision=POLICY,
                policy_sha256=req['policy']['sha256'], prompt_revision=req['prompt']['revision'],
                prompt_sha256=req['prompt']['sha256'], requested_scope=SCOPE)
    key = sha(canonical(work))
    tx = 'p2-' + sha(canonical([run, req['result'], key]))[:32]
    base = req['result']['path'][:-len('-result.json')]
    journal_path, receipt_path = base + '-publish-journal.json', base + '-receipt.json'
    structural_path = base + '-publish-verification.json'
    require(fs.read(receipt_path, True) is None and fs.read(structural_path, True) is None, 'existing publication artifact')
    today = now.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    fm = dict(title=doc['title'], summary=' '.join(doc['title'].split()), created=today, updated=today,
              last_reviewed=None, type='entity', status='draft', tags=['paper', 'llm-security', 'agent-security'],
              sources=[req['source']['path']], confidence='medium', contested=False, contradictions=[],
              schema='pkm-knowledge-page/v1', revision='1', transaction_id=tx, policy_revision=POLICY,
              prompt_revision=req['prompt']['revision'], generation_ref=req['result']['path'],
              read_scope=doc['read_scope'], unread_scope=doc['unread_scope'], review_state='unreviewed')
    taxonomy = fs.read('SCHEMA.md').decode().split('## 7. 태그', 1)
    require(len(taxonomy) == 2 and all('`' + tag + '`' in taxonomy[1].split('\n## ', 1)[0] for tag in fm['tags']), 'unapproved tags')
    page = ('---\n' + ''.join(k + ': ' + json.dumps(v, ensure_ascii=False, allow_nan=False) + '\n' for k, v in fm.items()) + '---\n\n' + doc['markdown_body'].rstrip() + '\n').encode()
    before_index = fs.read('index.md').decode()
    start, end, header = index_parts(before_index)
    link = '[[' + output[:-3] + ']]'
    require(link not in before_index, 'existing index entry')
    title = ' '.join(doc['title'].split()).replace('[', '&#91;').replace(']', '&#93;')
    entry = f'- {link} — {title} (draft, P2)\n'
    old_section = before_index[start:end]
    new_section = re.sub(r'^아직 작성된 페이지가 없다\.\n?', '', old_section, flags=re.M).rstrip() + '\n\n' + entry + '\n'
    new_header = f'Last updated: {today} | Total pages: {page_count(fs, output)}'
    after_index = before_index[:start] + new_section + before_index[end:]
    after_index = after_index.replace(header.group(), new_header, 1)
    log = fs.read('log.md')
    event = (f'\n## [{today}] create | P2 draft — arXiv {vid}\n\n'
             f'<!-- publication-event:{tx} -->\n- Page: `{output}`; run: `{run}`.\n'
             f'- Source SHA-256: `{req["source"]["sha256"]}`; work_key: `{key}`.\n'
             f'- Agent evidence review: `{req["agent_review"]["path"]}`; structural checks: `{structural_path}`.\n'
             '- Draft/unreviewed; no human review, visual inspection or experimental reproduction claimed.\n').encode()
    refs = [dict(path=output, sha256=sha(page), revision='1')]
    receipt = dict(schema='pkm-publication-receipt/v1', transaction_id=tx, run_id=Path(run).name,
                   work_key=key, actual_input_hashes=context['snapshots'], output_refs=refs,
                   committed_at=now.isoformat(), read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
                   evidence_check_ref=req['agent_review']['path'], structural_check_ref=structural_path,
                   human_review_ref=None, model_route={k: context['result'][k] for k in (*MODEL, 'response_model', 'route_base_url', 'api_mode', 'instructions_sha256')},
                   budget_usage_ref=req['result']['path'], cost_usd=context['result'].get('cost_usd'))
    item.update(status='published_draft', reason='Agent evidence review and durable draft publication; human unreviewed',
                requested_scope=SCOPE, read_scope=doc['read_scope'], unread_scope=doc['unread_scope'],
                resume_at=None, work_key=key, output_refs=refs, receipt_ref=receipt_path, human_review=None)
    state['transactions'].append(dict(transaction_id=tx, journal_path=journal_path, status='committed'))
    state['receipts'].append(receipt_path)
    require(len({e['event_id'] for e in state['cost_events']}) == len(state['cost_events']), 'duplicate cost event')
    charged = context['result'].get('cost_usd')
    state['cost_events'].append(dict(event_id=tx, run_id=Path(run).name, role='pilot', scope_id=vid,
                                     created_at=now.isoformat(), kst_day=today,
                                     status='unknown' if charged is None else 'settled',
                                     reserved_usd=None, charged_usd=charged, usage_receipt=req['result']['path']))
    state['last_run'] = run
    schema_validate(context['schema'], state, 'compilation')
    after_state = encoded(state)
    targets = [dict(path=output, before_hash=None, after_hash=sha(page), before_image=None, after_image=page.decode(), before_image_ref=None, after_image_ref=journal_path + '#/plan/targets/0/after_image', order=1, stage='planned'),
               dict(path='index.md', before_hash=sha(before_index.encode()), after_hash=sha(after_index.encode()), order=2, stage='planned'),
               dict(path='log.md', before_hash=sha(log), after_hash=sha(log + event), order=3, stage='planned'),
               dict(path=receipt_path, before_hash=None, after_hash=sha(encoded(receipt)), order=4, stage='planned'),
               dict(path=STATE, before_hash=sha(state_bytes), after_hash=sha(after_state), order=5, stage='planned')]
    return dict(schema='pkm-publication-journal/v1', transaction_id=tx, run_id=Path(run).name, role='pilot',
                started_at=now.isoformat(), approval_refs=[req['approval']] +
                ([req['publication_approval']] if 'publication_approval' in req else []), input_hashes=context['snapshots'],
                targets=targets, log_event_id=tx, status='prepared', work_key=key,
                journal_path=journal_path, receipt=receipt, state_after=state,
                structural_path=structural_path, structural_report=context['report'],
                index=dict(before_section=old_section, after_section=new_section,
                           before_header=header.group(), after_header=new_header),
                log=dict(prefix_bytes=len(log), prefix_sha256=sha(log), event=event.decode()))


def write_journal(fs, plan, before=None):
    data = encoded(dict(plan=plan, plan_sha256=sha(canonical(plan))))
    fs.write(plan['journal_path'], data, before)


def check_snapshots(fs, snapshots):
    for path, expected in snapshots.items():
        require(sha(fs.read(path)) == expected, 'input changed: ' + path)


def read_journal(fs, path):
    raw = fs.read(path, True)
    if raw is None:
        return None
    envelope = decode(raw)
    exact_keys(envelope, 'plan plan_sha256', 'journal envelope')
    plan = envelope['plan']
    require(sha(canonical(plan)) == envelope['plan_sha256'], 'journal hash conflict')
    require(plan['schema'] == 'pkm-publication-journal/v1' and plan['journal_path'] == path, 'journal identity conflict')
    require(plan['status'] in ('prepared', 'committed'), 'unresolved journal status')
    return plan


def reject_other_unresolved(fs, own_path):
    state = decode(fs.read(STATE))
    for tx in state['transactions']:
        require(tx['status'] == 'committed' or tx['journal_path'] == own_path, 'other unresolved state transaction')
    base = fs.root / '_meta/runs/wiki'
    for parent, dirs, files in os.walk(base, followlinks=False):
        require(all(not (Path(parent) / d).is_symlink() for d in dirs), 'unsafe run directory')
        for name in files:
            if name.endswith('-publish-journal.json') or name in ('publish-journal.json', 'journal.json'):
                path = (Path(parent) / name).relative_to(fs.root).as_posix()
                if path == own_path:
                    continue
                try:
                    other = read_journal(fs, path)
                    require(other is not None and other['status'] == 'committed', 'other unresolved journal')
                    require(any(t['transaction_id'] == other['transaction_id'] and t['journal_path'] == path and t['status'] == 'committed' for t in state['transactions']), 'unresolved journal/state mismatch')
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError('other unresolved/unrecognized journal: ' + path) from exc


def validate_plan(fs, plan, context, vid, run):
    base = context['request']['result']['path'][:-len('-result.json')]
    expected = [context['request']['output_path'], 'index.md', 'log.md', base + '-receipt.json', STATE]
    require([t['path'] for t in plan['targets']] == expected, 'journal target conflict')
    require(plan['structural_path'] == base + '-publish-verification.json' and plan['journal_path'] == base + '-publish-journal.json', 'journal artifact path conflict')
    require(plan['input_hashes'] == context['snapshots'], 'journal input snapshot conflict')
    require(plan['run_id'] == Path(run).name, 'journal run conflict')
    targets = plan['targets']
    require(targets[0]['before_hash'] is None and targets[0]['before_image'] is None and targets[3]['before_hash'] is None, 'overwrite journal forbidden')
    require(sha(targets[0]['after_image'].encode()) == targets[0]['after_hash'], 'journal knowledge hash conflict')
    require(sha(encoded(plan['receipt'])) == targets[3]['after_hash'] and sha(encoded(plan['state_after'])) == targets[4]['after_hash'], 'journal receipt/state hash conflict')
    require(plan['receipt']['actual_input_hashes'] == context['snapshots'] and plan['receipt']['transaction_id'] == plan['transaction_id'], 'receipt input/transaction conflict')
    require(plan['receipt']['output_refs'] == [dict(path=expected[0], sha256=targets[0]['after_hash'], revision='1')], 'receipt outputs conflict')
    req = context['request']
    work = dict(source='arxiv', version_id=vid, source_sha256=req['source']['sha256'], policy_revision=POLICY,
                policy_sha256=req['policy']['sha256'], prompt_revision=req['prompt']['revision'],
                prompt_sha256=req['prompt']['sha256'], requested_scope=SCOPE)
    require(sha(canonical(work)) == plan['work_key'] == plan['receipt']['work_key'], 'work key conflict')
    require(plan['transaction_id'] == 'p2-' + sha(canonical([run, req['result'], plan['work_key']]))[:32], 'transaction identity conflict')
    schema_validate(context['schema'], plan['state_after'], 'compilation')
    schema_validate(context['schema'], decode(fs.read(STATE)), 'compilation')


def classify(fs, plan):
    """Validate ALL current targets before writing any recovery step.

    Index comparison is the owned Entities section and count header; unrelated
    sections may advance. The log comparison is a preserved prefix plus exactly
    one complete event, not an old whole-file image. No rollback is attempted.
    """
    states = []
    targets = plan['targets']
    for target in (targets[0], targets[3], targets[4]):
        raw = fs.read(target['path'], True)
        got = sha(raw) if raw is not None else None
        require(got in (target['before_hash'], target['after_hash']), 'unexpected target/state conflict: ' + target['path'])
        states.append(got == target['after_hash'])
    index = fs.read('index.md').decode()
    start, end, header = index_parts(index)
    parts = plan['index']
    pair = (index[start:end], header.group())
    old = (parts['before_section'], parts['before_header'])
    new = (parts['after_section'], parts['after_header'])
    require(pair in (old, new), 'unexpected owned index edit')
    log = fs.read('log.md')
    spec = plan['log']
    prefix = spec['prefix_bytes']
    require(type(prefix) is int and prefix >= 0 and len(log) >= prefix and sha(log[:prefix]) == spec['prefix_sha256'], 'log prefix conflict')
    event = spec['event'].encode()
    marker = ('<!-- publication-event:' + plan['log_event_id'] + ' -->').encode()
    count = log[prefix:].count(marker)
    require(count in (0, 1) and log.count(event) == count and marker not in log[:prefix], 'partial/duplicate log event conflict')
    # Reject a torn append, rather than adding a complete event after a fragment.
    if not count:
        require(not any(log.endswith(event[:n]) for n in range(2, len(event))), 'partial log append conflict')
    ordered = [states[0], pair == new, bool(count), states[1], states[2]]
    require(ordered == sorted(ordered, reverse=True), 'out-of-order/missing committed output')
    evidence = fs.read(plan['structural_path'], True)
    require(evidence in (None, encoded(plan['structural_report'])), 'structural evidence conflict')
    require(not any(ordered) or evidence is not None, 'missing structural evidence')
    return ordered


def verify_committed(fs, plan, context, vid):
    """Relevant state/receipt/output verification allows later unrelated commits."""
    targets = plan['targets']
    require(fs.read(targets[0]['path'], True) == targets[0]['after_image'].encode(), 'missing/tampered output; not noop')
    require(fs.read(targets[3]['path'], True) == encoded(plan['receipt']), 'missing/tampered receipt; not noop')
    require(fs.read(plan['structural_path'], True) == encoded(plan['structural_report']), 'missing/tampered structural evidence')
    state = decode(fs.read(STATE))
    schema_validate(context['schema'], state, 'compilation')
    require(not state['safety_block'] and not state['enabled'], 'compilation safety block/enabled')
    current = [i for i in state['items'] if i['version_id'] == vid]
    expected = [i for i in plan['state_after']['items'] if i['version_id'] == vid]
    require(len(current) == 1 and current == expected, 'committed item edited; not noop')
    require(targets[3]['path'] in state['receipts'] and any(t == dict(transaction_id=plan['transaction_id'], journal_path=plan['journal_path'], status='committed') for t in state['transactions']), 'receipt/transaction state conflict')
    index = fs.read('index.md').decode()
    start, end, header = index_parts(index)
    link = '[[' + targets[0]['path'][:-3] + ']]'
    require(index.count(link) == 1 and link in index[start:end], 'missing/duplicate committed index entry')
    require(int(header.group().split('Total pages: ')[1]) == page_count(fs, targets[0]['path']), 'index page count conflict')
    log = fs.read('log.md')
    spec = plan['log']
    require(sha(log[:spec['prefix_bytes']]) == spec['prefix_sha256'] and log.count(spec['event'].encode()) == 1, 'committed log evidence conflict')


def apply_plan(fs, plan, context, hook, owns_lock):
    targets = plan['targets']
    classify(fs, plan)
    def guard():
        owns_lock()
        check_snapshots(fs, context['snapshots'])
        classify(fs, plan)
    def create_or_verify(path, value):
        old = fs.read(path, True)
        require(old is None or old == value, 'artifact conflict: ' + path)
        if old is None:
            fs.write(path, value, None)
    guard()
    create_or_verify(plan['structural_path'], encoded(plan['structural_report']))
    create_or_verify(targets[0]['path'], targets[0]['after_image'].encode())
    hook('after_page')
    guard()
    current = fs.read('index.md')
    text = current.decode()
    start, end, header = index_parts(text)
    if (text[start:end], header.group()) == (plan['index']['before_section'], plan['index']['before_header']):
        new = text[:start] + plan['index']['after_section'] + text[end:]
        new = new.replace(plan['index']['before_header'], plan['index']['after_header'], 1)
        fs.write('index.md', new.encode(), current)
    hook('after_index')
    guard()
    current = fs.read('log.md')
    event = plan['log']['event'].encode()
    if event not in current:
        fs.append('log.md', event, current)
    hook('after_log')
    guard()
    create_or_verify(targets[3]['path'], encoded(plan['receipt']))
    hook('after_receipt')
    guard()
    current = fs.read(STATE)
    if sha(current) == targets[4]['before_hash']:
        fs.write(STATE, encoded(plan['state_after']), current)
    hook('after_state')
    guard()
    old = fs.read(plan['journal_path'])
    plan['status'] = 'committed'
    for target in plan['targets']:
        target['stage'] = 'verified'
    write_journal(fs, plan, old)


def publish(root, vid, run, attempt, *, _hook=None, _now=None):
    require(isinstance(vid, str) and bool(re.fullmatch(VID_RE, vid)), 'invalid version ID')
    # Legacy slash IDs require a percent-encoded state path unsupported by the
    # current state schema; fail closed rather than normalize the supplied token.
    require('/' not in vid, 'legacy ID paths not supported by current state schema')
    require(isinstance(run, str) and bool(re.fullmatch(r'_meta/runs/wiki/[A-Za-z0-9_-]+', run)), 'invalid run path')
    require(isinstance(attempt, str) and bool(re.fullmatch(r'[A-Za-z0-9_-]+-result\.json', attempt)), 'invalid attempt basename')
    now = _now or datetime.now(timezone.utc)
    require(now.tzinfo is not None, 'timezone required')
    kst_time = now.astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')
    if kst_time >= '23:55' or kst_time < '01:35':
        return dict(status='skipped_busy', reason='collector priority window')
    fs = Files(root)
    hook = _hook or (lambda stage: None)
    context = inputs(fs, vid, run, attempt)
    check_snapshots(fs, context['snapshots'])
    state_snapshot = fs.read(STATE)
    journal_path = context['request']['result']['path'][:-len('-result.json')] + '-publish-journal.json'
    journal_snapshot = fs.read(journal_path, True)
    reject_other_unresolved(fs, journal_path)
    plan = read_journal(fs, journal_path)
    if plan is None:
        plan = new_plan(fs, context, vid, run, now)
    else:
        validate_plan(fs, plan, context, vid, run)
        if plan['status'] == 'committed':
            verify_committed(fs, plan, context, vid)
        else:
            classify(fs, plan)
    hook('before_lock')
    now = _now or datetime.now(timezone.utc)
    kst_time = now.astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')
    if kst_time >= '23:55' or kst_time < '01:35':
        return dict(status='skipped_busy', reason='collector priority window')
    with collection_lock(fs, Path(run).name, plan['transaction_id'], now) as owned:
        if not owned:
            return dict(status='skipped_busy', reason='collection.lock exists; never steal')
        hook('after_lock')
        owned()
        fresh = inputs(fs, vid, run, attempt)
        require(fresh['snapshots'] == context['snapshots'], 'inputs changed under lock')
        check_snapshots(fs, fresh['snapshots'])
        require(fs.read(STATE) == state_snapshot, 'state changed under lock')
        require(fs.read(journal_path, True) == journal_snapshot, 'journal changed under lock')
        reject_other_unresolved(fs, journal_path)
        if journal_snapshot is None:
            plan = new_plan(fs, fresh, vid, run, now)
            write_journal(fs, plan)
        else:
            validate_plan(fs, plan, fresh, vid, run)
            if plan['status'] == 'committed':
                verify_committed(fs, plan, fresh, vid)
                return dict(status='noop', work_key=plan['work_key'], output_refs=plan['receipt']['output_refs'])
        owned()
        apply_plan(fs, plan, fresh, hook, owned)
        verify_committed(fs, plan, fresh, vid)
        return dict(status='published_draft', work_key=plan['work_key'], output_refs=plan['receipt']['output_refs'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vid')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--run', default='_meta/runs/wiki/20260929T083140Z-p2-resume')
    parser.add_argument('--attempt', default='attempt-result.json')
    args = parser.parse_args(argv)
    try:
        result = publish(args.root, args.vid, args.run, args.attempt)
    except (ValueError, OSError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({'status': 'blocked_conflict', 'error': str(exc)}))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())