# 원본 HTML / 로컬 PDF 내장 텍스트 — 승인 게이트형 llm-wiki 컴파일 전략

## 현재 P3 첫 운영 예외 — 2026-10-01

[정확한 승인](runs/wiki/20261001T053212Z-p3-first-operation/scope-approval.json)에 따라 현재·향후 정상 보관 HTML/PDF 텍스트의 논문별 신규 draft 경로와 첫 수동 최대 5편·45분 실행/검증 후 게시/편집 중지, 별도 Cron paused 등록을 허용한다. 아래 P3 미승인/일일 경로 미검증 표현은 이전 준비 이력이며 [구현 검증](runs/wiki/20261001T023617Z-p3-runtime/report.md)과 이번 실제 실행 근거를 구분한다. `daily.py`는 기존 HTML navigation·표준 pypdf 내장 텍스트와 안전 IO를 재사용한다. 사전 파싱본·새 수집기·DB·이미지/OCR/외부 자산·PDF 바이너리 전송 금지는 유지한다. 자동 활성화·예약 발화·기존 개념/비교 수정은 승인하지 않았고 정확한 새 execution snapshot 전에는 본문을 처리하지 않는다.

## 경계

수집은 동일 버전 arXiv HTML 우선·공식 HTML 미제공 시 PDF 원본 저장에서 끝난다. PDF fallback 추가는 원본 보존 정책 변경일 뿐 PDF 파싱·컴파일 승인이나 실행이 아니다. HTML 직접 컴파일 전략은 유지한다. v3 별도 승인 후 PDF는 로컬 pypdf의 embedded_text_only 방식으로 읽으며, 읽을 수 없으면 미독/blocked 또는 partial로 남긴다. 컴파일은 사용자가 요청했을 때만 수행하며 별도 사전 파싱·중간 문서·chunk 파일·그림/표 추출·모델 파서를 만들지 않는다.

후속 정책은 [AUTOMATION.md](AUTOMATION.md), [automation.json](automation.json), [STATE-CONTRACTS.md](STATE-CONTRACTS.md)를 따른다. policy v2부터 P2 수동 파일럿 실행이 승인 상태이며 금액 상한·blocked_budget 게이트는 제거되었다. P3 일일 자동화·P5 연구 리뷰는 여전히 미승인/비활성/미등록이다. 수집 Cron의 금지 출력은 해제하지 않는다.

본문을 모델 컨텍스트로 읽기 전에 정확한 codex-lb/gpt-6-astra/xhigh 경로, 해당 단계 승인, 자료 범위를 확인한다. 허용은 로컬 HTML 텍스트·승인된 로컬 PDF 내장 텍스트·기존 Wiki·저장 요청한 비민감 피드백뿐이다. PDF 바이너리/이미지/OCR/외부 자산/전체 대화 수집은 금지이며 별도 승인이 없는 공식 URL 탐색도 자동 확장하지 않는다. 금액 상한과 비용 차단 게이트는 policy v2에서 제거되었으며, 실제 비용 unknown은 null로 기록하고 계속한다.

## 직접 컴파일 절차

