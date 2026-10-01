#!/usr/bin/env python3
"""Build the offline lecture from authored content. Does not run document commands."""
import base64
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from course_a import SLIDES as A
from course_b import SLIDES as B
from course_c import SLIDES as C
from diagram_art import render

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent
SLIDES=A+B+C
E=html.escape

def digest(data): return hashlib.sha256(data).hexdigest()
def bullets(items):
    rows=[]
    for item in items:
        rows.append('<li>'+ ('<strong>'+E(item[0])+'</strong>'+E(item[1]) if isinstance(item,list) else E(item))+'</li>')
    return '<ul class="bullets">'+''.join(rows)+'</ul>'

def content(s):
    kind=s['kind']
    if kind=='hero': return ''.join('<p class="hero-line">'+E(x)+'</p>' for x in s['items'])
    if kind=='bullets': return bullets(s['items'])
    if kind=='table':
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+E(s['title'])+' 표"><table><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in s['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>' for row in s['rows'])+'</tbody></table></div>'
    if kind=='compare': return '<div class="columns">'+''.join('<section class="column"><h3>'+E(col[0])+'</h3><ul>'+''.join('<li>'+E(x)+'</li>' for x in col[1:])+'</ul></section>' for col in s['columns'])+'</div>'
    if kind=='code': return '<div class="code-layout"><pre class="code-scroll" tabindex="0" aria-label="설명용 코드, 실행하지 않음"><code>'+E(s['code'])+'</code></pre>'+bullets(s['items'])+'</div>'
    if kind=='diagram': return render(s['diagram'])
    if kind=='exercise': return '<p class="question">'+E(s['prompt'])+'</p><details><summary>해설 보기 / 닫기</summary><p class="answer">'+E(s['answer'])+'</p></details>'
    raise ValueError(kind)

