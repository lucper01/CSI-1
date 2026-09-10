from pathlib import Path
import re

# ---------- index.html ----------
index_path = Path('index.html')
text = index_path.read_text(encoding='utf-8')

# Remove the TWIXAV bottom TBW-mean callout from FR root/_fr and EN blocks.
tbw_callout = '<div class=\\"callout\\" style=\\"margin-top:14px\\"><strong>TBW moyenne :</strong> environ 660 ms à 50 ms, 594 ms à 150 ms et 558 ms à 250 ms.</div>'
count = text.count(tbw_callout)
if count != 3:
    raise SystemExit(f'Unexpected TWIXAV TBW callout count: {count}')
text = text.replace(tbw_callout, '')

replacements = [
    (
        '<figcaption>La largeur moyenne de la TBW diminue avec la durée.</figcaption>',
        '<figcaption>La largeur moyenne de la TBW diminue avec la durée. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).</figcaption>',
        2,
    ),
    (
        '<figcaption>Mean TBW width decreases with duration.</figcaption>',
        '<figcaption>Mean TBW width decreases with duration. Error bars represent the standard error of the mean (SEM).</figcaption>',
        1,
    ),
    (
        '<figcaption>n = 24 - effet de condition : p &lt; .001. Les moyennes sont indiquées directement près des barres d’erreur.</figcaption>',
        '<figcaption>n = 24 - effet de condition : p &lt; .001. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).</figcaption>',
        2,
    ),
    (
        '<figcaption>n = 24 - condition effect: p &lt; .001. Means are labeled directly next to error bars.</figcaption>',
        '<figcaption>n = 24 - condition effect: p &lt; .001. Error bars represent the standard error of the mean (SEM).</figcaption>',
        1,
    ),
    (
        '<figcaption>Interaction condition × taille : p &lt; .001 - effet principal de taille : p = .601, n.s.</figcaption>',
        '<figcaption>Interaction condition × taille : p &lt; .001 - effet principal de taille : p = .601, n.s. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).</figcaption>',
        2,
    ),
    (
        '<figcaption>Condition × size interaction: p &lt; .001 - main effect of size: p = .601, n.s.</figcaption>',
        '<figcaption>Condition × size interaction: p &lt; .001 - main effect of size: p = .601, n.s. Error bars represent the standard error of the mean (SEM).</figcaption>',
        1,
    ),
]

for old, new, expected in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'Unexpected caption count {count} (expected {expected}) for: {old[:90]}')
    text = text.replace(old, new)

index_path.write_text(text, encoding='utf-8')

# ---------- TWIXAV TBW SVG ----------
tbw_path = Path('assets/results/twixav_tbw_width.svg')
tbw = tbw_path.read_text(encoding='utf-8')
pattern_tbw_labels = re.compile(r'<text x="(?:230|450|670)" y="[^"]+" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="800" text-anchor="middle" fill="#173f5f">(?:660|594|558) ms</text>')
tbw, n = pattern_tbw_labels.subn('', tbw)
if n != 3:
    raise SystemExit(f'Unexpected TWIXAV direct-value label count: {n}')
tbw_path.write_text(tbw, encoding='utf-8')

# ---------- VIBEX condition SVG ----------
v1_path = Path('assets/results/vibex_m1_olivia.svg')
v1 = v1_path.read_text(encoding='utf-8')
pattern_v1_labels = re.compile(r'<text x="[^"]+" y="[^"]+" text-anchor="middle" font-family="Arial" font-size="11" font-weight="700" fill="#[A-Fa-f0-9]+">\d+\.\d+</text>')
v1, n = pattern_v1_labels.subn('', v1)
if n != 12:
    raise SystemExit(f'Unexpected VIBEX condition direct-value label count: {n}')
v1 = v1.replace('<desc>Moyennes et IC95, LL relié à SS et SL relié à LS pour chaque taille.</desc>', '<desc>Moyennes et erreur standard de la moyenne (SEM), LL relié à SS et SL relié à LS pour chaque taille.</desc>')
v1 = v1.replace('LL-SS et SL-LS reliées séparément - moyenne et IC95', 'LL-SS et SL-LS reliées séparément - moyenne et SEM')
if 'IC95' in v1:
    raise SystemExit('Residual IC95 label in vibex_m1_olivia.svg')
v1_path.write_text(v1, encoding='utf-8')

# ---------- VIBEX size-interaction SVG ----------
v2_path = Path('assets/results/vibex_size_interaction.svg')
v2 = v2_path.read_text(encoding='utf-8')
pattern_v2_labels = re.compile(r'<text x="[^"]+" y="[^"]+" text-anchor="middle" font-family="Arial" font-size="10\.5" font-weight="700" fill="#[A-Fa-f0-9]+">\d+\.\d+</text>')
v2, n = pattern_v2_labels.subn('', v2)
if n != 12:
    raise SystemExit(f'Unexpected VIBEX size direct-value label count: {n}')
v2 = v2.replace('<desc>Trois facettes de taille, conditions en abscisse, pourcentage en ordonnée, moyennes et IC95.</desc>', '<desc>Trois facettes de taille, conditions en abscisse, pourcentage en ordonnée, moyennes et erreur standard de la moyenne (SEM).</desc>')
if 'IC95' in v2:
    raise SystemExit('Residual IC95 label in vibex_size_interaction.svg')
v2_path.write_text(v2, encoding='utf-8')

print('Removed TWIXAV estimate labels: 3')
print('Removed VIBEX estimate labels: 12 + 12')
print('Updated captions to identify error bars as SEM')
print('Removed TWIXAV TBW mean bottom callout')
