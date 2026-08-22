(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.BrowseShards = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function values(selected, key) {
    const raw = (selected && selected[key]) || [];
    return raw instanceof Set ? [...raw] : raw;
  }

  function intersects(selectedValues, shardValues) {
    if (!selectedValues.length) return true;
    // Old manifests did not carry fine-grained coverage. Include them rather than
    // incorrectly returning an empty result; the next Pages build upgrades metadata.
    if (!Array.isArray(shardValues)) return true;
    return selectedValues.some(value => shardValues.includes(value));
  }

  function shardMatches(shard, selected) {
    return (
      intersects(values(selected, "axis"), shard.axis ? [shard.axis] : undefined) &&
      intersects(values(selected, "cat"), shard.categories) &&
      intersects(values(selected, "src"), shard.sources) &&
      intersects(values(selected, "sta"), shard.statuses)
    );
  }

  function selectShardFiles(manifest, selected, query) {
    const hasFacet = ["axis", "cat", "src", "sta"].some(
      key => values(selected, key).length > 0
    );
    if (!hasFacet && !query) return [];
    return manifest.filter(shard => shardMatches(shard, selected)).map(shard => shard.file);
  }

  function allShardFiles(manifest) {
    return manifest.map(shard => shard.file);
  }

  function createLoader(fetchFile, acceptRecords) {
    const loaded = new Set();
    const pending = new Map();

    function load(file) {
      if (loaded.has(file)) return Promise.resolve();
      if (!pending.has(file)) {
        const request = Promise.resolve()
          .then(() => fetchFile(file))
          .then(response => {
            if (!response || !response.ok) {
              const status = response && response.status ? `HTTP ${response.status}` : "no response";
              throw new Error(`${file}: ${status}`);
            }
            return response.json();
          })
          .then(records => {
            if (!Array.isArray(records)) throw new Error(`${file}: expected a JSON array`);
            acceptRecords(records, file);
            loaded.add(file);
          });
        const tracked = request.finally(() => pending.delete(file));
        pending.set(file, tracked);
      }
      return pending.get(file);
    }

    return {
      loaded,
      pending,
      load,
      loadMany: files => Promise.all([...files].map(load)),
    };
  }

  return { allShardFiles, createLoader, selectShardFiles, shardMatches };
});
