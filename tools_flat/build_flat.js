const fs = require('fs');
const { chromium } = require('playwright');

const SAVE = 'index_save.html';
const OUT = 'index.html';

function clone(x){ return JSON.parse(JSON.stringify(x)); }
function text(s){ return `${s?.section||''} ${s?.kicker||''} ${s?.title||''} ${s?.lead||''} ${s?.content||''}`; }
function idx(slides, rx){ return slides.findIndex(s => rx.test(String(s?.title||''))); }
function anyIdx(slides, rx){ return slides.findIndex(s => rx.test(text(s))); }
function makeSlide(section,kicker,title,lead,content,study='',notes=''){
  const s={section,kicker,title,lead,content,notes};
  if(study) s.study=study;
  s._fr={section,kicker,title,lead,content,notes};
  return s;
}
function card(tag,title,body,dark=false){
  return `<div class="card${dark?' dark':''}"><div class="mono">${tag}</div><h3>${title}</h3><p>${body}</p></div>`;
}
function grid3(a,b,c){ return `<div class="grid three">${a}${b}${c}</div>`; }
function setSlide(s,p){ if(!s)return; Object.assign(s,p); if(s._fr) Object.assign(s._fr,p); }

function addScience(slides){
  // Clean one obsolete CSI member if it is still present anywhere in the saved state.
  for(const s of slides){
    for(const k of ['content','lead','notes']) if(typeof s[k]==='string') s[k]=s[k].replace(/Jean-Pierre THIBAUT/gi,'');
    if(s._fr) for(const k of ['content','lead','notes']) if(typeof s._fr[k]==='string') s._fr[k]=s._fr[k].replace(/Jean-Pierre THIBAUT/gi,'');
    if(s._en) for(const k of ['content','lead','notes']) if(typeof s._en[k]==='string') s._en[k]=s._en[k].replace(/Jean-Pierre THIBAUT/gi,'');
  }

  // General introduction - insert the theoretical lock immediately after the thesis axes.
  let axes=idx(slides,/deux axes|axes de la thèse|deux familles/i);
  if(axes<0) axes=anyIdx(slides,/axe 1[\s\S]*axe 2/i);
  if(axes<0) axes=idx(slides,/Y a-t-il un espace-temps pour les odeurs/i);
  const sela=makeSlide('Introduction générale','Verrou théorique','« No space, no time? » - le paradoxe de l’attention olfactive',
    'Sela et Sobel (2010) décrivent une modalité dont les contraintes spatiales et temporelles diffèrent fortement de celles de la vision et de l’audition. La thèse transforme cette asymétrie en question expérimentale.',
    grid3(
      card('Espace','Une spatialisation limitée','Les capacités humaines de localisation olfactive sont réduites relativement à la vision et à l’audition, ce qui contraint la sélection spatiale et la capture attentionnelle.'),
      card('Temps','Un échantillonnage par le sniff','L’information olfactive est échantillonnée de façon discontinue au rythme des inspirations, avec une temporalité propre à la délivrance et à la respiration.'),
      card('STOLF','Le verrou à tester','Ces contraintes abolissent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?',true)
    )+`<div class="callout" style="margin-top:16px"><strong>Point de départ :</strong> « No space, no time? » est une question de travail, pas l’affirmation que l’olfaction serait dépourvue de représentations spatiales ou temporelles.</div><div class="csi-cite">Sela, L. & Sobel, N. (2010). Human olfaction: a constant state of change-blindness. Experimental Brain Research, 205, 13-29.</div>`,
    '', 'Présenter Sela et Sobel comme un verrou théorique, pas comme une preuve d’absence d’espace ou de temps olfactif.');
  slides.splice(Math.max(0,axes+1),0,sela);

  // Architecture - replace the flat project overview in place.
  let arch=idx(slides,/Dix études principales|architecture du programme/i);
  const archSlide=makeSlide('Introduction générale','Architecture du programme','Cinq études centrales, des extensions clairement conditionnelles',
    'Le programme est hiérarchisé autour de cinq études directement nécessaires à la thèse. Les autres projets restent des prolongements activés selon les résultats, la faisabilité et le calendrier.',
    `<div class="grid three">${card('Référence temporelle','TWIXAV','Fenêtre temporelle audiovisuelle et asymétrie qui motive SOFT.')}${card('Référence spatiale','VIBEX','Boundary Extension visuelle servant de base directe à OASIS.')}${card('Étude centrale','SOFT','Onset, offset et durée perçus en audition, vision et olfaction.',true)}${card('Étude centrale','OASIS','Influence olfactive sur la mémoire spatiale des scènes.')}${card('Étude centrale','TWIXOLF','Transposition de la liaison temporelle à l’olfaction.')}${card('Projet annexe','FLUXOLF','Projet méthodologique distinct des deux axes de thèse.')}</div><div class="bridge"><strong>Extensions conditionnelles :</strong> SORBET - SOLAR - COBEX - BRAUD - BRAUDOLF.</div>`);
  if(arch>=0) slides[arch]=archSlide; else slides.splice(Math.max(0,axes+2),0,archSlide);

  // TWIXAV - Introduction / Method / Results / Discussion.
  let twm=idx(slides,/^TWIXAV\b/i);
  if(twm<0) twm=anyIdx(slides,/TWIXAV[\s\S]*jugement de simultanéité/i);
  if(twm>=0){
    setSlide(slides[twm],{section:'Études de l’année 1',kicker:'TWIXAV - Méthode',title:'TWIXAV - Méthode',study:'TWIXAV'});
    slides.splice(twm,0,makeSlide('Études de l’année 1','TWIXAV - Introduction','TWIXAV - pourquoi commencer par une fenêtre temporelle audiovisuelle ?',
      'Avant d’introduire l’olfaction, TWIXAV établit une référence temporelle dans deux modalités dont l’intégration est mieux caractérisée.',
      grid3(
        card('Concept','Temporal Binding Window','La probabilité de juger deux événements comme simultanés varie avec leur décalage temporel et permet de caractériser une fenêtre d’intégration.'),
        card('Question','La durée modifie-t-elle cette fenêtre ?','TWIXAV teste si la durée des stimuli affecte la tolérance au décalage audiovisuel plutôt que de supposer une fenêtre unique et fixe.'),
        card('Enjeu','Comprendre l’asymétrie','Une différence entre les directions temporelles constitue un indice mécanistique et motive une mesure directe du début et de la fin perceptifs avec SOFT.',true)
      ),'TWIXAV'));
  }
  let twr=idx(slides,/Un effet net de la durée|TWIXAV - Résultats/i);
  if(twr>=0){
    setSlide(slides[twr],{section:'Études de l’année 1',kicker:'TWIXAV - Résultats',title:'TWIXAV - Résultats',study:'TWIXAV'});
    slides.splice(twr+1,0,makeSlide('Études de l’année 1','TWIXAV - Discussion','TWIXAV - ce que les résultats changent pour la suite',
      'Les effets observés montrent que la synchronie audiovisuelle ne se résume pas à un seuil temporel unique. La durée et la direction du décalage doivent être prises en compte avant toute transposition à l’olfaction.',
      grid3(
        card('Résultat','Durée × SOA','Les effets de durée, de SOA et leur interaction indiquent que la fenêtre temporelle dépend des propriétés du stimulus.'),
        card('À consolider','PSS, fenêtre, asymétrie','Ces indicateurs sont consolidés dans les analyses finales sans ajouter de statistiques non encore verrouillées.'),
        card('Décision','SOFT puis TWIXOLF','SOFT teste directement onset et offset perceptifs, puis TWIXOLF transpose la question à l’olfaction.',true)
      ),'TWIXAV'));
  }

  // VIBEX - Introduction / Method / Results / Discussion, then year-1 synthesis.
  let vib=idx(slides,/^VIBEX\b/i);
  if(vib>=0){
    setSlide(slides[vib],{section:'Études de l’année 1',kicker:'VIBEX - Méthode',title:'VIBEX - Méthode',study:'VIBEX'});
    slides.splice(vib,0,makeSlide('Études de l’année 1','VIBEX - Introduction','VIBEX - pourquoi établir une référence visuelle ?',
      'VIBEX établit une référence comportementale de Boundary Extension avant d’introduire une modulation olfactive avec OASIS.',
      grid3(
        card('Phénomène','Boundary Extension','La mémoire d’une scène peut inclure des informations spatiales au-delà de ses limites réellement présentées, révélant une représentation constructive de l’espace.'),
        card('Référence','Une base visuelle contrôlée','Le paradigme doit être fonctionnel et stable sans odeur avant de pouvoir attribuer une modification ultérieure au contexte olfactif.'),
        card('Suite','Préparer OASIS','VIBEX fixe les scènes, la logique de comparaison et les indices comportementaux qui serviront de référence à l’étude olfactive.',true)
      ),'VIBEX'));
    vib=idx(slides,/^VIBEX - Méthode$/i);
    const vr=makeSlide('Études de l’année 1','VIBEX - Résultats','VIBEX - résultats du prétest et statut',
      'Le prétest montre que le paradigme est opérationnel et fournit des données exploitables. Les analyses finales doivent encore verrouiller la stabilité des effets.',
      grid3(
        card('Matériel','24 scènes','Le matériel visuel et la procédure permettent une collecte structurée sur les différentes configurations spatiales.'),
        card('Structure','LL, SS, LS et SL','Les quatre conditions permettent de caractériser les jugements identique/différent nécessaires aux indices de Boundary Extension.'),
        card('Statut','Prétest exploitable','Paradigme fonctionnel et données exploitables, sans inventer de statistique inférentielle supplémentaire avant consolidation.',true)
      ),'VIBEX');
    const vd=makeSlide('Études de l’année 1','VIBEX - Discussion','VIBEX - ce que le prétest permet maintenant',
      'Le prétest remplit son rôle de référence : le paradigme visuel est utilisable et peut maintenant être stabilisé avant sa transposition olfactive.',
      grid3(
        card('Acquis','Faisabilité','La chaîne de présentation et de réponse fonctionne sur les scènes et les différentes configurations spatiales.'),
        card('À verrouiller','Stabilité des indices','Norming des scènes, stabilité par taille et indice global de Boundary Extension sont finalisés avant l’étude suivante.'),
        card('Suite','Pont vers OASIS','OASIS conserve cette référence visuelle et teste si un contexte olfactif modifie la représentation spatiale mémorisée.',true)
      ),'VIBEX');
    slides.splice(vib+1,0,vr,vd);
    const vdi=idx(slides,/VIBEX - ce que le prétest permet maintenant/i);
    const y1=makeSlide('Bilan de première année','Deux références complémentaires','Deux acquis expérimentaux structurent la suite',
      'La première année fournit une référence temporelle et une référence spatiale. Ces deux bases orientent directement les trois études centrales de l’année suivante.',
      grid3(
        card('Temps','TWIXAV','Des données temporelles exploitables, un effet de la durée et une asymétrie qui justifie une mesure plus directe des bornes perceptives.'),
        card('Espace','VIBEX','Un paradigme de Boundary Extension fonctionnel et un prétest exploitable qui fournit la référence nécessaire à OASIS.'),
        card('Année 2','Trois études centrales','SOFT caractérise le temps propre des modalités, OASIS teste l’influence olfactive sur l’espace mémorisé, puis TWIXOLF transpose la liaison temporelle.',true)
      ));
    const tr=makeSlide('Transition vers l’année 2','Logique expérimentale','Deux références, trois études centrales pour l’année 2',
      'La progression relie les acquis de l’année 1 aux études centrales suivantes sans ouvrir prématurément les extensions conditionnelles.',
      `<div class="grid two">${card('Branche temporelle','TWIXAV → SOFT → TWIXOLF','De l’asymétrie audiovisuelle à la mesure des bornes perceptives, puis à la transposition olfactive.')}${card('Branche spatiale','VIBEX → OASIS','D’une référence visuelle de Boundary Extension à l’étude de l’influence d’un contexte olfactif.',true)}</div>`);
    slides.splice(vdi+1,0,y1,tr);
  }

  // SOFT - Introduction and Method at its original location.
  let soft=idx(slides,/^SOFT\b/i);
  if(soft>=0){
    setSlide(slides[soft],{section:'Études de l’année 2',kicker:'SOFT - Introduction',title:'SOFT - mesurer le temps propre de chaque modalité',study:'SOFT'});
    slides.splice(soft+1,0,makeSlide('Études de l’année 2','SOFT - Méthode','SOFT - Méthode',
      'Le protocole estime séparément le début et la fin perçus afin de tester si les asymétries temporelles reflètent des propriétés propres aux modalités.',
      grid3(
        card('Modalités','Audition, vision, olfaction','Les trois modalités sont comparées dans une architecture commune.'),
        card('Estimations','Onset, offset, durée','Les réponses permettent d’estimer le début perçu, la fin perçue et la durée dérivée sans figer ici les durées finales du protocole.'),
        card('Chaîne temporelle','Commandé, délivré, perçu','Logs press/release, Sniff-0, respiration et triggers distinguent commande logicielle, délivrance physique et disponibilité perceptive.',true)
      ),'SOFT'));
  }

  // OASIS - direct VIBEX extension, no approach-avoidance framing.
  let oasis=idx(slides,/^OASIS\b/i);
  if(oasis>=0){
    slides[oasis]=makeSlide('Études de l’année 2','OASIS - Introduction','OASIS - tester l’influence olfactive sur la mémoire spatiale des scènes',
      'OASIS prolonge directement VIBEX : la référence visuelle de Boundary Extension est conservée et un contexte olfactif est introduit pour tester son influence sur la représentation spatiale mémorisée.',
      grid3(
        card('Point de départ','VIBEX comme référence','Les scènes, la logique identique/différent et les indices de Boundary Extension fournissent une base visuelle déjà caractérisée.'),
        card('Question','Que change l’odeur ?','Tester si un contexte olfactif modifie le jugement spatial, l’accuracy, le temps de réponse ou l’indice global de Boundary Extension.'),
        card('Axe 2','Mémoire spatiale','L’enjeu est la représentation spatiale des scènes. OASIS n’est pas présenté comme une étude d’approche-évitement.',true)
      ),'OASIS');
    slides.splice(oasis+1,0,makeSlide('Études de l’année 2','OASIS - Méthode','OASIS - Méthode',
      'La méthode conserve la structure comportementale de VIBEX et ajoute une stimulation olfactive contrôlée, avec les contrôles nécessaires à l’interprétation d’un effet multisensoriel.',
      grid3(
        card('Référence visuelle','Structure de VIBEX','Scènes et logique expérimentale issues de VIBEX, avec conditions spatiales comparables.'),
        card('Contexte olfactif','Délivrance contrôlée','Sniff-0 et suivi respiratoire, avec contrôle de la stabilité du stimulus, de l’intensité et de la saillance.'),
        card('Mesures','Comportement et contrôles','p(same), accuracy, temps de réponse, indice global de Boundary Extension et physiologie selon le protocole final.',true)
      ),'OASIS'));
  }

  // TWIXOLF - Introduction and Method.
  let two=idx(slides,/^TWIXOLF\b/i);
  if(two>=0){
    setSlide(slides[two],{section:'Études de l’année 2',kicker:'TWIXOLF - Introduction',title:'TWIXOLF - transposer la liaison temporelle à l’olfaction',study:'TWIXOLF'});
    slides.splice(two+1,0,makeSlide('Études de l’année 2','TWIXOLF - Méthode','TWIXOLF - Méthode',
      'Le protocole adapte les décalages temporels et le jugement de simultanéité à une stimulation olfactive réellement synchronisée à l’inspiration.',
      grid3(
        card('Paradigme','Jugement temporel','Olfaction avec une modalité de référence, décalages temporels et jugement de simultanéité.'),
        card('Synchronisation','Respiration et délivrance','Déclenchement sur inspiration, Sniff-0, suivi respiratoire, PsychoPy, triggers et logs.'),
        card('Indices','PSS, fenêtre, asymétrie','p(same), PSS, largeur de fenêtre, asymétrie et stabilité. Les SOA définitifs restent à verrouiller par les pilotes.',true)
      )+`<div class="callout" style="margin-top:16px"><strong>Principe :</strong> l’analyse se réfère au moment où le stimulus devient réellement disponible au participant, pas seulement à l’horodatage logiciel.</div>`,'TWIXOLF'));
  }
  return slides;
}

