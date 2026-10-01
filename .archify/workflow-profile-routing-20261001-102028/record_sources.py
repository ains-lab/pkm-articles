"""Record documentation fingerprints only; never run a Gateway/API/model."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs/techblog/hermes-api-gateway-workdir-assoc'
paths = sorted(p for p in DOCS.rglob('*') if p.is_file())
manifest = {
    'kind': 'documentation-design-baseline',
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'scope': 'Existing documentation and slide artifacts; no live service claims',
    'files': [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                   sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],
}
target = OUT / 'source-baseline.json'
with target.open('x') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'baseline': str(target), 'file_count': len(paths)}))
