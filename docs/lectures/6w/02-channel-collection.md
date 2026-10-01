# 02. Agent Reach 채널별 수집 방법

[목차](README.md) · [다음: Raw·상태 계약](03-raw-and-state-contracts.md)

> 아래는 **승인 후 사용할 방법**입니다. 이번 문서 작성 중에는 CLI의 버전·도움말만 확인했으며 X·Reddit 로그인/검색, YouTube 검색/자막 다운로드를 실행하지 않았습니다.

## 1. 도구·준비 상태

| 대상 | 제안 백엔드 | 관측한 설치 버전 | 실제 콘텐츠 수집 |
|---|---|---|---|
| 접근 안내 | Agent Reach | 1.5.0 | 해당 없음 |
| X | twitter-cli | 0.8.6 | 미시험 |
| Reddit | rdt-cli | 0.4.2 | 미시험 |
| YouTube | yt-dlp | 2026.08.19 | 미시험 |

버전·명령 존재는 인증 성공이나 특정 자료의 가용성을 뜻하지 않습니다. 현재 upstream main 확인 기준은 `a19a171fa980a0785849596492e0af4db800c82f`이며 설치 버전과 별개의 근거입니다.

운영 전에는 `agent-reach doctor --json`을 확인합니다. 다만 이 명령은 여러 채널을 점검할 수 있어 이번 문서 작업에서는 실행하지 않았습니다. X/Reddit의 `active_backend:null`은 인증 보호를 위해 live probe를 생략한 상태일 수 있고, YouTube의 `yt-dlp` 판정도 특정 영상 자막 성공은 아닙니다.

새 설치는 하지 않습니다. 필요해지면 upstream 설치 문서를 검토하고 승인받습니다. **PyPI의 동명 `agent-reach`를 이 프로젝트로 가정하여 설치하지 않습니다.** upstream은 자신의 GitHub 설치 경로를 안내합니다.

## 2. X·Reddit 공통 인증 경계

현재 Hermes에 설치된 `agent-reach/references/hermes-local.md`가 이 서버의 우선 지침입니다.

1. 사용자가 명시적으로 저장한 해당 계정 자격증명만 사용합니다. 값은 Wiki·prompt·명령행·로그·보고서에 넣지 않습니다.
2. 브라우저 쿠키 자동 추출을 프로세스 내부에서 차단합니다. 인증 실패 시 다른 브라우저·계정·프록시로 자동 전환하지 않습니다.
3. X는 저장된 두 값을 **하나의 자식 프로세스 환경**으로만 전달하고 `twitter_cli.auth.extract_from_browser`가 호출되면 실패하도록 차단합니다. 기존 패키지나 전역 환경은 수정하지 않습니다.
4. Reddit은 `rdt_cli.auth.extract_browser_credential`을 차단하고 명시적으로 저장된 해당 credential만 사용합니다.
5. 보호된 인증 확인에서는 종료 코드 외에 `authenticated`와 실제 identity 존재를 모두 확인합니다. 민감한 identity 원문 대신 boolean만 보고합니다.
6. 인증 거부/403이면 중단합니다. 403만으로 쿠키 만료·계정·IP 중 어느 것이 원인인지 단정하지 않습니다.

이 문서는 보호 wrapper 프로그램을 새로 제공하거나 설치하지 않습니다. 다음 X/Reddit 예시의 JSON 배열은 **검토된 CLI에 전달할 인자 설명**이지 그대로 실행할 셸 명령이 아닙니다. 향후 실행자는 위 스킬의 process-local guard를 먼저 적용해야 합니다. bare `twitter status`, `rdt status`, `rdt login`을 자동 실행하지 않습니다.

기존 [5주차 안내](../5w/social-collection-agent-reach.md)의 bare 인증 점검·자동 로그인 예시는 이번 서버 운영에 그대로 복사하지 않습니다. 비밀값 입력·회전은 별도 승인된 사용자 측 절차이며, Cron은 대화식 로그인을 시도하지 않고 `blocked_auth`로 종료합니다.

## 3. X: 발견과 단건 본문 읽기를 구분

### 키워드 발견용 인자

```json
["search", "AI agent security", "--type", "latest", "--since", "2026-09-30", "--until", "2026-10-02", "-n", "10", "--json"]
```

검색어·날짜·10건은 **교육용 예시**이며 `0d0ad6c887e3` 설정이 아닙니다. `--since/--until`은 날짜 단위입니다. 운영 checkpoint의 정확한 UTC 초 단위 창과 동일하다고 보지 않고 반환된 실제 작성 시각으로 추가 확인합니다. 검색 상한에 도달하면 완전 탐색으로 처리하지 않습니다.

### 단건 캡처용 인자

```json
["tweet", "<검색결과에서 확인한 정확한 ID 또는 URL>", "-n", "10", "--json"]
```

