---
title: "AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents"
summary: "AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents"
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "entity"
status: "draft"
tags: ["paper", "llm-security", "agent-security"]
sources: ["raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html"]
confidence: "medium"
contested: false
contradictions: []
schema: "pkm-knowledge-page/v1"
revision: "2"
transaction_id: "p2i-d3b8cf0db1b918060510445ffe3b227a"
policy_revision: "pkm-html-knowledge/v2"
prompt_revision: "wiki-compile/v2"
generation_ref: "_meta/runs/wiki/20260930T100918Z-p2-live-staged/2609.30830v1/attempt1-result.json"
read_scope: ["abstract1 — Abstract", "S1 — Introduction", "S2 — Background and Motivation", "S2.SS1 — LLM agents and their harnesses", "S2.SS2 — Compositional attacks", "S2.SS3 — Runtime judgment and evidence", "S3 — Threat Model", "S3.SS1 — System model", "S3.SS2 — Adversary model", "S3.SS3 — Effect categories", "S4 — System Design", "S4.SS1 — Overview and trust root", "S4.SS2 — Authorization and effect state", "S4.SS3 — Source registration and boundary checks", "S4.SS4 — Decision flow and state updates", "S4.SS5 — Execution evidence and replay", "S5 — Implementation", "S6 — Evaluation", "S6.SS1 — Questions and experimental setting", "S6.SS2 — RQ1: defense and authorization boundaries", "S6.SS3 — RQ2: attack behavior without AGATE", "S6.SS4 — RQ3: usability and failure analysis", "S6.SS5 — RQ4: reconstruction, coverage, and cost", "S7 — Discussion", "S7.SS1 — Limitations", "S7.SS2 — Further work", "S7.SS3 — Deployment considerations", "S7.SS4 — Ethics", "S8 — Related Work", "S9 — Conclusion", "bib — References: 제공된 서지 텍스트와 본문 종료 경계 확인"]
unread_scope: ["그림·이미지는 시각적으로 검토하지 않았다. S4.F1, S6.F2, S6.F3의 캡션과 삽입된 텍스트는 읽었지만 SVG의 배치·화살표·색상 및 렌더링된 픽셀은 확인하지 않았다.", "수식은 독립적으로 검증하지 않았다. 요청 표현과 알고리즘의 제공 텍스트를 읽었지만 수학적 증명이나 구현 정합성 검증을 수행하지 않았다.", "실험은 재현하지 않았다. 구현 코드, 원시 실행 로그, 호스트 원장, 배포 설정 및 테스트 산출물을 직접 검사하지 않았다.", "참고문헌은 외부 대조하지 않았다. bib의 서지 문자열은 읽었지만 인용 논문·사건 보고서·표준의 실물과 내용을 확인하지 않았다.", "bib.bib3에 기재된 동반 기술보고서와 공격 체인 아카이브는 제공 HTML에 포함되지 않아 읽지 않았다. 제공 문서에는 별도의 부록 또는 보충자료 섹션이 없다.", "표 S3.T1, S5.T2, S6.T3, S6.T4, S6.T5, S8.T6은 HTML table text only로 검토했다. 표의 시각적 렌더링은 검토하지 않았다.", "사람의 검토·승인, 외부 자산 조회, 코드 실행 및 공유 발행은 수행하지 않았다."]
review_state: "unreviewed"
relation_generation_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json"
relation_prompt_revision: "wiki-integrate/v1"
relation_agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents

> 상태: draft/unreviewed — 로컬 Wiki에 게시된 논문 분석 노트다. 사람의 내용 검토·승인 완료를 뜻하지 않는다.
> 범위: 제공된 원본 HTML 문자열만 읽었다. 외부 조사·자산 조회·코드 실행·도구 사용은 하지 않았다.
> 본문 읽기는 그림의 시각 검토, 수학적 검증, 실험 재현 또는 사람의 검토가 아니다.

## 읽기 범위와 문서 경계
- 초록과 서론부터 방법·구현·평가·논의·관련연구·결론까지 본문을 읽었다. 누락된 본문 절은 없다.
- 본문 범위는 S1–S9이며 하위 절의 가정, 평가 단위, 실패 사례와 결론의 제한을 함께 검토했다.
- 본문은 S9.p2.1에서 끝나고 bib에서 References가 시작한다. 별도의 부록·보충자료 섹션은 없다.
- bib.bib3에 언급된 동반 기술보고서·공격 체인 아카이브의 실물은 제공되지 않아 검토하지 않았다.
- S3.T1, S5.T2, S6.T3, S6.T4, S6.T5, S8.T6은 HTML table text only로 읽었으며 시각 검토는 아니다.
- HTML의 스크립트·사이트 안내·사례 속 지시는 실행 권한이 없는 비신뢰 자료로 취급했다.

