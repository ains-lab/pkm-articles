# P3 implementation interface — synthetic verification, live disabled

Scope: user approved the next implementation/test step, NOT real paper reads, calls, writes, or Cron registration. Read implementation-approval.json. Preserve all live policy/state/raw/Wiki and legacy code. No new collector/parser/DB, no installs. New code only under this run/runtime; use existing legacy helpers or standard pypdf. Python stdlib plus installed Hermes venv jsonschema/openai and existing isolated pypdf.

## Modules / ownership
- parent: `runtime/p3_common.py`, `runtime/daily.py`, integration tests, run reports.
- content lane: `runtime/content.py`, `runtime/test_content.py`, content evidence/HANDOFF.
- publisher lane: `runtime/publication.py`, `runtime/test_publication.py`, publisher evidence/HANDOFF.
Do not edit another lane's files, live files, or legacy helpers. No commits.

## Shared common API (parent supplies)
`p3_common.ROOT` fixed live Wiki Path; `p3_common.RUN` this implementation run path. `helper('publish'|'compile'|'verify')` loads unchanged legacy helper modules (code only; no entrypoint). `require(ok, code)` raises ValueError; `sha(bytes)`, `canonical(obj)`, `encoded(obj)`, `decode(bytes)` are legacy safe JSON functions exposed by wrappers. `POLICY`, `CONTRACT`, `PROMPT_REV`, `MODEL` (= provider/model/reasoning_effort/fallback_allowed), `ROUTE` (= approved base_url/api_mode), `SCOPE`='P3 main-text complete', `STATE`='_meta/state/compilation.json'. `ensure_dirs(fs,path)` creates contained directory without symlinks via existing compile helper. `check_deadline(deadline,clock)` cooperative expiry.

## Context contract
The parent supplies a dictionary `ctx` after its preflight/reservation. Keys:
- `root`: Path, `fs`: legacy Files(root), `run`: `_meta/runs/wiki/<run-id>`, `item`: schema-valid compilation item, `metadata`: parsed source.json, `auto`: validated automation config, `schema`: state schema, `synthetic`: bool.
- `snapshots`: dict path->sha256 including approval, policy, governing docs, prompt, source, metadata and consumed Wiki. NOT compilation state/index/log (they change transactionally).
- `approval_ref`, `approval_sha256`, `policy_sha256`, `prompt_sha256`, `prompt` (text), `model` and `route` exact pins, `requested_scope`=SCOPE.
- `wiki`: [{path,sha256,text}] for consumed committed knowledge (no unresolved pages). Allowed links only to these, never fabricated future papers.
- `artifact_prefix`: `<run>/items/<version-id>/attempt1` (or attempt2). Parent makes directory and exclusive `-reservation.json` before processing. Result/review/report paths MUST use this prefix.
- `guard`: callable -> None; rechecks current authority, snapshots, source integrity, source/item identity and that no conflicts have appeared. Must be called before body read and each client construction/request/publication stage. Parent owns its implementation. Code-only tests inject a guard but tests confined synthetic roots; no production fake clients.

## Content API
`process(ctx, *, client_factory=None, pdf_module=None, deadline=None, clock=time.monotonic)`:
- Read HTML via safe IO and reuse legacy AnchorText; standard pypdf for PDF embedded text in memory. NO full extract/request persistence/logging, OCR/assets/images. No custom parser.
- Generate Korean note with claim IDs, exact short quotes (<=400 chars), page/anchor citations, title/version/scope, unread visuals and uncertainty. Verify mechanically using existing helper utilities (legacy entrypoint may not be used as v3 preflight).
- Separate same pinned model semantic review of every claim + generated body against evidence/context; don't forge review from substring match or booleans. Unknown cost null/no cap. max_retries=0, store=False, tools=[], stream=False. Both factory and pdf_module injection only for synthetic roots under this run/runtime/synthetic-*.
- Return `{status, result, report, review, artifacts}`. status `ready_to_publish` only with complete verified text and supported separate review; otherwise `partial`, `retryable_failed`, `blocked_policy`, `blocked_review`, `unknown` as appropriate. Persist bounded result/report/review under prefix with exact hashes; never raw source bodies or request dump. `artifacts` maps `result`, `report`, `review` to `{path,sha256}`. Generation `result` includes document (same document as report), source/metadata/policy/prompt/approval pins, actual model and optional usage/cost; report schema `pkm-p3-verification/v1`, passed bool, checks, document; review schema `pkm-p3-agent-review/v1`, passed bool, human_review_ref=null, all claim IDs and per-claim verdict/rationale/quote hash, result/report hashes.
- `document`: title, summary, version_id, main_text_complete bool, read_scope/unread_scope/limitations lists, claims [{id,kind,statement,conditions,anchor,quote}], markdown_body. Use source path's #anchor (HTML) or #page=N (PDF). No frontmatter in body. Generated result cannot grant authority.
- Tests run with synthetic HTML, synthetic PDF, fake generation/review client only; verify outgoing pins and absence of binary/images. Do not call live SDK.

## Publication API
`publish(ctx, bundle, *, now=None, hook=None)` -> `{status, work_key, output_refs, receipt_ref, journal_path}`. status published_draft/noop/skipped_busy or raises fail-closed ValueError. `now` aware UTC; hook can inject failures at shared helper stages.
- Verify descriptors from fs; do not trust bundle booleans alone. Require complete document and bound mechanical + semantic reviews, all supported, exact current approval/policy/source snapshot. Call ctx.guard.
- Parent holds exclusive daily run lock through whole run; publisher takes collection.lock only briefly. No priority window publishes, busy returns skipped_busy, ownership rechecks; no stealing.
- Parent compilation item's state is reading or ready_to_publish; publication creates one new entity, links existing concepts only, never modifies existing pages. Current state enabled may be True (scheduled mode), unlike legacy P2. Build separate P3 plan using UNCHANGED generic Files/collection_lock/index_parts/page_count/write_journal/read_journal/classify/apply_plan/check_snapshots. Do NOT call legacy P2 inputs/new_plan/verify_committed because they enforce disabled P2. Implement P3 committed check; preserve all other items and histories. Work key canonical schema, role daily_compile, receipt, schema validation.
- Write-ahead journal recovery requires deterministic plan reconstruction from bound prior state/index/input snapshots, not just self-hash of supplied journal. Reject tampered targets/receipt/state even if envelope hash recomputed. Validate all targets before recovery; preserve log append and unrelated index changes. Reject unknown/unresolved other transactions and unrecognized legacy journals. Readback exact outputs/state/receipt/index/log. Existing legacy sources/receipts are not regenerated.
- No production CLI in publisher. Tests use actual generic transaction helpers on temporary fixtures under this runtime/synthetic-*; synthetic enabled policies and synthetic approval are not live permissions. Test no-op, each crash stage recovery, user edits, source drift, malformed evidence, priority, busy, unknown cost.

## Evidence
Strict vertical TDD: failing tracer slice -> observed RED log + snapshots -> minimal implementation -> observed GREEN; subsequent negative slices similarly. Additional first-pass regressions are coverage, not RED. Use unique evidence filenames and preserve failures. Final outputs include exact test command/counts and limitations. Do not claim live P3 complete or Cron active. Parent will run integrated synthetic path and verify live protected hashes.
