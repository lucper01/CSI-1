from pathlib import Path
import json
import runpy

ROOT = Path('.')
INDEX = ROOT / 'index.html'
g = runpy.run_path(str(ROOT / 'tools_temp' / 'update_csi_results_demo.py'))
text = g['text']
slides = g['slides']
start = g['start']
end = g['end']
assert len(slides) == 44, f'Expected 44 slides, got {len(slides)}'
titles = [s.get('title') or s.get('_fr', {}).get('title', '') for s in slides]
for title in [
    'TWIXAV - les courbes empiriques',
    'TWIXAV - la fenêtre se rétrécit avec la durée',
    'TWIXAV - PSS et asymétrie restent stables',
    'VIBEX - l’asymétrie SL-LS reproduit la Boundary Extension',
    'VIBEX - la taille module l’effet sans effet principal global',
    'VIBEX - les temps de réaction convergent avec les jugements',
]:
    assert titles.count(title) == 1, title

text = text[:start] + json.dumps(slides, ensure_ascii=False, separators=(',', ':')) + text[end:]

CSS = r'''
<style id="csi-results-demo-v1">
.results-expanded{display:grid;grid-template-columns:minmax(280px,.78fr) minmax(500px,1.45fr);gap:18px;align-items:stretch}
.results-copy{display:flex;flex-direction:column;gap:14px;min-width:0}
.result-figure-large{margin:0;min-width:0;background:#fff;border:1px solid color-mix(in srgb,var(--study,var(--accent)) 24%,var(--line));border-radius:24px;padding:12px 14px 10px;box-shadow:0 12px 28px rgba(11,47,35,.08);display:flex;flex-direction:column;justify-content:center}
.result-figure-large img{width:100%;max-height:440px;object-fit:contain;display:block}
.result-figure-large figcaption{margin-top:7px;color:#526259;font-size:.78rem;line-height:1.3;text-align:center;font-weight:700}
html[data-theme="dark"] .result-figure-large{background:#f7faf8;color:#17231c}
.study-demo-launch{--demo-study:var(--accent);margin-top:14px;width:min(560px,100%);border:1px solid color-mix(in srgb,var(--demo-study) 36%,var(--line));background:linear-gradient(135deg,color-mix(in srgb,var(--demo-study) 12%,var(--white)),var(--white));color:var(--text);border-radius:20px;padding:12px 15px;display:grid;grid-template-columns:auto 1fr;column-gap:12px;row-gap:2px;text-align:left;cursor:pointer;box-shadow:var(--shadow-soft)}
.study-demo-launch::before{content:"▶";grid-row:1/5;align-self:center;display:grid;place-items:center;width:38px;height:38px;border-radius:13px;background:var(--demo-study);color:#fff;font-size:.9rem}
.study-demo-launch:hover,.study-demo-launch:focus-visible{transform:translateY(-2px);outline:none;box-shadow:0 14px 34px color-mix(in srgb,var(--demo-study) 22%,transparent)}
.study-demo-launch .demo-launch-kicker{color:var(--demo-study);font-size:.68rem;font-weight:950;letter-spacing:.08em}
.study-demo-launch strong{font-size:.96rem;line-height:1.15}
.study-demo-launch>span:not(.demo-launch-kicker),.study-demo-launch i{font-size:.75rem;color:var(--muted);font-style:normal;line-height:1.25}
.study-demo-launch i{font-weight:800;color:var(--demo-study)}
.study-demo-modal[hidden]{display:none!important}
.study-demo-modal{position:fixed;inset:0;z-index:5000;display:grid;place-items:center;padding:28px}
.study-demo-backdrop{position:absolute;inset:0;background:rgba(3,15,11,.82);backdrop-filter:blur(10px)}
.study-demo-panel{--demo-color:var(--accent);position:relative;z-index:1;width:min(1180px,94vw);height:min(820px,90vh);overflow:auto;background:var(--cream);color:var(--text);border:1px solid color-mix(in srgb,var(--demo-color) 35%,var(--line));border-radius:30px;box-shadow:0 32px 100px rgba(0,0,0,.42);padding:26px}
.demo-close{position:sticky;float:right;top:0;z-index:4;width:42px;height:42px;border:0;border-radius:50%;background:color-mix(in srgb,var(--demo-color) 15%,var(--white));color:var(--demo-color);cursor:pointer;font-size:1.35rem;font-weight:950}
.demo-head{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:18px;padding-right:52px}
.demo-head .demo-acronym{display:inline-flex;padding:6px 10px;border-radius:999px;background:var(--demo-color);color:#fff;font-weight:950;font-size:.75rem;letter-spacing:.07em}
.demo-head h2{margin:8px 0 4px;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.65rem,3vw,2.7rem);line-height:1;color:color-mix(in srgb,var(--demo-color) 78%,var(--text))}
.demo-head p{margin:0;color:var(--muted);max-width:780px}
.demo-meta{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 18px}
.demo-meta span{padding:6px 9px;border-radius:999px;background:color-mix(in srgb,var(--demo-color) 11%,var(--white));border:1px solid color-mix(in srgb,var(--demo-color) 20%,var(--line));color:color-mix(in srgb,var(--demo-color) 80%,var(--text));font-size:.75rem;font-weight:850}
.demo-workspace{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:16px}
.demo-screen{min-height:430px;border-radius:24px;background:#101512;color:#fff;display:grid;place-items:center;position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.12)}
.demo-screen .demo-stage{position:absolute;inset:0;display:grid;place-items:center}
.demo-fix{font-size:3.8rem;line-height:1;color:#fff}
.demo-cross{width:86px;height:86px;position:relative}
.demo-cross::before,.demo-cross::after{content:"";position:absolute;background:#fff;border-radius:4px}
.demo-cross::before{width:86px;height:12px;left:0;top:37px}.demo-cross::after{width:12px;height:86px;left:37px;top:0}
.demo-status{position:absolute;left:16px;top:14px;right:16px;display:flex;justify-content:space-between;gap:12px;color:rgba(255,255,255,.72);font-size:.76rem;font-weight:800;pointer-events:none}
.demo-response{display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:center}
.demo-response button,.demo-primary{border:0;border-radius:15px;padding:11px 16px;background:var(--demo-color);color:#fff;font-weight:900;cursor:pointer}.demo-response button.secondary{background:#fff;color:#15251c}
.demo-side{display:flex;flex-direction:column;gap:12px}.demo-side-card{padding:14px;background:var(--white);border:1px solid var(--line);border-radius:18px}.demo-side-card b{display:block;color:var(--demo-color);margin-bottom:5px}.demo-side-card p{margin:0;font-size:.82rem;line-height:1.4;color:var(--muted)}
.demo-trial-list{display:grid;gap:7px}.demo-trial-chip{border:1px solid var(--line);border-radius:13px;padding:8px 10px;background:var(--white);font-size:.78rem;font-weight:800}.demo-trial-chip.active{border-color:var(--demo-color);box-shadow:0 0 0 2px color-mix(in srgb,var(--demo-color) 14%,transparent)}
.vibex-frame{width:min(76%,640px);aspect-ratio:4/3;border-radius:12px;background:#e7ebe8;color:#213128;display:grid;place-items:center;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.14)}
.vibex-placeholder{width:100%;height:100%;display:grid;place-items:center;padding:20px;text-align:center;font-weight:900;background:linear-gradient(145deg,rgba(47,125,90,.22),rgba(255,255,255,.76)),repeating-linear-gradient(45deg,#dfe8e2 0 18px,#eef4f0 18px 36px)}
.demo-mask{width:100%;height:100%;background:repeating-conic-gradient(#d9dedb 0 9deg,#717b75 9deg 18deg,#f4f5f4 18deg 27deg,#303733 27deg 36deg);background-size:34px 34px;filter:contrast(130%)}
.demo-progress{height:5px;background:color-mix(in srgb,var(--demo-color) 12%,var(--line));border-radius:999px;overflow:hidden;margin-top:12px}.demo-progress>i{display:block;width:0;height:100%;background:var(--demo-color);transition:width .2s ease}
body.demo-open{overflow:hidden}
@media(max-width:980px){.results-expanded{grid-template-columns:1fr}.result-figure-large img{max-height:360px}.demo-workspace{grid-template-columns:1fr}.demo-screen{min-height:360px}.study-demo-panel{height:92vh}}
@media(max-width:650px){.study-demo-modal{padding:8px}.study-demo-panel{width:98vw;height:96vh;padding:16px;border-radius:22px}.demo-screen{min-height:330px}}
@media(prefers-reduced-motion:reduce){.study-demo-launch,.demo-progress>i{transition:none!important;transform:none!important}}
body.reduced-motion .study-demo-launch,body.reduced-motion .demo-progress>i{transition:none!important;transform:none!important}
</style>
'''

