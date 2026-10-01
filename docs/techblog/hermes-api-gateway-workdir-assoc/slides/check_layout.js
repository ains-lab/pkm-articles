(async()=>{
 await document.fonts.ready;
 const issues=[],slides=[...document.querySelectorAll('.slide')];
 // There are no slide animations. DOMRect/getBBox force layout; do not wait for
 // background-tab animation frames, which may be throttled beyond the CDP limit.
 const frame=()=>Promise.resolve();
 const mobile=innerWidth<900;
 document.querySelectorAll('.exercise details').forEach(d=>d.open=true);
 let checkedSvgText=0,checkedSlides=0;
 for(let i=0;i<slides.length;i++){
  document.querySelectorAll('#toc-list button')[i].click(); await frame();
  const s=slides[i],b=s.getBoundingClientRect(),footer=s.querySelector('.footer').getBoundingClientRect();
  const take=s.querySelector('.takeaway'); const limit=take?take.getBoundingClientRect().top:footer.top;
  if(s.hidden)issues.push({slide:i+1,type:'navigation_not_visible'});
  if(document.documentElement.scrollWidth>innerWidth+1)issues.push({slide:i+1,type:'document_horizontal_overflow'});
  if(!mobile){
   for(const el of s.querySelectorAll('.content > *, .content td, .content th, .content li, .answer, .takeaway, h1, h2,.lead,.footer')){
    const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;
    if(r.left<b.left-1||r.right>b.right+1||r.top<b.top-1||r.bottom>b.bottom+1)issues.push({slide:i+1,type:'outside_canvas',text:el.textContent.slice(0,80)});
   }
   for(const el of s.querySelectorAll('.content > *'))if(el.getBoundingClientRect().bottom>limit-3)issues.push({slide:i+1,type:'content_footer_overlap',bottom:el.getBoundingClientRect().bottom,limit});
  }
  for(const node of s.querySelectorAll('svg .node')){
   const rect=node.querySelector('rect');const box={x:+rect.getAttribute('x'),y:+rect.getAttribute('y'),w:+rect.getAttribute('width'),h:+rect.getAttribute('height')};
   for(const t of node.querySelectorAll('text')){checkedSvgText++;const r=t.getBBox();if(r.width && (r.x<box.x+5||r.x+r.width>box.x+box.w-5||r.y<box.y||r.y+r.height>box.y+box.h))issues.push({slide:i+1,type:'svg_text_outside_node',text:t.textContent});}
  }
  const texts=[...s.querySelectorAll('svg text')].map(t=>({t,b:t.getBBox()}));
  for(let j=0;j<texts.length;j++)for(let k=j+1;k<texts.length;k++){
   const a=texts[j].b,bx=texts[k].b;
   if(a.width && bx.width && a.x<bx.x+bx.width-2&&a.x+a.width>bx.x+2&&a.y<bx.y+bx.height-2&&a.y+a.height>bx.y+2)issues.push({slide:i+1,type:'svg_text_overlap',a:texts[j].t.textContent,b:texts[k].t.textContent});
  }
  checkedSlides++;
 }
 document.querySelectorAll('.exercise details').forEach(d=>d.open=false);
 return {viewport:[innerWidth,innerHeight],mode:mobile?'reading':'presentation',checkedSlides,checkedSvgText,issues,fonts:document.fonts.status};
})()
