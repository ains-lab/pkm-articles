# 전체 아키텍처·워크플로 — Archify

## 앱 요청부터 프로필별 Wiki 답변까지

[프로필 라우팅 해설과 그림 2장](PROFILE-ROUTING.md) — 전체 API 왕복 시퀀스와 URL→프로필→작업 경로 매핑 workflow다. `202` 접수, 파일 읽기, SSE 진행, 최종 상태/답변을 구분한다. 실제 서비스 적용이 아닌 설계 예시다.

## 외부 앱·작업 디렉터리 연동만 먼저 보기

[연동 집중 해설과 그림 3장](INTEGRATION-ARCHIFY.md) — 앱–BFF–Hermes–Wiki 구조, 작업 경로 적용 순서, 질문·SSE·재연결 흐름을 새로 좁혀 그렸다. 아래 기존 전체 지도 8개는 그대로 보존한다. 새 결과 역시 설계 시각화이며 서비스 적용·배포가 아니다.

## 기존 전체 지도

[브라우저에서 전체 지도 열기](../../../.archify/workflow-hermes-wiki-20261001-031930/index.html) · [상세 해설](../../../.archify/workflow-hermes-wiki-20261001-031930/README.md) · [최종 검증](../../../.archify/workflow-hermes-wiki-20261001-031930/verification.json)

기존 기술문서 12개와 `verification.json`을 바탕으로 만든 문서 시각화다. 이후 추가된 이 안내는 원천 문서 집계에 포함하지 않는다. 기존 문서·슬라이드는 보존했다.

| 순서 | 주제 |
|---|---|
| 01 | [전체 시스템 구조](../../../.archify/workflow-hermes-wiki-20261001-031930/01-system/diagram.html) — TLS/BFF, 읽기, 승인 질의, 수집·게시 분리 |
| 02 | [작업 경로와 접근 격리](../../../.archify/workflow-hermes-wiki-20261001-031930/02-workspace/diagram.html) — cwd는 sandbox가 아님 |
| 03 | [모델 없는 탐색·읽기](../../../.archify/workflow-hermes-wiki-20261001-031930/03-read/diagram.html) — pageId·권한·snapshot·receipt/hash |
| 04 | [질의·스트리밍·중지](../../../.archify/workflow-hermes-wiki-20261001-031930/04-query/diagram.html) — Runs, 단일 SSE 구독, 재연결·stop |
| 05 | [HTML 우선 수집](../../../.archify/workflow-hermes-wiki-20261001-031930/05-collection/diagram.html) — 공식 미제공 때만 PDF 원본 fallback |
| 06 | [컴파일·조건부 게시](../../../.archify/workflow-hermes-wiki-20261001-031930/06-publication/diagram.html) — 별도 승인·lock·WAL·복구 |
| 07 | [데이터·화면·상태](../../../.archify/workflow-hermes-wiki-20261001-031930/07-data-ui/diagram.html) — 파일 원장·DTO·독립 여섯 상태축 |
| 08 | [구현·검증 로드맵](../../../.archify/workflow-hermes-wiki-20261001-031930/08-roadmap/diagram.html) — R0–R4와 단계별 승인·QA |

- 8개 모두 Archify showcase 9/9, 오류·경고 0, validate/deliver/strict check/browser-check 통과. 실제 HTML과 명세·검증 receipt의 SHA-256을 대조했다.
- 자동 데스크톱 검사는 1440×900·1600×1000·1920×1080·2048×1320이다. 대표 캡처 시각 검토와 1440px/375px 노드 검색·Escape 검사도 별도 기록했다.
- **데스크톱 열람 권장.** 375px에서 01·02·07의 일부 텍스트는 화면 밖에 있고 보조 글씨가 작다. 전체 모바일 가독성·접근성 PASS를 뜻하지 않는다. 모든 카드·테마·조작·내보내기의 시각 전수 검토도 아니다.
- 본문은 한국어, 01–06 Viewer UI는 영문 fallback, 07–08은 한국어다.
- BFF·화면·격리는 제안이며 실행·배포 완료가 아니다. Gateway·모델·수집·논문 읽기·Wiki 게시·Cron 변경은 이 작업에서 실행하지 않았다.

`candidate.json`이 수정 가능한 원본이며 HTML 직접 변경은 검증 provenance를 무효화한다. 08의 최종 receipt는 `08-roadmap/repair-5/`에 있다. [8개 명세/HTML 해시와 receipt 경로](../../../.archify/workflow-hermes-wiki-20261001-031930/artifact-receipts.json)를 따른다.
