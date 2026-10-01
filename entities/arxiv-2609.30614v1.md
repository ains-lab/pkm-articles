---
title: "Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces"
summary: "이 논문은 에이전트가 자신을 구속하는 정책과 분류를 작성하는 authorship hazard에 대응해 게시 권한 분리와 협정 기반 도구 경계 집행을 제안하지만, 인간 검토의 효과·비정형 정보 보호·허용된 행동의 합성까지 안전성을 확립하지는 않는다."
created: "2026-10-01"
updated: "2026-10-01"
last_reviewed: null
type: "entity"
status: "draft"
tags: ["paper"]
sources: ["raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf"]
confidence: "medium"
contested: false
contradictions: []
schema: "pkm-knowledge-page/v1"
revision: "1"
transaction_id: "pdf3-9ed77666bcba802e33823720750afe4d"
policy_revision: "pkm-html-pdf-text-knowledge/v3"
prompt_revision: "wiki-compile/v3"
generation_ref: "_meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/2609.30614v1/attempt1-result.json"
read_scope: ["page=1", "page=2", "page=3", "page=4", "page=5", "page=6", "page=7", "page=8", "page=9", "page=10", "page=11", "page=12", "page=13", "page=14", "page=15", "page=16", "page=17", "page=18", "page=19", "page=20", "page=21", "page=22", "page=23"]
unread_scope: ["모든 그림·이미지 및 이미지 전용 내용: 미검토", "수식·레이아웃·표 구조: 텍스트 추출 모호성, 시각 검증 미수행", "물리적 page=5, page=7, page=9의 Figure 1–3은 추출된 캡션과 레이블 텍스트만 읽었으며, 도형·연결선·배치의 시각적 의미는 확인하지 않았다.", "Proposition 1의 형식기호, 승인 큐 수식, 표의 다단 행·열 대응은 제공된 텍스트와 주변 설명으로 확인 가능한 범위만 사용했다. 원 PDF의 수식 조판과 표 구조를 시각적으로 대조하지 않았다.", "스캔 또는 이미지 전용 내용은 처리하지 않았으며 OCR을 수행하지 않았다. 논문이 평가 대상으로 언급하는 첨부 스캔의 실제 내용도 제공되지 않았다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf": "a33d6b4d5ce71d59c9ea98170e5ad9d58a9b6225bca042e1cedb08ee95e00a0d"}
agent_review_ref: "_meta/runs/wiki/20261001T001438Z-pdf-wiki/reviews/2609.30614v1-attempt1-agent-review.json"
---

# Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces

> 초안 · 미검토. 아래 실험 수치는 모두 저자 보고이며 독립 재현, 형식 검증, 사람의 검토 또는 실제 게시 완료를 뜻하지 않는다.

## 읽은 버전과 범위

- 저자: Seungho Lee · Changbin Lee, Korea Trade Network (KTNET).
- 버전: `2609.30614v1`. 제공된 원문은 working draft로 표시되어 있다.
- 원본 식별 경로: `raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf`.
- 입력에 제공된 PDF SHA-256: `a33d6b4d5ce71d59c9ea98170e5ad9d58a9b6225bca042e1cedb08ee95e00a0d`.
- 입력에 제공된 metadata 경로: `raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.json`.
- 입력에 제공된 metadata SHA-256: `4525b94814015ced57de058196037ccb90f4ea66b599ce6295a8fd888f8e3e81`.
- 실제 읽은 범위는 물리적 `page=1`부터 `page=23`까지 제공된 내장 텍스트 전체다. 결론, Author Contributions, Appendix A, References를 포함하며 미독 텍스트 페이지는 없다. 인용의 페이지는 인쇄 쪽수가 아니라 PDF의 물리적 순서다.
- 해시는 입력의 식별값을 기록한 것이며 이 응답에서 재계산하지 않았다. 텍스트 전체를 읽었다는 선언은 이미지·수식·표의 시각적 완전 이해를 뜻하지 않는다.

## 문제와 동기

