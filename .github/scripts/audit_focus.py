from pathlib import Path
import hashlib, re, json

p = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
h = p.read_text(encoding='utf-8')

old_js = '''  function inferStudy(el){
    const own=String(el.dataset.study||'').toUpperCase();if(COLORS[own])return own;
    const parent=el.closest('[data-study]');const ps=String(parent&&parent.dataset.study||'').toUpperCase();if(COLORS[ps])return ps;
    const heading=String(el.querySelector('h3,h4')?.textContent||'').toUpperCase();
    const found=NAMES.filter(n=>new RegExp('(^|[^A-Z])'+n+'([^A-Z]|$)').test(heading));return found.length===1?found[0]:'';
  }'''
new_js = '''  function slideStudy(el){
    const slide=el?.closest('.slide');
    const idx=Number(slide?.dataset.index);
    const meta=Number.isInteger(idx)&&typeof slides!=='undefined'?slides[idx]:null;
    const study=String(meta&&meta.study||'').toUpperCase();
    return COLORS[study]?study:'';
  }
  function inferStudy(el){
    /* Study-specific slides keep their own identity color. Cross-study names stay separate badges. */
    const slideOwn=slideStudy(el);if(slideOwn)return slideOwn;
    const own=String(el.dataset.study||'').toUpperCase();if(COLORS[own])return own;
    const parent=el.parentElement?.closest('[data-study]');const ps=String(parent&&parent.dataset.study||'').toUpperCase();if(COLORS[ps])return ps;
    const nested=[...el.querySelectorAll('[data-study]')].map(n=>String(n.dataset.study||'').toUpperCase()).filter(k=>COLORS[k]);
    const unique=[...new Set(nested)];if(unique.length===1)return unique[0];if(unique.length>1)return '';
    const heading=String(el.querySelector('h3,h4')?.textContent||'').toUpperCase();
    const found=NAMES.filter(n=>new RegExp('(^|[^A-Z])'+n+'([^A-Z]|$)').test(heading));return found.length===1?found[0]:'';
  }'''
if old_js not in h:
    raise SystemExit('inferStudy block not found')
h = h.replace(old_js, new_js, 1)

old_css = '''.slide.csi-focus-enabled .csi-focus-target.csi-focus-active :is(.study-token,.v16-pills span,.v16-tool-pills span,.m1-stat-grid>div){background:rgba(255,255,255,.14)!important;border-color:rgba(255,255,255,.34)!important;color:#fff!important}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-active>div :is(b,span){color:#fff!important}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-active>div{box-shadow:none!important}
body.reduced-motion .csi-focus-target{transition:none!important;transform:none!important}'''
new_css = '''.slide.csi-focus-enabled .csi-focus-target.csi-focus-active :is(.v16-tool-pills span,.m1-stat-grid>div){background:rgba(255,255,255,.14)!important;border-color:rgba(255,255,255,.34)!important;color:#fff!important}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-active>div :is(b,span){color:#fff!important}
.slide.csi-focus-enabled .m1-stat-grid.csi-focus-active>div{box-shadow:none!important}

/* Study identities stay visible inside a focused card. This comes after the generic white-text rules. */
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active .study-token[data-study],
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active [data-study]:not(.csi-focus-target){
  --badge-study:var(--study-color,var(--study,var(--focus-color)));
  background:linear-gradient(145deg,color-mix(in srgb,var(--badge-study) 88%,#111),color-mix(in srgb,var(--badge-study) 82%,#000))!important;
  color:#fff!important;
  border-color:color-mix(in srgb,var(--badge-study) 72%,#fff)!important;
  box-shadow:0 0 0 1px rgba(255,255,255,.48),0 4px 12px color-mix(in srgb,var(--badge-study) 34%,transparent)!important;
  text-shadow:0 1px 2px rgba(0,0,0,.34)!important;
}
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active .study-year-name[data-study],
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active .v16-pills [data-study]{
  padding:5px 9px!important;
  border-radius:999px!important;
  font-weight:950!important;
}
.slide.csi-focus-enabled .csi-focus-target.csi-focus-active .v16-pills [data-study]{padding:7px 10px!important}

body.reduced-motion .csi-focus-target{transition:none!important;transform:none!important}'''
if old_css not in h:
    raise SystemExit('focus badge CSS block not found')
h = h.replace(old_css, new_css, 1)
p.write_text(h, encoding='utf-8')

if hashlib.sha256(save.read_bytes()).hexdigest() != save_before:
    raise SystemExit('index_save.html changed unexpectedly')

# Full audit of study identities and requested regressions.
colors = ['TWIXAV','SOFT','TWIXOLF','VIBEX','OASIS','SORBET','SOLAR','COBEX','BRAUD','BRAUDOLF','FLUXOLF']
m = re.search(r'const\s+slides\s*=\s*(\[.*?\]);\s*\n\s*const\s+mainSlides', h, re.S)
assert m, 'slides array missing'
slides_data = json.loads(m.group(1))
assert 'const slideOwn=slideStudy(el);if(slideOwn)return slideOwn;' in h
assert "const unique=[...new Set(nested)];if(unique.length===1)return unique[0];if(unique.length>1)return '';" in h
assert '.study-token[data-study]' in h
assert '[data-study]:not(.csi-focus-target)' in h
assert '--badge-study:var(--study-color,var(--study,var(--focus-color)))' in h
assert 'csi-progressive-focus-runtime' not in save.read_text(encoding='utf-8')

study_slides = []
cross_refs = []
for i, s in enumerate(slides_data, 1):
    own = str(s.get('study') or '').upper()
    if own:
        assert own in colors, (i, own)
        study_slides.append((i, own, s.get('title')))
        text = ' '.join(str(s.get(x) or '') for x in ['title','lead','content'])
        refs = [k for k in colors if k != own and re.search(r'\b'+re.escape(k)+r'\b', text, re.I)]
        if refs:
            cross_refs.append((i, own, refs, s.get('title')))

def slide(n):
    return slides_data[n-1]

for k in ['TWIXAV','SOFT','TWIXOLF','SORBET','VIBEX','OASIS','SOLAR','COBEX','BRAUD','BRAUDOLF']:
    assert f'data-study=\"{k}\"' in slide(3)['content'], ('slide3', k)
assert 'study-year-name' in slide(5)['content']
for k in ['TWIXAV','VIBEX','FLUXOLF','SOFT','OASIS','TWIXOLF']:
    assert k in slide(5)['content'], ('slide5', k)
assert str(slide(6).get('study')).upper() == 'TWIXAV' and 'SOFT' in slide(6)['content']
assert str(slide(9).get('study')).upper() == 'TWIXAV' and 'SOFT' in slide(9)['content'] and 'TWIXOLF' in slide(9)['content']
assert str(slide(10).get('study')).upper() == 'VIBEX' and 'OASIS' in slide(10)['content']
assert str(slide(13).get('study')).upper() == 'VIBEX' and 'OASIS' in slide(13)['content']

print('STUDY-SPECIFIC SLIDES:', len(study_slides))
print('CROSS-STUDY SLIDES/CARDS AUDITED:', len(cross_refs))
for row in cross_refs:
    print(row)
print('AUDIT PASSED')
