(function(){
  const frame=document.getElementById('presentation');
  if(!frame)return;
  const patch=()=>{
    try{
      const w=frame.contentWindow,d=w.document,C=w.CSI11;
      if(!C||!Array.isArray(C.slides))return;
      const slides=C.slides;
      const swap=(html)=>{
        if(!html||!html.includes('SOLAR')||!html.includes('COBEX'))return html;
        return html.replaceAll('SOLAR','__CSI_SOLAR__').replaceAll('COBEX','SOLAR').replaceAll('__CSI_SOLAR__','COBEX');
      };
      let s=slides[28];
      if(!s||!/Rétroplanning des études|Study timeline/i.test(s.title||'')){
        s=slides.find(x=>/Rétroplanning des études|Study timeline/i.test(x.title||''));
      }
      if(s){
        s.content=swap(s.content);
        if(s._fr)s._fr.content=swap(s._fr.content);
        if(s._en)s._en.content=swap(s._en.content);
      }
      if(typeof C.render==='function')C.render();
      else if(typeof w.render==='function')w.render();
    }catch(e){console.error('CSI V17',e)}
  };
  frame.addEventListener('load',()=>setTimeout(patch,900));
  if(frame.contentDocument&&frame.contentDocument.readyState==='complete')setTimeout(patch,1200);
})();
