from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
assets = [
    'assets/results/twixav_empirical_curves.svg',
    'assets/results/twixav_tbw_width.svg',
    'assets/results/vibex_m1_olivia.svg',
    'assets/results/vibex_size_interaction.svg',
]
for asset in assets:
    text = text.replace(asset + '?v=axes-restored', asset + '?v=axes-restored-2')
    text = text.replace(asset, asset + '?v=axes-restored-2')
path.write_text(text, encoding='utf-8')

for asset in assets:
    needle = asset + '?v=axes-restored-2'
    if needle not in text:
        raise SystemExit(f'Missing versioned asset URL: {needle}')
print('Versioned result graph URLs in index.html')
