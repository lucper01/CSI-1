from pathlib import Path
import json
import re

INDEX = Path('index.html')
SAVE = Path('index_save.html')

html = INDEX.read_text(encoding='utf-8')

# Save first: index_save.html becomes the exact current state before the new edits.
SAVE.write_text(html, encoding='utf-8')

m = re.search(r'const slides = (\[.*?\]);\s*\n\s*const mainSlides', html, re.S)
if not m:
    raise SystemExit('slides array not found')

slides = json.loads(m.group(1))

new_fr_content = """<div class=\"grid three\"><div class=\"card\"><div class=\"mono\">SOFT</div><h3>Timing perceptif</h3><p><strong>Onset · offset · durées · réponses</strong></p><p>Solution : même logique de tâche, horodatage commun et contrôle des séquences.</p></div><div class=\"card\"><div class=\"mono\">OASIS</div><h3>Synchroniser scène et odeur</h3><p><strong>Image · masque · odeur · respiration</strong></p><p>Solution : séquence verrouillée, repères respiratoires et essais pilotes.</p></div><div class=\"card dark\"><div class=\"mono\">TWIXOLF</div><h3>Ancrage olfactif</h3><p><strong>Inspiration · délai · SOA · simultanéité</strong></p><p>Solution : calibration Sniff-0 / Spir-0 et vérification des décalages.</p></div></div><div class=\"callout\" style=\"margin-top:16px\"><strong>Objectif :</strong> maîtriser le moment où chaque élément commence, sa durée de présentation et la façon dont les systèmes restent synchronisés.</div>"""
new_en_content = """<div class=\"grid three\"><div class=\"card\"><div class=\"mono\">SOFT</div><h3>Perceptual timing</h3><p><strong>Onset · offset · durations · responses</strong></p><p>Solution: shared task logic, common timestamps and sequence control.</p></div><div class=\"card\"><div class=\"mono\">OASIS</div><h3>Synchronizing scene and odor</h3><p><strong>Image · mask · odor · breathing</strong></p><p>Solution: locked sequence, respiratory markers and pilot trials.</p></div><div class=\"card dark\"><div class=\"mono\">TWIXOLF</div><h3>Olfactory anchoring</h3><p><strong>Inhalation · delay · SOA · simultaneity</strong></p><p>Solution: Sniff-0 / Spir-0 calibration and offset checks.</p></div></div><div class=\"callout\" style=\"margin-top:16px\"><strong>Goal:</strong> control when each element starts, how long it is presented and how systems remain synchronized.</div>"""

new_slide = {
    "chapter": "Année 2",
    "study": "",
    "appendix": False,
    "_fr": {
        "section": "Année 2",
        "kicker": "Retour technique",
        "title": "Difficultés techniques - SOFT, OASIS et TWIXOLF",
        "lead": "Les études de l’année 2 reposent sur une contrainte commune : faire tenir ensemble timing perceptif, déclenchement olfactif et synchronisation des éléments.",
        "content": new_fr_content,
        "notes": "Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2."
    },
    "_en": {
        "section": "Year 2",
        "kicker": "Technical feedback",
        "title": "Technical difficulties - SOFT, OASIS and TWIXOLF",
        "lead": "Year-2 studies share a common constraint: combining perceptual timing, olfactory triggering and element synchronization.",
        "content": new_en_content,
        "notes": "Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities."
    },
    "section": "Année 2",
    "kicker": "Retour technique",
    "title": "Difficultés techniques - SOFT, OASIS et TWIXOLF",
    "lead": "Les études de l’année 2 reposent sur une contrainte commune : faire tenir ensemble timing perceptif, déclenchement olfactif et synchronisation des éléments.",
    "content": new_fr_content,
    "notes": "Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2."
}

# Insert between current slide 40 and current slide 41, among non-appendix slides.
main_indices = [i for i, s in enumerate(slides) if not s.get('appendix')]
if len(main_indices) < 41:
    raise SystemExit(f'not enough main slides: {len(main_indices)}')
if not any((s.get('title') == new_slide['title'] or s.get('_fr', {}).get('title') == new_slide['title']) and not s.get('appendix') for s in slides):
    slides.insert(main_indices[40], new_slide)

# Change the extensions overview title and wording.
def repl_text(text, replacements):
    if not isinstance(text, str):
        return text
    for a, b in replacements:
        text = text.replace(a, b)
    return text

fr_ext_replacements = [
    ('Études complémentaires et exploratoires', 'Études complémentaires'),
    ('complémentaire / exploratoire', 'complémentaire'),
    ('Complémentaire / exploratoire', 'Complémentaire'),
    ('Restriction auditive - exploratoire.', 'Restriction auditive - complémentaire.'),
    ('Audition + olfaction - exploratoire.', 'Audition + olfaction - complémentaire.'),
]
en_ext_replacements = [
    ('Complementary and exploratory studies', 'Complementary studies'),
    ('Complementary / exploratory', 'Complementary'),
    ('Auditory restriction - exploratory.', 'Auditory restriction - complementary.'),
    ('Audition + olfaction - exploratory.', 'Audition + olfaction - complementary.'),
]

