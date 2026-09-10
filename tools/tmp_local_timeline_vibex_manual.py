from pathlib import Path
import json
import re
import subprocess
import tempfile

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
original = text

# ---------- Parse the JSON-compatible slides array ----------
marker = 'const slides = ['
start_marker = text.index(marker)
arr_start = text.index('[', start_marker)

def matching_bracket(src, start):
    depth = 0
    quote = None
    esc = False
    for i in range(start, len(src)):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return i
    raise RuntimeError('Could not locate end of slides array')

arr_end = matching_bracket(text, arr_start)
slides = json.loads(text[arr_start:arr_end + 1])

# ---------- Add a compact manual VIBEX sequence to the methodology slide ----------
def manual_markup(lang):
    if lang == 'en':
        return (
            '<div class="vibex-manual-demo" data-vibex-manual data-vib-step-current="0">'
            '<div class="vibex-manual-head"><span>MANUAL PREVIEW</span><b data-vibex-manual-label>Image 1</b></div>'
            '<button class="vibex-manual-frame" type="button" data-vibex-manual-next aria-label="Go to the next VIBEX step">'
            '<img data-vibex-manual-img src="assets/demo/image_S_16.jpg" alt="VIBEX image 1 - close framing"></button>'
            '<div class="vibex-manual-controls" role="group" aria-label="VIBEX trial steps">'
            '<button type="button" class="active" data-vib-step="0">Image 1</button>'
            '<button type="button" data-vib-step="1">Mask</button>'
            '<button type="button" data-vib-step="2">Image 2</button>'
            '</div></div>'
        )
    return (
        '<div class="vibex-manual-demo" data-vibex-manual data-vib-step-current="0">'
        '<div class="vibex-manual-head"><span>APERÇU MANUEL</span><b data-vibex-manual-label>Image 1</b></div>'
        '<button class="vibex-manual-frame" type="button" data-vibex-manual-next aria-label="Passer à l’étape VIBEX suivante">'
        '<img data-vibex-manual-img src="assets/demo/image_S_16.jpg" alt="VIBEX image 1 - cadrage serré"></button>'
        '<div class="vibex-manual-controls" role="group" aria-label="Étapes de l’essai VIBEX">'
        '<button type="button" class="active" data-vib-step="0">Image 1</button>'
        '<button type="button" data-vib-step="1">Masque</button>'
        '<button type="button" data-vib-step="2">Image 2</button>'
        '</div></div>'
    )

method_re = re.compile(r'(<div class="method-demo-wrap"><button class="study-demo-launch"[^>]*data-demo-open="vibex".*?</button></div>)', re.S)
changed_variants = 0
vibex_main_number = None
visible = [i for i, s in enumerate(slides) if not s.get('appendix')]

for i, slide in enumerate(slides):
    has_vibex_demo = 'data-demo-open="vibex"' in str(slide.get('content', '')) or 'data-demo-open="vibex"' in str(slide.get('_fr', {}).get('content', ''))
    if not has_vibex_demo:
        continue
    if i in visible:
        vibex_main_number = visible.index(i) + 1
    for container_key, lang in ((None, 'fr'), ('_fr', 'fr'), ('_en', 'en')):
        container = slide if container_key is None else slide.get(container_key)
        if not isinstance(container, dict):
            continue
        content = container.get('content')
        if not isinstance(content, str) or 'data-demo-open="vibex"' not in content or 'data-vibex-manual' in content:
            continue
        m = method_re.search(content)
        if not m:
            raise RuntimeError(f'Could not locate VIBEX demo launcher in variant {container_key or "top"}')
        replacement = '<div class="vibex-demo-row">' + m.group(1) + manual_markup(lang) + '</div>'
        container['content'] = content[:m.start()] + replacement + content[m.end():]
        changed_variants += 1

if changed_variants not in (0, 3):
    raise RuntimeError(f'Unexpected VIBEX variant modification count: {changed_variants}')
