"""Isolated unittest runner; immutable evidence, deny live paper/network IO."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import socket
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/ainsdev/wiki/pkm-articles')
sys.dont_write_bytecode = True

def main():
    p = argparse.ArgumentParser()
    p.add_argument('label')
    p.add_argument('modules', nargs='+')
    args = p.parse_args()
    if not args.label.replace('-', '').replace('_', '').isalnum():
        raise ValueError('invalid label')
    dest = HERE / 'parent-evidence' / args.label
    dest.mkdir(parents=True, exist_ok=False)
    snapshots = {}
    for name in ['p3_common.py', 'daily.py', 'content.py', 'publication.py', 'run_checks.py'] + list(dict.fromkeys(x.split('.')[0]+'.py' for x in args.modules)):
        file = HERE / name
        if file.is_file():
            data = file.read_bytes()
            (dest / (file.name+'.snapshot')).write_bytes(data)
            snapshots[file.name] = hashlib.sha256(data).hexdigest()
    observations = {'network_attempts': 0, 'real_source_body_attempts': 0}
    def audit(event, values):
        if event in ('socket.connect', 'socket.bind', 'socket.getaddrinfo'):
            observations['network_attempts'] += 1
            raise RuntimeError('network forbidden in synthetic tests')
        if event == 'open' and isinstance(values[0], (str, bytes)):
            path = Path(values[0].decode() if isinstance(values[0], bytes) else values[0]).absolute()
            if path.is_relative_to(ROOT/'raw') and path.name in ('source.html','source.pdf'):
                observations['real_source_body_attempts'] += 1
                raise RuntimeError('live paper body forbidden in synthetic tests')
    sys.addaudithook(audit)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromNames(args.modules)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    output = stream.getvalue()
    (dest/'output.txt').write_text(output)
    evidence = dict(schema='pkm-p3-synthetic-tests/v1', observed_at=datetime.now(timezone.utc).isoformat(),
        label=args.label, modules=args.modules, tests_run=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
        exit_code=0 if result.wasSuccessful() else 1, interpreter=sys.executable,
        snapshots=snapshots, observed_boundaries=observations, synthetic_only=True)
    (dest/'counts.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(output)
    print(json.dumps(evidence))
    return evidence['exit_code']

if __name__ == '__main__':
    raise SystemExit(main())
