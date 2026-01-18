#!/usr/bin/env python3

import asyncio
import sys
import yaml
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.collector import ConversationCollector


def get_model_descriptions():
    """Get model descriptions from config file"""
    with open("config/models.yaml", "r") as f:
        config = yaml.safe_load(f)
    return {model_name: data.get("note", model_name)
            for model_name, data in config.get("models", {}).items()}


async def main():
    """Main function to collect all model responses"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 2: Collecting Model Responses")
    print("-" * 40)

    collector = ConversationCollector()
    scenarios = collector.load_scenarios()

    model_descriptions = get_model_descriptions()

    print(f"📋 Loaded {len(scenarios)} scenarios")
    print("🤖 Testing models:")
    for model in collector.test_models:
        desc = model_descriptions.get(model.value, model.value)
        print(f"   • {desc}")
    print("💾 Progress will be saved after each conversation")
    print("⏸️  Can resume from where it left off if interrupted")
    print()

    conversations = await collector.collect_all_conversations(scenarios)

    print(f"\n✅ Collected {len(conversations)} conversations")
    print("📁 Responses saved to: data/responses/[model]/")


if __name__ == "__main__":
    asyncio.run(main())