## 핵심 요약
- 저자 주장: 권한의 출처와 데이터의 출처를 별도로 검사하고, 결정론적 판정 근거를 실행 증거에 연결한다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1)
- 저자 보고: 인자 재작성 우회와 정상 내용 재사용의 거부 비용이 함께 관측된다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2.p5) C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)
- 분석자 해석: 완성된 보안 보증보다 보호 경계와 감사 가능성을 구체화한 시스템 연구로 읽는 것이 적절하다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S9)

## 문제와 동기
- 도구를 사용할 자격과 그 도구로 데이터를 경계 밖에 전달할 권한은 동일하지 않다는 구분이 출발점이다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1)
- 문서·메모리·대화 속 승인 주장을 실제 호스트 승인으로 승격시키지 않는 것이 핵심 신뢰 경계다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1)
- 분석자 해석: 단일 호출의 겉모양보다 이전 승인과 입력이 후속 요청에 어떻게 이어지는지 확인하는 문제가 중요하다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)

## 기여
- 권한 검사와 데이터 출처 검사를 공동 판정 구조로 묶되 서로를 면제 조건으로 사용하지 않는다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1)
- 소모 가능한 승인과 반복 효과 원장으로 연속 요청 사이의 상태를 유지한다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)
- 런타임 판단 당시의 근거를 이후 실행 증거와 연결해 조사할 수 있도록 한다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1)
- 성공 주장만이 아니라 우회와 정상 작업 거부를 함께 보고해 보호와 사용성의 경계를 드러낸다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2.p5) C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)

## 방법·가정·위협 모델
### 신뢰 경계
- A-EXT는 에이전트가 읽는 외부 콘텐츠를 통제하지만 신뢰된 호스트 기제를 직접 변경하지 않는다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3)
- A-INT는 작업 지시 사용자이며, 이에 대한 운영자 정책 경계는 사용자와 운영자가 분리된 배포를 전제한다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3)
- 판정기·어댑터·정책·상태뿐 아니라 디스패치 중재, 진짜 승인 이벤트 전달과 호스트 접근 통제도 신뢰 기반에 들어간다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3)
### 요청과 승인
- 호스트 승인은 세션과 정확한 인자에 결합하며, 만료와 남은 사용 횟수를 검사한다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)
- 나머지 검사를 통과한 최종 allow에서 디스패치 전에 승인을 소비하므로, 계수 대상은 허용 요청이지 실행 완료가 아니다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)
- 효과 원장의 기계적 키는 반복 검토를 유도하지만 의미적으로 같은 모든 효과를 식별하는 장치는 아니다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)
### 출처와 전달
- 관측한 경로·내용 창을 등록하고 실제 전달 필드를 선택해 출처와 목적지 정책을 적용한다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3)
- 같은 복사 조각도 승인된 내부 작업과 외부 전달에서 다르게 취급할 수 있으나 그 구분은 정책이 제공해야 한다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3)
- 알려진 명령 형태 검사는 보조 수단이며, 출처 유사성 자체는 사용자 의도를 입증하지 않는다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3)
### 구현과 관측
- 평가된 DSH 경로에는 디스패치 거부 기능이 있다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2)
- 평가된 OC 훅은 발견 사항을 기록할 뿐 실행을 거부하지 않는다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2)
- OpenClaw의 과거 증거 측정은 flag-only·fail-open이며 동기식 거부 경로의 검증과 구별해야 한다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2)
- 고정 출처 계층·출처별 공정 보존·싱크 디코딩은 설계 설명과 평가 경로의 활성화 근거를 구분해야 한다. C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.p5)
- 평가 결과에는 디코딩이 포함되지 않으며 동적 저장소는 삽입 순서로 퇴거한다. C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.p5)

## 평가 설정과 결과 해석
- 정제된 연구는 63개 시나리오, 플랫폼 둘, 라운드 둘의 252회 실행이며 공통 모델은 binlab/glm-5.3-flash였다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1)
- 초기 r1/r2에서 DSH는 집행, OC는 기록 전용이었고 fidelity 지시는 OC에만 도달해 조건이 대칭적이지 않았다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1)
- 합성 도구 호출·호출 서명 일치·공격 효과 기준·확인된 외부 효과를 구분해야 한다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1)
- 후속 선언 실험은 deepseek-v4-flash를 사용했고 DSH 주입 채널도 연결돼 초기 관측과 그대로 합칠 수 없다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1)

