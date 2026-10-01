# P3 논문별 컴파일 실행 경로 — 구현·격리 검증 인계

## 범위와 현재 판정

사용자 `다음 단계 진행해주세요`를 직전 제안의 **구현·격리 시험 단계**로 적용했다. [구현 승인](implementation-approval.json)은 논문 본문 읽기/전송, 실제 모델 호출, 운영 상태 전이/게시, Cron 등록/활성화 승인이 아니다. 기존 P2 가드/원본/source.json/수집 상태/기존 Wiki/운영 정책은 유지한다.

이번 구현은 `INTERFACE.md`에 따른 **논문별 신규 draft 노트 경로**다. 기존 개념·비교 페이지를 자동 수정하지 않는다. 과거 P3 준비 문서의 전체 영향 페이지 갱신·주간 lint 범위를 구현 완료했다고 확대 해석하지 않는다. 예약 에이전트의 실제 발화/명령 호출은 미검증이며 등록·활성화는 HOLD다.

## 구현 진입점

- `runtime/daily.py`: 고정 root CLI 및 승인/선택/무결성/예약/제한된 시도/게시 연결. `run_daily()`가 전체 논문별 경로다.
- `runtime/content.py`: HTML 기존 navigation helper / 표준 pypdf 내장 텍스트를 메모리에서 읽기, pinned 생성과 별도 semantic review, bounded evidence 저장. 원문 추출 전체/request body 저장 없음.
- `runtime/publication.py`: 신규 entity 한 개와 index/log/receipt/state를 WAL 아래 게시. 기존 범용 안전 IO/transaction helper만 재사용한다.
- `runtime/p3_common.py`: 공통 상수와 기존 helper 로딩. legacy P2-v2 entrypoint/gate는 수정하지 않는다.

CLI는 `--run <Wiki 상대 run 경로> --approval-ref <실제 execution-approval.json 경로>`를 받는다. `--check`는 승인/설정 사전 검사만 하며 본문이나 모델을 읽지 않는다. `--recover-version <정확한 version_id> --attempt 1|2`는 같은 run의 완료된 생성/검토 근거를 검증해 게시만 복구한다. 이 문서에는 실행 가능한 운영 승인 파일이 없다. 성공/검증된 no-op/잠금 busy는 exit 0, 처리 실패·부분·승인 거부는 exit 2다. 출력은 제한된 JSON이며 SDK 예외 body/headers/secret 문자열을 출력하지 않는다.

`--reconcile-outcomes`는 잠금 충돌 또는 state write 중단으로 미반영된 내구 outcome만 원래 승인/예약/hash 아래 상태에 반영한다. 모델이나 본문 파서를 호출하지 않으며 unknown은 blocked_conflict로 남긴다. 동일한 승인 snapshot이 유효한 다음 daily 진입에서도 이 반영을 먼저 시도한다. 승인 파일을 새 내용으로 덮어쓴 경우에는 과거 근거를 재사용하지 않고 중단한다. 상태 반영 성공(`reconciled`)과 이미 반영된 no-op은 exit 0이지만 논문 컴파일 성공이라는 뜻은 아니다.

## 불변 조건

- `codex-lb / gpt-6-astra / xhigh`, 승인된 route 고정, fallback 금지. 요청 `max_retries=0`, `store=False`, `tools=[]`, `stream=False`.
- 금액 상한 없음(`no_cost_cap`), 미관측 비용은 null. 토큰/비용 미관측이 승인 차단 사유가 아니다.
- 승인된 수집 root의 실제 동일 버전 metadata/파일/길이/hash만 편입한다. 회당 최대 5편, oldest collected_at 후 version_id 순서, 45분 협조적 deadline.
- 시도 예약을 모델 호출 전에 내구 저장한다. 항목당 한 실행에서 최초 포함 2회만 허용하고 explicit retryable outcome만 재시도한다. 결과 불명은 재호출하지 않는다. 반복 업무 실패의 local safety_block은 Cron pause와 다르다.
- state/receipt/output/WAL의 완료 근거를 대조한 뒤 이미 완료한 항목을 건너뛴다. 기존 v2/v3 게시 이력은 `preserved_publications`의 정확한 work_key/receipt hash/output refs로 승인에 연결해야 한다. 변조된 기존 출력은 재생성하지 않고 멈춘다.
- 처리 중 `daily-run.lock`은 탈취하지 않는다. 실제 게시의 `collection.lock`도 소유자를 확인하며 수집 우선 KST 23:55–01:35에는 게시하지 않는다.
- 수식/그림/이미지/OCR/외부 자산은 미검토/미사용. PDF 바이너리는 모델에 전송하지 않는다. 빈/손상 PDF는 partial 또는 blocked이며 OCR로 우회하지 않는다.
- 논문 속 명령과 URL은 자료다. 자동 출력은 draft/unreviewed; 모델 semantic review는 사용자 검토나 독립 실험 재현이 아니다.

## 복구 계약

