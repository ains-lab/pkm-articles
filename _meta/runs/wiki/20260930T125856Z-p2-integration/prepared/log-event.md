
## [2026-09-30] update | P2 두 논문 통합 — 개념 3개·비교 1개 및 노트 연결

<!-- publication-event:p2i-d3b8cf0db1b918060510445ffe3b227a -->
- 사용자 “진행해주세요” 확인에 따라 두 승인 HTML과 기존 Wiki 노트만 사용했다. 실제 codex-lb/gpt-6-astra/xhigh 비스트리밍 생성 1회 completed; fallback·모델 재시도 없음. 호출 전 로컬 반환형 오류는 별도 보존했다.
- 신규: `concepts/agent-authority-and-effect-boundaries.md`, `concepts/provenance-and-audit-evidence.md`, `concepts/security-evaluation-units.md`, `comparisons/agate-vs-sdc-mcp-gateway.md`.
- 갱신: `entities/arxiv-2609.30830v1.md`, `entities/arxiv-2609.31358v1.md` (revision 2; 학술 주장 보존, 연결 추가, 원문 인용 경로·게시 상태 안내 정리), `index.md`, `_meta/state/compilation.json`.
- 신규 주장 36개를 원문 문맥과 대조하고 인용 근거 73건, 로컬 Markdown 링크 222건을 사전 검사했다. 지식 페이지 총 6개, 모두 draft/unreviewed. 선택 절 통합이며 새 전문 완독·인간 검토·도표 시각 검토·실험 재현이 아니다.
- collection.lock과 write-ahead journal 아래 지식/index/log/receipt/state 순서로 게시한다. 소비 가능 여부는 거래 committed와 최종 검증 기록을 확인한다. 원문 15편과 보호 74개 파일은 사전 검증에서 불변이며 raw/source.json·수집 state·Cron·전역 설정은 쓰지 않는다.
- 기록: `_meta/runs/wiki/20260930T125856Z-p2-integration/report.md`; 생성/구조/의미 대조 및 dependency-impact, 두 source별 receipt와 integration-publish-journal은 같은 run에 있다. 비용 미관측은 null, 비용 상한·fallback 없음; 자동화 enabled=false와 P3–P6 별도 승인 경계를 유지한다.