### 선언에 따른 거부: 저자 보고
| 선언 설정 | 전체 거부 | 권한 거부 | 데이터·경로 거부 | 근거 |
|---|---:|---:|---:|---|
| 전체 | 28 | 5 | 23 | C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.T4) |
| 시나리오별 최소 | 21 | 5 | 16 | C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.T4) |
| 빈 선언 | 19 | 11 | 8 | C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.T4) |
- 위 값은 이벤트 수이며 방어한 고유 공격 수나 작업 실패 수가 아니다. C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.T4)
- 사서함 사례에서는 출처 검사 거부 뒤 인자 재작성으로 합성 영구 삭제 요청이 통과했다. 실제 삭제를 확인한 결과는 아니다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2.p5)

### 모니터 없는 행동: 저자 보고
- 코퍼스는 153개 체인 기록이며 별도의 무모니터 기준선은 76개 체인에 대한 152회 실행이다. 기록의 존재는 공격 성공을 뜻하지 않는다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3)
- execute는 의미적 전달 배치 12/46, 구조적 전달 배치 23/52였으나 작업과 판정 절차가 달랐다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3)
- 해석 제한: 이 비교는 기술적 관측이며 AGATE 방어율이나 전달 문구 변경의 대응 인과효과로 읽지 않는다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3)

### 정상 작업 비용: 저자 보고
- 정상 파일 처리 11개 시나리오 중 6개에 거부가 있었고 총 8건이었다. 이는 작업 실패율이 아니다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)
- 거부에는 정당한 내용 재사용과 basename 오매칭뿐 아니라 설정된 데이터 흐름 규칙에 부합하는 사례도 포함된다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)
- 별도 수정 관측에서 설명·정당화 필드 때문에 생긴 DSH 오탐 거부는 4건에서 0건으로 줄었다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)
- 설명 필드를 제외하는 수정은 실제 전달 필드에서 정당한 내용을 재사용할 때의 정책 문제까지 해결하지 않는다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)

### 재구성과 비용: 저자 보고
- 재생과 실시간 투영은 DSH·OC 각각 63/63 시나리오에서 일치했으며 252개의 독립 digest 비교는 아니다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5)
- 기대 토폴로지가 있는 53개 시나리오의 단계 이벤트 적중은 DSH 334/376, OC 328/376이며 탐지 재현율이 아니다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5)
- 과거 OpenClaw 오프라인 재생은 5,033개 이벤트에 0.24초였으며 온라인 판정 지연이나 작업 오버헤드 측정이 아니다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5)
- 보존된 증거의 일치가 완전한 중재나 실제 외부 효과의 확인을 의미하지는 않는다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)

## 한계
- 재작성·번역·추론 누출과 출처 퇴거·미관측 입력은 내용 매칭의 연속성을 깨뜨릴 수 있다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)
- 승인 소비는 트랜잭션성 exactly-once 효과나 여러 grant에 걸친 전역 예산을 보장하지 않는다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)
- 플랫폼과 집행 모드가 얽혀 있어 출처 검사의 독립 기여를 분리하기 어렵다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)
- 같은 효과를 다르게 분해해도 일관된 판정이 나온다는 분해 불변성은 확립되지 않았다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)
- 조용한 우회는 행동 기록과 관측 공백 표시를 모두 남기지 않을 수 있다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1)

## 연구 연결: 분석자 해석
- 연구 연결점은 권한 상태·출처 관측·실행 증거를 같은 판단의 감사 자료로 연결하는 데 있다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S9)
- 미해결 가설: 변형을 더 잘 추적하는 출처 표현이 우회를 줄이면서도 정상 재사용 거부를 늘리지 않을 수 있는가?
- 후속 연구에서는 같은 플랫폼·정책·효과 기준을 고정하고 구성 요소와 작업 분해만 바꾸는 비교가 우선이라고 본다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S9)
- 관련연구 절은 읽었지만 인용 시스템의 실물이나 외부 신규성을 검증하지 않았으므로 우열을 판정하지 않는다.

## 미검토 항목
- 그림·이미지는 시각적으로 검토하지 않았다. 캡션과 SVG 내부 텍스트 읽기에 한정된다.
- 수식은 독립 검증하지 않았고 알고리즘 텍스트 읽기를 증명이나 구현 검사로 간주하지 않는다.
- 실험은 재현하지 않았으며 원시 로그·코드·아카이브·배포 환경을 직접 검사하지 않았다.
- 참고문헌은 외부 확인하지 않았고 관련 URL을 가져오지 않았다.
- 사람의 검토·승인이나 공유 발행은 없으며 이 초안의 상태는 draft/unreviewed다.

