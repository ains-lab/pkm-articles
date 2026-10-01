import json, os, hashlib
ROOT='/home/ainsdev/wiki/pkm-articles'
raw=os.path.join(ROOT,'raw/articles/4cff5b4f10ec')
html=pdf=0; problems=[]
for d in sorted(os.listdir(raw)):
    if not d.startswith('arxiv-'): continue
    vid=d[len('arxiv-'):]
    p=os.path.join(raw,d)
    files=sorted(os.listdir(p))
    sj=json.load(open(os.path.join(p,'source.json')))
    if sj['version_id']!=vid: problems.append(f'{vid}: id mismatch')
    if 'source.html' in files:
        b=open(os.path.join(p,'source.html'),'rb').read()
        if hashlib.sha256(b).hexdigest()!=sj.get('html_sha256') or len(b)!=sj.get('html_bytes'):
            problems.append(f'{vid}: html hash/bytes mismatch')
        if 'source.pdf' in files: problems.append(f'{vid}: both formats')
        html+=1
    elif 'source.pdf' in files:
        b=open(os.path.join(p,'source.pdf'),'rb').read()
        if hashlib.sha256(b).hexdigest()!=sj.get('pdf_sha256') or len(b)!=sj.get('pdf_bytes'):
            problems.append(f'{vid}: pdf hash/bytes mismatch')
        pdf+=1
    else:
        problems.append(f'{vid}: no original')
    if files not in (['source.html','source.json'],['source.json','source.pdf']):
        problems.append(f'{vid}: unexpected files {files}')
st=json.load(open(os.path.join(ROOT,'_meta/state/4cff5b4f10ec.json')))
print(f'FINAL: html={html} pdf={pdf} total={html+pdf} problems={problems}')
print('state.pending:', len(st['pending']), '| daily 0930 attempts:', len(st['daily_attempts']['2026-09-30']))
print('checkpoint:', st['discovered_through'], '| safety_block:', st['safety_block'])
print('last_run:', st['last_run']['run_id'], st['last_run']['status'])
stg=os.path.join(ROOT,'_meta/staging/4cff5b4f10ec')
print('staging dirs:', os.listdir(stg) if os.path.exists(stg) else 'none')
print('lock exists:', os.path.exists(os.path.join(ROOT,'_meta/locks/collection.lock')))
owned={d[len('arxiv-'):] for d in os.listdir(raw) if d.startswith('arxiv-')}
pend_ids={p['version_id'] for p in st['pending']}
overlap = pend_ids.intersection(owned)
print('pending vs owned overlap:', overlap if overlap else 'CLEAN (no overlap)')
print('pending ids unique:', len(pend_ids)==len(st['pending']))
for f in ['index.md','raw/articles/4cff5b4f10ec/index.md','log.md']:
    t=open(os.path.join(ROOT,f),encoding='utf-8').read()
    print(f, 'mentions run id:', t.count('20260929T150905Z-fbf97a79'))
