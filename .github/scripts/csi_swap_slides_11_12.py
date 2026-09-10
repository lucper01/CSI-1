from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = ['
start = text.find(marker)
if start < 0:
    raise SystemExit('slides array not found')
arr_start = text.find('[', start)

spans = []
depth = 0
obj_start = None
in_string = False
quote = ''
escape = False
i = arr_start + 1
while i < len(text):
    ch = text[i]
    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == quote:
            in_string = False
        i += 1
        continue
    if ch in ('"', "'", '`'):
        in_string = True
        quote = ch
        i += 1
        continue
    if ch == '{':
        if depth == 0:
            obj_start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0 and obj_start is not None:
            spans.append((obj_start, i + 1))
            obj_start = None
    elif ch == ']' and depth == 0:
        break
    i += 1

if len(spans) < 12:
    raise SystemExit(f'Only {len(spans)} slides found')

a1, a2 = spans[10]
b1, b2 = spans[11]
obj11 = text[a1:a2]
obj12 = text[b1:b2]
between = text[a2:b1]

def title(obj):
    m = re.search(r'"title"\s*:\s*"((?:\\.|[^"\\])*)"', obj)
    return m.group(1) if m else '(untitled)'

print('Before swap:')
print('11:', title(obj11))
print('12:', title(obj12))

text = text[:a1] + obj12 + between + obj11 + text[b2:]
path.write_text(text, encoding='utf-8')
print('After swap:')
print('11:', title(obj12))
print('12:', title(obj11))
