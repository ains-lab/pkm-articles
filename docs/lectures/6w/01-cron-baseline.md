# 01. 기준 Cron과 적용 범위

[목차](README.md) · [다음: 채널별 접근](02-channel-collection.md)

## 1. 실제로 확인한 사실

조회 기준은 2026-10-01 UTC, 활성 Hermes 프로필 `default`, home `/home/ainsdev/.hermes`입니다. [기준점 JSON](evidence/baseline.json)에 시각·ID 집합·보존 대상 해시를 남겼습니다.

- `cronjob_manage(action="list")`: paused를 포함하여 4개 잡, 요청 ID `0d0ad6c887e3` 없음.
- 활성 프로필 `cron/jobs.json`: ID를 정확히 비교하여 같은 결과를 확인. 프롬프트·인증 정보는 문서로 복사하지 않음.
- `hermes cron runs 0d0ad6c887e3 --limit 20`: `No cron execution attempts recorded.`
- 저장소 Markdown의 정확한 ID 검색, 현재 cron 디렉터리의 ID 포함 파일명 검색: 일치 없음.
- 대화 검색도 결과 없음. 검색 가능한 세션이 없다고 반환했으므로 과거에 존재하지 않았다는 근거로 쓰지 않음.
- 다른 프로필·이전 백업은 열지 않았으며, 삭제·이동 원인은 모름.

**결론:** 요청한 잡이 어디에도 없다는 결론이 아니라, 이번에 허용된 현재 조회 범위에서 **설정을 확인할 수 없었다**는 결론입니다. 유사한 잡으로 ID를 바꿔 끼우지 않습니다.

## 2. 관련 기존 잡 — SNS 기준값이 아님

| 잡 | 관측된 역할·설정 | 이 설계에서의 처리 |
|---|---|---|
| `4cff5b4f10ec` | arXiv 수집, `0 15 * * *`, local, enabled=true, `arxiv` | 논문 원천 수집 전용 유지 |
| `4839be6a1db1` | PKM Daily Wiki Compiler, `0 17 * * *`, local, enabled=false/state=paused, `llm-wiki` | 승인된 논문 신규 노트 경계 유지 |

두 잡의 모델 관측값은 `codex-lb / gpt-6-astra / xhigh`입니다. 일정의 KST 의도는 각각 00:00, 02:00이라고 로컬 계약에 기록돼 있습니다. **이 값은 대상 SNS 잡의 일정·모델을 증명하지 않습니다.** 나머지 두 잡은 이번 목적과 무관하므로 운영 설명·연결 대상에서 제외합니다.

## 3. 원래 설정을 받으면 채울 대응표

| 원설정 필드 | 현재 확인값 | SNS Wiki 방향으로 검토할 내용 |
|---|---|---|
| 정확한 job ID·프로필·name | ID만 사용자 제공 | 동일 잡인지 재조회; 다른 프로필 접근은 명시 승인 |
| schedule·시간대 | 미확인 | 기존 cadence 유지 여부; UTC/KST와 실제 next_run 대조 |
| prompt | 미확인 | 검색식·계정·기간·한도 추출; Discord 생성/전송 지시 제거 |
| skills | 미확인 | 수집은 `agent-reach`, 컴파일은 `llm-wiki`로 분리 |
| workdir | 미확인 | 승인 후 `/home/ainsdev/wiki/pkm-articles` 명시 |
| model/provider/reasoning | 미확인 | 수집 조정 모델과 SNS 컴파일 전송 모델을 각각 승인 |
| script/no_agent/monitor | 미확인 | 기존 script의 부작용·전송·인증 자동 추출 여부 점검 |
| context_from/continuity | 미확인 | 이전 요약문 대신 원천 manifest·state를 진실의 기준으로 사용 |
| deliver/failure_deliver | 미확인 | 둘 다 `local`; 직접 메시지 호출도 금지 |
| enabled·진행 중 실행·실패 이력 | 미확인 | 전환 전 중복 실행·중단·복구 계획 검토 |

