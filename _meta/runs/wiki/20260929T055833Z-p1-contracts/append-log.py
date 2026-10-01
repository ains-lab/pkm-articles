from pathlib import Path
import hashlib, os
root = Path('/home/ainsdev/wiki/pkm-articles')
p = root / 'log.md'
entry = (root / '_meta/runs/wiki/20260929T055833Z-p1-contracts/log-entry.md').read_text()
old = p.read_bytes()
assert not old.endswith(b'\n\n')
with p.open('ab') as f:
    f.write(('\n' + entry).encode())
    f.flush()
fd = os.open(p, os.O_RDONLY); os.fsync(fd); os.close(fd)
new = p.read_bytes()
assert new.startswith(old) and hashlib.sha256(new).hexdigest() != hashlib.sha256(old).hexdigest()
print('appended', len(new) - len(old), 'bytes; prefix preserved')
