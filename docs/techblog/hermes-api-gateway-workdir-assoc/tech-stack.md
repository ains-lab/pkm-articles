# 기술 스택: 관측한 기반과 신규 구현 권고

> 확인: 2026-10-01. 현재 설치 버전과 제안 라이브러리를 구분한다.
> [목차](README.md) · [아키텍처](architecture.md) · [근거](evidence.md)

## 1. 현재 사용 중인 저장소 계층

| 계층 | 확인된 기술/계약 | 의미 |
| --- | --- | --- |
| Wiki 지식 | Markdown, YAML frontmatter, wikilinks | 텍스트 파일이 정식 원장 |
| 원본 | arXiv HTML 또는 PDF + source.json | immutable HTTP 원본 보관 |
| 상태·정책 | JSON 및 JSON Schema | 수집/컴파일/승인·상태를 분리 |
| 동시성 | mkdir 기반 collection.lock | 수집·게시의 공유 경계 |
| 게시 증거 | hash, write-ahead journal, receipt | 중단·충돌·반복 no-op 대조 |
| 변경 이력 | Git + append-only log.md | 코드 이력과 실제 작업 이력 구분 |

현재 Wiki에 별도 DB·벡터 저장소·임베딩 인덱스를 도입하지 않는다. 기존 Hermes 자체 세션 저장소가 SQLite를 사용한다는 사실과 Wiki의 파일 기반 원장 정책은 서로 다른 계층이다. 이번 조사에서 기존 SQLite DB를 열지 않았다.

## 2. 설치 Hermes 런타임

로컬 소스 HEAD: `8d79c2ff57bba4b07e5b37ed90387b16541aef53`.
`pyproject.toml`의 package version은 `0.21.1`, Python 지원 범위는 `>=3.11,<3.14`다. 이는 최신 배포 버전이라는 주장이 아니라 조사한 checkout의 선언이다.

실제 launcher가 사용하는 venv의 package metadata를 조회했다.

| 항목 | 로컬 관측값 | 역할 |
| --- | --- | --- |
| Python | 3.11.15 | 설치 Hermes 실행 interpreter |
| aiohttp | 3.14.3 | API Server HTTP/SSE 어댑터 |
| OpenAI SDK | 2.24.0 | 지원 model/provider 연동 계층 |
| HTTPX | 0.28.1 | HTTP client dependency |
| PyYAML | 6.0.3 | YAML 설정·자료 처리 dependency |
| Pydantic | 2.13.4 | 데이터 검증 dependency |

작업 shell의 `python3`와 Hermes venv의 interpreter는 다를 수 있다. host의 Python 버전으로 Hermes runtime을 추정하지 않는다. dependency metadata 조회는 API Server 기동·provider 정상 여부의 증거가 아니다.

## 3. API Server 내부

- 서버 어댑터: `gateway/platforms/api_server.py`.
- OpenAI 호환 handler: `api_server_openai_routes.py`.
- 구조화 run lifecycle: `api_server_runs.py`.
- Runs 요청 중복 억제: `api_server_run_idempotency.py`.
- 동시성: `asyncio` 기반 HTTP/SSE와 executor에서 실행하는 `AIAgent`.
- 도구: `api_server` platform에 해석된 toolset. platform 모델/도구 설정이 실제 권한에 영향을 준다.

**Gateway API Server 자체는 aiohttp다.** 프로젝트에 FastAPI/Uvicorn 의존성이 존재한다는 이유로 이 어댑터를 FastAPI 서버라고 설명하면 안 된다. dashboard·TUI JSON-RPC·subscription proxy도 이름이 비슷하지만 본 설계의 HTTP API Server와 다른 surface다.

## 4. 신규 frontend/BFF 권고안 — 미설치·미구현

