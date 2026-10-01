---
title: "A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents"
summary: "A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents"
created: "2026-09-30"
updated: "2026-09-30"
last_reviewed: null
type: "entity"
status: "draft"
tags: ["paper", "llm-security", "agent-security"]
sources: ["raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html"]
confidence: "medium"
contested: false
contradictions: []
schema: "pkm-knowledge-page/v1"
revision: "2"
transaction_id: "p2i-d3b8cf0db1b918060510445ffe3b227a"
policy_revision: "pkm-html-knowledge/v2"
prompt_revision: "wiki-compile/v2"
generation_ref: "_meta/runs/wiki/20260930T100918Z-p2-live-staged/2609.31358v1/attempt1-result.json"
read_scope: ["abstract1 — Abstract", "S1 — 1 Introduction", "S2 — 2 Background and Related Work", "S3 — 3 Architecture and Implementation", "S4 — 4 SDC-to-MCP Mapping", "S4.SS1 — 4.1 Interpreting a Mapped Metric", "S4.SS2 — 4.2 Worked Example: From Monitor State to Agent Response", "S4.SS2.SSS0.Px1 — State quality is independent of mapping success.", "S5 — 5 Evaluation Methods", "S5.SS1 — 5.1 Simulated Devices and Task Context", "S5.SS2 — 5.2 Software-SDC Protocol Paths", "S5.SS3 — 5.3 No-execution, Lifecycle, and Provenance Checks", "S5.SS4 — 5.4 Agent Evaluation and Representation Ablation", "S5.SS5 — 5.5 Analysis and Reproducibility Discipline", "S6 — 6 Results", "S6.SS1 — 6.1 Resource Exposure and Protocol Interoperability", "S6.SS2 — 6.2 Boundary, Lifecycle, and Authorization Outcomes", "S6.SS3 — 6.3 Agent Interpretation and Retained Failures", "S6.SS4 — 6.4 Representation Ablation", "S6.SS5 — 6.5 Illustrative Archived Responses", "S6.SS6 — 6.6 Audit and Consolidated Evidence", "S7 — 7 Discussion and Limitations", "S8 — 8 Conclusion", "Sx1 — Software and Evaluation Materials", "bib — References: 제공된 서지 목록 텍스트만 열람"]
unread_scope: ["그림·이미지는 시각적으로 검토하지 않았다. 특히 S3.F1의 아키텍처 이미지 픽셀은 보지 않았으며, 본문 설명과 캡션만 읽었다.", "수식은 독립적으로 검증하지 않았다. S3.Ex1의 no-execution 조건과 S4.E1 및 주변 수학 표기의 정의·설명만 텍스트로 읽었다.", "실험을 재현하지 않았다. 프로토콜 통신, 경계 검사, 모델 호출, 표현 절제 비교, 감사 파일 검사를 실행하지 않았다.", "참고문헌은 외부 확인하지 않았다. bib의 서지 텍스트를 읽었지만 인용된 논문·표준·웹페이지 원문은 열람하지 않았다.", "Sx1이 가리키는 GitHub·Zenodo 소프트웨어와 평가 아카이브, 원시 모델 응답, 체크섬, 입력 잠금 파일 및 분석 스크립트는 가져오거나 검증하지 않았다.", "제공 HTML에는 별도 Appendix 또는 Supplement 섹션이 없다. S8 뒤의 Sx1은 자료 안내이며, 그 다음 bib에서 참고문헌이 시작한다. 외부 평가 자료는 본문 읽기 완료 범위에 포함하지 않았다.", "표는 S2.T1부터 S6.T11까지 제공된 HTML 표 텍스트만 읽었다. 렌더링된 표의 배치·이미지에 대한 시각 검토는 하지 않았다.", "사람에 의한 논문 검토, 임상 검토, 승인 또는 공유 게시를 수행하지 않았다."]
review_state: "unreviewed"
relation_generation_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/attempt1-result.json"
relation_prompt_revision: "wiki-integrate/v1"
relation_agent_review_ref: "_meta/runs/wiki/20260930T125856Z-p2-integration/agent-evidence-review.json"
---

# A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents

