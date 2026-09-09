from pathlib import Path
import json
import re
import hashlib

path = Path('index.html')
save = Path('index_save.html')
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
text = path.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end
removed = {'SORBET', 'COBEX'}

def slide_is_removed(slide):
    candidates = [slide.get('study',''), slide.get('title',''), slide.get('kicker','')]
    for lang in ('_fr', '_en'):
        d = slide.get(lang) or {}
        candidates += [d.get('study',''), d.get('title',''), d.get('kicker','')]
    return any(str(x).strip().upper() in removed for x in candidates)

def clean_value(v):
    if not isinstance(v, str):
        return v
    for token in removed:
        v = re.sub(r'<article\b[^>]*data-study="' + token + r'"[^>]*>[\s\S]*?</article>', '', v)
        v = re.sub(r'<span\b[^>]*data-study="' + token + r'"[^>]*>[\s\S]*?</span>', '', v)
        v = re.sub(r'<button\b[^>]*data-apparatus-study="' + token + r'"[^>]*>[\s\S]*?</button>', '', v)
        for old in [
            ' et ' + token, ' and ' + token,
            token + ' et ', token + ' and ',
            ', ' + token, token + ', ',
            ' - ' + token, ' · ' + token, ' / ' + token,
            '; ' + token, token
        ]:
            v = v.replace(old, '')
    v = re.sub(r'\s+([,.;:])', r'\1', v)
    v = re.sub(r'\s{2,}', ' ', v)
    return v.strip()

new_slides = []
for slide in slides:
    if slide_is_removed(slide):
        continue
    for key, value in list(slide.items()):
        if key in ('section','kicker','title','lead','content','notes','chapter','study'):
            slide[key] = clean_value(value)
    for lang in ('_fr','_en'):
        d = slide.get(lang)
        if isinstance(d, dict):
            for key, value in list(d.items()):
                if key in ('section','kicker','title','lead','content','notes','chapter','study'):
                    d[key] = clean_value(value)
    new_slides.append(slide)

# Remove empty extension-map artifacts and clean text outside slide JSON only after reinsertion.
new_json = json.dumps(new_slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

old = """  if(n>=52&&n<=54){
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active:n-52};
  }
  if(n>=55&&n<=57){
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active:n-55};
  }"""
new = """  if(n>=50&&n<=52){
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active:n-50};
  }
  if(n>=53&&n<=55){
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active:n-53};
  }"""
if old in text:
    text = text.replace(old, new, 1)

# Remove residual visible tokens everywhere in index.html.
text = text.replace('SORBET', '').replace('COBEX', '')
text = re.sub(r'>\s+<', '><', text)

assert 'SORBET' not in text
assert 'COBEX' not in text
assert len(new_slides) == len(slides) - 2, (len(slides), len(new_slides))
assert 'SOLAR' in text and 'BRAUD' in text and 'BRAUDOLF' in text
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
path.write_text(text, encoding='utf-8')
