# Manual PDF-text adapter — prepared, not live execution

## Observed result

- `manual_pdf.py` implements isolated preflight, ephemeral standard-pypdf page reading, one bounded nonstream model attempt, and read-only mechanical verification.
- Final synthetic suite: **107 unittest tests, 0 failures, 0 errors, 0 skipped**. Evidence: `evidence/green-final-guarded/{counts.json,output.txt,*.snapshot}`.
- Final guards observed **0 network connection attempts, 0 real-PDF read attempts**. Legacy compile/verify/publish helper hashes stayed unchanged.
- No real paper read, live model/credential resolution, live policy/state/Wiki/raw modification, collector, installation, OCR, rendering, extraction file, publication, or activation was performed by this adapter implementation task.
- All implementation/test/evidence writes are inside this `runtime/` directory. Synthetic PDF fixtures are created with PdfWriter/generic in memory, written only to temporary synthetic roots under runtime for nofollow filesystem tests, then removed. No source page-text files are produced.

## API

Import `manual_pdf.py` with importlib, under Python `-B` (or `PYTHONDONTWRITEBYTECODE=1`). Import itself reads no sources, approvals, credentials, or helpers and does not alter sys.path.

```python
ctx = manual_pdf.preflight(root=ROOT, run=RUN, vid="2609.30614v1")
# ctx contains ephemeral approved Wiki text; NEVER serialize ctx.
# preflight does not read either PDF body and performs no writes.
pages, telemetry = manual_pdf.read_pdf_pages(ctx)
# pages are ephemeral [{"page": 1, "text": "..."}, ...]; NEVER serialize them.

result = manual_pdf.compile_one(
    root=ROOT, run=RUN, vid="2609.30614v1", attempt="attempt1", timeout=2400
)
report = manual_pdf.verify_result(
    root=ROOT, run=RUN, vid="2609.30614v1", result=result
)
document = report["document"]
```

- ROOT must be exactly `/home/ainsdev/wiki/pkm-articles`; RUN must be exactly `_meta/runs/wiki/20261001T001438Z-pdf-wiki`. Only version IDs `2609.30614v1`, `2609.30824v1` are accepted.
- Normally call `compile_one` directly; it performs its own complete preflight and extraction. Calling `read_pdf_pages` first is not a required extra step.
- `verify_result` repeats approval/policy/state/hash gates and transient extraction, returns a report with document, and writes nothing. Verification must occur while the selected state item is still `queued`; it is not a post-publication reread bypass.
- `test_config` and `client_factory` are synthetic-test injection hooks only. TestConfig roots must be direct `runtime/synthetic-*` directories, never the real root; synthetic calls require a fake factory. Production factory injection is refused.

## Exact CLI

Run from `/home/ainsdev/wiki/pkm-articles`. **The following compile/verify commands are for the parent after its live gates; they were not executed here.**

```sh
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/manual_pdf.py preflight 2609.30614v1
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/manual_pdf.py compile 2609.30614v1 --attempt attempt1 --timeout 2400
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/manual_pdf.py verify 2609.30614v1 --attempt attempt1
```

Repeat explicitly for `2609.30824v1`. There is no automatic loop, batch dispatch, fallback, or retry. A deliberate second attempt uses `--attempt attempt2` and cannot be first. At most two slots including unknown started attempts; no deletion/reset/relabeling is supported. CLI exit codes: 0 preflight/transport/verifier success for that command, 1 incomplete/rejected response or failed verification, 2 local gate/storage refusal. `preflight` prints metadata only; `compile` prints completion metadata; `verify` prints report and generated document, never a PDF extract.

Synthetic test rerun (use a fresh evidence label, directory creation is exclusive):

```sh
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T001438Z-pdf-wiki/runtime/run_tests.py repeat-01
```

Hermes interpreter observed: Python 3.11.15, with existing openai/jsonschema. The only additional site path the production reader adds is exactly ROOT/`.venv-pdf-reader/lib/python3.12/site-packages`, after local approval gates; standard pypdf **6.19.0** is checked. No installer is included.

## Execution approval the parent must author

Path: `RUN/execution-approval.json`. It is NOT created by the adapter. Strict JSON parsing rejects duplicate keys and non-JSON numbers. Required fields:

```text
schema: pkm-pdf-text-run-approval/v1
approved: true
run_id: 20261001T001438Z-pdf-wiki
wiki_root: /home/ainsdev/wiki/pkm-articles
version_ids: [2609.30614v1, 2609.30824v1]  (exact order)
scope_approval_sha256: SHA256 of RUN/scope-approval.json bytes
policy_revision: pkm-html-pdf-text-knowledge/v3
contract_revision: pkm-contracts/v3
prompt_revision: wiki-compile/v3
policy_sha256: SHA256 of _meta/automation.json bytes
prompt_sha256: SHA256 of _meta/prompts/wiki-compile.md bytes
document_sha256: exact path-to-SHA256 map for all six DOCS below
instructions_path: root-relative .md path within RUN (e.g. RUN/runtime/instructions.md)
instructions_sha256: SHA256 of that file's bytes
sources: exact two-version mapping; each value has exactly:
  source_path: raw/articles/4cff5b4f10ec/arxiv-VERSION/source.pdf
  source_sha256: 64 lowercase hexadecimal digits
  source_bytes: positive integer
  metadata_path: raw/articles/4cff5b4f10ec/arxiv-VERSION/source.json
  metadata_sha256: 64 lowercase hexadecimal digits
wiki_inputs: array of {path, sha256}, no duplicates
approved_route: {base_url: http://10.10.1.244:2455/v1, api_mode: codex_responses}
provider: codex-lb
model: gpt-6-astra
reasoning_effort: xhigh
max_attempts_per_item: 2
publication_edit_freeze_confirmed: true
validated_publication_authorized: true
```

