from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'CSI_TIMELINE_KEYWORDS_V2' in text:
    raise SystemExit('Timeline keyword refinement already applied')

new_func = r'''function timelineStepLabel(s,E){
  // CSI_TIMELINE_KEYWORDS_V2 - short keywords taken from the slides actually crossed inside the current local part.
  const study=String(s.study||'').trim();
  const title=String(s.title||'').trim();
  const kicker=String(s.kicker||'').trim();
  const stripStudy=(value)=>{
    let out=String(value||'').trim();
    if(study){
      const safe=study.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
      out=out.replace(new RegExp('^'+safe+'\\s*[-:]?\\s*','i'),'').trim();
    }
    return out;
  };

  let raw=stripStudy(title);
  if(!raw || raw.toUpperCase()===study.toUpperCase()) raw=stripStudy(kicker);
  if(!raw) return study || '';

  const low=raw.toLowerCase();
  const rules=[
    [/no space|no time/, 'NO SPACE / NO TIME'],
    [/opposition/, 'OPPOSITION'],
    [/manque à combler|gap to fill/, E?'GAP':'MANQUE'],
    [/deux axes|two axes/, E?'TWO AXES':'DEUX AXES'],
    [/référence visuelle|visual reference/, E?'REFERENCE':'RÉFÉRENCE'],
    [/effet des conditions|condition effect/, 'CONDITIONS'],
    [/effet de la taille|image-size effect|size effect/, E?'IMAGE SIZE':'TAILLE'],
    [/fenêtre.*rétrécit|window.*narrow|largeur.*tbw|tbw.*width/, E?'TBW WIDTH':'LARGEUR TBW'],
    [/ajouter l['’]olfaction|adding olfaction|add olfaction/, E?'ADD OLFACTION':'AJOUT OLFACTION'],
    [/cer.*dpd|dpd.*cer/, 'CER / DPD'],
    [/soutenance|defense/, E?'DEFENSE':'SOUTENANCE'],
    [/planification|planning/, E?'PLANNING':'PLANIFICATION'],
    [/discussion|interprétation|interpretation/, 'DISCUSSION'],
    [/^méthode$|^method$/, E?'METHOD':'MÉTHODE'],
    [/^paradigme$|^paradigm$/, E?'PARADIGM':'PARADIGME'],
    [/^résultats?$|^results?$/, E?'RESULTS':'RÉSULTATS'],
    [/^introduction$|^intro$/, 'INTRO']
  ];
  for(const [rx,label] of rules){ if(rx.test(low)) return label; }

  raw=raw
    .replace(/\b20\d{2}(?:\s*-\s*20\d{2})?\b/g,'')
    .replace(/[–—]/g,'-')
    .replace(/\s+/g,' ')
    .trim();

  const stop=new Set(E
    ? ['the','a','an','of','to','and','in','on','for','with','from','by','is','are','our','this','that','first','year','study','studies','effect']
    : ['le','la','les','un','une','des','de','du','d','à','au','aux','et','en','dans','sur','pour','par','avec','sans','est','sont','ce','cette','ces','notre','nos','année','étude','études','effet']);
  const words=raw.split(/[\s/:,-]+/).map(w=>w.trim()).filter(w=>w && !stop.has(w.toLowerCase()));
  const picked=[];
  for(const word of words){
    const candidate=[...picked,word].join(' ');
    if(candidate.length>19 && picked.length) break;
    picked.push(word);
    if(picked.length===2) break;
  }
  let label=(picked.join(' ')||raw).toUpperCase();
  if(label.length>20) label=label.slice(0,19).trim()+'…';
  return label;
}'''

pattern = r"function timelineStepLabel\(s,E\)\{.*?\n\}\n\nfunction partTimelineFor"
text2, n = re.subn(pattern, new_func + "\n\nfunction partTimelineFor", text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Expected one timelineStepLabel function, found {n}')

path.write_text(text2, encoding='utf-8')
print('Timeline labels refined to slide-specific keywords.')
