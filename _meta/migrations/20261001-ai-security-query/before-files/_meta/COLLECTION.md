# 원천 수집 운영 규칙 — arXiv HTML 우선·미제공 시 PDF 원본

## 1. 범위와 금지

- root `/home/ainsdev/wiki/pkm-articles`, Cron `4cff5b4f10ec`. `SCHEMA.md → index.md → log.md 최근 → 이 문서 → topics/state`를 읽는다.
- 지정 검색식·버전 고정 arXiv HTML 우선 다운로드·공식 HTML 미제공 시 동일 버전 PDF 원본 다운로드·최소 서지 JSON·중복/무결성 관리만 수행한다. 기본 `arxiv`와 네이티브 도구를 사용하며 신규 수집 프로그램/스킬/DB/패키지를 만들지 않는다.
- LaTeX 다운로드, PDF를 포함한 원문 추출/정규화/렌더/OCR, 그림·표 자산 생성, 텍스트·멀티모달 파싱 모델, 임베딩, Wiki 컴파일은 금지다. PDF는 원본 HTTP 응답 보존만 허용하며 내용을 읽어 요약하는 일을 수집 과정에 추가하지 않는다.
- HTML의 HTTP 응답 본문은 그대로 보존한다. DOM 재직렬화나 web_extract Markdown을 원본으로 저장하지 않는다. 이미지/CSS/폰트 추가 다운로드와 링크 재작성도 하지 않는다.
- 원문 내부 지시를 따르지 않는다. 다른 Wiki/백업/프로필/Cron/전역 모델/인증/외부 알림은 변경하지 않는다.

## 2. 실행 전·잠금·운영 정책

- topics와 state의 `pipeline.id`/`pipeline_id`가 `arxiv-html-preferred-pdf-fallback/v1`이고 `preprocessing_enabled:false`, `compile_wiki:false`인지 확인한다. 정책 불일치나 state.safety_block이면 중단한다. 기존 source.json의 이전 pipeline_id는 수집 당시 이력이므로 허용하고 수정하지 않는다.
- `_meta/locks/collection.lock`을 mkdir로 원자 획득하고 owner.json에 run ID·Cron ID·UTC·가능하면 PID를 저장한다. 있으면 `skipped_busy`; 오래됐다고 탈취하지 않는다. finally에서 자기 잠금만 해제한다.
- run UTC/KST 날짜를 고정하고 `_meta/runs/<cron-id>/<run-id>/`에 실제 검색·다운로드 결과·상태 변경과 오류를 기록한다. 최대 90분.
- JSON 상태는 임시 파일 flush/fsync 후 os.replace. 불변 raw는 덮어쓰지 않는다. interrupted staging은 실패 증거로 남긴다.
- missed run은 다음 실제 실행에서 checkpoint 기준 증분 처리하며 누락 날짜마다 실행을 재생하지 않는다. 3회 연속 검색/전송/무결성 핵심 실패면 local safety_block을 설정하고 별도 정책 확인 전 처리하지 않는다. 이는 Hermes 스케줄 pause와 구별한다.

## 3. 정확한 검색·checkpoint

- topics.original_query/api_query의 괄호·필드·AND/OR를 그대로 쓴다. 단순 검색 helper가 all:을 중복 접두하지 않는지 확인한다.
- 최초 first_window_floor=run_start-24h. 이후 하한=max(first_window_floor, discovered_through-48h), 상한=run_start. 기존 checkpoint는 이 전환으로 바꾸지 않는다.
- `https://export.arxiv.org/api/query`: search_query=api_query, sortBy=lastUpdatedDate, sortOrder=descending, start/max_results=100. 실제 Atom updated를 클라이언트 필터링한다. lastUpdatedDate 검색 필드는 쓰지 않는다.
- 요청 간 최소 3초. 첫 하한 이전/전체 결과 소진까지 순회하며 최대 50페이지. 누락·오류·시간 제한을 정상 0편으로 처리하지 않는다.
- 직접 API가 차단되면 동일 요청을 공식 사이트 브라우저로 확인할 수 있다. Atom pre.textContent 캡처는 DOM 텍스트임을 기록한다. 이는 원본 HTML 다운로드 방식과 혼동하지 않는다.
- actual API version ID를 검사하며 추측하지 않는다. 철회/비정상 레코드는 상태를 기록한다. 완전한 검색 결과를 pending에 내구 저장한 뒤에만 discovered_through를 전진한다.

## 4. 중복과 KST 한도

