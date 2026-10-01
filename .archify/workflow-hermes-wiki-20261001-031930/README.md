# Wiki × Hermes — 전체 아키텍처와 워크플로

[브라우저 진입점](index.html) · [원문 목차](../../docs/techblog/hermes-api-gateway-workdir-assoc/README.md)

## 범위와 읽는 순서

기술문서 12개와 `verification.json`을 읽어 구성한 **문서 기반 시각화**다. `slides/`는 기존 파생 강의 자료이므로 원천 근거로 중복 사용하지 않았고 수정하지 않는다. 각 다이어그램은 Archify JSON과 독립 HTML로 보관한다. 실행 중인 시스템을 탐지한 그림이나 웹 앱 구현 결과가 아니다.

| 순서 | 다이어그램 | 핵심 질문 |
|---|---|---|
| 01 | [전체 구조](01-system/diagram.html) · architecture | 브라우저, TLS, BFF, Gateway, 격리 Agent, Wiki, 수집자, 게시자의 책임은 무엇인가? |
| 02 | [작업 경로와 격리](02-workspace/diagram.html) · architecture | cwd는 어떻게 해석되며 왜 sandbox가 아닌가? |
| 03 | [모델 없는 읽기](03-read/diagram.html) · workflow | pageId·권한·receipt/hash·snapshot 충돌을 어떻게 처리하는가? |
| 04 | [통제된 질의](04-query/diagram.html) · workflow | Runs, 단일 SSE 구독, 재연결, stop을 어떻게 분리하는가? |
| 05 | [원문 수집](05-collection/diagram.html) · workflow | HTML 우선, PDF fallback, 중복·오류·보관 완료의 경계는 무엇인가? |
| 06 | [컴파일과 게시](06-publication/diagram.html) · workflow | 승인·원문 읽기·근거 검토·lock·WAL·committed 검증은 어떻게 연결되는가? |
| 07 | [데이터와 화면](07-data-ui/diagram.html) · architecture | 파일 원장·DTO·화면과 여섯 상태 축은 어떻게 연결되는가? |
| 08 | [구현 로드맵](08-roadmap/diagram.html) · workflow | R0–R4의 선행 조건과 구현·운영 검증은 무엇인가? |

## 가장 중요한 구분

- **기존 기반:** 원본 HTML/PDF와 서지 JSON, 지식 Markdown, 상태·정책 JSON, collection.lock, journal/receipt. 수집 Cron은 collect-only다.
- **원문이 보고한 소스 관측:** Hermes API Server는 aiohttp이며 조사 기준 revision은 `8d79c2ff57bba4b07e5b37ed90387b16541aef53`다. 이번 시각화에서 설치 소스를 다시 전수 감사하거나 live API를 호출하지 않았다.
- **제안·미구현:** frontend/BFF/read facade, React·TypeScript·Next.js Node runtime, 서버측 소유권 관리, 별도 격리 실행 환경, 화면·배포 구조.
- **별도 승인 대상:** 실제 Gateway 설정·enable/bind·재시작, 질의 backend와 자료 전송, 새 원문 컴파일·게시·자동화. 다이어그램의 화살표는 실행 권한을 부여하지 않는다.

## API 표면과 식별자

| 표면 | 입력·대화 식별 | 주의 |
|---|---|---|
| Chat Completions | `messages`, `stream`; transcript는 `X-Hermes-Session-Id` | body의 `session_id`·`conversation_id`를 이 handler의 session 선택 필드로 대체하지 않는다. `X-Hermes-Session-Key`는 메모리 scope다. |
| Responses | `input`, `instructions`, `previous_response_id` 또는 `conversation` | `conversation_id`가 아니다. chain과 conversation 동시 지정 금지. |
| Runs | `input`, body `session_id`, `conversation_history`, `previous_response_id` | `202 / started`는 접수. 상태·결과·partial/interrupted/error를 별도 확인한다. |
| 제안 BFF | `/api/wiki/*`, `/api/agent/*`의 개별 method/path 허용 | 실제 구현된 endpoint가 아니다. wildcard proxy·관리 jobs/session 전체 공개 금지. |

근거: `api-contract.md:13–34,36–84,120–137`.

