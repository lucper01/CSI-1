from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')

replacements = [
    (
        'Largeur individuelle moyenne de la TBW - moyenne ± erreur-type rapportée dans le mémoire.',
        'Largeur individuelle moyenne de la TBW.'
    ),
    (
        'La progression relie les acquis de l’année 1 aux études centrales suivantes sans ouvrir prématurément les extensions conditionnelles.',
        'L’année 2 s’appuie directement sur TWIXAV et VIBEX pour engager trois études prioritaires : SOFT, OASIS et TWIXOLF.'
    ),
    (
        'Deux axes et une lecture temporelle simple : les dates sont portées par la frise, les encarts identifient uniquement les études.',
        'Le calendrier organise les études selon les deux axes de la thèse et leur ordre de mise en œuvre jusqu’en 2028.'
    ),
    (
        'Merci aux membres du Comité de Suivi Individuel pour leur lecture et leurs échanges.',
        'Merci aux membres du Comité de Suivi Individuel pour leur attention et leurs échanges.'
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f'Missing target: {old}')
    text = text.replace(old, new)
    print(f'Replaced {count} occurrence(s): {old[:70]}')

for old, new in replacements:
    assert old not in text
    assert new in text

p.write_text(text, encoding='utf-8')
print('OK - oral wording updated')
