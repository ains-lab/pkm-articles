"""Lecture content: foundations, architecture, workdir and data. No API calls."""
SLIDES = []
def s(chapter, title, lead, refs, kind='bullets', **content):
    SLIDES.append(dict(chapter=chapter,title=title,lead=lead,refs=refs,kind=kind,**content))

s('01 · 강의 안내','개인 Wiki를 웹으로 연결하기','Hermes API Gateway · 작업 경로 · 신뢰 경계', ['README.md:1-11','evidence.md:6-15'], 'hero',
  items=['파일 기반 지식 저장소를 안전한 웹 서비스로 연결하는 설계 수업','읽기 → 실행 → 게시를 구분하고, 각 단계의 증거를 확인한다.'],
  takeaway='2026-10-01 기술문서 기준 · 서비스 구현물이 아닌 강의 자료')
s('01 · 강의 안내','이 수업을 마치면','구성요소 이름보다 “누가 무엇을 허용하는가”를 설명할 수 있어야 합니다.', ['architecture.md:6-20','implementation-roadmap.md:18-64'],
  items=[['구조를 그린다','Browser, BFF, Gateway, Agent, Wiki의 책임과 신뢰 경계를 구분한다.'],['계약을 읽는다','cwd, session, run, SSE, revision, receipt가 보장하는 것과 못 하는 것을 설명한다.'],['오류를 설계한다','연결 단절·중복 요청·중지 경합·불완전 게시에서 안전한 다음 동작을 고른다.']],
  takeaway='권장 선수 지식: HTTP 요청/응답, JSON, 파일 경로 · 용어는 본문에서 다시 정의')
s('01 · 강의 안내','강의 지도','기능을 붙이는 순서가 아니라, 경계를 이해하는 순서로 진행합니다.', ['README.md:13-27'], 'table',
  headers=['학습 단위','핵심 질문'],rows=[['01–02 안내·아키텍처','어디까지가 웹이고 어디부터가 에이전트인가?'],['03–04 작업 경로·데이터','시작 위치와 권한, 파일과 공개 응답은 어떻게 다른가?'],['05–06 API·스트리밍','요청 접수, 진행, 재연결, 종료를 어떻게 판정하는가?'],['07–08 화면·보안','사용자에게 무엇을 보여주고 어떤 권한을 차단하는가?'],['09–10 게시·실습','언제 저장 완료라 말할 수 있고, 어떤 순서로 검증할까?']])
s('01 · 강의 안내','증거의 강도를 섞지 않는다','“문서에 있다”와 “실제로 동작했다”는 다른 문장입니다.', ['README.md:69-76','evidence.md:82-97'], 'table',
  headers=['표현','뜻','이 강의에서의 취급'],rows=[['관측','당시 파일·출력·소스에서 확인','과거 관측으로 시점을 붙임'],['공식 계약','조회 당시 공식 문서의 설명','설치 구현과 차이가 날 수 있음'],['제안','아직 만들지 않은 BFF·UI 설계','현재 endpoint로 말하지 않음'],['미확인','live API·모델·배포 등 미시험','성공/실패를 추정하지 않음']],
  takeaway='강의용 예시와 설계 실습은 실제 요청·응답 또는 운영 실행 결과가 아닙니다.')
s('01 · 강의 안내','이번 서비스의 출발점','개인용 인증 서비스의 read-only 탐색이 먼저입니다.', ['README.md:49-67','architecture.md:41-60'], 'compare',
  columns=[['초기 목표','목록과 기존 노트 탐색','출처·검토 상태 확인','모델 없이 정형 자료 조회'],['별도 승인 또는 비목표','통제된 질의는 후속 단계','컴파일·게시·Cron 제어는 분리','공개 무인 에이전트·새 DB/RAG는 초기 범위 아님']],
  takeaway='웹 화면을 만드는 일이 원문 처리나 자동화 권한을 늘려 주지 않습니다.')
