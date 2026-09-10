from pathlib import Path

INDEX = Path('index.html')
text = INDEX.read_text(encoding='utf-8')

# Cache-bust the four result SVGs so the updated labels are immediately visible.
for name in [
    'twixav_empirical_curves.svg',
    'twixav_tbw_width.svg',
    'vibex_m1_olivia.svg',
    'vibex_size_interaction.svg',
]:
    text = text.replace(f'{name}?v=axes-restored-2', f'{name}?v=sample-size-1')

# VIBEX slide 23 - replace the figure caption while retaining the inferential result.
fr23_old = 'n = 24 - effet de condition : p &lt; .001. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).'
fr23_new = '<strong>Taux moyen de réponses « Identiques » selon la condition et la taille. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).</strong><br>Effet de condition : p &lt; .001.'
if text.count(fr23_old) != 2:
    raise SystemExit(f'Unexpected FR slide 23 caption count: {text.count(fr23_old)}')
text = text.replace(fr23_old, fr23_new)

en23_old = 'n = 24 - condition effect: p &lt; .001. Error bars represent the standard error of the mean (SEM).'
en23_new = '<strong>Mean rate of “Identical” responses by condition and size. Error bars represent the standard error of the mean (SEM).</strong><br>Condition effect: p &lt; .001.'
if text.count(en23_old) != 1:
    raise SystemExit(f'Unexpected EN slide 23 caption count: {text.count(en23_old)}')
text = text.replace(en23_old, en23_new)

# VIBEX slide 24 - replace the figure caption while retaining the inferential results.
fr24_old = 'Interaction condition × taille : p &lt; .001 - effet principal de taille : p = .601, n.s. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).'
fr24_new = '<strong>Taux moyen de réponses « Identiques » selon la condition et la taille. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).</strong><br>Interaction condition × taille : p &lt; .001 - effet principal de taille : p = .601, n.s.'
if text.count(fr24_old) != 2:
    raise SystemExit(f'Unexpected FR slide 24 caption count: {text.count(fr24_old)}')
text = text.replace(fr24_old, fr24_new)

en24_old = 'Condition × size interaction: p &lt; .001 - main effect of size: p = .601, n.s. Error bars represent the standard error of the mean (SEM).'
en24_new = '<strong>Mean rate of “Identical” responses by condition and size. Error bars represent the standard error of the mean (SEM).</strong><br>Condition × size interaction: p &lt; .001 - main effect of size: p = .601, n.s.'
if text.count(en24_old) != 1:
    raise SystemExit(f'Unexpected EN slide 24 caption count: {text.count(en24_old)}')
text = text.replace(en24_old, en24_new)

INDEX.write_text(text, encoding='utf-8')

# Add sample size labels inside the two TWIXAV SVGs.
svg = Path('assets/results/twixav_empirical_curves.svg')
s = svg.read_text(encoding='utf-8')
if 'n = 20' not in s:
    s = s.replace('</svg>', '<text x="500" y="31" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="800" text-anchor="middle" fill="#26342d">n = 20</text></svg>')
svg.write_text(s, encoding='utf-8')

svg = Path('assets/results/twixav_tbw_width.svg')
s = svg.read_text(encoding='utf-8')
if 'n = 20' not in s:
    s = s.replace('</svg>', '<text x="855" y="30" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="800" text-anchor="end" fill="#26342d">n = 20</text></svg>')
svg.write_text(s, encoding='utf-8')

# VIBEX slide 23 - remove the footer sentence and add n = 24 at the top.
svg = Path('assets/results/vibex_m1_olivia.svg')
s = svg.read_text(encoding='utf-8')
footer = '<text x="430" y="505" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#1d6143">LL-SS et SL-LS reliées séparément - moyenne et SEM</text>'
if footer not in s:
    raise SystemExit('VIBEX slide 23 footer not found')
s = s.replace(footer, '')
if 'n = 24' not in s:
    s = s.replace('</svg>', '<text x="880" y="34" text-anchor="end" font-family="Arial" font-size="16" font-weight="800" fill="#26342d">n = 24</text></svg>')
s = s.replace('<title>VIBEX - condition et taille</title>', '<title>Taux moyen de réponses Identiques selon la condition et la taille</title>')
svg.write_text(s, encoding='utf-8')

# VIBEX slide 24 - add n = 24 at the top.
svg = Path('assets/results/vibex_size_interaction.svg')
s = svg.read_text(encoding='utf-8')
if 'n = 24' not in s:
    s = s.replace('</svg>', '<text x="880" y="34" text-anchor="end" font-family="Arial" font-size="16" font-weight="800" fill="#26342d">n = 24</text></svg>')
s = s.replace('<title>VIBEX - condition par taille</title>', '<title>Taux moyen de réponses Identiques selon la condition et la taille</title>')
svg.write_text(s, encoding='utf-8')

print('Figure sample sizes, VIBEX captions, and slide 23 footer updated successfully')
