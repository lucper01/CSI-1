# rerun trigger
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

before_count = len(slides)
assert before_count >= 48, before_count

# Remove current 1-based slides 46 and 48.
# Remove in descending order so the original numbering remains valid.
for idx in sorted([46, 48], reverse=True):
    del slides[idx - 1]

removed_tokens = {'SORBET', 'COBEX'}

def clean_cards(html):
    if not isinstance(html, str):
        return html
    for token in sorted(removed_tokens):
        html = re.sub(r'<article\b(?=[^>]*data-study=["\']' + token + r'["\'])[\s\S]*?</article>', '', html)
        html = re.sub(r'<div\b(?=[^>]*data-study=["\']' + token + r'["\'])[\s\S]*?</div>', '', html)
        html = re.sub(r'<span\b(?=[^>]*data-study=["\']' + token + r'["\'])[\s\S]*?</span>', '', html)
        html = re.sub(r'<button\b(?=[^>]*data-study=["\']' + token + r'["\'])[\s\S]*?</button>', '', html)
        html = re.sub(r'<article\b[\s\S]*?' + token + r'[\s\S]*?</article>', '', html)
    html = html.replace('SORBET · ', '').replace(' · SORBET', '').replace('SORBET', '')
    html = html.replace('COBEX · ', '').replace(' · COBEX', '').replace('COBEX', '')
    html = re.sub(r'\s{2,}', ' ', html)
    return html

slide45 = slides[44]
for key in ('content', 'lead', 'title', 'kicker', 'notes'):
    if key in slide45:
        slide45[key] = clean_cards(slide45[key])
for lang_key in ('_fr', '_en'):
    d = slide45.get(lang_key)
    if isinstance(d, dict):
        for key in ('content', 'lead', 'title', 'kicker', 'notes'):
            if key in d:
                d[key] = clean_cards(d[key])

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

old = """  if(n>=44&&n<=51){
    return {steps:E?['MAP','SOLAR','SORBET','COBEX','BRAUD','BRAUDOLF','ACTIVITIES']:['CARTE','SOLAR','SORBET','COBEX','BRAUD','BRAUDOLF','ACTIVITÉS'],active:Math.min(n-44,6)};
  }
  if(n>=52&&n<=54){
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active:n-52};
  }
  if(n>=55&&n<=57){
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active:n-55};
  }"""
new = """  if(n>=44&&n<=49){
    return {steps:E?['MAP','SOLAR','BRAUD','BRAUDOLF','ACTIVITIES']:['CARTE','SOLAR','BRAUD','BRAUDOLF','ACTIVITÉS'],active:Math.min(n-44,4)};
  }
  if(n>=50&&n<=52){
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active:n-50};
  }
  if(n>=53&&n<=55){
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active:n-53};
  }"""
if old in text:
    text = text.replace(old, new, 1)
else:
    text = text.replace("if(n>=44&&n<=51)", "if(n>=44&&n<=49)", 1)
    text = text.replace("if(n>=52&&n<=54)", "if(n>=50&&n<=52)", 1)
    text = text.replace("active:n-52", "active:n-50", 1)
    text = text.replace("if(n>=55&&n<=57)", "if(n>=53&&n<=55)", 1)
    text = text.replace("active:n-55", "active:n-53", 1)
    text = text.replace("'SORBET',", "")
    text = text.replace("'COBEX',", "")
    text = text.replace(",'SORBET'", "")
    text = text.replace(",'COBEX'", "")

assert len(slides) == before_count - 2, (before_count, len(slides))
slide45_json = json.dumps(slides[44], ensure_ascii=False)
assert 'SORBET' not in slide45_json
assert 'COBEX' not in slide45_json
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_hash_before
path.write_text(text, encoding='utf-8')
