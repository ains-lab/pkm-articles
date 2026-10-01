---
title: "AGATE와 SDC-to-MCP Gateway 비교"
summary: "AGATE는 계측된 실행 요청의 권한·데이터 흐름을 조건부로 중재하고 Gateway는 장치 실행 권한을 제외한 인터페이스를 제공하므로, 둘은 공통 보안 순위가 아니라 서로 다른 효과 계약과 증거 범위로 비교해야 한다."
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "comparison"
status: "draft"
tags: ["comparison", "agent-security", "llm-security", "provenance", "reproducibility"]
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
read_scope: ["2609.30830v1 — S1.p4", "2609.30830v1 — S3.SS1", "2609.30830v1 — S3.SS2", "2609.30830v1 — S4.SS1 — 설명 본문", "2609.30830v1 — S4.SS2 — 설명 본문", "2609.30830v1 — S4.SS3 — 설명 본문", "2609.30830v1 — S5.T2 — HTML 표 텍스트", "2609.30830v1 — S5.p5", "2609.30830v1 — S6.SS1", "2609.30830v1 — S6.SS2 — 설명 본문", "2609.30830v1 — S6.SS4", "2609.30830v1 — S6.SS5", "2609.30830v1 — S7.SS1", "2609.31358v1 — S3 — 설명 본문", "2609.31358v1 — S4.p4", "2609.31358v1 — S4.p5", "2609.31358v1 — S5.p1", "2609.31358v1 — S5.SS2", "2609.31358v1 — S5.SS3", "2609.31358v1 — S6.SS2", "2609.31358v1 — S6.SS6", "2609.31358v1 — S7"]
unread_scope: ["2609.30830v1 — 공통 플랫폼의 구성 요소 절제 실험, 전체 관측 범위 및 설계 기능의 실제 활성화는 직접 검증하지 않았다.", "2609.31358v1 — 물리 장치·임상 네트워크·연속 구독·인증된 임상 승인 및 원격 다중 사용자 MCP 배포는 이 비교의 실증 범위 밖이다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html": "89d515e6c33de5717ff141a6d9726830a01798e6dfead198c9f0525f0261d074", "raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html": "cfee938c27d5b30fb053d251d2bd1b1a6ac259b775582fe05558a370ddac566e"}
agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# AGATE와 SDC-to-MCP Gateway 비교

> 초안 · 미검토 Wiki 지식. 공통 읽기 한계: 제공 HTML의 명시된 본문 범위를 근거로 기존 두 노트를 연결했다. 이미지·PDF 읽기, 수학 검증, 코드·실험 재현, 외부 조회 및 사람의 검토는 수행하지 않았다.

**짧은 답 — AI 해석:** 두 시스템은 모델 밖의 결정론적 로직으로 경계를 정하지만, AGATE는 실행 가능한 요청을 조건부로 중재하고 Gateway는 평가된 인터페이스에서 장치 실행 권한 자체를 제외한다. 따라서 ‘어느 쪽이 더 안전한가’보다 **어떤 효과를 허용 대상으로 남겼고, 그 경계를 어디서 집행하며, 무엇을 관측했는가**가 비교의 중심이다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS1.p3] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3]

개별 문헌의 기존 설명은 [[entities/arxiv-2609.30830v1|AGATE 노트]]와 [[entities/arxiv-2609.31358v1|SDC-to-MCP Gateway 노트]]를 사용한다. 여기서는 그 본문을 대체하지 않고 [[concepts/agent-authority-and-effect-boundaries|권한과 실행 효과]], [[concepts/provenance-and-audit-evidence|출처와 감사 증거]], [[concepts/security-evaluation-units|평가 단위]]를 가로질러 비교한다.

## 비교표: 같은 단어가 같은 계약을 뜻하지 않는다

