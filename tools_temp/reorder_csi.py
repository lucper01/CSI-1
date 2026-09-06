from pathlib import Path
import json

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
pos = text.index(marker) + len(marker)
slides, used = json.JSONDecoder().raw_decode(text[pos:])
array_end = pos + used

def title(s):
    return s.get('title') or s.get('_fr', {}).get('title') or ''

before = [title(s) for s in slides]
print('SLIDE COUNT BEFORE:', len(slides))
for i, t in enumerate(before, 1):
    print(f'{i:02d}: {t}')

assert len(slides) == 41, len(slides)
assert before[0] == 'Y a-t-il un espace-temps pour les odeurs ?'
assert before[1] == 'Encadrement et CSI'
assert before[2] == 'Deux axes'
assert before[3] == '« No space, no time? » - le paradoxe de l’attention olfactive'
assert before[5] == 'Ce qui a été fait cette année'
assert before[15] == 'Enseignement, formation et encadrement'

old39 = slides[38]
old39_title = title(old39)
print('CURRENT SLIDE 39 TO MOVE LAST:', old39_title)

fr6 = '''<div class="v16-year-grid study-year-grid"><article class="study-year-card multi"><span>Études</span><h3 class="study-year-names"><span class="study-year-name" data-study="TWIXAV" style="--study-color:#2f6f9f;--study:#2f6f9f">TWIXAV</span><span class="study-year-sep">+</span><span class="study-year-name" data-study="VIBEX" style="--study-color:#2f7d5a;--study:#2f7d5a">VIBEX</span></h3><p>Prétests, passations pilotes, premières analyses et consolidation des paradigmes de référence.</p></article><article class="study-year-card" data-study="FLUXOLF" style="--study-color:#a34d5d;--study:#a34d5d"><span>Projet annexe</span><h3>FLUXOLF</h3><p>Analyses EDA, HR, HRV et EEG, avec standardisation progressive des sorties statistiques.</p></article><article class="study-year-card multi"><span>Développement</span><h3 class="study-year-names"><span class="study-year-name" data-study="SOFT" style="--study-color:#7652a8;--study:#7652a8">SOFT</span><span class="study-year-name" data-study="OASIS" style="--study-color:#b44e6c;--study:#b44e6c">OASIS</span><span class="study-year-name" data-study="TWIXOLF" style="--study-color:#c36c32;--study:#c36c32">TWIXOLF</span></h3><p>Programmation, intégration olfactométrique, respiration, triggers et préparation des collectes.</p></article><article class="study-year-card neutral"><span>Doctorat</span><h3>Enseignement, formation, encadrement</h3><p>54 h eq. TD valorisées, formations doctorales et encadrement de mémoires de Master 1.</p></article></div>'''
en6 = '''<div class="v16-year-grid study-year-grid"><article class="study-year-card multi"><span>Studies</span><h3 class="study-year-names"><span class="study-year-name" data-study="TWIXAV" style="--study-color:#2f6f9f;--study:#2f6f9f">TWIXAV</span><span class="study-year-sep">+</span><span class="study-year-name" data-study="VIBEX" style="--study-color:#2f7d5a;--study:#2f7d5a">VIBEX</span></h3><p>Pre-tests, pilot sessions, initial analyses and consolidation of reference paradigms.</p></article><article class="study-year-card" data-study="FLUXOLF" style="--study-color:#a34d5d;--study:#a34d5d"><span>Side project</span><h3>FLUXOLF</h3><p>EDA, HR, HRV and EEG analyses, with progressive standardization of statistical outputs.</p></article><article class="study-year-card multi"><span>Development</span><h3 class="study-year-names"><span class="study-year-name" data-study="SOFT" style="--study-color:#7652a8;--study:#7652a8">SOFT</span><span class="study-year-name" data-study="OASIS" style="--study-color:#b44e6c;--study:#b44e6c">OASIS</span><span class="study-year-name" data-study="TWIXOLF" style="--study-color:#c36c32;--study:#c36c32">TWIXOLF</span></h3><p>Programming, olfactometer integration, respiration, triggers and preparation for data collection.</p></article><article class="study-year-card neutral"><span>PhD activities</span><h3>Teaching, training, supervision</h3><p>54 tutorial-equivalent hours, doctoral training and supervision of Master's research projects.</p></article></div>'''