> 상태: draft/unreviewed — 로컬 Wiki에 게시된 논문 분석 노트다. 사람의 내용 검토·승인 완료를 뜻하지 않는다.
> 범위: 제공된 원본 HTML 텍스트만 읽었다. 외부 검색·자산 가져오기·코드 실행·도구 사용은 하지 않았다.
> 본문 읽기: Abstract부터 S1–S8의 서론·방법·평가·결과·논의·결론과 Sx1의 자료 안내까지 읽었으며, 누락된 본문 절은 없다.
> 문서 경계: S8 뒤의 Sx1은 Software and Evaluation Materials이고, 다음 bib에서 References가 시작한다. 별도 Appendix/Supplement 절은 없다.
> 매체 한계: 표와 listing은 HTML 텍스트만 읽었다. 이미지 시각 검토·수학 검증·실험 재현·참고문헌 외부 확인을 수행한 것은 아니다.

## 핵심 요약
- [저자 보고] 읽기 전용 자원과 비실행 제안을 통해 장치 상태를 노출하되, 장치 조작 권한은 주지 않는 게이트웨이다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 의미 보강의 관측된 이득은 경보를 더 잘 알아본 결과보다 정규 지표 식별자를 정확히 출력한 결과에 가깝다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1)
- [분석자 해석] 핵심은 모델의 올바른 판단을 신뢰하는 대신, 모델 출력이 낼 수 있는 장치 효과를 제한하는 데 있다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)

## 문제와 동기
- [저자 보고] 의료기기 상태를 에이전트가 이해하게 하면서 비결정론적 모델에 조작 권한을 넘기지 않는 것이 문제 설정이다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S1)
- [분석자 해석] 읽을 수 있는 데이터, 신뢰할 수 있는 관측, 실행할 수 있는 명령을 같은 개념으로 취급하지 않는 설계가 중요하다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)
- [분석자 해석] 잘못된 요약의 위험은 남더라도 장치 조작 경로는 열리지 않게 하는 분리가 이 노트의 관심점이다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)

## 기여
- [저자 보고] 장치·지표·경보·맥락·조작 관련 요소를 읽기 전용 자원과 dry-run 도구로 결정론적으로 투영한다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S1)
- [저자 보고] SDC-MIE는 코드·핸들·단위와 의미·정책·출처를 명시적으로 연결한다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4.1)
- [저자 보고] 자원·에이전트·결함·제안 경로를 다루는 프로토타입과 평가 프레임워크를 제시한다. C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S1)
- [저자 보고] SDC-MIE는 연구 명세이며 표준 적합성이나 TogoMCP 형식 호환성의 선언이 아니다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4.1)

## 방법·가정·위협 모델
### 실행 경계
- [저자 보고] 평가한 MCP 전송은 동일 호스트 subprocess의 stdio이며, 네트워크 공개 MCP listener는 평가하지 않았다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 쓰기 모드 설정 거부, 발견·스냅샷 읽기만 제공하는 어댑터 계약, 비실행 도구 정책으로 경계를 구성한다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 자원 읽기·제안 검증·승인 기록은 SDC Set Service 또는 ActivateOperation을 내보내지 않는다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 요청에 따른 조작 호출 부재가 핵심 속성이며, 상태 다이제스트 비교는 추가적인 통제 관측이다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 실제 공급자의 독립적인 측정값 변화는 읽기 도중에도 가능하므로, 그 자체를 게이트웨이 쓰기의 증거로 보지 않는다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 코드·설정이 온전하고 관찰 전용 어댑터를 사용하며 프로세스 경계 우회가 없다고 가정한다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] EPR 허용 목록은 정확한 문자열 제한이지 암호학적 공급자 인증이 아니며, mTLS도 승인 폼의 자유 입력 신원을 인증하지 않는다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 호스트 침해·위조 공급자·인증 실패와 원격 다중 사용자 MCP 보안은 이 경계의 보장 범위 밖이다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)

