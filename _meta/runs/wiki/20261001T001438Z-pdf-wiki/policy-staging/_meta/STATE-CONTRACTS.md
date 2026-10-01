# 후속 상태·게시 데이터 계약

Contract `pkm-contracts/v3`, policy `pkm-html-pdf-text-knowledge/v3`. [JSON Schema](automation-contracts.schema.json)의 `$defs`는 automation/compilation/feedback/research_review/compile_request와 공유 pdf_reading const를 정의한다. 상태와 원문은 분리한다. JSON 구문·스키마 통과는 실제 승인·의미적 근거·비용/동시성 안전성을 증명하지 않는다.

## 공통

- UTF-8 JSON, 스키마 이름/버전 일치, 알 수 없는 필드는 차단. 시각은 timezone-aware ISO 8601; 사건·창은 UTC로 정규화하고 관측 비용 사건의 날짜는 KST로 기록한다. 일일 비용 상한은 없다.
- 상대경로는 root 안에 있어야 하고 symlink/경로 이탈을 금지한다. ID는 원문 그대로 검증하며 malformed ID를 고쳐서 조회하지 않는다.
- 모든 상태 갱신은 승인된 거래에만 포함하며 flush/fsync/원자 교체. 로그와 journal 사건은 삭제하지 않는다. 정책/프롬프트 변경 시 revision과 hash를 갱신하고 이전 승인 범위를 다시 검토한다.
- `enabled=false`는 후속 처리 비활성이다. P1 당시 초기 HTML은 `blocked_approval`, PDF는 `blocked_policy`였다. v3 정책 적격 PDF는 `blocked_approval`에서 실행 gate를 기다리며 수집 완료 상태를 바꾸지 않는다.

## compilation.json

파일 schema `pkm-compilation-state/v1`. 필수 최상위 필드는 policy_revision, contract_revision, initialized_at, enabled, safety_block, safety_block_reason, items, transactions, receipts, cost_events, last_run이다.

각 item은 source/version_id/format/source_path/source_sha256/source_bytes/metadata_path/metadata_sha256/collected_at, status/reason, requested_scope/read_scope/unread_scope/resume_at, work_key/output_refs/receipt_ref/failure_count/human_review를 가진다. 경로·hash·길이는 실제 파일에서 얻는다. read_scope/unread_scope는 원본 절·앵커/행 범위 또는 PDF 물리적 1-based 페이지 범위를 식별하는 문자열 목록이지 추출 본문이 아니다. 처음에는 읽은 범위가 없고 실제 독서 전 문서 구조나 미독 절을 추측해 채우지 않는다.

허용 전이:

| 이전 | 다음 | 조건 |
| --- | --- | --- |
| blocked_approval | queued | 해당 단계의 실제 사용자 승인·모델 경로·자료/무결성 gate 확인; 비용 비차단 |
| queued | reading | 승인된 요청 범위, work_key, 원본 무결성 확인 |
| reading | partial | 실제 읽은/미독 범위·재개 위치 기록; receipt 없음 |
| partial | reading | 같은 입력/정책/출력 snapshot 검증 뒤 재개 |
| reading | ready_to_publish | 요청 범위·핵심 주장/수치 근거와 미검토 항목 검증 |
| ready_to_publish | published_draft | 지식/index/log/receipt/완료 state 거래 검증 |
| 처리 중 | blocked_conflict | 원본/정책/사용자 출력/경로 충돌; 덮어쓰기 없음 |
| 처리 중 | retryable_failed | 한도 안의 실제 일시 업무 실패; 실패 수 증가 |
| blocked_policy | blocked_approval | v3에서 PDF 내장 텍스트의 정책 적격을 확인한 경우만; reason=pdf_text_policy_eligible_pending_execution_gate, 자동 queued 전이 금지 |

`published_draft`에는 승인된 HTML 또는 PDF 내장 텍스트 범위, work_key, 비어 있지 않은 read_scope/output_refs 및 receipt가 필요하다. 완료 state만 있고 파일/receipt가 없으면 복구 대기이지 no-op이 아니다. partial 읽기로 페이지를 만들었으면 requested_scope 자체를 partial로 명시하며 “전문 완료”와 구분한다. P2의 두 편 완료 기준은 본문/결론과 실제 방법·평가 읽기 범위가 충족되어야 하며 partial 두 개로 대체하지 않는다.

