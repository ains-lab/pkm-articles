"""Verify exact delivered bytes and documentation; never call Hermes API."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
DOC = ROOT / 'docs/techblog/hermes-api-gateway-workdir-assoc'
REPORT = OUT / 'verification.json'


def digest(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def load(path):
    return json.loads(path.read_text())


expected = {'01-connect': 'architecture', '02-workdir': 'workflow', '03-query': 'workflow'}
checks = []
artifacts = []
for name, kind in expected.items():
    folder = OUT / name
    evidence_dir = folder / 'review-2' if name == '01-connect' else folder
    final = load(evidence_dir / 'diagram.finalize.json')
    browser = load(evidence_dir / 'diagram.browser-check.json')
    delivery = load(folder / 'diagram.delivery.json')
    capture = load(evidence_dir / 'visual-check/diagram.visual-check.json')
    candidate = load(folder / 'candidate.json')
    spec_hash = digest(folder / 'candidate.json')
    html_hash = digest(folder / 'diagram.html')
    assert final['ok'] and final['status'] == 'pass' and final['type'] == kind
    assert candidate['diagram_type'] == kind and candidate['meta']['locale'] == 'ko'
    assert all(final['stages'][g]['status'] == 'pass' for g in ('validate', 'deliver', 'check', 'browser-check'))
    validation = final['stages']['validate']['receipt']['validation']
    assert validation['checksPassed'] == validation['checkCount'] == 9
    assert validation['errors'] == validation['warnings'] == 0
    for k, v in spec_hash.items():
        assert final['specification'][k] == delivery['specification'][k] == v
    for k, v in html_hash.items():
        assert final['artifact'][k] == delivery['artifact'][k] == browser['artifact'][k] == capture['artifact'][k] == v
    assert browser['ok'] and browser['status'] == 'pass' and browser['provenance'] == 'current'
    assert capture['ok'] and capture['status'] == 'pass'
    viewports = browser['containment']['viewports']
    assert {(v['width'], v['height']) for v in viewports} == {(1440, 900), (1600, 1000), (1920, 1080), (2048, 1320)}
    assert all(v['ok'] and not v['overflowX'] for v in viewports)
    screenshots = sorted((evidence_dir / 'visual-check').glob('*.png'))
    assert len(screenshots) == 4
    artifacts.append({'name': name, 'type': kind, 'output': str(folder / 'diagram.html'),
                      'specification': spec_hash, 'artifact': html_hash, 'validation': validation,
                      'browser_evidence': 'passed', 'browser_executable': browser['chrome']['executable'],
                      'finalize_receipt': str(evidence_dir / 'diagram.finalize.json'),
                      'browser_receipt': str(evidence_dir / 'diagram.browser-check.json'),
                      'capture_receipt': str(evidence_dir / 'visual-check/diagram.visual-check.json'),
                      'screenshots': [{'path': str(p), **digest(p)} for p in screenshots],
                      'viewports': [{'width': v['width'], 'height': v['height'],
                                     'minimumProjectedNodeTextPx': v.get('minimumProjectedNodeTextPx'),
                                     'overflowX': v['overflowX']} for v in viewports],
                      'visual_review': {'status': 'sample_reviewed_with_limitations', 'scope': '1440x900 light, visible first screen only',
                                        'observed': 'No obvious clipped nodes or obstructive overlaps; arrow direction traceable.',
                                        'limitations': ['small/pale supporting text', 'offscreen cards not reviewed', 'mobile not tested', 'all interactions/exports/accessibility not audited']}})
assert len(artifacts) == 3
checks.append({'name': 'requested_diagrams', 'pass': True, 'expected': 3, 'actual': len(artifacts)})

baseline = load(OUT / 'source-baseline.json')['files']
changes = []
for item in baseline:
    actual = digest(ROOT / item['path'])
    if actual['sha256'] != item['sha256']:
        changes.append(item['path'])
allowed = str((DOC / 'ARCHIFY.md').relative_to(ROOT))
assert changes == [allowed], changes
intro = '''## 외부 앱·작업 디렉터리 연동만 먼저 보기

[연동 집중 해설과 그림 3장](INTEGRATION-ARCHIFY.md) — 앱–BFF–Hermes–Wiki 구조, 작업 경로 적용 순서, 질문·SSE·재연결 흐름을 새로 좁혀 그렸다. 아래 기존 전체 지도 8개는 그대로 보존한다. 새 결과 역시 설계 시각화이며 서비스 적용·배포가 아니다.

## 기존 전체 지도

'''
archify = (DOC / 'ARCHIFY.md').read_text()
assert archify.count(intro) == 1
original = archify.replace(intro, '', 1).encode()
assert hashlib.sha256(original).hexdigest() == next(x['sha256'] for x in baseline if x['path'] == allowed)
checks.append({'name': 'original_documents_and_slides', 'pass': True, 'baseline_files': len(baseline),
               'unchanged_files': len(baseline) - len(changes), 'only_additive_navigation_change': allowed})

source_evidence = load(OUT / 'evidence.json')
for item in source_evidence['sources']:
    lines = (ROOT / item['path']).read_text().splitlines()
    for start, end in item['ranges']:
        assert 1 <= start <= end <= len(lines)
checks.append({'name': 'source_line_ranges', 'pass': True})

links = []
for doc in (DOC / 'ARCHIFY.md', DOC / 'INTEGRATION-ARCHIFY.md'):
    content = doc.read_text()
    assert len(re.findall(r'^```', content, re.M)) % 2 == 0
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
        parts = urlsplit(target)
        if parts.scheme or not parts.path:
            continue
        path = (doc.parent / unquote(parts.path)).resolve()
        assert path.is_relative_to(ROOT)
        assert path.exists() or path == REPORT, path
        links.append({'from': str(doc.relative_to(ROOT)), 'to': str(path.relative_to(ROOT))})
    for code in re.findall(r'```bash\n(.*?)```', content, re.S):
        result = subprocess.run(['bash', '-n'], input=code, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
checks.append({'name': 'local_links_and_fences_and_bash_syntax', 'pass': True, 'link_count': len(links)})

evidence = {
    'schema': 'archify-document-package-verification/v1',
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'result': 'pass', 'diagram_count': len(artifacts), 'artifacts': artifacts, 'checks': checks,
    'basis': 'User-supplied working-tree technical documents + official documentation, not live system topology',
    'current_policy_exception': 'Current SCHEMA latest P3 approval overrides historical unapproved status; web query approval remains separate.',
    'browser_environment': {'executable': artifacts[0]['browser_executable'], 'no_sandbox': True,
                            'scope': 'Only locally generated Archify HTML verification processes; no global setting change'},
    'not_run': source_evidence['not_run'],
    'guide': str(DOC / 'INTEGRATION-ARCHIFY.md'),
    'receipt_note': '01-connect/review-2 contains the current artifact-bound finalizer/browser receipts; older evidence retained.',
    'repair_note': 'Serpentine workflows omit optional left-to-right mainPath annotation; semantic nodes/edges retained. Measured direct-route port repair removed avoidable detours.'
}
REPORT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'result': 'pass', 'diagram_count': len(artifacts), 'checks': checks, 'report': str(REPORT)}, ensure_ascii=False))
