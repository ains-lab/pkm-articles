# v3 PDF-note plan-builder handoff (synthetic validation only)

## Files / interface

Directory: `/home/ainsdev/wiki/pkm-articles/_meta/runs/wiki/20261001T001438Z-pdf-wiki/publication-support/`

- `pdf_plan.py`: read-only `build_plan(fs, vid, run, result, report, review, now) -> plan` and `validate_plan(fs, plan, vid, run, result, report, review, now) -> context`.
- `test_pdf_plan.py`: synthetic filesystem tests; no live PDF/result reads, no provider or parser.
- `verify_synthetic.py`: same suite with machine-readable counts, source hashes, AST check, and unchanged helper/adapter before/after hashes; prints JSON without persisting files itself.
- `evidence/final-verification.json`, `evidence/final-source-snapshot.json`: final observed test results and exact source bytes/hashes.
- `evidence/*.json`: raw RED/GREEN command outcomes plus exact implementation/test source snapshots and hashes. `05-supplemental-recovery-and-conflicts.json` records recovery/negative coverage that passed on first run, **not invented RED evidence**.

Only exact root `/home/ainsdev/wiki/pkm-articles`, run `_meta/runs/wiki/20261001T001438Z-pdf-wiki`, and `2609.30614v1` / `2609.30824v1` are accepted. Tests inject only this new module's ROOT into temporary synthetic roots inside this directory; **no generic-helper constants or guards are patched**.

The module safely loads unchanged legacy `publish-one.py` as code with nofollow/symlink/regular-file checks and no bytecode cache. It reexports the requested generic helpers unchanged. It never invokes legacy v2 `inputs`, `new_plan`, `validate_plan`, `publish`, or `main`; it never imports/calls manual_pdf or a provider.

`fs` is the unchanged generic `Files(ROOT)`; `now` is an aware datetime. Both public functions read/hash inputs but **write nothing**. `validate_plan` returns exactly the generic helper context shape: `{'schema': ..., 'snapshots': ...}`. It checks the whole deterministically rebuilt plan (not only hashes) and current target classification or committed output verification.

## Exact wrapper contract (parent-owned)

For `result` and `review`, pass:

```python
{'path': root_relative_path, 'sha256': sha256(exact_persisted_bytes),
 'value': strictly_decoded_original_json_object}
```

The builder re-reads these exact paths and compares hashes and JSON values. Do not add wrapper keys into the immutable underlying result/report objects.

- result path: `RUN + '/runtime/' + vid + '/attempt1-result.json'` (also permits legitimate `attempt2`).
- mechanical report path: `RUN + '/reviews/' + vid + '-attempt1-verification.json'`.
- semantic review path: `RUN + '/reviews/' + vid + '-attempt1-agent-review.json'`.

For `report`, use the same three descriptor keys **plus**:

```python
{
 'preflight': {
   'record': fresh_ctx['record'],
   'snapshots': fresh_ctx['snapshots'],
 },
 'observed_at': aware_iso_timestamp_after_the_fresh_verify_returned,
 'observers': ['manual_pdf.preflight', 'manual_pdf.verify_result'],
}
```

`report['value']` is exactly the unmodified `manual_pdf.verify_result(...)` return. Parent must really call both functions under lock, not fabricate these fields. After persisting the initial mechanical report, re-run verifier under lock and require canonical equality with that report; a different result is HOLD, not permission to silently replace a persisted report. Pass the fresh preflight's metadata-only `record` and `snapshots`, **not its Wiki text/prompt/instructions context**. This wrapper is trusted parent evidence, not a cryptographic proof that Python called the verifier.

The builder checks `passed is True`, all mechanical check `ok is True`, document == strict JSON result text, exact policy/contract/prompt/model/route/approval/document/source commitments and every preflight input. It does not reproduce mechanical or semantic review. All embedded-text physical pages must be complete (`main_text_complete is True`); partial outputs are deliberately unsupported.

Pass `timeout=result['value']['http_timeout_s']` explicitly to the fresh `manual_pdf.preflight` call. The CLI records a float (for example `2400.0`), while the Python default is an integer (`2400`); canonical record binding deliberately preserves that difference. Do not normalize the original result or relax the validator to conceal a caller mismatch. A refused plan build before journal creation is not a publication or a new model attempt.

### Exact semantic review JSON

Parent must author this only after checking **every generated claim and the body** against actual approved PDF embedded text. No fake/human review. Required values below are descriptive placeholders, not an artifact to auto-approve:

```python
{
 'schema': 'pkm-pdf-agent-evidence-review/v1',
 'actor': 'agent',
 'reviewer': '<actual agent identity>',
 'reviewed_at': '<aware ISO timestamp>',
 'version_id': vid,
 'passed': True,
 'human_review_ref': None,
 'result_sha256': result_descriptor['sha256'],
 'mechanical_report_sha256': report_descriptor['sha256'],
 'source_sha256': result_value['source_sha256'],
 'approval_sha256': result_value['approval_sha256'],
 'policy_sha256': result_value['policy_sha256'],
 'prompt_sha256': result_value['prompt_sha256'],
 'requested_scope': 'manual PDF embedded-text complete',
 'read_scope': document['read_scope'],
 'unread_scope': document['unread_scope'],
 'evidence_scope': list_of_unique_claim_page_N_anchors,
 'reviewed_claim_ids': claim_ids_in_generated_order,
 'claims': [
   {'id': claim['id'], 'anchor': claim['anchor'],
    'quote_sha256': sha256(claim['quote'].encode('utf-8')),
    'verdict': 'supported', 'rationale': '<actual claim-specific semantic reasoning>'},
   # exactly one entry per generated claim, in generated order
 ],
}
```

