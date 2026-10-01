# Biweekly Research Review — research-review/v3

Contract `pkm-contracts/v3`; policy `pkm-html-pdf-text-knowledge/v3`. Prepared prompt only; **P5 미승인, Cron 미등록, anchor 미정**.

## TASK / PREFLIGHT

대상은 `/home/ainsdev/wiki/pkm-articles` 하나. `SCHEMA.md` 전체 → `index.md` → `log.md` 최근 → `_meta/AUTOMATION.md`, `_meta/automation.json`, `_meta/STATE-CONTRACTS.md`, `_meta/RESEARCH-PROFILE.md`, `_meta/QUERY-FEEDBACK.md`, `_meta/RESEARCH-REVIEW.md`, 세 후속 state를 읽는다. llm-wiki와 brainstorming-research-ideas를 사용하되 다른 도구/모델/검색을 자동 확장하지 않는다.

P5 실행·등록·활성화 승인, enabled/job enabled, 정확한 Cron ID/프롬프트 hash/model pin/workdir/skills/local 전달/readback, 승인된 anchor가 모두 필요하다. 현재 P5의 이 값들은 미충족이다. PDF 수동 승인으로 P5가 승인되지 않는다. 미승인 단계는 blocked_approval이며 스스로 설정을 바꾸거나 실행하지 않는다. 안전 차단/정책·스키마 불일치/미완료 거래는 중단한다.

provider `codex-lb`, model `gpt-6-astra`, reasoning `xhigh`; fallback 금지. 허용 입력은 기존 committed Wiki, 필요시 해당 단계/범위로 승인된 로컬 HTML 또는 PDF 내장 텍스트, 명시적으로 저장 요청된 비민감 피드백뿐이다. PDF 바이너리/이미지/OCR/외부 자산/전체 대화 자동 수집/민감 정보/외부 신규성 검색 금지. 실제 route 확인이 없으면 본문을 읽거나 호출하지 않는다. 금액 상한·비용 차단 게이트는 policy v2에서 제거되었으며 unknown 비용은 null로 기록하고 0이 아니다. 45분은 협조적 한도다. 위임/비판 역할을 나누더라도 승인 모델을 우회하지 않는다.

## INPUT WINDOW

UTC anchor 기준 고정 `[start,end)` 14일 창. 처리 기준은 논문 출판/수집 시각이 아닌 실제 committed_at이다. 성공 창 다음의 가장 오래된 닫힌 창 최대 1개/실행을 처리한다. every 14d 발화 지연은 창 정의를 바꾸지 않는다. 사전 지식의 bootstrap/carryover는 승인된 목록만 포함한다.

입력 revision/hash/사건 ID와 미독/partial/PDF 텍스트층 문제·이미지 미검토/철회 영향/unresolved 거래를 동결한다. 과거 관련 지식은 배경으로 읽되 같은 원출처를 독립 근거로 반복 계산하지 않는다. late item은 원래 사건 시각/창, 실제 소비 창, 이유를 기록한다. 실패 입력을 consumed로 표시하거나 입력 확인 실패를 empty로 위장하지 않는다.

## DELIVERABLE

1. 개인 학습공백·문헌 수집공백·연구공백 후보를 분리한다.
2. 발산 뒤 별도 비판 관점으로 반례/중복/기각 이력/실행 가능성을 대조한다. 다수 AI의 동의는 신규성 인증이 아니다.
3. `queries/research-review-<window-id>.md` 창별 1개와 `queries/research-idea-<idea-id>.md` 추천 0–3개를 draft/type=query/last_reviewed=null로 작성한다. 후보가 없으면 없다고 보고한다.
4. 후보마다 문제/수혜자, 두 문장 pitch, 실제 읽은 근거·반대 근거, 반증 가능한 가설, 코퍼스의 최근접 연구와 차이, novelty_unverified, 최소 실험/기준선/지표/반증·중단 조건, 자원 unknown, 예상 반론, 추천 이유, 사용자 결정 상태를 기록한다. “Wiki에 없음”을 “학계에 없음”으로 쓰지 않는다.
5. 실험·코드 실행·데이터 다운로드·GPU 사용·논문 제출은 하지 않는다. 사용자 selected 기록이 없는 아이디어 또는 별도 P6 실행/비용 승인이 없는 제안서는 집필하지 않는다. 가짜 결과/수치/인용 없음.

## PUBLISH / VERIFY / STOP

허용 쓰기는 승인된 review/idea query 페이지, research-review state, index, append-only log, `_meta/staging/wiki/<run-id>/`, `_meta/runs/wiki/<run-id>/`뿐이다. raw/source.json/수집 상태·검색식·Cron/정책/전역 설정/다른 Wiki 변경 금지. 기존 사용자 편집/reviewed 문서/10개 이상 기존 페이지 변경은 승인 대기다.

긴 분석 중 잠금을 풀고 KST 23:55–01:35 게시 금지. collection.lock 원자 획득, 사용자 편집 중지, 마지막 정책/승인/입력/출력 hash/신규 경로 부재 확인, 최신 index/log 병합, 내구 journal → 페이지 → index → 중복 없는 log → 검증 receipt → 창 포인터/consumed ID 완료 state 순서다. 미완료 거래는 소비하지 않는다. busy skip, 고아 잠금 탈취 금지, 자기 잠금만 해제한다. unexpected hash면 충돌, raw/수집 checkpoint/log의 과거 snapshot 복구는 금지다.

