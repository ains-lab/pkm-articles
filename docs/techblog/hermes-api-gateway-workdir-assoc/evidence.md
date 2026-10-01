# 근거·호환성 차이·검증 범위

> 조사일: 2026-10-01 UTC. 파일과 코드를 읽은 사실, 정적 해석, 실제 실행을 분리한다.
> [목차](README.md) · [API 계약](api-contract.md) · [문서 검증 결과](verification.json)

## 1. 범위와 관측 기준점

- Wiki root: `/home/ainsdev/wiki/pkm-articles`.
- 작업 시작 branch: `main`. 기존 사용자 수정·untracked 파일이 있었으며 정리/commit/push하지 않는다.
- Hermes source: `/home/ainsdev/.hermes/hermes-agent`.
- 로컬 HEAD: `8d79c2ff57bba4b07e5b37ed90387b16541aef53`.
- 로컬 manifest version: `0.21.1`. package-lock.json의 기존 수정이 관측되었으므로 checkout 전체를 pristine이라고 부르지 않는다.
- 사용자 추가 확인: 기술문서에 Wiki 작업 경로와 적용 절차를 명시하고 **실제 Gateway 설정 유지**.

근거 해석 우선순위: Wiki 실행 경계는 현재 정식 Wiki 계약, Hermes 제품 설명은 최신 공식 문서, 설치 구현의 세부 동작은 해당 checkout 소스다. 최신 웹 문서와 로컬 구현이 다르면 어느 하나로 다른 쪽을 덮어쓰지 않고 호환성 위험으로 기록한다.

## 2. Wiki 정식 근거

| ID | 근거 | 적용 내용 |
| --- | --- | --- |
| W1 | [SCHEMA](../../../SCHEMA.md) §1–3, §9–10 | 파일 원장, 원본 보존, v3 PDF 텍스트 수동 예외와 금지 범위, 단계 승인 |
| W2 | [index](../../../index.md), [log](../../../log.md) | 현재 탐색·실제 작업 이력; 과거 기록을 새 실행으로 재사용하지 않음 |
| W3 | [COLLECTION](../../../_meta/COLLECTION.md) | 공유 mkdir lock, 원본 수집과 지식화 분리 |
| W4 | [STATE-CONTRACTS](../../../_meta/STATE-CONTRACTS.md) | 상태 전이, work_key, journal/receipt, no_cost_cap |
| W5 | [P3-PREPARATION](../../../_meta/P3-PREPARATION.md) | P3 HOLD, 승인/등록/활성화 분리, 현재 backlog |
| W6 | [compilation ledger](../../../_meta/state/compilation.json) | HTML/PDF별 compilation 상태의 정형 집계 |

원본 `source.json`만 읽어 버전·형식을 집계하고 source.html/source.pdf는 보호 hash 계산 외에 본문 분석에 사용하지 않았다. entities/concepts/comparisons/queries의 파일 수를 코드로 계산했다. 기존 논문의 내용을 재요약하거나 새로운 지식 페이지를 만들지 않았다.

### 동시 변경 관측

초기 기준점은 01:43:55 UTC다. 02:01:11 UTC 대조에서 이 작업의 write set 밖인 `AGENTS.md`, `SCHEMA.md`, `_meta/COMPILATION.md`, `_meta/STATE-CONTRACTS.md`, `_meta/automation.json`, `_meta/state/{compilation,research-review,feedback}.json`의 변경을 확인했다. 최근 log에는 별도 PDF 텍스트 정책 v3 적용 이력이 있었고, ledger의 PDF 두 편은 queued였다. 관련 정책을 다시 읽어 v3의 제한된 텍스트 경로를 문서에 반영했으며 원본이나 외부 변경을 되돌리지 않았다.

따라서 “모든 보호 파일 불변”으로 검증을 통과시키지 않는다. [verification.json](verification.json)은 초기 hash와 최종 hash의 차이, 원본/기존 지식 보존, 문서 작성의 실제 범위를 분리한다. 상태 파일은 이후에도 갱신될 수 있으며 문서 숫자는 명시된 시각의 관측값이다. 이 작업은 v3 실행·설치·본문 읽기·게시를 수행하지 않았다.

## 3. 최신 공식 Hermes 문서 — 실제 조회

