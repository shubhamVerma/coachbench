import json
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import re
import numpy as np
from datetime import datetime

from api_client import client
from models import (
    ModelName, Conversation, Evaluation, Scenario, Message
)

NUM_EVAL_RUNS = 3
SCORING_DIMENSIONS = [
    "evokes_awareness",
    "active_listening_indicators",
    "maintains_client_agency",
    "question_depth_progression",
    "client_centered_communication",
    "ethical_boundaries"
]


def to_dict(obj):
    """Recursively convert Pydantic objects to dicts"""
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


class Judge:
    """Evaluates conversations using DeepSeek-V3"""

    def __init__(self):
        self.judge_model = ModelName.DEEPSEEK_V3
        self.num_runs = NUM_EVAL_RUNS

    async def evaluate_conversation(
        self,
        scenario: Scenario,
        conversation: Conversation
    ) -> Evaluation:
        """Evaluate a full 3-turn conversation"""

        eval_prompt = self._build_evaluation_prompt(scenario, conversation)

        messages = [Message(role="user", content=eval_prompt)]
        response = await client.query(self.judge_model, messages)

        return self._parse_evaluation(response.content, conversation.model, scenario.id)

    async def evaluate_conversation_runs(
        self,
        scenario: Scenario,
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Evaluate a conversation multiple times and return aggregated results as plain dict"""

        all_scores = []
        all_runs = []

        for run_idx in range(self.num_runs):
            run_id = run_idx + 1
            print(f"  Run {run_id}/{self.num_runs}...", end=" ")

            eval_prompt = self._build_evaluation_prompt(scenario, conversation)
            messages = [Message(role="user", content=eval_prompt)]
            response = await client.query(self.judge_model, messages)

            eval_result = self._parse_evaluation(response.content, conversation.model, scenario.id)

            # Store scores (EvaluationScores object) for dimension calculations
            all_scores.append(eval_result.scores)

            # Store full evaluation result (convert Pydantic to dict)
            # Calculate total_score from dimension scores to avoid LLM math errors
            dimension_scores = to_dict(eval_result.scores)
            calculated_total = sum(dimension_scores.values())
            
            all_runs.append({
                "run_id": run_id,
                "evaluated_at": datetime.now().isoformat(),
                "scores": dimension_scores,
                "total_score": calculated_total,
                "coaching_vs_advice_moments": to_dict(eval_result.coaching_vs_advice_moments),
                "qualitative_assessment": str(eval_result.qualitative_assessment),
                "strong_examples": list(eval_result.strong_examples),
                "weak_examples": list(eval_result.weak_examples),
                "contra_evidence": list(eval_result.contra_evidence)
            })

            print("✓")

            # Delay between runs to avoid rate limits
            if run_idx < self.num_runs - 1:
                await asyncio.sleep(1.0)

        # Calculate mean and std per dimension
        # Scores must be integers (1-5), so round means to nearest integer
        mean_scores = {}
        std_scores = {}

        for dim in SCORING_DIMENSIONS:
            values = [getattr(s, dim) for s in all_scores]
            mean_scores[dim] = int(round(np.mean(values), 0))
            std_scores[dim] = float(round(np.std(values), 2))

        # Calculate total from mean_scores (not from DeepSeek's potentially erroneous total_score)
        total_mean = int(round(sum(mean_scores.values()), 0))
        total_std = float(round(np.std([sum(run["scores"].values()) for run in all_runs]), 2))

        # Build result as plain dict (no Pydantic objects for multi-run)
        result = {
            "model": conversation.model.value,
            "scenario_id": scenario.id,
            "scores": mean_scores,
            "total_score": total_mean,
            "coaching_vs_advice_moments": all_runs[0]["coaching_vs_advice_moments"],
            "qualitative_assessment": str(all_runs[0]["qualitative_assessment"]),
            "strong_examples": all_runs[0]["strong_examples"],
            "weak_examples": all_runs[0]["weak_examples"],
            "contra_evidence": all_runs[0]["contra_evidence"],
            "num_runs": self.num_runs,
            "temperature": 0,
            "runs": all_runs,
            "aggregated": {
                "mean_scores": mean_scores,
                "std_scores": std_scores,
                "total_mean": total_mean,
                "total_std": total_std
            }
        }

        return result

    def _build_evaluation_prompt(
        self,
        scenario: Scenario,
        conversation: Conversation
    ) -> str:
        """Build the evaluation prompt for the judge"""

        # Load judge prompt template
        with open("prompts/judge_prompt.txt", "r") as f:
            judge_instructions = f.read()

        # Handle both dict and ModelResponse objects
        def get_content(turn):
            if isinstance(turn, dict):
                return turn.get('content', '')
            return turn.content if hasattr(turn, 'content') else str(turn)

        conversation_text = f"""
SCENARIO: {scenario.prompt}

CATEGORY: {scenario.category.value}
DIFFICULTY: {scenario.difficulty}

TURN 1 - Model Response:
{get_content(conversation.turn1)}

TURN 2 - User Response:
{conversation.turn2_user_response}

TURN 2 - Model Response:
{get_content(conversation.turn2)}

TURN 3 - User Response:
{conversation.turn3_user_response}

TURNS 3 - Model Response:
{get_content(conversation.turn3)}
"""

        full_prompt = f"{judge_instructions}\n\n## Conversation to Evaluate:\n{conversation_text}\n\nProvide your evaluation:"

        return full_prompt

    def _parse_evaluation(
        self,
        response_content: str,
        model: ModelName,
        scenario_id: str
    ) -> Evaluation:
        """Parse the judge's response into an Evaluation object"""

        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")

            data = json.loads(json_str)

            # Calculate total_score from individual scores if not provided by judge
            # This ensures consistency and avoids relying on potentially buggy LLM math
            scores = data["scores"]
            if "total_score" in data:
                total_score = data["total_score"]
            else:
                total_score = sum(scores.values())

            # Create Evaluation object
            return Evaluation(
                model=model,
                scenario_id=scenario_id,
                scores=scores,
                total_score=total_score,
                coaching_vs_advice_moments=data["coaching_vs_advice_moments"],
                qualitative_assessment=data["qualitative_assessment"],
                strong_examples=data["strong_examples"],
                weak_examples=data["weak_examples"],
                contra_evidence=data["contra_evidence"]
            )

        except Exception as e:
            print(f"Error parsing evaluation: {e}")
            print(f"Raw response: {response_content}")

            # Return a default/placeholder evaluation
            return Evaluation(
                model=model,
                scenario_id=scenario_id,
                scores={
                    "evokes_awareness": 3,
                    "active_listening_indicators": 3,
                    "maintains_client_agency": 3,
                    "question_depth_progression": 3,
                    "client_centered_communication": 3,
                    "ethical_boundaries": 3
                },
                total_score=18,
                coaching_vs_advice_moments={
                    "stayed_in_inquiry": 0,
                    "slipped_to_advice": 0,
                    "slipped_to_therapy": 0,
                    "slipped_to_consulting": 0
                },
                qualitative_assessment="Evaluation parsing failed - manual review needed",
                strong_examples=[],
                weak_examples=[],
                contra_evidence=["Parsing error occurred"]
            )

    async def evaluate_all_conversations(
        self,
        conversations: List[Conversation],
        scenarios: List[Scenario]
    ) -> List[Dict]:
        """Evaluate all conversations with multi-run support and resumability"""

        # Create scenario lookup
        scenario_map = {s.id: s for s in scenarios}

        # Load existing evaluations for resumability
        existing_evals = {}
        if Path("data/evaluations.json").exists():
            with open("data/evaluations.json", "r") as f:
                evals = json.load(f)
                for eval_data in evals:
                    key = f"{eval_data['model']}_{eval_data['scenario_id']}"
                    existing_evals[key] = True

        evaluations = []
        total_expected = len(conversations)
        completed = 0

        for idx, conversation in enumerate(conversations):
            completed += 1
            key = f"{conversation.model.value}_{conversation.scenario_id}"

            # Skip if already evaluated
            if key in existing_evals:
                print(f"[{completed}/{total_expected}] ✓ Skipping {conversation.model.value} - {conversation.scenario_id} (already evaluated)")
                continue

            print(f"[{completed}/{total_expected}] Evaluating {conversation.model.value} - {conversation.scenario_id}")

            scenario = scenario_map.get(conversation.scenario_id)
            if not scenario:
                print(f"  ✗ Scenario not found")
                continue

            try:
                # Run multi-run evaluation (returns plain dict)
                result = await self.evaluate_conversation_runs(scenario, conversation)
                evaluations.append(result)

                # Save immediately
                self.save_evaluation(result)

                # Delay between evaluations to avoid rate limits
                await asyncio.sleep(2.0)

            except Exception as e:
                print(f"  ✗ Failed: {e}")
                import traceback
                traceback.print_exc()
                continue

        return evaluations

    def save_evaluation(self, evaluation: Dict):
        """Save a multi-run evaluation result (already a plain dict)"""
        filename = Path("data/evaluations.json")

        # Load existing evaluations if file exists
        evaluations = []
        if filename.exists():
            with open(filename, "r") as f:
                evaluations = json.load(f)

        # Add new evaluation
        evaluations.append(evaluation)

        # Save all evaluations
        with open(filename, "w") as f:
            json.dump(evaluations, f, indent=2)

    def load_conversations(self, base_path: Path = Path("data/responses")) -> List[Conversation]:
        """Load all conversations from file system"""
        conversations = []

        if not isinstance(base_path, Path):
            base_path = Path(base_path)

        for model_dir in base_path.iterdir():
            if not model_dir.is_dir():
                continue

            try:
                model_name = ModelName(model_dir.name)
            except ValueError:
                continue

            for file_path in model_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)

                conversation = Conversation(**data)
                conversations.append(conversation)

        return conversations


async def main():
    """Main function to run all evaluations"""
    judge = Judge()

    # Load scenarios
    with open("data/scenarios.json", "r") as f:
        scenarios_data = json.load(f)
    scenarios = [Scenario(**s) for s in scenarios_data]

    print(f"Loaded {len(scenarios)} scenarios")

    # Load conversations
    conversations = judge.load_conversations()
    print(f"Loaded {len(conversations)} conversations")

    print(f"\nRunning {NUM_EVAL_RUNS} evaluations per conversation for reproducibility")
    print("Using temperature=0 for deterministic outputs\n")

    # Run evaluations
    evaluations = await judge.evaluate_all_conversations(conversations, scenarios)

    print(f"\nEvaluation complete!")
    print(f"Total conversations evaluated: {len(evaluations)}")


if __name__ == "__main__":
    asyncio.run(main())
