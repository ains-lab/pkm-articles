# API 계약: Hermes 기존 API와 Wiki BFF 제안

> 기준: 공식 문서 + 로컬 Hermes `8d79c2ff57bba4b07e5b37ed90387b16541aef53` 정적 조사.
> live HTTP 요청은 실행하지 않았다. [근거·버전 차이](evidence.md) · [목차](README.md)

## 1. 두 API 영역

- **기존 Hermes:** 내부 base 예시 `http://127.0.0.1:8642`. 인증은 `Authorization` 헤더의 Bearer 방식이며 실제 키는 서버측에만 보관한다.
- **제안 BFF:** 사용자 인증·자료 projection·session/run ownership을 담당하는 same-origin `/api/wiki/*`, `/api/agent/*`. 아직 구현된 endpoint가 아니다.

브라우저가 보낸 path/body/header를 그대로 Hermes로 넘기는 wildcard proxy는 만들지 않는다.

## 2. 기존 Hermes의 주요 endpoint

| Method·path | 기능 | BFF 취급 권고 |
| --- | --- | --- |
| `GET /health`, `/v1/health` | 가벼운 liveness | 운영자만 upstream 확인 |
| `GET /health/detailed` | 인증 readiness | 필요한 상태만 projection |
| `GET /v1/models` | 안정적인 모델 alias 목록 | 전체 provider catalog와 구분 |
| `GET /v1/capabilities` | run/session/stream 기능 탐색 | 시작 시 지원 기능 확인 |
| `POST /v1/chat/completions` | OpenAI 형식 채팅 | 범용 client adapter |
| `POST /v1/responses` | 서버측 response chain | 저장·이력 정책 검토 후 |
| `GET /v1/responses/{id}` | 저장 응답 조회 | owner 확인 필수 |
| `DELETE /v1/responses/{id}` | 저장 응답 삭제 | 초기 BFF에서 차단 |
| `POST /v1/runs` | 비동기 작업 접수, 202 | custom UI 우선 검토 |
| `GET /v1/runs/{id}` | 현재 상태·결과 | owner 확인 후 전달 |
| `GET /v1/runs/{id}/events` | SSE 진행 이벤트 | BFF 단일 upstream 구독 |
| `POST /v1/runs/{id}/stop` | 중지 요청 | 접수와 종료 구분 |
| `POST /v1/runs/{id}/approval` | 대기 중인 도구 승인 결정 | 별도 관리자 scope |
| `POST /v1/runs/{id}/steer` | 실행 중 지시 큐 등록 | 선택 기능; running만 |
| `/api/sessions/*` | 세션·이력·fork·chat 등 | 전체 관리 surface 공개 금지 |
| `/api/jobs/*` | Cron CRUD/pause/resume/run | 초기 BFF 차단 |

`/api/model/options`, `/v1/skills`, `/v1/toolsets`도 존재한다. browser-control/artifact/room ingress 같은 별도 기능을 일반 파일 업로드·Wiki API로 확대하지 않는다.

## 3. Chat Completions 계약

다음 JSON은 **요청 예시이며 미전송**이다.

```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "user", "content": "기존 Wiki의 검토 상태를 설명해 주세요."}
  ],
  "stream": true
}
```

- `messages`는 비어 있지 않은 배열, `stream` 기본 false.
- system 메시지는 Hermes core prompt에 추가된다. 도구를 자동 제거하지 않는다.
- 일반적으로 client가 user/assistant 이력을 보낸다. 현재 구현은 임의 developer/tool role·클라이언트 tool-call 이력을 완전한 OpenAI proxy처럼 보존하지 않는다.
- 서버측 transcript를 계속할 때는 **`X-Hermes-Session-Id`**를 사용한다. 이 경우 과거 이력은 서버에서 읽고 마지막 입력은 body에서 취한다.
- body의 `session_id`, `conversation_id`, `user`를 이 handler의 session 선택이나 ACL 필드로 사용하지 않는다.
- 헤더가 없으면 첫 user content와 system prompt에서 session 식별자를 파생한다. 별도 대화의 시작 문장이 같을 수 있으므로 “완전히 무상태이고 충돌 없음”이라고 가정하지 않는다.
- `X-Hermes-Session-Key`는 장기 기억 scope이며 transcript ID·인증 identity와 별개다.

`model:"hermes-agent"`는 별칭이다. OpenAI 경로의 provider 없는 bare model은 기본적으로 실행 모델 선택에 반영되지 않을 수 있다. session override, model_routes, direct_model_requests, provider 옵션의 우선순위를 확인해야 한다. 응답의 model echo만으로 실제 모델을 검증하지 않는다.

## 4. Responses와 Runs

| 경로 | 입력/이력 필드 | 주의 |
| --- | --- | --- |
| Responses | `input`, `instructions`, `stream`, `store`, `previous_response_id` 또는 `conversation` | `conversation_id` 아님; chain+conversation 동시 지정 금지 |
| Runs | `input`, `instructions`, body `session_id`, `conversation_history`, `previous_response_id` | Chat의 messages/stream shape가 아님 |

Runs 예시 — placeholder를 실제 BFF 소유 ID로 바꿔야 한다:

```json
{
  "input": "허용된 기존 지식 페이지를 근거로 질문에 답해 주세요.",
  "session_id": "<BFF가 소유권을 관리하는 세션 ID>"
}
```

접수 응답은 202와 run ID다. 예시 shape는 다음과 같으며 실제 실행 결과가 아니다.

```json
{"run_id":"run_<example>","status":"started","replayed":false}
```

polling에서 queued/running/waiting_for_approval/stopping 및 completed/failed/cancelled/interrupted를 처리한다. `started` 접수 응답을 최종 성공으로 해석하지 않는다. 결과·partial/interrupted/error flags도 확인한다.

