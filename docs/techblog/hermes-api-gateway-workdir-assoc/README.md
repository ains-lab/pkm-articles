# 개인 논문 Wiki를 Hermes API Gateway에 연결하는 웹 서비스 설계

> 작성·확인: 2026-10-01 · 문서 상태: 구현 전 기술 설계
> 대상 Wiki: `/home/ainsdev/wiki/pkm-articles`
> **사용자 확인: 작업 경로와 적용 절차를 문서화하고, 실제 Gateway 설정은 유지한다.**

## 1. 이 문서가 답하는 질문

현재 파일 기반 논문 Wiki를 유지하면서 외부 frontend에서 목록·지식 페이지·근거를 탐색하고, 필요한 경우 Hermes에 질의하려면 무엇을 연결해야 하는가?

핵심은 **Wiki 디렉터리를 HTTP document root로 공개하는 것이 아니라, Hermes의 작업 기준 경로로 지정하는 것**이다. 웹에 노출할 자료는 별도 BFF(Backend for Frontend)가 허용 목록과 사용자 권한으로 제한한다. Hermes API Server는 모델 호출과 도구 실행을 제공하지만, 이 Wiki 전용 목록·페이지·컴파일 승인 API가 자동으로 생기는 것은 아니다.

## 2. 읽는 순서

| 문서 | 내용 | 주 독자 |
| --- | --- | --- |
| [아키텍처](architecture.md) | 시스템 경계, 배치 구조, 읽기·에이전트·게시 경로 | 설계자·전체 개발자 |
| [Wiki 경로와 Gateway 설정](workspace-and-gateway.md) | cwd 의미, 실제 관측값, 설정 우선순위, 승인 후 적용 절차 | 운영자 |
| [기술 스택](tech-stack.md) | 현재 사용 중인 기술과 신규 frontend/BFF 권고안 | 개발자 |
| [API 계약](api-contract.md) | 기존 Hermes HTTP/SSE 계약과 제안 BFF API의 구분 | backend·frontend |
| [워크플로](workflows.md) | 탐색, 질의, 재연결, 중지, 승인, 게시의 시퀀스 | 전체 개발자 |
| [데이터 계약](data-contracts.md) | 원본/지식/상태, revision/hash, 공개 DTO와 출처 연결 | backend·데이터 담당 |
| [프런트엔드 설계](frontend-design.md) | 화면·상태·접근성·스트리밍 UX | frontend·QA |
| [디자인 계약 초안](DESIGN.md) | 색상·타이포·간격·컴포넌트의 구현 전 기준 | frontend·디자이너 |
| [보안·운영](security-and-operations.md) | 토큰·권한·경로·원문·프록시·장애 대응 | 운영·보안 담당 |
| [구현·검증 로드맵](implementation-roadmap.md) | 단계별 수용 기준과 미실행 검증 | 구현 담당·리뷰어 |
| [근거와 검증 범위](evidence.md) | 공식 문서, 로컬 소스 기준점, 확인/미확인 구분 | 검토자 |

## 3. 현재 확인된 기반

2026-10-01 **01:43:55 UTC 작업 시작 기준점**의 로컬 관리 파일을 코드로 집계했다. 다음 표는 보존한 과거 snapshot이며 실시간 API 응답이 아니다.

| 구분 | 확인값 |
| --- | --- |
| 원문 보관 | 20개 고유 버전: HTML 18편, PDF 2편 |
| 활성 지식 문서 | 6개: entities 2, concepts 3, comparisons 1, queries 0 |
| 컴파일 ledger | `published_draft` 2, `blocked_approval` 16, `blocked_policy` 2 |
| 지식 검토 상태 | 기존 P2 산출물은 draft/unreviewed; 인간 검토 완료 아님 |
| 자동 컴파일·연구 리뷰 | 비활성·미등록; P3–P6 별도 승인 필요 |
| 관측한 기본 설정 | `terminal.cwd=.` / `terminal.backend=local` |
| API 서비스 실행 여부 | 이번 작업에서는 확인하지 않음; 설정 키 부재만으로 중지 상태를 단정하지 않음 |

