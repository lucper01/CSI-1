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

def insert_button(dst,key,demo_id,button):
    if key not in dst or f'data-demo-open="{demo_id}"' in dst[key]:
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

def move_one(src,dst,key,demo_id):
    if key not in src or key not in dst:
        return None
    c=src[key]
    pat=re.compile(r'<button class="study-demo-launch"[^>]*data-demo-open="'+re.escape(demo_id)+r'".*?</button>',re.S)
    m=pat.search(c)
    if not m:
        return None
    button=m.group(0)
    src[key]=c[:m.start()]+c[m.end():]
    insert_button(dst,key,demo_id,button)
    return button

english_buttons={
 'twixav':'<button class="study-demo-launch" type="button" data-demo-open="twixav" style="--demo-study:#2f6f9f"><span class="demo-launch-kicker">INTERACTIVE PARADIGM</span><strong>Run a TWIXAV demonstration</strong><span>3 trials - 50, 150 and 250 ms - one different SOA per duration</span><i>Click to enlarge</i></button>',
 'vibex':'<button class="study-demo-launch" type="button" data-demo-open="vibex" style="--demo-study:#2f7d5a"><span class="demo-launch-kicker">INTERACTIVE PARADIGM</span><strong>Run a VIBEX trial</strong><span>Fixation 300 ms - S image 200 ms - mask 1000 ms - L image 200 ms</span><i>Click to enlarge</i></button>'
}

for study,intro_title,method_title,demo_id in pairs:
    src=next(s for s in slides if title(s)==intro_title)
    dst=next(s for s in slides if title(s)==method_title)
    move_one(src,dst,'content',demo_id)
    if '_fr' in src and '_fr' in dst:
        move_one(src['_fr'],dst['_fr'],'content',demo_id)
    if '_en' in dst:
        if '_en' in src:
            move_one(src['_en'],dst['_en'],'content',demo_id)
        insert_button(dst['_en'],'content',demo_id,english_buttons[demo_id])

# Refresh VIBEX launch wording now that the supplied stimuli are integrated.
for s in slides:
    if title(s)=='VIBEX - Méthode':
        for holder in [s,s.get('_fr',{})]:
            if holder.get('content'):
                holder['content']=holder['content'].replace('Fixation 300 ms - image 200 ms - masque 1000 ms - image 200 ms','Fixation 300 ms - image S 200 ms - masque 1000 ms - image L 200 ms').replace('Les deux images définitives seront intégrées à réception','Cliquer pour agrandir')

new_json=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
text=text[:start]+new_json+text[end:]

css='''\n/* Interactive paradigms on methodology slides */\n.method-demo-wrap{margin-top:14px;display:flex;justify-content:flex-start}\n.method-demo-wrap .study-demo-launch{margin:0;max-width:520px;width:min(100%,520px)}\n@media(max-width:900px){.method-demo-wrap .study-demo-launch{max-width:none;width:100%}}\n'''
if '/* Interactive paradigms on methodology slides */' not in text:
    text=text.replace('</style>',css+'\n</style>',1)

p.write_text(text,encoding='utf-8')

out=p.read_text(encoding='utf-8')
start2=out.index(marker)+len(marker)
slides2,_=json.JSONDecoder().raw_decode(out[start2:])
for study,intro_title,method_title,demo_id in pairs:
    src=next(s for s in slides2 if title(s)==intro_title)
    dst=next(s for s in slides2 if title(s)==method_title)
    for holder in [src,src.get('_fr',{}),src.get('_en',{})]:
        if holder.get('content') is not None:
            assert f'data-demo-open="{demo_id}"' not in holder['content']
    assert f'data-demo-open="{demo_id}"' in dst['content']
    if dst.get('_fr',{}).get('content') is not None:
        assert f'data-demo-open="{demo_id}"' in dst['_fr']['content']
    if dst.get('_en',{}).get('content') is not None:
        assert f'data-demo-open="{demo_id}"' in dst['_en']['content']
print('OK - demos moved to method slides')
