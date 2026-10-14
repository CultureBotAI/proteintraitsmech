/* Shared description derived from map identities and the current browser index. */
window.MapCoverage = {
  describe(data) {
    const number = value => value.toLocaleString();
    return `${number(data.current_plotted)} of ${number(data.browser_total)} current records plotted; ` +
      `${number(data.not_plotted)} current records are outside this embedding snapshot.` +
      (data.outside_current ? ` The snapshot also contains ${number(data.outside_current)} older identifiers outside the current browser.` : "") +
      ` ${data.scope} ` + (data.embedding_date ? `Embedding date: ${data.embedding_date}.` : "Embedding date was not recorded.");
  }
};
