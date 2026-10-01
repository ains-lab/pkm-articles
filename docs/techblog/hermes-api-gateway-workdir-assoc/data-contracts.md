# 데이터 계약: 원본, 지식 페이지, 상태 projection

> 상태: 기존 파일 형식은 관측·정식 계약, HTTP DTO는 제안.
> [목차](README.md) · [API](api-contract.md) · [근거](evidence.md)

## 1. 정식 저장소

```text
/home/ainsdev/wiki/pkm-articles/
├── AGENTS.md / SCHEMA.md        작업 경계·스키마
├── index.md / log.md            탐색 색인·append-only 이력
├── raw/articles/<cron-id>/
│   ├── index.md
│   └── arxiv-<encoded-version-id>/
│       ├── source.html 또는 source.pdf
│       └── source.json
├── entities/                   논문별 노트
├── concepts/                   개념 연결
├── comparisons/                비교
├── queries/                    저장 승인된 질의
├── _meta/state/                수집·컴파일 등 상태
├── _meta/runs/                 실행·검증·승인 근거
└── docs/techblog/hermes-api-gateway-workdir-assoc/  이 기술문서; 지식 페이지 수 제외
```

이 구조는 웹 URL 구조와 동일하지 않다. 특히 `_meta/runs/`와 `log.md`는 공개 전체 원문 endpoint가 아니다. HTTP 응답은 필요한 필드만 명시적으로 고른다.

## 2. 원본과 서지

- HTML: `arxiv-html-source/v1`, `html_file`, `html_sha256`, `html_bytes`.
- PDF: `arxiv-pdf-source/v1`, `pdf_file`, `pdf_sha256`, `pdf_bytes`, HTML 미제공 근거.
- 공통: 정확한 `version_id`, title/authors/categories, URL, 수집 시각과 HTTP 보존 정보.
- 원본은 HTTP 응답 바이트 그대로이며 미리 변환한 Markdown·임베딩·구조화 논문 JSON을 전제하지 않는다.
- `source.json`의 `wiki_compiled:false`는 수집 당시 정보다. 이후의 완료 여부는 compilation ledger·receipt·실물 output으로 확인한다. 완료 표시를 맞추려고 원본 JSON을 수정하지 않는다.

PDF 파일을 read_file 같은 문서 추출 도구에 넣는 것도 분석 실행이다. 이 서비스 설계의 metadata listing 경로는 JSON만 읽고 PDF 내용을 해석하지 않는다. v3의 별도 승인 수동 컴파일만 표준 pypdf로 내장 텍스트를 메모리에서 읽을 수 있으며 일반 문서 변환 도구로 대체하지 않는다. raw HTML 역시 public origin에서 그대로 inline 실행하지 않는다.

## 3. 지식 페이지 메타데이터

기본 필드: title, summary, created, updated, last_reviewed, type, status, tags, sources, confidence, contested, contradictions.

후속 페이지는 다음 provenance도 가진다.

| 필드 | UI 의미 |
| --- | --- |
| `schema: pkm-knowledge-page/v1` | 계약 버전 |
| `revision` / `transaction_id` | 어떤 게시 결과인지 |
| `policy_revision` / `prompt_revision` | 생성 정책·프롬프트 기준 |
| `generation_ref` | 실제 생성 근거의 내부 참조; 원문 전체 자동 공개 금지 |
| `read_scope` / `unread_scope` | 읽음·미검토 범위 |
| `review_state` | unreviewed / needs_review / human_reviewed |
| `status` | draft / reviewed / superseded |

`draft + unreviewed`는 오류가 아니라 정상 미검토 상태다. `published_draft`는 compilation item 상태이며 페이지 `status`의 대체 enum이 아니다. 사용자가 내용 검토를 했다는 근거 없이 `reviewed`/`human_reviewed`로 승격하지 않는다.

## 4. 서로 다른 상태 축

| 축 | 예시 | 다른 축으로 추론하면 안 되는 것 |
| --- | --- | --- |
| 원문 확보 | HTML 보관, PDF 보관, 미확보 | 보관 성공 → 의미 분석 완료 |
| HTML 제공 | 제공, 공식 미제공, 일시 오류 | HTML 미제공 → 원문 미확보 |
| 컴파일 | blocked_approval, blocked_policy, reading, partial, published_draft | 모델 종료 → 게시 완료 |
| 게시 거래 | 미해결, committed | state 문자열 → 실물 무결성 보장 |
| 인간 검토 | unreviewed, human_reviewed | 자동 인용 검사 → 인간 검토 |
| API 실행 | running, completed, failed 등 | API completed → 논문 검토 완료 |

기준점과 v3 전이 관측은 [README](README.md)에 있다. `blocked_policy`는 과거 상태로 남을 수 있으나 PDF 형식만 보고 현재 상태를 하드코딩하지 않는다. v3 정책 적격/실행 승인 대기, queued/reading, partial, 실제 게시를 구분한다. 상태 합산은 정확한 버전 ID 집합으로 수행하고, pending과 HTML 미제공 이력을 보관 원본 수에 중복 가산하지 않는다.

