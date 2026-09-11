from pathlib import Path

index = Path('index.html')
visuals = Path('assets/csi-source-visuals.js')

html = index.read_text(encoding='utf-8')
js = visuals.read_text(encoding='utf-8')

old_src = 'assets/csi-source-visuals.js?v=1'
new_src = 'assets/csi-source-visuals.js?v=2'
if old_src not in html and new_src not in html:
    raise SystemExit('visual runtime script tag not found')
html = html.replace(old_src, new_src)

js = js.replace("const MARK = 'csi-source-visuals-v1';", "const MARK = 'csi-source-visuals-v2';")

landscape_line = "    landscape: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Lake_Mountain_Landscape.jpg/1280px-Lake_Mountain_Landscape.jpg', fr:'Paysage naturel', en:'Natural landscape', source:'Bonnie Moreland - CC0'}\n"
if landscape_line in js:
    js = js.replace(landscape_line, '')
    js = js.replace("    microphone: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/FEMA_-_39463_-_Microphones_at_the_podium.jpg/960px-FEMA_-_39463_-_Microphones_at_the_podium.jpg', fr:'Microphones de conférence', en:'Conference microphones', source:'Bill Koplitz/FEMA - domaine public'},\n  };",
                    "    microphone: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/FEMA_-_39463_-_Microphones_at_the_podium.jpg/960px-FEMA_-_39463_-_Microphones_at_the_podium.jpg', fr:'Microphones de conférence', en:'Conference microphones', source:'Bill Koplitz/FEMA - domaine public'}\n  };")

needle = "  function decorate(slideEl) {\n"
helper = """  function purgeLegacyStudyLandscape(slideEl) {\n    if (!slideEl) return;\n    const index = Number(slideEl.dataset.index);\n    if (!Number.isInteger(index)) return;\n    const study = norm(metaFor(index).study);\n    if (study === 'vibex' || study === 'vibolf') {\n      slideEl.querySelectorAll('.csi-source-visual[data-asset=\\\"landscape\\\"], .csi-source-visual[data-slot=\\\"vibex\\\"], .csi-source-visual[data-slot=\\\"vibolf-landscape\\\"]').forEach(node => node.remove());\n    }\n  }\n\n"""
if 'function purgeLegacyStudyLandscape' not in js:
    if needle not in js:
        raise SystemExit('decorate function not found')
    js = js.replace(needle, helper + needle, 1)

old_refresh = "  function refresh() { document.querySelectorAll('#deck .slide[data-index]').forEach(decorate); }"
new_refresh = "  function refresh() { document.querySelectorAll('#deck .slide[data-index]').forEach(slideEl => { purgeLegacyStudyLandscape(slideEl); decorate(slideEl); }); }"
if old_refresh in js:
    js = js.replace(old_refresh, new_refresh, 1)
elif new_refresh not in js:
    raise SystemExit('refresh function not found')

for forbidden in ["add(slideEl, 'landscape'", "vibolf-landscape", "data-slot=\\\"vibex\\\""]:
    if forbidden == "vibolf-landscape":
        # allowed only in the purge selector, nowhere as an add() call
        if "add(slideEl, 'landscape'" in js:
            raise SystemExit('landscape injection still present')
    elif forbidden.startswith("add") and forbidden in js:
        raise SystemExit('landscape injection still present')

if new_src not in html:
    raise SystemExit('cache-busted source not written')

index.write_text(html, encoding='utf-8')
visuals.write_text(js, encoding='utf-8')
print('Purged VIBEX/VIBOLF landscape injection and bumped runtime to v2')
