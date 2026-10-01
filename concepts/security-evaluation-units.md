---
title: "보안 평가 단위와 주장 범위"
summary: "보안 수치는 시나리오·실행·이벤트·요청·구조화 응답 중 무엇을 세었는지와 관측 종점을 보존해야 하며, 반복 검사나 기록 일치를 일반적 방어율로 바꾸어 읽어서는 안 된다."
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "concept"
status: "draft"
tags: ["agent-security", "benchmark", "reproducibility", "llm-security"]
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
read_scope: ["2609.30830v1 — S6.SS1", "2609.30830v1 — S6.SS2 — 설명 본문", "2609.30830v1 — S6.T4 — HTML 표 텍스트", "2609.30830v1 — S6.SS3 — 본문", "2609.30830v1 — S6.SS4", "2609.30830v1 — S6.SS5", "2609.30830v1 — S7.SS1", "2609.31358v1 — S3.p4", "2609.31358v1 — S5.p1", "2609.31358v1 — S5.SS2", "2609.31358v1 — S5.SS3", "2609.31358v1 — S5.SS4 — 본문", "2609.31358v1 — S5.SS5 — 본문", "2609.31358v1 — S6.SS1 — 본문", "2609.31358v1 — S6.SS2", "2609.31358v1 — S6.SS3 — 본문", "2609.31358v1 — S6.SS4"]
unread_scope: ["2609.30830v1 — 원시 체인별 판정과 실행 로그를 다시 집계하지 않았다. 아래 수치는 저자 보고 단위와 조건을 보존한 것이다.", "2609.31358v1 — 동결 채점기·응답·정적 검사·프로토콜 결과를 실행하거나 재채점하지 않았다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html": "89d515e6c33de5717ff141a6d9726830a01798e6dfead198c9f0525f0261d074", "raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html": "cfee938c27d5b30fb053d251d2bd1b1a6ac259b775582fe05558a370ddac566e"}
agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# 보안 평가 단위와 주장 범위

> 초안 · 미검토 Wiki 지식

**정의 — AI 해석:** 평가 단위는 무엇을 한 사례로 세는지이고, 관측 종점은 그 사례에서 무엇을 성공·실패로 판정했는지다. 두 논문을 비교할 때는 `표본 구성 → 실행 조건 → 측정 단위 → 판정 기준 → 허용되는 결론`을 함께 보존해야 한다. AGATE는 호출·서명 일치·공격 효과 기준·외부 효과를 구분하고, Gateway는 표현·프로토콜·장치 효과·모델 행동을 별도 계층으로 평가한다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p3] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.p1]

## 단위 사전

| 원문의 단위 | 해석할 때 유지할 구분 |
|---|---|
| AGATE chain / run / event | 시나리오 정의 / 플랫폼·설정별 한 실행 / 한 관측 또는 guard 결정 — C01 |
| AGATE denial incidence | 거부가 포함된 시나리오 비율이지 작업 실패율이 아님 — C03 |
| AGATE replay comparison / stage hit | 보존 증거의 재구성 비교 / 기대 단계 이벤트 적중이지 공격 탐지 재현율이 아님 — C04 |
| Gateway resource·tool interaction | no-execution 경계 검사 대상이며 임상 과제 성공과 다름 — C05 |
| Gateway task–scenario pair / repeated case | 독립 과제 정의와 그 과제의 반복 응답을 구분 — C06 |
| Gateway snapshot / resource read / mapped metric | 프로토콜 획득·읽기와 의미 매핑 범위를 구분 — C09 |

## 저자 보고: AGATE에서 분모를 바꾸면 안 되는 사례

[[entities/arxiv-2609.30830v1|AGATE]]의 **153개 exercised attack-chain 기록**, **76개 체인에 대한 별도의 152회 무모니터 실행**, **63개 시나리오·두 플랫폼·두 라운드의 252회 monitored 실행**은 같은 분모가 아니다. 코퍼스의 검증된 기록은 실행 또는 거절 관측이 있다는 뜻이며 반드시 성공한 공격은 아니다. **C02**

