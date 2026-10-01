# P3 자동 Wiki 컴파일 활성화 결과

## 판정

**설정·등록·로컬 안전성 검증 완료, 첫 예약 실행은 아직 미관측.** 원본 수집과 컴파일은 별도 일일 배치다. 사람 검토를 필수 단계에서 제거했지만 기계 검사와 별도 모델 의미 검토는 유지한다. 전체 Wiki lint를 새로 자동화한 것은 아니다.

## 승인과 적용 범위

- [사용자 범위 승인](scope-approval.json): 현재·향후 정상 수집 HTML/PDF 텍스트, 검증 후 신규 논문별 노트 게시, 매일 KST 02:00–02:45 직접 편집 중지.
- 신규 성공 노트: `status: compiled`, `review_state: auto_verified`, 사람 검토 필드는 null. 기존 draft 노트와 receipt는 보존한다.
- 고정 경로: `codex-lb / gpt-6-astra / xhigh`, fallback 금지, `no_cost_cap`, 미관측 비용 null.
- 원본/source.json, 수집 설정·상태, 기존 지식 페이지, legacy P2 가드는 변경하지 않는다. PDF 내장 텍스트만 허용하며 OCR·이미지·바이너리 전송·지속 추출본은 금지한다.

## 일정과 현재 재고

| 항목 | 확인 결과 |
| --- | --- |
| 원본 수집 | `4cff5b4f10ec`, 매일 KST 00:00, collect-only 유지 |
| Wiki 컴파일 | `4839be6a1db1`, 매일 KST 02:00, UTC `0 17 * * *`, enabled=true/state=scheduled |
| 다음 실행 | 등록 readback 기준 **2026-10-02 02:00 KST** |
| 처리 한도 | 오래된 실행 가능 항목부터 최대 5편, 해당 일 02:45 KST까지·최대 45분 |
| 원본 | 20편: HTML 18, PDF 2 |
| 기존 논문별 게시 | 4편, 지식 페이지 총 8개(개념·비교 포함) |
| 미완료 | 16편, 다음 정상 실행 gate를 기다리는 `blocked_approval`; 논문별 사용자 검토 대기 아님 |
| 전달 | local 저장만 사용, TUI 자동 알림·외부 전달 없음 |

현재 재고 기준 다음 선택은 `2609.30217v1`, `2609.30266v1`, `2609.30940v1`, `2609.31039v1`, `2609.31318v1`이다. 선택 예정은 실제 읽기·게시 완료가 아니다. 지속 유입량에 따라 매일 최대 5편으로 backlog 전량 소진을 보장하지 않는다.

## 이전 첫 배치 결과와 재시도

[이전 수동 배치](../20261001T053212Z-p3-first-operation/daily-report.json)는 5편 중 검토 거부 4편, 결과 불명 1편으로 종료했다. 신규 게시 성공으로 계산하지 않는다. 사용자 `5편 모두 새 승인으로 재시도 허용`에 따른 [별도 승인](retry-approval.json)으로 이 5편만 한 번 재대기 처리했다. 이전 reservation/result/report/review/outcome 및 실패 이력은 그대로 보존했다. 결과 불명 항목의 중복 모델 처리 가능성도 해당 승인에 명시돼 있다. 이후 unknown이나 safety_block을 자동으로 해제하는 권한은 아니다.

## 검증 근거

- [전체 회귀](runtime/parent-evidence/parent-final-full-02/counts.json): 단위·통합 93개, 실패/오류/skip 0. 실제 원문 본문 접근·네트워크 시도 0인 합성 시험이다. 정책 스키마 시험과 현재 automation/compilation/feedback/research-review 4개 instance도 별도 확인했다.
- [예약 안전성 추가 시험](runtime/parent-evidence/scheduler-supplemental-01/counts.json): 마감 후 생성/검토/게시 거부, 내구 terminal outcome, 게시 중단·복구, 정확한 runtime manifest 검증, 잔여 재고 보고를 포함한다.
- [활성 등록 readback](registration-active.json), [runtime manifest](runtime-manifest.json), [예약 실행 승인](scheduled/execution-approval.json): 실제 저장된 프롬프트·모델·스케줄·workdir·skills·local 전달 및 코드/정책 hash를 결합했다.
- [활성화 전후 대조](preflight.json), [최종 대조](final-verification.json): 원본·메타데이터·기존 지식·수집 설정/상태 50개 보호 파일, 기존 게시 output/receipt, source ID와 ledger 전체, index의 실제 8개 페이지, 과거 log prefix 및 실패 근거를 대조한다.
- 실제 운영 entrypoint의 구간 밖 `--check`는 exit 2/blocked였다. 읽기 전용 후속 검사에서 정확한 거부 이유 `edit_freeze_window`, run 디렉터리 미생성, 원문 접근·네트워크 시도 0을 확인했다. 시간을 위조하거나 즉시 논문 실행하지 않았다.
- 다른 Cron의 설정은 그대로다. 다른 정기 작업의 `repeat.completed` 증가는 실행 관측치이며 설정 변경과 구분했다. 최초 과도한 전체 repeat 비교의 실패를 성공으로 꾸미지 않는다.
- `git diff --check`를 확인하며 commit/push하지 않는다. 합성 시험·스키마·등록 확인은 실제 예약 발화나 신규 논문의 의미 검토 통과를 증명하지 않는다.

## 운영 및 검증 경계

중첩 실행은 skip하고 잠금을 탈취하지 않는다. 놓친 날짜는 다음 정상 구간의 오래된 backlog로 이어가며 구간 밖 재생하지 않는다. unknown·검증 거부·미완료 WAL은 완료로 세지 않고 자동 재호출하지 않는다. 안전 차단 해제는 원인 확인과 별도 복구 승인이 필요하다.

노트별 형식·출처/인용·링크·별도 모델 의미 검토 및 게시 무결성 검사는 적용돼 있다. **전체 Wiki의 고아 페이지·태그 전수·노후화·모순 등을 점검하는 통합 lint/주간 lint는 연결하지 않았다.** 개념·비교 자동 수정, P4–P6, 외부 알림·설치·다른 잡 변경도 범위 밖이다.

이번 작업에서는 새 논문을 모델로 처리하거나 지식 페이지를 추가하지 않았다. 실제 첫 예약 배치의 성공 여부는 해당 배치의 report/outcome/receipt로 확인해야 한다.
