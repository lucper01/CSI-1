from pathlib import Path

repo = Path('.')
css_path = repo / 'assets' / 'csi-responsive-stage.css'
js_path = repo / 'assets' / 'csi-responsive-stage.js'
index_path = repo / 'index.html'

css = r'''/* CSI_RESPONSIVE_STAGE_4K_V2
   Desktop presentation mode uses a fixed 1920x1080 virtual stage.
   The stage is fitted uniformly to the real browser viewport, up or down,
   so the composition remains stable across 1080p, 1440p and 4K displays. */
:root {
  --csi-stage-scale: 1;
  --csi-stage-top: 0px;
  --csi-stage-left: 0px;
  --csi-ui-top-appbar: 16px;
  --csi-ui-top-menu: 70px;
  --csi-ui-edge-x: 18px;
  --csi-ui-edge-y: 18px;
  --csi-ui-footer-bottom: 12px;
  --csi-ui-toast-bottom: 78px;
  --csi-progress-height: 4px;
}

body[data-view="slides"].csi-stage-fit {
  overflow: hidden !important;
}

body[data-view="slides"].csi-stage-fit .deck {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  overflow: hidden !important;
}

body[data-view="slides"].csi-stage-fit .slide {
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
  padding-left: 82px !important;
  padding-right: 82px !important;
}

body[data-view="slides"].csi-stage-fit .slide.active {
  display: flex !important;
}

/* Freeze the main desktop geometry before scaling it. */
body[data-view="slides"].csi-stage-fit .slide:not(.hero-slide) .slide-shell {
  width: min(1560px, 100%) !important;
}
body[data-view="slides"].csi-stage-fit .sela-visual-stack {
  right: -208px !important;
  width: 280px !important;
}

/* Presentation chrome is positioned from the fitted 16:9 stage edges. */
body[data-view="slides"].csi-stage-fit .appbar {
  width: 1500px !important;
  top: var(--csi-ui-top-appbar) !important;
  transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
  transform-origin: top center !important;
}

body[data-view="slides"].csi-stage-fit #csiV16Menu {
  width: 1500px !important;
  top: var(--csi-ui-top-menu) !important;
  transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
  transform-origin: top center !important;
}

body[data-view="slides"].csi-stage-fit .deck-footer {
  max-width: 1160px !important;
  bottom: var(--csi-ui-footer-bottom) !important;
  transform: translateX(-50%) scale(var(--csi-stage-scale)) !important;
  transform-origin: bottom center !important;
}

body[data-view="slides"].csi-stage-fit .nav-arrows {
  right: var(--csi-ui-edge-x) !important;
  bottom: var(--csi-ui-edge-y) !important;
  transform: scale(var(--csi-stage-scale)) !important;
  transform-origin: bottom right !important;
}

body[data-view="slides"].csi-stage-fit .timer-badge {
  left: var(--csi-ui-edge-x) !important;
  bottom: var(--csi-ui-edge-y) !important;
  transform: scale(var(--csi-stage-scale)) !important;
  transform-origin: bottom left !important;
}

body[data-view="slides"].csi-stage-fit .footer-progress {
  left: var(--csi-stage-left) !important;
  right: var(--csi-stage-left) !important;
  height: var(--csi-progress-height) !important;
}

body[data-view="slides"].csi-stage-fit .toast {
  bottom: var(--csi-ui-toast-bottom) !important;
  transform: translate(-50%, 18px) scale(var(--csi-stage-scale)) !important;
  transform-origin: bottom center !important;
}
body[data-view="slides"].csi-stage-fit .toast.show {
  transform: translate(-50%, 0) scale(var(--csi-stage-scale)) !important;
}

/* Keep overlays usable at native browser size. */
body[data-view="slides"].csi-stage-fit .drawer,
body[data-view="slides"].csi-stage-fit .navigator,
body[data-view="slides"].csi-stage-fit .overview,
body[data-view="slides"].csi-stage-fit .notes-panel,
body[data-view="slides"].csi-stage-fit .apparatus-modal,
body[data-view="slides"].csi-stage-fit .study-demo-modal,
body[data-view="slides"].csi-stage-fit #csiSheetViewer,
body[data-view="slides"].csi-stage-fit #csiQOverlay,
body[data-view="slides"].csi-stage-fit #csiQVault {
  transform: none !important;
}

@media print {
  body.csi-stage-fit .slide,
  body.csi-stage-fit .appbar,
  body.csi-stage-fit #csiV16Menu,
  body.csi-stage-fit .deck-footer,
  body.csi-stage-fit .nav-arrows,
  body.csi-stage-fit .timer-badge,
  body.csi-stage-fit .toast {
    transform: none !important;
  }
}
'''

