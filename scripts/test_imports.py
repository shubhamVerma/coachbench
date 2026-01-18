#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test imports
try:
    from src.models import ModelName
    from src.api_client import client
    from src.generator import ScenarioGenerator
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def main():
    """Generate scenarios for benchmark"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 1: Generating Scenarios")
    print("-" * 40)
    
    generator = ScenarioGenerator()
    scenarios = await generator.generate_scenarios()
    generator.save_scenarios(scenarios)
    
    print(f"\n✅ Generated {len(scenarios)} scenarios")
    print("📁 Saved to: data/scenarios.json")


if __name__ == "__main__":
    asyncio.run(main())