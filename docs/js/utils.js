// Utility functions

const Utils = {
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  formatTime(seconds) {
    return seconds.toFixed(1) + 's';
  },

  formatTokens(tokens) {
    return tokens || 'N/A';
  }
};

// Expose for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Utils;
}

window.Utils = Utils;
