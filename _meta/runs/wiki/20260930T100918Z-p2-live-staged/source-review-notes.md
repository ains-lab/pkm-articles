# P2 원문 선행 대조 메모 — 게시용 지식 페이지 아님

- 대상은 승인된 두 HTML 버전뿐이다. 원본 identity/hash는 `approval.json`의 sources와 `staging-baseline.json`에 묶는다.
- 기존 verifier의 AnchorText로 원본 HTML 절을 메모리에서 탐색했다. 별도 추출 본문·compile-input·표/그림 파일을 저장하지 않았다.
- 이 메모는 모델 응답을 기다리는 동안 수행한 원문 읽기의 기록이다. 아직 생성 결과의 claim ID별 의미 검증을 통과시킨 것이 아니다.
- 이미지·외부 자산·PDF·실험 코드·링크된 참고문헌은 읽거나 실행하지 않았다. HTML에 있는 표 텍스트/캡션은 시각 검토와 구분한다.

## 2609.31358v1 — A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents

읽은 주 본문: S1 Introduction, S2 Background and Related Work, S3 Architecture and Implementation, S4 SDC-to-MCP Mapping(하위 절 포함), S5 Evaluation Methods(하위 절 포함), S6 Results(하위 절 포함), S7 Discussion and Limitations, S8 Conclusion. Sx1 Software and Evaluation Materials의 문구도 읽었다. 참고문헌 bib 이후 외부 자료는 검증하지 않았다.

후속 초안에서 반드시 구분할 점:

- 읽기와 dry-run만 평가했다. 승인 기록도 장치 실행 권한을 부여하지 않는다. future controlled-write 경로를 현재 구현으로 설명하면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- W(q)=0과 시험 중 상태 동일성은 외부 갱신 없는 통제된 조건의 유한 검사다. 실제 연속 측정 장치에 상태 불변을 일반화하거나 전체 구현의 형식 증명으로 부르면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S3)
- SDC-MIE는 연구용 명세다. 정상 매핑, 알려지지 않음, 지원하지 않음, 충돌을 명시하며 매핑 성공이 freshness/validity/의학적 정확성을 보장하지 않는다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S4)
- 프로토콜 성공과 의미 매핑은 다르다. Python/Python은 15/15 snapshots, 120/120 reads, 7/11 매핑이고 Java/Python은 5/5 snapshots, 40/40 reads, 0/11 매핑이다. 물리 장치·임상망 검증은 아니다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS1)
- 모델 결과 414/420은 유한 합성 task suite에서의 구조화 응답 준수다. 6개 실패는 그대로 남으며 GPT-OSS의 alarm Boolean과 GPT-4.1 mini의 injection self-report flag가 실제 응답 의미와 불일치한다. 실제 위험 동작 6건으로 바꾸면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS3)
- ablation 63/84, 75/84, 81/84는 raw/generic/enriched이다. generic→enriched의 6개 반복 개선은 2 task–scenario pairs의 canonical metric 식별자 준수이며 임상 알람 인식 향상을 입증하지 않는다. raw 조건의 URI 생성은 catalogue 부재와 얽혀 있다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S6.SS4)
- deterministic baseline 28/28을 숨기지 않는다. LLM 필요성·임상 효용·개인정보·일반적 안전성은 입증하지 않았고, audit chain의 외부 anchor 부재와 승인 identity 미인증을 유지한다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.31358v1/source.html#S7)

## 2609.30830v1 — AGATE

읽은 범위: abstract1; S1 Introduction, S2 Background and Motivation, S3 Threat Model, S4 System Design, S5 Implementation, S6 Evaluation, S7 Discussion, S8 Related Work, S9 Conclusion과 각 하위 절. bib 경계는 확인했으나 참고문헌 외부 원문은 읽지 않았다. HTML 본문에 별도 appendix 절은 발견되지 않았다.

후속 초안에서 반드시 구분할 점:

- 승인 권한과 전송 데이터 provenance는 별개의 체크다. 선언·실제 host approval이 신뢰 근거이며 문서 속 승인 주장이 아니다. A-INT는 운영자와 지시 사용자가 다른 배포를 가정한다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S3)
- exact parameter/session binding, expiry/use/amount 제한은 요청 승인 수준이다. dispatch 전 consumption과 effect ledger를 완료된 외부 효과·exactly-once 보장으로 해석하면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S4.SS2)
- 설계의 pinned tier·fair-share retention·sink decoding을 평가에서 활성화된 기능으로 합치면 안 된다. 구현 절은 동적 저장소의 insertion-order eviction, 실제 관측의 content/path 검사, decoding 미평가를 구분한다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5)
- DSH veto와 OC flag-only는 다른 플랫폼/모드이며 OpenClaw의 역사적 collection은 flag-only/fail-open이다. 모두 같은 강도 차단 또는 동등 보호라고 쓰면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S5)
- 153 chain records, 152 no-monitor runs, 252 monitored runs와 63 scenarios는 서로 다른 단위·분모다. invocation, call signature, criterion match, 실제 외부 효과를 구분한다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS1)
- 선언별 5/5/11 authorization denials는 이벤트 수이고 방지 공격 수가 아니다. mailbox parameter rewrite는 synthetic deletion tool 요청의 우회이며 실제 메일 삭제가 아니다. historical signature의 DSH 2/12에는 정상 messaging task가 포함된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS2)
- delivery 12/46과 23/52는 다른 시나리오·판정 절차의 기술 비교이지 paired wording 효과가 아니다. 선택된 성공 후보만으로 전체 공격 성공률을 계산하면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS3)
- benign 6/11은 denial 발생 시나리오 비율이지 task failure rate가 아니다. 8개 이벤트의 원인과 별도 description-field 4→0 수정을 혼합하지 않는다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS4)
- replay 63/63 per platform은 수집 근거의 일관성이다. stage hits 334/376, 328/376은 복원 coverage이며 attack detection recall이 아니다. offline replay 처리량을 온라인 gate latency로 부르면 안 된다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S6.SS5)
- rewrite/관측누락/retention/실제 defense-path 검증 부재/플랫폼 confounding을 유지한다. decomposition invariance와 provenance의 독립 증분 효과는 향후 검증 대상이다. [원문](../../../../raw/articles/4cff5b4f10ec/arxiv-2609.30830v1/source.html#S7)

## 완료 조건

모델 응답의 completed/model/status와 구조 검사를 통과한 뒤, 각 claim의 본문·조건·인용·근거 위치 및 전체 markdown의 과장/미인용 수치를 대조한다. 통과한 경우에도 agent 검토일 뿐 human reviewed가 아니며 staging에만 저장한다. publication_request·publisher·운영 ledger 갱신은 게시 승인 전 수행하지 않는다.