**저자 보고 — 생성 품질과 게시 권한은 다른 문제다.** 정책이나 매핑을 잘 생성하는 것만으로 그 산출물이 실제 거버넌스 평면에 들어가도 된다는 인가가 성립하지 않는다. 게시된 정책과 어휘가 PDP의 판단 근거가 되는 환경에서는 게시가 권한을 바꾸는 사건이다. 저자는 정책의 적용 대상인 에이전트가 그 정책까지 작성하는 자기수정 문제를 **authorship hazard**라고 부르고, Principle P를 “An agent is a subject of the governance plane and never an author of it”로 제시한다. 에이전트의 초안 작성은 허용하되 최종 규범 작성 권한과 분리하자는 뜻이다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=2]

**조사의 범위도 제한되어 있다.** 저자는 ODRL 정책·온톨로지·정렬 생성 시스템 4개의 평가에서 별도의 게시 인가 단계를 찾지 못했다고 보고한다. 이는 생성 연구가 자기 평가 범위에서 잘못됐다는 비판이 아니라, 생성 품질 평가와 운영 인가 사이의 접점을 별도로 다뤄야 한다는 문제 제기다. 비포괄적인 선정 조사이므로 이 결과를 모든 선행연구의 부재 증명이나 보편적인 최초성으로 읽지 않는다. **C26** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=20]

## 핵심 아이디어와 설계

### 초안 작성자와 게시 주체의 분리

**Authorization channel을 없애는 구성이다.** registration agent는 매핑과 정책을 초안으로 만들지만 publishing API에 접근하지 못하고 게시용 approval artifact도 보유하지 않는다. API가 요구하는 자격 증명은 에이전트 신원이 아니라 인간 검토 뒤의 승인 산출물이다. 이 구분은 에이전트의 직접 게시를 불가능하게 만드는 구성 논증이지, 인간을 거쳐 영향을 미치는 모든 공격까지 차단하는 시스템 전체 보장이 아니다. **C03** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=5]

**Influence channel은 남으므로 검토 절차로 다룬다.** 제출물을 현재 게시 상태에 대한 diff로 만들고, 권한을 넓히는 변경 등을 결정론적으로 표시한다. 표시된 diff는 두 승인자의 elevated review로, 표시되지 않은 diff도 인간이 읽는 ordinary review로 보낸다. 최초 게시에는 비교할 이전 상태가 없어 전체 문서를 elevated 경로로 보낸다. 분류기의 역할은 인간 검토의 대체가 아니라 검토 경로와 부담의 분배다. **C04** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=6]

**승인과 게시 사이의 동일성도 묶는다.** approval artifact는 정확한 초안의 해시, 단회 사용, 짧은 유효기간, 승인자 신원에 결합되며 에이전트가 접근할 수 없는 서비스가 발급한다. 따라서 승인 후 내용을 바꾸어 게시하는 경로는 설계상 실패해야 한다. 다만 논문은 이 authorization 경로를 공격해 검증한 결과와 구성 요구사항을 구분한다. **C05** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=7]

### 분류 변경도 정책 작성이다

정책 문자열이 그대로여도 그 정책이 참조하는 민감도 분류가 바뀌면 보호 대상이 달라진다. 논문의 예처럼 필드를 보호 클래스 밖으로 옮기면 duty 자체가 여전히 존재하면서도 적용 집합이 줄어드는 조용한 변경이 가능하다. 대응 설계는 분류를 중앙 vocabulary registry의 속성으로 두고, 모든 분류 변경을 elevated review로 보내며 영향을 받는 기존 협정도 재검토 대상으로 나열하는 것이다. **이 registry 관리가 실제 프로토타입에 이미 구현됐다는 뜻은 아니다.** **C06** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=7]

### 협정의 duty를 실행 경계로 전달한다

실행 측 연결은 `negotiated ODRL agreement → duty compiler → tool gateway → 모델행 payload`로 이해할 수 있다. 도구 발견 단계의 필터는 어떤 도구를 볼 수 있는지 정하지만, 허용된 호출이 돌려준 응답에서 필드를 제거할 위치는 제공하지 않는다. 값에 작용하는 duty는 호출과 반환 경로에서 집행해야 한다는 것이 핵심이다. 따라서 discovery filtering과 응답 내용 통제는 대체 관계라기보다 다른 경계를 담당한다. **C07** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=8]

