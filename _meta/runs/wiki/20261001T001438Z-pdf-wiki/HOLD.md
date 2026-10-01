# PDF Wiki 적용 — 보호 편집 승인 대기

## 현재 상태

PDF 텍스트 정책·수동 컴파일·검증 후 게시와 편집 중지 승인은 `scope-approval.json`에 기록되어 있다. 별도 `AGENTS.md` 보호 편집 확인창이 하위 작업과 부모 재확인에서 시간초과되었다. 정책을 우회하거나 동일 편집을 다른 도구/경로로 적용하지 않는다. 전체 작업 완료가 아니다.

- `.venv-pdf-reader`에 표준 pypdf 6.19.0 설치 완료. 환경 경로만 `.gitignore`에 추가했다. 기존 전처리 환경 복원 아님.
- 지정 codex-lb / gpt-6-astra / xhigh 경로 확인: `model-route.json`. 실제 모델 요청은 미수행.
- 정책 staging 13/14개: `policy-staging/`. 누락은 AGENTS.md. 부모가 직접 재실행한 정책 시험 132개 통과, 실패/오류/skip 0: `parent-policy-tests.json`.
- 수동 PDF-text adapter: `runtime/manual_pdf.py`. 부모 재실행에서 합성 시험 107개 통과, 실패/오류/skip 0. 네트워크 연결 시도 0, 실제 원본 PDF 읽기 시도 0: `runtime/evidence/parent-verified-01/counts.json`.
- 기존 P2 helper 코드 불변, live 정책/compilation 상태/지식/raw/Cron에는 이번 변경을 게시하지 않았다.
- 두 대상 2609.30614v1, 2609.30824v1의 본문 읽기·전송·모델 생성·의미 검토·Wiki 게시 미수행. 지식 컴파일 성공으로 표시하지 않는다.

## 재개 순서

1. 사용자에게 AGENTS.md 보호 편집의 새 명시적 승인을 받고 정상 보호 편집 도구 절차를 따른다. 승인 시간초과를 우회하지 않는다.
2. live/현재 before hash를 다시 비교하고 나머지 staging 정책 전체를 검토한다. 새 collection.lock/변경 journal 아래 AGENTS 포함 정합한 v3 정책을 반영하고 회귀 검증한다. index는 운영 링크만 최신 내용에 병합, log는 실제 변경만 append한다.
3. runtime/HANDOFF.md의 정확한 계약을 읽고 실행 승인 snapshot을 작성한다. instructions_path는 run 안의 .md 경로가 필요하다. 기존 instructions.txt를 그대로 승인에 참조하면 안 되므로 동일 내용을 새 .md로 작성한 뒤 hash를 고정한다. adapter가 요구하는 VISUAL_UNREAD 문자열과 실제 instructions의 출력 요구도 일치시킨다. .txt 원본은 보존한다.
4. 승인된 두 PDF 항목만 정확한 모델·자료·문서·무결성·동시성 gate 확인 후 queued로 전이한다. 새 실행 승인 및 기존 scope 승인·정책·프롬프트·원천/메타데이터·소비 Wiki hash를 묶는다. Cron 활성화 승인은 아님.
5. 각 PDF를 명시적으로 compile attempt1 → verify한다. 미완료/오류/unknown을 성공으로 바꾸지 않는다. 자동 재시도·fallback 없음, 각 항목 최대2회. 표준 pypdf 내장 텍스트를 메모리에서만 처리하며 PDF 바이너리·이미지·OCR·영구 추출본 금지.
6. 원문 페이지별 실제 의미 대조 후 collection.lock·journal·최종 hash·receipt·state 계약으로 Wiki 노트와 관련 연결을 게시한다. 검증은 대상 상태가 queued인 동안 수행한다. 기존 사용자 수정/reviewed 보호, 로그 append-only, 원본/source.json/수집 state/Cron 불변을 최종 확인한다.

단위/계약 시험 통과는 실제 PDF 추출 품질·모델 완료·의미 검토·게시·P3 일일 자동화의 성공 근거가 아니다. no_cost_cap와 미관측 비용 null을 유지한다. 다른 정책/스키마 revision으로 바뀌거나 편집 중지 범위가 달라졌다면 재개 전에 다시 확인한다.
