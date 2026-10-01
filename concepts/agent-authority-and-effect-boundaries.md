---
title: "권한과 실행 효과의 경계"
summary: "에이전트의 승인 기록을 해석하려면 요청을 허용하는 권한, 집행 가능한 경계, 실제 실행과 외부 효과를 분리하고 비실행 제안 승인을 호출 권한으로 오인하지 않아야 한다."
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "concept"
status: "draft"
tags: ["agent-security", "llm-security", "infrastructure-security", "provenance"]
sources: ["raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html", "raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html"]
confidence: "medium"
contested: false
contradictions: []
schema: "pkm-knowledge-page/v1"
revision: "1"
transaction_id: "p2i-d3b8cf0db1b918060510445ffe3b227a"
policy_revision: "pkm-html-knowledge/v2"
prompt_revision: "wiki-integrate/v1"
generation_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json"
read_scope: ["2609.30830v1 — S1.p4", "2609.30830v1 — S4.SS1", "2609.30830v1 — S4.SS2 — 설명 본문", "2609.30830v1 — S4.SS4", "2609.30830v1 — S5.T2 — HTML 표 텍스트", "2609.30830v1 — S6.SS1.p2", "2609.31358v1 — S3 — 설명 본문", "2609.31358v1 — S4.p5", "2609.31358v1 — S5.SS3", "2609.31358v1 — S6.SS2"]
unread_scope: ["2609.30830v1 — 실제 호스트 승인 이벤트의 인증·전달 및 설치된 veto 경로는 원시 실행 자료로 확인하지 않았다.", "2609.31358v1 — 비실행 경계의 구현 전체 증명, 인증된 임상 승인 및 실제 장치 실행 경로는 확인 범위가 아니다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html": "89d515e6c33de5717ff141a6d9726830a01798e6dfead198c9f0525f0261d074", "raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html": "cfee938c27d5b30fb053d251d2bd1b1a6ac259b775582fe05558a370ddac566e"}
agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# 권한과 실행 효과의 경계

> 초안 · 미검토 Wiki 지식

**정의 — AI 해석:** 권한 경계는 어떤 요청을 누가 어떤 조건으로 허용할 수 있는지 정하고, 실행 효과의 경계는 그 허용이 실제로 어디까지 작용하는지 구분한다. 따라서 `승인됨 → 실행됨 → 외부 효과 완료`를 하나의 상태로 취급하지 않는다. AGATE는 최종 허용 시 디스패치 전에 권한을 소비하지만, SDC-to-MCP Gateway의 승인은 장치 조작을 디스패치하지 않는 기록이다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2.p4] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p2]

## 배경: 같은 ‘승인’이 다른 것을 뜻할 수 있다

이 페이지에서 비교하는 것은 승인 버튼이나 필드 이름이 아니라 **승인의 대상과 그 뒤의 집행 경로**다. [[entities/arxiv-2609.30830v1|AGATE 노트]]는 실행 가능한 에이전트 도구 요청을, [[entities/arxiv-2609.31358v1|SDC-to-MCP Gateway 노트]]는 장치 실행 권한이 없는 제안 수명주기를 찾아가는 출발점이다. 이 차이가 C01의 핵심이다.

| 구분할 대상 | AGATE에서의 의미 | Gateway에서의 의미 |
|---|---|---|
| 권한의 근거 | 운영자 선언과 호스트 발급 승인; 대화 속 승인 주장은 grant가 아님 — C02 | 정책·현재 상태를 재검사하는 비실행 제안 승인; 평가의 신원 필드는 인증되지 않음 — C06 |
| 승인 대상 | 세션·정확한 요청 인자에 결합된 제한적 grant — C03 | 장치·조작·매개변수·정책·스냅샷 등에 결합된 제안 — C06 |
| 집행 지점 | 설치된 어댑터에 따라 디스패치 거부 또는 기록만 가능 — C04 | 읽기와 dry-run만 제공하며 장치 조작 경로를 제외 — C05 |
| 결과를 뜻하지 않는 기록 | grant 소비와 반복 검토 원장은 완료된 외부 효과가 아님 — C01·C03 | approved 상태도 장치 실행을 뜻하지 않음 — C06 |

## 저자 보고: AGATE의 조건부 실행 권한

- **권한과 데이터 전달은 별도 검사다.** 대화 밖의 운영자 선언이 신뢰 루트를 제공하며, 작업·문서·기억 속 문장은 grant를 발급하지 못한다. 도구 grant가 있어도 보호 경계를 넘는 데이터 검사는 면제되지 않는다. 이는 [[concepts/provenance-and-audit-evidence|출처 증거]]를 곧바로 실행 권한으로 승격시키지 않는 구분이다. **C02**
- **정확한 요청 승인과 반복 효과 검토도 다르다.** 호스트 승인은 요청 digest, 세션, 만료와 남은 사용 횟수에 결합된다. 수신자나 인자가 바뀌면 새 승인 요청이 된다. 반면 effect ledger는 관측 가능한 대상별 반복 검토를 위한 것이며, 확정된 외부 효과의 원장이 아니다. **C03**
- **판정 코어의 존재만으로 집행을 주장할 수 없다.** 평가된 DSH는 디스패치 veto를 제공하지만 OC는 해당 훅에서 발견 사항만 기록한다. OpenClaw의 과거 증거 측정은 flag-only·fail-open 경로였으며 veto에는 동기식 정책 통합이 필요하다. **C04**

## 저자 보고: Gateway의 비실행 승인

