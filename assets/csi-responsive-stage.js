/* CSI_RESPONSIVE_STAGE_4K_V2 */
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
