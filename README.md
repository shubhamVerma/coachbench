# CoachBench: Evaluating Reflective Questioning Quality in Large Language Models

**January 2026**

![CoachBench Overview](https://raw.githubusercontent.com/shubhamVerma/coachbench/main/docs/og-image.png)

A standardized benchmark for AI coaching communication quality. Tests whether LLMs ask powerful questions or default to giving advice across 42 personal growth scenarios.

## Quick Start

```bash
# 1. Configure API keys
cp coaching-llm-benchmark/.env.template coaching-llm-benchmark/.env
# Add OPENROUTER_API_KEY and DEEPSEEK_API_KEY

# 2. Run evaluation
cd coaching-llm-benchmark
python scripts/03_run_evaluation.py

# 3. Generate results and web data
python scripts/04_analyze_results.py
```

## Results (Jan 2026)

| Model | Score (mean ± SD) | Rank |
|-------|-------------------|------|
| Claude Sonnet 4.5 | 16.5 ± 0.37 | 🥇 |
| GPT-5.2 Chat | 14.7 ± 0.38 | 🥈 |
| Gemini 3 Flash | 11.5 ± 0.28 | 🥉 |

42 scenarios, 126 conversations, 3 evaluations per conversation (DeepSeek-V3 judge, temperature=0).

## Data

| File | Description |
|------|-------------|
| `data/scenarios.json` | 42 frozen scenario prompts (v1.0, Jan 2026) |
| `data/responses/{model}/` | Model responses for each scenario |
| `data/evaluations.json` | Judge scores (DeepSeek-V3) |
| `docs/data/summary.json` | Aggregated results for web UI |

## Prompts

**Scenarios:** Personal growth situations across 6 categories — career transitions, relationship patterns, identity perception, decision making, habit formation, motivation resistance.

**Evaluation:** DeepSeek-V3 scores across 6 ICF Core Competencies (0-5 each):
- Evokes Awareness
- Active Listening
- Maintains Agency
- Question Depth
- Client-Centered
- Ethical Boundaries

## Citation

```bibtex
@article{verma2026coachbench,
  title={CoachBench: Evaluating Reflective Questioning Quality in Large Language Models},
  author={Verma, Shubham},
  year={2026},
  url={https://shubhamverma.github.io/coachbench/},
  note={Benchmark evaluating 3 LLMs across 42 coaching scenarios using ICF Core Competencies framework}
}
```

## Author

**Shubham Verma** is a Product Tinkerer exploring AI and personal development. This started as a personal experiment to understand how well current AI models can engage in coaching-style reflective questioning.

Open to collaboration with LLM researchers, model evaluation experts, and professional coaches.

[GitHub](https://github.com/shubhamVerma/coachbench) • [LinkedIn](https://www.linkedin.com/in/shubhamverma) • [X](https://x.com/shubhamVerman) • [Website](https://bit.ly/web-shubham) • [Email](mailto:shubham.verman@gmail.com)

---

**Note:** The 42 scenarios are frozen (v1.0, Jan 2026). See `coaching-llm-benchmark/scripts/01_generate_scenarios.py` for generation details.