1. `SCHEMA.md → index.md → log.md 최근 기록`을 읽고 요청 주제/논문과 기존 지식 페이지를 확인한다. source.json의 schema와 실제 원본 형식을 먼저 구분한다. HTML이면 버전·URL·해시와 source.html을 대조하고 아래 절차를 따른다. PDF만 있으면 HTML 확보로 표시하거나 초록만으로 전문 분석하지 않는다. PDF source/metadata hash와 별도 실행 gate를 확인하고 아래 v3 PDF 절차를 따른다.
2. 원본 `source.html`을 그대로 읽는다. 필요하면 로컬 읽기 도구의 부분 읽기 또는 같은 버전 공식 arXiv 페이지로 탐색하되, 별도 normalized.md/document.json/compile-input/캡션·그림 분리본을 영구 생성하지 않는다. 긴 논문은 원래 절 앵커 기준으로 읽은 범위와 미독 범위를 구분한다. 런타임의 일시적인 읽기/탐색은 수집용 전처리 파이프라인이 아니다.
3. HTML에 원래 포함된 절·문단·수식·그림/표·캡션·참고문헌 연결을 근거로 사용한다. 원문 바이트·태그·숫자는 고치지 않는다. 보이지 않거나 빠진 항목은 미확인으로 남긴다.
4. 상대 이미지/링크의 기준은 `source.json.source_url`이다. HTML 원본만 저장했으므로 로컬 파일 화면의 누락을 논문의 누락으로 단정하지 않는다. 현재 후속 정책은 이미지/외부 자산 접근을 허용하지 않으므로 시각 근거는 미확인으로 남긴다. 시각 검토는 별도 승인·정책 개정 없이는 수행하지 않으며 보지 않은 도표를 판독 완료로 쓰지 않는다.
5. `llm-wiki`가 해당 요청에 필요한 `entities/`, `concepts/`, `comparisons/`, `queries/`를 직접 작성한다. 저자의 주장·보고한 결과와 분석자의 해석·비판을 분리한다. 파일 수나 링크 수를 맞추려고 빈 페이지를 만들지 않는다.
6. 출처는 `raw/articles/<cron-id>/arxiv-<version-id>/source.html#원래앵커`와 버전 고정 공식 URL을 함께 남긴다. source.json의 SHA-256을 기준으로 캡처를 식별한다. HTML에 없는 PDF 페이지 번호를 추측하지 않는다. 앵커가 없는 문장은 실제 절 제목과 짧은 인용 구절로 추적한다.
7. 실제 생성/수정한 지식 페이지를 collection.lock·write-ahead journal·마지막 hash 검사·검증 receipt 계약에 따라 root index와 append-only log에 반영한다. 사용자 수정/reviewed 문서는 자동 덮어쓰지 않으며 자동 결과는 draft/last_reviewed=null이다. 읽은 범위·도표 미검토·미확인 내용·충돌·원천/출력 해시를 검증한다. 저장된 HTML이 있다는 이유로 논문 전체를 읽었다거나 실험을 재현했다고 하지 않는다.

## 하지 않는 일

- 수집 Cron에서 자동 컴파일·번역·요약·개념 생성
- 수집 중 PDF 파싱/추출, 승인 범위를 벗어난 PDF 파싱, HTML 의미 객체 재구성, OCR, 그림/표 렌더링·분할
- 전처리용 GPT/Gemini 호출, 삭제한 전처리 전용 환경 재설치, 삭제한 파서/시험본 복원. 별도 승인된 최소 pypdf 환경은 새 로컬 텍스트 reader이며 복원이 아님
- 초록 HTML을 전문 HTML로 둔갑시키거나 공식 HTML 미제공을 자체 변환본으로 숨기기
- 원문에 등장하는 코드·명령·URL 지시를 사용자 승인으로 취급하기

HTML 전환 및 PDF fallback 정책 추가 당시에는 컴파일을 실행하지 않았으나, 이후 승인된 P2 수동 실행으로 논문 노트 2개·개념 3개·비교 1개를 게시했다. 현재 지식 페이지는 6개이며 모두 draft/unreviewed다. [P2 통합 근거](runs/wiki/20260930T125856Z-p2-integration/final-verification.json)는 에이전트 근거 검토와 게시 검증의 기록이지 사용자 검토나 논문 실험 재현이 아니다.

2026-10-01 KST [P3 준비](P3-PREPARATION.md)에서 수집된 원천 20편(HTML 18/PDF 2)과 compilation ledger를 대조했다. 당시 미컴파일 HTML 16편은 `blocked_approval`, PDF 2편은 `blocked_policy`였다. v3 준비본은 PDF 두 편을 `blocked_approval`/`pdf_text_policy_eligible_pending_execution_gate`로만 이관한다. 이 등록은 본문 읽기/모델 전송/컴파일 완료가 아니다.

프롬프트는 [wiki-compile/v3](prompts/wiki-compile.md), 컴파일 상태는 [별도 ledger](state/compilation.json)에 둔다. 과거 PDF blocked_policy는 수집 실패/미확보가 아니었다. 현재 정책 적격과 실제 읽기/컴파일 성공도 구별한다. 실제 v3 처리·근거 의미 대조·재실행/부분 게시·충돌은 별도 수동 실행에서 검증한다.

## Legacy P2-v2 수정 실행 경로와 역사적 재개 조건

