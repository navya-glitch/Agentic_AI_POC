# agents/query_enhancement_agent.py
import json
from typing import Dict, Any

from ollama_client import chat_ollama


def enhance_query(intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query Enhancement Agent:
    - Fill in missing info with smart defaults.
    - Decide approximate propertyValue, budgetSensitivity, etc.
    - No extra user interaction for now.
    """

    system_prompt = """
You are a Query Enhancement Agent for an insurance comparison system.

Input: an 'intent' JSON from a previous agent.
Goal:
- Add helpful defaults without asking more questions.
- Infer:
  - propertyValueUsd: approximate numeric value (or null if not relevant).
  - budgetPreference: one of ["LowPremium", "Balanced", "HighCoverage"]
  - userStage: one of ["JustLooking", "Comparing", "ReadyToBuy"]

Rules:
- If policyType is "home" or "fire", guess a property value (between 150000 and 1000000).
- For renters/auto/health, propertyValueUsd can be null.
- Use the original intent as-is; just extend it.

Respond ONLY as strict JSON:
{
  "policyType": "...",
  "riskFactors": [...],
  "location": "...",
  "intent": "...",
  "propertyValueUsd": <number or null>,
  "budgetPreference": "<LowPremium|Balanced|HighCoverage>",
  "userStage": "<JustLooking|Comparing|ReadyToBuy>"
}
"""

    user_prompt = json.dumps(intent, indent=2)
    content = chat_ollama(system_prompt, user_prompt).strip()

    try:
        enhanced = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: basic extension
        policy = intent.get("policyType", "home")
        property_value = None
        if policy in ["home", "fire"]:
            property_value = 300000

        enhanced = {
            "policyType": policy,
            "riskFactors": intent.get("riskFactors", []),
            "location": intent.get("location", "Unknown"),
            "intent": intent.get("intent", "Comparison"),
            "propertyValueUsd": property_value,
            "budgetPreference": "Balanced",
            "userStage": "Comparing",
        }

    # Minimal sanity checks
    if enhanced.get("budgetPreference") not in ["LowPremium", "Balanced", "HighCoverage"]:
        enhanced["budgetPreference"] = "Balanced"
    if enhanced.get("userStage") not in ["JustLooking", "Comparing", "ReadyToBuy"]:
        enhanced["userStage"] = "Comparing"

    return enhanced
