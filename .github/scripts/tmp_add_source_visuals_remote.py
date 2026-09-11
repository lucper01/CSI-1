from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path('.')
INDEX = ROOT / 'index.html'
SAVE = ROOT / 'index_save.html'
RUNTIME = ROOT / 'assets' / 'csi-source-visuals.js'
SOURCES = ROOT / 'assets' / 'visuals' / 'SOURCES.md'
SOURCES.parent.mkdir(parents=True, exist_ok=True)

runtime = r'''(() => {
  'use strict';
  const MARK = 'csi-source-visuals-v1';
  if (window[MARK]) return;
  window[MARK] = true;

  const A = {
    eye: {src:'https://upload.wikimedia.org/wikipedia/commons/e/ec/Gray_Auge.jpg', fr:'Coupe anatomique de l’œil humain', en:'Anatomical cross-section of the human eye', source:'Gray’s Anatomy - domaine public'},
    ear: {src:'https://upload.wikimedia.org/wikipedia/commons/2/29/Gray907.png', fr:'Coupe anatomique de l’oreille humaine', en:'Anatomical cross-section of the human ear', source:'Gray’s Anatomy - domaine public'},
    nose: {src:'https://upload.wikimedia.org/wikipedia/commons/6/66/Nose_and_nasal_cavities.png', fr:'Nez et cavités nasales', en:'Nose and nasal cavities', source:'NCI/SEER - domaine public'},
    lecture: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Ohio_University_Lecture_Hall.jpg/1280px-Ohio_University_Lecture_Hall.jpg', fr:'Amphithéâtre universitaire', en:'University lecture hall', source:'Garden Sprite - CC0'},
    microphone: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/FEMA_-_39463_-_Microphones_at_the_podium.jpg/960px-FEMA_-_39463_-_Microphones_at_the_podium.jpg', fr:'Microphones de conférence', en:'Conference microphones', source:'Bill Koplitz/FEMA - domaine public'},
    landscape: {src:'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Lake_Mountain_Landscape.jpg/1280px-Lake_Mountain_Landscape.jpg', fr:'Paysage naturel', en:'Natural landscape', source:'Bonnie Moreland - CC0'}
  };

  const style = document.createElement('style');
  style.id = 'csi-source-visuals-style';
  style.textContent = `
    .slide{isolation:isolate}
    .csi-source-visual{position:absolute;z-index:0;pointer-events:none;margin:0;overflow:hidden;opacity:var(--csi-vis-opacity,.16);filter:saturate(.78) contrast(.94);transition:opacity .2s ease}
    .slide>*:not(.csi-source-visual){position:relative;z-index:1}
    .csi-source-visual img{display:block;width:100%;height:100%;object-fit:contain}
    .csi-source-visual.anatomy{width:clamp(150px,17vw,250px);height:clamp(130px,15vw,220px);right:clamp(24px,3vw,54px);bottom:clamp(62px,7vh,90px);background:rgba(255,255,255,.52);border-radius:28px;padding:12px;mix-blend-mode:multiply}
    .csi-source-visual.anatomy.soft{--csi-vis-opacity:.095}
    .csi-source-visual.photo{width:clamp(210px,22vw,330px);height:clamp(125px,14vw,200px);right:clamp(28px,3.5vw,62px);bottom:clamp(62px,7vh,94px);border-radius:24px;box-shadow:0 14px 34px rgba(11,47,35,.12);border:1px solid rgba(255,255,255,.62);--csi-vis-opacity:.15}
    .csi-source-visual.photo img{object-fit:cover}
    .csi-source-visual.duo-a{right:clamp(135px,12vw,205px);bottom:clamp(64px,7vh,92px);width:clamp(118px,12vw,175px);height:clamp(105px,11vw,155px);--csi-vis-opacity:.095}
    .csi-source-visual.duo-b{right:clamp(28px,3vw,55px);bottom:clamp(84px,9vh,118px);width:clamp(118px,12vw,175px);height:clamp(105px,11vw,155px);--csi-vis-opacity:.095}
    .csi-source-visual.study-photo{width:clamp(190px,19vw,290px);height:clamp(112px,12vw,172px);right:clamp(26px,3vw,54px);top:clamp(112px,15vh,154px);bottom:auto;--csi-vis-opacity:.12}
    .csi-source-visual.activity-photo{width:clamp(210px,21vw,320px);height:clamp(130px,14vw,205px);right:clamp(26px,3vw,56px);bottom:clamp(62px,7vh,90px);--csi-vis-opacity:.115}
    .csi-source-visual.activity-mic{width:clamp(110px,12vw,170px);height:clamp(100px,11vw,160px);right:clamp(205px,18vw,310px);bottom:clamp(70px,8vh,105px);--csi-vis-opacity:.075}
    html[data-theme="dark"] .csi-source-visual.anatomy{mix-blend-mode:screen;background:rgba(255,255,255,.05);filter:grayscale(1) invert(1) contrast(.82)}
    html[data-theme="dark"] .csi-source-visual.photo{filter:saturate(.55) brightness(.72)}
    body.high-contrast .csi-source-visual{display:none!important}
    @media(max-width:900px){.csi-source-visual{opacity:.06!important}.csi-source-visual.photo{width:180px;height:110px}.csi-source-visual.anatomy{width:145px;height:125px}}
    @media print{.csi-source-visual{opacity:.10!important}}
  `;
  document.head.appendChild(style);

  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const metaFor = index => { try { return Array.isArray(slides) ? (slides[index] || {}) : {}; } catch (_) { return {}; } };
  const lang = () => document.documentElement.lang === 'en' ? 'en' : 'fr';

  function add(slideEl, assetKey, cls, slot='') {
    const asset = A[assetKey];
    if (!asset || slideEl.querySelector(`.csi-source-visual[data-asset="${assetKey}"][data-slot="${slot}"]`)) return;
    const fig = document.createElement('figure');
    fig.className = `csi-source-visual ${cls}`;
    fig.dataset.asset = assetKey;
    fig.dataset.slot = slot;
    fig.title = asset.source;
    const img = document.createElement('img');
    img.src = asset.src;
    img.alt = lang() === 'en' ? asset.en : asset.fr;
    img.loading = 'eager';
    img.decoding = 'async';
    fig.appendChild(img);
    slideEl.appendChild(fig);
  }

  function decorate(slideEl) {
    if (!slideEl || slideEl.dataset.sourceVisualsDone === '1') return;
    const index = Number(slideEl.dataset.index);
    if (!Number.isInteger(index)) return;
    const s = metaFor(index);
    const title = norm(s.title);
    const kicker = norm(s.kicker);
    const section = norm(s.section || s.chapter);
    const study = norm(s.study);

    if (/vision et audition|vision and audition|deux organisations spatio-temporelles|two spatio-temporal organizations/.test(title)) {
      add(slideEl, 'eye', 'anatomy duo-a', 'eye');
      add(slideEl, 'ear', 'anatomy duo-b', 'ear');
    } else if (/^le temps|^time -|synchronie|synchrony/.test(title) && !study) {
      add(slideEl, 'ear', 'anatomy soft', 'time');
    } else if (/^l.?espace|^space -/.test(title) && !study) {
      add(slideEl, 'eye', 'anatomy soft', 'space');
    } else if (/espace \+ temps|space \+ time|un seul evenement|single event/.test(title) && !study) {
      add(slideEl, 'eye', 'anatomy duo-a', 'space-time-eye');
      add(slideEl, 'ear', 'anatomy duo-b', 'space-time-ear');
    } else if (/no space, no time|less space, less time|moins d.?espace|olfact/.test(title) && /theorique|theoretical|olfact/.test(section + ' ' + kicker + ' ' + title)) {
      add(slideEl, 'nose', 'anatomy', 'olfaction');
    }

    if (study === 'vibex' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'landscape', 'photo study-photo', 'vibex');
    }
    if (study === 'twixav' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'eye', 'anatomy duo-a', 'twixav-eye');
      add(slideEl, 'ear', 'anatomy duo-b', 'twixav-ear');
    }
    if (study === 'soft' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'eye', 'anatomy duo-a', 'soft-eye');
      add(slideEl, 'ear', 'anatomy duo-b', 'soft-ear');
    }
    if (study === 'twixolf' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'nose', 'anatomy', 'twixolf');
    }
    if (study === 'vibolf' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'landscape', 'photo study-photo', 'vibolf-landscape');
      add(slideEl, 'nose', 'anatomy soft', 'vibolf-nose');
    }

    if (/activites doctorales|doctoral activities/.test(title)) {
      add(slideEl, 'lecture', 'photo activity-photo', 'activity-lecture');
      add(slideEl, 'microphone', 'photo activity-mic', 'activity-mic');
    }

    slideEl.dataset.sourceVisualsDone = '1';
  }

  function refresh() { document.querySelectorAll('#deck .slide[data-index]').forEach(decorate); }
  refresh();
  const deck = document.getElementById('deck');
  if (deck) new MutationObserver(refresh).observe(deck, {subtree:true, childList:true});
  new MutationObserver(() => {
    document.querySelectorAll('.csi-source-visual img').forEach(img => {
      const a = A[img.closest('.csi-source-visual')?.dataset.asset];
      if (a) img.alt = lang() === 'en' ? a.en : a.fr;
    });
  }).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
})();
'''
RUNTIME.write_text(runtime, encoding='utf-8')

