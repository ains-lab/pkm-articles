"""Run synthetic unittest evidence with exact counts; no live model or papers."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
here = Path(__file__).parent
label = sys.argv[1]
if not label.replace('-', '').replace('_', '').isalnum():
    raise SystemExit('unsafe label')
dest = here / 'evidence' / label
dest.mkdir(parents=True, exist_ok=False)
for name in ('manual_pdf.py', 'test_manual_pdf.py', 'run_tests.py'):
    p = here / name
    if p.exists():
        (dest / (name + '.snapshot')).write_bytes(p.read_bytes())
spec = importlib.util.spec_from_file_location('pdf_tests', here / 'test_manual_pdf.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = (unittest.defaultTestLoader.loadTestsFromNames(sys.argv[2:], module) if len(sys.argv) > 2
         else unittest.defaultTestLoader.loadTestsFromModule(module))
log = io.StringIO()
import socket
from unittest.mock import patch
counters = {'network_attempts': 0, 'real_pdf_read_attempts': 0, 'synthetic_pdf_reads': 0}
root = Path('/home/ainsdev/wiki/pkm-articles')
legacy = root / '_meta/runs/wiki/20260929T083140Z-p2-resume'
protected = {str(legacy/n): hashlib.sha256((legacy/n).read_bytes()).hexdigest()
             for n in ('compile-one.py','verify-one.py','publish-one.py')}
def deny_network(*args, **kw):
    counters['network_attempts'] += 1
    raise AssertionError('network forbidden in synthetic tests')
files = module.M.helper('publish').Files if module.M is not None else None
original_read = files.read if files is not None else None
def bounded_read(fs, path, *args, **kw):
    if str(path).endswith('.pdf'):
        if not fs.root.is_relative_to(here) or not fs.root.name.startswith('synthetic-'):
            counters['real_pdf_read_attempts'] += 1
            raise AssertionError('real PDF read forbidden')
        counters['synthetic_pdf_reads'] += 1
    return original_read(fs, path, *args, **kw)
with patch.object(socket.socket, 'connect', deny_network), patch.object(socket.socket, 'connect_ex', deny_network):
    if files is None:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    else:
        with patch.object(files, 'read', bounded_read):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
protected_unchanged = all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p,h in protected.items())
(dest / 'output.txt').write_text(log.getvalue())
report = dict(schema='synthetic-pdf-test-evidence/v1', label=label, tests_run=result.testsRun,
    failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
    exit_code=0 if result.wasSuccessful() and protected_unchanged and not counters['network_attempts'] and not counters['real_pdf_read_attempts'] else 1,
    synthetic_only=True, observed_boundaries=counters, legacy_helpers_unchanged=protected_unchanged, legacy_sha256=protected,
    interpreter=sys.executable, python_version=sys.version,
    snapshots={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.glob('*.snapshot')})
(dest / 'counts.json').write_text(json.dumps(report, indent=2)+'\n')
print(log.getvalue())
print(json.dumps(report))
raise SystemExit(report['exit_code'])
