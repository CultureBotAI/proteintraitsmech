/* ProteinTraitsMech client-side faceted browser.
 *
 * Data source: docs/data/records.json (single flat array, ~8 MB uncompressed;
 * gzipped by Pages so wire size is far smaller).
 *
 * Views:
 *   #                    → paged, faceted list
 *   #record=<identifier> → single-record detail
 */

const REPO_RAW = "https://github.com/CultureBotAI/proteintraitsmech/blob/main/";
const PAGE_SIZE = 60;

// CURIE prefix → resolver URL. Missing prefixes fall through to a
// wikidata search URL.
const PREFIXES = {
  PROSITE:       "https://prosite.expasy.org/",
  GO:            "https://amigo.geneontology.org/amigo/term/GO:",
  ChEBI:         "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:",
  "CHEBI":       "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:",
  UniProtKB:     "https://www.uniprot.org/uniprotkb/",
  AlphaFoldDB:   "https://alphafold.ebi.ac.uk/entry/",
  SO:            "https://www.sequenceontology.org/browser/current_release/term/SO:",
  RHEA:          "https://www.rhea-db.org/rhea/",
  EC:            "https://enzyme.expasy.org/EC/",
  HAMAP:         "https://hamap.expasy.org/rule/",
  PMID:          "https://pubmed.ncbi.nlm.nih.gov/",
  DOI:           "https://doi.org/",
  NCBITaxon:     "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=",
  Pfam:          "https://www.ebi.ac.uk/interpro/entry/pfam/",
  InterPro:      "https://www.ebi.ac.uk/interpro/entry/InterPro/",
  TED:           "https://ted.cathdb.info/",
  PR:            "https://www.ebi.ac.uk/ols4/ontologies/pr/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FPR_",
  PATO:          "http://purl.obolibrary.org/obo/PATO_",
  RO:            "http://purl.obolibrary.org/obo/RO_",
  MOD:           "http://purl.obolibrary.org/obo/MOD_",
  HP:            "https://hpo.jax.org/browse/term/HP:",
  MONDO:         "https://www.ebi.ac.uk/ols4/ontologies/mondo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FMONDO_",
  CATH:          "https://www.cathdb.info/version/latest/superfamily/",
  SCOP:          "http://scop.mrc-lmb.cam.ac.uk/term/",
  MEROPS:        "https://www.ebi.ac.uk/merops/cgi-bin/pepsum?id=",
  MOD:           "https://www.ebi.ac.uk/ols4/ontologies/mod/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FMOD_",
  MI:            "https://www.ebi.ac.uk/ols4/ontologies/mi/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FMI_",
  PATO:          "https://www.ebi.ac.uk/ols4/ontologies/pato/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FPATO_",
  METPO:         "https://www.ebi.ac.uk/ols4/ontologies/metpo/classes/https%253A%252F%252Fw3id.org%252Fmetpo%252F",
  OMP:           "https://www.ebi.ac.uk/ols4/ontologies/omp/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FOMP_",
  ECOCORE:       "https://www.ebi.ac.uk/ols4/ontologies/ecocore/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FECOCORE_",
  valuesets:     "https://linkml.io/valuesets/elements/",
  proteintraitsmech: null, // internal — no external resolver
};

// Trait identifier prefix → UniProt search query for "all proteins carrying
// this family id". The query is a pure function of the id, so the members link
// is derived (no per-record data). CATH is exposed in UniProt as Gene3D; SCOP
// via SUPERFAMILY (needs an sccs→SSF map, so omitted here).
const MEMBER_QUERY = {
  Pfam:        id => `xref:pfam-${id}`,
  InterPro:    id => `xref:interpro-${id}`,
  CATH:        id => `xref:gene3d-${id}`,
  SUPERFAMILY: id => `xref:supfam-${id}`,
  PROSITE:     id => `xref:prosite-${id}`,
  SMART:       id => `xref:smart-${id}`,
  HAMAP:       id => `xref:hamap-${id}`,
  PANTHER:     id => `xref:panther-${id}`,
};

// Return the UniProtKB "all family members" search URL for a record id, or null.
function uniprotMembersUrl(curie) {
  const i = (curie || "").indexOf(":");
  if (i < 0) return null;
  const fn = MEMBER_QUERY[curie.slice(0, i)];
  if (!fn) return null;
  return "https://www.uniprot.org/uniprotkb?query=" +
         encodeURIComponent(fn(curie.slice(i + 1)));
}

const FACET_GROUPS = [
  { key: "axis", label: "Axis" },
  { key: "src",  label: "Source" },
  { key: "cat",  label: "Category" },
  { key: "sta",  label: "Status" },
];

/* ------------------------------------------------------------------ */
/* State                                                              */
/* ------------------------------------------------------------------ */

let RECORDS = [];       // all records, sorted by id
let ID_INDEX = new Map(); // id → record
let FACETS = { total: 0, counts: {} };
let SELECTED = { axis: new Set(), src: new Set(), cat: new Set(), sta: new Set() };
let QUERY = "";
let PAGE = 0;
let FILTERED_CACHE = null;

/* ------------------------------------------------------------------ */
/* Boot                                                               */
/* ------------------------------------------------------------------ */

