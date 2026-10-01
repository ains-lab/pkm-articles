# Compiler repair handoff — synthetic/mock execution only

## CLI

Both entrypoints use the same engine in `20260929T083140Z-p2-resume/compile-one.py`.

```text
<python> _meta/runs/wiki/20260929T083140Z-p2-resume/compile-one.py VID LABEL --root ABS_ROOT --run _meta/runs/wiki/NEW_RUN --instructions ROOT_RELATIVE_FILE [--timeout SECONDS]
<python> _meta/runs/wiki/20260930T082000Z-p2-nonstream/compile-one-nostream.py VID LABEL --root ABS_ROOT --run _meta/runs/wiki/NEW_RUN --instructions ROOT_RELATIVE_FILE [--timeout SECONDS]
```

`--attempt LABEL` replaces positional LABEL (not both). LABEL is a prefix, not a result filename. No implicit root/run/attempt/instruction defaults. Root must be absolute and equal automation.wiki_root. Timeout defaults to 2400, finite `0 < seconds <= 2700`. Nonstream retains VID LABEL positional compatibility. Use the installed Hermes venv for future authorized real execution; stdlib-only mock tests also run with python3. No real provider imports happen on import/preflight rejection.

Exit codes: 0 accepted completed model response; 1 invalid/failed/timed-out response; 2 preflight/storage refusal. This is generation acceptance, NOT semantic verification or publication.

The parent is updating compile-instructions.txt to the verifier's `statement`, `conditions`/`condition`, and top-level `limitations` keys. This child did not edit that instruction file. The synthetic compiler-to-real-verifier integration test uses those canonical keys and passes.

## Approval contract (never auto-created by compiler)

Pre-create a **new operator-approved run directory**, containing only `approval.json` and optionally the selected instruction file if directly within that directory. Existing historical runs or runs containing old attempts are refused. Approval is a local operator-authored trust artifact; booleans alone do not establish that the human actually approved it. No live approval was created by this repair.

Required `RUN/approval.json` fields:

```json
{
  "schema": "pkm-p2-run-approval/v1",
  "actor": "user",
  "approved": true,
  "phase": "P2",
  "scope": "manual-html-direct-compile",
  "run_id": "NEW_RUN",
  "wiki_root": "ABS_ROOT",
  "fresh_run": true,
  "operator_reviewed_prior_attempts": true,
  "version_ids": ["2609.30830v1", "2609.31358v1"],
  "provider": "codex-lb",
  "model": "gpt-6-astra",
  "reasoning_effort": "xhigh",
  "max_attempts_per_item": 2,
  "approved_route": {"base_url": "EXACT_APPROVED_NONSECRET_URL", "api_mode": "responses OR codex_responses"},
  "policy_revision": "pkm-html-knowledge/v2",
  "policy_sha256": "SHA256_OF__meta/automation.json",
  "prompt_revision": "wiki-compile/v2",
  "prompt_sha256": "SHA256_OF__meta/prompts/wiki-compile.md",
  "instructions_path": "ROOT_RELATIVE_FILE",
  "instructions_sha256": "SHA256_OF_EXACT_INSTRUCTION_BYTES",
  "document_sha256": {
    "AGENTS.md": "SHA256",
    "SCHEMA.md": "SHA256",
    "_meta/AUTOMATION.md": "SHA256",
    "_meta/STATE-CONTRACTS.md": "SHA256",
    "_meta/COMPILATION.md": "SHA256",
    "_meta/automation-contracts.schema.json": "SHA256"
  },
  "sources": {
    "SELECTED_VERSION_ID": {"source_sha256": "SHA256", "source_bytes": 1, "metadata_sha256": "SHA256"}
  },
  "confirmation": "Nonempty exact operator confirmation/reference"
}
```

