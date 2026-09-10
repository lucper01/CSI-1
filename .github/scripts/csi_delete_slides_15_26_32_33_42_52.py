from pathlib import Path
import json

TARGETS = [15, 26, 32, 33, 42, 52]
path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = ['
marker_pos = text.find(marker)
if marker_pos < 0:
    raise SystemExit('slides array not found')
array_open = marker_pos + len(marker) - 1

# Locate top-level slide objects while ignoring braces inside JSON strings.
spans = []
in_string = False
escaped = False
depth = 0
obj_start = None
for i in range(array_open + 1, len(text)):
    ch = text[i]
    if in_string:
        if escaped:
            escaped = False
        elif ch == '\\':
            escaped = True
        elif ch == '"':
            in_string = False
        continue
    if ch == '"':
        in_string = True
        continue
    if ch == '{':
        if depth == 0:
            obj_start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth < 0:
            raise SystemExit('invalid brace structure in slides array')
        if depth == 0 and obj_start is not None:
            spans.append((obj_start, i + 1))
            obj_start = None
    elif ch == ']' and depth == 0:
        break

if len(spans) < max(TARGETS):
    raise SystemExit(f'Only {len(spans)} slide objects found; cannot delete requested slides')

removed = []
for n in TARGETS:
    start, end = spans[n - 1]
    raw = text[start:end]
    try:
        obj = json.loads(raw)
        title = obj.get('title') or obj.get('_fr', {}).get('title') or obj.get('chapter') or '(sans titre)'
        appendix = bool(obj.get('appendix', False))
    except Exception as exc:
        raise SystemExit(f'Could not parse slide {n}: {exc}')
    if appendix:
        raise SystemExit(f'Slide {n} is marked as appendix; aborting to avoid numbering mismatch')
    removed.append((n, title))

# Delete from the end backwards so original positions remain valid.
for n in sorted(TARGETS, reverse=True):
    start, end = spans[n - 1]
    line_start = text.rfind('\n', 0, start) + 1
    p = end
    while p < len(text) and text[p] in ' \t':
        p += 1
    if p < len(text) and text[p] == ',':
        p += 1
        if text[p:p+2] == '\r\n':
            p += 2
        elif p < len(text) and text[p] == '\n':
            p += 1
        text = text[:line_start] + text[p:]
    else:
        # Fallback for a final object: remove the preceding comma and surrounding line whitespace.
        q = line_start - 1
        while q >= 0 and text[q] in ' \t\r\n':
            q -= 1
        if q >= 0 and text[q] == ',':
            text = text[:q] + text[end:]
        else:
            raise SystemExit(f'Could not safely remove slide {n}')

path.write_text(text, encoding='utf-8')
for n, title in removed:
    print(f'Removed slide {n}: {title}')
print(f'Removed {len(removed)} slides total')
