
## [2026-09-30] update | P2 정책·검증·게시 결함 수정 — 비용 비차단, 합성 회귀 108개 통과

- 사용자 요청 `위 정책 정합성, 검증, 개시 결함을 수정해주세요. 그리고 위키 컴파일 과정에서 비용은 고려하지 말아주세요. 토큰이 넉넉합니다.`에 따라 policy/contracts/prompt/state revision과 비용 비차단 계약을 정합화했다. AGENTS 보호 편집 최초 승인 시간초과 후 명시적으로 재질문했고 사용자가 `보호 편집 승인을 다시 요청`을 선택하여 도구 승인 후 반영했다. 이 요청을 실제 논문 호출·게시·Cron 활성화 승인으로 확대하지 않았다.
- no_cost_cap: 금액 상한·비용 예약·계측 검증·비용 강제 차단을 실행/게시 조건에서 제외한다. 미관측은 null이고 양수 비용도 비차단이다. 단계 승인·HTML 자료 한정·codex-lb/gpt-6-astra/xhigh·fallback 금지·무결성·유한 재시도·동시성/사용자 편집 보호는 유지했다.
- 기존 생성기/비스트리밍 진입점/검증기/게시자를 수정했다. 불완전 응답·본문 미완료·잘못된 앵커 인용·경로 이탈 차단, 프롬프트 필드 정합화, mkdir 공유 잠금, 실제 색인·페이지 수, canonical work_key, WAL/receipt/schema-validated state, 조건부 중단 복구·반복 no-op을 시험했다. 생성기/게시자의 신규 승인 형식 불일치도 실제 연결 시험에서 수정했다. 과거 close-run.py의 상태/log 재적용은 retired/exit 2로 차단했다.
- 부모 최종 통합 회귀 **108 tests, failures 0, errors 0, skipped 0**. 합성 SDK 경계와 임시 파일시스템에서 생성→검증→게시→no-op, 단계별 중단/복구·충돌을 실행했다. 실제 논문 모델 호출·본문 의미 검토·지식 게시·Cron 등록/활성화는 수행하지 않았다. 지식 페이지 0개, root index 불변이며 원본 HTML 13편·PDF 2편의 버전/바이트/해시는 보존했다.
- 변경 범위: AGENTS/SCHEMA/README, _meta의 기존 운영 정책·스키마·프롬프트·feedback/research-review revision, 기존 P2 스크립트 및 합성 회귀/수정 근거. raw/source.json·수집 설정/state·compilation state 등 보호 파일 37개 불변. 기존 log prefix는 보존하고 이 사건만 공유 잠금 아래 append한다. 커밋·푸시·설치·전역 설정 변경 없음.
- 근거: `_meta/runs/wiki/20260930T090330Z-p2-repair/report.md`, `final-tests.json/.txt`, RED 기록, `final-verification.json`. 다음 실제 P2는 새 run의 재개/게시 범위 확인과 실제 논문 근거 검토가 필요하며 비용은 재개 gate가 아니다. 과거 실패·unknown 기록은 보존한다.
