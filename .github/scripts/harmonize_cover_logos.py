from pathlib import Path
import re

root = Path('.')
path = root / 'index.html'
text = path.read_text(encoding='utf-8')

# Use the exact CNRS logo supplied by the user and already stored locally.
old_cnrs = 'https://raw.githubusercontent.com/Universite-Gustave-Eiffel/NoisePlanet/d0864656c42f5aa14dec5c26bd61258c8d1129e8/assets/img/contact/cnrs.svg'
text = text.replace(old_cnrs, 'assets/logos/cnrs-logo.png')

# Remove any previous temporary harmonization block before inserting the final one.
text = re.sub(r'\n?<style id="cover-logo-harmonization-v[0-9]+">.*?</style>\n?', '\n', text, flags=re.S)

css = r'''
<style id="cover-logo-harmonization-v4">
  /* Cover - consistent cards and balanced visual size for institutional logos */
  .hero-slide .v16-logo-cloud {
    display:flex!important;
    align-items:center!important;
    gap:10px!important;
    flex-wrap:wrap!important;
    margin-top:22px!important;
  }
  .hero-slide .v16-logo-cloud img {
    display:block!important;
    width:116px!important;
    height:62px!important;
    min-width:116px!important;
    max-width:116px!important;
    min-height:62px!important;
    max-height:62px!important;
    flex:0 0 116px!important;
    box-sizing:border-box!important;
    padding:7px 10px!important;
    border-radius:14px!important;
    background:#fff!important;
    object-fit:contain!important;
    object-position:center!important;
    box-shadow:none!important;
  }
  /* The supplied CNRS PNG contains transparent margins: crop only those margins. */
  .hero-slide .v16-logo-cloud img[alt="CNRS"] {
    padding:6px 20px!important;
    object-fit:cover!important;
    object-position:center!important;
  }
  /* The Institut Agro source is square although the visible wordmark is horizontal. */
  .hero-slide .v16-logo-cloud img[alt="L’Institut Agro Dijon"] {
    padding:6px 8px!important;
    object-fit:cover!important;
    object-position:center 51%!important;
  }
  @media (max-width:900px) {
    .hero-slide .v16-logo-cloud img {
      width:102px!important;
      height:56px!important;
      min-width:102px!important;
      max-width:102px!important;
      min-height:56px!important;
      max-height:56px!important;
      flex-basis:102px!important;
      padding:6px 8px!important;
    }
    .hero-slide .v16-logo-cloud img[alt="CNRS"] { padding:5px 18px!important; }
    .hero-slide .v16-logo-cloud img[alt="L’Institut Agro Dijon"] { padding:5px 7px!important; }
  }
</style>
'''
text = text.replace('</head>', css + '\n</head>', 1)

assert text.count('assets/logos/cnrs-logo.png') >= 3
assert 'cover-logo-harmonization-v4' in text
assert 'assets/logos/institut-agro-dijon.webp' in text
assert old_cnrs not in text
path.write_text(text, encoding='utf-8')
