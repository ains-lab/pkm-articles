from pathlib import Path
import hashlib
import json
from collections import Counter

ROOT = Path('/home/ainsdev/wiki/pkm-articles')
BASE = ROOT / '.archify/workflow-hermes-wiki-20261001-031930'
DOC = ROOT / 'docs/techblog/hermes-api-gateway-workdir-assoc'
READ_DOCS = ['workflows.md', 'api-contract.md', 'architecture.md', 'data-contracts.md', 'security-and-operations.md', 'frontend-design.md', 'evidence.md']

def digest(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

results = []
for folder in ('03-read', '04-query'):
    home = BASE / folder
    candidate = json.loads((home / 'candidate.json').read_text())
    evidence = json.loads((home / 'evidence.json').read_text())
    summary = json.loads((home / 'diagram.finalize-summary.json').read_text())
    full = json.loads((home / 'diagram.finalize.json').read_text())
    browser = json.loads((home / 'diagram.browser-check.json').read_text())
    delivery = json.loads((home / 'diagram.delivery.json').read_text())
    assert summary['ok'] and summary['status'] == 'pass'
    assert all(v == 'pass' for v in summary['gates'].values())
    assert all(stage['status'] == 'pass' and stage['exitCode'] == 0 for stage in full['stages'].values())
    validation = full['stages']['validate']['receipt']['validation']
    assert validation['checksPassed'] == validation['checkCount'] == 9
    assert validation['warnings'] == validation['errors'] == 0
    assert browser['status'] == 'pass'
    assert candidate['meta']['quality_profile'] == 'showcase'
    assert 'repository' not in candidate['meta'] and 'animation' not in candidate['meta']
    assert (ROOT / candidate['meta']['output']).resolve() == home / 'diagram.html'
    spec_hash = digest(home / 'candidate.json')
    artifact_hash = digest(home / 'diagram.html')
    assert spec_hash['sha256'] == summary['specification']['sha256'] == delivery['specification']['sha256'] == evidence['candidate_sha256']
    assert artifact_hash['sha256'] == summary['artifact']['sha256'] == delivery['artifact']['sha256']
    assert spec_hash['bytes'] == summary['specification']['bytes']
    assert artifact_hash['bytes'] == summary['artifact']['bytes']
    expected = {('node', item['id']) for item in candidate['nodes']} | {('edge', item['id']) for item in candidate['edges']}
    mapped = {(entry['element_type'], entry['element_id']) for entry in evidence['entries']}
    assert expected == mapped and len(evidence['entries']) == len(expected)
    classes = Counter()
    refs_checked = 0
    for entry in evidence['entries']:
        assert entry['references']
        for ref in entry['references']:
            lines = (ROOT / ref['path']).read_text().splitlines()
            assert 1 <= ref['line'] <= ref['end_line'] <= len(lines)
            assert ref['classification'] in {'관측', '공식계약', '제안', '미확인'}
            classes[ref['classification']] += 1
            refs_checked += 1
    for source in evidence['source_manifest']:
        identity = digest(ROOT / source['path'])
        assert identity['sha256'] == source['sha256'] and identity['bytes'] == source['bytes']
    source_files = []
    for doc in READ_DOCS:
        record = digest(DOC / doc)
        record['path'] = str((DOC / doc).relative_to(ROOT))
        record['lines'] = len((DOC / doc).read_text().splitlines())
        source_files.append(record)
    summary_output = {
        'schema': 'archify-document-handoff/v1', 'status': 'passed', 'folder': folder,
        'diagram_type': 'workflow', 'mode': 'document-description',
        'files': {name: digest(home / name) for name in ('candidate.json', 'diagram.html', 'evidence.json', 'diagram.finalize-summary.json', 'diagram.finalize.json', 'diagram.browser-check.json', 'diagram.delivery.json')},
        'counts': {'nodes': len(candidate['nodes']), 'edges': len(candidate['edges']), 'mapped_elements': len(mapped), 'unmapped_elements': 0, 'source_references_checked': refs_checked, 'read_source_documents': len(source_files)},
        'source_classification_counts': dict(classes), 'source_manifest': source_files,
        'validation': validation, 'gates': summary['gates'],
        'browser_evidence': 'passed', 'visual_review': 'not_requested', 'visual_correction_rounds': 0,
        'browser_environment': {'executable': '/home/ainsdev/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', 'ARCHIFY_CHROME_NO_SANDBOX': '1', 'caveat': '호스트 user-namespace sandbox 불가 환경에 대응하여 신뢰된 자체 생성 HTML 검증 프로세스에만 no-sandbox를 사용했다. 설치·전역 설정·Archify 소스 변경 없음.'},
        'update': summary['update'],
        'unresolved': ['BFF/UI/read facade/격리는 문서상 제안이며 미구현·서비스 live 검증 없음.', '한국어 내용, 고정 Viewer UI와 html lang English fallback.', 'Perceptual review 미실시. 통과 receipt의 route detour 권고는 시각 품질 확인을 대신하지 않음.'],
        'route_review_advisory': summary.get('visualReviewRecommendation'),
        'scope': '두 새 diagram 폴더 안에만 작성. 공통 문서·Gateway·config·live API·모델·논문·Cron·기존 slide 변경/실행 없음.'
    }
    output = home / 'handoff-verification.json'
    output.write_text(json.dumps(summary_output, ensure_ascii=False, indent=2) + '\n')
    results.append({'folder': folder, 'status': 'passed', 'counts': summary_output['counts'], 'validation': validation, 'specification': spec_hash, 'artifact': artifact_hash, 'source_map': digest(home / 'evidence.json'), 'summary_receipt': str(home / 'diagram.finalize-summary.json'), 'handoff_receipt': str(output), 'update_notice_required': summary['update']['noticeRequired']})
print(json.dumps({'diagrams_verified': len(results), 'results': results}, ensure_ascii=False, indent=2))
