from pathlib import Path
import hashlib

p = Path('index.html')
save = Path('index_save.html')
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
h = p.read_text(encoding='utf-8')

if 'id="csi-progressive-focus-style"' in h or 'id="csi-progressive-focus-runtime"' in h:
    raise SystemExit('progressive focus already installed')

css = r'''
<style id="csi-progressive-focus-style">
/* Progressive focus for oral presentation. The active color follows the study when present, otherwise the selected Portfolio accent. */
.slide.csi-focus-enabled .csi-focus-target{
  --focus-color:var(--study-color,var(--study,var(--accent)));
  position:relative;
  isolation:isolate;
  cursor:pointer;
  transition:transform .22s ease,box-shadow .22s ease,background .22s ease,border-color .22s ease,color .22s ease,opacity .22s ease;
}
.slide.csi-focus-enabled .csi-focus-target:not(.csi-focus-active){opacity:.86}
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active{
  opacity:1;
  transform:translateY(-3px) scale(1.012);
  background:linear-gradient(145deg,color-mix(in srgb,var(--focus-color) 92%,#111),var(--focus-color))!important;
  color:#fff!important;
  border-color:transparent!important;
  box-shadow:0 18px 42px color-mix(in srgb,var(--focus-color) 25%,transparent),0 0 0 3px color-mix(in srgb,var(--focus-color) 18%,transparent)!important;
  z-index:2;
}
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active :is(h3,h4,p,li,small,strong,b,.mono,.muted){color:#fff!important}
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active>span:not(.study-token){color:rgba(255,255,255,.84)!important}
.slide.csi-focus-enabled .card.dark.csi-focus-target:not(.csi-focus-active){background:var(--white)!important;color:var(--text)!important;border-color:var(--line)!important}
.slide.csi-focus-enabled .card.dark.csi-focus-target:not(.csi-focus-active) h3{color:var(--accent-strong)!important}
.slide.csi-focus-enabled .card.dark.csi-focus-target:not(.csi-focus-active) :is(p,li,.muted){color:var(--muted)!important}
.slide.csi-focus-enabled .card.dark.csi-focus-target:not(.csi-focus-active) .mono{color:var(--accent)!important}
.slide.csi-focus-enabled .v16-study-card.primary.csi-focus-target:not(.csi-focus-active){background:var(--white)!important;color:var(--text)!important;border-color:color-mix(in srgb,var(--study) 22%,var(--line))!important}
.slide.csi-focus-enabled .v16-study-card.primary.csi-focus-target:not(.csi-focus-active)>span{color:var(--study)!important}
.slide.csi-focus-enabled .v16-study-card.primary.csi-focus-target:not(.csi-focus-active) p{color:var(--muted)!important}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-target,.slide.csi-focus-enabled .m1-result-figure.csi-focus-target,.slide.csi-focus-enabled .m1-key-result.csi-focus-target{border-radius:22px}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-active{padding:10px}
body.reduced-motion .csi-focus-target{transition:none!important;transform:none!important}
@media(max-width:850px){.slide.csi-focus-enabled .csi-focus-target.csi-focus-active{transform:none}}
</style>
'''

