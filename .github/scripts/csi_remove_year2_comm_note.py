from pathlib import Path
import hashlib

index = Path('index.html')
save = Path('index_save.html')

save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')

fr = '<small>Seules les communications prévues en 2027 sont listées ici.</small>'
en = '<small>Only communications planned for 2027 are listed here.</small>'

assert text.count(fr) >= 1
assert text.count(en) >= 1
text = text.replace(fr, '')
text = text.replace(en, '')

index.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before