Place an entry for each version to be executed in `sources`; each invocation requires its exact selected-version entry. Hash placeholders are not executable approvals. `document_sha256` has exactly the six named keys. The URL must have http/https scheme and hostname, no username/password/query/fragment. Actual lazy runtime resolution must return requested_provider=codex-lb, provider=custom (installed Hermes named-custom-provider representation), model=gpt-6-astra, exact approved base_url/api_mode, no request_overrides. SDK is constructed with max_retries=0 and finite timeout. No fallback or automatic retry exists.

Preflight validates actual governing document revisions and known active-denial clauses, current policy/model/transfer/prompt/state/P2/safety pins, unresolved transactions, approval/hash bindings, metadata identity/hash, original HTML hash/length, no symlink/path escape, fresh scope and available attempt. Invalid live AGENTS v1 blocks before source body or client factory. Source is decoded strictly UTF-8 and sent exactly as input_text (scripts/styles/CRLF retained); no normalization, chunks, saved extraction, PDF, assets, or tools.

## Immutable output contract

`RUN/.compile-scope.json` binds the approval SHA-256. A short-lived atomic `.compile-reservation-lock/` serializes reservations; never stolen. Under `RUN/VID/`, `LABEL-reserved/` permanently consumes a slot, `LABEL-record.json` is exclusive/fsynced before the factory, and `LABEL-result.json` is exclusive/fsynced after processing. Any existing label record/result/reservation/model-output is refused, not reused. Maximum two labels/item/run. Start-only or reserved-only unknown outcomes are retained and count; no synthetic cancellation or zero cost is inferred. Results contain output text; no duplicate model-output file is generated.

Start schema: `pkm-p2-attempt/v4`. Result schema: `pkm-p2-attempt-result/v4`.

Common provenance: vid, run_id, attempt, provider, model, reasoning_effort, policy_revision/policy_sha256, prompt_revision/prompt_sha256, instructions_sha256, source_path/source_sha256/source_bytes, metadata_path/metadata_sha256, approval_ref/approval_sha256, route_base_url/api_mode, http_timeout_s, transport. Start adds started_at, outcome=unknown and null response_model/response_status/incomplete_details/usage/cost_usd.

Result adds finished_at, completed, error, elapsed_seconds, event_count, first_event_s, response_status, response_model, incomplete_details, response_error, text, usage, cost_usd, cost_status. Success requires exact response status=completed AND exact actual model=gpt-6-astra AND no incomplete_details/response error AND nonempty output text AND no transport/cleanup failure. Stream mode requires a clean terminal completed event with no failed/incomplete/error/duplicate terminal and no later stream failure. Both streams and clients close in finally.

Errors store bounded allowlisted type, numeric HTTP status if available, and local category code; never raw repr/message/headers/body. Incomplete reason is retained only for max_output_tokens/content_filter, otherwise a presence flag. Usage preserves input/output/total token counts and cached/reasoning-token details only. Known nonnegative finite response.cost_usd is retained; unknown remains null/unobserved_not_zero. Neither positive nor unknown cost gates execution.

## Evidence and limitations

Test file: `_meta/runs/wiki/20260929T083140Z-p2-resume/test_compile_one.py`.
Evidence: this directory's `01-red.json`/`01-green.json` through `06-red.json`/`06-green.json`, plus `04-red-valid.json` (corrected synthetic resolver test setup), and `final-installed-venv.json`. Raw subprocess commands, exit codes, stdout/stderr and later test/file hashes are retained. Initial RED tests cover import-time auth/SDK execution; later REDs cover missing positive path, stream support/cleanup, stale documents/freshness/runtime pins, source reread/exclusive writer/incomplete telemetry, and pre-request deadline. Regressions that already passed when added are supplemental coverage, not fabricated RED evidence.

No live paper body, credential read, provider/model call, PDF/assets, policy/AGENTS edit, compilation-state write, index/log write, or publication occurred. Live-root negative test reads governing policy files only and confirms no source read/client invocation/new run directory. Existing prior attempt outputs were not written. Parent should independently rerun the tests and validate actual operator approval before any future real operation. Local approval metadata is not cryptographic human authentication; no provider network behavior was exercised.
