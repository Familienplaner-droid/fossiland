const {chromium}=require('playwright');const D0='/tmp/claude-0/-home-claude/3c81d767-102f-5b19-b6b9-5bdb74ffc20c/scratchpad/';
(async()=>{const b=await chromium.launch();const errs=[];
// 1) neuer Spieler
let p=await b.newPage({viewport:{width:390,height:844}});p.on('pageerror',e=>errs.push('neu: '+e.message));
await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(900);
await p.evaluate(()=>{document.querySelectorAll('.title,.overlay,.coach,.coach-spot,.tap-hand').forEach(x=>x.remove());S.tutDone=1;show('dig')});await p.waitForTimeout(400);
console.log('neu:',await p.evaluate(()=>({site:SITES[S.site].id,era:S.era,tix:S.tix,target:D.target.id,bar:document.querySelector('.sitebar b').textContent})));
await p.screenshot({path:D0+'m_dig.png'});
await p.click('#siteBtn');await p.waitForTimeout(700);await p.screenshot({path:D0+'m_map.png'});
// Europa antippen (gedrängt) -> zoomt
const pos=await p.evaluate(()=>{const r=MV.vp.getBoundingClientRect();const[x,y]=mapXY(SITES.findIndex(s=>s.id==='tr'));return [r.left+x,r.top+y,MV.s]});
await p.evaluate(()=>{const i=SITES.findIndex(s=>s.id==='tr');mapCenter(SITES[i].x,SITES[i].y);mapDraw()});await p.waitForTimeout(200);
const pos2=await p.evaluate(()=>{const r=MV.vp.getBoundingClientRect();const[x,y]=mapXY(SITES.findIndex(s=>s.id==='tr'));return [r.left+x,r.top+y]});
await p.mouse.click(pos2[0],pos2[1]);await p.waitForTimeout(300);
console.log('Zoom nach Tipp auf Europa:',pos[2].toFixed(2),'->',await p.evaluate(()=>MV.s.toFixed(2)),'Auswahl',await p.evaluate(()=>SITES[MV.sel].id));
await p.screenshot({path:D0+'m_eu.png'});
// Ghost Ranch wählen (gleicher Kontinent, 3 Tickets) und fliegen
await p.evaluate(()=>{MV.sel=SITES.findIndex(s=>s.id==='gr');mapDraw();mapSheet()});await p.waitForTimeout(200);
await p.screenshot({path:D0+'m_sheet.png'});
await p.click('#mpFly');await p.waitForTimeout(1200);await p.screenshot({path:D0+'m_fly.png'});await p.waitForTimeout(1500);
await p.screenshot({path:D0+'m_arr.png'});
await p.click('#arrGo');await p.waitForTimeout(500);
console.log('nach Flug:',await p.evaluate(()=>({site:SITES[S.site].id,era:S.era,tix:S.tix,target:D.target.id,visited:Object.keys(S.visited)})));
// Pass
await p.click('#siteBtn');await p.waitForTimeout(500);await p.click('#mpPass');await p.waitForTimeout(400);await p.screenshot({path:D0+'m_pass.png'});
await p.click('#passOk');
// zu wenig Tickets -> Kauf-Angebot
await p.evaluate(()=>{MV.sel=SITES.findIndex(s=>s.id==='dw');mapDraw();mapSheet()});await p.waitForTimeout(200);
console.log('Angebot:',await p.evaluate(()=>!!document.querySelector('#mpTixAd')&&!!document.querySelector('#mpTixBuy')));
await p.click('#mpClose');
// Neuladen behält Ort
await p.reload();await p.waitForTimeout(900);console.log('nach Neuladen:',await p.evaluate(()=>[SITES[S.site].id,D.target.id]));
// Lager
await p.evaluate(()=>{document.querySelectorAll('.title,.overlay,.coach,.coach-spot,.tap-hand').forEach(x=>x.remove());S.coins=3000;show('shop')});await p.waitForTimeout(300);
await (await p.$('.camp')).screenshot({path:D0+'m_camp.png'});
await p.click('[data-up=camp]');await p.waitForTimeout(200);console.log('Lager:',await p.evaluate(()=>[S.campLv,staMax()]));
await p.close();
// 2) alter Spielstand (Kari-ähnlich, Kreide frei)
p=await b.newPage({viewport:{width:390,height:844}});p.on('pageerror',e=>errs.push('alt: '+e.message));
await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(400);
await p.evaluate(()=>{const ok={0:'ok',1:'ok',2:'ok',3:'ok',4:'ok'};const m={};['dime','edap','scut','inos','meso','plat','herr','coel'].forEach(k=>m[k]=ok);m.allo={0:'ok'};
 localStorage.setItem('fossilfieber',JSON.stringify({v:3,tutDone:1,era:2,museum:m,coins:700,lab:[],eraDigs:{0:null}}))});
await p.reload();await p.waitForTimeout(900);
console.log('alt:',await p.evaluate(()=>({site:SITES[S.site].id,era:S.era,tix:S.tix,frei:Object.keys(S.freeFly).length,besucht:Object.keys(S.visited),gifts:Object.keys(S.siteGift)})));
console.log('Fehler',errs);await b.close()})();