### 의미·상태·승인
- [저자 보고] 매핑 상태는 mapped·unmapped·unsupported·conflicting으로 드러나며, mapped 항목만 의미 보강된다. C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4.1)
- [저자 보고] 알려진 지표로 매핑되더라도 stale 또는 invalid 관측을 현재의 신뢰 가능한 상태로 바꾸지는 않는다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)
- [저자 보고] 허용된 제안 도구는 스키마·범위·대상·최신성·정책을 검사한다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)
- [저자 보고] 제안은 장치·조작·매개변수·정책·MDIB 버전·스냅샷 해시·제안자·만료 정보에 결합되며 승인 시 재검사된다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)
- [저자 보고] approved도 executed=false이고, 승인으로 변경·노후화·만료 상태를 무시할 수 없다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)
- [저자 보고] 스키마와 교차 항목 검사는 수동으로 붙인 임상 라벨의 의학적 정확성을 확립하지 않는다. C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)

### 평가 설계
- [저자 보고] 환자 모니터·인공호흡기는 합성 상태 예시이며 환자 기록이나 검증된 생리 모델이 아니다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] hold-out의 28개 과제–시나리오 쌍을 모델 5종이 온도 0에서 3회씩 수행했다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] 결정론적 기준선과 모델은 같은 직렬화 맥락을 받으며, 기대 정답은 채점기에만 제공된다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] 경보 과제의 지표 식별자는 정확 일치로 평가하고, 요약 과제의 명시적 Boolean은 경보 서술보다 우선한다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] GPT-4.1 mini 표현 비교는 보강 응답을 재사용했고, 비교군을 동시에 교차 실행한 실험이 아니다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] 반복은 안정성 탐색이지 독립 과제 표본의 추가가 아니며, 보고율은 유한 과제 집합의 기술 통계다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)

## 저자 보고 결과와 조건
### 프로토콜과 의미 범위
- [저자 보고] 동일 스택: 발견 15/15, 스냅샷 15/15, MCP 읽기 120/120, 지표 매핑 7/11이었다. C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1)
- [저자 보고] 독립 Java/Python 경로: 스냅샷 5/5, 읽기 40/40이지만 일반 코드 매핑은 0/11이었다. C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1)
- [저자 보고] 이는 로컬 소프트웨어 프로토콜 연결과 미지원 의미의 보수적 처리이지, 해당 코드의 임상 의미 상호운용성 입증이 아니다. C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1)

### 효과·수명주기 경계
- [저자 보고] 자원 12개와 도구 상호작용 7개 검사에서 조작 시도 0, 정규화 상태 다이제스트 불변을 보고했다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2)
- [저자 보고] 순서화 이벤트 14개, 도구 정책 7개, 승인 수명주기 7개 사례가 기대 결과와 일치했다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2)
- [저자 보고] 유한 검사이며 구현 전체의 증명이 아니다. 승인 신원은 인증되지 않았고 참여자 평가는 없었다. C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2)

### 에이전트 출력
- [저자 보고] 보강 조건에서 결정론적 기준선은 28/28, 호스팅 모델은 합계 414/420인 98.6%를 통과했다. C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p1.1)
- [저자 보고] 위험 권고·존재하지 않는 URI 생성·경계 우회는 동결 채점에서 관측되지 않았지만, 현실 오류율의 상한을 뜻하지 않는다. C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p1.1)
- [저자 보고] GPT-OSS 실패 3건은 경보가 없다는 서술과 active_alarm=true가 모순된 사례였다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3)
- [저자 보고] GPT-4.1 mini 실패 3건은 올바른 URI와 비행동적 응답을 냈지만 followed_injected_instruction=true를 선언한 사례였다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3)
- [저자 보고] 실패 6건은 제거하지 않았으며, 플래그 불일치를 주입 지시의 실제 실행으로 해석하지 않았다. C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3)

### 표현 절제 비교
- [저자 보고] GPT-4.1 mini는 원시 SDC 63/84, 일반 MCP 75/84, 보강 MCP 81/84를 통과했다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1)
- [저자 보고] 개선 6건은 과제–시나리오 쌍 2개의 3회 반복이며, 정규 지표 이름 준수에서 발생했고 악화된 대응 사례는 없었다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1)
- [저자 보고] 카탈로그 없는 원시 표현에서 URI 15개를 만들어 냈으므로, 원시 대비 차이에는 주소 카탈로그 제공 효과가 섞인다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4)
- [저자 보고] 평균 직렬화 맥락은 약 3.24 kB에서 4.71 kB로 늘었고, 저자는 45.2% 증가로 보고한다. C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4)
- [저자 보고] 일반 MCP도 활성 경보는 인식했으므로 점수 차이를 임상 경보 인식 개선으로 읽어서는 안 된다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1)