// Records are sharded by axis (records.<AXIS>[.NN].json). At ~274k records
// loading every shard upfront is ~95 MB — most of it STRUCTURE, which a
// SEQUENCE/FUNCTION/EVOLUTION browse never needs. So we load shards LAZILY,
// per axis, driven by the active filter: the facet panel + counts come from
// the tiny precomputed facets.json, and an axis's records are fetched only
// when a filter/search actually needs them.
let AXIS_SHARDS = {};                 // axis → [shard file]
const LOADED_AXES = new Set();
const AXIS_FETCH = new Map();         // axis → in-flight promise (dedup)
const CAT_AXIS = { SEQ: "SEQUENCE", STRUCT: "STRUCTURE",
                   MIXED: "SEQUENCE_STRUCTURE", FUNC: "FUNCTION", EVO: "EVOLUTION" };

function axisOfShard(file) {
  const m = file.match(/^records\.([A-Z_]+?)(?:\.\d+)?\.json$/);
  return m ? m[1] : "OTHER";
}

function loadAxis(axis) {
  if (LOADED_AXES.has(axis)) return Promise.resolve();
  if (!AXIS_FETCH.has(axis)) {
    const files = AXIS_SHARDS[axis] || [];
    AXIS_FETCH.set(axis, Promise.all(files.map(f =>
      fetch("data/" + f).then(r => (r.ok ? r.json() : [])).catch(() => [])
    )).then(parts => {
      for (const p of parts) for (const rec of p) {
        RECORDS.push(rec); ID_INDEX.set(rec.id, rec);
      }
      LOADED_AXES.add(axis);
      FILTERED_CACHE = null;
    }));
  }
  return AXIS_FETCH.get(axis);
}
const loadAxes = axes => Promise.all([...axes].map(loadAxis));
const loadAllAxes = () => loadAxes(Object.keys(AXIS_SHARDS));

// Which axis shards the current selection/query needs. Empty = landing (load
// nothing); a bare text query with no narrowing filter = the whole corpus.
function neededAxes() {
  const need = new Set();
  const axesBy = FACETS.axesBy || { src: {}, cat: {}, sta: {} };
  SELECTED.axis.forEach(a => need.add(a));
  // Prefer the precomputed cat→axis map (handles prefix-less categories like
  // UPPER); fall back to the category-prefix heuristic.
  SELECTED.cat.forEach(c => {
    const mapped = axesBy.cat[c];
    if (mapped && mapped.length) { mapped.forEach(a => need.add(a)); return; }
    const a = CAT_AXIS[c.split("_")[0]];
    if (a) need.add(a);
  });
  SELECTED.src.forEach(s => (axesBy.src[s] || []).forEach(a => need.add(a)));
  SELECTED.sta.forEach(s => (axesBy.sta[s] || []).forEach(a => need.add(a)));
  if (QUERY && need.size === 0) return new Set(Object.keys(AXIS_SHARDS));
  return need;
}

async function boot() {
  const results = document.getElementById("results");
  try {
    const facRes = await fetch("data/facets.json");
    if (!facRes.ok) throw new Error("facets.json " + facRes.status);
    FACETS = await facRes.json();
  } catch (e) {
    results.innerHTML = `<div class="empty">Failed to load index: ${e.message}</div>`;
    return;
  }
  const shards = (FACETS.shards && FACETS.shards.length)
    ? FACETS.shards.map(s => s.file) : ["records.json"];
  AXIS_SHARDS = {};
  for (const f of shards) (AXIS_SHARDS[axisOfShard(f)] ||= []).push(f);

  document.getElementById("record-count").textContent =
    FACETS.total.toLocaleString() + " records";
  renderFacetSidebar();
  wireInputs();
  window.addEventListener("hashchange", route);
  route();
}

/* ------------------------------------------------------------------ */
/* Routing                                                            */
/* ------------------------------------------------------------------ */

async function route() {
  const h = window.location.hash;
  if (h.startsWith("#record=")) {
    const id = decodeURIComponent(h.slice("#record=".length));
    let rec = ID_INDEX.get(id);
    if (!rec) {
      // Cold deep-link to a record whose axis isn't loaded — fall back to a
      // one-time full load, then look it up.
      document.getElementById("results").innerHTML =
        `<div class="empty">Loading record…</div>`;
      await loadAllAxes();
      rec = ID_INDEX.get(id);
    }
    if (rec) return renderDetail(rec);
    return renderNotFound(id);
  }
  // Facet deep-links (e.g. "#cat=STRUCT_FOLD", "#axis=SEQUENCE&src=PROSITE").
  // Only applied when the hash actually carries facet params, so returning
  // from a detail view to an empty hash preserves in-memory selections.
  const params = parseHashParams(h);
  if (Object.values(params).some(a => a.length)) applyHashFacets(params);
  renderList();
}

