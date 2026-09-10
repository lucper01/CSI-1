from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = [
    ('Compléments</h3>', 'Troisième année</h3>', 2),
    ('Extensions envisagées selon résultats et faisabilité.', 'Études complémentaires envisagées et activités doctorales prévisionnelles.', 2),
    ('"chapter": "Rétroplanning global",\n    "study": "",\n    "appendix": false,\n    "hero": true,\n    "divider": true,', '"chapter": "Planification",\n    "study": "",\n    "appendix": false,\n    "hero": true,\n    "divider": true,', 1),
    ('"section": "Rétroplanning global",\n      "kicker": "",\n      "title": "Rétroplanning"', '"section": "Planification",\n      "kicker": "",\n      "title": "Planification"', 1),
    ('"section": "Rétroplanning global",\n    "kicker": "",\n    "title": "Rétroplanning"', '"section": "Planification",\n    "kicker": "",\n    "title": "Planification"', 1),
    ('<h1>Rétroplanning</h1>', '<h1>Planification</h1>', 2),
    ('"title": "Rétroplanning - jusqu’à la soutenance"', '"title": "Planification - jusqu’à la soutenance"', 2),
]

for old, new, expected in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'Unexpected count {count} (expected {expected}) for target: {old}')
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')