work_key는 UTF-8 JSON(sort_keys=true,separators=(',',':'),ensure_ascii=false)의 SHA-256이다. 키 입력은 source, version_id, source_sha256, policy_revision, policy_sha256, prompt_revision, prompt_sha256, requested_scope다. 실행 ID/시각/모델/실제 범위는 run에 별도 기록한다. 모델 변경만으로 전체 재생성하지 않는다. 승인된 모델 변경과 재검토 요청이 있어야 한다.

output_refs는 path/sha256/revision 목록이다. no-op에는 같은 key, 실제 출력 전체 hash, 완료 receipt, unresolved 거래 없음, 적용 정책/범위 일치가 모두 필요하다. 사용자 수정은 충돌/수동 편집으로 분류한다. 개념/비교는 원출처 집합과 소비 page revision/hash를 별도 영향 목록으로 관리한다.

## 피드백·연구 상태

- `pkm-feedback-state/v1`: 사건은 event_id가 고유하고 동일 feedback_id의 전이를 append한다. actor(user/agent), target_page/target_sha256, claim_ref/content/evidence_refs, status, reason, affected_pages, created_at/committed_at, user_save_request_ref, sensitive=false가 필수다. [피드백 계약](QUERY-FEEDBACK.md)을 따른다.
- `pkm-research-review-state/v1`: anchor_utc, window_days=14, last_successful_window_end, windows/carryover/ideas/consumed_event_ids/cost_events를 가진다. anchor가 null이면 창 처리 금지. [연구 리뷰 계약](RESEARCH-REVIEW.md)을 따른다.
- selected 아이디어에는 사용자의 정확한 idea_id/revision/page_sha256에 대한 decision_ref/decision_at/decision_reason이 있어야 한다. JSON Schema가 이를 모두 의미 검증하지 않으므로 소비자가 결정 provenance를 대조한다. 기존 선택 뒤 revision/hash가 바뀌면 다시 선택받는다.

## journal·receipt의 필수 의미 계약

P2 구현의 `_meta/runs/wiki/<run-id>/<VID>/<attempt>-publish-journal.json`은 plan/plan_sha256 봉투 안의 `schema: pkm-publication-journal/v1` 계획으로 다음을 포함한다: transaction_id, run_id, role, started_at, approval_refs, policy/prompt/input hashes, targets(path,before_hash 또는 null,after_hash,order,stage), log_event_id, status. knowledge target에는 before_image_ref/after_image_ref와 실제 before/after bytes를 포함한다. log는 before prefix bytes/hash와 append event 내용을 기록하며 과거 전체 snapshot으로 롤백하지 않는다. index는 소유한 Entities 절과 페이지 수 header를 조건부 비교하며 다른 절과 log의 새 append는 보존한다.

같은 attempt의 `<attempt>-receipt.json`은 `schema: pkm-publication-receipt/v1`로 transaction/run/work key, actual input/output hashes, committed_at, read_scope/unread_scope, evidence_check_ref, structural_check_ref, human_review_ref 또는 null, model route metadata, budget_usage_ref를 포함한다. 다중 파일 공개가 원자적이라고 주장하지 않는다. state의 published_draft와 receipt가 일치하고 파일 실물이 검증되어야 소비 가능하다. 게시·중단 복구의 합성 fixture 검증은 [P2 결함 수정 보고서](runs/wiki/20260930T090330Z-p2-repair/report.md)에 기록하며 실제 논문 의미 검토/게시 완료와 구분한다.

## 비용·실패

cost_events는 event_id/run_id/role(pilot,daily_compile,research_review)/scope_id/created_at/kst_day/status/reserved_usd/charged_usd/usage_receipt를 기록한다. 역할별 상한은 폐지되었으므로 reserved_usd는 null을 쓴다. status는 reserved/settled/unknown이며 실제 비용 미관측은 charged_usd=null, 0이 아니다. event_id 중복을 거부한다. 관측된 사용량은 회신 메타데이터에서 정산하며, 요청 전 차단·잔여량 검증은 v2에서 요구하지 않는다. 사건의 KST 날짜와 장기 실행의 날짜 경계 비용 배분도 계측 근거로 정한다.

run 결과는 noop/partial/blocked_policy/blocked_approval/skipped_busy/integrity_conflict/model_timeout/publish_interrupted/committed로 구분한다(v2에서 blocked_budget/budget_exhausted 제거). 이 결과 코드는 item 상태 열거형과 다르다. 실패를 정상 빈 결과로 바꾸지 않는다. local safety_block은 스케줄러 pause가 아니며 운영자 승인과 원인 수정 없이는 해제하지 않는다.

