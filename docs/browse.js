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

  const residueRow = r.rs
    ? row(`Residue sequence (${r.rs.length} aa)`,
          `<dd class="pre">${escapeHTML(r.rs)}</dd>`, true)
    : "";

  const parentHtml = (r.pt || []).length
    ? `<ul class="xref-list">
        ${r.pt.map(x => `<li>${curieLink(x)}</li>`).join("")}
       </ul>`
    : "";
  const parentRow = parentHtml
    ? row("Parent traits", `<dd>${parentHtml}</dd>`, true)
    : "";

  const examples = r.ex || [];
  const examplesHtml = examples.length
    ? `<ul class="ex-list">${examples.map(renderExample).join("")}</ul>`
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
        ${patternRow}
        ${residueRow}
        ${parentRow}
        ${examplesRow}
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

function renderExample(e) {
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
