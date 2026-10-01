# 앱 요청 → 프로필 → Wiki → 응답

**문서 기반 연동 설계다. BFF 구현·프로필 생성·Gateway 적용 또는 실제 API 실행을 완료했다는 뜻이 아니다.**

## 그림 열기

1. **[전체 API 요청·응답 시퀀스](../../../.archify/workflow-profile-routing-20261001-102028/03-api-sequence/diagram.html)** — 먼저 볼 그림. 앱 질문에서 최종 답변까지 시간순으로 연결한다.
2. **[프로필별 작업 경로 매핑 workflow](../../../.archify/workflow-profile-routing-20261001-102028/02-profile-map/diagram.html)** — Wiki가 달라지면 어느 URL·프로필·cwd를 선택하는지 비교한다.

수정 가능한 원본은 각 HTML 옆의 `candidate.json`이다. 한국어 본문, 밝은/어두운 테마, 확대 열람을 제공한다. Viewer의 일부 부가 조작은 영문이다.

## 1. 앱의 요청은 어디로 가나요?

아래는 **Wiki마다 프로필을 하나씩 두는 구성안**이다. `team-wiki`와 그 경로는 설명용 가상 값이며 실제 존재를 확인하지 않았다.

| 앱이 호출하는 BFF API | BFF가 호출하는 Hermes API | 선택할 프로필 | 프로필에 설정할 기본 `terminal.cwd` |
|---|---|---|---|
| `POST /pkm-articles/v1/runs` | `POST /p/pkm-articles/v1/runs` | `pkm-articles` | `/home/ainsdev/wiki/pkm-articles` |
| `POST /team-wiki/v1/runs` | `POST /p/team-wiki/v1/runs` | `team-wiki` | `/srv/wiki/team-wiki` |

- 첫 번째 URL은 **사용자가 BFF/프록시에서 정의하는 외부 경로**다.
- `/p/<profile>/v1/runs`는 **공식 문서의 Hermes 프로필 라우팅 경로**다. 설치 버전의 지원 여부와 해당 프로필의 Gateway 서비스 등록·활성화는 실제 적용 전에 검증해야 한다.
- URL 이름이 파일 경로를 직접 만드는 것이 아니다. **BFF의 URL→프로필 허용 매핑**과 **프로필의 cwd 설정**이 두 단계를 연결한다.
- 이름이 같은 폴더를 자동 탐색하거나, 사용자 입력을 임의의 파일 경로로 치환하지 않는다. 매핑·권한·인증 실패는 실행 전에 거절한다.

## 2. 그림을 따라가는 순서

1. **앱**이 질문을 BFF로 보낸다. 앱은 Hermes 프로필 키를 갖지 않는다.
2. **BFF**가 로그인·대상 Wiki 권한을 확인하고 허용된 프로필을 고른다. 사용자·Wiki·profile·session 연결을 서버에서 유지한다.
3. BFF가 질문 `input`, 서버 관리 `session_id` 등을 구성해 Hermes의 해당 프로필 Runs API를 호출한다. 사용자 인증과 upstream 프로필 키 인증은 별개다.
4. **Gateway**가 선택된 프로필의 키를 인증하고 실행을 접수한다. `202 + run_id`는 **접수 성공이지 답변 완료가 아니다.**
5. **Agent·파일 도구**가 프로필 설정과 세션 상태로 실제 작업 기준을 결정한다. 이 그림은 local 파일 접근을 설명한다.
6. 자료·경로·도구 권한 검사를 통과한 Wiki 문서를 읽고 그 근거로 답한다. URL 라우팅 자체가 문서를 읽거나 `llm-wiki` 스킬을 실행하는 것은 아니다.
7. **BFF가 같은 프로필의 events를 구독**하고 앱에 진행·임시 답변을 중계한다. Agent 실행과 SSE 구독은 병행하며 SSE 구독이 실행의 시작 조건은 아니다.
8. 종료 이벤트 또는 연결 단절 후 BFF가 **기존 run의 상태**를 조회한다. 소유권·상태·노출 범위를 확인해 최종 답변과 근거, 또는 실패/미완료 상태를 앱에 반환한다.

