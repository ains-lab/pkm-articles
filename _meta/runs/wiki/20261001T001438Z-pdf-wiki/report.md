# 승인된 PDF 두 편 — 수동 Wiki 컴파일·게시 완료

## 결과

정상 보호 편집 승인을 받아 v3 정책을 적용한 뒤, 승인된 두 PDF의 **내장 텍스트만** 읽어 `codex-lb / gpt-6-astra / xhigh`로 각각 한 번 생성했다. 두 응답 모두 completed이며 fallback·모델 재시도는 없었다. 원본과 생성 결과를 바꾸지 않고 근거 대조 후 로컬 Wiki에 게시했다.

| 논문 | 실제 텍스트 범위 | 주장 문맥 대조 | 게시 페이지 |
| --- | --- | --- | --- |
| Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces — `2609.30614v1` | 물리적 1–23페이지, 빈 텍스트 페이지 없음 | 27개 | `entities/arxiv-2609.30614v1.md` |
| Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal — `2609.30824v1` | 물리적 1–9페이지, 빈 텍스트 페이지 없음 | 23개 | `entities/arxiv-2609.30824v1.md` |

두 페이지 모두 `draft`, `last_reviewed=null`, `review_state=unreviewed`다. 기존 개념 3개로 각각 연결했으며 기존 v2 지식 페이지 6개는 수정하지 않았다. 새로운 논문 간 비교·종합 페이지를 생성한 것은 아니다. 색인의 활성 지식 페이지 수는 **8개**이며, compilation에는 HTML 2편과 PDF 2편이 `published_draft`, 나머지 HTML 16편은 승인 대기로 남아 있다.

## 확인한 근거

- 각 결과의 기계 검사 32개, 합계 **64개 통과**: 지정 모델, 실제 물리적 페이지 범위, 해당 페이지의 짧은 인용 일치, 가시 주장 ID·출처 표식, 미검토 항목, 로컬 연결 등.
- 부모 에이전트가 생성 본문과 **50개 주장 전부**를 승인된 PDF 내장 텍스트의 짧은 근거·주변 문맥에 대조했다. 이 검토는 독립적인 전문 재독·사람의 검토·과학적 사실성 보증이 아니다.
- collection.lock, write-ahead journal, receipt, state와 실물 hash를 대조해 두 거래가 committed임을 확인했다. 다중 파일 쓰기의 순간적 원자성을 주장하지 않는다.
- 두 페이지에 대해 두 번씩 실제 no-op 검증을 수행했고, 관찰 대상 **89개 파일**의 해시가 그대로였다.
- Wiki 8개 페이지의 frontmatter·색인 포함 여부, wikilink **38회**, 로컬 인용 링크 **294회**를 검사했다. 깨진 링크는 발견되지 않았다. 이는 출현 횟수이며 고유 링크 수가 아니다.
- 보존 기준의 **50개 파일**과 과거 log prefix가 불변이다. 원본은 여전히 **20편(HTML 18·PDF 2)**, 발견 전체 **68개 버전**, 일일 한도 대기 **48편**이다. source.json의 수집 당시 `wiki_compiled:false`는 그대로 보존하고 실제 컴파일 상태는 별도 ledger에 기록했다.
- 정책 시험 132개, PDF adapter 합성 시험 107개, 게시 계획 합성 시험 9개(하위 사례 61개)가 통과했다. adapter 최종 재시험은 네트워크 및 실제 PDF 읽기 없이 수행했다. 실제 게시 검증은 위의 별도 근거다.
- 운영/상태 JSON Schema 4개 검증 및 `git diff --check`가 통과했다. 기존 legacy v2 compile/verify/publish helper는 수정하지 않았다.

## 남는 경계

- 그림·이미지·원래 표 레이아웃·불명료 수식은 미검토다. 캡션·레이블·셀 문자열을 읽은 것과 시각 검토를 구분했다. OCR·렌더링·지속 PDF 추출본·바이너리 전송·외부 자산 다운로드·실험 재현은 하지 않았다.
- 원문·source.json·수집 state·기존 지식 6개는 변경하지 않았다. 새 노트와 index/log/compilation 및 해당 run의 승인·검증·게시 근거만 갱신했다. 정책 적용 이력은 별도로 보존했다.
- 비용 정책은 `no_cost_cap`; 두 호출의 사용량은 실제 응답값이고 비용은 미관측 `null`이다. 이를 0으로 기록하거나 비용을 게시 차단 조건으로 사용하지 않았다.
- 수집 Cron `4cff5b4f10ec`는 기존 `0 15 * * *` 일정의 collect-only 상태다. 신규 Wiki Cron은 등록하지 않았고 자동화 enabled=false, P3–P6 실행 미승인을 유지했다.
- 첫 게시 준비에서 Python 기본 timeout `2400`과 실제 CLI 기록 `2400.0`의 canonical 차이를 가드가 거부했다. 해당 기록을 남기고 원래 timeout 값으로 다시 사전 검사했다. 원본 결과·검증기 가드는 바꾸지 않았으며, 이 거부는 모델 재시도나 부분 게시가 아니다. 이전 보호 편집 시간초과/HOLD 기록도 역사적 근거로 보존했다.

## 근거 파일

모든 경로는 이 보고서 디렉터리 기준이다.

- `final-verification.json` — 전체 원천/지식/상태/보존 대조와 논문별 실행 정보
- `scope-approval.json`, `execution-approval.json` — 정확한 범위와 입력 해시·모델·편집 중지 승인
- `runtime/<version-id>/attempt1-record.json`, `attempt1-result.json` — 실제 실행과 페이지별 문자 수·텍스트 해시 telemetry; 지속 원문 추출본 아님
- `reviews/<version-id>-attempt1-verification.json`, `-agent-review.json` — 기계 검사와 주장별 의미 대조
- `publications/<version-id>-attempt1-publish-journal.json`, `-receipt.json`, `-parent-bindings.json` — 게시 거래와 복구 입력 결합
- `publications/noop-verification.json` — 두 번씩 no-op 및 89개 파일 불변
- `publications/2609.30614v1-preparation-refusal.json` — 보존된 사전 검사 거부
- `runtime/evidence/parent-final-01/counts.json`, `publication-support/evidence/parent-verification.json`, `policy-live-tests.json` — 실제 시험 근거
- `publication-support/HANDOFF.md` — 정확한 timeout 타입 보존 및 수동 게시/복구 절차