정상 empty는 입력 열거 검증 후 보고서·empty receipt로만 완료한다. 실패 창은 포인터를 전진하지 않는다. 창 경계/ID 고유성/receipt/실제 파일 hash/링크/지식 수/출처/관측 사용량을 코드와 의미 검토로 구분해 확인한다. 결과는 local이며 자동 TUI 알림을 약속하지 않는다. 실제 업무 실패는 `[CRON_FAILURE]`; 승인/정책 차단과 busy/무변경을 구분하고 run 근거를 남긴다. 비용 미관측은 실행 차단이 아니다. 계획된 계약이나 파일 생성만으로 모델 실행/의미 검토/회복 성공을 주장하지 않는다.

## PDF 텍스트 승인 경계 — v3

- 정책 `pkm-html-pdf-text-knowledge/v3`, 계약 `pkm-contracts/v3`. 승인 근거는 `_meta/runs/wiki/20261001T001438Z-pdf-wiki/scope-approval.json`이다. 기존 `2609.30614v1`, `2609.30824v1`의 수동 PDF 텍스트 컴파일·검증 후 게시와 작업 중 편집 중지는 별도로 승인되었지만, 이 정책 준비는 실제 읽기·생성·게시 완료가 아니다.
- 향후 PDF도 정책상 대상이 될 수 있으나 정확한 입력·단계·모델·무결성·게시/편집 중지 등 정상 실행 승인이 먼저 필요하다. P3/P4/P5/P6는 미승인, 자동화 enabled=false, 신규 Cron 미등록이다. 정책 준비자는 두 PDF를 `blocked_approval`/`pdf_text_policy_eligible_pending_execution_gate`로만 전환하며 실행 gate 확인과 queued 전이는 부모 실행 담당자의 책임이다.
- 승인된 최소 읽기 환경 `.venv-pdf-reader`의 표준 `pypdf`로 로컬 `source.pdf`의 내장 텍스트만 페이지별로 메모리에서 읽는다(`embedded_text_only`). 삭제된 PyMuPDF/Docling/Marker 전처리 환경 복원이 아니며 새 커스텀 수집기·파서·DB를 만들지 않는다. 지속 추출본·compile-input·chunk·렌더·이미지·OCR·외부 자산은 금지한다.
- 모델 전송은 `codex-lb/gpt-6-astra/xhigh`의 PDF 텍스트에만 허용한다. `transfer.pdf_content=true`는 **PDF 텍스트만** 뜻하며 PDF 바이너리 전송은 false다. fallback 금지, `no_cost_cap`, 미관측 비용 null을 유지한다.
- PDF 인용은 `source.pdf#page=N`이며 N은 인쇄 쪽수가 아닌 **물리적 1-based 페이지**다. 실제 읽은 페이지, 페이지별 텍스트 길이(Unicode 문자 수), 추출 품질/누락, 미독 범위를 run 근거에 기록한다. page 수나 읽기를 추정하지 않고 이미지/그림은 미검토로 남긴다. 텍스트층 없음·손상·빈 페이지·읽기 실패는 blocked/partial로 남기며 OCR로 우회하지 않는다. PDF 원문 텍스트 전체를 run/prompt/debug 로그에 영구 저장하지 않는다. 짧은 근거 인용과 길이·품질 메타데이터는 지식/검증 근거다.
- `source.json`의 `wiki_compiled:false`와 기존 원본은 수집 당시 불변 이력이다. prior v2 run/page/receipt와 성공 항목을 v3로 다시 쓰지 않는다. outer state의 policy/contract revision만 이관하고 기존 성공/실패 근거를 보존한다.
- 기존 `compile-one.py`/`verify-one.py`/`publish-one.py`는 **legacy P2-v2**이며 v3 지원 근거가 아니다. 가드를 완화하지 않는다. 부모는 표준 pypdf와 재사용한 안전 IO/runtime helper로 한정된 수동 v3 처리를 별도 수행·검증하며 자동화 준비 완료를 주장하지 않는다.
- 기존 수집 Cron `4cff5b4f10ec`는 **collect-only**다. PDF 원본 저장만 하며 PDF 텍스트 추출·본문 분석·Wiki 컴파일을 하지 않는다. 이번 승인으로 수집 프롬프트·스케줄·state를 변경하지 않는다.

P5 승인 후에도 PDF 본문을 새로 읽거나 전송하려면 그 단계의 자료/모델/실행 gate를 별도로 통과해야 한다. 이미 committed인 PDF 기반 Wiki를 읽는 것과 PDF의 새 읽기를 구분하며 source.pdf#page=N의 물리적 페이지·짧은 quote·페이지별 텍스트 길이/품질 근거를 유지한다. 이번 scope-approval은 두 PDF의 수동 컴파일·검증 후 게시만을 허용하고 연구 리뷰 실행은 허용하지 않는다.
