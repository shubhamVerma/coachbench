// Chat renderer - Single model view with evaluation details side panel

const ChatRenderer = {
  currentScenario: null,
  currentResponses: null,
  currentModel: 'claude',
  evaluationHidden: false,

  modelConfig: {
    claude: { key: 'claude', name: 'Claude', color: '#2c5282', shortName: 'Claude' },
    chatgpt: { key: 'chatgpt', name: 'GPT-5.2 Chat', color: '#d62728', shortName: 'GPT-5.2' },
    gemini: { key: 'gemini', name: 'Gemini', color: '#e74c3c', shortName: 'Gemini' }
  },

  getScenariosByCategory(category) {
    return window.DataLoader.getScenariosByCategory(category);
  },

  initialize() {
    console.log('ChatRenderer: Initialized');

    // Setup event delegation for all interactive elements
    document.addEventListener('click', (e) => {
      const categoryTab = e.target.closest('.category-tab');
      if (categoryTab) {
        const newCategory = categoryTab.dataset.category;
        if (newCategory !== window.TabManager.getCurrentCategory()) {
          window.TabManager.switchCategory(newCategory);
        }
        return;
      }

      const modelTab = e.target.closest('.model-tab');
      if (modelTab) {
        this.switchModel(modelTab.dataset.model);
        return;
      }

      const prevBtn = e.target.closest('#prev-scenario');
      if (prevBtn && !prevBtn.disabled) {
        this.navigateScenario(-1);
        return;
      }

      const nextBtn = e.target.closest('#next-scenario');
      if (nextBtn && !nextBtn.disabled) {
        this.navigateScenario(1);
        return;
      }

      const scoresBtn = e.target.closest('#toggle-scores');
      if (scoresBtn) {
        if (this.evaluationHidden) {
          this.showChat();
        } else {
          this.showScores();
        }
        return;
      }
    });
  },

  showChat() {
    const chatLayout = document.querySelector('.chat-detail-layout');
    const toggleBtn = document.getElementById('toggle-scores');

    if (chatLayout) {
      chatLayout.classList.remove('evaluation-hidden');
      this.evaluationHidden = false;

      if (toggleBtn) {
        toggleBtn.classList.remove('active');
        toggleBtn.innerHTML = '<span class="btn-icon">📊</span><span>Hide Evaluation</span>';
      }
    }
  },

  showScores() {
    const chatLayout = document.querySelector('.chat-detail-layout');
    const toggleBtn = document.getElementById('toggle-scores');

    if (chatLayout) {
      chatLayout.classList.add('evaluation-hidden');
      this.evaluationHidden = true;

      if (toggleBtn) {
        toggleBtn.classList.add('active');
        toggleBtn.innerHTML = '<span class="btn-icon">📊</span><span>Show Evaluation</span>';
      }
    }
  },

  switchModel(modelKey) {
    this.currentModel = modelKey;

    // Update tab active state
    document.querySelectorAll('.model-tab').forEach(tab => {
      const isActive = tab.dataset.model === modelKey;
      tab.classList.toggle('active', isActive);
      tab.style.setProperty('--model-color', this.modelConfig[modelKey].color);
    });

    // Re-render with new model
    if (this.currentScenario && this.currentResponses) {
      this.renderChatComparison(this.currentScenario, this.currentResponses);
    }
  },

  async navigateScenario(direction) {
    const nextId = window.DataLoader.navigateScenario(direction);
    if (nextId) {
      const scenario = window.DataLoader.loadScenario(nextId);
      const responses = await window.DataLoader.loadResponsesForScenario(nextId);
      this.renderChatComparison(scenario, responses);

      // Update counter
      const category = window.TabManager.getCurrentCategory();
      const index = window.TabManager.getCurrentIndex();
      const total = window.TabManager.getCurrentTotal();
      this.updateNavControls(category, index, total);
    }
  },

  getShortScenarioName(scenario) {
    // Extract short name from prompt - first 40-50 chars
    const prompt = scenario.prompt || '';
    const words = prompt.split(' ');
    let shortName = words[0];

    for (let i = 1; i < words.length && shortName.length < 45; i++) {
      shortName += ' ' + words[i];
    }

    if (prompt.length > 45) {
      shortName += '...';
    }

    return shortName;
  },

  getCategoryDisplayName(category) {
    const names = {
      'career_transitions': 'Career Transitions',
      'relationship_patterns': 'Relationship Patterns',
      'identity_perception': 'Identity Perception',
      'decision_making': 'Decision Making',
      'habit_formation': 'Habit Formation',
      'motivation_resistance': 'Motivation Resistance'
    };
    return names[category] || category;
  },

  getScenarioNumber(scenarioId) {
    // Extract number from scenario_id (e.g., "career_transitions_007" -> "007")
    const parts = scenarioId.split('_');
    return parts[parts.length - 1].padStart(3, '0');
  },

  renderChatComparison(scenario, responses) {
    console.log('ChatRenderer: Rendering chat comparison for scenario:', scenario.id);

    this.currentScenario = scenario;
    this.currentResponses = responses;

    const container = document.getElementById('eval-content');
    if (!container) {
      console.error('ChatRenderer: eval-content container not found');
      return;
    }

    const category = window.TabManager.getCurrentCategory();
    const scenarios = window.DataLoader.getScenariosByCategory(category);
    const currentIndex = scenarios.findIndex(s => s.id === scenario.id);
    const total = scenarios.length;

    const modelData = this.getModelData(this.currentModel, responses);
    const modelScores = this.getModelScores(responses, scenario.id);

    // Determine winner
    const scores = [
      { key: 'claude', score: modelScores.claude },
      { key: 'chatgpt', score: modelScores.chatgpt },
      { key: 'gemini', score: modelScores.gemini }
    ].filter(m => m.score !== 'N/A');

    const winner = scores.reduce((max, m) => {
      const maxScore = parseFloat(max.score) || 0;
      const mScore = parseFloat(m.score) || 0;
      return mScore > maxScore ? m : max;
    }, scores[0]);

    const shortName = this.getShortScenarioName(scenario);
    const categoryName = this.getCategoryDisplayName(category);
    const scenarioNumber = this.getScenarioNumber(scenario.id);

    const toggleButtonText = this.evaluationHidden
      ? '<span class="btn-icon">📊</span><span>Show Evaluation</span>'
      : '<span class="btn-icon">📊</span><span>Hide Evaluation</span>';
    const toggleButtonActive = this.evaluationHidden ? 'active' : '';

    const categories = [
      { key: 'career_transitions', label: 'Career Transitions' },
      { key: 'relationship_patterns', label: 'Relationships' },
      { key: 'identity_perception', label: 'Identity' },
      { key: 'decision_making', label: 'Decision' },
      { key: 'habit_formation', label: 'Habit' },
      { key: 'motivation_resistance', label: 'Motivation' }
    ];

    let html = `
      <div class="category-tabs-row">
        ${categories.map(cat => `
          <button class="category-tab ${category === cat.key ? 'active' : ''}" data-category="${cat.key}">
            ${cat.label}
          </button>
        `).join('')}
      </div>

      <div class="combined-controls">
        <div class="control-group navigation-group">
          <button class="nav-button prev" id="prev-scenario" aria-label="Previous scenario">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </button>

          <div class="scenario-nav-info">
            <span class="scenario-label">${currentIndex + 1} of ${total}</span>
            <span class="scenario-full-name" title="${scenario.prompt}">${shortName}</span>
          </div>

          <button class="nav-button next" id="next-scenario" aria-label="Next scenario">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </button>
        </div>

        <div class="control-group models-row">
          <div class="model-tabs-container">
            ${['claude', 'chatgpt', 'gemini'].map(key => {
              const config = this.modelConfig[key];
              const score = modelScores[key] || 'N/A';
              const isWinner = winner && winner.key === key;
              const isActive = this.currentModel === key;

              return `
                <button class="model-tab ${isActive ? 'active' : ''} ${isWinner ? 'winner' : ''}"
                        data-model="${key}"
                        style="--model-color: ${config.color}"
                        aria-label="Select ${config.name}"
                        aria-pressed="${isActive}">
                  <span class="model-name">
                    ${config.name}
                    ${isWinner ? '🏆' : ''}
                  </span>
                  <span class="model-score">${score}</span>
                </button>
              `;
            }).join('')}
          </div>

          <button class="toggle-single-btn ${toggleButtonActive}" id="toggle-scores" aria-label="Toggle scores view">
            ${toggleButtonText}
          </button>
        </div>
      </div>

      <div class="chat-detail-layout ${this.evaluationHidden ? 'evaluation-hidden' : ''}">
        <div class="chat-column">
          <div class="chat-messages" id="chat-messages"></div>

          <div class="model-footer">
          </div>
        </div>

        <div class="evaluation-column">
          <div class="evaluation-header">Evaluation Details</div>
          <div id="evaluation-details"></div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    // Render chat messages
    if (modelData.error) {
      const messagesContainer = document.getElementById('chat-messages');
      const errorMsg = document.createElement('div');
      errorMsg.className = 'message-error';
      errorMsg.textContent = modelData.message || 'Response not available';
      messagesContainer.appendChild(errorMsg);
    } else {
      this.renderMessages(modelData);
      // Load and render evaluation
      this.loadAndRenderEvaluation();
    }

    this.updateNavControls(category, currentIndex, total);
  },

  getModelData(modelKey, responses) {
    const responseMap = {
      claude: responses[0],
      chatgpt: responses[1],
      gemini: responses[2]
    };

    return responseMap[modelKey] || { error: true, message: 'Response not available' };
  },

  getModelScores(responses, scenarioId) {
    const modelKeyMap = {
      'claude': 'claude_web_free',
      'chatgpt': 'chatgpt_web_free',
      'gemini': 'gemini_web_free'
    };

    const scores = {};
    Object.keys(modelKeyMap).forEach(modelKey => {
      const fullKey = modelKeyMap[modelKey];
      const evaluation = window.DataLoader.getEvaluation(scenarioId, fullKey);
      if (evaluation) {
        // Calculate total from dimension scores (total_score field removed)
        const scoreValues = Object.values(evaluation.scores);
        const totalScore = scoreValues.reduce((a, b) => a + b, 0);
        scores[modelKey] = `${totalScore.toFixed(1)}`;
      } else {
        scores[modelKey] = 'N/A';
      }
    });

    return scores;
  },

  renderMessages(data) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    // Add prompt as first message (user/right-aligned)
    this.renderPromptMessage(container, this.currentScenario.prompt);

    // Turn 1 (model/left-aligned)
    this.renderMessage(container, data.turn1?.content || 'No content', data.turn1);

    // User response (right-aligned)
    this.renderUserMessage(container, data.turn2_user_response || 'No user response recorded');

    // Turn 2 (model/left-aligned)
    this.renderMessage(container, data.turn2?.content || 'No content', data.turn2);

    // User response (right-aligned)
    this.renderUserMessage(container, data.turn3_user_response || 'No user response recorded');

    // Turn 3 (model/left-aligned)
    this.renderMessage(container, data.turn3?.content || 'No content', data.turn3);
  },

  renderPromptMessage(container, prompt) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-user';

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = 'Scenario Prompt';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = marked.parse(prompt);

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
  },

  renderMessage(container, content, metadata) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-model';

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = 'AI Response';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = marked.parse(content);

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
  },

  renderUserMessage(container, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-user';

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = 'User Response';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
  },

  async loadAndRenderEvaluation() {
    const modelKeyMap = {
      'claude': 'claude_web_free',
      'chatgpt': 'chatgpt_web_free',
      'gemini': 'gemini_web_free'
    };

    const modelKey = modelKeyMap[this.currentModel];
    const evaluationData = window.DataLoader.getEvaluation(this.currentScenario.id, modelKey);

    if (evaluationData) {
      this.renderEvaluationDetails(evaluationData);
    } else {
      this.renderEvaluationDetails({ evaluation: null });
    }
  },

  renderEvaluationDetails(data) {
    const container = document.getElementById('evaluation-details');
    if (!container) return;

    if (!data || !data.scores) {
      container.innerHTML = '<p class="no-evaluation">No evaluation data available for this scenario</p>';
      return;
    }

    const scores = data.scores;
    const dimensions = [
      { key: 'evokes_awareness', label: 'Evokes Awareness', score: scores.evokes_awareness },
      { key: 'active_listening_indicators', label: 'Active Listening', score: scores.active_listening_indicators },
      { key: 'maintains_client_agency', label: 'Maintains Agency', score: scores.maintains_client_agency },
      { key: 'question_depth_progression', label: 'Question Depth', score: scores.question_depth_progression },
      { key: 'client_centered_communication', label: 'Client-Centered', score: scores.client_centered_communication },
      { key: 'ethical_boundaries', label: 'Ethical Boundaries', score: scores.ethical_boundaries }
    ];

    let html = `
      <div class="dimensions-list">
    `;

    dimensions.forEach(dim => {
      const score = dim.score || 0;
      const percent = (score / 5) * 100;
      const barColor = percent >= 60 ? '#4ECDC4' : percent >= 40 ? '#FFEAA7' : '#FF6B6B';
      const comment = this.getDimensionComment(dim.key, score);
      const stars = this.getStars(score, barColor);

      html += `
        <div class="dimension-card">
          <div class="dimension-header">
            <span class="dimension-label" title="${comment}">${dim.label}</span>
            <span class="dimension-stars">${stars}</span>
          </div>
        </div>
      `;
    });

    html += `
      </div>

      <div class="moments-breakdown">
        <span class="moments-label">Coaching Moments Distribution</span>
        <div class="moments-chart-container">
          <canvas id="momentsPieChart"></canvas>
        </div>
      </div>

      <div class="notes-section">
        <h4>Qualitative Assessment</h4>
        <p>${data.qualitative_assessment || 'No assessment available.'}</p>
      </div>

      ${data.strong_examples && data.strong_examples.length > 0 ? `
      <div class="examples-section">
        <h4>Strong Examples</h4>
        <ul>
          ${data.strong_examples.map(ex => `<li>${this.escapeHtml(ex)}</li>`).join('')}
        </ul>
      </div>
      ` : ''}

      ${data.weak_examples && data.weak_examples.length > 0 ? `
      <div class="examples-section">
        <h4>Weak Examples</h4>
        <ul>
          ${data.weak_examples.map(ex => `<li>${this.escapeHtml(ex)}</li>`).join('')}
        </ul>
      </div>
      ` : ''}
    `;

    container.innerHTML = html;

    this.renderMomentsPieChart(data.coaching_vs_advice_moments);
  },

  renderMomentsPieChart(moments) {
    if (!moments) return;

    const total = (moments.stayed_in_inquiry || 0) +
                 (moments.slipped_to_advice || 0) +
                 (moments.slipped_to_therapy || 0) +
                 (moments.slipped_to_consulting || 0);

    if (total === 0) return;

    const ctx = document.getElementById('momentsPieChart');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Coaching', 'Advice', 'Therapy', 'Consulting'],
        datasets: [{
          data: [
            moments.stayed_in_inquiry || 0,
            moments.slipped_to_advice || 0,
            moments.slipped_to_therapy || 0,
            moments.slipped_to_consulting || 0
          ],
          backgroundColor: ['#4ECDC4', '#FF6B6B', '#FFEAA7', '#DDA0DD'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              font: {
                family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                size: 11
              },
              padding: 8,
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const value = context.raw;
                const percent = ((value / total) * 100).toFixed(1);
                return `${context.label}: ${value} (${percent}%)`;
              }
            }
          }
        }
      }
    });
  },

  getDimensionComment(dimension, score) {
    const comments = {
      evokes_awareness: {
        high: 'Excellent at helping client discover insights',
        mid: 'Some awareness evocation present',
        low: 'Limited insight facilitation'
      },
      active_listening_indicators: {
        high: 'Strong reflective and clarifying statements',
        mid: 'Some listening indicators present',
        low: 'Minimal reflective language'
      },
      maintains_client_agency: {
        high: 'Respects client autonomy throughout',
        mid: 'Some directive moments present',
        low: 'Frequently gives advice or solutions'
      },
      question_depth_progression: {
        high: 'Moves effectively to deeper inquiry',
        mid: 'Some depth progression visible',
        low: 'Remains at surface level'
      },
      client_centered_communication: {
        high: 'Consistently client-focused',
        mid: 'Mix of client and self focus',
        low: 'Model-centric approach'
      },
      ethical_boundaries: {
        high: 'Appropriate scope maintained',
        mid: 'Generally appropriate boundaries',
        low: 'Boundary concerns noted'
      }
    };

    const type = score >= 4 ? 'high' : score >= 2 ? 'mid' : 'low';
    return comments[dimension]?.[type] || '';
  },

  getStars(score, color) {
    const fullStars = Math.floor(score);
    const hasHalf = score % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

    let stars = '';
    for (let i = 0; i < fullStars; i++) {
      stars += `<span class="star" style="color: ${color}">★</span>`;
    }
    if (hasHalf) {
      stars += `<span class="star half" style="color: ${color}">★</span>`;
    }
    for (let i = 0; i < emptyStars; i++) {
      stars += `<span class="star empty">★</span>`;
    }

    return stars;
  },

  updateNavControls(category, index, total) {
    const counter = document.getElementById('scenario-counter');
    const prevBtn = document.getElementById('prev-scenario');
    const nextBtn = document.getElementById('next-scenario');

    if (prevBtn) prevBtn.disabled = index === 0;
    if (nextBtn) nextBtn.disabled = index === total - 1;
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  getCurrentScenario() {
    return this.currentScenario;
  },

  getCurrentResponses() {
    return this.currentResponses;
  }
};

window.ChatRenderer = ChatRenderer;