s('01 · 강의 안내','수치에는 시각과 단위를 붙인다','다음은 원문 문서의 과거 snapshot이지, 현재 운영 상태가 아닙니다.', ['README.md:29-47','verification.json:163-169','verification.json:294-306'], 'table',status='과거 관측',
  headers=['당시 관측','값','해석'],rows=[['01:43:55 UTC 원문 보관','20개 버전: HTML 18 / PDF 2','논문 본문 분석 완료 수가 아님'],['활성 지식 문서','6개: 논문 2 / 개념 3 / 비교 1','논문별 컴파일 수와 다름'],['초기 컴파일 ledger','published_draft 2 / blocked_approval 16 / blocked_policy 2','PDF 보관 실패를 뜻하지 않음'],['02:01:11 UTC v3 전이','blocked_approval 16 / queued 2 / published_draft 2','queued는 완료가 아님']],
  takeaway='날짜: 2026-10-01 · 형식만 보고 현재 정책 상태를 하드코딩하지 않는다.')

s('02 · 아키텍처','하나의 Wiki, 서로 다른 세 경로','읽기·질의·게시를 같은 HTTP 통로로 섞지 않습니다.', ['architecture.md:39-60'], 'diagram',diagram='three-paths',
  takeaway='정형 조회에는 LLM이 필요 없고, 질의 완료에는 게시 권한이 포함되지 않는다.')
s('02 · 아키텍처','BFF는 브라우저를 위한 제한된 서버','Backend for Frontend: 브라우저에 필요한 계약만 제공하는 중간 계층입니다.', ['architecture.md:12-20','api-contract.md:6-11'],
  items=[['인증과 소유권','사용자를 확인하고 page/run/session 접근 권한을 매 요청마다 검사한다.'],['Projection과 요청 구성','공개 필드만 고른 DTO를 반환하고 서버가 허용한 입력만 upstream으로 보낸다.'],['할 수 없는 일','BFF의 API 제한만으로 Agent의 host 파일·도구 접근을 격리할 수는 없다.']],
  takeaway='BFF ≠ 무제한 reverse proxy · DTO = 외부에 전달하도록 고른 데이터 구조')
s('02 · 아키텍처','신뢰 경계가 보이는 전체 구조','도형은 책임과 제안 배치를 나타냅니다. 서비스 설치 증거가 아닙니다.', ['architecture.md:22-37','architecture.md:62-70'], 'diagram',diagram='architecture',status='설계 제안',
  takeaway='인터넷에 노출하는 것은 인증 경계이지 Wiki root나 Gateway 관리 API 전체가 아니다.')
s('02 · 아키텍처','정형 읽기: 모델 없이 페이지를 연다','파일 존재 여부가 아니라 일관된 snapshot을 서비스합니다.', ['workflows.md:6-23','data-contracts.md:117-127'], 'diagram',diagram='read-sequence',status='설계 제안',
  takeaway='읽는 도중 게시가 바뀌면 snapshot_conflict · 빈 페이지나 완료본으로 위장하지 않는다.')
s('02 · 아키텍처','질의: 실행 문맥은 BFF가 소유한다','사용자의 질문은 입력이지만, 도구·모델·자료 범위를 정하는 권한은 아닙니다.', ['workflows.md:25-35'], 'diagram',diagram='query-sequence',status='설계 제안',
  takeaway='답변에는 확인 가능한 page revision/hash와 읽은 범위를 연결한다. 없는 인용은 만들지 않는다.')
s('02 · 아키텍처','같은 IP 표기도 다른 위치일 수 있다','127.0.0.1은 그 프로세스가 속한 network namespace의 loopback입니다.', ['architecture.md:64-70','security-and-operations.md:61-72'], 'compare',
  columns=[['같은 호스트·네임스페이스','BFF → loopback Gateway를 우선 검토','Gateway key는 BFF 서버 안에 보관','브라우저는 same-origin BFF만 호출'],['다른 호스트·컨테이너','서로의 127.0.0.1은 같은 서버가 아님','사설 라우팅·방화벽·서비스 인증 필요','경로 문자열만으로 mount가 생기지 않음']],
  takeaway='배치 위치를 먼저 그린 뒤 주소·인증·mount 계약을 정한다.')
