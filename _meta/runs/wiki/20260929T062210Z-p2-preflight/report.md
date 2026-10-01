# P2 사전 점검 — blocked_budget

## 실제 요청·승인

- 세션 재개 요청: “마지막 세션 작업을 이어서 진행해주세요”.
- 이전 세션 `20260929_024607_574197`의 마지막 결과와 현재 계약을 대조했다. P1은 완료, P2는 별도 승인 대기였다.
- 이번 확인창 응답: **“P2 실행 승인 — 사전 검증 통과 시 두 편 처리”**. 정확한 범위는 [approval.json](approval.json)에 기록했다.
- 후보는 `2609.30830v1`, `2609.31358v1`. P3–P6·신규 Cron·전역 설정 변경 승인은 아니다.

## 관측 결과

- 계약 인스턴스 4개를 설치된 JSON Schema validator로 재검증했고 `git diff --check`가 통과했다.
- 원본 10편(HTML 8·PDF 2)의 버전·파일·길이·SHA-256과 compilation ledger를 대조했다. 본문은 컨텍스트로 읽거나 추출하지 않았다. PDF는 바이트 길이·해시·경계 표식만 검사했다.
- 설정의 provider/model은 `codex-lb/gpt-6-astra`, transport는 `codex_responses`다. 실제 요청의 최종 모델·reasoning·fallback 부재는 아직 검증하지 않았다.
- 설치된 `agent/usage_pricing.py:324–363`의 순수 billing-route 판정은 이 공급자에 `unknown`을 반환했다. 이는 과금 0 또는 공급자가 가격 조회를 절대 지원하지 않는다는 뜻이 아니다.
- 설정된 목적지의 `/models`에 인증 없는 메타데이터 GET만 보냈으며 HTTP **401**이었다. 오류 본문·자격증명은 저장하지 않았고 `.env`·auth 파일을 열거나 인증을 변경하지 않았다. 이 결과는 실제 추론 실패나 모델 미존재를 뜻하지 않는다.
- 현재 정책은 `accounting_verified=false`, `hard_stop_verified=false`, 영수증 없음이다. 요청 전 최대 비용 예약·기동/추론/재시도 포함 전체 비용 정산·총 US$5 강제 차단을 검증하지 못했다.
- 설치된 `hermes_cli/model_cost_guard.py:73–116`은 알려진 고가 모델 선택 경고이며 unknown 가격에는 경고하지 않는다. `agent/iteration_budget.py:1–5,25–40`의 제한은 반복 횟수이며 USD 상한 증거가 아니다. 공식 [구성 문서](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)의 비용 표시도 강제 예산 제한과 구별한다.

## 판정과 수행하지 않은 작업

**blocked_budget — P2 미완료.** `_meta/AUTOMATION.md:24,40–46,80`에 따라 본문 읽기 전 중단했다.

- 두 후보 모두 처리/지식 게시 0편. 원문 본문·이미지·외부 자산을 모델에 보내지 않았다.
- 별도 모델 추론 probe·하위 에이전트·신규 Cron·새 설치·Git commit/push를 실행하지 않았다.
- 이 세션의 감독/사전 점검 모델 비용도 미관측이며 **0달러라고 주장하지 않는다**. charged_usd는 null이다.
- 의미 검토·인용 정확성·재실행/no-op·동시성·부분 게시·복구 시험은 실행하지 않았고 통과로 세지 않는다.
- 보호 파일 42개, 원본/서지 20개, 기존 collector 정확한 레코드와 잡 ID 집합이 기준선과 일치했다. 지식 페이지 0개, 후속 자동화 disabled/미등록을 유지했다.

## 승인 기록과 활성 상태의 구분

이번 조건부 P2 승인 기록은 이 run의 `approval.json`이다. 기존 `automation.json`과 compilation ledger는 P1 초기화 snapshot 그대로 두었다. 따라서 그 안의 `P2:false`/`blocked_approval`를 이번 사용자가 승인을 거절했다는 뜻으로 읽으면 안 된다. 아직 게이트를 통과하지 않아 실행 가능 상태로 전환하지 않은 것이다. **JSON 플래그를 true로 바꾸는 것만으로 재개하지 않는다.**

이번 쓰기는 격리된 run 근거 파일에만 한정했다. 공유 게시용 사용자 편집 중지 구간을 합의하지 않았으므로 `index.md`, `log.md`, 정책, 활성 state는 수정하지 않았다. 루트 log 반영은 향후 승인된 공유 게시 구간에 이 run ID로 중복 없이 추가해야 한다.

## 재개에 필요한 것

1. 승인된 공급자의 실제 가격/과금 계약 및 요청별 사용량·비용 영수증을 비밀 노출 없이 검증할 수 있는 경로.
2. 파일럿 총 US$5에 대해 기동·컨텍스트·추론·재시도 포함 요청 전 보수적 최대 비용 예약과 초과 요청 거부/취소를 실제 검증한 근거. 인증 성공·모델 목록·프롬프트 경고만으로 대체하지 않는다.
3. 그 후 정확한 모델 경로·reasoning·fallback 금지 검증, 승인/게이트 상태 연결, 게시 구간의 사용자 편집 중지 합의, HTML 두 편 처리 및 P2 시험.

위 조건을 보장할 수 없으면 현재 정책에서는 보류를 유지한다. 비용 위험 예외나 예산 정책 변경은 별도 사용자 승인과 정책 개정이 필요하며 이번 승인에서 추정하지 않는다. 다른 공급자나 새 프록시로 자동 전환하지 않는다.

## 근거

- [사전 기준선](preflight.json)
- [조건부 실행 승인](approval.json)
- [모델/예산 점검](model-budget-probe.json)
- [보호 범위 최종 대조](final-verification.json)
