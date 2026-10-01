---
title: "Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal"
summary: "이 제안은 신원에 결합된 capability token, 위임 시 권한 축소, LLM 밖의 credential wallet으로 에이전트의 행동 경계를 구성하지만, 폐기·신뢰 기반·구현 안전성에 남는 조건 때문에 실험적으로 검증된 범용 prompt injection 방어로 읽어서는 안 된다."
created: "2026-10-01"
updated: "2026-10-01"
last_reviewed: null
type: "entity"
status: "draft"
tags: ["paper"]
sources: ["raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf"]
confidence: "medium"
contested: false
contradictions: []
schema: "pkm-knowledge-page/v1"
revision: "1"
transaction_id: "pdf3-b99973e47fc40996683ae340e855c3a9"
policy_revision: "pkm-html-pdf-text-knowledge/v3"
prompt_revision: "wiki-compile/v3"
generation_ref: "_meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/2609.30824v1/attempt1-result.json"
read_scope: ["page=1", "page=2", "page=3", "page=4", "page=5", "page=6", "page=7", "page=8", "page=9"]
unread_scope: ["모든 그림·이미지 및 이미지 전용 내용: 미검토", "수식·레이아웃·표 구조: 텍스트 추출 모호성, 시각 검증 미수행", "그림 1–9의 시각적 관계·화살표·배치와 표 1–3의 원래 행·열 정렬은 확인하지 않았다. 제공된 추출 텍스트에 포함된 레이블·캡션·셀 문자열만 읽었다.", "참고문헌이 가리키는 외부 원문과 제공되지 않은 보충자료는 읽지 않았다. 제공된 페이지에는 별도 부록이 없으며, 미제공 부록의 존재나 내용을 추정하지 않는다."]
review_state: "unreviewed"
source_hashes: {"raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf": "4e58e68a3ad435c331a51ea767d057fa91c94dd5782200f6770d3b8040281fd8"}
agent_review_ref: "_meta/runs/wiki/20261001T001438Z-pdf-wiki/reviews/2609.30824v1-attempt1-agent-review.json"
---

# Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal

> 한국어 Wiki 초안 · status=draft · last_reviewed=null · review_state=unreviewed

핵심은 모델이 보안 지시를 잘 따르도록 설득하는 대신, 모델 밖의 신원·권한·credential 관리 계층에서 행동을 제한하자는 것이다. 다만 이는 설계 제안이며, 토큰에 적힌 제한이 실제 서비스와 도구에서 집행되는지는 별도 문제다.

## 읽은 버전과 범위

- 저자: Srikumar K. Subramanian, Shubhashis Sengupta. 소속: Accenture Labs.
- 버전: `2609.30824v1`.
- 원본: `raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf`.
- 제공된 물리적 `page=1`부터 `page=9`까지의 내장 텍스트를 모두 읽었다. 여기에는 마지막 두 페이지에 걸친 참고문헌과 추출된 그림 캡션·레이블·표 문자열이 포함된다. 제공된 페이지에 빈 텍스트 페이지는 없고, 별도 부록은 제시되지 않았다.
- 읽기 완료는 제공된 텍스트의 범위에 한정한다. 참고문헌을 읽었다고 해서 그 인용 대상 논문·표준·웹 문서를 읽은 것은 아니다. PDF 파일을 직접 열거나 OCR·이미지 해석을 수행하지 않았다.
- 모든 그림·이미지 및 이미지 전용 내용: 미검토
- 수식·레이아웃·표 구조: 텍스트 추출 모호성, 시각 검증 미수행

## 문제와 동기

이 논문에서 에이전트는 인간을 대신해 직접 또는 다른 에이전트를 거쳐 행동하는 프로그램이다. 여행 계획처럼 여러 서비스에 걸친 일을 맡길 때, 조정 에이전트의 전체 목표와 각 전문 에이전트가 알아야 할 정보·수행할 수 있는 행동은 같지 않다. 따라서 신원 확인뿐 아니라 제한된 권한을 전달하고 다시 좁혀 위임하는 표현이 필요하다는 문제 설정이다.

**저자 주장 — ACL과 capability의 비교:** 동일한 권한 관계라도 자원별 허용 주체를 보는 ACL 관점보다, 에이전트가 자신의 제한된 권한을 제시하는 capability 관점이 개방형·일시적 에이전트와 분산 위임에 적합하다고 논증한다. 이는 해당 사용 조건의 설계상 주장이지 ACL 대비 우월성을 측정한 결과가 아니다. **C01** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=2]

## 핵심 아이디어와 설계

### 신원, 토큰, 위임 체인을 분리해서 이해하기

