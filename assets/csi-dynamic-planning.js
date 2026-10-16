/* CSI_DYNAMIC_PLANNING_TIMELINE_V1 */
(()=>{
  'use strict';

  const START_YEAR = 2025;
  const START_MONTH = 9; // October, zero-based.
  const TOTAL_QUARTERS = 13;

  function currentQuarter(){
    const now = new Date();
    const monthOffset = (now.getFullYear() - START_YEAR) * 12 + (now.getMonth() - START_MONTH);
    return Math.floor(monthOffset / 3) + 1;
  }

  function gridRange(el){
    const style = String(el.getAttribute('style') || '');
    const match = style.match(new RegExp('grid-column\\s*:\\s*(\\d+)(?:\\s*\\/\\s*span\\s*(\\d+))?', 'i'));
    if(!match) return null;
    const start = Number(match[1]);
    const span = Number(match[2] || 1);
    return { start, end: start + span - 1 };
  }

  function classify(el, quarter){
    el.classList.remove('past','current-period','future');
    const range = gridRange(el);
    if(!range) return;

    if(quarter > TOTAL_QUARTERS || range.end < quarter){
      el.classList.add('past');
    }else if(quarter >= 1 && range.start <= quarter && quarter <= range.end){
      el.classList.add('current-period');
    }else{
      el.classList.add('future');
    }
  }

  function applyPlanningTime(){
    const quarter = currentQuarter();
    const english = document.documentElement.lang === 'en';

    document.querySelectorAll('.csi-plan12').forEach(plan=>{
      const quarters = [...plan.querySelectorAll('.quarters .q')];

      quarters.forEach((node, index)=>{
        node.classList.remove('past','now','future');
        node.querySelectorAll('.here').forEach(n=>n.remove());

        const q = index + 1;
        if(quarter > TOTAL_QUARTERS || q < quarter){
          node.classList.add('past');
        }else if(quarter >= 1 && q === quarter){
          node.classList.add('now');
          const here = document.createElement('span');
          here.className = 'here';
          here.textContent = english ? '📍 YOU ARE HERE' : '📍 VOUS ÊTES ICI';
          node.appendChild(here);
        }else{
          node.classList.add('future');
        }
      });

      plan.querySelectorAll('.evt').forEach(el=>classify(el, quarter));
      plan.querySelectorAll('.year').forEach(el=>classify(el, quarter));

      plan.dataset.currentQuarter = String(quarter);
      plan.dataset.timelineStart = '2025-10';
    });
  }

  let raf = 0;
  function schedule(){
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(applyPlanningTime);
  }

  const deck = document.getElementById('deck');
  if(deck){
    new MutationObserver(schedule).observe(deck, { childList:true, subtree:true });
  }

  new MutationObserver(schedule).observe(document.documentElement, {
    attributes:true,
    attributeFilter:['lang']
  });

  window.addEventListener('focus', schedule);
  window.addEventListener('pageshow', schedule);
  document.addEventListener('visibilitychange', ()=>{
    if(!document.hidden) schedule();
  });

  applyPlanningTime();
  requestAnimationFrame(applyPlanningTime);
})();