## schema 검증의 경계

compile_request(v3)는 승인된 provider/model/reasoning, fallback_allowed=false, phase_execution_approved=true, source_approval_id와 phase_approval_ref, images/external_assets/ocr/pdf_binary_transfer/persistent_extraction=false, `cost_policy: no_cost_cap` 및 비용 제거 승인 근거를 요구하는 **검증 입력 형식**이다. PDF branch는 source_format=pdf, source_path가 source.pdf, pdf_analysis=true, input_mode=embedded_text_only, pdf_reading=정확한 const 객체다. HTML branch는 source_format=html, source_path가 source.html, pdf_analysis=false, input_mode=html_direct_text, pdf_reading=null이며 PDF 권한을 얻지 않는다. 이것은 실행기/API가 아니며 true 플래그만으로 승인을 위조할 수 없다. 실제 근거 경로 존재/해시/권한·ID 고유성·창 경계·상태 전이는 별도 의미 검증한다. 승인 부재 시 이 요청을 생성·실행하지 않는다. 과거 부정 시험은 가상 객체만 검사했다.

## Legacy P2-v2 실행기·게시자 연결 — v3에 재사용할 승인 형식 아님

- 신규 run의 실행 승인은 `pkm-p2-run-approval/v1`이다. 실제 사용자 확인, 정확한 root/run/두 version_ids, 정책·문서·프롬프트·instructions·원천 hash, codex-lb/gpt-6-astra/xhigh, 승인 route, 과거 시도 검토, 최대 2회 시도를 묶는다. 과거 run/시작 기록/결과를 재사용하거나 덮어쓰지 않는다.
- 게시까지 승인한 run이면 같은 승인에 `publication_edit_freeze_confirmed=true`, `validated_draft_publication_authorized=true`, 사용자 요청/확인 범위, fallback=false, PDF·이미지·자산=false, no_cost_cap와 기존 P2 승인 참조가 추가로 필요하다. 이 필드가 없으면 컴파일 결과가 있어도 게시하지 않는다. 기존 resume 승인 형식은 별도 호환 경로이며 신규 실행기는 새 형식만 받는다.
- 게시 요청 `pkm-publication-request/v1`과 별도 `pkm-agent-evidence-review/v1`은 실제 의미 대조 후 작성한다. 결과/source/policy/prompt/approval hash, 모든 reviewed_claim_ids, 실제 evidence_scope, 각 주장의 anchor/quote_sha256/supported/rationale를 묶는다. 구조 검증 true나 모델의 완료 플래그를 의미 검토로 복사하지 않는다. 에이전트 검토는 human review가 아니다.
- 생성 JSON의 claims는 id/kind/statement/conditions/anchor/quote를 사용한다. limitations와 실제 read_scope/unread_scope를 요구하며 Cxx와 대응 source 앵커 링크는 같은 가시 Markdown 행에 둔다. 전체 입력 전달은 전체 읽기/의미 검토 완료 증거가 아니다.

## PDF 텍스트 승인 경계 — v3

