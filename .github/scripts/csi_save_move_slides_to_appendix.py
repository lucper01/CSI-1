from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

marker = 'const slides = ['
start = text.find(marker)
if start < 0:
    raise SystemExit('slides array marker not found')
array_start = start + len(marker)

# Find the matching closing bracket of the slides array, respecting strings.
i = array_start
depth = 1
quote = None
escape = False
while i < len(text):
    ch = text[i]
    if quote:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == quote:
            quote = None
    else:
        if ch in ('"', "'", '`'):
            quote = ch
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                array_end = i
                break
    i += 1
else:
    raise SystemExit('slides array end not found')

body = text[array_start:array_end]

# Extract top-level object spans from the array.
objects = []
i = 0
while i < len(body):
    if body[i].isspace() or body[i] == ',':
        i += 1
        continue
    if body[i] != '{':
        raise SystemExit(f'Unexpected token in slides array at offset {i}: {body[i:i+30]!r}')
    obj_start = i
    brace = 0
    quote = None
    escape = False
    while i < len(body):
        ch = body[i]
        if quote:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == quote:
                quote = None
        else:
            if ch in ('"', "'", '`'):
                quote = ch
            elif ch == '{':
                brace += 1
            elif ch == '}':
                brace -= 1
                if brace == 0:
                    i += 1
                    objects.append(body[obj_start:i])
                    break
        i += 1
    else:
        raise SystemExit('Unclosed slide object')

if not objects:
    raise SystemExit('No slide objects parsed')

main_indices = []
appendix_indices = []
for idx, obj in enumerate(objects):
    m = re.search(r'"appendix"\s*:\s*(true|false)', obj)
    if not m:
        raise SystemExit(f'Slide object {idx+1} missing appendix flag')
    (appendix_indices if m.group(1) == 'true' else main_indices).append(idx)

# User numbering refers to the current main presentation before this move.
target_numbers = [26, 36, 40, 41]
if max(target_numbers) > len(main_indices):
    raise SystemExit(f'Only {len(main_indices)} main slides, cannot move {target_numbers}')

target_object_indices = [main_indices[n-1] for n in target_numbers]

# Capture titles for verification.
def title_of(obj):
    m = re.search(r'"title"\s*:\s*"([^"]+)"', obj)
    return m.group(1) if m else '(sans titre)'

print('Main slides before:', len(main_indices))
for n, idx in zip(target_numbers, target_object_indices):
    print(f'Moving slide {n}: {title_of(objects[idx])}')

moved = []
remaining = []
target_set = set(target_object_indices)
for idx, obj in enumerate(objects):
    if idx in target_set:
        count = len(re.findall(r'"appendix"\s*:\s*false', obj))
        if count != 1:
            raise SystemExit(f'Slide target {idx+1} has {count} appendix:false flags')
        obj = re.sub(r'"appendix"\s*:\s*false', '"appendix": true', obj, count=1)
        moved.append(obj)
    else:
        remaining.append(obj)

# Keep all existing slides in their relative order and append moved slides to the annexes block.
new_objects = remaining + moved
new_body = '\n  ' + ',\n  '.join(obj.strip() for obj in new_objects) + '\n'
new_text = text[:array_start] + new_body + text[array_end:]

# Sanity checks.
if new_text == text:
    raise SystemExit('No changes produced')
main_after = len(main_indices) - len(target_numbers)
print('Expected main slides after:', main_after)
print('Moved to appendix:', len(moved))

path.write_text(new_text, encoding='utf-8')
