#!/usr/bin/env python3
"""Patch PROMPTURE Command Library v2.7 -> v2.7.1 (performance + bug fixes).

Fixes:
1. Unified tab bar drag-to-scroll (eliminates duplicate pointer + mouse execution).
2. Incremental rendering (100 rows/batch + IntersectionObserver) & 120ms search debounce.
3. Modal close button (X), Escape key support, and in-place favorite toggle (no scroll reset).
4. iOS overscroll guard for auto-hiding toolbar & safer fallbackCopy.
5. Sync <html lang> with MM/ENG toggle + minor Myanmar text typo cleanup.
"""

import shutil

SRC = 'index.html'
BACKUP = 'index.html.bak'

OLD_CSS = '.sheet-head{padding:24px 22px 0;flex:0 0 auto}'
NEW_CSS = (
    '.sheet-head{padding:24px 22px 0;flex:0 0 auto;position:relative}\n'
    '.sheet-close{position:absolute;top:16px;right:16px;width:30px;height:30px;border-radius:50%;'
    'border:1px solid var(--line);background:var(--input);color:var(--muted);font-size:.9rem;'
    'display:flex;align-items:center;justify-content:center;cursor:pointer}\n'
    '.sheet-close:active{transform:scale(.9)}\n'
    '.loadmore{display:block;width:100%;margin-top:12px;padding:12px;border-radius:12px;'
    'border:1px solid var(--gold);background:var(--input);color:var(--gold2);'
    'font-size:.88rem;font-weight:700;cursor:pointer}'
)

DATA_TYPOS = [
    (r'003\\) prompt', '003) prompt'),
    ('အကျဉ်းချုပ်ပြပါ။ ---"', 'အကျဉ်းချုပ်ပြပါ။"'),
    ('လျစ်လျူရှု ပါ', 'လျစ်လျူရှုပါ'),
    ('ကြည့်ရှု ပါ', 'ကြည့်ရှုပါ'),
    ('ခန ့ ်မှန်းပါ', 'ခန့်မှန်းပါ'),
    ('ပြန ့ ်ကား', 'ပြန့်ကား'),
    ('ဆန ့ ်ကျင်ဘက်', 'ဆန့်ကျင်ဘက်'),
    ('သီးသန ့ ်ဖြစ်သော', 'သီးသန့်ဖြစ်သော'),
    ('နေ ့ ခင်းဘက်', 'နေ့ခင်းဘက်'),
    ('ခေတ ္တ ရပ်ပါ', 'ခေတ္တရပ်ပါ'),
    ('တိုက်ရို က်', 'တိုက်ရိုက်'),
    ('မြန်မာ့ရို းရာ', 'မြန်မာ့ရိုးရာ'),
    ('ချုပ်ရို း', 'ချုပ်ရိုး'),
    ('ရို မန်းတစ်', 'ရိုမန်းတစ်'),
]

OLD_STR = r"""const STR={
 mm:{subtitle:'Command ၃၆၂၆ — ထိပြီး ဖတ် ၊ ကူးယူပြီး GPT/Gem မှာ paste လုပ်',searchPh:'ရှာရန်… (ဥပမာ: lighting, ဂါဝန်)',all:'🌟 အားလုံး',fav:'⭐ အကြိုက်ဆုံး',catAll:'📂 အားလုံး',found:n=>'တွေ့ရှိချက်: '+n+' commands',favEmpty:'⭐ အကြိုက်ဆုံး မရှိသေးပါ<br>ကြိုက်တဲ့ command ကို ထိပြီး 🤍 နှိပ်ထားနော် 💛',noResult:'မတွေ့ပါ — တခြားစကားလုံးနဲ့ ရှာကြည့်ပါနော် 🔍',copied:'ကူးယူပြီးပါပြီ ✅',favSaved:'အကြိုက်ဆုံးထဲ သိမ်းပြီးပါပြီ ⭐',langToast:'🌐 မြန်မာ'},
 en:{subtitle:'3626 commands — tap to read, copy & paste in GPT/Gem',searchPh:'Search… (e.g. lighting, gown)',all:'🌟 All',fav:'⭐ Favorites',catAll:'📂 All',found:n=>'Found: '+n+' commands',favEmpty:'⭐ No favorites yet<br>Tap a command and hit 🤍 to save it 💛',noResult:'Nothing found — try another word 🔍',copied:'Copied ✅',favSaved:'Saved to favorites ⭐',langToast:'🌐 English'}
};"""

