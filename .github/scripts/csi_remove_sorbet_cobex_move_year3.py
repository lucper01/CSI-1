from pathlib import Path
import json
import re
import hashlib

index = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

REMOVED = {'SORBET', 'COBEX'}

# Find the existing year 3 activity slide before cleanup.
year3_matches = []
for i, s in enumerate(slides):
    blob = json.dumps(s, ensure_ascii=False)
    if 'DocAdoct' in blob or 'FJC 2028' in blob or 'ISOT 2028' in blob:
        year3_matches.append((i, s))
assert len(year3_matches) == 1, [m[1].get('title') for m in year3_matches]
year3_slide = year3_matches[0][1]

# Remove SORBET and COBEX study slides, plus the temporary third-year divider.
clean = []
for s in slides:
    blob = json.dumps(s, ensure_ascii=False)
    study = str(s.get('study', '')).upper()
    is_removed_study = study in REMOVED or any(f'data-study="{name}"' in blob for name in REMOVED) and study in REMOVED
    is_year3_divider = bool(s.get('divider')) and (
        s.get('title') == 'Troisième année'
        or s.get('title') == 'Third year'
        or s.get('_fr', {}).get('title') == 'Troisième année'
        or s.get('_en', {}).get('title') == 'Third year'
    )
    if is_removed_study or is_year3_divider:
        continue
    if s is year3_slide:
        continue
    clean.append(s)
slides = clean

# Remove visible cards, pills and plain residues from all remaining HTML blocks.
def strip_removed_from_html(html):
    if not isinstance(html, str):
        return html
    for name in REMOVED:
        # Cards and study blocks.
        html = re.sub(r'<article\b(?=[^>]*data-study=\\"' + name + r'\\")[\s\S]*?</article>', '', html)
        html = re.sub(r'<article\b(?=[^>]*data-study="' + name + r'")[\s\S]*?</article>', '', html)
        # Spans and pills.
        html = re.sub(r'<span\b(?=[^>]*data-study=\\"' + name + r'\\")[\s\S]*?</span>', '', html)
        html = re.sub(r'<span\b(?=[^>]*data-study="' + name + r'")[\s\S]*?</span>', '', html)
        # Bare labels left in short lists.
        html = re.sub(r'\s*[·,;]\s*' + name + r'\b', '', html)
        html = re.sub(r'\b' + name + r'\s*[·,;]\s*', '', html)
        html = html.replace(name, '')
    html = re.sub(r'(?:<i></i>){2,}', '<i></i>', html)
    html = re.sub(r'\s{2,}', ' ', html)
    html = html.replace('><', '><')
    return html

for s in slides:
    for key in ('content', 'lead', 'title', 'kicker', 'section', 'chapter', 'notes'):
        if key in s:
            s[key] = strip_removed_from_html(s[key])
    for langkey in ('_fr', '_en'):
        d = s.get(langkey)
        if isinstance(d, dict):
            for key in ('content', 'lead', 'title', 'kicker', 'section', 'notes'):
                if key in d:
                    d[key] = strip_removed_from_html(d[key])

# Prepare and move year 3 activities to the end of the complementary section, after BRAUDOLF.
for d, fr in ((year3_slide, True), (year3_slide.get('_fr', {}), True), (year3_slide.get('_en', {}), False)):
    if not isinstance(d, dict):
        continue
    d['section'] = 'Compléments' if fr else 'Complements'
    d['chapter'] = 'Compléments' if fr else 'Complements'
    d['kicker'] = 'Activités doctorales à venir' if fr else 'Upcoming doctoral activities'
    d['title'] = 'Activités doctorales prévues - 2027-2028' if fr else 'Planned doctoral activities - 2027-2028'
    d['lead'] = 'Ces activités complètent la programmation scientifique de fin de thèse.' if fr else 'These activities complete the final-year scientific programme.'
year3_slide['section'] = 'Compléments'
year3_slide['chapter'] = 'Compléments'
year3_slide['appendix'] = False
year3_slide['divider'] = False
year3_slide['hero'] = False

# Insert after the BRAUDOLF slide. If absent, insert after the complementary overview.
braudolf_indices = [i for i, s in enumerate(slides) if s.get('study') == 'BRAUDOLF' or 'BRAUDOLF' in json.dumps(s, ensure_ascii=False)]
assert braudolf_indices, 'BRAUDOLF insertion anchor not found'
insert_pos = max(braudolf_indices) + 1
slides[insert_pos:insert_pos] = [year3_slide]

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

# Remove any remaining SORBET or COBEX occurrences outside the slide JSON, including CSS and JS maps.
for name in REMOVED:
    text = re.sub(r'\n?\s*\[data-study="' + name + r'"\][^{]*\{[^}]*\}', '', text)
    text = re.sub(r"[,'\"]" + name + r"[,'\"]", lambda m: m.group(0).replace(name, ''), text)
    text = text.replace(name, '')