MODAL = r'''
<div class="study-demo-modal" id="studyDemoModal" hidden aria-hidden="true">
  <div class="study-demo-backdrop" data-demo-close></div>
  <section class="study-demo-panel" id="studyDemoPanel" role="dialog" aria-modal="true" aria-labelledby="studyDemoTitle">
    <button class="demo-close" type="button" data-demo-close aria-label="Fermer">×</button>
    <div id="studyDemoMount"></div>
  </section>
</div>
'''

JS = r'''
<script id="csi-results-demo-runtime">
(() => {
  const modal=document.getElementById('studyDemoModal'), panel=document.getElementById('studyDemoPanel'), mount=document.getElementById('studyDemoMount');
  if(!modal||!panel||!mount)return;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  let running=false,audioCtx=null;
  const en=()=>document.documentElement.lang==='en'||(typeof currentLang!=='undefined'&&currentLang==='en');
  function closeDemo(){running=false;modal.hidden=true;modal.setAttribute('aria-hidden','true');document.body.classList.remove('demo-open');mount.innerHTML=''}
  function openDemo(kind){running=false;modal.hidden=false;modal.setAttribute('aria-hidden','false');document.body.classList.add('demo-open');if(kind==='twixav'){panel.style.setProperty('--demo-color','#2f6f9f');mount.innerHTML=twixMarkup();wireTwix()}else{panel.style.setProperty('--demo-color','#2f7d5a');mount.innerHTML=vibexMarkup();wireVibex()}modal.querySelector('.demo-close')?.focus({preventScroll:true})}
  document.addEventListener('click',e=>{const t=e.target.closest('[data-demo-open]');if(t){e.preventDefault();e.stopPropagation();openDemo(t.dataset.demoOpen);return}if(e.target.closest('[data-demo-close]'))closeDemo()});
  document.addEventListener('keydown',e=>{if(modal.hidden)return;if(e.key==='Escape')closeDemo();e.stopPropagation();e.stopImmediatePropagation()},true);
  function twixMarkup(){const E=en();return `<div class="demo-head"><div><span class="demo-acronym">TWIXAV</span><h2 id="studyDemoTitle">${E?'Audiovisual simultaneity judgment':'Jugement de simultanéité audiovisuelle'}</h2><p>${E?'Three illustrative trials reproduce the experimental logic with one SOA for each stimulus duration.':'Trois essais illustratifs reproduisent la logique expérimentale avec un SOA différent pour chacune des trois durées.'}</p></div></div><div class="demo-meta"><span>Fixation 1100 ms</span><span>${E?'Blank 400 ms':'Écran vide 400 ms'}</span><span>50 / 150 / 250 ms</span><span>SOA -300 / 0 / +300 ms</span></div><div class="demo-workspace"><div><div class="demo-screen"><div class="demo-status"><span id="twixTrialStatus">${E?'Ready':'Prêt'}</span><span id="twixEventStatus"></span></div><div class="demo-stage" id="twixStage"><button class="demo-primary" id="twixStart">${E?'Run the 3 trials':'Lancer les 3 essais'}</button></div></div><div class="demo-progress"><i id="twixProgress"></i></div></div><aside class="demo-side"><div class="demo-side-card"><b>${E?'SOA convention':'Convention du SOA'}</b><p>${E?'Negative: audition first. Positive: vision first. Zero: simultaneous onsets.':'Négatif : audition en premier. Positif : vision en premier. Zéro : débuts simultanés.'}</p></div><div class="demo-trial-list"><div class="demo-trial-chip" data-trial="0">1 - 50 ms - SOA -300 ms</div><div class="demo-trial-chip" data-trial="1">2 - 150 ms - SOA 0 ms</div><div class="demo-trial-chip" data-trial="2">3 - 250 ms - SOA +300 ms</div></div><div class="demo-side-card"><b>${E?'Response':'Réponse'}</b><p>${E?'After each pair, the participant judges the audiovisual events as simultaneous or non-simultaneous.':'Après chaque paire, le participant juge les événements audiovisuels simultanés ou non simultanés.'}</p></div></aside></div>`}
  function ensureAudio(){if(!audioCtx){const C=window.AudioContext||window.webkitAudioContext;if(C)audioCtx=new C()}if(audioCtx?.state==='suspended')audioCtx.resume()}
  function tone(d){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.frequency.value=1000;o.type='sine';g.gain.setValueAtTime(.0001,audioCtx.currentTime);g.gain.exponentialRampToValueAtTime(.16,audioCtx.currentTime+.008);g.gain.setValueAtTime(.16,audioCtx.currentTime+Math.max(.01,d/1000-.015));g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+d/1000);o.connect(g).connect(audioCtx.destination);o.start();o.stop(audioCtx.currentTime+d/1000+.02)}
  function flash(stage,d){const x=document.createElement('div');x.className='demo-cross';stage.replaceChildren(x);setTimeout(()=>{if(stage.contains(x))stage.replaceChildren()},d)}
  async function runTwixTrial(t,i){const stage=document.getElementById('twixStage'),ts=document.getElementById('twixTrialStatus'),es=document.getElementById('twixEventStatus'),p=document.getElementById('twixProgress'),E=en();document.querySelectorAll('.demo-trial-chip').forEach((el,j)=>el.classList.toggle('active',j===i));ts.textContent=`${E?'Trial':'Essai'} ${i+1}/3 - ${t.duration} ms - SOA ${t.soa>0?'+':''}${t.soa} ms`;p.style.width=`${i/3*100}%`;stage.innerHTML='<div class="demo-fix">●</div>';es.textContent='Fixation';await sleep(1100);stage.replaceChildren();es.textContent=E?'Blank':'Écran vide';await sleep(400);if(!running)return;const ad=t.soa<0?0:t.soa,vd=t.soa>0?0:Math.abs(t.soa);es.textContent=t.soa<0?(E?'Audition first':'Audition en premier'):t.soa>0?(E?'Vision first':'Vision en premier'):(E?'Simultaneous onsets':'Débuts simultanés');setTimeout(()=>{if(running)tone(t.duration)},ad);setTimeout(()=>{if(running)flash(stage,t.duration)},vd);await sleep(Math.max(ad,vd)+t.duration+320);if(!running)return;stage.innerHTML=`<div class="demo-response"><button data-demo-answer="same">${E?'Simultaneous':'Simultanés'}</button><button class="secondary" data-demo-answer="different">${E?'Non-simultaneous':'Non simultanés'}</button></div>`;es.textContent=E?'Simultaneity judgment':'Jugement de simultanéité';await new Promise(r=>{const f=e=>{if(e.target.closest('[data-demo-answer]')){stage.removeEventListener('click',f);r()}};stage.addEventListener('click',f)});stage.innerHTML=`<div style="font-weight:900">${E?'Response recorded':'Réponse enregistrée'}</div>`;await sleep(450);p.style.width=`${(i+1)/3*100}%`}
  function wireTwix(){document.getElementById('twixStart')?.addEventListener('click',async()=>{if(running)return;running=true;ensureAudio();const tr=[{duration:50,soa:-300},{duration:150,soa:0},{duration:250,soa:300}];for(let i=0;i<tr.length&&running;i++)await runTwixTrial(tr[i],i);if(!running)return;running=false;const s=document.getElementById('twixStage'),E=en();s.innerHTML=`<button class="demo-primary" id="twixRestart">${E?'Replay':'Rejouer'}</button>`;document.getElementById('twixEventStatus').textContent=E?'Demonstration complete':'Démonstration terminée';document.getElementById('twixProgress').style.width='100%';document.getElementById('twixRestart')?.addEventListener('click',()=>{mount.innerHTML=twixMarkup();wireTwix()})})}
  function vibexMarkup(){const E=en();return `<div class="demo-head"><div><span class="demo-acronym">VIBEX</span><h2 id="studyDemoTitle">${E?'Visual Boundary Extension trial':'Essai de Boundary Extension visuelle'}</h2><p>${E?'The timing and response logic are already reproduced. The two final scene images will replace the placeholders when supplied.':'Le timing et la logique de réponse sont déjà reproduits. Les deux images de scène définitives remplaceront les placeholders dès qu’elles seront fournies.'}</p></div></div><div class="demo-meta"><span>Fixation 300 ms</span><span>Image 1 - 200 ms</span><span>${E?'Mask - 1000 ms':'Masque - 1000 ms'}</span><span>Image 2 - 200 ms</span></div><div class="demo-workspace"><div><div class="demo-screen"><div class="demo-status"><span>${E?'Ready':'Prêt'}</span><span id="vibEventStatus"></span></div><div class="demo-stage" id="vibStage"><button class="demo-primary" id="vibStart">${E?'Run a trial':'Lancer un essai'}</button></div></div><div class="demo-progress"><i id="vibProgress"></i></div></div><aside class="demo-side"><div class="demo-side-card"><b>${E?'Four framing conditions':'Quatre conditions de cadrage'}</b><p>LL - SS - LS - SL</p></div><div class="demo-side-card"><b>${E?'Three image sizes':'Trois tailles d’image'}</b><p>${E?'Small - medium - large':'Petite - moyenne - grande'}</p></div><div class="demo-side-card"><b>${E?'Response':'Réponse'}</b><p>${E?'As soon as the second image appears, the participant decides whether its framing is identical to or different from the first.':'Dès l’apparition de la seconde image, le participant décide si son cadrage est identique ou différent de celui de la première.'}</p></div></aside></div>`}
  const vibPlaceholder=l=>`<div class="vibex-frame"><div class="vibex-placeholder">${l}</div></div>`;
  async function runVibex(){if(running)return;running=true;const s=document.getElementById('vibStage'),e=document.getElementById('vibEventStatus'),p=document.getElementById('vibProgress'),E=en();s.innerHTML='<div class="demo-fix">+</div>';e.textContent='Fixation - 300 ms';p.style.width='10%';await sleep(300);if(!running)return;s.innerHTML=vibPlaceholder(E?'Image 1 - close or wide view':'Image 1 - plan serré ou large');e.textContent='Image 1 - 200 ms';p.style.width='26%';await sleep(200);if(!running)return;s.innerHTML='<div class="vibex-frame"><div class="demo-mask"></div></div>';e.textContent=E?'Mask - 1000 ms':'Masque - 1000 ms';p.style.width='42%';await sleep(1000);if(!running)return;s.innerHTML=vibPlaceholder(E?'Image 2 - comparison framing':'Image 2 - cadrage de comparaison');e.textContent='Image 2 - 200 ms';p.style.width='72%';await sleep(200);if(!running)return;s.innerHTML=`<div class="demo-response"><button data-vib-answer="same">${E?'Identical':'Identique'}</button><button class="secondary" data-vib-answer="different">${E?'Different':'Différent'}</button></div>`;e.textContent=E?'Framing judgment':'Jugement du cadrage';p.style.width='88%';await new Promise(r=>{const f=x=>{if(x.target.closest('[data-vib-answer]')){s.removeEventListener('click',f);r()}};s.addEventListener('click',f)});s.innerHTML=`<div style="font-weight:900">${E?'Response recorded':'Réponse enregistrée'}</div>`;e.textContent=E?'Trial complete':'Essai terminé';p.style.width='100%';running=false;await sleep(500);s.innerHTML=`<button class="demo-primary" id="vibRestart">${E?'Replay trial':'Rejouer l’essai'}</button>`;document.getElementById('vibRestart')?.addEventListener('click',runVibex)}
  function wireVibex(){document.getElementById('vibStart')?.addEventListener('click',runVibex)}
})();
</script>
'''

if 'id="csi-results-demo-v1"' not in text:
    text = text.replace('</head>', CSS + '\n</head>', 1)
if 'id="studyDemoModal"' not in text:
    text = text.replace('</body>', MODAL + '\n' + JS + '\n</body>', 1)
INDEX.write_text(text, encoding='utf-8')
final = INDEX.read_text(encoding='utf-8')
assert 'TWIXAV - les courbes empiriques' in final
assert 'VIBEX - les temps de réaction convergent avec les jugements' in final
assert 'data-demo-open=\\"twixav\\"' in final
assert 'data-demo-open=\\"vibex\\"' in final
assert 'twixav_empirical_curves.svg' in final
assert 'vibex_rt_interaction.svg' in final
assert 'id="studyDemoModal"' in final
print('CSI update prepared:', len(slides), 'slides')
