# P2 빠른 사전·격리 테스트 — 실행 보류

- 사용자 요청: `P2 위키 컴파일 테스트를 빠르게 진행해주세요`.
- 결과: 사전·합성 fixture 검사 26개 중 17개 통과, 9개 실패. **실제 논문 컴파일/P2 완료가 아니다.**
- 근거: [실행 결과](test-report.json), [초기 결과](initial-test-report.json), [재현 코드 기록](reproduce.md).
- 이번 별도 모델 호출 0회, 원문 텍스트 전송 없음, 운영 지식 페이지 게시 없음. 원본은 SHA-256·길이·파일 목록·버전 대조만 했다. 합성 결과를 논문 분석이나 실제 모델 응답으로 사용하지 않았다.

## 통과한 주요 검사

- automation.json과 compilation.json의 현재 JSON Schema 검사.
- HTML 13편·PDF 2편, 총 15개 버전의 원본/서지 패키지 무결성. PDF 내용 추출은 하지 않았다.
- 기존 compilation ledger 10개 항목의 원본·서지 해시/길이.
- 지식 페이지 0개와 index 일치, 자동 작업 비활성·미등록 설정 유지.
- 격리 시험 전후 보호 파일 39개 SHA-256 불변. 이후 실제 작업 로그만 별도 append하며 최종 보존 검사는 final-verification.json에 기록한다.

## 실패와 재현 근거

| 종류 | 실패 | 위치 |
| --- | --- | --- |
| 정책 | AGENTS/SCHEMA는 v1의 P2 미승인·비용 제한, automation은 v2/P2 승인/no_cost_cap. 계측·강제 차단도 미검증 | AGENTS.md:29–33, SCHEMA.md:136–141, _meta/automation.json:34–65 |
| 상태 | feedback/research-review는 policy/contract v1이라 현재 v2 스키마에 부적합(2개 검사) | _meta/state/feedback.json, _meta/state/research-review.json |
| 프롬프트 | 설정/스키마가 v1을 가리키나 실제 두 프롬프트는 v2(2개 검사) | _meta/automation.json:82,100, _meta/prompts/*.md |
| 검증 | 합성 response_status=incomplete, main_text_complete=false를 passed=true로 판정 | _meta/runs/wiki/20260929T083140Z-p2-resume/verify-one.py:16–31 |
| 잠금 | 수집기의 mkdir 기반 디렉터리 잠금에 IsADirectoryError. 잠금이 없으면 flock용 일반 파일을 남김 | _meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py:54–60 |
| 게시 | 실제 index 헤더와 replace 문자열 불일치. 격리 시험에서 page 존재/색인 항목 없음/receipt 없음/AssertionError | 동일 publish-one.py:80–85,132 |
| 상태 게시 | committed는 item status 열거형 밖, work_key는 SHA-256 아님, output_refs는 객체가 아닌 문자열 | 동일 publish-one.py:101–105 |

게시·검증 스크립트는 운영 경로가 아닌 임시 디렉터리에서 **명시적 합성 HTML·합성 응답**으로 실행했다. 실제 원본 폴더와 상태에 합성 데이터를 쓰지 않았으며 fixture는 폐기했다. 불완전 입력을 게시에 넘긴 이유는 검증기를 통과한 잘못된 응답이 후속 경로에서 거부되는지도 확인하기 위해서다.

첫 검사에서 PDF 패키지의 기대 파일명 목록을 정렬하지 않아 검사기 자체 오탐이 있었다. initial-test-report.json을 보존하고 기대 목록을 정렬한 뒤 전체 검사를 재실행했다. PDF 원본·메타데이터를 수정해서 통과시킨 것이 아니다.

## 이전 시도에 대한 정정

비스트리밍 실제 시도에는 attempt1-record.json만 있고 결과가 없다. 현재 process_manage 목록도 비어 있다. 로컬 종료 원인·서버측 취소·비용은 관측되지 않았으므로 '세션 종료로 확정 실패/취소'라고 단정하지 않는다. 짧은 NONSTREAM_OK probe 성공은 실제 논문의 장시간 컴파일 성공 증거가 아니다.

실제 ledger 상태는 blocked_approval 6개, blocked_policy(PDF) 2개, retryable_failed 2개다. 이후 수집된 원본 5편은 아직 compilation ledger 밖이며 이번 P2 두 편 범위로 확대하지 않았다.

## 재개 조건

1. 기존 사용자 비용 제거 승인 기록과 충돌하는 AGENTS/SCHEMA/설정/상태/프롬프트를 승인된 절차로 일치시킨다. 이번 테스트에서 정책 제한을 임의 우회하거나 보호 지침을 수정하지 않았다.
2. 기존 검증·게시 경로의 위 실패를 수정하고 격리 재검증한다. 특히 mkdir 잠금, 출처/승인/정책 hash 재대조, write-ahead journal·receipt·published_draft 계약을 충족해야 한다.
3. 이후 승인된 codex-lb/gpt-6-astra/xhigh로 실제 HTML 두 편 테스트를 수행한다. 빠른 부분 테스트를 하더라도 P2 두 편 완료로 세지 않는다.

이번 변경 범위는 이 run의 검사 근거와 실제 작업 log append뿐이다. 원본/수집 state/후속 state/정책/검증·게시 코드/Cron/전역 설정은 변경하지 않았다. 커밋·push·신규 설치 없음.