if vibex_main_number is None:
    raise RuntimeError('VIBEX methodology slide not found')
print(f'VIBEX methodology slide is main slide {vibex_main_number}; modified variants={changed_variants}')

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
text = text[:arr_start] + new_array + text[arr_end + 1:]

# ---------- Replace the global six-part timeline with local timelines ----------
start_tag = '// CSI_LOCAL_PART_TIMELINE'
end_tag = 'function studyAxisBadgeFor(s){'
block_start = text.index(start_tag)
block_end = text.index(end_tag, block_start)

local_timeline_js = r'''// CSI_LOCAL_PART_TIMELINE
function timelineStepLabel(s,E){
  const study=String(s.study||'').trim();
  let raw=String(s.kicker||s.title||'').trim();
  if(study && raw.toUpperCase().startsWith(study.toUpperCase())){
    raw=raw.slice(study.length).replace(/^\s*[-–:]\s*/,'').trim();
  }
  if(!raw) raw=String(s.title||'').trim();
  const low=raw.toLowerCase();
  if(E){
    if(/introduction|\bintro\b/.test(low)) return 'INTRO';
    if(/paradigm|method/.test(low)) return 'METHOD';
    if(/result/.test(low)) return 'RESULTS';
    if(/discussion/.test(low)) return 'DISCUSSION';
    if(/conclusion/.test(low)) return 'CONCLUSION';
    if(/planning/.test(low)) return 'PLANNING';
    if(/activit/.test(low)) return 'ACTIVITIES';
    if(/projection/.test(low)) return 'PROJECTION';
    if(/question/.test(low)) return 'QUESTION';
  }else{
    if(/introduction|\bintro\b/.test(low)) return 'INTRO';
    if(/paradigme|méthode|methode/.test(low)) return 'MÉTHODE';
    if(/résultat|resultat/.test(low)) return 'RÉSULTATS';
    if(/discussion/.test(low)) return 'DISCUSSION';
    if(/conclusion/.test(low)) return 'CONCLUSION';
    if(/planification/.test(low)) return 'PLANIFICATION';
    if(/activité|activite/.test(low)) return 'ACTIVITÉS';
    if(/projection/.test(low)) return 'PROJECTION';
    if(/question/.test(low)) return 'QUESTION';
  }
  raw=raw.replace(/^(axe|axis)\s*\d+\s*[-–:]\s*/i,'').trim();
  return raw.length>22 ? raw.slice(0,21).trim()+'…' : raw.toUpperCase();
}

function partTimelineFor(index){
  const s=slides[index];
  if(!s || s.appendix || s.divider) return null;
  const E=document.documentElement.lang==='en';
  const vis=visibleIndexes();
  const study=String(s.study||'').trim().toUpperCase();
  const chapter=String(s.chapter||'').trim();
  const section=String(s.section||'').trim();
  let members=[];
  let group='';

  if(study){
    members=vis.filter(i=>{
      const x=slides[i];
      return x && !x.appendix && !x.divider && String(x.study||'').trim().toUpperCase()===study;
    });
    group=study;
  }else{
    members=vis.filter(i=>{
      const x=slides[i];
      if(!x || x.appendix || x.divider || String(x.study||'').trim()) return false;
      if(chapter) return String(x.chapter||'').trim()===chapter;
      return section && String(x.section||'').trim()===section;
    });
    group=section||chapter;
  }

  if(!members.includes(index)) members.push(index);
  members.sort((a,b)=>a-b);
  const steps=[];
  const stepByIndex=new Map();
  members.forEach(i=>{
    const label=timelineStepLabel(slides[i],E);
    if(!label) return;
    let pos=steps.indexOf(label);
    if(pos<0){ pos=steps.length; steps.push(label); }
    stepByIndex.set(i,pos);
  });
  if(!steps.length) return null;
  const active=stepByIndex.has(index) ? stepByIndex.get(index) : 0;
  return {steps,active,group};
}

function renderPartTimeline(index){
  const t=partTimelineFor(index);
  if(!t) return '';
  const label=document.documentElement.lang==='en'?'Progress within this section':'Progression dans cette partie';
  const group=t.group ? `<span class="part-local-label">${esc(t.group)}</span><i aria-hidden="true"></i>` : '';
  return `<div class="part-timeline footer-part-timeline local" aria-label="${label}">${group}${t.steps.map((step,j)=>`<span class="part-step${j===t.active?' active':''}">${esc(step)}</span>`).join('<i aria-hidden="true"></i>')}</div>`;
}

'''
text = text[:block_start] + local_timeline_js + text[block_end:]

