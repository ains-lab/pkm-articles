"""Run inside browser_exec's helper context; never calls the described Gateway.
Invoke with root set to this slides directory, then exec this file's text.
"""
import base64
import hashlib
import json
import pathlib
import re
import time
root=pathlib.Path(globals()['root'])
cdp=globals()['cdp'];js=globals()['js'];new_tab=globals()['new_tab']
wait_for_load=globals()['wait_for_load'];fill_input=globals()['fill_input']
qa=root/'qa';qa.mkdir(exist_ok=True)
sha=hashlib.sha256((root/'lecture.html').read_bytes()).hexdigest()
meta=json.loads((root/'source-map.json').read_text())
assert meta['artifact']['sha256']==sha

def save(name,value):
    (qa/name).write_text(json.dumps({'artifact_sha256':sha,**value},ensure_ascii=False,indent=2)+'\n')

def settle():
    cdp('Runtime.evaluate',expression='document.fonts.ready.then(()=>true)',awaitPromise=True,returnByValue=True)

def active():return js("document.querySelector('.slide:not([hidden])').id")
def choose(n):
    js(f"document.querySelectorAll('#toc-list button')[{n-1}].click()")
    time.sleep(.05)
    assert active()==f'slide-{n}'
def key(k,code,vk):
    cdp('Input.dispatchKeyEvent',type='keyDown',key=k,code=code,windowsVirtualKeyCode=vk)
    cdp('Input.dispatchKeyEvent',type='keyUp',key=k,code=code,windowsVirtualKeyCode=vk)
    time.sleep(.05)

new_tab('file://'+str(root/'lecture.html')+'#slide-1');wait_for_load()
cdp('Page.bringToFront')
cdp('Page.addScriptToEvaluateOnNewDocument',source="window.__lectureErrors=[];addEventListener('error',e=>window.__lectureErrors.push(e.message));addEventListener('unhandledrejection',e=>window.__lectureErrors.push(String(e.reason)));")
cdp('Network.enable')
cdp('Network.emulateNetworkConditions',offline=True,latency=0,downloadThroughput=0,uploadThroughput=0)
cdp('Page.reload',ignoreCache=True);wait_for_load();settle()
lineage={'script_matches_file':js('document.scripts[1].textContent')==(root/'deck.js').read_text(),'font_loaded':js("document.fonts.check('30px LectureKorean')")}
assert all(lineage.values()),lineage
geometry=[]
# Layout sweeps are faster than human navigation. Suppress history serialization
# only during geometry measurements to avoid Chromium's 200/10s navigation limit.
# Real hash/deep-link behavior is tested below with the original method restored.
js("window.__qaReplaceState=history.replaceState;history.replaceState=function(){}")
for w,h in [(1440,900),(1280,720),(768,1024),(375,812)]:
    cdp('Emulation.setDeviceMetricsOverride',width=w,height=h,deviceScaleFactor=1,mobile=False)
    time.sleep(.08)
    r=cdp('Runtime.evaluate',expression=(root/'check_layout.js').read_text(),awaitPromise=True,returnByValue=True)
    assert not r.get('exceptionDetails'),r
    geometry.append(r['result']['value'])
js("history.replaceState=window.__qaReplaceState;delete window.__qaReplaceState")
save('geometry.json',{'lineage':lineage,'checks':geometry})
assert all(x['checkedSlides']==len(meta['slides']) and not x['issues'] for x in geometry),geometry