s('02 · 아키텍처','설계 토론 ① 편리하지만 위험한 연결','“브라우저가 path와 Gateway key를 보내면 구현이 간단하지 않을까요?”', ['architecture.md:77-85','security-and-operations.md:23-47'], 'exercise',status='강의용 예시',
  prompt='이 설계에서 서로 다른 위험 세 가지를 찾고, 대체 경로를 제시해 보세요.',
  answer='키가 브라우저에 노출되고, 사용자 입력 path가 파일 접근 권한처럼 동작하며, 관리 API까지 중계할 위험이 있습니다. 서버측 key + pageId allowlist + method/path allowlist로 바꾸고 Agent의 OS/도구 격리를 별도로 검증합니다.')

s('03 · 작업 경로','cwd는 출발점이지 울타리가 아니다','current working directory는 상대경로를 해석하는 기준입니다.', ['workspace-and-gateway.md:7-24','workspace-and-gateway.md:118-124'], 'hero',
  items=['/home/ainsdev/wiki/pkm-articles','작업 루트 지정 ≠ HTTP document root 공개 ≠ 파일 접근 sandbox'],
  takeaway='local backend는 실행 사용자의 권한을 따르므로 Wiki 밖 절대경로도 별도 통제가 필요하다.')
s('03 · 작업 경로','기본 cwd가 결정되는 경로','다음은 기술문서가 조사한 local Gateway 구현의 설명입니다.', ['workspace-and-gateway.md:43-55'], 'diagram',diagram='cwd',status='문서 기반',
  takeaway='명령 workdir·세션 cwd는 기본값보다 우선할 수 있다. 비로컬 backend는 mount까지 확인한다.')
s('03 · 작업 경로','이름이 비슷해도 계약은 다르다','설정이 저장되었다고 런타임이 그 키를 읽는 것은 아닙니다.', ['workspace-and-gateway.md:17-24','workspace-and-gateway.md:57-63'], 'table',
  headers=['이름','실제 의미 / 문서의 경계'],rows=[['terminal.cwd','도구의 기본 작업 기준 경로'],['WIKI_PATH','Wiki 탐색 관례; Gateway cwd API가 아님'],['MESSAGING_CWD','명시적 cwd가 없는 local 경로의 legacy fallback'],['request cwd / workdir / workspace_root','조사한 HTTP handler에 공개 적용 계약 없음'],['gateway.platforms.api_server.cwd','확인된 설정 계약 아님'],['/p/<profile>/…','프로필 라우팅; 임의 디렉터리 선택이 아님']])
s('03 · 작업 경로','설정 절차도 작은 변경으로 나눈다','다음은 원문의 승인 후 절차 예시입니다. 이 강의에서는 실행하지 않습니다.', ['workspace-and-gateway.md:65-87'], 'code',status='강의용 예시',
  code='hermes -p default config get terminal.cwd\nhermes -p default config get terminal.backend\n\n# 별도 변경 승인 후에만\nhermes -p default config set terminal.cwd /home/ainsdev/wiki/pkm-articles\nhermes -p default config get terminal.cwd',
  items=['원래 값과 영향을 받는 프로필·플랫폼을 먼저 기록한다.','config.yaml 전체나 terminal block을 직접 덮어쓰지 않는다.','config readback은 저장 확인이다. 실행 중 세션의 적용 증거는 아니다.'])
