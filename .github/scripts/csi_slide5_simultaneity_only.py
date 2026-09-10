from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = [
    ('<h3>Ordre et simultanéité</h3>', '<h3>Simultanéité</h3>', 2),
    ('<p>Lorsque deux événements surviennent, on peut mesurer leur ordre temporel ou demander s’ils sont perçus comme simultanés.</p>', '<p>Lorsque deux événements surviennent, on peut demander s’ils sont perçus comme simultanés.</p>', 2),
    ('<h3>Order and simultaneity</h3>', '<h3>Simultaneity</h3>', 1),
    ('<p>When two events occur, their temporal order can be measured or observers can judge whether they appear simultaneous.</p>', '<p>When two events occur, observers can judge whether they appear simultaneous.</p>', 1),
]

for old, new, expected in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'Expected {expected} occurrence(s) of {old!r}, found {count}')
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')
print('Slide 5 relation card now covers simultaneity only in FR and EN.')