checks=[]
def rec(name,value,detail=None):checks.append({'check':name,'pass':bool(value),'detail':detail})
cdp('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=1,mobile=False)
choose(1)
rec('offline_initial_load',active()=='slide-1')
key('ArrowRight','ArrowRight',39);rec('keyboard_next',active()=='slide-2')
key('End','End',35);rec('end_and_disabled_next',active()=='slide-70' and js('document.getElementById("next").disabled'))
key('Home','Home',36);rec('home_and_disabled_previous',active()=='slide-1' and js('document.getElementById("prev").disabled'))
js("document.getElementById('contents-button').click()")
rec('contents_focus',js("document.activeElement.id==='search' && document.getElementById('toc-dialog').open"))
fill_input('#search','SSE');rec('contents_search',js("document.querySelectorAll('#toc-list li:not([hidden])').length>0 && document.querySelectorAll('#toc-list li:not([hidden])').length<70"))
fill_input('#search','zzzz-없는-검색');rec('contents_empty',js("!document.getElementById('search-empty').hidden"))
key('Escape','Escape',27);rec('escape_and_focus_return',js("!document.getElementById('toc-dialog').open && document.activeElement.id==='contents-button'"))
js("document.querySelector('.slide:not([hidden]) [data-sources]').click()")
rec('embedded_sources',js("document.getElementById('source-dialog').open && document.querySelectorAll('#source-body .source-block').length===2"))
key('Escape','Escape',27)
choose(13);js("document.querySelector('#slide-13 summary').click()")
rec('exercise_reveal',js("document.querySelector('#slide-13 details').open"))
js("location.hash='slide-27'");time.sleep(.12);rec('hash_deep_link',active()=='slide-27')
js("history.replaceState(null,'',location.pathname)");cdp('Page.reload',ignoreCache=True);wait_for_load();settle()
rec('local_storage_resume',active()=='slide-27')
rec('offline_font_loaded',js("document.fonts.check('30px LectureKorean') && [...document.fonts].every(f=>f.status==='loaded')"))
rec('no_external_resource_loads',js("performance.getEntriesByType('resource').filter(e=>/^https?:/.test(e.name)).length===0"))
rec('runtime_errors',js("window.__lectureErrors.length===0"),js('window.__lectureErrors'))
rec('skip_link_tracks_slide',js("document.querySelector('.skip').getAttribute('href')==='#heading-27'"))
r=cdp('Runtime.evaluate',expression="document.documentElement.requestFullscreen().then(()=>!!document.fullscreenElement).catch(e=>String(e))",awaitPromise=True,returnByValue=True,userGesture=True)
rec('fullscreen',r.get('result',{}).get('value') is True)
cdp('Runtime.evaluate',expression="document.fullscreenElement?document.exitFullscreen():null",awaitPromise=True,returnByValue=True)
# At maximum vertical scroll, the fixed toolbar must not conceal the final content.
cdp('Emulation.setDeviceMetricsOverride',width=375,height=812,deviceScaleFactor=1,mobile=False)
choose(9);js('window.scrollTo(0,document.documentElement.scrollHeight)');time.sleep(.08)
rec('mobile_last_content_reachable',js("document.querySelector('#slide-9 .footer').getBoundingClientRect().bottom<=document.querySelector('.toolbar').getBoundingClientRect().top+1"))
rec('mobile_scroll_hint',js("getComputedStyle(document.querySelector('#slide-9 .diagram-scroll'),'::before').content.includes('스크롤')"))
save('interaction.json',{'offline':True,'checks':checks})
assert all(c['pass'] for c in checks),checks

# Export PDF and verify the browser's print DOM independently of PDF object count.
cdp('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=1,mobile=False)
cdp('Emulation.setEmulatedMedia',media='print')
print_dom=js("(() => ({visibleSlides:[...document.querySelectorAll('.slide')].filter(e=>getComputedStyle(e).display!=='none').length,answers:[...document.querySelectorAll('.answer')].map(e=>({h:e.getBoundingClientRect().height,display:getComputedStyle(e).display})),overflows:[...document.querySelectorAll('.slide')].filter(s=>s.scrollHeight>s.clientHeight+2).map(s=>s.id)}))()")
pdf=cdp('Page.printToPDF',printBackground=True,displayHeaderFooter=False,preferCSSPageSize=True,transferMode='ReturnAsBase64')
data=base64.b64decode(pdf['data']);(root/'lecture-print.pdf').write_bytes(data)
page_objects=len(re.findall(rb'/Type\s*/Page\b',data))
save('print.json',{'pdf_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'page_objects':page_objects,'page_tree_counts':[int(x) for x in re.findall(rb'/Count\s+(\d+)',data)],'expected_slides':len(meta['slides']),'page_count_matches':page_objects==len(meta['slides']),'print_dom':print_dom})
assert page_objects==len(meta['slides']) and print_dom['visibleSlides']==len(meta['slides']) and not print_dom['overflows']
assert all(x['h']>0 and x['display']!='none' for x in print_dom['answers'])
cdp('Emulation.setEmulatedMedia',media='screen')

# Exact slide IDs are read back before screenshots; representative layouts + every SVG.
selected=sorted(set([1,3,13,17,25,36,37,51,63,67,68,70]+[s['number'] for s in meta['slides'] if s['kind']=='diagram']))
manifest=[]
for n in selected:
    choose(n);name=f'slide-{n:02d}-1440.png'
    (qa/name).write_bytes(base64.b64decode(cdp('Page.captureScreenshot',format='png',captureBeyondViewport=False)['data']))
    manifest.append({'slide':n,'observed':active(),'viewport':[1440,900],'file':name})
    save('screenshots.json',{'screenshots':manifest})
for w,h,n in [(768,1024,17),(375,812,9),(375,812,51)]:
    cdp('Emulation.setDeviceMetricsOverride',width=w,height=h,deviceScaleFactor=1,mobile=False)
    choose(n);js('window.scrollTo(0,0)');time.sleep(.08);name=f'slide-{n:02d}-{w}.png'
    (qa/name).write_bytes(base64.b64decode(cdp('Page.captureScreenshot',format='png',captureBeyondViewport=False)['data']))
    manifest.append({'slide':n,'observed':active(),'viewport':[w,h],'file':name})
save('screenshots.json',{'screenshots':manifest})
cdp('Network.emulateNetworkConditions',offline=False,latency=0,downloadThroughput=-1,uploadThroughput=-1)
print(json.dumps({'artifact_sha256':sha,'viewports':len(geometry),'slides_per_viewport':len(meta['slides']),'interaction_checks':len(checks),'failed_checks':[x for x in checks if not x['pass']],'pdf_pages':page_objects,'print_answers':len(print_dom['answers']),'screenshots':len(manifest)},ensure_ascii=False,indent=2))
