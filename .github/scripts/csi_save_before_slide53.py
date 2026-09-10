from pathlib import Path
src = Path('index.html')
dst = Path('index_save.html')
data = src.read_bytes()
dst.write_bytes(data)
print(f'Saved {len(data)} bytes')
