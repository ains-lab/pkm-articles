"""P3 daily orchestration. Live execution requires a separate P3 grant."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from contextlib import contextmanager
import copy
import os
import re
import stat
import time
import uuid
from typing import Any
import p3_common as C


def scheduler_gate(fs, auto, approval, observed, observer, synthetic):
    job=auto['jobs']['daily_compile']
    C.require(approval.get('run') is None and approval.get('cron_id')==job['cron_id'] and
        isinstance(job['cron_id'],str) and job['cron_id']!='4cff5b4f10ec' and
        all(auto[k] is True for k in ('enabled','registration_authorized','activation_authorized')) and
        job['enabled'] is True and job['registration_status']=='active','scheduled_authority')
    C.require(approval.get('edit_freeze')==dict(mode='daily_window',timezone='Asia/Seoul',start='02:00',end='02:45'), 'publication_freeze_scope')
    local=observed.astimezone(timezone(timedelta(hours=9))).strftime('%H:%M')
    C.require('02:00'<=local<'02:45','edit_freeze_window')
    if observer is None:
        C.require(not synthetic,'synthetic_requires_scheduler_observer')
        from cron.jobs import get_job
        observer=get_job
    registered=C.decode(fs.read(job['registration_readback']))
    live=observer(job['cron_id'])
    C.require(registered.get('schema')=='pkm-p3-registration/v1' and isinstance(live,dict),'scheduler_projection')
    if not isinstance(live,dict):
        raise ValueError('scheduler_projection')
    expected=dict(id=job['cron_id'],enabled=True,model=C.MODEL['model'],provider=C.MODEL['provider'],
        reasoning_effort=C.MODEL['reasoning_effort'],workdir=str(fs.root),skills=['llm-wiki'],deliver='local',failure_deliver='local',
        no_agent=False,attach_to_session=False,monitor_script=None,monitor_url=None,
        prompt=fs.read(C.PROMPT).decode().strip())
    for record in (registered['job'],live):
        C.require(all(C.canonical(record.get(k))==C.canonical(v) for k,v in expected.items()) and
            record.get('schedule',{}).get('kind')=='cron' and record['schedule'].get('expr')=='0 17 * * *' and
            not record.get('script') and not record.get('monitor') and not record.get('context_from') and
            not record.get('continuity') and not record.get('base_url'), 'scheduler_projection')
        C.require(isinstance(record.get('next_run_at'),str) and
            datetime.fromisoformat(record['next_run_at']).tzinfo is not None,'scheduler_next_run')


def preflight(*, root=C.ROOT, run, approval_ref, synthetic=False, now=None, scheduler_observer=None):
    root = C.synthetic_root(root) if synthetic is True else Path(root).absolute()
    C.require(root == C.ROOT or synthetic is True, 'wrong_root')
    C.require(type(synthetic) is bool, 'synthetic_flag')
    C.require(synthetic is True or scheduler_observer is None, 'test_injection_forbidden')
    C.require(isinstance(run,str) and re.fullmatch(r'_meta/runs/wiki/[A-Za-z0-9_-]+',run), 'run_path')
    C.require(isinstance(approval_ref,str) and approval_ref.startswith('_meta/runs/wiki/') and approval_ref.endswith('/execution-approval.json'), 'approval_path')
    fs=C.helper('publish').Files(root)
    auto=C.decode(fs.read('_meta/automation.json'))
    C.require(auto.get('phase_authorizations',{}).get('P3') is True, 'p3_execution_not_authorized')
    C.require(auto.get('policy_revision')==C.POLICY and auto.get('contract_revision')==C.CONTRACT and auto.get('wiki_root')==str(root), 'policy_identity')
    C.require(C.canonical(auto.get('model'))==C.canonical(C.MODEL), 'model_pin')
    C.require(C.canonical(auto.get('pdf_reading'))==C.canonical(C.PDF_READING), 'pdf_policy')
    C.require(auto.get('budget',{}).get('cost_policy')=='no_cost_cap', 'cost_policy')
    transfer=auto.get('transfer',{})
    C.require(all(transfer.get(k) is False for k in ('automatic_chat_capture','external_assets','external_novelty_search','images','secrets_or_sensitive_personal_data')), 'forbidden_transfer')
    C.require(transfer.get('local_html_text') is True and transfer.get('pdf_content') is True, 'text_transfer')
    schema=C.decode(fs.read(C.DOCS[-1]))
    C.helper('publish').schema_validate(schema,auto,'automation')
    raw=fs.read(approval_ref); approval=C.decode(raw)
    C.require(approval.get('schema')=='pkm-p3-execution-approval/v1' and approval.get('actor')=='user' and
        approval.get('approved') is True and approval.get('phase')=='P3' and
        isinstance(approval.get('user_request'),str) and approval['user_request'].strip(), 'execution_grant')
    C.require(approval.get('wiki_root')==str(root) and approval.get('mode') in ('manual','scheduled'), 'execution_scope')
    scheduled=approval['mode']=='scheduled'
    observed=now or datetime.now(timezone.utc)
    C.require(observed.tzinfo is not None,'timezone_required')
    if scheduled:
        scheduler_gate(fs,auto,approval,observed,scheduler_observer,synthetic)
    else:
        C.require(approval.get('run')==run and auto['enabled'] is False and auto['jobs']['daily_compile']['enabled'] is False, 'manual_mode_only')
        C.require(approval.get('edit_freeze')=={'mode':'run','run':run},'publication_freeze_scope')
    C.require(approval.get('source_scope')=='current_and_future_collected' and approval.get('formats')==['html','pdf'] and
        approval.get('collector_id')=='4cff5b4f10ec', 'source_scope')
    C.require(C.canonical(approval.get('model'))==C.canonical(C.MODEL) and C.canonical(approval.get('route'))==C.canonical(C.ROUTE), 'approval_model_route')
    C.require(approval.get('cost_policy')=='no_cost_cap' and approval.get('validated_publication_authorized') is True, 'publication_freeze_scope')
    snapshots=approval.get('snapshots',{})
    expected_snapshots=set((*C.DOCS,C.PROMPT,'_meta/automation.json'))
    if scheduled:expected_snapshots.add(auto['jobs']['daily_compile']['registration_readback'])
    C.require(set(snapshots)==expected_snapshots, 'governing_snapshot_set')
    C.helper('publish').check_snapshots(fs,snapshots)
    state=C.decode(fs.read(C.STATE))
    C.helper('publish').schema_validate(schema,state,'compilation')
    C.require(state['enabled'] is scheduled and state['safety_block'] is False, 'safety_block_or_state_mode')
    C.require(len({i['version_id'] for i in state['items']})==len(state['items']), 'duplicate_item')
    C.require(all(t['status']=='committed' for t in state['transactions']), 'unresolved_transaction')
    ctx=dict(root=root,fs=fs,run=run,auto=auto,schema=schema,state=state,synthetic=synthetic,
        approval_ref=approval_ref,approval_sha256=C.sha(raw),approval=approval,
        snapshots=dict(snapshots,**{approval_ref:C.sha(raw)}),
        policy_sha256=snapshots['_meta/automation.json'],prompt_sha256=snapshots[C.PROMPT],
        prompt=fs.read(C.PROMPT).decode(),model=dict(C.MODEL),route=dict(C.ROUTE),requested_scope=C.SCOPE,
        wiki=[],now=observed)
    def guard():
        tick(ctx)
        fresh=preflight(root=root,run=run,approval_ref=approval_ref,synthetic=synthetic,now=now,scheduler_observer=scheduler_observer)
        C.require(fresh['approval_sha256']==ctx['approval_sha256'], 'approval_drift')
        C.helper('publish').check_snapshots(fs,ctx['snapshots'])
        tick(ctx)
    ctx['guard']=guard
    return ctx


SOURCE_FIELDS=('source','version_id','format','source_path','source_sha256','source_bytes',
               'metadata_path','metadata_sha256','collected_at')
RUN_LOCK='_meta/locks/daily-run.lock'


def tick(ctx):
    C.check_deadline(ctx.get('deadline'),ctx.get('clock',time.monotonic))


def reject_dangling_reservations(ctx,items):
    """A started attempt without durable terminal evidence is never replayed."""
    fs=ctx['fs'];by_id={i['version_id']:i for i in items}
    for parent,dirs,files in os.walk(fs.root/'_meta/runs/wiki',followlinks=False):
        tick(ctx)
        C.require(all(not (Path(parent)/d).is_symlink() for d in dirs),'unsafe_run_tree')
        for name in files:
            if not name.endswith('-reservation.json'):continue
            path=(Path(parent)/name).relative_to(fs.root).as_posix()
            record=C.decode(fs.read(path));tick(ctx)
            if record.get('schema')!='pkm-p3-reservation/v1':continue
            outcome=fs.read(path.removesuffix('-reservation.json')+'-outcome.json',True)
            if outcome is not None:
                outcome=C.decode(outcome)
                C.require(outcome.get('schema')=='pkm-p3-outcome/v1' and
                    outcome.get('version_id')==record['version_id'] and
                    outcome.get('approval_sha256')==record.get('approval_sha256'),'outcome_binding')
                continue
            item=by_id.get(record['version_id'])
            C.require(item is not None and item['status']=='published_draft' and
                item['receipt_ref'].startswith(path.removesuffix('-reservation.json')),'unresolved_reservation')


def inventory(ctx):
    """Metadata and hash inventory, not paper interpretation or a collector."""
    tick(ctx);ctx['guard']();tick(ctx)
    fs=ctx['fs']; state=C.decode(fs.read(C.STATE))
    old={i['version_id']:i for i in state['items']}
    result=[]; observed=set()
    base='raw/articles/4cff5b4f10ec'
    with fs.parent(base+'/sentinel') as (fd,_):
        tick(ctx)
        names=sorted(os.listdir(fd))
        tick(ctx)
    for name in names:
        tick(ctx)
        if name=='index.md':
            continue
        C.require(re.fullmatch(r'arxiv-[0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*',name) is not None,'invalid_source_directory')
        vid=name.removeprefix('arxiv-'); metadata_path=base+'/'+name+'/source.json'
        raw=fs.read(metadata_path);tick(ctx);m=C.decode(raw)
        formats=[f for f in ('html','pdf') if f+'_file' in m]
        C.require(len(formats)==1,'source_format_conflict')
        fmt=formats[0]
        C.require(m.get('schema')=='arxiv-'+fmt+'-source/v1' and m.get('version_id')==vid and
            m.get('source')=='arxiv' and m.get('owning_cron_id')=='4cff5b4f10ec','source_identity')
        C.require(m.get(fmt+'_file')=='source.'+fmt and m.get('http_status')==200 and
            m.get('source_url')==f'https://arxiv.org/{fmt}/{vid}' and
            m.get('preprocessing') is False and m.get('offline_assets_bundled') is False and
            m.get('capture_method')=='http_response_body_no_rewrite','source_provenance')
        source_path=base+'/'+name+'/source.'+fmt
        data=fs.read(source_path)
        tick(ctx)
        C.require(type(m.get(fmt+'_bytes')) is int and m[fmt+'_bytes']==len(data) and
            m.get(fmt+'_sha256')==C.sha(data),'source_integrity')
        with fs.parent(source_path) as (fd,_):
            C.require(set(os.listdir(fd))=={'source.json','source.'+fmt},'unexpected_source_files')
        collected=datetime.fromisoformat(m['collected_at'])
        C.require(collected.tzinfo is not None,'source_timestamp')
        item: dict[str, Any]=dict(source='arxiv',version_id=vid,format=fmt,source_path=source_path,
            source_sha256=C.sha(data),source_bytes=len(data),metadata_path=metadata_path,
            metadata_sha256=C.sha(raw),collected_at=m['collected_at'])
        if vid in old:
            C.require(all(old[vid][k]==item[k] for k in SOURCE_FIELDS),'ledger_source_conflict')
            item=copy.deepcopy(old[vid])
        else:
            item.update(status='blocked_approval',reason='collected source pending execution gate',requested_scope=None,
                read_scope=[],unread_scope=[],resume_at=None,work_key=None,output_refs=[],receipt_ref=None,
                failure_count=0,human_review=None)
        C.require(vid not in observed,'duplicate_source')
        observed.add(vid); result.append(item)
    C.require(set(old)<=observed,'missing_stored_source')
    return result


def select(items, limit):
    C.require(type(limit) is int and 0<limit<=5,'selection_limit')
    eligible=[i for i in items if i['status'] in ('blocked_approval','queued','partial','retryable_failed') and
              i['human_review'] is None and i['failure_count']<3]
    return sorted(eligible,key=lambda i:(datetime.fromisoformat(i['collected_at']),i['version_id']))[:limit]


def published_context(ctx,items):
    """Verify committed outputs before no-op or consuming existing Wiki text."""
    ctx['guard']();fs=ctx['fs'];P=C.helper('publish')
    P.reject_other_unresolved(fs,'')
    state=C.decode(fs.read(C.STATE)); wiki={}
    index=fs.read('index.md').decode();log=fs.read('log.md')
    for item in items:
        if item['status']!='published_draft':continue
        C.require(item['receipt_ref'] in state['receipts'] and item['output_refs'] and item['read_scope'],'published_state_incomplete')
        raw=fs.read(item['receipt_ref']);receipt=C.decode(raw)
        refs=receipt.get('output_refs',receipt.get('actual_output_refs'))
        C.require(receipt.get('schema')=='pkm-publication-receipt/v1' and refs==item['output_refs'] and
            receipt.get('work_key')==item['work_key'] and
            receipt.get('actual_input_hashes',{}).get(item['source_path'])==item['source_sha256'],'receipt_binding')
        txs=[t for t in state['transactions'] if t['transaction_id']==receipt['transaction_id']]
        C.require(len(txs)==1 and txs[0]['status']=='committed','receipt_transaction')
        plan=P.read_journal(fs,txs[0]['journal_path'])
        C.require(plan is not None and plan['status']=='committed','receipt_journal')
        if plan is None:raise ValueError('receipt_journal')
        targets={t['path']:t['after_hash'] for t in plan['targets']}
        C.require(targets.get(item['receipt_ref'])==C.sha(raw),'receipt_journal_hash')
        preserved=ctx['approval'].get('preserved_publications',{}).get(item['version_id'])
        if preserved is not None:
            C.require(preserved==dict(work_key=item['work_key'],receipt_sha256=C.sha(raw),output_refs=refs),'preserved_publication_changed')
        else:
            work=dict(source='arxiv',version_id=item['version_id'],source_sha256=item['source_sha256'],
                policy_revision=C.POLICY,policy_sha256=ctx['policy_sha256'],prompt_revision=C.PROMPT_REV,
                prompt_sha256=ctx['prompt_sha256'],requested_scope=C.SCOPE)
            C.require(item['requested_scope']==C.SCOPE and item['work_key']==C.sha(C.canonical(work)),'legacy_publication_requires_preservation_grant')
        for ref in refs:
            path=ref['path']
            C.require(re.fullmatch(r'(entities|concepts|comparisons|queries)/[A-Za-z0-9_.-]+\.md',path) is not None,'wiki_path')
            data=fs.read(path)
            C.require(C.sha(data)==ref['sha256']==targets.get(path),'published_output_changed')
            C.require(index.count('[['+path[:-3]+']]')==1,'published_index_missing')
            C.require(path not in wiki or wiki[path]['sha256']==ref['sha256'],'wiki_revision_conflict')
            wiki[path]=dict(path=path,sha256=ref['sha256'],text=data.decode())
        spec=plan['log'];prefix=spec['prefix_bytes']
        C.require(C.sha(log[:prefix])==spec['prefix_sha256'] and log.count(spec['event'].encode())==1,'published_log_conflict')
    if wiki:
        _,_,header=P.index_parts(index)
        C.require(int(header.group().split('Total pages: ')[1])==P.page_count(fs,next(iter(wiki))),'published_page_count')
    return [wiki[p] for p in sorted(wiki)]


@contextmanager
def run_lock(ctx):
    """Durable no-steal run ownership, separate from short collection lock."""
    ctx['guard'](); fs=ctx['fs']
    owner=C.encoded(dict(run=ctx['run'],pid=os.getpid(),token=uuid.uuid4().hex))
    with fs.parent(RUN_LOCK) as (fd,name):
        try:os.mkdir(name,0o700,dir_fd=fd)
        except FileExistsError:
            yield False
            return
        os.fsync(fd); inode=os.stat(name,dir_fd=fd,follow_symlinks=False).st_ino
    try:
        fs.write(RUN_LOCK+'/owner.json',owner,None)
        def owned():
            with fs.parent(RUN_LOCK) as (fd,name):
                st=os.stat(name,dir_fd=fd,follow_symlinks=False)
                C.require(stat.S_ISDIR(st.st_mode) and st.st_ino==inode and
                    fs.read(RUN_LOCK+'/owner.json')==owner,'daily_run_owner_changed')
        ctx['owns_run']=owned
        yield owned
    finally:
        with fs.parent(RUN_LOCK) as (fd,name):
            try:
                st=os.stat(name,dir_fd=fd,follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode) and st.st_ino==inode and fs.read(RUN_LOCK+'/owner.json',True)==owner:
                    with fs.parent(RUN_LOCK+'/owner.json') as (ofd,oname):
                        os.unlink(oname,dir_fd=ofd);os.fsync(ofd)
                    os.rmdir(name,dir_fd=fd);os.fsync(fd)
            except (FileNotFoundError,NotADirectoryError):pass


def reserve(ctx, item, attempt):
    C.require(type(attempt) is int and attempt in (1,2),'attempt_limit')
    ctx['guard']();ctx['owns_run']()
    fs=ctx['fs'];vid=item['version_id']
    C.require(re.fullmatch(r'[0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*',vid) is not None,'version_id')
    prefix=f'{ctx["run"]}/items/{vid}/attempt{attempt}'
    C.ensure_dirs(fs,str(Path(prefix).parent))
    C.require(fs.read(prefix+'-reservation.json',True) is None,'attempt_exists')
    if attempt==2:
        previous=C.decode(fs.read(f'{ctx["run"]}/items/{vid}/attempt1-outcome.json'))
        C.require(previous.get('status')=='retryable_failed','retry_not_authorized')
    P=C.helper('publish')
    with P.collection_lock(fs,Path(ctx['run']).name,'reserve-'+vid,ctx['now']) as owned:
        if not owned:return None
        owned();ctx['guard']();ctx['owns_run']()
        P.reject_other_unresolved(fs,'')
        before=fs.read(C.STATE);state=C.decode(before)
        matched=[i for i in state['items'] if i['version_id']==vid]
        current=matched[0] if matched else copy.deepcopy(item)
        C.require(all(current[k]==item[k] for k in SOURCE_FIELDS),'reservation_source_drift')
        C.require(current['status'] in ('blocked_approval','queued','partial','retryable_failed') and
            current['human_review'] is None and not current['output_refs'] and current['receipt_ref'] is None,'item_not_reservable')
        snaps=dict(ctx['snapshots'],**{item['source_path']:item['source_sha256'],item['metadata_path']:item['metadata_sha256']})
        P.check_snapshots(fs,snaps)
        record=dict(schema='pkm-p3-reservation/v1',status='unknown',run=ctx['run'],version_id=vid,
            attempt=attempt,approval_sha256=ctx['approval_sha256'],snapshots=snaps,before_state_sha256=C.sha(before))
        fs.write(prefix+'-reservation.json',C.encoded(record),None)
        current.update(status='reading',reason='durable P3 reservation',requested_scope=C.SCOPE,resume_at=prefix)
        if not matched:state['items'].append(current)
        P.schema_validate(ctx['schema'],state,'compilation')
        owned();fs.write(C.STATE,C.encoded(state),before)
    return active_context(ctx,current,prefix,snaps)


def active_context(ctx,item,prefix,snaps):
    fs=ctx['fs'];P=C.helper('publish');vid=item['version_id']
    prepared=dict(ctx,item=copy.deepcopy(item),metadata=C.decode(fs.read(item['metadata_path'])),
        snapshots=snaps,artifact_prefix=prefix)
    def guard():
        ctx['guard']();ctx['owns_run']();P.check_snapshots(fs,prepared['snapshots'])
        current_state=C.decode(fs.read(C.STATE))
        observed=[i for i in current_state['items'] if i['version_id']==vid]
        C.require(len(observed)==1 and all(observed[0][k]==item[k] for k in SOURCE_FIELDS),'active_item_drift')
        active=observed[0]
        C.require(active['human_review'] is None and
            ((active['status'] in ('reading','ready_to_publish') and active['resume_at']==prefix) or
             (active['status']=='published_draft' and active['receipt_ref']==prefix+'-receipt.json')), 'active_item_owner')
    prepared['guard']=guard
    return prepared


def recover_publication(*,root=C.ROOT,run,approval_ref,version_id,attempt,
                        synthetic=False,now=None,scheduler_observer=None):
    """Explicit same-attempt recovery, never regenerates or steals a lock."""
    C.require(type(attempt) is int and attempt in (1,2) and
        re.fullmatch(r'[0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*',version_id) is not None,'recovery_identity')
    ctx=preflight(root=root,run=run,approval_ref=approval_ref,synthetic=synthetic,now=now,scheduler_observer=scheduler_observer)
    ctx['deadline']=time.monotonic()+ctx['auto']['limits']['soft_run_minutes']*60
    fs=ctx['fs'];P=C.helper('publish');prefix=f'{run}/items/{version_id}/attempt{attempt}'
    with run_lock(ctx) as owned:
        if not owned:return dict(status='skipped_busy')
        record=C.decode(fs.read(prefix+'-reservation.json'))
        C.require(record.get('schema')=='pkm-p3-reservation/v1' and record.get('run')==run and
            record.get('version_id')==version_id and record.get('attempt')==attempt and
            record.get('approval_sha256')==ctx['approval_sha256'],'recovery_reservation')
        C.require(fs.read(prefix+'-outcome.json',True) is None,'terminal_attempt_not_recoverable')
        candidates=[i for i in ctx['state']['items'] if i['version_id']==version_id]
        C.require(len(candidates)==1,'recovery_item')
        bundle: dict[str,Any]=dict(status='ready_to_publish',artifacts={})
        for name in ('result','report','review'):
            path=prefix+'-'+name+'.json';raw=fs.read(path)
            bundle[name]=C.decode(raw)
            bundle['artifacts'][name]=dict(path=path,sha256=C.sha(raw))
        for ref in bundle['result']['consumed_wiki']:
            C.require(re.fullmatch(r'(entities|concepts|comparisons|queries)/[A-Za-z0-9_.-]+\.md',ref['path']) is not None,'recovery_wiki_path')
            raw=fs.read(ref['path'])
            C.require(C.sha(raw)==ref['sha256'],'recovery_wiki_drift')
            ctx['wiki'].append(dict(**ref,text=raw.decode()))
        expected=dict(ctx['snapshots'],**{w['path']:w['sha256'] for w in ctx['wiki']},
            **{candidates[0]['source_path']:candidates[0]['source_sha256'],candidates[0]['metadata_path']:candidates[0]['metadata_sha256']})
        C.require(record['snapshots']==expected,'recovery_snapshot_set')
        P.check_snapshots(fs,expected)
        prepared=active_context(ctx,candidates[0],prefix,expected)
        from publication import publish
        return publish(prepared,bundle,now=now)


def record_outcome(ctx, bundle):
    """Immutable attempt outcome before state update; unknown is never retryable."""
    status=bundle['status']
    states={'retryable_failed':'retryable_failed','partial':'partial','blocked_policy':'blocked_policy',
            'blocked_review':'blocked_conflict','unknown':'blocked_conflict'}
    C.require(status in states,'unsupported_attempt_outcome')
    ctx['guard']();fs=ctx['fs'];P=C.helper('publish')
    path=ctx['artifact_prefix']+'-outcome.json'
    evidence: dict[str,Any]=dict(schema='pkm-p3-outcome/v1',status=status,version_id=ctx['item']['version_id'],
        approval_sha256=ctx['approval_sha256'],artifacts=bundle.get('artifacts',{}),
        error=bundle.get('error'),observed_at=ctx['now'].isoformat())
    update: dict[str,Any]=dict(status=states[status],reason='P3 '+status+'; see '+path)
    doc=bundle.get('report',{}).get('document') or {}
    if status=='partial':
        update.update(read_scope=doc.get('read_scope',[]),unread_scope=doc.get('unread_scope',[]),
            resume_at=doc.get('resume_at') or (doc.get('unread_scope') or [ctx['artifact_prefix']])[0])
        telemetry=bundle.get('result',{}).get('telemetry')
        if telemetry is not None:
            unread=telemetry.get('unread_pages') or []
            update.update(read_scope=telemetry['read_scope'],unread_scope=telemetry['required_unread_scope'],
                resume_at=f'page={unread[0]}' if unread else ctx['artifact_prefix'])
    cost=bundle.get('result',{}).get('cost_usd')
    evidence.update(update=update,reservation_sha256=C.sha(fs.read(ctx['artifact_prefix']+'-reservation.json')),
        cost_event=dict(event_id='attempt-'+C.sha(path.encode()),run_id=Path(ctx['run']).name,
            role='daily_compile',scope_id=ctx['item']['version_id'],created_at=ctx['now'].isoformat(),
            kst_day=ctx['now'].astimezone(timezone(timedelta(hours=9))).date().isoformat(),
            status='unknown' if cost is None else 'settled',reserved_usd=None,charged_usd=cost,
            usage_receipt=bundle.get('artifacts',{}).get('result',{}).get('path')))
    # The daily lock owns this immutable run artifact. Collection contention
    # must not discard an already observed terminal model outcome.
    C.require(fs.read(path,True) is None,'outcome_exists')
    fs.write(path,C.encoded(evidence),None)
    return apply_outcome(ctx,ctx['item'],ctx['artifact_prefix'])


def apply_outcome(ctx,item,prefix):
    """Reconcile one durable terminal outcome without any model interaction."""
    fs=ctx['fs'];P=C.helper('publish');ctx['guard']();ctx['owns_run']()
    match=re.fullmatch(r'(_meta/runs/wiki/[A-Za-z0-9_-]+)/items/([0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*)/attempt([12])',prefix)
    C.require(match is not None and match[2]==item['version_id'],'outcome_prefix')
    if match is None:raise ValueError('outcome_prefix')
    run=match[1];path=prefix+'-outcome.json';raw=fs.read(path);record=C.decode(raw)
    reservation_raw=fs.read(prefix+'-reservation.json');reservation=C.decode(reservation_raw)
    C.require(record.get('schema')=='pkm-p3-outcome/v1' and record['version_id']==item['version_id'] and
        record['approval_sha256']==ctx['approval_sha256'] and record['reservation_sha256']==C.sha(reservation_raw),'outcome_binding')
    C.require(reservation.get('schema')=='pkm-p3-reservation/v1' and reservation['run']==run and
        reservation['attempt']==int(match[3]) and reservation['version_id']==item['version_id'] and
        reservation['approval_sha256']==ctx['approval_sha256'],'outcome_reservation')
    snaps=reservation['snapshots']
    C.require(all(snaps.get(p)==h for p,h in ctx['snapshots'].items()) and
        snaps.get(item['source_path'])==item['source_sha256'] and
        snaps.get(item['metadata_path'])==item['metadata_sha256'],'outcome_snapshot_binding')
    P.check_snapshots(fs,snaps)
    states={'retryable_failed':'retryable_failed','partial':'partial','blocked_policy':'blocked_policy',
            'blocked_review':'blocked_conflict','unknown':'blocked_conflict'}
    status=record['status'];update=record['update'];event=record['cost_event']
    C.require(status in states and set(update)==({'status','reason','read_scope','unread_scope','resume_at'} if status=='partial' else {'status','reason'}) and
        update['status']==states[status] and update['reason']=='P3 '+status+'; see '+path,'outcome_transition')
    C.require(event['event_id']=='attempt-'+C.sha(path.encode()) and event['run_id']==Path(run).name and
        event['scope_id']==item['version_id'] and event['role']=='daily_compile','outcome_cost_binding')
    for name,ref in record['artifacts'].items():
        C.require(name in ('result','report','review') and ref['path']==prefix+'-'+name+'.json' and
            C.sha(fs.read(ref['path']))==ref['sha256'],'outcome_artifact_drift')
    with P.collection_lock(fs,Path(run).name,'outcome',ctx['now']) as owned:
        if not owned:return None
        owned();ctx['guard']();ctx['owns_run']();P.check_snapshots(fs,snaps)
        P.reject_other_unresolved(fs,'')
        before=fs.read(C.STATE);state=C.decode(before)
        current=next(i for i in state['items'] if i['version_id']==item['version_id'])
        C.require(current['status']=='reading' and current['resume_at']==prefix and current['human_review'] is None and
            all(current[k]==item[k] for k in SOURCE_FIELDS),'outcome_owner')
        C.require(not any(e['event_id']==event['event_id'] for e in state['cost_events']),'outcome_already_applied')
        current.update(update)
        if status=='retryable_failed':
            current['failure_count']+=1
            if current['failure_count']>=3:
                state.update(safety_block=True,safety_block_reason='three consecutive business failures: '+item['version_id'])
        state['cost_events'].append(event);state['last_run']=run
        P.schema_validate(ctx['schema'],state,'compilation')
        owned();C.require(fs.read(path)==raw and fs.read(prefix+'-reservation.json')==reservation_raw,'outcome_evidence_drift')
        fs.write(C.STATE,C.encoded(state),before)
        return state


def reconcile_pending(ctx):
    state=C.decode(ctx['fs'].read(C.STATE));count=0
    for item in state['items']:
        if item['status']!='reading':continue
        prefix=item['resume_at']
        if ctx['fs'].read(prefix+'-outcome.json',True) is None:continue
        state=apply_outcome(ctx,item,prefix)
        if state is None:return dict(status='skipped_busy',reconciled=count)
        count+=1
        if state['safety_block']:break
    return dict(status='reconciled' if count else 'noop',reconciled=count)


def reconcile_outcomes(*,root=C.ROOT,run,approval_ref,synthetic=False,now=None,scheduler_observer=None):
    ctx=preflight(root=root,run=run,approval_ref=approval_ref,synthetic=synthetic,now=now,scheduler_observer=scheduler_observer)
    ctx['deadline']=time.monotonic()+ctx['auto']['limits']['soft_run_minutes']*60
    with run_lock(ctx) as owned:
        if not owned:return dict(status='skipped_busy',reconciled=0)
        return reconcile_pending(ctx)


def run_daily(*, root=C.ROOT,run,approval_ref,synthetic=False,now=None,processor=None,
              client_factory=None,pdf_module=None,clock=time.monotonic,scheduler_observer=None):
    C.require(synthetic is True or (processor is None and client_factory is None and pdf_module is None), 'test_injection_forbidden')
    ctx=preflight(root=root,run=run,approval_ref=approval_ref,synthetic=synthetic,now=now,scheduler_observer=scheduler_observer)
    deadline=clock()+ctx['auto']['limits']['soft_run_minutes']*60
    ctx['deadline']=deadline;ctx['clock']=clock
    report: dict[str,Any]=dict(schema='pkm-p3-daily-report/v1',run=run,synthetic=synthetic,status='blocked_approval',
        inventory_count=0,selected=[],outcomes=[],live_automation_changed=False)
    with run_lock(ctx) as owned:
        if not owned:
            return dict(report,status='skipped_busy',reason='daily-run lock exists')
        C.ensure_dirs(ctx['fs'],run)
        report_path=run+'/daily-report.json'
        C.require(ctx['fs'].read(report_path,True) is None,'completed_run_use_fresh_id')
        C.check_deadline(deadline,clock)
        reconciled=reconcile_pending(ctx)
        if reconciled['status']=='skipped_busy':return dict(report,**reconciled)
        items=inventory(ctx)
        C.require(not any(i['status'] in ('reading','ready_to_publish') for i in items),'unresolved_reading')
        reject_dangling_reservations(ctx,items)
        ctx['wiki']=published_context(ctx,items)
        ctx['snapshots'].update({w['path']:w['sha256'] for w in ctx['wiki']})
        selected=select(items,ctx['auto']['limits']['daily_papers_per_run'])
        report.update(inventory_count=len(items),selected=[i['version_id'] for i in selected])
        if not selected and all(i['status']=='published_draft' for i in items):
            report['status']='noop'
        if selected and processor is None:
            from content import process
            processor=process
        stop=False
        for item in selected:
            for attempt in (1,2):
                if clock()>=deadline:
                    report['status']='partial'
                    break
                prepared=reserve(ctx,item,attempt)
                if prepared is None:
                    report['outcomes'].append(dict(version_id=item['version_id'],attempt=attempt,status='skipped_busy',stage='reservation'))
                    stop=True
                    break
                try:
                    assert processor is not None
                    bundle=processor(prepared,client_factory=client_factory,pdf_module=pdf_module,deadline=deadline,clock=clock)
                except (Exception,KeyboardInterrupt) as exc:
                    bundle=dict(status='unknown',error=C.helper('compile').safe_error(exc))
                if bundle['status']=='ready_to_publish':
                    from publication import publish
                    publication=publish(prepared,bundle,now=now)
                    report['outcomes'].append(dict(version_id=item['version_id'],attempt=attempt,**publication))
                    report['status']='committed' if publication['status'] in ('published_draft','noop') else publication['status']
                    break
                state=record_outcome(prepared,bundle)
                report['outcomes'].append(dict(version_id=item['version_id'],attempt=attempt,status=bundle['status']))
                report['status']=bundle['status']
                if state is None:
                    report['state_reconciliation']='pending';stop=True
                    break
                if bundle['status']!='retryable_failed' or state['safety_block']:
                    break
            if stop or C.decode(ctx['fs'].read(C.STATE))['safety_block'] or clock()>=deadline:
                break
        latest={entry['version_id']:entry['status'] for entry in report['outcomes']}
        for status in ('unknown','blocked_policy','blocked_review','retryable_failed','partial','skipped_busy'):
            if status in latest.values():
                report['status']=status
                break
        else:
            if len(latest)<len(selected):report['status']='partial'
        ctx['fs'].write(report_path,C.encoded(report),None)
    return report


def main(argv=None):
    """Fixed-root CLI: no test injection, implicit grant or scheduler changes."""
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True)
    parser.add_argument('--approval-ref',required=True)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--check',action='store_true')
    mode.add_argument('--reconcile-outcomes',action='store_true')
    mode.add_argument('--recover-version')
    parser.add_argument('--attempt',type=int,choices=(1,2))
    args=parser.parse_args(argv)
    if bool(args.recover_version)!=(args.attempt is not None):
        parser.error('--recover-version and --attempt are required together')
    try:
        kwargs=dict(run=args.run,approval_ref=args.approval_ref)
        if args.check:
            ctx=preflight(**kwargs)
            result=dict(status='preflight_passed',run=args.run,body_read=False,model_called=False,
                approval_sha256=ctx['approval_sha256'])
        elif args.recover_version:
            result=recover_publication(**kwargs,version_id=args.recover_version,attempt=args.attempt)
        elif args.reconcile_outcomes:
            result=reconcile_outcomes(**kwargs)
        else:
            result=run_daily(**kwargs)
        code=0 if result['status'] in ('preflight_passed','committed','noop','published_draft','skipped_busy','reconciled') else 2
    except (Exception,KeyboardInterrupt) as exc:
        error=C.helper('compile').safe_error(exc)
        error['message']='p3_execution_not_authorized' if type(exc) is ValueError and exc.args==('p3_execution_not_authorized',) else None
        result=dict(status='blocked',error=error,run=args.run);code=2
    print(C.encoded(result).decode(),end='')
    return code


if __name__=='__main__':
    raise SystemExit(main())
