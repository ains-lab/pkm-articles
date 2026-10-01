# 03. Raw 보관과 파일 기반 상태 계약

[목차](README.md) · [다음: Wiki 컴파일](04-wiki-compilation.md)

> 모든 경로·schema·상태 이름은 **SNS 도입 제안**입니다. 현재 arXiv 원천 schema를 변경하거나 아래 운영 파일을 생성한 것이 아닙니다. 구현된 수집기·검증기·DB를 가정하지 않습니다.

## 1. 디렉터리 제안

```text
/home/ainsdev/wiki/pkm-articles/
├── raw/
│   ├── articles/                 # 기존 arXiv 원본, 변경 금지
│   └── social/                   # 별도 정책 승인 후에만 생성
│       ├── x/<tweet-id>/captures/<capture-id>/
│       │   ├── payload.json      # 단건 twitter 출력, 허용 범위 확인
│       │   └── source.json
│       ├── reddit/<post-id>/captures/<capture-id>/
│       │   ├── payload.json      # 단건 post + 실제 반환된 댓글
│       │   └── source.json
│       └── youtube/<video-id>/captures/<capture-id>/
│           ├── captions.<lang>.<manual-or-auto>.vtt
│           └── source.json       # 공개 metadata + 자막 범위
├── _meta/
│   ├── sns/collection-policy.json # 제안: 승인 scope와 검색 기준
│   ├── state/sns-collection.json  # 제안: 발견·pending·관측 상태
│   ├── state/sns-compilation.json # 제안: 읽기·생성·검증·게시 상태
│   ├── staging/sns/<run-id>/      # 게시 전 파일, 소비 금지
│   └── runs/sns/<run-id>/         # 비밀값 없는 manifest/receipt/오류
├── entities/                     # 출처별 또는 실체별 draft
├── concepts/                     # 여러 출처의 공통 개념
├── comparisons/                  # 주장·조건·결과 비교
├── queries/                      # 재사용할 질의 답변
├── index.md
└── log.md
```

정식 캡처는 stable platform ID와 capture ID로 식별합니다. 제목·작성자·입력 URL을 그대로 파일명에 사용하지 않습니다. 경로 구분자·`..`·symlink·Wiki 루트 이탈을 거부하고 실제 정규 ID를 검증합니다. Reddit `t3_`/`t1_` 구분, YouTube URL의 실제 video ID, X 숫자 ID를 보존합니다.

`capture-id`는 고유한 UTC 수집 시각과 충돌 방지 토큰으로 구성하는 제안입니다. **플랫폼 자체의 버전 번호가 아닙니다.** 같은 ID라도 게시물 수정·자막 변경·댓글 추가는 새 캡처가 될 수 있습니다.

## 2. 무엇을 원천이라고 부를 것인가

| 데이터 | 보관 해석 | 하지 말아야 할 주장 |
|---|---|---|
| X CLI JSON | `tool_output_snapshot`; CLI가 선택·구조화한 자료 | 플랫폼 HTTP 응답 원문 전체 |
| Reddit 단건 JSON | post와 반환된 댓글 표본 | 모든 댓글·전체 이용자 의견 |
| YouTube VTT | 특정 언어·종류의 자막 캡처 | 영상/음성 원본 전체 또는 정확한 전사 |
| 선별된 YouTube metadata | `allowlisted_metadata`; 파생된 공개 서지 정보 | 변형 없는 원본 info JSON |
| 검색 목록 | `discovery_only`; 후보 발견 근거 | 단건 전문 확보·논문/영상 내용 검토 |
| 생성 요약·번역 | Wiki 해석 계층의 생성물 | raw 원문 |

arXiv의 `capture_method:http_response_body_no_rewrite`를 SNS CLI 출력에 붙이지 않습니다. `source.json`에도 `preprocessing:false`를 무조건 복제하지 않습니다. upstream 도구의 구조화·필드 선별 여부를 정확히 기록합니다.

허용된 공개 텍스트 외에 세션 token·서명된 접근 URL·비공개 데이터가 결과에 섞이면 raw 게시를 중단합니다. 불변이라는 이유로 민감정보를 영구 보존하지 않습니다. 필요한 필드 선별이 승인됐다면 **선별된 capture**로 명시하고, 비선별 payload를 “원본”이라는 이유로 유출·보관하지 않습니다. 이 문서는 선별용 새 parser 프로그램을 제공하지 않습니다.

