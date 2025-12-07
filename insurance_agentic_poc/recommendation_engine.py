# recommendation_engine.py
"""
Intelligent recommendation engine based on user profile and preferences.
Suggests best-fit plans, coverage amounts, riders, and alternatives.
"""
from typing import List, Dict, Any
from data_plans import DUMMY_PLANS

def get_coverage_recommendation(policy_type: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend ideal coverage amount based on user profile.
    """
    age = user_profile.get("age", 35)
    family_size = user_profile.get("family_size", 1)
    occupation = user_profile.get("occupation", "")

    recommendations = {}

    if policy_type == "home":
        # Home coverage: based on assumed property value
        # For demo, estimate based on family size and income proxy
        base_coverage = 300_000  # Base ₹30 lakh
        family_multiplier = min(family_size * 0.1, 0.5)
        recommended = base_coverage * (1 + family_multiplier)
        recommendations = {
            "min": base_coverage,
            "recommended": int(recommended),
            "max": base_coverage * 2,
            "reason": f"Based on family size ({family_size}) and location in moderate-risk area.",
        }

    elif policy_type == "health":
        base_coverage = 300_000 if family_size == 1 else 500_000
        age_factor = 1 + (age - 25) * 0.02  # Increases with age
        family_factor = 1 + (family_size - 1) * 0.3
        recommended = int(base_coverage * age_factor * family_factor)
        recommendations = {
            "min": 300_000,
            "recommended": recommended,
            "max": 2_000_000,
            "reason": f"Based on age ({age}), family size ({family_size}), and typical medical costs.",
        }

    elif policy_type == "renters":
        # Estimate belongings
        base = 250_000
        recommended = base * family_size
        recommendations = {
            "min": 100_000,
            "recommended": recommended,
            "max": 500_000,
            "reason": f"Based on family size and typical renter belongings. Make a list to be sure!",
        }

    elif policy_type == "auto":
        # Standard liability + collision
        recommendations = {
            "min": 100_000,
            "recommended": 200_000,
            "max": 500_000,
            "reason": "Standard recommendation: ₹2–5 lakh liability, collision coverage.",
        }

    return recommendations

def get_rider_recommendations(policy_type: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recommend suitable riders/add-ons based on user profile.
    """
    riders = []
    age = user_profile.get("age", 35)
    family_size = user_profile.get("family_size", 1)
    occupation = user_profile.get("occupation", "").lower()

    if policy_type == "health":
        riders.append({
            "name": "Critical Illness Rider",
            "reason": "Covers major illnesses like cancer, heart disease. Good for families.",
            "cost_increase": "~10%",
            "recommended": family_size > 1,
        })
        riders.append({
            "name": "Accidental Cover",
            "reason": "Covers accidents, fractures, emergency care.",
            "cost_increase": "~5%",
            "recommended": True,
        })
        if age > 50:
            riders.append({
                "name": "Senior Care Rider",
                "reason": "Age 50+: Extra coverage for age-related conditions.",
                "cost_increase": "~15%",
                "recommended": True,
            })

    elif policy_type == "auto":
        riders.append({
            "name": "Zero Depreciation",
            "reason": "Car age < 5 years? This rider pays full repair cost (no depreciation).",
            "cost_increase": "~12%",
            "recommended": True,
        })
        riders.append({
            "name": "Roadside Assistance",
            "reason": "If you travel frequently or drive long distances.",
            "cost_increase": "~3%",
            "recommended": "travel" in occupation or "driver" in occupation,
        })
        riders.append({
            "name": "Accidental Cover",
            "reason": "Covers accidental injury while driving.",
            "cost_increase": "~8%",
            "recommended": True,
        })

    elif policy_type == "home":
        riders.append({
            "name": "Home Maintenance Rider",
            "reason": "Covers accidental damage like broken pipes, electrical issues.",
            "cost_increase": "~4%",
            "recommended": True,
        })
        if family_size > 2:
            riders.append({
                "name": "Burglary/Theft Protection",
                "reason": "Larger household = higher theft risk.",
                "cost_increase": "~6%",
                "recommended": True,
            })

    return riders

def rank_plans_for_user(plans: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Rank plans based on best fit for user profile.
    Returns top 3: best-value, ideal-coverage, and alternative.
    """
    if not plans:
        return []

    # Score each plan
    scored = []
    for plan in plans:
        score = 0

        # Rating + reviews factor
        rating = float(plan.get("customer_rating", 3.0))
        reviews = int(plan.get("number_of_reviews", 0))
        score += rating * 25
        score += min(reviews / 100, 10)  # Normalize reviews

        # Value factor (coverage-to-premium ratio)
        premium = float(plan.get("adjusted_annual_premium_usd", 1000))
        coverage = float(plan.get("coverage_amount_usd", 100_000))
        if premium > 0:
            value_ratio = coverage / premium
            score += value_ratio / 100

        # Family size factor
        family_size = user_profile.get("family_size", 1)
        if family_size > 1 and "family" in plan.get("plan_name", "").lower():
            score += 10

        scored.append({"plan": plan, "fit_score": score})

    scored.sort(key=lambda x: x["fit_score"], reverse=True)

    # Return top 3 with categories
    result = []
    if len(scored) > 0:
        result.append({
            "category": "🏆 Best Value",
            **scored[0]["plan"],
            "reason": "Highest rating + good coverage-to-premium ratio.",
        })
    if len(scored) > 1:
        result.append({
            "category": "⭐ Ideal Coverage",
            **scored[1]["plan"],
            "reason": "Best coverage amount for your profile.",
        })
    if len(scored) > 2:
        result.append({
            "category": "💡 Alternative",
            **scored[2]["plan"],
            "reason": "Good option if top choices don't fit.",
        })

    return result

def get_personalized_recommendation_text(policy_type: str, user_profile: Dict[str, Any], recommended_plans: List[Dict[str, Any]]) -> str:
    """
    Generate personalized recommendation text.
    """
    age = user_profile.get("age", 35)
    family_size = user_profile.get("family_size", 1)
    occupation = user_profile.get("occupation", "")

    text = f"""
### 📋 Your Personalized Recommendation

**Your Profile:**
- Age: {age}
- Family Size: {family_size}
- Occupation: {occupation if occupation else 'Not specified'}

**Why you need {policy_type.title()} insurance:**
"""

    if policy_type == "health":
        text += "- Medical emergencies can cost ₹1–50+ lakh. Insurance covers it.\n"
        if age > 45:
            text += "- At your age, health risks increase. Early enrollment = lower premiums.\n"
        if family_size > 1:
            text += "- Family plan protects everyone with one policy.\n"

    elif policy_type == "home":
        text += "- Fire, theft, or natural disaster can destroy everything. Insurance restores it.\n"
        text += "- If you have a mortgage, lenders require home insurance.\n"
        if family_size > 2:
            text += "- Large families need more coverage for belongings.\n"

    elif policy_type == "auto":
        text += "- Required by law in most places.\n"
        text += "- One accident can cost lakhs in repairs or liability claims.\n"

    text += f"\n**Our recommendations for you:**\n"
    for i, plan in enumerate(recommended_plans[:3], 1):
        text += f"\n{i}. **{plan.get('category', '')} - {plan.get('plan_name')}** by {plan.get('company_name')}\n"
        text += f"   - Premium: ₹{plan.get('adjusted_annual_premium_usd', 0):,.0f}/year\n"
        text += f"   - Coverage: ₹{plan.get('coverage_amount_usd', 0):,.0f}\n"
        text += f"   - Rating: {plan.get('customer_rating', 0)} ⭐ ({plan.get('number_of_reviews', 0)} reviews)\n"

    text += "\n**Next Steps:**\n"
    text += "1. Click 'Buy Now' on your preferred plan.\n"
    text += "2. Customize riders and coverage if needed.\n"
    text += "3. Upload ID for quick KYC.\n"
    text += "4. Complete payment (takes ~2 minutes).\n"
    text += "5. Policy issued instantly!\n"

    return text