js = r'''/* CSI_RESPONSIVE_STAGE_4K_V2 */
(() => {
  'use strict';

  const BASE_WIDTH = 1920;
  const BASE_HEIGHT = 1080;
  const MIN_DESKTOP_WIDTH = 1100;
  const MIN_DESKTOP_HEIGHT = 620;
  const root = document.documentElement;
  const body = document.body;

  function setPx(name, value) {
    root.style.setProperty(name, `${Math.round(value * 100) / 100}px`);
  }

  function viewportSize() {
    const vv = window.visualViewport;
    return {
      width: Math.max(1, vv?.width || window.innerWidth || root.clientWidth || BASE_WIDTH),
      height: Math.max(1, vv?.height || window.innerHeight || root.clientHeight || BASE_HEIGHT),
    };
  }

  function physicalScreenSize() {
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    return {
      dpr,
      width: Math.round((window.screen?.width || 0) * dpr),
      height: Math.round((window.screen?.height || 0) * dpr),
    };
  }

  function updateStageScale() {
    const viewport = viewportSize();
    const screen = physicalScreenSize();
    const slidesMode = body.dataset.view === 'slides';
    const desktopViewport = viewport.width >= MIN_DESKTOP_WIDTH && viewport.height >= MIN_DESKTOP_HEIGHT;
    const physicalLargeDisplay = screen.width >= 3000 && screen.height >= 1600;
    const forced = new URLSearchParams(location.search).get('stage');
    const useStage = slidesMode && forced !== 'off' && (forced === 'on' || desktopViewport || physicalLargeDisplay);

    const scale = useStage
      ? Math.min(viewport.width / BASE_WIDTH, viewport.height / BASE_HEIGHT)
      : 1;

    const stageWidth = BASE_WIDTH * scale;
    const stageHeight = BASE_HEIGHT * scale;
    const stageLeft = Math.max(0, (viewport.width - stageWidth) / 2);
    const stageTop = Math.max(0, (viewport.height - stageHeight) / 2);

    root.style.setProperty('--csi-stage-scale', String(scale));
    setPx('--csi-stage-left', stageLeft);
    setPx('--csi-stage-top', stageTop);
    setPx('--csi-ui-top-appbar', stageTop + 16 * scale);
    setPx('--csi-ui-top-menu', stageTop + 70 * scale);
    setPx('--csi-ui-edge-x', stageLeft + 18 * scale);
    setPx('--csi-ui-edge-y', stageTop + 18 * scale);
    setPx('--csi-ui-footer-bottom', stageTop + 12 * scale);
    setPx('--csi-ui-toast-bottom', stageTop + 78 * scale);
    setPx('--csi-progress-height', 4 * scale);

    body.classList.toggle('csi-stage-fit', useStage);
    body.classList.remove('csi-stage-scaled');
    body.dataset.csiStageScale = scale.toFixed(4);
    body.dataset.csiStageMode = useStage ? 'fit-16x9' : 'responsive';
    body.dataset.csiStageReference = `${BASE_WIDTH}x${BASE_HEIGHT}`;
    body.dataset.csiViewport = `${Math.round(viewport.width)}x${Math.round(viewport.height)}`;
    body.dataset.csiPhysicalScreen = `${screen.width}x${screen.height}@${screen.dpr}`;
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
    window.visualViewport.addEventListener('scroll', scheduleUpdate, { passive: true });
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
  setTimeout(updateStageScale, 500);
})();
'''

css_path.write_text(css, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')

index = index_path.read_text(encoding='utf-8')
old_css = 'assets/csi-responsive-stage.css?v=1'
old_js = 'assets/csi-responsive-stage.js?v=1'
if old_css not in index or old_js not in index:
    raise SystemExit('Expected V1 responsive asset references were not found in index.html')
index = index.replace(old_css, 'assets/csi-responsive-stage.css?v=2', 1)
index = index.replace(old_js, 'assets/csi-responsive-stage.js?v=2', 1)
index_path.write_text(index, encoding='utf-8')

print('Responsive stage upgraded to V2')