요청의 model/provider/model_options는 지원하지만 **model 지정만으로 fallback 금지를 보장하지 않는다.** 현재 AIAgent 생성 경로는 confirmed runtime lock이 아니면 fallback chain을 전달할 수 있다. Wiki 컴파일의 고정 모델·no-fallback 계약은 별도 집행·실제 runtime 검증이 필요하다.

## 5. SSE wire format

| surface | 분기 기준 | 종료·주의 |
| --- | --- | --- |
| Chat | `data:` JSON의 chat.completion.chunk + named `event: hermes.tool.progress` | `[DONE]`, finish flags/usage 확인 |
| Responses | `response.*` event family | 이미 실행된 function_call/output을 client가 재실행하지 않음 |
| Runs | `data:` JSON 내부 **`event` 필드** | run.completed/failed/cancelled/interrupted 등 |

Runs 프레임 모양을 설명하는 축약 예시:

```text
data: {"event":"message.delta","run_id":"run_<example>","delta":"..."}

: keepalive

```

위 예시는 event 분기 위치 설명용이며 개별 event의 모든 필드를 고정하는 schema가 아니다. SSE parser는 blank line으로 프레임을 구분하고 comment, CRLF, multi-line data, UTF-8/JSON chunk 분할, unknown event를 처리한다.

**설치 버전의 중요한 제약:** Runs `/events`는 하나의 queue를 소비하고 종료 시 transport를 삭제한다. 이벤트 ID 기반 replay가 없으며 복수 upstream 구독자는 같은 queue를 나눠 소비할 수 있다. 재접속 endpoint가 404여도 작업은 계속될 수 있다. 따라서 BFF의 단일 구독 + 자체 fan-out + `GET /v1/runs/{id}` reconciliation을 권고한다. 장기 replay가 필요하면 별도 승인된 BFF 계약이 필요하다.

공식 live 문서는 keepalive 10초를 설명하지만 조사한 로컬 Runs 코드는 30초 timeout을 쓴다. reverse proxy timeout은 문서 숫자만 믿지 말고 실제 설치 버전으로 시험한다.

## 6. 재시도·오류·취소

- Runs `Idempotency-Key`: visible ASCII 1–255자. 같은 key+payload는 원 run의 202 replay, 다른 payload면 409. profile/credential scope와 session-key fingerprint가 적용된다.
- Runs store의 terminal 보존 기본은 24시간. DB 실패 시 in-memory fallback이 있으므로 capability의 durable 여부를 확인한다. replay는 실행 재개나 SSE replay가 아니다.
- Chat/Responses 비stream의 300초 캐시는 별도 구현이다. Runs와 같은 tenant-scoped durable 계약으로 간주하지 않는다. BFF는 재시도에 Runs를 우선 검토한다.
- 대표 HTTP 상태: 잘못된 입력 400, 인증 401, origin 거부 403, 미존재 404, 충돌 409, body 과다 413, 동시성 429, drain 503. endpoint별 envelope 차이를 정규화해야 한다.
- HTTP 200만으로 agent 성공을 판단하지 않는다. stream은 헤더 이후 실패할 수 있고 partial/인증 오류 텍스트를 반환하는 경로도 있다.
- `/stop`은 stopping을 반환한다. 실행이 중단을 인정한 뒤 cancelled가 되며 이미 완료한 결과와 경합하면 completed일 수 있다.
- `/steer`의 200은 큐 접수다. agent가 실제 소비했다는 뜻이 아니며 pending_steer 등 미소비 표시를 처리한다.
- `/approval`은 `choice`와 선택적 `request_id`를 받는다. 서버가 제공한 pending choices만 보여주고 allow-always 자동 선택은 하지 않는다.

## 7. 제안 BFF API — 모두 미구현

| Method·path | 계약 초안 | 인증/부수 효과 |
| --- | --- | --- |
| `GET /api/wiki/pages?type=...&cursor=...` | 공개 페이지 목록·다음 cursor | 인증, 읽기 전용 |
| `GET /api/wiki/pages/{pageId}` | revision/hash/본문/출처 DTO | page ACL, 읽기 전용 |
| `GET /api/wiki/sources?cursor=...` | 승인된 서지·보관/컴파일 상태 | 원본 내용 제외 |
| `GET /api/wiki/status` | 축약된 관측 상태·시각 | 소유자 전용 |
| `POST /api/agent/runs` | 질문·선택 pageId·client request ID | 실행 정책 승인 후만 |
| `GET /api/agent/runs/{id}` | normalized run status | owner 확인 |
| `GET /api/agent/runs/{id}/events` | BFF가 중계하는 이벤트 | owner 확인; 별도 replay 보장 없음 |
| `POST /api/agent/runs/{id}/stop` | 중지 요청과 현 상태 | owner·CSRF 확인 |

page DTO는 [데이터 계약](data-contracts.md)을 따른다. raw path, model/provider, tools, instructions, profile prefix, session ID를 client가 무제한 선택하도록 하지 않는다. compile/publish/Cron CRUD endpoint는 초기 설계에 없다.

## 8. 브라우저 직접 연동을 기본안으로 쓰지 않는 이유

키 노출·사용자별 ACL 외에도 로컬 CORS 구현에는 PATCH, Session-Key 허용 header, expose-header와 Runs SSE prepare 시점 관련 제약이 보인다. 이는 **정적 위험 발견**이며 브라우저 재현 시험은 하지 않았다. 임의 CORS wildcard를 열어 해결하지 말고 same-origin BFF 및 실제 통합 시험으로 검증한다.

API와 Wiki 정책이 맞닿는 지점은 [워크플로](workflows.md), 실행·검증 단계는 [로드맵](implementation-roadmap.md)에서 확인한다.