NEW_STR = r"""const STR={
 mm:{subtitle:'Command ၃၆၂၆ — ထိပြီး ဖတ် ၊ ကူးယူပြီး GPT/Gem မှာ paste လုပ်',searchPh:'ရှာရန်… (ဥပမာ: lighting, ဂါဝန်)',all:'🌟 အားလုံး',fav:'⭐ အကြိုက်ဆုံး',catAll:'📂 အားလုံး',found:n=>'တွေ့ရှိချက်: '+n+' commands',loadMore:(s,t)=>'နောက်ထပ်ပြရန် ('+(t-s)+' ခုကျန်)',favEmpty:'⭐ အကြိုက်ဆုံး မရှိသေးပါ<br>ကြိုက်တဲ့ command ကို ထိပြီး 🤍 နှိပ်ထားနော် 💛',noResult:'မတွေ့ပါ — တခြားစကားလုံးနဲ့ ရှာကြည့်ပါနော် 🔍',copied:'ကူးယူပြီးပါပြီ ✅',favSaved:'အကြိုက်ဆုံးထဲ သိမ်းပြီးပါပြီ ⭐',langToast:'🌐 မြန်မာ'},
 en:{subtitle:'3626 commands — tap to read, copy & paste in GPT/Gem',searchPh:'Search… (e.g. lighting, gown)',all:'🌟 All',fav:'⭐ Favorites',catAll:'📂 All',found:n=>'Found: '+n+' commands',loadMore:(s,t)=>'Load more ('+(t-s)+' left)',favEmpty:'⭐ No favorites yet<br>Tap a command and hit 🤍 to save it 💛',noResult:'Nothing found — try another word 🔍',copied:'Copied ✅',favSaved:'Saved to favorites ⭐',langToast:'🌐 English'}
};"""

OLD_APPLYLANG = """function applyLang(){
  document.getElementById('langbtn').textContent=lang==='mm'?'MM':'ENG';"""
NEW_APPLYLANG = """function applyLang(){
  document.documentElement.lang=lang==='mm'?'my':'en';
  document.getElementById('langbtn').textContent=lang==='mm'?'MM':'ENG';"""

OLD_COPY = "function fallbackCopy(t){ const ta=document.createElement('textarea'); ta.value=t; ta.style.position='fixed'; ta.style.top='0'; ta.style.opacity='0'; document.body.appendChild(ta); ta.focus(); ta.select(); try{ document.execCommand('copy'); }catch(e){} document.body.removeChild(ta); }"
NEW_COPY = "function fallbackCopy(t){ const ta=document.createElement('textarea'); ta.value=t; ta.setAttribute('readonly',''); ta.style.cssText='position:fixed;left:-9999px;top:0;opacity:0'; document.body.appendChild(ta); try{ ta.focus({preventScroll:true}); }catch(e){ ta.focus(); } ta.select(); try{ document.execCommand('copy'); }catch(e){} document.body.removeChild(ta); }"