- **신원도 신뢰 기반을 갖는다.** 공개 디렉터리를 통해 DID 문서와 에이전트를 연결하는 설명에서는 디렉터리에 대한 신뢰가 그 연결의 신뢰로 일부 이전된다. DID 사용을 곧 신뢰 기반이 없는 인증으로 읽지 않는다. **C02** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=2]
- **capability token은 권한을 담은 서명 구조다.** 에이전트 신원, 서명하는 grantor, 대상 자원, 접근 제약을 JSON에 담으며, grantor는 사용자 또는 상위 grant에 근거한 에이전트일 수 있다. 토큰의 진위 확인과 요청이 그 제약에 들어맞는지의 판단을 혼동하지 않아야 한다. **C03** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=3]
- **토큰을 갖고 있다는 사실과 신원 제어권은 구별된다.** 논문은 검증기의 난수에 에이전트 보안 계층이 서명하고 알려진 공개키로 검증하는 challenge–response를 제시한다. 다만 제어권 증명을 요구할 수 있다는 서술이므로 모든 서비스가 이를 의무적으로 구현했다고 단정할 수 없다. **C04** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=3]
- **위임은 권한 확대가 아니라 attenuation이어야 한다.** 하위 토큰을 상위 grant에 연결하고 서비스가 체인 전체의 권한 비확대를 검사한다. 각주는 “Determination of whether the attenuation constraint holds is domain-specific.”라고 한정한다. 서명 체인의 진위만 확인하면 지출·목적·자원 범위의 의미까지 자동으로 검증되는 것은 아니다. **C05** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=3]

### LLM 밖의 집행 계층

**조건부 저자 주장:** 개인키가 어느 LLM 컨텍스트에도 접근 가능하지 않고, 보안 모듈이 암호화·서명 결과만 반환한다면 그 컨텍스트를 통한 credential 유출을 구조적으로 불가능하게 만들 수 있다고 한다. 보장의 대상은 명시된 비밀 접근 경로이며, 에이전트가 보유한 정당한 권한을 잘못 사용하는 모든 경우까지 제거한다는 뜻은 아니다. **C06** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=3]

**도구에도 같은 전제가 필요하다.** 파일 시스템의 특정 디렉터리와 하위 디렉터리 접근을 중재하는 예를 들지만, 도구 자체가 capability-aware 시스템 기능만 사용해야 한다고 명시한다. 따라서 상위 서비스의 토큰 검사만으로 도구 내부의 모든 접근까지 제한된다고 가정해서는 안 된다. **C07** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=3]

## 여행 예시: 임시 확보와 결제 권한의 분리

Atlas는 조정 역할을 맡고 Skyway는 항공편, Haven은 호텔, Gourmand는 식당, Roadster는 현지 교통을 담당하는 설명용 구성을 사용한다. 각 전문 에이전트에 필요한 일과 권한을 나누는 것이 예시의 목적이다.

**저자 시나리오:** 사용자에게 계획을 제시하고 동의를 받은 뒤 기존 `block` 토큰을 폐기하고, 더 정확한 금액으로 실제 지출을 허용하는 토큰을 새로 발급한다. 임시 확보 권한이 결제 권한으로 저절로 바뀌는 흐름이 아니라 승인과 토큰 교체를 거치는 흐름이다. 다만 이는 설명된 절차이며 실제 예약·결제의 성공 관측이 아니다. **C08** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=4]

## 가정과 보장 경계

**위협 모델의 전제:** 사람과 에이전트가 DID 제어권을 증명할 수 있고, 폐기되지 않은 서명 체인이 서비스 수행의 충분한 권한이 되며, 토큰 수명은 짧게 유지된다고 가정한다. 핵심 서비스는 사용자가 신뢰하는 대상으로 놓는다. 이 모델을 악성 서비스 제공자까지 포괄하는 무조건적 방어로 확장할 수 없다. **C09** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=5]

**저자가 인정한 구현 의존성:** 뒤의 wallet 논의는 주입된 프롬프트로 촉발되는 사이버 공격을 일반적으로 배제할 수 없다고 명시한다. 앞의 비밀 격리 주장은 이 단서와 함께 읽어야 하며, 프로토콜의 이론적 성질이 구현 전체의 안전성이나 모든 credential 유출 경로의 차단을 증명하지는 않는다. **C10** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=5]

## Credential wallet과 선택적 공개

**구현 권고:** wallet을 별도 프로세스에서 typed IPC로만 연결하고, wallet 보유 비밀에 기반한 HMAC을 사용하며, 거부 메시지를 동일하게 유지하고, VP 비연결성에는 ECDSA 기반 proof 대신 BBS-2023을 사용하라고 권고한다. 이 목록은 보안 설계 지침이지 구현 완료 목록이나 효과 측정 결과가 아니다. **C11** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=5]

