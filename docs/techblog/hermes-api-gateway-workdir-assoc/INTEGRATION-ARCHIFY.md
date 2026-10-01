# 외부 앱 ↔ Hermes ↔ Wiki — 연동에 집중한 Archify

**한 줄 요약: 외부 앱은 BFF의 URL에 연결하고, Hermes는 서버에서 지정한 Wiki 작업 경로를 사용합니다. URL과 파일 경로는 서로 다른 설정입니다.**

이 문서는 기존 전체 지도에서 연동에 필요한 부분만 좁힌 설계입니다. 실제 Gateway 설정·서비스·Cron은 변경하지 않았습니다. [기존 전체 지도](ARCHIFY.md)는 그대로 보존합니다.

## 1. 그림 세 장으로 보기

아래 HTML은 브라우저에서 직접 열 수 있는 독립 Archify 파일입니다. 한국어 본문과 조작 UI, 확대·축소·검색·테마 전환을 제공합니다. **데스크톱 열람을 권장합니다.**

| 순서 | 그림 | 답하는 질문 |
|---|---|---|
| 01 | [외부 앱–BFF–Hermes–Wiki 아키텍처](../../../.archify/architecture-gateway-workdir-20261001-084424/01-connect/diagram.html) | 어떤 서비스가 무엇에 연결되는가? 목록 보기와 AI 질문은 왜 다른 경로인가? |
| 02 | [작업 디렉터리 적용 워크플로](../../../.archify/architecture-gateway-workdir-20261001-084424/02-workdir/diagram.html) | 작업 경로를 어디서 설정하고, 실제 적용을 어떻게 확인하는가? |
| 03 | [질의·SSE·재연결 워크플로](../../../.archify/architecture-gateway-workdir-20261001-084424/03-query/diagram.html) | 질문 접수부터 답변·중지까지 앱이 무엇을 관리해야 하는가? |

그림 01은 위쪽의 `외부 앱 → BFF → Gateway`부터 읽습니다. 아래쪽 Wiki로 내려가는 두 선은 **모델 없는 조회**와 **Agent의 허용된 읽기**입니다. 작업 경로 설정은 HTTP 데이터 전달이 아니라 실행 기준 경로를 정하는 관계입니다. 점선 자동 컴파일은 별도 배치이며 웹 요청이 호출하는 경로가 아닙니다.

그림 02는 첫 줄 왼쪽→오른쪽, 둘째 줄 오른쪽→왼쪽, 셋째 줄 왼쪽→오른쪽으로 화살표를 따라갑니다. 그림 03의 실행과 SSE 구독은 병행합니다. `202`, 스트리밍 중인 텍스트, 최종 결과를 구분해서 읽으면 됩니다.

## 2. 앱 종류에 따라 두 가지로 연결합니다

| 목적 | 연결 방식 | 별도로 필요한 것 |
|---|---|---|
| 기존 채팅 앱에서 Wiki에 질문 | OpenAI 호환 **앱 서버** → Hermes `POST /v1/chat/completions` | 앱 서버측 키 보관, 세션 구분, 제한된 도구·자료, 실제 버전 호환 시험 |
| Wiki 목록·본문·출처와 대화를 한 화면에 표시 | 전용 UI → **BFF** → 읽기 facade / Hermes Runs | 페이지 DTO·권한·session/run 소유권·SSE 중계·실패/중지 UX 구현 |

**이 Wiki에는 두 번째 방식을 권장합니다.** BFF(Backend for Frontend)는 앱 전용 중계 서버입니다. 사용자를 인증하고, 공개해도 되는 문서만 읽으며, Hermes를 호출할 때 자료·도구·모델과 대화 소유권을 제한합니다. 범용 채팅 UI만 연결한다고 Wiki 목록이나 출처·revision 화면이 생기지는 않습니다.

외부 SaaS가 사설 서버에 도달할 수 없다면 URL 입력만으로 연동되지 않습니다. 승인된 서버 간 사설 경로 또는 인증된 제한 relay를 먼저 설계해야 합니다. 브라우저에 Gateway 공용키를 넣거나 8642 포트를 무조건 인터넷에 여는 방식은 기본안이 아닙니다.

## 3. 실제로 맞춰야 할 네 가지