- Runs는 `data:` JSON 내부 `event`로 분기한다. Chat named event·Responses event family와 혼합하지 않는다. comment·CRLF·multi-line data·UTF-8/JSON chunk 분할을 처리한다.
- 원문 조사판 `/events`는 단일 queue 소비·연결 종료 시 transport 삭제다. BFF는 upstream 한 개를 구독하고 자체 fan-out한다. 끊기거나 events가 404면 `GET /v1/runs/{id}`로 조정한다. 무손실 replay나 `Last-Event-ID` 복구를 가정하지 않는다.
- `Idempotency-Key`는 같은 body의 전송 재시도다. 다른 body는 409이며 새로운 질문에는 새 key가 필요하다. Runs의 보존·memory fallback과 Chat/Responses의 300초 캐시는 다른 계약이다.
- `AbortController.abort()`는 연결 취소, `/stop`의 `stopping`은 접수다. `cancelled` 또는 완료 경합의 `completed` 등을 관측해야 하며 외부 효과는 자동 rollback되지 않는다.
- `/steer` 200은 큐 접수이지 agent 소비 완료가 아니다. 도구 승인과 Wiki 단계·자료·게시 승인은 별개다.
- `model:"hermes-agent"` alias 또는 응답 echo는 실제 실행 모델의 증거가 아니다. 모델 지정만으로 no-fallback이 보장되지 않는다.

근거: `api-contract.md:86–118`, `workflows.md:25–95`, `evidence.md:67–80`.

## 여섯 개의 독립 상태 축

| 축 | 의미 | 금지되는 등치 |
|---|---|---|
| 원문 확보 | HTML/PDF 보관·미확보 | 저장 성공 ≠ 의미 분석 |
| HTML 제공 | 제공·공식 미제공·일시 오류 | HTML 미제공 ≠ 원문 미확보 |
| 컴파일 | 승인 대기·reading·partial·published_draft | 모델 종료 ≠ 게시 |
| 게시 거래 | 미해결·committed | 상태 문자열 ≠ 실물 hash 검증 |
| 인간 검토 | unreviewed·human_reviewed | 자동 검사 ≠ 인간 검토 |
| API 실행 | running·completed·failed 등 | API completed ≠ Wiki 게시·논문 검토 |

근거: `data-contracts.md:28–67`. `source.json`의 `wiki_compiled:false`는 수집 당시 불변 이력이다. 이후 완료는 ledger, committed receipt, 실제 output hash로 확인한다.

## 원문 snapshot과 현재 상태를 혼합하지 않기

원문 README는 2026-10-01 01:43:55 UTC 기준점(원문 20편·지식 문서 6개·컴파일 published_draft 2개)과 작업 중 관측한 v3/queued 전이를 역사적으로 보존한다. `verification.json`의 옛 경로·hash도 이동 당시 설명과 함께 보존된다. **이 값들을 현재 live 상태로 재표시하지 않는다.** 이번에는 문서의 현재 바이트 hash만 별도 고정했다.

`source-baseline.json`은 기술문서 및 기존 슬라이드 파일의 작업 전 hash다. `source-coverage.json`은 원문 각 절과 시각화/이 안내의 대응표다. 각 폴더의 `evidence.json`은 의미별 문서 줄 인용이다. untracked 문서를 Git HEAD에 커밋된 구현 근거로 표시하지 않았으며, Archify `meta.repository` 검증을 수행한 것처럼 주장하지 않는다.

## 보안·자료·게시 불변 조건

- Wiki는 static document root가 아니다. pageId 허용 목록·경로 검증·safe open·read-only OS 권한을 함께 집행해야 한다. realpath 한 번으로 TOCTOU를 해결하지 않는다.
- Gateway key는 서버측에만 둔다. 쿠키/CSRF, run/session owner, 제한된 API, mount 및 egress가 각각 필요하다. cwd·AGENTS·프로필만으로 접근 격리가 생기지 않는다.
- raw HTML은 app origin에서 실행하지 않는다. Markdown raw HTML 비활성·URL scheme 제한·코드 escape가 필요하다. PDF preview 명목의 추출/OCR/렌더링도 금지된다.
- 수집은 원본 보관만 한다. 공식 HTML 미제공 때만 동일 버전 PDF fallback; 403/429/5xx/timeout은 fallback 사유가 아니다. 완료 버전의 형식 교체·추가 수집을 자동 수행하지 않는다.
- 승인된 수동 v3 PDF 경로만 표준 pypdf로 로컬 내장 텍스트를 메모리에서 읽는다. PDF 바이너리·이미지·OCR·지속 추출본은 허용되지 않는다. 이 예외가 웹 자유 질의에 승계되지 않는다.
- 컴파일 모델 계약은 `codex-lb / gpt-6-astra / xhigh`, fallback 금지다. `no_cost_cap`, 미관측 비용 `null`이며 비용 계측은 gate가 아니다. 자료·모델·단계·무결성·유한 재시도는 gate다.
- 게시자는 collection.lock, 수집 우선 시간, 최종 hash, WAL, 조건부 복구를 따른다. 다중 파일 쓰기를 OS 수준 단일 원자 거래로 설명하지 않는다. 사용자 수정과 unresolved 거래를 보존한다.

근거: `security-and-operations.md:6–103`, `workflows.md:97–122`, `implementation-roadmap.md:72–87`.

## 화면·기술 스택·운영 인계

