from pathlib import Path
import json, html, math

ROOT = Path(".")
INDEX = ROOT / "index.html"
text = INDEX.read_text(encoding="utf-8")

def svg_text(x, y, s, size=18, weight=500, anchor="start", fill="#202823"):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(s))}</text>'

def write_svg(name, body):
    out = ROOT / "assets" / "results" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")

# TWIXAV empirical simultaneity curves from Alicia Emorine Annex 12.
soas = [-500,-400,-300,-200,-100,0,100,200,300,400,500]
twix = {
    "50 ms":  [4.3,15.8,29.1,56.1,86.8,95.3,97.4,94.1,74.3,40.8,31.6],
    "150 ms": [7.4,8.8,17.8,56.3,83.3,94.2,96.7,88.8,62.8,38.1,26.6],
    "250 ms": [3.2,7.7,15.5,40.8,82.2,93.3,95.1,94.0,52.9,37.0,14.6],
}
twix_cols = {"50 ms":"#0072B2","150 ms":"#D55E00","250 ms":"#009E73"}

W,H = 1000,560
L,R,T,B = 90,35,55,80
PW,PH = W-L-R,H-T-B
def sx(v): return L + (v+500)/1000*PW
def sy(v): return T + (100-v)/100*PH
els = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" rx="24" fill="#ffffff"/>']
for y in range(0,101,20):
    yy=sy(y); els.append(f'<line x1="{L}" y1="{yy}" x2="{W-R}" y2="{yy}" stroke="#e6ebe8" stroke-width="1"/>')
    els.append(svg_text(L-14, yy+6, y, 15, 500, "end", "#5f6f65"))
for x in soas:
    xx=sx(x); els.append(f'<line x1="{xx}" y1="{T}" x2="{xx}" y2="{H-B}" stroke="#f0f2f1" stroke-width="1"/>')
    els.append(svg_text(xx, H-B+30, x, 14, 500, "middle", "#5f6f65"))
