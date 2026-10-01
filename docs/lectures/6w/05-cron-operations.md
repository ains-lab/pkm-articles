# 05. Cron 운영 설계 — 수집과 컴파일 분리

[목차](README.md) · [다음: 프롬프트·실습](06-prompts-and-lab.md)

> 이 문서는 실행 계획입니다. Cron 생성·수정·정지·재개·수동 발화는 하지 않았습니다. 대상 `0d0ad6c887e3`의 원설정 미확인으로 일정·범위 승계도 보류합니다.

## 1. 두 단계 구성

| 구분 | A: SNS 원천 수집 | B: SNS Wiki 컴파일 |
|---|---|---|
| 시작 조건 | 승인된 검색 scope·인증 보호·저장 정책 | committed 캡처 + 별도 입력/전송/게시 승인 |
| 스킬 | `agent-reach` | `llm-wiki` |
| 입력 | 공개 검색식·계정/채널 목록·checkpoint | 고정된 로컬 source manifest·기존 Wiki |
| 출력 | raw 캡처·source metadata·수집 상태·로컬 receipt | draft 노트·인용/검증·게시 receipt·별도 ledger |
| 금지 | 요약·분석·개념 생성·Discord 전송 | 새 웹 수집·raw 수정·임의 모델 fallback |
| 초기 운영 | 사용자 승인 수동 시험 | 사용자 승인 수동 시험 |
| 무인 운영 | 별도 승인 후 paused 등록 → 활성화 | SNS 컴파일 검증 뒤 별도 등록·활성화 |

수집 에이전트의 LLM은 파일 작업과 CLI 호출을 조정할 수 있지만 자료의 지식 요약을 만들지는 않습니다. 이를 “LLM 호출 0회”라고 표현하지 않습니다. `no_agent=true`는 검증된 script가 전체 작업을 수행할 때만 가능하며, 이 문서에는 그런 수집 script가 없습니다. 신규 커스텀 수집기·parser·DB를 만들어야 하는 방식은 기본안에서 제외합니다.

## 2. 설정 목표 — 실제 등록값이 아님

```json
{
  "record_kind": "sns-cron-design-proposal",
  "status": "prepared_not_registered",
  "based_on_requested_job_id": "0d0ad6c887e3",
  "baseline_settings_verified": false,
  "schedule": null,
  "schedule_timezone": null,
  "workdir": "/home/ainsdev/wiki/pkm-articles",
  "collector": {"skills": ["agent-reach"], "no_agent": false},
  "compiler": {"skills": ["llm-wiki"], "no_agent": false},
  "deliver": "local",
  "failure_deliver": "local",
  "attach_to_session": false,
  "continuity": false,
  "context_from": [],
  "script": null,
  "monitor": null,
  "model": null,
  "provider": null,
  "reasoning_effort": null,
  "enabled": false,
  "approval_ref": null
}
```

이 JSON은 설명용 projection이며 `cronjob_manage` 요청이나 설치된 schema 인스턴스가 아닙니다. collector/compiler를 하나의 실제 job 필드로 전달하지 않습니다. 모델·시간대·검색 범위·등록 ID·실행 승인은 운영자가 확정해야 합니다.

## 3. Discord 제외를 실제로 보장하려면

- `deliver=local`, `failure_deliver=local`을 명시합니다. `origin`은 메시징에서 만든 경우 그곳으로 전달될 수 있고 `all`은 여러 채널로 확산될 수 있어 쓰지 않습니다.
- 프롬프트에서 Discord용 digest 작성, 채널 ID, Webhook 전송, 직접 메시지 도구 호출을 제거합니다.
- 기존 script·monitor·context_from에도 전송 코드·지시가 없는지 검사합니다. `deliver=local`만 바꿔도 script의 직접 전송은 차단되지 않습니다.
- 수집/컴파일 에이전트의 불필요한 메시징 도구를 제외하는 방안을 검토합니다. 도구 제한만으로 terminal 네트워크 접근까지 차단됐다고 주장하지 않습니다.
- run 보고서는 ID·개수·hash·오류·경로 중심으로 로컬 저장합니다. 새 자료 없음도 로컬 이력에 남기되 알림은 없습니다.
- 이 TUI에는 Cron local 결과가 자동 도착하지 않습니다. `hermes cron list --all`, `hermes cron runs <실제ID>` 및 로컬 receipt를 확인합니다.

