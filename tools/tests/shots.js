const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const [name,vp] of [['p',{width:390,height:844}],['l',{width:1180,height:820}]]){
 for(let e=0;e<6;e++){const p=await b.newPage({viewport:vp});
  await p.goto('http://localhost:8765/index.html');
  await p.evaluate(e=>{const s=JSON.parse(localStorage.getItem('fossilfieber')||'{}');s.era=e;s.tut=99;s.seenTitle=1;localStorage.setItem('fossilfieber',JSON.stringify(s))},e);
  await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(1200);
  await p.evaluate(()=>{const b=document.querySelector('.title button, #play, .play');b&&b.click()});await p.waitForTimeout(1200);
  await p.evaluate(e=>{try{S.era=e;S.tut=99;document.querySelectorAll('.coach,.ov').forEach(x=>x.remove());drawScene();}catch(x){}},e);await p.waitForTimeout(800);
  const el=await p.$('.scene');await el.screenshot({path:`/tmp/claude-0/-home-claude/3c81d767-102f-5b19-b6b9-5bdb74ffc20c/scratchpad/sc_${name}${e}.png`});await p.close()}}
await b.close()})();
