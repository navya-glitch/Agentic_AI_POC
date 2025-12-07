# agents/recommendation_agent.py
import json
from typing import Dict, Any, List
from textwrap import dedent

from ollama_client import chat_ollama


def generate_recommendation(enhanced_query: Dict[str, Any],
                            plans: List[Dict[str, Any]]) -> str:
    """
    Recommendation + Comparison + Explanation Agent.

    Input:
      - enhanced_query: enriched user intent
      - plans: list of candidate plans (already scored)

    Output:
      - Human-readable explanation text (markdown-like).
    """

    if not plans:
        return (
            "I couldn't find any matching example plans for your query.\n"
            "For this PoC, try things like 'home insurance with pet in CA' or 'health plan in TX'."
        )

    # Keep top 5 for the LLM to reason about
    top_plans = plans[:5]

    system_prompt = """
You are a Policy Comparison and Recommendation Agent for an insurance e-commerce system.

You receive:
- An enhanced user query (with policyType, riskFactors, budgetPreference, etc.)
- A list of candidate plans WITH:
  - id, company_name, plan_name
  - insurance_type
  - adjusted_annual_premium_usd
  - customer_rating, number_of_reviews
  - features, limitations
  - valueScore

Your job:
1. Pick the best 2–3 plans for THIS user.
2. For each recommended plan, clearly specify:
   - Plan ID
   - Company + Plan Name
   - Approx annual premium
   - Key strengths
   - Main drawbacks
3. Provide a short comparison:
   - Which plan is best for LowPremium (budget-conscious)?
   - Which plan is best for HighCoverage / maximum protection?
4. Explain in 3–4 bullets:
   - When is generally a good time to buy this type of insurance?
   - What to keep in mind from a risk/coverage perspective.

Constraints:
- DO NOT invent new plans. Only work with the provided list.
- Be concise and structured (headings + bullet points).
- At the end, add: "Note: Example data only, not financial or legal advice."
"""

    user_payload = {
        "enhancedQuery": enhanced_query,
        "candidatePlans": top_plans,
    }

    user_prompt = dedent(f"""
    Here is the input JSON:

    {json.dumps(user_payload, indent=2)}
    """)

    response = chat_ollama(system_prompt, user_prompt)
    return response
