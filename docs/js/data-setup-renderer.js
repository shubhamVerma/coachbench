// Data setup renderer - Display scenarios in table format with copy functionality

const DataSetupRenderer = {
  allScenarios: [],
  categoryScenarios: {},

  async initialize() {
    console.log('DataSetupRenderer: Initializing...');

    try {
      const response = await fetch('data/scenarios.json');
      this.allScenarios = await response.json();
      this.groupByCategory();
      this.renderCategoryTabs();
      this.renderCategoryContent('career_transitions');
      this.setupTabHandlers();

      console.log('DataSetupRenderer: Initialized with', this.allScenarios.length, 'scenarios');
    } catch (error) {
      console.error('DataSetupRenderer: Failed to load scenarios:', error);
      const container = document.getElementById('data-setup-content');
      if (container) {
        container.innerHTML = '<p style="text-align: center; color: var(--accent-color);">Failed to load scenarios</p>';
      }
    }
  },

  groupByCategory() {
    this.categoryScenarios = {};
    this.allScenarios.forEach(scenario => {
      const category = scenario.category;
      if (!this.categoryScenarios[category]) {
        this.categoryScenarios[category] = [];
      }
      this.categoryScenarios[category].push(scenario);
    });
  },

  renderCategoryTabs() {
    const container = document.getElementById('data-setup-tabs');
    if (!container) return;

    const categories = [
      { key: 'career_transitions', label: 'Career Transitions' },
      { key: 'relationship_patterns', label: 'Relationships' },
      { key: 'identity_perception', label: 'Identity' },
      { key: 'decision_making', label: 'Decision' },
      { key: 'habit_formation', label: 'Habit' },
      { key: 'motivation_resistance', label: 'Motivation' }
    ];

    let html = '<div class="category-tabs-row">';
    categories.forEach(cat => {
      const activeClass = cat.key === 'career_transitions' ? 'active' : '';
      html += `<button class="category-tab ${activeClass}" data-category="${cat.key}">${cat.label}</button>`;
    });
    html += '</div>';

    container.innerHTML = html;
  },

  setupTabHandlers() {
    const tabs = document.querySelectorAll('#data-setup-tabs .category-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const category = tab.dataset.category;
        this.renderCategoryContent(category);
      });
    });
  },

  renderCategoryContent(category) {
    const container = document.getElementById('data-setup-content');
    if (!container) return;

    const scenarios = this.categoryScenarios[category] || [];

    if (scenarios.length === 0) {
      container.innerHTML = '<p style="text-align: center; padding: 2rem;">No scenarios available</p>';
      return;
    }

    let html = `<table class="data-setup-table">
      <thead>
        <tr>
          <th>Scenario</th>
          <th>Prompt</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
    `;

    scenarios.forEach(scenario => {
      const scenarioTitle = scenario.description.split(' - ')[1] || scenario.description;
      html += `
        <tr>
          <td class="scenario-cell">${scenarioTitle}</td>
          <td class="prompt-cell">
            <div class="prompt-preview">${this.escapeHtml(scenario.prompt)}</div>
          </td>
          <td class="action-cell">
            <button class="copy-button" onclick="window.DataSetupRenderer.copyPrompt('${scenario.id}')">Copy Prompt</button>
          </td>
        </tr>
      `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
  },

  copyPrompt(scenarioId) {
    const scenario = this.allScenarios.find(s => s.id === scenarioId);
    if (!scenario) return;

    navigator.clipboard.writeText(scenario.prompt).then(() => {
      const btn = document.querySelector(`button[onclick*="${scenarioId}"]`);
      if (btn) {
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.classList.add('copied');

        setTimeout(() => {
          btn.textContent = originalText;
          btn.classList.remove('copied');
        }, 2000);
      }
    }).catch(err => {
      console.error('Failed to copy prompt:', err);
      alert('Failed to copy prompt to clipboard');
    });
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};

window.DataSetupRenderer = DataSetupRenderer;