// Parse a facet deep-link hash into per-group value lists. Repeated keys
// accumulate, e.g. "#cat=A&cat=B" → { cat: ["A", "B"], … }.
function parseHashParams(h) {
  const out = { axis: [], src: [], cat: [], sta: [] };
  const body = (h || "").replace(/^#/, "");
  if (!body) return out;
  for (const pair of body.split("&")) {
    const eq = pair.indexOf("=");
    if (eq < 0) continue;
    const k = pair.slice(0, eq);
    if (!(k in out)) continue;
    out[k].push(decodeURIComponent(pair.slice(eq + 1)));
  }
  return out;
}

// Apply parsed facet params to SELECTED and sync the sidebar checkboxes.
function applyHashFacets(params) {
  for (const k of Object.keys(SELECTED)) SELECTED[k] = new Set(params[k]);
  document.querySelectorAll("#facet-scroll .facet-item").forEach(item => {
    const el = item.querySelector("input[type=checkbox]");
    if (!el) return;
    const on = SELECTED[el.dataset.facet] && SELECTED[el.dataset.facet].has(el.value);
    el.checked = on;
    item.classList.toggle("is-selected", !!on);  // stays visible while collapsed
  });
  FILTERED_CACHE = null;
  PAGE = 0;
  updateActiveCount();
  refreshFacetCounts();
}

/* ------------------------------------------------------------------ */
/* Facet sidebar                                                      */
/* ------------------------------------------------------------------ */

function renderFacetSidebar() {
  const scroll = document.getElementById("facet-scroll");
  const parts = [];
  for (const grp of FACET_GROUPS) {
    const counts = FACETS.counts[grp.key] || {};
    const entries = Object.entries(counts);
    const rows = entries.map(([val, n]) => {
      const sel = SELECTED[grp.key] && SELECTED[grp.key].has(val);
      return `
      <label class="facet-item${sel ? " is-selected" : ""}">
        <input type="checkbox" data-facet="${grp.key}" value="${escapeAttr(val)}" ${sel ? "checked" : ""}/>
        <span class="name" title="${escapeAttr(val)}">${escapeHTML(val)}</span>
        <span class="count">${n.toLocaleString()}</span>
      </label>`;
    }).join("");
    // Groups start collapsed: only selected values show until "Show all".
    parts.push(`
      <div class="facet-group" data-key="${grp.key}">
        <h3 class="facet-head" role="button" tabindex="0" aria-expanded="false">
          <span>${escapeHTML(grp.label)}</span>
          <button class="facet-toggle" type="button" tabindex="-1">Show all (${entries.length})</button>
        </h3>
        <div class="facet-items">${rows}</div>
      </div>`);
  }
  parts.push(`
    <div class="facet-toolbar">
      <button id="clear-facets">Clear all</button>
      <span id="active-count" class="count"></span>
    </div>`);
  scroll.innerHTML = parts.join("");

  scroll.querySelectorAll("input[type=checkbox]").forEach(el => {
    el.addEventListener("change", () => {
      const facet = el.dataset.facet;
      const item = el.closest(".facet-item");
      if (el.checked) { SELECTED[facet].add(el.value); item.classList.add("is-selected"); }
      else            { SELECTED[facet].delete(el.value); item.classList.remove("is-selected"); }
      FILTERED_CACHE = null;
      PAGE = 0;
      updateActiveCount();
      refreshFacetCounts();
      renderList();
    });
  });
  scroll.querySelectorAll(".facet-head").forEach(h => {
    const toggle = () => setGroupExpanded(h.closest(".facet-group"),
                                          !h.closest(".facet-group").classList.contains("expanded"));
    h.addEventListener("click", e => { if (e.target.tagName !== "INPUT") toggle(); });
    h.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
    });
  });
  document.getElementById("clear-facets").addEventListener("click", () => {
    for (const k of Object.keys(SELECTED)) SELECTED[k].clear();
    scroll.querySelectorAll(".facet-item").forEach(i => i.classList.remove("is-selected"));
    scroll.querySelectorAll("input[type=checkbox]").forEach(el => (el.checked = false));
    scroll.querySelectorAll(".facet-group").forEach(g => setGroupExpanded(g, false));
    FILTERED_CACHE = null;
    PAGE = 0;
    updateActiveCount();
    refreshFacetCounts();
    renderList();
  });
  updateActiveCount();
  refreshFacetCounts();
}

// Expand/collapse a facet group and sync its toggle button label.
function setGroupExpanded(group, open) {
  group.classList.toggle("expanded", open);
  const head = group.querySelector(".facet-head");
  const btn = group.querySelector(".facet-toggle");
  if (head) head.setAttribute("aria-expanded", open ? "true" : "false");
  if (btn) btn.textContent = open ? "Show less" : `Show all (${group.querySelectorAll(".facet-item").length})`;
}

function updateActiveCount() {
  const n = Object.values(SELECTED).reduce((a, s) => a + s.size, 0);
  const el = document.getElementById("active-count");
  el.textContent = n ? `${n} active` : "";
}

// Facet counts for the CURRENT filtered subset. For each group we count values
// across records that match all the OTHER active groups (and the search query)
// — standard faceted-search semantics, so each number is "how many records you
// get if you also pick this value". Values with 0 in the subset are returned as
// absent and hidden by refreshFacetCounts(). With no filters this equals the
// global counts. O(records × groups²) ≈ a few M ops — recomputed on each change.
function computeFacetCounts() {
  const groups = FACET_GROUPS.map(g => g.key);   // axis, src, cat, sta
  const counts = {};
  groups.forEach(k => (counts[k] = Object.create(null)));
  const qs = QUERY;
  for (const r of RECORDS) {
    if (qs && !(
      (r.id && r.id.toLowerCase().includes(qs)) ||
      (r.label && r.label.toLowerCase().includes(qs)) ||
      (r.def && r.def.toLowerCase().includes(qs)) ||
      (r.chem && r.chem.some(n => n.toLowerCase().includes(qs))) ||
      (r.chemx && r.chemx.some(n => n.toLowerCase().includes(qs))))) continue;
    for (const k of groups) {
      let ok = true;
      for (const k2 of groups) {
        if (k2 === k) continue;
        const sel = SELECTED[k2];
        if (sel.size && !sel.has(r[k2])) { ok = false; break; }
      }
      if (!ok) continue;
      const v = r[k];
      if (v != null && v !== "") counts[k][v] = (counts[k][v] || 0) + 1;
    }
  }
  return counts;
}