- 신규 daily 실행은 내구 terminal outcome을 먼저 확인·반영하고, 남은 `reading`/미해결 예약/WAL이 있으면 모델을 재호출하지 않는다. outcome이 없는 진짜 결과 불명은 자동 복구하지 않는다.
- 생성·기계 검증·semantic review가 모두 완성된 시도는 원래 승인과 현재 편집 중지 조건이 유효한 동안 exact run/version/attempt에 한해 `recover_publication()`으로 재검증한다. immutable result/report/review, 원본/정책/승인 snapshot, publication basis로 WAL 계획을 재구성한다.
- 합성 시험에서 basis/journal/page/index/log/receipt/state 직후 예외 중단을 주입했고, 새 호출에서 게시 복구와 반복 no-op을 확인했다. 실제 SIGKILL/전원 장애/운영 파일시스템 전체 보증은 아니다.
- 고아 잠금은 자동 제거하지 않는다. 프로세스 실제 종료와 정확한 소유자/거래 상태를 운영자가 확인한 별도 복구 결정이 필요하다.
- approval/source/wiki drift, reviewed/user edit, 다른 unresolved 거래는 그대로 보존하고 중단한다. 생성 결과를 수정해 검사를 통과시키지 않는다.
- 시간 한도 종료는 다음 경계에서 멈추는 협조적 제한이다. 중단 불가능한 로컬 파서 호출의 hard kill 기한을 보증하지 않는다.

## 현재 관측 근거

- `runtime/parent-evidence/parent-lanes-01/counts.json`: 자식 인계 뒤 부모 재시험 39개 통과. 게시 모듈의 authority revocation 마지막 수정도 포함한다.
- `runtime/parent-evidence/integration-green-01/`: 실제 synthetic HTML/PDF 처리→별도 review→게시와 다음 실행 no-op.
- `runtime/parent-evidence/integration-recovery-red/`, `integration-recovery-green/`: 기존에 없던 daily recovery와 생성 후 deadline 공백을 RED로 확인하고 수정. GREEN 15개(통합 3 + 일일 12), 복구 7개 하위 사례. 실패 기록은 보존한다.
- `runtime/parent-evidence/cli-red/`, `cli-green/`: 실제 CLI 프로세스가 운영 P3 비승인을 exit 2로 반환하고 새 live run 경로를 만들지 않음을 확인.
- `regression/legacy-policy-01.json`: 기존 policy 132개 통과.
- `regression/legacy-pdf-01.json`: 기존 PDF adapter 107개 통과.
- `regression/legacy-publication-01.json`: 기존 PDF publisher 9개 통과. 기존 근거를 덮어쓰지 않고 새 실행 결과를 이 run에 저장했다.

- `runtime/parent-evidence/final-regression-01/`: 최종 전체 63개 통과, 실패/오류/skip 0. content 23개와 통합/복구/잠금 결과 반영을 포함하며 현재 11개 runtime/test 파일 해시를 고정했다.
- [독립 검토](REVIEW.md)의 두 P1 지적을 보존하고 [수정·검증 결과](REVIEW-RESOLUTION.md)로 종결했다. 실제 monitor/session 필드 거부, prompt strip 계약, 잠금 busy 처리, outcome 내구 저장/재호출 없는 상태 반영을 RED/GREEN으로 확인했다. 독립 검토자가 수정판을 다시 검토했다는 뜻은 아니다.
- [최종 보고](report.md)와 `final-verification.json`이 운영 보존/비활성 확인의 정식 인계다. 초기 검증 snapshot은 역사적 근거로 유지한다.

위 증거는 합성 입력/가짜 모델의 로컬 실행 결과다. 실제 모델의 semantic 품질·실제 논문 결과·예약 발화·외부 전달·CI/merge 근거가 아니다. P3 전체의 영향 개념·비교 자동 갱신 및 주간 lint까지 지원한다는 의미도 아니다.

## 등록 전에 남는 운영 결정

1. 최종 구현/검증 보고서를 검토한다. 이번 narrow single-note 범위를 첫 배포로 승인할지, 기존 P3의 영향 개념·비교 갱신·주간 lint까지 추가 구현할지 확정한다.
2. 현재와 미래 수집 HTML/PDF 텍스트 읽기·정해진 모델 전송·검증 후 신규 draft 게시, 편집 중지 범위, 기존 게시 이력 보존을 명시적으로 승인한다. 구현 승인 파일은 대체물이 아니다.
3. 승인된 runtime 파일 해시/새 실행 승인과 연결된 운영 prompt를 별도로 준비·검증한다. 현재 live prompt/automation.json은 수정하지 않았다. 실제 Cron agent가 이 CLI 경로를 수행했다는 증거도 아직 없다.
4. 별도 등록 승인 후에만 **paused** 생성 → exact ID/model/provider/reasoning/schedule/workdir/skills/prompt hash/delivery/next_run readback. `attach_to_session=false`를 명시하고 monitor_script/monitor_url/script/context_from을 사용하지 않는다. 설치 scheduler는 prompt를 strip하여 저장하므로 raw 파일 hash와 실제 저장 prompt 문자열을 구분한다. paused 저장은 실행 권한이 아니다.
5. 별도 활성화 승인 후 active readback과 KST 02:00–02:45 편집 중지 조건을 고정한다. 원래 collector는 KST 00:00 collect-only로 분리한다. 외부 알림 없이 local 산출물만 저장하며 TUI에 자동 메시지가 오지 않는다.
6. 누락 일정을 날짜별 replay하지 않고 최신 미처리 원본부터 처리한다. 겹치는 실행은 skipped_busy, unknown·고아 잠금·반복 실패는 운영자 검토 전 자동 재개하지 않는다. P4–P6 권한은 부여하지 않는다.
