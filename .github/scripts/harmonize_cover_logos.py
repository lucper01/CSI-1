from pathlib import Path
import base64

root = Path('.')
parts = [root / f'assets/logos/cnrs-logo.png.b64.part{i}' for i in range(1, 6)]
payload = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
cnrs = base64.b64decode(payload, validate=True)
assert len(cnrs) == 12036, f'Unexpected CNRS PNG size: {len(cnrs)}'
assert cnrs[:8] == b'\x89PNG\r\n\x1a\n'
(root / 'assets/logos/cnrs-logo.png').write_bytes(cnrs)

path = root / 'index.html'
text = path.read_text(encoding='utf-8')
old_cnrs = 'https://raw.githubusercontent.com/Universite-Gustave-Eiffel/NoisePlanet/d0864656c42f5aa14dec5c26bd61258c8d1129e8/assets/img/contact/cnrs.svg'
text = text.replace(old_cnrs, 'assets/logos/cnrs-logo.png')

style_id = 'cover-logo-harmonization-v3'
if style_id not in text:
    css = r'''
<style id="cover-logo-harmonization-v3">
  /* Cover - equal visual footprint for all institutional logos */
  .hero-slide .v16-logo-cloud {
    display:flex!important;
    align-items:center!important;
    gap:10px!important;
    flex-wrap:wrap!important;
    margin-top:22px!important;
  }
  .hero-slide .v16-logo-cloud img {
    display:block!important;
    width:108px!important;
    height:58px!important;
    min-width:108px!important;
    max-width:108px!important;
    min-height:58px!important;
    max-height:58px!important;
    flex:0 0 108px!important;
    box-sizing:border-box!important;
    padding:7px 9px!important;
    border-radius:14px!important;
    background:#fff!important;
    object-fit:contain!important;
    object-position:center!important;
    box-shadow:none!important;
  }
  .hero-slide .v16-logo-cloud img[alt="CNRS"] {
    padding:8px 24px!important;
    object-fit:contain!important;
  }
  .hero-slide .v16-logo-cloud img[alt="L’Institut Agro Dijon"] {
    object-fit:cover!important;
    object-position:center 51%!important;
    padding:7px 9px!important;
  }
  @media (max-width:900px) {
    .hero-slide .v16-logo-cloud img {
      width:96px!important;
      height:52px!important;
      min-width:96px!important;
      max-width:96px!important;
      min-height:52px!important;
      max-height:52px!important;
      flex-basis:96px!important;
    }
    .hero-slide .v16-logo-cloud img[alt="CNRS"] { padding:7px 22px!important; }
  }
</style>
'''
    text = text.replace('</head>', css + '\n</head>', 1)

assert text.count('assets/logos/cnrs-logo.png') >= 3
assert 'cover-logo-harmonization-v3' in text
assert 'assets/logos/institut-agro-dijon.webp' in text
path.write_text(text, encoding='utf-8')
