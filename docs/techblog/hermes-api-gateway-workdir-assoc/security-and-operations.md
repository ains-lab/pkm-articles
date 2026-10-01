# 보안·운영: 외부 frontend와 개인 Wiki 사이의 경계

> 상태: 배포 전 설계·점검 기준. 방화벽/TLS/인증/서버 시작은 적용하지 않음.
> [목차](README.md) · [아키텍처](architecture.md) · [설정 절차](workspace-and-gateway.md)

## 1. 위협 모델

보호 대상은 개인 Wiki, Hermes가 접근 가능한 host 파일, 모델·도구 자격증명, 사용자 대화, 승인·실행 이력이다. 입력은 사용자 질문, 논문/Markdown 본문, 외부 URL, 브라우저 요청 모두 비신뢰로 취급한다.

최소 위협은 다음과 같다.

| 위협 | 필수 통제 제안 | 통제의 한계 |
| --- | --- | --- |
| Gateway key 탈취 | 서버측 보관, TLS, 로그/번들에서 제외 | key 하나가 세부 사용자 권한을 대신하지 않음 |
| 다른 사용자의 run/session 추측 | BFF의 owner mapping 및 요청마다 ACL | profile 분리만으로 OS 접근 격리 안 됨 |
| prompt injection | 도구·자료 allowlist, OS/컨테이너 격리, 승인 | AGENTS나 system prompt만으로 차단 불가 |
| 경로 이탈·symlink | pageId 매핑, no-follow, root 검증, read-only mount | realpath 한 번 검사만으로 TOCTOU 해결 안 됨 |
| HTML/Markdown XSS | raw HTML 비활성, URL scheme 제한, sanitize/CSP | 원본 파일 자체를 변환·덮어쓰지 않음 |
| SSRF·외부 자료 전송 | URL 입력 차단/allowlist, egress 통제 | API 자체 지원 기능을 정책 허용으로 오해 금지 |
| 잘못된 완료 표시 | receipt/hash/상태를 분리해서 검증 | HTTP 200·LLM “완료”가 게시 증거 아님 |
| 동시 게시·사용자 수정 손상 | shared lock, final hash, journal, 조건부 복구 | 오래된 snapshot 전체 rollback 금지 |

## 2. 인증·인가

### 브라우저와 BFF

인증 방식은 기존 조직/개인 운영 환경에 맞춰 결정해야 한다. 초안은 서버 세션을 사용하는 authenticated single-owner 서비스다. cookie를 쓰면 HttpOnly/Secure/SameSite, 변경 요청의 CSRF 토큰·Origin 검사, 만료·재인증을 구현한다. public signup은 제공하지 않는다.

### BFF와 Hermes

`API_SERVER_KEY`는 서버 간 credential이다. `NEXT_PUBLIC_*`, localStorage, URL query, 프런트엔드 번들, example 파일의 실제 값, 브라우저 콘솔에 두지 않는다. 문서에는 키 이름만 기록한다.

`/v1/runs`, 상태, events, stop, approval은 모두 BFF owner 검사를 거친다. 인증된 frontend 사용자가 존재한다는 사실만으로 default 프로필의 모든 session을 열람하게 하지 않는다. `X-Hermes-Session-Id`와 메모리 scope key는 클라이언트 임의값을 신뢰하지 않고 서버가 관리한다.

Hermes에 jobs/session/config 계열 API가 있다는 이유로 그 전체를 reverse proxy하지 않는다. UI에 필요한 method+path를 개별 허용하고 나머지는 거부한다. `/p/<profile>/...` prefix도 사용자 입력대로 중계하지 않는다.

## 3. 도구와 파일시스템 격리

`terminal.cwd`와 `MESSAGING_CWD`는 기본 작업 위치이지 chroot/ACL/sandbox가 아니다. 모델에게 “읽기 전용”이라고 지시하는 것과 실제 파일시스템이 쓰기를 거부하는 것은 다르다.

권고 배포 경계:

- UI/BFF는 공개 승인된 지식·서지 projection만 읽는다.
- 질의용 에이전트는 관리자가 승인한 별도 격리 환경에서 실행한다.
- host home 전체, credential directory, SSH key, 다른 Wiki, Docker socket은 노출하지 않는다.
- 보호 경로는 read-only mount/OS 권한으로 막는다. terminal뿐 아니라 모든 파일 도구가 실제 어느 환경에서 동작하는지 검증한다.
- 필요 없는 write/terminal/MCP/browser/cron/delegation 기능은 제한한다. 이름이 read_file이어도 PDF 문서 추출을 할 수 있으므로 **도구 허용과 자료 형식 허용을 함께** 검증한다.
- container 배치만으로 네트워크 egress·모델 전송·환경변수 비밀 노출이 해결되었다고 주장하지 않는다.

기존 default 프로필과 다른 프로필의 설정은 이번 작업에서 변경하지 않았다. 새 프로필·별도 process/container 생성도 별도 승인 후 수행한다.