용어를 좁혀 읽어야 한다. 여기서 **AnonymizeFieldClass는 통계적 익명화가 아니라 필드 suppression**이다. 모델에 전달할 payload에서 지정 클래스의 필드를 제거하는 것이며, 다른 필드나 자유 텍스트에 남은 동일 정보 또는 허용값에서 유도되는 정보를 일반적으로 없애는 기법은 아니다. **C25** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=17]

## 가정과 보장 경계

**신뢰 기반은 모델 밖에 있다.** 공격자는 모든 planner 출력을 통제하고 임의 초안과 하위 에이전트를 만들 수 있지만, EDC·executor·gateway·게시 및 승인 서비스·registry 같은 신뢰 구성요소를 침해하거나 암호를 깨지는 못한다고 가정한다. 인간 승인자는 정직하지만 주의력이 유한하다. 따라서 결과는 모델을 신뢰하지 않는 대신 집행 인프라와 승인 서비스를 신뢰하는 위협 모델에 속한다. **C02** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=4]

**재위임은 평가된 방어가 아니라 설계다.** 소유자가 ceiling을 정하고 보유자가 그 아래에서 추가로 권한을 줄이며, 신원·계보 attestation을 제시해 PDP가 권한을 도출하는 방식을 제안한다. 그러나 ceiling은 자식이 PDP에서 얻을 수 있는 권한을 제한할 뿐 부모가 합법적으로 가진 정보를 프롬프트로 전달하는 것을 막지 않는다. Case C가 실행되지 않았으므로 이 설계를 confinement이나 검증된 재위임 방어로 표현하지 않는다. **C08** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=9]

**명시적으로 해결하지 않는 위협이 중요하다.** T5는 허용된 행동들을 합성해 금지 결과를 만드는 경우이고, T6는 부모가 합법적으로 보유한 데이터를 자식의 ceiling 밖으로 전달하는 경우다. per-action 접근 통제는 계획 전체의 의미를 보지 못하고 정책 평면 밖의 정보 흐름도 관측하지 못한다. 따라서 개별 호출의 적법성을 전체 작업의 안전성으로 승격할 수 없다. **C09** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=4]

## 저자가 보고한 평가와 결과

### Case B — 모델에 도달하기 전의 값 노출

**결정론적 경계 측정:** 모델을 호출하지 않는 105건 risk set에서 prompt-only와 discovery filtering은 각각 **105/105**, compiled는 **0/105**의 보호 F2 값을 모델행 payload에 남겼다. compiled의 허용 F0/F1 과잉 제거도 0이었다. 단, 분모는 원 응답에 보호값이 있고 이름 있는 필드로 주소 지정할 수 있는 사례다. 저자는 compiled의 Wilson 95% 구간을 **0–3.5%**로 제시하며, 유한 코퍼스의 무노출 관측을 일반적인 실패 확률 0으로 읽지 말라고 제한한다. **C10** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=11]

**더 어려운 형태에서는 실패했다.** 자유 텍스트·첨부 스캔·유도 가능한 값·값의 조각을 포함한 별도 스트레스 집합 16건 중 literal scorer로 검출 가능한 7건은 compiled에서도 **7/7 노출**이었다. 나머지 9건은 해당 probe로 보이지 않아 어느 방향으로도 결론을 내리지 않았다. 따라서 비검출 사례를 방어 성공으로 세거나, 이름 있는 필드 집합의 결과를 모든 민감 정보 보호로 확장하면 원문의 부정적 결과를 지우게 된다. **C11** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=11]

**모델을 넣어도 context 노출과 출력 누출은 다른 지표다.** 9개 model/runtime 구성과 3개 조건의 총 1,320회 호출에서 prompt-only와 discovery filtering은 정상·공격 과제 각각 **220/220 context 노출**, compiled는 각각 **0/220**이었다. 정상 과제 성공은 순서대로 **219/220, 218/220, 219/220**이었다. 공격 과제의 최종 출력 누출은 **49/220, 57/220, 0/220**이지만, 한 로컬 구성이 다른 구성보다 더 많은 반복을 차지하는 불균형 설계다. 저자는 출력 누출의 조건 간 작은 차이를 우열로 읽지 않으며, 올바르게 답한 모델도 보호값을 이미 받았다는 점을 강조한다. **C12** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=12]