이번 문서 작업은 기존 잡의 Discord 전송을 제거한 작업이 아닙니다. 원래 잡 설정을 확인한 뒤 승인된 전환에서 적용해야 합니다.

## 4. `context_from`과 `continuity`의 한계

Hermes의 `context_from`은 다른 잡의 최근 완료 출력을 다음 프롬프트에 넣는 기능입니다. **선행 작업 성공을 기다리는 DAG, 같은 배치의 트랜잭션, exactly-once 보장은 아닙니다.** `continuity`도 자신의 이전 출력 기억일 뿐 durable 중복 방지 원장이 아닙니다.

따라서 기본안은 둘 다 끄고, B가 실제 로컬 manifest의 run ID·committed·source hash·승인 revision을 확인하도록 합니다. 두 작업을 시간 차로 예약해도 A가 끝났다는 보장은 없으므로 B는 데이터가 없거나 잠금 중이면 skip해야 합니다. 현재 문서의 schedule은 null이며 임의로 A/B 발화 시각을 만들지 않습니다.

## 5. 한도·실패·누락 정책 초안

아래 수치는 교육용 초기 **제안값**이며 원래 Cron 설정이나 집행된 정책이 아닙니다. 도입 전에 사용자 승인을 받습니다.

| 상황 | 제안 동작 | 완료 전 필요한 검증 |
|---|---|---|
| 소규모 파일럿 | 채널당 공개 항목 1개, 총 3개 이하 | 원천 파일·내용·출처 readback |
| 초기 정기 범위 | 채널당 후보 10개, 신규 캡처 5개, 댓글은 항목당 20개 이하 | 실제 CLI 반환·pending 집계 |
| 일시 timeout/5xx | 항목당 추가 재시도 최대 1회, run wall time 45분 상한 | deadline 강제·부분 실패 기록 |
| 429 | Retry-After 이전 재요청 금지; 해당 실행에서는 pending 이관 | next_attempt_at·재시도 금지 확인 |
| 인증 실패/403/challenge | 해당 채널 중단, 원인 미확정 표시, 사용자 확인 | 브라우저 추출·프록시 전환이 차단됐는지 |
| 실행 중복/공유 잠금 | `skipped_busy`, 겹친 run을 쌓지 않음 | 실제 owner lock·마지막 hash 확인 |
| 놓친 실행 | 다음 승인 run에서 checkpoint부터 제한된 증분; 날짜별 무한 재생 금지 | Hermes 자체 catch-up 정책과 충돌 여부 |
| 반복 핵심 실패 | 연속 3회면 SNS state의 safety block; 재개는 정책 검토 후 별도 승인 | state gate와 scheduler pause의 차이 확인 |
| 생성·검증 실패 | 성공 캡처 유지, 실패 source만 pending, 게시하지 않음 | 성공/실패 item별 분리 |
| 새 자료 없음 | 정상 empty 또는 reuse로 로컬 기록, 지식 재생성 없음 | 검색 실패를 empty로 위장하지 않음 |

요청 한도·시간 상한은 비용 절감을 위한 토큰 예산이 아니라 계정 보호·동시성·실패 범위 제어입니다. 기본 도구 내부 재시도와 외부 재시도가 중첩되지 않도록 버전별 실제 동작을 확인해야 합니다.

