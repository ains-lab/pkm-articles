# Wiki 작업 경로와 Hermes Gateway 설정

> 확인: 2026-10-01 · 실제 설정 변경 없음.
> 사용자 결정: 현재 Wiki 경로를 문서에 지정하고 live Gateway는 유지한다.
> [목차](README.md) · [보안·운영](security-and-operations.md) · [근거](evidence.md)

## 1. 경로의 의미

이 설계에서 지정할 **Wiki 작업 루트**는 다음과 같다.

```text
/home/ainsdev/wiki/pkm-articles
```

설정 개념은 `terminal.cwd`다. Hermes 설치 디렉터리를 Wiki로 옮기거나, Wiki를 web document root로 설정하는 작업이 아니다.

| 위치/설정 | 의미 | 이번 처리 |
| --- | --- | --- |
| `/home/ainsdev/wiki/pkm-articles` | 논문 Wiki와 이 기술문서의 root | 유지 |
| `/home/ainsdev/.hermes/hermes-agent` | 설치된 Hermes 소스/런타임 | 읽기 전용 조사 |
| 기본 프로필 설정 | terminal/API/runtime 설정 | 허용된 비밀 아닌 leaf key만 CLI 조회 |
| `terminal.cwd` | 도구의 기본 작업 기준 경로 | 현재 `.`; 변경하지 않음 |
| `WIKI_PATH` | llm-wiki 등의 저장소 탐색 관례 | API Gateway cwd 지정 API가 아님 |
| `MESSAGING_CWD` | 메시징 Gateway의 legacy fallback | 신규 설정의 주 경로로 사용하지 않음 |

## 2. 현재 관측과 한계

실제 실행한 읽기 전용 조회:

```bash
hermes config get terminal.cwd
hermes config get terminal.backend
hermes gateway --help
hermes gateway run --help
```

관측값은 `terminal.cwd=.` / `terminal.backend=local`이다. `api_server.*`, `gateway.platforms.api_server.*`, `gateway.api_server.enabled/host/port`, `platforms.api_server.enabled`의 조사한 키는 미설정으로 반환되었다. `.env`, 인증 파일, 서비스 환경 전체, 다른 프로필 설정은 열람하지 않았다.

따라서 **API Server가 꺼져 있다고 결론 내리지 않는다.** 환경변수·다른 지원 설정 위치·이미 실행 중인 프로세스에 별도 값이 있을 수 있다. 이번에는 live health·port·서비스 상태를 조회하거나 모델을 호출하지 않았다.

현재 도구 프로세스에서 `MESSAGING_CWD`와 `WIKI_PATH`는 미설정이었다. 이 관측을 별도 실행 중인 Gateway 서비스 환경의 값으로 일반화하지 않는다.

## 3. cwd 해석

로컬 단일 Gateway의 소스에서 확인한 동작:

1. 명시적 `terminal.cwd`를 런타임 `TERMINAL_CWD`에 전달한다. 이 terminal 설정 bridge에서는 config가 우선한다.
2. `.`, `auto`, `cwd`는 명시적 프로젝트 절대경로가 아니라 placeholder로 처리한다.
3. 명시적 cwd가 없는 local backend는 legacy `MESSAGING_CWD`, 없으면 사용자 home을 사용한다.
4. 비로컬 backend는 container/remote 경로와 mount 정책을 함께 해석한다. 호스트 경로를 그대로 넣어 container에서 접근 가능해지는 것은 아니다.
5. 명령별 `workdir`와 세션이 기억한 cwd는 기본 cwd보다 우선할 수 있다.

따라서 `cd /home/ainsdev/wiki/pkm-articles` 후 Gateway를 시작했다는 사실만으로 Wiki 고정 적용을 증명할 수 없다. 현재 CLI의 `.`와 장기 Gateway의 `.`도 같은 효과로 가정하지 않는다.

