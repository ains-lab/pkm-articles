# AI Security 검색식 전환 계약

[2026-10-01 승인 검색식 개정 — ai-security-ti-abs/v1]
사용자가 승인한 AI Security 검색식은 _meta/topics.json의 해당 cron_id 항목 original_query/api_query이며, 두 필드는 _meta/migrations/20261001-ai-security-query/approved-query.txt와 문자 그대로 같아야 한다. UTF-8 SHA-256=4ea7f574dbe38a7bfa6f1556d25016b404bfaffb70835a09b25c56cf35ac988c. 일치하지 않으면 임의 보정·all: 접두·단어 추가/삭제·AND/OR 변경 없이 정책 불일치로 중단한다. 기존 AI Agent Security라는 과거 표시명보다 이 정확한 검색 범위가 우선한다. ti:/abs: 기반 모델·에이전트 표현 AND 구체적인 보안 위협·방어 표현을 사용하며 카테고리 제한이나 의미 분류 모델을 새로 추가하지 않는다.

원본 다운로드 전 현행 쿼리 적격성을 모든 후보에 적용한다. 이전 검색식으로 들어온 pending을 자동 승계하지 않는다. 현재 실행의 정확한 쿼리 검색 응답에 동일 version_id가 있으면 일치 근거로 쓰고, 그렇지 않은 기존 pending은 동일 search_query와 versioned id_list를 동시에 보내 공식 API 교집합으로 확인한다. id_list는 최대 10개씩, GET request-line은 4094바이트 미만으로 제한한다. 요청이 길면 ID 배치를 더 줄이며 쿼리 자체는 줄이지 않는다. max_results=100/start=0, 실제 totalResults와 반환 개수·중복 없음·요청 ID 부분집합·정확한 버전·정상 Atom 응답을 확인한다. API가 최신 버전으로 바꿔 반환하면 원래 pending의 일치 근거로 쓰지 않는다. 각 요청/응답·query hash·matched/nonmatched/unknown ID 집합은 run에 기록한다. 요청 간 3초 이상, 검색과 pending 검증 요청을 합해 기존 50페이지/90분 제한 안에서 수행한다.

일치가 입증된 pending만 기존 next_attempt_at·일일 최대 5개·오래된 순 조건에 따라 다운로드한다. 정상 필터 결과의 비일치 항목은 pending을 삭제하거나 완료로 표시하지 않고 다운로드 대상에서 제외하여 query_not_matched 보류로 run 보고서에 구분한다. 불완전한 응답·HTTP 실패·버전 불일치는 query_verification_unknown으로 보존하고 다운로드하지 않는다. API 실패는 기존 실패 정책에 따라 기록하며 정상 0편/보안 비관련으로 위장하지 않는다. 현재 쿼리 검증 미완료 상태에서 옛 검색식의 적격성을 대신 쓰지 않는다. 다운로드를 시도하지 않은 항목을 daily_attempts에 예약하지 않는다.

first_window_floor/discovered_through를 검색식 변경만으로 초기화·전진·후퇴시키지 않는다. 다음 정상 실행은 기존 checkpoint와 48시간 overlap을 유지하며, 새 조건으로 과거 전체를 소급 검색하지 않는다. 알려진 pending ID만 재검증하는 것은 신규 과거 논문 발견이 아니다. 원본·source.json·기존 지식·과거 run/승인·컴파일 설정은 변경/삭제하지 않는다. 이 개정은 후보 검색의 변경이며 AI 보안 중심성의 의미 판정·영구 재수집 제외·별도 모델 호출 승인이 아니다. 승인 근거는 _meta/migrations/20261001-ai-security-query/approval.json이다.

## 검증 범위

- 공식 arXiv API 검색 및 기존 pending의 ID 교집합은 실제 네트워크 응답으로 확인한다.
- 검색 probe는 원본 수집 실행이 아니며 checkpoint·일일 시도·원본 파일을 변경하지 않는다.
- Cron 프롬프트의 예약 실행은 설정 readback과 구분해 보고한다.
- 새 커스텀 수집기·파서·DB를 만들지 않는다.
