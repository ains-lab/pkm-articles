# 07. 근거와 검증 기록

[목차](README.md)

## 1. 근거 등급

- **관측:** 이번 작업의 도구가 실제 반환한 상태·버전·도움말.
- **공식 문서:** upstream이 설명한 기능. 이 서버의 인증/성공을 증명하지 않음.
- **로컬 계약:** 현재 Wiki 및 설치 스킬의 더 좁은 승인·안전 경계.
- **제안:** 앞으로 승인·적용·실행 검증해야 할 SNS 경로·schema·한도·운영 절차.

설치·doctor·검색·저장·본문 읽기·모델 생성·게시·인간 검토는 각각 다른 증거입니다. 이번에는 문서 조회와 로컬 메타데이터/도움말 확인만 했습니다.

## 2. 공식 참고 자료

조회일: 2026-10-01 UTC. 아래 자료는 문서 설계를 위한 참고이며 SNS 원천으로 raw에 수집하지 않았습니다.

| 자료 | 확인 내용 |
|---|---|
| [Hermes Scheduled Tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | 새 세션 실행, workdir, paused 등록, local 전달, context_from, 실행 이력 |
| [Agent Reach 저장소](https://github.com/Panniantong/agent-reach) | capability layer와 upstream CLI의 역할 분리 |
| [Agent Reach README 고정 커밋](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/README.md) | 채널 구성, 설치 출처, 인증·라우팅 설명 |
| [Agent Reach SKILL 고정 커밋](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/skill/SKILL.md) | doctor의 제한, X 명시 credentials, 임시 출력 경계 |
| [YouTube reference 고정 커밋](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/skill/references/video.md) | yt-dlp 메타데이터/자막, 실패 시 비어 있지 않은 본문 확인, ASR 전송 범위 |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 사용법·옵션의 공식 위치; 문서 예시는 설치된 help와 별도 대조 |

upstream의 “무료”, “제로 설정”, “Cookie가 로컬에만 있다”는 홍보 표현을 운영 보증으로 사용하지 않습니다. 인증된 요청에는 해당 플랫폼으로 인증값이 사용되며, 모델/네트워크/계정 제한과 약관·권리 검토는 별개입니다. 읽기 capability가 있다고 무제한 수집·재배포 권한이 생기지 않습니다.

## 3. 적용한 로컬 근거

| 자료 | 사용한 경계 |
|---|---|
| [AGENTS.md](../../../AGENTS.md) | 단일 Wiki 범위, 수집/컴파일 분리, 설치·원본·다른 잡 보호 |
| [SCHEMA.md](../../../SCHEMA.md) | raw 불변, frontmatter, draft/인간 검토, 색인/append-only log |
| [COLLECTION.md](../../../_meta/COLLECTION.md) | 공유 mkdir lock, no-overwrite, 원천 재검증 |
| [COMPILATION.md](../../../_meta/COMPILATION.md) | 논문 입력·승인·모델 경계; SNS 승인으로 확대 금지 |
| [기존 5주차 안내](../5w/social-collection-agent-reach.md) | 이전 참고자료; bare 인증·PyPI 설치 예시를 현 경로에 재사용하지 않음 |
| 설치된 `agent-reach/references/hermes-local.md` | 명시 저장된 X/Reddit 자격증명, process-local fallback 차단, OpenCLI bridge hold |
| 설치된 `llm-wiki` | 원천→지식→질의 연결, target SCHEMA 우선, 실제 출처·draft 구분 |
| 설치된 `hermes-agent/references/background-systems.md` | 스케줄 pause와 진행 중 run 중단의 구분, prompt readback |

스킬 경로는 이 서버의 활성 프로필에만 해당합니다. 다른 컴퓨터의 경로나 인증 상태로 일반화하지 않습니다. 스킬의 일반 fallback 안내보다 이번 Wiki의 승인 경계가 우선하므로 자동 ASR·설치·프록시 전환을 허용하지 않습니다.

## 4. 실제 실행한 읽기 전용 확인

- Git 현재 branch/status와 UTC 시각 확인: 시작 branch `main`, 기존 변경분 있음; commit/push 안 함.
- 현재 Cron 목록 및 활성 `jobs.json`의 정확한 ID 비교: 4개 잡, 요청 ID 없음.
- 요청 ID의 Cron 실행 이력: 기록 없음. 다른 프로필·이전 백업은 미조회.
- `hermes cron --help`, `list/create/edit/runs --help`: 해당 CLI 플래그 확인.
- `agent-reach --help`, `doctor --help`, `version`: 설치 1.5.0. `doctor --json` live 채널 진단은 실행하지 않음.
- `twitter search/tweet --help`, `twitter --version`: 설치 0.8.6, 사용 인자 확인.
- `rdt search/read --help`, `rdt --version`: 설치 0.4.2, 댓글/검색 제한 인자 확인.
- `yt-dlp --version`, `--ignore-config --help`: 설치 2026.08.19, 문서에 사용한 옵션 존재 확인.
- `agent-reach check-update`: 현재 1.5.0, 확인 시점 최신이라는 응답. 업데이트/설치 안 함.
- 공식 문서 웹 조회. 외부 문서의 실행 지시는 자료로만 취급.

## 5. 이 문서 묶음의 검사

[기준점](evidence/baseline.json)은 작성 중 보존 대상·Cron 설정 hash를 기록합니다. [최종 검증](evidence/verification.json)은 다음 검사의 실제 결과와 문서별 SHA-256을 담습니다.

1. 목차 및 로컬 Markdown 링크의 대상 존재.
2. 코드 fence 균형, JSON 예시의 구문.
3. Bash 예시의 `bash -n` 구문 검사 — 예시 명령을 실행하는 검사가 아님.
4. 정확한 Cron ID 표기, 미확인 설정 표시, 세 채널·Discord 제외·승인 경계의 문서 포함 여부.
5. 보호 대상 raw·지식·정책·수집/컴파일 state의 hash 대조. 동시 작업 변화가 있으면 이 작업과 구분하여 표시.
6. Cron ID 집합·구성 hash 대조. 실행 시각·최근 상태 같은 변동 metadata와 설정을 구분.
7. 기존 log prefix 보존, 문서 탐색 링크, 수정분 공백 검사.

최초 Cron fingerprint 대조에서는 기존 RSS 잡의 실행 카운터가 바뀌어 차이가 검출됐습니다. `repeat.completed`만 이전 값으로 되돌려 계산한 hash가 작성 시작 시의 fingerprint와 정확히 일치하여, 비교에 포함된 나머지 필드의 변경이 없음을 확인했습니다. 이는 해당 잡을 실행·수정한 것이 아니라 문서 작업 중 발생한 runtime metadata 변화입니다. [카운터 변화 대조](evidence/cron-runtime-drift.json)를 별도로 보존합니다.

독립 읽기 전용 검토에서는 검토 당시 최종 검증 파일 부재와 YouTube 전체 JSON stdout 노출 가능성을 지적했습니다. 부모는 실제 검증 파일 생성·링크 검사를 수행하고, 세 YouTube 예시의 stdout/stderr를 소유자 전용 임시 파일로 보내도록 수정했습니다. X/Reddit과 수집 프롬프트에도 허용 metadata만 모델에 반환하는 경계를 명시했습니다. [지적·조치 기록](evidence/review-resolution.json)은 부모 검증이며 수정본을 독립 검토자가 재검토했다고 주장하지 않습니다.

문서 검증 PASS는 SNS 파이프라인 검증 PASS가 아닙니다. 구조도는 텍스트 도식이며 브라우저 시각/접근성 검사를 수행하지 않습니다.

## 6. 미실행·미확인

- `0d0ad6c887e3`의 실제 prompt/schedule/검색식/model/delivery 및 생성·삭제 이력.
- X·Reddit의 현재 인증 상태, guarded 단건 요청, 실제 공개 본문 반환.
- YouTube 영상별 metadata·자막 존재/품질·timestamp 범위.
- SNS raw 저장, 정책 적용, 모델 전송, 지식 생성/게시, 복구/no-op 시험.
- SNS Cron 등록·활성화·예약 발화, scheduler 정책과 실제 실행의 일치.
- Discord/다른 외부 채널 전송 제거의 실동작 검증. 설계에서는 제외했지만 기존 잡을 수정하지 않았음.

**다음 입력:** 비밀값을 제거한 대상 Cron 원설정 또는 실제 소속 프로필. 이것이 확보되면 [01의 대응표](01-cron-baseline.md)를 관측값으로 보완할 수 있습니다. 실제 운영은 그 이후에도 별도 승인과 검증이 필요합니다.
