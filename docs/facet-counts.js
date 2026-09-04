(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.BrowseFacetCounts = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // Row layout in facets.json's `cube`: one row per observed combination,
  // [axis, cat, src, sta, count], positional in this order.
  const KEYS = ["axis", "cat", "src", "sta"];

  function values(selected, key) {
    const raw = (selected && selected[key]) || [];
    return raw instanceof Set ? [...raw] : raw;
  }

  // A cube that is absent or malformed is not something to paint partial counts
  // from: the caller falls back to global corpus counts and says so. Silently
  // rendering a half-read cube would put wrong numbers on screen with no signal.
  function isUsable(cube) {
    if (!Array.isArray(cube) || cube.length === 0) return false;
    return cube.every(
      row =>
        Array.isArray(row) &&
        row.length === KEYS.length + 1 &&
        typeof row[KEYS.length] === "number" &&
        row[KEYS.length] >= 0
    );
  }

  // Exact subset-aware counts for every facet value, under AND-across-groups /
  // OR-within-group semantics.
  //
  // The rule that makes a facet sidebar usable: **a group does not constrain its
  // own counts.** Counting group `g` under every selection *except* g's own is
  // what lets you see what adding a second value to g would yield, and what lets
  // an already-selected value keep a truthful count. Constraining g by itself
  // instead makes the numbers self-referential -- the selected value keeps its
  // count and every sibling in the group reads 0, so the group can never be
  // widened. That is the mutation the property test exists to catch.
  //
  // Returns null when the cube is unusable, never a partly populated object.
  function countsFor(cube, selected) {
    if (!isUsable(cube)) return null;
    const chosen = KEYS.map(key => {
      const list = values(selected, key);
      return list.length ? new Set(list) : null;
    });
    const out = {};
    for (const key of KEYS) out[key] = {};

    for (const row of cube) {
      const n = row[KEYS.length];
      for (let g = 0; g < KEYS.length; g++) {
        let ok = true;
        for (let i = 0; i < KEYS.length; i++) {
          if (i === g) continue;
          if (chosen[i] && !chosen[i].has(row[i])) { ok = false; break; }
        }
        if (!ok) continue;
        const value = row[g];
        // A null is "this record has no value in this group" (#641). It counts
        // toward the groups it does have, but has no checkbox of its own, so it
        // must not become a facet value. A selection never matches it either.
        if (value === null || value === undefined) continue;
        const bucket = out[KEYS[g]];
        bucket[value] = (bucket[value] || 0) + n;
      }
    }
    return out;
  }

  // Records matching every active group at once -- the count a result list will
  // show. Unlike countsFor, each group constrains itself here.
  function matchingTotal(cube, selected) {
    if (!isUsable(cube)) return null;
    const chosen = KEYS.map(key => {
      const list = values(selected, key);
      return list.length ? new Set(list) : null;
    });
    let total = 0;
    for (const row of cube) {
      let ok = true;
      for (let i = 0; i < KEYS.length; i++) {
        if (chosen[i] && !chosen[i].has(row[i])) { ok = false; break; }
      }
      if (ok) total += row[KEYS.length];
    }
    return total;
  }

  // Whether a facet value should be hidden from the sidebar.
  //
  // A zero-count value is a dead end: clicking it can only return "No records
  // match". But a *selected* value is never hidden, even at zero -- removing the
  // control that produced the current view strands the user with no way to undo
  // it. In global mode nothing is hidden, because a global zero says nothing
  // about the current selection.
  function isDeadEnd(count, subsetAware, checked) {
    return Boolean(subsetAware) && !checked && !(count > 0);
  }

  // The sidebar note, which must describe the mode actually in force. Claiming
  // subset-aware counts while painting global ones is the failure this replaces.
  // A free-text query narrows the result list but not the cube, so say so.
  function note(subsetAware, hasQuery) {
    if (!subsetAware) {
      return {
        short: "Counts are global corpus totals; record shards load on demand.",
        long: "Facet counts are global corpus totals. Selecting a value loads only "
            + "record shards that can match all active filters.",
      };
    }
    if (hasQuery) {
      return {
        short: "Counts reflect the active filters, not the search text.",
        long: "Facet counts reflect every active filter except the search box, which "
            + "narrows the result list only. A value's count excludes its own group, "
            + "so the group can still be widened.",
      };
    }
    return {
      short: "Counts reflect the active filters; empty values are hidden.",
      long: "Facet counts reflect all other active filters, so no value shown can "
          + "return an empty result. A value's count excludes its own group, so the "
          + "group can still be widened.",
    };
  }

  // Everything the sidebar needs, derived together so the three cannot disagree.
  //
  // The counts, the mode flag that decides what gets hidden, and the note that
  // tells the reader which counts they are looking at all come from one decision:
  // whether the cube was usable. Deriving them separately in the page is what
  // would let it hide values on global counts, or promise filter-aware counts
  // while painting corpus totals.
  function sidebarState(cube, selected, hasQuery, globalCounts) {
    const subset = countsFor(cube, selected);
    const subsetAware = subset !== null;
    return {
      counts: subset || globalCounts || {},
      subsetAware,
      note: note(subsetAware, Boolean(hasQuery)),
    };
  }

  return { KEYS, countsFor, isDeadEnd, isUsable, matchingTotal, note, sidebarState };
});
