import json, re, pathlib

p=pathlib.Path('index.html')
h=p.read_text(encoding='utf-8')

# Parse the single native slide array.
m=re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides', h, re.S)
if not m:
    raise SystemExit('slides array not found')
slides=json.loads(m.group(1))

def title(s): return str(s.get('title',''))
def by_title(t):
    for s in slides:
        if title(s)==t: return s
    return None

def add_asset(s, html):
    if not s: return
    for k in ('content',):
        if html not in s.get(k,''):
            s[k]=s.get(k,'')+html
    if isinstance(s.get('_fr'),dict) and html not in s['_fr'].get('content',''):
        s['_fr']['content']=s['_fr'].get('content','')+html

# Remove standalone slides that interrupt the scientific narrative.
remove_titles={
    'Dispositifs expérimentaux et chaîne d’acquisition',
    'Plateforme expérimentale',
    'Affiches des études',
    'Communications et médiation scientifique - calendrier envisagé'
}
slides=[s for s in slides if title(s) not in remove_titles]

# Equalize the status of the five main thesis studies.
arch=by_title('Cinq études centrales, des extensions clairement conditionnelles')
if arch:
    arch['title']='Cinq études structurantes, des extensions clairement conditionnelles'
    arch['lead']='Le programme articule cinq études au même niveau dans le raisonnement de thèse. Elles ont des fonctions différentes, sans hiérarchie de centralité entre TWIXAV, VIBEX, SOFT, OASIS et TWIXOLF.'
    c=arch.get('content','')
    c=c.replace('Étude centrale','Étude de thèse')
    c=c.replace('<div class="card dark"><div class="mono">Étude de thèse</div><h3>SOFT</h3>','<div class="card"><div class="mono">Étude de thèse</div><h3>SOFT</h3>')
    arch['content']=c
    if isinstance(arch.get('_fr'),dict):
        arch['_fr'].update({k:arch[k] for k in ('title','lead','content')})

for s in slides:
    for field in ('title','lead','content','notes'):
        if isinstance(s.get(field),str):
            s[field]=s[field].replace('trois études centrales','trois études prioritaires').replace('Trois études centrales','Trois études prioritaires')
            s[field]=s[field].replace('collectes centrales','collectes prioritaires')
    if isinstance(s.get('_fr'),dict):
        for field in ('title','lead','content','notes'):
            if isinstance(s['_fr'].get(field),str):
                s['_fr'][field]=s['_fr'][field].replace('trois études centrales','trois études prioritaires').replace('Trois études centrales','Trois études prioritaires').replace('collectes centrales','collectes prioritaires')

# Remove Fête de la Science from the remaining communications slide.
com=by_title('Communications prévues')
if com:
    for container in (com, com.get('_fr',{}), com.get('_en',{})):
        if not isinstance(container,dict): continue
        c=container.get('content','')
        c=re.sub(r'<article><b>10\.2026</b><h3>Fête de la Science</h3></article>','',c)
        c=re.sub(r'<article><b>10\.2026</b><h3>Science Festival</h3></article>','',c)
        container['content']=c

# Compact floating resources integrated into relevant study slides.
ASSETS={
'TWIXAV': '''<div class="study-floating" aria-label="Ressources TWIXAV"><a class="float-card poster" href="affiches/TWIXAV.pdf" target="_blank" rel="noopener"><b>Affiche</b><span>TWIXAV</span></a><div class="float-card"><b>Matériel</b><span>PsychoPy - audio + vision - logs temporels</span></div></div>''',
'VIBEX': '''<div class="study-floating" aria-label="Ressources VIBEX"><a class="float-card poster" href="affiches/VIBEX.pdf" target="_blank" rel="noopener"><b>Affiche</b><span>VIBEX</span></a><div class="float-card"><b>Matériel</b><span>PsychoPy - scènes visuelles - réponses comportementales</span></div><div class="float-card m1"><b>Mémoire M1</b><span>Olivia</span></div></div>''',
'SOFT': '''<div class="study-floating" aria-label="Ressources SOFT"><a class="float-card poster" href="affiches/SOFT.pdf" target="_blank" rel="noopener"><b>Affiche</b><span>SOFT</span></a><div class="float-card"><b>Matériel</b><span>Sniff-0 + Spir-0 - respiration - triggers</span></div><div class="float-card"><b>Selon pilote</b><span>BioSemi / BIOPAC</span></div></div>''',
'OASIS': '''<div class="study-floating" aria-label="Ressources OASIS"><a class="float-card poster" href="affiches/OASIS.pdf" target="_blank" rel="noopener"><b>Affiche</b><span>OASIS</span></a><div class="float-card"><b>Matériel</b><span>Sniff-0 + Spir-0 - scènes visuelles - respiration</span></div></div>''',
'TWIXOLF': '''<div class="study-floating" aria-label="Ressources TWIXOLF"><a class="float-card poster" href="affiches/TWIXOLF.pdf" target="_blank" rel="noopener"><b>Affiche</b><span>TWIXOLF</span></a><div class="float-card"><b>Matériel</b><span>Sniff-0 + Spir-0 - PsychoPy - triggers</span></div></div>''',
'FLUXOLF': '''<div class="study-floating" aria-label="Ressources FLUXOLF"><a class="float-card poster" href="affiches/FLUXOLF_1.pdf" target="_blank" rel="noopener"><b>Affiche 1</b><span>FLUXOLF</span></a><a class="float-card poster" href="affiches/FLUXOLF_2.pdf" target="_blank" rel="noopener"><b>Affiche 2</b><span>FLUXOLF</span></a><div class="float-card"><b>Matériel</b><span>BioSemi ActiveTwo + BIOPAC MP160</span></div></div>'''
}
for key,html in ASSETS.items():
    target=None
    if key in ('TWIXAV','VIBEX','SOFT','OASIS','TWIXOLF'):
        target=next((s for s in slides if s.get('study')==key and 'Méthode' in title(s)),None)
        if target is None and key=='TWIXOLF': target=next((s for s in slides if s.get('study')==key),None)
    else:
        target=next((s for s in slides if s.get('study')==key),None)
    add_asset(target,html)

