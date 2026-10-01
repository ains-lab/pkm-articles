# P3 일일 증분 Wiki — 준비·검증 인계

- 확인 날짜: 2026-10-01 KST / run `20260930T234207Z-p3-preparation`.
- 판정: **준비 목록과 격리 검증 완료; P3 일일 실행·등록·활성화는 HOLD**.
- [사용자 승인 범위](runs/wiki/20260930T234207Z-p3-preparation/approval.json) · [검증 전 기준](runs/wiki/20260930T234207Z-p3-preparation/preflight.json) · [회귀 결과](runs/wiki/20260930T234207Z-p3-preparation/preapply-tests.json).
- [정식 운영 계약](AUTOMATION.md), [상태 계약](STATE-CONTRACTS.md), [HTML 직접 컴파일](COMPILATION.md)을 적용한다. 문서상의 준비 완료는 실행 권한이 아니다.

## 1. 완료 상태와 대기 목록

| 상태 | 편수 | 처리 |
| --- | ---: | --- |
| HTML `published_draft` | 2 | 기존 receipt/output/revision 유지; 논문 노트 재생성 없음 |
| HTML `blocked_approval` | 16 | 누락 10편 메타데이터만 추가; 읽기/시도/게시 기록 없음 |
| PDF `blocked_policy` | 2 | 원본 확보 완료지만 내용 읽기/추출/컴파일 금지 |
| 확보 원천 합계 | 20 | 20개 정확한 version_id, HTML 18/PDF 2 |

수집 대기 48편은 아직 보관 원천이 아니므로 이번 compilation 목록에 추가하지 않는다. 이미 보관된 원본의 형식을 교체하거나 HTML을 추가 수집하지 않는다.

대기는 `collected_at`의 실제 시각 오름차순, 동률이면 정확한 `version_id` 문자열 순서다. 아래는 **선택 미리보기**이며 예약/실행 요청이 아니다. 최대 5편/회와 45분 협조적 한도, 최초 포함 2회 시도·연속 업무 실패 3회 safety_block을 유지한다. 비용은 `no_cost_cap`, 미관측 값은 null이다.

| 순서 | version_id | 수집 시각 |
| ---: | --- | --- |
| 1 | `2609.30217v1` | `2026-09-28T10:42:11.138705+00:00` |
| 2 | `2609.30266v1` | `2026-09-28T10:42:14.317240+00:00` |
| 3 | `2609.30940v1` | `2026-09-28T10:42:39.734613+00:00` |
| 4 | `2609.31039v1` | `2026-09-28T10:42:42.912271+00:00` |
| 5 | `2609.31318v1` | `2026-09-28T10:42:56.338003+00:00` |
| 6 | `2609.31562v1` | `2026-09-28T10:43:02.651083+00:00` |
| 7 | `2609.35760v1` | `2026-09-29T15:09:07.955675+00:00` |
| 8 | `2608.29596v2` | `2026-09-29T15:09:08.398512+00:00` |
| 9 | `2609.35596v1` | `2026-09-29T15:09:08.548055+00:00` |
| 10 | `2609.35576v1` | `2026-09-29T15:09:08.679810+00:00` |
| 11 | `2509.09215v3` | `2026-09-29T15:09:08.972803+00:00` |
| 12 | `2609.35366v1` | `2026-09-30T15:09:18.518076+00:00` |
| 13 | `2609.35117v1` | `2026-09-30T15:09:21.436635+00:00` |
| 14 | `2609.35088v1` | `2026-09-30T15:09:24.426531+00:00` |
| 15 | `2605.09027v3` | `2026-09-30T15:09:27.411272+00:00` |
| 16 | `2609.34790v1` | `2026-09-30T15:09:30.436440+00:00` |

기계 판독 목록과 source/metadata hash는 [backlog.json](runs/wiki/20260930T234207Z-p3-preparation/backlog.json)에 있다. 실행 전에 최신 상태·원천/정책/승인·기존 출력 및 receipt를 다시 대조하고 그때 실행 가능한 오래된 항목만 선택한다. `published_draft`라는 상태 문자열만으로 no-op을 허용하지 않는다.