OLD_RENDER_BLOCK = r"""function render(){
  const list=filtered();
  result.textContent=STR[lang].found(list.length)+(search.value.trim()?' · "'+search.value.trim()+'"':'');
  if(!list.length){
    rows.innerHTML='<div class="empty">'+(coll==='fav'?STR[lang].favEmpty:STR[lang].noResult)+'</div>';
    return;
  }
  rows.innerHTML=list.map(({c,i})=>'<div class="row" data-i="'+i+'"><span class="tx">'+esc(lang==='mm'?(c.mm||c.text):c.text)+'</span><span class="rh"><button class="mini-fav" data-i="'+i+'">'+(favSet.has(i)?'❤️':'🤍')+'</button><span class="chev">›</span></span></div>').join('');
}
function openModal(i){
  const c=COMMANDS[i];
  sheet.innerHTML=
    '<div class="sheet-head"><span class="em-big">'+firstEmoji(c.text)+'</span><br>'+
    '<span class="badge">'+esc(COLL_NAME[c.collection])+' · '+esc(c.category)+' · #'+c.num+'</span></div>'+
    '<div class="sheet-scroll">'+
    '<div><span class="en-tag">EN</span></div><div class="en-text">'+esc(stripEmoji(c.text))+'</div>'+
    '<hr class="divider">'+
    '<div><span class="mm-tag">မြန်မာ</span></div><div class="mm-text">'+esc(stripEmoji(c.mm||''))+'</div>'+
    '</div>'+
    '<div class="sheet-foot"><div class="iconrow"><button class="icobtn" id="mcopy" title="ကူးယူ">📋</button>'+
    '<button class="icobtn" id="mfav" title="အကြိုက်ဆုံး">'+(favSet.has(i)?'❤️':'🤍')+'</button></div></div>';
  overlay.classList.add('show'); document.body.classList.add('modal-open');
  document.getElementById('mcopy').onclick=(e)=>{ e.stopPropagation();
    copyText(c.text).then(()=>showToast(STR[lang].copied)); };
  document.getElementById('mfav').onclick=(e)=>{ e.stopPropagation();
    if(favSet.has(i)){favSet.delete(i);}else{favSet.add(i);showToast(STR[lang].favSaved);}
    saveFavs(); openModal(i); render(); };
}
function closeModal(){ overlay.classList.remove('show'); document.body.classList.remove('modal-open'); }
overlay.addEventListener('click',e=>{ if(e.target===overlay) closeModal(); });
rows.addEventListener('click',e=>{
  const mf=e.target.closest('.mini-fav');
  if(mf){ e.stopPropagation(); const i=+mf.dataset.i;
    if(favSet.has(i)){favSet.delete(i);}else{favSet.add(i);showToast(STR[lang].favSaved);}
    saveFavs(); render(); return; }
  const r=e.target.closest('.row'); if(r) openModal(+r.dataset.i);
});
document.getElementById('tabs').addEventListener('click',e=>{
  if(window.__tabsDragged){ window.__tabsDragged=false; return; }
  const t=e.target.closest('.tab'); if(!t) return;
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); coll=t.dataset.coll; cat='';
  search.value='';  /* fix: clear search on tab switch */
  filterbtn.classList.remove('on'); catpanel.classList.remove('open');
  buildCats(); render();
});
filterbtn.addEventListener('click',()=>{ catpanel.classList.toggle('open'); filterbtn.classList.toggle('on'); });
catpanel.addEventListener('click',e=>{
  const b=e.target.closest('.catchip'); if(!b) return;
  cat=b.dataset.c; buildCats(); render();
});
search.addEventListener('input',render);
let lastY=0;
window.addEventListener('scroll',()=>{
  const y=window.scrollY;
  if(document.body.classList.contains('modal-open')) return;
  if(y>lastY&&y>120){ toolbar.classList.add('hide'); }
  else if(y<lastY){ toolbar.classList.remove('hide'); }
  lastY=y;
},{passive:true});"""

