from pathlib import Path
import json
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
start_marker = '  const slides = '
end_marker = ';\n\n  const mainSlides'
start = text.index(start_marker) + len(start_marker)
end = text.index(end_marker, start)
slides = json.loads(text[start:end])

main_indices = [i for i, s in enumerate(slides) if not s.get('appendix')]
if len(main_indices) < 29:
    raise SystemExit('Deck has fewer than 29 main slides')
idx = main_indices[28]
slide = slides[idx]

if 'TWIXOLF' not in json.dumps(slide, ensure_ascii=False) and 'Difficultés techniques' not in json.dumps(slide, ensure_ascii=False):
    raise SystemExit('Slide 29 does not match expected technical slide')

fr = {
    'section': 'Année 1',
    'kicker': 'Retour technique',
    'title': 'Difficultés techniques - TWIXAV et VIBEX',
    'lead': 'La difficulté centrale est de rendre comparables des paradigmes audiovisuels et visuels en maîtrisant le timing et la synchronisation des éléments.',
    'content': '<div class="grid three"><div class="card"><div class="mono">TWIXAV</div><h3>Timing audiovisuel</h3><p><strong>SOA · durées · onsets / offsets</strong></p><p>Solution : contrôle temporel fin, logs d’événements et vérification des décalages.</p></div><div class="card"><div class="mono">VIBEX</div><h3>Timing visuel</h3><p><strong>Refresh · frames · masque · durée d’affichage</strong></p><p>Solution : contrôle frame-by-frame, durées verrouillées et stimuli standardisés.</p></div><div class="card dark"><div class="mono">SYNCHRO</div><h3>Faire coexister les systèmes</h3><p><strong>PsychoPy · affichage · réponses · triggers</strong></p><p>Solution : horodatage commun, vérifications de latence et procédures de contrôle avant passation.</p></div></div><div class="callout" style="margin-top:16px"><strong>Objectif :</strong> maîtriser quand le stimulus commence, combien de temps il est présenté et comment les systèmes restent synchronisés.</div>',
    'notes': 'Mettre l’accent sur le timing audiovisuel de TWIXAV, le timing visuel de VIBEX et la synchronisation entre systèmes.'
}
en = {
    'section': 'Year 1',
    'kicker': 'Technical feedback',
    'title': 'Technical difficulties - TWIXAV and VIBEX',
    'lead': 'The central difficulty is making audiovisual and visual paradigms comparable by controlling timing and synchronization across elements.',
    'content': '<div class="grid three"><div class="card"><div class="mono">TWIXAV</div><h3>Audiovisual timing</h3><p><strong>SOA · durations · onsets / offsets</strong></p><p>Solution: fine temporal control, event logs and offset checks.</p></div><div class="card"><div class="mono">VIBEX</div><h3>Visual timing</h3><p><strong>Refresh rate · frames · mask · display duration</strong></p><p>Solution: frame-by-frame control, locked durations and standardized stimuli.</p></div><div class="card dark"><div class="mono">SYNC</div><h3>Making systems coexist</h3><p><strong>PsychoPy · display · responses · triggers</strong></p><p>Solution: shared timestamps, latency checks and control procedures before testing.</p></div></div><div class="callout" style="margin-top:16px"><strong>Goal:</strong> control when the stimulus starts, how long it is presented and how the systems remain synchronized.</div>',
    'notes': 'Emphasize TWIXAV audiovisual timing, VIBEX visual timing and synchronization across systems.'
}

slide['chapter'] = 'Année 1'
slide['study'] = ''
slide['section'] = fr['section']
slide['kicker'] = fr['kicker']
slide['title'] = fr['title']
slide['lead'] = fr['lead']
slide['content'] = fr['content']
slide['notes'] = fr['notes']
slide['_fr'] = fr
slide['_en'] = en
slides[idx] = slide

# Verification
payload = json.dumps(slide, ensure_ascii=False)
if 'TWIXOLF' in payload or 'olfactif' in payload.lower() or 'olfactory' in payload.lower():
    raise SystemExit('Unexpected TWIXOLF/olfactory wording remains in slide 29')
if 'TWIXAV' not in payload or 'VIBEX' not in payload:
    raise SystemExit('TWIXAV/VIBEX wording missing after patch')

new_array = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
new_text = text[:start] + new_array + text[end:]
path.write_text(new_text, encoding='utf-8')
print('Updated slide 29 to TWIXAV + VIBEX technical feedback')
