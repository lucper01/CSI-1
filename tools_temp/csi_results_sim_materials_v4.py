from pathlib import Path
import json, re, math

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')

# --- Cover logos: exact user-supplied assets + equal card geometry ---
old_cnrs = 'https://raw.githubusercontent.com/Universite-Gustave-Eiffel/NoisePlanet/d0864656c42f5aa14dec5c26bd61258c8d1129e8/assets/img/contact/cnrs.svg'
text = text.replace(old_cnrs, 'assets/logos/cnrs-logo.png')
text = text.replace('assets/logos/institut-agro-dijon.webp', 'assets/logos/institut-agro-dijon-cropped.webp')

# Remove earlier cover-specific override if present.
text = re.sub(r'\n\s*/\* Cover institutional logos.*?</style>', '\n</style>', text, flags=re.S)
text = re.sub(r'<style id="cover-logo-harmonization-v3">.*?</style>\s*', '', text, flags=re.S)

# Remove a previous version of this upgrade if rerun.
text = re.sub(r'\n<!-- CSI-UPGRADE-V4 START -->.*?<!-- CSI-UPGRADE-V4 END -->\n', '\n', text, flags=re.S)

# --- Parse slide JSON ---
prefix = 'const slides = '
start = text.index(prefix) + len(prefix)
end_marker = '];\n\n  const mainSlides'
end = text.index(end_marker, start) + 1
slides = json.loads(text[start:end])

def slide_title(s):
    return s.get('title') or s.get('_fr', {}).get('title', '')

def lang_block(section, kicker, title, lead, content, notes=''):
    return {'section': section, 'kicker': kicker, 'title': title, 'lead': lead, 'content': content, 'notes': notes}

def make_slide(chapter, study, fr, en, appendix=False):
    d = {'chapter': chapter, 'study': study, 'appendix': appendix, '_fr': fr, '_en': en}
    d.update(fr)
    return d

# --- Add simulation access cards to TWIXAV and VIBEX intro slides ---
def add_sim_card_to_slide(s, study):
    labels = {
        'TWIXAV': {
            'fr': ('SIMULATION', 'Voir un essai TWIXAV', '3 exemples interactifs - 50, 150 et 250 ms'),
            'en': ('SIMULATION', 'Run a TWIXAV trial', '3 interactive examples - 50, 150 and 250 ms')
        },
        'VIBEX': {
            'fr': ('SIMULATION', 'Voir un essai VIBEX', 'Séquence interactive - images à intégrer'),
            'en': ('SIMULATION', 'Run a VIBEX trial', 'Interactive sequence - images to be added')
        }
    }
    for key, lang in [('_fr','fr'),('_en','en')]:
        if key in s and f'data-csi-sim="{study}"' not in s[key].get('content',''):
            a,b,c = labels[study][lang]
            s[key]['content'] += f'<button class="csi-sim-card" type="button" data-csi-sim="{study}"><b>{a}</b><strong>{b}</strong><span>{c}</span></button>'
    if study == 'TWIXAV' and f'data-csi-sim="{study}"' not in s.get('content',''):
        a,b,c = labels[study]['fr']
        s['content'] += f'<button class="csi-sim-card" type="button" data-csi-sim="{study}"><b>{a}</b><strong>{b}</strong><span>{c}</span></button>'
    if study == 'VIBEX' and f'data-csi-sim="{study}"' not in s.get('content',''):
        a,b,c = labels[study]['fr']
        s['content'] += f'<button class="csi-sim-card" type="button" data-csi-sim="{study}"><b>{a}</b><strong>{b}</strong><span>{c}</span></button>'

for s in slides:
    t = slide_title(s)
    if t.startswith('TWIXAV - pourquoi commencer'):
        add_sim_card_to_slide(s, 'TWIXAV')
    if t.startswith('VIBEX - pourquoi établir'):
        add_sim_card_to_slide(s, 'VIBEX')

# --- Result slides ---
TWIX1_FR = lang_block(
    'Études de l’année 1','TWIXAV - Résultats 1/3','TWIXAV - simultanéité perçue selon le SOA',
    'Les courbes ci-dessous sont les moyennes empiriques observées. Aucun ajustement gaussien n’est affiché.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/twixav_empirical.svg" alt="Courbes empiriques du taux de simultanéité selon le SOA pour 50, 150 et 250 ms"><figcaption>Taux de simultanéité perçue selon le SOA et la durée.</figcaption></figure><div class="result-facts"><div class="m1-owner"><span>Mémoire M1</span><strong>Alicia Emorine</strong></div><article><b>n = 19</b><span>participants</span></article><article><b>F(2,72 ; 49) = 84,59</b><span>effet du SOA - p &lt; .001</span></article><article><b>F(2 ; 36) = 13,94</b><span>effet de la durée - p &lt; .001</span></article><article><b>F(20 ; 360) = 2,325</b><span>interaction Durée × SOA - p = .001</span></article></div></div>',
    'Insister sur le caractère empirique des courbes. Les points sont les moyennes observées, reliées uniquement pour faciliter la lecture.'
)
TWIX1_EN = lang_block(
    'Year 1 studies','TWIXAV - Results 1/3','TWIXAV - perceived simultaneity across SOA',
    'The curves below are empirical group means. No Gaussian fit is displayed.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/twixav_empirical.svg" alt="Empirical simultaneity-rate curves across SOA for 50, 150 and 250 ms"><figcaption>Perceived simultaneity as a function of SOA and duration.</figcaption></figure><div class="result-facts"><div class="m1-owner"><span>Master 1 thesis</span><strong>Alicia Emorine</strong></div><article><b>n = 19</b><span>participants</span></article><article><b>F(2.72, 49) = 84.59</b><span>SOA effect - p &lt; .001</span></article><article><b>F(2, 36) = 13.94</b><span>duration effect - p &lt; .001</span></article><article><b>F(20, 360) = 2.325</b><span>Duration × SOA - p = .001</span></article></div></div>',
    'Emphasize that these are empirical curves. Points are observed means, connected only to aid reading.'
)