function replaceSlidesArray(base, slides){
  const m=/\bconst\s+slides\s*=\s*\[/.exec(base);
  if(!m) throw new Error('Native slides array not found in base');
  const start=base.indexOf('[',m.index);
  let depth=0, quote=null, esc=false, end=-1;
  for(let i=start;i<base.length;i++){
    const ch=base[i];
    if(quote){
      if(esc) esc=false;
      else if(ch==='\\') esc=true;
      else if(ch===quote) quote=null;
      continue;
    }
    if(ch==='"'||ch==="'"||ch==='`'){ quote=ch; continue; }
    if(ch==='[') depth++;
    else if(ch===']'){
      depth--;
      if(depth===0){ end=i; break; }
    }
  }
  if(end<0) throw new Error('Could not close native slides array');
  return base.slice(0,start)+JSON.stringify(slides)+base.slice(end+1);
}

(async()=>{
  const saved=fs.readFileSync(SAVE,'utf8');
  const bm=/\bconst\s+base\s*=\s*("(?:\\.|[^"\\])*")\s*;/.exec(saved);
  if(!bm) throw new Error('Embedded base not found in saved index');
  let base=JSON.parse(bm[1]);

  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1600,height:1000}});
  const errs=[];
  page.on('pageerror',e=>errs.push(e.message));
  await page.goto('http://127.0.0.1:8000/index_save.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForTimeout(3200);
  const handle=await page.$('#presentation');
  const frame=await handle.contentFrame();
  const state=await frame.evaluate(()=>({
    slides: window.CSI11?.slides || [],
    styles:[...document.querySelectorAll('style')].map(s=>s.textContent||''),
    title:document.title
  }));
  await browser.close();
  if(errs.length) throw new Error('Saved runtime errors: '+errs.join(' | '));
  if(!Array.isArray(state.slides)||state.slides.length<20) throw new Error('Saved runtime did not expose final slides');

  let slides=addScience(clone(state.slides));
  base=replaceSlidesArray(base,slides);

  // Bake the fully-resolved V17 visual state into one static stylesheet.
  const flatCss=`\n<style id="csi-flat-v17">\n${state.styles.join('\n')}\n/* final single-layer study identities */\n.slide.v16-study-slide{--accent:var(--study,var(--green-main));}\n.csi-flat-sheet{position:absolute;right:24px;top:92px;z-index:20;padding:7px 11px;border-radius:999px;border:1px solid var(--line);background:var(--white);color:var(--accent-strong);font-weight:900;text-decoration:none;font-size:.72rem;box-shadow:var(--shadow-soft)}\n</style>\n`;
  base=base.replace('</head>',flatCss+'</head>');

  const flatRuntime=`\n<script id="csi-single-runtime">\n(()=>{\n  const COLORS={TWIXAV:'#2f6f9f',SOFT:'#7652a8',TWIXOLF:'#c36c32',VIBEX:'#2f7d5a',OASIS:'#b44e6c',SORBET:'#9a6b20',SOLAR:'#d09422',COBEX:'#5865a8',BRAUD:'#4f7187',BRAUDOLF:'#875a7c',FLUXOLF:'#a34d5d'};\n  const PDF={TWIXAV:'affiches/TWIXAV.pdf',TWIXOLF:'affiches/TWIXOLF.pdf',SOFT:'affiches/SOFT.pdf',VIBEX:'affiches/VIBEX.pdf',OASIS:'affiches/OASIS.pdf'};\n  function studyOf(s){const explicit=String(s&&s.study||'').toUpperCase();if(explicit)return explicit;const m=String(s&&s.title||'').match(/^(TWIXAV|TWIXOLF|SOFT|VIBEX|OASIS|SORBET|SOLAR|COBEX|BRAUDOLF|BRAUD|FLUXOLF)\\b/i);return m?m[1].toUpperCase():''}\n  function enhance(){\n    const els=[...document.querySelectorAll('#deck .slide,.slide')];\n    slides.forEach((s,i)=>{\n      const el=els[i];if(!el)return;const k=studyOf(s),c=COLORS[k];\n      if(c){el.style.setProperty('--study',c);el.style.setProperty('--accent',c);el.classList.add('v16-study-slide');}\n      if(PDF[k]&&!el.querySelector('.csi-flat-sheet')){const a=document.createElement('a');a.className='csi-flat-sheet';a.href=PDF[k];a.target='_blank';a.rel='noopener';a.textContent='Fiche '+k;el.appendChild(a)}\n    });\n    document.documentElement.dataset.singleLayer='1';\n  }\n  const old=window.renderSlides;\n  if(typeof old==='function'){window.renderSlides=function(){const r=old.apply(this,arguments);queueMicrotask(enhance);return r}}\n  enhance();\n  setTimeout(enhance,0);\n})();\n</script>\n`;
  base=base.replace('</body>',flatRuntime+'</body>');
  base=base.replace(/V16 - 03\/09/g,'CSI-1 - couche unique');
  fs.writeFileSync(OUT,base,'utf8');

  const must=['No space, no time?','TWIXAV - pourquoi commencer','TWIXAV - Méthode','TWIXAV - Résultats','TWIXAV - ce que les résultats changent','VIBEX - pourquoi établir','VIBEX - Méthode','VIBEX - résultats du prétest','VIBEX - ce que le prétest permet','Deux acquis expérimentaux structurent la suite','SOFT - Méthode','OASIS - Méthode','TWIXOLF - Méthode'];
  const out=fs.readFileSync(OUT,'utf8');
  for(const x of must) if(!out.includes(x)) throw new Error('Missing final content: '+x);
  console.log('Built single-layer index with',slides.length,'slides and',state.styles.length,'resolved style blocks');
})();
