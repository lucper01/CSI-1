from pathlib import Path
import json

p=Path('index.html')
text=p.read_text(encoding='utf-8')
marker='const slides = '
start=text.index(marker)+len(marker)
slides,rel_end=json.JSONDecoder().raw_decode(text[start:])
end=start+rel_end
assert len(slides)==49, f'Expected 49 slides, got {len(slides)}'

def title(s):
    return s.get('title') or s.get('_fr',{}).get('title','')

idx=next(i for i,s in enumerate(slides) if title(s)=='« No space, no time? » - le paradoxe de l’attention olfactive')
assert idx==1, f'Sela & Sobel slide should be slide 2, got {idx+1}'
s=slides[idx]

fr_inner='''<div class="grid three"><div class="card"><div class="mono">Espace</div><h3>Une spatialisation limitée</h3><p>Les capacités humaines de localisation olfactive sont réduites relativement à la vision et à l’audition, ce qui contraint la sélection spatiale et la capture attentionnelle.</p></div><div class="card"><div class="mono">Temps</div><h3>Un échantillonnage par le sniff</h3><p>L’information olfactive est échantillonnée de façon discontinue au rythme des inspirations, avec une temporalité propre à la délivrance et à la respiration.</p></div><div class="card dark"><div class="mono">STOLF</div><h3>Le verrou à tester</h3><p>Ces contraintes abolissent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?</p></div></div><div class="callout" style="margin-top:16px"><strong>Point de départ :</strong> « No space, no time? » est une question de travail, pas l’affirmation que l’olfaction serait dépourvue de représentations spatiales ou temporelles.</div><div class="csi-cite">Sela, L. & Sobel, N. (2010). Human olfaction: a constant state of change-blindness. Experimental Brain Research, 205, 13-29.</div>'''

en_inner='''<div class="grid three"><div class="card"><div class="mono">Space</div><h3>Limited spatialization</h3><p>Human olfactory localization is limited relative to vision and audition, constraining spatial selection and attentional capture.</p></div><div class="card"><div class="mono">Time</div><h3>Sampling through sniffing</h3><p>Olfactory information is sampled discontinuously with inhalations, giving odor delivery and respiration their own temporal structure.</p></div><div class="card dark"><div class="mono">STOLF</div><h3>The question to test</h3><p>Do these constraints abolish spatio-temporal organization, or do they mainly change how such organization becomes available to perception and attention?</p></div></div><div class="callout" style="margin-top:16px"><strong>Starting point:</strong> “No space, no time?” is a working question, not a claim that olfaction lacks spatial or temporal representations.</div><div class="csi-cite">Sela, L. & Sobel, N. (2010). Human olfaction: a constant state of change-blindness. Experimental Brain Research, 205, 13-29.</div>'''

visual='''<aside class="sela-visual-stack" aria-label="Sela and Sobel review and Albert Einstein"><div class="sela-review-card"><div class="sela-review-tag">REVIEW</div><div class="sela-review-body"><h3>Human olfaction: a constant state of change-blindness</h3><p class="sela-review-authors">Lee Sela · Noam Sobel</p><p class="sela-review-heading">No space for human olfactory attention</p><p class="sela-review-heading">No time for human olfactory attention</p></div></div><figure class="einstein-card"><div class="einstein-question q1">?</div><div class="einstein-question q2">?</div><img src="https://commons.wikimedia.org/wiki/Special:Redirect/file/Albert%20Einstein%20Head.jpg?width=600" alt="Portrait d’Albert Einstein"><figcaption>Une question volontairement provocatrice : « No space, no time? »</figcaption></figure></aside>'''

for holder,inner in [(s,fr_inner),(s.get('_fr',{}),fr_inner),(s.get('_en',{}),en_inner)]:
    if not holder:
        continue
    holder['content']=f'<div class="sela-slide-layout"><div class="sela-theory-copy">{inner}</div>{visual}</div>'