## 3. 최소 metadata 계약

| 필드 | 의미와 검사 |
|---|---|
| `schema` | `sns-source/v1-proposed`; 제안 이름, 운영 적용 시 확정 |
| `platform`, `source_id`, `canonical_url` | 반환 결과와 대조한 플랫폼·원래 ID·고정 공개 URL |
| `title`, `author_ref` | 관측한 공개 제목/작성자 식별, 최소 수집; 미확인은 null |
| `published_at`, `updated_at`, `collected_at` | 원천 작성/수정 시각과 실제 수집 시각을 분리; 모르면 null |
| `collector_ref` | 실제 run ID, 실제 job ID 또는 수동 실행, backend/version, scope revision |
| `capture_method`, `transformations` | 도구 출력/선별 metadata/자막, 수행한 변환을 숨기지 않음 |
| `content_scope` | 검색만/본문/댓글 표본/자막, 읽을 수 있는 실제 범위 |
| `files` | 파일별 상대경로·bytes·SHA-256·미디어 유형 |
| `coverage` | 요청/반환 수, 정렬, 제한, 더보기 여부, 언어·자막 종류·시간 범위 |
| `limitations` | 잘린 본문·미확보 댓글·미검토 영상·자동 자막 오류 가능성 |
| `access_policy_ref` | 공개 범위·인증 사용·보존·후속 모델 전송에 관한 승인 참조 |

아래 JSON은 필드 설명용 **미실행 템플릿**입니다. null·빈 배열은 아직 관측하지 않았다는 뜻이며 보관 성공으로 사용할 수 없습니다.

```json
{
  "schema": "sns-source/v1-proposed",
  "example_only": true,
  "platform": "youtube",
  "source_id": null,
  "canonical_url": null,
  "published_at": null,
  "updated_at": null,
  "collected_at": null,
  "collector_ref": {"job_id": null, "run_id": null, "backend": "yt-dlp", "backend_version": null},
  "capture_method": "caption_track_snapshot",
  "transformations": [],
  "content_scope": "selected_caption_track",
  "files": [],
  "coverage": {"language": null, "caption_kind": null, "time_ranges": [], "complete": null},
  "limitations": ["video_visuals_not_reviewed"],
  "access_policy_ref": null
}
```

파일 해시는 **실제 저장 바이트**로 계산합니다. payload 해시와 `source.json` 해시는 구분하고, 후자는 별도 receipt에서 참조하여 자기 자신을 해시하는 순환 구조를 만들지 않습니다. 인증 header·cookie·명령행 비밀값은 metadata에 포함하지 않습니다.

## 4. 중복은 세 가지 단위로 판단

1. **논리 원천:** `(platform, source_id)` — 검색식이나 Cron이 달라도 동일합니다. 다른 주제에서 찾았다는 이유로 같은 자료를 다시 전문 저장하지 않습니다.
2. **캡처:** 논리 원천 + 범위(댓글 정렬/언어/자막 종류 등) + 파일 manifest의 hash. 같은 자료·같은 범위·같은 바이트이면 기존 파일을 재검증하여 재사용합니다.
3. **컴파일 작업:** 승인된 source manifest hash + policy/prompt revision + 승인 모델 경로 + 출력 범위. 동일 입력의 검증된 committed 결과는 no-op 후보입니다.

전체 JSON hash 변화는 내용의 진실성 변화가 아닙니다. 조회수·좋아요·댓글 수만 변해도 바이트는 달라질 수 있습니다. 새 관측과 지식 재생성 필요성을 분리합니다. 최소 버전에서는 변경 캡처를 `needs_review`로 보내고, 나중에 승인된 의미 비교를 통해 본문/범위 변경이 없으면 “재컴파일 불필요” 근거를 남깁니다. 아직 없는 semantic hash 구현을 있다고 가정하지 않습니다.

## 5. 증분 발견과 checkpoint