### ① 앱이 호출할 URL

- 브라우저는 같은 origin의 BFF만 호출합니다. `/api/wiki/*`, `/api/agent/*`는 **새로 구현할 BFF 계약**입니다.
- BFF와 Hermes가 **같은 호스트·네트워크 namespace**에 있는 예: `http://127.0.0.1:8642`.
- OpenAI 호환 앱 서버의 base URL 예: `http://127.0.0.1:8642/v1`. SDK가 `/chat/completions`를 붙이는 형식이면 `/v1`을 중복해서 붙이지 않습니다.
- 다른 호스트나 컨테이너의 `127.0.0.1`은 Hermes 호스트가 아닙니다. 도달 가능한 사설 서비스 주소·방화벽·서버 인증이 필요합니다.
- `model: hermes-agent`는 API 별칭입니다. 요청값이나 응답의 model echo만으로 실제 실행 모델을 확인했다고 하지 않습니다.

### ② Hermes가 파일을 찾을 기준 경로

local backend에서 사용할 대상 Wiki는 `/home/ainsdev/wiki/pkm-articles`입니다. 지원되는 설정은 **대상 프로필의 `terminal.cwd`**입니다.

운영 변경 승인 후의 설정 예시이며 **이번에는 실행하지 않았습니다**:

```bash
hermes -p default config get terminal.cwd
hermes -p default config set terminal.cwd /home/ainsdev/wiki/pkm-articles
hermes -p default config get terminal.cwd
```

`default`는 기존 문서의 예시입니다. 실제 적용할 프로필·영향 범위를 먼저 승인해야 합니다. 기존 default를 바꾸면 다른 세션·플랫폼에도 영향을 줄 수 있습니다. 별도 프로필은 설정 분리 수단이지 OS 접근 격리의 증거가 아닙니다.

컨테이너라면 **호스트의 Wiki 경로 → 실행 환경에서 보이는 mount 경로**를 먼저 정하고, 실행 환경 기준의 cwd를 사용합니다. mount·파일 권한을 설정하지 않은 채 호스트 절대경로만 넣어도 파일이 보이는 것은 아닙니다. 같은 Wiki 전체를 외부 에이전트에 노출하기보다 승인된 지식·서지 범위를 최소 노출하는 설계가 필요합니다.

### ③ 키·사용자·대화의 연결

- `API_SERVER_KEY`: BFF/앱 서버 → Hermes 인증용. 브라우저 번들·localStorage·URL·로그에 넣지 않습니다.
- 앱 로그인: 누가 내 Wiki에 접근할 수 있는지 판단합니다. Gateway 키 하나가 앱 사용자별 권한을 대신하지 않습니다.
- 앱 conversation ID → Hermes session ID → run ID: BFF가 소유권을 관리하고 상태/events/stop 요청마다 재검사합니다.
- Chat의 대화 지속은 `X-Hermes-Session-Id`, Runs는 body `session_id`입니다. 서로 다른 계약을 혼합하지 않습니다.
- session ID, `/p/<profile>/`, `X-Hermes-Session-Key`는 임의 디렉터리 선택 권한이 아닙니다. 프로필 URL은 multiplex 활성화·프로필별 키 등 지원 조건을 확인한 경우만 사용합니다.

### ④ 실제 접근 권한

**cwd는 출발 위치일 뿐, 읽기 전용 보안 장치가 아닙니다.** AGENTS.md·system prompt만으로 쓰기나 Wiki 밖 절대경로 접근이 차단되지 않습니다.

질의용 환경은 허용 경로, read-only OS 권한/mount, 도구 허용 목록, 네트워크·모델 전송 범위를 실제로 집행해야 합니다. terminal만 격리하고 파일·MCP·브라우저 도구가 다른 경계를 사용하는 경우도 시험합니다. 읽기 도구 이름만 보고 PDF 추출까지 허용하지 않습니다.

## 4. 두 요청은 이렇게 다르게 흐릅니다

### 문서 보기 — 모델 호출 없음

`로그인 → GET /api/wiki/pages/{pageId} → BFF가 pageId/권한 확인 → committed receipt·revision/hash가 맞는 지식 Markdown 읽기 → 최소 DTO → 안전하게 렌더링`

