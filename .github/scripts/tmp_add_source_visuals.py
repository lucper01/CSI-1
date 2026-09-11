from __future__ import annotations

import hashlib
import html
import json
import os
import pathlib
import re
import urllib.request

from PIL import Image

ROOT = pathlib.Path('.')
INDEX = ROOT / 'index.html'
SAVE = ROOT / 'index_save.html'
VIS = ROOT / 'assets' / 'visuals'
RUNTIME = ROOT / 'assets' / 'csi-source-visuals.js'
SOURCES = VIS / 'SOURCES.md'

VIS.mkdir(parents=True, exist_ok=True)

assets = {
    'eye': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Gray_Auge.jpg',
        'file': 'eye-gray.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Gray_Auge.jpg',
        'credit': "Henry Gray / Henry Vandyke Carter - Gray's Anatomy",
        'license': 'Public domain',
        'alt_fr': "Coupe anatomique de l’œil humain",
        'alt_en': 'Anatomical cross-section of the human eye',
    },
    'ear': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Gray907.png',
        'file': 'ear-gray.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Gray907.png',
        'credit': "Henry Gray / Henry Vandyke Carter - Gray's Anatomy, plate 907",
        'license': 'Public domain',
        'alt_fr': "Coupe anatomique de l’oreille humaine",
        'alt_en': 'Anatomical cross-section of the human ear',
    },
    'nose': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/6/66/Nose_and_nasal_cavities.png',
        'file': 'nose-nasal-cavities.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Nose_and_nasal_cavities.png',
        'credit': 'U.S. National Cancer Institute / SEER',
        'license': 'Public domain - U.S. Government work',
        'alt_fr': 'Schéma anatomique du nez et des cavités nasales',
        'alt_en': 'Anatomical diagram of the nose and nasal cavities',
    },
    'brain': {
        'url': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Smith.PNG',
        'file': 'cortical-topography.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Smith.PNG',
        'credit': 'G. Elliot Smith - A New Topographical Survey of the Human Cerebral Cortex (1907)',
        'license': 'Public domain',
        'alt_fr': 'Topographie du cortex cérébral humain',
        'alt_en': 'Topography of the human cerebral cortex',
    },
    'lecture': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Ohio_University_Lecture_Hall.jpg',
        'file': 'lecture-hall.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Ohio_University_Lecture_Hall.jpg',
        'credit': 'Garden Sprite',
        'license': 'CC0 1.0',
        'alt_fr': 'Amphithéâtre universitaire',
        'alt_en': 'University lecture hall',
    },
    'microphone': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/1/18/FEMA_-_39463_-_Microphones_at_the_podium.jpg',
        'file': 'conference-microphones.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:FEMA_-_39463_-_Microphones_at_the_podium.jpg',
        'credit': 'Bill Koplitz / FEMA',
        'license': 'Public domain - U.S. Government work',
        'alt_fr': 'Microphones sur un pupitre de conférence',
        'alt_en': 'Microphones at a conference podium',
    },
    'landscape': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Lake_Mountain_Landscape.jpg/1280px-Lake_Mountain_Landscape.jpg',
        'file': 'boundary-landscape.webp',
        'source': 'https://commons.wikimedia.org/wiki/File:Lake_Mountain_Landscape.jpg',
        'credit': 'Bonnie Moreland',
        'license': 'CC0 1.0',
        'alt_fr': 'Photographie de paysage avec lac, forêt et montagne',
        'alt_en': 'Landscape photograph with lake, forest and mountain',
    },
}


def download(url: str, dest: pathlib.Path) -> None:
    req = urllib.request.Request(url, headers={'User-Agent': 'CSI-STOLF-visual-assets/1.0 (educational presentation)'})
    with urllib.request.urlopen(req, timeout=45) as response:
        dest.write_bytes(response.read())


def convert(src: pathlib.Path, dest: pathlib.Path, kind: str) -> None:
    with Image.open(src) as im:
        im.load()
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
        max_px = 1500 if kind in {'lecture', 'microphone', 'landscape'} else 900
        im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
        if im.mode == 'RGBA':
            bg = Image.new('RGB', im.size, 'white')
            bg.paste(im, mask=im.getchannel('A'))
            im = bg
        else:
            im = im.convert('RGB')
        im.save(dest, 'WEBP', quality=82, method=6)