원천 보관과 분석은 다른 지표다. 위 기준점에서 PDF 2편은 **보관 성공 + v2 컴파일 정책 차단**이었으며 수집 실패가 아니다. 논문별 컴파일 2편과 연결·비교를 포함한 지식 문서 6개도 같은 수가 아니다.

**작업 중 관측한 별도 정책 변경:** 02:01:11 UTC에 정식 정책이 `pkm-html-pdf-text-knowledge/v3`, 계약이 `pkm-contracts/v3`로 바뀐 것을 확인했다. 이때 compilation은 `blocked_approval` 16, `queued` 2, `published_draft` 2였다. PDF 2편은 별도 승인된 수동 텍스트 컴파일 경로로 전이했지만, queued는 완료가 아니다. 이 기술문서 작업이 정책을 변경하거나 해당 실행을 수행한 것은 아니다. 최종 파일 관측값과 기준점 대비 변경은 [검증 보고](verification.json)에 따로 남긴다.

v3에서는 정상 실행 gate를 통과한 **로컬 PDF 내장 텍스트**만 표준 pypdf로 메모리에서 읽는 수동 경로가 있다. PDF 바이너리·이미지 전송, OCR/렌더링, 지속 추출본 생성은 허용되지 않는다. 웹 MVP의 metadata listing·자유 질의에는 이 예외 권한이 자동 승계되지 않는다.

## 4. 제안 구조

```text
인증된 브라우저
    │ HTTPS / 사용자 세션
    ▼
Frontend + BFF                       ← 신규 구현 제안
    ├─ 정형 읽기 ── 허용된 Wiki 페이지·메타데이터
    └─ 승인된 질의 ── 내부 Hermes API Server
                         └─ AIAgent + 제한된 도구 실행 환경
                              └─ Wiki 작업 경로

별도 경로: 기존 수집 Cron / 승인된 지식 게시자
```

- **초기 범위:** 개인용 인증 서비스, 읽기 전용 탐색을 먼저 구현한다.
- **질의 범위:** 기존 Wiki 읽기와 허용 자료의 답변. 새 원문 컴파일·파일 쓰기·스케줄 변경은 별도 경로다.
- **비목표:** 공개 무인 에이전트, 다중 사용자 SaaS, 새 논문 수집기·DB·파서·벡터 저장소, PDF 분석.
- **보안 전제:** BFF만 추가하면 도구의 파일 접근까지 제한되는 것은 아니다. 에이전트 실행 환경도 별도 격리가 필요하다.

## 5. 문서의 상태 표기

- **관측:** 로컬 파일·CLI 출력 또는 실제 읽은 코드에서 확인한 사실.
- **공식 계약:** 조회한 Hermes 공식 문서에 정의된 기능. 설치 버전의 실제 응답은 별도 확인한다.
- **제안:** 아직 구현·설치·배포하지 않은 frontend/BFF/운영 설계.
- **미확인:** live API, 브라우저, 모델, 네트워크, 부하 검증을 하지 않은 사항.

본문 예시의 요청/응답은 설명용이며 실제 서비스 실행 결과가 아니다. 설정·시작 명령은 승인 후 운영 절차로만 제시한다. 문서 생성은 서버 시작·외부 공개·컴파일 승인·지식 페이지 게시를 뜻하지 않는다.

## 6. 정식 운영 기준

이 기술문서가 기존 정책을 대체하지 않는다. 충돌 시 [SCHEMA](../../../SCHEMA.md), [수집 계약](../../../_meta/COLLECTION.md), [후속 자동화 계약](../../../_meta/AUTOMATION.md), [상태·게시 계약](../../../_meta/STATE-CONTRACTS.md)을 따른다. 상세 정책을 바꾸려면 별도 승인이 필요하다.

이 폴더는 운영 기술문서이며 Wiki `Total pages`에 포함하지 않는다. 실제 파일 변경과 문서 검증 결과는 [작업 이력](../../../log.md) 및 [검증 보고](verification.json)에 기록한다.