- 플랫폼·검색식 revision·계정/채널 allowlist별 cursor/window를 따로 둡니다. X 실패로 Reddit 성공분을 되돌리거나 YouTube 기준점을 전진시키지 않습니다.
- 최초 범위와 overlap을 승인합니다. 예: 최근 24시간·48시간 overlap은 **제안값**이며 기존 논문 정책을 자동 상속하지 않습니다.
- `last_attempt_at`, `last_success_at`, `last_complete_window_end`를 구분합니다. 정상 0건과 실패 0건을 구분합니다.
- 발견한 candidate를 pending에 내구 저장한 뒤에만 해당 발견 단계의 cursor를 전진합니다. pending이 있으므로 발견 checkpoint와 캡처 완료 상태는 다를 수 있습니다.
- top-N 검색, ranking, 날짜 단위 필터, 늦은 색인은 완전성을 보장하지 않습니다. 상한에 도달하거나 다음 cursor를 끝까지 확인하지 못하면 `coverage:partial/unknown`으로 남깁니다.
- `last_complete_window_end`는 열거의 완전성이 관측된 경우에만 전진합니다. 순위 기반 검색은 `last_attempt_at`과 best-effort window만 기록하고 “이전 항목 없음”을 주장하지 않습니다.
- 큐 한도 초과는 실패와 다릅니다. 승인한 오래된 pending 우선순위·개수·시간 상한을 적용하고 밀린 데이터 수를 보고합니다.

## 6. 상태 축 — 현재 시스템에 없는 제안

| 축 | 상태 예시 | 완료 증거 |
|---|---|---|
| 발견 | discovered / rejected_scope / pending | 실제 ID·조회 조건·시각 |
| 캡처 | captured / partial / blocked_auth / retryable_failed / unavailable | 실물 파일·내용 범위·해시 |
| 컴파일 | blocked_approval / queued / generating / generated / failed | 승인 snapshot·실제 생성 응답 |
| 검증 | pending / pass / needs_review / rejected | 인용·범위·주장 대조 결과 |
| 게시 | not_published / staged / committed / conflict | journal·receipt·최종 파일 hash |
| 사람 검토 | unreviewed / needs_review / human_reviewed | 실제 사용자 검토 참조 |

집계는 플랫폼 ID 집합으로 계산합니다. 발견 수·캡처 수·자막 트랙 수·지식 페이지 수를 합산하여 “수집 건수” 하나로 부르지 않습니다. 한 YouTube 영상의 두 언어 자막은 영상 1개·트랙 2개입니다.

## 7. 불변 게시와 중단 복구

1. 비공개 임시 디렉터리에서 응답을 받고 승인 범위·본문·ID·민감정보를 검사합니다.
2. 같은 파일시스템의 `_meta/staging/sns/<run-id>/`로 검증된 파일을 준비합니다. `/tmp`와 raw 사이의 이동을 단일 원자 rename이라고 가정하지 않습니다.
3. 기존 `collection.lock` 계약과 호환되는 소유 잠금 아래 최종 hash·중복·사용자 변경을 확인합니다. 잠금이 있으면 `skipped_busy`; 오래됐다고 탈취하지 않습니다.
4. target이 없는 캡처 디렉터리에 덮어쓰기 없는 게시를 수행하고 exact target을 다시 읽어 검증합니다. 실패한 staging은 소비하지 않습니다.
5. receipt와 source manifest를 기록한 뒤 캡처 완료 state를 갱신합니다. 중간 중단 시 “파일 있음”만으로 성공 처리하지 않고 hash·receipt를 대조합니다.
6. Wiki 게시에는 별도 write-ahead journal을 사용합니다. 다중 파일을 OS 단일 원자 거래로 설명하지 않습니다. 조건부 복구만 허용하며 사용자 편집을 되돌리지 않습니다.

이 절은 구현 요구사항이지 SNS publisher가 이미 구현되었다는 설명이 아닙니다. 기존 논문 publisher는 원천/승인 schema가 다르므로 SNS payload를 억지로 넣거나 가드를 해제하지 않습니다.

## 8. 삭제·수정·보존 정책

나중에 원 게시물이 사라져도 과거 캡처를 “원래 없었다”고 바꾸지 않습니다. 삭제 관측 시각과 관련 지식의 `needs_review`를 별도로 기록합니다. 반대로 개인정보 삭제 요청·권리 문제가 생기면 무조건 영구 보존하지 않고 접근 차단·명시 승인된 삭제 절차를 적용합니다. 자동 대량 삭제·백업 복원은 없습니다.

공개 자료도 개인적 연구용 로컬 보관을 기본으로 하며 공개 Git 저장소에 raw를 commit/push하지 않습니다. 보존 기간·리뷰 주기·접근 권한은 첫 수집 전에 확정합니다.
