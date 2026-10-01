"""Capture actual unittest result and exact source bytes without overwriting evidence."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

runtime = Path(__file__).resolve().parents[1]
out = runtime / 'publisher-evidence' / sys.argv[1]
out.mkdir(exist_ok=False)
files = {}
for name in ('publication.py','test_publication.py','p3_common.py'):
    p = runtime / name
    if p.exists():
        raw = p.read_bytes()
        (out / name).write_bytes(raw)
        files[name] = hashlib.sha256(raw).hexdigest()
root = runtime.parents[4]
legacy = root / '_meta/runs/wiki/20260929T083140Z-p2-resume'
helpers = {n:hashlib.sha256((legacy/n).read_bytes()).hexdigest() for n in ('publish-one.py','compile-one.py','verify-one.py')}
command = [sys.executable,'-B','-m','unittest',*(sys.argv[2:] or ['test_publication']),'-v']
p = subprocess.run(command,cwd=runtime,text=True,capture_output=True)
(out / 'output.txt').write_text(p.stdout+p.stderr)
(out / 'result.json').write_text(json.dumps(dict(command=command,cwd=str(runtime),exit_code=p.returncode,
    source_sha256=files,legacy_sha256=helpers,observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2))
print(p.stdout+p.stderr)
print('EXIT',p.returncode,'EVIDENCE',out)
sys.exit(p.returncode)
