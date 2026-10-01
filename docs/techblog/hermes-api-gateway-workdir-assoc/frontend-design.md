# 프런트엔드 설계와 구현 인계

> 상태: frontend_design_brief / route-state / implementation handoff 초안.
> 구현·브라우저·접근성·시각 QA 결과는 모두 미관측.
> [목차](README.md) · [디자인 계약](DESIGN.md) · [워크플로](workflows.md)

## 1. 제품과 화면 우선순위

대상은 개인 논문 Wiki를 사용하는 연구자다. 주요 과업은 “자료 찾기 → 기존 노트 읽기 → 근거·미검토 범위 확인 → 필요할 때 질의”다. 대시보드를 장식하는 지표보다 자료의 상태와 근거를 정확히 보여주는 것이 우선이다.

현재 웹 앱·디자인 시스템은 이 폴더에 구현하지 않는다. 초기 구현은 greenfield이며 [DESIGN.md](DESIGN.md)를 토큰·컴포넌트 계약 초안으로 사용한다. 컴포넌트 작성 전에 구현 담당자가 이 계약을 확인·확정해야 한다.

## 2. 제안 라우트

다음은 **frontend route 제안**이지 현재 제공되는 URL이 아니다.

| 화면 | 제안 route | 핵심 정보 | 초기 범위 |
| --- | --- | --- | --- |
| 자료 탐색 | `/library` | 서지, 원문 형식, 지식 노트 유무, 필터 | read-only MVP |
| 지식 페이지 | `/knowledge/:pageId` | summary, 본문, revision, 검토·미독 범위 | read-only MVP |
| 개념·비교 탐색 | `/topics` | 기존 concepts/comparisons 링크 | read-only MVP |
| 질의 | `/chat/:conversationId` | 선택한 문서, 메시지, 실행 상태, 출처 | 별도 실행 승인 후 |
| 운영 상태 | `/operations` | 축약된 수집·컴파일 상태 | 소유자 전용, 정형 조회 |

계정 관리나 public signup은 MVP에 없다. pageId는 파일 경로가 아니라 서버가 검증한 식별자다. `/operations`는 Cron 수정·즉시 실행·raw state 편집 화면이 아니다.

## 3. 레이아웃과 읽기

- 데스크톱: 좌측 탐색, 중앙 본문, 선택적 우측 출처/목차.
- 태블릿: 우측 패널은 접고 본문 아래 또는 drawer로 이동한다.
- 모바일: 탐색 drawer, 단일 본문, 출처 disclosure. 화면 전체 가로 스크롤은 금지한다.
- 문서 헤더는 제목, summary, 상태 배지, 갱신일과 revision을 표시한다.
- 출처 패널은 논문 버전·원문 URL·인용 anchor·미확인 상태를 보여준다.
- Markdown의 raw HTML은 기본 비활성, 링크 protocol을 제한하고 코드 블록은 escape한다.
- wikilink는 서버가 제공한 page 매핑으로 해석한다. 못 찾은 링크는 오류를 숨기지 않고 “연결 대상 없음”으로 표현한다.

## 4. Route × 상태 행렬

| 화면 | Loading | Empty | Error | 정상·경계 상태 |
| --- | --- | --- | --- | --- |
| Library | 기존 목록 보존 + 로딩 문구 | “현재 필터에 맞는 자료 없음” | 재시도·인증 만료 구분 | pending/HTML/PDF/지식 유무 개별 표기 |
| Knowledge | 제목·본문 영역 안정적 skeleton | 노트 미작성 | 없음/권한 없음/snapshot 충돌 | draft/unreviewed와 partial 읽기 표시 |
| Topics | 목록 placeholder | 아직 연결 문서 없음 | 링크 조회 실패 | 개념·비교 유형 구분 |
| Chat | 접수/실행 단계 표시 | 질문과 문서 선택 안내 | 네트워크/정책/모델 실패 구분 | waiting approval/stopping/partial 결과 |
| Operations | 마지막 관측값+시각 | 아직 관측 없음 | 상태 조회 불가 | disabled·not_registered·busy 구분 |

모든 화면을 375/768/1280px에서 검증하고 최종 시각 검토에는 1440px도 포함한다. viewport 이름만 작성했다고 반응형 검증 완료가 아니다.

## 5. Chat 상태 모델

UI 상태는 Gateway status와 1:1로 무조건 같지 않다.

```text
idle → submitting → accepted → active
active → awaiting_approval → active
active → stopping → terminal
active → disconnected → reconciling → active 또는 terminal
terminal = completed / failed / cancelled / interrupted
```

`accepted`, `disconnected`, `reconciling`은 BFF/UI 로컬 상태다. 실제 upstream 상태·run ID를 함께 보관한다. UI의 `active`에는 설치 Gateway가 보고한 queued/running 등을 구분해 표시할 수 있다. 알 수 없는 상태는 unknown으로 안전하게 표시한다.