- **장치에 대한 no-execution이 명시적 계약이다.** 평가된 MCP 경계는 동일 호스트 stdio subprocess다. 쓰기 모드 설정을 거부하고, SDC 소비자 계약을 발견·스냅샷 읽기로 제한하며, 도구 정책과 결과 모델에 dry-run·비실행 의미를 요구한다. 이것은 모든 부수 효과가 없다는 뜻이 아니라 SDC 장치 조작을 내보내지 않는다는 뜻이다. **C05**
- **승인은 제안의 상태 전이지 실행 권한 부여가 아니다.** 제안은 장치·조작·매개변수·정책 버전·MDIB 버전·최신성·스냅샷 해시·제안자·만료에 결합된다. 승인 시 정책과 현재 상태를 다시 검사하며 변경·노후화·만료 상태를 승인으로 무시할 수 없다. 평가에서 approved 기록도 비실행이었고 신원/reference 필드는 인증되지 않았다. **C06**
- **상태 불변과 쓰기 부재를 혼동하지 않는다.** 요청에 의해 디스패치된 장치 조작이 0이라는 것이 목표 경계다. 전후 상태 digest 일치는 독립적인 장치 업데이트가 없는 통제 시험의 추가 관측이다. 실제 제공자가 읽기 도중 측정값을 바꾸는 현상은 그 자체로 게이트웨이 쓰기 권한의 증거가 아니며, 유한 시험은 모든 실행에 대한 증명이 아니다. **C07**

## 비동치 관계를 적용하는 질문

아래는 C01–C07을 배포 문서나 로그에 적용할 때 사용할 질문이다.

1. `approved`가 붙은 객체는 도구 호출인가, 실행되지 않는 제안인가?
2. 승인 발급자는 인증된 호스트 이벤트로 확인되는가, 아니면 문서·모델 출력·자유 입력 신원인가?
3. 승인 뒤 인자·수신자·스냅샷이 바뀌면 기존 승인을 재사용할 수 있는가?
4. deny가 남은 위치에 실제 veto가 있는가? 기록 전용 훅을 집행 경계로 부르고 있지 않은가?
5. 사용 횟수 소비, 실행 관측, 외부 완료 확인을 각각 어느 기록에서 찾을 수 있는가?
6. ‘상태가 바뀌었다’는 관측에서 요청의 효과와 제공자의 독립 업데이트를 구분했는가?

## 관련 지식

- [[concepts/security-evaluation-units|보안 평가 단위와 주장 범위]]에서 요청·이벤트·작업·외부 효과를 나누는 방법을 이어서 읽는다.
- [[concepts/provenance-and-audit-evidence|데이터 출처와 감사 증거의 구분]]은 승인 근거와 데이터 계보를 혼동하지 않기 위한 동반 개념이다.
- [[comparisons/agate-vs-sdc-mcp-gateway|AGATE와 SDC-to-MCP Gateway 비교]]에서 위협 모델과 미검증 가정을 함께 확인한다.

## 근거 표

| 주장 | 구분·조건 | 짧은 원문 인용과 연결 |
|---|---|---|
| C01 | AI 해석 · AGATE의 허용 요청 계수 | “Consumption occurs at the approval decision before tool dispatch.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2.p4) |
| C01 | AI 해석 · Gateway의 비실행 승인 | “Any approval is recorded without dispatching a device operation” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p2) |
| C02 | 저자 보고 · 대화 밖 신뢰 루트 | “Text in a task, document, or remembered conversation cannot issue a grant.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS1.p2) |
| C02 | 저자 보고 · 데이터 검사는 독립 | “does not exempt a boundary-crossing call from data checks” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1.p4) |
| C03 | 저자 보고 · 요청 결합 승인 | “Thus a changed recipient or argument creates a new approval request.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2.p2) |
| C03 | 저자 보고 · 반복 검토 원장 | “not a ledger of confirmed external effects.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2.p6) |
| C04 | 저자 보고 · DSH·OC 평가 경로 | “DSH supplies a dispatch veto” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p2) |
| C04 | 저자 보고 · 어댑터별 통제 차이 | “The evaluated hook records findings without a dispatch veto” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2) |
| C05 | 저자 보고 · 로컬 MCP 전송 | “Stdio confines the MCP boundary to a same-host subprocess” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p2) |
| C05 | 저자 보고 · 다층 비실행 계약 | “the SDC consumer contract exposes only discovery and snapshot reads” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p5) |
| C06 | 저자 보고 · 승인 시 재검사 | “changed, stale, or expired state cannot be overridden.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p5) |
| C06 | 저자 보고 · 합성 승인 평가 | “The identity/reference fields were not authenticated, and no participants evaluated the interface.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2.p3) |
| C07 | 저자 보고 · 외부 업데이트 없는 통제 시험 | “Zero dispatched operations is the intended request-level boundary.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p4) |

## 읽기·검증 범위

- 두 원본 HTML의 위 frontmatter에 기록한 선택 절을 통합한 Wiki 노트다. 새 전문 완독이나 논문 원고 작성이 아니다.
- 그림·PDF·외부 자산·외부 문헌을 검토하거나 실험을 재현하지 않았다. 사람의 내용 검토는 미완료다.
- 원문 버전·SHA-256은 원본 metadata 및 로컬 파일과 대조했다. 생성 모델의 미검토 선언과 오케스트레이터의 무결성 검사를 구분한다.
- [실제 생성 기록](../_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json) · [주장별 에이전트 근거 대조](../_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json)
