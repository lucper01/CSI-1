from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')
orig = t

# Restore presenter notes.
t = t.replace('#notesPanel{display:none!important}', '#notesPanel[hidden]{display:none!important}', 1)
t = t.replace('<aside class="notes-panel" id="notesPanel" hidden aria-live="polite">', '<aside class="notes-panel csi-notes" id="notesPanel" hidden aria-live="polite">', 1)

old_btn = '<button class="icon-btn" id="notesBtn" type="button" aria-label="Notes orateur" title="Notes orateur">N</button>'
new_btn = '<button class="icon-btn" id="notesBtn" type="button" aria-label="Notes orateur" aria-pressed="false" title="Notes orateur">N</button>'
if old_btn in t:
    t = t.replace(old_btn, new_btn, 1)
elif new_btn not in t:
    raise SystemExit('notes button not found')

# Add the compact download control next to N.
if 'id="downloadBtn"' not in t:
    export_ui = '''<div class="csi-export-wrap"><button class="icon-btn" id="downloadBtn" type="button" aria-label="Télécharger la présentation" aria-haspopup="menu" aria-expanded="false" title="Télécharger PDF / PowerPoint"><svg class="csi-download-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v11m0 0 4-4m-4 4-4-4M5 16v3h14v-3"/></svg></button><div class="csi-export-menu" id="exportMenu" role="menu" hidden><button type="button" role="menuitem" data-export="pdf"><strong>PDF</strong><span>Téléchargement direct</span></button><button type="button" role="menuitem" data-export="pptx"><strong>PowerPoint</strong><span>Fichier .pptx</span></button></div></div>'''
    t = t.replace(new_btn, new_btn + export_ui, 1)

# Load the isolated export assets.
if 'assets/csi-export.css' not in t:
    t = t.replace('</head>', '  <link rel="stylesheet" href="assets/csi-export.css?v=1">\n</head>', 1)
if 'assets/csi-export.js' not in t:
    t = t.replace('</body>', '  <script src="assets/csi-export.js?v=1"></script>\n</body>', 1)

# Remove only the C keyboard shortcut for the Personalization drawer.
t = t.replace("    if(k==='c') togglePanel('settingsDrawer');\n", '', 1)

for token in [
    'notes-panel csi-notes',
    '#notesPanel[hidden]{display:none!important}',
    'id="downloadBtn"',
    'id="exportMenu"',
    'assets/csi-export.css?v=1',
    'assets/csi-export.js?v=1',
]:
    if token not in t:
        raise SystemExit('missing expected token: ' + token)

if '#notesPanel{display:none!important}' in t:
    raise SystemExit('notes panel still forcibly hidden')
if "if(k==='c') togglePanel('settingsDrawer')" in t:
    raise SystemExit('C shortcut still present')
if t == orig:
    raise SystemExit('no changes made')

p.write_text(t, encoding='utf-8')
