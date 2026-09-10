from pathlib import Path
import json

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
pos = text.index(marker) + len(marker)
slides, consumed = json.JSONDecoder().raw_decode(text[pos:])
main = [s for s in slides if not s.get('appendix', False)]

assert len(main) >= 39
s15 = main[14]
s16 = main[15]
s17 = main[16]
assert s15.get('_variant') == 'slide14-vertical-flow'
assert s16.get('_variant') == 'slide14-vertical-flow-stage2'
assert s17.get('_variant') == 'slide14-vertical-flow-stage3'

# Snapshot the current destination boundaries before any move.
a28, a29 = main[27], main[28]
a38, a39 = main[37], main[38]


def content_slots(slide):
    slots = [(slide, 'content')]
    for lang in ('_fr', '_en'):
        if isinstance(slide.get(lang), dict):
            slots.append((slide[lang], 'content'))
    return slots

# Reverse all inter-study arrows on the three staged slides.
for slide in (s15, s16, s17):
    changed = 0
    for obj, key in content_slots(slide):
        value = obj.get(key, '')
        if 'content:"↑"' in value:
            value = value.replace('content:"↑"', 'content:"↓"')
            changed += 1
        obj[key] = value
    assert changed >= 2, (slide.get('_variant'), changed)

# Slide 16 state: only TWIXAV and VIBEX are transparent.
for obj, key in content_slots(s16):
    value = obj.get(key, '')
    value = value.replace('.s16-stage2 .v16-pills span[data-study]{opacity:.42}',
                          '.s16-stage2 .v16-pills span[data-study]{opacity:1}')
    obj[key] = value

# Slide 17 state: TWIXAV and VIBEX are fully opaque.
for obj, key in content_slots(s17):
    value = obj.get(key, '')
    value = value.replace('.s17-stage3 .v16-pills span[data-study]{opacity:.42}',
                          '.s17-stage3 .v16-pills span[data-study]{opacity:1}')
    obj[key] = value

# Update notes to match the requested states.
s16['_fr']['notes'] = 'Deuxième état : SOLAR, BRAUD et BRAUDOLF sont retirés. Seuls TWIXAV et VIBEX sont atténués ; SOFT, TWIXOLF et VIBOLF restent en pleine opacité. Les flèches entre études sont orientées vers le bas.'
s16['_en']['notes'] = 'Second state: SOLAR, BRAUD and BRAUDOLF are removed. Only TWIXAV and VIBEX are faded; SOFT, TWIXOLF and VIBOLF remain fully opaque. Arrows between studies point downward.'
s16['notes'] = s16['_fr']['notes']
s17['_fr']['notes'] = 'Troisième état, redérivé de la diapo 15 : seules TWIXAV et VIBEX restent visibles, sans transparence. Les flèches entre études sont orientées vers le bas.'
s17['_en']['notes'] = 'Third state, re-derived from slide 15: only TWIXAV and VIBEX remain visible, with no transparency. Arrows between studies point downward.'
s17['notes'] = s17['_fr']['notes']
s15['_fr']['notes'] = 'Copie de travail de la diapo 14 : études disposées verticalement. Toutes les études sont atténuées, sauf SOLAR, BRAUD et BRAUDOLF qui restent en pleine opacité. Les flèches entre études sont orientées vers le bas.'
s15['_en']['notes'] = 'Working copy of slide 14: studies are arranged vertically. All studies are faded except SOLAR, BRAUD and BRAUDOLF, which remain fully opaque. Arrows between studies point downward.'
s15['notes'] = s15['_fr']['notes']

# Validate opacity logic before moving.
fr15 = s15['_fr']['content']
assert '.s15-stage1 .v16-pills span[data-study]{opacity:.42}' in fr15
assert '[data-study="SOLAR"]' in fr15 and '[data-study="BRAUD"]' in fr15 and '[data-study="BRAUDOLF"]' in fr15
assert 'opacity:1' in fr15

fr16 = s16['_fr']['content']
assert 'data-study="SOLAR"' not in fr16 and 'data-study="BRAUD"' not in fr16 and 'data-study="BRAUDOLF"' not in fr16
assert '.s16-stage2 .v16-pills span[data-study]{opacity:1}' in fr16
assert '[data-study="TWIXAV"]' in fr16 and '[data-study="VIBEX"]' in fr16
assert '{opacity:.24}' in fr16

fr17 = s17['_fr']['content']
assert 'data-study="TWIXAV"' in fr17 and 'data-study="VIBEX"' in fr17
for name in ('SOFT', 'TWIXOLF', 'SOLAR', 'VIBOLF', 'BRAUD', 'BRAUDOLF'):
    assert f'data-study="{name}"' not in fr17
assert '.s17-stage3 .v16-pills span[data-study]{opacity:1}' in fr17

# Move current slide 16 between the CURRENT slides 28 and 29,
# and current slide 15 between the CURRENT slides 38 and 39.
slides.remove(s15)
slides.remove(s16)
slides.insert(slides.index(a29), s16)
slides.insert(slides.index(a39), s15)

# Verify the requested adjacency using the snapshotted destination slides.
main_after = [s for s in slides if not s.get('appendix', False)]

def mid_between(prev, item, nxt):
    ip = next(i for i, x in enumerate(main_after) if x is prev)
    ii = next(i for i, x in enumerate(main_after) if x is item)
    inx = next(i for i, x in enumerate(main_after) if x is nxt)
    return ip + 1 == ii and ii + 1 == inx

assert mid_between(a28, s16, a29)
assert mid_between(a38, s15, a39)
assert sum(1 for s in main_after if s.get('_variant') == 'slide14-vertical-flow') == 1
assert sum(1 for s in main_after if s.get('_variant') == 'slide14-vertical-flow-stage2') == 1
assert sum(1 for s in main_after if s.get('_variant') == 'slide14-vertical-flow-stage3') == 1

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
p.write_text(text[:pos] + new_array + text[pos + consumed:], encoding='utf-8')