els += [f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>',
        f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>']
for label,vals in twix.items():
    pts=" ".join(f"{sx(x):.1f},{sy(y):.1f}" for x,y in zip(soas,vals))
    c=twix_cols[label]
    els.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    for x,y in zip(soas,vals):
        els.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5.5" fill="{c}" stroke="#fff" stroke-width="2"/>')
lx=610
for i,label in enumerate(twix):
    x=lx+i*125
    els.append(f'<line x1="{x}" y1="25" x2="{x+28}" y2="25" stroke="{twix_cols[label]}" stroke-width="5"/>')
    els.append(f'<circle cx="{x+14}" cy="25" r="5" fill="{twix_cols[label]}"/>')
    els.append(svg_text(x+36,31,label,15,700,"start","#26342d"))
els.append(svg_text(W/2,H-18,"SOA (ms)",18,700,"middle","#26342d"))
els.append(f'<text x="25" y="{H/2}" transform="rotate(-90 25 {H/2})" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#26342d">Réponses « simultané » (%)</text>')
els.append(svg_text(L,T-18,"Moyennes empiriques - sans ajustement",16,700,"start","#2f6f9f"))
els.append('</svg>')
write_svg("twixav_empirical_curves.svg","".join(els))

# TWIXAV mean individual TBW width.
dur_labels=["50 ms","150 ms","250 ms"]
tbw=[659.93,593.54,558.33]
tbw_se=[42.91,39.55,34.28]
W,H=900,520; L,R,T,B=100,45,55,85; PW,PH=W-L-R,H-T-B
def sy2(v): return T+(760-v)/760*PH
els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/>']
for y in range(0,761,100):
    yy=sy2(y); els.append(f'<line x1="{L}" y1="{yy}" x2="{W-R}" y2="{yy}" stroke="#e6ebe8"/>'); els.append(svg_text(L-12,yy+6,y,14,500,"end","#5f6f65"))
xs=[230,450,670]
for x,label,m,se in zip(xs,dur_labels,tbw,tbw_se):
    y=sy2(m); y1=sy2(m-se); y2=sy2(m+se)
    els.append(f'<rect x="{x-52}" y="{y}" width="104" height="{H-B-y}" rx="14" fill="#dceaf4"/>')
    els.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#2f6f9f"/>')
    els.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#173f5f" stroke-width="4"/><line x1="{x-12}" y1="{y1}" x2="{x+12}" y2="{y1}" stroke="#173f5f" stroke-width="4"/><line x1="{x-12}" y1="{y2}" x2="{x+12}" y2="{y2}" stroke="#173f5f" stroke-width="4"/>')
    els.append(svg_text(x,y-18,f"{m:.0f} ms",20,800,"middle","#173f5f"))
    els.append(svg_text(x,H-B+34,label,17,700,"middle","#26342d"))
els.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<text x="28" y="{H/2}" transform="rotate(-90 28 {H/2})" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#26342d">Largeur individuelle moyenne de la TBW (ms)</text>')
els.append(svg_text(W/2,30,"La fenêtre se rétrécit quand la durée augmente",21,800,"middle","#173f5f"))
els.append('</svg>')
write_svg("twixav_tbw_width.svg","".join(els))

# TWIXAV PSS and asymmetry.
W,H=1000,520
els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/>']
panels=[("PSS (ms)",[96.94,82.29,79.87],[13.009,15.37,13.18],0,130,60,470),
        ("Asymétrie (ms)",[176.74,176.08,174.07],[26.39,32.48,27.28],100,240,540,950)]
for ptitle,vals,errs,ymin,ymax,x0,x1 in panels:
    ytop,ybot=75,410
    def py(v): return ytop+(ymax-v)/(ymax-ymin)*(ybot-ytop)
    els.append(svg_text((x0+x1)/2,38,ptitle,20,800,"middle","#173f5f"))
    for frac in [0,.25,.5,.75,1]:
        v=ymin+(ymax-ymin)*frac; yy=py(v)
        els.append(f'<line x1="{x0}" y1="{yy}" x2="{x1}" y2="{yy}" stroke="#e8ecea"/>')
        els.append(svg_text(x0-8,yy+5,f"{v:.0f}",13,500,"end","#5f6f65"))
    pxs=[x0+90,(x0+x1)/2,x1-90]
    for x,label,v,e in zip(pxs,dur_labels,vals,errs):
        y=py(v); ylo=py(v-e); yhi=py(v+e)
        els.append(f'<line x1="{x}" y1="{ylo}" x2="{x}" y2="{yhi}" stroke="#2f6f9f" stroke-width="4"/><circle cx="{x}" cy="{y}" r="10" fill="#2f6f9f"/>')
        els.append(svg_text(x,y-17,f"{v:.0f}",17,800,"middle","#173f5f"))
        els.append(svg_text(x,ybot+31,label,15,700,"middle","#26342d"))
    els.append(f'<line x1="{x0}" y1="{ybot}" x2="{x1}" y2="{ybot}" stroke="#26342d" stroke-width="2"/>')
els.append(svg_text(250,485,"Effet de la durée : p = .232 - n.s.",16,700,"middle","#5f6f65"))
els.append(svg_text(750,485,"Effet de la durée : p = .991 - n.s.",16,700,"middle","#5f6f65"))
els.append('</svg>')
write_svg("twixav_pss_asymmetry.svg","".join(els))

# VIBEX same-response rate by condition with 95% CI.
conds=["LL","SS","SL","LS"]
means=[78.8,74.7,52.0,28.4]
ci=[(73.9,83.8),(68.7,80.6),(44.4,59.6),(21.4,35.4)]
W,H=900,520; L,R,T,B=90,45,55,80; PW,PH=W-L-R,H-T-B
def vy(v): return T+(90-v)/75*PH
xs=[200,370,540,710]
els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/>']
for y in [20,40,60,80]:
    yy=vy(y); els.append(f'<line x1="{L}" y1="{yy}" x2="{W-R}" y2="{yy}" stroke="#e6ebe8"/>'); els.append(svg_text(L-12,yy+5,y,14,500,"end","#5f6f65"))
for x,c,m,(lo,hi) in zip(xs,conds,means,ci):
    y=vy(m); ylo=vy(lo); yhi=vy(hi)
    els.append(f'<line x1="{x}" y1="{ylo}" x2="{x}" y2="{yhi}" stroke="#2f7d5a" stroke-width="4"/><line x1="{x-10}" y1="{ylo}" x2="{x+10}" y2="{ylo}" stroke="#2f7d5a" stroke-width="4"/><line x1="{x-10}" y1="{yhi}" x2="{x+10}" y2="{yhi}" stroke="#2f7d5a" stroke-width="4"/>')
    els.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="#2f7d5a" stroke-width="4"/>')
    els.append(svg_text(x,y-20,f"{m:.1f}%",18,800,"middle","#1d6143"))
    els.append(svg_text(x,H-B+34,c,18,800,"middle","#26342d"))
els.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<text x="25" y="{H/2}" transform="rotate(-90 25 {H/2})" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#26342d">Réponses « identique » (%)</text>')
els.append(svg_text(625,95,"SL > LS : p < .001",18,800,"middle","#1d6143"))
els.append(svg_text(285,120,"LL vs SS : n.s.",16,700,"middle","#5f6f65"))
els.append('</svg>')
write_svg("vibex_conditions.svg","".join(els))

# VIBEX condition x size same-response rate.
sizes=["Petite","Moyenne","Grande"]
vib_psame={"LL":[79.4,77.5,79.5],"SS":[68.4,77.6,77.9],"SL":[58.4,50.5,47.1],"LS":[27.8,25.2,32.3]}
vcols={"LL":"#173f5f","SS":"#6d8b7a","SL":"#2f7d5a","LS":"#9bbcaf"}
W,H=920,520; L,R,T,B=90,55,60,85; xvals=[230,470,710]
def pyv(v): return T+(90-v)/75*(H-T-B)
els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/>']
for y in [20,40,60,80]:
    yy=pyv(y); els.append(f'<line x1="{L}" y1="{yy}" x2="{W-R}" y2="{yy}" stroke="#e6ebe8"/>'); els.append(svg_text(L-12,yy+5,y,14,500,"end","#5f6f65"))
for cond,vals in vib_psame.items():
    pts=" ".join(f"{x},{pyv(v):.1f}" for x,v in zip(xvals,vals))
    c=vcols[cond]; els.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="5" stroke-linejoin="round"/>')
    for x,v in zip(xvals,vals): els.append(f'<circle cx="{x}" cy="{pyv(v)}" r="8" fill="{c}" stroke="#fff" stroke-width="2"/>')
for x,s in zip(xvals,sizes): els.append(svg_text(x,H-B+34,s,17,800,"middle","#26342d"))
els.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<text x="25" y="{H/2}" transform="rotate(-90 25 {H/2})" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#26342d">Réponses « identique » (%)</text>')
for i,(cond,c) in enumerate(vcols.items()):
    x=560+i*75; els.append(f'<circle cx="{x}" cy="28" r="6" fill="{c}"/>'); els.append(svg_text(x+10,33,cond,14,700))
els.append(svg_text(460,485,"Écart SL-LS : 30,6 % - 25,3 % - 14,8 %",18,800,"middle","#1d6143"))
els.append('</svg>')
write_svg("vibex_size_interaction.svg","".join(els))

# VIBEX reaction times by condition x size.
vib_rt={"LL":[821,838,803],"SS":[850,808,804],"SL":[842,848,821],"LS":[789,811,807]}
W,H=920,520; L,R,T,B=90,55,60,85; xvals=[230,470,710]
def pyr(v): return T+(900-v)/(900-740)*(H-T-B)
els=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/>']
for y in [750,800,850,900]:
    yy=pyr(y); els.append(f'<line x1="{L}" y1="{yy}" x2="{W-R}" y2="{yy}" stroke="#e6ebe8"/>'); els.append(svg_text(L-12,yy+5,y,14,500,"end","#5f6f65"))
for cond,vals in vib_rt.items():
    pts=" ".join(f"{x},{pyr(v):.1f}" for x,v in zip(xvals,vals))
    c=vcols[cond]; els.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="5" stroke-linejoin="round"/>')
    for x,v in zip(xvals,vals): els.append(f'<circle cx="{x}" cy="{pyr(v)}" r="8" fill="{c}" stroke="#fff" stroke-width="2"/>')
for x,s in zip(xvals,sizes): els.append(svg_text(x,H-B+34,s,17,800,"middle","#26342d"))
els.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#26342d" stroke-width="2"/>')
els.append(f'<text x="25" y="{H/2}" transform="rotate(-90 25 {H/2})" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#26342d">Temps de réaction (ms)</text>')
for i,(cond,c) in enumerate(vcols.items()):
    x=560+i*75; els.append(f'<circle cx="{x}" cy="28" r="6" fill="{c}"/>'); els.append(svg_text(x+10,33,cond,14,700))
els.append(svg_text(460,485,"SL-LS : +53 ms (petite), +37 ms (moyenne), +14 ms (grande)",17,800,"middle","#1d6143"))
els.append('</svg>')
write_svg("vibex_rt_interaction.svg","".join(els))

# Parse slides.
marker = "const slides = "
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

def stitle(s):
    return s.get("title") or s.get("_fr",{}).get("title","")

def loc(section,kicker,title,lead,content,notes=""):
    return {"section":section,"kicker":kicker,"title":title,"lead":lead,"content":content,"notes":notes}

def new_slide(fr,en,study=""):
    d={"section":fr["section"],"kicker":fr["kicker"],"title":fr["title"],"lead":fr["lead"],"content":fr["content"],"notes":fr.get("notes",""),"_fr":fr,"_en":en}
    if study: d["study"]=study
    return d

twix_intro = next(s for s in slides if stitle(s)=="TWIXAV - pourquoi commencer par une fenêtre temporelle audiovisuelle ?")
vib_intro = next(s for s in slides if stitle(s)=="VIBEX - pourquoi établir une référence visuelle ?")

twix_card = '''<button class="study-demo-launch" type="button" data-demo-open="twixav" style="--demo-study:#2f6f9f"><span class="demo-launch-kicker">PARADIGME INTERACTIF</span><strong>Voir TWIXAV en action</strong><span>3 essais - 50, 150 et 250 ms - un SOA différent par durée</span><i>Cliquer pour agrandir</i></button>'''
twix_card_en = '''<button class="study-demo-launch" type="button" data-demo-open="twixav" style="--demo-study:#2f6f9f"><span class="demo-launch-kicker">INTERACTIVE PARADIGM</span><strong>Run a TWIXAV demonstration</strong><span>3 trials - 50, 150 and 250 ms - one different SOA per duration</span><i>Click to enlarge</i></button>'''
vib_card = '''<button class="study-demo-launch" type="button" data-demo-open="vibex" style="--demo-study:#2f7d5a"><span class="demo-launch-kicker">PARADIGME INTERACTIF</span><strong>Voir un essai VIBEX</strong><span>Fixation 300 ms - image 200 ms - masque 1000 ms - image 200 ms</span><i>Les deux images définitives seront intégrées à réception</i></button>'''
vib_card_en = '''<button class="study-demo-launch" type="button" data-demo-open="vibex" style="--demo-study:#2f7d5a"><span class="demo-launch-kicker">INTERACTIVE PARADIGM</span><strong>Run a VIBEX trial</strong><span>Fixation 300 ms - image 200 ms - mask 1000 ms - image 200 ms</span><i>The two final images will be inserted when supplied</i></button>'''

for s,card_fr,card_en in [(twix_intro,twix_card,twix_card_en),(vib_intro,vib_card,vib_card_en)]:
    if 'data-demo-open=' not in s["content"]: s["content"] += card_fr
    if "_fr" in s and 'data-demo-open=' not in s["_fr"]["content"]: s["_fr"]["content"] += card_fr
    if "_en" in s and 'data-demo-open=' not in s["_en"]["content"]: s["_en"]["content"] += card_en

twix1_fr = loc("Études de l’année 1","TWIXAV - Résultats 1/3","TWIXAV - les courbes empiriques","Le taux de simultanéité varie fortement avec le SOA et dépend aussi de la durée des stimuli.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-owner"><span>Mémoire M1</span><strong>Alicia Emorine - n = 19</strong></div><div class="m1-stat-grid"><div><b>F(2,72;49) = 84,59</b><span>effet du SOA - p &lt; .001</span></div><div><b>F(2;36) = 13,94</b><span>effet de la durée - p &lt; .001</span></div><div><b>F(20;360) = 2,325</b><span>interaction - p = .001</span></div></div><div class="callout"><strong>Lecture :</strong> les trois séries sont les moyennes empiriques observées. Aucune courbe psychométrique ou gaussienne n’est ajustée sur cette diapositive.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_empirical_curves.svg" alt="Courbes empiriques du taux de réponses simultané selon le SOA pour 50, 150 et 250 ms"><figcaption>Probabilité empirique de réponse « simultané » selon le SOA et la durée.</figcaption></figure></div>''')
twix1_en = loc("Year 1 studies","TWIXAV - Results 1/3","TWIXAV - empirical curves","Simultaneity judgments strongly vary with SOA and also depend on stimulus duration.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-owner"><span>Master's thesis</span><strong>Alicia Emorine - n = 19</strong></div><div class="m1-stat-grid"><div><b>F(2.72,49) = 84.59</b><span>SOA effect - p &lt; .001</span></div><div><b>F(2,36) = 13.94</b><span>duration effect - p &lt; .001</span></div><div><b>F(20,360) = 2.325</b><span>interaction - p = .001</span></div></div><div class="callout"><strong>Reading:</strong> the three series are the observed empirical means. No psychometric or Gaussian fit is shown.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_empirical_curves.svg" alt="Empirical simultaneity-response curves by SOA for 50, 150 and 250 ms"><figcaption>Empirical probability of a “simultaneous” response by SOA and duration.</figcaption></figure></div>''')

twix2_fr = loc("Études de l’année 1","TWIXAV - Résultats 2/3","TWIXAV - la fenêtre se rétrécit avec la durée","La largeur individuelle moyenne de la fenêtre temporelle diminue d’environ 102 ms entre les durées 50 et 250 ms.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>660 ms</b><span>durée 50 ms</span></div><div><b>594 ms</b><span>durée 150 ms</span></div><div><b>558 ms</b><span>durée 250 ms</span></div><div><b>F(2;36) = 8,82</b><span>p &lt; .001</span></div></div><div class="callout"><strong>Post-hoc FDR :</strong> 50 vs 150 ms, pFDR = .030 - 50 vs 250 ms, pFDR = .006 - 150 vs 250 ms, pFDR = .060.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_tbw_width.svg" alt="Largeur moyenne de la fenêtre temporelle audiovisuelle selon la durée"><figcaption>Largeur individuelle moyenne de la TBW - moyenne ± erreur-type rapportée dans le mémoire.</figcaption></figure></div>''')
twix2_en = loc("Year 1 studies","TWIXAV - Results 2/3","TWIXAV - the window narrows with duration","Mean individual temporal-window width decreases by about 102 ms between the 50 and 250 ms durations.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>660 ms</b><span>50 ms duration</span></div><div><b>594 ms</b><span>150 ms duration</span></div><div><b>558 ms</b><span>250 ms duration</span></div><div><b>F(2,36) = 8.82</b><span>p &lt; .001</span></div></div><div class="callout"><strong>FDR post-hoc:</strong> 50 vs 150 ms, pFDR = .030 - 50 vs 250 ms, pFDR = .006 - 150 vs 250 ms, pFDR = .060.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_tbw_width.svg" alt="Mean audiovisual temporal-window width by duration"><figcaption>Mean individual TBW width - mean ± standard error reported in the thesis.</figcaption></figure></div>''')

twix3_fr = loc("Études de l’année 1","TWIXAV - Résultats 3/3","TWIXAV - PSS et asymétrie restent stables","La durée réduit la largeur de la fenêtre sans déplacer significativement son centre subjectif ni modifier son asymétrie.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>96,9 - 82,3 - 79,9 ms</b><span>PSS pour 50 - 150 - 250 ms</span></div><div><b>p = .232</b><span>effet durée sur le PSS - n.s.</span></div><div><b>176,7 - 176,1 - 174,1 ms</b><span>asymétrie</span></div><div><b>p = .991</b><span>effet durée sur l’asymétrie - n.s.</span></div></div><div class="callout"><strong>Point important :</strong> les PSS sont positifs pour les trois durées, ce qui traduit une plus grande tolérance lorsque l’audition est retardée par rapport à la vision.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_pss_asymmetry.svg" alt="PSS et asymétrie selon la durée"><figcaption>La stabilité du PSS et de l’asymétrie contraste avec le rétrécissement de la TBW.</figcaption></figure></div>''')
twix3_en = loc("Year 1 studies","TWIXAV - Results 3/3","TWIXAV - PSS and asymmetry remain stable","Duration narrows the window without significantly shifting its subjective center or changing its asymmetry.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>96.9 - 82.3 - 79.9 ms</b><span>PSS at 50 - 150 - 250 ms</span></div><div><b>p = .232</b><span>duration effect on PSS - n.s.</span></div><div><b>176.7 - 176.1 - 174.1 ms</b><span>asymmetry</span></div><div><b>p = .991</b><span>duration effect on asymmetry - n.s.</span></div></div><div class="callout"><strong>Key point:</strong> PSS values are positive at all three durations, indicating greater tolerance when audition lags vision.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_pss_asymmetry.svg" alt="PSS and asymmetry by duration"><figcaption>Stable PSS and asymmetry contrast with the narrowing TBW.</figcaption></figure></div>''')

vib1_fr = loc("Études de l’année 1","VIBEX - Résultats 1/3","VIBEX - l’asymétrie SL-LS reproduit la Boundary Extension","La signature comportementale principale apparaît lorsque le cadrage serré est suivi d’un cadrage large.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-owner"><span>Mémoire M1</span><strong>Olivia Hiridjee - n = 24</strong></div><div class="m1-stat-grid"><div><b>78,8 %</b><span>LL</span></div><div><b>74,7 %</b><span>SS</span></div><div><b>52,0 %</b><span>SL</span></div><div><b>28,4 %</b><span>LS</span></div></div><div class="callout"><strong>Condition :</strong> F(3;69) = 119,419, p &lt; .001. SL &gt; LS, t(23) = 9,09, p &lt; .001 - LL vs SS n.s., p = .121.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_conditions.svg" alt="Pourcentage de réponses identique pour les conditions LL, SS, SL et LS"><figcaption>Réponses « identique » selon la transition de cadrage - IC95.</figcaption></figure></div>''')
vib1_en = loc("Year 1 studies","VIBEX - Results 1/3","VIBEX - the SL-LS asymmetry reproduces Boundary Extension","The main behavioral signature appears when a close view is followed by a wide view.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-owner"><span>Master's thesis</span><strong>Olivia Hiridjee - n = 24</strong></div><div class="m1-stat-grid"><div><b>78.8%</b><span>LL</span></div><div><b>74.7%</b><span>SS</span></div><div><b>52.0%</b><span>SL</span></div><div><b>28.4%</b><span>LS</span></div></div><div class="callout"><strong>Condition:</strong> F(3,69) = 119.419, p &lt; .001. SL &gt; LS, t(23) = 9.09, p &lt; .001 - LL vs SS n.s., p = .121.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_conditions.svg" alt="Percentage of same responses in LL, SS, SL and LS conditions"><figcaption>“Same” responses by framing transition - 95% CI.</figcaption></figure></div>''')

vib2_fr = loc("Études de l’année 1","VIBEX - Résultats 2/3","VIBEX - la taille module l’effet sans effet principal global","La taille n’a pas d’effet principal, mais elle modifie la différence entre les conditions de cadrage.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>p = .601</b><span>effet principal Taille - n.s.</span></div><div><b>p &lt; .001</b><span>Condition × Taille</span></div><div><b>30,6 %</b><span>SL-LS - petite</span></div><div><b>25,3 % / 14,8 %</b><span>moyenne / grande</span></div></div><div class="callout"><strong>Lecture :</strong> SL-LS est significatif pour les trois tailles, mais l’écart est maximal pour les petites images. SL petite vs grande : p = .045.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_size_interaction.svg" alt="Réponses identique par condition et taille d’image"><figcaption>Interaction Condition × Taille sur les réponses « identique ».</figcaption></figure></div>''')
vib2_en = loc("Year 1 studies","VIBEX - Results 2/3","VIBEX - size modulates the effect without a global main effect","Image size has no main effect but changes the contrast between framing conditions.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>p = .601</b><span>main Size effect - n.s.</span></div><div><b>p &lt; .001</b><span>Condition × Size</span></div><div><b>30.6%</b><span>SL-LS - small</span></div><div><b>25.3% / 14.8%</b><span>medium / large</span></div></div><div class="callout"><strong>Reading:</strong> SL-LS is significant at all three sizes, but the gap is largest for small images. SL small vs large: p = .045.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_size_interaction.svg" alt="Same responses by condition and image size"><figcaption>Condition × Size interaction on “same” responses.</figcaption></figure></div>''')

vib3_fr = loc("Études de l’année 1","VIBEX - Résultats 3/3","VIBEX - les temps de réaction convergent avec les jugements","Les temps de réaction renforcent l’interprétation : le conflit SL-LS est surtout visible pour les petites images.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>F(3;69) = 3,12</b><span>Condition - p = .031</span></div><div><b>F(6;138) = 3,29</b><span>Condition × Taille - p = .005</span></div><div><b>+53 ms</b><span>SL-LS petite - p = .024</span></div><div><b>+37 / +14 ms</b><span>moyenne / grande - n.s.</span></div></div><div class="callout"><strong>Convergence :</strong> la condition SL ralentit davantage la réponse que LS, surtout pour les petites images - le même pattern que celui observé sur les réponses « identique ».</div></div><figure class="result-figure-large"><img src="assets/results/vibex_rt_interaction.svg" alt="Temps de réaction par condition et taille d’image"><figcaption>Temps de réaction selon les quatre conditions et les trois tailles d’image.</figcaption></figure></div>''')
vib3_en = loc("Year 1 studies","VIBEX - Results 3/3","VIBEX - reaction times converge with judgments","Reaction times reinforce the interpretation: the SL-LS conflict is mainly visible for small images.",
'''<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>F(3,69) = 3.12</b><span>Condition - p = .031</span></div><div><b>F(6,138) = 3.29</b><span>Condition × Size - p = .005</span></div><div><b>+53 ms</b><span>SL-LS small - p = .024</span></div><div><b>+37 / +14 ms</b><span>medium / large - n.s.</span></div></div><div class="callout"><strong>Convergence:</strong> SL slows responses more than LS, especially for small images - the same pattern seen in “same” judgments.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_rt_interaction.svg" alt="Reaction time by condition and image size"><figcaption>Reaction times across four conditions and three image sizes.</figcaption></figure></div>''')

twix_old = next(i for i,s in enumerate(slides) if stitle(s)=="TWIXAV - Résultats")
slides[twix_old:twix_old+1] = [new_slide(twix1_fr,twix1_en,"TWIXAV"),new_slide(twix2_fr,twix2_en,"TWIXAV"),new_slide(twix3_fr,twix3_en,"TWIXAV")]
vib_old = next(i for i,s in enumerate(slides) if stitle(s)=="VIBEX - résultats du prétest et statut")
slides[vib_old:vib_old+1] = [new_slide(vib1_fr,vib1_en,"VIBEX"),new_slide(vib2_fr,vib2_en,"VIBEX"),new_slide(vib3_fr,vib3_en,"VIBEX")]

CNRS_DATA = "data:image/webp;base64,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..."