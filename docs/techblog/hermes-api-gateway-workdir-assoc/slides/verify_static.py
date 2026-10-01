#!/usr/bin/env python3
"""Static checks for the generated lecture, not for the described web service."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import unquote
import hashlib,json,re
ROOT=Path(__file__).resolve().parent
class Check(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.external=[];self.sections=[];self.svgs=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.links.append(a['href'])
        if tag in ['script','img','iframe','link','audio','video','source']:
            v=a.get('src',a.get('href',''))
            if v and not v.startswith('data:'):self.external.append((tag,v))
        if tag=='section' and 'slide' in (a.get('class') or '').split():self.sections.append(a)
        if tag=='svg':self.svgs+=1

def main():
    html=(ROOT/'lecture.html').read_text();p=Check();p.feed(html)
    meta=json.loads((ROOT/'source-map.json').read_text());baseline=json.loads((ROOT/'source-baseline.json').read_text())
    errors=[]
    if len(p.sections)!=meta['slide_count']:errors.append('slide count')
    if len(set(p.ids))!=len(p.ids):errors.append('duplicate IDs')
    if p.external:errors.append(['external resources',p.external])
    for link in p.links:
        if link.startswith('#') and unquote(link[1:]) not in p.ids:errors.append(['broken fragment',link])
        elif link and not link.startswith(('#','https:','http:','data:')) and not (ROOT/link.split('#')[0]).exists():errors.append(['broken local link',link])
    for f,info in baseline['files'].items():
        if hashlib.sha256((ROOT.parent/f).read_bytes()).hexdigest()!=info['sha256']:errors.append(['source changed',f])
    if not all(meta['coverage'].values()):errors.append('uncovered input source')
    if len(meta['sources'])!=13:errors.append('input inventory mismatch')
    expected=[f'slide-{i}' for i in range(1,len(p.sections)+1)]
    if [s['id'] for s in p.sections]!=expected:errors.append('slide ordering')
    for s in meta['slides']:
        if not s['refs']:errors.append(['missing sources',s['number']])
        if s['kind']=='table' and any(len(row)!=len(s['headers']) for row in s['rows']):errors.append(['bad table',s['number']])
    # The teaching SSE multi-line data frame must decode to a real JSON object.
    wire=next(s['code'] for s in meta['slides'] if s['title']=='HTTP chunk는 메시지 경계가 아니다')
    event=json.loads('\n'.join(line[6:] for line in wire.split('\n\n')[0].splitlines() if line.startswith('data: ')))
    assert event['event']=='message.delta' and event['delta']=='한글'
    json.loads(next(s['code'] for s in meta['slides'] if s['title']=='DTO: 필요한 필드만 공개한다'))
    result={'scope':'lecture artifact only','artifact_sha256':hashlib.sha256((ROOT/'lecture.html').read_bytes()).hexdigest(),'slide_count':len(p.sections),'diagram_count':p.svgs,'exercise_count':meta['kinds']['exercise'],'source_count':len(meta['sources']),'all_sources_preserved':not any(isinstance(e,list) and e[0]=='source changed' for e in errors),'coverage_complete':all(meta['coverage'].values()),'external_resource_references':p.external,'duplicate_ids':len(p.ids)-len(set(p.ids)),'sse_example_json_valid':True,'errors':errors,'result':'pass' if not errors else 'fail'}
    (ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa/static.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2));assert not errors,errors
if __name__=='__main__':main()
