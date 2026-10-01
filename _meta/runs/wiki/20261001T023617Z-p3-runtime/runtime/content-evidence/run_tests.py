"""Capture actual isolated content test output and immutable code snapshots."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

here = Path(__file__).resolve().parent.parent
label = sys.argv[1]
tests = sys.argv[2:] or ['test_content']
target = here / 'content-evidence' / label
target.mkdir(exist_ok=False)
for name in ('content.py', 'test_content.py', 'p3_common.py'):
    path = here / name
    if path.exists():
        shutil.copyfile(path, target / name)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
command = [sys.executable, '-B', '-m', 'unittest', '-v', *tests]
result = subprocess.run(command, cwd=here, env=env, capture_output=True, timeout=120)
(target / 'stdout.txt').write_bytes(result.stdout)
(target / 'stderr.txt').write_bytes(result.stderr)
manifest = dict(command=command, cwd=str(here), returncode=result.returncode,
    evidence_kind='synthetic_only_execution', live_model_calls=0,
    snapshots={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir() if p.is_file()})
(target / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(result.stdout.decode(), end='')
print(result.stderr.decode(), end='')
print(json.dumps(manifest, indent=2))
sys.exit(result.returncode)
