'use strict';
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const $ = id => document.getElementById(id);
  const storageKey = 'hermes-gateway-lecture-v1-slide';
  const sourceData = JSON.parse($('source-data').textContent);
  let current = 0, lastTrigger = null;
  const dialogs = [$('toc-dialog'), $('source-dialog'), $('help-dialog')];
  function stored() { try { return Number(localStorage.getItem(storageKey)) || 1; } catch { return 1; } }
  function hashPage() { const m = /^#slide-(\d+)$/.exec(location.hash); return m ? Number(m[1]) : null; }
  function fit() {
    const stage = $('stage').getBoundingClientRect();
    document.documentElement.style.setProperty('--scale', Math.min(stage.width / 1600, stage.height / 900));
  }
  function show(n, focus = false) {
    current = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, i) => { s.hidden = i !== current; s.setAttribute('aria-hidden', String(i !== current)); });
    $('slide-count').textContent = `${current + 1} / ${slides.length}`;
    $('prev').disabled = current === 0; $('next').disabled = current === slides.length - 1;
    $('progress').style.width = `${(current + 1) / slides.length * 100}%`;
    $('announcer').textContent = `${current + 1} / ${slides.length}. ${slides[current].dataset.title}`;
    document.querySelector('.skip').href = `#heading-${current + 1}`;
    try { if(location.hash !== `#slide-${current + 1}`) history.replaceState(null, '', `#slide-${current + 1}`); } catch { /* rapid navigation/storage policies must not block content */ }
    try { localStorage.setItem(storageKey, String(current + 1)); } catch { /* storage is optional */ }
    if (focus) slides[current].querySelector('h1,h2').focus({preventScroll:true});
    if (matchMedia('(max-width:899px)').matches) window.scrollTo(0,0);
    fit();
  }
  function openDialog(d, trigger) {
    lastTrigger = trigger || document.activeElement;
    d.showModal();
    if(d === $('toc-dialog')) $('search').focus();
    else d.querySelector('button').focus();
  }
  dialogs.forEach(d => {
    d.querySelector('[data-close]').addEventListener('click', () => d.close());
    d.addEventListener('keydown', e => { if(e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); d.close(); } });
    d.addEventListener('close', () => { if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus(); });
  });
  $('prev').addEventListener('click', () => show(current-1,true));
  $('next').addEventListener('click', () => show(current+1,true));
  $('contents-button').addEventListener('click', e => openDialog($('toc-dialog'),e.currentTarget));
  $('help-button').addEventListener('click', e => openDialog($('help-dialog'),e.currentTarget));
  $('print-button').addEventListener('click', () => window.print());
  async function fullscreen() {
    try {
      if(document.fullscreenElement) await document.exitFullscreen();
      else if(document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else $('announcer').textContent = '이 브라우저는 전체화면 API를 지원하지 않습니다.';
    } catch { $('announcer').textContent = '전체화면 진입이 차단되었습니다. 브라우저 전체화면 기능을 사용하세요.'; }
  }
  $('fullscreen-button').addEventListener('click',fullscreen);
  const list = $('toc-list');
  slides.forEach((s,i) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    const chapter = document.createElement('span'); chapter.className='toc-chapter'; chapter.textContent=s.dataset.chapter;
    b.append(chapter, document.createTextNode(`${String(i+1).padStart(2,'0')} · ${s.dataset.title}`));
    b.addEventListener('click',()=> { $('toc-dialog').close(); show(i,true); });
    li.dataset.search=(s.dataset.chapter+' '+s.dataset.title+' '+s.querySelector('.lead').textContent).toLocaleLowerCase();
    li.append(b);list.append(li);
  });
  $('search').addEventListener('input',()=> {
    const q=$('search').value.trim().toLocaleLowerCase(); let count=0;
    [...list.children].forEach(li=> {li.hidden=!li.dataset.search.includes(q); if(!li.hidden) count++;});
    $('search-empty').hidden=Boolean(count);
    $('search-result').textContent=`${count}개 슬라이드`;
  });
  document.querySelectorAll('[data-sources]').forEach(button=>button.addEventListener('click',()=> {
    const body=$('source-body');body.replaceChildren();
    const intro=document.createElement('p');intro.textContent='기술문서의 인용 구간입니다. 과거 관측·제안·미검증의 문맥을 함께 읽으세요. 전체 원문 링크는 원래 폴더가 필요합니다.';body.append(intro);
    JSON.parse(button.dataset.sources).forEach(ref=> {
      const item=sourceData.excerpts[ref];const section=document.createElement('section');section.className='source-block';
      const h=document.createElement('h3');h.textContent=ref;const a=document.createElement('a');a.href='../'+item.file;a.textContent='전체 원문 열기';a.target='_blank';a.rel='noopener';
      const pre=document.createElement('pre');pre.textContent=item.text;section.append(h,a,pre);body.append(section);
    });
    openDialog($('source-dialog'),button);
  }));
  document.addEventListener('keydown',e=> {
    if(e.isComposing || e.ctrlKey || e.metaKey || e.altKey || dialogs.some(d=>d.open)) return;
    if(e.target.closest('input,textarea,select,button,a,summary,[contenteditable="true"],.diagram-scroll,.table-scroll,.code-scroll')) return;
    if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1,true);}
    else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1,true);}
    else if(e.key==='Home'){e.preventDefault();show(0,true);}
    else if(e.key==='End'){e.preventDefault();show(slides.length-1,true);}
    else if(e.key.toLowerCase()==='t'){e.preventDefault();openDialog($('toc-dialog'));}
    else if(e.key.toLowerCase()==='f'){e.preventDefault();fullscreen();}
    else if(e.key==='?'){e.preventDefault();openDialog($('help-dialog'));}
  });
  window.addEventListener('resize',fit);
  window.addEventListener('hashchange',()=> {const n=hashPage();if(n!==null)show(n-1,true);});
  // Expanded answers must print even on browsers without ::details-content support.
  let closedBeforePrint=[];
  window.addEventListener('beforeprint',()=> {closedBeforePrint=[...document.querySelectorAll('details:not([open])')];closedBeforePrint.forEach(d=>d.open=true);});
  window.addEventListener('afterprint',()=> {closedBeforePrint.forEach(d=>d.open=false);closedBeforePrint=[];});
  document.fonts.ready.then(fit);
  show((hashPage()||stored())-1);
})();