## 4. 원문 표시

- raw HTML은 원형을 보존한다. sanitizing을 이유로 `source.html`을 덮어쓰지 않는다.
- 웹 앱과 같은 origin에서 raw HTML을 그대로 실행하지 않는다.
- MVP는 공식 버전 고정 arXiv 링크를 제공한다. 링크를 여는 것은 도표 검토 완료가 아니다.
- raw 파일 download/별도 origin 제공은 공개 범위 승인·헤더/CSP/권한 시험을 거친 별도 기능이다.
- PDF preview를 위해 서버측 text extraction·OCR·page rendering을 추가하지 않는다.
- 웹 MVP는 이미지/외부 자산·PDF 내용을 모델에 보내지 않는다. v3의 별도 수동 컴파일 승인은 로컬 PDF 내장 텍스트만 예외적으로 허용하며 바이너리·이미지·OCR·지속 추출본은 계속 금지한다. 이 예외를 웹 자유 질의 권한으로 확대하지 않는다.

## 5. 전송·프록시

BFF와 Gateway가 같은 host일 때 loopback을 우선한다. 다른 host면 private routing과 엄격한 ingress를 설계한다. HTTP API를 그대로 0.0.0.0에 노출하는 것을 기본 절차로 두지 않는다.

SSE relay의 요구사항:

- 응답은 `text/event-stream`, 변환·캐시·buffering 없이 순차 전달한다.
- proxy/LB idle timeout은 실제 keepalive 간격과 장시간 도구 실행을 반영해 검증한다.
- browser 단절과 서버 작업 중지를 분리한다.
- 오류 뒤 재실행 여부를 결정할 때 기존 run 상태와 idempotency를 확인한다.
- cookie 기반 BFF SSE도 ownership 검사한다. token을 query string에 넣지 않는다.
- CORS는 브라우저 cross-origin 정책이며 인증이나 firewall의 대체가 아니다. BFF server-to-server 경로는 Gateway CORS를 열 필요가 없다.

## 6. 관측과 로그

제안 최소 이벤트: request ID, BFF의 익명화된 주체 식별자, run ID, 정책 결과, 시작/종료 시각, endpoint, HTTP status, 실제 run status, model route 검증 결과, 허용된 문서 revision/hash.

기본 제외: Authorization/cookie, 질문·대화 원문, 원본 HTML/PDF, raw tool arguments/output, 비공개 추론, 세션의 전체 환경. 디버깅 시에도 redact 후 최소 범위를 별도 승인하여 수집한다.

비용·사용량은 선택적 관측이다. Wiki 후속 지식화의 `no_cost_cap`을 유지하며 비용 미관측은 null이다. 동시성 제한·네트워크 남용 방지·승인 경계는 비용 상한과 다른 통제다.

## 7. 장애 대응 표

| 관측 신호 | 먼저 확인 | 금지되는 대응 |
| --- | --- | --- |
| `/health` 성공, 질의 실패 | capability/readiness/auth/model/tool별 상태 | liveness만으로 서비스 전체 정상 선언 |
| 401 | BFF credential의 배포·profile binding | 로그나 채팅에 실제 키 출력 |
| 403/정책 거부 | 앱 ACL·자료/작업 허용 범위 | 프롬프트 변경으로 정책 우회 |
| 429 | 동시 실행 수·재시도 조건 | 무한 즉시 retry |
| 409 | idempotency body 차이·run 상태 경합 | 같은 key로 다른 요청 강제 |
| SSE 단절 | GET run status·proxy buffering·timeout | 무조건 새 run 생성 |
| stopping 장기 유지 | 실제 executor 종료·도구 상태 | 종료 확인 전 cancelled로 숨김 |
| interrupted | Gateway shutdown/restart 이력 | 성공으로 승격·외부 효과 자동 재실행 |
| Wiki snapshot 충돌 | committed receipt·해시·잠금 | partial 데이터를 최신 완료본으로 캐시 |
| collection.lock 존재 | 기존 owner와 운영 계약 | 오래됐다는 이유로 자동 삭제 |

## 8. 배포·복구 원칙

새 frontend release를 rollback하는 것과 Wiki 원본/상태를 rollback하는 것은 다른 작업이다. 앱 배포 rollback이 `raw/`나 `log.md`를 과거 snapshot으로 되돌려서는 안 된다.

필수 운영 확인: secret provisioning 경로, 인증 만료, allowlist, live model route, 네트워크 경계, 실제 mount 권한, 스트림 단절·중지, health/readiness, 로그 비밀값 누락, page snapshot 일관성. 동작 시험 전에는 운영 준비 완료를 선언하지 않는다.

새 설치·동기화·외부 알림·backup 복원·Cron 변경은 이 설계의 부수 작업으로 수행하지 않는다. 승인 후 단계는 [구현 로드맵](implementation-roadmap.md)에 있다.