Cron의 automatic retry/catch-up이 있더라도 승인 snapshot·멱등성·safety block을 우회해서는 안 됩니다. 프롬프트에 한 줄 쓴 것만으로 hard gate가 집행된다고 주장할 수 없습니다. 무인 활성화 전에 실패 주입·중단 복구로 입증해야 합니다.

## 6. 승인 후 paused 등록 예시

**아래 명령은 실행하지 않았습니다.** 원설정 조회 → 정책 확정 → 수동 파일럿 → 원천/컴파일 검증 → 등록 승인이 먼저입니다. 원래 잡이 나중에 발견되면 중복 생성하지 말고 승인된 기존 잡 전환을 우선 검토합니다.

```bash
: "${SNS_SCHEDULE:?시간대까지 검토한 실제 수집 일정을 설정하세요}"
: "${SNS_APPROVED_PROMPT:?독립 실행 가능한 승인 수집 프롬프트를 설정하세요}"
: "${SNS_MODEL:?사용자가 승인한 수집 조정 모델을 설정하세요}"
: "${SNS_PROVIDER:?사용자가 승인한 provider를 설정하세요}"
: "${SNS_REASONING:?사용자가 승인한 reasoning 수준을 설정하세요}"
hermes cron create "$SNS_SCHEDULE" "$SNS_APPROVED_PROMPT"   --name "SNS Raw Collector" --skill agent-reach   --workdir /home/ainsdev/wiki/pkm-articles   --model "$SNS_MODEL" --provider "$SNS_PROVIDER"   --reasoning-effort "$SNS_REASONING"   --deliver local --failure-deliver local   --paused --paused-reason "Scope and runtime validation pending activation approval"
```

설치 CLI의 `--paused`, `--paused-reason`, `--workdir`, 모델 pin·전달 옵션은 도움말에서 확인했습니다. 일부 최신 웹 문서와 달리 현재 이 세션의 cron tool schema에는 임의 모델/reasoning 필드가 없으므로 존재하지 않는 tool 필드를 만들어 쓰지 않습니다. 모델 선택은 사용자 결정이며 전역 설정을 바꾸지 않습니다.

생성 직후 exact job을 읽어 prompt 전체·skills·모델·provider·reasoning·workdir·local/local·script/monitor/context·enabled=false/state=paused/next_run_at=null을 확인해야 합니다. CLI에서 지정할 수 없는 의도 필드도 저장값을 확인하고 승인 범위의 tool로 조정합니다. 생성 성공 메시지만으로 완료하지 않습니다.

컴파일 B는 이 명령을 무심코 복제해 등록하지 않습니다. SNS 컴파일 승인·모델·범위가 확정되면 `llm-wiki`와 독립적인 프롬프트를 사용해 별도로 검토합니다. `paused`는 자동 발화를 막는 상태일 뿐 수동 `run` 금지 보안 경계가 아닙니다.

## 7. 운영자가 매번 확인할 결과

- 수집: 플랫폼별 discovered/accepted/captured/reused/partial/blocked/failed/pending의 **ID 집합**과 실제 파일 수.
- 컴파일: 선택된 source 수, 실제 읽은 범위, 생성/검증/게시 실패 수와 미처리 사유.
- 게시: receipt committed, 페이지/index/state의 실제 hash, 원천 불변·log append 보존.
- 검토: draft/unreviewed, 사용자 검토된 범위, 여전히 미확인인 영상/댓글/연결 전문.
- 장애: scheduler의 `last_status:ok`와 업무 산출물 성공을 분리. 실제 업무 실패는 설치 Hermes가 인식하는 첫 줄 `[CRON_FAILURE]` 규약을 검토하고 local 이력을 남깁니다.

정지 시에는 신규 발화 중단과 이미 실행 중인 작업 종료를 구별합니다. 활성 owner가 남아 있으면 잠금을 탈취하지 않습니다. 다른 잡·Gateway 전체를 정지하는 방식으로 SNS 작업을 전환하지 않습니다.
