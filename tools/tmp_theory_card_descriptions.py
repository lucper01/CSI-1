from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import json, re

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')

MARKER = 'CSI_THEORY_CARD_DESCRIPTIONS_TO_NOTES_V1'
if MARKER in text:
    raise SystemExit('Patch already applied')

# Extract the JSON-compatible slides array from the JavaScript source.
needle = 'const slides = ['
start = text.find(needle)
if start < 0:
    raise SystemExit('slides array not found')
arr_start = text.find('[', start)

def find_matching_array(src, pos):
    depth = 0
    in_str = False
    esc = False
    quote = ''
    for i in range(pos, len(src)):
        ch = src[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError('Unclosed slides array')

arr_end = find_matching_array(text, arr_start)
slides = json.loads(text[arr_start:arr_end+1])

# The theoretical section is everything before the first Year 1 / Première année divider.
def norm(s):
    return str(s or '').lower()

boundary = None
for i, s in enumerate(slides):
    if not s.get('divider'):
        continue
    hay = ' '.join(norm(s.get(k)) for k in ('title','chapter','section','kicker'))
    if ('première année' in hay or 'premiere annee' in hay or 'year 1' in hay or 'first year' in hay):
        boundary = i
        break
if boundary is None:
    for i, s in enumerate(slides):
        hay = ' '.join(norm(s.get(k)) for k in ('chapter','section','kicker','title'))
        if 'année 1' in hay or 'annee 1' in hay or 'première année' in hay or 'year 1' in hay:
            boundary = i
            break
if boundary is None:
    raise SystemExit('Could not determine theoretical section boundary')

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class CardParagraphStripper(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.stack = []
        self.target_depth = 0
        self.suppress_stack = None
        self.capture = []
        self.removed = []

    def _is_card(self, attrs):
        cls = ''
        for k, v in attrs:
            if k == 'class' and v:
                cls = v
                break
        tokens = cls.split()
        return any(t == 'card' or t.endswith('-card') for t in tokens)

    def handle_starttag(self, tag, attrs):
        tl = tag.lower()
        if self.suppress_stack is not None:
            if tl not in VOID:
                self.suppress_stack.append(tl)
            if tl == 'br':
                self.capture.append(' ')
            return
        if tl == 'p' and self.target_depth > 0:
            self.suppress_stack = ['p']
            self.capture = []
            return
        self.out.append(self.get_starttag_text())
        if tl not in VOID:
            target = self._is_card(attrs)
            self.stack.append((tl, target))
            if target:
                self.target_depth += 1

    def handle_startendtag(self, tag, attrs):
        if self.suppress_stack is not None:
            if tag.lower() == 'br':
                self.capture.append(' ')
            return
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        tl = tag.lower()
        if self.suppress_stack is not None:
            if tl in self.suppress_stack:
                # Pop through the matching tag, tolerant of simple malformed fragments.
                while self.suppress_stack:
                    x = self.suppress_stack.pop()
                    if x == tl:
                        break
            if not self.suppress_stack:
                clean = re.sub(r'\s+', ' ', unescape(''.join(self.capture))).strip()
                if clean:
                    self.removed.append(clean)
                self.suppress_stack = None
                self.capture = []
            return
        self.out.append(f'</{tag}>')
        if self.stack:
            # HTML fragments in this deck are well formed; pop the latest matching element.
            for j in range(len(self.stack)-1, -1, -1):
                if self.stack[j][0] == tl:
                    popped = self.stack[j:]
                    self.stack = self.stack[:j]
                    for _, target in popped:
                        if target:
                            self.target_depth -= 1
                    break

    def handle_data(self, data):
        if self.suppress_stack is not None:
            self.capture.append(data)
        else:
            self.out.append(data)

    def handle_entityref(self, name):
        raw = f'&{name};'
        if self.suppress_stack is not None:
            self.capture.append(raw)
        else:
            self.out.append(raw)

    def handle_charref(self, name):
        raw = f'&#{name};'
        if self.suppress_stack is not None:
            self.capture.append(raw)
        else:
            self.out.append(raw)

    def handle_comment(self, data):
        if self.suppress_stack is None:
            self.out.append(f'<!--{data}-->')

    def unknown_decl(self, data):
        if self.suppress_stack is None:
            self.out.append(f'<![{data}]>')


def strip_card_paragraphs(html):
    if not html or '<p' not in html.lower() or 'card' not in html.lower():
        return html, []
    p = CardParagraphStripper()
    p.feed(html)
    p.close()
    return ''.join(p.out), p.removed


def append_notes(notes, removed, english=False):
    if not removed:
        return notes or ''
    prefix = 'Card details kept for speaker notes:' if english else 'Détails des cartes conservés pour les notes orateur :'
    block = prefix + '\n' + '\n'.join(f'- {x}' for x in removed)
    base = (notes or '').strip()
    if block in base:
        return base
    return (base + '\n\n' + block).strip() if base else block

changed_slides = 0
removed_total = 0
for i in range(boundary):
    s = slides[i]
    slide_changed = False
    # Top-level content is the active/default language and is kept in sync too.
    for key, english in ((None, False), ('_fr', False), ('_en', True)):
        obj = s if key is None else s.get(key)
        if not isinstance(obj, dict):
            continue
        old = obj.get('content')
        if not isinstance(old, str):
            continue
        new, removed = strip_card_paragraphs(old)
        if removed:
            obj['content'] = new
            obj['notes'] = append_notes(obj.get('notes',''), removed, english=english)
            removed_total += len(removed)
            slide_changed = True
    if slide_changed:
        s['_theory_cards_compacted'] = True
        changed_slides += 1

if changed_slides == 0 or removed_total == 0:
    raise SystemExit('No theoretical card descriptions found to move')

# Add a harmless source marker outside the data model for rerun safety.
new_array = json.dumps(slides, ensure_ascii=False, indent=2)
patched = text[:arr_start] + new_array + text[arr_end+1:]
marker = f'\n<!-- {MARKER}: {changed_slides} slides, {removed_total} card descriptions moved to speaker notes -->\n'
patched = patched.replace('</body>', marker + '</body>', 1)
PATH.write_text(patched, encoding='utf-8')
print(f'Theoretical boundary: slide {boundary+1}; changed slides: {changed_slides}; moved descriptions: {removed_total}')
