# agents/connectors_agent.py
from typing import Dict, Any, List
import math

from data_plans import DUMMY_PLANS


def _matches_type(plan: Dict[str, Any], policy_type: str) -> bool:
    return plan["insurance_type"].lower() == policy_type.lower()


def _matches_location(plan: Dict[str, Any], location: str) -> bool:
    if not location or location == "Unknown":
        return True
    location = location.upper()
    # assume the last two chars (if uppercase letters) are state
    state = location[-2:]
    return "ALL" in plan["states"] or state in plan["states"]


def _compute_adjusted_premium(plan: Dict[str, Any],
                              enhanced_query: Dict[str, Any]) -> float:
    """
    Very simple pricing adjustments based on riskFactors & budgetPreference.
    Just for demo.
    """
    base = float(plan["base_annual_premium_usd"])
    risk_factors = [rf.lower() for rf in enhanced_query.get("riskFactors", [])]
    budget_pref = enhanced_query.get("budgetPreference", "Balanced")

    # Risk surcharges
    if "pet" in risk_factors:
        base *= 1.05  # +5%
    if "swimming_pool" in risk_factors:
        base *= 1.10  # +10%

    # Budget preference tweaks
    if budget_pref == "LowPremium":
        base *= 0.95
    elif budget_pref == "HighCoverage":
        base *= 1.05

    # Round to nearest whole dollar
    return round(base, 2)


def _value_score(plan: Dict[str, Any], adjusted_premium: float) -> float:
    """
    Simple heuristic:
    - lower premium better
    - higher rating better
    - more reviews slightly better
    - better coverage/premium ratio better
    """
    rating = float(plan["customer_rating"])
    reviews = max(int(plan["number_of_reviews"]), 1)
    coverage = float(plan["coverage_amount_usd"])

    coverage_ratio = coverage / adjusted_premium if adjusted_premium > 0 else 0.0

    score = (
        0.4 * coverage_ratio +
        0.4 * rating +
        0.2 * math.log10(reviews)
    )
    return score


def fetch_and_score_plans(enhanced_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Insurance Connector + Pricing Agent (simplified).
    - Filters dummy plans by policyType + location.
    - Computes adjusted premium.
    - Computes valueScore.
    - Returns sorted list.
    """
    policy_type = enhanced_query["policyType"]
    location = enhanced_query.get("location", "Unknown")

    candidates: List[Dict[str, Any]] = []

    for plan in DUMMY_PLANS:
        if not _matches_type(plan, policy_type):
            continue
        if not _matches_location(plan, location):
            continue

        adj = _compute_adjusted_premium(plan, enhanced_query)
        value = _value_score(plan, adj)

        enriched = dict(plan)
        enriched["adjusted_annual_premium_usd"] = adj
        enriched["valueScore"] = round(value, 3)
        candidates.append(enriched)

    candidates.sort(key=lambda p: p["valueScore"], reverse=True)
    return candidates
