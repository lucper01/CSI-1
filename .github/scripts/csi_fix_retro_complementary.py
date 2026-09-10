from pathlib import Path

p = Path('index.html')
html = p.read_text(encoding='utf-8')
html = html.replace('Complémentaire / exploratoire', 'Complémentaire')
html = html.replace('Complementary / exploratory', 'Complementary')
p.write_text(html, encoding='utf-8')
