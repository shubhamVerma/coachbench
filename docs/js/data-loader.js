// Data loader - Load responses index and group by category

let allScenarios = {};
let categoryScenarios = {};
let allEvaluations = [];

const DataLoader = {
  loadResponsesIndex() {
    console.log('DataLoader: Loading responses index...');
    return fetch('data/responses_index.json')
      .then(res => res.json())
      .then(index => {
        allScenarios = index.scenarios;
        this.groupByCategory();
        console.log('DataLoader: Responses index loaded:', Object.keys(allScenarios).length, 'scenarios');
        return index;
      })
      .catch(error => {
        console.error('DataLoader: Error loading responses index:', error);
        throw error;
      });
  },

  loadEvaluationsIndex() {
    console.log('DataLoader: Loading evaluations index...');
    return fetch('data/evaluations.json')
      .then(res => res.json())
      .then(evaluations => {
        allEvaluations = evaluations;
        console.log('DataLoader: Evaluations loaded:', evaluations.length, 'evaluations');
        return evaluations;
      })
      .catch(error => {
        console.error('DataLoader: Error loading evaluations:', error);
        throw error;
      });
  },

  groupByCategory() {
    categoryScenarios = {};
    allScenarios.forEach(scenario => {
      const category = scenario.category;
      if (!categoryScenarios[category]) {
        categoryScenarios[category] = [];
      }
      categoryScenarios[category].push(scenario);
    });
    console.log('DataLoader: Scenarios grouped by category:', Object.keys(categoryScenarios));
  },

  loadScenario(scenarioId) {
    const scenario = allScenarios.find(s => s.id === scenarioId);
    if (!scenario) {
      console.error('DataLoader: Scenario not found:', scenarioId);
      throw new Error(`Scenario ${scenarioId} not found`);
    }
    return scenario;
  },

  navigateScenario(direction) {
    const category = window.TabManager.getCurrentCategory();
    const scenarios = categoryScenarios[category];
    const currentIndex = window.TabManager.getCurrentIndex();

    const newIndex = currentIndex + direction;
    if (newIndex >= 0 && newIndex < scenarios.length) {
      const nextScenario = scenarios[newIndex];
      return nextScenario.id;
    }
    return null;
  },

  getScenariosByCategory(category) {
    return categoryScenarios[category] || [];
  },

  getEvaluation(scenarioId, model) {
    return allEvaluations.find(e => e.scenario_id === scenarioId && e.model === model);
  },

  async loadResponsesForScenario(scenarioId) {
    console.log('DataLoader: Loading responses for scenario:', scenarioId);

    const promises = [
      fetch(`data/responses/claude_web_free/${scenarioId}.json`)
        .then(res => {
          if (!res.ok) throw new Error('Not found');
          return res.json();
        })
        .catch(err => ({ error: true, message: 'Response not available' })),

      fetch(`data/responses/chatgpt_web_free/${scenarioId}.json`)
        .then(res => {
          if (!res.ok) throw new Error('Not found');
          return res.json();
        })
        .catch(err => ({ error: true, message: 'Response not available' })),

      fetch(`data/responses/gemini_web_free/${scenarioId}.json`)
        .then(res => {
          if (!res.ok) throw new Error('Not found');
          return res.json();
        })
        .catch(err => ({ error: true, message: 'Response not available' })),

      fetch(`data/responses/grok_4_1_fast/${scenarioId}.json`)
        .then(res => {
          if (!res.ok) throw new Error('Not found');
          return res.json();
        })
        .catch(err => ({ error: true, message: 'Response not available' })),

      fetch(`data/responses/mistral_large/${scenarioId}.json`)
        .then(res => {
          if (!res.ok) throw new Error('Not found');
          return res.json();
        })
        .catch(err => ({ error: true, message: 'Response not available' }))
    ];

    const responses = await Promise.all(promises);

    console.log('DataLoader: Responses loaded for', scenarioId, responses.map(r => r.error ? 'error' : 'ok'));
    return responses;
  }
};

// Expose for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataLoader;
}

window.DataLoader = DataLoader;
