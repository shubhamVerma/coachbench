// Tab manager - Handle category tab switching

const TabManager = {
  currentCategory: null,

  setupTabHandlers() {
    console.log('TabManager: Setting up tab handlers...');

    const tabs = document.querySelectorAll('.category-tab');

    if (tabs.length === 0) {
      console.error('TabManager: No category tabs found!');
      return;
    }

    // Set initial category from first tab if not set
    if (!this.currentCategory) {
      const firstTab = tabs[0];
      if (firstTab) {
        this.currentCategory = firstTab.dataset.category;
      }
    }

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        console.log('TabManager: Tab clicked:', tab.dataset.category);
        this.switchCategory(tab.dataset.category);
      });
    });

    console.log('TabManager: Tab handlers setup complete');
  },

  switchCategory(category) {
    console.log('TabManager: Switching to category:', category);
    this.currentCategory = category;

    // Update all category tabs (both old sidebar and new inline)
    const allTabs = document.querySelectorAll('.category-tab, #eval-category-tabs .tab');
    allTabs.forEach(t => {
      t.classList.toggle('active', t.dataset.category === category);
    });

    // Load first scenario of this category
    const scenarios = window.DataLoader.getScenariosByCategory(category);
    if (scenarios && scenarios.length > 0) {
      window.DataLoader.loadResponsesForScenario(scenarios[0].id)
        .then(responses => {
          window.ChatRenderer.renderChatComparison(scenarios[0], responses);
        })
        .catch(error => {
          console.error('Failed to load responses:', error);
        });
    }
  },

  getCurrentCategory() {
    const activeTab = document.querySelector('.category-tab.active');
    return activeTab ? activeTab.dataset.category : null;
  },

  getCurrentIndex() {
    const category = this.getCurrentCategory();
    if (!category) return -1;

    const scenarios = window.DataLoader.getScenariosByCategory(category);
    const currentScenario = window.ChatRenderer.getCurrentScenario();
    if (!currentScenario) return -1;

    return scenarios.findIndex(s => s.id === currentScenario.id);
  },

  getCurrentTotal() {
    const category = this.getCurrentCategory();
    if (!category) return 0;

    const scenarios = window.DataLoader.getScenariosByCategory(category);
    return scenarios.length;
  },

  getScenariosByCategory(category) {
    return window.DataLoader.getScenariosByCategory(category);
  }
};

// Expose for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TabManager;
}

window.TabManager = TabManager;
