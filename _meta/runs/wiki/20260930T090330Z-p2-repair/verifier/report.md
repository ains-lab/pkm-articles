# P2 verifier repair — observed local verification

## Outcome and interface

Modified only `../../20260929T083140Z-p2-resume/verify-one.py` and added its sibling `test_verify_one.py`; all other writes by this worker are evidence in this directory. No commit, global skill change, source/collector/state/Cron change or automatic activation.

```python
def verify_result(root: Path, vid: str, result: dict) -> dict:
    # {"vid": str, "passed": bool,
    #  "checks": [{"check": str, "ok": bool, "detail": str}],
    #  "document": dict | None}
```

Import has no I/O or CLI execution. Function reads only safe local source/linked Markdown files and does not write or mutate the supplied result. `document` is the strictly parsed single JSON object, including when subsequent verification fails; malformed/duplicate-key/nonobject JSON returns `None`. Publisher must require `passed is True`, not merely a nonnull document, and invoke again inside its publication lock.

CLI: `python3 -B verify-one.py VID [--root ROOT] [--run RUN] [--attempt ATTEMPT]`. Root defaults to current directory, run defaults to `_meta/runs/wiki/20260929T083140Z-p2-resume`, attempt defaults to `attempt`. Relative run paths are rooted under ROOT; absolute run paths must be inside it. Reads `<run>/<VID>/<attempt>-result.json`; exclusively creates `<attempt>-verify-report.json`. It never rewrites historical `verify-report.json` or an existing attempt report. Exit 0 = passed, 1 = failed verification, 2 = unsafe/I/O/existing-report refusal. Malformed readable result envelopes produce a failed report.

## Acceptance contract

- `completed is True`, `response_status == "completed"`, missing/null error and incomplete_details, actual `response_model == "gpt-6-astra"`.
- Costs are not acceptance gates: unknown/null, zero and positive observed cost all accepted. No cost is invented or converted to zero.
- Expected modern arXiv version ID, immutable source SHA-256, complete main text, nonempty title/read_scope/unread_scope/limitations.
- Claims: nonempty list, unique `C[0-9]+` IDs, kind `author_report` or `analyst_interpretation`, nonempty statement and `conditions` (or singular `condition`), original anchor and quote.
- Each claim ID must be referenced with its exact source-path/anchor citation on the same visible Markdown line (including evidence-table rows). Supports `[label](raw/.../source.html#anchor)` and `^[raw/.../source.html#anchor]`. Arbitrary line/claim-count quotas were replaced with these substantive checks. Fake code/comment citations, unknown claim references, frontmatter, malformed/broken/escaping/symlink wikilinks, missing heading/block anchors and broken raw-source citations fail.
- Quotes match only whitespace-normalized visible text in the exact anchor subtree, decoding HTML entities and respecting inline text boundaries; attributes/comments/script/style/template/hidden text cannot supply evidence. Missing/duplicate anchors and unbalanced HTML subtrees fail.
- No symlink traversal: descriptor-relative component opening with `O_NOFOLLOW`; no escaping VID/root/run/attempt/source override/wikilink paths; regular-file reads and exclusive report creation.

## Observed evidence

Original script preserved before any edit: `verify-one.original.py`, SHA-256 `504c088f07c346b39f6b6ada944f9ef5e1cbe08d330f50a0da61976534119507`.

- `red-01-output.txt`: original CLI, 3 tests; positive control passed, incomplete response and partial text incorrectly passed the old verifier, causing 2 regression failures. Exit 1. This is actual behavior reproduction, not an import/API failure.
- Subsequent RED/GREEN slices retain command, output, source and test snapshots (`red-02` through `red-06`, `green-01` through `green-06`). `red-02` import errors specifically document the missing import-safe API; they are not claimed as adversarial rejection evidence.
- Final command, from `/home/ainsdev/wiki/pkm-articles`:
  `python3 -B -m unittest discover -s _meta/runs/wiki/20260929T083140Z-p2-resume -p test_verify_one.py -v`
- `final-test-output.txt`: `Ran 32 tests in 0.756s`, `OK`, exit 0.
- Ten additional CLI executions captured in `cli-reports/<case>/attempt-verify-report.json`: two cost-positive/unknown successes and eight required negative cases, all with expected exit and verdict. Commands/stdout/stderr are adjacent `command.json` files. Temporary synthetic sources were discarded, not retained as extracts or compile inputs.
- `final-verification.json`: exact command, file hashes, CLI report paths, in-memory Python compilation and whitespace checks, and 34 preexisting raw files SHA-256 unchanged compared with `raw-hashes-before.json`.
- Final source/test snapshots: `verify-one.py.final`, `test_verify_one.py.final`; original-to-final diff: `implementation.diff`.

## Boundaries and reusable checks

All functional runs use explicitly synthetic temporary HTML, result and Wiki fixtures. Existing real source bytes were only hashed; no real paper body was exposed to the model, no external fetch/PDF processing/model call/publication occurred. Preserve original evidence first, run original CLI with a valid positive control and targeted negatives, then advance through independently observed RED/GREEN slices; retain fresh evidence names instead of overwriting previous results.

This verifier checks structure and exact local textual grounding, not scientific truth or semantic entailment. HTML visibility checks use markup and inline hidden markers; external CSS/assets are deliberately not fetched or rendered. Full browser-layout equivalence and human review are not claimed. Existing concurrent/preexisting modifications outside the two owned code files were left alone.
