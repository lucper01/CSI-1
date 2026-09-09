from pathlib import Path
import json
import hashlib

p = Path('index.html')
save = Path('index_save.html')
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

solar_span = '<span data-study="SOLAR">SOLAR</span>'
sorbet_span = '<span data-study="SORBET">SORBET</span>'

def fix_axes_slide(html, lang):
    axis2_label = '<article><b>Axe 2</b>' if lang == 'fr' else '<article><b>Axis 2</b>'
    assert axis2_label in html
    first, second = html.split(axis2_label, 1)
    first = first.replace(solar_span, '')
    second = second.replace(solar_span, '')
    assert sorbet_span in first
    first = first.replace(sorbet_span, sorbet_span + solar_span, 1)
    return first + axis2_label + second

def fix_extensions(html, lang):
    old = '<article data-study="SOLAR"><b>Axe 2</b>' if lang == 'fr' else '<article data-study="SOLAR"><b>Axis 2</b>'
    new = '<article data-study="SOLAR"><b>Axe 1</b>' if lang == 'fr' else '<article data-study="SOLAR"><b>Axis 1</b>'
    assert old in html
    return html.replace(old, new, 1)

def fix_retro(html, lang):
    if lang == 'fr':
        axis2 = '<section><h3>Axe 2 - Espace</h3>'
        old_axis1_ext = '<div class="lane ext"><b>Complémentaire</b><i></i><i></i><article data-study="SORBET"><strong>SORBET</strong></article><i></i></div>'
        new_axis1_ext = '<div class="lane ext"><b>Complémentaire</b><i></i><i></i><article class="stack"><span data-study="SORBET"><strong>SORBET</strong></span><span data-study="SOLAR"><strong>SOLAR</strong></span></article><i></i></div>'
    else:
        axis2 = '<section><h3>Axis 2 - Space</h3>'
        old_axis1_ext = '<div class="lane ext"><b>Complementary</b><i></i><i></i><article data-study="SORBET"><strong>SORBET</strong></article><i></i></div>'
        new_axis1_ext = '<div class="lane ext"><b>Complementary</b><i></i><i></i><article class="stack"><span data-study="SORBET"><strong>SORBET</strong></span><span data-study="SOLAR"><strong>SOLAR</strong></span></article><i></i></div>'
    assert axis2 in html
    a1, rest = html.split(axis2, 1)
    assert old_axis1_ext in a1
    a1 = a1.replace(old_axis1_ext, new_axis1_ext, 1)
    rest = rest.replace('<span data-study="SOLAR"><strong>SOLAR</strong></span>', '', 1)
    return a1 + axis2 + rest

for s in slides:
    title = s.get('title', '')
    if title == 'Deux axes':
        s['content'] = fix_axes_slide(s['content'], 'fr')
        s['_fr']['content'] = fix_axes_slide(s['_fr']['content'], 'fr')
        s['_en']['content'] = fix_axes_slide(s['_en']['content'], 'en')
    elif title == 'Études complémentaires et exploratoires':
        s['content'] = fix_extensions(s['content'], 'fr')
        s['_fr']['content'] = fix_extensions(s['_fr']['content'], 'fr')
        s['_en']['content'] = fix_extensions(s['_en']['content'], 'en')
    elif title == 'Rétroplanning des études':
        s['content'] = fix_retro(s['content'], 'fr')
        s['_fr']['content'] = fix_retro(s['_fr']['content'], 'fr')
        s['_en']['content'] = fix_retro(s['_en']['content'], 'en')

for s in slides:
    if s.get('appendix'):
        continue
    for langkey, lang in ((None, 'fr'), ('_fr', 'fr'), ('_en', 'en')):
        d = s if langkey is None else s.get(langkey, {})
        html = d.get('content', '')
        if 'SOLAR' not in html:
            continue
        if s.get('title') == 'Deux axes':
            split_label = '<article><b>Axe 2</b>' if lang == 'fr' else '<article><b>Axis 2</b>'
            before, after = html.split(split_label, 1)
            assert 'SOLAR' in before and 'SOLAR' not in after
        if s.get('title') == 'Études complémentaires et exploratoires':
            wanted = '<article data-study="SOLAR"><b>Axe 1</b>' if lang == 'fr' else '<article data-study="SOLAR"><b>Axis 1</b>'
            assert wanted in html
        if s.get('title') == 'Rétroplanning des études':
            split_label = '<section><h3>Axe 2 - Espace</h3>' if lang == 'fr' else '<section><h3>Axis 2 - Space</h3>'
            before, after = html.split(split_label, 1)
            assert 'SOLAR' in before and 'SOLAR' not in after

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
p.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
