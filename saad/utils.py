import json
import re

def extract_valid_json(text):
    """Extract JSON content between ```json and ``` ensuring valid JSON."""
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    
    if json_match:
        try:
            return json.loads(json_match.group(1))  # Convert to dict
        except json.JSONDecodeError:
            return {"relevant_ids": []}  # Return empty response if invalid JSON
    
    return {"relevant_ids": []}  # Return empty response if no JSON found
