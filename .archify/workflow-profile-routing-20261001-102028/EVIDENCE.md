# 근거와 산출물 경계

이 패키지는 기술문서와 공식 계약을 기반으로 한 **미적용 서비스 설계**다. 실행 중인 서비스의 토폴로지, 새 프로필 존재, BFF 구현 또는 live API 응답을 관측했다는 뜻이 아니다. Wiki 원문은 읽거나 전송하지 않았다.

## 문서 근거

아래 경로는 Wiki 저장소 루트 기준이며, 줄 번호는 이번에 읽은 작업 트리 문서의 위치다. untracked/수정 문서를 Git HEAD의 커밋된 구현 근거로 표시하지 않는다. 해당 문서 및 기존 슬라이드의 SHA-256은 `source-baseline.json`에 기록했다.

| 주장 | 근거 |
|---|---|
| BFF와 Hermes API 구분, run 생성·상태·SSE·stop | `docs/techblog/hermes-api-gateway-workdir-assoc/api-contract.md:6–32,60–118` |
| 사용자·session·run 소유권과 답변/게시 분리 | `docs/techblog/hermes-api-gateway-workdir-assoc/workflows.md:25–35,37–82` |
| terminal.cwd, 세션 경로 우선, 임의 cwd payload 비지원 조사 범위 | `docs/techblog/hermes-api-gateway-workdir-assoc/workspace-and-gateway.md:43–63,118–124` |
| 키 서버 보관, method/path allowlist, 도구·자료·read-only 집행 | `docs/techblog/hermes-api-gateway-workdir-assoc/security-and-operations.md:23–50,61–78` |
| 기존 수집/컴파일은 웹 요청과 별도 | `docs/techblog/hermes-api-gateway-workdir-assoc/INTEGRATION-ARCHIFY.md:80–95`; `SCHEMA.md:3–7` |

## 공식 계약·설치 소스 확인

- [API Server — Multi-profile routing](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server#multi-profile-routing-pprofile): `/p/<profile>/v1/...`, 프로필별 API_SERVER_KEY, 생성한 프로필에 run 귀속. 이번 대화에서 조회한 공식 문서 캐시의 806–822행을 재확인했다.
- [Multi-profile gateways — What does not change](https://hermes-agent.nousresearch.com/docs/user-guide/multi-profile-gateways#what-does-not-change): terminal.backend/cwd/mount 등은 라우팅된 프로필별로 해석한다. 공식 문서 캐시의 620–629행을 재확인했다.
- [Working Directory](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#working-directory): terminal.cwd는 기본 작업 경로다.
- `/home/ainsdev/.hermes/hermes-agent/tools/file_tools_paths.py:116–177`: 세션 cwd → 등록된 override → 설정된 cwd, 상대경로 결합 및 절대경로 취급. 로컬 소스 읽기만 했으며 runtime 호출 검증은 아니다.

## 이번에 설계한 부분

- 외부 API `/pkm-articles/v1/runs` → 내부 `/p/pkm-articles/v1/runs`의 BFF 허용 매핑.
- 대상 `pkm-articles` 프로필의 기본 cwd를 `/home/ainsdev/wiki/pkm-articles`로 구성하는 안. 해당 프로필을 조회·생성·변경하지 않았다.
- `team-wiki`와 `/srv/wiki/team-wiki`는 다중 프로필을 설명하기 위한 **가상 값**이다. 다른 Wiki나 프로필을 열람하지 않았다.
- BFF가 사용자·Wiki·profile·session·run을 연결하고 모든 상태/events/stop 요청을 검사한다는 것은 구현 요구사항이다.
- 입력 자료·도구·모델 전송 승인과 실제 격리 검증은 서비스 적용 전 조건이다. 기존 자동 컴파일 승인을 새 웹 질의 권한으로 확대하지 않는다.

## 최종 전달물과 제외한 시도

- `03-api-sequence/diagram.html`: **주 그림**. 전체 요청/응답을 시간순으로 나타낸다. 최종 자동 근거는 `03-api-sequence/label-review/`. 시각 표본에서 숨겨진 note에만 있던 cwd 설명을 발견해 그림의 단계 제목·화살표 라벨에 경로와 cwd 해석을 직접 표시했다.
- `02-profile-map/diagram.html`: 보조 매핑 workflow. 최종 자동 근거는 `02-profile-map/review-3/`. 분기선 일부가 우회하므로 정확한 매핑 표를 해설과 함께 제공한다.
- `01-roundtrip/candidate.json`: flowchart 형태의 초안. 폭·경로 겹침 및 endpoint-side 제약을 해결하지 못해 **미전달**로 보존한다. 이후 전체 흐름을 Sequence 방식으로 재표현했다. 이 초안의 실패를 성공으로 집계하지 않는다.
- mapping의 시각 개선 시도 `review-2`는 실패했다. 검증된 이전 명세로 복원한 `review-3`의 HTML을 전달하며 남은 우회선 한계를 숨기지 않는다.

실제 브라우저 자동 검사·이미지 표본 검토·자료 hash 검증과 live 서비스 통합 시험은 별개다. 후자는 실행하지 않았다.
