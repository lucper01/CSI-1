from pathlib import Path
import re

FILES = [
    Path('assets/results/twixav_empirical_curves.svg'),
    Path('assets/results/twixav_tbw_width.svg'),
    Path('assets/results/vibex_m1_olivia.svg'),
    Path('assets/results/vibex_size_interaction.svg'),
]

text_re = re.compile(r'<text\b[^>]*>.*?</text>', re.DOTALL)
inner_re = re.compile(r'^<text\b[^>]*>(.*?)</text>$', re.DOTALL)

for path in FILES:
    src = path.read_text(encoding='utf-8')
    removed = []

    def repl(match):
        block = match.group(0)
        m = inner_re.match(block)
        inner = m.group(1) if m else ''
        visible = re.sub(r'<[^>]+>', '', inner)
        if re.search(r'\d', visible):
            removed.append(visible.strip())
            return ''
        return block

    out = text_re.sub(repl, src)
    if out == src:
        print(f'{path}: no numeric text labels found')
    else:
        path.write_text(out, encoding='utf-8')
        print(f'{path}: removed {len(removed)} numeric labels')
        print('  ' + ' | '.join(removed[:30]))

# Verify no visible SVG text element contains a digit anymore.
for path in FILES:
    src = path.read_text(encoding='utf-8')
    leftovers = []
    for block in text_re.findall(src):
        m = inner_re.match(block)
        inner = m.group(1) if m else ''
        visible = re.sub(r'<[^>]+>', '', inner)
        if re.search(r'\d', visible):
            leftovers.append(visible.strip())
    if leftovers:
        raise SystemExit(f'{path}: numeric text labels remain: {leftovers}')
    print(f'{path}: verified - no numeric text labels remain')
