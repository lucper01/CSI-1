from pathlib import Path
import json

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = ['
start = text.find(marker)
if start < 0:
    raise SystemExit('const slides array not found')
arr_start = text.find('[', start)

# Find matching closing bracket for slides array.
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

slides = json.loads(text[arr_start:arr_end])
main_abs = [i for i, s in enumerate(slides) if not s.get('appendix', False)]
if len(main_abs) < 34:
    raise SystemExit(f'Only {len(main_abs)} main slides found')

# Resolve all positions before deletion to avoid renumbering ambiguity.
target_positions = [14, 25, 34]
target_abs = [main_abs[n-1] for n in target_positions]
delete_abs = main_abs[12]  # current main slide 13

fr_lead = "La thèse s'organise autour de deux axes complémentaires"
en_lead = "The thesis is organized around two complementary axes"

for n, idx in zip(target_positions, target_abs):
    s = slides[idx]
    print(f'Updating current main slide {n}: title={s.get("title", "")} variant={s.get("_variant", "")}')
    # These are the staged two-axis slides; update only their description/lead.
    s['lead'] = fr_lead
    if isinstance(s.get('_fr'), dict):
        s['_fr']['lead'] = fr_lead
    if isinstance(s.get('_en'), dict):
        s['_en']['lead'] = en_lead

print(f'Deleting current main slide 13: title={slides[delete_abs].get("title", "")} variant={slides[delete_abs].get("_variant", "")}')
del slides[delete_abs]

# Serialize the array cleanly; only index.html is touched.
new_arr = json.dumps(slides, ensure_ascii=False, indent=2)
new_text = text[:arr_start] + new_arr + text[arr_end:]
path.write_text(new_text, encoding='utf-8')

# Validate result semantically.
check = path.read_text(encoding='utf-8')
cs = check.find(marker)
ca = check.find('[', cs)
in_string = False
escape = False
depth = 0
ce = None
for i in range(ca, len(check)):
    ch = check[i]
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
parsed = json.loads(check[ca:ce])
main_after = [s for s in parsed if not s.get('appendix', False)]
if len(main_after) != len(main_abs) - 1:
    raise SystemExit('main slide count did not decrease by exactly one')

# Former current slides 14,25,34 are now 13,24,33 after deleting current slide 13.
for pos in [13, 24, 33]:
    s = main_after[pos-1]
    if s.get('lead') != fr_lead:
        raise SystemExit(f'FR lead mismatch on new main slide {pos}')
    if isinstance(s.get('_fr'), dict) and s['_fr'].get('lead') != fr_lead:
        raise SystemExit(f'_fr lead mismatch on new main slide {pos}')
    if isinstance(s.get('_en'), dict) and s['_en'].get('lead') != en_lead:
        raise SystemExit(f'_en lead mismatch on new main slide {pos}')
print('Validation passed. Main slides:', len(main_after))
