# 승인된 논문 3편 삭제 결과

- 사용자 확정 범위: TokenCast (`2609.35760v1`), Financial Fragility (`2609.30940v1`), Planarian (`2609.35366v1`).
- 활성 원천에서 `source.html` 3개, `source.json` 3개 및 해당 디렉터리 3개를 삭제했다.
- 세 편의 게시된 위키 문서는 없었다. 기존 지식 문서 8개 및 다른 논문과 공유하는 문서는 모두 유지했다. Financial Fragility의 과거 실패 생성·검토·outcome은 감사 기록으로 보존했다.
- 현재 compilation items에서 세 편만 제거했다. 다른 17개 항목과 비용 관측·과거 거래·receipt·안전 차단 상태·last_run은 바꾸지 않았다. 수집 state는 통째로 보존했다.
- 루트와 원본 색인을 현재 보관 17편(HTML 15/PDF 2), 수집 대기 48편, 현행 관리 대상 65개로 정비했다. 기존 68개 이력 중 삭제 3편을 실패나 대기로 바꾸지 않았다. 현재 컴파일 ledger는 published_draft 4편, blocked_approval 13편이다.

## 검증

- [승인 범위·삭제/수정 파일·사전 해시](manifest.json)
- [실제 삭제 결과](deletion.json)
- [보존·ID·해시·상태 스키마 검증](verification.json): PASS. 삭제/수정 대상 외 사전 목록 1,887파일 불변, 과거 log prefix 불변, 현재 원본과 ledger·색인 ID 일치, 운영 승인 snapshot 해시 유효.
- [현재 색인·지식 문서 링크 검증](navigation-verification.json): 10문서의 로컬 링크 344개, 깨진 링크 0개. 코드 예시의 가상 wikilink는 실제 링크가 아니므로 제외했다. 원본 색인 표는 끊김 없이 17행이다.
- 실제 Cron 실행·새 논문 읽기·모델 호출·위키 컴파일·자동 게시 시험은 수행하지 않았다. 따라서 이 삭제 검증을 다음 정기 실행 성공으로 표시하지 않는다.

## 복구용 백업

`/home/ainsdev/wiki-removal-backups/pkm-articles/20261001-remove-three-offtopic-papers/before.tar.gz`

삭제 전 원본 6파일과 수정 전 관리 파일 4개, 합계 10개 멤버의 SHA-256을 검증했다. 활성 Wiki 밖 신규 백업이며 이전 백업을 열거나 복원하지 않았다.

## 범위 밖

검색식·Cron·전역 설정·모델·인증·운영 프로그램·스키마·과거 승인/실행 근거는 변경하지 않았다. 향후 재수집 제외 정책은 설치하지 않았으므로 재발견 시 동일 논문이 다시 수집될 가능성이 남는다. commit/push는 하지 않았다.