SOURCES.write_text('''# Sources visuelles - CSI-1\n\nCette couche visuelle utilise uniquement des photographies ou illustrations existantes. Aucune image générée par IA n’est utilisée.\n\n- Œil - Henry Gray / Henry Vandyke Carter, *Gray’s Anatomy*. Domaine public. https://commons.wikimedia.org/wiki/File:Gray_Auge.jpg\n- Oreille - Henry Gray / Henry Vandyke Carter, *Gray’s Anatomy*, planche 907. Domaine public. https://commons.wikimedia.org/wiki/File:Gray907.png\n- Nez et cavités nasales - U.S. National Cancer Institute / SEER. Domaine public, œuvre du gouvernement fédéral américain. https://commons.wikimedia.org/wiki/File:Nose_and_nasal_cavities.png\n- Amphithéâtre universitaire - Garden Sprite. CC0 1.0. https://commons.wikimedia.org/wiki/File:Ohio_University_Lecture_Hall.jpg\n- Microphones de conférence - Bill Koplitz / FEMA. Domaine public, œuvre du gouvernement fédéral américain. https://commons.wikimedia.org/wiki/File:FEMA_-_39463_-_Microphones_at_the_podium.jpg\n- Paysage lac / montagne - Bonnie Moreland. CC0 1.0. https://commons.wikimedia.org/wiki/File:Lake_Mountain_Landscape.jpg\n''', encoding='utf-8')

index = INDEX.read_text(encoding='utf-8')
tag = '  <script src="assets/csi-source-visuals.js?v=1"></script>\n'
if 'assets/csi-source-visuals.js' not in index:
    anchor = '  <script src="assets/csi-export.js?v=1"></script>'
    if anchor not in index:
        raise SystemExit('export script anchor not found')
    index = index.replace(anchor, tag + anchor, 1)
    INDEX.write_text(index, encoding='utf-8')

print('Sourced visual layer integrated')
print('index:', hashlib.sha256(INDEX.read_bytes()).hexdigest())
print('save :', hashlib.sha256(SAVE.read_bytes()).hexdigest())
