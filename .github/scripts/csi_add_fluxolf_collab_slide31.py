from pathlib import Path
import json
import hashlib

path = Path('index.html')
save = Path('index_save.html')
save_hash_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = path.read_text(encoding='utf-8')

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

assert len(slides) >= 31, len(slides)
slide = slides[30]

CARD_FR = '<article class="v16-activity-card"><b>1 projet</b><h3>Collaborations</h3><p>FLUXOLF</p></article>'
CARD_EN = '<article class="v16-activity-card"><b>1 project</b><h3>Collaborations</h3><p>FLUXOLF</p></article>'

def add_card(html, lang='fr'):
    if not isinstance(html, str) or not html:
        return html
    if 'FLUXOLF' in html and 'Collaborations' in html:
        return html
    card = CARD_EN if lang == 'en' else CARD_FR
    pos = html.rfind('</article>')
    if pos != -1:
        pos += len('</article>')
        return html[:pos] + card + html[pos:]
    # fallback: insert before the last grid/container close when no article is found
    pos = html.rfind('</div>')
    if pos != -1:
        return html[:pos] + card + html[pos:]
    return html + card

for key in ('content',):
    if key in slide:
        slide[key] = add_card(slide[key], 'fr')

fr = slide.get('_fr')
if isinstance(fr, dict) and 'content' in fr:
    fr['content'] = add_card(fr['content'], 'fr')

en = slide.get('_en')
if isinstance(en, dict) and 'content' in en:
    en['content'] = add_card(en['content'], 'en')

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
new_text = text[:start] + new_json + text[end:]

slide31_json = json.dumps(slides[30], ensure_ascii=False)
assert 'FLUXOLF' in slide31_json
assert 'Collaborations' in slide31_json
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_hash_before

path.write_text(new_text, encoding='utf-8')
