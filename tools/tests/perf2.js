const {chromium}=require('playwright');const D0='/tmp/claude-0/-home-claude/3c81d767-102f-5b19-b6b9-5bdb74ffc20c/scratchpad/';
(async()=>{const b=await chromium.launch();const errs=[];
for(const f of ['old.html','index.html']){const c=await b.newContext({viewport:{width:412,height:915},deviceScaleFactor:2.6});const p=await c.newPage();p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8765/'+f);await p.waitForTimeout(1200);
 await p.evaluate(()=>{const s=JSON.parse(localStorage.getItem('fossilfieber')||'{}');s.tutDone=1;s.dig=null;s.era=1;localStorage.setItem('fossilfieber',JSON.stringify(s))});
 await p.reload();await p.waitForTimeout(1500);
 await p.evaluate(()=>{Math.random=(()=>{let x=7;return()=>{x=(x*16807)%2147483647;return x/2147483647}})();document.querySelectorAll('.title,.overlay,.coach,.coach-spot').forEach(x=>x.remove());S.st=500;D=null;S.dig=null;show('dig');newDig();tool='probe';hit(30);tool='brush';D.grid.forEach((g,i)=>{if(i%3)return;for(let k=0;k<(i%2?2:1);k++)hit(i)});particles=[];shake=0});
 await p.waitForTimeout(1500);
 const cdp=await c.newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:6});
 const r=await p.evaluate(async()=>{let work=0,n=0;const orig=drawPit;window.drawPit=function(t){const a=performance.now();orig(t);work+=performance.now()-a;n++};
   await new Promise(r=>setTimeout(r,3000));return {msZeichnenProSekunde:(work/3).toFixed(0),aufrufe:n}});
 console.log(f,r);
 await cdp.send('Emulation.setCPUThrottlingRate',{rate:1});
 const el=await p.$('#pit');await el.screenshot({path:D0+'perf_'+f+'.png'});
 // Tippen und Partikel funktionieren noch?
 await p.evaluate(()=>{hit(5)});await p.waitForTimeout(100);await el.screenshot({path:D0+'perf_tap_'+f+'.png'});
 await c.close()}
console.log(errs);await b.close()})();
