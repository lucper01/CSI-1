from pathlib import Path
import json
import re

INDEX = Path('index.html')
SAVE = Path('index_save.html')
text = INDEX.read_text(encoding='utf-8')

# 1) Save the exact pre-modification state.
SAVE.write_text(text, encoding='utf-8')

m = re.search(r"const slides = (\[.*?\]);\n\n\s*const mainSlides", text, re.S)
if not m:
    raise SystemExit('Cannot locate slides array')
slides = json.loads(m.group(1))

main_indices = [i for i, s in enumerate(slides) if not s.get('appendix')]
if len(main_indices) < 41:
    raise SystemExit(f'Not enough main slides: {len(main_indices)}')

# Helpers
def as_text(s):
    return (s.get('title') or '') + ' ' + (s.get('kicker') or '') + ' ' + (s.get('section') or '')

def replace_in_obj(obj, replacements):
    if isinstance(obj, dict):
        return {k: replace_in_obj(v, replacements) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_in_obj(v, replacements) for v in obj]
    if isinstance(obj, str):
        out = obj
        for a, b in replacements:
            out = out.replace(a, b)
        return out
    return obj

# 2) Slide 44 current: simplify only the title when the target title exists.
for s in slides:
    if s.get('appendix'):
        continue
    if s.get('title') == 'Études complémentaires et exploratoires':
        s['title'] = 'Études complémentaires'
    if s.get('_fr', {}).get('title') == 'Études complémentaires et exploratoires':
        s['_fr']['title'] = 'Études complémentaires'
    if s.get('_en', {}).get('title') == 'Complementary and exploratory studies':
        s['_en']['title'] = 'Complementary studies'

# 3) Slides dedicated to BRAUD and BRAUDOLF: status wording only, from exploratory to complementary.
status_replacements = [
    ('exploratoire conditionnel', 'complémentaire'),
    ('Exploratoire conditionnel', 'Complémentaire'),
    ('exploratoire', 'complémentaire'),
    ('Exploratoire', 'Complémentaire'),
    ('conditional exploratory', 'complementary'),
    ('Conditional exploratory', 'Complementary'),
    ('exploratory conditional', 'complementary'),
    ('Exploratory conditional', 'Complementary'),
    ('exploratory', 'complementary'),
    ('Exploratory', 'Complementary'),
]
for idx, s in enumerate(slides):
    if s.get('appendix'):
        continue
    study = str(s.get('study') or '').upper()
    title = str(s.get('title') or '').upper()
    if study in {'BRAUD', 'BRAUDOLF'} or title in {'BRAUD', 'BRAUDOLF'}:
        slides[idx] = replace_in_obj(s, status_replacements)

