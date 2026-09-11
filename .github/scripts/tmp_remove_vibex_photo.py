from pathlib import Path

p = Path('assets/csi-source-visuals.js')
text = p.read_text(encoding='utf-8')
block = """    if (study === 'vibex' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {\n      add(slideEl, 'landscape', 'photo study-photo', 'vibex');\n    }\n"""
if block not in text:
    raise SystemExit('VIBEX photo block not found')
text = text.replace(block, '', 1)
if "'vibex'" in text and "study === 'vibex'" in text:
    raise SystemExit('Unexpected VIBEX visual rule remains')
p.write_text(text, encoding='utf-8')
print('Removed VIBEX sourced photo rule')
