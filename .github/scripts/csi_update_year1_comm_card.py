from pathlib import Path
import hashlib

index = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')

old_fr = '<article class="tools"><b>JDD 2026</b><h3>Communications</h3></article>'
new_fr = '<article class="tools"><b>Communications</b><h3>JDD 2026</h3><p>Présentation de l’Axe 2 du projet STOLF.</p></article>'
old_en = '<article class="tools"><b>JDD 2026</b><h3>Scientific communication</h3></article>'
new_en = '<article class="tools"><b>Scientific communication</b><h3>JDD 2026</h3><p>Presentation of Axis 2 of the STOLF project.</p></article>'

assert text.count(old_fr) >= 1
assert text.count(old_en) >= 1
text = text.replace(old_fr, new_fr)
text = text.replace(old_en, new_en)

index.write_text(text, encoding='utf-8')
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before