# 4) Insert one technical-difficulties slide between current slides 40 and 41.
tech_title = 'Difficultés techniques - SOFT, OASIS et TWIXOLF'
if not any((s.get('title') == tech_title or s.get('_fr', {}).get('title') == tech_title) and not s.get('appendix') for s in slides):
    insert_at = main_indices[40]  # before current slide 41, therefore after current slide 40
    tech_slide = {
        'chapter': 'Année 2',
        'study': '',
        'appendix': False,
        '_fr': {
            'section': 'Année 2',
            'kicker': 'Retour technique',
            'title': tech_title,
            'lead': 'Les études de l’année 2 reposent sur une contrainte commune : articuler le timing perceptif, le déclenchement olfactif et la synchronisation des éléments.',
            'content': '<div class="grid three"><div class="card"><div class="mono">SOFT</div><h3>Timing perceptif</h3><p><strong>Onset · offset · durées · réponses</strong></p><p>Solution : même logique de tâche, horodatage commun et contrôle strict des séquences.</p></div><div class="card"><div class="mono">OASIS</div><h3>Synchroniser scène et odeur</h3><p><strong>Image · masque · odeur · respiration</strong></p><p>Solution : séquence verrouillée, repères respiratoires et essais pilotes avant collecte.</p></div><div class="card dark"><div class="mono">TWIXOLF</div><h3>Ancrage olfactif</h3><p><strong>Inspiration · délai · SOA · simultanéité</strong></p><p>Solution : calibration Sniff-0 / Spir-0 et vérification systématique des décalages.</p></div></div><div class="callout" style="margin-top:16px"><strong>Objectif :</strong> maîtriser le moment où chaque élément commence, sa durée de présentation et la façon dont les systèmes restent synchronisés.</div>',
            'notes': 'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2.'
        },
        '_en': {
            'section': 'Year 2',
            'kicker': 'Technical feedback',
            'title': 'Technical difficulties - SOFT, OASIS and TWIXOLF',
            'lead': 'Year-2 studies share one constraint: aligning perceptual timing, olfactory triggering and synchronization across elements.',
            'content': '<div class="grid three"><div class="card"><div class="mono">SOFT</div><h3>Perceptual timing</h3><p><strong>Onset · offset · durations · responses</strong></p><p>Solution: shared task logic, common timestamps and strict sequence control.</p></div><div class="card"><div class="mono">OASIS</div><h3>Synchronizing scene and odor</h3><p><strong>Image · mask · odor · breathing</strong></p><p>Solution: locked sequence, respiratory markers and pilot trials before data collection.</p></div><div class="card dark"><div class="mono">TWIXOLF</div><h3>Olfactory anchoring</h3><p><strong>Inhalation · delay · SOA · simultaneity</strong></p><p>Solution: Sniff-0 / Spir-0 calibration and systematic offset checks.</p></div></div><div class="callout" style="margin-top:16px"><strong>Goal:</strong> control when each element starts, how long it is presented and how systems remain synchronized.</div>',
            'notes': 'Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities.'
        },
        'section': 'Année 2',
        'kicker': 'Retour technique',
        'title': tech_title,
        'lead': 'Les études de l’année 2 reposent sur une contrainte commune : articuler le timing perceptif, le déclenchement olfactif et la synchronisation des éléments.',
        'content': '<div class="grid three"><div class="card"><div class="mono">SOFT</div><h3>Timing perceptif</h3><p><strong>Onset · offset · durées · réponses</strong></p><p>Solution : même logique de tâche, horodatage commun et contrôle strict des séquences.</p></div><div class="card"><div class="mono">OASIS</div><h3>Synchroniser scène et odeur</h3><p><strong>Image · masque · odeur · respiration</strong></p><p>Solution : séquence verrouillée, repères respiratoires et essais pilotes avant collecte.</p></div><div class="card dark"><div class="mono">TWIXOLF</div><h3>Ancrage olfactif</h3><p><strong>Inspiration · délai · SOA · simultanéité</strong></p><p>Solution : calibration Sniff-0 / Spir-0 et vérification systématique des décalages.</p></div></div><div class="callout" style="margin-top:16px"><strong>Objectif :</strong> maîtriser le moment où chaque élément commence, sa durée de présentation et la façon dont les systèmes restent synchronisés.</div>',
        'notes': 'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2.'
    }
    slides.insert(insert_at, tech_slide)

