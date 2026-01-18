# LLM Benchmark Research Page

Tufte-inspired HTML page displaying LLM Reflective Questioning Benchmark results.

## Local Development

To view the page locally:

```bash
cd web
python3 -m http.server 8080
```

Then open your browser to: http://localhost:8080

Or open the file directly: `index.html`

## Deployment to Vercel

The directory is ready for Vercel deployment. It includes:

- `vercel.json` - Configuration for static site hosting
- `index.html` - Main page
- `css/tufte.css` - Tufte-inspired styling
- `data/scenarios.json` - Copy of scenarios data
- `data/summary.json` - Copy of summary data

To deploy:

```bash
vercel login
cd web
vercel
```

## Files

- `index.html` - Main research page with all sections
- `css/tufte.css` - Tufte-inspired design system
- `vercel.json` - Vercel configuration
- `data/summary.json` - Benchmark results data
- `data/scenarios.json` - Input scenarios data

## Design Principles

Based on Edward Tufte's principles:

- **High data-ink ratio** - Minimal decoration, maximum data
- **Clean typography** - Libre Baskerville serif with Inter sans-serif
- **Whitespace** - Generous margins and spacing
- **No chart junk** - Clean tables and visualizations
- **Integration** - Seamless blend of text, tables, and data

## Sections

1. Title & Author
2. Abstract
3. Experiment Setup
4. Data Setup (Interactive - Category tabs with scenario tables)
5. Results Summary (with interactive visualizations)
6. Interactive Evaluations (placeholder - coming soon)
7. Conclusion
8. About Author

## Interactive Features

### Interactive Evaluations Section
- **Category tabs**: 6 tabs to filter scenarios by category
- **Scenario navigation**: Previous/Next buttons to browse through scenarios
- **Side-by-side comparison**: 3 columns showing all models simultaneously
  - Claude Sonnet 4.5 (blue header)
  - ChatGPT 4o Mini (bronze header)
  - Gemini 3 Flash (green header)
- **Model metrics**: Response time and token count displayed in header
- **Chat UI**: Traditional chat bubble styling with markdown rendering
  - Model messages: White background with border
  - User messages: Centered gray background, spans all columns (inline)
- **Turn display**: All 3 turns shown simultaneously (implicit ordering)
- **Formatting preserved**: Markdown (bold, bullets, line breaks) rendered correctly
- **Responsive**: Horizontal scroll on mobile for side-by-side comparison

### Interactive Features

### Data Setup Section
- **Category tabs**: 6 tabs for different scenario categories
  - Career Transitions (7 scenarios)
  - Relationship Patterns (9 scenarios)
  - Identity Perception (7 scenarios)
  - Decision Making (7 scenarios)
  - Habit Formation (6 scenarios)
  - Motivation Resistance (6 scenarios)
- **Scenario tables**: Each category shows scenarios in a clean table
  - ID column: Scenario identifier
  - Prompt column: Full user problem statement (text wraps)
  - Description column: Brief summary
  - Action column: Copy button for prompt text
- **Copy functionality**: Click "Copy" to copy scenario prompt to clipboard

### Interactive Evaluations Section
### Interactive Evaluations Section
- **Category tabs**: 6 tabs to filter scenarios by category
- **Scenario navigation**: Previous/Next buttons to browse through scenarios
- **Side-by-side comparison**: 3 columns showing all models simultaneously
  - Claude Sonnet 4.5 (blue header)
  - ChatGPT 4o Mini (bronze header)
  - Gemini 3 Flash (green header)
- **Model metrics**: Response time and token count displayed in header
- **Chat UI**: Traditional chat bubble styling with markdown rendering
  - Model messages: White background with border
  - User messages: Centered gray background, spans all columns (inline)
- **Turn display**: All 3 turns shown simultaneously (implicit ordering)
- **Formatting preserved**: Markdown (bold, bullets, line breaks) rendered correctly
- **Responsive**: Horizontal scroll on mobile for side-by-side comparison

### Results Summary Visualizations
- **Chart.js integration**: 4 interactive charts
  1. Overall Scores (bar chart)
  2. Dimension Breakdown (radar chart)
  3. Coaching vs Advice (stacked bar chart)
  4. Statistical Significance (bar chart with error bars)
- **Dynamic data loading**: All data loaded from JSON
- **Color palette**: Sophisticated colors (navy blue, bronze, forest green)
- **Responsive**: Works on desktop and mobile