// Push counts into the sidebar DOM. With lazy loading there are two regimes:
//  • nothing loaded yet → show the GLOBAL counts (from facets.json) and hide
//    nothing, so every value stays clickable (clicking loads its axis);
//  • axes loaded → show subset counts over the loaded records and hide empties,
//    EXCEPT the axis group, which always shows global counts so any axis stays
//    switchable (picking it lazily loads that shard).
function refreshFacetCounts() {
  const global = LOADED_AXES.size === 0;
  const counts = global ? null : computeFacetCounts();
  const gcounts = (FACETS.counts) || {};
  document.querySelectorAll("#facet-scroll .facet-group").forEach(group => {
    const key = group.dataset.key;
    const useGlobal = global || key === "axis";
    const c = useGlobal ? (gcounts[key] || {}) : (counts[key] || {});
    let visible = 0;
    group.querySelectorAll(".facet-item").forEach(item => {
      const el = item.querySelector("input[type=checkbox]");
      if (!el) return;
      const n = c[el.value] || 0;
      const cnt = item.querySelector(".count");
      if (cnt) cnt.textContent = n.toLocaleString();
      const selected = SELECTED[key] && SELECTED[key].has(el.value);
      const empty = !useGlobal && n === 0 && !selected;
      item.classList.toggle("is-empty", empty);
      if (!empty) visible++;
    });
    const btn = group.querySelector(".facet-toggle");
    if (btn && !group.classList.contains("expanded"))
      btn.textContent = `Show all (${visible})`;
  });
}

/* ------------------------------------------------------------------ */
/* Inputs                                                             */
/* ------------------------------------------------------------------ */

function wireInputs() {
  const q = document.getElementById("q");
  let timer;
  q.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      QUERY = q.value.trim().toLowerCase();
      FILTERED_CACHE = null;
      PAGE = 0;
      refreshFacetCounts();
      renderList();
    }, 120);
  });
}

/* ------------------------------------------------------------------ */
/* Filtering                                                          */
/* ------------------------------------------------------------------ */

function filterRecords() {
  if (FILTERED_CACHE) return FILTERED_CACHE;
  const qs = QUERY;
  const anyFacet = Object.values(SELECTED).some(s => s.size > 0);
  let out = RECORDS;
  if (anyFacet) {
    out = out.filter(r =>
      (!SELECTED.axis.size || SELECTED.axis.has(r.axis)) &&
      (!SELECTED.src.size  || SELECTED.src.has(r.src))   &&
      (!SELECTED.cat.size  || SELECTED.cat.has(r.cat))   &&
      (!SELECTED.sta.size  || SELECTED.sta.has(r.sta))
    );
  }
  if (qs) {
    out = out.filter(r =>
      (r.id && r.id.toLowerCase().includes(qs)) ||
      (r.label && r.label.toLowerCase().includes(qs)) ||
      (r.def && r.def.toLowerCase().includes(qs))
    );
  }
  FILTERED_CACHE = out;
  return out;
}

/* ------------------------------------------------------------------ */
/* List view                                                          */
/* ------------------------------------------------------------------ */

async function renderList() {
  const results = document.getElementById("results");
  const need = neededAxes();

  // Landing: nothing selected and no query — don't bulk-load the corpus; the
  // facet panel (global counts) is already shown, so prompt the user to pick.
  if (need.size === 0) {
    const axisCounts = (FACETS.counts && FACETS.counts.axis) || {};
    const cards = Object.entries(axisCounts).sort((a, b) => b[1] - a[1])
      .map(([a, n]) => `<a class="axis-card" href="#axis=${encodeURIComponent(a)}">
        <strong>${n.toLocaleString()}</strong><span>${escapeHTML(a)}</span></a>`).join("");
    results.innerHTML = `<div class="landing">
      <p><strong>${FACETS.total.toLocaleString()} trait records.</strong>
      Pick an axis, category or source on the left — or search — to load records.
      (Records are loaded per axis on demand to keep the page light.)</p>
      <div class="axis-cards">${cards}</div></div>`;
    return;
  }

  // Load only the axis shards this view needs; show a spinner while fetching.
  const missing = [...need].filter(a => !LOADED_AXES.has(a));
  if (missing.length) {
    results.innerHTML = `<div class="empty">Loading ${missing.join(", ")}…</div>`;
    await loadAxes(need);
    refreshFacetCounts();
  }

  const list = filterRecords();
  const pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
  if (PAGE >= pages) PAGE = pages - 1;
  const slice = list.slice(PAGE * PAGE_SIZE, (PAGE + 1) * PAGE_SIZE);

  const header = `
    <div class="results-header">
      <div class="summary">
        ${list.length.toLocaleString()} record${list.length === 1 ? "" : "s"}
        ${(QUERY || Object.values(SELECTED).some(s => s.size)) ? "· filtered" : ""}
      </div>
      <div class="paging">
        <button ${PAGE === 0 ? "disabled" : ""} onclick="_go(-1)">‹ Prev</button>
        <span>Page ${PAGE + 1} / ${pages}</span>
        <button ${PAGE >= pages - 1 ? "disabled" : ""} onclick="_go(1)">Next ›</button>
      </div>
    </div>`;

  if (list.length === 0) {
    results.innerHTML = header + `<div class="empty">No records match. Clear filters or the search box.</div>`;
    return;
  }

  // Each pill is its own facet-filter link (#axis=/#cat=/#src=/#sta=), NOT a
  // span inside the card's record anchor — so clicking a badge filters by it
  // instead of all four just opening the record.
  const facetPill = (key, val, cls) => val
    ? `<a class="pill${cls ? " " + cls : ""}" href="#${key}=${encodeURIComponent(val)}" title="filter: ${escapeAttr(val)}">${escapeHTML(val)}</a>`
    : "";
  const cards = slice.map(r => `
    <div class="card">
      <a class="card-main" href="#record=${encodeURIComponent(r.id)}">
        <div class="cid">${escapeHTML(r.id)}</div>
        <h3>${escapeHTML(r.label)}</h3>
        <p>${escapeHTML(r.def || "")}</p>
      </a>
      <div class="pills">
        ${facetPill("axis", r.axis, "axis")}
        ${facetPill("cat", r.cat, "")}
        ${facetPill("src", r.src, "src")}
        ${facetPill("sta", r.sta, "sta")}
      </div>
    </div>`).join("");

  results.innerHTML = header + `<div class="grid">${cards}</div>` + header;
}