- 검색결과만 읽었다면 `discovery_only`; 단건을 읽었으면 실제 tweet와 반환된 reply 범위를 기록합니다.
- 안정 식별자는 숫자 tweet ID입니다. 사용자명·표시명·제목으로 식별하지 않습니다.
- `twitter tweet`의 `-n`은 댓글 범위 제한이지 전체 thread 보증이 아닙니다. 답글·인용글·재게시를 서로 구분합니다.
- 긴 글이나 X Article이 잘렸다면 전문 확보로 표시하지 않습니다. 별도 Article 읽기는 승인 대상·CLI 확인 후 수행합니다.
- 사진·영상·링크된 논문은 자동으로 따라가지 않습니다. 게시글의 텍스트 주장과 미검토 첨부를 구분합니다.
- X 검색 엔드포인트 실패는 단건 부재나 검색 결과 0건이 아닙니다. 업그레이드·OpenCLI·feed 전환으로 범위를 자동 확장하지 않습니다.

## 4. Reddit: 게시글과 댓글의 출처를 분리

```json
["search", "AI agent security", "-r", "LocalLLaMA", "-s", "new", "-t", "week", "-n", "10", "--json"]
```

```json
["read", "<검색결과에서 확인한 정확한 post ID>", "-s", "new", "-n", "20", "--json"]
```

- 키워드·subreddit·week·한도는 제안 예시입니다. 검색의 `--after` cursor는 서버 응답에서 실제 받은 값만 사용합니다. cursor를 만들거나 무제한 댓글 확장을 요청하지 않습니다.
- root post는 `t3_...`, 댓글은 `t1_...`로 구분해 원래 ID와 parent ID를 보존합니다. URL은 표시명이 아니라 실제 permalink로 확인합니다.
- 댓글 20개 반환은 전체 여론이 아닙니다. 정렬·응답 수·more 표시·삭제된 본문·접기·미확보 범위를 기록합니다.
- `--compact`는 필드를 생략할 수 있으므로 인증 진단에 쓰는 간결 출력과 보존용 출력을 구분합니다. raw 보존에는 확인한 일반 JSON을 우선합니다.
- 외부 링크 게시물은 Reddit 본문을 확보한 것이지 링크 대상 전문을 확보한 것이 아닙니다.
- 이 서버는 guarded rdt 경로를 사용하도록 로컬 지침이 정해져 있습니다. 원격 OpenCLI browser bridge는 safety hold 상태로 취급하며 자동 fallback하지 않습니다.

## 5. YouTube: 메타데이터 → 언어 선택 → 자막

아래 Bash는 설치 CLI의 옵션 존재를 확인한 **승인 후 실습 예시**입니다. URL은 공개 영상 하나만 넣고 playlist URL·개인화 피드는 사용하지 않습니다. `--ignore-config`로 사용자 설정에 숨은 다운로드·exec·cookie 옵션을 배제합니다.

### 발견

```bash
set -e
umask 077
DISCOVERY_TMP=$(mktemp -d /tmp/sns-youtube-discovery.XXXXXX)
yt-dlp --ignore-config --no-cookies --no-cookies-from-browser \
  --skip-download --dump-json --socket-timeout 20 --retries 1 \
  "ytsearch5:AI agent security" \
  > "$DISCOVERY_TMP/discovery.jsonl" 2> "$DISCOVERY_TMP/diagnostic.log"
```

`--dump-json`은 여러 JSON 객체를 줄별로 출력하므로 파일 형식은 JSONL입니다. **전체 JSONL·진단 로그를 도구 응답/모델 컨텍스트에 출력하지 않습니다.** 승인된 로컬 실행 경계에서 표준 JSON 기능으로 메모리 내 검사한 뒤 ID·canonical URL·제목·채널·게시 시각처럼 승인한 공개 필드와 성공/실패 코드만 반환합니다. `formats`, 서명된 `url`, 자막 접근 URL, header/cookie 및 diagnostic 원문은 반환하지 않습니다. 이 필드 선별은 새 커스텀 수집기나 지속 파싱본을 만드는 단계가 아닙니다. 오류 처리에서도 로그 전문을 그대로 출력하지 않습니다.

검색 5개는 순위 기반 후보 표본이지 날짜 구간의 모든 영상이 아닙니다. 검색결과에서 ID·canonical URL을 확인하고 허용 주제·시간창에 맞는 항목만 선택합니다. 채널 단위 발견은 향후 승인된 채널 ID/URL allowlist를 사용합니다.

### 제공 자막 확인

```bash
set -e
: "${VIDEO_URL:?승인된 공개 단일 영상 URL을 설정하세요}"
umask 077
SUBS_TMP=$(mktemp -d /tmp/sns-youtube-tracks.XXXXXX)
yt-dlp --ignore-config --no-cookies --no-cookies-from-browser \
  --no-playlist --skip-download --list-subs \
  --socket-timeout 20 --retries 1 "$VIDEO_URL" \
  > "$SUBS_TMP/tracks.txt" 2> "$SUBS_TMP/diagnostic.log"
```