## 5. 공개 DTO 초안 — 구현되지 않은 계약

BFF가 저장소 메타데이터를 최소 노출 형태로 투영할 때 권고하는 shape다. 아래 `<...>`는 실제 관측값이 아닌 설명용 placeholder다.

```json
{
  "schema": "pkm-web-page/v1",
  "page_id": "entity-arxiv-2609.30830v1",
  "title": "<페이지 title>",
  "summary": "<페이지 summary>",
  "type": "entity",
  "revision": 2,
  "status": "draft",
  "review_state": "unreviewed",
  "content_sha256": "<64자리 실제 SHA-256>",
  "markdown": "<허용한 지식 페이지 본문>",
  "sources": [
    {
      "version_id": "2609.30830v1",
      "format": "html",
      "source_sha256": "<원본 SHA-256>",
      "source_url": "https://arxiv.org/html/2609.30830v1",
      "anchor": "<실제 원문에 존재하는 anchor>"
    }
  ],
  "read_scope": [],
  "unread_scope": [],
  "snapshot_id": "<서버가 계산한 committed snapshot 식별자>"
}
```

- page_id는 서버 생성 식별자다. 브라우저가 절대/상대 파일 경로를 전달해 읽는 방식은 금지한다.
- `snapshot_id`와 `pkm-web-page/v1`은 **제안된 BFF 계약**이며 기존 Hermes 필드가 아니다.
- `<64자리 실제 SHA-256>`은 길이 검증 예시가 아니다. 구현에서는 실제 hex 64자리와 파일 해시 일치를 검사한다.
- 본문 전체가 필요 없는 목록 API에서는 markdown·claim detail·내부 evidence 경로를 생략한다.
- 비용을 노출한다면 관측된 값만 사용하고 미관측은 `null`로 둔다. `0`으로 채우지 않는다.

## 6. URL와 파일 경로 연결

1. BFF가 공개 page_id → 허용된 루트 상대 Markdown 경로의 매핑을 가진다.
2. `entities/`, `concepts/`, `comparisons/`, `queries/`의 승인된 파일만 후보로 사용한다.
3. NUL, 절대경로, `..`, 역슬래시 혼용, 중복 URL decoding, symlink를 거부한다.
4. 해석한 canonical 경로가 root 하위인지 확인하되, 이 검사만으로 TOCTOU를 해결했다고 주장하지 않는다. 안전한 파일 열기와 불변 snapshot/권한 경계를 함께 구현한다.
5. `[[entities/arxiv-2609.30830v1]]`을 UI page URL로 연결한다. 확장자는 문자열 끝에 `.md`를 **덧붙인다**. ID의 점을 확장자로 오인해 치환하지 않는다.
6. HTML 인용은 버전 고정 `source_url`과 실제 anchor로 보낸다. 승인된 PDF 텍스트 인용은 `source.pdf#page=N`의 물리적 1-based 페이지를 사용한다. HTML에 PDF 페이지 번호를 발명하지 않으며, PDF의 시각 요소·불명료 수식/레이아웃 미검토 표시를 유지한다.

브라우저에 `/home/ainsdev/...` 같은 서버 절대경로를 노출하지 않는다. 원문 anchor가 확인되지 않으면 논문 단위 링크와 “세부 위치 미확인”을 표시한다.

## 7. 일관성 있는 읽기와 캐시

권고 read procedure:

1. 읽을 output 목록과 committed receipt/거래 상태를 확인한다.
2. 해당 revision과 파일 hash를 대조한다.
3. 읽기 전후 관련 상태 식별자가 변하지 않았는지 검사한다.
4. 충돌하면 제한적으로 재시도하거나 `snapshot_conflict`를 반환한다.
5. 성공한 snapshot만 page hash를 ETag로 사용해 캐시한다.

새 DB를 원장으로 만들지 않는다. process-local index/cache는 파생된 가속 수단이며 재생성 가능해야 한다. 캐시를 도입해도 collection state·원본 JSON·지식 provenance를 덮어쓰지 않는다. 초기 구현은 공유 캐시 없이 private/no-store부터 시작해도 된다.

## 8. 쓰기 계약은 별도

현재 frontend 초안은 파일 수정 endpoint를 제공하지 않는다. 향후 편집·피드백 저장에는 사용자 저장 요청, 정확한 page revision/hash, 민감 정보 제외, 잠금·조건부 갱신·append-only 이력이 필요하다. Web form 제출을 자동 연구 리뷰나 전체 대화 저장 허가로 확대하지 않는다.

정식 상태 전이와 journal/receipt 필드는 [STATE-CONTRACTS](../../../_meta/STATE-CONTRACTS.md), 피드백은 [QUERY-FEEDBACK](../../../_meta/QUERY-FEEDBACK.md)을 따른다.
