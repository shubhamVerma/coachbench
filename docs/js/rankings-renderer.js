// Rankings renderer - Populate Overall Rankings table

const RankingsRenderer = {
  // Professional colorblind-friendly color palettes
  colors: {
    // Model colors (colorblind-friendly, high contrast)
    models: {
      claude: '#e67e22',      // Orange
      chatgpt: '#27ae60',     // Green
      gemini: '#2c5282',      // Deep Blue
      grok: '#6b7280',        // Gray
      mistral: '#8b5cf6'      // Purple
    },
    // Dimension colors (ColorBrewer-style categorical palette)
    dimensions: {
      evokesAwareness: '#3182bd',         // Blue
      activeListening: '#6baed6',          // Teal
      maintainsAgency: '#e6550d',          // Orange
      questionDepth: '#006d2c',             // Dark Green
      clientCentered: '#9467bd',           // Purple
      ethicalBoundaries: '#fd7e14'         // Yellow-Orange
    },
    // Coaching vs Advice pie colors (semantic meaning)
    coachingVsAdvice: {
      coaching: '#2c5282',     // Blue (positive)
      advice: '#e74c3c',       // Orange (needs attention)
      listening: '#6baed6',      // Teal
      other: '#9467bd'         // Purple
    },
    // Category chart colors
    categories: {
      career_transitions: '#3182bd',
      relationship_patterns: '#6baed6',
      identity_perception: '#2c5282',
      decision_making: '#e6550d',
      habit_formation: '#006d2c',
      motivation_resistance: '#9467bd'
    }
  },

  modelNames: {
    'claude_web_free': 'Claude Sonnet 4.5',
    'chatgpt_web_free': 'GPT-5.2 Chat',
    'gemini_web_free': 'Gemini 3 Flash',
    'grok_4_1_fast': 'Grok 4.1 Fast',
    'mistral_large': 'Mistral Large'
  },

  categoryNames: {
    'career_transitions': 'Career Transitions',
    'relationship_patterns': 'Relationship Patterns',
    'identity_perception': 'Identity Perception',
    'decision_making': 'Decision Making',
    'habit_formation': 'Habit Formation',
    'motivation_resistance': 'Motivation Resistance'
  },

  async initialize() {
    console.log('RankingsRenderer: Initializing...');

    try {
      const response = await fetch('data/summary.json');
      const summary = await response.json();

      this.renderRankingsTable(summary.overall_ranking);
      this.renderCharts(summary);

      // Load category analysis
      await this.loadCategoryAnalysis();

      console.log('RankingsRenderer: Initialized successfully');
    } catch (error) {
      console.error('RankingsRenderer: Failed to load summary:', error);
      const tbody = document.getElementById('rankings-table');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">Failed to load rankings</td></tr>';
      }
    }
  },

  async loadCategoryAnalysis() {
    try {
      const [evaluationsRes, scenariosRes] = await Promise.all([
        fetch('data/evaluations.json'),
        fetch('data/scenarios.json')
      ]);

      const evaluations = await evaluationsRes.json();
      const scenarios = await scenariosRes.json();

      // Create scenario ID to category mapping
      const scenarioCategoryMap = {};
      scenarios.forEach(s => {
        scenarioCategoryMap[s.id] = s.category;
      });

      // Calculate category averages
      const categoryData = this.calculateCategoryAverages(evaluations, scenarioCategoryMap);

      // Render category analysis
      this.renderCategoryTable(categoryData);
      this.renderCategoryInsights(categoryData);
      this.renderCategoryChart(categoryData);

      console.log('RankingsRenderer: Category analysis loaded');
    } catch (error) {
      console.error('RankingsRenderer: Failed to load category analysis:', error);
    }
  },

  calculateCategoryAverages(evaluations, scenarioCategoryMap) {
    // Group evaluations by category
    const categoryScores = {};
    const categoryCounts = {};

    evaluations.forEach(eval => {
      const category = scenarioCategoryMap[eval.scenario_id];
      if (!category) return;

      if (!categoryScores[category]) {
        categoryScores[category] = {
          claude_web_free: [],
          chatgpt_web_free: [],
          gemini_web_free: [],
          grok_4_1_fast: [],
          mistral_large: []
        };
        categoryCounts[category] = { claude_web_free: 0, chatgpt_web_free: 0, gemini_web_free: 0, grok_4_1_fast: 0, mistral_large: 0 };
      }

      if (categoryScores[category][eval.model]) {
        // Calculate total from dimension scores (total_score field removed)
        const totalScore = Object.values(eval.scores).reduce((a, b) => a + b, 0);
        categoryScores[category][eval.model].push(totalScore);
        categoryCounts[category][eval.model]++;
      }
    });

    // Calculate averages
    const categoryAverages = {};
    Object.keys(categoryScores).forEach(category => {
      categoryAverages[category] = {};
      let bestModel = null;
      let bestAvg = -1;

      ['claude_web_free', 'chatgpt_web_free', 'gemini_web_free', 'grok_4_1_fast', 'mistral_large'].forEach(model => {
        const scores = categoryScores[category][model];
        if (scores && scores.length > 0) {
          const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
          categoryAverages[category][model] = avg;
          if (avg > bestAvg) {
            bestAvg = avg;
            bestModel = model;
          }
        } else {
          categoryAverages[category][model] = null;
        }
      });

      categoryAverages[category].best = bestModel;
    });

    return categoryAverages;
  },

  renderCategoryTable(categoryData) {
    const tbody = document.getElementById('category-table-body');
    if (!tbody) return;

    let html = '';

    Object.keys(categoryData).forEach(category => {
      const data = categoryData[category];
      const categoryName = this.categoryNames[category] || category;

      const scores = [
        { model: 'claude_web_free', value: data.claude_web_free },
        { model: 'chatgpt_web_free', value: data.chatgpt_web_free },
        { model: 'gemini_web_free', value: data.gemini_web_free },
        { model: 'grok_4_1_fast', value: data.grok_4_1_fast },
        { model: 'mistral_large', value: data.mistral_large }
      ].filter(s => s.value !== null).sort((a, b) => b.value - a.value);

      const scoreDisplay = (value) => value !== null ? value.toFixed(1) : '-';
      const getClass = (modelVal, scores) => {
        if (modelVal === null) return '';
        if (modelVal === scores[0]?.value) return 'best';
        if (modelVal === scores[scores.length - 1]?.value) return 'worst';
        return 'second';
      };

      html += `
        <tr>
          <td>${categoryName}</td>
          <td class="score ${getClass(data.claude_web_free, scores)}">${scoreDisplay(data.claude_web_free)}</td>
          <td class="score ${getClass(data.chatgpt_web_free, scores)}">${scoreDisplay(data.chatgpt_web_free)}</td>
          <td class="score ${getClass(data.gemini_web_free, scores)}">${scoreDisplay(data.gemini_web_free)}</td>
          <td class="score ${getClass(data.grok_4_1_fast, scores)}">${scoreDisplay(data.grok_4_1_fast)}</td>
          <td class="score ${getClass(data.mistral_large, scores)}">${scoreDisplay(data.mistral_large)}</td>
        </tr>
      `;
    });

    tbody.innerHTML = html;
  },

  renderCategoryInsights(categoryData) {
    const container = document.getElementById('category-insights');
    if (!container) return;

    // Find patterns
    let modelBestCounts = { claude_web_free: 0, chatgpt_web_free: 0, gemini_web_free: 0, grok_4_1_fast: 0, mistral_large: 0 };
    let overallBest = null;
    let overallWorst = null;
    let overallBestScore = -1;
    let overallWorstScore = 100;

    Object.keys(categoryData).forEach(category => {
      const data = categoryData[category];
      if (data.best) modelBestCounts[data.best]++;

      const scores = [data.claude_web_free, data.chatgpt_web_free, data.gemini_web_free, data.grok_4_1_fast, data.mistral_large].filter(s => s !== null);
      if (scores.length > 0) {
        const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
        if (avgScore > overallBestScore) {
          overallBestScore = avgScore;
          overallBest = category;
        }
        if (avgScore < overallWorstScore) {
          overallWorstScore = avgScore;
          overallWorst = category;
        }
      }
    });

    const insights = [];

    // Best performer
    const bestModel = Object.entries(modelBestCounts).reduce((a, b) => a[1] > b[1] ? a : b);
    if (bestModel[1] > 0) {
      const modelLabel = this.modelNames[bestModel[0]];
      insights.push(`${modelLabel} performed best in ${bestModel[1]} out of 6 categories.`);
    }

    // Most challenging category
    if (overallWorst) {
      insights.push(`${this.categoryNames[overallWorst]} was the most challenging category for all models.`);
    }

    container.innerHTML = insights.map(i => `<p>• ${i}</p>`).join('');
  },

  renderCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryBreakdownChart');
    if (!ctx) return;

    const categories = Object.keys(categoryData).map(c => this.categoryNames[c]);
    const models = ['claude_web_free', 'chatgpt_web_free', 'gemini_web_free', 'grok_4_1_fast', 'mistral_large'];
    const modelLabels = ['Claude Sonnet 4.5', 'GPT-5.2 Chat', 'Gemini 3 Flash', 'Grok 4.1 Fast', 'Mistral Large'];
    const colors = [this.colors.models.claude, this.colors.models.chatgpt, this.colors.models.gemini, this.colors.models.grok, this.colors.models.mistral];

    const datasets = models.map((model, i) => ({
      label: modelLabels[i],
      data: Object.keys(categoryData).map(cat => categoryData[cat][model] || 0),
      backgroundColor: colors[i],
      borderColor: colors[i],
      borderWidth: 1
    }));

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: categories,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${context.raw.toFixed(1)} / 30`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 20,
            title: {
              display: true,
              text: 'Average Score'
            }
          },
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        }
      }
    });
  },

  renderRankingsTable(rankings) {
    const tbody = document.getElementById('rankings-table');
    if (!tbody) return;

    let html = '';

    rankings.forEach(ranking => {
      const modelName = this.modelNames[ranking.model] || ranking.model;
      const rankClass = ranking.rank === 1 ? 'rank-1' : '';

      // Display mean ± std if available, otherwise just mean
      let scoreDisplay = ranking.total_score.toFixed(1);
      if (ranking.total_std !== undefined) {
        scoreDisplay = `${ranking.total_score.toFixed(1)} ± ${ranking.total_std.toFixed(2)}`;
      }

      html += `
        <tr class="${rankClass}">
          <td>${ranking.rank}</td>
          <td>${modelName}</td>
          <td><strong>${scoreDisplay}</strong></td>
        </tr>
      `;
    });

    tbody.innerHTML = html;
  },

  renderCharts(summary) {
    this.renderOverallScoresChart(summary);
    this.renderDimensionRadarChart(summary);
    // Category chart is rendered by loadCategoryAnalysis() after data is loaded
  },

  renderOverallScoresChart(summary) {
    const ctx = document.getElementById('overallScoresChart');
    if (!ctx) return;

    const labels = summary.overall_ranking.map(r => this.modelNames[r.model]);
    const scores = summary.overall_ranking.map(r => r.total_score);
    const stds = summary.overall_ranking.map(r => r.total_std);
    const colors = summary.overall_ranking.map(r => {
      const colorMap = { claude_web_free: 'claude', chatgpt_web_free: 'chatgpt', gemini_web_free: 'gemini', grok_4_1_fast: 'grok', mistral_large: 'mistral' };
      return this.colors.models[colorMap[r.model]];
    });

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Overall Score (out of 30)',
          data: scores,
          backgroundColor: colors,
          borderColor: colors,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const std = stds[context.dataIndex];
                if (std !== undefined) {
                  return `Score: ${context.raw.toFixed(1)} ± ${std.toFixed(2)} / 30`;
                }
                return `Score: ${context.raw.toFixed(1)} / 30`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 18
          }
        }
      }
    });
  },

  renderDimensionRadarChart(summary) {
    const ctx = document.getElementById('dimensionRadarChart');
    if (!ctx) return;

    const dimensions = [
      'evokes_awareness',
      'active_listening_indicators',
      'maintains_client_agency',
      'question_depth_progression',
      'client_centered_communication',
      'ethical_boundaries'
    ];

    const dimensionLabels = dimensions.map(d => 
      d.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );

    const modelColors = {
      'claude_web_free': 'rgba(230, 126, 34, 0.2)',
      'chatgpt_web_free': 'rgba(39, 174, 96, 0.2)',
      'gemini_web_free': 'rgba(44, 82, 130, 0.2)',
      'grok_4_1_fast': 'rgba(107, 114, 128, 0.2)',
      'mistral_large': 'rgba(139, 92, 246, 0.2)'
    };

    const modelBorderColors = {
      'claude_web_free': 'rgba(230, 126, 34, 1)',
      'chatgpt_web_free': 'rgba(39, 174, 96, 1)',
      'gemini_web_free': 'rgba(44, 82, 130, 1)',
      'grok_4_1_fast': 'rgba(107, 114, 128, 1)',
      'mistral_large': 'rgba(139, 92, 246, 1)'
    };

    const datasets = summary.overall_ranking.map(r => ({
      label: this.modelNames[r.model],
      data: dimensions.map(d => r[d]),
      backgroundColor: modelColors[r.model],
      borderColor: modelBorderColors[r.model],
      borderWidth: 2,
      pointBackgroundColor: modelBorderColors[r.model]
    }));

    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: dimensionLabels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 4,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
  },

  renderDimensionHeatmap(summary) {
    const container = document.getElementById('dimensionHeatmap');
    if (!container) return;

    const dimensions = [
      'evokes_awareness',
      'active_listening_indicators',
      'maintains_client_agency',
      'question_depth_progression',
      'client_centered_communication',
      'ethical_boundaries'
    ];

    const modelOrder = summary.overall_ranking.map(r => r.model);
    const modelLabels = modelOrder.map(m => this.modelNames[m]);
    const dimensionLabels = dimensions.map(d => 
      d.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );

    // Find max for color scaling
    const allScores = [];
    modelOrder.forEach(model => {
      const r = summary.overall_ranking.find(item => item.model === model);
      dimensions.forEach(d => allScores.push(r[d]));
    });
    const maxScore = Math.max(...allScores);

    let html = '<table class="heatmap-table"><thead><tr><th></th>';
    modelLabels.forEach(label => {
      html += `<th>${label}</th>`;
    });
    html += '</tr></thead><tbody>';

    dimensions.forEach((dim, i) => {
      html += `<tr><td class="heatmap-label">${dimensionLabels[i]}</td>`;
      modelOrder.forEach(model => {
        const r = summary.overall_ranking.find(item => item.model === model);
        const score = r[dim];
        const intensity = score / maxScore;
        // Color gradient from light to dark based on score
        const rVal = Math.round(230 - intensity * 180);
        const gVal = Math.round(230 - intensity * 180);
        const bVal = Math.round(255 - intensity * 220);
        const bgColor = `rgb(${rVal}, ${gVal}, ${bVal})`;
        const textColor = intensity > 0.6 ? '#fff' : '#333';
        html += `<td style="background-color: ${bgColor}; color: ${textColor}">${score.toFixed(2)}</td>`;
      });
      html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
  }
};

window.RankingsRenderer = RankingsRenderer;
