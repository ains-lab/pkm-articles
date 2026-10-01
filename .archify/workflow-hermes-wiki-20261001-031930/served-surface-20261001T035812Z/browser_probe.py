"""Read-only QA for generated HTML. Run via browser_exec with helpers in globals."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# Supplied by browser_exec; annotations do not replace the live helpers.
cdp: Callable[..., Any]
js: Callable[..., Any]
goto_url: Callable[..., Any]
wait_for_load: Callable[..., Any]
fill_input: Callable[..., Any]

BASE = Path('/home/ainsdev/wiki/pkm-articles/.archify/workflow-hermes-wiki-20261001-031930')
OUT = BASE / 'served-surface-20261001T035812Z'


def shot(name):
    path = OUT / name
    path.write_bytes(base64.b64decode(cdp('Page.captureScreenshot', format='png')['data']))
    return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def escape():
    cdp('Input.dispatchKeyEvent', type='keyDown', key='Escape', code='Escape', windowsVirtualKeyCode=27)
    cdp('Input.dispatchKeyEvent', type='keyUp', key='Escape', code='Escape', windowsVirtualKeyCode=27)


def run_surface(name):
    file = BASE / ('index.html' if name == 'index' else name + '/diagram.html')
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    for width, height in [(1440, 900), (375, 812)]:
        cdp('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=False)
        goto_url(file.as_uri())
        wait_for_load()
        cdp('Page.bringToFront')
        js('document.fonts.ready.then(()=>true)')
        initial = js('''(() => {
          const visible = e => {const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&Number(s.opacity)!==0};
          const texts=[...document.querySelectorAll('svg text')].filter(visible);
          const sizes=texts.map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*(m?Math.hypot(m.a,m.b):1)}).sort((a,b)=>a-b);
          return {url:location.href,title:document.title,lang:document.documentElement.lang,theme:document.documentElement.dataset.theme||null,width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,textCount:texts.length,
            svgHorizontalOutside:texts.filter(e=>{const b=e.getBoundingClientRect();return b.left<0||b.right>innerWidth}).map(e=>e.textContent),
            minSvgFontPx:sizes.length?sizes[0]:null,medianSvgFontPx:sizes.length?sizes[Math.floor(sizes.length/2)]:null,
            ordinaryHorizontalOutside:[...document.querySelectorAll('h1,h2,h3,p,li,summary')].filter(visible).filter(e=>{const b=e.getBoundingClientRect();return b.left<0||b.right>innerWidth}).map(e=>e.innerText.slice(0,160)),
            hookPresent:!!window.__surfaceQA};
        })()''')
        row = {'surface':name,'source_lineage':{'repository':'/home/ainsdev/wiki/pkm-articles','artifact':str(file),'sha256':digest},'observed_at':datetime.now(timezone.utc).isoformat(),'viewport':[width,height],'initial':initial,'captures':{'default':shot(f'{name}-{width}-default.png')}}
        if name == 'index':
            cdp('Input.dispatchKeyEvent',type='keyDown',key='Tab',code='Tab',windowsVirtualKeyCode=9)
            cdp('Input.dispatchKeyEvent',type='keyUp',key='Tab',code='Tab',windowsVirtualKeyCode=9)
            row['first_tab'] = js('({text:document.activeElement.textContent,href:document.activeElement.getAttribute("href")})')
            js('document.querySelector("details summary").click();document.querySelector("details").scrollIntoView()')
            row['details'] = js('({open:document.querySelector("details").open,text:document.querySelector("details").innerText})')
            row['captures']['details'] = shot(f'{name}-{width}-details.png')
        else:
            js('document.querySelector("#btn-theme").click()')
            row['theme_after'] = js('document.documentElement.dataset.theme')
            js('document.querySelector("#btn-node-finder").click()')
            fill_input('#node-finder-input','__no_matching_node_20261001__')
            row['finder'] = js('({focus:document.activeElement.id,visible:!!document.querySelector("#node-finder-input").getBoundingClientRect().width,text:document.querySelector("#node-finder-input").closest("[role=dialog]").innerText})')
            if width == 375:
                row['captures']['finder'] = shot(f'{name}-{width}-finder.png')
            escape()
            row['after_escape'] = js('({focus:document.activeElement.id,visible:!!document.querySelector("#node-finder-input").getBoundingClientRect().width})')
        js('window.scrollTo(0,document.documentElement.scrollHeight)')
        row['bottom'] = js('({y:scrollY,scrollHeight:document.documentElement.scrollHeight,viewport:innerHeight,scrollWidth:document.documentElement.scrollWidth,text:document.body.innerText.slice(-500)})')
        row['captures']['bottom'] = shot(f'{name}-{width}-bottom.png')
        row['health'] = js('({hook:window.__surfaceQA||null,httpResources:performance.getEntriesByType("resource").filter(x=>/^https?:/.test(x.name)).map(x=>({name:x.name,status:x.responseStatus??null}))})')
        if name == 'index':
            js('document.querySelector("a.diagram").click()')
            wait_for_load()
            row['clicked_first_diagram'] = js('({url:location.href,title:document.title,svg:document.querySelectorAll("svg").length})')
            js('history.back()')
            wait_for_load()
            row['back_url'] = js('location.href')
        assert hashlib.sha256(file.read_bytes()).hexdigest() == digest
        with (OUT/'observations.jsonl').open('a') as f:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(json.dumps({'surface':name,'viewport':[width,height],'overflowX':initial['scrollWidth']>width,'svg_offscreen':len(initial['svgHorizontalOutside']),'minSvgFontPx':initial['minSvgFontPx'],'medianSvgFontPx':initial['medianSvgFontPx'],'ordinary_offscreen':len(initial['ordinaryHorizontalOutside']),'health':row['health'],'escape':row.get('after_escape'),'capture':row['captures']['default']['path']},ensure_ascii=False))
