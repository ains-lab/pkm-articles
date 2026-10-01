# 수동 2논문 통합 게시 계약 — wiki-integrate/v1

이 run은 직전 통합 컴파일·게시 및 직접 편집 중지 확인 요청에 사용자가 “진행해주세요”라고 재확인한 P2 수동 작업이다. 이전 확인창 시간초과를 소급 승인으로 고치지 않는다. P3–P6·Cron 권한을 만들지 않는다. 기본 policy pkm-html-knowledge/v2, contract pkm-contracts/v2와 원본 불변 규칙을 유지한다.

## 입력·출력

- 입력은 승인된 두 로컬 source.html과 기존 entities revision 1 두 개뿐이다. 원본을 일시 메모리에 읽어 지정 모델에 직접 전달하며 추출/정규화/compile-input/graph/이미지/표 파일은 만들지 않는다. 실행 instructions와 해시 manifest는 운영 근거이지 별도 전문 파싱본이 아니다.
- 지정 route codex-lb/gpt-6-astra/xhigh, fallback 없음, SDK retry=0. 최대 2회는 운영자 검토 후에만 사용하며 자동 재시도하지 않는다. 비용 상한·비용 절감 토큰 상한 없음. 미관측 비용 null. 모델 API에는 tools=[]·store=false·텍스트 입력만 사용한다.
- 새 개념 3개와 비교 1개는 approval.json의 정확한 경로만 허용한다. 기존 entities 두 개는 학술 본문 보존 + 연결 절 추가 + revision 갱신만 한다. draft/unreviewed 유지. 기존 human-reviewed/예상 밖 변경은 덮어쓰지 않는다.
- 기존 노트의 원 생성 근거는 유지하고, 관계 추가의 실제 generation_ref는 별도 relation_generation_ref로 기록한다. before/의 노트 snapshot은 journal 전후 비교 및 소비 revision 증거이며 모델에 재투입하는 compile-input이 아니다.

## 검증·의존성

- 구조 gate: 경로/유형/태그/정확한 두 출처, 유일 claim ID, 같은 실제 anchor 내부의 짧은 인용, 가시 Markdown의 claim→anchor 링크, 지식 wikilink 실존, 읽기/미독 범위, 양방향 링크.
- 별도 의미 gate: 저자 보고/분석 해석 구분, 근거 문맥·조건, 주장/인용 일치, 숫자 단위·비교 불가능성·시각/실험/인간 검토 미완료를 부모 에이전트가 검토한다. 단순 literal match나 모델 자기 보고를 의미 검토 통과로 승격하지 않는다.
- source_set과 consumed_wiki_refs(path/revision/hash/before snapshot), 영향을 받는 페이지 경로를 run의 영향 명세에 기록한다. 기존 노트에 추가되는 연결은 원 학술 본문을 바꾸지 않아 소비 revision 1의 의미 근거를 유지한다. 새 현재 revision은 2다.
- 과거 원 생성/게시 승인·결과·journal·receipt는 불변이다. 기존 단일 논문 publisher를 과거 요청으로 다시 실행하면 현재 revision과 충돌하는 것이 정상이며, 새 통합 manifest/receipt로 no-op을 검사한다. stale receipt에 새 파일 hash를 덮어쓰지 않는다.

## 게시·재개

- 긴 생성/검토에는 잠금 없음. 게시 시작/잠금 획득 직전 KST 23:55–01:35 수집 우선 창 확인. collection.lock 원자 획득·소유 확인, busy면 중단/skip, 탈취 금지.
- 마지막 잠금에서 승인/정책/원본/소비 노트/새 경로 부재/현재 state를 다시 확인한다. before/new/unexpected로 분류하며 unexpected는 쓰기 전 중단. 로그 기존 prefix는 보존한다.
- write-ahead journal → 지식 6개 → 최신 index의 소유 Entities/Concepts/Comparisons 절 및 Total pages → 중복 없는 log append → 두 source별 receipt → 완료 compilation state 순서다. 각 write는 기존 tested publisher의 dirfd/no-follow/fsync/조건부 Files.write·Files.append를 사용한다. 다중 파일 원자성을 주장하지 않는다.
- journal은 기존 pkm-publication-journal/v1 봉투와 transaction identity, 승인/정책/input hash, 순서별 before/after image/hash, 진행 단계, log prefix/event를 기록한다. 통합 추가 필드/여러 target은 이번 run의 수동 publisher만 해석한다. 기존 publisher의 다른 미완료 거래 검사와는 status/schema/transaction 구조로 호환된다.
- 재개는 정확한 manifest와 일치하는 old/new target에만 허용한다. 현재 index의 비소유 절 및 log의 다른 append를 보존한다. 부분 log event/중복/손상/수동 편집은 거부하며 자동 전체 rollback을 하지 않는다.
- source별 work_key는 기존 공식에 requested_scope=“P2 two-paper integrated concepts/comparison and navigation”, prompt_revision=wiki-integrate/v1, 해당 instructions hash를 사용한다. 각 source receipt에는 공동 source_set, 소비 노트 snapshot, 새 산출물 전체 refs를 명시한다. compilation items는 승인된 두 ID만 새 work_key/receipt/output refs로 갱신하며 실패 수와 나머지 항목/과거 transactions/receipts는 보존한다.
- 공동 모델 호출의 cost_event는 한 번만 append한다. 두 receipt는 같은 usage 근거를 가리키며 합산 비용을 두 번 세지 않는다.
- 최종 state/receipt/page/index/event readback과 현재 통합 manifest의 반복 no-op, 모든 raw/보호 hash·원본 파일 수·지식 페이지 수/링크를 검증한다. 실패한 단계는 미완료로 남긴다.