// Called by inline paging buttons.
window._go = function (delta) {
  PAGE += delta;
  renderList();
  window.scrollTo({ top: 0, behavior: "smooth" });
};

/* ------------------------------------------------------------------ */
/* Detail view                                                        */
/* ------------------------------------------------------------------ */

async function renderDetail(r) {
  const results = document.getElementById("results");
  // Detail-only fields (full definition, path, parents, xrefs, mapped assocs,
  // chemistry, examples + sequences, pattern) live in a lazy per-record detail
  // sidecar to keep the upfront list/facet payload small. Fetch + merge before
  // rendering; bail if the user navigated away meanwhile.
  if (!r._dl) {
    await loadDetail(r);
    if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  }
  await loadNeighbors(r);
  if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  // Semantic neighbors: [neighbor_id, cosine] → internal record links.
  const relatedHtml = (r._nb || []).length
    ? `<ul class="xref-list">
        ${r._nb.map(([nid, sc]) =>
          `<li><a href="#record=${encodeURIComponent(nid)}">${escapeHTML(nid)}</a>`
          + ` <span class="map-src">${(sc).toFixed(2)}</span></li>`).join("")}
       </ul>`
    : "";
  const rawYamlLink = REPO_RAW + (r.path || "");
  const xrefsHtml = (r.xr || []).length
    ? `<ul class="xref-list">
        ${r.xr.map(x => `<li>${curieLink(x)}</li>`).join("")}
       </ul>`
    : "<em>none</em>";
  // Mapping-derived cross-references: [object, mapping_source] pairs, shown
  // with their provenance so they read distinctly from source-direct xrefs.
  const mappedHtml = (r.mx || []).length
    ? `<ul class="xref-list">
        ${r.mx.map(([obj, src, pred]) =>
          `<li>${curieLink(obj)} <span class="map-src">${pred ? escapeHTML(pred.replace("biolink:", "")) + " · " : ""}via ${escapeHTML(src || "mapping")}</span></li>`
        ).join("")}
       </ul>`
    : "";

  // Cross-source equivalence (biolink:close_match) from the InterPro member-DB
  // integration overlay — [object, predicate, relation_source] triples, linked
  // both ways (an InterPro entry lists its member signatures and vice-versa).
  const eqHtml = (r.eq || []).length
    ? `<ul class="xref-list">
        ${r.eq.map(([obj, pred, src]) =>
          `<li>${curieLink(obj)} <span class="map-src">${escapeHTML((pred || "biolink:close_match").replace("biolink:", ""))} · via ${escapeHTML(src || "mapping")}</span></li>`
        ).join("")}
       </ul>`
    : "";

  const ssRow = (r.ss || []).length
    ? row("Secondary structure (topology)",
          `<dd class="pre">${escapeHTML(r.ss.filter(Boolean).join("  ·  "))}</dd>`, true)
    : "";
  const geoRow = (r.geo || []).length
    ? row("Structure representative",
          `<dd>${r.geo.map(g => curieLink(g)).join(", ")}</dd>`, true)
    : "";

  const patternRow = r.pat
    ? row("Sequence pattern", `<dd class="pre">${escapeHTML(r.pat)}</dd>`, true)
    : "";

  const residueRow = r.rs
    ? row(`Residue sequence (${r.rs.length} aa)`,
          `<dd class="pre">${escapeHTML(r.rs)}</dd>`, true)
    : "";

  const parentHtml = (r.pt || []).length
    ? `<ul class="xref-list">
        ${r.pt.map(x => {
          const [cur, pred] = Array.isArray(x) ? x : [x, null];
          const rel = pred && pred !== "biolink:subclass_of"
            ? ` <span class="map-src">${escapeHTML(pred.replace("biolink:", ""))}</span>` : "";
          return `<li>${curieLink(cur)}${rel}</li>`;
        }).join("")}
       </ul>`
    : "";
  const parentRow = parentHtml
    ? row("Parent traits", `<dd>${parentHtml}</dd>`, true)
    : "";

  const examples = r.ex || [];
  // Sequences ride inside each example in the detail sidecar (already loaded
  // above), so examples render fully in one pass — no second lazy fetch.
  const examplesHtml = examples.length
    ? `<ul class="ex-list" id="ex-list">${examples.map(e => renderExample(e, false)).join("")}</ul>`
    : "";
  const examplesRow = examplesHtml
    ? row(`Example proteins (${examples.length})`,
          `<dd>${examplesHtml}</dd>`, true)
    : "";

  results.innerHTML = `
    <div class="detail">
      <div class="breadcrumb">
        <a href="#" onclick="history.back(); return false;">← back to results</a>
      </div>
      <h1>${escapeHTML(r.label)}</h1>
      <div class="cid">${escapeHTML(r.id)}</div>
      <div class="pills">
        ${r.axis ? `<span class="pill axis">${escapeHTML(r.axis)}</span>` : ""}
        ${r.cat  ? `<span class="pill">${escapeHTML(r.cat)}</span>`      : ""}
        ${r.src  ? `<span class="pill src">${escapeHTML(r.src)}</span>`  : ""}
        ${r.sta  ? `<span class="pill sta">${escapeHTML(r.sta)}</span>`  : ""}
      </div>
      <dl>
        ${row("Definition", `<dd>${escapeHTML(r.def || "—")}</dd>`, true)}
        ${row("Axis", `<dd>${escapeHTML(r.axis || "")}</dd>`, true)}
        ${row("Category", `<dd>${escapeHTML(r.cat  || "")}</dd>`, true)}
        ${row("Source", `<dd>${escapeHTML(r.src   || "")}</dd>`, true)}
        ${row("Status", `<dd>${escapeHTML(r.sta   || "")}</dd>`, true)}
        ${ssRow}
        ${geoRow}
        ${patternRow}
        ${residueRow}
        ${parentRow}
        ${examplesRow}
        ${uniprotMembersUrl(r.id)
          ? row("UniProt members",
                `<dd><a href="${escapeAttr(uniprotMembersUrl(r.id))}" target="_blank" rel="noopener">all proteins carrying ${escapeHTML(r.id)} ↗</a></dd>`, true)
          : ""}
        ${row("Cross-references", `<dd>${xrefsHtml}</dd>`, true)}
        ${mappedHtml ? row("Mapped associations", `<dd>${mappedHtml}</dd>`, true) : ""}
        ${eqHtml ? row("Equivalent entries", `<dd>${eqHtml}</dd>`, true) : ""}
        ${relatedHtml ? row("Related traits (semantic)", `<dd>${relatedHtml}</dd>`, true) : ""}
        ${(r.cp || []).length ? row("Chemistry", `<dd id="chem-list">${chemistryHtml(r)}</dd>`, true) : ""}
        ${(r.chemx || []).length ? row("Chemistry (via mappings)", `<dd>${r.chemx.map(escapeHTML).join(", ")}</dd>`, true) : ""}
        ${row("Detection methods", `<dd id="method-list">${METHODS ? (methodsHtml(r) || "<em>—</em>") : "<em>loading…</em>"}</dd>`, true)}
        ${row("Source file", `<dd><a href="${escapeAttr(rawYamlLink)}" target="_blank" rel="noopener"><code>${escapeHTML(r.path)}</code></a></dd>`, true)}
      </dl>
    </div>`;
  document.title = r.label + " — ProteinTraitsMech";
  // Enrich the chemistry row with names/formulae/InChIKeys once the ChEBI
  // sidecar loads (the row already shows linked ChEBI ids + roles).
  if ((r.cp || []).length && !CHEBI) {
    loadChebi().then(() => {
      if (window.location.hash === "#record=" + encodeURIComponent(r.id)) {
        const dd = document.getElementById("chem-list");
        if (dd) dd.innerHTML = chemistryHtml(r);
      }
    });
  }
  // Fill the detection-methods row once the (small) methods catalogue loads —
  // resolved from the record's source + category, not stored per-record.
  loadMethods().then(() => {
    if (window.location.hash === "#record=" + encodeURIComponent(r.id)) {
      const dd = document.getElementById("method-list");
      if (dd) dd.innerHTML = methodsHtml(r) || "<em>— (no catalogued method for this source/category)</em>";
    }
  });
}