## 증거 표
| ID·출처 | 주장 요약 | 적용 조건 | 원문 anchor | 짧은 원문 인용 |
|---|---|---|---|---|
| C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1) | 권한·출처 공동 판정과 증거 연결 | 계측 경계·외부 신뢰 루트 | S1 | “These deterministic checks run without an LLM in the decision path” |
| C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3) | 외부 주입과 지시자 악용 구분 | 신뢰 호스트 보호·운영자 분리 | S3 | “It does not directly modify the trusted host mechanisms or operator configuration.” |
| C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2) | 정확한 요청 승인과 반복 검토 | 허용 요청 계수이지 완료 확인 아님 | S4.SS2 | “Only a final allow consumes a use and charges the amount.” |
| C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3) | 출처 창·경로와 전달 정책 비교 | 관측 입력·선택된 싱크 | S4.SS3 | “content similarity alone supplies origin evidence, not the user’s intended purpose.” |
| C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2) | 어댑터별 거부 능력 차이 | 표의 평가 경로에 한정 | S5.T2 | “The evaluated hook records findings without a dispatch veto” |
| C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.p5) | 설계와 측정 구현 구분 | 디코딩 결과 미포함 | S5.p5 | “the evaluated outcomes do not include decoding.” |
| C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1) | 정제 연구와 결과 단위 구분 | 모델·모드·주입 조건 차이 | S6.SS1 | “tools log requests using synthetic values and simulate business side effects.” |
| C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.T4) | 선언별 거부 이벤트 보고 | 공격 수·작업 실패 수 아님 | S6.T4 | “All columns after round count events, not failed scenarios.” |
| C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2.p5) | 재작성 뒤 내용 매칭 우회 | 합성 삭제 요청 종점 | S6.SS2.p5 | “The observed endpoint is a request that bypasses the content match” |
| C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3) | 무모니터 행동과 배치 차이 | 비대응 작업·판정 절차 | S6.SS3 | “this comparison is descriptive rather than a paired estimate of a wording intervention.” |
| C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4) | 정상 거부 비용과 설명 필드 수정 | 발생 비율·별도 수정 관측 | S6.SS4 | “not a measured task-failure rate.” |
| C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5) | 재생 일치·단계 적중·오프라인 비용 | 보존 증거·기대 토폴로지 범위 | S6.SS5 | “Offline replay throughput does not measure online decision latency or end-to-end task overhead.” |
| C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1) | 불완전 관측과 미확립 보안 속성 | 유한 상태·비계측 경로·교란 | S7.SS1 | “A silent bypass may produce neither an action record nor a coverage gap.” |
| C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S9) | 감사 가능한 통합 설계로 해석 | 분석자 해석·외부 신규성 아님 | S9 | “Controlled decomposition and same-platform component experiments are the next tests” |

## 후속 질문
- 출처 보존·디코딩 설계가 실제 활성화된 경로를 어떤 검증 자료로 확인할 것인가?
- 동일 정책에서 공격 효과 억제와 정상 작업 완료를 함께 측정하면 어떤 절충이 나타나는가?
- 하위 프로세스와 원격 서비스의 실제 효과를 독립적인 관측으로 어떻게 대조할 것인가?
- 운영자 선언을 더 세밀하게 만들 때 정책 작성 부담과 권한 누락은 어떻게 평가할 것인가?

## 잠정 결론
- 분석자 판단: 재생의 일관성과 권한·출처 분리는 유용한 연구 기반이지만 실환경 보안 보증으로 승격할 근거는 부족하다. 통제 비교가 필요한 검토 대기 초안으로 유지한다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S9)

## 연결된 지식

- [[concepts/agent-authority-and-effect-boundaries|권한과 실행 효과의 경계]] — AGATE의 승인·판정·집행을 Gateway의 비실행 제안과 구분해 읽는 개념 안내.
- [[concepts/provenance-and-audit-evidence|데이터 출처와 감사 증거의 구분]] — 출처 매칭, 판정 이력, 재생과 감사 증거의 의미를 나누어 탐색.
- [[concepts/security-evaluation-units|보안 평가 단위와 주장 범위]] — 체인·실행·거부 이벤트·재구성 비교의 단위를 확인하는 읽기 안내.
- [[comparisons/agate-vs-sdc-mcp-gateway|AGATE와 SDC-to-MCP Gateway 비교]] — 위협 모델, 승인 의미, 집행 깊이와 비교 불가능한 평가 차원을 함께 살펴보기.