| 축 | AGATE | SDC-to-MCP Gateway |
|---|---|---|
| 위협 모델 | 외부 콘텐츠 주입 A-EXT와 작업 지시자 악용 A-INT; A-INT는 운영자와 사용자의 분리를 전제 — C02 | 잘못된 MCP 요청, prompt-like 자원 내용, 유사 제공자 식별자, 설정 변경·사후 로그 편집을 다루는 로컬 범위 — C03 |
| 신뢰 경계 | 판정기·어댑터·선언·승인/출처 상태·증거 저장소와 호스트의 중재·승인 이벤트·접근 통제 — C02 | 온전한 코드·호스트·프로세스 경계와 결정론적 gateway 로직; 모델은 그 밖에 위치 — C01·C03 |
| 승인 의미 | 호스트 발급 요청 결합 grant; 데이터 검사는 별도로 유지 — C04 | 현재 상태와 정책을 재검사한 비실행 제안 기록; 승인 신원 필드는 평가에서 미인증 — C06 |
| 집행 깊이 | DSH veto, OC 기록 전용, OpenClaw 과거 증거 수집과 동기식 veto 경로를 구분 — C05 | 쓰기 모드·소비자 계약·도구 정책에서 장치 조작 경로 제외 — C06 |
| provenance 의미 | 등록된 자료가 어느 전달 필드·목적지로 재사용되는지 판단 — C07 | 코드·핸들·단위의 의미 매핑과 사용한 스냅샷·설정·결정의 결합 — C07·C08 |
| 감사 증거 | 보존 이벤트의 그래프 재생 일치; 완전 관측과 다름 — C08 | 사용 가능한 로컬 파일의 해시 체인 검사; 외부 anchor 없는 꼬리 삭제는 별도 — C08 |
| 평가 단위 | 체인·실행·결정 이벤트·공격 기준·재구성 비교 — C09 | 요청별 조작 시도, 통제 상태, 프로토콜 읽기, 구조화 응답 채점 — C09 |
| 남은 가정·한계 | 변형·비계측 경로·설계 활성화·플랫폼/모드 교란 — C10 | 물리 장치·연속 구독·인증 신원·임상 적절성·외부 감사 기준점 — C11 |

## 1. 위협 모델과 신뢰 가정

### 저자 보고: AGATE

A-EXT는 에이전트가 읽는 콘텐츠를 통제하지만 신뢰된 호스트 기제나 운영자 설정을 직접 수정하지 않는다. A-INT는 작업을 지시하는 사용자이며 별도 운영자가 권한을 제한하는 배포를 전제한다. 개인 배포에서 둘이 같은 주체라면 이 분리가 그대로 적용되지 않는다. TCB에는 판정기뿐 아니라 dispatch interception, 실제 승인 이벤트 전달, 정책·상태 보호 접근 통제가 포함된다. **C02**

### 저자 보고: Gateway

Gateway의 로컬 위협 모델은 장치 상태 무결성, 설정 출처, 자격 증명과 감사 증거를 대상으로 하되 코드·호스트·프로세스 경계가 온전하다고 가정한다. mTLS는 시험에 설정된 TLS peer를 인증하지만 합성 승인 워크플로의 자유 입력 신원은 인증하지 않는다. EPR 문자열 일치도 제공자 인증이 아니며, 로컬 MCP 시험은 원격 사용자 인증·다중 테넌트 권한을 평가하지 않는다. **C03**

## 2. 승인의 대상과 집행 경로

**AGATE — 저자 보고:** grant는 정확한 요청 digest와 세션·만료·사용 횟수에 결합된다. 수신자나 인자 변경은 새 승인 요청이 되며, grant가 있더라도 경계 횡단 데이터 검사가 면제되지 않는다. **C04**

**AGATE — 저자 보고:** 같은 판정 결과라도 어댑터 통제 능력이 다르다. 평가된 DSH에는 디스패치 veto가 있지만 OC는 기록만 남긴다. OpenClaw의 과거 flag-only·fail-open 증거 측정을 동기식 차단의 검증으로 대체하지 않는다. **C05**

**Gateway — 저자 보고:** 제안은 장치·매개변수·정책·스냅샷에 결합되고 승인 때 정책과 상태를 재검사한다. 그 뒤에도 장치 권한은 생기지 않는다. 쓰기 모드 거부, 읽기 전용 소비자 계약과 비실행 도구 결과가 경계를 구성하며, 평가의 approved는 실제 장치 실행이나 인증된 임상 승인을 뜻하지 않는다. **C06**

## 3. provenance와 감사가 설명하는 범위

**AI 해석:** AGATE의 provenance는 주로 **관측 자료의 재사용과 경계 횡단 정책**에, Gateway의 SDC-MIE는 **상태의 의미 표현과 사용 설정의 식별**에 답한다. 이 둘을 동일한 ‘신뢰된 데이터’ 표시로 합치면 안 된다. AGATE의 내용 유사성은 의도를 입증하지 않고, Gateway의 스키마·최근 시각도 센서 정확성이나 환자 연결을 입증하지 않는다. **C07** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p6] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p5]

