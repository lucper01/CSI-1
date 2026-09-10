from pathlib import Path
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')

marker = 'Difficultés techniques - SOFT, OASIS et TWIXOLF'
start = text.find(marker)
if start < 0:
    raise SystemExit('Slide marker not found')

# Limit the edit to the local technical-difficulties slide area.
end_candidates = [
    text.find('Activités doctorales prévues - 2027-2028', start),
    text.find('Publications', start),
]
end_candidates = [x for x in end_candidates if x > start]
end = min(end_candidates) if end_candidates else start + 30000
segment = text[start:end]

pattern = re.compile(
    r'(<div class=\\\\?"mono\\\\?">SOFT</div><h3>)(.*?)(</h3><p><strong>)(.*?)(</strong></p><p>)(.*?)(</p>)'
)

changes = 0

def repl(m):
    global changes
    changes += 1
    old_title = m.group(2)
    is_en = 'Perceptual' in old_title or 'Timing and' in old_title
    if is_en:
        title = 'Timing and synchronization'
        strong = 'Onset · offset · durations · Sniff-0 / Spir-0 · EEG / BIOPAC'
        solution = 'Solution: common timestamps, shared triggers and Sniff-0 / Spir-0 / EEG / BIOPAC synchronization before testing.'
    else:
        title = 'Timing et synchronisation'
        strong = 'Onset · offset · durées · Sniff-0 / Spir-0 · EEG / BIOPAC'
        solution = 'Solution : horodatage commun, triggers partagés et synchronisation Sniff-0 / Spir-0 / EEG / BIOPAC avant passation.'
    return m.group(1) + title + m.group(3) + strong + m.group(5) + solution + m.group(7)

segment2 = pattern.sub(repl, segment)
if changes == 0:
    raise SystemExit('SOFT card not found in target slide segment')

segment2 = segment2.replace(
    'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2.',
    'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2, en insistant pour SOFT sur la synchronisation Sniff-0 / Spir-0 / EEG / BIOPAC.'
).replace(
    'Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities.',
    'Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities, emphasizing Sniff-0 / Spir-0 / EEG / BIOPAC synchronization for SOFT.'
)

text = text[:start] + segment2 + text[end:]

if 'Sniff-0 / Spir-0 · EEG / BIOPAC' not in text:
    raise SystemExit('SOFT synchronization wording not inserted')

p.write_text(text, encoding='utf-8')
print(f'Updated SOFT synchronization wording: {changes} SOFT card occurrence(s)')
