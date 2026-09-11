from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

marker = 'CSI_RESPONSIVE_STAGE_4K_V1'
if marker in text:
    raise SystemExit('Responsive stage marker already present in index.html')

css = r'''/* CSI_RESPONSIVE_STAGE_4K_V1
   Large-display presentation mode.
   Slides keep the 1920x1080 desktop composition and are uniformly scaled up.
   Smaller viewports keep the existing responsive rules untouched. */
:root {
  --csi-stage-scale: 1;
  --csi-appbar-top: 16px;
  --csi-menu-top: 70px;
  --csi-ui-edge: 18px;
  --csi-footer-bottom: 12px;
  --csi-toast-bottom: 78px;
  --csi-progress-height: 4px;
}

@media (min-width: 1920px) and (min-height: 1080px) {
  body[data-view="slides"].csi-stage-scaled .deck {
    position: fixed !important;
    inset: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    overflow: hidden !important;
  }

  body[data-view="slides"].csi-stage-scaled .slide {
    position: absolute !important;
    left: 50% !important;
    top: 50% !important;
    width: 1920px !important;
    min-width: 1920px !important;
    max-width: 1920px !important;
    height: 1080px !important;
    min-height: 1080px !important;
    max-height: 1080px !important;
    margin: -540px 0 0 -960px !important;
    transform: scale(var(--csi-stage-scale)) !important;
    transform-origin: 50% 50% !important;
  }

  body[data-view="slides"].csi-stage-scaled .slide.active {
    display: flex !important;
  }

  /* One theoretical visual used viewport arithmetic. Freeze it to its 1920px geometry
     so that it scales with the slide instead of scaling twice on 4K. */
  body[data-view="slides"].csi-stage-scaled .sela-visual-stack {
    right: -208px !important;
    width: 280px !important;
  }

  /* Presentation chrome follows the same enlargement as the slide canvas. */
  body[data-view="slides"].csi-stage-scaled .appbar {
    width: 1500px !important;
    top: var(--csi-appbar-top) !important;
    transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
    transform-origin: top center !important;
  }

  body[data-view="slides"].csi-stage-scaled #csiV16Menu {
    width: 1500px !important;
    top: var(--csi-menu-top) !important;
    transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
    transform-origin: top center !important;
  }

  body[data-view="slides"].csi-stage-scaled .deck-footer {
    max-width: 1160px !important;
    bottom: var(--csi-footer-bottom) !important;
    transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
    transform-origin: bottom center !important;
  }

  body[data-view="slides"].csi-stage-scaled .nav-arrows {
    right: var(--csi-ui-edge) !important;
    bottom: var(--csi-ui-edge) !important;
    transform: scale(var(--csi-stage-scale)) !important;
    transform-origin: bottom right !important;
  }

  body[data-view="slides"].csi-stage-scaled .timer-badge {
    left: var(--csi-ui-edge) !important;
    bottom: var(--csi-ui-edge) !important;
    transform: scale(var(--csi-stage-scale)) !important;
    transform-origin: bottom left !important;
  }

  body[data-view="slides"].csi-stage-scaled .footer-progress {
    height: var(--csi-progress-height) !important;
  }

  body[data-view="slides"].csi-stage-scaled .toast {
    bottom: var(--csi-toast-bottom) !important;
    transform: translate(-50%, 18px) scale(var(--csi-stage-scale)) !important;
    transform-origin: bottom center !important;
  }

  body[data-view="slides"].csi-stage-scaled .toast.show {
    transform: translate(-50%, 0) scale(var(--csi-stage-scale)) !important;
  }
}

@media print {
  body.csi-stage-scaled .slide,
  body.csi-stage-scaled .appbar,
  body.csi-stage-scaled #csiV16Menu,
  body.csi-stage-scaled .deck-footer,
  body.csi-stage-scaled .nav-arrows,
  body.csi-stage-scaled .timer-badge,
  body.csi-stage-scaled .toast {
    transform: none !important;
  }
}
'''

js = r'''/* CSI_RESPONSIVE_STAGE_4K_V1 */
(() => {
  'use strict';

  const BASE_WIDTH = 1920;
  const BASE_HEIGHT = 1080;
  const root = document.documentElement;
  const body = document.body;

  function px(name, value) {
    root.style.setProperty(name, `${Math.round(value * 100) / 100}px`);
  }

  function updateStageScale() {
    const width = window.innerWidth || root.clientWidth || BASE_WIDTH;
    const height = window.innerHeight || root.clientHeight || BASE_HEIGHT;
    const rawScale = Math.min(width / BASE_WIDTH, height / BASE_HEIGHT);
    const slidesMode = body.dataset.view === 'slides';
    const useScaledStage = slidesMode && rawScale > 1.02 && width >= BASE_WIDTH && height >= BASE_HEIGHT;
    const scale = useScaledStage ? rawScale : 1;

    root.style.setProperty('--csi-stage-scale', String(scale));
    body.classList.toggle('csi-stage-scaled', useScaledStage);
    body.dataset.csiStageScale = scale.toFixed(4);
    body.dataset.csiStageReference = `${BASE_WIDTH}x${BASE_HEIGHT}`;

    px('--csi-appbar-top', 16 * scale);
    px('--csi-menu-top', 70 * scale);
    px('--csi-ui-edge', 18 * scale);
    px('--csi-footer-bottom', 12 * scale);
    px('--csi-toast-bottom', 78 * scale);
    px('--csi-progress-height', 4 * scale);
  }

  let raf = 0;
  function scheduleUpdate() {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(updateStageScale);
  }

  window.addEventListener('resize', scheduleUpdate, { passive: true });
  window.addEventListener('orientationchange', scheduleUpdate, { passive: true });
  document.addEventListener('fullscreenchange', scheduleUpdate);
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', scheduleUpdate, { passive: true });
  }

  const viewObserver = new MutationObserver((mutations) => {
    if (mutations.some((m) => m.type === 'attributes' && m.attributeName === 'data-view')) {
      scheduleUpdate();
    }
  });
  viewObserver.observe(body, { attributes: true, attributeFilter: ['data-view'] });

  updateStageScale();
  requestAnimationFrame(updateStageScale);
  setTimeout(updateStageScale, 120);
})();
'''

Path('assets/csi-responsive-stage.css').write_text(css, encoding='utf-8')
Path('assets/csi-responsive-stage.js').write_text(js, encoding='utf-8')

css_tag = '  <link rel="stylesheet" href="assets/csi-responsive-stage.css?v=1">\n'
js_tag = '  <script src="assets/csi-responsive-stage.js?v=1"></script>\n'

if 'assets/csi-responsive-stage.css' in text or 'assets/csi-responsive-stage.js' in text:
    raise SystemExit('Responsive stage assets already linked')

head_pos = text.rfind('</head>')
body_pos = text.rfind('</body>')
if head_pos < 0 or body_pos < 0:
    raise SystemExit('Could not find closing head/body tags')

text = text[:head_pos] + css_tag + text[head_pos:]
body_pos = text.rfind('</body>')
text = text[:body_pos] + js_tag + text[body_pos:]
index.write_text(text, encoding='utf-8')

print('Added 1920x1080 logical stage scaling for large displays, including 3840x2160.')