### Case E — 제약의 출처가 실제 협정인가

최소 프로파일 확장 뒤 `AnonymizeFieldClass` duty가 실제 협상으로 만들어진 양쪽 협정에 남고, 기존 compiler와 gateway에 그대로 들어갔다고 보고한다. Case B의 risk set을 이 협정으로 재생한 결과는 제약의 출처를 fixture에서 협정으로 바꾸어도 연결이 유지되는지 확인한 것이다. **별도의 독립적인 gateway 효과 측정으로 중복 집계하지 않는다.** Appendix A의 term·제약 스키마·등록 지점 설명도 읽었지만 패치 적용이나 validator 실행은 하지 않았다. **C13** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=13] ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=22]

Authorization invariance의 협상 조건에도 한정이 있다. 12개 협상 검사에서 최종 성립한 **3개 협정은 모두 제공자가 그 시점에 저장한 definition과 같았다.** 하지만 게시 후 definition이 확대되면 과거 offer를 인용한 요청에도 확대된 정책이 돌아왔다. 따라서 측정된 경계는 “소비자가 예전에 본 offer”가 아니라 “제공자의 현재 저장 정책”이다. **C14** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=13]

**출처 연결과 구현 완성도를 분리해야 한다.** 협정이 주는 것은 클래스 수준의 규범적 duty이며 구체적인 필드 이름으로의 매핑은 로컬 분류 메타데이터다. 정책급 게시 통제를 받는 registry-held classification은 설계돼 있고 Case D에서 모델링됐지만 프로토타입에 구현되지 않았다. 이 연결 고리를 생략하면 “모든 집행 매개변수가 승인된 협정에서 나온다”는 과도한 결론이 된다. **C15** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=17]

### Case D — 초안 게시가 권한을 얼마나 바꾸는가

초안보다 먼저 동결한 요청 24개를 사용해, 하나의 게시 상태에 대한 초안 380개를 각각 적용하고 판정 변화를 셌다. no gate에서는 **authorization reversal 80건, duty neutralization 4건**이었다. 표시되지 않은 초안만 보면 V1은 **49건의 reversal**, V2는 **0건**이었다. reversal은 기준 상태에서 거부된 요청이 허용으로 바뀐 사건이므로 “성공한 초안 80개”라는 뜻이 아니다. V1도 기존 외부 시스템이 아니라 저자 분류기의 ablation이다. **C16** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=13]

가장 중요한 차이는 정책 텍스트 밖에서 발생했다. 분류 공격 초안 **50개 중 41개**가 실제 판정을 바꾸었고 이 공격군이 **80건 중 49건**의 reversal을 만들었다. 정책 diff만 보는 V1이 이 변경을 보지 못하고 모든 재분류를 표시하는 V2가 검토로 보내는 것은 구성상 결정된다. 측정의 핵심은 분류기의 학습 능력이 아니라 **정책 문자열을 그대로 둔 재분류도 권한 판정을 바꾼다**는 의미론적 효과다. **C17** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=14]

그 대가는 검토량이다. 인간 elevated review로의 이관은 **140/380에서 270/380**, 즉 **36.8%에서 71.1%**로 늘었다. 별도의 literal-embedding 초안 **50개, 13.2%**는 gateway가 자동 거부하므로 인간 검토 이관에 합산하면 안 된다. 분류 변경의 방향을 따지지 않는 규칙은 정당한 분류 강화에도 검토 부담을 부과하며, 이러한 비율은 공격 중심 코퍼스의 구성에 의존한다. **C18** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=14]

**V2의 0은 review 결과가 아니라 routing 결과다.** Case D는 사람 대신 classifier를 사용하고 flagged 초안을 caught로 세었다. 따라서 승인자의 피로·사회공학·재분류의 의미를 이해하는 능력은 측정하지 않았다. evaluator 역시 EDC PDP가 아니라 논문 규칙의 재구현이다. 이 결과를 connector에서 검증된 차단율이나 실제 인간 검토의 탐지율로 표현해서는 안 된다. **C19** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=16]

