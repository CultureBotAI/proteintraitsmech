/* ProteinTraitsMech client-side faceted browser.
 *
 * Data source: filter-aware docs/data/records.*.json shards. The landing page
 * fetches no record shard; active facets determine the smallest useful subset.
 *
 * Views:
 *   #                    → paged, faceted list
 *   #record=<identifier> → single-record detail
 */

const REPO_RAW = "https://github.com/CultureBotAI/proteintraitsmech/blob/main/";
const PAGE_SIZE = 60;

// CURIE prefix → resolver URL. Missing prefixes fall through to a
// readable accession when no verified entry route is available.
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
  SCOP:          null, // SCOPe sunids are not the newer SCOP identifier system.
  PDB:           "https://www.rcsb.org/structure/",
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
let LAST_RESULTS_HASH = "#";
let LIST_RENDER_GENERATION = 0;

/* ------------------------------------------------------------------ */
/* Boot                                                               */
/* ------------------------------------------------------------------ */

// Records are partitioned by axis/category. facets.json keeps global counts and a
// manifest describing each shard's category/source/status coverage, so narrow filters
// fetch only intersecting shards. A free-text query with no facets still searches all
// shards; a dedicated search index would be needed to avoid that explicit tradeoff.
let SHARD_MANIFEST = [];
const SHARD_LOADER = BrowseShards.createLoader(
  file => fetch("data/" + file),
  part => {
    for (const rec of part) {
      RECORDS.push(rec); ID_INDEX.set(rec.id, rec);
    }
    FILTERED_CACHE = null;
  }
);
const LOADED_SHARDS = SHARD_LOADER.loaded;
const loadShards = files => SHARD_LOADER.loadMany(files);
async function exactRecord(id) {
  if (ID_INDEX.has(id)) return ID_INDEX.get(id);
  const lookup = FACETS.lookup;
  if (!lookup || lookup.algorithm !== "sha256-first16-mod") throw new Error("Record lookup unavailable");
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(id)));
  const bucket = ((digest[0] << 8) | digest[1]) % lookup.buckets;
  const entries = await fetchJSON(`data/${lookup.directory}/${String(bucket).padStart(4, "0")}.json`);
  const file = Object.prototype.hasOwnProperty.call(entries, id) ? entries[id] : null;
  if (!file) return null;
  if (!SHARD_MANIFEST.some(shard => shard.file === file)) throw new Error("Invalid record lookup");
  await loadShards([file]);
  const record = ID_INDEX.get(id);
  if (!record) throw new Error("Record index is temporarily inconsistent");
  return record;
}
async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("Request failed");
  const data = url.endsWith(".json.gz")
    ? await new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).json()
    : await response.json();
  if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("Invalid response");
  return data;
}

