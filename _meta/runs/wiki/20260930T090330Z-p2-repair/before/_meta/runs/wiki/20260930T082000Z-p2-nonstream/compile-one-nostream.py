import sys, json, time, hashlib, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/ainsdev/.hermes/hermes-agent")
from hermes_cli.runtime_provider import resolve_runtime_provider
from openai import OpenAI

RUN = Path("_meta/runs/wiki/20260930T082000Z-p2-nonstream")
VID = sys.argv[1]
LABEL = sys.argv[2] if len(sys.argv) > 2 else "attempt1"
HTTP_TIMEOUT_S = 5400

INSTR = Path("_meta/runs/wiki/20260929T083140Z-p2-resume/compile-instructions.txt").read_text()
src = Path(f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html")
src_bytes = src.read_bytes()
sha = hashlib.sha256(src_bytes).hexdigest()
html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", src_bytes.decode("utf-8", "replace"))

rt = resolve_runtime_provider(requested="codex-lb", target_model="gpt-6-astra")
client = OpenAI(api_key=rt["api_key"], base_url=rt["base_url"],
                default_headers=rt.get("extra_headers") or {}, max_retries=0, timeout=HTTP_TIMEOUT_S)

(RUN / VID).mkdir(parents=True, exist_ok=True)
(RUN / VID / f"{LABEL}-record.json").write_text(json.dumps({
    "schema": "pkm-p2-attempt/v3-nonstream", "started_at": datetime.now(timezone.utc).isoformat(),
    "vid": VID, "source_sha256": sha, "source_bytes": len(src_bytes), "sent_text_chars": len(html),
    "transport": "http-nonstream", "http_timeout_s": HTTP_TIMEOUT_S,
    "route_base_url": rt["base_url"], "api_mode": rt["api_mode"], "model": "gpt-6-astra",
    "prior_run_ref": "_meta/runs/wiki/20260929T083140Z-p2-resume/run-report.json",
    "bypass_evidence": "_meta/runs/wiki/20260929T083140Z-p2-resume/probe-nonstream.json"}, ensure_ascii=False, indent=2) + "\n")

t0 = time.monotonic(); resp = None; err = None
try:
    resp = client.responses.create(
        model="gpt-6-astra", instructions=INSTR,
        input=[{"role": "user", "content": [{"type": "input_text", "text": html}]}],
        reasoning={"effort": "xhigh"}, store=False, stream=False, tools=[])
except Exception as e:
    err = f"{type(e).__name__}: {e}"
elapsed = round(time.monotonic() - t0, 1)

out = {"schema": "pkm-p2-attempt-result/v3-nonstream", "vid": VID, "transport": "http-nonstream",
       "finished_at": datetime.now(timezone.utc).isoformat(), "completed": resp is not None,
       "error": err, "elapsed_seconds": elapsed,
       "response_status": getattr(resp, "status", None), "response_model": getattr(resp, "model", None),
       "source_sha256": sha,
       "incomplete_details": getattr(resp, "incomplete_details", None)}
if resp is not None:
    out["text"] = resp.output_text or ""
    u = getattr(resp, "usage", None)
    if u is not None:
        out["usage"] = {k: v for k, v in u.model_dump().items() if k != "attribution"}
out["cost_usd"] = None; out["cost_status"] = "unobserved_not_zero"
(RUN / VID / f"{LABEL}-result.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
if resp is not None and out.get("text"):
    (RUN / VID / f"{LABEL}-model-output.md").write_text(out["text"])
print(json.dumps({"vid": VID, "completed": resp is not None, "elapsed": elapsed,
                  "err": (err or "")[:200], "usage": out.get("usage"),
                  "status": out.get("response_status")}, ensure_ascii=False))
