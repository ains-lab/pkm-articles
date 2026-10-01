# AI Agent Security — 원본 색인 (HTML 우선·PDF fallback)

- Cron ID: `4cff5b4f10ec`; 매일 KST 00:00(UTC `0 15 * * *`), KST 날짜당 최대 5편.
- 원본 수집만 수행한다. 전처리·자동 Wiki 컴파일은 하지 않는다.
- [설정](../../../_meta/topics.json) · [수집 규칙](../../../_meta/COLLECTION.md) · [직접 컴파일 전략](../../../_meta/COMPILATION.md).
- 2026-10-01 사용자 승인 삭제 후 현재 관리 대상은 **65개 버전 ID = 원문 보관 17편(HTML 15편 + PDF 2편) + 일일 한도 대기 48편**이다. 기존 전체 이력 68개 중 삭제 3편은 대기·실패로 세지 않는다. HTML 미제공 이력이 있는 PDF 2편도 원문 보관에 포함한다. [삭제 범위·백업 근거](../../../_meta/migrations/20261001-remove-three-offtopic-papers/manifest.json). 직전 수집 당시의 68개/보관 20편 대조는 [과거 실행 근거](../../../_meta/runs/4cff5b4f10ec/20260930T150351Z-62d474aa/inventory-verification.json)로 보존한다.
- 최근 정기 실행: `20260930T150351Z-62d474aa`(KST 2026-10-01). 검색창 `2026-09-27T15:09:05.363026+00:00`~`2026-09-30T15:05:07.821597+00:00`, actual updated 기준 후보 **48편 = 신규 23편 + 기존 pending 21편 + 보관 원본 중복 4편**. 직접 API HTTP 200, 100개 레코드의 버전 고유성·updated 내림차순·검색 하한 통과를 검증했다. pending 내구 저장 이후 checkpoint를 상한 시각으로 전진했다.
- 오래된 pending 5편을 우선하여 KST 일일 시도를 예약한 뒤 동일 버전 HTML 5편을 저장·검증·원자 게시했다. 신규 PDF 0편, 새 HTML 미제공 0편, 전송·무결성 실패 0건이다. 기존 원본 15편은 재검증 후 재사용했으며 기존 PDF를 재요청하거나 HTML로 교체하지 않았다. 대기 48편은 `daily_budget_exhausted`, 다음 시도는 `2026-10-01T15:00:00+00:00`(KST 10월 2일 00:00)부터다. [실행 보고서](../../../_meta/runs/4cff5b4f10ec/20260930T150351Z-62d474aa/report.json) · [pending 상태](../../../_meta/state/4cff5b4f10ec.json).
- 기존 지식 페이지 6개는 변경하지 않았다. 원본 HTTP 보존·무결성 확인만 수행했고 본문 분석·도표 검토·추출·OCR·자동 Wiki 컴파일은 하지 않았다.

## 이전 수집 이력 — 당시 수치

