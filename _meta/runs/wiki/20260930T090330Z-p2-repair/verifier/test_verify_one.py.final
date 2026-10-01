"""Isolated synthetic P2 verifier regressions; no real paper or model reads."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("verify-one.py").resolve()
RUN = Path("_meta/runs/wiki/20260929T083140Z-p2-resume")
VID = "2609.00001v1"
SOURCE = Path(f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html")


def make_fixture(root):
    source = root / SOURCE
    source.parent.mkdir(parents=True)
    source.write_text('<html><body><section id="S1"><p id="P1">Synthetic evidence supports a bounded claim.</p></section><section id="S2">Other anchor contains different evidence.</section></body></html>', encoding="utf-8")
    claims = [{"id": f"C{i:02d}", "kind": "author_report", "statement": f"Synthetic bounded claim {i}.", "conditions": "Only the synthetic fixture, not a scientific result.", "anchor": "S1", "quote": "Synthetic evidence supports a bounded claim."} for i in range(1, 9)]
    lines = ["## Synthetic analysis"]
    for c in claims:
        lines += [f"### {c['id']}", f"{c['id']}: {c['statement']} [{c['id']} evidence]({SOURCE}#{c['anchor']})", "This is synthetic, not a paper result.", "Conditions: synthetic local fixture only.", "Scope: section S1 was read.", "Uncertainty: figures were not reviewed.", "Method: no model or external request.", "Interpretation: bounded to fixture evidence.", "Limit: no empirical reproduction.", "Related knowledge pages are not available.", "No figures or equations were reviewed.", "No external evidence was obtained."]
    document = {"title": "Synthetic verifier fixture", "version_id": VID, "main_text_complete": True, "read_scope": ["S1", "S2"], "unread_scope": ["Figures not reviewed", "Equations not reviewed", "Appendix not reviewed"], "limitations": ["Synthetic evidence only; no scientific validation."], "claims": claims, "markdown_body": "\n".join(lines)}
    result = {"completed": True, "response_status": "completed", "error": None, "incomplete_details": None, "response_model": "gpt-6-astra", "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "cost_usd": None, "cost_status": "unobserved_not_zero", "text": json.dumps(document)}
    return result, document


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="p2-verifier-synthetic-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.result, self.document = make_fixture(self.root)

    def cli(self, result=None, *args):
        dest = self.root / RUN / VID
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "attempt-result.json").write_text(json.dumps(self.result if result is None else result), encoding="utf-8")
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), VID, *args], cwd=self.root, text=True, capture_output=True, timeout=20)
        path = dest / "attempt-verify-report.json"
        if not path.exists():  # Exercise the ORIGINAL CLI before the repair.
            path = dest / "verify-report.json"
        report = json.loads(path.read_text()) if path.exists() else None
        return proc, report

    def verify(self, result=None):
        spec = importlib.util.spec_from_file_location("p2_verify_one", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.verify_result(self.root, VID, self.result if result is None else result)

    def document_report(self, document=None):
        result = copy.deepcopy(self.result)
        result["text"] = json.dumps(self.document if document is None else document)
        return self.verify(result)


class CompletionTests(FixtureCase):
    def test_positive_legacy_cli_control(self):
        proc, report = self.cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(report["passed"], report)

    def test_incomplete_response_rejected(self):
        self.result["response_status"] = "incomplete"
        proc, report = self.cli()
        self.assertFalse(report["passed"], report)
        self.assertNotEqual(proc.returncode, 0)

    def test_partial_main_text_rejected(self):
        self.document["main_text_complete"] = False
        self.result["text"] = json.dumps(self.document)
        proc, report = self.cli()
        self.assertFalse(report["passed"], report)
        self.assertNotEqual(proc.returncode, 0)


class InterfaceTests(FixtureCase):
    def test_malformed_result_envelope_gets_failed_report(self):
        dest = self.root / RUN / VID
        dest.mkdir(parents=True)
        for attempt, payload in [("broken", "{"), ("duplicate", '{"text":"a","text":"b"}'), ("nonobject", "[]")]:
            with self.subTest(attempt=attempt):
                (dest / f"{attempt}-result.json").write_text(payload)
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT), VID, "--root", str(self.root), "--attempt", attempt], cwd=self.root, capture_output=True, text=True, timeout=20)
                self.assertNotEqual(proc.returncode, 0)
                report_path = dest / f"{attempt}-verify-report.json"
                self.assertTrue(report_path.exists())
                report = json.loads(report_path.read_text())
                self.assertFalse(report["passed"])
                self.assertIsNone(report["document"])

    def test_import_safe_read_only_interface(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result_before = copy.deepcopy(self.result)
        report = self.verify()
        self.assertEqual(set(report) & {"passed", "checks", "document"}, {"passed", "checks", "document"})
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["document"], self.document)
        self.assertEqual(self.result, result_before)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_cli_explicit_paths_attempt_and_no_overwrite(self):
        run = self.root / "custom-run"
        dest = run / VID
        dest.mkdir(parents=True)
        (dest / "second-result.json").write_text(json.dumps(self.result))
        historical = dest / "verify-report.json"
        historical.write_bytes(b"historical evidence\n")
        cmd = [sys.executable, "-B", str(SCRIPT), VID, "--root", str(self.root), "--run", str(run), "--attempt", "second"]
        proc = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report_path = dest / "second-verify-report.json"
        self.assertTrue(report_path.exists())
        original = report_path.read_bytes()
        self.assertTrue(json.loads(original)["passed"])
        proc = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(report_path.read_bytes(), original)
        self.assertEqual(historical.read_bytes(), b"historical evidence\n")

    def test_default_cli_does_not_write_historical_report(self):
        proc, report = self.cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        dest = self.root / RUN / VID
        self.assertTrue((dest / "attempt-verify-report.json").exists())
        self.assertFalse((dest / "verify-report.json").exists())

    def test_cost_unknown_and_observed_costs_are_nonblocking(self):
        for value, status in [(None, "unknown"), (None, "unobserved_not_zero"), (0, "known"), (42.5, "observed")]:
            with self.subTest(value=value, status=status):
                result = copy.deepcopy(self.result)
                result.update(cost_usd=value, cost_status=status)
                self.assertTrue(self.verify(result)["passed"])

    def test_transport_and_model_rejections(self):
        for key, value in [("completed", False), ("completed", 1), ("response_status", None), ("error", {}), ("incomplete_details", {}), ("response_model", "other-model")]:
            with self.subTest(key=key, value=value):
                result = copy.deepcopy(self.result)
                result[key] = value
                report = self.verify(result)
                self.assertFalse(report["passed"])


class DocumentTests(FixtureCase):
    def test_overflow_number_cannot_make_non_json_report(self):
        result = copy.deepcopy(self.result)
        result["text"] = result["text"][:-1] + ',"extra":1e999}'
        report = self.verify(result)
        self.assertFalse(report["passed"])
        self.assertIsNone(report["document"])

    def test_unclosed_fence_and_indented_code_are_not_citations(self):
        for body in ["```markdown\n" + self.document["markdown_body"], "\n".join("    " + line for line in self.document["markdown_body"].splitlines())]:
            with self.subTest(body=body[:30]):
                document = copy.deepcopy(self.document)
                document["markdown_body"] = body
                self.assertFalse(self.document_report(document)["passed"])

    def test_wikilink_fragments_must_exist(self):
        target = self.root / "entities" / "related.md"
        target.parent.mkdir()
        target.write_text("# Related synthetic page\nParagraph.\n")
        for fragment, expected in [("related-synthetic-page", True), ("Related synthetic page", True), ("nonexistent", False)]:
            with self.subTest(fragment=fragment):
                document = copy.deepcopy(self.document)
                document["markdown_body"] += f"\n[[entities/related#{fragment}|Read more]]"
                self.assertEqual(self.document_report(document)["passed"], expected)

    def test_malformed_wikilinks_and_extra_broken_source_citations(self):
        for extra in ["\n[[entities/missing", "\n[bad](" + str(SOURCE) + "#missing)", "\n[bad](raw/articles/other/source.html#S1)"]:
            with self.subTest(extra=extra):
                document = copy.deepcopy(self.document)
                document["markdown_body"] += extra
                self.assertFalse(self.document_report(document)["passed"])

    def test_rejects_invalid_json_documents(self):
        for text in ["{", "{}{}", "[]", "null", "42", '"document"', "prefix " + self.result["text"], self.result["text"] + " trailing", '```json\n' + self.result["text"] + '\n```', '{"a":1,"a":2}', self.result["text"][:-1] + ',"extra":NaN}']:
            with self.subTest(text=text[:40]):
                result = copy.deepcopy(self.result)
                result["text"] = text
                report = self.verify(result)
                self.assertFalse(report["passed"])
                self.assertIsNone(report["document"])

    def test_duplicate_keys_in_valid_document_rejected(self):
        for old, new in [('"title":', '"title":"duplicate", "title":'), ('"id": "C01"', '"id":"duplicate", "id": "C01"')]:
            with self.subTest(old=old):
                result = copy.deepcopy(self.result)
                result["text"] = result["text"].replace(old, new, 1)
                report = self.verify(result)
                self.assertFalse(report["passed"])
                self.assertIsNone(report["document"])

    def test_rejects_wrong_vid_empty_scopes_and_limitations(self):
        for key, value in [("version_id", "2609.00002v1"), ("title", "  "), ("read_scope", [""]), ("read_scope", [1]), ("unread_scope", []), ("unread_scope", ["Figures unreviewed", "", ""]), ("limitations", []), ("limitations", "  "), ("main_text_complete", 1)]:
            with self.subTest(key=key, value=value):
                document = copy.deepcopy(self.document)
                document[key] = value
                self.assertFalse(self.document_report(document)["passed"])

    def test_rejects_invalid_and_duplicate_claim_fields(self):
        for key, value in [("id", "C02"), ("id", ""), ("kind", "unsupported"), ("statement", ""), ("statement", []), ("conditions", " "), ("conditions", None), ("anchor", "#S1"), ("quote", "")]:
            with self.subTest(key=key, value=value):
                document = copy.deepcopy(self.document)
                document["claims"][0][key] = value
                self.assertFalse(self.document_report(document)["passed"])
        for claims in [[], [None], {}, "invalid"]:
            with self.subTest(claims=claims):
                document = copy.deepcopy(self.document)
                document["claims"] = claims
                self.assertFalse(self.document_report(document)["passed"])

    def test_rejects_unreferenced_claims_fake_citations_and_frontmatter(self):
        body = self.document["markdown_body"]
        variants = [body.replace("C08", "C88"), body.replace(str(SOURCE) + "#S1", "elsewhere.html#S1"), "---\nstatus: reviewed\n---\n" + body, "<!--\n" + body + "\n-->", "```markdown\n" + body + "\n```", "\n".join(["C01 lacks actual citations"] * 100), body + "\n[[entities/missing-page]]"]
        for markdown in variants:
            with self.subTest(markdown=markdown[:50]):
                document = copy.deepcopy(self.document)
                document["markdown_body"] = markdown
                self.assertFalse(self.document_report(document)["passed"])

    def test_concise_cited_markdown_and_existing_wikilinks_accepted(self):
        target = self.root / "entities" / "2609.00002v1.md"
        target.parent.mkdir()
        target.write_text("# Related synthetic page\n")
        self.document["markdown_body"] = "\n".join(f"{c['id']}: {c['statement']} ^[{SOURCE}#{c['anchor']}]" for c in self.document["claims"]) + "\n[[entities/2609.00002v1|Related]]"
        report = self.document_report()
        self.assertTrue(report["passed"], report)


class EvidenceTests(FixtureCase):
    def set_html(self, html):
        source = self.root / SOURCE
        source.write_text(html, encoding="utf-8")
        self.result["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()

    def test_quote_must_be_in_exact_anchor_subtree(self):
        self.document["claims"][0]["anchor"] = "S2"
        self.document["markdown_body"] = self.document["markdown_body"].replace(f"[C01 evidence]({SOURCE}#S1)", f"[C01 evidence]({SOURCE}#S2)")
        report = self.document_report()
        self.assertFalse(report["passed"])
        self.assertTrue(any(not c["ok"] and "quote" in c["check"] for c in report["checks"]))

    def test_decoded_entities_inline_tags_and_whitespace_are_visible(self):
        self.set_html("<html><body><section id='S1'><p>Synthetic <em>evidence</em> supports\n a bounded claim. A&amp;B use <b>inter</b>leaved words.</p></section></body></html>")
        self.document["claims"][0]["quote"] = "A&B use interleaved words."
        self.assertTrue(self.document_report()["passed"])

    def test_quote_cannot_come_from_attributes_comments_or_hidden_nodes(self):
        quote = "Synthetic evidence supports a bounded claim."
        for hidden in [f'<span title="{quote}">other</span>', f'<!-- {quote} -->', f'<script>{quote}</script>', f'<style>{quote}</style>', f'<template>{quote}</template>', f'<span hidden>{quote}</span>', f'<span aria-hidden="true">{quote}</span>', f'<span style="display:none">{quote}</span>', f'<span style="visibility: hidden">{quote}</span>']:
            with self.subTest(hidden=hidden):
                self.set_html(f'<html><body><section id="S1">{hidden}</section></body></html>')
                self.assertFalse(self.document_report()["passed"])

    def test_duplicate_anchor_is_ambiguous(self):
        quote = "Synthetic evidence supports a bounded claim."
        self.set_html(f'<html><body><section id="S1">{quote}</section><p id="S1">{quote}</p></body></html>')
        self.assertFalse(self.document_report()["passed"])

    def test_missing_anchor_and_hash_drift_rejected(self):
        self.document["claims"][0]["anchor"] = "missing"
        self.assertFalse(self.document_report()["passed"])
        self.result["source_sha256"] = "0" * 64
        self.assertFalse(self.verify()["passed"])


class PathTests(FixtureCase):
    def test_invalid_expected_vid_is_not_repaired_or_used_as_path(self):
        spec = importlib.util.spec_from_file_location("p2_verify_invalid", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for vid in ["../2609.00001v1", "2609.00001v1/..", "2609.00001", " 2609.00001v1", "2609.00001v0", "2609.00001v01"]:
            with self.subTest(vid=vid):
                report = module.verify_result(self.root, vid, self.result)
                self.assertFalse(report["passed"])

    def test_output_symlink_does_not_overwrite_target(self):
        dest = self.root / RUN / VID
        dest.mkdir(parents=True)
        sentinel = self.root / "historical.json"
        sentinel.write_bytes(b'{"historical": true}')
        (dest / "attempt-verify-report.json").symlink_to(sentinel)
        proc, report = self.cli()
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(sentinel.read_bytes(), b'{"historical": true}')

    def test_source_file_symlink_rejected_even_inside_root(self):
        source = self.root / SOURCE
        target = source.with_name("copy.html")
        source.rename(target)
        source.symlink_to(target)
        self.assertFalse(self.verify()["passed"])

    def test_source_directory_symlink_rejected(self):
        source_dir = (self.root / SOURCE).parent
        moved = source_dir.with_name("moved")
        source_dir.rename(moved)
        source_dir.symlink_to(moved, target_is_directory=True)
        self.assertFalse(self.verify()["passed"])

    def test_result_source_override_is_rejected(self):
        for path in ["../../outside.html", "/tmp/outside.html", "raw/../elsewhere.html"]:
            with self.subTest(path=path):
                result = copy.deepcopy(self.result)
                result["source_path"] = path
                self.assertFalse(self.verify(result)["passed"])

    def test_cli_path_escape_and_symlink_root_rejected(self):
        dest = self.root / RUN / VID
        dest.mkdir(parents=True)
        (dest / "attempt-result.json").write_text(json.dumps(self.result))
        link = self.root / "alias"
        link.symlink_to(self.root, target_is_directory=True)
        for args in [["--root", str(link)], ["--run", str(self.root / RUN / ".." / RUN.name)], ["--attempt", "../escape"], ["--run", "/tmp"]]:
            with self.subTest(args=args):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT), VID, "--root", str(self.root), *args], cwd=self.root, text=True, capture_output=True, timeout=20)
                self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((dest / "attempt-verify-report.json").exists())

    def test_cli_result_symlink_rejected(self):
        dest = self.root / RUN / VID
        dest.mkdir(parents=True)
        target = self.root / "external-result.json"
        target.write_text(json.dumps(self.result))
        (dest / "attempt-result.json").symlink_to(target)
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), VID, "--root", str(self.root)], cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(proc.returncode, 0)

    def test_wikilinks_cannot_escape_or_use_symlink(self):
        target = self.root / "existing.md"
        target.write_text("# Synthetic\n")
        link = self.root / "alias.md"
        link.symlink_to(target)
        for name in ["alias", str(target), "../" + self.root.name + "/existing"]:
            with self.subTest(name=name):
                result = copy.deepcopy(self.result)
                document = copy.deepcopy(self.document)
                document["markdown_body"] += f"\n[[{name}]]"
                result["text"] = json.dumps(document)
                self.assertFalse(self.verify(result)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
