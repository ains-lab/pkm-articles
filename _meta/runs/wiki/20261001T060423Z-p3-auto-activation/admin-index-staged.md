# 논문 지식 색인

> Last updated: 2026-10-01 | Total pages: 8

아래 목록은 해석·검토·질의로 작성한 지식 페이지를 위한 것이며, HTML/PDF 원본 수집과 구분한다. 별도 컴파일 Cron `4839be6a1db1`을 **활성화**했으며, 매일 KST 02:00–02:45에 정상 수집 원본 중 미완료 항목을 오래된 순으로 최대 5편 처리한다. 신규 노트는 기계·별도 모델 검증 통과 시 `compiled/auto_verified`로 자동 게시하며 사용자 검토를 필수 조건으로 두지 않는다. 기존 draft 노트는 과거 상태를 보존한다. 등록 확인 기준 첫 예약은 **2026-10-02 02:00 KST**, 실제 발화는 아직 미관측이다. 현재 20편 중 4편의 논문별 노트가 있고 16편이 실행 gate 대기 중이며, 전체 Wiki lint는 자동화하지 않았다. 미작성 논문 요약이나 개념 페이지를 있는 것으로 표시하지 않는다.

## Entities — 논문별 요약·분석 / 모델·도구

- [[entities/arxiv-2609.30830v1]] — AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents — 공통 개념·비교 연결 (draft/unreviewed, r2)
- [[entities/arxiv-2609.31358v1]] — A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents — 공통 개념·비교 연결 (draft/unreviewed, r2)

- [[entities/arxiv-2609.30614v1]] — Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces (draft/unreviewed, PDF text)

- [[entities/arxiv-2609.30824v1]] — Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal (draft/unreviewed, PDF text)

## Concepts — 개념·주제

- [[concepts/agent-authority-and-effect-boundaries]] — 에이전트의 승인 기록을 해석하려면 요청을 허용하는 권한, 집행 가능한 경계, 실제 실행과 외부 효과를 분리하고 비실행 제안 승인을 호출 권한으로 오인하지 않아야 한다. (draft/unreviewed, r1)
- [[concepts/provenance-and-audit-evidence]] — 출처·매핑·판정 이력·재생 일치·해시 체인은 서로 다른 질문에 답하는 증거이며, 어느 하나도 데이터 진실성이나 완전 관측을 자동으로 확립하지 않는다. (draft/unreviewed, r1)
- [[concepts/security-evaluation-units]] — 보안 수치는 시나리오·실행·이벤트·요청·구조화 응답 중 무엇을 세었는지와 관측 종점을 보존해야 하며, 반복 검사나 기록 일치를 일반적 방어율로 바꾸어 읽어서는 안 된다. (draft/unreviewed, r1)

## Comparisons — 논문·방법 비교

- [[comparisons/agate-vs-sdc-mcp-gateway]] — AGATE는 계측된 실행 요청의 권한·데이터 흐름을 조건부로 중재하고 Gateway는 장치 실행 권한을 제외한 인터페이스를 제공하므로, 둘은 공통 보안 순위가 아니라 서로 다른 효과 계약과 증거 범위로 비교해야 한다. (draft/unreviewed, r1)

## Queries — 질문과 답변

아직 작성된 페이지가 없다.

## Raw Sources — 원천 자료

발견·기존 승인 대상을 포함한 **전체 68개 버전 ID** 중 **20편 원문 확보**: **arXiv HTML 원본 18편**, **PDF 원본 2편**이다. **전문 미확보 48편은 모두 일일 한도 대기**이며 저장 완료로 세지 않는다. KST 2026-10-01 정기 수집에서 오래된 pending 5편의 동일 버전 HTML을 저장·검증·게시했다(신규 PDF 0편, 새 HTML 미제공 0편, 전송·무결성 실패 0건). 기존 원본 15편은 재검증했고 HTML 미제공 이력이 있는 PDF 2편도 원문 확보에 포함한다. [정기 실행 근거](_meta/runs/4cff5b4f10ec/20260930T150351Z-62d474aa/report.json) · [전체 ID·파일·해시 대조](_meta/runs/4cff5b4f10ec/20260930T150351Z-62d474aa/inventory-verification.json). 원천과 운영 문서는 Total pages에 포함하지 않는다.