for key, meta in assets.items():
    tmp = pathlib.Path('/tmp') / ('csi_' + key + pathlib.Path(meta['url'].split('?')[0]).suffix)
    download(meta['url'], tmp)
    convert(tmp, VIS / meta['file'], key)

runtime = r'''(() => {
  'use strict';

  const MARK = 'csi-source-visuals-v1';
  if (window[MARK]) return;
  window[MARK] = true;

  const A = {
    eye: {src:'assets/visuals/eye-gray.webp', fr:'Coupe anatomique de l’œil humain', en:'Anatomical cross-section of the human eye', source:'Gray’s Anatomy - domaine public'},
    ear: {src:'assets/visuals/ear-gray.webp', fr:'Coupe anatomique de l’oreille humaine', en:'Anatomical cross-section of the human ear', source:'Gray’s Anatomy - domaine public'},
    nose: {src:'assets/visuals/nose-nasal-cavities.webp', fr:'Nez et cavités nasales', en:'Nose and nasal cavities', source:'NCI/SEER - domaine public'},
    brain: {src:'assets/visuals/cortical-topography.webp', fr:'Topographie du cortex cérébral', en:'Topography of the cerebral cortex', source:'G. Elliot Smith, 1907 - domaine public'},
    lecture: {src:'assets/visuals/lecture-hall.webp', fr:'Amphithéâtre universitaire', en:'University lecture hall', source:'Garden Sprite - CC0'},
    microphone: {src:'assets/visuals/conference-microphones.webp', fr:'Microphones de conférence', en:'Conference microphones', source:'Bill Koplitz/FEMA - domaine public'},
    landscape: {src:'assets/visuals/boundary-landscape.webp', fr:'Paysage naturel', en:'Natural landscape', source:'Bonnie Moreland - CC0'}
  };

  const style = document.createElement('style');
  style.id = 'csi-source-visuals-style';
  style.textContent = `
    .slide{isolation:isolate}
    .csi-source-visual{position:absolute;z-index:0;pointer-events:none;margin:0;overflow:hidden;opacity:var(--csi-vis-opacity,.16);filter:saturate(.78) contrast(.94);transition:opacity .2s ease}
    .slide>*:not(.csi-source-visual){position:relative;z-index:1}
    .csi-source-visual img{display:block;width:100%;height:100%;object-fit:contain}
    .csi-source-visual.anatomy{width:clamp(150px,17vw,250px);height:clamp(130px,15vw,220px);right:clamp(24px,3vw,54px);bottom:clamp(62px,7vh,90px);background:rgba(255,255,255,.54);border-radius:28px;padding:12px;mix-blend-mode:multiply}
    .csi-source-visual.anatomy.soft{--csi-vis-opacity:.105}
    .csi-source-visual.photo{width:clamp(210px,22vw,330px);height:clamp(125px,14vw,200px);right:clamp(28px,3.5vw,62px);bottom:clamp(62px,7vh,94px);border-radius:24px;box-shadow:0 14px 34px rgba(11,47,35,.12);border:1px solid rgba(255,255,255,.62);--csi-vis-opacity:.16}
    .csi-source-visual.photo img{object-fit:cover}
    .csi-source-visual.duo-a{right:clamp(135px,12vw,205px);bottom:clamp(64px,7vh,92px);width:clamp(118px,12vw,175px);height:clamp(105px,11vw,155px);--csi-vis-opacity:.11}
    .csi-source-visual.duo-b{right:clamp(28px,3vw,55px);bottom:clamp(84px,9vh,118px);width:clamp(118px,12vw,175px);height:clamp(105px,11vw,155px);--csi-vis-opacity:.11}
    .csi-source-visual.study-photo{width:clamp(190px,19vw,290px);height:clamp(112px,12vw,172px);right:clamp(26px,3vw,54px);top:clamp(112px,15vh,154px);bottom:auto;--csi-vis-opacity:.13}
    .csi-source-visual.activity-photo{width:clamp(210px,21vw,320px);height:clamp(130px,14vw,205px);right:clamp(26px,3vw,56px);bottom:clamp(62px,7vh,90px);--csi-vis-opacity:.12}
    .csi-source-visual.activity-mic{width:clamp(110px,12vw,170px);height:clamp(100px,11vw,160px);right:clamp(205px,18vw,310px);bottom:clamp(70px,8vh,105px);--csi-vis-opacity:.09}
    html[data-theme="dark"] .csi-source-visual.anatomy{mix-blend-mode:screen;background:rgba(255,255,255,.06);filter:grayscale(1) invert(1) contrast(.82)}
    html[data-theme="dark"] .csi-source-visual.photo{filter:saturate(.55) brightness(.72)}
    body.high-contrast .csi-source-visual{display:none!important}
    @media(max-width:900px){.csi-source-visual{opacity:.07!important}.csi-source-visual.photo{width:180px;height:110px}.csi-source-visual.anatomy{width:145px;height:125px}}
    @media print{.csi-source-visual{opacity:.11!important}}
  `;
  document.head.appendChild(style);

  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const metaFor = index => {
    let s = null;
    try { s = Array.isArray(slides) ? slides[index] : null; } catch (_) {}
    return s || {};
  };
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

    // Theoretical framework: sensory anatomy as a very light visual watermark.
    if (/vision et audition|vision and audition|deux organisations spatio-temporelles|two spatio-temporal organizations/.test(title)) {
      add(slideEl, 'eye', 'anatomy duo-a', 'a');
      add(slideEl, 'ear', 'anatomy duo-b', 'b');
    } else if (/^le temps|^time -|synchronie|synchrony/.test(title) && !study) {
      add(slideEl, 'brain', 'anatomy soft', 'time');
    } else if (/^l.?espace|^space -/.test(title) && !study) {
      add(slideEl, 'eye', 'anatomy soft', 'space');
    } else if (/espace \+ temps|space \+ time|un seul evenement|single event/.test(title) && !study) {
      add(slideEl, 'brain', 'anatomy soft', 'integration');
    } else if (/no space, no time|less space, less time|moins d.?espace|olfact/.test(title) && /theorique|theoretical|olfact/.test(section + ' ' + kicker + ' ' + title)) {
      add(slideEl, 'nose', 'anatomy', 'olfaction');
    }

    // Experimental sections: only method/introduction slides receive illustrations so figures/results stay clean.
    if (study === 'vibex' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'landscape', 'photo study-photo', 'vibex');
    }
    if (study === 'twixav' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'eye', 'anatomy duo-a', 'twixav-eye');
      add(slideEl, 'ear', 'anatomy duo-b', 'twixav-ear');
    }
    if (study === 'soft' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'brain', 'anatomy soft', 'soft');
    }
    if (study === 'twixolf' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'nose', 'anatomy', 'twixolf');
    }
    if (study === 'vibolf' && /(intro|methode|method|paradigme|protocole|protocol)/.test(title + ' ' + kicker)) {
      add(slideEl, 'landscape', 'photo study-photo', 'vibolf-landscape');
      add(slideEl, 'nose', 'anatomy soft', 'vibolf-nose');
    }

    // Doctoral activities: real, openly licensed photographs, kept deliberately subtle.
    if (/activites doctorales|doctoral activities/.test(title)) {
      add(slideEl, 'lecture', 'photo activity-photo', 'activity-lecture');
      add(slideEl, 'microphone', 'photo activity-mic', 'activity-mic');
    }

    slideEl.dataset.sourceVisualsDone = '1';
  }

  function refresh() {
    document.querySelectorAll('#deck .slide[data-index]').forEach(decorate);
  }

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

src_lines = [
    '# Visual sources used in CSI-1',
    '',
    'These assets are external photographs or historical/scientific illustrations. No generative-AI image is used by this visual layer.',
    '',
]
for key, meta in assets.items():
    src_lines += [
        f"## {key}",
        f"- File: `{meta['file']}`",
        f"- Source: {meta['source']}",
        f"- Credit: {meta['credit']}",
        f"- License: {meta['license']}",
        '',
    ]
SOURCES.write_text('\n'.join(src_lines), encoding='utf-8')

index = INDEX.read_text(encoding='utf-8')
script_tag = '  <script src="assets/csi-source-visuals.js?v=1"></script>\n'
if 'assets/csi-source-visuals.js' not in index:
    anchor = '  <script src="assets/csi-export.js?v=1"></script>'
    if anchor not in index:
        raise SystemExit('Could not find export script anchor in index.html')
    index = index.replace(anchor, script_tag + anchor, 1)
    INDEX.write_text(index, encoding='utf-8')

print('Integrated sourced visual assets:', ', '.join(assets))
print('index sha256:', hashlib.sha256(INDEX.read_bytes()).hexdigest())
print('save sha256 :', hashlib.sha256(SAVE.read_bytes()).hexdigest())
