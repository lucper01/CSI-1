from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = {
    'Définir les critères de lancement de SORBET, SOLAR, COBEX, BRAUD et BRAUDOLF.': 'Définir les critères de lancement de SOLAR, BRAUD et BRAUDOLF.',
    'Define launch criteria for SORBET, SOLAR, COBEX, BRAUD and BRAUDOLF.': 'Define launch criteria for SOLAR, BRAUD and BRAUDOLF.',
}

for old, new in replacements.items():
    count = text.count(old)
    if count == 0:
        raise SystemExit(f'Expected slide 53 text not found: {old}')
    text = text.replace(old, new)
    print(f'Replaced {count} occurrence(s): {old} -> {new}')

path.write_text(text, encoding='utf-8')
