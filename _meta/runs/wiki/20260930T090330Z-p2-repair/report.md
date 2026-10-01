# P2 정책·검증·게시 결함 수정

## 결과

- 정책 정합화 및 코드 수정 완료. 최종 **108 tests / 0 failures / 0 errors / 0 skipped**.
- 실제 논문 모델 호출·지식 게시·Cron 등록/활성화는 수행하지 않았다. 네트워크/SDK 경계는 합성 클라이언트로 대체했고, 생성기·검증기·게시자와 임시 파일시스템은 실제 코드를 실행했다.
- 원본 **HTML 13편 + PDF 2편 = 15개 버전**, raw/수집 설정·state/compilation state 등 보호 파일 **37개 불변**. root index 불변, 지식 페이지 0개.
- 코드 결함 수정 완료는 실제 논문 독서·의미 검토·장시간 모델 전송 성공 또는 P2 파일럿 완료를 뜻하지 않는다.

## 사용자 승인과 범위

원 요청은 `approval.json`에 그대로 기록했다. AGENTS.md 보호 편집의 최초 승인 요청은 시간초과로 실패했으며 우회하지 않았다. 이후 명시적으로 재요청 가능 여부를 물었고 사용자가 **“보호 편집 승인을 다시 요청”**을 선택했다. 보호 편집 도구 재호출이 성공해 AGENTS도 정합화했다. 이 확인은 실제 논문 호출·게시·자동화 활성화 승인이 아니다.

## 변경 내용

### 정책·비용

- AGENTS/SCHEMA 및 운영 문서: `pkm-html-knowledge/v2`, `pkm-contracts/v2`, P2 수동 파일럿 승인 범위와 자동화 비활성을 일치시켰다.
- automation/schema/prompt 파일의 `wiki-compile/v2`, `research-review/v2` 및 feedback/research-review 상태 revision을 정합화했다. 두 비파일럿 상태는 revision 이외 내용이 기존 snapshot과 동일하다.
- **no_cost_cap**: 금액 상한·사전 비용 예약·계측 검증·강제 차단을 컴파일 조건으로 사용하지 않는다. 미관측 비용은 null이며 0으로 바꾸지 않는다. 양수 비용도 상한 비교 없이 허용한다.
- cost_events 스키마에 reserved_usd=null을 허용해 문서와 게시자 간 충돌을 해결했다. 과거 숫자 기록도 읽을 수 있다.
- 승인·자료 범위·모델 고정·원본 무결성·시간초과·유한 재시도·실패 safety block·사용자 편집 보호는 유지한다.

### 생성·검증

수정 파일은 `_meta/runs/wiki/20260929T083140Z-p2-resume/`의 `compile-one.py`, `verify-one.py`, `compile-instructions.txt`와 `_meta/runs/wiki/20260930T082000Z-p2-nonstream/compile-one-nostream.py`다.

- Import-safe 진입점, 명시적 신규 run 승인, 모델/route/자료/정책 hash gate, 배타적 attempt 예약, 기존 결과 덮어쓰기 금지, 자동 재시도/fallback 금지.
- 스트림·비스트림 모두 실제 응답 completed/model/error/incomplete_details를 확인한다. 실패를 성공 빈 응답으로 바꾸지 않으며 시작만 남은 시도는 unknown으로 보존한다.
- 단일 JSON 객체, 본문 읽기 완료, read/unread 범위, limitations, 고유 claim ID, 주장·조건, 가시 Markdown 인용/링크를 검증한다.
- 인용은 **지정 앵커의 하위 가시 텍스트**에 있어야 한다. 다른 절의 인용·hidden/script/속성 텍스트·중복 앵커·symlink/경로 이탈을 거부한다. 탐색 결과는 메모리에서만 사용하며 원문 추출본을 저장하지 않는다.
- 프롬프트의 statement_ko/condition_ko와 검증기의 statement/conditions 불일치를 해소하고, 누락된 limitations 및 같은 행의 Cxx/출처 링크를 명시했다.

### 게시·복구

