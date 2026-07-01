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
  valuesets:     "https://linkml.io/valuesets/elements/",
  proteintraitsmech: null, // internal — no external resolver
};

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

async function boot() {
  const results = document.getElementById("results");
  try {
    const [recRes, facRes] = await Promise.all([
      fetch("data/records.json"),
      fetch("data/facets.json"),
    ]);
    if (!recRes.ok) throw new Error("records.json " + recRes.status);
    if (!facRes.ok) throw new Error("facets.json "  + facRes.status);
    RECORDS = await recRes.json();
    FACETS = await facRes.json();
  } catch (e) {
    results.innerHTML = `<div class="empty">Failed to load records: ${e.message}</div>`;
    return;
  }
  ID_INDEX = new Map(RECORDS.map(r => [r.id, r]));

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

function route() {
  const h = window.location.hash;
  if (h.startsWith("#record=")) {
    const id = decodeURIComponent(h.slice("#record=".length));
    const rec = ID_INDEX.get(id);
    if (rec) return renderDetail(rec);
    return renderNotFound(id);
  }
  renderList();
}

/* ------------------------------------------------------------------ */
/* Facet sidebar                                                      */
/* ------------------------------------------------------------------ */

function renderFacetSidebar() {
  const scroll = document.getElementById("facet-scroll");
  const parts = [];
  for (const grp of FACET_GROUPS) {
    const counts = FACETS.counts[grp.key] || {};
    const rows = Object.entries(counts).map(([val, n]) => `
      <label class="facet-item">
        <input type="checkbox" data-facet="${grp.key}" value="${escapeAttr(val)}" />
        <span class="name" title="${escapeAttr(val)}">${escapeHTML(val)}</span>
        <span class="count">${n.toLocaleString()}</span>
      </label>`).join("");
    parts.push(`
      <div class="facet-group">
        <h3>${escapeHTML(grp.label)}</h3>
        ${rows}
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
      if (el.checked) SELECTED[facet].add(el.value);
      else            SELECTED[facet].delete(el.value);
      FILTERED_CACHE = null;
      PAGE = 0;
      updateActiveCount();
      renderList();
    });
  });
  document.getElementById("clear-facets").addEventListener("click", () => {
    for (const k of Object.keys(SELECTED)) SELECTED[k].clear();
    document.querySelectorAll("#facet-scroll input[type=checkbox]").forEach(el => (el.checked = false));
    FILTERED_CACHE = null;
    PAGE = 0;
    updateActiveCount();
    renderList();
  });
  updateActiveCount();
}

function updateActiveCount() {
  const n = Object.values(SELECTED).reduce((a, s) => a + s.size, 0);
  const el = document.getElementById("active-count");
  el.textContent = n ? `${n} active` : "";
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

function renderList() {
  const results = document.getElementById("results");
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

  const cards = slice.map(r => `
    <a class="card" href="#record=${encodeURIComponent(r.id)}">
      <div class="cid">${escapeHTML(r.id)}</div>
      <h3>${escapeHTML(r.label)}</h3>
      <p>${escapeHTML(r.def || "")}</p>
      <div class="pills">
        ${r.axis ? `<span class="pill axis">${escapeHTML(r.axis)}</span>` : ""}
        ${r.cat  ? `<span class="pill">${escapeHTML(r.cat)}</span>`      : ""}
        ${r.src  ? `<span class="pill src">${escapeHTML(r.src)}</span>`  : ""}
        ${r.sta  ? `<span class="pill sta">${escapeHTML(r.sta)}</span>`  : ""}
      </div>
    </a>`).join("");

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

function renderDetail(r) {
  const results = document.getElementById("results");
  const rawYamlLink = REPO_RAW + r.path;
  const xrefsHtml = (r.xr || []).length
    ? `<ul class="xref-list">
        ${r.xr.map(x => `<li>${curieLink(x)}</li>`).join("")}
       </ul>`
    : "<em>none</em>";

  const patternRow = r.pat
    ? row("Sequence pattern", `<dd class="pre">${escapeHTML(r.pat)}</dd>`, true)
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
        ${patternRow}
        ${row("Cross-references", `<dd>${xrefsHtml}</dd>`, true)}
        ${row("Source file", `<dd><a href="${escapeAttr(rawYamlLink)}" target="_blank" rel="noopener"><code>${escapeHTML(r.path)}</code></a></dd>`, true)}
      </dl>
    </div>`;
  document.title = r.label + " — ProteinTraitsMech";
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
