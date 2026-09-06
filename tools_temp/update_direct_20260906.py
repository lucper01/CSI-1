import json,re,pathlib

p=pathlib.Path('index.html')
h=p.read_text(encoding='utf-8')
m=re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides',h,re.S)
if not m: raise SystemExit('slides array not found')
slides=json.loads(m.group(1))

def get(title):
    for s in slides:
        if s.get('title')==title:return s
    raise SystemExit('slide not found: '+title)

def set_lang(s,fr=None,en=None):
    if fr:
        s.update(fr)
        if isinstance(s.get('_fr'),dict): s['_fr'].update(fr)
    if en and isinstance(s.get('_en'),dict): s['_en'].update(en)

# 1. Enrich doctoral activities with M1 supervision and research tools.
act=get('Enseignement, formation et encadrement')
fr_act='''<div class="v16-activity"><article><b>54 h eq. TD</b><h3>Enseignement</h3><p>40 h de méthodologie expérimentale en L1 et 14 h de TER en L3. Les 6 h de TP Master sont affichées séparément du total.</p></article><article><b>60 h</b><h3>Formation doctorale</h3><p>Pédagogie universitaire, enseignement, IA et éducation, intégrité scientifique, intelligence économique et Zotero.</p></article><article><b>M1</b><h3>Encadrement</h3><p><strong>TWIXAV</strong> - Alicia Emorine. <strong>VIBEX</strong> - Olivia Hiridjee. Un nouveau mémoire M1 est également proposé sur l’influence de l’olfaction sur la mémoire de scènes visuelles.</p></article><article class="tools"><b>4 outils</b><h3>Développement pour la recherche</h3><p>Conception d’outils pour fiabiliser l’organisation des études et soutenir leur diffusion.</p><div class="v16-tool-pills"><span>Lab Inventory</span><span>Participant Manager</span><span>Dilution Manager</span><span>Portfolio</span></div><small>Inventaire - participants - dilutions olfactives - diffusion du projet STOLF.</small></article></div>'''
en_act='''<div class="v16-activity"><article><b>54 tutorial-equivalent h</b><h3>Teaching</h3><p>40 h of experimental methodology in Year 1 undergraduate courses and 14 h of Year 3 research tutorials. The 6 h of Master's practical classes are shown separately from the total.</p></article><article><b>60 h</b><h3>Doctoral training</h3><p>University pedagogy, teaching, AI and education, research integrity, economic intelligence and Zotero.</p></article><article><b>M1</b><h3>Supervision</h3><p><strong>TWIXAV</strong> - Alicia Emorine. <strong>VIBEX</strong> - Olivia Hiridjee. A new Master 1 project is also proposed on the influence of olfaction on memory for visual scenes.</p></article><article class="tools"><b>4 tools</b><h3>Research tool development</h3><p>Development of tools to strengthen study organization and support dissemination.</p><div class="v16-tool-pills"><span>Lab Inventory</span><span>Participant Manager</span><span>Dilution Manager</span><span>Portfolio</span></div><small>Inventory - participants - olfactory dilutions - dissemination of the STOLF project.</small></article></div>'''
set_lang(act,{'content':fr_act},{'content':en_act})