### 승인 용량 — 중앙화의 실패와 연합형의 조건

최저 초안 발생률을 사용한 중앙 큐 격자에서 승인자 **3명**은 참가자 **200명**까지 유지됐지만 다음 점인 **500명**에서 발산했고, 승인자 **30명**은 **3,000명**까지 유지됐다. 이는 정해진 승인자별 검토 용량과 도착률의 provisioning 결과이지 메커니즘이 부과하는 보편적인 참가자 상한이 아니다. 참가자별 quota가 flooding을 국소화하는 것과 전체 도착량이 서비스 용량을 넘는 문제도 별개다. **C20** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=15]

Case D5의 연합형 구조에서는 참가자가 자체 초안을 검토하고 중앙 풀은 어휘·분류 정의·분류기 변경만 맡는다. 중앙 포화점은 **`N* = KcC/(λμ)`**로 옮겨가지만 없어지지 않는다. 실제 운영에서 중앙 검토 비중 **μ가 얼마나 작은지 측정하지 않았고**, 일정 도착률 시뮬레이션이라 안정 상태의 대기시간 차이를 실증한 결과도 아니다. **C21** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=15]

### Case A — 매 행동 판정과 철회의 비용

Per-action 경로의 추가 지연은 도구 호출당 중앙값 **20.4 ms**, 실제 측정한 **50-step plan당 1,019 ms**였다. 이는 협정 조회·철회 조회·로컬 평가를 포함한 testbed 비용이며, 네트워크 없는 필드 변환 microbenchmark와 다른 구간이다. **5초 캐시**는 지연을 낮추지만 첫 철회 거부를 per-action의 **34 ms**에서 **5,025 ms**로 늦추고, 그 사이 **101개 결정**을 계속 허용했다. 비용과 철회 신선도가 같은 설정 손잡이에 연결되어 있다. **C22** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=16]

추가로, 협정만 읽고 철회를 별도로 조회하지 않은 경로는 **30초 동안 440개 결정에서 거부하지 않았다.** 협정 객체에 철회 상태가 자동 반영된다고 가정해서는 안 된다는 구현상 주의점이다. 이 관측 창 밖에서도 영원히 거부하지 않는다고 확대 해석하지 않는다. **C23** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=16]

### 별도 출력 연구 — 거절도 비공개성을 뜻하지 않는다

보호값이 이미 context에 들어간 별도 prompt-only 연구에서 공격 시행 **900회 중 39회**가 최종 답변에 보호값을 누출했고, 그중 **24회**는 거절하면서 보호값을 그대로 인용한 경우였다. 나머지 **15회**는 일반적인 공격 순응이었다. 이 연구는 모델의 사후 출력 행동을 본 것이며 앞의 Case B와 합산할 수 없다. 거절 문구의 존재를 데이터가 모델에 전달되지 않았다는 증거나 비공개성의 증거로 취급하면 안 된다. **C24** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=17]

## 한계와 반론

핵심 한계는 다음처럼 분리해서 읽는 편이 정확하다.

- **설계와 구현:** 게시 권한 분리, registry-held classification, 재위임 ceiling의 서술이 동일한 구현·평가 수준을 갖지 않는다.
- **쉬운 데이터 형태와 어려운 정보 형태:** 이름 있는 필드 제거의 성공은 자유 텍스트나 파생 정보 보호를 대신하지 않는다.
- **검토 경로와 검토 품질:** elevated review로 보낸 것과 승인자가 악성 변경을 이해하고 거부한 것은 다른 사건이다.
- **접근과 정보 흐름:** PDP에서 권한을 제한하는 것과 부모·자식 사이의 정보 전달을 봉쇄하는 것은 다른 보장이다.
- **유한 실험과 운영 규모:** 구성된 요청·초안·큐 도착률을 실제 배포의 빈도와 지연으로 바꾸려면 추가 측정이 필요하다.

위 항목들은 앞 절에서 근거를 붙인 저자 보고의 경계를 정리한 것이다. 원시 trial record, 구현 코드, 배포 환경을 새로 검사한 판단은 아니다.

