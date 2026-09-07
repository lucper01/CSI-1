from pathlib import Path
import hashlib

p = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
h = p.read_text(encoding='utf-8')

old_agro = 'https://dijon.uniagro.fr/images/upload/agrosup_dijon_alumni/ecole_asd/logo__agrosup_dijon_complet.jpg'
new_agro = 'assets/logos/institut-agro-dijon.webp'
old_cnrs = 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Cnrs-logo.svg'
new_cnrs = 'https://raw.githubusercontent.com/Universite-Gustave-Eiffel/NoisePlanet/d0864656c42f5aa14dec5c26bd61258c8d1129e8/assets/img/contact/cnrs.svg'

if old_agro not in h:
    raise SystemExit('old AgroSup URL not found')
if old_cnrs not in h:
    raise SystemExit('old CNRS URL not found')

h = h.replace(old_agro, new_agro)
h = h.replace('alt=\\"AgroSup Dijon\\"', 'alt=\\"L’Institut Agro Dijon\\"')
h = h.replace(old_cnrs, new_cnrs)

# Add a little width allowance for the horizontal Institut Agro logo without changing the row architecture.
marker = '</style>'
css = '''\n    /* Cover institutional logos - local Institut Agro asset + stable CNRS mark */\n    .hero-slide .v16-logo-cloud img[alt="L’Institut Agro Dijon"] { width: clamp(118px, 9.5vw, 168px); max-height: 72px; object-fit: contain; }\n    .hero-slide .v16-logo-cloud img[alt="CNRS"] { object-fit: contain; }\n'''
if css.strip() not in h:
    h = h.replace(marker, css + marker, 1)

p.write_text(h, encoding='utf-8')

if hashlib.sha256(save.read_bytes()).hexdigest() != save_before:
    raise SystemExit('index_save.html changed unexpectedly')

assert new_agro in h and old_agro not in h
assert 'L’Institut Agro Dijon' in h
assert new_cnrs in h and old_cnrs not in h
print('cover logos replaced')
