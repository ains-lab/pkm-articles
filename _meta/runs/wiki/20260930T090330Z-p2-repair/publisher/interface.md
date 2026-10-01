# Publisher handoff (synthetic fixtures only)

## Current verification status

- Previous vertical slice `green-03.txt`: 25 tests OK (journal/recovery/no-op/locks, schema, costs non-gating, sequential index insertion).
- `red-04.txt`: real sibling verifier integration and journal ordering passed; four newly introduced regressions reproduced.
- Those four implementations are patched. Latest current-source run (`latest-validation.json/.txt`): 35 tests, 2 failures + 25 errors. Every reported cause is the canonical `reserved_usd=null` versus numeric-only schema conflict. Do NOT call this final GREEN. Parent must correct the schema owned by parent and rerun.
- Root ancestor replacement regression has independent RED/GREEN evidence (`red-05-root.txt`, `green-05-root.txt`).
- `protected-verification.json`: all 37 parent-preflight protected files unchanged, live knowledge pages 0, Python AST parse passed.

## Required parent action

`_meta/STATE-CONTRACTS.md` prescribes reserved_usd=null in v2. Both compilation/research_review cost_events schemas still reject null. Publisher now records cost telemetry per that normative contract; schema validation blocks BEFORE journal/page writes rather than weakening schema. Correct those canonical definitions in the parent's scope; preserve historical numeric events if needed. Then rerun:

```sh
/home/ainsdev/.hermes/hermes-agent/venv/bin/python -B _meta/runs/wiki/20260929T083140Z-p2-resume/test_publish_one.py -v
```

Protected AGENTS approval timeout remains an independent live gate. No protected-edit retry/bypass was attempted.

## Entrypoints / artifacts

- CLI: `publish-one.py VID --root ROOT --run _meta/runs/wiki/RUN --attempt attempt1-result.json`.
- `--run` is root-relative `_meta/runs/wiki/<single-run-id>`. `--attempt` is a basename ending `-result.json` (not the verifier CLI's attempt prefix).
- API: `publish(root, vid, run, attempt, *, _hook=None, _now=None)`; failure injection/time override are internal Python-only test inputs, never environment/CLI flags.
- Request: `<run>/<VID>/attempt1-publication-request.json`.
- Outputs: `attempt1-publish-journal.json`, `attempt1-publish-verification.json`, `attempt1-receipt.json`; page `entities/arxiv-<VID>.md`.
- Sibling verifier interface: import-safe `verify_result(root, vid, result) -> {passed, checks, document}`. Fresh calls before/inside collection.lock; existing verify-report.json never trusted.
- CLI returns structured JSON; successful status published_draft/noop/skipped_busy. Rejection exits nonzero with blocked_conflict (no assertion traceback).

## Exact publication request keys

`schema` = `pkm-publication-request/v1`; `version_id`; `requested_scope` = `P2 main-text complete`; `result`={path,sha256}; `approval`={path,sha256}; `policy`={path,sha256,revision}; `prompt`={path,sha256,revision}; `source`={path,sha256,metadata_path,metadata_sha256}; `output_path`; `agent_review`={path,sha256}; `consumed_wiki_refs`=[{path,sha256,revision}]. Unknown request keys rejected. All file refs root-relative, non-symlink, hash-bound.

- result path must be the selected attempt; output path must be the derived VID page.
- policy `_meta/automation.json` / pkm-html-knowledge/v2; prompt `_meta/prompts/wiki-compile.md` / wiki-compile/v2.
- source `raw/articles/4cff5b4f10ec/arxiv-VID/source.html` and sibling source.json; source/state/result bytes/hash/version agree.
- approval must be fresh for this run: `schema=pkm-p2-resume-approval/v1`, matching run_id, VID in versions; actual user_request/confirmation/confirmation_scope; publication_edit_freeze_confirmed=true; validated_draft_publication_authorized=true; pinned model, fallback false, PDF/images/assets false, no_cost_cap; prior_approval_ref to the original P2 cost-waiver execution approval.
- automation.approval_amendment_ref is snapshotted only as cost-policy amendment. Repair approval does NOT grant live execution/publication.

## Exact semantic-review keys

`schema`=`pkm-agent-evidence-review/v1`; actor=`agent`; reviewer (nonempty); reviewed_at (timezone-aware ISO); version_id; result_sha256; source_sha256; requested_scope; read_scope; unread_scope; evidence_scope (set of all original claim anchors); reviewed_claim_ids (all IDs in document order); claims in the same order with EXACT keys `{id, anchor, quote_sha256, verdict:'supported', rationale:nonempty}`. Quote SHA-256 is UTF-8 of the exact document claim.quote string. Read/unread arrays and result/source hashes must exactly bind the reviewed attempt.

The parent MUST author this review/request only after actual claim/condition/evidence-scope semantic checking. It cannot be copied from a model's boolean or structural passed=true. The publisher proves bindings/coverage, not the truth of the agent rationale. Agent review never becomes human review: page status=draft, review_state=unreviewed, last_reviewed=null.

## Producer result metadata

Required provider/model/response_model/reasoning_effort (codex-lb/gpt-6-astra/gpt-6-astra/xhigh); completed=true, response_status=completed, error=null; text is verifier-compatible complete JSON document; policy_revision/sha256, prompt_revision/sha256, instructions_sha256; source_sha256/bytes, metadata_sha256; approval_ref/sha256; route_base_url/api_mode. Cost_usd null or observed nonnegative numeric is telemetry, never compared to any cap. Verification document requires read/unread scopes, limitations, claims with id/kind/statement/conditions/anchor/quote and rendered source citations (see sibling verifier tests).

## Recovery boundary

Journal embeds exact proposed knowledge bytes, input snapshots, before/after hashes, index-owned Entities/count components, log prefix length/hash and complete event, candidate schema-validated state and receipt. Order is page/index/log append/receipt/state with fsync and directory fsync. Atomic no-clobber page creation; no prior page is overwritten. Unexpected old/new values stop with evidence retained; no rollback or whole index/log restore. Unrelated non-Entities index sections and log suffix appends survive recovery; concurrent changes to the owned Entities section/count cause a conservative conflict. Missing/tampered committed output is never no-op. Other unresolved journals block new work.
