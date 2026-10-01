# 구현·검증 로드맵

> 상태: 후속 구현 제안. 아래 단계의 실행·설치·배포 승인은 아직 아님.
> [목차](README.md) · [아키텍처](architecture.md) · [근거·실제 검증](evidence.md)

## 1. 이번 작업의 완료 기준

- [x] 현재 Wiki 경로, 운영 계약, API 연동 방식의 기술문서를 작성한다.
- [x] 설정 유지라는 사용자 결정을 반영한다.
- [x] 현재 확인값·공식 기능·제안 설계·미확인 사항을 구분한다.
- [x] 정형 읽기/에이전트 실행/컴파일·게시를 분리한다.
- [ ] 실제 웹 앱·BFF 구축 — 이번 범위 아님.
- [ ] Gateway enable/restart·외부 공개 — 이번 범위 아님.
- [ ] 새 원문 컴파일·지식 게시·Cron 활성화 — 별도 승인 필요.

문서의 링크·코드 예시 검사와 원본 보존 결과는 [verification.json](verification.json)에 기록한다. 문서 검증을 HTTP 통합 시험 또는 UI 검증으로 표현하지 않는다.

## 2. 단계 R0 — 배포 계약 확정

확정할 항목:

1. 사용자 한 명만 접근하는지, 공개 자료가 있는지.
2. frontend/BFF/Gateway의 배치 위치와 네트워크 경로.
3. 인증 제공자·cookie/세션 방식·비밀키 관리 주체.
4. 별도 실행 환경/프로필의 필요성과 변경 승인 범위.
5. 공개 가능한 서지·지식·운영 상태 필드와 보존 정책.
6. 자유 질의의 모델·자료·도구 허용 범위. Wiki 컴파일 모델 계약을 임의 확장하지 않는다.

수용 기준: 경로·키·권한·승인 주체·적용/복구 범위를 명시한 짧은 배포 결정문. 미결이면 개인 읽기 전용 서비스까지만 진행한다.

## 3. 단계 R1 — read-only 탐색 MVP

구현 대상: [기술 스택](tech-stack.md)의 frontend/BFF, allowlisted metadata projection, pageId 매핑, 안전한 Markdown·wikilink 렌더링. 이 단계에는 Hermes 모델 호출이 필요 없다.

수용 기준:

- 사용자 인증 없는 자료 접근 거부.
- raw/_meta/절대경로를 임의 열람할 수 없음.
- 목록·페이지·출처에서 draft와 unreviewed가 유지됨.
- PDF 보관과 현재 정책 적격·승인 대기·queued·실제 게시를 구분하고 과거 blocked_policy를 현재 상태로 고정하지 않음.
- receipt/hash 불일치·미해결 게시를 완료본으로 서비스하지 않음.
- read-only mount/OS 권한을 실제 쓰기 거부 시험으로 확인함.
- 원본/서지/수집 state hash 불변.

시험 fixture는 합성 데이터로 분명히 표시하고 실제 논문 원문을 외부 서비스에 보내지 않는다. 이 단계에서 새 논문 parser/collector/DB를 만들지 않는다.

## 4. 단계 R2 — 통제된 질의와 실행 UX

선행 조건: R0 정책 승인, 격리된 Gateway 준비, 인증·도구·모델 경로 검증. live `/v1/capabilities`에 따라 지원 범위를 확정한다.

구현 대상: BFF run/session ownership, 안전한 요청 구성, Runs 생성, 상태 조회, SSE relay, 중지, 재연결, idempotency. 관리자 approval UI가 필요하면 별도 scope로 승인받는다.

수용 기준:

- 사용자 간 run/session ID 교환으로 타인의 결과를 읽을 수 없음.
- 같은 요청의 retry에서 작업이 중복 실행되지 않음.
- SSE chunk 분할·CRLF·multi-line data·comment·unknown event를 처리함.
- delta/commentary/tool/final 중복 표시 없음.
- 연결 단절 후 run 상태로 복구하고 자동 재실행하지 않음.
- stop 접수와 실제 종료를 구분함.
- 모델 fallback이나 요청/실행 경로 차이를 숨기지 않음.
- free-form 입력이 파일 쓰기·PDF 분석·Cron 변경으로 확대되지 않음.

처음에는 비민감 합성 질문으로 검증한다. 실제 Wiki 내용 모델 전송은 별도 승인된 범위에서만 실시한다.

