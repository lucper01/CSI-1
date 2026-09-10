from pathlib import Path
import json

p = Path('index.html')
text = p.read_text(encoding='utf-8')
marker = 'const slides = '
pos = text.index(marker) + len(marker)
slides, consumed = json.JSONDecoder().raw_decode(text[pos:])
main = [s for s in slides if not s.get('appendix', False)]
targets = [s for s in main if s.get('_fr', {}).get('title') == 'STOLF - des axes aux études']
assert len(targets) == 1
target = targets[0]
assert main.index(target) == 34, f'Expected slide 35, got {main.index(target)+1}'

css = r'''<style>
.stolf-map-v2{width:min(1060px,96%);margin:0 auto;position:relative;--connector:color-mix(in srgb,var(--accent-strong) 24%,transparent)}
.stolf-map-v2 *{box-sizing:border-box}
.stolf-map-v2 .root-zone{position:relative;display:flex;justify-content:center;margin-bottom:34px}
.stolf-map-v2 .root-shell{position:relative;z-index:3;display:flex;align-items:center;justify-content:center;width:300px;min-height:68px;padding:11px 18px;border:1px solid var(--line);border-radius:24px;background:var(--white);box-shadow:var(--shadow-soft)}
.stolf-map-v2 .root-chip{display:inline-flex;align-items:center;justify-content:center;min-width:180px;padding:10px 24px;border-radius:999px;background:var(--accent-strong);color:#fff;font-weight:950;font-size:1.45rem;letter-spacing:.07em}
.stolf-map-v2 .root-zone:after{content:"";position:absolute;z-index:1;left:50%;top:68px;width:1px;height:34px;background:var(--connector)}
.stolf-map-v2 .branches{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:58px}
.stolf-map-v2 .branches:before{content:"";position:absolute;z-index:0;left:25%;right:25%;top:-18px;height:1px;background:var(--connector)}
.stolf-map-v2 .axis{position:relative;display:flex;flex-direction:column;align-items:center;min-width:0}
.stolf-map-v2 .axis:before{content:"";position:absolute;z-index:0;top:-18px;left:50%;width:1px;height:22px;background:var(--connector)}
.stolf-map-v2 .axis-card{position:relative;z-index:2;width:min(430px,100%);min-height:94px;padding:16px 20px 17px;border:1px solid var(--line);border-radius:24px;background:var(--white);box-shadow:var(--shadow-soft);text-align:center}
.stolf-map-v2 .axis-label{display:inline-flex;align-items:center;justify-content:center;padding:5px 11px;border-radius:999px;background:var(--accent-soft);color:var(--accent-strong);font-size:.72rem;font-weight:950;letter-spacing:.08em;text-transform:uppercase}
.stolf-map-v2 .axis-title{margin:9px auto 0;max-width:360px;color:var(--accent-strong);font:800 1.04rem/1.25 Georgia,"Times New Roman",serif}
.stolf-map-v2 .study-chain{position:relative;width:min(290px,82%);margin-top:16px;display:grid;gap:12px}
.stolf-map-v2 .study-chain:before{content:"";position:absolute;z-index:0;left:50%;top:-16px;bottom:22px;width:1px;background:var(--connector)}
.stolf-map-v2 .study-shell{--study:var(--accent);position:relative;z-index:2;display:flex;align-items:center;justify-content:center;min-height:52px;padding:8px 14px;border:1px solid var(--line);border-radius:18px;background:var(--white);box-shadow:0 7px 18px color-mix(in srgb,var(--accent-strong) 7%,transparent)}
.stolf-map-v2 .study-chip{display:inline-flex;align-items:center;justify-content:center;min-width:126px;padding:7px 15px;border-radius:999px;background:var(--study);color:#fff;font-size:.87rem;font-weight:950;letter-spacing:.035em;box-shadow:0 3px 8px color-mix(in srgb,var(--study) 17%,transparent);opacity:1}
.stolf-map-v2 .study-shell.faded .study-chip{opacity:.30}
.stolf-map-v2 .study-shell.focus{box-shadow:0 9px 23px color-mix(in srgb,var(--accent-strong) 10%,transparent)}
.stolf-map-v2 .twixav{--study:#2f6f9f}.stolf-map-v2 .soft{--study:#7652a8}.stolf-map-v2 .twixolf{--study:#c36c32}.stolf-map-v2 .solar{--study:#d09422}.stolf-map-v2 .vibex{--study:#2f7d5a}.stolf-map-v2 .vibolf{--study:#b44e6c}.stolf-map-v2 .braud{--study:#4f7187}.stolf-map-v2 .braudolf{--study:#875a7c}
@media(max-width:900px){.stolf-map-v2{width:100%}.stolf-map-v2 .branches{gap:26px}.stolf-map-v2 .axis-card{padding:13px 14px;min-height:90px}.stolf-map-v2 .axis-title{font-size:.9rem}.stolf-map-v2 .study-chain{width:88%}.stolf-map-v2 .study-shell{min-height:46px}.stolf-map-v2 .study-chip{font-size:.8rem;min-width:108px}}
</style>'''

