# 독립 검토 지적의 수정·검증 결과

원래 [REVIEW.md](REVIEW.md)의 no_ship 판정과 두 지적을 역사적 근거로 보존한다. 아래는 부모 구현 담당자의 수정 및 실제 회귀 결과이며 독립 검토자가 수정판을 재승인한 기록은 아니다.

## P1 scheduler projection — 수정·회귀 통과

- 설치 Hermes `cron/jobs.py`의 실제 필드 `monitor_script`, `monitor_url`, `attach_to_session`을 재확인했다. monitor 두 필드는 None, attach는 **명시적 false**가 아니면 거부한다. 미설정 attach가 전역 설정을 따르는 경우도 거부한다.
- 실제 create_job이 `.strip()`하여 prompt를 저장하는 차이도 확인했다. 원본 prompt 파일 hash는 그대로 검사하고, scheduler 문자열 비교만 같은 정규화를 적용했다.
- `runtime/parent-evidence/scheduler-runtime-red/`: 정상 런타임 prompt 직렬화를 잘못 거부한 RED.
- `scheduler-fields-red/`: monitor_script/monitor_url/attach true/attach unset 네 경우를 받아들이던 실제 실패.
- `scheduler-fields-green/`: 동일 시험이 정상 scheduled fixture를 수용하고 네 비승인 변경을 모두 거부했다. 실제 Cron 등록/수정은 없었다.

## P1 collection contention / lost outcome — 수정·회귀 통과

- 예약 전에 수집 lock이 busy이면 정상 skipped_busy를 반환하며 호출·reading 예약을 만들지 않는다.
- 이미 관측한 non-publication outcome은 daily lock 소유권 아래 run artifact에 먼저 내구 저장한다. 수집 lock은 state 반영에만 사용한다. busy이면 outcome status와 `state_reconciliation=pending`을 보고하고 추가 시도를 중지한다.
- `reconcile_outcomes()`/CLI `--reconcile-outcomes`는 원래 예약 hash·동일 승인·source/wiki/policy snapshots·exact artifact descriptors·reading 소유자를 재확인한 뒤 상태와 cost event를 한 번만 반영한다. unknown은 blocked_conflict이며 모델 재호출이 아니다. 다음 authorized daily에서도 동일한 승인 근거가 유효할 때 먼저 반영한다.
- 기존 outcome 없는 미해결 예약과 고아 잠금은 그대로 fail-closed다. 원래 승인 변경/원본 drift/다른 unresolved 거래를 해결했다고 가장하지 않는다.
- `runtime/parent-evidence/contention-red/`: 예약 및 결과 기록 두 busy 경로가 예외로 중단되던 실패를 재현했다.
- `contention-green/`: busy 뒤 알려진 unknown 내구 보존 → 잠금 해제 후 모델 재호출 없는 상태 반영 → 반복 no-op을 실제 합성 파일시스템에서 확인했다.
- `reconcile-cli-red/`의 CLI 옵션 누락을 수정했다. 최종 회귀는 CLI 전달과 state write 직전 중단·source drift 거부·복구 후 실패/비용 1회 반영을 포함한다.

## 최종 판정

`runtime/parent-evidence/final-regression-01/counts.json`: **63개 시험, 실패 0, 오류 0, skip 0, exit 0**. 결과에는 테스트에 사용한 최종 implementation/test 해시가 있다. 알려진 위 두 구현 결함에 대한 부모 회귀 gate는 PASS다. 전체 자동화 운영/예약 발화/실제 논문 의미 검토/영향 개념·비교 자동 갱신에 대한 PASS는 아니다.
