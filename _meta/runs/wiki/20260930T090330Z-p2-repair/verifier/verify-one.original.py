import sys, json, re, hashlib
from pathlib import Path

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
VID = sys.argv[1]
res = json.loads((RUN / VID / "attempt-result.json").read_text())
report = {"vid": VID, "checks": [], "passed": True}

def check(name, ok, detail=""):
    report["checks"].append({"check": name, "ok": bool(ok), "detail": str(detail)[:200]})
    if not ok:
        report["passed"] = False

src = Path(f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html").read_text("utf-8", "replace")
check("source_sha256_match", res.get("source_sha256") == hashlib.sha256(Path(f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html").read_bytes()).hexdigest())
check("completed", res.get("completed") is True and res.get("error") is None)
check("response_model_gpt-6-astra", res.get("response_model") == "gpt-6-astra")
check("cost_recorded_as_unobserved", res.get("cost_usd") is None and res.get("cost_status") == "unobserved_not_zero")

raw = res.get("text", "")
# model must output exactly one JSON object
m = re.search(r"\{.*\}", raw, re.S)
check("single_json_object", bool(m))
if not m:
    (RUN / VID / "verify-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2)); sys.exit(0)
doc = json.loads(m.group(0))

check("title_present", bool(doc.get("title")))
check("version_id_match", doc.get("version_id") == VID)
check("main_text_complete_bool", isinstance(doc.get("main_text_complete"), bool))
check("read_scope_nonempty", isinstance(doc.get("read_scope"), list) and len(doc.get("read_scope")) > 0)
unread = doc.get("unread_scope") or []
check("unread_scope_flags_unreviewed", any("그림" in u or "figure" in u.lower() or "미검" in u for u in unread) and len(unread) >= 3, unread[:3])
claims = doc.get("claims") or []
check("claims_8_to_14", 8 <= len(claims) <= 14, f"n={len(claims)}")
kinds = {c.get("kind") for c in claims}
check("claim_kinds_valid", kinds <= {"author_report", "analyst_interpretation"}, kinds)
body = doc.get("markdown_body") or ""
nlines = len([l for l in body.splitlines() if l.strip()])
check("body_90_150_lines", 90 <= nlines <= 150, f"n={nlines}")
check("body_has_evidence_table", "| C" in body or "C01" in body)

# anchors must exist in source (id="..."); quotes must be substrings of source text
src_flat = re.sub(r"\s+", " ", re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", src))
missing_anchor, bad_quote = [], []
ids = set(re.findall(r'id="([^"]+)"', src))
for c in claims:
    a = c.get("anchor")
    if not a or a.startswith("#") or a not in ids:
        missing_anchor.append(a)
    q = re.sub(r"\s+", " ", (c.get("quote") or "").strip())
    if not q or q not in src_flat:
        bad_quote.append((c.get("id"), q[:60]))
check("anchors_exist_in_source", not missing_anchor, missing_anchor[:5])
check("quotes_verbatim_in_source", not bad_quote, bad_quote[:3])

(RUN / VID / "verify-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False, indent=2))
