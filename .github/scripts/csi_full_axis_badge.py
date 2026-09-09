from pathlib import Path
import hashlib

p = Path('index.html')
save = Path('index_save.html')
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
text = p.read_text(encoding='utf-8')

old = "return `<span class=\"study-axis-badge\" tabindex=\"0\" title=\"${esc(full)}\" aria-label=\"${esc(short+' - '+full)}\">${short}</span>`;"
new = "return `<span class=\"study-axis-badge\" tabindex=\"0\" title=\"${esc(short+' - '+full)}\" aria-label=\"${esc(short+' - '+full)}\"><strong>${short}</strong><span> - ${esc(full)}</span></span>`;"
assert old in text, 'Axis badge render line not found'
text = text.replace(old, new, 1)

css = '''
/* CSI_FULL_AXIS_BADGE */
.study-axis-badge {
  max-width: min(100%, 860px);
  padding: 4px 10px !important;
  gap: 4px;
  white-space: normal !important;
  text-transform: none !important;
  line-height: 1.18 !important;
  text-align: left;
}
.study-axis-badge strong {
  flex: 0 0 auto;
  font-weight: 950;
  text-transform: uppercase;
}
.study-axis-badge > span {
  font-weight: 760;
  letter-spacing: .015em;
}
@media (max-width: 760px) {
  .study-axis-badge { max-width: 100%; font-size: .48rem; }
}
'''
if 'CSI_FULL_AXIS_BADGE' not in text:
    pos = text.rfind('</style>')
    assert pos != -1
    text = text[:pos] + css + text[pos:]

p.write_text(text, encoding='utf-8')
out = p.read_text(encoding='utf-8')
assert '<strong>${short}</strong><span> - ${esc(full)}</span>' in out
assert 'CSI_FULL_AXIS_BADGE' in out
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
