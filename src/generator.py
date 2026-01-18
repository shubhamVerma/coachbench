import json
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.api_client import client
from src.models import ModelName, Scenario, ScenarioCategory, Message


class ScenarioGenerator:
    """Generates 5 unique scenarios per category using specific prompts"""
    
    def __init__(self):
        self.model = ModelName.QWEN_72B
    
    async def generate_scenarios(self, count: int = 42) -> List[Scenario]:
        """Generate 5 unique scenarios per category using specific prompts"""
        
        # Category-specific unique prompt requirements
        category_requirements = {
            "career_transitions": [
                "Role transitions and changing industries",
                "Career stagnation and feeling stuck despite skills",
                "Industry changes and automation/AI impact",
                "Work-life balance, burnout, and boundary setting",
                "Career identity outside work and life transitions",
                "Career pivots and finding new purpose",
                "Layoffs, restructuring, or organizational changes"
            ],
            "relationship_patterns": [
                "Recurring conflicts and communication patterns",
                "Boundary issues - saying yes, people-pleasing, assertiveness",
                "Emotional distance and lack of vulnerability",
                "Communication styles and conflict patterns",
                "Trust issues including jealousy, secrets, betrayals",
                "Family dynamics and in-law relationships",
                "Relationship transitions and dating challenges",
                "Loneliness and isolation despite wanting connection",
                "Social relationships and friendship challenges",
            ],
            "habit_formation": [
                "Exercise routines and gym habits",
                "Productivity patterns including procrastination",
                "Lifestyle habits including eating, sleep, and screen time",
                "Learning habits including study routines",
                "Breaking bad habits and trigger identification",
                "Consistency challenges and accountability struggles",
            ],
            "identity_perception": [
                "Self-worth and imposter syndrome",
                "Social comparison trap and envy",
                "Perfectionism and fear of failure",
                "Role identity and defining self by work",
                "Self-acceptance and body image issues",
                "Authenticity and feeling fake or inauthentic",
                "Life transitions and identity shifts",
            ],
            "decision_making": [
                "Career choices and job offers",
                "Relocation decisions and lifestyle trade-offs",
                "Education choices and skill development",
                "Financial decisions and major purchases",
                "Life transitions including marriage, children, retirement",
                "Commitment paralysis and overthinking",
                "Fear of wrong choices and analysis paralysis",
            ],
            "motivation_resistance": [
                "Procrastination despite knowing what to do",
                "Self-sabotage and negative self-talk",
                "Burnout and exhaustion",
                "Lack of clear purpose and direction",
                "Resistance to change and comfort zone issues",
                "Perfectionism and fear of not being good enough",
            ]
        }
        
        scenarios = []
        
        print(f"Generating {count} unique scenarios...")
        
        total_scenario_id = 1
        for category_name, requirements_list in category_requirements.items():
            for specific_focus in requirements_list:
                total_scenario_id_str = f"{category_name}_{total_scenario_id:03d}"
                
                prompt = f"""Generate a realistic personal growth scenario for category: {category_name}

Specific Focus for this scenario: {specific_focus}

Category: {category_name}
Scenario ID: {total_scenario_id_str}

Requirements:
- Authentic and nuanced, like real human struggles
- Complex but not textbook examples  
- Person thinks they know the issue but might not
- Multiple valid perspectives possible
- Person is stuck in a specific pattern
- Generate ONLY the initial user statement (prompt)
- DO NOT generate any follow-up responses or turn2_response

Format your response as JSON with ONLY these fields:
{{
  "category": "{category_name}",
  "prompt": "The user's exact words they would say - their initial statement ONLY"
}}

Just provide the JSON with these exact 2 fields, no other text or fields."""
                
                messages = [Message(role="user", content=prompt)]
                
                try:
                    print(f"Generating {total_scenario_id_str}/{count}...")
                    response = await client.query(self.model, messages, max_tokens=1000)
                    
                    try:
                        scenario_data = json.loads(response.content)
                        if isinstance(scenario_data, dict) and "prompt" in scenario_data:
                            scenario_data["id"] = total_scenario_id_str
                            scenario_data["category"] = category_name
                            scenario_data["created_at"] = "2026-01-02T13:57:14.171574"
                            
                            scenario = Scenario(
                                id=scenario_data["id"],
                                category=ScenarioCategory(category_name),
                                prompt=scenario_data["prompt"],
                                description=f"{category_name} - {specific_focus}",
                                difficulty="medium"
                            )
                            
                            scenarios.append(scenario)
                            print(f"Scenario {total_scenario_id_str}: {specific_focus}")
                            total_scenario_id += 1
                            
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON for scenario {total_scenario_id_str}")
                    
                except Exception as e:
                    print(f"Error generating scenario {total_scenario_id_str}: {e}")
                    
                await asyncio.sleep(2.0)
        
        print(f"Successfully generated {len(scenarios)} scenarios")
        return scenarios
    
    def save_scenarios(self, scenarios: List[Scenario], filename: str = "data/scenarios.json"):
        """Save scenarios to JSON file"""
        with open(filename, "w") as f:
            json.dump([scenario.dict() for scenario in scenarios], f, indent=2, default=str)


async def main():
    """Main function to generate scenarios"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 1: Generating Scenarios")
    print("-" * 40)
    
    generator = ScenarioGenerator()
    scenarios = await generator.generate_scenarios()
    generator.save_scenarios(scenarios)
    
    print(f"\nGenerated {len(scenarios)} scenarios")
    print("Saved to: data/scenarios.json")


if __name__ == "__main__":
    asyncio.run(main())