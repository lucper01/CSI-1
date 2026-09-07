from pathlib import Path
import json,re

p=Path('index.html')
text=p.read_text(encoding='utf-8')
marker='const slides = '
start=text.index(marker)+len(marker)
slides,rel_end=json.JSONDecoder().raw_decode(text[start:])
end=start+rel_end

pairs=[
    ('TWIXAV','TWIXAV - pourquoi commencer par une fenêtre temporelle audiovisuelle ?','TWIXAV - Méthode','twixav'),
    ('VIBEX','VIBEX - pourquoi établir une référence visuelle ?','VIBEX - Méthode','vibex'),
]

def title(s):
    return s.get('title') or s.get('_fr',{}).get('title','')

def move_one(src,dst,key,demo_id):
    if key not in src or key not in dst:
        return
    c=src[key]
    pat=re.compile(r'<button class="study-demo-launch"[^>]*data-demo-open="'+re.escape(demo_id)+r'".*?</button>',re.S)
    m=pat.search(c)
    if not m:
        return
    button=m.group(0)
    src[key]=c[:m.start()]+c[m.end():]
    if f'data-demo-open="{demo_id}"' in dst[key]:
        return
    target=dst[key]
    anchors=['<div class="study-floating','<div class="float-card']
    pos=-1
    for a in anchors:
        q=target.find(a)
        if q!=-1:
            pos=q
            break
    spacer='<div class="method-demo-wrap">'+button+'</div>'
    dst[key]=target[:pos]+spacer+target[pos:] if pos!=-1 else target+spacer

for study,intro_title,method_title,demo_id in pairs:
    src=next(s for s in slides if title(s)==intro_title)
    dst=next(s for s in slides if title(s)==method_title)
    move_one(src,dst,'content',demo_id)
    for loc in ('_fr','_en'):
        if loc in src and loc in dst:
            move_one(src[loc],dst[loc],'content',demo_id)

new_json=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
text=text[:start]+new_json+text[end:]

css='''\n/* Interactive paradigms on methodology slides */\n.method-demo-wrap{margin-top:14px;display:flex;justify-content:flex-start}\n.method-demo-wrap .study-demo-launch{margin:0;max-width:520px;width:min(100%,520px)}\n@media(max-width:900px){.method-demo-wrap .study-demo-launch{max-width:none;width:100%}}\n'''
if '/* Interactive paradigms on methodology slides */' not in text:
    text=text.replace('</style>',css+'\n</style>',1)

p.write_text(text,encoding='utf-8')

out=p.read_text(encoding='utf-8')
assert 'VIBEX - Méthode' in out and 'TWIXAV - Méthode' in out
start2=out.index(marker)+len(marker)
slides2,_=json.JSONDecoder().raw_decode(out[start2:])
for study,intro_title,method_title,demo_id in pairs:
    src=next(s for s in slides2 if title(s)==intro_title)
    dst=next(s for s in slides2 if title(s)==method_title)
    for holder in [src,src.get('_fr',{}),src.get('_en',{})]:
        if holder.get('content') is not None:
            assert f'data-demo-open="{demo_id}"' not in holder['content']
    for holder in [dst,dst.get('_fr',{}),dst.get('_en',{})]:
        if holder.get('content') is not None:
            assert f'data-demo-open="{demo_id}"' in holder['content']
print('OK - demos moved to method slides')
