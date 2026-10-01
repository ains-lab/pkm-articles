"""P2 result validation. Importing this module performs no I/O."""
import argparse
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import sys

RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
VID_PATTERN = re.compile(r"[0-9]{4}\.[0-9]{4,5}v[1-9][0-9]*")


def valid_vid(vid):
    return isinstance(vid, str) and VID_PATTERN.fullmatch(vid) is not None


def relative_parts(path):
    path = Path(path)
    if path.is_absolute() or not path.parts or any(p in (".", "..") or "\\" in p or "\x00" in p for p in path.parts):
        raise ValueError("Unsafe relative path")
    return path.parts


@contextmanager
def directory_fd(path):
    """Open every component without following links, including root ancestors."""
    path = Path(path).absolute()
    if ".." in path.parts:
        raise ValueError("Unsafe root path")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


@contextmanager
def parent_fd(root, relative):
    parts = relative_parts(relative)
    with directory_fd(root) as root_fd:
        fd = os.dup(root_fd)
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = child
            yield fd, parts[-1]
        finally:
            os.close(fd)


def read_local(root, relative):
    with parent_fd(root, relative) as (parent, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise ValueError("Expected a regular file")
            return source.read()


def normalize_visible(text):
    # No lowercasing, fuzzy matching or punctuation changes: whitespace only.
    return re.sub(r"\s+", " ", text).strip()


class AnchorText(HTMLParser):
    """Ephemeral navigation of visible text in each original id's subtree.

    Does not execute scripts, fetch CSS/assets, render figures or save extracts.
    Visibility is limited to HTML/inline hidden markers, not external CSS.
    """
    VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
    HIDDEN = frozenset("head script style template noscript iframe object svg".split())
    BLOCK = frozenset("address article aside blockquote br dd div dl dt fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hr li main nav ol p pre section table tbody td th thead tr ul".split())

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.anchors = {}
        self.duplicates = set()
        self.balanced = True

    def append(self, text):
        if self.stack and not self.stack[-1][1]:
            for _, _, anchor in self.stack:
                if anchor is not None:
                    self.anchors[anchor].append(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden_style = re.search(r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))\s*(?:!important\s*)?(?:;|$)", attrs.get("style") or "", re.I)
        hidden = bool((self.stack and self.stack[-1][1]) or tag in self.HIDDEN or "hidden" in attrs or (attrs.get("aria-hidden") or "").lower() == "true" or hidden_style)
        anchor = attrs.get("id")
        if anchor is not None:
            if anchor in self.anchors:
                self.duplicates.add(anchor)
            else:
                self.anchors[anchor] = []
        if tag in self.BLOCK:
            self.append(" ")
        if tag not in self.VOID:
            self.stack.append((tag, hidden, anchor))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.balanced = False
            return
        if tag in self.BLOCK:
            self.append(" ")
        self.stack.pop()

    def handle_data(self, data):
        self.append(data)

    def text_at(self, anchor):
        return normalize_visible("".join(self.anchors[anchor]))


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
    # Overflowing numbers and invalid Unicode must not produce an invalid report.
    json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return obj


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def text_list(value):
    return isinstance(value, list) and bool(value) and all(nonempty_text(v) for v in value)


def visible_markdown(body):
    """Discard comments and code, which cannot supply rendered citations."""
    body = re.sub(r"<!--.*?(?:-->|\Z)", "", body, flags=re.S)
    lines = []
    fence = None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
        elif not line.startswith(("    ", "\t")):
            lines.append(re.sub(r"`+[^`\n]*`+", "", line))
    return "\n".join(lines)


def citation_targets(line):
    links = re.findall(r"(?<!!)\[([^\]\n]+)\]\(([^\s()]+)\)", line)
    return {target for label, target in links if label.strip()} | set(re.findall(r"\^\[([^\]\s]+)\]", line))


def markdown_anchor_exists(text, fragment):
    rendered = visible_markdown(text)
    for heading in re.findall(r"(?m)^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", rendered):
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")
        if fragment in (heading, slug):
            return True
    return bool(re.search(r"(?m)(?:^|\s)\^" + re.escape(fragment.lstrip("^")) + r"\s*$", rendered))


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
    check("no_response_error", result.get("response_error") is None)
    check("no_incomplete_details", result.get("incomplete_details") is None)
    check("response_model_gpt-6-astra", result.get("response_model") == "gpt-6-astra")
    # Costs are telemetry, not an acceptance gate under the approved v2 policy.
    check("cost_nonblocking", True, "Observed or unknown cost does not gate verification")

    try:
        doc = strict_object(result.get("text", ""))
    except (ValueError, TypeError, RecursionError):
        check("single_json_object", False)
        return report
    report["document"] = doc
    check("single_json_object", True)
    check("expected_vid_valid", valid_vid(vid))
    if not valid_vid(vid):
        return report
    source_rel = f"raw/articles/4cff5b4f10ec/arxiv-{vid}/source.html"
    check("source_path_expected", "source_path" not in result or result["source_path"] == source_rel)
    try:
        source_bytes = read_local(root, source_rel)
        src = source_bytes.decode("utf-8")
    except (OSError, ValueError, TypeError):
        check("source_safe_readable", False)
        return report
    check("source_sha256_match", result.get("source_sha256") == hashlib.sha256(source_bytes).hexdigest())
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
    cited = valid_ids and all(any(re.search(r"\b" + re.escape(c["id"]) + r"\b", line) and f"{source_rel}#{c.get('anchor')}" in citation_targets(line) for line in markdown.splitlines()) for c in claims)
    check("markdown_claim_citations", cited)
    link_pattern = r"\[\[([^\[\]\n]+)\]\]"
    remaining = re.sub(link_pattern, "", markdown)
    wikilinks_ok = "[[" not in remaining and "]]" not in remaining
    for target in re.findall(link_pattern, markdown):
        name, marker, fragment = target.split("|", 1)[0].partition("#")
        try:
            if not name:
                raise ValueError("Empty wikilink")
            linked_text = read_local(root, name if name.endswith(".md") else name + ".md").decode("utf-8")
            if marker and (not fragment or not markdown_anchor_exists(linked_text, fragment)):
                wikilinks_ok = False
        except (OSError, ValueError):
            wikilinks_ok = False
    check("wikilinks_resolve", wikilinks_ok)
    html = AnchorText()
    html.feed(src)
    html.close()
    check("html_subtrees_unambiguous", html.balanced and not html.stack)
    anchors_valid = all(nonempty_text(c.get("anchor")) and not c["anchor"].startswith("#") and c["anchor"] in html.anchors and c["anchor"] not in html.duplicates for c in claims)
    check("anchors_exist_in_source", anchors_valid)
    check("quotes_verbatim_in_anchor_subtree", anchors_valid and all(nonempty_text(c.get("quote")) and normalize_visible(c["quote"]) in html.text_at(c["anchor"]) for c in claims))
    source_links_ok = True
    for line in markdown.splitlines():
        for target in citation_targets(line):
            if target.startswith("raw/"):
                path, marker, anchor = target.partition("#")
                if path != source_rel or not marker or anchor not in html.anchors or anchor in html.duplicates:
                    source_links_ok = False
    check("markdown_source_citations_resolve", source_links_ok)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vid")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--attempt", default="attempt")
    args = parser.parse_args(argv)
    try:
        if not valid_vid(args.vid) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.attempt):
            raise ValueError("Invalid VID or attempt")
        root = args.root.absolute()
        run = args.run.relative_to(root) if args.run.is_absolute() else args.run
        relative_parts(run)
        dest = run / args.vid
        report_path = dest / f"{args.attempt}-verify-report.json"
        raw_result = read_local(root, dest / f"{args.attempt}-result.json")
        try:
            result = strict_object(raw_result.decode("utf-8"))
        except (ValueError, TypeError, RecursionError):
            report = {"vid": args.vid, "passed": False, "document": None, "checks": [{"check": "result_json_object", "ok": False, "detail": "Invalid JSON result envelope"}]}
        else:
            report = verify_result(args.root, args.vid, result)
        with parent_fd(root, report_path) as (parent, name):
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                out.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
                out.flush()
                os.fsync(out.fileno())
            os.fsync(parent)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Verification refused: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