s6 = slides[5]
s6['content'] = fr6
if '_fr' in s6:
    s6['_fr']['content'] = fr6
if '_en' in s6:
    s6['_en']['content'] = en6

fr_sentence = ' Un nouveau mémoire M1 est également proposé sur l’influence de l’olfaction sur la mémoire de scènes visuelles.'
en_sentence = ' A new Master 1 project is also proposed on the influence of olfaction on memory for visual scenes.'
s16 = slides[15]
if 'content' in s16:
    s16['content'] = s16['content'].replace(fr_sentence, '')
if '_fr' in s16:
    s16['_fr']['content'] = s16['_fr']['content'].replace(fr_sentence, '')
if '_en' in s16:
    s16['_en']['content'] = s16['_en']['content'].replace(en_sentence, '')

moved = slides.pop(38)
assert moved is old39
slides[2], slides[3] = slides[3], slides[2]
removed = slides.pop(1)
assert title(removed) == 'Encadrement et CSI'
slides.append(moved)

after = [title(s) for s in slides]
print('SLIDE COUNT AFTER:', len(slides))
for i, t in enumerate(after, 1):
    print(f'{i:02d}: {t}')

assert len(slides) == 40
assert after[0] == 'Y a-t-il un espace-temps pour les odeurs ?'
assert after[1] == '« No space, no time? » - le paradoxe de l’attention olfactive'
assert after[2] == 'Deux axes'
assert 'Encadrement et CSI' not in after
assert after[-1] == old39_title

year = next(s for s in slides if title(s) == 'Ce qui a été fait cette année')
ytxt = json.dumps(year, ensure_ascii=False)
for k, c in [('TWIXAV','#2f6f9f'),('VIBEX','#2f7d5a'),('FLUXOLF','#a34d5d'),('SOFT','#7652a8'),('OASIS','#b44e6c'),('TWIXOLF','#c36c32')]:
    assert k in ytxt and c in ytxt

supervision = next(s for s in slides if title(s) == 'Enseignement, formation et encadrement')
stxt = json.dumps(supervision, ensure_ascii=False)
assert 'Alicia Emorine' in stxt and 'Olivia Hiridjee' in stxt and 'Morgane Barret' in stxt
assert 'Un nouveau mémoire M1 est également proposé' not in stxt
assert 'A new Master 1 project is also proposed' not in stxt

new_array = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:pos] + new_array + text[array_end:]

css = '''
    /* study-year-grid - exact study identity colors */
    .study-year-grid .study-year-card{position:relative;overflow:hidden}
    .study-year-grid .study-year-card[data-study]{--study:var(--study-color,var(--accent));border-color:color-mix(in srgb,var(--study) 34%,var(--line));background:linear-gradient(145deg,color-mix(in srgb,var(--study) 8%,var(--white)),var(--white));box-shadow:0 10px 26px color-mix(in srgb,var(--study) 10%,transparent)}
    .study-year-grid .study-year-card[data-study]>span,.study-year-grid .study-year-card[data-study]>h3{color:var(--study)}
    .study-year-names{display:flex!important;align-items:center;gap:7px;flex-wrap:wrap;font-family:inherit!important}
    .study-year-name{display:inline-flex!important;align-items:center;padding:5px 9px!important;border-radius:999px;background:color-mix(in srgb,var(--study) 13%,var(--white))!important;border:1px solid color-mix(in srgb,var(--study) 30%,transparent)!important;color:var(--study)!important;font:900 .92rem system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;letter-spacing:0!important;text-transform:none!important}
    .study-year-sep{color:var(--muted)!important;font-weight:900!important}
    .study-year-grid .neutral{background:var(--white)}
    @media(max-width:850px){.study-year-names{gap:5px}.study-year-name{font-size:.82rem!important}}
'''
if 'study-year-grid - exact study identity colors' not in text:
    text = text.replace('</style>', css + '\n  </style>', 1)

p.write_text(text, encoding='utf-8')
Path('/tmp/old39_title.txt').write_text(old39_title, encoding='utf-8')