**AI 해석:** 재생 일치와 해시 체인은 감사 증거의 서로 다른 속성이다. AGATE는 보존된 증거의 재구성 일치를 보고하되 조용한 우회와 외부 효과 미관측을 허용하는 한계를 적는다. Gateway는 스냅샷·매핑·정책·결정을 결합한 로컬 체인의 변경 검출을 보고하되 외부 anchor 없는 tail truncation을 제외한다. 어느 검사도 그 자체로 완전한 관측과 외부 보관 신뢰를 동시에 확보하지 않는다. **C08** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p5] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1]

## 4. 명시적으로 비교 불가능한 차원

다음 항목은 **공통 성능 순위로 환산하지 않는다 — AI 해석, C09**.

- AGATE의 거부 이벤트 수와 Gateway의 구조화 응답 채점 통과 수: 판정 대상과 실패 의미가 다르다.
- AGATE의 공격 효과 기준 충족 여부와 Gateway의 no-execution 검사: 전자는 특정 요청·전달을, 후자는 장치 조작 경로 부재를 다룬다.
- AGATE의 replay 일치와 Gateway의 프로토콜 읽기·의미 매핑: 재구성 일관성과 상태 전달·표현은 다른 증거 계층이다.
- AGATE의 오프라인 재생 처리량과 Gateway의 snapshot-to-resource 지연: 측정 구간이 달라 온라인 guard 비용이나 종단 성능의 우열이 아니다.

^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p3] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.p1] ^[raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p3] ^[raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS2.p3]

## 5. 무엇이 아직 검증되지 않았는가

**AGATE — 저자 보고:** 재작성은 등록 내용 매칭을 우회할 수 있고, 메모리 쓰기 중재도 지원된 경로에 한정된다. 고정 계층·공정 보존·디코딩 설계의 평가 경로 활성화는 확립되지 않았으며 평가 결과에는 디코딩이 포함되지 않는다. DSH enforce와 OC flag-only 비교에는 플랫폼과 모드가 얽혀 있어 provenance의 독립 기여를 분리하지 못한다. **C10**

**Gateway — 저자 보고:** 물리 장치·임상 네트워크·다중 공급업체 배포는 없었다. 최신성·경보·승인은 합성 순서 상태로 검사했으며 연속 구독, 임상 타이밍, 인증된 신원과 유효한 장치 제어를 검증하지 않았다. 로컬 해시는 설정 교체를 막지 않고 감사 체인은 외부 anchor가 없다. 모델 평가 역시 동결 과제 밖의 임상 적절성·개인정보 보호·강건성을 확립하지 않는다. **C11**

## 재사용할 비교 질문

1. 허용해야 할 효과가 실제 도구 실행인가, 읽기인가, 비실행 제안인가?
2. ‘신뢰된 경계’ 목록에 실제 승인 이벤트 전달과 호스트 접근 통제가 포함되는가?
3. 모델이 잘못 답해도 실행 경로가 열리지 않는가, 아니면 별도 veto에 의존하는가?
4. `approved`의 의미를 로그 소비자와 UI가 같은 방식으로 이해하는가?
5. provenance가 추적하는 것은 자료 복사, 의미 매핑, 설정 식별, 제공자 인증 중 무엇인가?
6. 근거가 없는 외부 효과를 그래프나 상태 필드만으로 확정하고 있지 않은가?
7. 비교하려는 수치에 같은 분모·관측 종점·측정 구간이 존재하는가?

## 원문과 관련 지식

