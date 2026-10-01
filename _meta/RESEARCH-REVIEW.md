# 고정 14일 연구 리뷰·아이디어 계약

Policy `pkm-html-knowledge/v2` / contract `pkm-contracts/v2`. [research-review.json](state/research-review.json), [작업 프롬프트](prompts/research-review.md). P5/P6 실행은 미승인, Cron 미등록, anchor=null이다.

## 창과 입력

- 사용자가 승인한 UTC anchor 이후 `[start,end)`를 정확히 14일 간격으로 정의한다. KST는 표시용이다. `every 14d`는 스케줄 발화 의도이며 처리 구간/달력 시각 보장은 아니다. 월 일자 `*/14`를 사용하지 않는다.
- 실제 committed_at을 기준으로 컴파일 revision 및 accepted/withdrawn 피드백 사건의 멤버십을 정한다. start는 포함, end는 다음 창. 논문의 published/updated/collected_at은 멤버십 기준이 아니다.
- 최신 성공 창의 다음 **닫힌 창**을 가장 오래된 순으로 한 실행 최대 1개 처리한다. anchor/첫 실행이 없으면 추정하지 않고 blocked_approval이다. 밀린 창은 carryover 또는 별도 승인 catch-up으로 남긴다.
- 최초 활성화 이전의 committed 지식은 자동으로 사라지게 하지 않는다. 첫 리뷰 전에 사용자와 bootstrap 입력 목록/anchor를 확정하고 원래 시각과 실제 소비 창을 carryover에 기록한다. 사전 승인이 없으면 포함 여부를 보류한다.
- 입력 manifest에는 source version/hash, page revision/hash, 사건 ID, 입력 시각, 제외/partial/미독/PDF blocked 및 unresolved 거래 목록을 동결한다. unresolved·근거 철회 페이지는 확정 지식으로 소비하지 않는다. 기존 관련 Wiki는 배경으로 읽되 같은 원출처를 독립 증거로 중복 계산하지 않는다.
- 실패·지연 항목은 original_committed_at/original_window_id/actual_window_id/reason과 함께 이월한다. 성공하지 않은 항목의 consumed 표시 금지. 입력 열거/무결성 확인이 실패하면 empty 창이 아니다.

## 분석과 산출물

개인 학습공백, 문헌 수집공백, 연구공백 **후보**를 구분한다. 발산 후 별도 비판 관점으로 반론/기각 이력/중복을 대조한다. 에이전트 추가 호출·별도 모델은 비용/공급자 승인 밖으로 확장하지 않는다. 현재 코퍼스만 쓰며 외부 신규성 검색은 금지다.

정식 보고서는 창별 `queries/research-review-<window-id>.md` 한 개, 후보는 `queries/research-idea-<idea-id>.md`에 둔다. type=query/status=draft/last_reviewed=null. 0–3개 추천은 상한이지 할당량이 아니다. 추천이 없으면 이유를 기록한다.

각 아이디어에는 문제/수혜자, 두 문장 pitch, 논문 근거와 반대 근거, 반증 가능한 가설, 코퍼스에서 확인한 최근접 연구와 차이, 조사 범위/novelty_unverified, 최소 실험/기준선/지표/반증·중단 조건, 알려진 자원과 unknown, 반론, 추천/보류 이유, 사용자 결정 상태를 담는다. “내 Wiki에 없다”를 “학계에 없다”로 바꾸지 않는다. 해시/앵커 존재만으로 의미 검토를 대체하지 않는다.

## 게시와 재시도

AUTOMATION의 공통 잠금·journal을 사용한다. 보고서/아이디어 → 최신 index → log event → 검증 receipt → 창 포인터/consumed_event_ids를 완료 거래로 확정한다. 중단되면 미완료 거래로 차단하고 old/new/unexpected hash를 대조한다. 재시도에 보고서/사건 소비를 중복 생성하지 않는다. 파일 생성만으로 성공 포인터를 전진하지 않는다.

관측상 신규 입력이 없는 닫힌 창은 입력 열거·무결성 검증 근거가 있는 empty receipt로 완료할 수 있다. 보고서에는 범위와 빈 이유를 남기고 아이디어를 강제로 생성하지 않는다. 승인/정책 차단은 empty로 처리하지 않는다. 비용 미관측 자체는 차단 사유가 아니다.

## 아이디어 선택과 제안서

사용자가 정확한 idea_id/revision/page_sha256을 선택한 사건만 selected가 된다. 선택/기각/철회 시각·이유·actor=user·근거를 보존한다. revised/withdrawn/rejected 아이디어는 자동 집필하지 않는다. 선택 자체도 P6 실행·집필 비용 승인을 대체하지 않는다.

P6 승인 뒤에만 `queries/research-proposal-<idea-id>.md`를 **연구 제안서/결과 미작성 논문 초안**으로 작성한다. 실험 전에는 관측 결과·수치·가짜 References/BibTeX를 만들지 않는다. 사용자 선택이 없어도 정상 상태다. 실험/코드 실행/GPU/데이터 다운로드/제출은 별도 승인 범위다.
