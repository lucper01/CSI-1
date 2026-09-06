from pathlib import Path
import re, json

p = Path('index.html')
h = p.read_text(encoding='utf-8')
m = re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides', h, re.S)
if not m:
    raise SystemExit('slides array not found')
slides = json.loads(m.group(1))

hardware = {
    'SOFT - Méthode': 'Sniff-0 · Spir-0 · BIOPAC MP160 · EEG BioSemi',
    'OASIS - Méthode': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'TWIXOLF - Méthode': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'SORBET': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'SOLAR': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'COBEX': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'BRAUD': 'Sniff-0 · Spir-0 · BIOPAC MP160',
    'BRAUDOLF': 'Sniff-0 · Spir-0 · BIOPAC MP160',
}

hw_re = re.compile(r'<div class="hardware-floating"[^>]*>.*?</div></div>', re.S)
sf_re = re.compile(r'(<div class="study-floating"[^>]*>)(.*?)(</div>)', re.S)

def harmonize(content, title, lang='fr'):
    if not isinstance(content, str):
        return content
    label = 'Matériel' if lang == 'fr' else 'Hardware'
    card = f'<div class="float-card hardware-card"><b>{label}</b><span>{hardware[title]}</span></div>'
    content, n = hw_re.subn('', content, count=1)
    if n != 1:
        raise SystemExit(f'hardware block count {n} for {title}/{lang}')
    if title.endswith(' - Méthode'):
        def repl(mm):
            return mm.group(1) + mm.group(2) + card + mm.group(3)
        content, n = sf_re.subn(repl, content, count=1)
        if n != 1:
            raise SystemExit(f'resource row missing for {title}/{lang}')
    else:
        content += f'<div class="study-floating hardware-resource-row" aria-label="{label} {title}">{card}</div>'
    return content

for s in slides:
    title = s.get('title', '')
    if title not in hardware:
        continue
    s['content'] = harmonize(s.get('content', ''), title, 'fr')
    if isinstance(s.get('_fr'), dict) and isinstance(s['_fr'].get('content'), str):
        s['_fr']['content'] = harmonize(s['_fr']['content'], title, 'fr')
    if isinstance(s.get('_en'), dict) and isinstance(s['_en'].get('content'), str):
        s['_en']['content'] = harmonize(s['_en']['content'], title, 'en')

# Slide 33: remove VIBEX from the planned timeline while preserving the bottom banner that mentions it.
retro = next((s for s in slides if s.get('title') == 'Rétroplanning des études'), None)
if not retro:
    raise SystemExit('timeline slide not found')
fr_vibex = '<article data-study="VIBEX"><strong>VIBEX</strong></article>'
for container in (retro, retro.get('_fr', {})):
    if isinstance(container, dict) and isinstance(container.get('content'), str):
        if fr_vibex not in container['content']:
            raise SystemExit('VIBEX planned item missing in FR timeline')
        container['content'] = container['content'].replace(fr_vibex, '<i></i>', 1)
if isinstance(retro.get('_en'), dict) and isinstance(retro['_en'].get('content'), str):
    if fr_vibex not in retro['_en']['content']:
        raise SystemExit('VIBEX planned item missing in EN timeline')
    retro['_en']['content'] = retro['_en']['content'].replace(fr_vibex, '<i></i>', 1)

# Slide 34: simplify dissemination wording.
activities = next((s for s in slides if s.get('title') == 'Activités doctorales prévues - 2026-2027'), None)
if not activities:
    raise SystemExit('activities slide not found')
for container in (activities, activities.get('_fr', {})):
    if isinstance(container, dict) and isinstance(container.get('content'), str):
        container['content'] = container['content'].replace(
            'La diffusion scientifique se poursuit en parallèle des collectes, sans diapo de calendrier séparée.',
            'La diffusion scientifique se poursuit en parallèle des collectes.'
        )
if isinstance(activities.get('_en'), dict) and isinstance(activities['_en'].get('content'), str):
    activities['_en']['content'] = activities['_en']['content'].replace(
        'Scientific dissemination continues alongside data collection, without a separate communication-calendar slide.',
        'Scientific dissemination continues alongside data collection.'
    )

# Remove the stale SOFT pilot wording that remained in the discussion slide.
for s in slides:
    for container in (s, s.get('_fr', {}), s.get('_en', {})):
        if not isinstance(container, dict):
            continue
        for field in ('content', 'lead', 'notes'):
            if not isinstance(container.get(field), str):
                continue
            container[field] = container[field].replace('critères de simplification après le pilote', 'critères de simplification si nécessaire')
            container[field] = container[field].replace('simplification criteria after the pilot', 'simplification criteria if needed')

arr = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
h = h[:m.start(1)] + arr + h[m.end(1):]

css = '''
/* Hardware resource cards V3 - same ergonomics as VIBEX/TWIXAV */
.study-floating .float-card.hardware-card{
  min-width:190px;
  max-width:245px;
  padding:10px 13px;
  justify-content:center;
  background:color-mix(in srgb,var(--white) 94%,var(--study,var(--accent)) 6%);
}
.study-floating .float-card.hardware-card>span{
  display:block;
  margin-top:2px;
  font-size:.72rem;
  line-height:1.25;
  font-weight:520;
  color:var(--text);
  white-space:normal;
}
.study-floating.hardware-resource-row{
  margin-top:14px!important;
  margin-left:auto!important;
  justify-content:flex-end!important;
}
@media(max-width:900px){
  .study-floating .float-card.hardware-card{min-width:0;max-width:none;flex:1 1 190px}
  .study-floating.hardware-resource-row{margin-left:0!important;justify-content:flex-start!important}
}
'''
marker = '</style>\n\n<style id="csi-flat-v17">'
if marker not in h:
    raise SystemExit('style marker not found')
h = h.replace(marker, css + '\n</style>\n\n<style id="csi-flat-v17">', 1)
p.write_text(h, encoding='utf-8')

# Validation
m2 = re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides', h, re.S)
check = json.loads(m2.group(1))
assert len(check) == 40
for title in hardware:
    s = next(x for x in check if x.get('title') == title)
    blob = json.dumps(s, ensure_ascii=False)
    assert 'hardware-floating' not in blob, title
    assert 'hardware-card' in blob, title
    assert 'Sniff-0' in blob and 'Spir-0' in blob and 'BIOPAC MP160' in blob, title
    if title == 'SOFT - Méthode':
        assert 'EEG BioSemi' in blob
    else:
        assert 'EEG BioSemi' not in blob
retro = next(x for x in check if x.get('title') == 'Rétroplanning des études')
retro_blob = json.dumps(retro, ensure_ascii=False)
assert '<article data-study="VIBEX"><strong>VIBEX</strong></article>' not in retro_blob
assert 'analyses, figures et manuscrits TWIXAV / VIBEX' in retro_blob
act = next(x for x in check if x.get('title') == 'Activités doctorales prévues - 2026-2027')
act_blob = json.dumps(act, ensure_ascii=False)
assert 'sans diapo de calendrier séparée' not in act_blob
assert 'without a separate communication-calendar slide' not in act_blob
assert 'après le pilote' not in json.dumps(check, ensure_ascii=False)
print('CSI UPDATE VALIDATED')