Rationale must be nonempty. The whole generated result hash binds statements/conditions/quotes/body; quote hashes bind each checked excerpt. `reviewed_claim_ids` must exactly match generated order, and evidence_scope must cover all actual claim anchors. **Contextual excerpt review is sufficient for this artifact when honestly scoped:** reviewing every claim against short surrounding embedded-text excerpts is not an independent full reread. `read_scope` / `unread_scope` bind the generated document's reading disclosure; they do not claim the reviewing agent independently reread every page. Record the actual contextual support/conditions in each rationale. This is agent evidence review, **not** user/human review, visual inspection, or experimental reproduction.

## Parent's live sequence / required gates

1. Independently review this builder and rerun synthetic tests first. Both IDs must be queued before initial verification; on the second publication, peer `published_draft` is permitted. Keep all six prior knowledge pages and v2 runs/pages/receipts immutable throughout this work, including the three approved concept inputs: **no backlink edits even after both compiles finish**. New notes link outward to concepts; index provides inbound discovery. Only the execution approval's `wiki_inputs` are consumed (the parent's three concepts, not an invented six-page set).
2. Before lock and again under unchanged `collection_lock`, check collector-priority time (KST 23:55–01:35 excluded), current user approval/edit freeze, unchanged code/policy/sources/metadata/Wiki/model route, source hash **and byte count**, no unresolved other journal, and exact state. Builder is not a scheduler/lock owner or full preflight implementation. Do not use a v2 publisher entrypoint.
3. Under lock, actually run fresh `manual_pdf.preflight` and `verify_result`, check returned passed flags and the bound persisted report equality, and bind the trusted all-claims review. Target must still be `queued`; do not change to `reading`/`ready_to_publish` first because the unchanged adapter requires queued. The journal records the validated queued-to-published transaction; intermediate reading/validation evidence lives in result/report/review, not fake ledger events.
4. Ensure safe `RUN/reviews` and `RUN/publications` directories exist (caller creates explicitly). No artifacts go into `runtime/<vid>/` besides adapter record/result files: its attempt scan rejects unknown filenames.
5. Under that same lock, call `build_plan`, then `validate_plan`; call unchanged `write_journal(fs, plan)`, `apply_plan(fs, plan, context, hook, owns_lock)`, and `verify_committed(fs, plan, context, vid)`. Check lock ownership and snapshots immediately before execution. Read back the persisted envelope with strict decode and verify `plan_sha256 == sha(canonical(plan))`, then validate it before claiming success.
6. For subsequent no-op, read/verify the envelope, re-check inputs/authority/time under lock, call the **v3** `validate_plan` then generic `verify_committed`; do not call `build_plan` on an existing output, and do not call `apply_plan` for a committed plan.

Publication artifacts are `RUN/publications/<vid>-<attempt>-publish-journal.json`, `-receipt.json`, and `-verification.json`. The last is the generic helper's exact report copy; the original report in `reviews/` remains immutable. The plan has exactly five targets: new note, index, append-only log, receipt, compilation state. Journal/report files are helper-owned auxiliary artifacts, not extra Wiki/state targets.

## Snapshot / recovery details

- `context['snapshots']`, plan `input_hashes`, and receipt `actual_input_hashes` contain **all preflight immutable inputs**, both approved PDF source hashes, immutable result/report/review hashes. Only mutable compilation state is removed from invariant checks.
- Original compilation bytes are bound via `before_state`, target 5 `before_hash`, and the original parent preflight snapshot. Generic classify conditionally permits only before/after target states. Removing compilation from invariant snapshots is required: otherwise the post-state-write guard rejects the publisher's own successful write.
- Keep the original report wrapper's metadata for recovery; fresh post-write compilation snapshots must **not** replace its original before-state commitment. Recovery rechecks immutable inputs and current targets against that original plan. Do not revert a published item to queued just to get adapter preflight to run. Once state is published, fresh generation preflight is intentionally unavailable; use committed verification and independently revalidate authority/source/time, not generation reruns.
- Prepared recovery is forward-only and conditional: unexpected edits, missing/torn/duplicate log events, bad source hashes, out-of-order targets or conflicting artifacts refuse. Generic helpers preserve unrelated index sections/log appends. No destructive rollback or user-page overwrites.
- First plan's committed no-op remains valid after the peer commits: validation does not demand the old whole-state hash; generic verifier checks the exact committed item/output/receipt, actual index page count and log prefix/event.

## Output / limitations

New notes only: draft, last_reviewed=null, review_state=unreviewed, revision='1'; summary is the generated document summary, with source_hashes and agent_review_ref. Generated Markdown body is appended **byte-for-byte in UTF-8**, including trailing whitespace/newlines; no claim/provenance edits or backlink rewrites. No original source.json/raw/collector/policy edits.

Caller is responsible for real preflight, real verifier, genuine semantic review, collection-priority time, resolving any unrelated journal, accurate source lengths and authority freshness, lock/edit-freeze discipline. A noncooperating editor can still race filesystem checks; unchanged helpers require cooperative locking. Passing synthetic tests is not live execution/publication authorization or proof of scientific correctness. No OCR/rendering/parser install/PDF text persistence/provider call/Cron/new collector/automatic publisher exists here.

Run tests:

```text
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20261001T001438Z-pdf-wiki/publication-support/test_pdf_plan.py
```
