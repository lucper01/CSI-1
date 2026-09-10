from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'id="laserBtn"' in text or 'id="laserPointer"' in text:
    raise SystemExit('Laser pointer already present')

css_anchor = "    .drawer, .navigator, .overview, .notes-panel {"
html_anchor = '      <button class="icon-btn" id="fullscreenBtn" type="button" aria-label="Plein écran" title="Plein écran">⛶</button>'
js_anchor = "  document.getElementById('fullscreenBtn').addEventListener('click',async()=>{ try{ if(!document.fullscreenElement) await document.documentElement.requestFullscreen(); else await document.exitFullscreen(); }catch(e){showToast('Le plein écran n\\'est pas disponible dans ce contexte.');} });"
key_anchor = "    if(k==='f') document.getElementById('fullscreenBtn').click();"

if text.count(css_anchor) < 1:
    raise SystemExit('CSS anchor missing')
for anchor, label in [(html_anchor, 'HTML'), (js_anchor, 'JS'), (key_anchor, 'keyboard')]:
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f'Unexpected {label} anchor count: {count}')

pointer_css = '''    .laser-btn-dot {
      display:block;
      width:11px;
      height:11px;
      border-radius:50%;
      background:#e00000;
      box-shadow:0 0 0 2px rgba(224,0,0,.15);
    }
    #laserBtn.active {
      background:rgba(224,0,0,.12);
      color:#b00000;
    }
    #laserPointer {
      position:fixed;
      z-index:3000;
      width:16px;
      height:16px;
      border-radius:50%;
      background:#e00000;
      box-shadow:0 0 0 5px rgba(224,0,0,.16), 0 0 18px rgba(224,0,0,.72);
      transform:translate(-50%,-50%);
      pointer-events:none;
      opacity:0;
      visibility:hidden;
      transition:opacity .08s linear;
    }
    #laserPointer.visible {
      opacity:1;
      visibility:visible;
    }
    body.laser-enabled .slide,
    body.laser-enabled .slide * {
      cursor:none !important;
    }

'''
text = text.replace(css_anchor, pointer_css + css_anchor, 1)

pointer_button = '      <button class="icon-btn" id="laserBtn" type="button" aria-label="Activer le pointeur rouge" aria-pressed="false" title="Pointeur rouge (P)"><span class="laser-btn-dot" aria-hidden="true"></span></button>\n'
text = text.replace(html_anchor, pointer_button + html_anchor, 1)

pointer_js = '''  const laserBtn = document.getElementById('laserBtn');
  const laserPointer = document.createElement('div');
  laserPointer.id = 'laserPointer';
  laserPointer.setAttribute('aria-hidden','true');
  document.body.appendChild(laserPointer);
  let laserEnabled = false;
  function setLaserPointer(enabled){
    laserEnabled = !!enabled;
    document.body.classList.toggle('laser-enabled',laserEnabled);
    laserBtn.classList.toggle('active',laserEnabled);
    laserBtn.setAttribute('aria-pressed',laserEnabled?'true':'false');
    laserBtn.setAttribute('aria-label',laserEnabled?'Désactiver le pointeur rouge':'Activer le pointeur rouge');
    laserBtn.title = laserEnabled?'Désactiver le pointeur rouge (P)':'Pointeur rouge (P)';
    if(!laserEnabled) laserPointer.classList.remove('visible');
  }
  laserBtn.addEventListener('click',()=>setLaserPointer(!laserEnabled));
  document.addEventListener('pointermove',e=>{
    if(!laserEnabled || e.pointerType==='touch'){
      laserPointer.classList.remove('visible');
      return;
    }
    const target = e.target instanceof Element ? e.target : null;
    const slide = target?.closest('.slide');
    if(!slide){
      laserPointer.classList.remove('visible');
      return;
    }
    laserPointer.style.left = `${e.clientX}px`;
    laserPointer.style.top = `${e.clientY}px`;
    laserPointer.classList.add('visible');
  });
  document.addEventListener('pointerleave',()=>laserPointer.classList.remove('visible'));
  document.addEventListener('visibilitychange',()=>{if(document.hidden) laserPointer.classList.remove('visible');});
'''
text = text.replace(js_anchor, js_anchor + '\n' + pointer_js, 1)
text = text.replace(key_anchor, key_anchor + "\n    if(k==='p'){e.preventDefault();setLaserPointer(!laserEnabled);}", 1)

path.write_text(text, encoding='utf-8')