for s in slides:
    # Overview slide of extensions.
    is_ext_overview = 'v16-extension-map' in str(s.get('content', '')) or 'v16-extension-map' in str(s.get('_fr', {}).get('content', ''))
    if is_ext_overview:
        for key in ['title', 'lead', 'content', 'notes']:
            s[key] = repl_text(s.get(key), fr_ext_replacements)
        if '_fr' in s:
            for key in ['title', 'lead', 'content', 'notes']:
                s['_fr'][key] = repl_text(s['_fr'].get(key), fr_ext_replacements)
        if '_en' in s:
            for key in ['title', 'lead', 'content', 'notes']:
                s['_en'][key] = repl_text(s['_en'].get(key), en_ext_replacements)

    # Dedicated BRAUD and BRAUDOLF slides.
    study = str(s.get('study', '')).upper()
    if study in {'BRAUD', 'BRAUDOLF'}:
        fr_rep = [
            ('exploratoire conditionnel', 'complémentaire'),
            ('Exploratoire conditionnel', 'Complémentaire'),
            ('exploratoire', 'complémentaire'),
            ('Exploratoire', 'Complémentaire'),
        ]
        en_rep = [
            ('conditional exploratory', 'complementary'),
            ('Conditional exploratory', 'Complementary'),
            ('exploratory conditional', 'complementary'),
            ('Exploratory conditional', 'Complementary'),
            ('exploratory', 'complementary'),
            ('Exploratory', 'Complementary'),
        ]
        for key in ['section', 'kicker', 'title', 'lead', 'content', 'notes']:
            s[key] = repl_text(s.get(key), fr_rep)
        if '_fr' in s:
            for key in ['section', 'kicker', 'title', 'lead', 'content', 'notes']:
                s['_fr'][key] = repl_text(s['_fr'].get(key), fr_rep)
        if '_en' in s:
            for key in ['section', 'kicker', 'title', 'lead', 'content', 'notes']:
                s['_en'][key] = repl_text(s['_en'].get(key), en_rep)

array_text = json.dumps(slides, ensure_ascii=False, indent=2)
html = html[:m.start(1)] + array_text + html[m.end(1):]

old_timeline = re.search(
    r"  if\(\(n>=33&&n<=41\)\|\|n===44\)\{.*?  if\(n>=52&&n<=54\)\{\n    return \{steps:E\?\['SUMMARY','DISCUSSION','THANK YOU'\]:\['BILAN','DISCUSSION','MERCI'\],active:n-52\};\n  \}\n",
    html,
    re.S,
)
if old_timeline:
    new_timeline = """  if(n>=33&&n<=43){
    const steps=E
      ? ['PRIORITIES','SOFT','OASIS','TWIXOLF','TECHNICAL FEEDBACK','ACTIVITIES','PUBLICATIONS']
      : ['PRIORITÉS','SOFT','OASIS','TWIXOLF','RETOUR TECHNIQUE','ACTIVITÉS','PUBLICATIONS'];
    let active=0;
    if(n>=35&&n<=36) active=1;
    else if(n>=37&&n<=38) active=2;
    else if(n>=39&&n<=40) active=3;
    else if(n===41) active=4;
    else if(n===42) active=5;
    else if(n===43) active=6;
    return {steps,active};
  }
  if(n===44){
    return {steps:E?['YEAR 3']:['ANNÉE 3'],active:0};
  }
  if(n>=45&&n<=49){
    const steps=E
      ? ['OVERVIEW','SOLAR','BRAUD','BRAUDOLF','ACTIVITIES']
      : ['VUE D\'ENSEMBLE','SOLAR','BRAUD','BRAUDOLF','ACTIVITÉS'];
    let active=0;
    if(n===46) active=1;
    else if(n===47) active=2;
    else if(n===48) active=3;
    else if(n===49) active=4;
    return {steps,active};
  }
  if(n>=51&&n<=52){
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active:n-50};
  }

  if(n>=53&&n<=55){
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active:n-53};
  }
"""
    html = html[:old_timeline.start()] + new_timeline + html[old_timeline.end():]
else:
    print('timeline block not found; slide content updated without timeline patch')

INDEX.write_text(html, encoding='utf-8')

# Lightweight checks.
updated_titles = [s.get('title') for s in slides if not s.get('appendix')]
if updated_titles[40] != new_slide['title']:
    raise SystemExit(f'new slide is not at position 41: {updated_titles[40]!r}')
if not any(s.get('title') == 'Études complémentaires' for s in slides if not s.get('appendix')):
    raise SystemExit('extension title not updated')
if any('exploratoire conditionnel' in str(s).lower() for s in slides if str(s.get('study', '')).upper() in {'BRAUD', 'BRAUDOLF'}):
    raise SystemExit('exploratoire conditionnel still present in BRAUD/BRAUDOLF')
