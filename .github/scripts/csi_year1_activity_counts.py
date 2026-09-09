from pathlib import Path
import json
import hashlib

index = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

matches = [s for s in slides if s.get('title') == 'Enseignement, formation et encadrement']
assert len(matches) == 1
s = matches[0]

fr_comm_variants = [
    '<article class="tools"><b>JDD 2026</b><h3>Communications</h3></article>',
    '<article class="tools"><b>Communications</b><h3>JDD 2026</h3><p>Présentation de l’Axe 2 du projet STOLF.</p></article>',
]
fr_comm_new = '<article class="tools"><b>1 communication</b><h3>Communications</h3><p><strong>JDD 2026</strong><br>Présentation de l’Axe 2 du projet STOLF.</p></article>'

en_comm_variants = [
    '<article class="tools"><b>JDD 2026</b><h3>Scientific communication</h3></article>',
    '<article class="tools"><b>Scientific communication</b><h3>JDD 2026</h3><p>Presentation of Axis 2 of the STOLF project.</p></article>',
]
en_comm_new = '<article class="tools"><b>1 communication</b><h3>Scientific communication</h3><p><strong>JDD 2026</strong><br>Presentation of Axis 2 of the STOLF project.</p></article>'

def patch_fr(html):
    html = html.replace('<article><b>M1</b><h3>Encadrement</h3>', '<article><b>3 M1</b><h3>Encadrement</h3>')
    html = html.replace('<article><b>3 M1</b><h3>Encadrement</h3>', '<article><b>3 M1</b><h3>Encadrement</h3>')
    replaced = False
    for old in fr_comm_variants:
        if old in html:
            html = html.replace(old, fr_comm_new)
            replaced = True
            break
    if not replaced:
        assert fr_comm_new in html
    assert '<b>3 M1</b><h3>Encadrement</h3>' in html
    assert fr_comm_new in html
    return html

def patch_en(html):
    html = html.replace('<article><b>M1</b><h3>Supervision</h3>', '<article><b>3 M1</b><h3>Supervision</h3>')
    replaced = False
    for old in en_comm_variants:
        if old in html:
            html = html.replace(old, en_comm_new)
            replaced = True
            break
    if not replaced:
        assert en_comm_new in html
    assert '<b>3 M1</b><h3>Supervision</h3>' in html
    assert en_comm_new in html
    return html

s['content'] = patch_fr(s['content'])
s['_fr']['content'] = patch_fr(s['_fr']['content'])
s['_en']['content'] = patch_en(s['_en']['content'])

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
index.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before
