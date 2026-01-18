# CoachBench: LLM Reflective Questioning Benchmark
**January 2026**

## What
Evaluates how well AI models engage in coaching-style reflective questioning. Tests 42 personal growth scenarios where each model has a 3-turn conversation. DeepSeek-V3 judges responses across 6 dimensions based on ICF Core Competencies. Measures whether models ask questions that help you think deeper (coaching style) vs. giving direct advice.

## Results (Jan 2026)
| Model | Score (mean ± SD) | Rank |
|-------|-------------------|------|
| Claude Sonnet 4.5 | 16.4 ± 0.2 | 🥇 |
| GPT-5.2 Chat | 14.5 ± 0.3 | 🥈 |
| Gemini 3 Flash | 11.4 ± 0.2 | 🥉 |

Evaluated 42 scenarios, 126 conversations, 3 evaluations per conversation at temperature=0 for reproducibility.

## Methodology

Each conversation is evaluated 3 times using DeepSeek-V3 as judge with **temperature=0** for deterministic outputs. Results are reported as mean ± standard deviation across the 3 runs.

Temperature=0 ensures reproducible results. Multiple runs account for any remaining variance in LLM-as-judge scoring.

## Stack
Python (data pipeline) • OpenRouter (models) • DeepSeek (judge) • Chart.js (interactive web)

## Goal
Evaluate how well LLMs use coaching-style reflective questioning in personal growth conversations.

## Setup

```bash
# 1. Clone and enter project
git clone <repo-url>
cd coaching-llm-benchmark

# 2. Create isolated Python environment
python3 -m venv venv && source venv/bin/activate

# 3. Install dependencies (pandas, pyyaml, httpx, etc.)
pip install -r requirements.txt

# 4. Configure API keys
cp .env.template .env
# Add OPENROUTER_API_KEY and DEEPSEEK_API_KEY

# 5. Generate 42 test scenarios (Qwen2.5-72B)
python scripts/01_generate_scenarios.py

# 6. Collect 3-turn conversations from 3 models
python scripts/02_collect_responses.py

# 7. Score each response 3 times with DeepSeek-V3 (temperature=0)
python scripts/03_run_evaluation.py

# 8. Generate summary + interactive web data
python scripts/04_analyze_results.py
```

## Author
**Shubham Verma** — Engineer building at the intersection of AI and personal development  
[GitHub](https://github.com/shubham-verma) • [LinkedIn](https://www.linkedin.com/in/shubhamverma) • [X](https://x.com/shubhamVerman) • [Email](mailto:shubham.verman@gmail.com)