// Methods catalogue (data/methods.json): how a trait is detected/predicted,
// keyed by_source + by_category. Loaded once on first detail view, cached.
let METHODS = null;
let METHODS_PROMISE = null;
function loadMethods() {
  if (!METHODS_PROMISE) {
    METHODS_PROMISE = fetch("data/methods.json")
      .then(res => (res.ok ? res.json() : {}))
      .then(j => { METHODS = j; return j; })
      .catch(() => { METHODS = {}; return {}; });
  }
  return METHODS_PROMISE;
}

// A record's detection methods = source-specific ∪ category-generic (the
// common-parent feature), source first, de-duplicated by name.
function methodsHtml(r) {
  if (!METHODS) return "";
  const bs = (METHODS.by_source || {})[r.src] || [];
  const bc = (METHODS.by_category || {})[r.cat] || [];
  const seen = new Set();
  const items = [];
  for (const [group, list] of [["source", bs], ["category", bc]]) {
    for (const m of list) {
      if (!m || seen.has(m.name)) continue;
      seen.add(m.name);
      const toolLink = m.tool && m.tool.startsWith("biotools:")
        ? `<a href="https://bio.tools/${m.tool.slice(9)}" target="_blank" rel="noopener">${escapeHTML(m.tool.slice(9))}</a>`
        : (m.tool ? `<a href="${escapeAttr(m.tool)}" target="_blank" rel="noopener">tool</a>` : "");
      const grounding = [m.edam, m.eco].filter(Boolean).map(escapeHTML).join(" · ");
      items.push(`<li>
        <strong>${escapeHTML(m.name)}</strong>
        <span class="map-src">${escapeHTML((m.method_type || "").toLowerCase().replace(/_/g, " "))} · ${group}</span>
        ${toolLink ? " · " + toolLink : ""}
        ${m.ref ? " · " + curieLink(m.ref) : ""}
        ${m.recipe ? `<div class="pre" style="margin:.25rem 0 0">${escapeHTML(m.recipe)}</div>` : ""}
        ${grounding ? `<div class="map-src">${grounding}</div>` : ""}
      </li>`);
    }
  }
  return items.length ? `<ul class="xref-list">${items.join("")}</ul>` : "";
}

