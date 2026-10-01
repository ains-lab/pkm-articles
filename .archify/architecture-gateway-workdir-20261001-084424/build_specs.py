"""Author document-based diagrams, not an implementation snapshot."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DOC = ROOT / 'docs/techblog/hermes-api-gateway-workdir-assoc'
CATALOG = ROOT / '.archify/workflow-hermes-wiki-20261001-031930/07-data-ui/candidate.json'
translations = json.loads(CATALOG.read_text())['meta']['translations']
translations.update({'legend.architecture.database': 'Wiki 파일', 'viewer.kind.database': '파일 저장소', 'legend.workflow.database': '문서·상태 읽기'})


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def meta(title, folder):
    return {'title': title, 'locale': 'ko', 'translations': translations,
            'quality_profile': 'showcase',
            'output': str((OUT / folder / 'diagram.html').relative_to(ROOT))}


def node(id, type, label, sublabel, x, y, tag=None):
    n = dict(id=id, type=type, label=label, sublabel=sublabel, pos=[x, y], size=[220, 90])
    if tag:
        n['tag'] = tag
    return n


def step(id, lane, col, type, label, sublabel, tag=None):
    n = dict(id=id, lane=lane, col=col, type=type, label=label, sublabel=sublabel, width=220, height=76)
    if tag:
        n['tag'] = tag
    return n


def edge(id, source, target, label=None, variant='default', **kw):
    e = dict(id=id, to=target, variant=variant, **kw)
    e['from'] = source
    if label:
        e['label'] = label
    return e


architecture = {
    'schema_version': 1, 'diagram_type': 'architecture',
    'meta': meta('01 · 외부 앱과 Wiki는 이렇게 연결합니다 — 설계안', '01-connect'),
    'components': [
        node('app', 'frontend', '외부 앱 화면', '목록 보기 · 질문하기', 40, 80, '신규 UI / 기존 채팅 UI'),
        node('bff', 'security', '앱 서버 · BFF', '로그인 · pageId · run 소유권', 410, 80, '신규 구현 제안'),
        node('gateway', 'backend', 'Hermes API Gateway', 'HTTP / Runs / SSE', 800, 80, '기존 제품 기능'),
        node('agent', 'backend', '질의용 Agent · 도구', '허용 지식만 읽고 답변', 800, 360, '격리·쓰기 거부 검증 필요'),
        node('wiki', 'database', 'Wiki 문서 폴더', 'pkm-articles / 지식 Markdown', 410, 360, '기존 저장소 · 웹 루트 아님'),
        node('publisher', 'backend', '별도 자동 컴파일', '정책 · 잠금 · hash · receipt', 40, 360, '기존 승인 범위 유지'),
        node('cwd', 'security', '서버의 작업 경로 설정', 'terminal.cwd + mount / OS 권한', 800, 620, '설정은 서버에서 · 적용 전')
    ],
    'connections': [
        edge('app-request', 'app', 'bff', 'HTTPS', 'emphasis'),
        edge('api-request', 'bff', 'gateway', 'Bearer / API', 'emphasis'),
        edge('plain-read', 'bff', 'wiki', '허용 목록·본문 읽기'),
        edge('agent-execution', 'gateway', 'agent', '승인된 질의', 'emphasis'),
        edge('agent-read', 'agent', 'wiki', '허용 읽기', 'emphasis'),
        edge('cwd-binding', 'cwd', 'agent', '기준 경로', 'security'),
        edge('verified-publish', 'publisher', 'wiki', '검증 후 게시', 'dashed')
    ],
    'cards': [
        {'dot': 'cyan', 'title': '두 경로만 기억하세요', 'items': [
            '목록·본문 보기: 앱 → BFF → Wiki. 모델 호출은 없습니다.',
            '질문하기: 앱 → BFF → Hermes → 허용 Wiki. 결과는 BFF를 통해 앱으로 돌아옵니다.',
            'BFF는 앱 전용 중계 서버입니다. /api/wiki/*와 /api/agent/*는 신규 구현할 계약입니다.'
        ]},
        {'dot': 'amber', 'title': 'URL 연결과 폴더 연결은 다릅니다', 'items': [
            '같은 호스트·네트워크 namespace 예시: Gateway http://127.0.0.1:8642',
            '작업 루트: /home/ainsdev/wiki/pkm-articles — terminal.cwd로 서버에서 지정합니다.',
            '다른 서버·컨테이너: 사설 주소와 실제 mount 경로가 필요합니다. localhost와 호스트 경로를 그대로 복사하지 않습니다.'
        ]},
        {'dot': 'rose', 'title': '연동해도 자동으로 생기지 않는 권한', 'items': [
            '키는 앱 서버에만 보관합니다. 브라우저에 Gateway 키·임의 파일 경로·관리 API를 주지 않습니다.',
            'cwd·프로필·AGENTS.md는 sandbox가 아닙니다. 도구 전체의 실제 읽기·쓰기·외부 전송 경계를 검증해야 합니다.',
            '자동 컴파일은 별도 승인된 배치입니다. 웹 질의 완료는 Wiki 게시가 아니며, 웹 앱에 그 권한을 승계하지 않습니다.'
        ]}
    ]
}

setup = {
    'schema_version': 2, 'diagram_type': 'workflow',
    'meta': meta('02 · 작업 디렉터리를 연결하는 순서 — 승인 후 적용안', '02-workdir'),
    'lanes': [{'id': 'scope', 'label': '1 · 대상과 접근 범위'},
              {'id': 'apply', 'label': '2 · 서버 적용과 새 세션'},
              {'id': 'connect', 'label': '3 · API와 앱 연결'}],

    'nodes': [
        step('approve', 'scope', 0, 'security', '운영 변경 승인', '대상 프로필 · 영향 범위 합의'),
        step('path', 'scope', 1, 'database', 'Wiki 경로 확인', '호스트 경로와 실행 경로 대조'),
        step('isolate', 'scope', 2, 'security', '실행 경계 준비', '허용 경로 · 읽기 전용 · 전송 정책'),
        step('configure', 'apply', 2, 'backend', '서버 설정 적용', 'terminal.cwd · API bind · 비밀키'),
        step('restart', 'apply', 1, 'backend', '새 실행 문맥 시작', '승인된 재시작 또는 신규 시작'),
        step('testcwd', 'apply', 0, 'security', '실제 파일 접근 시험', 'cwd · 지침 · 읽기 · 쓰기 거부'),
        step('health', 'connect', 0, 'backend', 'API 지원 기능 확인', '/health · /v1/capabilities'),
        step('connectapp', 'connect', 1, 'backend', 'BFF에서 연결', '서버측 URL · 키 · 세션 매핑'),
        step('ready', 'connect', 2, 'frontend', '합성 입력 통합 시험', '조회 · SSE · 중지 · 권한 거부')
    ],
    'edges': [
        edge('approved-scope', 'approve', 'path', '승인', 'security'),
        edge('path-boundary', 'path', 'isolate'),
        edge('isolation-config', 'isolate', 'configure', '범위 확정', 'security'),
        edge('config-start', 'configure', 'restart'),
        edge('fresh-session', 'restart', 'testcwd', '새 세션', fromSide='left', toSide='right'),
        edge('cwd-tested', 'testcwd', 'health', '통과만', 'security', fromSide='bottom', toSide='top'),
        edge('capabilities-tested', 'health', 'connectapp', '지원 확인'),
        edge('integration-test', 'connectapp', 'ready')
    ],
    'cards': [
        {'dot': 'amber', 'title': '작업 경로는 HTTP 요청 필드가 아닙니다', 'items': [
            'local backend 예시 값: terminal.cwd = /home/ainsdev/wiki/pkm-articles',
            '요청 body의 cwd / workdir / workspace_root는 문서 조사판에서 지원이 확인된 계약이 아닙니다.',
            'session_id는 대화 식별자입니다. /p/<profile>/ 역시 임의 폴더 선택 API가 아닙니다.'
        ]},
        {'dot': 'cyan', 'title': 'API 선택은 앱의 목적에 맞춥니다', 'items': [
            'Wiki 전용 앱: BFF + Runs. 목록·페이지 API는 BFF가 별도로 구현합니다.',
            'OpenAI 호환 채팅 UI: UI 서버에서 base URL .../v1 + Chat Completions를 사용합니다.',
            '기존 UI도 Wiki 페이지·revision·출처 화면이나 접근 격리를 자동 제공하지 않습니다.'
        ]},
        {'dot': 'rose', 'title': '시험이 실패하면 공개하지 않습니다', 'items': [
            '설정 readback만으로 적용 성공이 아닙니다. 실제 새 세션과 모든 파일 도구에서 경계를 시험합니다.',
            '단순 cd, WIKI_PATH 또는 프롬프트만으로 Gateway 작업 루트를 고정했다고 주장하지 않습니다.',
            '현재 그림은 적용 절차입니다. 설정 변경·재시작·서비스 연결 시험은 실행하지 않았습니다.'
        ]}
    ]
}

query = {
    'schema_version': 2, 'diagram_type': 'workflow',
    'meta': meta('03 · 질문 한 번이 답변으로 돌아오는 과정 — 설계안', '03-query'),
    'lanes': [{'id': 'request', 'label': '1 · 앱 → BFF → API'},
              {'id': 'execute', 'label': '2 · 실행과 관측은 병행'},
              {'id': 'result', 'label': '3 · 결과 확인과 표시'},
              {'id': 'recovery', 'label': '4 · 끊김·중지 처리', 'variant': 'exception'}],

    'nodes': [
        step('ask', 'request', 0, 'frontend', '질문 + pageId 선택', '앱 → /api/agent/runs'),
        step('gate', 'request', 1, 'security', 'BFF 권한·범위 검사', 'owner · session 매핑 · 자료 제한'),
        step('submit', 'request', 2, 'backend', 'POST /v1/runs', 'input + session_id · 중복 방지 키', '202 = 접수'),
        step('agent', 'execute', 0, 'backend', '허용 Wiki 읽고 답변', '격리 도구 · 승인 자료·모델만'),
        step('sse', 'execute', 2, 'messagebus', 'SSE 하나만 구독', 'GET /v1/runs/{id}/events'),
        step('display', 'result', 0, 'frontend', '앱에 실제 결과 표시', '출처 · revision · 실패/부분 구분'),
        step('check', 'result', 1, 'security', 'BFF 최종 상태 대조', 'status + 결과 + 오류/partial'),
        step('disconnect', 'result', 2, 'messagebus', '연결이 끊어진 경우', '새 run을 만들지 않음'),
        step('stop', 'recovery', 0, 'security', '사용자가 중지 요청', 'owner 검사 후 /stop · stopping'),
        step('poll', 'recovery', 1, 'backend', '기존 run 상태 조회', 'GET /v1/runs/{id}')
    ],
    'edges': [
        edge('ask-auth', 'ask', 'gate'),
        edge('allowed-request', 'gate', 'submit', '허용만', 'security'),
        edge('accepted-execute', 'submit', 'agent', '실행', 'emphasis', role='main'),
        edge('accepted-observe', 'submit', 'sse', '202 후', 'dashed', role='async'),
        edge('result-check', 'agent', 'check', '종료 결과', 'emphasis', fromSide='bottom', toSide='top'),
        edge('stream-events', 'sse', 'check', '허용 이벤트', 'dashed'),
        edge('checked-display', 'check', 'display', '확인 결과', 'emphasis'),
        edge('stream-lost', 'sse', 'disconnect', '단절', 'security', role='error'),
        edge('reconcile', 'disconnect', 'poll', '복구', 'dashed', role='branch'),
        edge('poll-state', 'poll', 'check', '현재 상태', 'dashed', role='return'),
        edge('stop-status', 'stop', 'poll', '종료 확인', 'security', role='branch')
    ],
    'cards': [
        {'dot': 'cyan', 'title': 'BFF가 실행 문맥을 소유합니다', 'items': [
            '브라우저는 질문·pageId를 보냅니다. BFF가 사용자 → 대화 → Hermes session/run 소유권을 관리합니다.',
            '모델·도구·자료·instructions는 서버 정책으로 제한합니다. 경로·프로필·raw 요청을 그대로 전달하지 않습니다.',
            '쓰기·신규 원문 처리·Cron 조작은 이 읽기 질의 경로에서 거부합니다.'
        ]},
        {'dot': 'amber', 'title': '스트림은 진행 표시, 상태 조회는 복구 수단', 'items': [
            '설치 조사판의 제약에 대비해 BFF가 upstream SSE 하나를 유지하고 앱에 허용 이벤트만 중계합니다.',
            'Runs는 data JSON의 event 필드로 분기합니다. delta는 임시 표시이며 최종 결과와 다릅니다.',
            '재접속은 기존 run을 조회합니다. 이벤트 전체 replay나 Last-Event-ID 복구를 가정하지 않습니다.'
        ]},
        {'dot': 'rose', 'title': '완료를 과장하지 않습니다', 'items': [
            '202는 접수입니다. failed / interrupted / partial은 성공 답변으로 숨기지 않습니다.',
            'stop 접수는 stopping입니다. cancelled 또는 완료 경합을 확인하며 이미 발생한 효과를 되돌리지 않습니다.',
            '답변 완료 ≠ Wiki 저장. 기존 자동 컴파일·검증·게시 경로는 웹 요청과 별개입니다.'
        ]}
    ]
}

specs = {'01-connect': architecture, '02-workdir': setup, '03-query': query}
for folder, spec in specs.items():
    save(OUT / folder / 'candidate.json', spec)

baseline_path = OUT / 'source-baseline.json'
if not baseline_path.exists():
    entries = []
    for p in sorted(DOC.rglob('*')):
        if p.is_file() and not p.is_symlink():
            b = p.read_bytes()
            entries.append({'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)})
    save(baseline_path, {'kind': 'working-tree-document-snapshot', 'files': entries,
                         'note': 'Untracked documents are not evidence committed at Git HEAD. No meta.repository claim.'})

save(OUT / 'evidence.json', {
    'kind': 'document-based-design-not-runtime-observation',
    'wiki_root': str(ROOT),
    'sources': [
        {'path': str((DOC / f).relative_to(ROOT)), 'ranges': ranges}
        for f, ranges in [
            ('architecture.md', [[6, 20], [39, 75], [87, 93]]),
            ('workspace-and-gateway.md', [[7, 24], [43, 63], [65, 124]]),
            ('api-contract.md', [[6, 34], [36, 118], [120, 137]]),
            ('workflows.md', [[6, 95]]),
            ('data-contracts.md', [[100, 133]]),
            ('security-and-operations.md', [[6, 72]]),
            ('implementation-roadmap.md', [[18, 64]]),
            ('evidence.md', [[8, 15], [46, 80]])]
    ],
    'official_docs_read': [
        'https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server',
        'https://hermes-agent.nousresearch.com/docs/user-guide/configuration#working-directory'
    ],
    'historical_source_revision_reported_by_documents': '8d79c2ff57bba4b07e5b37ed90387b16541aef53',
    'current_policy': {'path': 'SCHEMA.md', 'ranges': [[3, 7]], 'effect': 'P3 automatic compile approved; do not copy historical unapproved status into current diagrams. Does not authorize web queries/publication.'},
    'diagram_claim_map': {
        '01-connect': {'app-request': 'architecture.md:64-71', 'api-request': 'api-contract.md:6-11', 'plain-read': 'architecture.md:41-48; data-contracts.md:117-127', 'agent-execution': 'architecture.md:50-60', 'agent-read': 'security-and-operations.md:37-48', 'cwd-binding': 'workspace-and-gateway.md:43-63', 'verified-publish': 'SCHEMA.md:3-7; architecture.md:87-93'},
        '02-workdir': {'approve/path/isolate': 'implementation-roadmap.md:18-29; security-and-operations.md:37-50', 'configure/restart/testcwd': 'workspace-and-gateway.md:65-124', 'health/connectapp/ready': 'workspace-and-gateway.md:107-116; implementation-roadmap.md:47-64'},
        '03-query': {'ask/gate/submit/agent': 'workflows.md:25-35; api-contract.md:60-84', 'sse/disconnect/poll': 'workflows.md:37-72; api-contract.md:86-112', 'check/display/stop': 'workflows.md:58-82; api-contract.md:114-118'}
    },
    'not_run': ['gateway_config_change', 'service_start_restart', 'live_hermes_api', 'model_call', 'wiki_publication', 'cron_change', 'installation', 'deployment']
})
print(json.dumps({'created_candidates': list(specs), 'source_baseline': str(baseline_path)}, ensure_ascii=False))