## 기존 Wiki와의 연결

**AI 해석 — 재사용할 점검 단위는 정책 파일 하나가 아니라 그 정책이 참조하는 권한 상태다.** 게시 승인이 정책 본문만 확인하고 분류·어휘의 변경은 일반 데이터 수정으로 취급한다면 같은 정책 문자열 아래에서도 보호 범위가 달라질 수 있다. 이를 새로운 보편적 방어 정리로 주장하기보다, 승인 대상과 변경 영향 범위를 묻는 운영 질문으로 재사용하는 것이 적절하다. **C27** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30614v1/source.pdf#page=18]

- [[concepts/agent-authority-and-effect-boundaries]]: 초안 작성 능력, 게시 자격 증명, 검토 경로, 실제 게시 효과를 나누어 읽는 개념적 연결이다. 승인 또는 표시 상태만으로 뒤의 효과를 가정하지 않는 관점을 공유한다.
- [[concepts/provenance-and-audit-evidence]]: 규범적 duty가 협정에서 왔다는 계보와, 구체적인 분류가 승인·구현되었는지 및 실제 집행이 완전한지는 다른 질문이라는 연결이다.
- [[concepts/security-evaluation-units]]: 초안 수, 요청 판정 reversal, context 노출, 최종 출력 누출, 큐 시뮬레이션, 호출 지연을 서로 다른 단위로 유지하는 데 직접 관련된다.

이 연결은 제공된 기존 Wiki 초안을 보조적인 편집 증거로 사용한 것이다. 그 페이지들이 요약한 원논문을 이번에 새로 읽거나 독립 검증한 것이 아니며, 논문 간 수치를 하나의 성능 순위로 비교하지 않는다.

## 열린 질문과 미확인 항목

다음은 결과가 아니라 후속 연구·검토 질문이다.

- 실제 승인자는 단순 레이블 수정처럼 보이는 재분류 공격을 얼마나 잘 구별하는가? 검토 시간과 피로를 함께 측정할 수 있는가?
- 실제 무역 문서에서 이름 있는 필드 밖의 민감 정보가 차지하는 비중은 얼마이며, 유도 가능한 정보에는 어떤 채점기가 필요한가?
- registry와 협정·필드 매핑이 바뀔 때 관련 협정의 재검토 및 집행 갱신을 어떻게 원자적으로 연결할 것인가?
- 정당한 권한 확대와 최초 게시가 포함된 현실적인 초안 분포에서는 검토량과 중앙 검토 비중이 어떻게 달라지는가?
- 재위임 ceiling이 정당한 작업을 막는 정도와 허용 행동 합성의 위험을 같은 도메인 과제로 평가할 수 있는가?
- 캐시·철회 조회·장애 시 동작을 실제 운영 요구에 맞출 때 어떤 비용과 철회 창을 받아들일 것인가?

## 원문 근거와 미검토 범위

주장별 근거는 위의 물리적 페이지 인용과 JSON의 짧은 원문 인용에 연결되어 있다. Appendix A의 텍스트를 읽은 것은 코드나 패치를 검증한 것이 아니고, References를 읽은 것은 인용 문헌의 원문을 읽은 것이 아니다. 페이지별 문자 수를 새로 계측하지 않았으며 전체 PDF 텍스트나 추출 표를 이 노트에 복제하지 않았다.

- 모든 그림·이미지 및 이미지 전용 내용: 미검토
- 수식·레이아웃·표 구조: 텍스트 추출 모호성, 시각 검증 미수행
- Figure 1–3의 추출된 캡션·레이블은 읽었지만 도형, 연결선, 배치를 보았다고 주장하지 않는다.
- 형식기호와 표의 행·열 관계는 텍스트 및 주변 설명으로 확인 가능한 부분만 사용했고 원 PDF 레이아웃은 대조하지 않았다.
- 스캔·이미지 전용 내용을 처리하거나 OCR을 수행하지 않았다.
- 제공된 텍스트 페이지와 Appendix A, References에 미독 범위는 없지만, 외부 문헌·실험 자료·이미지·코드 실행은 확인 범위 밖이다.