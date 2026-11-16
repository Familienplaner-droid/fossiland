const {chromium}=require('playwright');const D0='/tmp/claude-0/-home-claude/3c81d767-102f-5b19-b6b9-5bdb74ffc20c/scratchpad/';
(async()=>{const b=await chromium.launch();const errs=[];
for(const [vw,vh,tag] of [[390,844,'p'],[844,390,'l']]){
let p=await b.newPage({viewport:{width:vw,height:vh}});p.on('pageerror',e=>errs.push(tag+': '+e.message));
await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(900);
await p.evaluate(()=>{document.querySelectorAll('.title,.overlay,.coach,.coach-spot,.tap-hand').forEach(x=>x.remove());S.tutDone=1;S.tix=40;ERAS.forEach(e=>e.need=0);show('dig')});await p.waitForTimeout(300);
console.log(tag,'start',await p.evaluate(()=>SITES[S.site].id+' '+SITES[S.site].r));
await p.click('#siteBtn');await p.waitForTimeout(900);await p.screenshot({path:D0+`m2_${tag}_open.png`});
console.log(tag,'view',await p.evaluate(()=>MV.view+' s='+MV.s.toFixed(2)));
await p.click('#mpBack');await p.waitForTimeout(600);await p.screenshot({path:D0+`m2_${tag}_world.png`});
// Sammelpunkt Europa antippen
const r=await p.evaluate(()=>{const b=document.querySelector('[data-reg=eu]').getBoundingClientRect();return[b.x+b.width/2,b.y+b.height/2]});
await p.mouse.click(r[0],r[1]);await p.waitForTimeout(600);console.log(tag,'nach Tipp',await p.evaluate(()=>MV.view));
await p.screenshot({path:D0+`m2_${tag}_eu.png`});
// Flug innerhalb EU
await p.evaluate(()=>{MV.sel=SITES.findIndex(s=>s.id==='so');mapDraw();mapSheet()});await p.waitForTimeout(200);
await p.screenshot({path:D0+`m2_${tag}_sheet.png`});
await p.click('#mpFly');await p.waitForTimeout(1100);await p.screenshot({path:D0+`m2_${tag}_flyeu.png`});await p.waitForTimeout(1500);
await p.click('#arrGo');await p.waitForTimeout(400);console.log(tag,'jetzt',await p.evaluate(()=>SITES[S.site].id));
// Flug EU -> USA (Weltkarte)
await p.click('#siteBtn');await p.waitForTimeout(700);
await p.evaluate(()=>{mapView('us');MV.sel=SITES.findIndex(s=>s.id==='gr');mapDraw();mapSheet()});await p.waitForTimeout(400);
await p.screenshot({path:D0+`m2_${tag}_us.png`});
await p.click('#mpFly');await p.waitForTimeout(1100);console.log(tag,'Flugansicht',await p.evaluate(()=>MV.view));await p.screenshot({path:D0+`m2_${tag}_flyw.png`});await p.waitForTimeout(1500);
await p.click('#arrGo');await p.waitForTimeout(400);console.log(tag,'jetzt',await p.evaluate(()=>SITES[S.site].id));
// max Zoom Detail
await p.click('#siteBtn');await p.waitForTimeout(700);await p.evaluate(()=>{mapZoomAt(9,MV.vp.clientWidth/2,MV.vp.clientHeight/2)});await p.waitForTimeout(400);
await p.screenshot({path:D0+`m2_${tag}_zoom.png`});
await p.close()}
console.log('Fehler',errs);await b.close()})();
