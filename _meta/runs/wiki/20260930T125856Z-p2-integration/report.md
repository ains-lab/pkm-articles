# P2 수동 통합 컴파일·게시 완료

- 완료: `2026-09-30T13:36:31.079363+00:00`
- run: `20260930T125856Z-p2-integration`; transaction: `p2i-d3b8cf0db1b918060510445ffe3b227a`
- 결과: **개념 3개 + 비교 1개 신설, 기존 논문 노트 2개 연결 갱신, 활성 지식 페이지 6개**. 모두 `draft/unreviewed`, `last_reviewed=null`. 논문 원고를 쓴 것이 아니라 기존 원문을 개념·비교·논문 노트 사이에 연결한 Wiki 지식이다.

## 산출물

| 구분 | 경로 | revision |
|---|---|---|
| 신규 | `concepts/agent-authority-and-effect-boundaries.md` | 1 |
| 신규 | `concepts/provenance-and-audit-evidence.md` | 1 |
| 신규 | `concepts/security-evaluation-units.md` | 1 |
| 신규 | `comparisons/agate-vs-sdc-mcp-gateway.md` | 1 |
| 갱신 | `entities/arxiv-2609.30830v1.md` | 2 |
| 갱신 | `entities/arxiv-2609.31358v1.md` | 2 |

- `index.md`: 실제 6개 페이지 색인, Entities/Concepts/Comparisons와 페이지 수만 갱신; Queries·Raw Sources·운영 안내 보존.
- `log.md`: 기존 prefix를 유지하고 이번 거래 사건 한 번 append.
- `_meta/state/compilation.json`: 승인된 두 source만 새 output refs/work key/receipt로 갱신. 기존 실패 수·이전 transactions/receipts와 다른 8개 item 보존.
- 기존 논문 노트는 학술 주장과 원 generation_ref를 보존했다. revision=2, 새 relation_generation_ref를 추가하고 연결 절·게시 안내·일반 Markdown에서 열리는 원문 상대 경로 141건을 정리했다. 소비 revision 1은 `before/`와 `dependency-impact.json`에 hash로 보존한다.

## 실제 생성과 근거 검토

- `codex-lb / gpt-6-astra / xhigh`, 승인된 route에서 실제 비스트리밍 모델 요청 1회 completed. SDK 재시도 0, fallback 없음, 외부 도구 없음.
- 입력: 두 원본 HTML과 기존 Wiki 노트 두 개만. 원문 파싱본·이미지·PDF·전체 대화·외부 검색을 입력하지 않았다.
- 새 주장 **36개**를 부모 에이전트가 원본 **52개 고유 앵커**의 문맥과 대조했다. 짧은 식별 인용·같은 행 citation **73건**은 모두 literal/anchor 검사 통과.
- `agent-evidence-review.json`은 각 page/claim의 별도 rationale와 정확한 source/quote hash를 기록한다. 모델 자기 보고와 구조 검사만으로 의미 검토를 대신하지 않았다.
- 이번 통합 읽기는 선택 절 기반이다. 이전 노트의 전문 읽기 선언을 이번 새 전문 완독으로 승계하지 않았다. 저자 보고·AI 해석 및 분모/집행 범위/실험 한계를 유지한다.

## 게시와 최종 검증

- 기존 collection.lock을 공유하고 수집 우선 창 밖에서 실행했다. journal → 지식 6개 → index → log → source별 receipt 2개 → state 순으로 내구 게시, 마지막 journal 상태 `committed`. 다중 파일 원자성을 주장하지 않는다.
- 게시 후 실제 지식·receipt·state·index·event를 다시 읽어 hash 및 대응을 확인했다. unresolved 거래 없음, 자기 잠금 해제 확인.
- **로컬 Markdown 링크 222개, Wiki 연결 28개 정상; 깨진 링크·고립 페이지 없음.**
- 같은 통합 manifest로 **no-op 두 번**을 실행했다. 매회 **122개 파일 내용 불변**, 새 모델 호출·중복 사건 없음. 과거 단일 노트 게시 요청은 superseded revision에 대한 것이므로 현재 no-op 근거로 쓰지 않는다.
- 원문 **15편(HTML 13·PDF 2)**의 실제 버전·바이트·hash, 보호 **74개 파일** 불변. PDF는 metadata/바이트 hash만 확인했으며 내용을 읽거나 파싱하지 않았다.
- 합성 회귀 **61개 통과**: 기존 publisher 41개 + 이번 수동 거래 fixture 20개. 중간 중단/복구, grant 누락, 사용자 수정, 부분 log, 동시 편집, journal 손상, busy 및 수집 우선 창을 검사했다. 논문 실험 재현은 아니다.

## 비용·진단·미수행 범위

- 비용 상한/절감 토큰 상한 없이 실행. 실제 사용량: {"input_tokens": 184441, "output_tokens": 32287, "total_tokens": 216728, "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 6990}}. 비용은 미관측 `null`이며 0으로 추정하지 않았다. 공동 호출의 cost_event는 한 번만 기록했다.
- 호출 전 로컬 준비 오류: `read_json`의 `(object,digest)` 반환값 처리 오류가 모델 요청 전에 발생했다. 반환형과 실제 함수 정의를 대조하여 수정했고 실패 기록을 보존했다.
- 최종 검사 첫 스캔은 index의 inline-code 예시 `[[디렉터리/파일명]]`를 실제 페이지로 잘못 셌다. 원인 확인 후 실제 catalogue 범위로 검사하고 가짜 누락 항목 부정 시험을 통과했다. 원본 index를 검사에 맞춰 고치지 않았다.
- 인간 내용 검토·그림 시각 검토·수식 독립 검증·실험 재현·임상 판단 검증 없음. 다른 13개 원문은 이번 작업에서 컴파일하지 않았다. 수집 때 추가된 5개 버전의 compilation ledger 미등록 상태도 범위 밖이라 유지했다.
- `enabled=false` 유지. P3–P6, Cron 등록/활성화, 추가 수집, 설치, 독립 수집기/파서/DB 추가, 전역 설정·인증 변경, commit/push 없음.

## 근거

- `approval.json`, `attempt1-record.json`, `attempt1-result.json`
- `structural-check-initial.json`, `agent-evidence-review.json`, `prepublication-verification.json`
- `publication-manifest.json`, `integration-publish-journal.json`, `publication-result.json`
- `2609.30830v1-receipt.json`, `2609.31358v1-receipt.json`
- `dependency-impact.json`, `entity-change-verification.json`, `noop-verification.json`, `final-verification.json`
- `preflight-invocation-failure.json`, `verification-scan-correction.json`