# 2. Add a dedicated JDD 2026 slide immediately after doctoral activities.
if not any(s.get('title')=='JDD 2026 - faire connaître STOLF' for s in slides):
    idx=slides.index(act)+1
    jdd={
      'chapter':'Année 1','study':'','appendix':False,
      'section':'Année 1','kicker':'Communication scientifique','title':'JDD 2026 - faire connaître STOLF',
      'lead':'La Journée des Doctorants 2026 a constitué un premier temps de valorisation du projet STOLF auprès de la communauté doctorale.',
      'content':'''<div class="v16-jdd"><article class="jdd-main"><span>Journée des Doctorants 2026</span><h3>Première valorisation du projet STOLF</h3><p>Communication doctorale consacrée à la question « Y a-t-il un espace-temps pour les odeurs ? », à ses deux axes et à l’architecture expérimentale mise en place pendant la première année.</p></article><article><b>01</b><h3>Rendre le projet lisible</h3><p>Présenter le fil espace-temps de la thèse et la place respective de l’olfaction, de la vision et de l’audition.</p></article><article><b>02</b><h3>Montrer la démarche</h3><p>Mettre en avant les premiers paradigmes, les outils méthodologiques et la progression vers les études olfactives.</p></article><article class="award"><b>Prix</b><h3>Prix de l’originalité</h3><p>La communication a été distinguée lors de la JDD 2026, renforçant la dynamique de diffusion scientifique du projet.</p></article></div><div class="v16-callout"><strong>Suite :</strong> prolonger cette dynamique avec les prochaines communications et le Portfolio, qui rend le projet STOLF accessible et visible au fil de son développement.</div>''',
      'notes':'Présenter la JDD comme un jalon de communication et de valorisation du projet, sans interrompre le fil scientifique.',
    }
    jdd['_fr']={k:jdd[k] for k in ('section','kicker','title','lead','content','notes')}
    jdd['_en']={
      'section':'Year 1','kicker':'Scientific communication','title':'JDD 2026 - communicating STOLF',
      'lead':'The 2026 Doctoral Day provided an early opportunity to disseminate the STOLF project within the doctoral community.',
      'content':'''<div class="v16-jdd"><article class="jdd-main"><span>Doctoral Day 2026</span><h3>Early dissemination of the STOLF project</h3><p>A doctoral communication centered on the question “Is there a space-time for odors?”, its two research axes, and the experimental architecture developed during the first year.</p></article><article><b>01</b><h3>Make the project readable</h3><p>Present the space-time thread of the thesis and the respective roles of olfaction, vision and audition.</p></article><article><b>02</b><h3>Show the approach</h3><p>Highlight the first paradigms, methodological tools and progression toward olfactory studies.</p></article><article class="award"><b>Award</b><h3>Originality award</h3><p>The communication received the originality award at JDD 2026, supporting the scientific dissemination of the project.</p></article></div><div class="v16-callout"><strong>Next:</strong> extend this dissemination through upcoming events and the Portfolio, which makes the STOLF project accessible throughout its development.</div>''',
      'notes':'Present JDD as a dissemination milestone without interrupting the scientific narrative.'
    }
    slides.insert(idx,jdd)

# 3. Simplify the study timeline and swap COBEX / SOLAR.
retro=get('Rétroplanning des études')
fr_retro='''<div class="v16-retro"><div class="v16-periods"><span>Sept-Déc 2026</span><span>Jan-Juin 2027</span><span>Juil-Déc 2027</span><span>Jan-Juin 2028</span></div><section><h3>Axe 1 - Temps</h3><div class="lane core"><b>Planifiées</b><article data-study="SOFT"><strong>SOFT</strong></article><article data-study="TWIXOLF"><strong>TWIXOLF</strong></article><i></i><i></i></div><div class="lane ext"><b>Complémentaire</b><i></i><i></i><article data-study="SORBET"><strong>SORBET</strong></article><i></i></div></section><section><h3>Axe 2 - Espace</h3><div class="lane core"><b>Planifiées</b><article data-study="VIBEX"><strong>VIBEX</strong></article><article data-study="OASIS"><strong>OASIS</strong></article><i></i><i></i></div><div class="lane ext"><b>Complémentaire / exploratoire</b><i></i><i></i><article data-study="COBEX"><strong>COBEX</strong></article><article class="stack"><span data-study="SOLAR"><strong>SOLAR</strong></span><span data-study="BRAUD"><strong>BRAUD</strong></span><span data-study="BRAUDOLF"><strong>BRAUDOLF</strong></span></article></div></section></div><div class="v16-callout"><strong>En parallèle :</strong> analyses, figures et manuscrits TWIXAV / VIBEX pendant l’année 2; synthèse et rédaction doctorale au fil des collectes.</div>'''
en_retro='''<div class="v16-retro"><div class="v16-periods"><span>Sep-Dec 2026</span><span>Jan-Jun 2027</span><span>Jul-Dec 2027</span><span>Jan-Jun 2028</span></div><section><h3>Axis 1 - Time</h3><div class="lane core"><b>Planned</b><article data-study="SOFT"><strong>SOFT</strong></article><article data-study="TWIXOLF"><strong>TWIXOLF</strong></article><i></i><i></i></div><div class="lane ext"><b>Complementary</b><i></i><i></i><article data-study="SORBET"><strong>SORBET</strong></article><i></i></div></section><section><h3>Axis 2 - Space</h3><div class="lane core"><b>Planned</b><article data-study="VIBEX"><strong>VIBEX</strong></article><article data-study="OASIS"><strong>OASIS</strong></article><i></i><i></i></div><div class="lane ext"><b>Complementary / exploratory</b><i></i><i></i><article data-study="COBEX"><strong>COBEX</strong></article><article class="stack"><span data-study="SOLAR"><strong>SOLAR</strong></span><span data-study="BRAUD"><strong>BRAUD</strong></span><span data-study="BRAUDOLF"><strong>BRAUDOLF</strong></span></article></div></section></div><div class="v16-callout"><strong>In parallel:</strong> TWIXAV / VIBEX analyses, figures and manuscripts during year 2; doctoral synthesis and writing throughout data collection.</div>'''
set_lang(retro,{'lead':'Deux axes et une lecture temporelle simple : les dates sont portées par la frise, les encarts identifient uniquement les études.','content':fr_retro},{'lead':'Two axes and a simple temporal reading: dates are carried by the timeline, while the boxes identify studies only.','content':en_retro})

