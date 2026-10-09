/* Offline DOM-contract test, not a real-browser layout/screenshot test. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {webcrypto, createHash} = require("node:crypto");
const root = path.resolve(__dirname, "..");
const ids = new Map();
class Element {
  constructor(tag) {this.tag=tag;this.children=[];this.textContent="";this.events={};}
  append(...nodes) {this.children.push(...nodes);}
  replaceChildren(...nodes) {this.children=nodes;this.textContent="";}
  addEventListener(type, callback) {this.events[type]=callback;}
  set id(id) {this._id=id;ids.set(id,this);}
  get id() {return this._id;}
  showModal() {this.open=true;}
  close() {this.open=false;}
  scrollIntoView() {}
}
const html=fs.readFileSync(path.join(root,"docs/slc10.html"),"utf8");
for(const [,id] of html.matchAll(/\bid="([^"]+)"/g))new Element("div").id=id;
const raw=fs.readFileSync(path.join(root,"data/molecular/slc10/pilot.json"));
const bundle=JSON.parse(raw);
const receipt={file:"slc10-pilot-v1.json",bundle_id:bundle.bundle_id,version:bundle.version,
  sha256:createHash("sha256").update(raw).digest("hex"),bytes:raw.length};
const document={getElementById:id=>ids.get(id)||null,createElement:tag=>new Element(tag),
  createTextNode:text=>{const n=new Element("text");n.textContent=text;return n;}};
const context=vm.createContext({document,Node:Element,URL,TextDecoder,Uint8Array,crypto:webcrypto,
  location:{href:"http://localhost/slc10.html",hash:""},fetch:async url=>{
    assert(["data/slc10-pilot-manifest.json","data/slc10-pilot-v1.json"].includes(url));
    return {ok:true,json:async()=>receipt,arrayBuffer:async()=>raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.length)};
  }});
let js=fs.readFileSync(path.join(root,"docs/slc10.js"),"utf8");
assert(js.includes("main().catch("));
js=js.replace("main().catch(","globalThis.finished = main().catch(");
const text=n=>n.textContent+n.children.map(c=>typeof c==="string"?c:text(c)).join(" ");
const all=n=>[n,...n.children.flatMap(c=>c instanceof Element?all(c):[])];
async function run(){
  vm.runInContext(js,context);
  await context.finished;
  assert(!text(ids.get("summary")).includes("Cannot display"));
  const cards=ids.get("residue-reasoning").children;
  assert.equal(cards.length,2);
  assert(text(cards[0]).includes("S267F"));
  assert(text(cards[1]).includes("R252H"));
  assert(text(cards[0]).includes("UNRESOLVED"));
  assert(text(cards[0]).includes("glycochenodeoxycholic acid"));
  assert(text(cards[1]).includes("Reference side-chain pKa"));
  const simulation=all(cards[0]).find(n=>n.tag==="button"&&text(n)==="Inspect PUBLISHED_SIMULATION");
  simulation.events.click();
  assert(ids.get("detail").open);
  assert(text(ids.get("detail-body")).includes("10.1016/j.bpj.2024.03.033"));
  assert(text(ids.get("detail-body")).includes("CHEBI:36257"));
  const chemistry=all(cards[1]).find(n=>n.tag==="button"&&text(n).startsWith("Inspect reference/alternate"));
  chemistry.events.click();
  assert(text(ids.get("detail-body")).includes('"llm_assisted": true'));
  assert(text(ids.get("detail-body")).includes("NOT_APPLICABLE")===false); // R/H have defined pKa.
  console.log("SLC10 DOM contract passed: two cases, properties, gaps, provenance and detail actions");
}
run().catch(error=>{console.error(error);process.exitCode=1;});
