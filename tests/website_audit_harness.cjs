const assert = require('node:assert/strict');
const fs = require('node:fs');
const {gzipSync}=require('node:zlib');
const vm = require('node:vm');
const crypto = require('node:crypto').webcrypto;
const nodes = new Map();
const node = id => { if (!nodes.has(id)) nodes.set(id, {innerHTML:'',textContent:''}); return nodes.get(id); };
let reject = false, payload = {}, calls = [];
const context = vm.createContext({console, Map, Set, TextEncoder, crypto, Uint8Array, URLSearchParams, Response, DecompressionStream, Blob,
  history:{replaceState:(_s,_t,hash)=>{context.window.location.hash=hash;}},
  window:{location:{hash:'#record=test%3A1'}},
  document:{getElementById:node,querySelectorAll:()=>[]},
  BrowseShards:{createLoader:()=>({load:async()=>{}})},
  fetch:async url=>{calls.push(url);if(reject) throw new Error('offline');return {ok:true,json:async()=>payload,body:new Blob([gzipSync(JSON.stringify(payload))]).stream()};}});
let source=fs.readFileSync('docs/browse.js','utf8').replace(/boot\(\);\s*$/, '');
vm.runInContext(source,context);
const run=code=>vm.runInContext(code,context);
(async()=>{
 assert.equal(run('sourceUrl("PDB:1TIM")'),'https://www.rcsb.org/structure/1TIM');
 assert.equal(run('sourceUrl("PDB:1TIM_A")'),null);
 assert.equal(run('sourceUrl("SCOP:63467")'),null);
 assert.equal(run('sourceUrl("unknown:1")'),null);
 run('LABELS={"parent:1":"Parent"};');
 assert.match(run('localTraitLink("parent:1")'),/#record=parent%3A1/);
 assert.doesNotMatch(run('localTraitLink("unknown:1")'),/#record/);
 assert.match(run('structuredData([{action:"<script>",evidence:["PMID:1"]}])'),/&lt;script&gt;/);
 assert.doesNotMatch(run('structuredData([{action:"<script>"}])'),/<script>/);
 for(const [loader,reset] of [['loadLabels','LABELS=null; LABELS_PROMISE=null'],['loadMethods','METHODS=null; METHODS_PROMISE=null'],['fetchDetailBucket("detail/test.json")','DETAIL_CACHE.clear()']]){
  run(reset);reject=true;
  await assert.rejects(run(loader.includes('(')?loader:loader+'()'));
  reject=false;payload={loaded:true};
  assert.equal((await run(loader.includes('(')?loader:loader+'()')).loaded,true);
 }
 run('let r={id:"test:1",label:"Test",df:"detail/test.json"}; DETAIL_CACHE.clear();');
 reject=true;await assert.rejects(run('loadDetail(r)'));assert.equal(run('r._dl'),undefined);
 reject=false;payload={'test:1':{xr:['PDB:1TIM']}};await run('loadDetail(r)');assert.equal(run('r._dl'),true);
 run('let graphRecord={id:"graph:1",gf:"graphs/001.json.gz"};');
 reject=true;await assert.rejects(run('loadGraphs(graphRecord)'));assert.equal(run('graphRecord.cg'),undefined);
 reject=false;payload={"graph:1":[{edges:[{evidence:["PMID:1"]}]}]};await run('loadGraphs(graphRecord)');assert.equal(run('graphRecord.cg.length'),1);
 for(const invalid of [null,{}, {"test:1":[],"graph:1":{}}]){
  run('r={id:"test:1",df:"detail/test.json"}; graphRecord={id:"graph:1",gf:"graphs/001.json.gz"}; DETAIL_CACHE.clear();');
  payload=invalid;
  await assert.rejects(run('loadDetail(r)'));
  await assert.rejects(run('loadGraphs(graphRecord)'));
  assert.equal(run('DETAIL_CACHE.size'),0);
  payload={"test:1":{xr:["PDB:1TIM"]},"graph:1":[{edges:[]}]};
  await run('loadDetail(r)');await run('loadGraphs(graphRecord)');
  assert.equal(run('r._dl'),true);assert.equal(run('graphRecord.cg.length'),1);
 }
 run('LABELS={"parent:1":"Parent"}; LABELS_PROMISE=Promise.resolve(LABELS); METHODS={}; METHODS_PROMISE=Promise.resolve(METHODS); r={id:"test:1",label:"Test",_dl:true,_nb:[],pt:[["parent:1","biolink:subclass_of"],["parent:1","biolink:subclass_of"],["parent:1","biolink:part_of"]],syn:["aacCA2"],cg:[{edges:[{subject:"a",object:"b",evidence:["PMID:1"]}]}],history:[{date:"2026-01-01",action:"CREATED"}]};');
 await run('renderDetail(r)');
 let html=node('results').innerHTML;
 assert.equal((html.match(/href="#record=parent%3A1"/g)||[]).length,2);
 for(const text of ['Synonyms','aacCA2','Causal graphs','PMID:1','Curation history','2026-01-01']) assert.ok(html.includes(text),text);
 assert.doesNotMatch(html,/history.back/);
 assert.match(html,/href="#">← back to results/);
 run('LAST_RESULTS_HASH="#src=PROSITE"');await run('renderDetail(r)');assert.match(node('results').innerHTML,/#src=PROSITE/);
 run('RECORDS=[{id:"a",syn:["aacCA2"]},{id:"b",syn:["aacCA2"]}]; QUERY="aacca2"; FILTERED_CACHE=null');assert.equal(run('filterRecords().length'),2);
 run('SELECTED={axis:new Set(),cat:new Set(["B"]),src:new Set(["Source"]),sta:new Set()}; PAGE=2;');
 node('q').value='aacCA2'; context.window.location.hash='#cat=A';
 run('syncResultsHash()'); const saved=context.window.location.hash;
 assert.ok(saved.includes('cat=B') && saved.includes('src=Source') && saved.includes('q=aacCA2') && saved.includes('page=2'));
 run('SELECTED.cat.clear(); QUERY=""; PAGE=0; refreshFacetCounts=()=>{}; renderList=()=>{};');
 await run('route()');
 assert.equal(run('[...SELECTED.cat][0]'),'B'); assert.equal(run('QUERY'),'aacca2'); assert.equal(run('PAGE'),2);
 run('let rejectOld; exactRecord=()=>new Promise((_, reject)=>{rejectOld=reject;});');
 context.window.location.hash='#record=slow%3Aold'; const old=run('route()');
 context.window.location.hash='#record=new%3Arecord'; node('results').innerHTML='new record remains';
 run('rejectOld(new Error("offline"))'); await old;
 assert.equal(node('results').innerHTML,'new record remains');
 console.log('browser identity, navigation, structured evidence, synonyms and recoverable errors PASS');
})().catch(error=>{console.error(error);process.exitCode=1});