## 3. cwd는 어떻게 실제 파일이 되나요?

상대경로 기준은 **세션의 현재 cwd → 등록된 작업 cwd override → 프로필 기본 terminal.cwd** 순이다. 따라서 프로필 설정만 바꾸어도 기존 모든 세션이 자동으로 새 경로를 쓰는 것은 아니다.

위 예시의 Wiki 루트가 실제 유효 cwd일 때 파일 도구의 `index.md`는 `/home/ainsdev/wiki/pkm-articles/index.md`로 해석된다. 절대경로 접근은 별도 자료·도구·OS 경계로 제한해야 한다. **cwd는 기본 위치일 뿐 sandbox가 아니다.**

한 프로필로 여러 폴더에 접근할 수는 있지만 `terminal.cwd`는 기본 경로 하나다. 요청 내용에 맞춰 여러 cwd 중 하나를 자동 선택하는 기능이나 요청 body의 임의 `workspace_id`/`cwd` 자동 적용을 가정하지 않는다. 이 설계에서는 명확한 선택을 위해 **Wiki별 프로필**을 사용한다.

## 4. 생성 이후도 같은 프로필을 유지합니다

주 그림에서 `P = pkm-articles`, `R = /p/{P}/v1/runs/{id}`다. `GET R`은 설명용 축약이며 실제 호출에는 아래 경로를 쓴다.

| 동작 | 앱 → BFF의 예시 | BFF → Hermes |
|---|---|---|
| 생성 | `POST /pkm-articles/v1/runs` | `POST /p/pkm-articles/v1/runs` |
| 상태 | `GET /pkm-articles/v1/runs/{id}` | `GET /p/pkm-articles/v1/runs/{id}` |
| SSE | `GET /pkm-articles/v1/runs/{id}/events` | `GET /p/pkm-articles/v1/runs/{id}/events` |
| 중지 | `POST /pkm-articles/v1/runs/{id}/stop` | `POST /p/pkm-articles/v1/runs/{id}/stop` |

모든 요청에서 BFF가 사용자·Wiki·profile·run 소유권을 검사한다. `run_id`나 `session_id`만으로 접근 권한이 생기지 않는다. SSE가 끊겼다고 새 run을 만들지 않으며 전체 이벤트 replay도 가정하지 않는다. 중지 접수와 실제 종료를 구분하고 failed/interrupted/partial을 완료로 표시하지 않는다.

## 적용 전제와 검증 범위

- 승인된 자료·모델·도구만 읽기 전용으로 사용하도록 집행하고 실제 격리를 검증해야 한다. 프롬프트 지시와 cwd만으로 접근을 통제하지 않는다.
- 답변은 Wiki 게시가 아니다. 기존 수집·컴파일 Cron과 원본·게시 정책은 그대로이며 기존 자동 컴파일 승인을 새 웹 질의 권한으로 확대하지 않는다.
- 두 전달 HTML은 Archify `showcase` 9/9 및 validate/deliver/strict provenance check/Chromium browser-check를 통과했다. 캡처 자동 검사와 이미지 표본 검토는 별도로 기록한다.
- 주 그림의 데스크톱 전체 시퀀스 표본, 보조 그림의 데스크톱 첫 화면을 시각 검토했다. 작은 보조 글씨는 확대가 필요하고, 매핑 그림에는 우회하는 분기선이 있다. 화면 밖 설명 카드·모바일 전체·접근성·모든 내보내기 검증은 주장하지 않는다.
- 실제 Hermes HTTP 요청·모델 호출, 설정·프로필·Cron 변경, 설치·서비스 배포는 하지 않았다.

[근거와 제외한 초안](../../../.archify/workflow-profile-routing-20261001-102028/EVIDENCE.md) · [검증 집계](../../../.archify/workflow-profile-routing-20261001-102028/verification.json)

최종 receipt: 주 그림 `03-api-sequence/label-review/diagram.finalize.json`, 보조 그림 `02-profile-map/review-3/diagram.finalize.json`. 이전 receipt가 아닌 **현재 전달 HTML과 해시가 일치하는 최종 receipt**를 사용한다.