- commentary: 진행 메시지 영역.
- tool event: 도구 이름과 최소 상태; raw arguments/result 전체 노출 금지.
- delta: 임시 본문; 재접속 후 최종 snapshot과 중복 제거.
- final: 종료 상태에 연결된 최종 답변.
- usage/cost: 관측값만; 미관측은 “확인되지 않음”.

비공개 추론을 수집·저장·재구성하지 않는다. reasoning field를 제공하는 upstream을 사용하더라도 사용자에게 보여줄 범위와 보존 여부를 서버에서 별도 결정한다.

## 6. 컴포넌트 인벤토리

| 컴포넌트 | 필수 상태·동작 |
| --- | --- |
| SearchInput | 기본/focus/입력 중/clear/disabled/error; 한국어 IME 조합 중 제출 금지 |
| FilterControl | 선택/미선택/focus/disabled; 키보드로 동등 조작 |
| SourceRow | 링크 focus/hover, PDF 보관과 정책 적격/승인 대기/실행/게시를 분리, 노트 없음 |
| ReviewBadge | 색상+문자; “검토 완료”는 실제 인간 검토 근거가 있을 때만 |
| MarkdownViewer | 로딩/빈 본문/escape된 코드/미해결 wikilink/넓은 표 |
| CitationPanel | 닫힘/열림/근거 없음/anchor 미확인; focus 복귀 |
| Composer | draft/submitting/busy/error; Enter/Shift+Enter 규칙 고지 |
| RunStatus | pending/active/approval/stopping/terminal/unknown |
| StopButton | active만 활성, 제출 중 disabled, 처리 결과 고지 |
| ApprovalDialog | pending/expired/submitting/resolved; 서버가 보낸 선택지만 허용 |

기본·hover·focus-visible·active·disabled·loading·empty·error 변형 중 적용되지 않는 것은 의도적으로 “해당 없음”으로 기록한다. 아이콘만으로 위험·검토·처리 상태를 표현하지 않는다.

## 7. 접근성·CJK

- 모든 입력에 label, 페이지에 하나의 주 제목과 일관된 heading hierarchy를 둔다.
- keyboard-only 탐색, 본문 건너뛰기, focus-visible, dialog focus trap/복귀를 검증한다.
- 한국어 본문 최소 14px, 기본 16px, 충분한 line-height. 제목의 조사 고립과 ID 줄바꿈을 점검한다.
- 긴 arXiv ID/해시/URL은 전체 값을 복사할 수 있게 하며 말줄임표가 유일한 접근 수단이 되지 않도록 한다.
- SSE token마다 스크린리더 알림을 발생시키지 않는다. 단계 변경과 완료를 `aria-live`로 조절한다.
- `prefers-reduced-motion`을 존중하며 auto-scroll 중 사용자가 위로 이동하면 강제 하단 이동을 중지한다.

## 8. 성능 목표 — 측정 결과 아님

제안 측정 조건: 중급 모바일, 375px, 제한된 4G/CPU profile, 인증된 `/library` 및 `/knowledge/:pageId`의 cold navigation. 구현 첫 baseline의 브라우저/네트워크/CPU profile을 정확히 기록하고 같은 조건으로 비교한다.

- field 목표: p75 LCP < 2.5s, INP < 200ms, CLS < 0.1.
- 현재 baseline: **없음**. Lighthouse/실사용 수치 모두 미측정.
- lab에서는 LCP element와 지연 구간, 이동한 node, 입력 처리 지연을 진단한다. lab 통과를 field p75 통과로 표시하지 않는다.
- API 지연과 모델 생성 지연은 별도 측정한다. 첫 화면 rendering이 모델 답변 완료에 종속되지 않게 한다.
- 목록 pagination, 필요한 지식 본문만 로드, 스트림 batch rendering으로 불필요한 전체 재렌더를 피한다.

## 9. 구현 인계와 QA

담당 역할 제안: frontend는 화면/stream reducer, BFF는 정책·ownership·projection, 운영자는 격리·TLS·키, 검토자는 Wiki provenance와 승인 경계.

구현 뒤 실제 화면에서 Library/Knowledge/Chat의 정상·empty·error·긴 한국어·긴 코드·연결 단절 상태를 캡처한다. 차이를 Blocker/High/Medium/Nit로 분류하고 수정 후 재검증한다. 키보드·스크린리더·모바일 검토와 악성 Markdown 시험도 필요하다.

현재 상태는 **prepared_not_observed**다. 브라우저 screenshot, UI 구현, 접근성 PASS, Lighthouse 점수, 배포 성공은 생성하지 않았으며 주장하지 않는다. 구체적인 테스트 경계는 [로드맵](implementation-roadmap.md)에 있다.
