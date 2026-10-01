# 나의 논문 지식 Wiki

개인 논문 원문을 보관하고 요청 시 요약·분석·비교·질의로 연결하는 로컬 Markdown 지식 저장소다. 사용자 본인과 Hermes가 사용하며 별도 DB는 없다.

## 시작점

- [논문 수집 자동화 — 쉬운 안내](docs/lectures/5w/paper-collection.md), [Cron 생성·현재 구성](docs/lectures/5w/paper-collection-cron.md), [설명서 목록](docs/README.md)
- [지식 색인](index.md), [스키마](SCHEMA.md), [에이전트 범위](AGENTS.md), [작업 이력](log.md)
- [AI Agent Security 원본 색인](raw/articles/4cff5b4f10ec/index.md)
- [HTML 우선·PDF fallback 원본 수집 규칙](_meta/COLLECTION.md), [정확한 검색식·한도](_meta/topics.json)
- [HTML/PDF 텍스트 llm-wiki 컴파일 전략](_meta/COMPILATION.md)
- [후속 지식화 운영 계약 — P2 수동 승인, 자동화 비활성](_meta/AUTOMATION.md), [승인 모델·비용 비차단·게이트](_meta/automation.json), [상태 계약](_meta/STATE-CONTRACTS.md)

## 현재 방식

**arXiv 검색 → 동일 버전 HTML 우선 저장 → 공식 HTML 미제공이면 동일 버전 PDF 원본 저장**

사전 파싱 단계는 없다. 2026-09-29 승인으로 PDF 원본 HTTP 다운로드만 fallback으로 허용했다. 수집 단계의 fulltext/블록 추출, 이미지/표/페이지 분리, OCR, 구조화·정규화, 전처리 모델 호출 및 전용 환경은 제거 상태를 유지한다. 정기 수집은 원본 저장에서 끝나며 자동 지식 컴파일을 하지 않는다. HTML은 별도 사용자 요청에서 직접 읽어 컴파일한다. v3에서는 정상 실행 gate 통과 후 PDF 내장 텍스트도 표준 pypdf로 로컬에서 페이지별로 읽을 수 있다.

- 2026-09-29 수집 당시 기존 대상 **10편 모두 원문 확보**: **HTML 원본 8편**, **PDF 원본 2편**, **전문 미확보·수집 대기 0편**이다. 2026-09-29 사용자 요청으로 PDF 2편을 실제 다운로드·검증했다. 최신 현황은 [원본 색인](raw/articles/4cff5b4f10ec/index.md)과 state를 확인한다.
- HTML 미제공: `2609.30614v1`, `2609.30824v1`. 기존 공식 HTML URL 404·abs 페이지 PDF-only 근거를 유지하며 이번에 동일 버전 PDF를 확보했다. 초록을 전문으로 저장하지 않았다.
- 2026-09-28 사용자 승인으로 PDF 10편·기존 전처리 산출물·시험본·전용 환경을 새 백업 없이 영구 삭제한 이력은 유지한다. 이번 PDF 수집은 삭제본/백업 복원이 아니라 공식 원본의 신규 다운로드다. [수집 근거](_meta/runs/4cff5b4f10ec/20260929T042631Z-pdf-capture-808d882a/report.json).
- 2026-09-29 PDF 수집 당시 지식 페이지는 **0개**였다. 이후 HTML P2 게시·통합으로 6개 draft/unreviewed가 생겼다. 이번 PDF 텍스트 정책 준비는 새 읽기·게시 완료가 아니며 최신 수는 index를 확인한다.
- 기존 Cron `4cff5b4f10ec`는 HTML 우선·공식 미제공 시 PDF 원본 수집 정책을 따른다. 매일 **KST 00:00**, 정기 KST 날짜당 최대 5개 ID 시도, local 전달은 유지한다. 같은 ID의 HTML→PDF는 하루 한 번으로 센다. 실제 재개/실행 상태는 Cron 목록과 최신 log를 확인한다.
- **후속 지식화 policy v3 (`pkm-html-pdf-text-knowledge/v3`).** 모델 `codex-lb/gpt-6-astra/xhigh`, 로컬 HTML 텍스트·승인된 로컬 PDF 내장 텍스트·기존 Wiki·저장 요청한 비민감 피드백만 허용한다. 2026-09-29 사용자 요청으로 금액 상한·비용 차단 게이트를 제거했고 P2 수동 파일럿(HTML 2편) 실행을 승인했다. PDF 바이너리·이미지·외부 자산·전체 대화 자동 수집은 계속 제외이며 실제 비용 미관측은 null로 기록한다. P3 일일 자동화·P5 연구 리뷰·신규 Cron 등록/활성화는 미승인이다. PDF 2편은 정책 적격이지만 준비 ledger는 blocked_approval이며 실제 실행 gate 확인 전 queued로 만들지 않는다.

