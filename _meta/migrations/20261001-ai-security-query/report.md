# AI Security 원본 수집 검색식 전환

## 적용 상태

- 사용자 승인: `위 쿼리 조건을 적용하여 원본 논문 수집 자동화 할 수 있도록 적용해주세요`.
- 기존 수집 Cron `4cff5b4f10ec`의 이름·프롬프트 및 `_meta/topics.json`, `_meta/COLLECTION.md`에 `ai-security-ti-abs/v1`을 적용했다.
- 승인된 쿼리의 제목/초록 필드·단어·괄호·AND/OR·문자열을 그대로 유지했다. SHA-256: `4ea7f574dbe38a7bfa6f1556d25016b404bfaffb70835a09b25c56cf35ac988c`.
- 등록 readback: enabled=true, state=scheduled. 다음 예약 **2026-10-02 00:00 KST**. 매일 KST 00:00, 최대 5개 서로 다른 버전 ID/한국 날짜, 최대 90분, HTML 우선·공식 미제공 시 동일 버전 PDF 원본 정책을 유지했다.
- 수집 모델·reasoning·스킬·workdir·local 전달·반복 설정·다음 실행은 변경하지 않았다. 새 Cron 또는 커스텀 수집기/파서/DB를 만들지 않았다.

## 실제 검증

- 정확한 쿼리의 공식 arXiv API probe: HTTP 200, 정상 Atom 5개 레코드, 고유 ID 및 updated 내림차순 확인. 전체 결과를 수집하거나 정밀도를 평가한 것은 아니다.
- 기존 pending **48편 전체**의 버전 ID를 공식 API로 확인하고 새 쿼리와 교집합 대조: **일치 16편 / 비일치 32편 / 미확인 0편**.
- 첫 48-ID 교집합 요청은 HTTP 400 `Request Line is too large (4217 > 4094)`였다. 실패 기록을 보존하고 동일 쿼리에서 ID만 최대 10개씩 5묶음으로 나눠 성공했다. 운영 계약에 ID 배치 및 request-line 제한을 반영했다.
- 기존 pending을 삭제하지 않고 현행 쿼리의 동일 버전 일치를 다운로드 전 확인하도록 등록했다. 비일치 항목은 다운로드·시도 예약에서 제외하고 pending 및 run 근거를 보존한다. 불명·전송 실패를 정상 비일치로 처리하지 않는다.
- 쿼리·일정·등록값 readback, JSON, 로컬 링크 90건, git diff --check 통과. 보호 파일 71개 및 컴파일 고정 hash 18개 불변, 과거 log prefix 보존 확인.
- 기존 원본 **17편(HTML 15/PDF 2)**, 지식 문서 **8개**, 수집/컴파일 state·checkpoint·일일 시도 기록은 유지했다. 다른 Cron 3개의 조사한 실행 설정과 전체 job ID 집합도 유지했다.

## 아직 관측하지 않은 것

- 새 프롬프트로 예약 발화한 수집 실행 및 실제 원본 다운로드는 **미관측**이다. 이번 작업의 원본 다운로드는 0편이다.
- 기존 스케줄러의 활성 heartbeat는 확인했으나 미래 실행 성공을 보증하지 않는다.
- 새 쿼리의 일치는 AI 보안 중심성의 의미 판정이 아니다. 별도 의미 분류 모델이나 기존 논문 자동 삭제는 추가하지 않았다.
- 이전 검색 범위의 checkpoint·최초 하한은 그대로다. 새 검색식으로 과거 전체를 소급 수집하지 않는다.
- 별도 KST 02:00 Wiki 컴파일 Cron `4839be6a1db1` 및 승인/프로그램/정책 hash는 변경하지 않았다.
- 독립 읽기 전용 검토는 **ship / 차단 결함 없음**으로 완료했다. 정확한 쿼리, API 응답 해시 및 pending 48편의 집합 대조, 한도·checkpoint·원본 보존, 컴파일 hash-pin 경계를 확인했다. 검토자는 live Cron readback을 직접 수행하지 않았으며 해당 근거는 부모의 registration-after.json 및 verification.json에 있다. 예약 실행은 여전히 미관측이다.

## 근거

- [승인](approval.json), [정확한 쿼리](approved-query.txt), [전환 계약](query-policy.md)
- [적용 전 설정·보호 hash](before.json), `before-files/`의 이번 변경 대상 5개 파일 복사본
- [검색 probe](probe.json), `probe-response.xml`
- [기존 pending 전수 결과](pending-validation-batched.json), `pending-id-only.json/.xml`, `pending-filter-batch-1`~`5`의 JSON/XML
- 이전 필터 실패: `pending-query-filter.json`, `pending-validation.json`, `pending-filter-diagnostic-response.txt`
- [등록 readback](registration-after.json), [최종 대조](verification.json)
- [독립 검토](independent-review.json), [소유 잠금 해제](lock-release.json)
- `collector-prompt-before.txt`, `collector-prompt.txt`

복구가 필요하면 이번 변경 전 파일과 프롬프트를 기준으로 사용자 승인 아래 조건부 복구한다. 현재 외부 편집이나 새 실행을 덮어쓰는 자동 rollback은 하지 않는다.