NEW_RENDER_BLOCK = r"""const PAGE_SIZE=100;
let renderLimit=PAGE_SIZE, lastList=[], moreIO=null, searchTimer=null;
function rowHtml({c,i}){
  return '<div class="row" data-i="'+i+'"><span class="tx">'+esc(lang==='mm'?(c.mm||c.text):c.text)+'</span><span class="rh"><button class="mini-fav" data-i="'+i+'">'+(favSet.has(i)?'❤️':'🤍')+'</button><span class="chev">›</span></span></div>';
}
function loadMoreRows(){
  const lm=document.getElementById('loadmore'); if(!lm) return;
  const prev=renderLimit; renderLimit+=PAGE_SIZE;
  const more=lastList.slice(prev,renderLimit).map(rowHtml).join('');
  lm.insertAdjacentHTML('beforebegin',more);
  if(renderLimit>=lastList.length){
    if(moreIO) moreIO.disconnect();
    lm.remove();
  }else{
    lm.textContent=STR[lang].loadMore(Math.min(renderLimit,lastList.length),lastList.length);
  }
}
function observeMore(){
  if(moreIO) moreIO.disconnect();
  const lm=document.getElementById('loadmore');
  if(!lm||!window.IntersectionObserver) return;
  moreIO=new IntersectionObserver(entries=>{
    if(entries.some(e=>e.isIntersecting)) loadMoreRows();
  },{rootMargin:'300px'});
  moreIO.observe(lm);
}
function render(opts){
  const keep=opts&&opts.keepLimit;
  if(!keep) renderLimit=PAGE_SIZE;
  lastList=filtered();
  const list=lastList;
  result.textContent=STR[lang].found(list.length)+(search.value.trim()?' · "'+search.value.trim()+'"':'');
  if(!list.length){
    if(moreIO) moreIO.disconnect();
    rows.innerHTML='<div class="empty">'+(coll==='fav'?STR[lang].favEmpty:STR[lang].noResult)+'</div>';
    return;
  }
  const slice=list.slice(0,renderLimit);
  let html=slice.map(rowHtml).join('');
  if(renderLimit<list.length){
    html+='<button class="loadmore" id="loadmore">'+esc(STR[lang].loadMore(slice.length,list.length))+'</button>';
  }
  rows.innerHTML=html;
  observeMore();
}
function openModal(i){
  const c=COMMANDS[i];
  sheet.innerHTML=
    '<div class="sheet-head"><button class="sheet-close" id="mclose" title="Close">✕</button>'+
    '<span class="em-big">'+firstEmoji(c.text)+'</span><br>'+
    '<span class="badge">'+esc(COLL_NAME[c.collection])+' · '+esc(c.category)+' · #'+c.num+'</span></div>'+
    '<div class="sheet-scroll">'+
    '<div><span class="en-tag">EN</span></div><div class="en-text">'+esc(stripEmoji(c.text))+'</div>'+
    '<hr class="divider">'+
    '<div><span class="mm-tag">မြန်မာ</span></div><div class="mm-text">'+esc(stripEmoji(c.mm||''))+'</div>'+
    '</div>'+
    '<div class="sheet-foot"><div class="iconrow"><button class="icobtn" id="mcopy" title="ကူးယူ">📋</button>'+
    '<button class="icobtn" id="mfav" title="အကြိုက်ဆုံး">'+(favSet.has(i)?'❤️':'🤍')+'</button></div></div>';
  overlay.classList.add('show'); document.body.classList.add('modal-open');
  document.getElementById('mclose').onclick=closeModal;
  document.getElementById('mcopy').onclick=(e)=>{ e.stopPropagation();
    /* emoji မပါဘဲ copy ချင်ရင် c.text အစား stripEmoji(c.text) ကို သုံးနိုင်ပါတယ် */
    copyText(c.text).then(()=>showToast(STR[lang].copied)); };
  const mfav=document.getElementById('mfav');
  mfav.onclick=(e)=>{ e.stopPropagation();
    if(favSet.has(i)){favSet.delete(i);}else{favSet.add(i);showToast(STR[lang].favSaved);}
    const on=favSet.has(i);
    mfav.textContent=on?'❤️':'🤍';
    saveFavs();
    const rb=rows.querySelector('.mini-fav[data-i="'+i+'"]');
    if(rb) rb.textContent=on?'❤️':'🤍';
    if(coll==='fav') render({keepLimit:true});
  };
}
function closeModal(){ overlay.classList.remove('show'); document.body.classList.remove('modal-open'); }
overlay.addEventListener('click',e=>{ if(e.target===overlay) closeModal(); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&overlay.classList.contains('show')) closeModal(); });
rows.addEventListener('click',e=>{
  const lm=e.target.closest('#loadmore');
  if(lm){ loadMoreRows(); return; }
  const mf=e.target.closest('.mini-fav');
  if(mf){ e.stopPropagation(); const i=+mf.dataset.i;
    if(favSet.has(i)){favSet.delete(i);}else{favSet.add(i);showToast(STR[lang].favSaved);}
    mf.textContent=favSet.has(i)?'❤️':'🤍';
    saveFavs();
    if(coll==='fav') render({keepLimit:true});
    return; }
  const r=e.target.closest('.row'); if(r) openModal(+r.dataset.i);
});
document.getElementById('tabs').addEventListener('click',e=>{
  if(window.__tabsDragged){ window.__tabsDragged=false; return; }
  const t=e.target.closest('.tab'); if(!t) return;
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); coll=t.dataset.coll; cat='';
  clearTimeout(searchTimer); search.value='';  /* fix: clear search on tab switch */
  filterbtn.classList.remove('on'); catpanel.classList.remove('open');
  buildCats(); render();
});
filterbtn.addEventListener('click',()=>{ catpanel.classList.toggle('open'); filterbtn.classList.toggle('on'); });
catpanel.addEventListener('click',e=>{
  const b=e.target.closest('.catchip'); if(!b) return;
  cat=b.dataset.c; buildCats(); render();
});
search.addEventListener('input',()=>{ clearTimeout(searchTimer); searchTimer=setTimeout(()=>render(),120); });
let lastY=0;
window.addEventListener('scroll',()=>{
  const y=window.scrollY;
  if(document.body.classList.contains('modal-open')) return;
  if(y<=10){ toolbar.classList.remove('hide'); lastY=0; return; }
  if(y>lastY&&y>120){ toolbar.classList.add('hide'); }
  else if(y<lastY){ toolbar.classList.remove('hide'); }
  lastY=y;
},{passive:true});"""