# Keep displayed FR content synchronized with _fr.
s['content']=s['_fr']['content']

new_json=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
text=text[:start]+new_json+text[end:]

css='''
/* Sela & Sobel slide 2 - theory + visual anchor */
.sela-slide-layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,.62fr);gap:24px;align-items:start}
.sela-theory-copy{min-width:0}
.sela-theory-copy .grid.three{grid-template-columns:repeat(3,minmax(0,1fr))!important}
.sela-visual-stack{display:grid;gap:14px;align-content:start}
.sela-review-card{overflow:hidden;border:1px solid var(--line);border-radius:22px;background:#fff;color:#171717;box-shadow:0 12px 30px rgba(11,47,35,.12)}
.sela-review-tag{padding:6px 12px;background:#b9b9b9;border-bottom:1px solid #9a9a9a;font-family:Georgia,"Times New Roman",serif;font-size:.72rem;font-weight:800;letter-spacing:.12em;color:#222}
.sela-review-body{padding:15px 16px 14px}
.sela-review-body h3{margin:0 0 7px!important;font-family:Georgia,"Times New Roman",serif;font-size:1.05rem!important;line-height:1.15!important;letter-spacing:-.015em!important;color:#111!important}
.sela-review-authors{margin:0 0 14px;font-family:Georgia,"Times New Roman",serif;font-size:.78rem;color:#222}
.sela-review-heading{margin:12px 0 0;font-family:Georgia,"Times New Roman",serif;font-weight:800;font-size:.95rem;line-height:1.2;color:#111}
.einstein-card{position:relative;margin:0;min-height:330px;overflow:hidden;border-radius:24px;border:1px solid var(--line);background:linear-gradient(160deg,#061f17,#0b2f23);box-shadow:0 14px 34px rgba(11,47,35,.16);display:grid;place-items:end center}
.einstein-card img{display:block;width:100%;height:330px;object-fit:cover;object-position:center 24%;filter:grayscale(1) contrast(1.03)}
.einstein-card::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 56%,rgba(6,31,23,.84));pointer-events:none}
.einstein-card figcaption{position:absolute;z-index:2;left:16px;right:16px;bottom:13px;margin:0;color:#fff;font-size:.78rem;font-weight:800;line-height:1.25}
.einstein-question{position:absolute;z-index:3;font-family:Georgia,"Times New Roman",serif;font-weight:900;color:#fff;text-shadow:0 3px 18px rgba(0,0,0,.35);line-height:1}
.einstein-question.q1{right:18px;top:12px;font-size:4.8rem;transform:rotate(8deg)}
.einstein-question.q2{right:78px;top:72px;font-size:2.5rem;opacity:.82;transform:rotate(-8deg)}
@media(max-width:1180px){.sela-slide-layout{grid-template-columns:1fr}.sela-visual-stack{grid-template-columns:1fr 1fr}.einstein-card,.einstein-card img{min-height:250px;height:250px}}
@media(max-width:760px){.sela-theory-copy .grid.three,.sela-visual-stack{grid-template-columns:1fr!important}.einstein-card,.einstein-card img{min-height:300px;height:300px}}
'''
if '/* Sela & Sobel slide 2 - theory + visual anchor */' not in text:
    text=text.replace('</style>',css+'\n</style>',1)

p.write_text(text,encoding='utf-8')

# Validate exactly slide 2 changed structurally.
out=p.read_text(encoding='utf-8')
st2=out.index(marker)+len(marker)
chk,_=json.JSONDecoder().raw_decode(out[st2:])
assert len(chk)==49
assert title(chk[1])=='« No space, no time? » - le paradoxe de l’attention olfactive'
assert 'sela-review-card' in chk[1]['content']
assert 'Albert%20Einstein%20Head.jpg' in chk[1]['content']
assert title(chk[2])=='Architecture de la thèse'
print('OK - slide 2 visual layout updated only; deck remains 49 slides')
