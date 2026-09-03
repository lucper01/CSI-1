(function(){
  const frame=document.getElementById('presentation');
  if(!frame)return;
  const BASE='https://raw.githubusercontent.com/lucper01/CSI-1/main/';
  const UBE='https://til.u-bourgogne.fr/wp-content/uploads/2025/01/logo-UBE-drapeau-quadri.jpg';
  const CNRS='https://www.sb-roscoff.fr/system/files/styles/highest/private/images/LOGO_CNRS_2019_BLEU_12.png.webp?itok=B9mit875';
  const INRAE='https://insituculture.eu/wp-content/uploads/2022/09/INRAE_logo-1.png';
  const BIOSEMI_B64=BASE+'assets/current/biosemi.webp.b64';
  const CYNE='https://www.cynexo.com/wp-content/uploads/2018/09/sniff-O-foto1.jpg';
  const BIOPAC='https://img.medicalexpo.com/images_me/photo-g/126111-14323895.jpg';

  const txt=(s)=>`${s.title||''} ${s.kicker||''} ${s.lead||''} ${s.content||''}`;
  const addRefs=(s,refs)=>{
    if(!s||s.content.includes('csi-extra-refs')) return;
    s.content += `<div class="csi-extra-refs"><strong>Références complémentaires :</strong> ${refs}</div>`;
    if(s._fr) s._fr.content=s.content;
  };
  const find=(slides,...patterns)=>slides.find(s=>patterns.some(p=>p.test(txt(s))));
  const moveBefore=(slides,item,before)=>{
    if(!item||!before||item===before)return;
    const a=slides.indexOf(item),b=slides.indexOf(before); if(a<0||b<0||a<b)return;
    slides.splice(a,1); slides.splice(slides.indexOf(before),0,item);
  };
  const swapTerms=(html,a,b)=> html ? html.replaceAll(a,'__TMP_SWAP__').replaceAll(b,a).replaceAll('__TMP_SWAP__',b) : html;

  function patch(){
    try{
      const w=frame.contentWindow,d=w.document,C=w.CSI11;
      if(!C||!Array.isArray(C.slides)) return;
      const slides=C.slides;

      const style=d.createElement('style');
      style.textContent=`
        .csi-institutions{margin-top:18px;display:flex;flex-direction:column;gap:12px;max-width:1120px}
        .csi-logo-row{display:flex;align-items:center;gap:16px;flex-wrap:wrap;background:#fff;border:1px solid var(--line,#d9ded9);border-radius:18px;padding:10px 14px}.csi-logo-row img{width:auto;height:54px;max-width:180px;object-fit:contain}.csi-logo-word{font-weight:700;color:#222;line-height:1.05}.csi-logo-word b{font-size:1.15em}
        .csi-members{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}
        .csi-member{padding:12px 14px;border-radius:16px;border:1px solid var(--line,#d9ded9);background:var(--white,#fff)}
        .csi-member strong{display:block;color:var(--accent-strong,#073d2b);font-size:.9rem}.csi-member span{color:var(--muted,#647067);font-size:.78rem}
        .csi-extra-refs{margin-top:10px;padding-top:8px;border-top:1px solid var(--line,#d9ded9);font-size:.68rem;line-height:1.32;color:var(--muted,#647067)}
        .csi-extra-refs strong{color:var(--accent-strong,#073d2b)}
        .csi-hardware-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
        .csi-hardware-card{overflow:hidden;border:1px solid var(--line,#d9ded9);background:var(--white,#fff);border-radius:22px;box-shadow:var(--shadow-soft,0 8px 24px rgba(0,0,0,.07))}
        .csi-hardware-card img{display:block;width:100%;height:175px;object-fit:contain;background:#fff;padding:8px;box-sizing:border-box}
        .csi-hardware-card .copy{padding:14px 16px}.csi-hardware-card h3{margin:0 0 5px;font-size:1.05rem}.csi-hardware-card p{margin:0;font-size:.79rem;line-height:1.34;color:var(--muted,#647067)}
        .csi-thanks-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}.csi-thanks-grid .card{text-align:center}
        .csi-qbtn{margin-left:8px;border:1px solid var(--line,#d9ded9);background:var(--white,#fff);color:var(--accent-strong,#073d2b);border-radius:14px;padding:8px 12px;font-weight:900;cursor:pointer}
        #csiQOverlay{position:fixed;inset:0;z-index:100000;background:var(--bg,#f4f7f2);color:var(--text,#10251c);display:none;padding:clamp(26px,5vw,72px);box-sizing:border-box}
        #csiQOverlay.open{display:block}#csiQOverlay .qhead{display:flex;align-items:center;justify-content:space-between;gap:20px}#csiQOverlay h1{font:800 clamp(2.4rem,5vw,5.2rem)/.98 Georgia,serif;margin:12vh 0 0;color:var(--accent-strong,#073d2b)}#csiQOverlay p{color:var(--muted,#647067);font-size:1rem}#csiQOverlay button{border:1px solid var(--line,#d9ded9);background:var(--white,#fff);border-radius:14px;padding:9px 14px;font-weight:900;cursor:pointer}
        .csi-fit{padding-bottom:96px!important}.csi-fit .card,.csi-fit .decision-card,.csi-fit li{line-height:1.22!important}.csi-fit .card{padding-top:12px!important;padding-bottom:12px!important}
        @media(max-height:820px){.slide{padding-top:26px!important;padding-bottom:84px!important}.slide h1,.slide h2{font-size:clamp(2rem,4vw,3.7rem)!important}.slide .lead{margin-bottom:12px!important}.csi-fit{font-size:.9em}.csi-fit .card{padding:10px 13px!important}.csi-hardware-card img{height:130px}}
        @media(max-width:980px){.csi-members,.csi-thanks-grid,.csi-hardware-grid{grid-template-columns:1fr}.csi-hardware-card img{height:150px}}
      `;
      d.head.appendChild(style);

      const cover=find(slides,/espace-temps pour les odeurs/i,/comité de suivi individuel/i);
      if(cover && !cover.content.includes('csi-institutions')){
        cover.content += `<div class="csi-institutions"><div class="csi-logo-row"><img src="${UBE}" alt="Université Bourgogne Europe"><img src="${CNRS}" alt="CNRS"><img src="${INRAE}" alt="INRAE"><div class="csi-logo-word">L’Institut Agro<br><b>Dijon</b></div></div><div class="csi-members"><div class="csi-member"><strong>Jean-Pierre THIBAUT</strong><span>Référent de l'École Doctorale - responsable du suivi</span></div><div class="csi-member"><strong>Renaud BROCHARD</strong><span>Directeur de thèse</span></div><div class="csi-member"><strong>Arnaud LELEU</strong><span>Co-directeur de thèse</span></div></div></div>`;
        if(cover._fr)cover._fr.content=cover.content;
      }

      const roadmap=find(slides,/rétroplanning/i,/priorités à moyen terme/i,/roadmap/i);
      const difficulties=find(slides,/difficult/i,/contraintes techniques/i,/points de vigilance/i,/risques principaux/i);
      const hardware=find(slides,/dispositifs.*contraintes/i,/infrastructure multimodale/i,/matériel.*expérimental/i);
      if(difficulties&&roadmap) moveBefore(slides,difficulties,roadmap);
      if(hardware&&roadmap) moveBefore(slides,hardware,roadmap);

      slides.forEach(s=>{
        if(/rétroplanning|priorités à moyen terme|planning|calendrier/i.test(txt(s)) && /OASIS/i.test(txt(s)) && /TWIXOLF/i.test(txt(s))){
          s.content=swapTerms(s.content,'TWIXOLF','OASIS');
          if(s.lead)s.lead=swapTerms(s.lead,'TWIXOLF','OASIS');
          if(s._fr){s._fr.content=s.content;s._fr.lead=s.lead}
        }
      });

      const comm=find(slides,/communication/i,/valorisation/i,/rendre la recherche visible/i);
      if(comm){
        comm.title='Communications et médiation scientifique - calendrier envisagé';
        comm.lead='La diffusion est planifiée dans la continuité des collectes et des analyses, sans anticiper des résultats qui ne seraient pas encore stabilisés.';
        comm.content=`<div class="grid four"><div class="card dark"><h3>Septembre 2026</h3><p><strong>Nuit des chercheurs</strong><br>Médiation scientifique et présentation du programme STOLF.</p></div><div class="card"><h3>Octobre 2026</h3><p><strong>Fête de la Science</strong><br>Présentation grand public des enjeux de perception multisensorielle.</p></div><div class="card"><h3>Mars 2027</h3><p><strong>Expérimentarium</strong><br>Dispositif de médiation autour des expériences et méthodes.</p></div><div class="card"><h3>Juin 2027</h3><p><strong>FJC et JDD</strong><br>Communications selon la maturité des résultats disponibles à cette date.</p></div></div>`;
        if(comm._fr){comm._fr.title=comm.title;comm._fr.lead=comm.lead;comm._fr.content=comm.content}
      }

      let hw=find(slides,/dispositifs.*contraintes/i,/infrastructure multimodale/i,/EEG.*physiolog/i,/olfactom/i);
      if(hw){
        hw.title='Dispositifs expérimentaux et chaîne d’acquisition';
        hw.lead='Les principaux dispositifs sont présentés ici comme une chaîne instrumentale cohérente : stimulation olfactive, acquisition EEG et psychophysiologie.';
        hw.content=`<div class="csi-hardware-grid"><div class="csi-hardware-card"><img src="${CYNE}" alt="CyNexo Sniff-0 olfactometer"><div class="copy"><h3>CyNexo Sniff-0</h3><p>Olfactomètre multicanal utilisé pour la délivrance contrôlée des stimuli, avec synchronisation respiratoire via Spir-0 et déclenchements programmables.</p></div></div><div class="csi-hardware-card"><img data-b64-src="${BIOSEMI_B64}" alt="BioSemi ActiveTwo EEG"><div class="copy"><h3>BioSemi ActiveTwo</h3><p>EEG haute densité 128 canaux, utilisé lorsque l’objectif expérimental nécessite une mesure électrophysiologique synchronisée aux événements.</p></div></div><div class="csi-hardware-card"><img src="${BIOPAC}" alt="BIOPAC MP160"><div class="copy"><h3>BIOPAC MP160</h3><p>Acquisition psychophysiologique et synchronisation : ECG, EDA, EMG et autres canaux selon le protocole, sous AcqKnowledge.</p></div></div></div><div class="csi-extra-refs"><strong>Documentation matérielle :</strong> CyNexo Sniff-0 ; BioSemi ActiveTwo ; BIOPAC MP160/AcqKnowledge.</div>`;
        if(hw._fr){hw._fr.title=hw.title;hw._fr.lead=hw.lead;hw._fr.content=hw.content}
      }

      addRefs(find(slides,/TWIXAV.*asymétr/i,/asymétrie.*verrou/i),'Vroomen & Keetels, 2010 ; Stevenson et al., 2012 ; Wallace & Stevenson, 2014 ; Powers et al., 2009.');
      addRefs(find(slides,/SOFT.*onset/i,/temps propre.*modalit/i),'Vroomen & Keetels, 2010 ; Wallace & Stevenson, 2014 ; Stevenson et al., 2012 ; Gotow & Kobayakawa, 2017.');
      addRefs(find(slides,/TWIXOLF/i),'Gotow & Kobayakawa, 2017 ; Gottfried, 2010 ; Sela & Sobel, 2010 ; Zhou et al., 2010.');
      addRefs(find(slides,/OASIS/i),'Intraub & Richardson, 1989 ; Intraub, 2012 ; Bainbridge & Baker, 2020 ; Rekow et al., 2022.');
      addRefs(find(slides,/Boundary Extension/i,/VIBEX/i),'Intraub & Richardson, 1989 ; Gagnier et al., 2013 ; Bainbridge & Baker, 2020 ; Park et al., 2024.');

      if(!slides.some(s=>/remerciements.*comité/i.test(txt(s)))){
        const thanks={section:'Conclusion',kicker:'Remerciements',title:'Merci aux membres du Comité de Suivi Individuel',lead:'Merci pour le temps consacré au suivi de cette première année, aux échanges méthodologiques et aux arbitrages sur la suite du programme doctoral.',content:`<div class="csi-thanks-grid"><div class="card dark"><h3>Jean-Pierre THIBAUT</h3><p>Référent de l'École Doctorale et responsable du suivi individuel.</p></div><div class="card"><h3>Renaud BROCHARD</h3><p>Directeur de thèse.</p></div><div class="card"><h3>Arnaud LELEU</h3><p>Co-directeur de thèse.</p></div></div><div class="csi-institutions"><div class="csi-logo-row"><img src="${UBE}" alt="Université Bourgogne Europe"><img src="${CNRS}" alt="CNRS"><img src="${INRAE}" alt="INRAE"><div class="csi-logo-word">L’Institut Agro<br><b>Dijon</b></div></div></div>`,notes:'Terminer la présentation principale sur les remerciements avant d’ouvrir la discussion et les éventuelles diapositives cachées.'};
        const refIndex=slides.findIndex(s=>/références|bibliograph/i.test(`${s.section||''} ${s.title||''}`));
        slides.splice(refIndex>=0?refIndex:slides.length,0,thanks);
      }

      if(!d.getElementById('csiQOverlay')){
        const overlay=d.createElement('div');overlay.id='csiQOverlay';overlay.innerHTML=`<div class="qhead"><strong>Diapositives cachées - réponses aux questions</strong><button id="csiQClose">Retour à la présentation</button></div><h1>Réponses aux questions</h1><p>Page volontairement vierge - les diapositives spécifiques seront ajoutées ultérieurement.</p>`;d.body.appendChild(overlay);
        d.getElementById('csiQClose').onclick=()=>overlay.classList.remove('open');
        const header=d.querySelector('header,.topbar,.header,.toolbar,.controls')||d.body.firstElementChild;
        const btn=d.createElement('button');btn.className='csi-qbtn';btn.type='button';btn.textContent='Q&A';btn.title='Ouvrir les diapositives cachées';btn.onclick=()=>overlay.classList.add('open');
        if(header)header.appendChild(btn);
      }

      if(typeof C.render==='function')C.render(); else if(typeof w.render==='function')w.render();
      d.querySelectorAll('img[data-b64-src]').forEach(async img=>{try{const b=(await fetch(img.dataset.b64Src,{cache:'force-cache'}).then(r=>r.text())).trim();img.src='data:image/webp;base64,'+b}catch(e){console.warn('BioSemi asset',e)}});
      [...d.querySelectorAll('.slide,section')].forEach(el=>{const t=(el.textContent||'');if(/arbitrages les plus utiles|décisions.*comité/i.test(t))el.classList.add('csi-fit')});
    }catch(e){console.error('CSI V17 CSI-1 patch',e)}
  }
  frame.addEventListener('load',()=>setTimeout(patch,1250));
  if(frame.contentDocument&&frame.contentDocument.readyState==='complete')setTimeout(patch,1500);
})();