js = r'''
<script id="csi-progressive-focus-runtime">
(()=>{
  const COLORS={TWIXAV:'#2f6f9f',SOFT:'#7652a8',TWIXOLF:'#c36c32',VIBEX:'#2f7d5a',OASIS:'#b44e6c',SORBET:'#9a6b20',SOLAR:'#d09422',COBEX:'#5865a8',BRAUD:'#4f7187',BRAUDOLF:'#875a7c',FLUXOLF:'#a34d5d'};
  const NAMES=Object.keys(COLORS).sort((a,b)=>b.length-a.length);
  const SELECTOR=['.grid > .card','.v16-axes > article','.v16-year-grid > article','.v16-checks > article','.v16-priority > article','.v16-study-grid > .v16-study-card','.v16-extension-map > article','.v16-activity > article','.v16-jdd > article','.v16-pubs > article','.v16-decisions > article','.v16-summary > article','.v16-plan > article','.v16-retro > section','.m1-stat-grid','.m1-key-result','.m1-result-figure'].join(',');
  let stepBySlide=new Map(),pendingEntry='first',bypassButtons=false,scheduled=false;
  function activeSlide(){return document.querySelector('#deck .slide.active')}
  function inferStudy(el){
    const own=String(el.dataset.study||'').toUpperCase();if(COLORS[own])return own;
    const parent=el.closest('[data-study]');const ps=String(parent&&parent.dataset.study||'').toUpperCase();if(COLORS[ps])return ps;
    const heading=String(el.querySelector('h3,h4')?.textContent||'').toUpperCase();
    const found=NAMES.filter(n=>new RegExp('(^|[^A-Z])'+n+'([^A-Z]|$)').test(heading));return found.length===1?found[0]:'';
  }
  function candidates(slide){
    if(!slide||slide.classList.contains('hero-slide'))return [];
    const els=[...slide.querySelectorAll(SELECTOR)].filter(el=>!el.closest('.study-floating,.csi-cite,.v16-ref,.csi-extra-refs'));
    const unique=[];els.forEach(el=>{if(unique.some(parent=>parent.contains(el)))return;unique.push(el)});return unique;
  }
  function apply(slide,els,step){els.forEach((el,i)=>{const on=i===step;el.classList.toggle('csi-focus-active',on);if(on)el.setAttribute('aria-current','step');else el.removeAttribute('aria-current')})}
  function decorate(slide,entry='keep'){
    if(!slide)return [];
    const els=candidates(slide);
    slide.querySelectorAll('.csi-focus-target').forEach(el=>{if(!els.includes(el)){el.classList.remove('csi-focus-target','csi-focus-active');el.removeAttribute('aria-current')}});
    els.forEach((el,i)=>{el.classList.add('csi-focus-target');el.dataset.focusIndex=String(i);const study=inferStudy(el);if(study)el.style.setProperty('--focus-color',COLORS[study]);else el.style.removeProperty('--focus-color')});
    slide.classList.toggle('csi-focus-enabled',els.length>0);if(!els.length)return els;
    const idx=Number(slide.dataset.index||0);let step=stepBySlide.get(idx);
    if(entry==='first')step=0;else if(entry==='last')step=els.length-1;else if(!Number.isInteger(step)||step<0||step>=els.length)step=0;
    stepBySlide.set(idx,step);apply(slide,els,step);return els;
  }
  function currentStep(slide){const idx=Number(slide?.dataset.index||0),value=stepBySlide.get(idx);return Number.isInteger(value)?value:0}
  function setStep(slide,step){const els=decorate(slide,'keep');if(!els.length)return false;step=Math.max(0,Math.min(els.length-1,step));stepBySlide.set(Number(slide.dataset.index||0),step);apply(slide,els,step);return true}
  function navigate(delta){
    pendingEntry=delta<0?'last':'first';const button=document.getElementById(delta>0?'nextBtn':'prevBtn');if(!button)return;
    bypassButtons=true;button.click();bypassButtons=false;
    requestAnimationFrame(()=>{decorate(activeSlide(),pendingEntry);pendingEntry='first'});
  }
  function forward(){const slide=activeSlide(),els=decorate(slide,'keep');if(!els.length){navigate(1);return}const step=currentStep(slide);if(step<els.length-1)setStep(slide,step+1);else navigate(1)}
  function backward(){const slide=activeSlide(),els=decorate(slide,'keep');if(!els.length){navigate(-1);return}const step=currentStep(slide);if(step>0)setStep(slide,step-1);else navigate(-1)}
  function scheduleRefresh(entry){if(entry)pendingEntry=entry;if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;decorate(activeSlide(),pendingEntry);pendingEntry='first'})}
  document.addEventListener('keydown',e=>{
    if(['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)||document.body.dataset.view!=='slides')return;
    const k=e.key.toLowerCase();
    if(['arrowright','pagedown',' '].includes(k)){e.preventDefault();e.stopImmediatePropagation();forward()}
    else if(['arrowleft','pageup'].includes(k)){e.preventDefault();e.stopImmediatePropagation();backward()}
  },true);
  ['nextBtn','prevBtn'].forEach(id=>document.getElementById(id)?.addEventListener('click',e=>{if(bypassButtons)return;e.preventDefault();e.stopImmediatePropagation();if(id==='nextBtn')forward();else backward()},true));
  document.addEventListener('click',e=>{if(e.target.closest('a,button,input,textarea,select,label'))return;const target=e.target.closest('.csi-focus-target'),slide=target?.closest('.slide.active');if(!target||!slide)return;const els=decorate(slide,'keep'),idx=els.indexOf(target);if(idx>=0)setStep(slide,idx)});
  const deck=document.getElementById('deck');
  if(deck)new MutationObserver(mutations=>{if(mutations.some(m=>m.type==='childList'||(m.type==='attributes'&&m.target.classList?.contains('slide'))))scheduleRefresh()}).observe(deck,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
  scheduleRefresh('first');
})();
</script>
'''

if '</head>' not in h or '</body>' not in h:
    raise SystemExit('HTML markers missing')
h = h.replace('</head>', css + '\n</head>', 1)
h = h.replace('</body>', js + '\n</body>', 1)
p.write_text(h, encoding='utf-8')

after_save = hashlib.sha256(save.read_bytes()).hexdigest()
if before_save != after_save:
    raise SystemExit('index_save.html changed unexpectedly')

check = p.read_text(encoding='utf-8')
assert check.count('id="csi-progressive-focus-style"') == 1
assert check.count('id="csi-progressive-focus-runtime"') == 1
assert '--focus-color:var(--study-color,var(--study,var(--accent)))' in check
assert 'csi-progressive-focus-runtime' not in save.read_text(encoding='utf-8')
print('VALIDATION PASSED')