# ---------- CSS for the local timeline label + discreet manual viewer ----------
css_marker = '/* CSI_VIBEX_MANUAL_LOCAL_TIMELINE */'
if css_marker not in text:
    css = r'''
<style id="csi-vibex-manual-local-timeline">
/* CSI_VIBEX_MANUAL_LOCAL_TIMELINE */
.deck-footer .footer-part-timeline.local .part-local-label{
  display:inline-flex;align-items:center;max-width:118px;padding:4px 8px;border-radius:999px;
  background:var(--accent-soft);color:var(--accent-strong);font-weight:950;letter-spacing:.045em;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.vibex-demo-row{display:grid;grid-template-columns:minmax(0,520px) 270px;gap:12px;align-items:stretch;margin-top:14px;max-width:810px}
.vibex-demo-row .method-demo-wrap{margin-top:0;min-width:0}
.vibex-demo-row .method-demo-wrap .study-demo-launch{height:100%;min-height:132px}
.vibex-manual-demo{border:1px solid var(--line);border-radius:18px;background:color-mix(in srgb,var(--white) 86%,transparent);padding:9px 10px 10px;box-shadow:0 8px 20px color-mix(in srgb,#2f7d5a 8%,transparent);min-width:0}
.vibex-manual-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:7px;color:var(--muted);font-size:.63rem;line-height:1;text-transform:uppercase;letter-spacing:.07em;font-weight:850}
.vibex-manual-head b{color:#2f7d5a;font-size:.68rem;letter-spacing:.02em}
.vibex-manual-frame{display:block;width:100%;height:78px;padding:0;border:0;border-radius:11px;overflow:hidden;background:color-mix(in srgb,var(--accent-pale) 74%,var(--white));cursor:pointer;box-shadow:inset 0 0 0 1px var(--line)}
.vibex-manual-frame img{display:block;width:100%;height:100%;object-fit:cover}
.vibex-manual-controls{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin-top:7px}
.vibex-manual-controls button{border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--muted);padding:4px 5px;font-size:.64rem;line-height:1.15;font-weight:800;cursor:pointer;white-space:nowrap}
.vibex-manual-controls button:hover{background:var(--accent-pale);color:var(--text)}
.vibex-manual-controls button.active{background:color-mix(in srgb,#2f7d5a 14%,var(--white));border-color:color-mix(in srgb,#2f7d5a 42%,var(--line));color:#2f7d5a;font-weight:950}
@media(max-width:900px){.vibex-demo-row{grid-template-columns:1fr;max-width:none}.vibex-demo-row .method-demo-wrap .study-demo-launch{min-height:0}.vibex-manual-demo{width:min(100%,360px)}.vibex-manual-frame{height:96px}}
</style>
'''
    text = text.replace('</head>', css + '\n</head>', 1)

