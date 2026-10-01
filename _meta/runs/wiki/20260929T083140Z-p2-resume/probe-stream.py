import sys, json, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/ainsdev/.hermes/hermes-agent")
from hermes_cli.runtime_provider import resolve_runtime_provider
from openai import OpenAI

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
PROBE_CAP_S = 300  # observation cap for time-to-first-event with a trivial prompt

def now():
    return datetime.now(timezone.utc).isoformat()

rt = resolve_runtime_provider(requested="codex-lb", target_model="gpt-6-astra")
route = {
    "requested_provider": "codex-lb",
    "resolved_base_url": rt["base_url"],
    "api_mode": rt["api_mode"],
    "model": rt.get("model"),
    "request_overrides_present": bool(rt.get("request_overrides")),
    "paper_content_sent": False,
}
(RUN / "probe-route.json").write_text(json.dumps(route, ensure_ascii=False, indent=2) + "\n")

client = OpenAI(api_key=rt["api_key"], base_url=rt["base_url"],
                default_headers=rt.get("extra_headers") or {}, max_retries=0, timeout=PROBE_CAP_S + 30)

events = []
t0 = time.monotonic()
final = None
err = None
try:
    stream = client.responses.create(
        model="gpt-6-astra",
        instructions="Reply with exactly the token STREAM_OK. No tools, no extra text.",
        input=[{"role": "user", "content": [{"type": "input_text", "text": "ping"}]}],
        reasoning={"effort": "xhigh"}, store=False, stream=True, tools=[])
    for ev in stream:
        events.append({"t": round(time.monotonic() - t0, 3), "type": ev.type})
        if ev.type == "response.completed":
            final = ev.response
        if time.monotonic() - t0 > PROBE_CAP_S:
            break
except Exception as e:
    err = f"{type(e).__name__}: {e}"

out = {
    "schema": "pkm-p2-stream-probe/v1",
    "recorded_at": now(),
    "purpose": "phase-1 diagnosis: time-to-first-event and stream health with trivial input, no paper content",
    "probe_cap_seconds": PROBE_CAP_S,
    "reasoning": "xhigh",
    "event_count": len(events),
    "first_event": events[0] if events else None,
    "event_types": sorted({e["type"] for e in events}),
    "last_events": events[-5:],
    "completed": final is not None,
    "response_status": getattr(final, "status", None),
    "response_model": getattr(final, "model", None),
    "text": (getattr(final, "output_text", "") or "")[:100] if final is not None else None,
    "elapsed_seconds": round(time.monotonic() - t0, 3),
    "error": err,
}
if final is not None:
    u = getattr(final, "usage", None)
    if u is not None:
        out["usage"] = {k: v for k, v in u.model_dump().items() if k != "attribution"}
out["cost_usd"] = None
out["cost_status"] = "unobserved_not_zero"
(RUN / "probe-stream.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(out, ensure_ascii=False))
