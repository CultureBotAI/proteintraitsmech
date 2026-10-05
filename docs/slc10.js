/* Source data is rendered only with textContent and validated http(s) links. */
"use strict";
const $ = id => document.getElementById(id);
const el = (tag, text, cls) => { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(cls)n.className=cls; return n; };
const labels = {Q14973:"Human NTCP",Q12908:"Human ASBT",Q3KNW5:"Human SOAT",Q96EP9:"Human SLC10A4",Q0GE19:"Human SLC10A7",P26435:"Rat Ntcp",O08705:"Mouse Ntcp"};
const name = id => labels[id.split(":").pop()] || id;
const num = x => x === undefined ? "—" : Number(x).toFixed(2);
function link(text, href) {
  const n=el("a",text); const u=new URL(href,location.href);
  if(!["http:","https:"].includes(u.protocol))throw new Error("Unsafe source URL");
  n.href=u.href; return n;
}
function evidence(parent, rows=[]) {
  for(const e of rows) {const d=el("div"); d.append(link(e.reference,e.reference.replace(/^DOI:/,"https://doi.org/")));
    if(e.snippet)d.append(el("blockquote",e.snippet)); if(e.notes)d.append(el("p",e.notes)); parent.append(d);}
}
function details(row) {
  const heading=el("h2",row.label||row.title||row.graph?.title||row.activity||row.assertion_id||row.source_id||row.mechanism_id);
  heading.id="detail-title"; const body=$("detail-body"); body.replaceChildren(heading);
  if(row.limitations)body.append(el("p",row.limitations,"notice")); evidence(body,row.evidence);
  body.append(el("pre",JSON.stringify(row,null,2))); $("detail").showModal();
}
function action(text,row,cls) {const b=el("button",text,cls); b.type="button"; b.addEventListener("click",()=>details(row)); return b;}
function table(node,headings,rows,caption) {
  node.replaceChildren(el("caption",caption)); const head=el("thead"), tr=el("tr");
  for(const text of headings){const th=el("th",text);th.scope="col";tr.append(th);} head.append(tr);node.append(head);
  const body=el("tbody"); for(const row of rows){const r=el("tr");row.forEach((v,i)=>{const c=el(i===0?"th":"td");if(i===0)c.scope="row";c.append(v instanceof Node?v:document.createTextNode(String(v)));r.append(c);});body.append(r);}node.append(body);
}
async function main() {
  const receiptResponse=await fetch("data/slc10-pilot-manifest.json");if(!receiptResponse.ok)throw new Error("Export manifest unavailable");
  const receipt=await receiptResponse.json();if(!/^slc10-pilot-v[1-9][0-9]*\.json$/.test(receipt.file))throw new Error("Unexpected export file");
  const response=await fetch("data/"+receipt.file);if(!response.ok)throw new Error("Evidence bundle unavailable");
  const raw=await response.arrayBuffer();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",raw)),b=>b.toString(16).padStart(2,"0")).join("");
  if(hash!==receipt.sha256||raw.byteLength!==receipt.bytes)throw new Error("Evidence export does not match its manifest");
  const b=JSON.parse(new TextDecoder().decode(raw));
  if(b.bundle_id!==receipt.bundle_id||b.version!==receipt.version)throw new Error("Bundle identity mismatch");
  $("download").href="data/"+receipt.file;
  $("panel-scope").textContent=b.scope_note;
  $("summary").textContent=`${b.protein_references.length} proteins · ${b.sites.length} ligand-instance shells · ${b.functional_observations.length} observations/assessments · ${b.mechanisms.length} mechanisms · bundle v${b.version}`;
  const indexed=new Map([...(b.sites||[]),...(b.comparisons||[]),...(b.model_comparisons||[]),...(b.functional_observations||[]),...(b.explanations||[])].map(r=>[r.assertion_id,r]));
  for(const e of b.explanations){const c=el("article",undefined,"card");c.id=e.assertion_id;c.append(el("span",e.assessment+" · "+e.review_status,"badge"),el("h3",e.claim),el("p",e.limitations));
    const ul=el("ul");for(const q of e.unresolved_questions)ul.append(el("li",q));c.append(ul);
    for(const ref of [...(e.supporting_assertions||[]),...(e.challenging_assertions||[])])c.append(action(ref,indexed.get(ref)));
    evidence(c,e.evidence);$("explanations").append(c);}
  function matrix(){const site=b.sites.find(s=>s.assertion_id===$("site").value);
    const positions=[...new Set(site.contacts.map(c=>c.protein_position))].sort((a,z)=>a-z);
    $("site-context").textContent=site.structure_state+" · "+site.ligand_instance+" · "+site.distance_cutoff_angstrom+" Å heavy-atom cutoff. "+site.limitations;
    table($("matrix"),["Protein",...positions.map(p=>site.contacts.find(c=>c.protein_position===p).protein_residue+p)],b.protein_references.map(protein=>{
      const comparison=b.comparisons.find(c=>c.site_ref===site.assertion_id&&c.protein_id===protein.protein_id);
      return [name(protein.protein_id),...positions.map(p=>{const r=comparison.residues.find(r=>r.anchor_position===p);
        const btn=action(r.status==="UNRESOLVED"?"?":r.target_residue+r.target_position,{...comparison,selected_residue:r},"cell "+r.status.toLowerCase());
        btn.title=`${name(protein.protein_id)}: anchor ${p}; ${r.status}; derived correspondence`;return btn;})];}),"Each protein uses its own UniProt numbering");
    $("site-detail").replaceChildren(action("Inspect full contact assertion",site));evidence($("site-detail"),site.evidence);
    if(site.cutoff_sensitivity){const t=el("table");table(t,["Cutoff (Å)","Atom pairs","Residues","Side-chain N/O/S positions"],site.cutoff_sensitivity.map(s=>[s.cutoff_angstrom,s.atom_pair_count,s.residue_positions.length,s.sidechain_heteroatom_positions.join(", ")||"None"]),"Cutoff sensitivity; N/O/S proximity is not proof of coordination");$("site-detail").append(t);}
  }
  for(const s of b.sites){const o=el("option",s.structure_id+" · "+s.ligand_instance);o.value=s.assertion_id;$("site").append(o);}
  $("site").value="slc10-site:7ZYI-J-706-NA-4.5A";$("site").addEventListener("change",matrix);matrix();
  table($("models"),["Apo model","Fit pairs","Global RMSD (Å)","E257 candidate","E257 CA residual (Å)","Evidence"],(b.model_comparisons||[]).map(m=>{
    const p=m.pairs.find(p=>p.anchor_position===257);return [name(m.protein_id),m.fit_residue_count,num(m.fit_rmsd_angstrom),p.target_position?p.target_residue+p.target_position:"Unresolved",num(p.ca_displacement_angstrom),action("Inspect fit and confidence",m)];}),"All models compared with experimental 7ZYI; no target ligand occupancy inferred");
  table($("assays"),["Protein","Activity / substrate","Outcome","Conditions & evidence"],b.functional_observations.map(o=>[name(o.protein_id),o.activity+" — "+o.substrate,o.outcome+(o.outcome==="NOT_ASSESSED"?" (evidence gap)":""),action("Inspect assay",o)]),"Measured results remain separate from computational comparisons");
  for(const m of b.mechanisms){const c=el("article",undefined,"card");c.id=m.mechanism_id;c.append(el("span",m.review_status,"badge"),el("h3",m.graph.title));
    const nodes=new Map(m.graph.nodes.map(n=>[n.node_id,n]));for(const e of m.graph.edges){const line=el("div",undefined,"edge");line.append(el("b",nodes.get(e.subject).label),el("span","↓ "+e.predicate),el("b",nodes.get(e.object).label));c.append(line,el("p",e.description));evidence(c,e.evidence);}
    c.append(el("p",m.limitations),action("Inspect graph and residue bindings",m));$("mechanisms").append(c);}
  for(const s of b.sources){const p=el("p");p.append(link(s.source_id,s.reference),document.createTextNode(" · "+s.source_version+" · "),link(s.license,s.license_url),el("br"),el("code",s.sha256));$("sources").append(p);}
  if(location.hash){const id=decodeURIComponent(location.hash.slice(1));if(indexed.has(id))details(indexed.get(id));else document.getElementById(id)?.scrollIntoView();}
}
$("close-detail").addEventListener("click",()=>$("detail").close());
main().catch(error=>{$("summary").textContent="Cannot display verified evidence: "+error.message;$("summary").className="notice";});
