(() => {
  const downloadBtn = document.getElementById('downloadBtn');
  const exportMenu = document.getElementById('exportMenu');
  const notesPanel = document.getElementById('notesPanel');
  const notesBtn = document.getElementById('notesBtn');
  if (!downloadBtn || !exportMenu) return;

  const progress = document.createElement('div');
  progress.className = 'csi-export-progress';
  progress.hidden = true;
  document.body.appendChild(progress);

  const setProgress = text => {
    progress.textContent = text;
    progress.hidden = false;
  };
  const clearProgress = () => { progress.hidden = true; };
  const setMenu = open => {
    exportMenu.hidden = !open;
    downloadBtn.setAttribute('aria-expanded', String(open));
  };

  downloadBtn.addEventListener('click', event => {
    event.stopPropagation();
    setMenu(exportMenu.hidden);
  });
  exportMenu.addEventListener('click', event => event.stopPropagation());
  document.addEventListener('click', () => setMenu(false));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') setMenu(false);
  });

  function loadScriptOnce(id, src, test) {
    if (test()) return Promise.resolve();
    const existing = document.getElementById(id);
    if (existing) {
      return new Promise((resolve, reject) => {
        existing.addEventListener('load', () => test() ? resolve() : reject(new Error(id)), { once: true });
        existing.addEventListener('error', reject, { once: true });
      });
    }
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.id = id;
      script.src = src;
      script.async = true;
      script.onload = () => test() ? resolve() : reject(new Error(id));
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  const ensureCapture = () => loadScriptOnce(
    'csi-domtoimage',
    'https://cdn.jsdelivr.net/npm/dom-to-image-more@3.10.2/dist/dom-to-image-more.min.js',
    () => !!window.domtoimage
  );
  const ensurePdf = () => loadScriptOnce(
    'csi-jspdf',
    'https://cdn.jsdelivr.net/npm/jspdf@4.2.1/dist/jspdf.umd.min.js',
    () => !!window.jspdf?.jsPDF
  );
  const ensurePptx = () => loadScriptOnce(
    'csi-pptxgen',
    'https://cdn.jsdelivr.net/npm/pptxgenjs@4.0.1/dist/pptxgen.bundle.js',
    () => !!window.PptxGenJS
  );

  const waitForImages = root => Promise.all(
    [...root.querySelectorAll('img')].map(img => img.complete ? Promise.resolve() : new Promise(resolve => {
      img.addEventListener('load', resolve, { once: true });
      img.addEventListener('error', resolve, { once: true });
    }))
  );

  async function captureSlide(index) {
    const source = document.querySelector(`.slide[data-index="${index}"]`);
    if (!source) throw new Error(`Slide introuvable: ${index + 1}`);

    const clone = source.cloneNode(true);
    clone.removeAttribute('id');
    clone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
    clone.classList.add('active', 'csi-export-clone');

    const width = 1600;
    const height = 900;
    const forced = {
      display: 'flex',
      position: 'fixed',
      left: '-20000px',
      top: '0',
      width: `${width}px`,
      height: `${height}px`,
      'min-height': `${height}px`,
      'max-height': `${height}px`,
      overflow: 'hidden',
      'z-index': '-1'
    };
    Object.entries(forced).forEach(([name, value]) => clone.style.setProperty(name, value, 'important'));
    document.body.appendChild(clone);

    try {
      if (document.fonts?.ready) await document.fonts.ready;
      await waitForImages(clone);
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return await window.domtoimage.toPng(clone, {
        width,
        height,
        cacheBust: true,
        bgcolor: getComputedStyle(document.body).backgroundColor || '#ffffff'
      });
    } finally {
      clone.remove();
    }
  }

  function exportIndexes() {
    const indexes = typeof visibleIndexes === 'function'
      ? visibleIndexes()
      : [...document.querySelectorAll('.slide')].map(el => Number(el.dataset.index)).filter(Number.isFinite);
    if (!indexes.length) throw new Error('Aucune diapo à exporter.');
    return indexes;
  }

  async function exportPdf() {
    await Promise.all([ensureCapture(), ensurePdf()]);
    const indexes = exportIndexes();
    const { jsPDF } = window.jspdf;
    const pageWidth = 297;
    const pageHeight = 167.0625;
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: [pageWidth, pageHeight], compress: true });

    for (let n = 0; n < indexes.length; n += 1) {
      setProgress(`PDF - diapo ${n + 1}/${indexes.length}`);
      const image = await captureSlide(indexes[n]);
      if (n) pdf.addPage([pageWidth, pageHeight], 'landscape');
      pdf.addImage(image, 'PNG', 0, 0, pageWidth, pageHeight, undefined, 'FAST');
    }
    pdf.save('CSI_1_Luc_Perroquin.pdf');
  }

  async function exportPptx() {
    await Promise.all([ensureCapture(), ensurePptx()]);
    const indexes = exportIndexes();
    const pptx = new window.PptxGenJS();
    pptx.layout = 'LAYOUT_WIDE';
    pptx.author = 'Luc Perroquin';
    pptx.title = 'CSI 1 - Luc Perroquin';
    pptx.subject = 'Comité de suivi individuel - CSI 1';

    for (let n = 0; n < indexes.length; n += 1) {
      setProgress(`PowerPoint - diapo ${n + 1}/${indexes.length}`);
      const image = await captureSlide(indexes[n]);
      const slide = pptx.addSlide();
      slide.addImage({ data: image, x: 0, y: 0, w: 13.333, h: 7.5 });
    }
    setProgress('PowerPoint - création du fichier…');
    await pptx.writeFile({ fileName: 'CSI_1_Luc_Perroquin.pptx' });
  }

  async function runExport(type) {
    setMenu(false);
    downloadBtn.disabled = true;
    downloadBtn.setAttribute('aria-busy', 'true');
    try {
      if (type === 'pdf') await exportPdf();
      else await exportPptx();
      if (typeof showToast === 'function') showToast(type === 'pdf' ? 'PDF téléchargé.' : 'PowerPoint téléchargé.');
    } catch (error) {
      console.error('[CSI EXPORT]', error);
      if (type === 'pdf') {
        if (typeof showToast === 'function') showToast('Export direct indisponible - ouverture du dialogue PDF.');
        window.print();
      } else if (typeof showToast === 'function') {
        showToast('Export PowerPoint impossible. Vérifiez la connexion puis réessayez.');
      }
    } finally {
      clearProgress();
      downloadBtn.disabled = false;
      downloadBtn.removeAttribute('aria-busy');
    }
  }

  exportMenu.querySelector('[data-export="pdf"]')?.addEventListener('click', () => runExport('pdf'));
  exportMenu.querySelector('[data-export="pptx"]')?.addEventListener('click', () => runExport('pptx'));

  if (notesPanel && notesBtn) {
    const syncNotesState = () => {
      const open = !notesPanel.hidden;
      notesBtn.classList.toggle('active', open);
      notesBtn.setAttribute('aria-pressed', String(open));
    };
    new MutationObserver(syncNotesState).observe(notesPanel, { attributes: true, attributeFilter: ['hidden'] });
    syncNotesState();

    const notesHead = notesPanel.querySelector('.panel-head');
    if (notesHead) {
      let drag = null;
      notesHead.addEventListener('pointerdown', event => {
        if (event.button !== 0 || event.target.closest('button')) return;
        const rect = notesPanel.getBoundingClientRect();
        drag = { x: event.clientX - rect.left, y: event.clientY - rect.top, id: event.pointerId };
        notesHead.setPointerCapture?.(event.pointerId);
        event.preventDefault();
      });
      notesHead.addEventListener('pointermove', event => {
        if (!drag || event.pointerId !== drag.id) return;
        const x = Math.max(8, Math.min(innerWidth - notesPanel.offsetWidth - 8, event.clientX - drag.x));
        const y = Math.max(72, Math.min(innerHeight - notesPanel.offsetHeight - 8, event.clientY - drag.y));
        notesPanel.style.setProperty('left', `${x}px`, 'important');
        notesPanel.style.setProperty('top', `${y}px`, 'important');
      });
      ['pointerup', 'pointercancel'].forEach(type => notesHead.addEventListener(type, () => { drag = null; }));
    }
  }
})();