# ---------- Event delegation for the manual VIBEX viewer ----------
js_marker = '// CSI_VIBEX_MANUAL_RUNTIME'
if js_marker not in text:
    js = r'''
<script id="csi-vibex-manual-runtime">
// CSI_VIBEX_MANUAL_RUNTIME
(()=>{
  const steps={
    fr:[
      {src:'assets/demo/image_S_16.jpg',label:'Image 1',alt:'VIBEX image 1 - cadrage serré'},
      {src:'assets/demo/Masque_SCR.webp',label:'Masque',alt:'VIBEX - masque visuel'},
      {src:'assets/demo/image_L_16.jpg',label:'Image 2',alt:'VIBEX image 2 - cadrage large'}
    ],
    en:[
      {src:'assets/demo/image_S_16.jpg',label:'Image 1',alt:'VIBEX image 1 - close framing'},
      {src:'assets/demo/Masque_SCR.webp',label:'Mask',alt:'VIBEX - visual mask'},
      {src:'assets/demo/image_L_16.jpg',label:'Image 2',alt:'VIBEX image 2 - wide framing'}
    ]
  };
  function setStep(box,n){
    if(!box) return;
    const lang=document.documentElement.lang==='en'?'en':'fr';
    const list=steps[lang];
    const idx=((Number(n)||0)%list.length+list.length)%list.length;
    const item=list[idx];
    box.dataset.vibStepCurrent=String(idx);
    const img=box.querySelector('[data-vibex-manual-img]');
    if(img){img.src=item.src;img.alt=item.alt;}
    const label=box.querySelector('[data-vibex-manual-label]');
    if(label) label.textContent=item.label;
    box.querySelectorAll('[data-vib-step]').forEach(btn=>btn.classList.toggle('active',Number(btn.dataset.vibStep)===idx));
  }
  document.addEventListener('click',e=>{
    const direct=e.target.closest('[data-vib-step]');
    if(direct){
      const box=direct.closest('[data-vibex-manual]');
      if(box){e.preventDefault();e.stopPropagation();setStep(box,direct.dataset.vibStep);}
      return;
    }
    const next=e.target.closest('[data-vibex-manual-next]');
    if(next){
      const box=next.closest('[data-vibex-manual]');
      if(box){e.preventDefault();e.stopPropagation();setStep(box,Number(box.dataset.vibStepCurrent||0)+1);}
    }
  });
})();
</script>
'''
    text = text.replace('</body>', js + '\n</body>', 1)

if text == original:
    raise RuntimeError('Patch made no changes')

PATH.write_text(text, encoding='utf-8')

# ---------- Validate the script containing the slides array ----------
updated = PATH.read_text(encoding='utf-8')
script_matches = list(re.finditer(r'<script(?:\s[^>]*)?>(.*?)</script>', updated, re.S | re.I))
slides_script = next((m.group(1) for m in script_matches if 'const slides = [' in m.group(1)), None)
manual_script = next((m.group(1) for m in script_matches if 'CSI_VIBEX_MANUAL_RUNTIME' in m.group(1)), None)
if not slides_script or not manual_script:
    raise RuntimeError('Could not extract scripts for validation')
for label, src in [('slides', slides_script), ('vibex-manual', manual_script)]:
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
        f.write(src)
        tmp = f.name
    result = subprocess.run(['node', '--check', tmp], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Node validation failed for {label}:\n{result.stderr}')

# Re-parse final slides array to ensure it remains valid JSON-compatible data.
final_start_marker = updated.index(marker)
final_arr_start = updated.index('[', final_start_marker)
final_arr_end = matching_bracket(updated, final_arr_start)
final_slides = json.loads(updated[final_arr_start:final_arr_end + 1])
manual_hits = 0
for s in final_slides:
    for c in (s, s.get('_fr') if isinstance(s.get('_fr'), dict) else {}, s.get('_en') if isinstance(s.get('_en'), dict) else {}):
        if 'data-vibex-manual' in str(c.get('content', '')):
            manual_hits += 1
if manual_hits != 3:
    raise RuntimeError(f'Expected 3 VIBEX manual viewer variants, found {manual_hits}')
if "['CONTEXTE','ARCHITECTURE','ANNÉE 1','ANNÉE 2','ANNÉE 3','PLANIFICATION']" in updated:
    raise RuntimeError('Old global timeline is still present')
print('Validation OK: local timeline + manual VIBEX viewer')
