#!/usr/bin/env python3
"""Generate responses index for interactive evaluations section"""

import json
from pathlib import Path

CATEGORY_LABELS = {
    'career_transitions': 'Career Transitions',
    'relationship_patterns': 'Relationship Patterns',
    'identity_perception': 'Identity Perception',
    'decision_making': 'Decision Making',
    'habit_formation': 'Habit Formation',
    'motivation_resistance': 'Motivation Resistance'
}

def main():
    # Load scenarios
    with open('data/scenarios.json', 'r') as f:
        scenarios = json.load(f)
    
    responses_dir = Path('data/responses')
    models = ['claude_web_free', 'chatgpt_web_free', 'gemini_web_free']
    
    # Track category indices
    category_indices = {cat: 0 for cat in CATEGORY_LABELS.keys()}
    
    index = []
    
    for scenario in scenarios:
        category = scenario['category']
        
        # Check which models have responses
        available_models = []
        for model in models:
            response_file = responses_dir / model / f"{scenario['id']}.json"
            if response_file.exists():
                available_models.append(model)
        
        index.append({
            'id': scenario['id'],
            'category': category,
            'category_label': CATEGORY_LABELS[category],
            'prompt': scenario['prompt'],
            'description': scenario['description'],
            'models': available_models,
            'index_in_category': category_indices[category]
        })
        
        category_indices[category] += 1
    
    # Save index
    output = {'scenarios': index}
    
    with open('data/responses_index.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Copy to web directory
    web_dir = Path('web/data')
    web_dir.mkdir(parents=True, exist_ok=True)
    
    with open('web/data/responses_index.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated responses_index.json with {len(index)} scenarios")
    print(f"Copied to web/data/responses_index.json")

if __name__ == '__main__':
    main()