**잔여 위험과 완화책:** 표 2의 추출 텍스트는 누적 공개에 요청 제한·presentation별 승인을, VP의 LLM 컨텍스트 경유에 wallet의 verifier 직접 전송과 에이전트의 pass/fail 수신을 대응시킨다. LLM의 challenge 취득에는 out-of-band 전달을, 정책 UI 조작에는 별도의 확인 수단을 권고한다. 이는 잔여 위험을 인정한 대응안이며 표의 시각 구조나 방어 효과는 검증하지 않았다. **C12** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=6]

**암호학적 비연결성과 내용 기반 식별은 다르다.** 같은 표는 VP 서명 전에 W3C Bitstring Status List를 확인하는 방안과, 독특한 claim 조합에 의한 재식별을 별도로 다룬다. 후자는 암호학만의 문제가 아니므로 최소 필요 공개와 claim-set 다양성 분석을 요구한다. **C13** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=6]

**서비스 사이의 분리:** 호텔 단계의 캡션은 항공 세션과 다른 pairwise DID를 사용해 연결되지 않는 presentation을 만든다고 설명한다. 이는 캡션의 설계 주장으로 기록하며, 공개 속성의 조합이나 다른 관측 정보까지 포함한 전역적 비연결성의 확인으로 취급하지 않는다. **C14** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=7]

**단일 verifier의 검증 흐름:** 그림 9의 추출 문자열에는 `allowedClaims`, `allowedVerifiers`, challenge 존재 검사, BBS+ ZKP 생성, 서명 검증, `nonce₁ → consumed set`이 나타난다. 신원 presentation에서 `memberOf`, `role`을 공개하는 흐름이다. 이 문자열의 체크 표시를 실제 시험 통과로 세거나 nonce 상태 관리의 모든 경쟁 조건이 해결됐다고 읽지 않는다. **C15** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=8]

## 폐기: 즉시 중단이라는 목표와 실제 확인 경로

**기본 상충관계:** 수신자가 토큰의 모든 요소를 순수 오프라인으로 검증한다면 최신 폐기를 반영하기가 매우 어렵거나 불가능하다고 저자는 설명한다. 반대로 상태 확인을 위한 중개·네트워크 경로에는 지연이 따른다. 논문은 이를 정량적으로 측정하지 않는다. **C16** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=5]

- **짧은 수명과 갱신:** 예시로 5분 수명을 두고 갱신 실패를 통해 폐기를 인식한다. 5분은 설명용 값이지 고정 기본값이나 실험 수치가 아니다. 갱신 지연이 남으며, 이 대안만으로 즉시 폐기를 보장한다고 읽을 수 없다. **C17** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=6]
- **상위 체인 순회:** 각 토큰에 상위 참조를 넣고 서비스가 전체 grant chain의 유효성을 확인하면 하위 트리 단위 폐기를 지원할 수 있다. 대신 지연이 위임 깊이에 의존한다. 폐기 선언과 모든 서비스의 폐기 관측은 구분해야 한다. **C18** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=6]
- **Cryptographic accumulator:** 알려진 지점에 accumulator를 게시하고 capability에 witness와 epoch를 넣어, 체인 내 토큰이 제거되면 검증 실패로 반영하는 대안을 제시한다. 저자는 관리 복잡성도 언급하며, 본문은 완성된 갱신 프로토콜이나 성능 결과를 제공하지 않는다. **C19** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=6]

## 감사 이력, 실제 효과, 발견 서비스의 경계

**감사 추적의 시간 구조:** 저자는 토큰 생성·교환·폐기가 감사 가능한 흔적을 제공한다고 설명하면서, 여러 에이전트가 행동하면 단일 엄격 시간 순서 대신 요청과 VP의 순서에 따른 복수의 선형 시간 threads가 생긴다고 구분한다. 서명된 이력이 있다는 사실을 완전한 전역 순서나 모든 행동의 관측으로 확대해서는 안 된다. **C20** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=7]

**AI 해석 — 검증 이력은 결제 영수증이 아니다.** 저자는 최종 결제 실행을 결제 제공자가 구현해야 한다고 명시하고, 설명된 과정의 주목적을 결제를 유발한 의사결정의 검증 이력으로 둔다. 따라서 신원 검증, 지출 권한 확인, 호출, 결제 완료를 서로 다른 상태로 읽어야 한다. **C21** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=8]