TWIX2_FR = lang_block(
    'Études de l’année 1','TWIXAV - Résultats 2/3','TWIXAV - la fenêtre se resserre avec la durée',
    'L’augmentation de la durée des stimuli est associée à une diminution de la largeur individuelle de la fenêtre d’intégration temporelle.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/twixav_tbw_widths.svg" alt="Largeur moyenne de la fenêtre temporelle pour 50, 150 et 250 ms"><figcaption>Largeur moyenne individuelle de la TBW.</figcaption></figure><div class="result-facts"><article><b>659,93 ± 42,91 ms</b><span>durée 50 ms</span></article><article><b>593,54 ± 39,55 ms</b><span>durée 150 ms</span></article><article><b>558,33 ± 34,28 ms</b><span>durée 250 ms</span></article><article class="key"><b>F(2 ; 36) = 8,82</b><span>effet de la durée - p &lt; .001</span></article><small>Post-hoc FDR : 50 vs 150 ms, pFDR = .03 ; 150 vs 250 ms, pFDR = .06 ; 50 vs 250 ms, pFDR = .006.</small></div></div>'
)
TWIX2_EN = lang_block(
    'Year 1 studies','TWIXAV - Results 2/3','TWIXAV - the temporal window narrows with duration',
    'Longer stimuli are associated with a reduction in individual temporal binding-window width.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/twixav_tbw_widths.svg" alt="Mean temporal window width for 50, 150 and 250 ms"><figcaption>Mean individual TBW width.</figcaption></figure><div class="result-facts"><article><b>659.93 ± 42.91 ms</b><span>50-ms duration</span></article><article><b>593.54 ± 39.55 ms</b><span>150-ms duration</span></article><article><b>558.33 ± 34.28 ms</b><span>250-ms duration</span></article><article class="key"><b>F(2, 36) = 8.82</b><span>duration effect - p &lt; .001</span></article><small>FDR post-hoc: 50 vs 150 ms, pFDR = .03; 150 vs 250 ms, pFDR = .06; 50 vs 250 ms, pFDR = .006.</small></div></div>'
)

TWIX3_FR = lang_block(
    'Études de l’année 1','TWIXAV - Résultats 3/3','TWIXAV - PSS et asymétrie',
    'La durée resserre la fenêtre sans déplacer significativement son centre ni modifier son asymétrie.',
    '<div class="dual-results"><figure class="result-chart small"><img src="assets/results/twixav_pss.svg" alt="PSS moyen pour les trois durées"><figcaption>PSS moyen selon la durée.</figcaption></figure><figure class="result-chart small"><img src="assets/results/twixav_asymmetry.svg" alt="Asymétrie moyenne de la fenêtre selon la durée"><figcaption>Asymétrie moyenne selon la durée.</figcaption></figure></div><div class="result-summary-row"><article><b>PSS - p = .232</b><span>pas d’effet significatif de la durée</span></article><article><b>PSS &gt; 0</b><span>pour les trois durées - tous pFDR &lt; .005</span></article><article><b>Asymétrie - p = .991</b><span>pas d’effet significatif de la durée</span></article></div>'
)
TWIX3_EN = lang_block(
    'Year 1 studies','TWIXAV - Results 3/3','TWIXAV - PSS and asymmetry',
    'Duration narrows the window without significantly shifting its center or changing its asymmetry.',
    '<div class="dual-results"><figure class="result-chart small"><img src="assets/results/twixav_pss.svg" alt="Mean PSS for the three durations"><figcaption>Mean PSS by duration.</figcaption></figure><figure class="result-chart small"><img src="assets/results/twixav_asymmetry.svg" alt="Mean window asymmetry by duration"><figcaption>Mean asymmetry by duration.</figcaption></figure></div><div class="result-summary-row"><article><b>PSS - p = .232</b><span>no significant duration effect</span></article><article><b>PSS &gt; 0</b><span>for all durations - all pFDR &lt; .005</span></article><article><b>Asymmetry - p = .991</b><span>no significant duration effect</span></article></div>'
)

VIB1_FR = lang_block(
    'Études de l’année 1','VIBEX - Résultats 1/3','VIBEX - le cadrage produit l’asymétrie attendue',
    'Le jugement « identique » dépend fortement de l’ordre des cadrages, avec une asymétrie nette entre SL et LS.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_conditions.svg" alt="Pourcentage de réponses identique pour LL, SS, SL et LS"><figcaption>Réponses « identique » selon la condition.</figcaption></figure><div class="result-facts"><div class="m1-owner"><span>Mémoire M1</span><strong>Olivia Hiridjee</strong></div><article><b>n = 24</b><span>participants</span></article><article><b>F(3 ; 69) = 119,419</b><span>effet de la condition - p &lt; .001</span></article><article><b>52,0 % vs 28,4 %</b><span>SL vs LS - t(23) = 9,09, p &lt; .001</span></article><article><b>78,8 % vs 74,7 %</b><span>LL vs SS - p = .121, n.s.</span></article></div></div>'
)
VIB1_EN = lang_block(
    'Year 1 studies','VIBEX - Results 1/3','VIBEX - framing produces the expected asymmetry',
    '“Same” judgments strongly depend on framing order, with a clear asymmetry between SL and LS.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_conditions.svg" alt="Percentage of same responses for LL, SS, SL and LS"><figcaption>“Same” responses by condition.</figcaption></figure><div class="result-facts"><div class="m1-owner"><span>Master 1 thesis</span><strong>Olivia Hiridjee</strong></div><article><b>n = 24</b><span>participants</span></article><article><b>F(3, 69) = 119.419</b><span>condition effect - p &lt; .001</span></article><article><b>52.0% vs 28.4%</b><span>SL vs LS - t(23) = 9.09, p &lt; .001</span></article><article><b>78.8% vs 74.7%</b><span>LL vs SS - p = .121, n.s.</span></article></div></div>'
)

