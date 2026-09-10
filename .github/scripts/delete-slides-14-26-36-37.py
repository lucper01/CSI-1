from pathlib import Path
import json

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = ['
start = text.find(marker)
if start < 0:
    raise SystemExit('const slides array not found')
arr_start = text.find('[', start)

# Find the matching closing bracket for the slides array while respecting JS/JSON strings.
in_string = False
escape = False
depth = 0
arr_end = None
for i in range(arr_start, len(text)):
    ch = text[i]
    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == '"':
            in_string = False
        continue
    if ch == '"':
        in_string = True
    elif ch == '[':
        depth += 1
    elif ch == ']':
        depth -= 1
        if depth == 0:
            arr_end = i + 1
            break
if arr_end is None:
    raise SystemExit('slides array closing bracket not found')

arr = text[arr_start:arr_end]

# Locate top-level object spans without reserializing their contents.
spans = []
in_string = False
escape = False
brace = 0
obj_start = None
for i, ch in enumerate(arr):
    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == '"':
            in_string = False
        continue
    if ch == '"':
        in_string = True
    elif ch == '{':
        if brace == 0:
            obj_start = i
        brace += 1
    elif ch == '}':
        brace -= 1
        if brace == 0 and obj_start is not None:
            spans.append((obj_start, i + 1))
            obj_start = None

if not spans:
    raise SystemExit('no slide objects found')

slides = []
for s, e in spans:
    try:
        slides.append(json.loads(arr[s:e]))
    except Exception as exc:
        raise SystemExit(f'failed to parse slide object at {s}:{e}: {exc}')

main_abs = [i for i, slide in enumerate(slides) if not slide.get('appendix', False)]
appendix_before = sum(1 for slide in slides if slide.get('appendix', False))
main_before = len(main_abs)
target_numbers = [14, 26, 36, 37]
if main_before < max(target_numbers):
    raise SystemExit(f'only {main_before} main slides, cannot delete requested positions')

target_abs = {main_abs[n - 1] for n in target_numbers}
print('Main slide count before:', main_before)
for n in target_numbers:
    slide = slides[main_abs[n - 1]]
    print(f'Deleting current main slide {n}: {slide.get("title", "<untitled>")} | chapter={slide.get("chapter", "")}')

kept_indices = [i for i in range(len(slides)) if i not in target_abs]
if len(kept_indices) != len(slides) - 4:
    raise SystemExit('unexpected deletion count')

# Rebuild only the array separators, preserving every kept slide object byte-for-byte.
if len(spans) > 1:
    sep = arr[spans[0][1]:spans[1][0]]
else:
    sep = ',\n'
raw_kept = [arr[spans[i][0]:spans[i][1]] for i in kept_indices]
new_arr = arr[:spans[0][0]] + sep.join(raw_kept) + arr[spans[-1][1]:]
new_text = text[:arr_start] + new_arr + text[arr_end:]
path.write_text(new_text, encoding='utf-8')

# Validate semantic result.
check_text = path.read_text(encoding='utf-8')
cs = check_text.find(marker)
ca = check_text.find('[', cs)
in_string = False
escape = False
depth = 0
ce = None
for i in range(ca, len(check_text)):
    ch = check_text[i]
    if in_string:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == '"':
            in_string = False
        continue
    if ch == '"':
        in_string = True
    elif ch == '[':
        depth += 1
    elif ch == ']':
        depth -= 1
        if depth == 0:
            ce = i + 1
            break
parsed = json.loads(check_text[ca:ce])
main_after = sum(1 for slide in parsed if not slide.get('appendix', False))
appendix_after = sum(1 for slide in parsed if slide.get('appendix', False))
if main_after != main_before - 4:
    raise SystemExit(f'main slide count mismatch: {main_after} vs expected {main_before - 4}')
if appendix_after != appendix_before:
    raise SystemExit('appendix slide count changed unexpectedly')
print('Main slide count after:', main_after)
print('Appendix slide count unchanged:', appendix_after)
