import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import numpy as np

from models import ModelName, Evaluation, EvaluationSummary, Scenario


class Analyzer:
    """Analyzes evaluation results and creates visualizations"""

    MAX_SCORE = 30
    DIMENSION_SCORE = 5
    NUM_TURNS = 3
    NUM_CATEGORIES = 6
    SCORING_DIMENSIONS = [
        "evokes_awareness",
        "active_listening_indicators",
        "maintains_client_agency",
        "question_depth_progression",
        "client_centered_communication",
        "ethical_boundaries"
    ]

    def __init__(self):
        self.evaluations = []
        self.scenarios = []

        # Load model configuration
        with open("config/models.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        self.model_descriptions = {
            model_name: data.get("note", model_name)
            for model_name, data in self.config.get("models", {}).items()
        }

    def load_data(self, eval_file: str = "data/evaluations.json",
                  scenario_file: str = "data/scenarios.json"):
        """Load evaluation and scenario data - supports both old and new formats"""

        with open(eval_file, "r") as f:
            eval_data = json.load(f)

        # Handle both old format (list of Evaluation objects) and new format (dict with aggregated)
        self.evaluations = []
        for eval_item in eval_data:
            if isinstance(eval_item, dict) and "aggregated" in eval_item:
                # New format: multi-run evaluation with aggregated results
                self.evaluations.append(eval_item)
            else:
                # Old format: single Evaluation object
                self.evaluations.append(Evaluation(**eval_item))

        with open(scenario_file, "r") as f:
            scenario_data = json.load(f)
        self.scenarios = [Scenario(**s) for s in scenario_data]

        print(f"Loaded {len(self.evaluations)} evaluations and {len(self.scenarios)} scenarios")

    def calculate_model_averages(self) -> Dict[ModelName, Dict[str, float]]:
        """Calculate average scores by model - uses aggregated results when available"""

        model_scores = {}

        for model in ModelName:
            if model == ModelName.QWEN_72B or model == ModelName.DEEPSEEK_V3:
                continue  # Skip non-test models

            model_evals = [e for e in self.evaluations
                          if (e["model"] if isinstance(e, dict) else e.model) == model.value]
            if not model_evals:
                continue

            # Check if we have aggregated results (new format)
            if isinstance(model_evals[0], dict) and "aggregated" in model_evals[0]:
                # Use aggregated mean from multi-run evaluation
                scores = {}
                for dim in self.SCORING_DIMENSIONS:
                    scores[dim] = np.mean([ev["aggregated"]["mean_scores"][dim] for ev in model_evals])
                scores["total_score"] = np.mean([ev["aggregated"]["total_mean"] for ev in model_evals])
                scores["total_std"] = np.mean([ev["aggregated"]["total_std"] for ev in model_evals])
            else:
                # Old format: calculate from individual evaluations
                scores = {}
                for dim in self.SCORING_DIMENSIONS:
                    scores[dim] = np.mean([getattr(e.scores, dim) for e in model_evals])
                scores["total_score"] = np.mean([e.total_score for e in model_evals])

            model_scores[model] = scores

        return model_scores

    def create_ranking(self) -> List[Dict[str, Any]]:
        """Create overall ranking of models - includes std for multi-run evaluations"""

        model_averages = self.calculate_model_averages()

        # Sort by total score
        ranked_models = sorted(
            model_averages.items(),
            key=lambda x: x[1]["total_score"],
            reverse=True
        )

        ranking = []
        for rank, (model, scores) in enumerate(ranked_models, 1):
            entry = {
                "rank": rank,
                "model": model.value,
                "total_score": round(scores["total_score"], 2),
                "evokes_awareness": round(scores["evokes_awareness"], 2),
                "active_listening_indicators": round(scores["active_listening_indicators"], 2),
                "maintains_client_agency": round(scores["maintains_client_agency"], 2),
                "question_depth_progression": round(scores["question_depth_progression"], 2),
                "client_centered_communication": round(scores["client_centered_communication"], 2),
                "ethical_boundaries": round(scores["ethical_boundaries"], 2)
            }
            # Add std if available (multi-run format)
            if "total_std" in scores:
                entry["total_std"] = round(scores["total_std"], 2)

            ranking.append(entry)

        return ranking

    def save_results(self):
        """Save analysis results"""

        # Ensure results directory exists
        Path("results").mkdir(parents=True, exist_ok=True)

        model_averages = self.calculate_model_averages()
        ranking = self.create_ranking()

        # Build model averages with std
        model_averages_output = {}
        for model, scores in model_averages.items():
            model_key = model.value
            model_averages_output[model_key] = {
                "evokes_awareness": scores.get("evokes_awareness", 0),
                "active_listening_indicators": scores.get("active_listening_indicators", 0),
                "maintains_client_agency": scores.get("maintains_client_agency", 0),
                "question_depth_progression": scores.get("question_depth_progression", 0),
                "client_centered_communication": scores.get("client_centered_communication", 0),
                "ethical_boundaries": scores.get("ethical_boundaries", 0),
                "total_score": scores.get("total_score", 0)
            }
            if "total_std" in scores:
                model_averages_output[model_key]["total_std"] = scores["total_std"]

        summary = {
            "total_scenarios": len(self.scenarios),
            "total_evaluations": len(self.evaluations),
            "model_averages": model_averages_output,
            "overall_ranking": ranking,
            "generated_at": str(datetime.now())
        }

        # Save summary as JSON
        with open("results/summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        # Generate markdown summary
        self._generate_markdown_summary(summary)

        print(f"Results saved to results/summary.json and results/summary.md")

    def _generate_markdown_summary(self, summary: Dict):
        """Generate human-readable summary in markdown"""

        from datetime import datetime

        ranking = summary.get("overall_ranking", [])
        model_averages = summary.get("model_averages", {})

        md_content = f"""# LLM Reflective Questioning Benchmark - Results

## Overview

- **Total Scenarios**: {summary.get('total_scenarios', 'N/A')}
- **Total Evaluations**: {summary.get('total_evluations', 'N/A')}
- **Evaluation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - **Methodology**: 3 runs per evaluation at temperature=0 for reproducibility

## Model Rankings

| Rank | Model | Overall Score | Evokes Awareness | Active Listening | Maintains Agency | Question Depth | Client-Centered | Ethical Boundaries |
|------|-------|---------------|------------------|------------------|------------------|----------------|-----------------|-------------------|
"""

        for r in ranking:
            model_desc = self.model_descriptions.get(r["model"], r["model"])
            score_str = f"{r['total_score']:.1f}"
            if "total_std" in r:
                score_str = f"{r['total_score']:.1f} ± {r['total_std']:.2f}"
            md_content += f"| {r['rank']} | {model_desc} | {score_str} | {r['evokes_awareness']:.1f} | {r['active_listening_indicators']:.1f} | {r['maintains_client_agency']:.1f} | {r['question_depth_progression']:.1f} | {r['client_centered_communication']:.1f} | {r['ethical_boundaries']:.1f} |\n"

        # Find best performer for key findings
        best_model = ranking[0] if ranking else None
        if best_model:
            best_desc = self.model_descriptions.get(best_model["model"], best_model["model"])

            md_content += f"""
## Key Findings

### Best Overall Performance

**{best_desc}** achieved the highest overall score of {best_model['total_score']:.1f}/30.

Key strengths:
- Evokes Awareness: {best_model['evokes_awareness']:.1f}/5
- Active Listening: {best_model['active_listening_indicators']:.1f}/5
- Maintains Client Agency: {best_model['maintains_client_agency']:.1f}/5
"""

        md_content += """
## Methodology

This benchmark evaluates coaching-style communication quality in LLMs using:
- 42 personal growth scenarios across 6 categories
- 3-turn conversations with each model
- Independent evaluation using DeepSeek-V3 (temperature=0)
- 3 evaluations per conversation, results averaged
- Scoring based on ICF Core Competencies
- Focus on reflective questioning vs advice-giving

## Important Limitations

1. **Not evaluating actual coaching**: This measures coaching-style communication techniques, not embodied coaching relationships
2. **Text-only evaluation**: Cannot assess presence, intuition, or relational dynamics
3. **Simulated conversations**: Turn 3 responses are AI-generated, not from real humans
4. **Specific scenarios**: Results may vary with different types of challenges or conversation contexts

---

*Generated by LLM Reflective Questioning Benchmark*
"""

        with open("results/summary.md", "w") as f:
            f.write(md_content)


def main():
    """Main analysis function"""
    analyzer = Analyzer()

    # Load data
    analyzer.load_data()

    # Save results
    analyzer.save_results()

    print("\nAnalysis complete!")
    print("Files generated:")
    print("- results/summary.json")
    print("- results/summary.md")


if __name__ == "__main__":
    main()