## 5. 단계 R3 — 운영 상태 화면

수집·컴파일 ledger를 읽기 전용 projection으로 제공한다. 기존 Cron의 즉시 실행·pause/resume·편집 API를 UI에 자동 연결하지 않는다.

수용 기준: 관측 시각, 자료 확보·대기·정책 차단·실패를 구분하고 실제 ID 집합으로 집계한다. “미등록”, “비활성”, “busy”, “마지막 실패”, “미관측”을 같은 상태로 합치지 않는다. 내부 승인 문서·대화·경로는 비공개다.

## 6. 단계 R4 — 승인된 지식 작업 연결(선택)

기존 P3–P6 승인을 우회하는 UI를 만들지 않는다. 현재 P3 준비 상태는 전체 일일 실행기의 검증 완료가 아니다.

후속 수용 기준:

- 해당 단계 실행 승인과 정확한 원문·정책·모델·출력 snapshot.
- `codex-lb / gpt-6-astra / xhigh`, no-fallback, 허용 HTML 및 v3에서 별도 승인된 로컬 PDF 내장 텍스트만. PDF 바이너리·이미지·OCR·지속 추출본은 제외.
- no_cost_cap 및 미관측 비용 null 유지.
- 원문 직접 읽기, 의미 근거 검토와 시각 미검토 범위 기록.
- 게시·편집 중지 승인과 shared collection.lock.
- journal·receipt·조건부 복구·exact-repeat no-op·사용자 수정 충돌 시험.
- raw/source.json/collector state 쓰기 없음.
- 필요한 별도 등록 승인 → paused 생성 → exact readback → 별도 활성화 승인.

R4는 문서의 권고일 뿐 구현·자동화 허가가 아니다.

## 7. 회귀 시험 매트릭스

| 계층 | 합성/정적 검사 | 실제 통합 검사 |
| --- | --- | --- |
| Data | ID/경로/enum/frontmatter/hash/중복 집계 | 게시 중 snapshot 충돌·read-only 권한 |
| API | request allowlist, ownership, 오류 mapping | 설치 Gateway capability/auth/status |
| SSE | 프레임 분할·종료·unknown event reducer | proxy buffering·idle timeout·detach |
| Security | 악성 Markdown/URL/경로/symlink fixture | 키 비노출·인증 만료·CSRF·격리 경계 |
| UX | 상태 전이·IME·긴 텍스트 | 375/768/1280/1440px·키보드·screen reader |
| Reliability | 중복 요청/경합/취소·실패 reducer | Gateway restart·중지 경합·run 상태 복구 |
| Wiki publication | 기존 계약 fixture/no-op/충돌 | 별도 승인된 실제 게시와 hash 대조 |

실행하지 않은 항목의 판정은 `not_run`이다. 합성 fake provider 시험을 실제 모델 실행 성공으로 기록하지 않는다.

## 8. 실행 증거 템플릿

다음은 **후속 구현 단계에서 사용할 예시**이며 현재의 결과 파일이 아니다.

```json
{
  "artifact": "pkm-web",
  "build_ref": "<실제 commit 또는 build ID>",
  "gateway_revision": "<설치 Hermes revision>",
  "test_scope": "read-only-library",
  "environment": "<device/network/auth profile>",
  "started_at": "<timezone-aware timestamp>",
  "checks": [],
  "result": "not_run",
  "unverified": ["live_api", "browser", "deployment"]
}
```

완료 보고에는 실제 실행한 명령, 결과 경로, 실패/미실행 범위, 설정 변경과 readback을 포함한다. 배포 승인·서비스 health·실제 사용자 접근은 각각 다른 증거다.

## 9. 남은 결정과 중단 조건

구현 담당자/인증 제공자/배치 환경/production dependency versions는 아직 확정하지 않았다. 인증·격리·자료 공개 범위가 불명확하면 서버 노출 전에 중단한다. 정책 충돌·무결성 불일치·다른 프로필 변경 필요·잠금 소유권 불명확은 자동 우회하지 않는다.

설계 문서의 누락을 메꾸기 위해 live 설정을 추정하거나 원문 처리·추가 설치를 시작하지 않는다. 실제 적용 요청을 받으면 이 문서의 관측 날짜와 설치 revision부터 다시 확인한다.
