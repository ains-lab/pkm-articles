"""P2 result validation. Importing this module performs no I/O."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")


def strict_object(text):
    """Exactly one JSON object; duplicates and non-JSON constants are invalid."""
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError("Duplicate JSON key")
            obj[key] = value
        return obj

    def invalid_constant(_):
        raise ValueError("Non-JSON constant")

    if not isinstance(text, str):
        raise ValueError("Expected JSON text")
    obj = json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)
    if not isinstance(obj, dict):
        raise ValueError("Expected an object")
    return obj


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def text_list(value):
    return isinstance(value, list) and bool(value) and all(nonempty_text(v) for v in value)


def visible_markdown(body):
    """Discard comments and code, which cannot supply rendered citations."""
    body = re.sub(r"<!--.*?(?:-->|\Z)", "", body, flags=re.S)
    body = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", body)
    return re.sub(r"`+[^`\n]*`+", "", body)


def citation_targets(line):
    links = re.findall(r"(?<!!)\[([^\]\n]+)\]\(([^\s()]+)\)", line)
    return {target for label, target in links if label.strip()} | set(re.findall(r"\^\[([^\]\s]+)\]", line))


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
        doc = strict_object(result.get("text", ""))
    except (ValueError, TypeError, RecursionError):
        check("single_json_object", False)
        return report
    report["document"] = doc
    check("single_json_object", True)
    check("title_present", nonempty_text(doc.get("title")))
    check("version_id_match", doc.get("version_id") == vid)
    check("main_text_complete", doc.get("main_text_complete") is True)
    check("read_scope_nonempty", text_list(doc.get("read_scope")))
    check("unread_scope_nonempty", text_list(doc.get("unread_scope")))
    limitations = doc.get("limitations")
    check("limitations_nonempty", nonempty_text(limitations) or text_list(limitations))
    claims = doc.get("claims") or []
    check("claims_nonempty", isinstance(claims, list) and bool(claims))
    if not isinstance(claims, list) or not all(isinstance(c, dict) for c in claims):
        check("claims_objects", False)
        return report
    check("claim_kinds_valid", all(c.get("kind") in ("author_report", "analyst_interpretation") for c in claims))
    claim_ids = [c.get("id") for c in claims]
    valid_ids = all(isinstance(i, str) and re.fullmatch(r"C[0-9]+", i) for i in claim_ids)
    check("claim_ids_unique", valid_ids and len(set(claim_ids)) == len(claim_ids))
    check("claim_statements_present", all(nonempty_text(c.get("statement")) for c in claims))
    check("claim_conditions_present", all(nonempty_text(c.get("conditions", c.get("condition"))) for c in claims))
    body = doc.get("markdown_body") or ""
    if not isinstance(body, str):
        check("body_string", False)
        return report
    check("body_nonempty", nonempty_text(body))
    check("no_unexpected_frontmatter", "frontmatter" not in doc and not re.match(r"\A\s*(?:---|\+\+\+)\s*(?:\n|$)", body))
    markdown = visible_markdown(body)
    mentioned = set(re.findall(r"\bC[0-9]+\b", markdown))
    check("markdown_claim_references", valid_ids and mentioned == set(claim_ids))
    source_rel = f"raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html"
    cited = valid_ids and all(any(re.search(r"\b" + re.escape(c["id"]) + r"\b", line) and f"{source_rel}#{c.get('anchor')}" in citation_targets(line) for line in markdown.splitlines()) for c in claims)
    check("markdown_claim_citations", cited)
    wikilinks_ok = True
    for target in re.findall(r"\[\[([^\]\n]+)\]\]", markdown):
        name = target.split("|", 1)[0].split("#", 1)[0]
        path = Path(root) / (name if name.endswith(".md") else name + ".md")
        if not name or not path.is_file():
            wikilinks_ok = False
    check("wikilinks_resolve", wikilinks_ok)
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