- KST 2026-09-30 실행은 신규 후보 35편 중 HTML 5편을 저장하고 30편을 대기 등록했다. 당시 보관 원문은 HTML 13편·PDF 2편이었다. [당시 실행 근거](../../../_meta/runs/4cff5b4f10ec/20260929T150905Z-fbf97a79/report.json). 당시 색인의 ‘15편 모두 확보’는 보관 대상만 센 수치였으며 발견 pending 30편을 포함한 전체 대상 수가 아니었다. 현재 집계는 모든 대상 ID의 합집합을 사용한다.
- 2026-09-29 11:51 KST의 정책 변경 전 로컬 전수 대조에서 전체 ID·보유 상태와 원본 8편의 버전·제목·크기·SHA-256이 일치했다. 당시 pending은 0편이었다. [이전 검증 근거](../../../_meta/runs/4cff5b4f10ec/20260929T025147Z-index-sync/inventory-verification.json). 새 정책은 `arxiv-html-preferred-pdf-fallback/v1`이며 기존 원본은 변경하지 않는다.
- 최근 정기 수집 실행: `20260928T150302Z-78f455f6`(KST 2026-09-29). `2026-09-27T07:07:13.632288+00:00`부터 `2026-09-28T15:03:02.148817+00:00`까지 실제 Atom updated 기준 신규 후보 **0편**. 직접 API HTTP 406은 같은 URL의 공식 브라우저 Atom 확인으로 복구했다. DOM 텍스트 캡처·브라우저 해시 대조 근거를 보존하고 검색식·100개 버전 ID의 고유성·updated 내림차순·검색 하한 통과를 확인했다. DOM 캡처는 HTTP 원문 바이트가 아니다.
- 위 정기 수집 당시 결과: 신규 HTML **0편**, 중복 처리 **0편**, 새 HTML 미제공 **0편**, 미복구 업무 실패 **0건**. 당시 신규 날짜별 시도 0개, pending 0편이며 기존 미제공 2편은 재확인 시각 전이므로 요청하지 않았다. 이후 정책 변경으로 등록한 PDF pending 2편은 이번 수동 수집에서 완료·제거했다. [정기 실행 근거](../../../_meta/runs/4cff5b4f10ec/20260928T150302Z-78f455f6/report.json).
- 이번 수동 수집 `20260929T042631Z-pdf-capture-808d882a`: 신규 PDF **2편**, 실패 **0건**. 공식 동일 버전 URL의 HTTP 200·application/pdf·%PDF-/%%EOF 표식·Content-Length·SHA-256과 게시 후 파일을 확인했다. 기존 HTML/서지 16개 파일은 그대로 유지했다. 새 검색 없이 기존 대기만 처리했으므로 discovery checkpoint는 변경하지 않았다. KST 2026-09-29의 날짜별 시도는 2개 ID다.
- 기존 8편은 **source.html + source.json**, 신규 PDF 2편은 **source.pdf + source.json**만 보관한다. 두 형식을 동시에 받거나 기존 원본을 교체하지 않았다. 외부 자산 수집·PDF 본문 추출·렌더링·OCR·내용 분석·Wiki 컴파일은 하지 않았다.
- 미제공 2편의 PDF를 2026-09-28 사용자 승인으로 삭제한 이력과 당시 공식 HTML 확인 근거는 보존한다. 이번에는 삭제본/백업 복원이 아닌 공식 PDF 신규 다운로드로 전문을 확보했다. HTML 미제공을 새로 온라인 확인한 것은 아니며 기존 근거를 재사용했다. PDF 완료 버전은 기존 HTML 재확인 예정일에도 자동 HTML 추가 수집·교체를 하지 않는다.

## 보관 원문 — HTML 15편 · PDF 2편

| 버전 ID | 제목 | 원본 상태 |
| --- | --- | --- |
| 2609.35117v1 | Tool Mediation Alters Refusal Mechanisms in Large Language Models | [원본 HTML](arxiv-2609.35117v1/source.html) · [서지·해시](arxiv-2609.35117v1/source.json) |
| 2609.35088v1 | When Valid Tool Calls Change Meaning: Formation-Consistent Dispatch for LLM Agents | [원본 HTML](arxiv-2609.35088v1/source.html) · [서지·해시](arxiv-2609.35088v1/source.json) |
| 2605.09027v3 | Agent Collectives Should Not Detect Their Own Imposters: A Chess Case Study | [원본 HTML](arxiv-2605.09027v3/source.html) · [서지·해시](arxiv-2605.09027v3/source.json) |
| 2609.34790v1 | CoSec: Benchmarking Agent Security in Communities | [원본 HTML](arxiv-2609.34790v1/source.html) · [서지·해시](arxiv-2609.34790v1/source.json) |
| 2609.35596v1 | SEABench: Benchmarking Endogenous Misalignment In Self-Evolving Agents | [원본 HTML](arxiv-2609.35596v1/source.html) · [서지·해시](arxiv-2609.35596v1/source.json) |
| 2609.35576v1 | Share-Borne AI Virus: Memory-Hopping Attacks Across LLM Agents | [원본 HTML](arxiv-2609.35576v1/source.html) · [서지·해시](arxiv-2609.35576v1/source.json) |
| 2608.29596v2 | A Systematic Survey of Agentic Skills: Architecture, Lifecycle, and Security | [원본 HTML](arxiv-2608.29596v2/source.html) · [서지·해시](arxiv-2608.29596v2/source.json) |
| 2509.09215v3 | Enabling Regulatory Multi-Agent Collaboration: Architecture, Challenges, and Solutions | [원본 HTML](arxiv-2509.09215v3/source.html) · [서지·해시](arxiv-2509.09215v3/source.json) |
| 2609.31562v1 | Agentic Economies for Autonomous Scientific Discovery | [원본 HTML](arxiv-2609.31562v1/source.html) · [서지·해시](arxiv-2609.31562v1/source.json) |
| 2609.31358v1 | A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents | [원본 HTML](arxiv-2609.31358v1/source.html) · [서지·해시](arxiv-2609.31358v1/source.json) |
| 2609.31318v1 | AgentXploit: Autonomous Repository-to-Runtime Red-Teaming for AI Agents | [원본 HTML](arxiv-2609.31318v1/source.html) · [서지·해시](arxiv-2609.31318v1/source.json) |
| 2609.31039v1 | MetaPermit: Scalable and Auditable Access Control for AI Agents via LLM-Inferred Meta-Attributes | [원본 HTML](arxiv-2609.31039v1/source.html) · [서지·해시](arxiv-2609.31039v1/source.json) |
| 2609.30830v1 | AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents | [원본 HTML](arxiv-2609.30830v1/source.html) · [서지·해시](arxiv-2609.30830v1/source.json) |
| 2609.30824v1 | Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal | [원본 PDF](arxiv-2609.30824v1/source.pdf) · [서지·해시](arxiv-2609.30824v1/source.json) · HTML 미제공 근거 보존 |
| 2609.30614v1 | Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces | [원본 PDF](arxiv-2609.30614v1/source.pdf) · [서지·해시](arxiv-2609.30614v1/source.json) · HTML 미제공 근거 보존 |
| 2609.30266v1 | LLM Agents Can Easily Tamper With Their Own Traces | [원본 HTML](arxiv-2609.30266v1/source.html) · [서지·해시](arxiv-2609.30266v1/source.json) |
| 2609.30217v1 | Instrumental Monitor Evasion Emerges Under Ordinary Task Pressure | [원본 HTML](arxiv-2609.30217v1/source.html) · [서지·해시](arxiv-2609.30217v1/source.json) |

