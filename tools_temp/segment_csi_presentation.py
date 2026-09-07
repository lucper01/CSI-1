from pathlib import Path
import json,re

p=Path('index.html')
text=p.read_text(encoding='utf-8')
marker='const slides = '
start=text.index(marker)+len(marker)
slides,rel_end=json.JSONDecoder().raw_decode(text[start:])
end=start+rel_end

# Make the updater idempotent if rerun.
base=[s for s in slides if not s.get('divider')]
assert len(base)==44, f'Expected 44 pre-divider slides, got {len(base)}'

def title(s):
    return s.get('title') or s.get('_fr',{}).get('title','')

# Validate the current numbering used in the requested reorganisation.
expected={
  1:'Y a-t-il un espace-temps pour les odeurs ?',
  2:'« No space, no time? » - le paradoxe de l’attention olfactive',
  3:'Deux axes',
  4:'Cinq études structurantes, des extensions clairement conditionnelles',
  5:'Ce qui a été fait cette année',
  22:'Ce que l’année 1 a sécurisé',
  23:'Deux références, trois études prioritaires pour l’année 2',
  30:'TWIXOLF - Méthode',
  31:'Études complémentaires et exploratoires',
  36:'BRAUDOLF',
  37:'Rétroplanning des études',
  38:'Activités doctorales prévues - 2026-2027',
  39:'Publications',
  40:'Points à discuter',
  41:'Bilan',
  42:'Axe 1 - temps et multisensorialité',
  43:'Axe 2 - espace et scènes',
  44:'Merci pour votre attention',
}
for n,t in expected.items():
    assert title(base[n-1])==t, f'Slide {n}: expected {t!r}, got {title(base[n-1])!r}'

# Remove FLUXOLF only from the architecture slide (current slide 4).
arch=base[3]
for holder in [arch,arch.get('_fr',{}),arch.get('_en',{})]:
    c=holder.get('content','')
    # Remove the complete card containing FLUXOLF, without touching later FLUXOLF slides.
    c2,n=re.subn(r'<div class="card"><div class="mono">[^<]*</div><h3>FLUXOLF</h3><p>.*?</p></div>', '', c, count=1, flags=re.S)
    assert n==1, 'FLUXOLF architecture card was not found exactly once'
    # Give the remaining five cards a balanced 3 + 2 layout.
    c2=c2.replace('<div class="grid three">','<div class="grid three architecture-core-grid">',1)
    holder['content']=c2


def divider(num, fr, en, chapter):
    def content(label,title):
        return f'<div class="section-divider-inner"><span class="section-divider-number">{label}</span><h1>{title}</h1><i aria-hidden="true"></i></div>'
    frd={'section':chapter,'kicker':'','title':fr,'lead':'','content':content(f'PARTIE {num}',fr),'notes':''}
    end={'section':chapter,'kicker':'','title':en,'lead':'','content':content(f'PART {num}',en),'notes':''}
    return {
      'chapter':chapter,'study':'','appendix':False,'hero':True,'divider':True,
      '_fr':frd,'_en':end,
      'section':frd['section'],'kicker':'','title':frd['title'],'lead':'','content':frd['content'],'notes':''
    }

# Requested grouping refers to the pre-divider numbering.
intro=base[0:2]
architecture=base[2:4]                 # current 3-4
year1=base[4:22]                       # current 5-22
year2=base[22:30] + base[37:39]        # current 23-30, then current 38-39
extensions=base[30:36]                 # current 31-36
retro=[base[36],base[39],base[40],base[41],base[42]]  # current 37,40,41,42,43
closing=base[43:]                      # current 44

slides=(intro+
  [divider(1,'Architecture de la thèse','Thesis architecture','Architecture')]+architecture+
  [divider(2,'Ce qui a été fait en première année','What was done in year 1','Première année')]+year1+
  [divider(3,'Ce qui sera fait en deuxième année','What will be done in year 2','Deuxième année')]+year2+
  [divider(4,'Ce qu’on envisage pour compléter','What we are considering to complete the programme','Compléments')]+extensions+
  [divider(5,'Rétroplanning global','Global timeline','Rétroplanning global')]+retro+
  closing)

