---
title: "데이터 출처와 감사 증거의 구분"
summary: "출처·매핑·판정 이력·재생 일치·해시 체인은 서로 다른 질문에 답하는 증거이며, 어느 하나도 데이터 진실성이나 완전 관측을 자동으로 확립하지 않는다."
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "concept"
status: "draft"
tags: ["provenance", "agent-security", "reproducibility", "infrastructure-security"]
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
read_scope: ["2609.30830v1 — S4.SS3 — 설명 본문", "2609.30830v1 — S4.SS5 — 설명 본문", "2609.30830v1 — S5.p4", "2609.30830v1 — S5.p5", "2609.30830v1 — S6.SS2.p5", "2609.30830v1 — S7.SS1.p2", "2609.30830v1 — S7.SS1.p5", "2609.31358v1 — S3.p6", "2609.31358v1 — S3.p7", "2609.31358v1 — S4.p4", "2609.31358v1 — S4.SS2.SSS0.Px1", "2609.31358v1 — S5.SS3.p4", "2609.31358v1 — S6.SS6", "2609.31358v1 — S7.p5", "2609.31358v1 — S7.p6"]
unread_scope: ["2609.30830v1 — 원시 이벤트와 독립 호스트 기록을 대조하지 않았으므로 관측 완전성이나 어댑터 진실성을 확인한 것이 아니다.", "2609.31358v1 — 실제 감사 체인, 매핑 파일, 공급자 인증 자료와 외부 보관 기준점은 확인하지 않았다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html": "89d515e6c33de5717ff141a6d9726830a01798e6dfead198c9f0525f0261d074", "raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html": "cfee938c27d5b30fb053d251d2bd1b1a6ac259b775582fe05558a370ddac566e"}
agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# 데이터 출처와 감사 증거의 구분

> 초안 · 미검토 Wiki 지식

**정의 — AI 해석:** 출처 증거는 관측한 자료가 어떤 경로로 들어왔거나 어떤 상태·설정에 연결되는지 설명한다. 그것만으로 자료가 참인지, 현재 사용해도 되는지, 실행 권한이 있는지는 결정되지 않는다. AGATE의 origin은 워크플로 유입 경로를 기술하고, Gateway는 스키마와 최근 timestamp만으로 센서 정확성·환자 연결 등을 확립할 수 없다고 한정한다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p1] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p5]

## 먼저 증거가 답하는 질문을 정한다

| 증거의 역할 | 답하려는 질문 | 자동으로 답하지 못하는 질문 |
|---|---|---|
| 입력 경로·내용의 출처 | 이 자료는 어디서 관측되어 후속 요청에 재사용되었는가? — C02 | 사용자의 의도나 전달 허용 여부를 유사성만으로 결정할 수 있는가? |
| 매핑·상태 품질 | 어느 식별자와 의미에 대응하며 stale·invalid인가? — C06 | 임상 라벨과 센서값이 실제로 맞는가? |
| 판정·실행 기록의 상관관계 | 어떤 요청·근거·관측 결과가 연결되는가? — C04 | 예측한 효과가 실제로 발생했는가? |
| 재생 일치 | 보존 이벤트로 같은 투영을 재구성하는가? — C05 | 누락 없이 모든 행동을 관측했는가? |
| 로컬 해시 체인 | 남아 있는 파일 내부의 변경을 검출하는가? — C07 | 외부 기준점 없이 꼬리 삭제를 검출하는가? |

이 구분은 [[concepts/agent-authority-and-effect-boundaries|권한과 실행 효과의 경계]]와 연결된다. 자료의 계보를 알게 된 것과 그 자료를 명령·승인으로 취급해도 된다는 것은 다른 판단이다. **C01**

## 저자 보고: AGATE의 관측 기반 데이터 흐름

[[entities/arxiv-2609.30830v1|AGATE]]는 지원되는 읽기·도구 결과·웹·명령 출력 등의 관측에서 경로와 정규화된 내용 창을 등록한다. 선택된 전달 필드를 등록된 자료와 대조한 뒤 출처–목적지 정책을 적용한다. 같은 조각의 복사도 승인된 내부 작업과 외부 전달에서 다르게 취급될 수 있지만, 그 차이는 정책이 제공해야 한다. 내용 유사성은 출처 단서이지 사용자 의도의 증거가 아니다. **C02**

**설계와 평가된 경로를 분리한다.** 고정 출처 계층, 출처별 공정 보존, base64·hex·percent 디코딩은 설계에 기술되어 있지만 배포 기록은 평가 경로에서의 활성화를 확립하지 않는다. 저자는 평가 결과에 디코딩이 포함되지 않는다고 명시한다. 사서함 사례의 재작성 우회도 실제 삭제가 아니라 내용 매칭을 우회한 합성 도구 요청이 종점이다. **C03**

**그래프의 연결 강도도 구분한다.** AGATE의 상관관계에는 exact·session-level·heuristic이 있고 예측 효과와 관측 결과는 별도 기록이다. 동기식 grant 소비와 비동기 그래프 수집은 별도의 영속화 경로를 사용하므로 forensic spool을 판정 큐나 실행 완료 원장으로 읽지 않는다. **C04**

**재생은 누락을 되살리지 않는다.** 저자는 replay equality를 보존된 증거의 일관성으로 한정한다. 어댑터 진실성·완전 중재·외부 효과 확인을 확립하지 않으며, 조용한 우회는 행동 기록과 공백 표시를 모두 남기지 않을 수 있다. **C05**

## 저자 보고: Gateway의 상태·설정 결합과 감사

