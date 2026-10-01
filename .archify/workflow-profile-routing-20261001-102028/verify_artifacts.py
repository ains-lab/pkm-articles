"""Verify actual delivered bytes and local docs; no Gateway/API requests."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
DOCS = ROOT / 'docs/techblog/hermes-api-gateway-workdir-assoc'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

artifacts = []
for folder, review, kind in [
    ('03-api-sequence', 'label-review', 'sequence'),
    ('02-profile-map', 'review-3', 'workflow'),
]:
    d = OUT / folder
    r = d / review
    spec, html = d / 'candidate.json', d / 'diagram.html'
    final = load(r / 'diagram.finalize.json')
    assert final['ok'] and final['status'] == 'pass'
    assert final['type'] == kind
    assert final['specification']['sha256'] == digest(spec)
    assert final['artifact']['sha256'] == digest(html)
    assert final['artifact']['bytes'] == html.stat().st_size
    for stage in ('validate', 'deliver', 'check', 'browser-check'):
        assert final['stages'][stage]['status'] == 'pass', (folder, stage)
    validation = final['stages']['deliver']['receipt']['validation']
    assert validation['checksPassed'] == validation['checkCount'] == 9
    assert validation['errors'] == validation['warnings'] == 0
    evidence = []
    for p in (r / 'diagram.browser-check.json', r / 'visual-check/diagram.visual-check.json'):
        e = load(p)
        assert e['ok'] and e['status'] == 'pass'
        assert e['artifact']['sha256'] == digest(html)
        assert e['provenance'] == 'current'
        evidence.append(str(p.relative_to(ROOT)))
    artifacts.append(dict(type=kind, html=str(html.relative_to(ROOT)),
        specification=str(spec.relative_to(ROOT)), sha256=digest(html),
        specification_sha256=digest(spec), validation=validation,
        finalize=str((r / 'diagram.finalize.json').relative_to(ROOT)), evidence=evidence))
assert len(artifacts) == 2
assert len({a['html'] for a in artifacts}) == 2

baseline = load(OUT / 'source-baseline.json')
changed = []
for entry in baseline['files']:
    p = ROOT / entry['path']
    assert p.is_file(), entry['path']
    if digest(p) != entry['sha256']:
        changed.append(entry['path'])
assert changed == ['docs/techblog/hermes-api-gateway-workdir-assoc/ARCHIFY.md'], changed

links = []
for name in ('PROFILE-ROUTING.md', 'ARCHIFY.md'):
    p = DOCS / name
    text = p.read_text()
    assert text.count('```') % 2 == 0
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if target.startswith(('https://', 'http://', '#')):
            continue
        q = (p.parent / target.split('#')[0]).resolve()
        # This script creates the linked report after all assertions pass.
        assert q == OUT / 'verification.json' or q.is_file(), (name, target)
        links.append(dict(document=name, target=target))
seq = load(OUT / '03-api-sequence/candidate.json')
assert len({m['id'] for m in seq['messages']}) == len(seq['messages'])
assert all(m['from'] != m['to'] for m in seq['messages'])
visible = json.dumps(seq['segments'], ensure_ascii=False) + ' '.join(m['label'] for m in seq['messages'])
for required in ('terminal.cwd=/home/ainsdev/wiki/pkm-articles', 'P 설정·cwd 해석', 'cwd 기준 경로 검사·읽기', '202', 'SSE', 'GET R', '상태·답변·근거'):
    assert required in visible, required
report = dict(
    status='pass', verified_at=datetime.now(timezone.utc).isoformat(),
    delivered_count=len(artifacts), artifacts=artifacts,
    preserved_document_slide_files=len(baseline['files']) - len(changed),
    baseline_file_count=len(baseline['files']), intentional_existing_doc_changes=changed,
    local_link_count=len(links), links=links,
    actual_live_api_tests=False, deployment=False,
    perceptual_review='sampled; see visual-review.json; not mobile/accessibility/full-card PASS',
    excluded_draft='01-roundtrip: failed workflow geometry; replaced by delivered sequence',
)
(OUT / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('status','delivered_count','baseline_file_count','preserved_document_slide_files','local_link_count','actual_live_api_tests')}, ensure_ascii=False))
