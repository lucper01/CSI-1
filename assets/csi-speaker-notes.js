(() => {
  'use strict';

  const button = document.getElementById('notesBtn');
  if (!button) return;

  let notesWindow = null;
  let lastSignature = '';

  button.title = 'Notes orateur - ouvrir dans une fenêtre séparée';
  button.setAttribute('aria-label', 'Ouvrir les notes orateur dans une fenêtre séparée');
  button.setAttribute('aria-pressed', 'false');

  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));

  const clean = value => String(value ?? '').replace(/\s+/g, ' ').trim();

  function allSlides() {
    try {
      if (typeof slides !== 'undefined' && Array.isArray(slides)) return slides;
    } catch (_) {}
    return [];
  }

  function currentSlideIndex() {
    try {
      if (typeof current !== 'undefined' && Number.isInteger(current)) return current;
    } catch (_) {}
    const active = document.querySelector('#deck .slide.active');
    const index = Number(active?.dataset.index);
    return Number.isInteger(index) ? index : 0;
  }

  function visibleState(index) {
    const list = allSlides();
    let visible = list.map((_, i) => i);
    try {
      if (typeof visibleIndexes === 'function') visible = visibleIndexes();
    } catch (_) {}
    const position = Math.max(0, visible.indexOf(index));
    return {
      visible,
      position,
      total: visible.length,
      previous: position > 0 ? visible[position - 1] : null,
      next: position < visible.length - 1 ? visible[position + 1] : null
    };
  }

  function collectTalkingPoints(index, title, lead) {
    const slide = document.querySelector(`#deck .slide[data-index="${index}"]`);
    if (!slide) return [];
    const candidates = [...slide.querySelectorAll(
      'h3,h4,li,.callout,.question,.status-row .desc,.card p,.axis-card p,.flow-card p,.roadmap-card p,.result p'
    )];
    const blocked = new Set([clean(title).toLowerCase(), clean(lead).toLowerCase()]);
    const seen = new Set();
    const points = [];
    for (const element of candidates) {
      const text = clean(element.textContent);
      const key = text.toLowerCase();
      if (!text || text.length < 8 || text.length > 260 || blocked.has(key) || seen.has(key)) continue;
      seen.add(key);
      points.push(text);
      if (points.length >= 8) break;
    }
    return points;
  }

  function noteParagraphs(note) {
    const text = clean(note);
    if (!text) return [];
    const parts = String(note).split(/\n{2,}|\n(?=[A-ZÀ-ÖØ-Ý0-9])/).map(clean).filter(Boolean);
    return parts.length ? parts : [text];
  }

  function palette() {
    const styles = getComputedStyle(document.documentElement);
    return {
      accent: clean(styles.getPropertyValue('--accent')) || '#1f6f50',
      strong: clean(styles.getPropertyValue('--accent-strong')) || '#0b2f23',
      soft: clean(styles.getPropertyValue('--accent-soft')) || '#dceee3',
      pale: clean(styles.getPropertyValue('--accent-pale')) || '#f3faf5'
    };
  }

  function isEnglish() {
    return document.documentElement.lang === 'en';
  }

  function renderNotes() {
    if (!notesWindow || notesWindow.closed) return;

    const list = allSlides();
    const index = currentSlideIndex();
    const slide = list[index];
    if (!slide) return;

    const state = visibleState(index);
    const title = clean(slide.title) || (isEnglish() ? 'Untitled slide' : 'Diapositive sans titre');
    const lead = clean(slide.lead);
    const notes = noteParagraphs(slide.notes);
    const points = collectTalkingPoints(index, title, lead);
    const nextSlide = state.next !== null ? list[state.next] : null;
    const previousSlide = state.previous !== null ? list[state.previous] : null;
    const nextTitle = clean(nextSlide?.title);
    const section = clean(slide.section || slide.chapter);
    const study = clean(slide.study);
    const lang = isEnglish() ? 'en' : 'fr';
    const colors = palette();

    const signature = JSON.stringify({ index, title, lead, notes, points, nextTitle, lang, colors });
    if (signature === lastSignature) return;
    lastSignature = signature;

    const E = lang === 'en';
    const labels = E ? {
      speaker: 'Speaker notes', slide: 'Slide', of: 'of', section: 'Section', study: 'Study',
      key: 'Key message', script: 'Speaking notes', points: 'Points to develop', transition: 'Transition',
      previous: 'Previous slide', next: 'Next slide', close: 'Close', noNotes: 'No specific note was written for this slide.',
      intro: 'Open by stating the idea in your own words rather than reading the slide.'
    } : {
      speaker: 'Notes orateur', slide: 'Diapo', of: 'sur', section: 'Section', study: 'Étude',
      key: 'Message clé', script: 'Déroulé oral', points: 'Points à développer', transition: 'Transition',
      previous: 'Diapo précédente', next: 'Diapo suivante', close: 'Fermer', noNotes: 'Aucune note spécifique n’a été rédigée pour cette diapo.',
      intro: 'Commencer par formuler l’idée avec ses propres mots, sans lire la diapo.'
    };

    const leadBlock = lead
      ? `<section class="note-card key"><h2>${labels.key}</h2><p>${esc(lead)}</p></section>`
      : '';

    const noteItems = notes.length
      ? notes.map(text => `<p>${esc(text)}</p>`).join('')
      : `<p class="muted">${labels.noNotes}</p>`;

    const pointsBlock = points.length
      ? `<section class="note-card"><h2>${labels.points}</h2><ul>${points.map(text => `<li>${esc(text)}</li>`).join('')}</ul></section>`
      : '';

    const transitionBlock = nextTitle
      ? `<section class="note-card transition"><h2>${labels.transition}</h2><p>${E ? 'Lead naturally into' : 'Enchaîner naturellement vers'} <strong>${esc(nextTitle)}</strong>.</p></section>`
      : '';

    const root = notesWindow.document.getElementById('speaker-root');
    if (!root) return;
    root.style.setProperty('--accent', colors.accent);
    root.style.setProperty('--accent-strong', colors.strong);
    root.style.setProperty('--accent-soft', colors.soft);
    root.style.setProperty('--accent-pale', colors.pale);
    root.innerHTML = `
      <header class="speaker-head">
        <div>
          <div class="eyebrow">${labels.speaker}</div>
          <div class="counter">${labels.slide} ${state.position + 1} ${labels.of} ${state.total}</div>
        </div>
        <div class="speaker-actions">
          <button type="button" id="speaker-prev" ${previousSlide ? '' : 'disabled'} title="${labels.previous}">←</button>
          <button type="button" id="speaker-next" ${nextSlide ? '' : 'disabled'} title="${labels.next}">→</button>
          <button type="button" id="speaker-close">${labels.close}</button>
        </div>
      </header>
      <main>
        <div class="meta">${section ? `<span>${labels.section} - ${esc(section)}</span>` : ''}${study ? `<span>${labels.study} - ${esc(study)}</span>` : ''}</div>
        <h1>${esc(title)}</h1>
        ${leadBlock}
        <section class="note-card script">
          <h2>${labels.script}</h2>
          <p class="opening">${labels.intro}</p>
          ${noteItems}
        </section>
        ${pointsBlock}
        ${transitionBlock}
      </main>`;

    notesWindow.document.title = `${labels.speaker} - ${state.position + 1} - ${title}`;
    notesWindow.document.getElementById('speaker-prev')?.addEventListener('click', () => {
      window.document.getElementById('prevBtn')?.click();
    });
    notesWindow.document.getElementById('speaker-next')?.addEventListener('click', () => {
      window.document.getElementById('nextBtn')?.click();
    });
    notesWindow.document.getElementById('speaker-close')?.addEventListener('click', () => notesWindow.close());
  }

  function initialiseWindow() {
    if (!notesWindow || notesWindow.closed) return false;
    const doc = notesWindow.document;
    doc.open();
    doc.write(`<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
      :root{color-scheme:light}*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f7f7f4;color:#1d261f;line-height:1.55}#speaker-root{--accent:#1f6f50;--accent-strong:#0b2f23;--accent-soft:#dceee3;--accent-pale:#f3faf5;min-height:100vh;background:linear-gradient(180deg,#fbf7ed,var(--accent-pale));padding-bottom:38px}.speaker-head{position:sticky;top:0;z-index:3;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 22px;background:rgba(251,247,237,.95);border-bottom:1px solid rgba(11,47,35,.13);backdrop-filter:blur(14px)}.eyebrow{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;font-weight:950;color:var(--accent)}.counter{margin-top:2px;font-size:.84rem;color:#5f6f65;font-weight:800}.speaker-actions{display:flex;gap:7px;align-items:center}.speaker-actions button{border:1px solid rgba(11,47,35,.13);background:white;color:var(--accent-strong);border-radius:999px;min-width:38px;height:38px;padding:0 13px;font-weight:900;cursor:pointer}.speaker-actions button:hover{background:var(--accent-soft)}.speaker-actions button:disabled{opacity:.35;cursor:default}main{width:min(760px,100%);margin:0 auto;padding:28px 24px 0}.meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.meta span{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;font-weight:900;color:var(--accent-strong);background:var(--accent-soft);padding:5px 9px;border-radius:999px}h1{font-family:Georgia,"Times New Roman",serif;color:var(--accent-strong);font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.08;letter-spacing:-.035em;margin:10px 0 22px}.note-card{margin:14px 0;padding:18px 20px;border:1px solid rgba(11,47,35,.13);border-radius:20px;background:white;box-shadow:0 8px 24px rgba(11,47,35,.07)}.note-card.key{border-left:5px solid var(--accent);background:color-mix(in srgb,var(--accent-pale) 62%,white)}.note-card.transition{background:var(--accent-pale)}.note-card h2{font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 11px}.note-card p{margin:9px 0}.note-card .opening{font-weight:800;color:var(--accent-strong)}.note-card ul{margin:0;padding-left:20px}.note-card li{margin:8px 0}.muted{color:#6f7e74;font-style:italic}@media(max-width:560px){.speaker-head{align-items:flex-start;padding:13px 14px}.speaker-actions{gap:4px}.speaker-actions button{padding:0 10px}main{padding:22px 14px 0}.note-card{padding:16px}}
    </style></head><body><div id="speaker-root"></div></body></html>`);
    doc.close();
    return true;
  }

  function setButtonState(open) {
    button.classList.toggle('active', open);
    button.setAttribute('aria-pressed', String(open));
  }

  function openNotesWindow() {
    if (notesWindow && !notesWindow.closed) {
      notesWindow.focus();
      renderNotes();
      return;
    }
    notesWindow = window.open('', 'csiSpeakerNotes', 'popup=yes,width=680,height=860,resizable=yes,scrollbars=yes');
    if (!notesWindow) {
      try {
        if (typeof showToast === 'function') showToast('Autorisez les fenêtres contextuelles pour afficher les notes orateur.');
      } catch (_) {}
      setButtonState(false);
      return;
    }
    lastSignature = '';
    initialiseWindow();
    setButtonState(true);
    renderNotes();
    notesWindow.focus();
  }

  function toggleNotesWindow() {
    if (notesWindow && !notesWindow.closed) {
      notesWindow.close();
      notesWindow = null;
      lastSignature = '';
      setButtonState(false);
    } else {
      openNotesWindow();
    }
  }

  button.addEventListener('click', event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    toggleNotesWindow();
  }, true);

  document.addEventListener('keydown', event => {
    if (event.key.toLowerCase() !== 'n') return;
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    toggleNotesWindow();
  }, true);

  const deck = document.getElementById('deck');
  if (deck) {
    new MutationObserver(() => {
      if (notesWindow && !notesWindow.closed) renderNotes();
    }).observe(deck, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
  }

  new MutationObserver(() => {
    if (notesWindow && !notesWindow.closed) {
      lastSignature = '';
      renderNotes();
    }
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['lang', 'data-theme', 'data-accent'] });

  window.setInterval(() => {
    if (notesWindow && !notesWindow.closed) {
      setButtonState(true);
      renderNotes();
    } else if (notesWindow) {
      notesWindow = null;
      lastSignature = '';
      setButtonState(false);
    }
  }, 500);
})();
