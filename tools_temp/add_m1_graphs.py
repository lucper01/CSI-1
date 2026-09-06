import json,re,pathlib

p=pathlib.Path('index.html')
h=p.read_text(encoding='utf-8')
m=re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides',h,re.S)
if not m: raise SystemExit('slides array not found')
slides=json.loads(m.group(1))

def get(t):
    for s in slides:
        if s.get('title')==t:return s
    raise SystemExit('slide not found: '+t)

def set_content(s,fr,en=None):
    s['content']=fr
    if isinstance(s.get('_fr'),dict):s['_fr']['content']=fr
    if en is not None and isinstance(s.get('_en'),dict):s['_en']['content']=en

# Full M1 names in the study resource cards.
tw_m=get('TWIXAV - Méthode')
for obj in [tw_m,tw_m.get('_fr',{})]:
    if isinstance(obj,dict):
        c=obj.get('content','')
        if 'Alicia Emorine' not in c and 'study-floating' in c:
            pos=c.rfind('</div>')
            if pos<0:raise SystemExit('TWIXAV floating-card end not found')
            card='<div class="float-card m1"><b>Mémoire M1</b><span>Alicia Emorine</span></div>'
            c=c[:pos]+card+c[pos:]
        obj['content']=c
v_m=get('VIBEX - Méthode')
for obj in [v_m,v_m.get('_fr',{})]:
    if isinstance(obj,dict):obj['content']=obj.get('content','').replace('<span>Olivia</span>','<span>Olivia Hiridjee</span>')

# Result slides: scientific summaries + figure from each M1.
tw=get('TWIXAV - Résultats')
tw_fr='''<div class="m1-results-layout"><div class="m1-results-copy"><div class="m1-owner"><span>Mémoire M1</span><strong>Alicia Emorine</strong></div><div class="m1-stat-grid"><div><b>n = 19</b><span>participants</span></div><div><b>p &lt; .001</b><span>effet de la durée</span></div><div><b>p &lt; .001</b><span>largeur de la TBW</span></div><div><b>n.s.</b><span>PSS et asymétrie selon la durée</span></div></div><div class="callout m1-key-result"><strong>Résultat clé :</strong> la largeur moyenne individuelle de la TBW diminue avec la durée des stimuli - environ 660 ms à 50 ms, 594 ms à 150 ms et 558 ms à 250 ms.</div></div><figure class="m1-result-figure"><img src="assets/results/twixav_m1_alicia.svg" alt="Fenêtres d’intégration temporelle audiovisuelle pour des stimuli de 50, 150 et 250 ms"><figcaption><strong>TWIXAV - Alicia Emorine.</strong> Fenêtres temporelles ajustées selon la durée - redessin de la Figure 5 du mémoire pour la présentation.</figcaption></figure></div>'''
tw_en='''<div class="m1-results-layout"><div class="m1-results-copy"><div class="m1-owner"><span>Master 1 thesis</span><strong>Alicia Emorine</strong></div><div class="m1-stat-grid"><div><b>n = 19</b><span>participants</span></div><div><b>p &lt; .001</b><span>duration effect</span></div><div><b>p &lt; .001</b><span>TBW width</span></div><div><b>n.s.</b><span>PSS and asymmetry across durations</span></div></div><div class="callout m1-key-result"><strong>Key result:</strong> mean individual TBW width decreases with stimulus duration - about 660 ms at 50 ms, 594 ms at 150 ms and 558 ms at 250 ms.</div></div><figure class="m1-result-figure"><img src="assets/results/twixav_m1_alicia.svg" alt="Audiovisual temporal binding windows for 50, 150 and 250 ms stimuli"><figcaption><strong>TWIXAV - Alicia Emorine.</strong> Fitted temporal windows by duration - redrawn from Figure 5 of the Master 1 thesis for presentation.</figcaption></figure></div>'''
set_content(tw,tw_fr,tw_en)

