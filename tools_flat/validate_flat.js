const { chromium } = require('playwright');

async function check(viewport,label){
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.stack||e.message));
  page.on('console',m=>{ if(m.type()==='error') errors.push('console: '+m.text()); });
  await page.goto('http://127.0.0.1:8000/index.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForTimeout(1800);
  const state=await page.evaluate(()=>{
    const slides=[...document.querySelectorAll('.slide')];
    const text=document.body?.innerText||'';
    const titles=slides.map(s=>s.querySelector('h1,h2')?.textContent?.trim()||'');
    const idx=q=>titles.findIndex(t=>t.includes(q));
    const visible=slides.filter(s=>{const r=s.getBoundingClientRect(),cs=getComputedStyle(s);return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0;});
    return {
      single:document.documentElement.dataset.singleLayer||'',
      iframeCount:document.querySelectorAll('iframe#presentation').length,
      slideCount:slides.length,
      visibleCount:visible.length,
      firstText:(slides[0]?.innerText||'').slice(0,500),
      text,
      sheetCount:document.querySelectorAll('.csi-flat-sheet').length,
      blankBody:!text.trim(),
      jeanPierre:text.includes('Jean-Pierre THIBAUT'),
      order:{
        sela:idx('No space, no time?'),
        tw:[idx('TWIXAV - pourquoi commencer'),idx('TWIXAV - Méthode'),idx('TWIXAV - Résultats'),idx('TWIXAV - ce que les résultats changent')],
        vib:[idx('VIBEX - pourquoi établir'),idx('VIBEX - Méthode'),idx('VIBEX - résultats du prétest'),idx('VIBEX - ce que le prétest permet')],
        y1:[idx('Deux acquis expérimentaux structurent la suite'),idx('Deux références, trois études centrales pour l’année 2')],
        soft:[idx('SOFT - mesurer le temps propre'),idx('SOFT - Méthode')],
        oasis:[idx('OASIS - tester l’influence olfactive'),idx('OASIS - Méthode')],
        twolf:[idx('TWIXOLF - transposer la liaison temporelle'),idx('TWIXOLF - Méthode')]
      }
    };
  });
  console.log(label,JSON.stringify(state,null,2));
  console.log(label,'ERRORS',JSON.stringify(errors));
  const inc=a=>a.every((v,i)=>v>=0&&(i===0||v>a[i-1]));
  const orderOK=state.order.sela>=0&&inc(state.order.tw)&&inc(state.order.vib)&&inc(state.order.y1)&&inc(state.order.soft)&&inc(state.order.oasis)&&inc(state.order.twolf);
  if(errors.length||state.single!=='1'||state.iframeCount!==0||state.slideCount<38||state.blankBody||!state.firstText||!orderOK||state.jeanPierre){
    throw new Error(label+' validation failed: '+JSON.stringify({errors,state,orderOK}));
  }
  await page.screenshot({path:`validate-${label}.png`,fullPage:false});
  await browser.close();
}

(async()=>{
  await check({width:1600,height:1000},'desktop');
  await check({width:690,height:1536},'mobile');
  console.log('SINGLE-LAYER VALIDATION PASSED');
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
