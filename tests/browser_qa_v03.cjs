#!/usr/bin/env node
// BUILD-022 headless Chromium browser QA; synthetic test data only.
// No external dependencies, real documents, cloud deployment or tax advice.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {spawn,spawnSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const index=path.resolve(__dirname,'../site/taxgenie-screen-pilot/index.html');
assert(fs.existsSync(index),'Screen entrypoint missing');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function chromeBinary(){
 const names=[process.env.CHROME_BIN,'chromium','chromium-browser','google-chrome','google-chrome-stable'].filter(Boolean);
 for(const name of names){
   if(name.includes('/')&&fs.existsSync(name))return name;
   if(spawnSync('which',[name],{stdio:'ignore'}).status===0)return name;
 }
 throw Error('Chrome/Chromium unavailable — browser QA cannot be skipped');
}
async function run(){
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'tg-qa-'));
 const child=spawn(chromeBinary(),[
  '--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
  '--no-first-run','--remote-allow-origins=*','--remote-debugging-port=0',
  '--user-data-dir='+tmp,'about:blank'
 ],{stdio:'ignore'});
 let ws;
 const pending=new Map(), errors=[];
 let id=0;
 try{
  let port;
  for(let n=0;n<140;n++){
   if(child.exitCode!==null)throw Error('Chrome startup failed');
   const file=path.join(tmp,'DevToolsActivePort');
   if(fs.existsSync(file)){
    port=Number(fs.readFileSync(file,'utf8').split('\n')[0]);
    if(port>0)break;
   }
   await delay(100);
  }
  assert(port,'DevTools did not start');
  let target;
  for(let n=0;n<40;n++){
   try{
    const response=await fetch('http://127.0.0.1:'+port+'/json/list');
    const targets=await response.json();
    target=targets.find(t=>t.type==='page');
    if(target)break;
   }catch(_){}
   await delay(100);
  }
  assert(target,'No browser page available');
  ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
   const t=setTimeout(()=>reject(Error('CDP connect timeout')),5000);
   ws.addEventListener('open',()=>{clearTimeout(t);resolve();},{once:true});
   ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP connect error'));},{once:true});
  });
  ws.addEventListener('message',evt=>{
   const msg=JSON.parse(String(evt.data));
   if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params?.exceptionDetails?.text||'exception');
   if(msg.id&&pending.has(msg.id)){
    const p=pending.get(msg.id);pending.delete(msg.id);
    if(msg.error)p.reject(Error(JSON.stringify(msg.error)));
    else p.resolve(msg.result);
   }
  });
  const cmd=(method,params={})=>new Promise((resolve,reject)=>{
   const k=++id;pending.set(k,{resolve,reject});
   ws.send(JSON.stringify({id:k,method,params}));
   setTimeout(()=>{if(pending.has(k)){pending.delete(k);reject(Error('CDP timeout '+method));}},6500);
  });
  const evalJs=async expr=>{
   const result=await cmd('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});
   if(result.exceptionDetails)throw Error('Page error: '+result.exceptionDetails.text);
   return result.result?.value;
  };
  const val=name=>evalJs('document.getElementById('+JSON.stringify(name)+').textContent');
  const set=async(name,value)=>{
   const expr='(()=>{const e=document.getElementById('+JSON.stringify(name)+');e.value='+JSON.stringify(value)+';e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}));return true;})()';
   return evalJs(expr);
  };
  await cmd('Page.enable');await cmd('Runtime.enable');
  await cmd('Page.navigate',{url:process.env.TAXGENIE_TEST_URL||pathToFileURL(index).href});
  let ready=false;
  for(let n=0;n<70;n++){
   try{ready=await evalJs("document.readyState==='complete' && document.getElementById('est')?.value==='DE' && document.getElementById('refund')?.value==='FR'");if(ready)break;}
   catch(_){}
   await delay(100);
  }
  assert(ready,'Page did not initialize');
  assert.equal(await evalJs("document.querySelectorAll('script[src=\"./assets/app-v03-r2.js\"]').length"),1,'external JS asset');
  assert.equal(await evalJs("document.querySelectorAll('link[href=\"./assets/style-v03-r2.css\"]').length"),1,'external CSS asset');
  assert.match(await evalJs("getComputedStyle(document.body).backgroundImage"),/gradient/,'CSS actually loaded');
  assert.equal(await evalJs("document.querySelectorAll('#est option').length"),27);
  assert.match(await val('amount'),/1,200\.00/);
  assert.match(await val('minimum'),/50/);
  assert.match(await val('threshold'),/NOT ASSESSED.*requested refund unknown/,'Charged VAT must not be treated as claimed refund');
  assert.match(await val('status'),/eligibility not assessed/i);
  assert.match(await val('brief-flags'),/synthetic research prompts/);
  assert.equal(await evalJs("document.querySelectorAll('#signal-grid .signal-card').length")>0,true,'scenario findings actually rendered');
  assert.match(await evalJs("document.querySelector('#signal-grid').textContent"),/Requested refund cannot be calculated/);

  assert.equal(await evalJs("document.querySelectorAll('input[type=file], form').length"),0);
  // Premium Explorer and brand regression checks.
  assert.equal(await evalJs("document.querySelectorAll('.logo-symbol').length"),1,'branded standalone SVG logo');
  assert.equal(await evalJs("document.querySelectorAll('.hero-atlas').length"),1,'themed cover illustration');
  assert.equal(await evalJs("document.querySelectorAll('[data-preset]').length"),3,'three sample scenarios');
  assert.equal(await evalJs("document.querySelectorAll('#about').length"),1,'about us panel');

  assert.equal(await evalJs("document.querySelectorAll('[data-evidence]').length"),6,'six evidence questions');
  assert.equal(await evalJs("document.querySelectorAll('[data-service]').length"),4,'four service directions');
  assert.equal(await evalJs("document.querySelector('img[src=\"./assets/evidence-atlas.svg\"]').complete && document.querySelector('img[src=\"./assets/evidence-atlas.svg\"]').naturalWidth>0"),true,'thematic atlas artwork loaded');
  assert.equal(await evalJs("document.querySelector('link[rel=icon]').getAttribute('href')"),'./assets/favicon.svg');
  await evalJs("document.querySelector('[data-evidence=\"invoice\"]').click()");
  assert.match(await val('evidence-count'),/1 \/ 6/,'evidence interaction counts questions, not validated files');
  assert.match(await val('brief-evidence'),/1 of 6/,'brief stays in sync');
  await evalJs("document.querySelector('#evidence-reset').click()");
  assert.match(await val('evidence-count'),/0 \/ 6/,'evidence clear works');
  await evalJs("document.querySelector('[data-service=\"rules\"]').click()");
  assert.match(await val('service-stage'),/DESIGN ONLY/,'service explorer cannot overpromise active watch');
  assert.match(await val('service-description'),/No live country rule watch/);
  await evalJs("document.querySelector('[data-service=\"mapping\"]').click()");
  assert.match(await val('service-stage'),/DISCOVERY PILOT/);

  assert.match(await evalJs("document.querySelector('.end-credit').textContent"),/Created by.*Proof & Signal/);
  await evalJs("document.querySelector('[data-preset=\"fr-de\"]').click()");
  assert.equal(await evalJs("document.getElementById('est').value"),'FR');
  assert.equal(await evalJs("document.getElementById('refund').value"),'DE');
  assert.match(await val('minimum'),/400/);
  assert.match(await val('threshold'),/NOT ASSESSED/);
  await evalJs("document.querySelector('[data-preset=\"domestic\"]').click()");
  assert.match(await val('status'),/Domestic VAT route/);
  await evalJs("document.querySelector('[data-preset=\"de-fr\"]').click()");
  assert.match(await val('route'),/DE.*FR/);
  assert.match(await val('amount'),/1,200\.00/);

  await set('period','short');assert.match(await val('minimum'),/400/);
  await set('refund','DE');assert.match(await val('status'),/Domestic VAT route/i);
  assert.match(await evalJs("document.querySelector('#signal-grid').textContent"),/Domestic route, different process/,'same-country case changes research findings');
  await set('refund','FR');
  await set('vat','12.345');assert.equal(await evalJs("document.getElementById('copy').disabled"),true);
  assert.equal(await evalJs("document.getElementById('brief-copy').disabled"),true,'cannot export invalid research dossier');
  await set('vat','-5');assert.equal(await evalJs("document.getElementById('copy').disabled"),true);
  await set('vat','10');
  assert.match(await val('threshold'),/NOT ASSESSED/,'Even small charged VAT cannot establish application minimum');
  assert.doesNotMatch(await val('status'),/Below general EU application minimum/,'No illegal inference from charged VAT');
  await set('vat','500');assert.equal(await evalJs("document.getElementById('copy').disabled"),false);
  await set('expense','Fuel');assert.match(await val('expenseStatus'),/Fuel.*UNVERIFIED/);
  await set('deduction','no');assert.match(await val('status'),/human review required/i);
  const summary=await evalJs('summary()');
  assert.match(summary,/Recoverable VAT: NOT ASSESSED/);
  assert.match(summary,/Eligibility: UNDETERMINED/);
  assert.match(summary,/Minimum comparison: NOT ASSESSED/);
  assert.doesNotMatch(summary,/Estimated recoverable VAT: €|Guaranteed|Approved claim/i);
  await evalJs("document.getElementById('reset').click()");
  assert.match(await val('amount'),/1,200\.00/);
  assert.match(await val('minimum'),/50/);
  const href=await evalJs("document.querySelector('a[href^=\"mailto:\"]').getAttribute('href')");
  assert.match(href,/mailto:clients@proofandsignal\.xyz/);
  // Exact calendar-year scenario rules; general EU deadlines do not prove legal eligibility.
  await set('period','remainder');
  assert.match(await val('minimum'),/50/,'remainder-of-year application minimum');
  const earliest=await evalJs("document.querySelector('#year option').value");
  await set('year',earliest);
  assert.match(await val('status'),/deadline has passed/i,'past general deadline warning');
  const upcoming=await evalJs("String(new Date().getFullYear()+1)");
  await set('year',upcoming);
  assert.doesNotMatch(await val('status'),/deadline has passed/i,'future year is not marked expired');
  assert.match(await val('details'),/National restrictions.*NOT VERIFIED/,'no automated refund conclusion');
  // Preserve full-page visual evidence in CI to inspect actual product design.
  await evalJs("document.getElementById('reset').click()");
  await cmd('Emulation.setDeviceMetricsOverride',{width:1440,height:950,deviceScaleFactor:1,mobile:false});
  await delay(150);
  const screenshots=path.resolve(__dirname,'../dist');
  fs.mkdirSync(screenshots,{recursive:true});
  const desktopPng=await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
  fs.writeFileSync(path.join(screenshots,'taxgenie-atlas-desktop.png'),Buffer.from(desktopPng.data,'base64'));
  await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await delay(120);
  const size=await evalJs('({viewport:window.innerWidth,scroll:document.documentElement.scrollWidth})');
  assert(size.scroll<=size.viewport+1,'Mobile horizontal overflow '+JSON.stringify(size));

  const mobilePng=await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
  fs.writeFileSync(path.join(screenshots,'taxgenie-atlas-mobile.png'),Buffer.from(mobilePng.data,'base64'));
  console.log('VISUAL QA ARTIFACTS: desktop + 390px mobile screenshots saved');

  assert.equal(errors.length,0,'Uncaught JS errors: '+errors.join(','));
  console.log('Browser QA PASS: 27 countries, amount, period, same country, negative values, expense/risk, copy summary, reset, mailto, 390px mobile');
 }finally{
  if(ws&&ws.readyState===WebSocket.OPEN)ws.close();
  child.kill('SIGTERM');await delay(100);
  if(child.exitCode===null)child.kill('SIGKILL');
  fs.rmSync(tmp,{recursive:true,force:true});
 }
}
run().catch(e=>{console.error('Browser QA FAIL:',e.stack||e);process.exitCode=1;});