제안 화면은 `/library`, `/knowledge/:pageId`, `/topics`, 승인 후 `/chat/:conversationId`, 소유자용 `/operations`다. operations는 정형 조회이지 Cron 편집 화면이 아니다. UI의 accepted/disconnected/reconciling은 로컬 상태이며 Gateway status와 혼합하지 않는다.

DESIGN의 Civic Navy·sans·문자 동반 상태 배지·revision/review/source 헤더를 인계 기준으로 보존한다. 키보드/focus 복귀/한국어 IME/긴 ID/스크린리더/reduced-motion과 화면별 loading·empty·error·partial 상태는 후속 앱 검증 대상이다. 원문의 375/768/1280/1440px 기준과 LCP/INP/CLS 목표는 **실제 앱 측정 결과가 아니다**. 이 패키지의 Archify HTML 브라우저 검사는 그 미래 앱의 QA를 대신하지 않는다.

운영 로그는 필요한 request/run/정책/revision/hash 위주로 제한한다. credential·원문·전체 대화·raw tool output·비공개 추론을 자동 보관하지 않는다. 앱 rollback과 Wiki 원본/이력 rollback은 별개다. liveness 성공만으로 인증·모델·도구·게시 정상까지 선언하지 않는다.

## 사용과 검증 근거

1. `index.html`을 브라우저에서 열고 원하는 주제의 HTML로 이동한다.
2. 각 HTML은 CSS·JavaScript·SVG가 포함된 독립 파일이다. 내용은 모두 한국어다. 01–06의 내장 Viewer 조작 UI와 `<html lang>`은 영문 fallback, 07–08은 한국어다. 모션은 기본 정지다.
3. 수정 가능한 원본은 각 `candidate.json`이다. HTML을 직접 고치면 provenance가 무효화된다.
4. 각 `diagram.finalize-summary.json`과 `diagram.delivery.json`, 실제 artifact에 결합된 browser receipt를 확인한다. **08의 최종 통과 receipt는 `08-roadmap/repair-5/`에 있다.** 루트의 초기 실패 기록을 최종 결과로 혼동하지 않는다. 전체 경로·명세/HTML hash는 `artifact-receipts.json`에 모았다.
5. 전체 최종 결과는 `verification.json`에 기록한다. 자동 검사, 캡처, 화면 표본 검토, 접근성 감사를 서로 구분한다.

### 데스크톱 권장과 검증 한계

- 8개 모두 showcase 9/9, 오류·경고 0 및 validate/deliver/strict check/browser-check를 통과했다. 자동 브라우저 기준은 1440×900, 1600×1000, 1920×1080, 2048×1320이다. 긴 도식은 선언된 Reader의 세로 페이지 스크롤을 사용한다.
- **도식은 데스크톱에서 읽는 것을 권장한다.** 375px에서 목차는 정상 배치지만 01·02·07은 일부 도식 텍스트가 화면 오른쪽 밖에 있다. 다른 도식의 가로 경계 안 배치 역시 모바일 글자 가독성·접근성 통과를 뜻하지 않는다. 캔버스 이동·확대나 노드 검색은 보조 탐색 수단이지 모바일 최적화 증거가 아니다.
- 8개 도식의 대표 데스크톱 캡처를 이미지 도구로 검토했다. 해당 첫 화면에서 노드·라벨의 명백한 겹침/내부 잘림은 관찰되지 않았지만, 작은 보조 글씨·낮은 대비와 복잡한 분기/우회선은 제한으로 남는다. 아래로 이어지는 모든 카드·모든 테마·모든 UI 상태의 시각 전수 검토는 아니다.
- 1440px/375px에서 8개 모두 노드 검색 입력과 Escape 닫기·검색 버튼으로의 포커스 복귀를 확인했다. 01·02는 `Wiki` 일치 검색, 03–08은 검색 결과 없음 상태를 확인했다. 테마 전환·모바일 카메라 검사는 기록된 일부 도식에 한정한다. Export·전체 키보드 순서·스크린리더·전체 console/network 감사·실제 웹 앱 접근성은 검증하지 않았다.
- 전체 모바일 시각 QA/접근성 PASS를 선언하지 않는다. 자동 데스크톱 검사 PASS와 이 제한을 함께 전달한다.

검증 환경: 기존 Chromium을 명시하고, 해당 호스트의 user namespace sandbox 오류 때문에 Archify가 제공하는 `ARCHIFY_CHROME_NO_SANDBOX=1`을 **자체 생성 로컬 HTML 검증 프로세스에만** 사용한다. 전역 브라우저/Gateway 설정이나 Archify 소스는 수정하지 않는다. 자동 browser-check와 사람이/이미지 모델이 본 시각 검토는 서로 다른 결과다.

이 작업은 문서 시각화다. 웹 서비스 구축, live API·모델 실행, 논문 원문 처리, 지식 게시, 설정·Cron 변경, 의존성 설치, commit/push를 수행하지 않는다.
