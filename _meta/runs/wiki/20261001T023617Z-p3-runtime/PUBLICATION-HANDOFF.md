# P3 publication lane — integration contract (implementation progressing)

`publish(ctx,bundle,*,now=None,hook=None)` is implemented with unchanged generic safe IO/WAL helpers. HTML happy path, interrupted-page recovery, all-claims/body review checks and result bindings have observed RED/GREEN evidence. More adversarial/priority coverage in progress. No live publication.

## Actual content compatibility (supersedes initial proposed envelope)

Publisher now follows content.py's actual output rather than the first draft specimen:
- Bundle `{status,result,report,review,artifacts}`, `status=ready_to_publish`.
- Descriptors EXACT `{path,sha256}` for `<artifact_prefix>-result.json`, `-report.json`, `-review.json`.
- Result `schema=pkm-p3-content-result/v1`, `document`, complete source/metadata pins, policy/contract/prompt revisions + hashes, approval ref/hash, version, requested_scope, pinned flat provider/model/reasoning_effort/fallback_allowed, `route` (not approved_route), consumed_wiki=[{path,sha256}], cost_policy=no_cost_cap, completed=true, response_status=completed, response_model exact, error=null. Optional observed usage/cost/telemetry allowed.
- Report `schema=pkm-p3-verification/v1`, passed=true, nonempty checks all ok=true, same document, result_sha256.
- Review `schema=pkm-p3-agent-review/v1`, passed=true, human_review_ref=null, result_sha256/report_sha256, response_model exact + response_status=completed, claim_ids equal all ordered generated IDs, claims=[{id,quote_sha256,verdict:supported,rationale}], body_verdict=supported, body_supported=true, body_rationale nonempty, main_text_complete=true, coverage_rationale nonempty. Claim records may be reordered but IDs must match exactly. Hashes bind entire generated body via result, not merely short quotes.
- Claim anchor/read_scope use original HTML anchor token / PDF page=N, while visible citations use source_path#anchor. This matches existing content implementation.

## Parent contract / recovery

Parent owns daily generation lock and `ctx.guard`; publisher takes collection.lock, checks safe descriptor readbacks and snapshots at every transaction stage. `ctx.guard` must permit the exact item's owned transition through ready/published during recovery and final stage; it must not require the original global state byte hash after publication. Snapshot compilation/index/log excluded.

New immutable `<prefix>-publication-basis.json` freezes before-state/index/log/count/time and original evidence hashes. Parent should treat it as protected per-attempt evidence. WAL is reconstructed from this independent basis + currently hash-checked result/report/review, not supplied plan fields. All targets classified before recovery. Generic helpers remain untouched; custom committed verifier permits enabled=True, later unrelated state/index/log changes, but rejects edits to this item's output/state/receipt/owned cost event.

Publisher output `{status,work_key,output_refs,receipt_ref,journal_path}`. Status published_draft/noop/skipped_busy. Additional artifact suffixes: -publish-journal.json, -publish-verification.json, -receipt.json, -publication-basis.json. New entity only `entities/arxiv-<version-id>.md`.

Final exact test counts/evidence and limitations pending; parent can inspect publisher-evidence slice results. No model/network/real source bodies/installations/live state changes performed.
