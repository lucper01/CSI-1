from pathlib import Path
import json
import re
import hashlib

index = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

# Find the year 3 activity slide created previously.
year3_candidates = []
for i, s in enumerate(slides):
    blob = json.dumps(s, ensure_ascii=False)
    if ('DocAdoct' in blob or 'FJC 2028' in blob or 'ISOT 2028' in blob) and ('Troisième année' in blob or 'Year 3' in blob):
        year3_candidates.append((i, s))
assert len(year3_candidates) == 1, [s.get('title') for _, s in year3_candidates]
year3_idx, year3_slide = year3_candidates[0]

# Remove any previous year 3 divider if this script is re-run.
slides = [s for s in slides if not (
    s.get('divider') and (
        s.get('title') in ('Troisième année', 'Third year')
        or s.get('_fr', {}).get('title') == 'Troisième année'
        or s.get('_en', {}).get('title') == 'Third year'
    )
)]

# Remove the activity slide from its current position; it will be reinserted just after the divider.
slides = [s for s in slides if s is not year3_slide]

fr_content = '<div class="section-divider-inner"><span class="section-divider-number">PARTIE 6</span><h1>Troisième année</h1><i aria-hidden="true"></i></div>'
en_content = '<div class="section-divider-inner"><span class="section-divider-number">PART 6</span><h1>Third year</h1><i aria-hidden="true"></i></div>'
year3_divider = {
    'chapter': 'Troisième année',
    'study': '',
    'appendix': False,
    'hero': True,
    'divider': True,
    '_fr': {
        'section': 'Troisième année',
        'kicker': '',
        'title': 'Troisième année',
        'lead': '',
        'content': fr_content,
        'notes': ''
    },
    '_en': {
        'section': 'Third year',
        'kicker': '',
        'title': 'Third year',
        'lead': '',
        'content': en_content,
        'notes': ''
    },
    'section': 'Troisième année',
    'kicker': '',
    'title': 'Troisième année',
    'lead': '',
    'content': fr_content,
    'notes': ''
}

# Insert between visible slides 51 and 52, i.e. after the 51st non-appendix slide.
visible_indices = [i for i, s in enumerate(slides) if not s.get('appendix')]
assert len(visible_indices) >= 52, len(visible_indices)
insert_after_visible = 51
insert_pos = visible_indices[insert_after_visible - 1] + 1
slides[insert_pos:insert_pos] = [year3_divider, year3_slide]

# Keep the year 3 activity slide explicitly attached to the new section.
for key in (None, '_fr', '_en'):
    d = year3_slide if key is None else year3_slide.get(key, {})
    if not d:
        continue
    if key == '_en':
        d['section'] = 'Third year'
    else:
        d['section'] = 'Troisième année'

# Shift timeline numerical ranges because one visible divider was inserted at position 52,
# and the year 3 activity slide was moved after it. It gets its own local timeline.
new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

fn_start = text.index('function partTimelineFor(index){')
fn_end = text.index('\nfunction renderPartTimeline', fn_start)
fn = text[fn_start:fn_end]

# Remove previous year 3 timeline block if present.
fn = re.sub(r"\n  if\(n>=52&&n<=53\)\{\n    return \{steps:E\?\['YEAR 3','ACTIVITIES'\]:\['3ÈME ANNÉE','ACTIVITÉS'\],active:n-52\};\n  \}", '', fn)

# Shift all slide-number references from 52 onward by +1, then add a block for new slides 52-53.
def shift_match(m):
    op = m.group(1)
    num = int(m.group(2))
    if num >= 52:
        num += 1
    return f'n{op}{num}'
fn = re.sub(r'n(>=|<=|===)(\d+)', shift_match, fn)
insert_block = "\n  if(n>=52&&n<=53){\n    return {steps:E?['YEAR 3','ACTIVITIES']:['3ÈME ANNÉE','ACTIVITÉS'],active:n-52};\n  }"
anchor = '  if(n>=54&&n<=56){'
# After shifting, the previous planning block starts at 54; insert just before it.
assert anchor in fn
fn = fn.replace(anchor, insert_block + '\n' + anchor, 1)
text = text[:fn_start] + fn + text[fn_end:]

# Checks.
visible = [(i, s) for i, s in enumerate(slides) if not s.get('appendix')]
assert visible[51][1].get('title') == 'Troisième année', visible[51][1].get('title')
assert visible[52][1] is year3_slide
assert 'DocAdoct' in json.dumps(visible[52][1], ensure_ascii=False)
assert 'PARTIE 6' in json.dumps(visible[51][1], ensure_ascii=False)
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before

index.write_text(text, encoding='utf-8')
