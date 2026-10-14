#!/usr/bin/env node
// Optional real-browser smoke test. Uses a fresh, isolated Chrome profile, never the user's tabs.
// Usage: node scripts/check_slc10_page.mjs <Chrome executable> <loopback pilot URL>
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const [chrome, url] = process.argv.slice(2);
assert(chrome && url, 'Chrome executable and local page URL are required');
const parsed = new URL(url);
assert(['127.0.0.1','localhost'].includes(parsed.hostname), 'Smoke test only permits loopback pages');
const directory = await mkdtemp(join(tmpdir(), 'ptm-slc10-browser-'));
const child = spawn(chrome, ['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--enable-automation','--disable-background-networking','--no-proxy-server','--password-store=basic','--use-mock-keychain',
  '--remote-debugging-port=0','--remote-debugging-address=127.0.0.1',`--user-data-dir=${directory}`,'about:blank'],
  {stdio:['ignore','ignore','pipe']});
let browserErrors='';
child.stderr.on('data',chunk=>{browserErrors=(browserErrors+chunk.toString()).slice(-3000);});
let socket, nextId=0;
const pending = new Map();
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
async function until(fn, description) {
  const end=Date.now()+45000;
  while(Date.now()<end){const result=await fn();if(result)return result;await pause(100);}
  throw new Error('Timed out: '+description);
}
function call(method, params={}, sessionId) {
  const id=++nextId;
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},45000);
    pending.set(id,{resolve:r=>{clearTimeout(timer);resolve(r);},reject:e=>{clearTimeout(timer);reject(e);}});
    socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
}
try {
  const port=await until(async()=>{
    try{return (await readFile(join(directory,'DevToolsActivePort'),'utf8')).split('\n')[0];}
    catch(e){if(e.code==='ENOENT')return null;throw e;}
  },'isolated Chrome');
  const version=await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  console.log('Browser:',version.Browser);
  socket=new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message',event=>{
    const message=JSON.parse(event.data);
    if(message.method==='Network.requestWillBeSent'&&message.params.request.url.startsWith(parsed.origin))
      console.log('Request:',message.params.request.url);
    if(message.method==='Network.responseReceived'&&message.params.response.url.startsWith(parsed.origin))
      console.log('Response:',message.params.response.status,message.params.response.url);
    if(message.method==='Network.loadingFailed')console.error('Network failure:',JSON.stringify(message.params));
    if(message.method==='Runtime.exceptionThrown')console.error('Page exception:',JSON.stringify(message.params));
    const task=pending.get(message.id);if(!task)return;
    pending.delete(message.id);if(message.error)task.reject(new Error(JSON.stringify(message.error)));else task.resolve(message.result);
  });
  const {targetId}=await call('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await call('Target.attachToTarget',{targetId,flatten:true});
  await call('Page.enable',{},sessionId);
  await call('Runtime.enable',{},sessionId);
  await call('Network.enable',{},sessionId);
  await call('Runtime.runIfWaitingForDebugger',{},sessionId);
  await call('Target.activateTarget',{targetId});
  const run=async expression=>{
    const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);
    if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));return result.result.value;
  };
  const screenshot=async name=>{
    const result=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);
    const path=join(directory,name);await writeFile(path,Buffer.from(result.data,'base64'));return path;
  };
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false},sessionId);
  assert.equal(await run('1+1'),2);
  console.log('JavaScript execution context ready');
  console.log('Checking local page in isolated Chrome');
  // Navigation may destroy the old context before its evaluate reply arrives.
  // Do not let that reply block checks against the newly loaded page.
  call('Page.navigate',{url},sessionId).catch(error=>console.error('Navigation reply:',error.message));
  await until(()=>run('document.querySelectorAll("#matrix .cell").length > 0'),'verified export rendering');
  assert.equal(await run('document.querySelectorAll("#site option").length'),7);
  assert.equal(await run('document.querySelectorAll("#matrix tbody tr").length'),7);
  assert.equal(await run('document.querySelectorAll("#models tbody tr").length'),3);
  assert.equal(await run('document.querySelectorAll("#mechanisms article").length'),7);
  assert.equal(await run('document.querySelectorAll("#assays tbody tr").length'),16);
  assert.equal(await run('document.querySelectorAll("#explanations article").length'),5);
  assert.match(await run('document.getElementById("slc10-explanation:ntcp-r252h-surface-availability").textContent'),/SUPPORTED.*PROPOSED/);
  assert.match(await run('document.getElementById("slc10-mechanism:ntcp-r252h-surface-availability").textContent'),/AUTHOR INTERPRETATION/);
  assert.equal(await run('document.getElementById("slc10-mechanism:ntcp-s267f-substrate-selectivity").querySelectorAll(".edge").length'),2);
  await run('[...document.querySelectorAll("#assays tbody tr")].find(r=>r.textContent.includes("Cell-surface detection of NTCP R252H")).querySelector("button").click()');
  assert.match(await run('document.getElementById("detail-body").textContent'),/NOT_DETECTED/);
  assert.match(await run('document.getElementById("assay-substitutions").textContent'),/R252/);
  assert.equal(await run('document.querySelector("#assay-substitutions tbody td").textContent'),'H');
  await run('document.getElementById("close-detail").click()');
  assert.match(await run('document.getElementById("slc10-explanation:a7-site-divergence").textContent'),/UNRESOLVED/);
  await run('[...document.getElementById("slc10-explanation:a4-residue-loss").querySelectorAll("button")].find(b=>b.textContent==="Taurocholate uptake").click()');
  assert.match(await run('document.getElementById("detail-body").textContent'),/NOT_DETECTED/);
  await run('document.getElementById("close-detail").click()');
  await run('document.querySelector("#matrix .cell").click()');
  assert.equal(await run('document.getElementById("detail").open'),true);
  assert.match(await run('document.getElementById("detail-body").textContent'),/sequence_sha256/);
  await run('document.getElementById("close-detail").click()');
  const graphTitle=await run('document.querySelector("#mechanisms article h3").textContent');
  await run('document.querySelector("#mechanisms article button").click()');
  assert.equal(await run('document.getElementById("detail-title").textContent'),graphTitle);
  assert.equal(await run('document.getElementById("detail").getAttribute("aria-labelledby")'),'detail-title');
  await run('document.getElementById("close-detail").click()');
  await run('[...document.querySelectorAll("#assays tbody tr")].find(r=>r.textContent.includes("E257A")).querySelector("button").click()');
  assert.match(await run('document.getElementById("assay-substitutions").textContent'),/E257/);
  assert.equal(await run('document.querySelector("#assay-substitutions tbody td").textContent'),'A');
  const substitution=await screenshot('substitution.png');
  await run('document.getElementById("close-detail").click()');
  await run('document.getElementById("site").selectedIndex=0; document.getElementById("site").dispatchEvent(new Event("change"))');
  assert.equal(await run('document.querySelectorAll("#matrix .cell").length'),91);
  await run('document.getElementById("site").selectedIndex=3; document.getElementById("site").dispatchEvent(new Event("change"))');
  await run('window.scrollTo(0,0)');
  const desktop=await screenshot('desktop.png');
  await run('document.getElementById("site-heading").scrollIntoView()');
  const matrix=await screenshot('matrix.png');
  await run('document.getElementById("mechanism-heading").scrollIntoView()');
  const mechanisms=await screenshot('mechanisms.png');
  await run('document.getElementById("slc10-mechanism:ntcp-r252h-surface-availability").scrollIntoView()');
  const residueChain=await screenshot('residue-chain.png');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true},sessionId);
  assert.equal(await run('document.documentElement.scrollWidth <= window.innerWidth'),true);
  await run('window.scrollTo(0,0)');
  const mobile=await screenshot('mobile.png');
  await run('setTimeout(()=>{location.href='+JSON.stringify(url+'#'+encodeURIComponent('slc10-assay:mouse-pres1-binding-2013'))+';location.reload()},0); true');
  await until(()=>run('document.getElementById("detail")?.open'),'stable assertion deep link');
  assert.match(await run('document.getElementById("detail-body").textContent'),/HBV preS1 peptide binding/);
  console.log(JSON.stringify({status:'passed',desktop,matrix,mechanisms,residueChain,mobile,substitution,checks:['verified export','matrix','site switching','separate assay context','unresolved explanation','typed substitution dialog','R252H localization and interpreted mediation','S267F substrate-specific branches','model table','accessible graph dialog','mechanisms','mobile overflow','stable assertion deep link']},null,2));
} catch(error) {
  console.error('Isolated browser diagnostics:',browserErrors);
  throw error;
} finally {
  if(socket)socket.close();
  child.kill('SIGTERM');
  // Preserve screenshots and isolated test profile for inspection; never delete user profiles.
}
