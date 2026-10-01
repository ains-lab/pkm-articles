# 원문 부분 대조 — 초안 검토에서 유지할 조건

이 문서는 완료된 논문 요약이나 게시된 지식 페이지가 아니다. 상위 Hermes 세션이 로컬 원본 HTML의 아래 범위를 직접 읽고 남긴 검토 주의사항이다. 생성 API가 원문 전체를 입력받았다는 사실과 본문 전체 읽기·의미 검토 완료를 구분한다. 그림·이미지·외부 자산·PDF는 열지 않았고 실험을 재현하지 않았다.

## 2609.30830v1

- 원본: `raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html`
- SHA-256: `89d515e6c33de5717ff141a6d9726830a01798e6dfead198c9f0525f0261d074`
- 이 부분 검토의 실제 범위: 원문 행 1853–2027, §6.4·§6.5·§7.1 및 §7.2 일부. 별도로 절 제목/원래 ID 목록을 확인했으나 제목 목록 확인은 해당 절 본문 독서가 아니다.
- §6.4 `S6.SS4.p1.1`: “The 6/11 count is a scenario incidence of denials, not a measured task-failure rate.” 이 비율을 정상 과제 실패율로 쓰지 않는다.
- §6.5 `S6.SS5.p1.1`: 재생 digest 일치는 보존된 증거의 scenario-level 대조다. 독립 실행 전부의 별도 검증으로 부풀리지 않는다.
- §6.5 `S6.SS5.p2.1`: “These counts measure reconstruction coverage, not attack-detection recall.” 관측 이벤트 복원 범위를 공격 탐지 재현율로 바꾸지 않는다.
- §6.5 `S6.SS5.p3.1`: offline replay throughput은 online guard latency 또는 end-to-end task overhead의 측정값이 아니다.
- §7.1 `S7.SS1.p1.1`: “Consumption before dispatch does not confirm completion or provide transactional exactly-once effects.” 권한/효과 ledger를 외부 효과의 완료 확인이나 exactly-once 트랜잭션으로 해석하지 않는다.
- §7.1 `S7.SS1.p4.1`: DSH enforce와 OC flag-only는 플랫폼과 모드가 혼재된 비교다. provenance의 독립 기여나 모집단 공격률을 확정하는 실험으로 소개하지 않는다.
- §7.1 `S7.SS1.p5.1`: “Replay equality establishes consistency of retained evidence.” adapter 진실성·complete mediation·외부 효과 확인은 별도 문제다.

## 2609.31358v1

- 원본: `raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html`
- SHA-256: `cfee938c27d5b30fb053d251d2bd1b1a6ac259b775582fe05558a370ddac566e`
- 이 부분 검토의 실제 범위: 원문 행 1260–1494, §6.2–§6.6·§7 및 §8 제목. §8 결론 본문은 이 읽기에서 아직 읽지 않았다. 표는 HTML 텍스트만 보았고 시각적 검토는 하지 않았다.
- §6.2 `S6.SS2.p3.1`: 승인 기록도 non-executing이다. authorization 사례 성공을 장치 동작 성공으로 부르지 않는다.
- §6.3 `S6.SS3.p1.1`: enriched-resource 조건의 414/420, 98.6%는 저자 보고다. 원문의 “observed absences in this suite, not upper bounds on real-world error rates”를 유지한다.
- §6.3 `S6.SS3.p2.1`·`S6.SS3.p3.1`: 서술과 구조화 플래그의 불일치로 남긴 실패가 있다. 특히 주입 지시 flag 실패를 실제 주입 지시 실행 관측으로 바꾸지 않는다.
- §6.4 `S6.SS4.p1.1`: generic MCP 대비 enriched MCP의 개선은 해당 평가의 canonical metric identifier 출력 계약 준수다. “not demonstrated improvement in clinical alarm recognition”이며 반복 사례들을 독립적인 일반화 증거로 세지 않는다.
- §6.4 `S6.SS4.p2.1`: raw/generic 비교에는 addressing catalogue 제공 여부가 함께 달라진다. 전체 차이를 semantics 단독 효과로 귀속하지 않는다.
- §6.6 `S6.SS6.p1.1`: hash chain은 외부 anchor 없이 tail truncation을 탐지하지 못한다.
- §7 `S7.p1.1`·`S7.p4.1`·`S7.p6.1`·`S7.p7.1`: clinical safety, 임상적 추론 타당성, 다중 공급사 실제 장치 검증, closed-loop control을 입증하지 않았다. “an experimental integration pattern, not a deployable controller”라는 범위를 유지한다.

## 검토 상태

위 항목은 원문 조건을 보존하기 위한 부분 대조이며, 아직 나오지 않은 생성 결과에 합격 판정을 내린 것이 아니다. 두 논문의 방법·평가·결론 전체를 읽고 핵심 주장을 대조하기 전에는 P2 논문 처리 완료로 세지 않는다. 서로 다른 평가 체계의 수치를 직접 우열 비교하지 않는다. 별도 신규성 검색·독립 재현·인간 검토는 미수행이다.