| 영역 | 권고 | 선택 이유 | 주의 |
| --- | --- | --- | --- |
| UI | React + TypeScript | 명시적 상태 모델, 컴포넌트 재사용 | 현재 repo에 구현됐다는 뜻 아님 |
| 웹/BFF 통합 | Next.js의 Node runtime | 같은 origin의 UI와 서버 경계 구성 | Edge runtime의 FS/장기 stream 제약을 가정하지 말고 Node 경로 검증 |
| style | CSS Modules + DESIGN tokens | 작은 서비스에서 낮은 의존성·명시적 스타일 | 대형 UI kit를 초기 필수로 두지 않음 |
| DTO 검증 | Zod 또는 동등 schema validator | browser 입력과 서버 응답 shape 검증 | Wiki JSON Schema를 임의 대체하지 않음 |
| Markdown | react-markdown + remark-gfm + 엄격한 URL/HTML 정책 | 문서·표·코드 표시 | raw HTML 확장은 기본 off; AST 변환도 검증 |
| HTTP/SSE | server fetch + 스트림 parser | custom Runs 이벤트와 ownership 중계 | 브라우저 EventSource만으로 Bearer/POST 모두 해결 불가 |
| UI 시험 | Vitest + Testing Library | reducer·상태·입력 상호작용 | fake stream임을 명시 |
| 통합/브라우저 | Playwright + 접근성 점검 | 실제 auth/stream/viewport 확인 | 실행한 뒤에만 PASS |
| ingress | 기존 Nginx 또는 Caddy | TLS·routing·SSE 전달 | 신규 설치는 승인 대상 |

현재 manifest/lockfile을 새로 만들지 않았다. 제안 package의 구체적 version은 구현 착수 시 지원되는 release와 보안 공지를 확인하고 lockfile로 고정한다. 이 문서의 작성 날짜만으로 “최신 패키지”를 주장하지 않는다.

## 5. 설계상 패키지 책임 분리

향후 별도 웹 앱 repository에서 사용할 수 있는 **개념적 구조**다. 아래 파일은 이번에 생성하지 않았다.

```text
web-app/
  app/                  route와 UI composition
  components/           지식·출처·실행 상태 primitives
  server/auth/          인증·CSRF·owner mapping
  server/wiki/          공개 projection·pageId·snapshot 검증
  server/hermes/        upstream client·SSE parser·run reconciliation
  contracts/            BFF request/response schema
  tests/                합성 unit·실제 integration 분리
```

Wiki repository를 앱 빌드 출력이나 node_modules로 채우지 않는다. 서비스 자체 구현 위치는 별도 요청에서 정한다. `server/wiki`는 read facade이지 수집기·논문 파서·새 지식 원장이 아니다.

## 6. 대안 비교

| 선택지 | 적합한 경우 | 한계/결정 |
| --- | --- | --- |
| 기존 Open WebUI | 소유자가 빠르게 일반 채팅 연결 시험 | Wiki provenance UI는 별도; 설치는 미승인 |
| React SPA + 독립 BFF | UI 정적 hosting과 backend 운영이 분리됨 | 서비스 경계와 auth 배포를 별도로 관리 |
| Next.js + Node BFF | 작은 팀이 UI/API를 함께 유지 | 이 문서의 권고; 확정 아님 |
| FastAPI BFF + React | Python 운영 역량·기존 backend가 있음 | 가능하지만 Hermes API 내부와 혼동 금지 |
| Browser direct → Hermes | 제한된 개발 실험 | key·CORS·ownership·SSE 제약 때문에 기본안으로 채택하지 않음 |

새 Redis/Kafka/PostgreSQL/vector DB는 초기 필수 요소가 아니다. 향후 다중 사용자·수평 확장·내구 BFF event replay가 필요하면 현재 “개인용 파일 Wiki” 경계를 다시 승인받고 설계한다.

## 7. 구현 전에 확인할 호환성

1. 설치 revision과 `/v1/capabilities`의 실제 응답.
2. API Server의 named SSE와 JSON event envelope 차이.
3. BFF가 Node runtime에서 실제 파일·stream 접근을 수행하는지.
4. 인증 provider/쿠키/CSRF와 reverse proxy의 idle timeout.
5. read-only mount가 terminal 및 파일 도구 모두에 적용되는지.
6. model alias와 실제 runtime model/fallback의 차이.
7. Wiki에서 허용한 상태 enum·revision/hash/receipt 연결.

버전·기능 차이를 숨기는 adapter 대신 capability negotiation과 fail-closed 처리를 적용한다. 상세 wire 계약은 [API 문서](api-contract.md)에 있다.
