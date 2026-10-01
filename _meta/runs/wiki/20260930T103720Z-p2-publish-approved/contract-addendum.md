# P2 후속 게시 승인 부속 계약

- 적용: 검증된 staging 결과 `2609.30830v1`, `2609.31358v1` 두 편만. 사용자 요청 “다음 단계 진행해주세요” 및 추가 확인 “편집 중지 확인 · 두 편 게시 승인”에 근거한다. 확인 질문·원본 snapshot은 [preflight.json](preflight.json)에 있다.
- 원 생성 run: `_meta/runs/wiki/20260930T100918Z-p2-live-staged`. 기존 `pkm-p2-run-approval/v1`의 게시 false/timeout 기록, 결과·review·원본·instructions·정책 문서를 변경하지 않는다.
- 기존 동시 생성/게시 승인 경로 `pkm-publication-request/v1`은 그대로 유지한다. 이번 후속 승인 경로 `pkm-publication-request/v2`는 기존 `approval` 해시와 별도 `publication_approval` 해시를 동시에 요구한다. 생성 결과의 `approval_ref/approval_sha256`는 기존 생성 승인을 계속 가리킨다. 과거 false를 true로 고치거나 결과 봉투를 재작성하지 않는다.
- `pkm-p2-publication-approval/v1`은 user/approved/P2, 정확한 Wiki root·생성 run·허용 version 집합·timezone 확인 시각, 요청/확인 범위, 두 게시/편집중지 true, generation approval ref, 버전별 result/review/source+metadata/output path를 결합한다. 알 수 없는 필드, 다른 버전/root/run, 입력 hash 변경은 쓰기 전에 거부한다.
- v2 권한은 후속 게시의 두 플래그만 보완한다. 생성·모델·fallback 금지·no_cost_cap·P2 범위·구조 검증·주장별 의미 검토·PDF/이미지 금지·모든 기존 무결성 gate는 유지한다. 정책 snapshot 문서의 동시 승인 설명을 소급 수정하지 않으며 이번의 명시적 후속 게시 권한을 별도 연결한다.
- 잠금 전/후에 승인과 입력을 다시 검사한다. journal approval_refs에는 원 생성 승인과 후속 게시 승인 모두, input_hashes에는 승인/요청 실물 hash를 남긴다. 기존 page→index→append-only log→receipt→state 순서·동시성·중단 복구·사용자 편집 보호·no-op 검증은 유지한다.
- 이 권한은 새 모델 호출/재생성/추가 논문/P3–P6/Cron 등록·활성화 권한이 아니다. 인간의 학술 내용 검토로 승격하지 않으며 페이지는 draft/unreviewed다.

## 구현·시험 근거

- 게시자: `_meta/runs/wiki/20260929T083140Z-p2-resume/publish-one.py` SHA-256 `d725cd82e66822e1dd60850fbad870bb39688590395b044c005c0be86ab004cc`.
- 최초 delayed-approval RED, 단일 GREEN, 기존 테스트에서 발견된 malformed-request 회귀, 최종 전체 GREEN은 각 별도 증거로 보존했다.
- [regression-tests-final.json](regression-tests-final.json): 114개 통과. 새로운 6개에는 17개 잘못된 후속 승인 subcase, 구 생성 승인 변조, 잠금 직전 변경, 중단 복구 및 반복 no-op이 포함된다. 부정 사례 추가 시험은 기존 구현 경계 확인이며 별도의 기능 RED로 주장하지 않는다.