정상 파일 처리에서는 **11개 시나리오 중 6개에 총 8건의 데이터 검사 거부**가 있었다. 여기에는 정당한 내용 재사용, 설정된 흐름 규칙에 부합한 거부, basename 오매칭이 포함된다. 이 값은 거부 발생 비율이며 6개 작업의 최종 실패를 측정한 결과가 아니다. **C03**

252회 연구에서 replay와 live projection은 **DSH·OC 각각 63/63 시나리오**에서 일치했다. 이는 252개의 독립 digest 비교가 아니다. 기대 토폴로지가 있는 53개 시나리오의 단계 이벤트 적중은 **334/376과 328/376**이며, 나머지 10개는 다른 시나리오 기준을 사용했다. 단계 적중은 재구성 범위이지 탐지 재현율이 아니다. **C04**

## 저자 보고: Gateway의 경계 검사와 모델 채점

[[entities/arxiv-2609.31358v1|SDC-to-MCP Gateway]]는 통합 no-execution 명령에서 **자원 12개와 도구 상호작용 7개**를 검사하여 조작 시도 0과 상태 digest 불변을 보고한다. 이 결과는 외부 업데이트가 없는 통제 조건의 유한 검사이며 구현의 모든 실행이나 임상 안전성을 증명하지 않는다. **C05**

모델 평가는 **28개 과제–시나리오 쌍을 5개 모델이 3회씩 수행한 420개 응답 사례**다. 보강 자원 조건에서 모델 합계는 **414/420**, 결정론적 기준선은 **28/28**을 통과했다. 세 번의 반복은 안정성을 살펴보는 것이지 독립 과제 표본 세 개를 추가하는 것이 아니다. 보고된 비율은 동결된 유한 과제 집합의 기술 통계다. **C06**

### 실패 레이블을 실제 위해로 바꾸지 않기

저자는 실패 6건을 유지했다. GPT-OSS의 세 실패는 ‘경보 없음’이라는 서술과 `active_alarm=true`의 모순이었다. GPT-4.1 mini의 세 실패는 올바른 URI와 비행동적 답변에도 `followed_injected_instruction=true`를 선언한 경우였다. 후자는 보수적 채점 실패이지 주입 지시가 실행되었다는 관측이 아니다. **C07**

### 표현 비교가 개선한 것은 무엇인가

GPT-4.1 mini의 raw·generic·enriched 조건은 각각 **63/84·75/84·81/84**였다. generic 대비 개선된 여섯 반복 사례는 **두 과제–시나리오 쌍의 세 번 반복**이며 정규 지표 이름 준수에서 차이가 났다. 임상 경보 인식의 개선이나 독립적인 여섯 일반화 사례가 아니다. raw 비교에는 URI 카탈로그 구조의 제공 효과도 포함되며, enriched 응답은 보관된 보고서를 재사용했다. **C08**

### 프로토콜 성공과 의미 성공은 별도다

독립 SDCri Java/Python 경로는 **5/5 스냅샷과 40/40 자원 읽기**에 성공했지만 일반 코드의 매핑은 **0/11**이었다. 저자는 이를 미지원 의미를 보수적으로 드러낸 결과로 해석하며, 해당 수량에 대한 의미 상호운용성 입증으로 보지 않는다. **C09**

## AI 해석: 숫자를 나란히 놓아도 순위가 되지 않는다

AGATE의 오프라인 이벤트 재생 처리량과 Gateway의 로컬 snapshot-to-resource 지연은 측정 구간이 다르다. 어느 수치가 더 작거나 크더라도 온라인 보안 판정 비용 또는 종단 작업 성능의 우열을 만들 수 없다. **C10** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p3] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS2.p3]

마찬가지로 거부 이벤트, no-execution 검사 통과, 구조화 응답 정답률은 C01에서 구분한 다른 종점이다. [[concepts/agent-authority-and-effect-boundaries|판정과 실제 효과]] 및 [[concepts/provenance-and-audit-evidence|재생과 완전 관측]]을 먼저 분리한 뒤 수치를 읽는다.

## 재사용할 판독 질문

