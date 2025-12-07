# main.py
"""
Agentic Insurance E-commerce Search & Comparison PoC

Flow:
1. User types natural language query.
2. IntentAgent -> extract structured intent.
3. QueryEnhancementAgent -> add defaults (property value, budget preference).
4. ConnectorAgent -> fetch + price dummy plans, compute value score.
5. RecommendationAgent -> compare, recommend, and explain.
"""

from agents.intent_agent import extract_intent
from agents.query_enhancement_agent import enhance_query
from agents.connectors_agent import fetch_and_score_plans
from agents.recommendation_agent import generate_recommendation


def main():
    print("=== Agentic Insurance Search & Comparison (PoC) ===\n")
    print("Examples:")
    print('- "Home insurance with pet and swimming pool in CA"')
    print('- "Best health insurance in TX for family"')
    print('- "Cheap renters insurance in NY"')
    print()

    user_query = input("Describe what you are looking for: ").strip()
    if not user_query:
        print("Empty query. Exiting.")
        return

    print("\n[Orchestrator] -> Calling Intent Agent...\n")
    intent = extract_intent(user_query)
    print("Intent (structured):")
    print(intent)
    print("\n[Orchestrator] -> Calling Query Enhancement Agent...\n")
    enhanced = enhance_query(intent)
    print("Enhanced Query:")
    print(enhanced)

    print("\n[Orchestrator] -> Calling Connector + Pricing Agent...\n")
    plans = fetch_and_score_plans(enhanced)
    if not plans:
        print("No dummy plans matched this type/location combo.")
        print("For demo, try 'home insurance in CA' or 'health plan in TX'.")
        return

    print("Top candidate plans (internal view):")
    for p in plans[:5]:
        print(
            f"- {p['id']} | {p['company_name']} - {p['plan_name']} | "
            f"premium=${p['adjusted_annual_premium_usd']} | "
            f"rating={p['customer_rating']} | reviews={p['number_of_reviews']} | "
            f"valueScore={p['valueScore']}"
        )

    print("\n[Orchestrator] -> Calling Recommendation & Explanation Agent...\n")
    recommendation_text = generate_recommendation(enhanced, plans)

    print("\n===== Recommendation & Explanation =====\n")
    print(recommendation_text)
    print("\n========================================\n")


if __name__ == "__main__":
    main()