def main():
    sourcefiles=sorted([*SOURCE.glob('*.md'),SOURCE/'verification.json'])
    assert len(sourcefiles)==13
    sourceinfo={p.name:dict(sha256=digest(p.read_bytes()),lines=len(p.read_text().splitlines())) for p in sourcefiles}
    baseline=HERE/'source-baseline.json'
    if baseline.exists():
        old=json.loads(baseline.read_text())['files']
        assert old==sourceinfo, 'Technical source changed; stop and review before rebuilding.'
    else:
        baseline.write_text(json.dumps(dict(observed_at=datetime.now(timezone.utc).isoformat(),files=sourceinfo),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    excerpts={}; coverage={p.name:[] for p in sourcefiles}; sections=[]
    for i,s in enumerate(SLIDES,1):
        for ref in s['refs']:
            m=re.fullmatch(r'([\w.-]+):(\d+)-(\d+)',ref); assert m,ref
            f,start,end=m.group(1),int(m.group(2)),int(m.group(3))
            lines=(SOURCE/f).read_text().splitlines();assert 1<=start<=end<=len(lines),ref
            excerpts[ref]=dict(file=f,text='\n'.join(f'{j} | {lines[j-1]}' for j in range(start,end+1)))
            coverage[f].append(i)
        title_tag='h1' if i==1 else 'h2'
        status=s.get('status','문서 기반')
        takeaway='<p class="takeaway">'+E(s['takeaway'])+'</p>' if s.get('takeaway') else ''
        refs=E(json.dumps(s['refs'],ensure_ascii=False),quote=True)
        label=' · '.join(s['refs'])
        sections.append(f'<section id="slide-{i}" class="slide {s["kind"]}" data-title="{E(s["title"],quote=True)}" data-chapter="{E(s["chapter"],quote=True)}" aria-labelledby="heading-{i}"'+(' hidden' if i>1 else '')+f'><div class="meta"><span>{E(s["chapter"])}</span><span class="status">{E(status)}</span></div><{title_tag} id="heading-{i}" tabindex="-1">{E(s["title"])}</{title_tag}><p class="lead">{E(s["lead"])}</p><div class="content">{content(s)}</div>{takeaway}<footer class="footer"><div><button type="button" data-sources="{refs}">근거 {len(s["refs"])}곳</button> <span class="source-label">{E(label)}</span></div><span class="page">{i:02d} / {len(SLIDES)}</span></footer></section>')
    assert all(coverage.values()),coverage
    fontpath=HERE/'lecture-korean.woff2'
    font=fontpath.read_bytes()
    full_license=Path('/usr/share/doc/fonts-nanum/copyright').read_text()
    # Preserve only the complete font copyright/OFL block, not unrelated Debian packaging license.
    license_text=full_license.split('Files: debian/*')[0].rstrip()+'\n'
    (HERE/'FONT-LICENSE.txt').write_text(license_text,encoding='utf-8')
    fontstyle='@font-face{font-family:LectureKorean;src:url(data:font/woff2;base64,'+base64.b64encode(font).decode()+') format("woff2");font-weight:400;font-style:normal;font-display:block}'
    css=(HERE/'deck.css').read_text(); js=(HERE/'deck.js').read_text()
    sourcejson=json.dumps(dict(excerpts=excerpts,files=sourceinfo),ensure_ascii=False).replace('<','\\u003c')
    head='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="Hermes API Gateway와 파일 Wiki 연결 설계: 한국어 강의용 오프라인 슬라이드"><title>Wiki × Hermes API Gateway — 기술 설계 강의</title><style>'+fontstyle+'\n'+css+'</style></head><body>'
    nav='<a class="skip" href="#heading-1">슬라이드 본문으로</a><div id="announcer" class="sr-only" aria-live="polite" aria-atomic="true"></div><main id="stage" class="stage" aria-label="강의 슬라이드"><div class="deck">'+''.join(sections)+'</div></main><div id="progress" class="progress" aria-hidden="true"></div><nav class="toolbar" aria-label="슬라이드 조작"><button id="prev" aria-label="이전 슬라이드">← 이전</button><output id="slide-count" class="count" aria-label="현재 슬라이드"></output><button id="next" aria-label="다음 슬라이드">다음 →</button><button id="contents-button" class="secondary" aria-label="목차 열기 (T)">목차</button><button id="fullscreen-button" aria-label="전체화면 (F)">전체화면</button><button id="print-button">인쇄</button><button id="help-button" aria-label="도움말 (?)">?</button></nav>'
    toc='<dialog id="toc-dialog" aria-labelledby="toc-title"><div class="dialog-head"><h2 id="toc-title">강의 목차</h2><button data-close aria-label="목차 닫기">닫기</button></div><label for="search">슬라이드 제목·주제 검색</label><input id="search" type="search" autocomplete="off" placeholder="예: SSE, cwd, 게시"><p id="search-result" role="status">전체 슬라이드</p><p id="search-empty" hidden>검색 결과가 없습니다. 다른 단어를 입력하세요.</p><ol id="toc-list"></ol></dialog>'
    sourcedialog='<dialog id="source-dialog" aria-labelledby="source-title"><div class="dialog-head"><h2 id="source-title">원문 근거</h2><button data-close aria-label="근거 닫기">닫기</button></div><div id="source-body" class="dialog-body"></div></dialog>'
    helpdialog='<dialog id="help-dialog" aria-labelledby="help-title"><div class="dialog-head"><h2 id="help-title">강의 자료 사용법</h2><button data-close aria-label="도움말 닫기">닫기</button></div><p>방향키 / PageUp·PageDown / Space: 이동<br>Home·End: 처음·마지막<br>T: 목차 · F: 전체화면 · ?: 도움말 · Escape: 대화상자 닫기</p><p>버튼·입력·도식에 초점이 있으면 해당 요소의 키보드 동작을 우선합니다. 도식·표는 좁은 화면에서 가로로 스크롤할 수 있습니다. 마지막 슬라이드만 로컬 브라우저에 기억하며 저장소가 차단되어도 사용할 수 있습니다.</p><p>각 장의 설계 실습은 실제 요청을 보내지 않습니다. 해설은 클릭해서 펼치며 인쇄에는 모두 포함됩니다. 브라우저 인쇄는 슬라이드당 한 페이지입니다. 헤더/푸터는 끄고 배경 그래픽을 켜면 화면 색상을 유지할 수 있습니다.</p><p>HTML 단독 오프라인 사용 가능. 외부 폰트·CDN·분석 스크립트·API 연결 없음. 원문 링크를 클릭할 때만 해당 문서로 이동합니다.</p><details><summary>내장 폰트 저작권·라이선스</summary><pre id="license">'+E(license_text)+'</pre></details></dialog>'
    nojs='<noscript><p>JavaScript가 꺼져 있어 첫 슬라이드만 표시됩니다. 전체 강의 탐색에는 JavaScript를 켜거나 브라우저 인쇄를 사용하세요.</p></noscript>'
    output=head+nav+toc+sourcedialog+helpdialog+nojs+'<script id="source-data" type="application/json">'+sourcejson+'</script><script>'+js+'</script></body></html>\n'
    out=HERE/'lecture.html';out.write_text(output,encoding='utf-8')
    metadata=dict(schema='lecture-source-map/v1',scope='Supplied technical documentation; not a live Hermes capability audit',slide_count=len(SLIDES),chapters=dict(Counter(s['chapter'] for s in SLIDES)),kinds=dict(Counter(s['kind'] for s in SLIDES)),artifact=dict(file=out.name,sha256=digest(out.read_bytes()),bytes=out.stat().st_size),font=dict(path=str(fontpath),sha256=digest(font),renamed_subset=True,license='OFL-1.1'),sources=sourceinfo,coverage=coverage,slides=[dict(number=i,**s) for i,s in enumerate(SLIDES,1)])
    (HERE/'source-map.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    outline=['# 강의 슬라이드 목차','', '원문 기술문서 기준의 강의 구성. 실습은 합성 설계 과제이며 실제 서비스를 실행하지 않는다.','']
    last=''
    for i,s in enumerate(SLIDES,1):
        if s['chapter']!=last: outline+=['','## '+s['chapter'],''];last=s['chapter']
        outline+= [f'- [{i:02d}. {s["title"]}](lecture.html#slide-{i}) — {s["lead"]}']
    (HERE/'OUTLINE.md').write_text('\n'.join(outline)+'\n',encoding='utf-8')
    print(json.dumps({k:metadata[k] for k in ['slide_count','chapters','kinds','artifact']},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
