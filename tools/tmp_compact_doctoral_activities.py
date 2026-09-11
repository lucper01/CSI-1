from pathlib import Path
import json, re, html

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
marker = 'const slides = ['
start = text.index(marker) + len('const slides = ')

# Find the end of the JSON-compatible slides array while respecting quoted strings.
i = start
depth = 0
in_str = False
esc = False
end = None
while i < len(text):
    ch = text[i]
    if in_str:
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif ch == '"':
            in_str = False
    else:
        if ch == '"':
            in_str = True
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    i += 1
if end is None:
    raise SystemExit('Could not locate end of slides array')

slides = json.loads(text[start:end])

TAG_RE = re.compile(r'<[^>]+>')
P_RE = re.compile(r'<p\b[^>]*>(.*?)</p>', re.I | re.S)


def clean_html(fragment):
    value = TAG_RE.sub(' ', fragment)
    value = html.unescape(value)
    return re.sub(r'\s+', ' ', value).strip()


def is_activity_title(title):
    t = str(title or '').lower()
    return ('activités doctorales' in t or 'activites doctorales' in t or 'doctoral activities' in t)


def compact_payload(payload, english=False):
    if not isinstance(payload, dict):
        return 0
    content = str(payload.get('content') or '')
    if not content:
        return 0
    found = P_RE.findall(content)
    details = [clean_html(x) for x in found]
    details = [x for x in details if x]
    if not details:
        return 0

    # Activity slides are overview slides: keep figures, headings and keywords only.
    payload['content'] = P_RE.sub('', content)

    notes = str(payload.get('notes') or '').strip()
    marker_text = 'Card details kept for speaker notes:' if english else 'Détails des cartes conservés pour les notes orateur :'
    if marker_text not in notes:
        block = marker_text + '\n' + '\n'.join('- ' + x for x in details)
        payload['notes'] = (notes + '\n\n' + block).strip() if notes else block
    return len(details)

matched = 0
removed = 0
for slide in slides:
    if not isinstance(slide, dict):
        continue
    root_match = is_activity_title(slide.get('title'))
    en = slide.get('_en') if isinstance(slide.get('_en'), dict) else None
    en_match = is_activity_title(en.get('title')) if en else False
    if not (root_match or en_match):
        continue
    matched += 1
    removed += compact_payload(slide, english=False)
    if en:
        removed += compact_payload(en, english=True)
    slide['_activities_cards_compacted'] = True

if matched < 3:
    raise SystemExit(f'Expected at least 3 doctoral activity slides, found {matched}')
if removed == 0:
    raise SystemExit('No activity detail paragraphs were removed')

serialized = json.dumps(slides, ensure_ascii=False, indent=2)
new_text = text[:start] + serialized + text[end:]
comment = f'<!-- CSI_DOCTORAL_ACTIVITIES_COMPACT_V1: {matched} slides, {removed} detail paragraphs moved to speaker notes -->'
if 'CSI_DOCTORAL_ACTIVITIES_COMPACT_V1' not in new_text:
    new_text = new_text.replace('</body>', comment + '\n</body>')
PATH.write_text(new_text, encoding='utf-8')
print(f'Compacted {matched} doctoral activity slides; moved {removed} detail paragraphs to speaker notes.')