DOCS keys: `AGENTS.md`, `SCHEMA.md`, `_meta/AUTOMATION.md`, `_meta/COMPILATION.md`, `_meta/STATE-CONTRACTS.md`, `_meta/automation-contracts.schema.json`. Each governing document must contain the v3 policy identifier; the prompt must also contain the v3 contract/prompt identifiers. Historical mentions are allowed, but bound hashes must match. The local `$defs/automation` and `$defs/compilation` schemas must validate live policy/state. External `$ref`, `$dynamicRef`, and `$recursiveRef` are forbidden.

`wiki_inputs` accepts only root-relative `entities|concepts|comparisons|queries` `.md` files with simple lowercase filenames, no traversal or symlinks. Nothing is discovered or added automatically. Only their bound text is transferred; no raw, logs, conversation, configuration, or credentials. Generated Wiki links may target those approved snapshots or exactly the two future `entities/arxiv-VERSION` notes. Future fragments are not accepted until the target is an approved snapshot.

Scope approval is independently checked: exact schema/root/run/versions/model; exact recorded Korean user request/configuration/publication confirmations; seven explicit authority booleans true; persistent extraction, PDF binary transfer, images, OCR, external assets, Cron registration/activation false; no_cost_cap. A filename alone is not authority.

Actual policy must be v3, disabled, P3–P6 false, registration/activation false, both jobs disabled/unregistered with null cron IDs/readbacks, pinned no-fallback model, PDF text transfer true, unsafe transfers false. `pdf_reading` must equal exactly the approved embedded_text_only/pypdf/.venv-pdf-reader/physical_1_based object with all forbidden features false. Integer zero is not accepted as false. The selected PDF item must be `queued`, failure_count integer below 3, global safety_block=false, no unresolved state transaction. Both source metadata records/paths/hash/length commitments are validated before reading either body. A peer can already be published_draft/partial/retryable_failed while the selected item remains queued.

## Request, artifacts, and verification contract

- One request uses unchanged `runtime_client` route resolution, `max_retries=0`, model gpt-6-astra, xhigh, `store=False`, `tools=[]`, `stream=False`. Timeout is 2400 seconds maximum, cooperatively checked around I/O/extraction/request/close; not a hard process kill or a cost/token cap.
- The user payload is JSON containing source/metadata identifiers, exact pypdf page text with physical integer page numbers, approved Wiki texts, allowed links, and required unread disclosures. Source instructions are explicitly untrusted data. PDF binary bytes never enter the request.
- Only `runtime/VERSION/attemptN-record.json` and `attemptN-result.json` are written during generation. They hold immutable input identifiers/hashes, nontext PDF telemetry, attempt metadata, sanitized errors, and generated model output. No extraction/payload/body dump is saved.
- Record is exclusive/fsynced before provider resolution and starts unknown. Existing attempts bind the same approval hash. Errors never stringify SDK exceptions. Costs remain null when unknown; positive or unknown cost is nonblocking.
- Reader rejects encrypted, all-empty, invalid, hash/length-mismatched PDFs before the client. Blank physical pages remain explicitly unread and forbid full coverage. Telemetry records page count, per-page character lengths/text hashes, blank page numbers, and pypdf version, never extracted text.
- Exact output fields: title (exact source metadata title), summary, version_id, main_text_complete boolean, read_scope, unread_scope, limitations list, claims list, markdown_body. Claim fields exactly id Cxx, kind author_report|analyst_interpretation, statement, conditions, anchor page=N, quote (literal short excerpt, max 400 characters).
- Every visible occurrence of a claim ID must share a line with its unescaped canonical `^[raw/articles/4cff5b4f10ec/arxiv-VERSION/source.pdf#page=N]`. Whitespace-only quote matching is restricted to THAT physical page. Duplicate claims, wrong page, invented anchors, hidden/fenced citations, frontmatter including BOM-prefixed forms, invalid links, and model/status/error/source-hash mismatches fail.
- Model copies both exact `VISUAL_UNREAD` strings (and blank-page declarations) into unread_scope AND visible Korean body. `main_text_complete=true` requires exact full physical page coverage and no blanks; it never certifies figures, image-only text, formulas, layout, or semantic correctness.

## Evidence interpretation and remaining work

Five API/CLI tracer slices have preserved missing-feature RED and passing GREEN snapshots. The adversarial audit found and fixed six safety counterexamples (integer false equivalence, BOM frontmatter, escaped citation, uncited repeated claim); one initial test error was corrected to catch the legacy helper's distinct Rejected class. External dynamic-schema-reference rejection has separate RED/GREEN evidence. Supplemental cases that passed immediately are existing-behavior coverage, not claimed as new RED evidence. All historical logs are retained.

The parent still owns live policy/document promotion, hash-bound execution approval, queued state transition, actual model runs, semantic review, and transactional Wiki publication with collection.lock, journal, final hashes, edit freeze, and readback. A completed result is not a verified document; a passed mechanical report is not semantic approval or publication. No live readiness claim is made here. Workflow lessons are recorded in this scoped handoff rather than modifying global skills, as the task forbids skill writes.
