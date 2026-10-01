# Content lane handoff — hardened, synthetic verification complete

## Scope and outcome

Audited `INTERFACE.md`, `implementation-approval.json`, current `content.py` and unchanged legacy helpers. Modified only `runtime/content.py`, `runtime/test_content.py`, this handoff, and new labels under `runtime/content-evidence/`. No changes to daily/publication/common, legacy helpers, live policy/state/raw/Wiki, Cron, installations or credentials. No real paper body reads, model execution or publication. Parent owns integration and any later approval gates.

Seven observed RED→GREEN slices, each with identical test snapshot hashes across its pair:

- `11-pdf-coverage`: complete PDF declarations must match the exact observed physical page token set, not a subset; duplicate scopes remain invalid. All nonempty physical pages are required, conservatively including appendices.
- `12-claim-occurrences`: every visible line mentioning a claim ID needs that claim's citation. A citation on another occurrence's line cannot license an uncited repeat; escaped citation punctuation fails closed.
- `13-link-contract`: reject residual bracket/reference/malformed link syntax after allowlisted Wiki/simple inline/caret forms. Valid source links and committed Wiki links still pass.
- `14-bom`: a BOM cannot conceal YAML/TOML frontmatter.
- `15-transport`: dispatch exceptions, including connection reset and review failures, are `unknown`, never automatically retryable. Construction failures before dispatch remain `retryable_failed`, except the legacy runtime's local `Rejected` (including runtime-route mismatch), which is `blocked_policy`. No exception messages/bodies are persisted. The older ConnectionError retry expectation was explicitly superseded in this slice; historical evidence was retained.
- `16-partial-telemetry`: PDF failure after observed pages preserves `result.telemetry.read_scope`, `pages`, character lengths/hashes, `page_count`, `requested_pages` and `unread_pages`; `required_unread_scope` now discloses failed/unattempted pages, or unknown page extent. Blank pages retain their distinct disclosure. No model call follows incomplete extraction.
- `19-blank-link`: blank/whitespace inline labels cannot bypass helper target validation.

`17-supplemental-regressions` adds first-pass existing-behavior coverage, not manufactured RED: production fake injection refusal before IO; source drift; actual synthetic snapshot drift at each source/factory/request guard checkpoint; wrong generation/review response model/status/error/incomplete fields; duplicate JSON keys and claim IDs; false/nonboolean completeness; forged pass/authority; incorrect quote hashes; unsupported/uncertain semantic decisions; unknown close failures. Synthetic filesystem writes stay under `runtime/synthetic-*`; fixtures are cleaned up.

## Stable interface

- Return `{status, result, report, review, artifacts}` unchanged. No bulk schema/key changes.
- Result: `pkm-p3-content-result/v1`, flat source/metadata/policy/prompt/approval pins, `document`, exact route/model pins, observed response metadata, `telemetry`, nullable cost (`no_cost_cap`). Report document is the same candidate.
- Report: `pkm-p3-verification/v1`, `{check,ok}` entries, result hash. Adds `pdf_read_scope_complete` only for PDF.
- Review: `pkm-p3-agent-review/v1`, claim IDs plus per-claim verdict/rationale/quote hash, body verdict/support/rationale, completeness/rationale, `human_review_ref:null`, bound result/report hashes. Supported/pass fields derive from a separately received validated decision, not quote substring matching.
- Artifacts stay `<artifact_prefix>-result.json`, `-report.json`, `-review.json`, with `{path,sha256}` descriptors and exact readback.
- Factory and Responses pins unchanged: `approved_route`, bounded timeout, `max_retries=0`; `store=False`, `tools=[]`, `stream=False`, exact model/reasoning. HTML remains direct original text with the existing navigation helper, no new parser. PDF uses installed standard pypdf embedded text in memory, no binary/images/OCR/assets.
- Existing `sample-bundle-v1.json` is retained as historical schema/interoperability evidence. Its removed synthetic root is not a publishable artifact location.

## Exact verification

Final captured invocation, from `/home/ainsdev/wiki/pkm-articles`:

```text
python3 -B _meta/runs/wiki/20261001T023617Z-p3-runtime/runtime/content-evidence/run_tests.py 19-blank-link-green
```

The runner executed `/usr/bin/python3 -B -m unittest -v test_content` in this run's `runtime/`:

```text
Ran 23 tests in 3.289s

OK
```

Return code 0. Exact stdout/stderr, code/test/common snapshots and hashes are under `19-blank-link-green/`. `20-final-audit/verification.json` checks all seven RED exit=1/GREEN exit=0 pairs and unchanged paired test hashes. Baseline `10-hardening-baseline/` and all earlier evidence were preserved. Diff whitespace checks emitted no diagnostics (`git diff --no-index --check` exits 1 because files differ).

Final SHA-256:
- `content.py`: `ddd89bc0d19b92bf6e8c457c0c70f3d654ad8517ff5e69e0e67880a9ccf1cd95`
- `test_content.py`: `58f702d5c5b9886a6ea2caa5ace575ee7df17b7cc428368c575dd1fedbd13078`

## Parent integration and limitations

- Parent should record partial scope from **`bundle['result']['telemetry']`**, not a missing generated document: read_scope/unread_pages/page_count/pages are observed extraction metadata, not model or scientific reading proof. No new extracted-text artifact is needed.
- Per-page text availability and a separate model verdict cannot prove comprehension, scientific correctness, experimental reproduction, human review or visual coverage. HTML anchor coverage still relies on the existing helper plus semantic review; no new HTML completeness parser was introduced.
- Markdown validation intentionally accepts a restricted grammar, not full CommonMark. Bare bracket prose, reference links, titled/complex links and escaped link punctuation may be conservatively rejected. Citation occurrence checking is per visible line; multiple occurrences on one line share the line's citation requirement. Semantic assertions without IDs still depend on the separate whole-body reviewer.
- Tests use fake generation/review responses and synthetic pypdf documents/faults. They prove control flow, binding and rejection, not real provider behavior or model quality. Parent's actual guard implementation and full daily/publication integration were not changed or reverified by this lane.
- Dispatch exceptions conservatively become unknown even where an upstream status might ultimately prove non-execution. No automatic retry inference from transport failure. Pre-dispatch classification relies on the pinned factory's no-request construction contract and its actual `Rejected` type.
- Cooperative deadline, guard or unexpected exception paths can abort before durable coverage output; this patch does not redesign cancellation/timeout cleanup or guarantee partial telemetry after every possible abort. Recorded partial extraction failures are distinct from those aborted paths.