- 정책 `pkm-html-pdf-text-knowledge/v3`, 계약 `pkm-contracts/v3`. 승인 근거는 `_meta/runs/wiki/20261001T001438Z-pdf-wiki/scope-approval.json`이다. 기존 `2609.30614v1`, `2609.30824v1`의 수동 PDF 텍스트 컴파일·검증 후 게시와 작업 중 편집 중지는 별도로 승인되었지만, 이 정책 준비는 실제 읽기·생성·게시 완료가 아니다.
- 향후 PDF도 정책상 대상이 될 수 있으나 정확한 입력·단계·모델·무결성·게시/편집 중지 등 정상 실행 승인이 먼저 필요하다. P3/P4/P5/P6는 미승인, 자동화 enabled=false, 신규 Cron 미등록이다. 정책 준비자는 두 PDF를 `blocked_approval`/`pdf_text_policy_eligible_pending_execution_gate`로만 전환하며 실행 gate 확인과 queued 전이는 부모 실행 담당자의 책임이다.
- 승인된 최소 읽기 환경 `.venv-pdf-reader`의 표준 `pypdf`로 로컬 `source.pdf`의 내장 텍스트만 페이지별로 메모리에서 읽는다(`embedded_text_only`). 삭제된 PyMuPDF/Docling/Marker 전처리 환경 복원이 아니며 새 커스텀 수집기·파서·DB를 만들지 않는다. 지속 추출본·compile-input·chunk·렌더·이미지·OCR·외부 자산은 금지한다.
- 모델 전송은 `codex-lb/gpt-6-astra/xhigh`의 PDF 텍스트에만 허용한다. `transfer.pdf_content=true`는 **PDF 텍스트만** 뜻하며 PDF 바이너리 전송은 false다. fallback 금지, `no_cost_cap`, 미관측 비용 null을 유지한다.
- PDF 인용은 `source.pdf#page=N`이며 N은 인쇄 쪽수가 아닌 **물리적 1-based 페이지**다. 실제 읽은 페이지, 페이지별 텍스트 길이(Unicode 문자 수), 추출 품질/누락, 미독 범위를 run 근거에 기록한다. page 수나 읽기를 추정하지 않고 이미지/그림은 미검토로 남긴다. 텍스트층 없음·손상·빈 페이지·읽기 실패는 blocked/partial로 남기며 OCR로 우회하지 않는다. PDF 원문 텍스트 전체를 run/prompt/debug 로그에 영구 저장하지 않는다. 짧은 근거 인용과 길이·품질 메타데이터는 지식/검증 근거다.
- `source.json`의 `wiki_compiled:false`와 기존 원본은 수집 당시 불변 이력이다. prior v2 run/page/receipt와 성공 항목을 v3로 다시 쓰지 않는다. outer state의 policy/contract revision만 이관하고 기존 성공/실패 근거를 보존한다.
- 기존 `compile-one.py`/`verify-one.py`/`publish-one.py`는 **legacy P2-v2**이며 v3 지원 근거가 아니다. 가드를 완화하지 않는다. 부모는 표준 pypdf와 재사용한 안전 IO/runtime helper로 한정된 수동 v3 처리를 별도 수행·검증하며 자동화 준비 완료를 주장하지 않는다.
- 기존 수집 Cron `4cff5b4f10ec`는 **collect-only**다. PDF 원본 저장만 하며 PDF 텍스트 추출·본문 분석·Wiki 컴파일을 하지 않는다. 이번 승인으로 수집 프롬프트·스케줄·state를 변경하지 않는다.

### v3 계약·이관의 의미 검증

- automation.pdf_reading은 다음 **정확한 const 객체**이며 추가 키/누락 키/true 전환을 허용하지 않는다. compile_request의 PDF branch도 동일 객체를 요구한다.

```json
{"mode":"embedded_text_only","library":"pypdf","environment":".venv-pdf-reader","pdf_binary_transfer":false,"images":false,"ocr":false,"external_assets":false,"persistent_extraction":false,"page_citation":"physical_1_based"}
```

- automation.pdf_text_policy_approval_ref는 이 정책의 scope-approval을 가리킨다. 기존 approval/approval_amendment_ref는 역사적 승인으로 보존한다. source_approval_id와 phase_approval_ref 문자열이 존재한다고 승인된 것이 아니며 실제 정확한 run/ID/정책·프롬프트 hash/자료 범위와 실행 gate를 대조한다. 이번 두 PDF의 수동 승인은 다른 PDF나 P3–P6 실행 권한이 아니다.
- 세 상태 파일의 schema 식별자(v1)는 유지하고 outer policy_revision/contract_revision만 v3로 이관한다. 기존 HTML 항목 전체, receipts/transactions/cost_events/last_run 및 prior v2 run/page/receipt의 revision/hash는 그대로 둔다. PDF 두 항목은 status/reason만 바꾸며 read_scope/unread_scope, page, attempt, 완료 시각/receipt를 꾸미지 않는다.
- PDF의 read_scope는 실제 물리적 페이지와 읽은 텍스트 범위를, unread_scope는 미독/이미지/불명료 표 등을 구분한다. 실제 page_count·페이지별 text_length(Unicode 문자 수)/extraction_quality와 reader 버전은 run의 메타데이터 근거에 남긴다. `source.pdf#page=N` N의 범위·대응 quote·실제 읽기/추출 품질·완전성은 별도 의미 검증한다. 상태 스키마는 PDF published_draft 구조를 허용하지만 존재하는 실제 receipt/evidence·page 숫자의 진실성까지 증명하지 않는다.
- 공개된 v2 evidence를 새 정책으로 소급 재검증해 바꾸지 않는다. legacy v2 tests는 frozen v2 fixture/schema로 실행하고 v3 tests와 분리한다. legacy 코드 가드를 약화하지 않는다. v3 안전 IO 재사용은 v3 생성·검증·게시 전체 동작이 이미 증명되었다는 뜻이 아니다.