s('03 · 작업 경로','API bind와 secret은 별도 결정','cwd 변경 승인에 API 활성화·재시작 승인까지 들어 있지 않습니다.', ['workspace-and-gateway.md:89-116'], 'code',status='강의용 예시',
  code='# API enable/bind 변경까지 별도 승인한 경우만\nhermes -p default config set gateway.api_server.enabled true\nhermes -p default config set gateway.api_server.host 127.0.0.1\nhermes -p default config set gateway.api_server.port 8642',
  items=['API_SERVER_KEY는 운영자의 secret provisioning 경로로만 주입한다.','API_SERVER_* override와 terminal.cwd bridge의 우선순위를 혼동하지 않는다.','restart와 gateway run을 무조건 연속 실행하지 않는다. 실행 중 작업부터 확인한다.'])
s('03 · 작업 경로','적용 성공은 새 세션에서 확인한다','설정값 · 실제 도구 위치 · 프로젝트 지침 · 접근 권한은 각각 확인해야 합니다.', ['workspace-and-gateway.md:107-124','implementation-roadmap.md:47-64'],
  items=[['실행 경로','새 세션의 실제 tool cwd와 허용 자료 접근을 확인한다.'],['지침 발견','AGENTS 외 우선순위 파일·skip 설정·git-root 탐색·prompt 캐시를 고려한다.'],['권한 집행','쓰기 거부와 Wiki 밖 접근 제한을 실제 도구 경로마다 시험한다.'],['서비스 계약','승인 후 health → capabilities → 비민감 합성 API 시험으로 확인한다.']],
  takeaway='원문의 과거 terminal.cwd=. 관측을 현재값이나 무조건적인 rollback 값으로 재사용하지 않는다.')
s('03 · 작업 경로','설계 토론 ② 설정 성공의 함정','“임의 cwd 키를 저장했고 config get에도 나오니 적용 완료입니다.”', ['workspace-and-gateway.md:57-63','workspace-and-gateway.md:107-124'], 'exercise',status='강의용 예시',
  prompt='이 주장을 반박하는 데 필요한 확인 항목을 나열해 보세요.',
  answer='실제 소비하는 설정 키와 handler를 먼저 확인합니다. 새 세션에서 tool cwd·프로젝트 지침을 관측하고, 비로컬 환경은 mount를 확인합니다. 마지막으로 OS/파일 도구의 접근 거부를 시험해야 합니다. 키 저장 성공은 지원 계약이나 sandbox 증거가 아닙니다.')

s('04 · 데이터 계약','파일 원장과 HTTP 응답은 다르다','저장소 구조를 URL 구조로 그대로 복사하지 않습니다.', ['data-contracts.md:6-26','tech-stack.md:6-17'], 'diagram',diagram='data-layers',
  takeaway='원본·지식·상태·실행 근거를 분리하고, BFF는 필요한 지식·서지만 최소 투영한다.')
s('04 · 데이터 계약','원본 기록은 나중에 고쳐 맞추지 않는다','source.json의 wiki_compiled:false는 수집 당시의 정보입니다.', ['data-contracts.md:28-36'],
  items=[['수집 시점','원본 HTML/PDF 바이트와 형식·버전·길이·hash를 보관한다.'],['컴파일 이후','완료 여부는 compilation ledger + receipt + 실제 output으로 확인한다.'],['잘못된 동기화','UI 배지를 맞추려고 불변 source.json을 수정하면 이력이 손상된다.']],
  takeaway='목록 API는 승인된 metadata를 읽는다. 목록 표시를 위해 PDF를 추출하지 않는다.')
s('04 · 데이터 계약','상태는 하나의 초록불이 아니다','서로 독립된 질문을 하나의 completed 배지로 합치지 않습니다.', ['data-contracts.md:54-67'], 'table',
  headers=['상태 축','확인하는 질문','다른 의미로 확대 금지'],rows=[['원문 확보','파일을 보관했는가?','의미 분석 완료 아님'],['HTML 제공','공식 HTML이 제공되는가?','PDF까지 미확보란 뜻 아님'],['컴파일','읽기·생성은 어느 단계인가?','모델 종료 ≠ 게시 완료'],['게시 거래','committed인가?','실물 hash 검사를 대체 못함'],['인간 검토','human_reviewed 근거가 있는가?','자동 검사는 인간 검토 아님'],['API 실행','run이 종료되었는가?','논문 주장·업무 성공 보장 아님']])
