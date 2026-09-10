from pathlib import Path
import copy, json, re

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
pos = text.index(marker) + len(marker)
slides, consumed = json.JSONDecoder().raw_decode(text[pos:])

# Target the working copy created from slide 14.
target_indices = [i for i, s in enumerate(slides) if s.get('_variant') == 'slide14-vertical-flow' and not s.get('appendix', False)]
assert len(target_indices) == 1, target_indices
ti = target_indices[0]

# Ensure we do not accidentally duplicate stages on a rerun.
assert not any(s.get('_variant') in {'slide14-vertical-flow-stage2','slide14-vertical-flow-stage3'} for s in slides)

# Preserve the main slide immediately before the working copy byte-for-byte at object level.
orig14 = copy.deepcopy(slides[ti-1])

scope_old = 'v16-axes-flowcopy'
scope15 = 'v16-axes-flowcopy s15-stage1'

opacity_css_fr = '''\n<style>\n.s15-stage1 .v16-pills span[data-study]{opacity:.42}\n.s15-stage1 .v16-pills span[data-study="SOLAR"],\n.s15-stage1 .v16-pills span[data-study="BRAUD"],\n.s15-stage1 .v16-pills span[data-study="BRAUDOLF"]{opacity:1}\n</style>'''
opacity_css_en = opacity_css_fr

# Stage 1 - slide 15: preserve all studies, fade all except SOLAR / BRAUD / BRAUDOLF.
target = slides[ti]
for key in ('_fr','_en'):
    c = target[key]['content']
    c = c.replace('class="v16-axes v16-axes-flowcopy"', 'class="v16-axes v16-axes-flowcopy s15-stage1"', 1)
    c += opacity_css_fr if key == '_fr' else opacity_css_en
    target[key]['content'] = c

target['content'] = target['_fr']['content']
target['_fr']['notes'] = "Copie de travail de la diapo 14 : études disposées verticalement et reliées par des flèches ascendantes. Toutes les études sont atténuées, sauf SOLAR, BRAUD et BRAUDOLF qui restent en pleine opacité."
target['_en']['notes'] = "Working copy of slide 14: studies arranged vertically and linked by upward arrows. All studies are faded except SOLAR, BRAUD and BRAUDOLF, which remain fully opaque."
target['notes'] = target['_fr']['notes']

# Build stage 2 from modified slide 15.
stage2 = copy.deepcopy(target)
stage2['_variant'] = 'slide14-vertical-flow-stage2'
for key in ('_fr','_en'):
    c = stage2[key]['content']
    c = c.replace('s15-stage1', 's16-stage2')
    # Remove highlighted extension studies entirely.
    for study in ('SOLAR','BRAUD','BRAUDOLF'):
        c = re.sub(r'<span data-study="%s">%s</span>' % (study, study), '', c)
    # Replace inherited stage-1 opacity rules with stage-2-specific rules.
    c = re.sub(
        r'<style>\n\.s16-stage2 \.v16-pills span\[data-study\]\{opacity:\.42\}\n\.s16-stage2 \.v16-pills span\[data-study="SOLAR"\],\n\.s16-stage2 \.v16-pills span\[data-study="BRAUD"\],\n\.s16-stage2 \.v16-pills span\[data-study="BRAUDOLF"\]\{opacity:1\}\n</style>',
        '<style>\n.s16-stage2 .v16-pills span[data-study]{opacity:.42}\n.s16-stage2 .v16-pills span[data-study="TWIXAV"],\n.s16-stage2 .v16-pills span[data-study="VIBEX"]{opacity:.24}\n</style>',
        c
    )
    stage2[key]['content'] = c
stage2['content'] = stage2['_fr']['content']
stage2['_fr']['notes'] = "Deuxième état : SOLAR, BRAUD et BRAUDOLF sont retirés. TWIXAV et VIBEX sont davantage atténués que SOFT, TWIXOLF et VIBOLF."
stage2['_en']['notes'] = "Second state: SOLAR, BRAUD and BRAUDOLF are removed. TWIXAV and VIBEX are more strongly faded than SOFT, TWIXOLF and VIBOLF."
stage2['notes'] = stage2['_fr']['notes']

# Build stage 3 directly from modified slide 15, as requested.
stage3 = copy.deepcopy(target)
stage3['_variant'] = 'slide14-vertical-flow-stage3'
for key in ('_fr','_en'):
    c = stage3[key]['content']
    c = c.replace('s15-stage1', 's17-stage3')
    for study in ('SOFT','TWIXOLF','SOLAR','VIBOLF','BRAUD','BRAUDOLF'):
        c = re.sub(r'<span data-study="%s">%s</span>' % (study, study), '', c)
    # Stage 3 is a fresh duplicate of slide 15: TWIXAV and VIBEX keep slide-15 fading.
    c = re.sub(
        r'<style>\n\.s17-stage3 \.v16-pills span\[data-study\]\{opacity:\.42\}\n\.s17-stage3 \.v16-pills span\[data-study="SOLAR"\],\n\.s17-stage3 \.v16-pills span\[data-study="BRAUD"\],\n\.s17-stage3 \.v16-pills span\[data-study="BRAUDOLF"\]\{opacity:1\}\n</style>',
        '<style>\n.s17-stage3 .v16-pills span[data-study]{opacity:.42}\n</style>',
        c
    )
    stage3[key]['content'] = c
stage3['content'] = stage3['_fr']['content']
stage3['_fr']['notes'] = "Troisième état, redérivé de la diapo 15 : seules TWIXAV et VIBEX restent visibles."
stage3['_en']['notes'] = "Third state, duplicated again from slide 15: only TWIXAV and VIBEX remain visible."
stage3['notes'] = stage3['_fr']['notes']

# Insert the two new states immediately after slide 15.
slides[ti+1:ti+1] = [stage2, stage3]

# Validation.
assert slides[ti-1] == orig14
assert 'data-study="SOLAR"' in slides[ti]['_fr']['content']
assert '.s15-stage1 .v16-pills span[data-study]{opacity:.42}' in slides[ti]['_fr']['content']
assert '.s15-stage1 .v16-pills span[data-study="SOLAR"]' in slides[ti]['_fr']['content']
assert 'data-study="SOLAR"' not in slides[ti+1]['_fr']['content']
assert 'data-study="BRAUD"' not in slides[ti+1]['_fr']['content']
assert 'data-study="BRAUDOLF"' not in slides[ti+1]['_fr']['content']
assert '.s16-stage2 .v16-pills span[data-study="TWIXAV"]' in slides[ti+1]['_fr']['content']
assert 'opacity:.24' in slides[ti+1]['_fr']['content']
for study in ('TWIXAV','VIBEX'):
    assert f'data-study="{study}"' in slides[ti+2]['_fr']['content']
for study in ('SOFT','TWIXOLF','SOLAR','VIBOLF','BRAUD','BRAUDOLF'):
    assert f'data-study="{study}"' not in slides[ti+2]['_fr']['content']

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
out = text[:pos] + new_array + text[pos+consumed:]
p.write_text(out, encoding='utf-8')
