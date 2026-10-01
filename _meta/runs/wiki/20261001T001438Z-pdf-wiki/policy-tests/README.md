# PDF 텍스트 정책 v3 준비 인계 — 부분 준비 / 게시 HOLD

## 결과

- 정책 `pkm-html-pdf-text-knowledge/v3`, 계약 `pkm-contracts/v3`, 프롬프트 `wiki-compile/v3` / `research-review/v3`를 staging에 준비했다. 운영 root에 게시하지 않았다.
- 요청 14개 중 **13개**를 준비했다. **`policy-staging/AGENTS.md`는 보호 파일 승인창 시간초과로 미작성**이다. 같은 편집 재시도나 다른 경로/도구 우회를 하지 않았다. 새 명시적 보호 편집 승인 없이 진행하지 않는다. 이 blocker 해결 전 전체 정책 적용 완료로 표시하면 안 된다.
- 두 PDF의 status/reason만 `blocked_approval` / `pdf_text_policy_eligible_pending_execution_gate`로 변경했다. 나머지 18개 item과 기존 성공 항목/receipt/transaction/비용·실패 이력은 보존했다. PDF에 페이지·읽기·attempt 필드를 추가하지 않았다. queued 전이와 실제 실행 gate는 부모 담당이다.
- automation.pdf_reading은 부모가 지정한 정확한 const 객체다. `transfer.pdf_content=true`는 PDF 텍스트만 허용하며 바이너리/이미지/OCR/외부 자산/지속 추출은 금지한다. HTML 요청은 PDF 분석 권한을 얻지 않는다.
- P3–P6 false, 전역/job enabled=false, cron_id=null, 등록/활성화 false, no_cost_cap와 미관측 비용 null을 유지했다. legacy P2-v2 코드/가드는 수정하지 않았다.

## 정확한 경로

Run root:
`/home/ainsdev/wiki/pkm-articles/_meta/runs/wiki/20261001T001438Z-pdf-wiki`

Staging root:
`/home/ainsdev/wiki/pkm-articles/_meta/runs/wiki/20261001T001438Z-pdf-wiki/policy-staging`

준비된 상대 경로:

- `SCHEMA.md`
- `README.md`
- `_meta/AUTOMATION.md`
- `_meta/COMPILATION.md`
- `_meta/STATE-CONTRACTS.md`
- `_meta/automation.json`
- `_meta/automation-contracts.schema.json`
- `_meta/prompts/wiki-compile.md`
- `_meta/prompts/research-review.md`
- `_meta/state/compilation.json`
- `_meta/state/feedback.json`
- `_meta/state/research-review.json`
- `_meta/P3-PREPARATION.md`

미작성: `AGENTS.md` — 보호 승인 시간초과. 대체 파일에 같은 편집을 기록하지 않았다.

Tests root:
`/home/ainsdev/wiki/pkm-articles/_meta/runs/wiki/20261001T001438Z-pdf-wiki/policy-tests`

- `verification.json`: 전체 manifest, before/staged 해시, live before-image 15개 불변 대조, 항목별 보존, blocker.
- `staged-policy.diff`: before 대비 13개 준비본의 전체 diff.
- `red-initial.txt` / `red-initial.json`: 기존 v2 스키마가 합법적인 v3 PDF 텍스트 요청을 거부한 최초 RED(1 test, 실패 1, exit 1).
- `test_contracts_initial.py.snapshot`: 최초 RED 시험 원본. `green-initial.json`의 test hash와 같다.
- `green-initial.txt` / `green-initial.json`: 동일 시험의 최초 GREEN(1 test, exit 0).
- `green-matrix-initial.txt` / `green-matrix-initial.json`: 첫 확장 회귀(133 tests, 실패/오류 0). imported base test의 중복 discovery 1개를 제거한 결과가 최종본이다.
- `green-final.txt` / `green-final.json`: 최종 **132 tests, 실패 0, 오류 0, skip 0**, exit 0.
- `test_contracts.py`, `test_migration.py`: 재현 가능한 합성/메타데이터 시험.

## 재현 방법

```bash
cd /home/ainsdev/wiki/pkm-articles
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B -m unittest discover -s _meta/runs/wiki/20261001T001438Z-pdf-wiki/policy-tests -p 'test_*.py' -v
```

설치된 Hermes venv의 jsonschema 4.26.0을 사용했으며 패키지 설치는 하지 않았다. 실제 테스트 범위는 v3 JSON Schema 검사, 합법적인 HTML/PDF 요청, 바이너리/이미지/OCR/지속추출·변형 reader·모델/fallback·승인 누락·경로/해시·알 수 없는 입력 거부, 4개 v3 인스턴스, ledger 보존, frozen v2 스키마의 원래 4개 인스턴스 수용, 문서/프롬프트 경계다. 실제 페이지 인용·텍스트 길이·추출 품질의 진실성은 부모 실행 단계의 의미 검증이다.

## 반복 가능한 준비 절차와 제한

1. scope 승인 및 SCHEMA → index → 최근 log를 읽는다. 원문/모델 결과는 읽지 않는다.
2. before의 정책·메타데이터에서 준비한다. 기존 v2 run/page/receipt를 재작성하지 않는다.
3. 합성 요청으로 RED를 남긴 뒤 v3 branch와 정확한 pdf_reading const를 추가하고 동일 테스트의 GREEN을 남긴다. 확장 부정 시험은 최초부터 통과한 회귀로 구분한다.
4. outer state revision만 이관하며 지정 PDF의 status/reason 외 item 변경을 금지한다. 자동화 및 수집 경계를 유지한다.
5. before와 live 정책/상태/index/log를 바이트 해시 대조하고 준비된 파일 수/누락을 코드로 계산한다. hash 검사에 원본 PDF나 모델 결과를 포함하지 않는다.
6. 보호 파일 승인 실패는 HOLD로 남기며 우회하지 않는다. 부모는 승인 재확인 후 남은 정책 편집, 실행 gate, bounded manual v3 처리, 의미 검토, 게시·index/log를 별도로 담당한다.

논문 body/모델 결과 읽기·provider 호출·실제 PDF 추출·설치·legacy runtime 시험·지식 게시·수집기/Cron 변경·전역 스킬 편집은 이 작업에서 수행하지 않았다. 부모의 표준 pypdf와 안전 IO/runtime helper를 재사용하는 한정된 수동 v3 adapter는 별도 실행이며, 이 정책/스키마 검증을 자동화 준비 완료나 실제 PDF 컴파일 성공으로 사용할 수 없다.
