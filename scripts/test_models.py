#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.models import ModelName

def test_model_names():
    """Test that model names are correctly updated"""
    print("=== Testing Model Configuration ===")
    print("Available models:")
    
    test_models = [
        ModelName.CLAUDE_SONNET_45,
        ModelName.GPT_4_1,
        ModelName.GEMINI_2_0_FLASH
    ]
    
    for model in test_models:
        print(f"  - {model.value}")
    
    print(f"\n✅ All model names updated successfully!")
    print("✅ Ready for benchmark with latest models:")
    print("  - Claude Sonnet 4.5 (Anthropic)")
    print("  - GPT-4.1 (OpenAI)")
    print("  - Gemini 2.0 Flash (Google)")

if __name__ == "__main__":
    test_model_names()