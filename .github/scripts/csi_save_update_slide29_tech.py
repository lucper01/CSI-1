from pathlib import Path
import json
import re
import hashlib

path = Path('index.html')
save = Path('index_save.html')
text = path.read_text(encoding='utf-8')

# 1) Save current active deck before modifying slide 29.
save.write_text(text, encoding='utf-8')
save_hash_after_copy = hashlib.sha256(save.read_bytes()).hexdigest()

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end
assert len(slides) >= 29, len(slides)

slide = slides[28]  # current slide 29, 1-based numbering

fr_content = '''<div class="grid three"><div class="card"><div class="mono">VIBEX</div><h3>Timing visuel</h3><p><strong>Refresh · frames · masque · onsets / offsets</strong></p><p>Solution : contrôle frame-by-frame, durées verrouillées et logs d'affichage.</p></div><div class="card"><div class="mono">TWIXOLF</div><h3>Timing olfactif</h3><p><strong>Respiration · délai olfactomètre · onset perçu</strong></p><p>Solution : déclenchement sur inspiration, calibration Sniff-0 / Spir-0 et tests pilotes.</p></div><div class="card dark"><div class="mono">SYNCHRO</div><h3>Faire coexister les systèmes</h3><p><strong>PsychoPy · Sniff-0 · Spir-0 · réponses · triggers</strong></p><p>Solution : horodatage commun, vérifications TTL et procédures de contrôle avant passation.</p></div></div><div class="callout" style="margin-top:16px"><strong>Objectif :</strong> maîtriser quand le stimulus commence, combien de temps il est présenté et comment les systèmes restent synchronisés.</div>'''

en_content = '''<div class="grid three"><div class="card"><div class="mono">VIBEX</div><h3>Visual timing</h3><p><strong>Refresh rate · frames · mask · onsets / offsets</strong></p><p>Solution: frame-by-frame control, locked durations and display logs.</p></div><div class="card"><div class="mono">TWIXOLF</div><h3>Olfactory timing</h3><p><strong>Breathing · olfactometer delay · perceived onset</strong></p><p>Solution: inhalation-triggered delivery, Sniff-0 / Spir-0 calibration and pilot tests.</p></div><div class="card dark"><div class="mono">SYNC</div><h3>Making systems coexist</h3><p><strong>PsychoPy · Sniff-0 · Spir-0 · responses · triggers</strong></p><p>Solution: shared timestamps, TTL checks and control procedures before testing.</p></div></div><div class="callout" style="margin-top:16px"><strong>Goal:</strong> control when the stimulus starts, how long it is presented and how the systems remain synchronized.</div>'''

updates = {
    'section': 'Année 1',
    'kicker': 'Retour technique',
    'title': 'Difficultés techniques - VIBEX et TWIXOLF',
    'lead': 'La difficulté centrale est de rendre comparables des paradigmes très différents en maîtrisant le timing et la synchronisation des éléments.',
    'content': fr_content,
    'notes': 'Mettre l’accent sur le timing, la synchronisation entre systèmes et les solutions de contrôle technique.'
}
slide.update(updates)
slide['study'] = ''
slide['chapter'] = 'Année 1'

slide['_fr'] = dict(slide.get('_fr') or {})
slide['_fr'].update(updates)
slide['_en'] = dict(slide.get('_en') or {})
slide['_en'].update({
    'section': 'Year 1',
    'kicker': 'Technical feedback',
    'title': 'Technical difficulties - VIBEX and TWIXOLF',
    'lead': 'The central difficulty is making very different paradigms comparable by controlling timing and synchronization across elements.',
    'content': en_content,
    'notes': 'Emphasize timing, synchronization across systems and technical control solutions.'
})

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
new_text = text[:start] + new_json + text[end:]

# Keep current DA and structure: no extra style blocks, no slide deletion.
assert len(slides) >= 29
assert 'Difficultés techniques - VIBEX et TWIXOLF' in new_text
assert 'Refresh · frames · masque · onsets / offsets' in new_text
assert 'Respiration · délai olfactomètre · onset perçu' in new_text
assert 'PsychoPy · Sniff-0 · Spir-0 · réponses · triggers' in new_text
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_hash_after_copy

path.write_text(new_text, encoding='utf-8')
