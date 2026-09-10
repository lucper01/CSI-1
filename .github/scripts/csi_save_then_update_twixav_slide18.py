from pathlib import Path
import json

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
arr, end_rel = json.JSONDecoder().raw_decode(text[start:])

matches = [s for s in arr if s.get('kicker') == 'TWIXAV - Résultats' and s.get('title') == 'TWIXAV - Temporal Binding Window']
if len(matches) != 1:
    raise SystemExit(f'Expected exactly one TWIXAV results slide, found {len(matches)}')
slide = matches[0]

def replace_once(value, old, new, label):
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}: {old}')
    return value.replace(old, new, 1)

def update_fr(value):
    reps = [
        ('alt="Courbes empiriques du taux de simultanéité selon le SOA et la durée"', 'alt="Taux moyen de réponse simultané selon le SOA et selon la durée"', 'FR alt figure 1'),
        ('Probabilité de réponse « simultané » selon le décalage et la durée.', 'Taux moyen de réponse « simultané » selon le SOA et selon la durée.', 'FR caption figure 1'),
        ('alt="Largeur moyenne de la TBW selon la durée"', 'alt="FWHM moyenne de la TBW selon la durée"', 'FR alt figure 2'),
        ('La largeur moyenne de la TBW diminue avec la durée. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).', 'FWHM moyenne de la TBW selon la durée. Les barres d’erreur correspondent à l’erreur standard de la moyenne (SEM).', 'FR caption figure 2'),
        ('<div><b>p &lt; .001</b><span>effet du décalage temporel</span></div>', '<div><span>effet du décalage temporel</span><b>p &lt; .001</b></div>', 'FR stat offset'),
        ('<div><b>p &lt; .001</b><span>effet de la durée</span></div>', '<div><span>effet de la durée</span><b>p &lt; .001</b></div>', 'FR stat duration'),
        ('<div><b>p = .001</b><span>interaction décalage × durée</span></div>', '<div><span>interaction décalage × durée</span><b>p = .001</b></div>', 'FR stat interaction'),
        ('<div><b>p &lt; .001</b><span>effet de la durée sur la largeur de TBW</span></div>', '<div><span>effet de la durée sur la FWHM de la TBW</span><b>p &lt; .001</b></div>', 'FR stat FWHM'),
    ]
    for old, new, label in reps:
        value = replace_once(value, old, new, label)
    return value

def update_en(value):
    reps = [
        ('alt="Courbes empiriques du taux de simultanéité selon le SOA et la durée"', 'alt="Mean simultaneous-response rate by SOA and duration"', 'EN alt figure 1'),
        ('Probabilité de réponse « simultané » selon le décalage et la durée.', 'Mean rate of “simultaneous” responses by SOA and duration.', 'EN caption figure 1'),
        ('alt="Largeur moyenne de la TBW selon la durée"', 'alt="Mean TBW FWHM by duration"', 'EN alt figure 2'),
        ('Mean TBW width decreases with duration. Error bars represent the standard error of the mean (SEM).', 'Mean TBW FWHM by duration. Error bars represent the standard error of the mean (SEM).', 'EN caption figure 2'),
        ('<div><b>p &lt; .001</b><span>temporal-offset effect</span></div>', '<div><span>temporal-offset effect</span><b>p &lt; .001</b></div>', 'EN stat offset'),
        ('<div><b>p &lt; .001</b><span>duration effect</span></div>', '<div><span>duration effect</span><b>p &lt; .001</b></div>', 'EN stat duration'),
        ('<div><b>p = .001</b><span>offset × duration interaction</span></div>', '<div><span>offset × duration interaction</span><b>p = .001</b></div>', 'EN stat interaction'),
        ('<div><b>p &lt; .001</b><span>duration effect sur la largeur de TBW</span></div>', '<div><span>duration effect on TBW FWHM</span><b>p &lt; .001</b></div>', 'EN stat FWHM'),
    ]
    for old, new, label in reps:
        value = replace_once(value, old, new, label)
    return value

slide['content'] = update_fr(slide['content'])
slide['_fr']['content'] = update_fr(slide['_fr']['content'])
slide['_en']['content'] = update_en(slide['_en']['content'])

new_arr = json.dumps(arr, ensure_ascii=False, indent=2)
new_text = text[:start] + new_arr + text[start + end_rel:]
path.write_text(new_text, encoding='utf-8')

# Final semantic guards.
out = path.read_text(encoding='utf-8')
for required in [
    'Taux moyen de réponse « simultané » selon le SOA et selon la durée.',
    'FWHM moyenne de la TBW selon la durée.',
    '<span>effet du décalage temporel</span><b>p &lt; .001</b>',
    '<span>effet de la durée sur la FWHM de la TBW</span><b>p &lt; .001</b>',
]:
    if required not in out:
        raise SystemExit(f'Missing required final text: {required}')
print('TWIXAV slide 18 updated successfully')