설정을 공유할 때 Cookie, Authorization, API key, 계정 세션, Webhook 비밀 URL을 포함하지 않습니다. 채널 ID도 이 설계에는 필요하지 않습니다. 원설정 없이는 “기존 검색식 유지”, “기존 일정 승계”, “기존 Discord 전송 제거 완료”라고 말할 수 없습니다.

## 4. 현재 Wiki 정책과 충돌하는 지점

현재 [SCHEMA](../../../SCHEMA.md)는 arXiv 버전별 HTML/PDF를 원천으로 정의합니다. [컴파일 계약](../../../_meta/COMPILATION.md)의 허용 입력도 로컬 HTML·별도 승인 PDF 내장 텍스트 등으로 한정되어 있습니다.

| SNS 요구 | 별도 승인·설계가 필요한 이유 |
|---|---|
| JSON·VTT를 raw에 보관 | 현재 원천 schema와 다름; `arxiv-*-source/v1` 재사용 불가 |
| 게시글·댓글·자막을 모델에 전달 | 논문 입력 승인으로 SNS 전송을 허용할 수 없음 |
| 사용자별·서브레딧별 추적 | 수집 대상·개인정보·기간·약관 검토 필요 |
| 원천별 draft·개념·비교 갱신 | 기존 P3는 신규 논문별 노트에 한정; SNS·기존 페이지 갱신 별도 승인 |
| SNS 예약 수집·컴파일 | 현재 승인 Cron을 바꾸거나 새 Cron을 등록할 권한이 아님 |
| 자막 실패 시 음성 전사 | 오디오 다운로드·외부 ASR 전송으로 범위가 달라짐; 기본 금지 |

이 기술문서는 AGENTS/SCHEMA/automation 정책을 수정하지 않습니다. 문서에 제안한 `sns-source/v1-proposed` 같은 이름은 **신규 계약 초안**이며 설치된 schema·검증기·지원 API가 아닙니다.

## 5. 역할과 권한

- **Hermes Cron:** 새 세션에서 정해진 작업을 시작하고 로컬 결과·이력을 남깁니다. 현재 대화를 자동 승계하지 않으므로 프롬프트는 독립적으로 이해돼야 합니다.
- **Agent Reach:** 플랫폼별 백엔드 선택·설치 안내·진단을 제공합니다. 실제 읽기는 `twitter`, `rdt`, `yt-dlp` 등이 담당합니다. Wiki 수집 DB나 컴파일러가 아닙니다.
- **원천 보관 담당:** 승인된 응답을 검증하여 `raw/`에 불변으로 게시합니다. 지식 해석은 하지 않습니다.
- **llm-wiki 컴파일 담당:** 승인된 로컬 캡처만 읽고 출처를 단 draft를 생성합니다. 플랫폼에 새 검색을 요청하지 않습니다.
- **사용자:** 주제·범위·인증 사용·모델 전송·게시·검토 및 자동화 활성화를 결정합니다.

`workdir`와 `AGENTS.md`는 접근 통제 의도를 전달할 뿐 OS sandbox가 아닙니다. 필요하면 제한된 계정·파일 권한을 따로 설계해야 하며, 이번 문서 작업에서 환경을 바꾸지 않습니다.

## 6. 다음 확인에 쓸 읽기 전용 명령

```bash
hermes cron list --all
hermes cron runs 0d0ad6c887e3 --limit 20
hermes cron create --help
hermes cron edit --help
```

현재 CLI에는 `hermes cron show`를 가정하지 않습니다. 목록의 preview만으로 전체 prompt를 검증할 수 없으므로, 운영 전에는 승인된 프로필의 정확한 저장 레코드를 **비밀값 제외·필드 선별 방식**으로 대조해야 합니다. `jobs.json`을 수동 편집하지 않습니다.
