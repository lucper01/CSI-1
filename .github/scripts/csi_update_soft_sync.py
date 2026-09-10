from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')

replacements = {
    '<div class=\\"mono\\">SOFT</div><h3>Timing perceptif</h3><p><strong>Onset · offset · durées · réponses</strong></p><p>Solution : même logique de tâche, horodatage commun et contrôle des séquences.</p>':
    '<div class=\\"mono\\">SOFT</div><h3>Timing et synchronisation</h3><p><strong>Onset · offset · durées · Sniff-0 / Spir-0 · EEG / BIOPAC</strong></p><p>Solution : horodatage commun, triggers partagés et synchronisation Sniff-0 / Spir-0 / EEG / BIOPAC avant passation.</p>',

    '<div class=\\"mono\\">SOFT</div><h3>Perceptual timing</h3><p><strong>Onset · offset · durations · responses</strong></p><p>Solution: shared task logic, common timestamps and sequence control.</p>':
    '<div class=\\"mono\\">SOFT</div><h3>Timing and synchronization</h3><p><strong>Onset · offset · durations · Sniff-0 / Spir-0 · EEG / BIOPAC</strong></p><p>Solution: common timestamps, shared triggers and Sniff-0 / Spir-0 / EEG / BIOPAC synchronization before testing.</p>',

    'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2.':
    'Présenter cette diapositive comme un retour technique synthétique avant les activités doctorales de l’année 2, en insistant pour SOFT sur la synchronisation Sniff-0 / Spir-0 / EEG / BIOPAC.',

    'Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities.':
    'Present this slide as a synthetic technical feedback slide before Year-2 doctoral activities, emphasizing Sniff-0 / Spir-0 / EEG / BIOPAC synchronization for SOFT.'
}

count = 0
for old, new in replacements.items():
    n = text.count(old)
    if n == 0:
        raise SystemExit(f'Missing expected text: {old[:90]}')
    text = text.replace(old, new)
    count += n

if 'Sniff-0 / Spir-0 · EEG / BIOPAC' not in text:
    raise SystemExit('SOFT synchronization wording not inserted')

p.write_text(text, encoding='utf-8')
print(f'Updated SOFT synchronization wording: {count} replacements')
