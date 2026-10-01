"""Cross-component regressions using synthetic files only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
RUN = Path('_meta/runs/wiki/20260929T083140Z-p2-resume')


class HandoffTests(unittest.TestCase):
    def test_instructions_use_the_verified_document_contract(self):
        text = (ROOT / RUN / 'compile-instructions.txt').read_text()
        self.assertNotIn('statement_ko', text)
        self.assertNotIn('condition_ko', text)
        for field in ('statement (', 'conditions (', 'limitations ('):
            self.assertIn(field, text)
        self.assertIn('[Evidence](raw/articles/4cff5b4f10ec/arxiv-<version_id>/source.html#<anchor>)', text)

    def test_historical_closer_is_import_safe_and_cannot_replay_writes(self):
        with tempfile.TemporaryDirectory(prefix='p2-handoff-SYNTHETIC-') as td:
            root = Path(td)
            (root / RUN).mkdir(parents=True)
            (root / '_meta/state').mkdir(parents=True)
            (root / 'entities').mkdir()
            items = []
            for vid in ('2609.30830v1', '2609.31358v1'):
                source = root / 'raw/articles/4cff5b4f10ec' / ('arxiv-' + vid)
                source.mkdir(parents=True)
                (source / 'source.html').write_text('SYNTHETIC TEST ONLY')
                items.append(dict(version_id=vid, status='retryable_failed', failure_count=1))
            (root / '_meta/state/compilation.json').write_text(json.dumps({'items': items}))
            (root / 'log.md').write_text('# SYNTHETIC LOG\n')
            def hashes():
                return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob('*') if p.is_file()}
            before = hashes()
            script = str(ROOT / RUN / 'close-run.py')
            code = ('import importlib.util; '
                    f's=importlib.util.spec_from_file_location("legacy", {script!r}); '
                    'm=importlib.util.module_from_spec(s); s.loader.exec_module(m)')
            imported = subprocess.run([sys.executable, '-B', '-c', code], cwd=root,
                                      capture_output=True, text=True)
            self.assertEqual(imported.returncode, 0, imported.stderr)
            self.assertEqual(hashes(), before, 'import must not replay historical writes')
            direct = subprocess.run([sys.executable, '-B', script], cwd=root,
                                    capture_output=True, text=True)
            self.assertNotEqual(direct.returncode, 0, 'historical mutation script must be retired')
            self.assertEqual(hashes(), before)
            self.assertIn('retired', direct.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