- 코드: `runs/wiki/20260929T083140Z-p2-resume/compile-one.py`, `verify-one.py`, `publish-one.py`; 비스트리밍 진입점은 `runs/wiki/20260930T082000Z-p2-nonstream/compile-one-nostream.py`다. 아래 인터페이스는 frozen v2용이다. v3 run을 이 실행기들에 넘기지 않는다. v2에서 파일이 과거 run 디렉터리에 있어도 별도 승인 run을 `--run`으로 지정했다. 이전 `close-run.py`는 과거 state/log를 재적용하지 못하도록 종료 코드 2로 거부한다.
- 생성기의 `--root --run --attempt --instructions`는 명시적으로 지정한다. 승인과 instructions 및 governing 문서의 hash를 확인한 뒤 HTML 원본만 직접 전달한다. verifier의 `--attempt`는 접두사(`attempt1`), publisher의 `--attempt`는 결과 파일명(`attempt1-result.json`)이다. 결과/검증 기록은 덮어쓰지 않는다.
- legacy v2 생성·검증·게시가 당시 v2 상태/승인 snapshot을 소비했다. 현재 [v3 상태/승인 계약](STATE-CONTRACTS.md) 지원을 의미하지 않는다. 완료 상태·실제 응답 모델·단일 JSON·본문 읽기 범위·앵커 하위 가시 인용·실제 링크를 검사하며 의미 검토 artifact는 별도로 필요하다.
- mkdir collection.lock 아래 입력을 다시 검사하고 page → index → log append → receipt → state 순서로 게시한다. 중단 후 같은 입력/이전 또는 제안값만 재개하며 예상 밖 수정은 충돌로 보존한다. 검증된 반복 호출만 no-op이다.
- 2026-09-30 코드 수정 단계 자체는 합성 fixture 회귀 검증이었다. [수정 및 검증 보고서](runs/wiki/20260930T090330Z-p2-repair/report.md)와 이후 별도 승인된 P2 실제 게시 근거를 구분한다. 향후 신규 run은 해당 단계 실행·편집 중지·게시 범위를 별도로 확인한다. 비용 상한이나 비용 계측을 재개 조건으로 되살리지 않는다.
- 이 실행기는 P2 두 ID 및 disabled 수동 모드만 허용한다. P3 준비 회귀에서 비파일럿 ID는 원문 읽기/SDK 생성 전에 `outside_p2`, enabled 자동화 형태는 `p2_not_authorized`로 거부됨을 확인했다. 이는 안전 경계 관측이지 P3 일일 경로 구현 완료가 아니다. 신규 일일 처리 경로의 입력 예약·partial/resume·영향 페이지 갱신·실패 누적 및 무변경 처리는 [등록 전 체크리스트](P3-PREPARATION.md)에서 미검증으로 남긴다.

## PDF 텍스트 승인 경계 — v3