# Improve study labels and M1 wording in the doctoral-activities slide.
act=by_title('Enseignement, formation et encadrement')
if act:
    repl='<p>Accompagnement de mémoires de Master 1 adossés aux paradigmes expérimentaux de la thèse. VIBEX a notamment donné lieu au mémoire M1 d’Olivia.</p>'
    for container in (act,act.get('_fr',{})):
        if isinstance(container,dict):
            container['content']=re.sub(r'<p>Accompagnement de projets de Master autour des paradigmes temporels et de Boundary Extension\.</p>',repl,container.get('content',''))

# Rebuild a logical narrative order from exact titles.
order=[
"Y a-t-il un espace-temps pour les odeurs ?",
"Encadrement et CSI",
"Deux axes",
"« No space, no time? » - le paradoxe de l’attention olfactive",
"Cinq études structurantes, des extensions clairement conditionnelles",
"Ce qui a été fait cette année",
"TWIXAV - pourquoi commencer par une fenêtre temporelle audiovisuelle ?",
"TWIXAV - Méthode",
"TWIXAV - Résultats",
"TWIXAV - ce que les résultats changent pour la suite",
"VIBEX - pourquoi établir une référence visuelle ?",
"VIBEX - Méthode",
"VIBEX - résultats du prétest et statut",
"VIBEX - ce que le prétest permet maintenant",
"FLUXOLF",
"Enseignement, formation et encadrement",
"Deux acquis expérimentaux structurent la suite",
"Ce que l’année 1 a sécurisé",
"Deux références, trois études prioritaires pour l’année 2",
"Trois études prioritaires",
"SOFT - mesurer le temps propre de chaque modalité",
"SOFT - Méthode",
"OASIS - tester l’influence olfactive sur la mémoire spatiale des scènes",
"OASIS - Méthode",
"TWIXOLF - transposer la liaison temporelle à l’olfaction",
"TWIXOLF - Méthode",
"Études complémentaires et exploratoires",
"SORBET","SOLAR","COBEX","BRAUD","BRAUDOLF",
"Rétroplanning des études",
"Communications prévues",
"Publications",
"Points à discuter",
"Bilan",
"Merci pour votre attention",
"Axe 1 - temps et multisensorialité",
"Axe 2 - espace et scènes"
]
# Title may still be old transition wording; normalize it.
tr=by_title('Deux références, trois études centrales pour l’année 2')
if tr:
    tr['title']='Deux références, trois études prioritaires pour l’année 2'
    if isinstance(tr.get('_fr'),dict): tr['_fr']['title']=tr['title']

rank={t:i for i,t in enumerate(order)}
original_pos={id(s):i for i,s in enumerate(slides)}
slides.sort(key=lambda s:(rank.get(title(s),1000),original_pos[id(s)]))

# Replace slide array.
newarr=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
h=h[:m.start(1)]+newarr+h[m.end(1):]

