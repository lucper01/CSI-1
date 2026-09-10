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

assert len(slides) >= 51, len(slides)
removed = ('SORBET', 'COBEX')

def compact(html: str) -> str:
    html = re.sub(r'\s{2,}', ' ', html)
    html = re.sub(r'\s+([,;:])', r'\1', html)
    html = re.sub(r'([,;:])\s*([,;:])', r'\1', html)
    return html.strip()

def remove_token_elements(html):
    if not isinstance(html, str) or not html:
        return html
    original = html
    for token in removed:
        # Tagged elements, usually study cards/buttons/nodes.
        for tag in ('article', 'button', 'span', 'div', 'li', 'a'):
            html = re.sub(
                rf'<{tag}\b(?=[^>]*(?:data-study|data-target|data-apparatus-study|data-slide|aria-label)=["\'][^"\']*{token}[^"\']*["\'])[^>]*>[\s\S]*?</{tag}>',
                '',
                html,
                flags=re.IGNORECASE,
            )
        # Untagged buttons/pills/cards/list items containing the removed study.
        for tag in ('button', 'article', 'li'):
            html = re.sub(rf'<{tag}\b[^>]*>[\s\S]*?{token}[\s\S]*?</{tag}>', '', html, flags=re.IGNORECASE)
        # Compact card-like divs/spans containing only short labels around the token.
        html = re.sub(rf'<span\b[^>]*>[^<]{{0,80}}{token}[^<]{{0,80}}</span>', '', html, flags=re.IGNORECASE)
        html = re.sub(rf'<div\b[^>]*(?:class=["\'][^"\']*(?:chip|pill|badge|node|mini|tag|study|project)[^"\']*["\'])[^>]*>[\s\S]*?{token}[\s\S]*?</div>', '', html, flags=re.IGNORECASE)
        # Separators in inline button rows.
        html = html.replace(f' · {token}', '')
        html = html.replace(f'{token} · ', '')
        html = html.replace(f' / {token}', '')
        html = html.replace(f'{token} / ', '')
        html = html.replace(f', {token}', '')
        html = html.replace(f'{token}, ', '')
    html = compact(html)
    return html if html != original else original

for slide_number in (14, 51):
    slide = slides[slide_number - 1]
    for key in ('content', 'lead', 'notes'):
        if key in slide:
            slide[key] = remove_token_elements(slide[key])
    for lang_key in ('_fr', '_en'):
        d = slide.get(lang_key)
        if isinstance(d, dict):
            for key in ('content', 'lead', 'notes'):
                if key in d:
                    d[key] = remove_token_elements(d[key])

# Verification: the targeted slides must no longer display SORBET/COBEX.
for slide_number in (14, 51):
    dump = json.dumps(slides[slide_number - 1], ensure_ascii=False)
    assert 'SORBET' not in dump, f'SORBET still present on slide {slide_number}'
    assert 'COBEX' not in dump, f'COBEX still present on slide {slide_number}'

assert hashlib.sha256(save.read_bytes()).hexdigest() == save_hash_before, 'index_save.html changed unexpectedly'

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]
path.write_text(text, encoding='utf-8')
