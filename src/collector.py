import json
import asyncio
import sys
from pathlib import Path
from typing import List
import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from api_client import client
from models import ModelName, Scenario, ScenarioCategory, Message, Conversation, ModelResponse


def load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / "config" / "models.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class ConversationCollector:
    """Collects 3-turn conversations from test models"""

    def __init__(self):
        config = load_config()
        self.test_models = [ModelName(m) for m in config["test_models"]]
        self.generator_model = ModelName.QWEN_72B
    
    async def generate_turn2_user_response(
        self, 
        turn1_response: str,
        scenario_prompt: str
    ) -> str:
        """Generate a realistic Turn 2 user response based on Turn 1 coaching"""
        
        prompt = f"""Based on this coaching conversation, generate a realistic Turn 2 user response.

Scenario Prompt: {scenario_prompt}

Turn 1 Coaching Response: {turn1_response}

Requirements for user response:
1. Authentic and natural, not robotic
2. Shows some reflection on coach's questions
3. Still maintains core assumptions or resistances
4. Sounds like a real person (2-4 sentences)
5. Doesn't have sudden breakthroughs
6. May express some confusion or continued stuckness

Generate only as user response, no other text."""
        
        messages = [Message(role="user", content=prompt)]
        response = await client.query(self.generator_model, messages, max_tokens=500)
        return response.content.strip()
    
    async def collect_all_conversations(self, scenarios: List[Scenario]) -> List[Conversation]:
        """Collect conversations for all scenarios and models with resume capability"""
        
        all_conversations = []
        total_expected = len(scenarios) * len(self.test_models)
        completed = 0
        
        for idx, scenario in enumerate(scenarios):
            print(f"\n[{idx + 1}/{len(scenarios)}] Processing scenario: {scenario.id}")
            
            for model in self.test_models:
                completed += 1
                print(f"  [{completed}/{total_expected}] {model.value}...", end=" ")
                
                # Check if already exists
                filename = Path(f"data/responses/{model.value}/{scenario.id}.json")
                if filename.exists():
                    print(f"✓ already exists, skipping")
                    continue
                
                try:
                    conversation = await self.run_conversation(scenario, model)
                    all_conversations.append(conversation)
                    
                    # Save immediately to avoid data loss
                    self.save_conversation(conversation)
                    
                    print("✓ completed")
                    
                    # Delay between conversations to avoid rate limits
                    await asyncio.sleep(2.0)
                    
                except Exception as e:
                    print(f"✗ failed: {e}")
                    continue
        
        return all_conversations
    
    async def run_conversation(
        self, 
        scenario: Scenario, 
        model_name: ModelName
    ) -> Conversation:
        """Run a 3-turn conversation with a model"""
        
        # Turn 1: Initial response to scenario
        turn1_messages = [Message(role="user", content=scenario.prompt)]
        turn1 = await client.query(model_name, turn1_messages)
        
        # Turn 2: Generate dynamic user response
        turn2_user_content = await self.generate_turn2_user_response(turn1.content, scenario.prompt)
        
        turn2_messages = [
            Message(role="user", content=scenario.prompt),
            Message(role="assistant", content=turn1.content),
            Message(role="user", content=turn2_user_content)
        ]
        turn2 = await client.query(model_name, turn2_messages)
        
        # Turn 3: Contextual deepening
        turn3_prompt = await self.generate_turn3_prompt(
            scenario, turn1.content, turn2.content
        )
        
        turn3_messages = [
            Message(role="user", content=scenario.prompt),
            Message(role="assistant", content=turn1.content),
            Message(role="user", content=turn2_user_content),
            Message(role="assistant", content=turn2.content),
            Message(role="user", content=turn3_prompt)
        ]
        turn3 = await client.query(model_name, turn3_messages)

        return Conversation(
            scenario_id=scenario.id,
            model=model_name,
            turn1=turn1,
            turn2=turn2,
            turn3=turn3,
            turn2_user_response=turn2_user_content,
            turn3_user_response=turn3_prompt
        )
    
    async def generate_turn3_prompt(
        self,
        scenario: Scenario,
        turn1_response: str,
        turn2_response: str
    ) -> str:
        """Generate contextual Turn 3 prompt using Qwen"""

        # turn1_response = Turn 1 coaching response from the model
        # turn2_response = Turn 2 coaching response from the model (NOT user response)

        # We need to reconstruct the full conversation for context
        # But we don't have the generated user response in the function params
        # So we'll generate a new user response for Turn 3

        prompt = f"""Based on this coaching conversation, generate a realistic Turn 3 user response.

Scenario: {scenario.prompt}

Turn 1 Coaching Response: {turn1_response}

Turn 2 Coaching Response: {turn2_response}

Generate a realistic, authentic user response that:
1. Shows some reflection on both previous coaching responses
2. May express some confusion or continued stuckness
3. Could have a small insight or shift in perspective
4. Is 2-4 sentences long
5. Doesn't have sudden breakthroughs

Response only, no explanation."""

        messages = [Message(role="user", content=prompt)]
        response = await client.query(self.generator_model, messages, max_tokens=500)
        return response.content.strip()
    
    def save_conversation(self, conversation: Conversation):
        """Save a single conversation to file"""
        model_dir = Path(f"data/responses/{conversation.model.value}")
        model_dir.mkdir(parents=True, exist_ok=True)

        filename = model_dir / f"{conversation.scenario_id}.json"

        with open(filename, "w") as f:
            # Use model_dump() for Pydantic v2, or dict() for v1
            try:
                data = conversation.model_dump()
            except AttributeError:
                data = conversation.dict()
            json.dump(data, f, indent=2, default=str)
    
    def load_scenarios(self, filename="data/scenarios.json"):
        """Load scenarios from file"""
        with open(filename, "r") as f:
            data = json.load(f)
        
        return [Scenario(**scenario_data) for scenario_data in data]


async def main():
    """Main function to collect all model responses"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 2: Collecting Model Responses")
    print("-" * 40)
    
    collector = ConversationCollector()
    scenarios = collector.load_scenarios()
    
    print(f"  Loaded {len(scenarios)} scenarios")
    print("  Testing models: Claude 3.5 Sonnet (Free Web), ChatGPT 4o Mini (Free Web), Gemini 2.0 Flash (Free Web)")
    print()
    
    conversations = await collector.collect_all_conversations(scenarios)
    
    print(f"\n  Collected {len(conversations)} conversations")
    print("  Responses saved to: data/responses/[model]/")


if __name__ == "__main__":
    asyncio.run(main())