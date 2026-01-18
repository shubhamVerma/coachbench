#!/usr/bin/env python3

import asyncio
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from evaluator import Judge
from models import Scenario


async def main():
    """Evaluate model responses using DeepSeek"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 3: Running Evaluation")
    print("-" * 40)

    judge = Judge()

    # Load conversations
    conversations = judge.load_conversations()
    print(f"📝 Loaded {len(conversations)} conversations")

    # Load scenarios
    with open("data/scenarios.json", "r") as f:
        scenarios_data = json.load(f)
    scenarios = [Scenario(**s) for s in scenarios_data]
    print(f"📋 Loaded {len(scenarios)} scenarios")

    print("⚖️  Evaluating with DeepSeek-V3 judge...")
    print("💾 Progress will be saved after each evaluation")
    print("⏸️  Can resume from where it left off if interrupted")
    print()

    evaluations = await judge.evaluate_all_conversations(conversations, scenarios)

    print(f"\n✅ Completed {len(evaluations)} evaluations")
    print("📁 Results saved to: data/evaluations.json")


if __name__ == "__main__":
    asyncio.run(main())