# 5) Replace the local timeline logic with a content-aware version to keep the footer aligned after insertion.
new_timeline = r'''function partTimelineFor(index){
  const n=index+1;
  const s=slides[index]||{};
  const E=document.documentElement.lang==='en';
  const txt=(String(s.section||'')+' '+String(s.chapter||'')+' '+String(s.kicker||'')+' '+String(s.title||'')+' '+String(s.study||'')).toUpperCase();
  const study=String(s.study||'').toUpperCase();
  if(n>=4&&n<=12){
    const steps=E
      ? ['VISION + AUDITION','TIME','SPACE','INTEGRATION','SYNTHESIS','OLFACTION','AXES','INFLUENCE']
      : ['VISION + AUDITION','TEMPS','ESPACE','INTÉGRATION','SYNTHÈSE','OLFACTION','AXES','INFLUENCE'];
    const active={4:0,5:1,6:2,7:3,8:4,9:5,10:5,11:6,12:7}[n];
    return {steps,active};
  }
  if(n>=14&&n<=15){
    return {steps:E?['AXES','STUDY PROGRAM']:['AXES','PROGRAMME D\'ÉTUDES'],active:n===14?0:1};
  }
  if(txt.includes('ANNÉE 1') || txt.includes('YEAR 1')){
    const steps=E
      ? ['REVIEW','TWIXAV','VIBEX','FLUXOLF','ACTIVITIES','TRANSITION']
      : ['BILAN','TWIXAV','VIBEX','FLUXOLF','ACTIVITÉS','TRANSITION'];
    let active=0;
    if(study==='TWIXAV' || txt.includes('TWIXAV')) active=1;
    else if(study==='VIBEX' || txt.includes('VIBEX')) active=2;
    else if(study==='FLUXOLF' || txt.includes('FLUXOLF')) active=3;
    else if(txt.includes('ACTIVITÉS') || txt.includes('ACTIVITIES') || txt.includes('ENSEIGNEMENT')) active=4;
    else if(txt.includes('TRANSITION') || txt.includes('DEUXIÈME ANNÉE') || txt.includes('YEAR 2')) active=5;
    return {steps,active};
  }
  if(txt.includes('ANNÉE 2') || txt.includes('YEAR 2') || study==='SOFT' || study==='OASIS' || study==='TWIXOLF' || txt.includes('2026-2027')){
    const steps=E
      ? ['PRIORITIES','SOFT','OASIS','TWIXOLF','TECHNICAL','ACTIVITIES','PUBLICATIONS']
      : ['PRIORITÉS','SOFT','OASIS','TWIXOLF','TECHNIQUE','ACTIVITÉS','PUBLICATIONS'];
    let active=0;
    if(study==='SOFT' || txt.includes('SOFT')) active=1;
    if(study==='OASIS' || txt.includes('OASIS')) active=2;
    if(study==='TWIXOLF' || txt.includes('TWIXOLF')) active=3;
    if(txt.includes('DIFFICULTÉS TECHNIQUES') || txt.includes('TECHNICAL DIFFICULTIES')) active=4;
    if(txt.includes('ACTIVITÉS') || txt.includes('ACTIVITIES')) active=5;
    if(txt.includes('PUBLICATIONS')) active=6;
    return {steps,active};
  }
  if(study==='SOLAR' || study==='BRAUD' || study==='BRAUDOLF' || txt.includes('COMPLÉMENT') || txt.includes('COMPLEMENT')){
    const steps=E
      ? ['OVERVIEW','SOLAR','BRAUD','BRAUDOLF']
      : ['VUE D\'ENSEMBLE','SOLAR','BRAUD','BRAUDOLF'];
    let active=0;
    if(study==='SOLAR' || txt.includes('SOLAR')) active=1;
    else if(study==='BRAUDOLF' || txt.includes('BRAUDOLF')) active=3;
    else if(study==='BRAUD' || txt.includes('BRAUD')) active=2;
    return {steps,active};
  }
  if(txt.includes('RÉTROPLANNING') || txt.includes('RETROPLANNING') || txt.includes('TIMELINE') || txt.includes('SOUTENANCE') || txt.includes('DEFENSE')){
    const steps=E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'];
    let active=0;
    if(txt.includes('ÉTUDES') || txt.includes('STUDY')) active=1;
    if(txt.includes('SOUTENANCE') || txt.includes('DEFENSE') || txt.includes('JUSQU')) active=2;
    return {steps,active};
  }
  if(txt.includes('DISCUSSION') || txt.includes('BILAN') || txt.includes('MERCI') || txt.includes('THANK')){
    const steps=E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'];
    let active=0;
    if(txt.includes('DISCUSSION') || txt.includes('POINTS')) active=1;
    if(txt.includes('MERCI') || txt.includes('THANK')) active=2;
    return {steps,active};
  }
  return null;
}
'''
text_after = re.sub(r"function partTimelineFor\(index\)\{.*?\n\}\nfunction renderPartTimeline\(index\)", new_timeline + "function renderPartTimeline(index)", text, flags=re.S, count=1)
if text_after == text:
    raise SystemExit('Timeline function replacement failed')

slides_json = json.dumps(slides, ensure_ascii=False, indent=2)
text_after = text_after[:m.start(1)] + slides_json + text_after[m.end(1):]

# Sanity checks
if tech_title not in text_after:
    raise SystemExit('Technical slide was not inserted')
if 'Études complémentaires et exploratoires' in text_after:
    raise SystemExit('Old complementary/exploratory title still present')

INDEX.write_text(text_after, encoding='utf-8')
print('Saved pre-modification state to index_save.html')
print('Inserted year-2 technical slide between current slides 40 and 41')
print('Simplified complementary studies title and BRAUD/BRAUDOLF statuses')