## 2. 관측된 증거와 검증 한계

| 항목 | 결과 / 근거 범위 |
| --- | --- |
| P2 논문별 게시 | [기존 실제 게시](runs/wiki/20260930T103720Z-p2-publish-approved/final-verification.json); 이번 재생성 아님 |
| P2 개념/비교 통합 | [기존 통합 검증](runs/wiki/20260930T125856Z-p2-integration/final-verification.json): 6개 지식 페이지, 에이전트 의미 대조·반복 no-op·격리 복구 근거 |
| 현재 안전 회귀 | 124개 통과, 0 실패/오류/skip. 기존 114개와 준비 경계 10개. 외부 모델 대신 합성 fixture/FakeClient 사용 |
| 반복·출력 손실·사용자 편집 | 기존 게시기 격리 회귀 통과: 정상 반복은 no-op, 출력 손실/외부 변경/reviewed 문서는 거부 |
| 게시 중단·복구·동시성 | page/index/log/receipt/state 단계 장애·조건부 재개, 로그 중복 방지, busy/소유자 변경·원자 시도 예약 회귀 통과 |
| P3 ID 진입 | 현재 생성기가 비파일럿 ID를 `outside_p2`로 **본문 읽기/클라이언트 생성 전 거부**함을 확인 |
| P3 enabled 형태 | 합성 enabled 정책도 `p2_not_authorized`로 거부. P2를 억지로 일일 실행기로 전용하지 않음 |
| 의미/시각/실험 | 이번 실제 논문 의미 검토 없음. 기존 페이지는 draft/unreviewed. 사용자 검토·그림 판독·논문 실험 재현 아님 |
| 일일 전체 경로 | 예약→선택→읽기/partial→검증→영향 페이지 갱신→게시→실패 누적/재개는 **미검증**, 통과 주장 금지 |

[시험 원문](runs/wiki/20260930T234207Z-p3-preparation/preapply-tests.txt) · [준비 경계 시험](runs/wiki/20260930T234207Z-p3-preparation/test_p3_readiness.py). 처음부터 통과한 기존 동작 회귀이며 새 실행기 구현의 RED/GREEN 증거가 아니다. 현재 실행기의 P2 제한은 결함이 아니라 기존 권한 경계다.

## 3. 일정·등록 준비 상태

- 의도: `PKM Daily Wiki Compiler`, 매일 KST 02:00. 설치 런타임의 읽기 전용 일정 계산에서 시간대 UTC, `0 17 * * *`의 다음 시각을 KST 02:00으로 확인했다. [런타임 관측](runs/wiki/20260930T234207Z-p3-preparation/runtime-readiness-before.json). 이것은 **미등록 일정 미리보기**이지 저장 잡의 next_run 또는 실제 발화 증거가 아니다.
- 설치 CLI [help](runs/wiki/20260930T234207Z-p3-preparation/installed-cron-help.txt)에서 `--paused`, `--model`, `--provider`, `--reasoning-effort`, `--workdir`, `--skill`, `--deliver`, `--failure-deliver` 지원을 확인했다. 생성 명령은 실행하지 않았다.
- 승인 후 저장할 값: provider `codex-lb`, model `gpt-6-astra`, reasoning `xhigh`; root `/home/ainsdev/wiki/pkm-articles`, skill `llm-wiki`, 전달과 실패 전달 `local`, 처음부터 paused. SDK/런타임에서 fallback 금지와 reasoning 실제 전달은 별도 검증해야 한다.
- 현재 `cron_id=null`, `not_registered`, 전역/job enabled=false, 등록/활성화 승인=false. **paused 잡이 이미 존재한다는 뜻이 아니다.** 기존 원문 수집 잡 `4cff5b4f10ec`와 다른 잡은 변경하지 않는다.
- `context_from`/continuity를 선행 성공 배리어로 쓰지 않는다. 최신 committed state/receipt를 직접 확인한다. 문서/프롬프트 revision과 hash를 재확인해야 하므로 지금의 임시 프롬프트를 곧바로 등록하지 않는다.
- 외부 전달 없음. TUI에 예약 결과가 자동 도착한다고 약속하지 않는다. 정상 무변경도 검증 receipt를 남기며 local 보고로 끝낸다.