## 폴더 구조

```text
raw/articles/<cron-id>/
  index.md
  arxiv-<version-id>/
    source.html       # HTML 제공 시; 미제공 확인 시에는 source.pdf
    source.json       # 서지·버전 고정 URL·시각·크기·SHA-256
entities/             # 수동 컴파일 요청으로 생성할 논문별 분석
concepts/             # 개념 연결
comparisons/          # 비교
queries/              # 질의 답변
_meta/topics.json     # 검색식·HTML 우선/PDF fallback 수집 정책
_meta/state/          # checkpoint·pending·HTML 미제공
_meta/runs/           # 정기 실행 근거
_meta/migrations/     # 이번 전환·삭제·검증 기록
```

HTML 미제공 논문에 가짜 원천 폴더/placeholder HTML을 만들지 않는다. PDF 원본 검증에 성공한 경우만 source.pdf와 source.json 두 파일을 게시한다. 기존 raw/papers, transcripts, assets는 비어 있으며 이번 수집에 사용하지 않는다.

## 원본 그대로 저장한다는 의미

HTML을 Markdown으로 변환하거나 내용을 재작성하지 않는다. 페이지의 외부 이미지·CSS·폰트와 상대 링크도 그대로 유지하므로, 로컬 파일만 열면 일부 그림/스타일이 표시되지 않을 수 있다. 이것은 오프라인 자산 번들이 아니다. 정밀하게 읽을 때에는 source.json의 동일 버전 공식 URL을 기준으로 확인한다.

HTTP 상태·논문 버전·응답 길이·해시와 형식별 검증은 잘못된 응답을 저장하지 않기 위한 보존 검사다. 수집 시 HTML은 제목/본문 존재를, PDF는 MIME·%PDF-/%%EOF 표식을 검사하되 본문·페이지 수를 파싱하지 않는다. PDF 파일 내부의 내용 완전성 검토를 의미하지 않는다. 403/429/5xx/timeout을 HTML 미제공으로 취급하거나 PDF로 우회하지 않는다.

## 컴파일 요청 예

“저장된 원본 HTML을 직접 읽고 이 논문을 한국어 논문 페이지로 정리해줘.”

`llm-wiki`는 기존 지식과 중복을 확인하고 원본을 직접 읽어 entities/concepts/comparisons/queries를 작성한다. 원본 버전·HTML 앵커 또는 PDF 물리적 페이지·읽은 범위·미검토 도표를 명시하고 index와 log를 갱신한다. 원문 저장 성공만으로 분석·시각 검토·실험 재현을 완료했다고 표시하지 않는다.

후속 실행은 [단계·자료 게이트](_meta/AUTOMATION.md)를 먼저 통과해야 한다. 운영 계약과 프롬프트 작성은 자동화 가동 성공이 아니다. HTML P2의 과거 성공은 보존한다. 이번 PDF 두 편의 수동 처리·게시 승인은 별도 범위이며 정책 준비만으로 완료되었다고 하지 않는다. 질의 환류와 연구 아이디어 규칙은 [피드백 계약](_meta/QUERY-FEEDBACK.md), [연구 리뷰 계약](_meta/RESEARCH-REVIEW.md), [연구 프로필](_meta/RESEARCH-PROFILE.md)을 참고한다.

## 보존과 범위

HTML/PDF 원본은 불변이다. 같은 버전·같은 형식의 다른 응답 해시는 충돌로 기록하고 덮어쓰지 않는다. 기존 HTML 8편과 source.json은 그대로 유지한다. PDF로 저장 완료한 버전을 자동으로 HTML로 교체하지 않는다. 새 버전은 별도 보존한다. 과거 영구 삭제 승인은 일반 삭제 권한이 아니며 이후 대량 이동·삭제는 다시 확인한다.