- 정책 `pkm-html-pdf-text-knowledge/v3`, 계약 `pkm-contracts/v3`. 승인 근거는 `_meta/runs/wiki/20261001T001438Z-pdf-wiki/scope-approval.json`이다. 기존 `2609.30614v1`, `2609.30824v1`의 수동 PDF 텍스트 컴파일·검증 후 게시와 작업 중 편집 중지는 별도로 승인되었지만, 이 정책 준비는 실제 읽기·생성·게시 완료가 아니다.
- 향후 PDF도 정책상 대상이 될 수 있으나 정확한 입력·단계·모델·무결성·게시/편집 중지 등 정상 실행 승인이 먼저 필요하다. P3/P4/P5/P6는 미승인, 자동화 enabled=false, 신규 Cron 미등록이다. 정책 준비자는 두 PDF를 `blocked_approval`/`pdf_text_policy_eligible_pending_execution_gate`로만 전환하며 실행 gate 확인과 queued 전이는 부모 실행 담당자의 책임이다.
- 승인된 최소 읽기 환경 `.venv-pdf-reader`의 표준 `pypdf`로 로컬 `source.pdf`의 내장 텍스트만 페이지별로 메모리에서 읽는다(`embedded_text_only`). 삭제된 PyMuPDF/Docling/Marker 전처리 환경 복원이 아니며 새 커스텀 수집기·파서·DB를 만들지 않는다. 지속 추출본·compile-input·chunk·렌더·이미지·OCR·외부 자산은 금지한다.
- 모델 전송은 `codex-lb/gpt-6-astra/xhigh`의 PDF 텍스트에만 허용한다. `transfer.pdf_content=true`는 **PDF 텍스트만** 뜻하며 PDF 바이너리 전송은 false다. fallback 금지, `no_cost_cap`, 미관측 비용 null을 유지한다.
- PDF 인용은 `source.pdf#page=N`이며 N은 인쇄 쪽수가 아닌 **물리적 1-based 페이지**다. 실제 읽은 페이지, 페이지별 텍스트 길이(Unicode 문자 수), 추출 품질/누락, 미독 범위를 run 근거에 기록한다. page 수나 읽기를 추정하지 않고 이미지/그림은 미검토로 남긴다. 텍스트층 없음·손상·빈 페이지·읽기 실패는 blocked/partial로 남기며 OCR로 우회하지 않는다. PDF 원문 텍스트 전체를 run/prompt/debug 로그에 영구 저장하지 않는다. 짧은 근거 인용과 길이·품질 메타데이터는 지식/검증 근거다.
- `source.json`의 `wiki_compiled:false`와 기존 원본은 수집 당시 불변 이력이다. prior v2 run/page/receipt와 성공 항목을 v3로 다시 쓰지 않는다. outer state의 policy/contract revision만 이관하고 기존 성공/실패 근거를 보존한다.
- 기존 `compile-one.py`/`verify-one.py`/`publish-one.py`는 **legacy P2-v2**이며 v3 지원 근거가 아니다. 가드를 완화하지 않는다. 부모는 표준 pypdf와 재사용한 안전 IO/runtime helper로 한정된 수동 v3 처리를 별도 수행·검증하며 자동화 준비 완료를 주장하지 않는다.
- 기존 수집 Cron `4cff5b4f10ec`는 **collect-only**다. PDF 원본 저장만 하며 PDF 텍스트 추출·본문 분석·Wiki 컴파일을 하지 않는다. 이번 승인으로 수집 프롬프트·스케줄·state를 변경하지 않는다.

### v3 PDF 요청·근거 검증

1. `pkm-compile-request/v3`의 PDF branch는 source_format=pdf, pdf_analysis=true, input_mode=embedded_text_only와 automation.pdf_reading의 정확한 const 객체를 요구한다. images/external_assets/ocr/pdf_binary_transfer/persistent_extraction/fallback_allowed는 false다. HTML branch는 source_format=html, pdf_analysis=false, input_mode=html_direct_text, pdf_reading=null이며 PDF 분석을 얻지 않는다.
2. `.venv-pdf-reader`의 pypdf에서 매 페이지의 내장 텍스트를 메모리로 읽고 실제 물리적 페이지와 함께 제한된 승인 모델에 전달한다. page_count·페이지별 text_length·extraction_quality·읽은/미독 범위는 실제 관측만 저장한다. 전체 추출 텍스트/요청 프롬프트 덤프/본문 chunk를 파일·로그·추가 DB에 보관하지 않는다.
3. claim별 `source.pdf#page=N`, version/source_sha256, 짧은 quote를 실제 해당 페이지 텍스트와 대조한다. 인쇄 쪽수나 섹션 번호를 N으로 쓰지 않는다. 테이블 텍스트의 순서/레이아웃이 불분명하면 미확인으로 남기며 그림/수식 시각 검토를 주장하지 않는다.
4. 빈 텍스트·손상·누락은 extraction-quality 근거와 함께 blocked 또는 partial; OCR/이미지 렌더/다른 parser fallback 없음. 완전한 요청 범위를 못 읽은 결과를 전문 완료로 게시하지 않는다.
5. 검증된 지식 초안의 게시만 별도 승인·edit freeze·WAL·최종 hash/receipt 조건을 적용한다. 부모의 bounded manual v3 adapter는 표준 pypdf와 기존 안전 IO/runtime helper를 재사용할 수 있지만 legacy 검증/게시 가드 완화, 새 커스텀 수집기/파서, 자동 실행기 구현 허가는 아니다.