fr = css + r'''
<div class="stolf-map-v2">
  <div class="root-zone"><div class="root-shell"><span class="root-chip">STOLF</span></div></div>
  <div class="branches">
    <section class="axis">
      <div class="axis-card">
        <span class="axis-label">Axe 1</span>
        <h3 class="axis-title">Relations spatio-temporelles entre Olfaction, Vision, Audition</h3>
      </div>
      <div class="study-chain">
        <div class="study-shell twixav faded" data-study="TWIXAV"><span class="study-chip">TWIXAV</span></div>
        <div class="study-shell soft faded" data-study="SOFT"><span class="study-chip">SOFT</span></div>
        <div class="study-shell twixolf faded" data-study="TWIXOLF"><span class="study-chip">TWIXOLF</span></div>
        <div class="study-shell solar focus" data-study="SOLAR"><span class="study-chip">SOLAR</span></div>
      </div>
    </section>
    <section class="axis">
      <div class="axis-card">
        <span class="axis-label">Axe 2</span>
        <h3 class="axis-title">Influence des odeurs sur la perception spatio-temporelle en Audition et Vision</h3>
      </div>
      <div class="study-chain">
        <div class="study-shell vibex faded" data-study="VIBEX"><span class="study-chip">VIBEX</span></div>
        <div class="study-shell vibolf faded" data-study="VIBOLF"><span class="study-chip">VIBOLF</span></div>
        <div class="study-shell braud focus" data-study="BRAUD"><span class="study-chip">BRAUD</span></div>
        <div class="study-shell braudolf focus" data-study="BRAUDOLF"><span class="study-chip">BRAUDOLF</span></div>
      </div>
    </section>
  </div>
</div>'''

en = css + r'''
<div class="stolf-map-v2">
  <div class="root-zone"><div class="root-shell"><span class="root-chip">STOLF</span></div></div>
  <div class="branches">
    <section class="axis">
      <div class="axis-card">
        <span class="axis-label">Axis 1</span>
        <h3 class="axis-title">Spatio-temporal relationships between Olfaction, Vision and Audition</h3>
      </div>
      <div class="study-chain">
        <div class="study-shell twixav faded" data-study="TWIXAV"><span class="study-chip">TWIXAV</span></div>
        <div class="study-shell soft faded" data-study="SOFT"><span class="study-chip">SOFT</span></div>
        <div class="study-shell twixolf faded" data-study="TWIXOLF"><span class="study-chip">TWIXOLF</span></div>
        <div class="study-shell solar focus" data-study="SOLAR"><span class="study-chip">SOLAR</span></div>
      </div>
    </section>
    <section class="axis">
      <div class="axis-card">
        <span class="axis-label">Axis 2</span>
        <h3 class="axis-title">Influence of odors on spatio-temporal perception in Audition and Vision</h3>
      </div>
      <div class="study-chain">
        <div class="study-shell vibex faded" data-study="VIBEX"><span class="study-chip">VIBEX</span></div>
        <div class="study-shell vibolf faded" data-study="VIBOLF"><span class="study-chip">VIBOLF</span></div>
        <div class="study-shell braud focus" data-study="BRAUD"><span class="study-chip">BRAUD</span></div>
        <div class="study-shell braudolf focus" data-study="BRAUDOLF"><span class="study-chip">BRAUDOLF</span></div>
      </div>
    </section>
  </div>
</div>'''

target['_fr']['content'] = fr
target['_en']['content'] = en
target['content'] = fr
target['_fr']['notes'] = 'Présenter les intitulés officiels des deux axes. Les études apparaissent dans des cartes neutres avec leur vignette de couleur. TWIXAV, SOFT, TWIXOLF, VIBEX et VIBOLF sont atténués uniquement par transparence de leur vignette ; SOLAR, BRAUD et BRAUDOLF restent à pleine opacité.'
target['_en']['notes'] = 'Present the official titles of both axes. Studies appear in neutral cards with their colored badge. TWIXAV, SOFT, TWIXOLF, VIBEX and VIBOLF are faded only through badge opacity; SOLAR, BRAUD and BRAUDOLF remain fully opaque.'
target['notes'] = target['_fr']['notes']

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
p.write_text(text[:pos] + new_array + text[pos+consumed:], encoding='utf-8')