# Add floating-resource and universal study-token CSS before </style>.
css=r'''
    .study-floating{position:absolute;right:clamp(18px,2.4vw,38px);bottom:clamp(18px,2.4vw,34px);z-index:8;display:flex;gap:9px;align-items:stretch;max-width:min(62%,760px);filter:drop-shadow(0 10px 18px rgba(11,47,35,.12))}
    .float-card{display:flex;flex-direction:column;justify-content:center;gap:2px;min-width:130px;max-width:210px;padding:9px 12px;border-radius:16px;border:1px solid color-mix(in srgb,var(--study,var(--accent)) 34%,var(--line));background:color-mix(in srgb,var(--white) 91%,transparent);backdrop-filter:blur(12px);text-decoration:none;color:var(--text);font-size:.72rem;line-height:1.25}
    .float-card b{color:var(--study,var(--accent));font-size:.68rem;text-transform:uppercase;letter-spacing:.07em}.float-card.poster{background:color-mix(in srgb,var(--study,var(--accent)) 11%,var(--white));}.float-card.m1{border-style:dashed}
    .study-token{display:inline-flex;align-items:center;padding:.08em .42em;border-radius:999px;font-weight:900;line-height:1.25;background:color-mix(in srgb,var(--study-color) 13%,transparent);color:var(--study-color);border:1px solid color-mix(in srgb,var(--study-color) 28%,transparent);white-space:nowrap}
    [data-study]{--study-color:var(--accent)}
    @media(max-width:900px){.study-floating{position:static;max-width:none;margin-top:14px;flex-wrap:wrap}.float-card{min-width:120px;flex:1 1 120px}.slide-shell{position:relative}}
'''
h=h.replace('</style>',css+'\n</style>',1)

# Replace single runtime with one cleaner enhancer: no generic PDF button on every slide.
rt=re.search(r'<script id="csi-single-runtime">.*?</script>',h,re.S)
if not rt: raise SystemExit('single runtime not found')
runtime=r'''<script id="csi-single-runtime">
(()=>{
  const COLORS={TWIXAV:'#2f6f9f',SOFT:'#7652a8',TWIXOLF:'#c36c32',VIBEX:'#2f7d5a',OASIS:'#b44e6c',SORBET:'#9a6b20',SOLAR:'#d09422',COBEX:'#5865a8',BRAUD:'#4f7187',BRAUDOLF:'#875a7c',FLUXOLF:'#a34d5d'};
  const names=Object.keys(COLORS).sort((a,b)=>b.length-a.length);
  function studyOf(s){const e=String(s&&s.study||'').toUpperCase();if(e)return e;const m=String(s&&s.title||'').match(/^(TWIXAV|TWIXOLF|SOFT|VIBEX|OASIS|SORBET|SOLAR|COBEX|BRAUDOLF|BRAUD|FLUXOLF)\b/i);return m?m[1].toUpperCase():''}
  function wrapMentions(root){
    const rx=new RegExp('\\b('+names.join('|')+')\\b','g');
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode(n){
      if(!n.nodeValue||!rx.test(n.nodeValue)){rx.lastIndex=0;return NodeFilter.FILTER_REJECT}rx.lastIndex=0;
      const p=n.parentElement;if(!p||p.closest('.study-token,[data-study],script,style,code,.v16-acronym'))return p?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_REJECT;
    }});
    const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
    nodes.forEach(n=>{const frag=document.createDocumentFragment();let last=0;String(n.nodeValue).replace(rx,(match,_,off)=>{if(off>last)frag.append(document.createTextNode(n.nodeValue.slice(last,off)));const k=match.toUpperCase();const sp=document.createElement('span');sp.className='study-token';sp.dataset.study=k;sp.style.setProperty('--study-color',COLORS[k]);sp.textContent=match;frag.append(sp);last=off+match.length});if(last<n.nodeValue.length)frag.append(document.createTextNode(n.nodeValue.slice(last)));n.replaceWith(frag)});
  }
  function enhance(){
    const els=[...document.querySelectorAll('#deck .slide,.slide')];
    slides.forEach((s,i)=>{const el=els[i];if(!el)return;const k=studyOf(s),c=COLORS[k];if(c){el.style.setProperty('--study',c);el.style.setProperty('--accent',c);el.classList.add('v16-study-slide')}wrapMentions(el)});
    document.querySelectorAll('[data-study]').forEach(el=>{const k=String(el.dataset.study||'').toUpperCase(),c=COLORS[k];if(c){el.style.setProperty('--study-color',c);el.style.setProperty('--study',c)}});
    document.documentElement.dataset.singleLayer='1';
  }
  const old=window.renderSlides;if(typeof old==='function'){window.renderSlides=function(){const r=old.apply(this,arguments);queueMicrotask(enhance);return r}}
  enhance();
})();
</script>'''
h=h[:rt.start()]+runtime+h[rt.end():]

p.write_text(h,encoding='utf-8')
print('slides',len(slides),'bytes',p.stat().st_size)
print('\n'.join(f'{i+1:02d} {title(s)}' for i,s in enumerate(slides)))