s('04 · 데이터 계약','페이지의 provenance를 화면에 남긴다','Provenance는 결과가 어떤 입력·정책·작업에서 왔는지 추적하는 정보입니다.', ['data-contracts.md:38-54'], 'compare',
  columns=[['문서의 정체성','schema / type / title / summary','revision / transaction_id','policy_revision / prompt_revision'],['검토의 범위','read_scope / unread_scope','status: draft / reviewed / superseded','review_state: unreviewed / needs_review / human_reviewed']],
  takeaway='published_draft는 compilation 상태다. 페이지 status의 enum으로 바꿔 넣지 않는다.')
s('04 · 데이터 계약','DTO: 필요한 필드만 공개한다','아래는 제안된 BFF 응답의 축약 예시이며 실제 응답이 아닙니다.', ['data-contracts.md:69-104'], 'code',status='설계 제안',
  code='{\n  "schema": "pkm-web-page/v1",\n  "page_id": "entity-arxiv-2609.30830v1",\n  "revision": 2,\n  "status": "draft",\n  "review_state": "unreviewed",\n  "content_sha256": "<실제 hex SHA-256>",\n  "snapshot_id": "<committed snapshot 식별자>"\n}',
  items=['page_id는 서버가 생성·검증하는 식별자다. 파일 path가 아니다.','목록에는 본문·claim 상세·내부 evidence 경로를 생략한다.','pkm-web-page/v1과 snapshot_id는 Hermes의 기존 필드가 아니다.'])
s('04 · 데이터 계약','ID를 파일로 바꾸는 순간이 경계다','허용된 ID라도 실제로 여는 파일까지 안전해야 합니다.', ['data-contracts.md:106-115'],
  items=[['입력 제한','pageId → 승인된 Markdown 매핑을 사용한다. NUL·절대경로·..·혼합 구분자·중복 decoding·symlink를 거부한다.'],['열기까지의 일관성','canonical path 확인만으로는 검사와 사용 사이의 교체(TOCTOU)를 막지 못한다. 안전한 열기·snapshot·권한을 결합한다.'],['링크 해석','arxiv-2609.30830v1 뒤에 .md를 덧붙인다. 점 이후 문자열을 확장자로 오인해 치환하지 않는다.']],
  takeaway='서버 절대경로는 실제 웹 DTO에서 비공개다. 이 강의의 로컬 경로 표기는 설명용이다.')
s('04 · 데이터 계약','캐시도 검증한 snapshot만 기억한다','오래된 값보다 더 위험한 것은, 서로 다른 시점의 값을 한 페이지로 합치는 것입니다.', ['data-contracts.md:117-127','architecture.md:87-93'], 'diagram',diagram='snapshot',status='설계 제안',
  takeaway='충돌은 제한 재시도 또는 snapshot_conflict · process-local cache는 정식 원장이 아니다.')
s('04 · 데이터 계약','출처 링크도 범위를 말해야 한다','링크가 있다는 사실과 내용을 검토했다는 사실은 다릅니다.', ['data-contracts.md:106-115','security-and-operations.md:52-59'], 'compare',
  columns=[['HTML 근거','정확한 버전 source_url','실제 존재하는 anchor','불명확하면 “세부 위치 미확인”'],['승인된 PDF 텍스트 근거','source.pdf#page=N','물리적 1-based 페이지','그림·불명료 수식·레이아웃 미검토 유지']],
  takeaway='HTML에 없는 PDF 페이지 번호를 만들지 않는다. 원문 링크 열기는 도표 검토 완료가 아니다.')
