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

fr_year2_article = '''<article class="tools"><b>5 communications 2027</b><h3>Communications scientifiques</h3><p>Communications prévues pendant l’année 2, après les formations doctorales et en articulation avec les collectes.</p><div class="v16-tool-pills"><span>FJC 2027</span><span>JDD 2027</span><span>ECRO 2027</span><span>GDR03 2027</span><span>Expérimentarium 2027</span></div><small>Seules les communications prévues en 2027 sont listées ici.</small></article>'''

en_year2_article = '''<article class="tools"><b>5 events in 2027</b><h3>Scientific communications</h3><p>Planned year-2 communications, positioned after doctoral training activities and coordinated with data collection.</p><div class="v16-tool-pills"><span>FJC 2027</span><span>JDD 2027</span><span>ECRO 2027</span><span>GDR03 2027</span><span>Experimentarium 2027</span></div><small>Only communications planned for 2027 are listed here.</small></article>'''

def replace_tools_article(html, new_article):
    start_idx = html.index('<article class="tools">')
    end_idx = html.index('</article>', start_idx) + len('</article>')
    return html[:start_idx] + new_article + html[end_idx:]

def patch_global_timeline_fr(html):
    html = html.replace('Expérimentarium - FJC - JDD - ECRO - GDR03', 'FJC 2027 - JDD 2027<br>ECRO 2027 - GDR03 2027<br>Expérimentarium 2027')
    html = html.replace('FJC 2028 - JDD 2028 - ISOT si financement', 'FJC 2028<br>JDD 2028<br>ISOT 2028 si financement')
    return html

def patch_global_timeline_en(html):
    html = html.replace('Nuit des chercheurs 2026', 'Researchers’ Night 2026')
    html = html.replace('Expérimentarium - FJC - JDD - ECRO - GDR03', 'FJC 2027 - JDD 2027<br>ECRO 2027 - GDR03 2027<br>Experimentarium 2027')
    html = html.replace('FJC 2028 - JDD 2028 - ISOT si financement', 'FJC 2028<br>JDD 2028<br>ISOT 2028 if funded')
    html = html.replace('Enseignements / formations', 'Teaching / training')
    html = html.replace('Rédaction / valorisation', 'Writing / dissemination')
    html = html.replace('Soutenance', 'Defense')
    return html

for s in slides:
    title = s.get('title', '')
    if title == 'Activités doctorales prévues - 2026-2027':
        s['content'] = replace_tools_article(s['content'], fr_year2_article)
        s['_fr']['content'] = replace_tools_article(s['_fr']['content'], fr_year2_article)
        s['_en']['content'] = replace_tools_article(s['_en']['content'], en_year2_article)
    elif title == 'Rétroplanning - jusqu’à la soutenance':
        s['content'] = patch_global_timeline_fr(s['content'])
        s['_fr']['content'] = patch_global_timeline_fr(s['_fr']['content'])
        s['_en']['content'] = patch_global_timeline_en(s['_en']['content'])

# Validation: year-2 activity slide must contain only 2027 communications in the communications block.
for s in slides:
    if s.get('title') == 'Activités doctorales prévues - 2026-2027':
        for langkey, expected_exp in ((None, 'Expérimentarium 2027'), ('_fr', 'Expérimentarium 2027'), ('_en', 'Experimentarium 2027')):
            d = s if langkey is None else s.get(langkey, {})
            html = d.get('content', '')
            assert 'Communications scientifiques' in html or 'Scientific communications' in html
            for item in ['FJC 2027', 'JDD 2027', 'ECRO 2027', 'GDR03 2027']:
                assert item in html
            assert expected_exp in html
            block = html[html.index('<article class="tools">'):html.index('</article></div>', html.index('<article class="tools">'))]
            assert 'Nuit des chercheurs 2026' not in block
            assert 'Researchers’ Night 2026' not in block
            assert '2028' not in block

# Validation: global timeline keeps the full dated communication list.
for s in slides:
    if s.get('title') == 'Rétroplanning - jusqu’à la soutenance':
        fr = s.get('content', '')
        en = s.get('_en', {}).get('content', '')
        for item in ['Nuit des chercheurs 2026', 'FJC 2027', 'JDD 2027', 'ECRO 2027', 'GDR03 2027', 'Expérimentarium 2027', 'FJC 2028', 'JDD 2028', 'ISOT 2028 si financement']:
            assert item in fr
        for item in ['Researchers’ Night 2026', 'FJC 2027', 'JDD 2027', 'ECRO 2027', 'GDR03 2027', 'Experimentarium 2027', 'FJC 2028', 'JDD 2028', 'ISOT 2028 if funded']:
            assert item in en

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
p.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