| ID | URL | 사용 범위 |
| --- | --- | --- |
| H1 | [API Server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server) | HTTP endpoint, auth, model 선택, SSE, run/session 계약 |
| H2 | [Programmatic Integration](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration) | API/TUI/ACP 구분, run control·terminal outcome 설명 |
| H3 | [문서 진입점](https://hermes-agent.nousresearch.com/docs/) · [LLM 문서 색인](https://hermes-agent.nousresearch.com/docs/llms.txt) | 공식 문서 탐색 |

API 문서의 중간 절은 추출 cache 파일을 추가로 읽어 확인했다. API endpoint를 호출한 것이 아니라 문서 웹페이지를 조회한 것이다. configuration의 cwd 상세와 context-files/profiles는 아래 설치 checkout의 공식 문서 소스를 조사했다. 해당 원격 페이지를 별도 모두 재조회한 것으로 표시하지 않는다.

## 4. 설치 소스 근거 지도

아래 file:line은 위 로컬 HEAD를 기준으로 한다. 링크는 해당 revision의 upstream source를 가리키며, local 코드 판독이 근거다. 웹 permalink 각각의 원격 도달성까지 검증한 것은 아니다.

| ID | 소스 | 핵심 근거 |
| --- | --- | --- |
| S1 | [gateway/run.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/run.py#L1892):1892–1942,2071–2087 | terminal config bridge와 placeholder cwd |
| S2 | [gateway/platforms/api_server.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server.py#L323):323–345,2098–2169 | 요청 override 범위, AIAgent·toolset·fallback 생성 |
| S3 | [api_server.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server.py#L770):770–826,3805–3837 | CORS 헤더 시점, key startup guard, aiohttp |
| S4 | [api_server_openai_routes.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server_openai_routes.py#L424):424–510,769–849 | Chat 세션 header와 이력, Responses 입력 |
| S5 | [api_server_runs.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server_runs.py#L598):598–656,717–756,857–878 | event queue·완료·연결 종료·중지 경합 |
| S6 | [api_server_run_idempotency.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server_run_idempotency.py#L51):51–82,131–185 | 내구 store, memory fallback, terminal 보존 |
| S7 | [api_server.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/gateway/platforms/api_server.py#L954):954–994,3742–3743 | 별도 300초 캐시, transport/status TTL |
| S8 | [agent/system_prompt.py](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/agent/system_prompt.py#L586):586–597 및 agent/prompt_builder.py:1501–1609 | cwd 기준 project context, 우선순위·AGENTS 탐색 |
| S9 | [pyproject.toml](https://github.com/NousResearch/hermes-agent/blob/8d79c2ff57bba4b07e5b37ed90387b16541aef53/pyproject.toml#L3):3–15,40–64,128–135,200 | 패키지/Python 범위와 dependency 선언 |
| S10 | website/docs/user-guide/configuration.md:2781–2796 | terminal.cwd 정식 설정, legacy env |
| S11 | gateway/config.py:355–443, gateway/session_context.py:115–143 | 공개 platform cwd 필드와 내부 세션 문맥의 구분 |
| S12 | tools/file_tools_paths.py:116–202, tools/environments/local.py:775–788 | 상대경로 해석과 local 사용자 권한 |

두 독립 읽기 전용 조사 결과를 통합했고, 작성자가 cwd bridge, API request selection, fallback, key guard, CORS, Chat session, Runs queue/stop/idempotency 핵심 구간을 직접 다시 읽었다. 관련 테스트 assertion의 정적 조사는 실행한 테스트 통과 수가 아니다.

## 5. 공식 문서와 로컬 구현의 차이

| 항목 | 공식 문서/일반 기대 | 로컬 소스 관측과 문서 처리 |
| --- | --- | --- |
| SSE keepalive | H1은 10초를 설명 | Runs handler의 wait timeout은 30초. 배포판 실측 필요 |
| Runs 재접속 | attach/detach 가능한 UX 설명 | 단일 queue 소비·finally transport 삭제; 무손실 replay/fan-out 보장으로 해석 금지 |
| CORS | explicit origin allowlist 제공 | PATCH/Session-Key/expose header 및 prepared SSE 헤더 시점 제약. 정적 위험이며 browser 재현 미실시 |
| Idempotency | Runs는 내구 key 계약 | store memory fallback 가능; Chat/Responses 300초 캐시와 구분 |
| 실행 모델 | 최신 문서에 runtime metadata와 엄격한 terminal outcome 설명 | 로컬 Runs `_execute_run`의 완료 payload에는 동일한 모든 필드가 있지 않음. client는 capability/실제 응답으로 협상해야 함 |
| terminal 성공 | 최신 문서는 partial/interrupted의 엄격한 실패 분류 설명 | 로컬 handler마다 분기·flags 차이가 있어 HTTP 200/`completed`만으로 업무 성공 판정 금지 |
| 세션 직렬화 | 최신 문서에 turn lease 설명 | 이번 조사만으로 모든 호출 경로의 집행을 독립 검증하지 않음. BFF 단일 writer 및 동시성 시험 필요 |
| 파일 업로드 | Chat/Responses의 일반 파일 입력 미지원 | artifact 등 별도 route 존재가 논문 업로드·PDF 분석 권한을 만들지 않음 |

위 차이들은 Hermes 소스 수정 요청이 아니므로 이번 작업에서 고치지 않았다. 특히 최신 웹 문서에 나온 필드를 설치판이 항상 반환한다고 가정한 타입 정의를 만들지 않는다.

## 6. 실제 수행한 검증 종류

- Git: Wiki branch/status, 설치 Hermes HEAD/status 확인.
- CLI: Gateway/help와 비밀 아닌 설정 leaf key 읽기.
- Package: launcher venv의 Python과 선택 dependency metadata 확인.
- Wiki: metadata·파일 목록 집계, 보호 대상 hash 기준점과 최종 대조.
- 문서: 로컬 링크, code fence, JSON 예시 구문, Bash 예시 `bash -n`, Git whitespace 확인.
- 변경 경계: 이전 log prefix 보존, 기술문서 색인 반영, 기존 지식 페이지 수 유지.

실제 횟수·결과·파일 hash는 [verification.json](verification.json)에 기록한다. 문서 예시는 schema/업무 의미 전체를 검증한 것이 아니며, shell syntax 통과는 설정 명령 실행 성공이 아니다.

## 7. 수행하지 않은 항목

Gateway 설정 변경, key 생성/열람, 서버 시작·재시작, 포트 공개, live API/모델 호출, 브라우저 렌더링, Lighthouse·접근성 audit, 외부 frontend 배포, Hermes 코드 수정·전체 test suite, dependency 설치, 신규 profile/DB/collector, 논문 본문 분석/PDF 추출, 지식 게시, Cron 변경, commit/push는 하지 않았다.

`.env`·인증 파일·타 프로필·기존 SQLite DB·이전 백업을 열지 않았다. 이번 결과는 **기술문서 패키지 완료**이지 **서비스 구현·운영 준비 완료**가 아니다.
