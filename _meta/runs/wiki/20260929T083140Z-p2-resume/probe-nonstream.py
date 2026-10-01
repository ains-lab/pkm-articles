import sys, json, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/ainsdev/.hermes/hermes-agent")
from hermes_cli.runtime_provider import resolve_runtime_provider
from openai import OpenAI

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
CAP_S = 600

rt = resolve_runtime_provider(requested="codex-lb", target_model="gpt-6-astra")
client = OpenAI(api_key=rt["api_key"], base_url=rt["base_url"],
                default_headers=rt.get("extra_headers") or {}, max_retries=0, timeout=CAP_S)

t0 = time.monotonic(); err = None; resp = None
try:
    resp = client.responses.create(
        model="gpt-6-astra",
        instructions="Reply with exactly the token NONSTREAM_OK. No tools, no extra text.",
        input=[{"role": "user", "content": [{"type": "input_text", "text": "ping"}]}],
        reasoning={"effort": "xhigh"}, store=False, stream=False, tools=[])
except Exception as e:
    err = f"{type(e).__name__}: {e}"

out = {"schema": "pkm-p2-nonstream-probe/v1", "recorded_at": datetime.now(timezone.utc).isoformat(),
       "purpose": "비스트리밍 경로가 프록시 websocket keepalive 타임아웃을 우회하는지 확인 (논문 내용 없음)",
       "paper_content_sent": False, "cap_seconds": CAP_S,
       "completed": resp is not None, "error": err,
       "elapsed_seconds": round(time.monotonic() - t0, 1),
       "response_status": getattr(resp, "status", None),
       "response_model": getattr(resp, "model", None),
       "text": (getattr(resp, "output_text", "") or "")[:100] if resp is not None else None}
if resp is not None:
    u = getattr(resp, "usage", None)
    if u is not None:
        out["usage"] = {k: v for k, v in u.model_dump().items() if k != "attribution"}
out["cost_usd"] = None; out["cost_status"] = "unobserved_not_zero"
(RUN / "probe-nonstream.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(out, ensure_ascii=False))
