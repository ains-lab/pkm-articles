# HTML 우선·PDF fallback 정책 적용 및 최종 대조

- 전환 ID: `20260929T034401Z-pdf-fallback-policy`
- 최종 검증: `2026-09-29T04:03:28.239721+00:00`
- 결과: 정책·상태·Cron·운영 설명서 반영과 로컬 일관성 검증 완료. 새 논문 수집 실행은 미수행.

## 실제 원본과 목록

| 구분 | 편수 |
| --- | ---: |
| 전체 대상 버전 ID | 10 |
| HTML 원본 저장 | 8 |
| PDF 원본 저장 | 0 |
| 전문 미확보·PDF 수집 대기 | 2 |

PDF 대기 ID는 `2609.30614v1`, `2609.30824v1`이다. 아직 로컬 전문이 없으며 대기 등록을 확보 성공으로 표시하지 않는다. 전체 ID·제목·원천 색인·state·실제 파일이 일치한다. 기존 원본/서지 16개 파일의 SHA-256은 변경 전과 동일하다.

## 적용 범위

- 승인된 정책: `arxiv-html-preferred-pdf-fallback/v1`. HTML을 우선하고 공식 HTML 미제공 근거가 있을 때만 동일 버전 공식 PDF 원본을 무변경 저장한다.
- HTML 403/429/5xx/timeout 등은 fallback 사유가 아니다. PDF 저장은 전송·버전·형식 표식·길이·해시 보존 검사에 한정한다.
- 기존 원본과 source.json, 검색식·한도·checkpoint·일일 시도·마지막 수집 기록·기존 미제공 확인 시각은 보존했다. state 변경은 pipeline_id/pending/html_unavailable의 대기 표식/policy_update에 한정했다.
- AGENTS, SCHEMA, README, COLLECTION, COMPILATION, topics/state, 루트·주제 색인, 운영 설명서 2개와 append-only log를 맞췄다. 정확한 문서 목록·해시는 final-verification.json에 있다.

## Cron 등록 재조회

- ID: `4cff5b4f10ec`
- 상태: `enabled=true`, `state=scheduled`
- 저장한 프롬프트와 실제 등록 프롬프트: 전체 일치
- 예약: UTC `0 15 * * *`, 매일 KST 00:00
- 다음 예정: `2026-09-30T00:00:00+09:00`
- 모델 `codex-lb/gpt-6-astra`, reasoning `xhigh`, skills `[arxiv]`, local 전달을 유지했다. 다른 Cron 설정은 변경하지 않았다.
- 다음 예정과 활성 등록은 새 정책의 수집 성공 증거가 아니다. 자기 정책 변경 잠금은 해제했다.

## 검증 결과

- 기존 log의 앞 42063바이트 SHA-256 유지: append-only 확인.
- 활성 문서 9개, 로컬 링크 98개 확인.
- Bash 예시 4개 `bash -n` 통과. 예시 생성·실행 명령은 실행하지 않음.
- 전체 `git diff --check` 통과.
- 지식 페이지 0개. 커밋·push 없음.

## 미수행·남은 확인

이번 정책 변경에서는 arXiv 재조회·신규 HTML/PDF 다운로드·원문 분석·도표 검토·PDF 추출/렌더/OCR·별도 전처리 모델·Wiki 컴파일을 하지 않았다. 삭제된 PDF·파서·백업을 복원하지 않았다. 실제 PDF 저장과 새 정책 전체 실행은 다음 수집의 원본 파일·state·run 보고서로 별도 확인해야 한다.

## 근거

- [변경 전 스냅샷](preflight.json)
- [전환 후 상태](state-after.json)
- [등록할 프롬프트](cron-prompt.txt)
- [핵심 검증](core-verification.json)
- [재개 후 실제 등록값](cron-after-resume.json)
- [최종 전수 대조](final-verification.json)
