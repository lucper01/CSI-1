from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = [
    (
        '<strong style="font-size:2.2rem;color:var(--accent);line-height:1">05</strong><h3 style="margin:0">Compléments</h3></div><p style="margin:8px 0 0;color:var(--muted)">Extensions envisagées selon résultats et faisabilité.</p>',
        '<strong style="font-size:2.2rem;color:var(--accent);line-height:1">05</strong><h3 style="margin:0">Troisième année</h3></div><p style="margin:8px 0 0;color:var(--muted)">Études complémentaires envisagées et activités doctorales prévisionnelles.</p>'
    ),
    (
        '<strong style="font-size:2.2rem;color:var(--accent);line-height:1">05</strong><h3 style="margin:0">Extensions</h3></div><p style="margin:8px 0 0;color:var(--muted)">Additional studies depending on results and feasibility.</p>',
        '<strong style="font-size:2.2rem;color:var(--accent);line-height:1">05</strong><h3 style="margin:0">Year 3</h3></div><p style="margin:8px 0 0;color:var(--muted)">Complementary studies under consideration and planned doctoral activities.</p>'
    ),
    (
        '"chapter": "Rétroplanning global",\n    "study": "",\n    "appendix": false,\n    "hero": true,\n    "divider": true,\n    "_fr": {\n      "section": "Rétroplanning global",\n      "kicker": "",\n      "title": "Rétroplanning",\n      "lead": "",\n      "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PARTIE 6</span><h1>Rétroplanning</h1>',
        '"chapter": "Planification",\n    "study": "",\n    "appendix": false,\n    "hero": true,\n    "divider": true,\n    "_fr": {\n      "section": "Planification",\n      "kicker": "",\n      "title": "Planification",\n      "lead": "",\n      "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PARTIE 6</span><h1>Planification</h1>'
    ),
    (
        '"section": "Rétroplanning global",\n      "kicker": "",\n      "title": "Timeline",\n      "lead": "",\n      "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PART 6</span><h1>Timeline</h1>',
        '"section": "Planning",\n      "kicker": "",\n      "title": "Planning",\n      "lead": "",\n      "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PART 6</span><h1>Planning</h1>'
    ),
    (
        '"section": "Rétroplanning global",\n    "kicker": "",\n    "title": "Rétroplanning",\n    "lead": "",\n    "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PARTIE 6</span><h1>Rétroplanning</h1>',
        '"section": "Planification",\n    "kicker": "",\n    "title": "Planification",\n    "lead": "",\n    "content": "<div class=\\"section-divider-inner\\"><span class=\\"section-divider-number\\">PARTIE 6</span><h1>Planification</h1>'
    ),
    (
        '"title": "Rétroplanning - jusqu’à la soutenance"',
        '"title": "Planification - jusqu’à la soutenance"'
    ),
    (
        '"title": "Timeline - through the defense"',
        '"title": "Planning - through the defense"'
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f'Missing expected target: {old[:120]}')
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')
