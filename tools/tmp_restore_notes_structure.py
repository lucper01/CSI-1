from pathlib import Path

path = Path('assets/csi-speaker-notes.js')
text = path.read_text(encoding='utf-8')

marker = 'CSI_THEORY_NOTES_STRUCTURE_V2'
if marker in text:
    raise SystemExit('Speaker notes structure already restored')

old = """  function noteParagraphs(note) {\n    const text = clean(note);\n    if (!text) return [];\n    const parts = String(note).split(/\\n{2,}|\\n(?=[A-ZÀ-ÖØ-Ý0-9])/).map(clean).filter(Boolean);\n    return parts.length ? parts : [text];\n  }\n"""

new = """  // CSI_THEORY_NOTES_STRUCTURE_V2\n  // Keep the original speaker-note organisation even when theoretical card descriptions\n  // have been removed from the slide and stored in slide.notes.\n  function splitStructuredNotes(note) {\n    const raw = String(note ?? '');\n    if (!raw.trim()) return { script: [], cardDetails: [] };\n\n    const markers = [\n      'Détails des cartes conservés pour les notes orateur :',\n      'Card details kept for speaker notes:'\n    ];\n    let markerIndex = -1;\n    let markerText = '';\n    for (const candidate of markers) {\n      const idx = raw.indexOf(candidate);\n      if (idx >= 0 && (markerIndex < 0 || idx < markerIndex)) {\n        markerIndex = idx;\n        markerText = candidate;\n      }\n    }\n\n    const scriptRaw = markerIndex >= 0 ? raw.slice(0, markerIndex).trim() : raw.trim();\n    const detailsRaw = markerIndex >= 0 ? raw.slice(markerIndex + markerText.length).trim() : '';\n\n    const script = scriptRaw\n      ? scriptRaw.split(/\\n{2,}|\\n(?=[A-ZÀ-ÖØ-Ý0-9])/).map(clean).filter(Boolean)\n      : [];\n    const cardDetails = detailsRaw\n      ? detailsRaw.split(/\\n+/).map(line => clean(line.replace(/^[-•]\\s*/, ''))).filter(Boolean)\n      : [];\n\n    return { script, cardDetails };\n  }\n\n  function noteParagraphs(note) {\n    return splitStructuredNotes(note).script;\n  }\n"""

if old not in text:
    raise SystemExit('noteParagraphs block not found')
text = text.replace(old, new, 1)

old2 = """    const notes = noteParagraphs(slide.notes);\n    const points = collectTalkingPoints(index, title, lead);\n"""
new2 = """    const structuredNotes = splitStructuredNotes(slide.notes);\n    const notes = structuredNotes.script;\n    const points = [...structuredNotes.cardDetails, ...collectTalkingPoints(index, title, lead)]\n      .filter((text, i, arr) => text && arr.indexOf(text) === i)\n      .slice(0, 10);\n"""
if old2 not in text:
    raise SystemExit('render notes/points block not found')
text = text.replace(old2, new2, 1)

path.write_text(text, encoding='utf-8')
print('Restored speaker-note organisation: card details -> Points to develop; original notes -> Speaking notes.')
