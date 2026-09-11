/* CSI_RESPONSIVE_STAGE_4K_V1 */
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