수정 파일은 같은 resume 디렉터리의 `publish-one.py`, `close-run.py`다.

- 수집기와 같은 mkdir collection.lock, 소유자 확인/자기 잠금만 해제, KST [23:55, 01:35) 수집 우선.
- 잠금 아래 검증기 재실행 및 입력 hash 재확인. 별도의 주장별 의미 검토 artifact와 게시 요청/편집 중지 승인이 필요하다. 자동 결과는 draft/unreviewed다.
- 실제 Entities 절에 색인을 넣고 페이지 수를 계산한다. work_key/output_refs/receipt/state가 계약과 일치한다.
- fsync된 WAL → page → index → log append → receipt → state. 중단은 조건부 재개하며 이미 게시된 경우 실제 파일·receipt·state를 확인한 후만 no-op 처리한다.
- 사용자 수정, reviewed 페이지, 다른 미해결 거래, 변조/누락 출력은 충돌로 보존한다. 다른 index 절과 log의 새 append를 과거 snapshot으로 되돌리지 않는다. Entities 절 자체의 동시 변경은 보수적으로 충돌 처리한다.
- 부모 통합 시험에서 추가 발견한 생성기/게시자 승인 schema 불일치를 해결했다. 신규 `pkm-p2-run-approval/v1`을 양쪽에서 공유하고 실행·문서·route·원천 hash 및 별도 게시 승인 필드를 대조한다.
- 과거 state/log를 반복 적용하던 close-run.py는 재실행 불가로 폐기했다. import는 무부작용, 직접 실행은 retired/exit 2다. 과거 run-report/final-verification 기록은 덮어쓰지 않았다.

## 실행 근거

- `final-tests.json`, `final-tests.txt`: 부모 세션 통합 재실행, 108개 전부 통과.
- `test_policy_alignment.py`: 네 계약 instance, revision/prompt, 비용 비차단, 범위·자동화 비활성, 비용 사건 null/양수 검증.
- `test_handoff.py`: 프롬프트 계약 정합화, 과거 종료 스크립트 import/재실행 부작용 차단.
- `test_cross_component.py`: 합성 SDK 응답 → 실제 생성기 → 실제 검증기 → 실제 게시 → 반복 no-op. null/양수 비용 및 별도 게시 승인 거부를 확인했다.
- resume 디렉터리의 `test_compile_one.py`, `test_verify_one.py`, `test_publish_one.py`: 생성·검증·게시/복구 회귀.
- RED 근거: `policy-red.txt`, `cost-schema-red.txt`, `handoff-red.txt`, `cross-component-red.txt`, `response-error-red.txt`, verifier/publisher 하위 RED 기록.
- 이전 자식 보고서의 스키마 충돌/AGENTS 차단 상태는 당시 기록이다. **최종 판단은 부모의 final-tests 및 본 보고서를 따른다.**
- `integrity-before-log.json`, `final-verification.json`: 보호 파일, 원본 인벤토리/서지 해시·길이, index, log prefix·단일 append·잠금 해제, 코드 hash 확인.
- `git diff --check`와 Python AST 검사 통과. 커밋·푸시·패키지 설치·전역 설정/다른 프로필 변경 없음.

## 다음 실제 P2 재개

1. 새 run ID로 두 파일럿의 재개 및 필요시 편집 중지·검증된 draft 게시를 확인한다. 이번 repair 승인이나 과거 실패 run을 재사용하지 않는다.
2. `_meta/COMPILATION.md` 및 `_meta/STATE-CONTRACTS.md`의 새 실행/게시 계약으로 실제 입력·route·승인 hash를 기록한다. 실제 upstream 장시간 요청 성공은 아직 확인하지 않았다.
3. 실제 본문 읽기·주장/조건/근거 대조 후에만 의미 검토 artifact를 작성하고 게시한다. 구조 검사만으로 논문 의미 타당성이나 인간 검토 완료를 주장하지 않는다.
4. 비용 계측이나 비용 상한은 재개 조건이 아니다. P3–P6 및 후속 Cron 등록/활성화는 계속 별도 승인 대상이다.
