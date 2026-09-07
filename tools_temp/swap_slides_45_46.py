from pathlib import Path
import json

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

assert len(slides) == 49, f'Expected 49 slides, got {len(slides)}'

def title(s):
    return s.get('title') or s.get('_fr', {}).get('title', '')

assert title(slides[44]) == 'Points à discuter', f"Slide 45 unexpected: {title(slides[44])}"
assert title(slides[45]) == 'Bilan', f"Slide 46 unexpected: {title(slides[45])}"

slides[44], slides[45] = slides[45], slides[44]

assert title(slides[44]) == 'Bilan'
assert title(slides[45]) == 'Points à discuter'

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
p.write_text(text[:start] + new_json + text[end:], encoding='utf-8')
print('OK - slides 45 and 46 swapped: Bilan then Points à discuter')