### 감사
- [저자 보고] 로컬 감사·출처 검사 7개가 통과했으며, 레코드 변조 검출 후 추가 append를 거부했다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1.1)
- [저자 보고] 외부 앵커가 없으면 체인의 꼬리 부분 삭제는 검출하지 못한다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1.1)

## 한계와 해석 경계
- [저자 보고] 실물 기기·임상 네트워크·다중 공급업체 배치가 없어 결과는 실험적 통합 패턴의 범위에 머문다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7)
- [저자 보고] 최신성·스키마만으로 센서 정확성, 시계 동기화, 환자 연결이나 임상 관련성을 확보할 수 없다. C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7)
- [저자 보고] 비실행 경계는 온전한 호스트·코드·설정에 의존하며 전체 배포 보안 평가가 아니다. C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- [저자 보고] 반복 호출·호스팅 별칭·비동시 표현 비교 때문에 기술 통계를 일반적 신뢰성 추정으로 확대하지 않는다. C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5)
- [저자 보고] 표현 보강 이득은 단일 모델의 정확한 식별자 출력 계약에 관한 제한된 관측이다. C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1)
- [분석자 해석] 벤치마크 통과, 장치 쓰기 차단, 임상 해석의 적절성은 서로 대체 가능한 안전 지표가 아니다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)

## 연구 연결 — 분석자의 해석
- 정책 집행을 모델 밖에 두는 설계를 검토할 때, 모델 거절 능력과 실행 권한 제한을 분리하는 사례로 활용할 수 있다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)
- 후속 평가에서는 효과 차단·관측 품질·구조화 응답 일관성을 별도 축으로 기록하는 편이 실패 원인을 해석하기 쉽다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)
- 결정론적 기준선의 통과 결과를 고려하면, LLM의 추가 가치는 고정 질의 정확도보다 유연한 상호작용에서 별도로 입증해야 한다는 연구 질문이 남는다. C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p1.1)
- 감사 체인은 증거 연결의 출발점으로 볼 수 있지만, 외부 신뢰 기준점과 보관 정책까지 포함하는 설계는 별도 연구 과제다. C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1.1)
- 이 연결은 제공된 논문에 대한 해석이며 외부 선행연구 대비 신규성 판단이 아니다. 다른 파일럿 논문의 내용은 합치지 않았다.

## 미검토 항목과 후속 질문
- S3.F1의 이미지 픽셀은 보지 않았고 캡션·본문 설명만 읽었다.
- S3.Ex1과 S4.E1 및 주변 수학 정의는 읽었지만 독립 증명이나 구현 대응 검증을 하지 않았다.
- 표는 HTML 표 텍스트만 읽었으며 렌더링 결과를 시각 검토하지 않았다.
- 소스 코드·외부 평가 아카이브·원시 응답·파일 해시는 가져오지 않았다.
- 실험 재현, 모델 재호출, 임상 검토, 사람의 검토·승인은 수행하지 않았다.
- References의 서지 텍스트는 읽었지만 인용 원문과 표준 문서를 외부 확인하지 않았다.
- [미해결 질문] 실제 보고 스트림의 손실·재연결·순서 역전에서도 상태 결합과 비실행 정책을 어떻게 검증할 것인가?
- [미해결 질문] 엄격한 식별자 채점과 동의어 허용 의미 채점을 병행하면 어떤 오류 유형이 각각 드러날 것인가?