// ChEBI sidecar (data/chebi.json): CHEBI id → {name, formula, inchikey}. One
// small (~2 MB) file, fetched once on first chemistry view and cached, so
// formula / InChIKey / canonical name aren't duplicated onto every record.
let CHEBI = null;
let CHEBI_PROMISE = null;
function loadChebi() {
  if (!CHEBI_PROMISE) {
    CHEBI_PROMISE = fetch("data/chebi.json")
      .then(res => (res.ok ? res.json() : {}))
      .then(j => { CHEBI = j; return j; })
      .catch(() => { CHEBI = {}; return {}; });
  }
  return CHEBI_PROMISE;
}

const ROLE_LABEL = {
  SUBSTRATE: "substrate", PRODUCT: "product",
  SUBSTRATE_OR_PRODUCT: "substrate/product", COFACTOR: "cofactor",
  TRANSPORTED: "transported", INHIBITOR: "inhibitor",
};

// One chemistry participant row. Uses the ChEBI sidecar when loaded (name +
// formula + InChIKey); degrades to just the linked ChEBI id + role otherwise.
function chemistryHtml(r) {
  const cps = r.cp || [];
  if (!cps.length) return "";
  return `<ul class="xref-list">
    ${cps.map(([id, role]) => {
      const info = (CHEBI && CHEBI[id]) || null;
      const name = info && info.name ? ` ${escapeHTML(info.name)}` : "";
      const formula = info && info.formula
        ? ` <span class="map-src">${escapeHTML(info.formula)}</span>` : "";
      const ik = info && info.inchikey
        ? ` <span class="map-src">${escapeHTML(info.inchikey)}</span>` : "";
      const rl = ROLE_LABEL[role] || (role || "").toLowerCase();
      return `<li>${curieLink(id)}${name}${formula}${ik}` +
             `${rl ? ` <span class="map-src">— ${escapeHTML(rl)}</span>` : ""}</li>`;
    }).join("")}
   </ul>`;
}

// Detail sidecars are bucketed: r.df is a bucket path (e.g. "detail/023.json")
// holding {record_id: detail} for ~780 records. Everything the list/facet views
// don't need (full definition, path, parents, xrefs, mapped assocs, chemistry,
// examples + their sequences, pattern) lives here so the upfront payload stays
// lean. Cache each bucket's fetch so opening several records in the same bucket
// costs one request.
const DETAIL_CACHE = new Map();
function fetchDetailBucket(file) {
  if (!DETAIL_CACHE.has(file)) {
    DETAIL_CACHE.set(file,
      fetch("data/" + file)
        .then(res => (res.ok ? res.json() : {}))
        .catch(() => ({})));
  }
  return DETAIL_CACHE.get(file);
}

// Merge a record's detail sidecar into the record object (once). Degrades
// gracefully: on any failure the lean fields (label, short def, pills) still
// render.
async function loadDetail(r) {
  if (r._dl) return;
  if (!r.df) { r._dl = true; return; }
  try {
    const bucket = await fetchDetailBucket(r.df);
    const d = bucket[r.id];
    if (d) Object.assign(r, d);   // full def, path, pt, xr, mx, cp, ex, rs, pat
  } catch (_) { /* keep lean fields */ }
  r._dl = true;
}

// Semantic "related traits" — precomputed nearest neighbors (scripts/
// embed_neighbors.py) live in neighbors/NNN.json, sharded by the SAME bucket
// number as the detail sidecar (r.df = "detail/NNN.json"). Lazy-loaded per
// record; absent (feature not built) → the row simply doesn't render.
async function loadNeighbors(r) {
  if (r._nb !== undefined) return;
  r._nb = null;
  if (!r.df) return;
  try {
    const bucket = await fetchDetailBucket(r.df.replace("detail/", "neighbors/"));
    if (bucket[r.id]) r._nb = bucket[r.id];   // [[neighbor_id, cosine], …]
  } catch (_) { /* no neighbors */ }
}

function renderNotFound(id) {
  document.getElementById("results").innerHTML = `
    <div class="detail">
      <div class="breadcrumb"><a href="#">← back to results</a></div>
      <h1>Record not found</h1>
      <p><code>${escapeHTML(id)}</code> is not in the current index.</p>
    </div>`;
}

function row(dt, ddHtml, always) {
  if (!always && !ddHtml) return "";
  return `<div><dt>${escapeHTML(dt)}</dt>${ddHtml}</div>`;
}

function renderExample(e, lazyPending) {
  const badges = [];
  if (e.rev === true)  badges.push(`<span class="pill sta">reviewed</span>`);
  if (e.rev === false) badges.push(`<span class="pill">unreviewed</span>`);
  if (e.asc)           badges.push(`<span class="pill">annotation ${escapeHTML(String(e.asc))}/5</span>`);
  if (e.len)           badges.push(`<span class="pill">${escapeHTML(String(e.len))} aa</span>`);
  if (e.src === "UNIPROTKB_API") badges.push(`<span class="pill src">UniProtKB API</span>`);
  else if (e.src === "CURATOR")  badges.push(`<span class="pill src">curator</span>`);

  const families = (e.fams || []).length
    ? `<div class="ex-families">${e.fams.map(curieLink).join(" ")}</div>`
    : "";
  const idLink = e.id ? curieLink(e.id) : "";
  const tax = e.tax ? `<div class="ex-tax">${escapeHTML(e.tax)}</div>` : "";

  const sequenceHtml = e.seq
    ? renderSequenceViewer(e.seq, e.feats || [])
    : "";

  return `
    <li class="ex-item">
      <div class="ex-head">
        <span class="ex-id">${idLink}</span>
        <span class="ex-label">${escapeHTML(e.label || "")}</span>
      </div>
      ${tax}
      <div class="ex-badges">${badges.join(" ")}</div>
      ${families}
      ${sequenceHtml}
    </li>`;
}