정책 변경 전 로컬 대조 **2026-09-29 11:51 KST**에서 전체 10개 ID와 당시 저장된 HTML 8편을 확인했다. [이전 검증 근거](_meta/runs/4cff5b4f10ec/20260929T025147Z-index-sync/inventory-verification.json). 정책 변경으로 등록한 PDF pending 2편은 이번 수동 수집에서 완료했고 KST 2026-09-29 일일 시도에 2개 ID를 기록했다. 새 검색 없이 대기만 처리했으므로 first_window_floor·discovered_through는 유지했다. HTML 미제공의 원래 확인·재확인 시각은 역사적 근거로 보존하며 PDF 완료 버전의 HTML을 자동 재확인하거나 형식을 교체하지 않는다.

최근 정기 검색 기준 `2026-09-30T15:05:07.821597+00:00`(KST 2026-10-01): 승인된 검색식을 그대로 조회한 100개 레코드 중 actual updated 창에 48편이 포함되었다. 이 중 신규 후보 23편, 기존 pending 재발견 21편, 보관 원본 중복 4편이다. 완전한 검색과 pending 내구 저장 후 discovery checkpoint를 위 시각으로 전진했다. KST 일일 5개 ID를 다운로드 전에 예약했고, 남은 pending 48편의 다음 시도 가능 시각은 `2026-10-01T15:00:00+00:00`(KST 10월 2일 00:00)이다. 이 Cron에서는 본문 분석·도표 검토·PDF 추출·OCR·Wiki 컴파일을 하지 않았다. 기존 지식 페이지 6개는 변경하지 않았다.

- [AI Agent Security — Cron 4cff5b4f10ec](raw/articles/4cff5b4f10ec/index.md) — 매일 KST 00:00, HTML 우선·공식 미제공 시 PDF 원본 수집 전용.

- [논문 원천](raw/papers/)
- [주제별 정기 논문 원천](raw/articles/)
- [강연·세미나 원천](raw/transcripts/)
- [기타 자산 위치 — 현재 비어 있음](raw/assets/)

## 운영 안내

- [외부 웹 서비스 기술문서 — Wiki × Hermes API Gateway](docs/techblog/hermes-api-gateway-workdir-assoc/README.md) — 아키텍처·작업 경로·워크플로·기술 스택·API·보안·구현 로드맵; 구현 전 설계, 설정 유지.
- [전체 아키텍처·워크플로 — Archify](docs/techblog/hermes-api-gateway-workdir-assoc/ARCHIFY.md) — 문서 기반 독립 HTML 8개·해설·근거/검증 기록; 데스크톱 권장, 서비스 구현·운영 실행 아님.
- [논문 수집 자동화 — 쉬운 안내](docs/lectures/5w/paper-collection.md)
- [논문 수집 Cron — 생성 방법과 현재 구성](docs/lectures/5w/paper-collection-cron.md)
- [6주차 — Agent Reach SNS Second Brain](docs/lectures/6w/README.md) — X·Reddit·YouTube 원천 보관·승인 컴파일·운영 설계; Discord 제외, 기준 Cron 원설정 확인 필요, 실행하지 않음.
- [시작 안내](README.md)
- [스키마](SCHEMA.md)
- [원본 HTML·승인된 PDF 텍스트 컴파일 전략](_meta/COMPILATION.md)
- [후속 지식화 운영 계약 — P3 자동 검증 완료 게시·일일 컴파일 활성·비용 상한 없음](_meta/AUTOMATION.md)
- [P3 자동 컴파일 활성화 보고서·검증 근거](_meta/runs/wiki/20261001T060423Z-p3-auto-activation/report.md) — 원본 보존·기존 4편/미완료 16편, 등록 성공과 실제 예약 발화는 구분한다.
- [이전 P3 첫 운영 승인·paused Cron 등록·실행 gate](_meta/runs/wiki/20261001T053212Z-p3-first-operation/preflight.json) — 과거 준비 근거; 첫 배치의 검토 거부 4편·unknown 1편은 성공으로 세지 않고 별도 승인에 따라 재대기했다.
- [이전 P3 준비·검증 이력 — 당시 승인 대기 목록](_meta/P3-PREPARATION.md)
- [승인 모델·전송·예산과 실행 게이트](_meta/automation.json)
- [후속 상태·게시 계약](_meta/STATE-CONTRACTS.md)
- [질의 피드백·철회 계약](_meta/QUERY-FEEDBACK.md), [격주 연구 리뷰 계약](_meta/RESEARCH-REVIEW.md), [개인 연구 프로필](_meta/RESEARCH-PROFILE.md)
- [Hermes 작업 안내](AGENTS.md)
- [작업 이력](log.md)

지식 페이지를 만들거나 갱신할 때 해당 유형 아래에 `[[디렉터리/파일명]] — 한 줄 설명`을 추가하고 페이지 수·날짜를 갱신한다. 원천만 수집한 작업을 지식 정리 완료로 세지 않는다.