OLD_DRAG = r"""/* tab bar: drag-to-scroll (mouse/pen) + wheel-to-horizontal */
(function(){
  const tabsEl=document.getElementById('tabs');
  let isDown=false, startX=0, startScroll=0, moved=0;
  tabsEl.addEventListener('pointerdown',e=>{
    if(e.pointerType==='touch') return;
    isDown=true; moved=0; startX=e.clientX; startScroll=tabsEl.scrollLeft;
    tabsEl.classList.add('dragging');
  });
  tabsEl.addEventListener('pointermove',e=>{
    if(!isDown) return;
    const dx=e.clientX-startX;
    moved=Math.max(moved,Math.abs(dx));
    tabsEl.scrollLeft=startScroll-dx;
  });
  function endDrag(){
    if(!isDown) return;
    isDown=false; tabsEl.classList.remove('dragging');
    if(moved>6){ window.__tabsDragged=true; setTimeout(()=>{ window.__tabsDragged=false; },150); }
  }
  window.addEventListener('pointerup',endDrag);
  window.addEventListener('pointercancel',endDrag);
  tabsEl.addEventListener('wheel',e=>{
    if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){ e.preventDefault(); tabsEl.scrollLeft+=e.deltaY; }
  },{passive:false});
})();

/* tab bar: mouse-event drag fallback (covers environments that don't deliver pointer events) */
(function(){
  const tabsEl=document.getElementById('tabs');
  let down=false, sx=0, ss=0, mv=0;
  tabsEl.addEventListener('mousedown',e=>{
    if(e.button!==0) return;
    down=true; mv=0; sx=e.clientX; ss=tabsEl.scrollLeft;
    tabsEl.classList.add('dragging');
  });
  window.addEventListener('mousemove',e=>{
    if(!down) return;
    const dx=e.clientX-sx;
    mv=Math.max(mv,Math.abs(dx));
    tabsEl.scrollLeft=ss-dx;
  });
  function up(){
    if(!down) return;
    down=false; tabsEl.classList.remove('dragging');
    if(mv>6){ window.__tabsDragged=true; setTimeout(()=>{ window.__tabsDragged=false; },150); }
  }
  window.addEventListener('mouseup',up);
})();"""

NEW_DRAG = r"""/* tab bar: unified drag-to-scroll (pointer or mouse fallback) + wheel-to-horizontal */
(function(){
  const tabsEl=document.getElementById('tabs');
  let isDown=false, startX=0, startScroll=0, moved=0;
  function start(x){ isDown=true; moved=0; startX=x; startScroll=tabsEl.scrollLeft; tabsEl.classList.add('dragging'); }
  function move(x){ if(!isDown) return; const dx=x-startX; moved=Math.max(moved,Math.abs(dx)); tabsEl.scrollLeft=startScroll-dx; }
  function end(){
    if(!isDown) return;
    isDown=false; tabsEl.classList.remove('dragging');
    if(moved>6){ window.__tabsDragged=true; setTimeout(()=>{ window.__tabsDragged=false; },150); }
  }
  if(window.PointerEvent){
    tabsEl.addEventListener('pointerdown',e=>{ if(e.pointerType!=='touch'&&e.button===0) start(e.clientX); });
    window.addEventListener('pointermove',e=>{ if(isDown&&e.pointerType!=='touch') move(e.clientX); });
    window.addEventListener('pointerup',end);
    window.addEventListener('pointercancel',end);
  }else{
    tabsEl.addEventListener('mousedown',e=>{ if(e.button===0) start(e.clientX); });
    window.addEventListener('mousemove',e=>move(e.clientX));
    window.addEventListener('mouseup',end);
  }
  tabsEl.addEventListener('wheel',e=>{
    if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){ e.preventDefault(); tabsEl.scrollLeft+=e.deltaY; }
  },{passive:false});
})();"""


def main():
    shutil.copy2(SRC, BACKUP)
    html = open(SRC, encoding='utf-8').read()

    assert 'PROMPTURE Command Library v2.7' in html, 'Expected v2.7 index.html'

    replacements = [
        ('CSS', OLD_CSS, NEW_CSS),
        ('STR', OLD_STR, NEW_STR),
        ('applyLang', OLD_APPLYLANG, NEW_APPLYLANG),
        ('fallbackCopy', OLD_COPY, NEW_COPY),
        ('render/modal/scroll', OLD_RENDER_BLOCK, NEW_RENDER_BLOCK),
        ('tab-drag', OLD_DRAG, NEW_DRAG),
    ]

    for label, old, new in replacements:
        assert old in html, f'Anchor not found for: {label}'
        html = html.replace(old, new, 1)
        print(f'[OK] Patched {label}')

    typo_count = 0
    for bad, good in DATA_TYPOS:
        if bad in html:
            typo_count += html.count(bad)
            html = html.replace(bad, good)
    print(f'[OK] Cleaned {typo_count} data typo(s)')

    open(SRC, 'w', encoding='utf-8').write(html)
    print(f'Done! Backup saved at {BACKUP}, updated {SRC}.')


if __name__ == '__main__':
    main()
