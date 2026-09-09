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

for key in ('content',):
    s[key] = s[key].replace('<b>1 communication</b>', '<b>1 talk</b>')
for langkey in ('_fr','_en'):
    s[langkey]['content'] = s[langkey]['content'].replace('<b>1 communication</b>', '<b>1 talk</b>')

assert '<b>1 talk</b>' in s['content']
assert '<b>1 talk</b>' in s['_fr']['content']
assert '<b>1 talk</b>' in s['_en']['content']

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
index.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before
