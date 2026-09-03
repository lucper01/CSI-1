(function(){
const frame=document.getElementById('presentation');if(!frame)return;
frame.addEventListener('load',()=>{
  const run=()=>{try{
    const d=frame.contentDocument;if(!d)return;
    if(!d.getElementById('csiV15Style')){
      const st=d.createElement('style');st.id='csiV15Style';st.textContent=`
        /* Le badge du doctorant suit toujours la palette active. */
        .csi-person.primary .role{
          background:var(--accent-soft)!important;
          color:var(--accent-strong)!important;
          border-color:color-mix(in srgb,var(--accent) 28%,transparent)!important;
        }
        .csi-person.primary .role::before{background:var(--accent)!important}
        .csi-person .csi-photo{background:color-mix(in srgb,var(--accent-pale) 58%,#fff)!important}
        .csi-person.primary .csi-photo{background:color-mix(in srgb,var(--accent-pale) 72%,#fff)!important}
        .csi-photo img.csi-portrait-luc{object-fit:cover!important;object-position:center 12%!important}
        .csi-photo img.csi-portrait-renaud{object-fit:cover!important;object-position:center 18%!important}
        .csi-photo img.csi-portrait-arnaud{object-fit:cover!important;object-position:center 14%!important}
        .csi-photo img.csi-portrait-fabrice{object-fit:contain!important;object-position:center bottom!important;padding:3px 8px 0!important;background:color-mix(in srgb,var(--accent-pale) 62%,#fff)!important}
        .csi-photo img.csi-portrait-camille{object-fit:cover!important;object-position:center 18%!important}
      `;d.head.appendChild(st);
    }
    const portraits={
      'Luc PERROQUIN':{src:'https://raw.githubusercontent.com/lucper01/Portfolio/main/assets/photo-profil.png',cls:'csi-portrait-luc'},
      'Renaud BROCHARD':{src:'https://raw.githubusercontent.com/lucper01/Portfolio/main/assets/renaud.jpg',cls:'csi-portrait-renaud'},
      'Arnaud LELEU':{src:'https://raw.githubusercontent.com/lucper01/Portfolio/main/assets/arnaud.jpg',cls:'csi-portrait-arnaud'},
      'Fabrice Damon':{src:'https://csga.fr/data/summernote/filemanager/scientifiques/equipe_docc/FD.png',cls:'csi-portrait-fabrice'},
      'Camille Ferdenzi-Lemaître':{src:'https://www.crnl.fr/sites/default/files/styles/medium/public/actualite/Camille_Ferdenzi_220px_0.jpg?itok=68_Metx0',cls:'csi-portrait-camille'}
    };
    d.querySelectorAll('.csi-person h3').forEach(h=>{
      const name=h.textContent.trim(),cfg=portraits[name];if(!cfg)return;
      const slot=h.closest('.csi-person')?.querySelector('.csi-photo');if(!slot)return;
      let img=slot.querySelector('img');
      if(!img||img.dataset.csiPerson!==name){
        slot.innerHTML='';img=d.createElement('img');slot.appendChild(img);
      }
      img.dataset.csiPerson=name;img.src=cfg.src;img.alt=name;img.className=cfg.cls;
    });
  }catch(e){console.warn('CSI V15',e)}};
  [180,420,850,1400].forEach(ms=>setTimeout(run,ms));
  try{const d=frame.contentDocument;if(d&&d.body){new MutationObserver(run).observe(d.body,{childList:true,subtree:true})}}catch(e){}
});
})();