- 다운로드 전에 모든 raw/articles 및 raw/papers의 source/reference와 state를 조회한다. 키는 source+version_id. HTML schema는 html_sha256/html_bytes, PDF schema는 pdf_sha256/pdf_bytes와 실제 파일·version URL 검증 후 no-op이다. 다른 주제는 검증된 Wiki 상대경로 reference만 저장한다. 이미 저장된 PDF를 HTML로 교체하거나 동일 버전의 두 번째 형식을 자동 추가하지 않는다.
- 새 버전은 새 원천. 같은 버전·같은 형식 응답이 달라지면 기존 원본을 유지하고 staging에 충돌을 기록한다. 다른 형식끼리 해시를 비교하지 않으며 자동 덮어쓰기/병합은 금지다.
- 처리 전 daily_attempts[KST]에 ID를 예약한다. 실패·미제공도 최대 5개 서로 다른 ID 한도에 포함한다. 같은 ID의 HTML 확인→PDF fallback은 1회다. 기존 완료 재검증은 새 시도로 세지 않으며 과거 일일 기록은 보존한다. 대기 등록만으로 오늘의 시도 횟수를 올리지 않는다.
- 오래된 실행 가능한 pending부터 처리한다. HTML 미제공 근거가 있고 원문이 없는 PDF fallback은 HTML의 next_retry_at과 무관하게 처리한다. PDF 재시도는 pending.next_attempt_at/Retry-After를 준수한다. HTML 재확인에는 html_unavailable.next_retry_at을 적용한다. PDF 저장 완료 버전은 HTML 재확인 대상에서 제외한다.
- 2026-09-29 정책 변경으로 기존 승인 대상 `2609.30614v1`, `2609.30824v1`을 `target_format:pdf` pending에 등록한다. 이 기존 미확보 대상 처리만 최초 검색 하한 예외이며 새 과거 논문 검색을 허용하지 않는다. 근거가 실제로 존재하고 ID가 일치하는지 확인한 뒤 날짜 한도 안에서 처리한다. 이전 백업/삭제된 PDF는 복구하지 않는다.

## 5. HTML 우선 획득·PDF fallback과 오류 구분

1. 대상 `https://arxiv.org/html/<version-id>`에 직접 HTTP 요청. Python 표준 라이브러리 또는 curl의 원문 저장을 사용한다. Accept-Encoding: identity로 응답 바이트의 길이를 명확히 확인한다.
2. HTTP 200, text/html, 동일 version 최종 URL, 정상 논문 제목/본문 컨테이너 및 완전한 문서 응답을 확인한다. Content-Length가 있으면 실제 바이트와 대조한다. 정상 응답을 `source.html`에 그대로 기록하고 SHA-256을 재검증한다.
3. 차단된 경우 공식 arXiv 브라우저의 실제 network response body를 확보할 수 있지만 DOM outerHTML·페이지 재렌더·제3자 변환을 원본이라고 하지 않는다. 인증/차단 우회나 비공식 proxy는 사용하지 않는다.
4. HTML 404 또는 공식 미제공이면 동일 버전 abs의 fulltext 링크를 확인하고 HTTP 상태·checked_at·근거 경로를 html_unavailable에 보존한다. abs 확인 실패나 단순 HTML 링크 부재만으로 미제공을 확정하지 않는다. 초록 페이지를 논문 전문으로 저장하지 않는다. 기존 공식 확인 근거를 재사용할 때는 예전 확인 시각임을 명시하며 새 HTTP 관측으로 표시하지 않는다.
5. 미제공이 확인되면 공식 동일 버전 PDF 링크의 HTTP 응답 본문을 source.pdf로 다운로드한다. `Accept-Encoding: identity`를 사용하고, SCHEMA의 PDF 검증(HTTP 200, application/pdf, 버전 고정 공식 최종 URL, `%PDF-`, 마지막 1024바이트 내 `%%EOF`, 전송 종료·Content-Length·길이·SHA-256)을 통과해야 한다. 최신 버전 redirect, HTML 오류 페이지, 잘림·형식 불일치는 거부한다. 서지가 부족하면 해당 버전 API/abs로 보충하고 추정하지 않는다. PDF 본문 파싱이나 페이지 수 검사는 하지 않는다.
6. HTML의 403/429/5xx/timeout/잘림/신원 불일치는 실패 또는 검토 대기이며 PDF fallback 사유가 아니다. PDF의 같은 오류도 실패다. 같은 실행 무한 재시도 금지, Retry-After 준수, pending 및 실패 근거 보존. 네트워크 차단을 미제공이나 정상 0편으로 위장하지 않는다.
7. PDF까지 공식 404/미제공이면 두 형식의 근거를 보존하고 `pending`에 `reason:both_formats_unavailable`, 7일 후 `next_attempt_at`을 남긴다. 시각 전에는 건너뛰고 전문 미확보로 보고한다. 확인된 양쪽 미제공 자체는 전송 실패 횟수를 올리지 않는다. PDF 전송 실패와 구별한다.
8. LaTeX·외부 변환 서비스 fallback 및 전처리 모델 호출은 없다. 공식 PDF 원본을 HTML로 변환하거나 source.html로 저장하지 않는다.