vb=get('VIBEX - résultats du prétest et statut')
vb_fr='''<div class="m1-results-layout"><div class="m1-results-copy"><div class="m1-owner"><span>Mémoire M1</span><strong>Olivia Hiridjee</strong></div><div class="m1-stat-grid"><div><b>n = 24</b><span>participants</span></div><div><b>p &lt; .001</b><span>effet de la condition</span></div><div><b>p &lt; .001</b><span>interaction Condition × Taille</span></div><div><b>p = .601</b><span>effet principal de la taille - n.s.</span></div></div><div class="callout m1-key-result"><strong>Résultat clé :</strong> l’écart SL-LS est maximal pour les petites images (30,6 %), intermédiaire pour les moyennes (25,3 %) et plus faible pour les grandes (14,8 %).</div></div><figure class="m1-result-figure"><img src="assets/results/vibex_m1_olivia.svg" alt="Pourcentage de réponses identique pour les conditions LL, SS, SL et LS selon trois tailles d’image"><figcaption><strong>VIBEX - Olivia Hiridjee.</strong> Réponses « identique » selon le cadrage et la taille - redessin de la Figure 6 du mémoire pour la présentation.</figcaption></figure></div>'''
vb_en='''<div class="m1-results-layout"><div class="m1-results-copy"><div class="m1-owner"><span>Master 1 thesis</span><strong>Olivia Hiridjee</strong></div><div class="m1-stat-grid"><div><b>n = 24</b><span>participants</span></div><div><b>p &lt; .001</b><span>condition effect</span></div><div><b>p &lt; .001</b><span>Condition × Size interaction</span></div><div><b>p = .601</b><span>main size effect - n.s.</span></div></div><div class="callout m1-key-result"><strong>Key result:</strong> the SL-LS gap is largest for small images (30.6%), intermediate for medium images (25.3%), and smaller for large images (14.8%).</div></div><figure class="m1-result-figure"><img src="assets/results/vibex_m1_olivia.svg" alt="Same-response rate for LL, SS, SL and LS conditions across three image sizes"><figcaption><strong>VIBEX - Olivia Hiridjee.</strong> Same responses by framing condition and image size - redrawn from Figure 6 of the Master 1 thesis for presentation.</figcaption></figure></div>'''
set_content(vb,vb_fr,vb_en)

# Update doctoral supervision wording to name both M1 students.
for s in slides:
    if s.get('title')=='Enseignement, formation et encadrement':
        for obj in [s,s.get('_fr',{})]:
            if isinstance(obj,dict):
                c=obj.get('content','')
                c=c.replace('VIBEX a notamment donné lieu au mémoire M1 d’Olivia.','TWIXAV a donné lieu au mémoire M1 d’Alicia Emorine et VIBEX au mémoire M1 d’Olivia Hiridjee.')
                c=c.replace("VIBEX a notamment donné lieu au mémoire M1 d'Olivia.","TWIXAV a donné lieu au mémoire M1 d'Alicia Emorine et VIBEX au mémoire M1 d'Olivia Hiridjee.")
                obj['content']=c

newarr=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
h=h[:m.start(1)]+newarr+h[m.end(1):]

css='''\n    .m1-results-layout{display:grid;grid-template-columns:minmax(0,.92fr) minmax(360px,1.08fr);gap:clamp(18px,2.3vw,34px);align-items:center;margin-top:8px}\n    .m1-results-copy{min-width:0}.m1-owner{display:inline-flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid color-mix(in srgb,var(--study,var(--accent)) 30%,var(--line));border-radius:999px;background:color-mix(in srgb,var(--study,var(--accent)) 9%,var(--white));margin-bottom:14px}.m1-owner span{font-size:.69rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:800}.m1-owner strong{color:var(--study,var(--accent));font-size:.88rem}.m1-stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.m1-stat-grid>div{padding:11px 12px;border:1px solid color-mix(in srgb,var(--study,var(--accent)) 22%,var(--line));border-radius:15px;background:color-mix(in srgb,var(--study,var(--accent)) 5%,var(--white));display:flex;flex-direction:column;gap:2px}.m1-stat-grid b{font-size:1.05rem;color:var(--study,var(--accent))}.m1-stat-grid span{font-size:.72rem;line-height:1.25;color:var(--muted)}.m1-key-result{margin-top:12px!important;font-size:.86rem;line-height:1.4}.m1-result-figure{margin:0;min-width:0;padding:12px;border-radius:22px;border:1px solid color-mix(in srgb,var(--study,var(--accent)) 26%,var(--line));background:rgba(255,255,255,.94);box-shadow:0 16px 38px rgba(8,45,32,.10)}.m1-result-figure img{display:block;width:100%;max-height:430px;object-fit:contain;border-radius:13px}.m1-result-figure figcaption{font-size:.68rem;line-height:1.3;color:#53645d;margin-top:7px}.m1-result-figure figcaption strong{color:var(--study,var(--accent))}\n    @media(max-width:980px){.m1-results-layout{grid-template-columns:1fr;align-items:start}.m1-result-figure img{max-height:300px}.m1-stat-grid{grid-template-columns:1fr 1fr}}\n    @media(max-width:620px){.m1-stat-grid{grid-template-columns:1fr}.m1-owner{display:flex;width:max-content;max-width:100%}.m1-result-figure{padding:8px}.m1-result-figure img{max-height:260px}}\n'''
if '.m1-results-layout{' not in h:
    h=h.replace('</style>',css+'\n</style>',1)

p.write_text(h,encoding='utf-8')
print('M1 figures integrated; slides=',len(slides))
