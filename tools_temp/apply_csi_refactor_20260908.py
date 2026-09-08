from pathlib import Path
import json
import re

index_path = Path('index.html')
save_path = Path('index_save.html')

text = index_path.read_text(encoding='utf-8')
saved = save_path.read_text(encoding='utf-8')
if text != saved:
    raise SystemExit('Safety stop: index_save.html is not an exact copy of index.html before refactor.')

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end
original_count = len(slides)

# Slide 16 - TWIXAV must use its own study blue rather than the Portfolio accent.
def accent_twixav(html: str) -> str:
    if not isinstance(html, str):
        return html
    pos = html.find('TWIXAV')
    if pos < 0:
        return html
    card_start = html.rfind('<div class="card', 0, pos)
    if card_start < 0:
        return html
    tag_end = html.find('>', card_start)
    if tag_end < 0:
        return html
    tag = html[card_start:tag_end + 1]
    accent = 'border-color:#0072B2;box-shadow:inset 4px 0 0 #0072B2'
    if 'style="' in tag:
        new_tag = re.sub(
            r'style="([^"]*)"',
            lambda m: 'style="' + m.group(1).rstrip(';') + ';' + accent + '"',
            tag,
            count=1,
        )
    else:
        new_tag = tag[:-1] + f' style="{accent}">'
    return html[:card_start] + new_tag + html[tag_end + 1:]

s16 = slides[15]
for lang in ('_fr', '_en'):
    if isinstance(s16.get(lang), dict) and isinstance(s16[lang].get('content'), str):
        s16[lang]['content'] = accent_twixav(s16[lang]['content'])
if isinstance(s16.get('content'), str):
    s16['content'] = accent_twixav(s16['content'])

# Remove current slide 34.
removed_slide = slides.pop(33)

# Former slide 35 is now slide 34 - lighter visual treatment, no lower dark banner.
s = slides[33]
fr = {
    'section': 'Transition vers la deuxième année',
    'kicker': 'PARTIE 3 - BILAN',
    'title': 'Deux paradigmes stabilisés ouvrent la deuxième année',
    'lead': 'TWIXAV et VIBEX constituent désormais deux socles expérimentaux suffisamment fixés pour engager les trois études prioritaires de l’année suivante.',
    'content': '''<div class="grid two" style="gap:22px;align-items:stretch">
<div class="card" style="border-color:#0072B2;box-shadow:inset 4px 0 0 #0072B2"><div class="mono">SOCLE TEMPOREL</div><h3>TWIXAV</h3><p>Paradigme, protocole, mesures et analyses sont stabilisés. Ce socle permet d’aller vers <strong>SOFT</strong>, puis vers la transposition olfactive avec <strong>TWIXOLF</strong>.</p></div>
<div class="card"><div class="mono">SOCLE SPATIAL</div><h3>VIBEX</h3><p>Le paradigme de Boundary Extension, son protocole et ses analyses sont fixés. Ce socle permet de tester directement l’influence olfactive avec <strong>OASIS</strong>.</p></div>
</div>
<div style="display:flex;align-items:center;justify-content:center;gap:22px;margin-top:26px;flex-wrap:wrap;text-align:center">
<div><div class="mono">ANNÉE 1</div><h3 style="margin:6px 0 0">2 paradigmes opérationnels</h3></div>
<div aria-hidden="true" style="font-size:32px;font-weight:800;opacity:.55">→</div>
<div><div class="mono">ANNÉE 2</div><h3 style="margin:6px 0 0">SOFT - OASIS - TWIXOLF</h3></div>
</div>''',
    'notes': 'Insister sur la transition : deux paradigmes et protocoles bien fixés en année 1 permettent d’ouvrir directement les trois études prioritaires de l’année 2.'
}
en = {
    'section': 'Transition to Year 2',
    'kicker': 'PART 3 - SUMMARY',
    'title': 'Two stabilized paradigms open the way to Year 2',
    'lead': 'TWIXAV and VIBEX now provide two sufficiently stabilized experimental foundations to launch the three priority studies of the following year.',
    'content': '''<div class="grid two" style="gap:22px;align-items:stretch">
<div class="card" style="border-color:#0072B2;box-shadow:inset 4px 0 0 #0072B2"><div class="mono">TEMPORAL FOUNDATION</div><h3>TWIXAV</h3><p>The paradigm, protocol, measures and analyses are stabilized. This foundation supports <strong>SOFT</strong>, then the olfactory transposition with <strong>TWIXOLF</strong>.</p></div>
<div class="card"><div class="mono">SPATIAL FOUNDATION</div><h3>VIBEX</h3><p>The Boundary Extension paradigm, protocol and analyses are fixed. This foundation supports the direct test of olfactory influence with <strong>OASIS</strong>.</p></div>
</div>
<div style="display:flex;align-items:center;justify-content:center;gap:22px;margin-top:26px;flex-wrap:wrap;text-align:center">
<div><div class="mono">YEAR 1</div><h3 style="margin:6px 0 0">2 operational paradigms</h3></div>
<div aria-hidden="true" style="font-size:32px;font-weight:800;opacity:.55">→</div>
<div><div class="mono">YEAR 2</div><h3 style="margin:6px 0 0">SOFT - OASIS - TWIXOLF</h3></div>
</div>''',
    'notes': 'Emphasize the transition: two well-established Year 1 paradigms and protocols directly support the three priority Year 2 studies.'
}
s.update(fr)
s['_fr'] = fr.copy()
s['_en'] = en

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
new_text = text[:start] + new_json + text[end:]
index_path.write_text(new_text, encoding='utf-8')

# Validation
check = index_path.read_text(encoding='utf-8')
check_start = check.index(marker) + len(marker)
check_slides, _ = json.JSONDecoder().raw_decode(check[check_start:])
assert len(check_slides) == original_count - 1
assert check_slides[33].get('title') == 'Deux paradigmes stabilisés ouvrent la deuxième année'
assert 'card dark' not in check_slides[33].get('content', '')
slide16_html = (check_slides[15].get('content') or '') + str(check_slides[15].get('_fr', {}).get('content', ''))
assert 'TWIXAV' in slide16_html and '#0072B2' in slide16_html
assert save_path.read_text(encoding='utf-8') == saved
print('OK - removed slide 34, simplified former slide 35, fixed TWIXAV accent on slide 16, save untouched.')