브라우저는 임의 파일 경로를 전달하지 않습니다. Wiki 전체를 static document root로 열지 않고, raw HTML을 앱 origin에서 그대로 실행하지 않습니다. snapshot 충돌은 “갱신 중, 다시 시도”로 처리합니다.

### AI에게 질문 — 실행 정책 승인 후

`질문·pageId → BFF 권한·자료 검사 → input/session_id와 Idempotency-Key 구성 → POST /v1/runs → 202/run_id → 실행 + SSE 관측 → 최종 상태·결과 확인 → 답변·실제 출처 표시`

- Runs `/events`는 `data:` JSON의 `event` 필드로 분기합니다. Chat/Responses 스트림 형식과 혼합하지 않습니다.
- 기존 문서의 설치 조사판은 SSE 단일 queue·연결 종료 후 transport 소멸 제약을 보고했습니다. 따라서 BFF upstream 구독 하나 + 필요한 앱 중계 + `GET /v1/runs/{id}` 상태 대조를 보수적 기본안으로 둡니다. 현재 설치판은 live capability와 실제 통합 시험으로 다시 확인해야 합니다.
- 새로고침·단절은 새 실행이 아닙니다. 기존 run을 조회하며 전체 이벤트 replay를 가정하지 않습니다.
- 같은 요청의 전송 재시도에는 같은 idempotency key/payload를 사용합니다. 수정된 질문은 새 요청입니다.
- 중지는 소유권 확인 후 `/stop`을 호출하고 종료 상태를 확인합니다. `stopping`이나 브라우저 연결 종료만으로 “취소 완료”라고 하지 않습니다.
- 답변 완료는 Wiki 저장이 아닙니다. 초기 BFF에는 임의 쓰기·compile/publish·Cron 변경 API를 연결하지 않습니다.

## 5. 기존 자동 컴파일과의 관계

기술문서의 초기 snapshot에는 P3 미승인·비활성 설명이 남아 있습니다. **현재 정식 [SCHEMA의 최신 운영 개정](../../../SCHEMA.md)은 별도 P3 자동 컴파일·자동 검증 후 게시를 승인했습니다.** 이를 다시 사용자 검토 필수나 미승인 상태로 표시하지 않습니다.

다만 기존 배치의 승인은 신규 웹 질의 backend·새 자료 전송·임의 페이지 수정 권한이 아닙니다. 수집/컴파일 Cron은 유지하고, 웹 앱은 검증된 결과를 읽는 소비자로 설계합니다. 여기서는 등록 상태를 재조회하거나 예약 실행 성공을 검증하지 않았습니다.

## 6. 근거와 검증

- 주 근거: [작업 경로](workspace-and-gateway.md), [아키텍처](architecture.md), [API 계약](api-contract.md), [워크플로](workflows.md), [보안](security-and-operations.md), [데이터 계약](data-contracts.md).
- 재조회한 공식 문서: [Hermes API Server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server), [Working Directory](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#working-directory).
- [문서 줄·의미별 근거](../../../.archify/architecture-gateway-workdir-20261001-084424/evidence.json), [원문 파일 hash 기준점](../../../.archify/architecture-gateway-workdir-20261001-084424/source-baseline.json), [산출물·브라우저 검증 집계](../../../.archify/architecture-gateway-workdir-20261001-084424/verification.json).
- 원천 문서는 untracked 작업 트리 자료를 포함합니다. Git HEAD에 커밋된 구현 증거나 live 서비스 관측으로 바꾸어 표시하지 않았습니다.

각 `candidate.json`이 수정 가능한 명세입니다. 생성된 HTML을 직접 고치면 검증 hash가 달라집니다. 01의 최종 finalize/browser 근거는 `01-connect/review-2/`, 나머지는 각 폴더 루트입니다.

자동 검사는 Archify showcase와 실제 Chromium의 데스크톱 containment·테마 검사를 뜻합니다. 대표 캡처의 잘림·겹침 검토는 표본이며 모바일 전체 가독성, 스크린리더, 모든 Viewer 조작·내보내기, 실제 서비스 통합 검증을 대신하지 않습니다. 보조 글씨는 작으므로 확대하거나 이 해설을 함께 읽으세요.
