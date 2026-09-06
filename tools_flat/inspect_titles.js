const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage();
  await p.goto('http://127.0.0.1:8000/index_save.html',{waitUntil:'domcontentloaded',timeout:30000});
  await p.waitForTimeout(3200);
  const h=await p.$('#presentation');
  const f=await h.contentFrame();
  const x=await f.evaluate(()=>window.CSI11?.slides?.map((s,i)=>({i,title:s.title,kicker:s.kicker,section:s.section,lead:(s.lead||'').slice(0,140),text:(s.content||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').slice(0,260)}))||[]);
  console.log('FINAL_TITLES',JSON.stringify(x,null,2));
  await b.close();
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