## 완료·미확보의 의미

- 2026-10-01 사용자 확인에 따라 TokenCast (`2609.35760v1`), Financial Fragility (`2609.30940v1`), Planarian (`2609.35366v1`)의 원본·서지를 현재 보관 목록에서 삭제하고 현재 컴파일 항목에서도 제거했다. 게시된 전용 위키 문서는 없었다. 복구용 백업은 활성 Wiki 밖에 보관하고 과거 수집·컴파일 시도 기록은 유지한다. 검색식·Cron·향후 제외 정책은 변경하지 않아 재발견 시 다시 수집될 수 있다.
- 저장 완료는 arXiv HTML 또는 PDF 원본 확보와 무결성 확인이다. 논문 내용 분석·도표 판독·실험 재현 완료가 아니다. 대기 등록은 저장 성공이 아니다.
- HTML은 원본 그대로여서 일부 외부 자산·상대 링크의 로컬 표시에는 제약이 있다. 원래 URL은 source.json에 있으며 원문을 수정해 링크를 고치지 않았다.
- HTML 미제공 근거는 state.html_unavailable에 남기며 PDF가 저장되면 원문 확보로 집계한다. HTML 미제공 기록 수와 전문 미확보 수는 다르다. PDF 완료 버전은 자동 HTML 재확인·형식 교체를 하지 않는다. 양쪽 원본이 공식 미제공이면 7일 후 재확인하며 일시 전송 오류와 구별한다.
- 동일 source+version_id는 해시 검증 후 재사용한다. 다른 주제와 공유할 때는 reference만 저장한다.

## 전환 근거

- [실행 보고서](../../../_meta/migrations/20260928T104108Z-html-only/report.md)
- [원본 다운로드 기록](../../../_meta/migrations/20260928T104108Z-html-only/downloads.json)
- [HTML 미제공 확인](../../../_meta/migrations/20260928T104108Z-html-only/html-unavailable-evidence.json)
- [영구 삭제·원본 게시 기록](../../../_meta/migrations/20260928T104108Z-html-only/cutover.json)

이전 PDF·추출·시각 검토 상태는 폐기된 전처리 이력이다. 이전 active 파일은 삭제되었으며 log의 과거 경로가 더 이상 존재하지 않을 수 있다. 새 백업은 만들지 않았고 이전 백업은 접근·변경하지 않았다.