- [AGATE 공식 HTML — 2609.30830v1](https://arxiv.org/html/2609.30830v1)
- [Gateway 공식 HTML — 2609.31358v1](https://arxiv.org/html/2609.31358v1)
- [[concepts/agent-authority-and-effect-boundaries|권한과 실행 효과의 경계]]: 승인·판정·집행·외부 효과를 분리해 읽기.
- [[concepts/provenance-and-audit-evidence|데이터 출처와 감사 증거의 구분]]: 출처·진실성·재생·변경 검출의 비동치 관계.
- [[concepts/security-evaluation-units|보안 평가 단위와 주장 범위]]: 분모와 관측 종점을 보존한 수치 해석.

## 근거 표

| 주장 | 구분·조건 | 짧은 원문 인용과 연결 |
|---|---|---|
| C01 | AI 해석 · 모델 밖 AGATE 판정 | “no LLM in the judgment path” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS1.p3) |
| C01 | AI 해석 · Gateway의 모델·효과 분리 | “The LLM remains outside the trusted boundary” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3) |
| C02 | 저자 보고 · A-EXT 능력 | “It does not directly modify the trusted host mechanisms or operator configuration.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3.SS2.p1) |
| C02 | 저자 보고 · A-INT 전제 | “This case assumes an operator distinct from the user” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3.SS2.p2) |
| C02 | 저자 보고 · 호스트 의존 TCB | “Excluding the rest of the harness from the TCB does not remove these dependencies.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3.SS1.p2) |
| C03 | 저자 보고 · 로컬 위협 범위 | “assuming uncompromised code, host, and process boundary.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p6) |
| C03 | 저자 보고 · 전송 보안과 애플리케이션 권한 | “Transport security and application authority are separate.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p7) |
| C04 | 저자 보고 · 요청 결합 승인 | “Thus a changed recipient or argument creates a new approval request.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2.p2) |
| C04 | 저자 보고 · 데이터 검사 독립 | “does not exempt a boundary-crossing call from data checks” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S1.p4) |
| C05 | 저자 보고 · 어댑터별 집행 능력 | “A host may expose observations without a veto” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.T2) |
| C06 | 저자 보고 · 제안 재검사 | “changed, stale, or expired state cannot be overridden.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p5) |
| C06 | 저자 보고 · 비실행 계약 | “configuration loading rejects write-enabled modes” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3.p5) |
| C06 | 저자 보고 · 합성 승인 결과 | “an approved record remained non-executing.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2.p3) |
| C07 | AI 해석 · 관측 자료의 흐름 | “content similarity alone supplies origin evidence, not the user’s intended purpose.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS3.p6) |
| C07 | AI 해석 · 의미 매핑 문서 | “SDC-MIE is the gateway’s versioned, machine-readable semantic mapping document.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4) |
| C07 | AI 해석 · 상태 품질의 신뢰 가정 | “A correct schema and a recent timestamp cannot establish sensor correctness” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p5) |
| C08 | AI 해석 · 재생과 완전 관측 | “A silent bypass may produce neither an action record nor a coverage gap.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p5) |
| C08 | AI 해석 · 체인과 외부 기준점 | “but not tail truncation without an external anchor.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1) |
| C09 | AI 해석 · 호출과 공격 효과 | “A signature can match only the tool and recipient without testing malicious content.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1.p3) |
| C09 | AI 해석 · 서로 다른 평가 계층 | “their experimental units and acquisition paths differ” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.p1) |
| C09 | AI 해석 · 오프라인 재생 시간 | “Offline replay throughput does not measure online decision latency or end-to-end task overhead.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5.p3) |
| C09 | AI 해석 · 로컬 프로토콜 지연 | “Protocol latency is a local snapshot-to-resource measurement” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5.SS2.p3) |
| C10 | 저자 보고 · 변형·미계측 경로 | “The mailbox-deletion case provides an observed parameter-rewriting bypass.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p2) |
| C10 | 저자 보고 · 설계 활성화 한계 | “the evaluated outcomes do not include decoding.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5.p5) |
| C10 | 저자 보고 · 비교 교란 | “DSH enforce and OC flag-only confound platform with mode” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7.SS1.p4) |
| C11 | 저자 보고 · 임상 배포 범위 제외 | “no physical device, clinical network, or multi-vendor deployment was available.” — [원문](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p6) |

## 읽기·검증 범위

- 두 원본 HTML의 위 frontmatter에 기록한 선택 절을 통합한 Wiki 노트다. 새 전문 완독이나 논문 원고 작성이 아니다.
- 그림·PDF·외부 자산·외부 문헌을 검토하거나 실험을 재현하지 않았다. 사람의 내용 검토는 미완료다.
- 원문 버전·SHA-256은 원본 metadata 및 로컬 파일과 대조했다. 생성 모델의 미검토 선언과 오케스트레이터의 무결성 검사를 구분한다.
- [실제 생성 기록](../_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json) · [주장별 에이전트 근거 대조](../_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json)
