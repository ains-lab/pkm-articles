# P2 두 편 후속 게시 완료

- 결과: 승인된 두 기존 초안의 로컬 Wiki 게시 완료. 기존 모델 산출물을 재사용했으며 새 모델 호출·재생성·외부 게시/동기화·Cron 등록/활성화를 하지 않았다.
- 확인 시각: `2026-09-30T10:50:05.494512+00:00`. 사용자 요청 “다음 단계 진행해주세요” 및 명시적 확인 “편집 중지 확인 · 두 편 게시 승인”에 근거한다.
- 페이지는 `draft/unreviewed`, `last_reviewed=null`이다. 사용자의 게시 승인과 학술 내용에 대한 인간 검토는 구분한다.

| 논문 | Wiki 페이지 | 상태 | 게시 직전 구조 검사 | 기존 의미 검토 |
|---|---|---|---:|---:|
| AGATE — 2609.30830v1 | [열기](../../../../entities/arxiv-2609.30830v1.md) | published_draft | 32 | 14개 주장 |
| SDC-to-MCP Gateway — 2609.31358v1 | [열기](../../../../entities/arxiv-2609.31358v1.md) | published_draft | 32 | 14개 주장 |

## 실제 검증

- 실제 출력 두 파일·색인 각 1개 항목·게시 로그 각 1개 사건·committed journal·receipt·compilation 상태 및 hash 일치를 readback했다. Total pages는 실제 지식 페이지 수 2와 같다.
- 게시자가 잠금 전/후에 수행한 구조·인용 검사는 총 64개 통과했다. 기존 주장별 의미 검토 28개와 결과/source hash 결합을 다시 확인했다. 생성된 Markdown 본문은 staging/원 응답과 같으며 의미 검토를 새로 수행했다고 주장하지 않는다.
- 게시자 실경로를 두 번 더 실행해 각 `noop`을 확인했다. 입력·원문·지식·state·승인/게시 증거 등 74개 파일의 목록/해시가 전후 동일했다.
- root 기준 로컬 Wiki/source 링크·HTML 앵커 141개 확인, 끊어진 대상 없음. 표준 Markdown 렌더러의 상대경로 표시 호환성이나 시각 렌더링 검사는 아니다.
- 원문 15편(HTML 13·PDF 2)의 정확한 version·원본 파일 1개·바이트 길이·hash·source.json을 재검증했다. PDF는 바이트/해시만 확인했으며 내용 추출/파싱은 하지 않았다. source.json의 `wiki_compiled:false`는 수집 당시 이력이므로 수정하지 않았다.
- 게시로 변경 가능한 index/log/compilation state를 제외한 기존 snapshot 48개 불변, log 기존 prefix 보존, collection.lock 정상 해제.
- 수정 후 합성 회귀 114개 통과. 후속 승인 전용 6개 시험에는 17개의 잘못된 승인 subcase, 이전 승인 변조, 잠금 직전 승인 변경, 부분 게시 복구, 정확한 no-op을 포함한다. 기존 전체 회귀에서 발견한 잘못된 JSON 타입 처리 회귀는 수정했으며 실패 증거도 보존했다.
- automation/compilation/feedback/research-review 4개 계약 instance JSON Schema 통과, `git diff --check` 통과.

## 후속 승인과 변경 내역

기존 게시자는 생성과 게시를 동시에 승인한 v1 경로만 지원했다. [부속 계약](contract-addendum.md)에 따라 원 생성 승인/결과를 덮어쓰지 않는 v2 후속 게시 경로를 추가하고 검증했다. 기존 정책·문서·프롬프트 snapshot은 유지하며, 새로운 게시 승인은 원 승인과 결과/review/source/metadata/출력 경로를 함께 묶는다. journal에는 두 승인 참조가 모두 남는다.

- 지식/공유 변경: `entities/arxiv-2609.30830v1.md`, `entities/arxiv-2609.31358v1.md`, `index.md`, append-only `log.md`, `_meta/state/compilation.json`.
- 코드: `_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py`; 새 회귀 `test_publish_separate_approval.py`.
- 증거: `_meta/runs/wiki/20260930T100918Z-p2-live-staged/publication-approval.json`; 각 논문 디렉터리의 새 `attempt1-publication-request.json`, `attempt1-publish-journal.json`, `attempt1-publish-verification.json`, `attempt1-receipt.json`; 이 보고서 디렉터리의 preflight/시험/게시 CLI/no-op/검증 자료.
- 원 생성 승인·응답·review·staging은 보존했다. 과거 실패/unknown 결과도 유지하며 두 compilation 항목의 기존 failure_count=1을 지우지 않았다.
- 허용 범위의 재사용 절차는 현재 프로필의 기존 llm-wiki 스킬에 일반 규칙으로 추가했다. 별도 수집/파싱 스킬이나 프로그램을 만들지 않았다.

## 범위·남은 권한

이번 수동 게시 작업은 완료다. 사람의 내용 검토·그림 시각 검토·수학 검증·실험 재현은 완료로 주장하지 않는다.

`enabled=false`를 유지했다. P3 자동 compiler 등록/활성화, P4–P6 및 연구 리뷰는 별도 승인 전 실행하지 않는다. 기존 수집 Cron·수집 state·검색식/한도·전역 모델/인증·다른 Wiki/프로필은 변경하지 않았다. 커밋/푸시/설치 없음. 관측되지 않은 모델 비용은 원래 `null`을 그대로 유지한다.

## 증거 파일

- [publication-verification.json](publication-verification.json): 26개 게시/보존 검사, 원문 15편 명세, 출력/receipt/key.
- [noop-verification.json](noop-verification.json): 실제 no-op 응답 및 74개 파일 전후 hash.
- [regression-tests-final.json](regression-tests-final.json): 7개 시험 파일의 114개 최종 통과.
- [final-verification.json](final-verification.json): 아래 요약 로그 append 후 최종 readback.
