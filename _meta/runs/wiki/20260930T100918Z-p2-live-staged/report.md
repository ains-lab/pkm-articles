# P2 실제 컴파일·검증 결과 — 게시 보류

## 결과

승인된 HTML 두 편을 `codex-lb / gpt-6-astra / xhigh`로 순차 비스트리밍 호출했다. 둘 다 최초 시도에서 `response_status=completed`, 실제 응답 모델 일치, 불완전 응답·오류 없음으로 완료했다. fallback·재시도는 없었다.

| 버전 | 구조·인용 검사 | 에이전트 의미 검토 | 현재 상태 |
|---|---:|---:|---|
| 2609.30830v1 | 32개 통과 | 14개 근거 대조 | 미게시 초안 |
| 2609.31358v1 | 32개 통과 | 14개 근거 대조 | 미게시 초안 |

- 생성 2/2편, 구조 검사 총 64개 통과, 핵심 주장 총 28개를 원문 문맥·조건·수치·인용과 대조했다.
- 두 Markdown 본문 전체를 검토했고 원본 생성 본문을 수정하지 않았다. read_scope의 실제 HTML 앵커, 짧은 인용의 같은 앵커 내 일치, 출처/결과/검토/초안 hash 결합을 검사했다.
- 저자 보고와 분석자 해석, 설계와 평가된 구현, 호출/이벤트/시나리오/외부 효과를 구분한다. 논문 결과의 독립적 사실성 입증은 아니다.
- 초안은 `draft / unreviewed / last_reviewed=null`이다. 에이전트 근거 대조를 사람의 검토로 승격하지 않았다.

## 읽을 수 있는 산출물

- [AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents](../../../staging/wiki/20260930T100918Z-p2-live-staged/entities/arxiv-2609.30830v1.md) — `/home/ainsdev/wiki/pkm-articles/_meta/staging/wiki/20260930T100918Z-p2-live-staged/entities/arxiv-2609.30830v1.md`
- [A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents](../../../staging/wiki/20260930T100918Z-p2-live-staged/entities/arxiv-2609.31358v1.md) — `/home/ainsdev/wiki/pkm-articles/_meta/staging/wiki/20260930T100918Z-p2-live-staged/entities/arxiv-2609.31358v1.md`

위 파일은 `_meta/staging/wiki/`에 있는 검토용 노트다. 실제 `entities/` 게시, root index 등록, compilation 완료 상태 전이는 하지 않았다. 출처 링크는 Wiki 루트 기준 경로다.

## 범위와 승인

사용자 요청은 “다음 단계를 진행해주세요”다. 새 run에서 두 편의 P2 생성·검증을 재개했다. 추가 게시/직접 편집 중지 확인은 시간초과로 확인되지 않아 `publication_authorized=false`로 보존했다. 게시 요청·journal·receipt는 생성하지 않았다. P3–P6·신규 Cron 등록/활성화로 권한을 확대하지 않았다.

- 첫 논문 응답: SDC-to-MCP — 비실행 경계와 임상 안전성, 프로토콜 성공과 의미 매핑, 출력 식별자 준수와 알람 인식을 분리했다.
- 두 번째 응답: AGATE — 설계의 보존/디코딩과 평가된 경로, synthetic 요청 우회와 실제 외부 효과, 정상 denial incidence와 task failure rate, replay 일관성과 완전한 중재를 분리했다.
- 원본 HTML 텍스트만 입력으로 제공했다. 이미지/SVG의 시각적 배치·픽셀·PDF 내용·외부 자산·외부 문헌·동반 코드/아카이브는 검토하지 않았다. 실험 재현 없음.
- 금액·비용 절감용 토큰 상한 없이 진행했다. 관측된 두 모델 호출 사용량은 합계 200,743 tokens이며, 비용은 미관측 `null`이다. 부모 에이전트 사용량을 포함한 전체 세션 합계가 아니며 비용을 0으로 만들지 않았다.

## 보존 검증과 변경

- 원문 15편(HTML 13·PDF 2)의 version·단일 원본 파일·길이·SHA-256를 재검증했다. PDF는 바이트 길이/해시만 확인했으며 내용 파싱을 하지 않았다.
- 보호 파일 37개 불변: raw/source.json, 수집 index·topics·state와 compilation state 포함. root index와 활성 지식 페이지 0개 상태 유지.
- `_meta/AUTOMATION.md`에 남아 있던 최초 AGENTS 승인 시간초과 안내를 기존 최종 수정 근거에 맞게 바로잡은 뒤 그 문서 hash로 새 승인을 고정했다. 정책·모델·원본은 생성 중 변경되지 않았다.
- 신규 파일: 이 run의 승인/instructions/attempt 결과·검증·의미 검토·보고서, 두 staging 노트. 과거 실패/unknown 기록은 덮어쓰지 않았다.
- 작업 로그는 collection.lock 아래 기존 내용을 유지한 채 이 실제 생성·검증 사건만 append한다. 최종 readback은 `final-verification.json`에 남긴다.
- 커밋·푸시·설치·수집·전역 설정·다른 Wiki/DB/프로필 변경 없음. 기존 수집 Cron을 호출하거나 편집하지 않았다.

## 남은 단계

사용자의 게시 및 직접 편집 중지 확인 후, 별도 게시 승인 근거와 기존 immutable generation 승인 간 결합을 확인하여 공유 잠금·최종 hash·journal/receipt 절차로 게시해야 한다. 이번 결과는 **P2 생성·근거 검증 성공**이며 **실제 게시 및 P2 전체 종료**를 뜻하지 않는다. 원본 재전송/재생성은 자동으로 하지 않는다.

구조 검사·의미 검토의 상세 근거는 각 버전 디렉터리의 `attempt1-verify-report.json`, `attempt1-agent-review.json`, `attempt1-staging-validation.json`이다.
