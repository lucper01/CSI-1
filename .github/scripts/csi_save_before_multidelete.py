from pathlib import Path
src=Path('index.html')
dst=Path('index_save.html')
dst.write_bytes(src.read_bytes())
print('Saved current index.html into index_save.html')
# trigger