## 4. 등록 전 남은 최소 게이트 — 현재 모두 실행 승인 아님

1. **일일 경로를 합성 입력으로 완결 검증**: 최대 5편 선택, 수집 시 추가된 원천의 메타데이터 편입, snapshot 예약/중복 방지, 단일 논문과 영향 개념·비교의 분리, 주간 한정 lint. P2 제한을 삭제하는 것만으로 대체하지 않는다. 별도 수집기·파서·DB를 만들지 않는다.
2. **일일 상태 전이**: 실행 가능한 항목만 선택, 부분 읽기와 미독 범위/재개 anchor, 항목당 2회 시도·연속 업무 실패 3회 누적과 safety_block, unknown completion 보존. 승인 대기/no-op/busy는 업무 실패가 아니다. PDF 입력은 모델 앞에서 차단한다.
3. **모델·승인·게시 연결**: 지정 경로와 no-fallback, 해당 단계/정확한 입력의 새 승인, 편집 중지 범위, 최종 정책/입력/대상 hash를 실제 일일 진입점에서 검증한다. 이번 운영 문서 변경 전 snapshot/승인을 그대로 재사용하지 않는다.
4. **공유 게이트**: 수집 우선 KST 23:55–01:35에는 게시 금지, lock busy는 skipped_busy, 고아/타인 잠금 탈취 금지. 앞선 작업이 아직 진행 중이면 중복 예약/게시하지 않는다. 정식 일일 경로에서 충돌·중단·재개/no-op을 다시 검증한다.
5. **갱신 경계**: 검토 완료/사용자 수정 페이지 보존, 기존 페이지 10개 이상 변경은 별도 승인. 신규 근거로 영향받는 개념·비교만 검토한다. 과거 지식 전체 재작성이나 전체 색인/로그 snapshot 복원 금지.
6. **누락 일정/실패**: missed run은 날짜를 재생하지 않고 오래된 실행 가능 상태부터 처리. 반복 업무 실패는 local safety_block이며 Cron pause와 다르다. 실제 잡 pause/resume은 정확한 잡과 별도 승인·readback이 필요하다.
7. **별도 등록 승인 → paused 생성 → exact readback → 별도 활성화 승인**: 저장 ID·paused/enabled·schedule·next_run/시간대·프롬프트 hash·pin·skills·workdir·local 전달을 확인한다. P5 anchor/첫 발화는 계속 미승인이다.

금액 상한·계측 검증·강제 비용 차단은 위 게이트에 추가하지 않는다. 새 논문 모델 호출, 실제 일일 발화, 신규 지식 게시, P4–P6 처리는 이번 준비에서 하지 않았다.

## 5. 변경·복구 기록

이번 메타데이터 정비는 collection.lock과 before/after hash 기록 하에서 수행한다. 기존 compilation 항목/완료 거래는 그대로 두고 누락 10항목만 추가하며, log는 실제 완료 작업을 중복 없이 append한다. 원본·수집 ledger·기존 지식·과거 실행 파일은 보호 대상이다. 실행 기록은 [준비 run](runs/wiki/20260930T234207Z-p3-preparation/)에 남긴다.

중간 중단 시 이번 run의 `preparation-change-journal.json`과 현재 target hash를 비교해 old/new/unexpected로 분류하고 운영자 검토 후 남은 **메타데이터** 변경만 진행한다. 이는 기존 P2 지식 게시기의 자동 복구 인터페이스가 아니며 해당 publisher로 재생하지 않는다. 예기치 않은 수정이나 고아 잠금은 보존하고 멈춘다. 과거 로그 절단·전체 index 복구·raw/수집 state 복원은 금지다.