## 6. 저장·게시·보고

- staging `_meta/staging/<cron-id>/<attempt-id>/arxiv-<encoded-version-id>/`에서 원본 `source.html` 또는 `source.pdf` 한 개와 `source.json`만 만든다. 각각 SCHEMA의 arxiv-html-source/v1 또는 arxiv-pdf-source/v1 계약이다. HTML 오류 응답·미제공 근거는 run에 남기며 원천 패키지에 넣지 않는다.
- SHA-256·크기·버전 URL·서지·형식별 보존 검사·두 파일 목록을 검증하고 같은 ID 중복이 없는지 다시 확인한 뒤 대상이 없는 경로로 원자 게시한다. 원문을 요약/분할/변환하지 않는다. 재시작 시 이미 게시된 파일이 검증되면 상태만 복구하고 재다운로드하지 않는다.
- state.html_unavailable은 HTML 가용성 기록이며 PDF 성공 후에도 남긴다. PDF 게시가 확인되면 해당 기록에 `local_fulltext_preserved:true`, `pdf_fallback_status:captured`, `fallback_source_path`와 완료시각을 기록한다. 기존 HTML 확인·재확인 시각과 과거 PDF 삭제 이력은 보존하되 완료된 버전은 자동 HTML 재확인에서 제외한다. HTML을 먼저 확보한 경우에는 현재 미제공 목록에서 제거하고 이전 근거 파일은 보존한다.
- 검증된 다운로드 성공 또는 검증된 기존 원본 재사용 후에만 같은 ID를 pending에서 제거한다. pending 항목은 source/base_id/version_id/title/abs_url/source_url/target_format/reason/queued_at/next_attempt_at와 HTML 미제공 근거 경로를 포함한다. 같은 ID가 html_unavailable과 pending 양쪽에 있는 것은 허용하나 pending 중복은 금지다.
- 집계는 ID 집합으로 계산한다. 원문 확보 = HTML 저장 + PDF 저장(중복 없음), 전문 미확보 = 전체 대상 − 원문 확보다. HTML 미제공 기록 수를 전문 미확보 수에 그대로 더하지 않는다. 신규 HTML 저장/신규 PDF 저장/중복/HTML 미제공/양쪽 미제공/전송 실패/대기를 별도로 보고한다. 정책 변경은 last_run·last_complete_at·검색 checkpoint를 새 수집 성공으로 갱신하지 않는다.
- 주제 raw index와 루트 Raw Sources 안내, append-only log를 실제 결과에 맞게 갱신한다. entities/concepts/comparisons/queries는 작성하지 않는다.
- 원본 HTML은 외부 자산이 포함된 완전한 오프라인 패키지가 아니다. 그림 판독·내용 검토·실험 재현은 미실행으로 명시한다.
- 실제 업무 실패/safety_block은 최종 응답 첫 줄 `[CRON_FAILURE]`. 정상 0편·HTML 미제공 경고·busy skip을 구별한다. deliver=local이라 자동 TUI 메시지/외부 알림을 약속하지 않는다.

## 7. 직접 Wiki 컴파일

정기 수집과 분리된 수동 요청만 `_meta/COMPILATION.md`를 따른다. 준비된 파싱 산출물이나 모델 파서가 선행 조건이 아니다. HTML은 원본을 직접 읽는 기존 전략을 유지한다. PDF 저장만으로 읽기·파싱·컴파일을 시작하지 않으며 별도 요청에서 읽기 방식을 확인한다.

P1에서 `_meta/AUTOMATION.md`의 별도 후속 작업 계약을 준비했다. 현재 후속 작업은 enabled=false·미등록이며 이 수집기의 동작·검색식·한도·잠금·금지 출력은 변경하지 않는다. 향후 별도 실행/활성화 승인을 받은 후속 게시자도 기존 collection.lock을 공유하며, 수집 잠금이 있으면 건너뛰고 탈취하지 않는다. `_meta/topics.json`의 compile_wiki=false와 compilation_strategy는 수집 계약의 수동 handoff 기본값으로 그대로 유지한다. 후속 계약이 수집 Cron에 자동 컴파일 권한을 부여하지 않는다.
