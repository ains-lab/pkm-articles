# DESIGN — 연구 Wiki 웹 클라이언트 디자인 계약 초안

> 상태: 제안·미구현. 개발 착수 전 확정할 기준이며 렌더링 증거가 아니다.
> [목차](README.md) · [프런트엔드 설계](frontend-design.md)

## 0. Research log

- 2026-10-01 로컬 OMH design reference를 조회했다: palette/docs, font/docs, ux/dev-tool.
- 채택 방향: Civic Navy의 읽기 대비와 문자 병행 상태 표시, dev-tool의 코드 복사·오류 후속 행동·진행 표시 원칙.
- 채택하지 않음: serif 문서 스타일과 따뜻한 sepia 배경. 이 서비스는 문서 읽기와 실행 상태가 결합된 도구이므로 운영 화면에 맞춘 sans와 차가운 중립색을 쓴다.
- 사용자 시각 레퍼런스: 없음. 외부 제품 screenshot/브랜드 자산 조사: 수행하지 않음. 유사 서비스 디자인 복제는 목표가 아니다.
- 조회 실패 기록: 공백으로 합친 context는 CLI가 거부했으며, 지원되는 단일 context로 재조회했다. 이는 디자인 품질 검증 결과가 아니다.

## 1. Atmosphere & identity

방향: **Operational**. 성격은 명료함·차분함·근거 중심이다. 대상은 지식의 상태를 빠르게 구분하려는 한국어 연구 사용자다.

시그니처는 장식이 아니라 “revision + review state + source version”이 결합된 문서 헤더다. 세 칸짜리 홍보 카드, hero gradient, 장식용 blob, 반복 eyebrow/설명문은 쓰지 않는다. 본문과 처리 상태의 정보 밀도가 우선이다.

## 2. Color

| Token | 제안 값 | 용도 |
| --- | --- | --- |
| background | `#FFFFFF` | 본문 바탕 |
| surface | `#F4F6F9` | 탐색·출처 패널 |
| text | `#10233F` | 주요 문장 |
| muted | `#4E5F78` | 보조 설명 |
| border | `#D3DAE4` | 비상호작용 영역 구분 |
| primary | `#1B3E7A` | 링크·주요 조작 |
| on-primary | `#FFFFFF` | 주요 버튼 문자 |
| warning | `#8A5A00` | 대기·주의 |
| danger | `#A32118` | 오류·위험 |
| success | `#17633B` | 검증된 특정 완료 사건 |

중립 배경이 화면 대부분을 차지하고 강조색은 조작·상태에만 제한한다. 초록을 “논문 주장이 참”이라는 의미로 쓰지 않는다. 버튼/입력 경계와 focus indicator는 WCAG AA의 해당 대비 조건을 별도 확인한다. 위 palette만으로 접근성 통과를 선언하지 않는다.

## 3. Typography

- 본문·제목: `system-ui, -apple-system, "Segoe UI", "Noto Sans KR", "Malgun Gothic", sans-serif`.
- 코드·식별자: `ui-monospace, "SFMono-Regular", Consolas, monospace`.
- 외부 폰트 자동 다운로드 없음. 별도 폰트 설치/hosting은 후속 승인·라이선스 확인 대상.
- scale: 14px 보조, 16px 본문, 20px 소제목, 24px 절 제목, 32px 페이지 제목.
- weight: 400/600/700. 한국어 본문 line-height 1.7, 제목 1.35, 코드 1.5.
- 본문 letter-spacing 0. 한국어 문장은 keep-all과 overflow-wrap을 함께 검토하고, ID·URL·해시는 별도 anywhere 줄바꿈을 허용한다.
- 제목 다중 행을 허용한다. 본문에서 중요한 근거를 clamp로 숨기지 않는다.

## 4. Spacing & layout

- 기본 단위 4px; spacing scale 4/8/12/16/24/32/48px.
- 본문 읽기 폭 최대 76ch, 앱 최대 폭 1440px 제안.
- 데스크톱 좌측 navigation 240px, 우측 provenance 280px, 중앙은 유동 폭.
- 1280px 이상은 3영역, 768px 이상은 2영역, 작은 화면은 1영역으로 설계한다.
- desktop에서는 본문 pane, mobile에서는 문서 페이지가 스크롤을 소유한다. 넓은 표·코드 블록만 자체 가로 스크롤을 허용한다.
- Chat은 메시지 영역만 스크롤하며 composer는 안정적으로 유지한다. 가상 키보드와 safe area를 검증한다.

## 5. Components

[컴포넌트 인벤토리](frontend-design.md)에 따른다. 주요 기준:

- Button: primary/secondary/danger, 높이 최소 44px 제안. hover·focus·active·disabled·loading을 구분한다.
- Input: 항상 보이는 label과 inline error, placeholder를 label 대체로 쓰지 않는다.
- Badge: 짧은 상태 문구+필요한 아이콘; 클릭 가능한 badge라면 버튼 semantics.
- Table/list: 식별자·검토 상태가 제목보다 과도하게 강조되지 않도록 한다. empty·loading·error 전용 행을 설계한다.
- Dialog/drawer: focus 관리, 닫기 동작, submit pending, stale approval 상태.
- Code block: language label, copy action, 복사 완료 알림. escape된 원문만 표시한다.

모든 interactive component의 상태는 default/hover/focus-visible/active/disabled/loading/error를 명시하며 empty가 적용되는 component는 empty도 정의한다.

## 6. Motion & interaction

- 기본 transition 120ms ease-out, drawer 최대 180ms ease-out.
- streaming text에 타자기 재생 애니메이션을 추가하지 않는다.
- bounce·상시 pulse·화면 전체 skeleton shimmer는 사용하지 않는다.
- reduced-motion에서는 위치 이동 애니메이션을 제거한다.
- focus나 읽던 위치를 스트림 이벤트마다 이동하지 않는다.

## 7. Depth & surface

flat surface + 1px border를 기본으로 한다. 모든 카드에 shadow를 주지 않는다. dialog와 떠 있는 menu만 배경과 구분되는 제한적 elevation을 사용한다. glass/blur/gradient는 기본 토큰에 없다.

## 8. Accessibility constraints & accepted debt

- WCAG AA를 목표로 하지만 현재 미검증이다.
- keyboard path, skip link, focus-visible, label, 문서 구조, 상태의 문자 병행이 필수다.
- 한글 입력 IME, 200% 확대, 긴 ID, 좁은 화면, screen reader의 live region을 실제 시험한다.
- 미해결 사항: 색 대비의 전체 조합, 화면별 정보 밀도, 실제 표·수식 렌더링, mobile drawer 높이.
- accepted debt: 없음. “미검증”은 수용한 접근성 결함이 아니라 구현 전 확인 항목이다.

다음 gate: 구현 담당자의 계약 확인 → read-only 화면 구현 → 실제 browser 증거 → 수정·재검증. 이 파일 자체는 시각 QA PASS가 아니다.
