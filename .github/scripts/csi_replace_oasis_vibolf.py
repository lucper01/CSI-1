from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
count = text.count('OASIS')
if count == 0:
    raise SystemExit('No OASIS occurrence found in index.html')
text = text.replace('OASIS', 'VIBOLF')
path.write_text(text, encoding='utf-8')
print(f'Replaced {count} occurrence(s) of OASIS with VIBOLF in index.html')
# trigger