### 수동 자막 우선 저장

```bash
set -e
: "${VIDEO_URL:?승인된 공개 단일 영상 URL을 설정하세요}"
umask 077
CAPTURE_TMP=$(mktemp -d /tmp/sns-youtube.XXXXXX)
yt-dlp --ignore-config --no-cookies --no-cookies-from-browser \
  --no-playlist --skip-download --write-subs --no-write-auto-subs \
  --sub-langs "ko,en" --sub-format vtt --socket-timeout 20 --retries 1 \
  -o "$CAPTURE_TMP/%(id)s.%(ext)s" "$VIDEO_URL" \
  > "$CAPTURE_TMP/stdout.log" 2> "$CAPTURE_TMP/diagnostic.log"
```

각 예시는 별도의 제한된 셸에서 실행하고 `set -x`/verbose를 켜지 않습니다. 트랙 확인은 언어·자막 종류·형식만, 다운로드 결과는 실제 파일명·길이·hash·오류 분류만 승인 범위 안에서 반환합니다. 본문을 모델로 읽는 것은 별도 컴파일 전송 승인 이후입니다. `set -e`는 CLI 오류를 조용히 성공으로 덮지 않기 위한 것이며, 종료 코드 0일 때의 본문·파일 검증을 대신하지 않습니다.

요청 언어가 제공되는지 앞 단계에서 확인합니다. 제공되지 않는 언어를 있다고 추정하지 않습니다. 자동 자막을 별도로 허용했다면 **새 임시 디렉터리**에서 `--write-auto-subs` 경로를 선택하고 `caption_kind:auto`, 언어, 번역 여부를 기록합니다. 서로 다른 언어/수동/자동 자막을 동일 원천 revision으로 합치지 않습니다.

자막 성공은 실제 **비어 있지 않은 VTT 본문·유효한 timestamp·video ID·언어**로 확인합니다. 종료 코드 0이나 `.info.json`만으로 자막 성공을 선언하지 않습니다. 정확한 발언 원문이 아니라 자동 자막의 오인식일 수 있습니다.

### 보존·실패 경계

- yt-dlp JSON은 metadata/서명된 미디어·자막 URL을 포함할 수 있습니다. 전체 stdout/info JSON을 무조건 raw에 복사하지 않습니다. 영속 metadata는 ID·canonical URL·제목·채널·게시 시각·선택 언어 등 허용 필드만 사용하고 원본 HTTP JSON이라고 부르지 않습니다.
- VTT는 도구가 받은 자막 캡처입니다. `.vtt` 바이트는 보존하되 “영상 전체 보존”, “시각 자료 검토 완료”, “발언 정확성 보장”으로 확대하지 않습니다.
- 반복 행 정리·번역은 raw에서 하지 않고 컴파일 중 메모리에서 해석합니다. 원래 cue timestamp를 인용에 유지합니다.
- 빈 자막/차단/네트워크 실패를 `no_captions`로 합치지 않습니다. 실제 제공 트랙 없음과 요청 실패를 분리합니다.
- bot challenge·403에서 로그인·우회·무한 재시도하지 않습니다. OpenCLI 또는 `agent-reach transcribe`는 기본 경로에 없습니다. 후자는 오디오 다운로드 및 외부 모델 전송이므로 별도 승인 없이는 금지합니다.

## 6. 원천 보관 경계로 넘기기

Agent Reach 임시 도구 출력은 `/tmp/`에서 다룹니다. 검증된 결과만 **별도 승인된 Wiki 보관 단계**가 `raw/social/`에 옮깁니다. 도구가 현재 작업 디렉터리에 JSON·자막을 흩뿌리게 하지 않습니다. 임시 출력과 진단 로그도 민감정보를 포함할 수 있어 소유자 전용 권한·보존 기간을 정하고 정리합니다.

이 출력 통제는 X/Reddit에도 적용합니다. 보호된 자식 프로세스 안에서 일반 JSON을 파일/메모리로 받고, 전체 raw 출력이나 identity·diagnostic을 모델에 직접 반환하지 않습니다. 수집 조정 모델이 볼 공개 metadata의 범위와 후속 컴파일 모델이 볼 본문 범위를 각각 승인합니다. “수집은 요약하지 않는다”는 말이 수집 과정의 모델 노출을 자동으로 없애 주지는 않습니다.

도구의 검색/조회 출력이 stdout에 성공처럼 보여도 인식 가능한 오류 객체, HTML 로그인 페이지, 빈 자료, 잘린 본문이면 캡처 성공이 아닙니다. 자세한 기록 형식은 [03](03-raw-and-state-contracts.md)을 따릅니다.