이전 초기화 백업·다른 Wiki·DB·Hermes 프로필·다른 Cron·전역 스킬은 변경하지 않는다. log는 과거 경로를 포함한 append-only 이력으로 유지하며 폐기된 전처리 지시를 현재 실행 규칙으로 사용하지 않는다. PDF fallback 정책 전환 근거는 [_meta/migrations/20260929T034401Z-pdf-fallback-policy/](_meta/migrations/20260929T034401Z-pdf-fallback-policy/)에 보존한다.

## PDF 텍스트 승인 경계 — v3

- 정책 `pkm-html-pdf-text-knowledge/v3`, 계약 `pkm-contracts/v3`. 승인 근거는 `_meta/runs/wiki/20261001T001438Z-pdf-wiki/scope-approval.json`이다. 기존 `2609.30614v1`, `2609.30824v1`의 수동 PDF 텍스트 컴파일·검증 후 게시와 작업 중 편집 중지는 별도로 승인되었지만, 이 정책 준비는 실제 읽기·생성·게시 완료가 아니다.
- 향후 PDF도 정책상 대상이 될 수 있으나 정확한 입력·단계·모델·무결성·게시/편집 중지 등 정상 실행 승인이 먼저 필요하다. P3/P4/P5/P6는 미승인, 자동화 enabled=false, 신규 Cron 미등록이다. 정책 준비자는 두 PDF를 `blocked_approval`/`pdf_text_policy_eligible_pending_execution_gate`로만 전환하며 실행 gate 확인과 queued 전이는 부모 실행 담당자의 책임이다.
- 승인된 최소 읽기 환경 `.venv-pdf-reader`의 표준 `pypdf`로 로컬 `source.pdf`의 내장 텍스트만 페이지별로 메모리에서 읽는다(`embedded_text_only`). 삭제된 PyMuPDF/Docling/Marker 전처리 환경 복원이 아니며 새 커스텀 수집기·파서·DB를 만들지 않는다. 지속 추출본·compile-input·chunk·렌더·이미지·OCR·외부 자산은 금지한다.
- 모델 전송은 `codex-lb/gpt-6-astra/xhigh`의 PDF 텍스트에만 허용한다. `transfer.pdf_content=true`는 **PDF 텍스트만** 뜻하며 PDF 바이너리 전송은 false다. fallback 금지, `no_cost_cap`, 미관측 비용 null을 유지한다.
- PDF 인용은 `source.pdf#page=N`이며 N은 인쇄 쪽수가 아닌 **물리적 1-based 페이지**다. 실제 읽은 페이지, 페이지별 텍스트 길이(Unicode 문자 수), 추출 품질/누락, 미독 범위를 run 근거에 기록한다. page 수나 읽기를 추정하지 않고 이미지/그림은 미검토로 남긴다. 텍스트층 없음·손상·빈 페이지·읽기 실패는 blocked/partial로 남기며 OCR로 우회하지 않는다. PDF 원문 텍스트 전체를 run/prompt/debug 로그에 영구 저장하지 않는다. 짧은 근거 인용과 길이·품질 메타데이터는 지식/검증 근거다.
- `source.json`의 `wiki_compiled:false`와 기존 원본은 수집 당시 불변 이력이다. prior v2 run/page/receipt와 성공 항목을 v3로 다시 쓰지 않는다. outer state의 policy/contract revision만 이관하고 기존 성공/실패 근거를 보존한다.
- 기존 `compile-one.py`/`verify-one.py`/`publish-one.py`는 **legacy P2-v2**이며 v3 지원 근거가 아니다. 가드를 완화하지 않는다. 부모는 표준 pypdf와 재사용한 안전 IO/runtime helper로 한정된 수동 v3 처리를 별도 수행·검증하며 자동화 준비 완료를 주장하지 않는다.
- 기존 수집 Cron `4cff5b4f10ec`는 **collect-only**다. PDF 원본 저장만 하며 PDF 텍스트 추출·본문 분석·Wiki 컴파일을 하지 않는다. 이번 승인으로 수집 프롬프트·스케줄·state를 변경하지 않는다.
