"""P2 result validation. Importing this module performs no I/O."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")


def verify_result(root: Path, vid: str, result: dict) -> dict:
    """Read local HTML only; return checks and parsed document without writing."""
    report = {"vid": vid, "passed": True, "checks": [], "document": None}

    def check(name, ok, detail=""):
        report["checks"].append({"check": name, "ok": bool(ok), "detail": str(detail)[:200]})
        if not ok:
            report["passed"] = False

    check("result_object", isinstance(result, dict))
    if not isinstance(result, dict):
        return report
    check("completed", result.get("completed") is True)
    check("response_status_completed", result.get("response_status") == "completed")
    check("no_error", result.get("error") is None)
    check("no_incomplete_details", result.get("incomplete_details") is None)
    check("response_model_gpt-6-astra", result.get("response_model") == "gpt-6-astra")
    # Costs are telemetry, not an acceptance gate under the approved v2 policy.
    check("cost_nonblocking", True, "Observed or unknown cost does not gate verification")

    source = Path(root) / f"raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html"
    try:
        source_bytes = source.read_bytes()
        src = source_bytes.decode("utf-8")
    except (OSError, UnicodeError):
        check("source_readable", False)
        return report
    check("source_sha256_match", result.get("source_sha256") == hashlib.sha256(source_bytes).hexdigest())
    try:
        doc = json.loads(result.get("text", ""))
        if not isinstance(doc, dict):
            raise ValueError("Expected an object")
    except (ValueError, TypeError):
        check("single_json_object", False)
        return report
    report["document"] = doc
    check("single_json_object", True)
    check("title_present", bool(doc.get("title")))
    check("version_id_match", doc.get("version_id") == vid)
    check("main_text_complete", doc.get("main_text_complete") is True)
    check("read_scope_nonempty", isinstance(doc.get("read_scope"), list) and bool(doc["read_scope"]))
    unread = doc.get("unread_scope") or []
    check("unread_scope_flags_unreviewed", isinstance(unread, list) and all(isinstance(u, str) for u in unread) and len(unread) >= 3 and any("그림" in u or "figure" in u.lower() or "미검" in u for u in unread))
    claims = doc.get("claims") or []
    check("claims_8_to_14", isinstance(claims, list) and 8 <= len(claims) <= 14)
    if not isinstance(claims, list) or not all(isinstance(c, dict) for c in claims):
        check("claims_objects", False)
        return report
    check("claim_kinds_valid", all(c.get("kind") in ("author_report", "analyst_interpretation") for c in claims))
    body = doc.get("markdown_body") or ""
    if not isinstance(body, str):
        check("body_string", False)
        return report
    nlines = len([line for line in body.splitlines() if line.strip()])
    check("body_90_150_lines", 90 <= nlines <= 150)
    check("body_has_evidence_table", "| C" in body or "C01" in body)
    src_flat = re.sub(r"\s+", " ", re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", src))
    ids = set(re.findall(r'id="([^"]+)"', src))
    check("anchors_exist_in_source", all(isinstance(c.get("anchor"), str) and c["anchor"] in ids for c in claims))
    check("quotes_verbatim_in_source", all(isinstance(c.get("quote"), str) and bool(c["quote"].strip()) and re.sub(r"\s+", " ", c["quote"].strip()) in src_flat for c in claims))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vid")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--attempt", default="attempt")
    args = parser.parse_args(argv)
    run = args.run if args.run.is_absolute() else args.root / args.run
    dest = run / args.vid
    report_path = dest / f"{args.attempt}-verify-report.json"
    try:
        result = json.loads((dest / f"{args.attempt}-result.json").read_text(encoding="utf-8"))
        report = verify_result(args.root, args.vid, result)
        with report_path.open("x", encoding="utf-8") as out:
            out.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            out.flush()
            os.fsync(out.fileno())
    except (OSError, ValueError, TypeError) as exc:
        print(f"Verification refused: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