# Replace the local timeline function with a metadata-based version so section markers remain correct after deletions and moves.
fn_start = text.index('function partTimelineFor(index){')
fn_end = text.index('\nfunction renderPartTimeline', fn_start)
new_fn = r'''function partTimelineFor(index){
  const s=slides[index]||{};
  if(s.appendix||s.hero||s.divider) return null;
  const E=document.documentElement.lang==='en';
  const raw=((s.section||'')+' '+(s.chapter||'')+' '+(s.title||'')+' '+(s.study||''));
  const t=raw.toLowerCase();
  const study=String(s.study||'').toUpperCase();
  if(t.includes('année 2')||t.includes('year 2')||['SOFT','OASIS','TWIXOLF'].includes(study)){
    const steps=E?['PRIORITIES','SOFT','OASIS','TWIXOLF','ACTIVITIES','PUBLICATIONS']:['PRIORITÉS','SOFT','OASIS','TWIXOLF','ACTIVITÉS','PUBLICATIONS'];
    let active=0;
    if(study==='SOFT') active=1;
    else if(study==='OASIS') active=2;
    else if(study==='TWIXOLF') active=3;
    else if(t.includes('activité')||t.includes('activities')) active=4;
    else if(t.includes('publication')) active=5;
    return {steps,active};
  }
  if(t.includes('complément')||t.includes('complement')||t.includes('extension')||['SOLAR','BRAUD','BRAUDOLF'].includes(study)){
    const steps=E?['OVERVIEW','SOLAR','BRAUD','BRAUDOLF','ACTIVITIES']:['VUE D\'ENSEMBLE','SOLAR','BRAUD','BRAUDOLF','ACTIVITÉS'];
    let active=0;
    if(study==='SOLAR') active=1;
    else if(study==='BRAUD') active=2;
    else if(study==='BRAUDOLF') active=3;
    else if(t.includes('activité')||t.includes('activities')||t.includes('2027-2028')) active=4;
    return {steps,active};
  }
  if(t.includes('calendrier')||t.includes('planning')||t.includes('soutenance')||t.includes('defense')){
    let active=0;
    if(t.includes('études')||t.includes('studies')) active=1;
    if(t.includes('soutenance')||t.includes('defense')) active=2;
    return {steps:E?['GLOBAL','STUDIES','DEFENSE']:['GLOBAL','ÉTUDES','SOUTENANCE'],active};
  }
  if(t.includes('bilan')||t.includes('discussion')||t.includes('merci')||t.includes('summary')||t.includes('thank')){
    let active=0;
    if(t.includes('discussion')) active=1;
    if(t.includes('merci')||t.includes('thank')) active=2;
    return {steps:E?['SUMMARY','DISCUSSION','THANK YOU']:['BILAN','DISCUSSION','MERCI'],active};
  }
  const n=index+1;
  if(n>=4&&n<=12){
    const steps=E?['VISION + AUDITION','TIME','SPACE','INTEGRATION','SYNTHESIS','OLFACTION','AXES','INFLUENCE']:['VISION + AUDITION','TEMPS','ESPACE','INTÉGRATION','SYNTHÈSE','OLFACTION','AXES','INFLUENCE'];
    return {steps,active:Math.min(Math.max(n-4,0),steps.length-1)};
  }
  if(n>=14&&n<=18){
    const steps=E?['QUESTION','TREE','AXIS 1','AXIS 2','PRIORITIES']:['QUESTION','ARBRE','AXE 1','AXE 2','PRIORITÉS'];
    return {steps,active:Math.min(Math.max(n-14,0),steps.length-1)};
  }
  if(t.includes('année 1')||t.includes('year 1')||['TWIXAV','VIBEX','FLUXOLF'].includes(study)){
    const steps=E?['OVERVIEW','TWIXAV','VIBEX','FLUXOLF','ACTIVITIES','TRANSITION']:['BILAN','TWIXAV','VIBEX','FLUXOLF','ACTIVITÉS','TRANSITION'];
    let active=0;
    if(study==='TWIXAV') active=1;
    else if(study==='VIBEX') active=2;
    else if(study==='FLUXOLF') active=3;
    else if(t.includes('activité')||t.includes('activities')||t.includes('enseignement')) active=4;
    else if(t.includes('transition')) active=5;
    return {steps,active};
  }
  return null;
}'''
text = text[:fn_start] + new_fn + text[fn_end:]

# Final checks: no removed labels anywhere, no third-year divider, moved activity slide is after BRAUDOLF.
assert 'SORBET' not in text
assert 'COBEX' not in text
assert 'Troisième année</h1>' not in text
assert 'Third year</h1>' not in text
assert 'DocAdoct' in text
visible = [s for s in slides if not s.get('appendix')]
idx_activity = [i for i, s in enumerate(visible) if 'DocAdoct' in json.dumps(s, ensure_ascii=False)]
idx_braudolf = [i for i, s in enumerate(visible) if 'BRAUDOLF' in json.dumps(s, ensure_ascii=False)]
assert len(idx_activity) == 1
assert idx_braudolf and idx_activity[0] > max(idx_braudolf)
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before

index.write_text(text, encoding='utf-8')