## 근거 표
아래 인용은 제공 HTML의 해당 앵커 또는 하위 요소에서 가져온 짧은 원문이며, 표를 시각 검토했다는 뜻은 아니다.
| ID·근거 | 주장 요지 | 적용 조건 | 원문 앵커 | 짧은 원문 인용 |
|---|---|---|---|---|
| C01 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S1) | 조작 권한 없는 상태 노출과 매핑·평가 프레임워크 | 읽기와 비실행 제안 | S1 | “without granting non-deterministic models authority over device operation.” |
| C02 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3) | safety-bounded는 장치 효과 제한 | 온전한 코드·호스트, 로컬 stdio | S3 | “The bounded property concerns device effects, not general safety.” |
| C03 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4.p4.1) | 매핑 상태를 명시하고 mapped만 보강 | 연구 명세와 선언된 매핑 | S4.p4.1 | “only mapped tuples are enriched.” |
| C04 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4) | 상태 품질·승인과 실행 권한을 분리 | 정책·현재 상태 재검사 | S4 | “Even approved requires executed=false and grants no SDC authority.” |
| C05 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S5) | 합성 hold-out과 반복·표현 비교 | 독립 표본 아님, 비동시 비교 | S5 | “Three repetitions probe stability but are not three independent task samples” |
| C06 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1) | 프로토콜 성공과 의미 매핑 범위는 별개 | 로컬 소프트웨어 시험 | S6.SS1 | “this is successful conservative handling of unsupported semantics” |
| C07 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS2) | 조작 시도 부재와 상태 불변 관측 | 외부 업데이트 없는 유한 검사 | S6.SS2 | “The independent operation-attempt counter remained zero and normalized device-state digests were unchanged.” |
| C08 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3.p1.1) | 보강 조건 모델 414/420, 98.6% 통과 | 동결 합성 과제, 현실 오류율 아님 | S6.SS3.p1.1 | “The hosted models passed 414/420 cases (98.6%) in the enriched-resource condition” |
| C09 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3) | 구조화 필드 불일치 실패를 유지 | 플래그 기반 보수적 채점 | S6.SS3 | “All six failures remain in the reported total.” |
| C10 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4.p1.1) | 보강 이득은 정규 식별자 계약 준수 | 단일 모델, 반복된 과제 쌍 | S6.SS4.p1.1 | “The gain is therefore compliance with the explicit semantic output contract” |
| C11 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4) | 카탈로그 효과와 맥락 크기 증가 | 압축·토큰 비용 효과가 아님 | S6.SS4 | “The observed gain is not a compression effect” |
| C12 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS6.p1.1) | 로컬 변조 검출과 꼬리 삭제 한계 | 외부 앵커 없는 파일 체인 | S6.SS6.p1.1 | “but not tail truncation without an external anchor.” |
| C13 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7) | 임상 배포 가능한 제어기가 아님 | 실물·임상·워크플로 검증 부재 | S7 | “The architecture is an experimental integration pattern, not a deployable controller.” |
| C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1) | 해석: 출력 품질과 장치 효과를 별도 평가 | 본문 기반 연구 연결 해석 | S7.p3.1 | “a model error can still create a misleading summary without opening an operation channel.” |

## 잠정 결론
- [분석자 해석] 채택할 근거는 제한된 비실행 인터페이스와 분리된 평가 관점이다. 임상 추론이나 배포 안전성이 검증되었다는 결론은 보류한다. C14 [Evidence](../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7.p3.1)
- 상태는 draft/unreviewed로 유지한다. 이 산출물은 staged 분석 내용이며 공유 게시 또는 사람의 승인을 주장하지 않는다.

## 연결된 지식

- [[concepts/agent-authority-and-effect-boundaries|권한과 실행 효과의 경계]] — Gateway의 제안·승인 용어를 실제 실행 권한과 구분하는 개념 안내.
- [[concepts/provenance-and-audit-evidence|데이터 출처와 감사 증거의 구분]] — 상태 매핑, 출처 기록, 데이터 진실성과 감사 체인의 구분을 탐색.
- [[concepts/security-evaluation-units|보안 평가 단위와 주장 범위]] — 요청 검사·프로토콜 읽기·반복 모델 응답의 서로 다른 단위를 확인하기.
- [[comparisons/agate-vs-sdc-mcp-gateway|AGATE와 SDC-to-MCP Gateway 비교]] — AGATE와의 효과 계약, 신뢰 경계, 증거 범위 차이를 읽는 비교 안내.