/* ------------------------------------------------------------------ */
/* Sequence viewer with overlap-aware feature colouring               */
/* ------------------------------------------------------------------ */

// Colour per trait axis. FUNCTION features aren't localised so they
// don't appear in the per-residue tracks.
const AXIS_COLORS = {
  SEQUENCE:            "#2563eb",  // blue
  STRUCTURE:           "#16a34a",  // green
  SEQUENCE_STRUCTURE:  "#a855f7",  // purple
};
const AXIS_LABELS = {
  SEQUENCE:            "sequence",
  STRUCTURE:           "structure",
  SEQUENCE_STRUCTURE:  "mixed",
};
const ROW_LENGTH = 60;

function renderSequenceViewer(seq, feats) {
  // Normalise feats: [start, end, ft_type, axis, note] tuples.
  // Filter to spans that intersect the sequence and have a localisable axis.
  const featObjs = (feats || [])
    .map(f => ({
      start: f[0], end: f[1], type: f[2], axis: f[3], note: f[4] || ""
    }))
    .filter(f =>
      f.axis && AXIS_COLORS[f.axis] &&
      f.start >= 1 && f.end >= f.start && f.start <= seq.length
    )
    .map(f => ({ ...f, end: Math.min(f.end, seq.length) }));

  // Assign each unique feature a stable colour + row index. Ordering:
  // by axis (SEQUENCE, MIXED, STRUCTURE), then by start position.
  const axisOrder = { SEQUENCE: 0, SEQUENCE_STRUCTURE: 1, STRUCTURE: 2 };
  featObjs.sort((a, b) => {
    const da = (axisOrder[a.axis] || 9) - (axisOrder[b.axis] || 9);
    if (da) return da;
    return a.start - b.start || a.end - b.end;
  });

  // Per-residue: which features touch this position?
  // residueFeats[i] = list of indices into featObjs.
  const residueFeats = new Array(seq.length);
  for (let i = 0; i < seq.length; i++) residueFeats[i] = [];
  featObjs.forEach((f, idx) => {
    for (let p = f.start; p <= f.end; p++) residueFeats[p - 1].push(idx);
  });

  const rowsHtml = [];
  for (let rowStart = 0; rowStart < seq.length; rowStart += ROW_LENGTH) {
    const rowEnd = Math.min(rowStart + ROW_LENGTH, seq.length);
    const cells = [];
    for (let i = rowStart; i < rowEnd; i++) {
      const idxs = residueFeats[i];
      let strips = "";
      if (idxs.length) {
        const h = (100 / idxs.length).toFixed(2);
        for (let k = 0; k < idxs.length; k++) {
          const f = featObjs[idxs[k]];
          const color = AXIS_COLORS[f.axis];
          const tip = `${f.type}${f.note ? ": " + f.note : ""} (${f.start}–${f.end})`;
          strips += `<span class="rstrip" style="background:${color};height:${h}%;" title="${escapeAttr(tip)}"></span>`;
        }
      }
      cells.push(
        `<span class="rcell"><span class="rletter">${escapeHTML(seq[i])}</span><span class="rstrips">${strips}</span></span>`
      );
    }
    const num = String(rowStart + 1).padStart(4, " ");
    rowsHtml.push(
      `<div class="srow"><span class="sn">${num}</span><span class="sr">${cells.join("")}</span></div>`
    );
  }

  const legend = renderLegend(featObjs);
  return `
    <details class="ex-seq" open>
      <summary>Sequence &amp; feature map (${seq.length} aa, ${featObjs.length} feature${featObjs.length === 1 ? "" : "s"})</summary>
      ${legend}
      <div class="sviewer">${rowsHtml.join("")}</div>
    </details>`;
}

function renderLegend(featObjs) {
  const byAxis = new Map();
  for (const f of featObjs) {
    if (!byAxis.has(f.axis)) byAxis.set(f.axis, new Map());
    const m = byAxis.get(f.axis);
    m.set(f.type, (m.get(f.type) || 0) + 1);
  }
  if (byAxis.size === 0) return "";
  const chips = [];
  for (const [axis, typeCounts] of byAxis) {
    const color = AXIS_COLORS[axis];
    const types = [...typeCounts.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([t, n]) => `${t}×${n}`)
      .join(", ");
    chips.push(
      `<span class="sleg"><span class="sswatch" style="background:${color}"></span> <b>${AXIS_LABELS[axis]}</b> — ${escapeHTML(types)}</span>`
    );
  }
  return `<div class="slegend">${chips.join("")}</div>`;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function curieLink(curie) {
  const idx = curie.indexOf(":");
  if (idx < 0) return `<span class="mono">${escapeHTML(curie)}</span>`;
  const prefix = curie.slice(0, idx);
  const local  = curie.slice(idx + 1);
  const base   = PREFIXES[prefix];
  if (base === null) {
    // Internal CURIE (proteintraitsmech:*) — try to resolve to a record in the index.
    if (ID_INDEX.has(curie)) {
      return `<a href="#record=${encodeURIComponent(curie)}">${escapeHTML(curie)}</a>`;
    }
    return `<span class="mono">${escapeHTML(curie)}</span>`;
  }
  if (!base) return `<span class="mono">${escapeHTML(curie)}</span>`;
  return `<a href="${base}${encodeURIComponent(local)}" target="_blank" rel="noopener">${escapeHTML(curie)}</a>`;
}

function escapeHTML(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function escapeAttr(s) { return escapeHTML(s); }

boot();
