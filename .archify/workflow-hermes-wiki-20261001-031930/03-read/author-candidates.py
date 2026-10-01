from pathlib import Path
import hashlib
import json

ROOT = Path('/home/ainsdev/wiki/pkm-articles')
BASE = Path('.archify/workflow-hermes-wiki-20261001-031930')
DOC = Path('docs/techblog/hermes-api-gateway-workdir-assoc')


def ref(name, line, end_line, classification='제안'):
    return {'path': (DOC / name).as_posix(), 'line': line, 'end_line': end_line, 'classification': classification}


def emit(folder, title, lanes, node_specs, edge_specs, cards):
    target = ROOT / BASE / folder
    target.mkdir(parents=True, exist_ok=True)
    nodes, edges, entries = [], [], []
    for spec in node_specs:
        ident, lane, col, kind, label, sublabel, tag, refs = spec
        node = {'id': ident, 'lane': lane, 'col': col, 'type': kind, 'label': label, 'sublabel': sublabel, 'tag': tag, 'width': 236, 'height': 82}
        nodes.append(node)
        entries.append({'element_type': 'node', 'element_id': ident, 'claim': ' / '.join([label, sublabel, tag]), 'references': refs})
    for spec in edge_specs:
        ident, source, dest, label, variant, role, refs = spec
        edge = {'id': ident, 'from': source, 'to': dest, 'variant': variant, 'role': role}
        if label:
            edge['label'] = label
        edges.append(edge)
        entries.append({'element_type': 'edge', 'element_id': ident, 'claim': f'{source} → {dest}: {label or "인접 단계의 의미대로 진행"}', 'references': refs})
    common_cards = [
        {'dot': 'amber', 'title': '문서 설명 · 구현 완료 아님', 'items': [
            'BFF·UI·read facade·실행 격리는 제안/미구현이다. Gateway·모델·논문·Cron은 실행하거나 변경하지 않았다.',
            '관측은 기술문서에 기록된 로컬 정적 조사, 공식계약은 기술문서가 인용한 API 계약이다. 이 그림의 live 검증이 아니다.',
            '한국어 authored content. 고정 Viewer UI와 html lang은 English fallback이다. 정지형이며 motion을 요청하지 않았다.'
        ]},
        {'dot': 'slate', 'title': '근거 경로와 분류', 'items': [
            '아래 파일명은 docs/techblog/hermes-api-gateway-workdir-assoc/ 기준이다. 각 node/edge의 정확한 line/end_line·분류는 같은 폴더 evidence.json에 있다.',
            '분류: 관측 / 공식계약 / 제안 / 미확인. untracked 설계문서이므로 meta.repository·HEAD·--repo-root 근거를 만들지 않는다.',
            'architecture.md:3–4, 37 · evidence.md:15, 65–80, 93–97 · frontend-design.md:3–4, 109–113'
        ]}
    ]
    # Evidence-based reflow: compiler-owned stacks retain semantic text.
    if folder == '03-read':
        lanes = [
            {'id':'request','label':'브라우저 → BFF · 인증 gate [제안]'},
            {'id':'path','label':'Read facade · 허용 파일 gate [제안]'},
            {'id':'read','label':'Read facade · 읽기·일관성·공개 projection [제안]'},
            {'id':'display','label':'브라우저 · 출처·검토·미독 상태 표시 [제안]'}
        ]
        placement = {
            'open_page':('request',0,0), 'authorize':('request',1,0), 'denied':('request',2,0),
            'resolve':('path',1,0), 'unsafe':('path',2,0),
            'read_files':('read',1,-110), 'snapshot':('read',1,0), 'dto':('read',1,110),
            'retry':('read',0,0), 'conflict':('read',2,0), 'updating':('read',2,110),
            'render':('display',1,0)
        }
    else:
        lanes = [
            {'id':'intake','label':'브라우저 → BFF · 인증·실행 gate [제안]'},
            {'id':'binding','label':'BFF → Hermes · 서버 문맥·Runs 요청 [제안·계약]'},
            {'id':'accepted','label':'Hermes/BFF · key 검사와 202 접수 [관측·제안]'},
            {'id':'relay','label':'BFF · 단일 구독·SSE parser·fan-out [제안·관측]'},
            {'id':'active','label':'UI · 실행·단절·중지 의사 [제안]'},
            {'id':'recovery','label':'BFF/Hermes · 재조정·중지 접수 [제안·관측]'},
            {'id':'terminal','label':'Hermes → UI · 종료와 실제 근거 [계약·제안]'}
        ]
        placement = {
            'question':('intake',0,0), 'owner':('intake',1,0), 'policy':('intake',2,0),
            'binding':('binding',1,-60), 'post':('binding',1,60), 'blocked':('binding',2,-60),
            'idempotency':('accepted',1,-60), 'accepted':('accepted',1,60),
            'replayed':('accepted',0,60), 'body_conflict':('accepted',2,-60),
            'upstream':('relay',1,-60), 'relay':('relay',1,60),
            'active':('active',1,0), 'disconnected':('active',0,0), 'stop':('active',2,0),
            'reconcile':('recovery',0,0), 'stopping':('recovery',2,0),
            'terminal':('terminal',1,-60), 'answer':('terminal',1,60)
        }
        for edge in edges:
            if edge['id'] == 'recovered_terminal':
                edge.update({'fromSide':'bottom','toSide':'left'})
    for node in nodes:
        node['lane'], node['col'], node['yOffset'] = placement[node['id']]
        if folder == '04-query':
            node['width'] = 224
    candidate = {'schema_version': 2, 'diagram_type': 'workflow', 'meta': {'title': title, 'locale': 'en', 'quality_profile': 'showcase', 'output': (BASE / folder / 'diagram.html').as_posix()}, 'lanes': lanes, 'nodes': nodes, 'edges': edges, 'cards': common_cards + cards}
    candidate_bytes = (json.dumps(candidate, ensure_ascii=False, indent=2) + '\n').encode()
    (target / 'candidate.json').write_bytes(candidate_bytes)
    source_paths = sorted({r['path'] for e in entries for r in e['references']})
    manifest = []
    for relative in source_paths:
        data = (ROOT / relative).read_bytes()
        count = len(data.decode().splitlines())
        for e in entries:
            for r in e['references']:
                if r['path'] == relative:
                    assert 1 <= r['line'] <= r['end_line'] <= count, r
        manifest.append({'path': relative, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'lines': count})
    assert len({n['id'] for n in nodes}) == len(nodes)
    assert len({e['id'] for e in edges}) == len(edges)
    assert all(e['from'] in {n['id'] for n in nodes} and e['to'] in {n['id'] for n in nodes} for e in edges)
    evidence = {
        'schema': 'archify-document-evidence/v1', 'mode': 'document-description',
        'diagram_type': 'workflow', 'language': {'authored': 'ko', 'viewer_fallback': 'en', 'html_lang_fallback': 'en'},
        'candidate': (BASE / folder / 'candidate.json').as_posix(),
        'candidate_sha256': hashlib.sha256(candidate_bytes).hexdigest(),
        'source_root': '.', 'document_base': DOC.as_posix(), 'repository_claim': None,
        'scope': '읽은 설계문서만 재구성. BFF/UI/격리 미구현. live API 또는 모델 검증을 뜻하지 않는다.',
        'classification_definitions': {'관측': '기술문서가 보고한 정적 소스/파일 관측; 본 작업의 live 관측 아님', '공식계약': '기술문서가 명시한 공식 API 또는 정식 Wiki 계약', '제안': '아직 구현·배포·검증하지 않은 BFF/UI/격리 설계', '미확인': '실행/호환성/배포 미검증 또는 보장하지 않는 속성'},
        'coverage': {'nodes': len(nodes), 'edges': len(edges), 'mapped_nodes': len(nodes), 'mapped_edges': len(edges), 'unmapped': []},
        'entries': entries, 'source_manifest': manifest,
        'verification_limits': ['문서 line 범위·SHA-256·node/edge 전수 매핑 검사', 'Archify finalize receipt는 별도 생성', '실제 서비스 구현·Gateway/모델/논문/Cron 실행 없음', 'perceptual visual review 미요청']
    }
    (target / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(folder, len(nodes), 'nodes', len(edges), 'edges', len(entries), 'mapped entries')


emit('03-read', '03 · 모델 없는 Wiki 읽기와 snapshot 충돌', [
    {'id': 'request', 'label': '브라우저 · 탐색 요청 [제안]'},
    {'id': 'access', 'label': 'BFF · 인증과 객체 권한 [제안]'},
    {'id': 'path', 'label': 'Read facade · 허용 경로 [제안]'},
    {'id': 'read', 'label': 'Wiki 파일 · 최소 읽기 [제안]'},
    {'id': 'consistency', 'label': 'Read facade · 일관성 gate [제안]'},
    {'id': 'projection', 'label': 'BFF · 공개 projection [제안]'},
    {'id': 'display', 'label': '브라우저 · 안전한 표시 [제안]'}
], [
    ('open_page','request',1,'frontend','목록·지식 페이지 열기','page_id 조회 · 모델 호출 없음','탐색이 모델 답변을 기다리지 않음',[ref('workflows.md',6,23),ref('architecture.md',41,48)]),
    ('authorize','access',1,'security','사용자 인증·page ACL','개인 Wiki 접근 권한 확인','page_id는 서버 소유 식별자',[ref('workflows.md',14,20),ref('data-contracts.md',100,111)]),
    ('denied','access',2,'security','읽기 요청 거부','인증 만료·권한 없음 구분','본문·내부 경로를 공개하지 않음',[ref('frontend-design.md',39,45),ref('security-and-operations.md',23,35)]),
    ('resolve','path',1,'security','page_id → 허용 파일','승인된 지식 Markdown 매핑','no-follow·안전한 open·root 검증',[ref('data-contracts.md',106,115),ref('security-and-operations.md',14,18)]),
    ('unsafe','path',2,'security','위험 경로 거부','NUL·절대경로·..·symlink 차단','realpath만으로 TOCTOU 해결 아님',[ref('data-contracts.md',108,111)]),
    ('read_files','read',1,'database','허용 자료만 읽기','지식 Markdown · 서지 JSON','PDF 해석·HTML 분석·모델 없음',[ref('data-contracts.md',26,36),ref('architecture.md',41,48)]),
    ('snapshot','consistency',1,'security','일관된 snapshot인가?','committed receipt·revision·hash','읽기 전후 상태 ID도 불변 확인',[ref('data-contracts.md',117,127),ref('architecture.md',89,91)]),
    ('retry','consistency',0,'messagebus','제한된 재시도','충돌 · 남은 횟수가 있을 때만','일부 파일로 완료 승격 금지',[ref('data-contracts.md',119,125),ref('workflows.md',23,23)]),
    ('conflict','consistency',2,'security','snapshot_conflict','재시도로도 일관성 미확정','partial 데이터를 캐시하지 않음',[ref('data-contracts.md',119,127),ref('security-and-operations.md',91,95)]),
    ('dto','projection',1,'backend','최소 공개 DTO + ETag','성공 snapshot만 · ETag=page hash','본문·출처·revision·검토·미독 범위',[ref('data-contracts.md',69,104),ref('data-contracts.md',119,127)]),
    ('updating','projection',2,'frontend','갱신 중 · 다시 시도','충돌은 빈 페이지·없음과 다름','새로운 완료본으로 표시하지 않음',[ref('workflows.md',23,23),ref('architecture.md',89,91),ref('frontend-design.md',39,45)]),
    ('render','display',1,'frontend','안전한 Markdown 표시','raw HTML 비활성 · URL 제한','출처·미검토 범위·상태 축을 분리',[ref('frontend-design.md',29,35),ref('data-contracts.md',54,67),ref('security-and-operations.md',52,59)])
], [
    ('request_auth','open_page','authorize','인증된 조회','default','main',[ref('workflows.md',14,16)]),
    ('deny_acl','authorize','denied','불허','security','error',[ref('security-and-operations.md',23,35),ref('frontend-design.md',39,45)]),
    ('allow_map','authorize','resolve','권한 확인','emphasis','main',[ref('data-contracts.md',100,111)]),
    ('deny_path','resolve','unsafe','검증 실패','security','error',[ref('data-contracts.md',108,111)]),
    ('safe_read','resolve','read_files','허용 파일만','emphasis','main',[ref('data-contracts.md',108,111),ref('data-contracts.md',26,36)]),
    ('check_snapshot','read_files','snapshot','상태·본문 대조','default','main',[ref('workflows.md',17,18),ref('data-contracts.md',121,123)]),
    ('bounded_retry','snapshot','retry','충돌·잔여 시도','dashed','branch',[ref('data-contracts.md',123,124)]),
    ('reread','retry','read_files','다시 읽기','dashed','return',[ref('data-contracts.md',119,125)]),
    ('unresolved','snapshot','conflict','끝내 불일치','security','error',[ref('data-contracts.md',123,124)]),
    ('consistent','snapshot','dto','일치할 때만','emphasis','main',[ref('data-contracts.md',121,125)]),
    ('conflict_ui','conflict','updating','재시도 가능 안내','security','error',[ref('workflows.md',23,23),ref('architecture.md',91,91)]),
    ('render_success','dto','render','허용 필드만','emphasis','main',[ref('workflows.md',19,20),ref('frontend-design.md',29,35)])
], [
    {'dot':'cyan','title':'공개 projection과 상태 의미','items':[
        'DTO는 제안 pkm-web-page/v1·snapshot_id. 목록에는 markdown·claim detail·내부 evidence 경로를 생략한다. 서버 절대경로도 노출하지 않는다. [data-contracts.md:69–115]',
        'source.json의 wiki_compiled:false는 수집 당시 불변값이다. 완료는 compilation ledger·receipt·실물 output으로 확인한다. [data-contracts.md:28–36]',
        '원문 보관 ≠ 분석 완료 ≠ 게시 committed ≠ 인간 검토. draft/unreviewed·수집 대기·노트 미작성은 정상 경계 상태다. [data-contracts.md:54–67; workflows.md:23]'
    ]},
    {'dot':'emerald','title':'읽기·캐시·보안 근거','items':[
        'open_page → authorize → resolve → read_files: workflows.md:14–20; data-contracts.md:100–115. denied/unsafe는 권한·경로 거부이며 snapshot_conflict와 다르다.',
        'snapshot → retry / conflict / dto: data-contracts.md:119–127. 최신 committed receipt·revision·파일 hash·읽기 전후 상태 ID를 대조한다. 다중 파일의 OS 원자성을 주장하지 않는다.',
        'dto → render: page hash ETag는 성공 snapshot만. 초기 private/no-store도 가능하다. process-local cache는 원장이 아니다. [data-contracts.md:125–127]',
        '원본 HTML은 같은 origin에서 실행하지 않는다. 공식 버전 링크를 제공하고 실제 anchor 미확인은 표시한다. PDF preview용 추출·OCR·render를 추가하지 않는다. [security-and-operations.md:52–59; data-contracts.md:113–115]'
    ]}
])

emit('04-query', '04 · 통제된 질의 — Runs·SSE·재연결·중지', [
    {'id':'intake','label':'브라우저 → BFF · 제출과 정책 [제안]'},
    {'id':'binding','label':'BFF · 서버 소유 실행 문맥 [제안]'},
    {'id':'create','label':'Hermes Runs · 요청 계약 [공식계약·정적 관측]'},
    {'id':'idempotency','label':'Hermes Runs · 중복 방지 [정적 관측]'},
    {'id':'accepted','label':'BFF/UI · 접수와 실행을 구분 [제안]'},
    {'id':'subscribe','label':'BFF → Hermes · 단일 upstream [제안·정적 제약]'},
    {'id':'relay','label':'BFF → UI · parser와 자체 fan-out [제안]'},
    {'id':'active','label':'UI · 실행·단절·중지 의사 [제안]'},
    {'id':'recovery','label':'BFF/Hermes · 재조정과 중지 접수 [제안·관측]'},
    {'id':'terminal','label':'UI · 실제 종료 상태 확인 [제안]'},
    {'id':'answer','label':'UI · 근거 있는 답변, 게시와 분리 [제안]'}
], [
    ('question','intake',0,'frontend','질문·선택 pageId 제출','클라이언트 요청 ID 포함','임의 path·model·도구·prompt 금지',[ref('workflows.md',25,35),ref('api-contract.md',128,133)]),
    ('owner','intake',1,'security','인증·객체 소유권','대화·session·run마다 ACL','다른 사용자 run/key 재사용 차단',[ref('workflows.md',29,33),ref('workflows.md',68,72),ref('security-and-operations.md',31,35)]),
    ('policy','intake',2,'security','질의 실행 gate','별도 승인 + 실제 격리 검증','자료·모델·도구 서버 allowlist',[ref('workflows.md',27,32),ref('security-and-operations.md',37,50)]),
    ('binding','binding',1,'backend','서버 소유 문맥 고정','conversation → body session_id','세션 단일 writer · 허용 문서만',[ref('workflows.md',29,34),ref('architecture.md',89,89),ref('api-contract.md',62,74,'공식계약')]),
    ('blocked','binding',2,'security','승인 밖 작업 차단','신규 원문·PDF 분석·쓰기·게시','격리 미검증이면 실행하지 않음',[ref('workflows.md',27,35),ref('architecture.md',54,60),ref('security-and-operations.md',43,59)]),
    ('post','create',1,'backend','POST /v1/runs','input + body session_id','BFF 소유 Idempotency-Key',[ref('api-contract.md',62,82,'공식계약'),ref('workflows.md',68,72)]),
    ('idempotency','idempotency',1,'security','key·body 중복 검사','같은 body 재시도 / 다른 body','전송 재시도 ≠ 수정 질문 재생성',[ref('api-contract.md',109,113,'관측'),ref('workflows.md',66,72,'공식계약')]),
    ('body_conflict','idempotency',2,'security','409 · 다른 body','같은 key로 변경 요청 거부','수정 질의는 새 key + 명시 제출',[ref('api-contract.md',111,114,'관측'),ref('workflows.md',68,72,'공식계약')]),
    ('replayed','accepted',0,'messagebus','202 replay · 기존 run','동일 key + 동일 payload','재실행·SSE replay가 아님',[ref('api-contract.md',111,113,'관측')]),
    ('accepted','accepted',1,'messagebus','202 · started 접수','run_id 보관 · 성공 아님','queued/running 등 실제 상태 분리',[ref('api-contract.md',76,84,'공식계약'),ref('frontend-design.md',49,61)]),
    ('upstream','subscribe',1,'messagebus','GET run /events','BFF 단일 upstream 구독','단일 queue · 종료 시 transport 삭제',[ref('api-contract.md',25,28,'공식계약'),ref('api-contract.md',103,107,'관측'),ref('workflows.md',58,64)]),
    ('relay','relay',1,'backend','SSE 파싱·자체 fan-out','data JSON.event로 분기','허용된 최소 이벤트만 owner에게',[ref('api-contract.md',86,105,'관측'),ref('workflows.md',49,64),ref('security-and-operations.md',65,78)]),
    ('active','active',1,'frontend','실행 중 · 도구 승인 대기','delta는 임시 · final과 분리','도구 승인 ≠ Wiki 단계·게시 승인',[ref('frontend-design.md',49,69),ref('workflows.md',84,95)]),
    ('disconnected','active',0,'messagebus','단절·events 404','작업 실패·취소를 뜻하지 않음','Last-Event-ID 복구 보장 없음',[ref('api-contract.md',103,107,'관측'),ref('workflows.md',62,64)]),
    ('stop','active',2,'security','사용자가 중지 요청','owner + CSRF 재확인','POST run /stop · abort와 다름',[ref('api-contract.md',128,131),ref('workflows.md',74,82)]),
    ('reconcile','recovery',0,'backend','GET run 상태 재조정','현재·최종 snapshot으로 복구','진행 중이면 polling · 새 run 금지',[ref('workflows.md',52,64),ref('api-contract.md',105,105,'관측')]),
    ('stopping','recovery',2,'messagebus','stopping · 중지 접수','취소 확정 전에는 대기 표시','cancelled 또는 completed 경합',[ref('api-contract.md',116,116,'관측'),ref('workflows.md',76,82),ref('security-and-operations.md',91,93)]),
    ('terminal','terminal',1,'backend','실제 terminal 확인','completed/failed/cancelled','interrupted·partial·error도 확인',[ref('api-contract.md',82,84,'공식계약'),ref('api-contract.md',114,116,'관측'),ref('evidence.md',75,77,'미확인'),ref('frontend-design.md',53,61)]),
    ('answer','answer',1,'frontend','답변 + 실제 근거 표시','Wiki page·revision/hash·읽은 범위','답변 완료 ≠ Wiki 저장·게시 완료',[ref('workflows.md',34,35),ref('frontend-design.md',63,69),ref('architecture.md',56,60)])
], [
    ('submit','question','owner','인증된 제출','default','main',[ref('workflows.md',29,33)]),
    ('check_policy','owner','policy','owner 확인','security','main',[ref('workflows.md',27,32)]),
    ('reject_scope','policy','blocked','불허·미검증','security','error',[ref('workflows.md',27,32),ref('security-and-operations.md',43,50)]),
    ('bind_context','policy','binding','승인·검증 통과','emphasis','main',[ref('workflows.md',27,33),ref('architecture.md',89,89)]),
    ('create_run','binding','post','서버 결정값만','emphasis','main',[ref('api-contract.md',65,74,'공식계약'),ref('api-contract.md',133,133)]),
    ('dedupe','post','idempotency','key + payload','default','main',[ref('api-contract.md',111,113,'관측')]),
    ('different_body','idempotency','body_conflict','동일 key·변경 body','security','error',[ref('api-contract.md',111,111,'관측')]),
    ('same_body','idempotency','replayed','동일 key·body','dashed','branch',[ref('api-contract.md',111,112,'관측')]),
    ('new_run','idempotency','accepted','신규 key','emphasis','main',[ref('workflows.md',46,48,'공식계약'),ref('workflows.md',68,72,'공식계약')]),
    ('reuse_id','replayed','accepted','기존 run_id','dashed','return',[ref('api-contract.md',111,112,'관측')]),
    ('subscribe_once','accepted','upstream','구독 소유권 관리','emphasis','main',[ref('workflows.md',49,64),ref('api-contract.md',105,105)]),
    ('relay_events','upstream','relay','단일 소비','default','async',[ref('api-contract.md',103,105,'관측')]),
    ('display_events','relay','active','분리된 진행 표시','emphasis','async',[ref('workflows.md',58,61),ref('frontend-design.md',63,69)]),
    ('network_lost','active','disconnected','전송 단절','dashed','branch',[ref('workflows.md',62,64),ref('frontend-design.md',53,61)]),
    ('events_unavailable','upstream','disconnected','404·연결 종료','dashed','error',[ref('api-contract.md',105,105,'관측')]),
    ('recover_snapshot','disconnected','reconcile','기존 run 조회','emphasis','main',[ref('workflows.md',52,64)]),
    ('still_running','reconcile','active','진행 중·polling','dashed','return',[ref('workflows.md',62,64),ref('frontend-design.md',57,61)]),
    ('recovered_terminal','reconcile','terminal','최종 상태','emphasis','branch',[ref('workflows.md',53,58),ref('api-contract.md',82,82,'공식계약')]),
    ('ask_stop','active','stop','명시적 중지','security','branch',[ref('workflows.md',76,82)]),
    ('stop_accepted','stop','stopping','stopping 응답','security','async',[ref('api-contract.md',116,116,'관측'),ref('workflows.md',76,79)]),
    ('stop_race','stopping','terminal','종료·완료 경합 확인','security','async',[ref('api-contract.md',116,116,'관측'),ref('workflows.md',78,82)]),
    ('terminal_event','active','terminal','실제 종료 이벤트','emphasis','async',[ref('api-contract.md',82,92,'공식계약'),ref('frontend-design.md',53,61)]),
    ('final_result','terminal','answer','상태·결과 분리','emphasis','main',[ref('workflows.md',34,35),ref('workflows.md',58,59),ref('evidence.md',75,76,'미확인')])
], [
    {'dot':'cyan','title':'Runs 입력·재시도·모델 계약','items':[
        'Runs는 input + body session_id다. Chat의 messages/stream 또는 X-Hermes-Session-Id와 혼동하지 않는다. [api-contract.md:50–65, 69–84]',
        'BFF가 (인증 주체, 대화, client request ID) → key/run을 관리한다. 429/timeout이면 생성 성공 여부를 먼저 확인한다. 같은 key·body만 기존 run 202 replay, 다른 body는 409. [workflows.md:68–72; api-contract.md:111–114]',
        'key visible ASCII 1–255, profile/credential scope·session-key fingerprint. terminal 기본 24h·DB 실패 memory fallback 가능. Chat/Responses 300초 캐시와 별개다. [api-contract.md:111–113; evidence.md:74]',
        'model alias echo는 실제 실행 모델 증거가 아니다. model/provider 지정만으로 no-fallback을 보장하지 않으므로 별도 runtime 집행·검증 필요. [api-contract.md:58, 84; evidence.md:75–77]'
    ]},
    {'dot':'violet','title':'SSE 파서·단일 소비·재접속','items':[
        'Runs는 data JSON 내부 event 필드로 분기한다. blank line·comment/keepalive·CRLF·multi-line data·UTF-8/JSON/chunk 분할·unknown event를 처리한다. [api-contract.md:86–105]',
        '설치판은 queue 하나를 소비하며 연결 종료 시 transport 삭제. 복수 upstream은 이벤트를 나눠 가져갈 수 있다. BFF 한 구독과 자체 fan-out이 제안이다. [api-contract.md:105; evidence.md:56, 72]',
        'events 404·단절에도 run은 계속될 수 있다. GET /v1/runs/{id}로 먼저 조정, 이후 polling. Last-Event-ID/전체 replay를 가정하지 않고 새로고침에서 새 run을 만들지 않는다. [workflows.md:52–64]',
        'commentary/tool/delta/final을 분리한다. raw arguments/output·비공개 추론을 노출하지 않는다. 임시 delta는 최종 snapshot과 중복 제거한다. [frontend-design.md:63–69; security-and-operations.md:76–78]',
        '공식 keepalive 10초와 조사 설치판 30초 timeout이 다르다. reverse proxy의 buffering/idle timeout은 배포 버전에서 시험해야 한다. [api-contract.md:107; security-and-operations.md:65–72]'
    ]},
    {'dot':'rose','title':'중지·승인·완료의 별도 경계','items':[
        'POST /v1/runs/{id}/stop의 stopping은 접수다. 실제 cancelled 또는 completed 경합·failed를 확인한다. abort ≠ stop ≠ rollback이며 이미 실행된 파일/외부 효과는 되돌리지 않는다. [workflows.md:74–82; api-contract.md:116]',
        'interrupted는 성공이 아니고 자동 재실행 근거도 아니다. HTTP 200/completed만으로 업무 성공을 판정하지 않고 partial/interrupted/error flags를 확인한다. [api-contract.md:82, 114–116; evidence.md:75–76]',
        'Hermes tool approval은 Wiki 단계·자료·게시 승인이 아니다. 관리 UI는 실제 pending ID·선택지·만료·owner를 재확인하고 /approval로 전달한다. stale/always 자동 승인은 금지다. [workflows.md:84–95; api-contract.md:118]',
        '질의 최종 답변에는 실제 참조 page·revision/hash·읽은 범위만 표시한다. 없는 인용·실행 모델·Wiki 저장 성공을 UI가 만들어내지 않는다. [workflows.md:34–35; api-contract.md:58, 84]',
        'owner/policy/binding은 제안, Runs 상세는 공식계약과 문서의 정적 관측을 구분한다. 모든 node/edge별 원문 범위는 evidence.json에서 확인한다.'
    ]}
])
