from pathlib import Path
import json
import re
import hashlib

path = Path('index.html')
save = Path('index_save.html')
save_hash_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = path.read_text(encoding='utf-8')

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

before_count = len(slides)
assert before_count >= 30, before_count
removed = slides.pop(29)
removed_title = str(removed.get('title', ''))
removed_fr_title = str((removed.get('_fr') or {}).get('title', ''))
removed_en_title = str((removed.get('_en') or {}).get('title', ''))

# Rebuild the slide JSON only; no style/content changes on other slides.
new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

# After deleting slide 30, any part-timeline hard-coded reference at or after 30
# must move back by one slide. Keep the earlier sections unchanged.
def shift_num(match):
    n = int(match.group(1))
    return f'n>={n-1}' if n >= 30 else match.group(0)

def shift_le(match):
    n = int(match.group(1))
    return f'n<={n-1}' if n >= 30 else match.group(0)

def shift_active(match):
    n = int(match.group(1))
    return f'active:n-{n-1}' if n >= 30 else match.group(0)

text = re.sub(r'n>=(\d+)', shift_num, text)
text = re.sub(r'n<=(\d+)', shift_le, text)
text = re.sub(r'active:n-(\d+)', shift_active, text)
# Handles compact forms such as active:Math.min(n-44,4)
def shift_mathmin(match):
    n = int(match.group(1))
    rest = match.group(2)
    return f'active:Math.min(n-{n-1},{rest})' if n >= 30 else match.group(0)
text = re.sub(r'active:Math\.min\(n-(\d+),([^\)]+)\)', shift_mathmin, text)

assert len(slides) == before_count - 1, (before_count, len(slides))
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_hash_before
path.write_text(text, encoding='utf-8')
print(f'Deleted slide 30: {removed_title or removed_fr_title or removed_en_title}')