VIB2_FR = lang_block(
    'Études de l’année 1','VIBEX - Résultats 2/3','VIBEX - l’effet dépend de la taille de l’image',
    'Il n’y a pas d’effet principal de la taille, mais la taille module la différence entre conditions.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_size_interaction.svg" alt="Pourcentage de réponses identique pour les quatre conditions selon la taille"><figcaption>Interaction Condition × Taille.</figcaption></figure><div class="result-facts"><article><b>F(2 ; 46) = 0,515</b><span>effet principal de la taille - p = .601</span></article><article><b>F(6 ; 138) = 6,575</b><span>interaction Condition × Taille - p &lt; .001</span></article><article><b>30,6 %</b><span>écart SL-LS - petites images</span></article><article><b>25,3 % puis 14,8 %</b><span>images moyennes puis grandes</span></article><small>En condition SL, petites vs grandes : t(23) = 3,6708, p = .045.</small></div></div>'
)
VIB2_EN = lang_block(
    'Year 1 studies','VIBEX - Results 2/3','VIBEX - the effect depends on image size',
    'There is no main effect of size, but size modulates the difference between framing conditions.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_size_interaction.svg" alt="Percentage of same responses for the four conditions by size"><figcaption>Condition × Size interaction.</figcaption></figure><div class="result-facts"><article><b>F(2, 46) = 0.515</b><span>main size effect - p = .601</span></article><article><b>F(6, 138) = 6.575</b><span>Condition × Size - p &lt; .001</span></article><article><b>30.6%</b><span>SL-LS gap - small images</span></article><article><b>25.3% then 14.8%</b><span>medium then large images</span></article><small>In SL, small vs large: t(23) = 3.6708, p = .045.</small></div></div>'
)

VIB3_FR = lang_block(
    'Études de l’année 1','VIBEX - Résultats 3/3','VIBEX - le temps de réponse confirme l’asymétrie',
    'Les réponses sont plus lentes en SL qu’en LS, surtout pour les petites images.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_rt.svg" alt="Temps de réaction moyen pour les conditions LL, SS, SL et LS"><figcaption>Temps de réaction moyen selon la condition - IC95 %.</figcaption></figure><div class="result-facts"><article><b>F(3 ; 69) = 3,12</b><span>effet de la condition - p = .031</span></article><article><b>837 ms vs 802 ms</b><span>SL vs LS - p = .004</span></article><article><b>F(6 ; 138) = 3,29</b><span>interaction Condition × Taille - p = .005</span></article><article class="key"><b>+53 ms</b><span>SL-LS pour les petites images - p = .024</span></article><small>Écart SL-LS : +37 ms pour les moyennes, p = .073 ; +14 ms pour les grandes, p = 1.000.</small></div></div>'
)
VIB3_EN = lang_block(
    'Year 1 studies','VIBEX - Results 3/3','VIBEX - response time confirms the asymmetry',
    'Responses are slower in SL than LS, especially for small images.',
    '<div class="result-split"><figure class="result-chart"><img src="assets/results/vibex_rt.svg" alt="Mean response time for LL, SS, SL and LS"><figcaption>Mean response time by condition - 95% CI.</figcaption></figure><div class="result-facts"><article><b>F(3, 69) = 3.12</b><span>condition effect - p = .031</span></article><article><b>837 ms vs 802 ms</b><span>SL vs LS - p = .004</span></article><article><b>F(6, 138) = 3.29</b><span>Condition × Size - p = .005</span></article><article class="key"><b>+53 ms</b><span>SL-LS for small images - p = .024</span></article><small>SL-LS gap: +37 ms for medium images, p = .073; +14 ms for large images, p = 1.000.</small></div></div>'
)

new_twix = [make_slide('Année 1','TWIXAV',TWIX1_FR,TWIX1_EN), make_slide('Année 1','TWIXAV',TWIX2_FR,TWIX2_EN), make_slide('Année 1','TWIXAV',TWIX3_FR,TWIX3_EN)]
new_vib = [make_slide('Année 1','VIBEX',VIB1_FR,VIB1_EN), make_slide('Année 1','VIBEX',VIB2_FR,VIB2_EN), make_slide('Année 1','VIBEX',VIB3_FR,VIB3_EN)]

# Replace old single result slides, while keeping the surrounding narrative.
out=[]
for s in slides:
    t=slide_title(s)
    if t == 'TWIXAV - Résultats':
        out.extend(new_twix)
    elif t == 'VIBEX - résultats du prétest et statut':
        out.extend(new_vib)
    else:
        # Avoid duplication if this script is rerun after a partial commit.
        if t in {x['title'] for x in new_twix+new_vib}:
            continue
        out.append(s)
slides=out

# Re-serialize compactly, preserving Unicode.
new_json=json.dumps(slides, ensure_ascii=False, separators=(',',':'))
text = text[:start] + new_json + text[end:]

# --- Generate result SVGs ---
results = Path('assets/results'); results.mkdir(parents=True, exist_ok=True)

def esc(x):
    return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def line_svg(title, xvals, series, ymin=0, ymax=1, y_percent=False, xlabel='SOA (ms)', ylabel='Taux de simultanéité'):
    W,H=900,520; L,R,T,B=90,45,58,75; pw=W-L-R; ph=H-T-B
    def X(v): return L+(v-min(xvals))/(max(xvals)-min(xvals))*pw
    def Y(v): return T+(ymax-v)/(ymax-ymin)*ph
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/><style>text{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#24352d}} .mut{{fill:#66776d}} .grid{{stroke:#dce5df;stroke-width:1}} .axis{{stroke:#809088;stroke-width:1.5}} .lab{{font-size:15px}} .ttl{{font-size:22px;font-weight:800}}</style><text x="{L}" y="32" class="ttl">{esc(title)}</text>']
    for i in range(6):
        v=ymin+(ymax-ymin)*i/5; y=Y(v); s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="grid"/>')
        lab=f'{v*100:.0f}%' if y_percent else f'{v:.0f}'
        s.append(f'<text x="{L-12}" y="{y+5:.1f}" text-anchor="end" class="lab mut">{lab}</text>')
    for xv in xvals:
        x=X(xv); s.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H-B}" class="grid" opacity=".55"/><text x="{x:.1f}" y="{H-B+26}" text-anchor="middle" class="lab mut">{xv}</text>')
    s += [f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" class="axis"/>',f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" class="axis"/>',f'<text x="{L+pw/2}" y="{H-18}" text-anchor="middle" class="lab">{esc(xlabel)}</text>',f'<text transform="translate(25 {T+ph/2}) rotate(-90)" text-anchor="middle" class="lab">{esc(ylabel)}</text>']
    legend_x=W-R-230; legend_y=70
    for j,ser in enumerate(series):
        vals=ser['values']; color=ser['color']; se=ser.get('se')
        pts=' '.join(f'{X(xvals[i]):.1f},{Y(vals[i]):.1f}' for i in range(len(xvals)))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
        for i,v in enumerate(vals):
            x=X(xvals[i]); y=Y(v)
            if se:
                y1=Y(min(ymax,v+se[i])); y2=Y(max(ymin,v-se[i])); s.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5" opacity=".55"/><line x1="{x-4:.1f}" y1="{y1:.1f}" x2="{x+4:.1f}" y2="{y1:.1f}" stroke="{color}"/><line x1="{x-4:.1f}" y1="{y2:.1f}" x2="{x+4:.1f}" y2="{y2:.1f}" stroke="{color}"/>')
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="{color}" stroke-width="3"/>')
        ly=legend_y+j*30; s.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x+30}" y2="{ly}" stroke="{color}" stroke-width="4"/><circle cx="{legend_x+15}" cy="{ly}" r="4" fill="#fff" stroke="{color}" stroke-width="2"/><text x="{legend_x+40}" y="{ly+5}" class="lab">{esc(ser["label"])}</text>')
    s.append('</svg>'); return ''.join(s)

