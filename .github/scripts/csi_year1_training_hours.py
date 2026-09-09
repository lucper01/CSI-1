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

def patch_fr(html):
    old_teach = '<article><b>54 h eq. TD</b><h3>Enseignement</h3>'
    new_teach = '<article><b>54 h eq. TD - 27 h valorisées</b><h3>Enseignement</h3>'
    assert old_teach in html or new_teach in html
    html = html.replace(old_teach, new_teach, 1)

    old_train = '<article><b>60 h</b><h3>Formation doctorale</h3><p>Pédagogie universitaire, enseignement, IA et éducation, intégrité scientifique, intelligence économique et Zotero.</p></article>'
    new_train = '<article><b>33 h</b><h3>Formation doctorale</h3><p>Pédagogie universitaire, IA et éducation, intégrité scientifique, intelligence économique et Zotero.</p></article>'
    assert old_train in html or new_train in html
    html = html.replace(old_train, new_train, 1)

    assert new_teach in html
    assert new_train in html
    return html

def patch_en(html):
    old_teach = '<article><b>54 tutorial-equivalent h</b><h3>Teaching</h3>'
    new_teach = '<article><b>54 tutorial-equivalent h - 27 h credited</b><h3>Teaching</h3>'
    assert old_teach in html or new_teach in html
    html = html.replace(old_teach, new_teach, 1)

    old_train = '<article><b>60 h</b><h3>Doctoral training</h3><p>University pedagogy, teaching, AI and education, research integrity, economic intelligence and Zotero.</p></article>'
    new_train = '<article><b>33 h</b><h3>Doctoral training</h3><p>University pedagogy, AI and education, research integrity, economic intelligence and Zotero.</p></article>'
    assert old_train in html or new_train in html
    html = html.replace(old_train, new_train, 1)

    assert new_teach in html
    assert new_train in html
    return html

s['content'] = patch_fr(s['content'])
s['_fr']['content'] = patch_fr(s['_fr']['content'])
s['_en']['content'] = patch_en(s['_en']['content'])

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
index.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before