**발견은 별도의 신뢰 문제다.** 논문은 에이전트 발견을 범위 밖에 두면서도 발견 과정에 악성 에이전트가 주입될 수 있음을 인정한다. 인증기관과 비견되는 추가 신뢰 원천을 언급하므로, 도메인 제어권이나 DID 확인을 서비스의 선의·업무 적합성까지 보장하는 것으로 읽을 수 없다. **C22** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=8]

## 제안의 검증 수준

**AI 해석:** 논문은 여행 예시의 구조와 메시지 교환, 폐기 설계 질문을 설명하는 제안이다. 제공된 전체 텍스트에서 공격 실험 표본·방어 성공률·지연 벤치마크·독립 재현·형식 검증 증거를 확인하지 못했다. 흐름도의 성공 표시와 완료 서술을 실행 관측으로 승격하지 않으며, 보편적 신규성이나 검증된 범용 방어를 주장하지 않는다. **C23** ^[raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.pdf#page=2]

## 기존 Wiki와의 연결

다음 연결은 제공된 미검토 Wiki 초안을 이용한 개념적 연결이다. 그 초안들이 다루는 다른 논문의 원문을 이번에 다시 읽거나 독립 검증한 것은 아니다.

- [[concepts/agent-authority-and-effect-boundaries]]: 임시 확보·지출 승인·서비스 검증·실제 결제 완료를 분리하는 데 유용하다. 토큰이 표현하는 권한과 실제 집행 지점이 어디인지 질문하도록 돕는다.
- [[concepts/provenance-and-audit-evidence]]: 서명된 토큰 이력, 요청 순서, 외부 완료 증거가 각각 무엇을 입증하는지 나누어 읽는 연결이다. 감사 가능성을 관측 완전성으로 바꾸지 않는다.
- [[concepts/security-evaluation-units]]: 이 논문의 설명용 시나리오를 다른 논문의 공격 실행·요청 판정·외부 효과 측정과 같은 평가 단위로 취급하지 않기 위한 연결이다. 비교 가능한 실험 분모가 확인되지 않은 상태에서 성능 순위를 만들지 않는다.

## 열린 질문과 미확인 항목

아래는 AI가 제안하는 후속 검토 질문이며, 사용자 의견이나 확인된 취약점·실험 결과가 아니다.

- 도메인별 attenuation을 어떤 규칙과 데이터 모델로 판정하는가? 시간·목적·자원 범위가 복합적으로 결합된 위임에도 같은 규칙이 적용되는가?
- 병렬 하위 위임 각각의 한도가 적절하더라도, 전체 누적 지출 한도는 누가 어떤 원자적 상태로 관리하는가?
- 폐기와 거래 실행이 경쟁하거나 상태 확인 서비스가 응답하지 않을 때, 서비스는 어떤 실패 정책을 적용하는가?
- challenge·nonce 소비, 재시도, 프로세스 재시작, 분산 verifier 사이의 상태 공유는 어떻게 정의되는가?
- capability 서명, credential proof, holder 신원, verifier domain 사이의 결합은 어떤 구현 사양으로 고정되는가?
- 비밀이 모델에 노출되지 않는 것과, 모델이 wallet에 부적절한 허용 요청을 반복하는 것은 어떻게 구분하여 시험할 것인가?
- 실제 검증에서는 권한 거부, 비밀 유출, 권한 내 오용, 폐기 전파, 정상 업무 완료를 각각 어떤 관측 종점으로 기록할 것인가?

## 원문 근거와 기록 경계

주장별 근거는 위의 물리적 `source.pdf#page=N` 표식과 구조화된 짧은 인용에 연결했다. 페이지 식별자는 인쇄 쪽수가 아니라 제공된 PDF 파일 순서다. 본문 설명은 주로 앞부분의 설계·위협 모델·흐름에서 가져왔고, 참고문헌 페이지는 인용 대상의 존재를 읽은 범위일 뿐 그 자료의 내용을 검증하는 근거로 사용하지 않았다.

- 입력이 제공한 PDF SHA-256: `4e58e68a3ad435c331a51ea767d057fa91c94dd5782200f6770d3b8040281fd8`.
- 메타데이터 경로: `raw/articles/4cff5b4f10ec/arxiv-2609.30824v1/source.json`.
- 입력이 제공한 메타데이터 SHA-256: `56af875b7311e8d9db06a9b9cb9ed3ec21cf7505fc3dc2ec19b3cf29294855eb`.

이 해시들은 제공된 식별 정보를 보존한 것이며 이 응답에서 재계산한 무결성 검사 결과가 아니다. 이 노트 작성은 원본 수정, 실험 실행, 독립 보안 검증, 사람의 reviewed 판정 또는 Wiki 게시 완료를 뜻하지 않는다.