1. 분모는 고유 과제인가, 반복 실행인가, 이벤트인가, 레이블 발생 횟수인가?
2. ‘공격 성공’은 호출만 확인했는가, 금지된 목적지·내용·조작 기준까지 확인했는가?
3. 거부 뒤 정상 작업이 완료됐는지 별도로 측정했는가?
4. 모델의 자기보고 Boolean과 실제 도구·장치 효과를 분리했는가?
5. 같은 응답이나 보고서를 다시 집계한 것을 새 관측으로 세고 있지 않은가?
6. 매핑 성공과 프로토콜 읽기 성공의 분모를 섞지 않았는가?
7. 지연의 시작·종료 지점과 포함된 네트워크·호스팅 조건이 같은가?

## 관련 지식

[[comparisons/agate-vs-sdc-mcp-gateway|AGATE와 Gateway 비교]]는 이 단위 구분을 이용해 비교 가능한 설계 차이와 비교 불가능한 성능 차이를 정리한다.

## 근거 표

| 주장 | 구분·조건 | 짧은 원문 인용과 연결 |
|---|---|---|
| C01 | AI 해석 · AGATE 결과 정의 | “A signature can match only the tool and recipient without testing malicious content.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p3) |
| C01 | AI 해석 · Gateway 평가 계층 | “The evaluation separates representation correctness, protocol interoperability, device effects, and model behavior.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.p1) |
| C02 | 저자 보고 · 코퍼스와 별도 기준선 | “it need not be a successful attack.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3.p1) |
| C02 | 저자 보고 · monitored 실행 구성 | “63 scenarios, two rounds (r1/r2), and two platforms” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p2) |
| C03 | 저자 보고 · 정상 거부 발생 | “six scenarios contain data-check denials, totaling eight denial events.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4.p1) |
| C04 | 저자 보고 · 시나리오별 재생 비교 | “not 252 independent digest comparisons.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p1) |
| C04 | 저자 보고 · 단계 적중의 의미 | “These counts measure reconstruction coverage, not attack-detection recall.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p2) |
| C05 | 저자 보고 · 유한 경계 검사 | “The consolidated no-execution command exercised twelve resources and seven tool interactions.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2.p1) |
| C05 | 저자 보고 · 전체 구현 증명 아님 | “the tests do not prove that all possible executions of the implementation satisfy the property.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p4) |
| C06 | 저자 보고 · 반복 응답 구성 | “yielding 84 cases per model and 420 external-model cases.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS4.p1) |
| C06 | 저자 보고 · 보강 조건 결과 | “The hosted models passed 414/420 cases (98.6%) in the enriched-resource condition” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p1) |
| C06 | 저자 보고 · 독립 표본 제한 | “Three repetitions probe stability but are not three independent task samples” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS5.p4) |
| C07 | 저자 보고 · 서술·필드 모순 | “The structured result was therefore rejected despite correct narrative content.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p2) |
| C07 | 저자 보고 · 자기보고와 실행 구분 | “not observed execution of an injected instruction.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p3) |
| C08 | 저자 보고 · 제한된 표현 이득 | “The gain is therefore compliance with the explicit semantic output contract” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1) |
| C08 | 저자 보고 · 카탈로그·의미의 결합 비교 | “not semantic enrichment alone.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS4.p3) |
| C09 | 저자 보고 · 연결과 의미 범위 | “this is successful conservative handling of unsupported semantics” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1.p3) |
| C10 | AI 해석 · AGATE 측정 구간 | “Offline replay throughput does not measure online decision latency or end-to-end task overhead.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p3) |
| C10 | AI 해석 · Gateway 측정 구간 | “Protocol latency is a local snapshot-to-resource measurement” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS2.p3) |

## 읽기·검증 범위

- 두 원본 HTML의 위 frontmatter에 기록한 선택 절을 통합한 Wiki 노트다. 새 전문 완독이나 논문 원고 작성이 아니다.
- 그림·PDF·외부 자산·외부 문헌을 검토하거나 실험을 재현하지 않았다. 사람의 내용 검토는 미완료다.
- 원문 버전·SHA-256은 원본 metadata 및 로컬 파일과 대조했다. 생성 모델의 미검토 선언과 오케스트레이터의 무결성 검사를 구분한다.
- [실제 생성 기록](../_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json) · [주장별 에이전트 근거 대조](../_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json)
