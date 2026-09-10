from pathlib import Path

source = Path('index.html')
target = Path('index_save.html')

data = source.read_bytes()
target.write_bytes(data)
print(f'Saved {len(data)} bytes from {source} to {target}')
