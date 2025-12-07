"""Lightweight Dynamic Agents Integration.

Provides a minimal DynamicAgentsController for the UI to call.
This allows the search/recommendation features to run even if the full
agent system is not available.
"""
from typing import Dict, List, Any, Optional


class DynamicAgentsController:
    """Minimal agent controller for UI integration.

    Methods the UI calls:
    - search_and_compare(query, plans) -> recommendations dict
    - get_quote_for_search(query, plan) -> quote string
    """

    def __init__(self):
        """Initialize the controller."""
        pass

    def search_and_compare(self, query: str, plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI recommendations from a search query and plans.

        Args:
            query: User's search query
            plans: List of insurance plans to analyze

        Returns:
            Dict with top_recommendation, recommendation reason, and reasons list
        """
        if not plans:
            return {
                "top_recommendation": "No plans available",
                "recommendation": "Please refine your search.",
                "reasons": [],
            }

        # Simple heuristic: recommend highest-rated plan
        best = max(plans, key=lambda p: p.get("rating", 0))
        return {
            "top_recommendation": best.get("plan_name", "Best Option"),
            "recommendation": f"This plan offers the best customer rating ({best.get('rating', 0)}/5) and good coverage for your needs.",
            "reasons": [
                f"Customer Rating: {best.get('rating', 0)}/5",
                f"Coverage: ${best.get('coverage_amount', 0):,}",
                f"Annual Premium: ${best.get('annual_premium', 0):,}",
            ],
        }

    def get_quote_for_search(self, query: str, plan: Dict[str, Any]) -> str:
        """Generate a personalized quote for a selected plan.

        Args:
            query: User's search query
            plan: Selected insurance plan

        Returns:
            Quote message string
        """
        plan_name = plan.get("plan_name", "Selected Plan")
        insurer = plan.get("insurer", "Insurer")
        premium = plan.get("annual_premium", 0)

        return f"Quote for {plan_name} by {insurer}: ${premium:,}/year. Based on your profile, you qualify for standard rates. Click 'Buy Now' to proceed with the application."