assert len(slides)==49
# Check the important new transitions.
assert slides[2].get('divider') and title(slides[2])=='Architecture de la thèse'
assert title(slides[3])=='Deux axes'
assert title(slides[4])=='Cinq études structurantes, des extensions clairement conditionnelles'
assert slides[5].get('divider') and title(slides[5])=='Ce qui a été fait en première année'
# The second-year block must end with doctoral activities + publications before complements.
pos_twix=next(i for i,s in enumerate(slides) if title(s)=='TWIXOLF - Méthode')
pos_act=next(i for i,s in enumerate(slides) if title(s)=='Activités doctorales prévues - 2026-2027')
pos_pub=next(i for i,s in enumerate(slides) if title(s)=='Publications')
pos_comp=next(i for i,s in enumerate(slides) if title(s)=='Ce qu’on envisage pour compléter')
assert pos_act==pos_twix+1 and pos_pub==pos_act+1 and pos_comp==pos_pub+1
# Retro block order exactly follows the requested current slides.
pos_retro=next(i for i,s in enumerate(slides) if title(s)=='Rétroplanning global')
assert [title(s) for s in slides[pos_retro+1:pos_retro+6]]==[
 'Rétroplanning des études','Points à discuter','Bilan','Axe 1 - temps et multisensorialité','Axe 2 - espace et scènes']
assert 'FLUXOLF' not in base[3]['content']

new_json=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
text=text[:start]+new_json+text[end:]

# Add a dedicated divider class during rendering.
needle="if(s.hero) classes.push('hero-slide');"
if "if(s.divider) classes.push('section-divider-slide');" not in text:
    assert needle in text
    text=text.replace(needle,needle+"\n      if(s.divider) classes.push('section-divider-slide');",1)

css='''
/* CSI major section dividers */
.section-divider-slide{
  background:
    radial-gradient(circle at 78% 18%,rgba(119,184,146,.18),transparent 27%),
    radial-gradient(circle at 12% 84%,rgba(220,238,227,.10),transparent 31%),
    linear-gradient(135deg,#061f17 0%,#0b2f23 58%,#123e2e 100%)!important;
  color:#fff!important;
  align-items:center!important;
  overflow:hidden!important;
}
.section-divider-slide .slide-shell{
  display:grid!important;
  grid-template-columns:1fr!important;
  place-items:center!important;
  width:100%!important;
  max-width:none!important;
  min-height:calc(100vh - 190px)!important;
  margin:0!important;
}
.section-divider-inner{
  width:min(1180px,92vw);
  margin:auto;
  text-align:center;
  display:grid;
  justify-items:center;
  gap:22px;
}
.section-divider-number{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-height:38px;
  padding:8px 17px;
  border:1px solid rgba(255,255,255,.28);
  border-radius:999px;
  color:rgba(255,255,255,.78);
  font-size:.82rem;
  font-weight:950;
  letter-spacing:.13em;
}
.section-divider-inner h1{
  margin:0!important;
  max-width:1180px!important;
  color:#fff!important;
  font-family:Georgia,"Times New Roman",serif;
  font-size:clamp(3.4rem,7vw,7.5rem)!important;
  line-height:.94!important;
  letter-spacing:-.055em!important;
  text-wrap:balance;
}
.section-divider-inner i{
  display:block;
  width:120px;
  height:5px;
  border-radius:999px;
  background:#77b892;
  box-shadow:0 0 28px rgba(119,184,146,.34);
}
.grid.three.architecture-core-grid{grid-template-columns:repeat(6,minmax(0,1fr))!important}
.grid.three.architecture-core-grid>.card{grid-column:span 2}
.grid.three.architecture-core-grid>.card:nth-child(4),
.grid.three.architecture-core-grid>.card:nth-child(5){grid-column:span 3}
@media(max-width:1050px){
  .section-divider-slide .slide-shell{min-height:calc(100vh - 145px)!important}
  .grid.three.architecture-core-grid{grid-template-columns:1fr!important}
  .grid.three.architecture-core-grid>.card{grid-column:auto!important}
}
'''
if '/* CSI major section dividers */' not in text:
    text=text.replace('</style>',css+'\n</style>',1)

p.write_text(text,encoding='utf-8')

# Reparse final file and validate the saved deck.
out=p.read_text(encoding='utf-8')
start2=out.index(marker)+len(marker)
check,_=json.JSONDecoder().raw_decode(out[start2:])
assert len(check)==49
assert sum(bool(s.get('divider')) for s in check)==5
assert [title(s) for s in check if s.get('divider')]==[
 'Architecture de la thèse','Ce qui a été fait en première année','Ce qui sera fait en deuxième année','Ce qu’on envisage pour compléter','Rétroplanning global']
assert 'section-divider-slide' in out
print('OK - 49 slides, 5 major divider slides, requested reordering applied')