function neededShards() {
  return BrowseShards.selectShardFiles(SHARD_MANIFEST, SELECTED, QUERY);
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
  SHARD_MANIFEST = (FACETS.shards && FACETS.shards.length)
    ? FACETS.shards : [{ file: "records.json" }];

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
      // A small accession bucket identifies just the necessary record shard.
      document.getElementById("results").innerHTML =
        `<div class="empty">Loading record…</div>`;
      try {
        rec = await exactRecord(id);
        if (window.location.hash !== h) return;
      } catch (error) {
        if (window.location.hash !== h) return;
        return renderShardLoadFailure(error);
      }
      rec = ID_INDEX.get(id);
    }
    if (rec) return renderDetail(rec);
    return renderNotFound(id);
  }
  LAST_RESULTS_HASH = h || "#";
  // Facet deep-links (e.g. "#cat=STRUCT_FOLD", "#axis=SEQUENCE&src=PROSITE").
  // Query, facets and page are restored from the complete results URL.
  const params = parseHashParams(h);
  const state = new URLSearchParams(h.replace(/^#/, ""));
  const query = state.get("q") || "";
  QUERY = query.trim().toLowerCase();
  document.getElementById("q").value = query;
  applyHashFacets(params);
  PAGE = Math.max(0, Number.parseInt(state.get("page"), 10) || 0);
  syncResultsHash();
  renderList();
}

// Keep the current history entry aligned with visible filters before any record link
// adds a new entry. Both the local Back link and the browser Back restore it exactly.
function syncResultsHash() {
  const params = new URLSearchParams();
  for (const [key, values] of Object.entries(SELECTED)) {
    for (const value of values) params.append(key, value);
  }
  const query = document.getElementById("q").value.trim();
  if (query) params.set("q", query);
  if (PAGE) params.set("page", String(PAGE));
  LAST_RESULTS_HASH = "#" + params.toString();
  history.replaceState(null, "", LAST_RESULTS_HASH);
}

// Parse a facet deep-link hash into per-group value lists. Repeated keys
// accumulate, e.g. "#cat=A&cat=B" → { cat: ["A", "B"], … }.
function parseHashParams(h) {
  const out = { axis: [], src: [], cat: [], sta: [] };
  for (const [key, value] of new URLSearchParams((h || "").replace(/^#/, ""))) {
    if (Object.prototype.hasOwnProperty.call(out, key)) out[key].push(value);
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
      syncResultsHash();
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
    syncResultsHash();
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
  if (btn) btn.textContent = open
    ? "Show less"
    : `Show all (${group.querySelectorAll(".facet-item:not(.is-empty)").length})`;
}

function updateActiveCount() {
  const n = Object.values(SELECTED).reduce((a, s) => a + s.size, 0);
  const el = document.getElementById("active-count");
  el.textContent = n ? `${n} active` : "";
}

// Counts come from the build-time contingency cube in facets.json, which holds one
// row per observed (axis, cat, src, sta) combination -- so a selection's counts are
// an exact sum over 112-ish rows, independent of which shards happen to be loaded.
// This is deliberately neither of the two things it replaced: counts derived from
// the partially loaded RECORDS array hid valid choices after a narrow query (#544),
// and always-global counts offered dozens of clickable dead ends (#638).
//
// Without a usable cube -- an older facets.json, a corpus past MAX_CUBE_ROWS -- the
// global tallies still render, and the sidebar note says which of the two you are
// reading. It must never claim subset-aware counts while painting global ones.
function refreshFacetCounts() {
  const state = BrowseFacetCounts.sidebarState(
    FACETS.cube, SELECTED, QUERY, FACETS.counts);

  document.querySelectorAll("#facet-scroll .facet-group").forEach(group => {
    const key = group.dataset.key;
    const c = state.counts[key] || {};
    let shown = 0;
    group.querySelectorAll(".facet-item").forEach(item => {
      const el = item.querySelector("input[type=checkbox]");
      if (!el) return;
      const n = c[el.value] || 0;
      const cnt = item.querySelector(".count");
      if (cnt) cnt.textContent = n.toLocaleString();
      const empty = BrowseFacetCounts.isDeadEnd(n, state.subsetAware, el.checked);
      item.classList.toggle("is-empty", empty);
      if (!empty) shown++;
    });
    const btn = group.querySelector(".facet-toggle");
    // Count what "Show all" would actually reveal, not what is in the DOM.
    if (btn && !group.classList.contains("expanded")) btn.textContent = `Show all (${shown})`;
  });

  describeFacetCounts(state.note);
}

// Paint the note that sidebarState derived alongside the counts, so the wording
// and the numbers can never describe different modes.
function describeFacetCounts(words) {
  const text = document.getElementById("facet-info-text");
  const icon = document.getElementById("facet-info-icon");
  if (!text) return;
  text.textContent = words.short;
  if (icon) icon.title = words.long;
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
      syncResultsHash();
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
      (r.def && r.def.toLowerCase().includes(qs)) ||
      (r.syn && r.syn.some(name => name.toLowerCase().includes(qs))) ||
      (r.chem && r.chem.some(n => n.toLowerCase().includes(qs))) ||
      (r.chemx && r.chemx.some(n => n.toLowerCase().includes(qs)))
    );
  }
  FILTERED_CACHE = out;
  return out;
}

/* ------------------------------------------------------------------ */
/* List view                                                          */
/* ------------------------------------------------------------------ */

async function renderList() {
  const generation = ++LIST_RENDER_GENERATION;
  const hash = window.location.hash;
  const isCurrent = () => generation === LIST_RENDER_GENERATION && window.location.hash === hash;
  const results = document.getElementById("results");
  const need = neededShards();
  const hasSelection = QUERY || Object.values(SELECTED).some(values => values.size > 0);

  // Landing: nothing selected and no query — don't bulk-load the corpus; the
  // facet panel (global counts) is already shown, so prompt the user to pick.
  if (need.length === 0 && !hasSelection) {
    const axisCounts = (FACETS.counts && FACETS.counts.axis) || {};
    const cards = Object.entries(axisCounts).sort((a, b) => b[1] - a[1])
      .map(([a, n]) => `<a class="axis-card" href="#axis=${encodeURIComponent(a)}">
        <strong>${n.toLocaleString()}</strong><span>${escapeHTML(a)}</span></a>`).join("");
    results.innerHTML = `<div class="landing">
      <p><strong>${FACETS.total.toLocaleString()} trait records.</strong>
      Pick an axis, category or source on the left — or search — to load records.
      (Records are loaded from filter-aware shards on demand.)</p>
      <div class="axis-cards">${cards}</div></div>`;
    return;
  }

  // Load only shards intersecting every active facet; show a spinner while fetching.
  const missing = need.filter(file => !LOADED_SHARDS.has(file));
  if (missing.length) {
    results.innerHTML = `<div class="empty">Loading ${missing.length} shard${missing.length === 1 ? "" : "s"}…</div>`;
    try {
      await loadShards(need);
    } catch (error) {
      if (!isCurrent()) return;
      return renderShardLoadFailure(error);
    }
    if (!isCurrent()) return;
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
  syncResultsHash();
  renderList();
  window.scrollTo({ top: 0, behavior: "smooth" });
};

function renderShardLoadFailure(error) {
  document.getElementById("results").innerHTML =
    `<div class="empty" role="alert">Records could not be loaded. Please try again. ` +
    `<button onclick="_retryShardLoad()">Retry</button></div>`;
}

window._retryShardLoad = function () { route(); };

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
    try { await loadDetail(r); } catch (_) { /* Show lean metadata with an explicit warning below. */ }
    if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  }
  let graphsFailed = false;
  try { await loadGraphs(r); } catch (_) { graphsFailed = true; }
  if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  await loadNeighbors(r);
  if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  // Labels for every id rendered below (`<CURIE> — <label>`); one cached fetch.
  let labelsFailed = false;
  try { await loadLabels(); } catch (_) { labelsFailed = true; }
  if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
  // Semantic neighbors: [neighbor_id, cosine] → internal record links.
  const relatedHtml = (r._nb || []).length
    ? `<ul class="xref-list">
        ${r._nb.map(([nid, sc]) =>
          `<li><a href="#record=${encodeURIComponent(nid)}">${escapeHTML(nid)}</a>${labelSuffix(nid)}`
          + ` <span class="map-src">${(sc).toFixed(2)}</span></li>`).join("")}
       </ul>`
    : "";
  const rawYamlLink = REPO_RAW + (r.path || "");
  const xrefsHtml = (r.xr || []).length
    ? `<ul class="xref-list">
        ${r.xr.map(x => `<li>${curieLink(x)}</li>`).join("")}
       </ul>`
    : (r._dl ? "<em>none recorded</em>" : "<em>Unavailable until record details load.</em>");
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

  const parents = [...new Map((r.pt || []).map(parent => {
    const pair = Array.isArray(parent) ? parent : [parent, "biolink:subclass_of"];
    return [JSON.stringify([pair[0], pair[1] || "biolink:subclass_of"]), parent];
  })).values()];
  const parentHtml = parents.length
    ? `<ul class="xref-list">
        ${parents.map(x => {
          const [cur, pred] = Array.isArray(x) ? x : [x, null];
          const rel = pred && pred !== "biolink:subclass_of"
            ? ` <span class="map-src">${escapeHTML(pred.replace("biolink:", ""))}</span>` : "";
          return `<li>${localTraitLink(cur)}${rel}</li>`;
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
        <a href="${escapeAttr(LAST_RESULTS_HASH)}">← back to results</a>
      </div>
      <h1>${escapeHTML(r.label)}</h1>
      <div class="cid">${escapeHTML(r.id)}</div>
      <p>${sourceEntry(r.id)}</p>
      ${!r._dl ? '<p role="alert">Record details could not be loaded. Evidence, examples and other supplemental fields are unavailable. <button onclick="_retrySupplement()">Retry details</button></p>' : ""}
      ${graphsFailed ? '<p role="alert">Causal graphs could not be loaded. <button onclick="_retrySupplement()">Retry graphs</button>, or use the repository YAML source below.</p>' : ""}
      ${labelsFailed ? '<p role="alert">Reference labels could not be loaded. Identifiers remain available. <button onclick="_retrySupplement()">Retry labels</button></p>' : ""}
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
        ${(r.syn || []).length ? row("Synonyms", `<dd>${r.syn.map(escapeHTML).join("; ")}</dd>`, true) : ""}
        ${ssRow}
        ${geoRow}
        ${patternRow}
        ${residueRow}
        ${parentRow}
        ${examplesRow}
        ${(r.defs || []).length ? row("Definitions", `<dd>${
          r.defs.map(d => `<b>${escapeHTML((d[0] || "").toLowerCase())}</b>: ${escapeHTML(d[1] || "")}${d[2] ? ` <span class="map-src">${escapeHTML(d[2])}</span>` : ""}`).join("<br>")
        }</dd>`, true) : ""}
        ${r.escope ? row("Evolutionary scope", `<dd>${
          [r.escope.taxon_scope && escapeHTML(r.escope.taxon_scope) + (r.escope.taxon_rank ? ` (${escapeHTML(r.escope.taxon_rank)})` : ""),
           (r.escope.min_prevalence != null || r.escope.max_prevalence != null) && `prevalence ${r.escope.min_prevalence ?? "?"}–${r.escope.max_prevalence ?? "?"}`,
           r.escope.definition_method && escapeHTML(r.escope.definition_method),
           r.escope.conservation_metric && escapeHTML(r.escope.conservation_metric),
           r.escope.orthology_basis && escapeHTML(r.escope.orthology_basis)].filter(Boolean).join(" · ") || "—"
        }</dd>`, true) : ""}
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
        ${(r.ev || []).length ? row(`Evidence (${r.ev.length})`, `<dd>${
          r.ev.map(e => `${curieLink(e[0])}${e[1] ? ` <span class="map-src">${escapeHTML(e[1])}</span>` : ""}`).join("<br>")
        }</dd>`, true) : ""}
        ${row("Detection methods", `<dd id="method-list">${METHODS ? (methodsHtml(r) || "<em>—</em>") : "<em>loading…</em>"}</dd>`, true)}
        ${(r.cg || []).length ? row("Causal graphs", `<dd><p>Asserted relations and their recorded evidence:</p>${structuredData(r.cg)}</dd>`, true) : ""}
        ${(r.history || []).length ? row("Curation history", `<dd>${structuredData(r.history)}</dd>`, true) : ""}
        ${r.path ? row("Repository YAML source", `<dd><a href="${escapeAttr(rawYamlLink)}" target="_blank" rel="noopener"><code>${escapeHTML(r.path)}</code></a></dd>`, true) : ""}
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
  }).catch(() => {
    if (window.location.hash !== "#record=" + encodeURIComponent(r.id)) return;
    const dd = document.getElementById("method-list");
    if (dd) dd.innerHTML = '<span role="alert">Detection methods could not be loaded.</span> <button onclick="_retrySupplement()">Retry methods</button>';
  });
}

window._retrySupplement = () => route();

// Render all source fields, including nested edge evidence, without inventing relations.
function structuredData(value) {
  if (Array.isArray(value)) return `<ol>${value.map(item => `<li>${structuredData(item)}</li>`).join("")}</ol>`;
  if (value && typeof value === "object") return `<dl class="structured-data">${Object.entries(value).map(([key, item]) =>
    `<div><dt>${escapeHTML(key.replace(/_/g, " "))}</dt><dd>${structuredData(item)}</dd></div>`).join("")}</dl>`;
  return escapeHTML(value);
}
function localTraitLink(id) {
  const known = ID_INDEX.has(id) || (LABELS && Object.prototype.hasOwnProperty.call(LABELS, id));
  return known ? `<a href="#record=${encodeURIComponent(id)}">${escapeHTML(id)}</a>${labelSuffix(id)}` : curieLink(id);
}
function sourceUrl(curie) {
  const index = (curie || "").indexOf(":");
  if (index < 0) return null;
  const prefix = curie.slice(0, index), local = curie.slice(index + 1);
  if (prefix === "PDB" && !/^[0-9][A-Za-z0-9]{3}$/.test(local) && !/^pdb_[A-Za-z0-9]{8}$/.test(local)) return null;
  return PREFIXES[prefix] ? PREFIXES[prefix] + encodeURIComponent(local) : null;
}
function sourceEntry(id) {
  const url = sourceUrl(id);
  return url ? `<a href="${escapeAttr(url)}" target="_blank" rel="noopener">Source database entry: ${escapeHTML(id)} ↗</a>`
    : `<span class="map-src">Source entry link unavailable for ${escapeHTML(id)}${id.startsWith("SCOP:") ? " (legacy SCOPe identifier)" : ""}.</span>`;
}

// Methods catalogue (data/methods.json): how a trait is detected/predicted,
// keyed by_source + by_category. Loaded once on first detail view, cached.
let METHODS = null;
let METHODS_PROMISE = null;
function loadMethods() {
  if (!METHODS_PROMISE) {
    METHODS_PROMISE = fetchJSON("data/methods.json")
      .then(j => { METHODS = j; return j; })
      .catch(error => { METHODS_PROMISE = null; throw error; });
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

// id → label sidecar (data/labels.json): every corpus record's label, so any id
// the detail view renders shows as `<CURIE> — <label>`. ~4 MB gzipped, fetched
// once on first detail view and cached (independent of lazy record-shard loading).
let LABELS = null;
let LABELS_PROMISE = null;
function loadLabels() {
  if (!LABELS_PROMISE) {
    LABELS_PROMISE = fetchJSON("data/labels.json")
      .then(j => { LABELS = j; return j; })
      .catch(error => { LABELS_PROMISE = null; throw error; });
  }
  return LABELS_PROMISE;
}
// Resolve an id/CURIE to its label — from the labels map, the loaded record
// index, or the ChEBI sidecar. "" when no label is known.
function labelFor(curie) {
  if (LABELS && LABELS[curie]) return LABELS[curie];
  const rec = ID_INDEX.get(curie);
  if (rec && rec.label && rec.label !== curie) return rec.label;
  if (curie.startsWith("CHEBI:") && CHEBI && CHEBI[curie]) {
    const n = CHEBI[curie];
    return (typeof n === "string" ? n : (n && n.name)) || "";
  }
  return "";
}
// " — <label>" HTML suffix for an id, or "" when no label is known.
function labelSuffix(curie) {
  const l = labelFor(curie);
  return l ? ` <span class="curie-label">— ${escapeHTML(l)}</span>` : "";
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
      fetchJSON("data/" + file)
        .catch(error => { DETAIL_CACHE.delete(file); throw error; }));
  }
  return DETAIL_CACHE.get(file);
}

// Merge a record's detail sidecar into the record object (once). Degrades
// gracefully: on any failure the lean fields (label, short def, pills) still
// render.
async function loadDetail(r) {
  if (r._dl) return;
  if (!r.df) { r._dl = true; return; }
  const bucket = await fetchDetailBucket(r.df);
  const d = bucket && bucket[r.id];
  if (!d || typeof d !== "object" || Array.isArray(d)) {
    DETAIL_CACHE.delete(r.df);
    throw new Error("Record detail unavailable");
  }
  Object.assign(r, d);
  r._dl = true;
}

async function loadGraphs(r) {
  if (!r.gf || r.cg !== undefined) return;
  const bucket = await fetchDetailBucket(r.gf);
  if (!bucket || !Array.isArray(bucket[r.id])) {
    DETAIL_CACHE.delete(r.gf);
    throw new Error("Graph content unavailable");
  }
  r.cg = bucket[r.id];
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
  // Profile-matrix picks are ranked suggestions, not curated archetypes — say so.
  else if (e.src === "SWISSPROT_PROFILE") badges.push(`<span class="pill src">Swiss-Prot profile · suggested</span>`);

  const families = (e.fams || []).length
    ? `<div class="ex-families">${e.fams.map(curieLink).join(" ")}</div>`
    : "";
  const idLink = e.id ? curieLink(e.id) : "";
  const tax = e.tax ? `<div class="ex-tax">${escapeHTML(e.tax)}</div>` : "";

  const sequenceHtml = e.seq
    ? renderSequenceViewer(e.seq, e.feats || [])
    : "";
  const sequenceReference = e.seq && e.seqsrc === "ProteinReference"
    ? `<div class="ex-seq-reference">Release-pinned UniProt sequence
        ${e.rel ? ` · ${escapeHTML(e.rel)}` : ""}
        ${e.sv ? ` · sequence version ${escapeHTML(String(e.sv))}` : ""}
        ${e.seqsha ? `<br>SHA-256: <code>${escapeHTML(e.seqsha)}</code>` : ""}</div>`
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
      ${sequenceReference}
      ${sequenceHtml}
    </li>`;
}

/* ------------------------------------------------------------------ */
/* Sequence viewer with overlap-aware feature colouring               */
/* ------------------------------------------------------------------ */

// Colour per trait axis. FUNCTION features aren't localised so they
// don't appear in the per-residue tracks.
// Categorical hues in fixed order, validated with the dataviz skill's checker:
// worst adjacent CVD ΔE 9.1 light / 8.4 dark (target >=8). The previous set
// failed — blue vs purple ΔE 2.6 under protanopia, green vs teal ΔE 10.8 even
// with normal vision (issue #5). Adjacent-pair is the right test: an axis hue
// is always rendered beside its label, so identity is never colour-alone.
const AXIS_COLORS_LIGHT = {SEQUENCE: "#2a78d6", STRUCTURE: "#eb6834", FUNCTION: "#1baf7a", SEQUENCE_STRUCTURE: "#eda100", EVOLUTION: "#e87ba4", OTHER: "#8a8a85"};
const AXIS_COLORS_DARK  = {SEQUENCE: "#3987e5", STRUCTURE: "#d95926", FUNCTION: "#199e70", SEQUENCE_STRUCTURE: "#c98500", EVOLUTION: "#d55181", OTHER: "#9a9a95"};
const AXIS_COLORS = new Proxy({}, {get: (_t, k) => {
  const dark = document.documentElement.dataset.theme === "dark"
    || (!document.documentElement.dataset.theme
        && window.matchMedia("(prefers-color-scheme: dark)").matches);
  return (dark ? AXIS_COLORS_DARK : AXIS_COLORS_LIGHT)[k];
}});


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
  const summary = featObjs.length
    ? `Sequence &amp; feature map (${seq.length} aa, ${featObjs.length} feature${featObjs.length === 1 ? "" : "s"})`
    : `Sequence (${seq.length} aa; ${(feats || []).length ? "no displayable feature annotations" : "no feature annotations stored"})`;
  return `
    <details class="ex-seq" open>
      <summary>${summary}</summary>
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
  const suffix = labelSuffix(curie);   // " — <label>" when a label is known
  if (base === null) {
    // Internal CURIE (proteintraitsmech:*) — try to resolve to a record in the index.
    if (ID_INDEX.has(curie) || (LABELS && LABELS[curie])) {
      return `<a href="#record=${encodeURIComponent(curie)}">${escapeHTML(curie)}</a>${suffix}`;
    }
    return `<span class="mono">${escapeHTML(curie)}</span>${suffix}${prefix === "SCOP" ? ' <span class="map-src">(legacy SCOPe source entry unavailable)</span>' : ""}`;
  }
  const url = sourceUrl(curie);
  if (!url) return `<span class="mono">${escapeHTML(curie)}</span>${suffix}`;
  return `<a href="${escapeAttr(url)}" target="_blank" rel="noopener">${escapeHTML(curie)}</a>${suffix}`;
}

function escapeHTML(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function escapeAttr(s) { return escapeHTML(s); }

boot();