def bar_svg(title, labels, values, errors=None, color='#2f6f9f', ymax=None, ylabel='', suffix=''):
    W,H=820,500; L,R,T,B=85,35,58,72; pw=W-L-R; ph=H-T-B
    if ymax is None: ymax=max(values)*1.22
    def Y(v): return T+(ymax-v)/ymax*ph
    n=len(values); gap=pw/n; bw=min(100,gap*.55)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/><style>text{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#24352d}} .mut{{fill:#66776d}} .grid{{stroke:#dce5df;stroke-width:1}} .lab{{font-size:15px}} .ttl{{font-size:22px;font-weight:800}}</style><text x="{L}" y="32" class="ttl">{esc(title)}</text>']
    for i in range(6):
        v=ymax*i/5; y=Y(v); s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="grid"/><text x="{L-10}" y="{y+5:.1f}" text-anchor="end" class="lab mut">{v:.0f}{suffix}</text>')
    for i,(lab,val) in enumerate(zip(labels,values)):
        cx=L+gap*(i+.5); x=cx-bw/2; y=Y(val); h=H-B-y
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="10" fill="{color}" opacity=".86"/><text x="{cx:.1f}" y="{H-B+28}" text-anchor="middle" class="lab">{esc(lab)}</text><text x="{cx:.1f}" y="{y-10:.1f}" text-anchor="middle" class="lab" font-weight="800">{val:.1f}{suffix}</text>')
        if errors:
            lo=max(0,val-errors[i]); hi=min(ymax,val+errors[i]); y1=Y(hi); y2=Y(lo); s.append(f'<line x1="{cx:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{y2:.1f}" stroke="#24352d" stroke-width="2"/><line x1="{cx-8:.1f}" y1="{y1:.1f}" x2="{cx+8:.1f}" y2="{y1:.1f}" stroke="#24352d" stroke-width="2"/><line x1="{cx-8:.1f}" y1="{y2:.1f}" x2="{cx+8:.1f}" y2="{y2:.1f}" stroke="#24352d" stroke-width="2"/>')
    s.append(f'<text transform="translate(23 {T+ph/2}) rotate(-90)" text-anchor="middle" class="lab">{esc(ylabel)}</text></svg>'); return ''.join(s)

def dot_ci_svg(title, labels, means, lows, highs, color='#2f7d5a', ymin=700, ymax=920, ylabel='Temps de réaction (ms)'):
    W,H=820,500; L,R,T,B=90,35,58,72; pw=W-L-R; ph=H-T-B
    def Y(v): return T+(ymax-v)/(ymax-ymin)*ph
    n=len(means); gap=pw/n
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" rx="24" fill="#fff"/><style>text{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#24352d}} .mut{{fill:#66776d}} .grid{{stroke:#dce5df;stroke-width:1}} .lab{{font-size:15px}} .ttl{{font-size:22px;font-weight:800}}</style><text x="{L}" y="32" class="ttl">{esc(title)}</text>']
    for i in range(6):
        v=ymin+(ymax-ymin)*i/5; y=Y(v); s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="grid"/><text x="{L-10}" y="{y+5:.1f}" text-anchor="end" class="lab mut">{v:.0f}</text>')
    for i,(lab,m,lo,hi) in enumerate(zip(labels,means,lows,highs)):
        cx=L+gap*(i+.5); y=Y(m); ylo=Y(lo); yhi=Y(hi)
        s.append(f'<line x1="{cx:.1f}" y1="{yhi:.1f}" x2="{cx:.1f}" y2="{ylo:.1f}" stroke="{color}" stroke-width="4"/><line x1="{cx-12:.1f}" y1="{yhi:.1f}" x2="{cx+12:.1f}" y2="{yhi:.1f}" stroke="{color}" stroke-width="3"/><line x1="{cx-12:.1f}" y1="{ylo:.1f}" x2="{cx+12:.1f}" y2="{ylo:.1f}" stroke="{color}" stroke-width="3"/><circle cx="{cx:.1f}" cy="{y:.1f}" r="9" fill="#fff" stroke="{color}" stroke-width="4"/><text x="{cx:.1f}" y="{H-B+28}" text-anchor="middle" class="lab">{lab}</text><text x="{cx:.1f}" y="{y-16:.1f}" text-anchor="middle" class="lab" font-weight="800">{m:.0f}</text>')
    s.append(f'<text transform="translate(24 {T+ph/2}) rotate(-90)" text-anchor="middle" class="lab">{esc(ylabel)}</text></svg>'); return ''.join(s)

soas=[-500,-400,-300,-200,-100,0,100,200,300,400,500]
series=[
 {'label':'50 ms','color':'#2f6f9f','values':[.043,.158,.291,.561,.889,.953,.974,.941,.743,.488,.316],'se':[.019,.044,.067,.064,.039,.023,.018,.021,.064,.079,.075]},
 {'label':'150 ms','color':'#5f8fb4','values':[.074,.098,.178,.553,.833,.942,.947,.888,.628,.381,.256],'se':[.032,.030,.050,.068,.041,.018,.023,.039,.086,.076,.068]},
 {'label':'250 ms','color':'#173f5f','values':[.032,.077,.155,.408,.822,.933,.951,.940,.529,.370,.146],'se':[.014,.025,.051,.058,.046,.021,.016,.024,.080,.082,.063]}
]
(results/'twixav_empirical.svg').write_text(line_svg('TWIXAV - données empiriques',soas,series,0,1,True,'SOA (ms)','Réponses « simultané »'),encoding='utf-8')
(results/'twixav_tbw_widths.svg').write_text(bar_svg('Largeur de la fenêtre temporelle',['50 ms','150 ms','250 ms'],[659.93,593.54,558.33],[42.91,39.55,34.28],'#2f6f9f',760,'Largeur de TBW (ms)'),encoding='utf-8')
(results/'twixav_pss.svg').write_text(bar_svg('Point de simultanéité subjectif',['50 ms','150 ms','250 ms'],[96.94,82.29,79.87],[13.009,15.37,13.18],'#2f6f9f',140,'PSS (ms)'),encoding='utf-8')
(results/'twixav_asymmetry.svg').write_text(bar_svg('Asymétrie de la fenêtre',['50 ms','150 ms','250 ms'],[176.74,176.08,174.07],[26.39,32.48,27.28],'#2f6f9f',250,'Asymétrie (ms)'),encoding='utf-8')
(results/'vibex_conditions.svg').write_text(bar_svg('Réponses « identique »',['LL','SS','SL','LS'],[78.8,74.7,52.0,28.4],None,'#2f7d5a',100,'Réponses identique (%)','%'),encoding='utf-8')
size_series=[
 {'label':'LL','color':'#173f2d','values':[.794,.775,.795]},
 {'label':'SS','color':'#4e9b75','values':[.684,.776,.779]},
 {'label':'SL','color':'#2f7d5a','values':[.584,.505,.471]},
 {'label':'LS','color':'#9abfaa','values':[.278,.252,.323]}
]
(results/'vibex_size_interaction.svg').write_text(line_svg('VIBEX - interaction Condition × Taille',[0,1,2],size_series,0,1,True,'Taille : petite   moyenne   grande','Réponses « identique »'),encoding='utf-8')
(results/'vibex_rt.svg').write_text(dot_ci_svg('Temps de réaction selon la condition',['LL','SS','SL','LS'],[821,821,837,802],[757,755,779,745],[884,886,895,859]),encoding='utf-8')

# Fix x labels of the VIBEX size chart from numeric placeholders to words.
p=results/'vibex_size_interaction.svg'; z=p.read_text(encoding='utf-8'); z=z.replace('>0</text>','>Petite</text>',1).replace('>1</text>','>Moyenne</text>',1).replace('>2</text>','>Grande</text>',1); p.write_text(z,encoding='utf-8')

# --- CSS + hidden interactive slide runtime ---
upgrade = r'''
<!-- CSI-UPGRADE-V4 START -->
<style id="csi-upgrade-v4-style">
  /* Equal cover logo cards */
  .hero-slide .v16-logo-cloud{display:flex!important;align-items:center!important;gap:12px!important;flex-wrap:wrap!important;margin-top:22px!important}
  .hero-slide .v16-logo-cloud img{display:block!important;width:112px!important;height:62px!important;min-width:112px!important;max-width:112px!important;min-height:62px!important;max-height:62px!important;box-sizing:border-box!important;padding:7px 9px!important;border-radius:14px!important;background:#fff!important;object-fit:contain!important;object-position:center!important}
  .hero-slide .v16-logo-cloud img[alt="CNRS"]{padding:6px 24px!important}
  .hero-slide .v16-logo-cloud img[alt="L’Institut Agro Dijon"]{padding:9px 7px!important}
  @media(max-width:900px){.hero-slide .v16-logo-cloud img{width:98px!important;height:54px!important;min-width:98px!important;max-width:98px!important;min-height:54px!important;max-height:54px!important}.hero-slide .v16-logo-cloud img[alt="CNRS"]{padding:6px 22px!important}}

  .result-split{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.72fr);gap:20px;align-items:stretch}
  .result-chart{margin:0;background:var(--white);border:1px solid var(--line);border-radius:24px;padding:12px;box-shadow:var(--shadow-soft);min-width:0}
  .result-chart img{display:block;width:100%;height:min(49vh,480px);object-fit:contain;border-radius:17px;background:#fff}
  .result-chart figcaption{font-size:.82rem;color:var(--muted);padding:8px 5px 1px}
  .result-facts{display:grid;grid-template-columns:1fr;gap:10px;align-content:start}
  .result-facts article,.result-summary-row article{padding:15px 17px;border-radius:18px;background:var(--white);border:1px solid var(--line);box-shadow:var(--shadow-soft)}
  .result-facts article b,.result-summary-row article b{display:block;color:var(--study,var(--accent));font-size:1.08rem;margin-bottom:3px}
  .result-facts article span,.result-summary-row article span{font-size:.9rem;color:var(--muted);line-height:1.35}
  .result-facts article.key{border-color:color-mix(in srgb,var(--study,var(--accent)) 40%,var(--line));background:color-mix(in srgb,var(--study,var(--accent)) 8%,var(--white))}
  .result-facts small{padding:4px 5px;color:var(--muted);font-size:.78rem;line-height:1.4}
  .dual-results{display:grid;grid-template-columns:1fr 1fr;gap:18px}.dual-results .result-chart img{height:min(39vh,370px)}
  .result-summary-row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:14px}
  @media(max-width:980px){.result-split{grid-template-columns:1fr}.result-facts{grid-template-columns:repeat(2,1fr)}.dual-results{grid-template-columns:1fr}.result-summary-row{grid-template-columns:1fr}.result-chart img{height:auto}}

  .csi-sim-card{margin-top:16px;width:min(360px,100%);border:1px solid color-mix(in srgb,var(--study,var(--accent)) 35%,var(--line));border-radius:20px;background:color-mix(in srgb,var(--study,var(--accent)) 8%,var(--white));box-shadow:var(--shadow-soft);padding:13px 16px;text-align:left;cursor:pointer;color:var(--text);display:grid;gap:2px}
  .csi-sim-card:hover{transform:translateY(-2px);box-shadow:0 16px 34px color-mix(in srgb,var(--study,var(--accent)) 18%,transparent)}
  .csi-sim-card b{font-size:.7rem;letter-spacing:.08em;color:var(--study,var(--accent));text-transform:uppercase}.csi-sim-card strong{font-size:1rem}.csi-sim-card span{font-size:.8rem;color:var(--muted)}

  [data-csi-material="1"]{cursor:pointer!important;position:relative!important;outline:none}
  [data-csi-material="1"]::after{content:"voir";position:absolute;top:7px;right:9px;font-size:.62rem;font-weight:900;letter-spacing:.04em;text-transform:uppercase;color:var(--study,var(--accent));opacity:.72}
  [data-csi-material="1"]:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--study,var(--accent)) 42%,var(--line))!important}
  [data-csi-material="1"]:focus-visible{box-shadow:0 0 0 4px color-mix(in srgb,var(--study,var(--accent)) 24%,transparent)!important}

  #csiHiddenSlide{position:fixed;inset:0;z-index:5000;background:linear-gradient(135deg,color-mix(in srgb,var(--hidden-study,#1f6f50) 18%,#07130f),#07130f 70%);display:grid;place-items:center;padding:26px}
  #csiHiddenSlide[hidden]{display:none}
  .hidden-slide-shell{width:min(1420px,96vw);height:min(860px,92vh);border:1px solid rgba(255,255,255,.16);border-radius:34px;background:color-mix(in srgb,var(--cream) 96%,transparent);box-shadow:0 30px 80px rgba(0,0,0,.45);padding:30px 34px;overflow:auto;position:relative}
  .hidden-slide-top{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:20px}.hidden-slide-top span{display:block;color:var(--hidden-study,#1f6f50);font-weight:950;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem}.hidden-slide-top h2{font:800 clamp(1.8rem,3vw,3rem) Georgia,serif;margin:5px 0 0;color:var(--text)}
  .hidden-slide-close{border:0;border-radius:999px;background:var(--accent-soft);color:var(--accent-strong);width:44px;height:44px;cursor:pointer;font-size:1.2rem;font-weight:950}
  .material-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.material-item{padding:20px;border-radius:22px;border:1px solid var(--line);background:var(--white);box-shadow:var(--shadow-soft);min-height:150px}.material-item b{display:grid;place-items:center;width:50px;height:50px;border-radius:16px;background:var(--hidden-study,#1f6f50);color:#fff;margin-bottom:14px;font-size:.78rem}.material-item h3{margin:0 0 6px;color:var(--hidden-study,#1f6f50);font:800 1.2rem Georgia,serif}.material-item p{margin:0;color:var(--muted);font-size:.92rem;line-height:1.45}
  .hidden-note{margin-top:16px;padding:13px 16px;border-radius:16px;background:color-mix(in srgb,var(--hidden-study,#1f6f50) 9%,var(--white));border:1px solid color-mix(in srgb,var(--hidden-study,#1f6f50) 25%,var(--line));color:var(--muted);font-size:.86rem}

  .sim-layout{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(260px,.6fr);gap:20px}.sim-screen{min-height:470px;background:#111;border-radius:26px;border:1px solid rgba(255,255,255,.12);display:grid;place-items:center;position:relative;overflow:hidden;color:#fff}.sim-cross{width:100px;height:100px;position:relative}.sim-cross::before,.sim-cross::after{content:"";position:absolute;background:#fff;border-radius:3px}.sim-cross::before{width:8px;height:100px;left:46px}.sim-cross::after{height:8px;width:100px;top:46px}.sim-fix{width:22px;height:22px;border-radius:50%;background:#fff}.sim-panel{display:grid;align-content:start;gap:12px}.sim-panel article{padding:14px 15px;border:1px solid var(--line);border-radius:17px;background:var(--white)}.sim-panel b{color:var(--hidden-study,#1f6f50)}.sim-panel p{margin:5px 0 0;font-size:.86rem;color:var(--muted)}.sim-run{border:0;border-radius:16px;padding:12px 16px;background:var(--hidden-study,#1f6f50);color:#fff;font-weight:900;cursor:pointer}.sim-response{display:flex;gap:10px}.sim-response button{flex:1;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.08);color:#fff;border-radius:14px;padding:12px;font-weight:850}.sim-status{position:absolute;left:18px;bottom:16px;font-size:.78rem;color:#bbb}.sim-vibex-stage{width:min(720px,86%);display:grid;gap:14px}.sim-image-placeholder{height:260px;border:2px dashed rgba(255,255,255,.32);border-radius:20px;display:grid;place-items:center;text-align:center;color:#ddd;padding:20px}.sim-mask{height:260px;border-radius:20px;background:repeating-linear-gradient(45deg,#222 0 8px,#444 8px 16px);display:grid;place-items:center;color:#fff;font-weight:900}.sim-timeline{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}.sim-timeline span{padding:7px 10px;border-radius:999px;background:rgba(255,255,255,.09);color:#ddd;font-size:.78rem}
  @media(max-width:900px){.sim-layout{grid-template-columns:1fr}.hidden-slide-shell{padding:22px}.sim-screen{min-height:390px}}
</style>
<div id="csiHiddenSlide" hidden aria-modal="true" role="dialog" aria-labelledby="csiHiddenTitle">
  <div class="hidden-slide-shell">
    <div class="hidden-slide-top"><div><span id="csiHiddenKicker">Détail</span><h2 id="csiHiddenTitle">Détail</h2></div><button class="hidden-slide-close" id="csiHiddenClose" type="button" aria-label="Fermer">×</button></div>
    <div id="csiHiddenBody"></div>
  </div>
</div>
<script id="csi-upgrade-v4-runtime">
(() => {
  const COLORS={TWIXAV:'#2f6f9f',SOFT:'#7652a8',TWIXOLF:'#c36c32',VIBEX:'#2f7d5a',OASIS:'#b44e6c',SORBET:'#9a6b20',SOLAR:'#d09422',COBEX:'#5865a8',BRAUD:'#4f7187',BRAUDOLF:'#875a7c',FLUXOLF:'#a34d5d'};
  const MAT={
    TWIXAV:[['PsychoPy','PsychoPy 2023.1.3','Pilotage des stimuli, randomisation, monitoring et enregistrement des réponses.'],['AUDIO','Casque AKG K511','Diffusion du son pur à 1000 Hz dans une cabine isolée.'],['2×','Double écran','Un écran participant et un écran expérimentateur pour le monitoring.'],['REP','Clavier de réponse','Touches opposées pour le jugement simultané / successif.'],['POS','Cabine + mentonnière','Contrôle du bruit, de la lumière, de la distance et de la hauteur du regard.']],
    VIBEX:[['PsychoPy','PsychoPy 2023.1.3','Présentation des scènes et du masque, chronométrage et recueil des réponses.'],['PC×2','Deux ordinateurs','Un poste participant en cabine et un poste expérimentateur pour le contrôle de la passation.'],['57 cm','Mentonnière','Distance oeil-écran fixée à 57 cm pour contrôler l’angle visuel.'],['ECR','Écran participant','Présentation des images en trois tailles et des cadrages L / S.'],['REP','Clavier de réponse','Jugement identique / différent avec touches contrebalancées.']],
    FLUXOLF:[['EEG','BioSemi ActiveTwo','EEG 128 électrodes + 2 références.'],['BIO','BIOPAC MP160','Acquisition physiologique et synchronisation des signaux.'],['EDA','EDA','Activité électrodermale sur la main.'],['ECG','ECG','Mesure cardiaque pour HR et HRV.'],['EMG','EMG facial','Zygomatique et corrugateur selon le montage.']],
    SOFT:[['OLF','Sniff-0','Délivrance olfactive contrôlée.'],['RESP','Spir-0','Détection du cycle respiratoire et déclenchement sur inspiration.'],['BIO','BIOPAC MP160','ECG, EDA et synchronisation physiologique.'],['EEG','BioSemi ActiveTwo','EEG 128 électrodes + 2 références.'],['PSY','PsychoPy','Présentation, timing, réponses et logs.']],
    OASIS:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Suivi respiratoire et synchronisation.'],['BIO','BIOPAC MP160','Physiologie et marqueurs.'],['PSY','PsychoPy','Présentation des scènes et recueil comportemental.']],
    TWIXOLF:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Détection de l’inspiration.'],['BIO','BIOPAC MP160','Physiologie et marqueurs.'],['PSY','PsychoPy','Timing, stimuli et jugement de simultanéité.']],
    SORBET:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Suivi du cycle respiratoire.'],['BIO','BIOPAC MP160','Physiologie et triggers.'],['PSY','PsychoPy','Présentation et réponses.']],
    SOLAR:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Suivi du cycle respiratoire.'],['BIO','BIOPAC MP160','Physiologie et triggers.'],['PSY','PsychoPy','Présentation visuelle et réponses.']],
    COBEX:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Suivi du cycle respiratoire.'],['BIO','BIOPAC MP160','Physiologie et triggers.'],['PSY','PsychoPy','Présentation des scènes et réponses.']],
    BRAUD:[['OLF','Sniff-0','Chaîne olfactive disponible dans le protocole étendu.'],['RESP','Spir-0','Suivi du cycle respiratoire.'],['BIO','BIOPAC MP160','Physiologie et triggers.'],['AUD','Système audio','Présentation des scènes auditives.']],
    BRAUDOLF:[['OLF','Sniff-0','Délivrance olfactive.'],['RESP','Spir-0','Suivi du cycle respiratoire.'],['BIO','BIOPAC MP160','Physiologie et triggers.'],['AUD','Système audio','Présentation des scènes auditives.']]
  };
  const modal=document.getElementById('csiHiddenSlide'), body=document.getElementById('csiHiddenBody'), title=document.getElementById('csiHiddenTitle'), kicker=document.getElementById('csiHiddenKicker');
  const close=document.getElementById('csiHiddenClose'); let lastFocus=null, twixIndex=0;
  const lang=()=>document.documentElement.lang==='en'?'en':'fr';
  function studyFromEl(el){ const slide=el.closest('.slide'); const idx=slide?Number(slide.dataset.index):-1; if(idx>=0&&window.slides&&slides[idx]&&slides[idx].study)return slides[idx].study; const named=el.closest('[data-study]'); return named?named.dataset.study:null; }
  function markMaterialCards(){ document.querySelectorAll('.float-card,.hardware-card').forEach(el=>{ const b=el.querySelector(':scope > b'); if(!b)return; if(/matériel|hardware/i.test(b.textContent)){ el.dataset.csiMaterial='1'; el.setAttribute('role','button'); el.setAttribute('tabindex','0'); el.setAttribute('aria-label',(lang()==='en'?'Open hardware slide for ':'Ouvrir la diapo matériel de ')+(studyFromEl(el)||'')); } }); }
  function openBase(study, k, t){ lastFocus=document.activeElement; modal.style.setProperty('--hidden-study',COLORS[study]||getComputedStyle(document.documentElement).getPropertyValue('--accent')); kicker.textContent=k; title.textContent=t; modal.hidden=false; document.body.style.overflow='hidden'; close.focus(); }
  function closeModal(){ modal.hidden=true; body.innerHTML=''; document.body.style.overflow=''; if(lastFocus&&lastFocus.focus)lastFocus.focus(); }
  close.addEventListener('click',closeModal); modal.addEventListener('click',e=>{if(e.target===modal)closeModal()});
  document.addEventListener('keydown',e=>{if(!modal.hidden&&e.key==='Escape'){e.preventDefault();closeModal();}});
  function openMaterial(study){ const items=MAT[study]||[]; const en=lang()==='en'; openBase(study,en?'Hardware':'Matériel',study+' - '+(en?'experimental setup':'matériel expérimental')); body.innerHTML='<div class="material-grid">'+items.map(x=>'<article class="material-item"><b>'+x[0]+'</b><h3>'+x[1]+'</h3><p>'+x[2]+'</p></article>').join('')+'</div><div class="hidden-note">'+(en?'This hidden slide is opened only from the hardware card and is not part of the normal slide sequence.':'Cette diapo cachée s’ouvre uniquement depuis la carte matériel et ne fait pas partie de la séquence normale.')+'</div>'; }
  function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
  function tone(ms,delay=0){ const C=window.AudioContext||window.webkitAudioContext; if(!C)return; const ctx=new C(); const o=ctx.createOscillator(),g=ctx.createGain(); o.frequency.value=1000; o.type='sine'; o.connect(g); g.connect(ctx.destination); const t=ctx.currentTime+delay/1000, end=t+ms/1000; g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(.06,t+.005); g.gain.setValueAtTime(.06,Math.max(t+.006,end-.005)); g.gain.linearRampToValueAtTime(0,end); o.start(t); o.stop(end+.01); o.onended=()=>ctx.close(); }
  async function runTwix(){ const trials=[{d:50,soa:-200},{d:150,soa:100},{d:250,soa:300}],tr=trials[twixIndex%trials.length]; twixIndex++; const scr=document.getElementById('twixScreen'), status=document.getElementById('twixStatus'), run=document.getElementById('twixRun'); run.disabled=true; status.textContent='Fixation - 1100 ms'; scr.innerHTML='<div class="sim-fix"></div><div class="sim-status" id="twixStatus">Fixation - 1100 ms</div>'; await sleep(1100); scr.innerHTML='<div class="sim-status" id="twixStatus">Délai - 400 ms</div>'; await sleep(400); const visual=()=>{const c=document.createElement('div');c.className='sim-cross';scr.appendChild(c);setTimeout(()=>c.remove(),tr.d)}; if(tr.soa<0){tone(tr.d,0); setTimeout(visual,Math.abs(tr.soa));}else if(tr.soa>0){visual(); tone(tr.d,tr.soa);}else{visual();tone(tr.d,0);} await sleep(Math.abs(tr.soa)+tr.d+220); scr.innerHTML='<div class="sim-response"><button>Simultané</button><button>Successif</button></div><div class="sim-status">Durée '+tr.d+' ms - SOA '+(tr.soa>0?'+':'')+tr.soa+' ms</div>'; document.getElementById('twixTrial').innerHTML='<b>Essai '+(((twixIndex-1)%3)+1)+'/3</b><p>Durée : '+tr.d+' ms<br>SOA : '+(tr.soa>0?'+':'')+tr.soa+' ms</p>'; run.disabled=false; run.textContent=twixIndex%3===0?'Recommencer':'Essai suivant'; }
  function openTwix(){ const en=lang()==='en'; openBase('TWIXAV',en?'Interactive paradigm':'Paradigme interactif','TWIXAV - '+(en?'trial simulation':'simulation d’un essai')); body.innerHTML='<div class="sim-layout"><div class="sim-screen" id="twixScreen"><div><div class="sim-fix" style="margin:auto"></div><p style="color:#bbb;margin-top:20px">'+(en?'Click “Run trial” to start.':'Cliquez sur « Lancer l’essai » pour démarrer.')+'</p></div></div><div class="sim-panel"><article id="twixTrial"><b>'+ (en?'Three examples':'Trois exemples') +'</b><p>50 ms / SOA -200 ms<br>150 ms / SOA +100 ms<br>250 ms / SOA +300 ms</p></article><article><b>Stimuli</b><p>'+ (en?'White 100 × 100 px cross and 1000-Hz pure tone.':'Croix blanche 100 × 100 px et son pur à 1000 Hz.') +'</p></article><article><b>Essai</b><p>'+ (en?'1100-ms fixation, 400-ms blank, audiovisual stimulation, then simultaneity judgment.':'Fixation 1100 ms, délai 400 ms, stimulation audiovisuelle, puis jugement de simultanéité.') +'</p></article><button id="twixRun" class="sim-run" type="button">'+(en?'Run trial':'Lancer l’essai')+'</button></div></div>'; document.getElementById('twixRun').addEventListener('click',runTwix); }
  function openVibex(){ const en=lang()==='en'; openBase('VIBEX',en?'Interactive paradigm':'Paradigme interactif','VIBEX - '+(en?'trial simulation':'simulation d’un essai')); body.innerHTML='<div class="sim-layout"><div class="sim-screen"><div class="sim-vibex-stage"><div class="sim-image-placeholder"><div><b>'+ (en?'IMAGE 1':'IMAGE 1') +'</b><br>'+ (en?'Close-up or wide view - image to be supplied':'Plan serré ou large - image à fournir') +'</div></div><div class="sim-timeline"><span>Fixation 300 ms</span><span>Image 1 - 200 ms</span><span>Masque - 1000 ms</span><span>Image 2 - 200 ms</span></div><div class="sim-image-placeholder"><div><b>'+ (en?'IMAGE 2':'IMAGE 2') +'</b><br>'+ (en?'Same scene, second framing - image to be supplied':'Même scène, second cadrage - image à fournir') +'</div></div></div></div><div class="sim-panel"><article><b>Conditions</b><p>LL - SS - SL - LS</p></article><article><b>'+ (en?'Three sizes':'Trois tailles') +'</b><p>'+ (en?'Small, medium and large.':'Petite, moyenne et grande.') +'</p></article><article><b>'+ (en?'Response':'Réponse') +'</b><p>'+ (en?'Same / different framing.':'Cadrage identique / différent.') +'</p></article><div class="hidden-note">'+(en?'The interaction is ready. The two scene images you provide will replace these placeholders.':'L’interaction est prête. Les deux images de scène que vous fournirez remplaceront ces emplacements.')+'</div></div></div>'; }
  document.addEventListener('click',e=>{ const sim=e.target.closest('[data-csi-sim]'); if(sim){e.preventDefault(); sim.dataset.csiSim==='TWIXAV'?openTwix():openVibex(); return;} const m=e.target.closest('[data-csi-material="1"]'); if(m){e.preventDefault();openMaterial(studyFromEl(m));} });
  document.addEventListener('keydown',e=>{ const m=e.target.closest&&e.target.closest('[data-csi-material="1"]'); if(m&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openMaterial(studyFromEl(m));} });
  const obs=new MutationObserver(markMaterialCards); obs.observe(document.getElementById('deck'),{childList:true,subtree:true}); markMaterialCards();
})();
</script>
<!-- CSI-UPGRADE-V4 END -->
'''
text = text.replace('</body>', upgrade + '\n</body>', 1)

# Validation guards.
assert text.count('TWIXAV - Résultats 1/3') >= 1
assert text.count('VIBEX - Résultats 1/3') >= 1
assert 'redessin de la Figure 5 du mémoire pour la présentation' not in text
assert 'assets/logos/cnrs-logo.png' in text
assert 'assets/logos/institut-agro-dijon-cropped.webp' in text
assert 'data-csi-sim="TWIXAV"' in text and 'data-csi-sim="VIBEX"' in text
assert 'csiHiddenSlide' in text
assert len(slides) == 44, len(slides)
PATH.write_text(text, encoding='utf-8')
print('CSI upgrade complete:', len(slides), 'slides')
