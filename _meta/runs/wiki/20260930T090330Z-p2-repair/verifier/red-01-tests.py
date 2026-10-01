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
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.verify_result(self.root, VID, self.result if result is None else result)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