[[entities/arxiv-2609.31358v1|SDC-to-MCP Gateway]]의 매핑 성공은 상태 품질이나 의학적 정확성과 별개다. 알려진 지표로 매핑된 값도 stale 또는 invalid일 수 있다. 스키마 검사는 문서 형태를, 교차 항목 검사는 식별자 유일성·단위 일관성 등을 확인하지만 수동 임상 라벨의 의학적 정확성을 확립하지 않는다. **C06**

로컬 감사 실험은 제공자 식별자, 정규 스냅샷, 매핑·정책·과제·프롬프트·처리기·시각·결정 이유를 연결한 네 레코드를 만들었다. 온전한 SHA-256 체인은 검증되었고 첫 레코드 수정은 검출되었지만, 외부 anchor 없는 꼬리 삭제는 검출 범위 밖이다. 또한 EPR 정확 일치는 허용된 식별자 제한이지 제공자 신원의 암호학적 증명이 아니다. **C07**

## AI 해석: ‘감사 가능’이라는 말을 분해해서 사용한다

두 논문의 증거를 하나의 감사 점수로 합치기보다 **재구성 일관성, 수집 범위, 파일 내부 변경 검출, 외부 기준점**을 별도 항목으로 기록하는 편이 정확하다. AGATE의 replay 한계와 Gateway의 tail-truncation 한계는 서로 다른 실패 조건이므로 어느 한 검사의 성공으로 다른 조건을 충족했다고 볼 수 없다. **C08** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p5] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1]

## 재사용할 질문

- ‘출처 확인’은 관측 채널·자료 해시·제공자 식별자 중 무엇을 확인한 것인가? 신원 인증과 혼동하지 않았는가?
- 내용이나 파일 경로를 등록하지 못했거나 보존 예산에서 퇴거했을 때 어떤 증거가 남는가?
- 같은 입력에서 만든 두 산출물이 일치한 것인가, 독립적인 관측원과 대조한 것인가?
- 그래프 edge는 정확한 요청 연결인가, 세션 단위인가, 휴리스틱인가?
- `mapped`, `fresh`, `valid` 각각의 근거와 설정 책임자는 누구인가?
- 감사 체인의 마지막 레코드를 삭제했을 때 비교할 외부 기준점이 있는가?
- 설계에 적힌 변환 추적 기능이 실제 평가 경로에서도 켜졌다는 자료가 있는가?

## 관련 지식

- [[concepts/security-evaluation-units|보안 평가 단위와 주장 범위]]는 재생 일치율과 탐지 재현율을 구분한다.
- [[comparisons/agate-vs-sdc-mcp-gateway|두 시스템 비교]]는 서로 다른 provenance 의미를 위협 모델과 함께 정리한다.

## 근거 표

| 주장 | 구분·조건 | 짧은 원문 인용과 연결 |
|---|---|---|
| C01 | AI 해석 · 관측 origin | “The origin describes how material entered the workflow.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p1) |
| C01 | AI 해석 · 데이터 진실성의 한계 | “A correct schema and a recent timestamp cannot establish sensor correctness” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p5) |
| C02 | 저자 보고 · 관측 경로·내용 창 | “Character-level windows make matching independent of a model tokenizer.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p2) |
| C02 | 저자 보고 · 정책과 의도 구분 | “content similarity alone supplies origin evidence, not the user’s intended purpose.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p6) |
| C03 | 저자 보고 · 설계와 평가 경로 | “the evaluated outcomes do not include decoding.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.p5) |
| C03 | 저자 보고 · 재작성 우회의 관측 종점 | “The observed endpoint is a request that bypasses the content match” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2.p5) |
| C04 | 저자 보고 · 상관관계 강도 | “exact, session-level, and heuristic relationships.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS5.p2) |
| C04 | 저자 보고 · 별도 영속화 경로 | “the forensic spool is not the decision queue.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS5.p3) |
| C05 | 저자 보고 · 보존 증거에 한정 | “A silent bypass may produce neither an action record nor a coverage gap.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p5) |
| C06 | 저자 보고 · 매핑과 상태 품질 | “Mapping can still identify these quantities; it must not turn them into current, trustworthy observations.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.SS2.SSS0.Px1.p1) |
| C06 | 저자 보고 · 매핑 검증과 의학적 정확성 | “Neither establishes that a manually supplied clinical label is medically correct.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.SS2.SSS0.Px1.p3) |
| C07 | 저자 보고 · 로컬 감사 체인 | “but not tail truncation without an external anchor.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1) |
| C07 | 저자 보고 · EPR와 신원 인증 | “an EPR allowlist restricts accepted identifiers but is not a cryptographic proof of provider identity.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p7) |
| C08 | AI 해석 · 재구성과 수집 범위 | “Replay equality establishes consistency of retained evidence.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p5) |
| C08 | AI 해석 · 변경 검출과 외부 기준점 | “but not tail truncation without an external anchor.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1) |

## 읽기·검증 범위

- 두 원본 HTML의 위 frontmatter에 기록한 선택 절을 통합한 Wiki 노트다. 새 전문 완독이나 논문 원고 작성이 아니다.
- 그림·PDF·외부 자산·외부 문헌을 검토하거나 실험을 재현하지 않았다. 사람의 내용 검토는 미완료다.
- 원문 버전·SHA-256은 원본 metadata 및 로컬 파일과 대조했다. 생성 모델의 미검토 선언과 오케스트레이터의 무결성 검사를 구분한다.
- [실제 생성 기록](../_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json) · [주장별 에이전트 근거 대조](../_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json)
