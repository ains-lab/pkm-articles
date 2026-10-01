"""Isolated synthetic publication tests. Never publish into the live Wiki.

Publication request/review contract is documented by Fixture.prepare_request below.
Requests must be authored by the orchestrating agent AFTER actual semantic review,
not copied from model output or an old verifier's passed=true flag. Agent review
never sets human-reviewed status.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRIPT = HERE / 'publish-one.py'


def load_publisher():
    spec = importlib.util.spec_from_file_location('p2_publisher', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EntrypointTests(unittest.TestCase):
    def test_help_is_an_import_safe_cli_not_publication(self):
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, '-B', str(SCRIPT), '--help'],
                               cwd=td, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('--root', p.stdout)
            self.assertIn('--run', p.stdout)
            self.assertIn('--attempt', p.stdout)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_import_does_not_read_arguments_or_publish(self):
        code = ('import importlib.util; '
                f's=importlib.util.spec_from_file_location("p", {str(SCRIPT)!r}); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                'assert callable(m.main)')
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, '-B', '-c', code], cwd=td,
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(list(Path(td).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