# 4. CSS fixes for floating resource cards, publications, timelines, activities and JDD.
marker='/* csi-direct-fixes-20260906 */'
if marker not in h:
    css=r'''
    /* csi-direct-fixes-20260906 */
    .study-floating{position:relative!important;right:auto!important;bottom:auto!important;margin:14px 0 0 auto!important;max-width:100%!important;justify-content:flex-end!important;flex-wrap:wrap!important;filter:none!important;z-index:4!important}
    .study-floating .float-card{box-shadow:0 10px 24px color-mix(in srgb,var(--study,var(--accent)) 12%,transparent)}
    .v16-pubs p .study-token{display:inline-flex!important;width:auto!important;height:auto!important;min-width:0!important;min-height:0!important;padding:.05em .38em!important;border-radius:999px!important;background:color-mix(in srgb,var(--study-color) 12%,transparent)!important;color:var(--study-color)!important;border:1px solid color-mix(in srgb,var(--study-color) 24%,transparent)!important;vertical-align:baseline!important;line-height:1.25!important}
    .v16-retro .lane article:not(.stack),.v16-retro .stack span{display:flex;align-items:center;justify-content:center;text-align:center}
    .v16-retro .lane article,.v16-retro .lane>i{min-height:54px}
    .v16-comms{display:grid!important;grid-template-columns:repeat(4,minmax(170px,1fr))!important;gap:20px!important;position:relative!important;max-width:980px!important;margin:34px auto 0!important}
    .v16-comms:before{left:7%!important;right:7%!important}
    .v16-comms article{display:flex!important;flex-direction:column;align-items:center;text-align:center}
    .v16-activity{grid-template-columns:repeat(2,1fr)!important;gap:14px!important}
    .v16-activity article{padding:20px!important}
    .v16-activity b{font-size:1.75rem!important}
    .v16-activity p{font-size:.9rem!important;line-height:1.42!important}
    .v16-tool-pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
    .v16-tool-pills span{padding:6px 9px;border-radius:999px;background:var(--accent-soft);color:var(--accent-strong);font-size:.72rem;font-weight:900}
    .v16-activity small{display:block;margin-top:8px;color:var(--muted);font-size:.75rem;line-height:1.35}
    .v16-jdd{display:grid;grid-template-columns:1.3fr repeat(3,1fr);gap:14px}
    .v16-jdd article{padding:21px;border:1px solid var(--line);border-radius:23px;background:var(--white);box-shadow:var(--shadow-soft)}
    .v16-jdd .jdd-main{background:linear-gradient(145deg,var(--hero-mid),var(--hero-start));color:#fff}
    .v16-jdd span{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;font-weight:950;color:var(--accent)}
    .v16-jdd .jdd-main span,.v16-jdd .jdd-main h3,.v16-jdd .jdd-main p{color:#fff}
    .v16-jdd b{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:var(--accent);color:#fff}
    .v16-jdd h3{font:800 1.18rem Georgia,serif;color:var(--accent-strong);margin:10px 0 6px}
    .v16-jdd p{margin:0;color:var(--muted);font-size:.9rem;line-height:1.45}
    .v16-jdd .award{border-color:color-mix(in srgb,var(--accent) 45%,var(--line));background:color-mix(in srgb,var(--accent) 7%,var(--white))}
    @media(max-width:1100px){.v16-jdd{grid-template-columns:1fr 1fr}.v16-comms{max-width:820px!important}}
    @media(max-width:850px){.study-floating{margin-top:12px!important;justify-content:flex-start!important}.v16-activity,.v16-jdd{grid-template-columns:1fr!important}.v16-comms{grid-template-columns:repeat(2,minmax(170px,1fr))!important;max-width:100%!important}.v16-comms:before{display:none}}
'''
    h=h.replace('</style>',css+'\n</style>',1)

# Re-serialize slide array only after all modifications and insertion.
newarr=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
h=h[:m.start(1)]+newarr+h[m.end(1):]
p.write_text(h,encoding='utf-8')

assert len(slides)==41, len(slides)
assert sum(not s.get('appendix') for s in slides)==39
assert slides.index(get('JDD 2026 - faire connaître STOLF'))==slides.index(get('Enseignement, formation et encadrement'))+1
assert '<small>' not in get('Rétroplanning des études')['content']
assert get('Rétroplanning des études')['content'].index('COBEX') < get('Rétroplanning des études')['content'].index('SOLAR')
print('Updated',len(slides),'slides /',sum(not s.get('appendix') for s in slides),'main slides')
