# P3 논문별 컴파일 실행기 구현·격리 검증 보고

## 판정

- **논문별 신규 draft 컴파일 경로의 구현·합성 검증: PASS.**
- **실제 P3 논문 실행·Cron 등록·활성화: HOLD / 수행하지 않음.**
- 기존 P3 준비 문서의 영향 개념·비교 자동 갱신·주간 lint까지 완료한 것은 아니다. 첫 운영 범위를 논문별 노트로 한정할지 먼저 확정해야 한다.

## 구현 결과

`runtime/daily.py`, `content.py`, `publication.py`, `p3_common.py`를 통해 승인/정책/모델/자료/무결성 gate → 오래된 미처리 원본 선택 → 내구 예약 → HTML/PDF 텍스트 생성 → 별도 pinned-model semantic review → 근거 해시 검증 → 신규 draft 게시 → 완료 receipt/state와 다음 실행 no-op을 연결했다.

- 회당 최대 5편·45분 협조적 한도, 최초 포함 2회 시도, 결과 불명 자동 재호출 금지, 반복 업무 실패 safety_block.
- 실제 HTML은 기존 helper를 재사용하며 새 수집기·파서·DB를 만들지 않았다. PDF는 기존 격리 환경 표준 pypdf의 내장 텍스트만 메모리에서 읽는다.
- 원본·source.json·수집 ledger·기존 페이지는 쓰기 대상이 아니다. 신규 노트만 draft/unreviewed로 계획하고 index/log/receipt/state는 조건부 WAL 게시한다.
- 게시 중단 7개 지점 복구, 잠금 소유권/수집 우선, 사용자 편집·원본/승인 drift 거부를 시험했다. 마지막 성공이 앞선 partial을 숨기지 않도록 집계를 수정했다.
- 생성 후 시간 한도 만료가 게시로 넘어가지 않게 연결했다. 부분 PDF의 실제 관측 페이지와 미독 범위를 일일 ledger에 남긴다.
- 독립 검토의 실제 scheduler 필드 누락과 잠금 busy 시 outcome 유실을 수정했다. 원래 검토/실패 근거는 보존한다. [수정 결과](REVIEW-RESOLUTION.md).

## 실제 시험

| 범위 | 관측 |
| --- | --- |
| 최종 P3 전체 | 63개 통과, 실패/오류/skip 0 |
| 기존 policy 회귀 | 132개 통과 |
| 기존 PDF adapter 회귀 | 107개 통과 |
| 기존 PDF 게시기 회귀 | 9개 통과 |
| 문법/공백 | runtime Python 11개 AST parse, trailing whitespace 없음; git diff --check 통과 |
| 실제 고정-root CLI 거부 | P3 미승인 exit 2, 새 live run 경로 없음 |

최종 명령:

```text
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T023617Z-p3-runtime/runtime/run_checks.py final-regression-01 test_common test_daily test_content test_publication test_integration test_contention
```

[최종 시험 로그](runtime/parent-evidence/final-regression-01/output.txt) · [개수/코드 해시](runtime/parent-evidence/final-regression-01/counts.json) · [보존/설정 확인](final-verification.json). 과거 RED와 중간 GREEN은 별도 디렉터리에 보존했다. 일부 보강 시험은 첫 실행부터 통과한 기존 동작 coverage이며 RED/GREEN이라고 주장하지 않는다.

## 운영 보존 및 미수행

원본은 HTML 18/PDF 2, compilation은 기존 published_draft 4편·HTML 승인 대기 16편이다. 기존 지식 페이지 8개와 색인은 유지한다. 보호 기준 87개 파일은 최종 행정 로그 추가 전 모두 동일했고, 로그 추가 후에는 다른 86개 파일과 기존 log prefix를 대조한다. `log.md`에는 이 구현·시험 사실만 append한다.

실제 논문 본문 해석/전송·새 모델 호출·신규 운영 Wiki 게시·수집/Cron 변경·설치·외부 알림·commit/push 없음. 원문 해시는 보존 확인용으로만 읽었다. `enabled=false`, 신규 Cron ID null, P3 실행/등록/활성화 승인 없음. 기존 수집 Cron은 별도 collect-only다.

합성 모델 응답은 시험 fixture이며 실제 논문이나 제공자 응답이 아니다. 시험은 요청 pin/자료 경계/거부/트랜잭션/복구를 검증하며, 실제 모델의 과학적 정확성·시각 판독·재현·사용자 검토를 보증하지 않는다. SIGKILL 뒤 고아 잠금 자동 탈취, 운영 hard timeout, 실제 예약 발화는 검증하지 않았다. 별도 전역 linter/typechecker·CI/merge는 실행 근거가 없다.

## 다음 결정

1. 이번 **논문별 draft 노트 경로**를 첫 배포 범위로 할지, 개념·비교 갱신까지 확장할지 확정.
2. 실제 current/future HTML/PDF 텍스트 읽기·고정 모델 전송·검증 후 게시·편집 중지에 대한 별도 실행 승인과 최신 snapshot, 운영 prompt/CLI 연결 검증.
3. 별도 등록 승인 → paused Cron 생성 및 exact readback → 별도 활성화 승인. 자동으로 이 단계로 넘어가지 않았다.

자세한 사용/복구/승인 경계는 [RUNTIME-HANDOFF.md](RUNTIME-HANDOFF.md)를 따른다.
