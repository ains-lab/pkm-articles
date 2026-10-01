"""Shared P3 constants and unchanged legacy IO utilities; import has no IO."""
import functools
import os
from pathlib import Path
import time
import types

ROOT = Path('/home/ainsdev/wiki/pkm-articles')
RUN = '_meta/runs/wiki/20261001T060423Z-p3-auto-activation'
POLICY = 'pkm-html-pdf-text-knowledge/v3'
CONTRACT = 'pkm-contracts/v3'
PROMPT_REV = 'wiki-compile/v3'
PROMPT = '_meta/prompts/wiki-compile.md'
STATE = '_meta/state/compilation.json'
PUBLISHED_STATUSES = ('published_draft', 'published_auto_verified')
SCOPE = 'P3 main-text complete'
MODEL = dict(provider='codex-lb', model='gpt-6-astra', reasoning_effort='xhigh', fallback_allowed=False)
ROUTE = dict(base_url='http://10.10.1.244:2455/v1', api_mode='codex_responses')
DOCS = ('AGENTS.md', 'SCHEMA.md', '_meta/AUTOMATION.md', '_meta/COMPILATION.md',
        '_meta/STATE-CONTRACTS.md', '_meta/automation-contracts.schema.json')
PDF_READING = dict(mode='embedded_text_only', library='pypdf', environment='.venv-pdf-reader',
    pdf_binary_transfer=False, images=False, ocr=False, external_assets=False,
    persistent_extraction=False, page_citation='physical_1_based')

def require(ok, code):
    if not ok:
        raise ValueError(code)

@functools.lru_cache(maxsize=3)
def helper(name):
    require(name in ('publish','compile','verify'), 'unknown helper')
    path = ROOT / '_meta/runs/wiki/20260929T083140Z-p2-resume' / (name+'-one.py')
    require(all(not p.is_symlink() for p in (path, *path.parents)), 'unsafe helper')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        import stat
        st = os.fstat(stream.fileno())
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, 'unsafe helper file')
        module = types.ModuleType('_p3_legacy_'+name)
        module.__file__ = str(path)
        exec(compile(stream.read(), str(path), 'exec'), module.__dict__)
        return module

def sha(data):
    return helper('publish').sha(data)

def encoded(value):
    return helper('publish').encoded(value)

def canonical(value):
    return helper('publish').canonical(value)

def decode(data):
    return helper('publish').decode(data)

def synthetic_root(root):
    root = Path(os.path.abspath(root))
    require(root.parent == ROOT/RUN/'runtime' and root.name.startswith('synthetic-'), 'synthetic root required')
    helper('publish').Files(root)
    return root

def ensure_dirs(fs, path):
    parts = fs.parts(path)
    current = fs.root
    for part in parts:
        current /= part
        helper('compile').mkdir_no_links(current, exist_ok=True)

def check_deadline(deadline, clock=time.monotonic):
    if deadline is not None and clock() >= deadline:
        raise TimeoutError('cooperative deadline')
