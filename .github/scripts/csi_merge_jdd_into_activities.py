from pathlib import Path
import json
import re

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

visible = [(i, s) for i, s in enumerate(slides) if not s.get('appendix')]
assert visible[30][1].get('title') == 'Enseignement, formation et encadrement', visible[30][1].get('title')
assert visible[31][1].get('title') == 'JDD 2026 - faire connaître STOLF', visible[31][1].get('title')

activity_idx = visible[30][0]
jdd_idx = visible[31][0]
activity = slides[activity_idx]

fr_card = '<article class="tools"><b>JDD 2026</b><h3>Communications</h3></article>'
en_card = '<article class="tools"><b>JDD 2026</b><h3>Scientific communication</h3></article>'

def add_card(html, card):
    assert html.startswith('<div class="v16-activity">')
    assert html.endswith('</div>')
    assert 'JDD 2026' not in html
    return html[:-6] + card + '</div>'

activity['content'] = add_card(activity['content'], fr_card)
activity['_fr']['content'] = add_card(activity['_fr']['content'], fr_card)
activity['_en']['content'] = add_card(activity['_en']['content'], en_card)

# Remove the dedicated JDD slide after its essential mention has been merged into slide 31.
del slides[jdd_idx]

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

# The local part timeline is indexed by visible slide number. One visible slide was removed at position 32,
# so all later numeric boundaries shift by one. Slide 31 alone remains the Activities step.
fn_start = text.index('function partTimelineFor(index){')
fn_end = text.index('\nfunction renderPartTimeline', fn_start)
fn = text[fn_start:fn_end]
fn = fn.replace('else if(n>=31&&n<=32) active=4;', 'else if(n===31) active=4;')

def shift_match(m):
    op = m.group(1)
    num = int(m.group(2))
    if num >= 33:
        num -= 1
    return f'n{op}{num}'

fn = re.sub(r'n(>=|<=|===)(\d+)', shift_match, fn)
text = text[:fn_start] + fn + text[fn_end:]

# Final checks.
assert text.count('"title":"JDD 2026 - faire connaître STOLF"') == 0
assert text.count('<b>JDD 2026</b><h3>Communications</h3>') >= 2
assert 'else if(n===31) active=4;' in text
assert 'else if(n===32) active=5;' in text

p.write_text(text, encoding='utf-8')
