/* Pure overlay operations, shared by the map UI and offline tests. */
(function (root) {
  "use strict";
  const value = (series, id) => {
    const row = series && series.values[id];
    return row && row.status === "OK" && Number.isFinite(row.value) ? row.value : null;
  };
  const passes = (series, id, min, max, availableOnly) => {
    if (!series) return true;
    const v = value(series, id);
    if (v === null) return !availableOnly && min === null && max === null;
    return (min === null || v >= min) && (max === null || v <= max);
  };
  const color = (series, id) => {
    const v = value(series, id);
    if (v === null) return "#999999";
    const span = series.maximum - series.minimum;
    const t = span > 0 ? Math.max(0, Math.min(1, (v - series.minimum) / span)) : 0.5;
    // Monotone light-to-dark blue, accompanied by numerical bounds and CSV values.
    const a = [198, 219, 239], b = [8, 48, 107];
    return "rgb(" + a.map((v, i) => Math.round(v + t * (b[i] - v))).join(",") + ")";
  };
  const api = {value, passes, color};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.PTMBiophysical = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
