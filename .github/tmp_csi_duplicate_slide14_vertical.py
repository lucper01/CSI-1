from pathlib import Path
import json, copy, re, subprocess

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
pos = text.index(marker) + len(marker)
slides, consumed = json.JSONDecoder().raw_decode(text[pos:])
main = [s for s in slides if not s.get('appendix', False)]
assert len(main) >= 14, 'Fewer than 14 main slides'
assert not any(s.get('_variant') == 'slide14-vertical-flow' for s in slides), 'Vertical-flow copy already exists'

source = main[13]
source_before = json.dumps(source, ensure_ascii=False, sort_keys=True)
source_title = source.get('_fr', {}).get('title', source.get('title', ''))
print('Source main slide 14:', source_title)

for lang in ('_fr', '_en'):
    content = source.get(lang, {}).get('content', '')
    assert '<div class="v16-axes">' in content, f'Slide 14 {lang} does not contain v16-axes'
    assert 'v16-pills' in content, f'Slide 14 {lang} does not contain study pills'

copy_slide = copy.deepcopy(source)
copy_slide['_variant'] = 'slide14-vertical-flow'

style = r'''<style>
.v16-axes-flowcopy{align-items:stretch;gap:24px}
.v16-axes-flowcopy article{display:flex;flex-direction:column;min-height:500px}
.v16-axes-flowcopy .v16-pills{display:flex;flex-direction:column;flex-wrap:nowrap;align-items:center;gap:24px;width:100%;margin-top:auto;padding-top:22px}
.v16-axes-flowcopy .v16-pills span{position:relative;display:flex;align-items:center;justify-content:center;width:min(310px,82%);min-height:50px;padding:12px 22px;border-radius:999px;font-size:1.02rem;letter-spacing:.015em;box-shadow:0 7px 18px color-mix(in srgb,var(--study,#777) 10%,transparent)}
.v16-axes-flowcopy .v16-pills span + span::before{content:"↑";position:absolute;left:50%;top:-22px;transform:translateX(-50%);color:color-mix(in srgb,var(--accent-strong) 55%,var(--muted));font-size:1.12rem;font-weight:950;line-height:1}
@media(max-width:900px){.v16-axes-flowcopy article{min-height:auto}.v16-axes-flowcopy .v16-pills span{width:90%;font-size:.92rem}.v16-axes-flowcopy .v16-pills{gap:22px}}
</style>'''

def transform(content):
    out = content.replace('<div class="v16-axes">', '<div class="v16-axes v16-axes-flowcopy">', 1)
    assert out != content
    return style + out

for lang in ('_fr', '_en'):
    copy_slide[lang]['content'] = transform(copy_slide[lang]['content'])
    old_notes = copy_slide[lang].get('notes', '')
    note = ' Copie de travail : pastilles d’études verticales, agrandies et reliées par des flèches orientées du bas vers le haut.' if lang == '_fr' else ' Working copy: study pills arranged vertically, enlarged and linked with upward-pointing arrows.'
    copy_slide[lang]['notes'] = (old_notes + note).strip()

copy_slide['content'] = copy_slide['_fr']['content']
copy_slide['notes'] = copy_slide['_fr']['notes']

src_idx = next(i for i, s in enumerate(slides) if s is source)
slides.insert(src_idx + 1, copy_slide)
assert json.dumps(source, ensure_ascii=False, sort_keys=True) == source_before, 'Original slide 14 changed'

main_after = [s for s in slides if not s.get('appendix', False)]
assert main_after[13] is source
assert main_after[14].get('_variant') == 'slide14-vertical-flow'
assert main_after[14].get('_fr', {}).get('title') == source_title
assert 'flex-direction:column' in main_after[14]['_fr']['content']
assert 'content:"↑"' in main_after[14]['_fr']['content']

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
out = text[:pos] + new_array + text[pos+consumed:]
p.write_text(out, encoding='utf-8')

# Validate only the script that contains const slides = [
scripts = re.findall(r'<script>(.*?)</script>', out, flags=re.S)
matches = [s for s in scripts if 'const slides = [' in s]
assert len(matches) == 1
Path('/tmp/slides.js').write_text(matches[0], encoding='utf-8')
subprocess.run(['node', '--check', '/tmp/slides.js'], check=True)
print('Main slides:', len(main), '->', len(main_after))
print('Original slide 14 preserved; modified copy inserted as slide 15.')
