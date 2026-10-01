# P3 준비·검증 결과

- Run: `20260930T234207Z-p3-preparation` / 최종 판정: **preparation_complete_execution_hold**.
- 승인 범위는 준비·검증이며 논문 모델 호출·Cron 등록/활성화는 포함하지 않는다.

## 반영 완료

- 수집 원천 **20편(HTML 18/PDF 2)** 전체 ID·원본 길이/SHA-256·source.json hash를 상태와 대조했다.
- 누락 HTML **10편**을 `blocked_approval`로 추가했다. 현재 **HTML 승인 대기 16편, HTML published_draft 2편, PDF blocked_policy 2편**이다.
- 기존 compilation 항목·완료 거래·receipt·실패 기록을 변경하지 않았다. 기존 지식 **6개**와 P2 통합 output hash는 일치한다.
- 오래된 `collected_at` 우선 대기 순서를 [backlog.json](backlog.json)에 기록했다. 첫 5편은 `2609.30217v1, 2609.30266v1, 2609.30940v1, 2609.31039v1, 2609.31318v1`이며 실행/예약한 것은 아니다.
- [운영 인계](../../../P3-PREPARATION.md), AUTOMATION/COMPILATION과 index 운영 링크를 현재 P2 게시 근거에 맞게 정비했다. automation.json의 stale blocker 설명 외 권한/모델/한도/gate는 변경하지 않았다.
- collection.lock·before/after hash·[변경 journal](preparation-change-journal.json) 아래 메타데이터를 반영했고 log는 원래 prefix를 유지하며 이벤트 1개를 append했다. 잠금은 해제했다.

## 실제 검증

- [최종 시험](final-tests.json): **124개 통과, 실패 0, 오류 0, skip 0**. 합성 fixture/FakeClient만 사용했다. 기존 회귀 114개 + 준비 경계 10개이며 별도 P3 production 실행기를 구현한 것이 아니다.
- 기존 게시기의 정상 반복 no-op, 사용자 수정/reviewed 충돌, 출력 손실, page/index/log/receipt/state 장애 후 재개, 로그 중복 방지, busy/소유권/예약 동시성 시험을 통과했다.
- P2 생성기는 비파일럿 ID를 `outside_p2`로 본문 읽기/SDK 생성 전에 거부하고 enabled 일일 형태도 `p2_not_authorized`로 거부했다. 이 제한을 우회하지 않았다.
- 보호 hash **365개** 불변; 원천·수집 정책/ledger·기존 지식·이전 실행 근거 유지. 운영 문서/색인 로컬 링크 **57개** 확인, broken link 0. `git diff --check` 통과.
- [Cron readback](runtime-readiness-after.json): 기존 수집 잡 exact record와 전체 job ID 집합 불변, 신규 compiler/reviewer 잡 미등록. 전역/job enabled=false 유지.
- 설치 CLI는 paused·모델/provider/reasoning pin 옵션을 제공한다. UTC 계산으로 `0 17 * * *`가 KST 02:00임을 확인했지만 이것은 **미등록 일정 미리보기**이며 저장 next_run이나 실제 발화 관측이 아니다.

## 남은 작업 — 등록/활성화 차단

현재 실행기는 **P2 전용**이다. 일일 선택/예약→부분 읽기/재개→단일 노트와 영향 개념·비교 갱신→게시→실패 누적·재실행의 실제 P3 경로는 검증되지 않았다. 따라서 이번 124개 통과를 일일 자동화 ready로 표시하지 않았다.

다음은 새 논문 전송 없이 실제 일일 진입점의 합성 종단간 검증을 준비하는 것이다. 단계/입력·편집 중지·게시 승인, paused 등록 승인, exact readback과 별도 활성화 승인은 각각 유지한다. 기존 수집기는 건드리지 않는다. 비용은 no_cost_cap이며 미관측 비용 null은 차단 사유가 아니다.

## 바꾸지 않은 것

새 지식 게시 0, 실제 논문 모델 호출 0, 논문 본문 분석/그림 검토/PDF 추출 없음, 추가 원천 수집 없음, Cron 쓰기/전역 설정 변경/설치/commit/push 없음. 사용자 내용 검토 완료로 승격한 페이지 없음. 원본 hash 확인은 본문 의미 분석이 아니다.

[최종 기계 검증](final-verification.json) · [승인](approval.json) · [기준 snapshot](preflight.json) · [변경 전 시험](preapply-tests.json) · [최종 시험 원문](final-tests.txt).
