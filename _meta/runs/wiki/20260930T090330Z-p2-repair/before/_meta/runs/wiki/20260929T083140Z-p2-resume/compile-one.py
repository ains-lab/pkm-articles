import sys, json, time, hashlib, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/ainsdev/.hermes/hermes-agent")
from hermes_cli.runtime_provider import resolve_runtime_provider
from openai import OpenAI

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
VID = sys.argv[1]
INSTR = Path(sys.argv[2]).read_text()
CALL_DEADLINE_S = int(sys.argv[3]) if len(sys.argv) > 3 else 2400
LABEL = sys.argv[4] if len(sys.argv) > 4 else "attempt"

src = Path(f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html")
src_bytes = src.read_bytes()
sha = hashlib.sha256(src_bytes).hexdigest()
html = src_bytes.decode("utf-8", "replace")
# strip scripts/styles: keep text-bearing markup for anchors; send as plain text content
html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)

rt = resolve_runtime_provider(requested="codex-lb", target_model="gpt-6-astra")
client = OpenAI(api_key=rt["api_key"], base_url=rt["base_url"],
                default_headers=rt.get("extra_headers") or {}, max_retries=0, timeout=CALL_DEADLINE_S + 60)

meta = {"vid": VID, "source_sha256": sha, "source_bytes": len(src_bytes),
        "sent_text_chars": len(html), "call_deadline_s": CALL_DEADLINE_S,
        "route_base_url": rt["base_url"], "api_mode": rt["api_mode"], "model": "gpt-6-astra"}
(RUN/f"{VID}/{LABEL}-record.json").parent.mkdir(parents=True, exist_ok=True)
(RUN/f"{VID}/{LABEL}-record.json").write_text(json.dumps({"schema":"pkm-p2-attempt/v2","started_at":datetime.now(timezone.utc).isoformat(),**meta}, ensure_ascii=False, indent=2)+"\n")

events = 0; first_t = None; t0 = time.monotonic(); final = None; err = None
try:
    stream = client.responses.create(
        model="gpt-6-astra",
        instructions=INSTR,
        input=[{"role": "user", "content": [{"type": "input_text", "text": html}]}],
        reasoning={"effort": "xhigh"}, store=False, stream=True, tools=[])
    for ev in stream:
        events += 1
        if first_t is None: first_t = round(time.monotonic() - t0, 1)
        if ev.type == "response.completed":
            final = ev.response
        elif ev.type in ("response.failed", "error", "response.incomplete"):
            (RUN/f"{VID}/{LABEL}-error-event.json").write_text(json.dumps({"t": round(time.monotonic()-t0,1), "type": ev.type, "raw": getattr(ev, "model_dump", lambda: {"type": ev.type})()}, default=str)+"\n")
except Exception as e:
    err = f"{type(e).__name__}: {e}"
elapsed = round(time.monotonic() - t0, 1)

out = {"schema": "pkm-p2-attempt-result/v2", "vid": VID, "finished_at": datetime.now(timezone.utc).isoformat(),
       "completed": final is not None, "error": err, "elapsed_seconds": elapsed,
       "event_count": events, "first_event_s": first_t,
       "response_status": getattr(final, "status", None), "response_model": getattr(final, "model", None),
       "source_sha256": sha}
if final is not None:
    out["text"] = final.output_text or ""
    u = getattr(final, "usage", None)
    if u is not None:
        out["usage"] = {k: v for k, v in u.model_dump().items() if k != "attribution"}
out["cost_usd"] = None; out["cost_status"] = "unobserved_not_zero"
(RUN/f"{VID}/{LABEL}-result.json").write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n")
# store model output verbatim for verification (staged; not published)
if final is not None and out.get("text"):
    (RUN/f"{VID}/{LABEL}-model-output.md").write_text(out["text"])
print(json.dumps({"vid": VID, "completed": final is not None, "elapsed": elapsed, "first_event_s": first_t, "err": (err or "")[:200], "usage": out.get("usage")}, ensure_ascii=False))