근거: Hermes `gateway/run.py:1892–1942,2071–2087`, `gateway/cwd_placeholder.py`, [공식 configuration의 Working Directory](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#working-directory).

## 4. 지원하지 않는 것으로 취급할 설정 방식

조사한 HTTP handler에는 요청별 `cwd`, `workdir`, `workspace_root`를 받아 작업 루트로 적용하는 공개 계약이 없다. API payload에 그런 필드를 넣고 반영됐다고 표시하지 않는다.

`gateway.platforms.api_server.cwd` 역시 확인된 설정 계약이 아니다. config CLI는 알 수 없는 키를 저장할 수 있으므로 `set` 성공이 기능 지원의 증거가 아니다. 정확한 leaf key와 실행 경로를 먼저 확인해야 한다.

`/p/<profile>/...`는 multiplex 프로필 라우팅이며 arbitrary directory selection이 아니다. session ID나 conversation ID도 cwd/파일 권한을 선택하는 토큰이 아니다.

## 5. 승인 후 적용할 절차 — 이번에는 실행하지 않음

아래는 **기본 프로필 변경을 별도 승인했을 때**의 예시다. default를 바꾸면 API 전용이 아니라 해당 프로필의 다른 세션/플랫폼에도 영향을 줄 수 있다. 외부 서비스용 별도 프로필·실행 환경을 만드는 대안은 먼저 운영자와 확정한다.

### A. 현재값 확인과 범위 고정

```bash
hermes -p default config path
hermes -p default config get terminal.cwd
hermes -p default config get terminal.backend
```

원래 값과 변경 승인 범위를 안전한 운영 기록에 남긴다. config 전체 dump·credential 출력은 하지 않는다.

### B. 작업 경로 leaf key 설정

```bash
# 별도 변경 승인 후에만 실행
hermes -p default config set terminal.cwd /home/ainsdev/wiki/pkm-articles
hermes -p default config get terminal.cwd
```

`config.yaml`을 직접 편집하거나 전체 terminal block을 덮어쓰지 않는다. `MESSAGING_CWD`/`TERMINAL_CWD`를 새 `.env` 설정으로 중복 추가하지 않는다.

### C. API 활성화와 bind — 별도 승인·secret 준비 후

비밀 아닌 API 설정은 지원되는 nested config를 사용한다.

```bash
# API enable/bind 변경까지 승인한 경우의 예시; 미실행
hermes -p default config set gateway.api_server.enabled true
hermes -p default config set gateway.api_server.host 127.0.0.1
hermes -p default config set gateway.api_server.port 8642
hermes -p default config get gateway.api_server.enabled
hermes -p default config get gateway.api_server.host
hermes -p default config get gateway.api_server.port
```

`API_SERVER_KEY`는 secret 전용 provisioning 경로에서 운영자가 주입한다. YAML 예시에 실제 키를 넣거나 채팅으로 받지 않는다. 설치 소스는 loopback에서도 키를 요구하고 누락/placeholder/16자 미만 등 강도 검증 실패 시 시작을 거부한다. 최소 길이를 만족하는 것만으로 충분한 entropy를 보장하지 않는다.

API의 `API_SERVER_*` 환경변수 override는 config보다 우선할 수 있다. 이 API 설정 우선순위와 앞의 terminal.cwd bridge 우선순위를 혼동하지 않는다. 서비스 manager에서 실제 유효값을 확인해야 하며 이 문서는 secret 파일 열람을 요구하지 않는다.

### D. 적용·검증

- 기존 서비스 여부와 실행 중 작업을 확인한다. 확인 없이 두 번째 dispatcher를 띄우지 않는다.
- 기존 서비스 재시작과 새 foreground 시작은 각각 별도 운영 승인 후 선택한다.
- CLI가 제공하는 `hermes -p default gateway restart` 또는 `hermes -p default gateway run`을 적절한 경우에만 사용한다. 둘을 연속 실행하지 않는다.
- `--force`, `--replace`, `--accept-hooks`로 보호 경계를 자동 우회하지 않는다.
- 재시작 후 새 세션에서 실제 tool cwd·프로젝트 지침·허용 자료·write 거부를 검증한다. config readback만으로 적용 성공을 선언하지 않는다.
- `/health` → 인증된 `/v1/capabilities` → 필요한 API만 합성 입력으로 시험한다. [로드맵](implementation-roadmap.md)의 순서를 따른다.

실제 적용 시 이전 값을 복구하는 절차도 그때의 observed old value에 묶는다. 이 문서의 과거 `.`를 무조건 복원값으로 사용하지 않는다.

## 6. 프로젝트 지침과 보안

Wiki의 `AGENTS.md`는 프로젝트 컨텍스트 발견 대상이다. 현재 소스는 더 높은 우선순위 `.hermes.md/HERMES.md`, `AGENTS.override.md`, skip 설정과 git-root→cwd 탐색 규칙도 가진다. cwd를 설정한 것만으로 정확한 지침 전체가 로드됐다고 단정하지 않는다.

기존 세션은 system prompt를 캐시할 수 있다. 실행 중 대화의 설정·지침이 즉시 바뀐다고 가정하지 말고 새 세션에서 확인한다.

**AGENTS·프로필·cwd는 sandbox가 아니다.** local backend는 실행 사용자의 권한으로 Wiki 밖 절대경로에 접근할 수 있다. 외부 웹 사용자에게 필요한 실제 격리는 [보안·운영](security-and-operations.md)에서 별도로 다룬다.
