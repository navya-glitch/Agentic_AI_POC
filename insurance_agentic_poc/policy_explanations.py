# policy_explanations.py
"""
Plain-language explanations for each policy type and common questions.
Makes complex insurance terms simple and understandable.
"""

POLICY_EXPLANATIONS = {
    "home": {
        "what_is_it": "Comprehensive coverage for residential property, protecting against structural damage, loss of personal property, and third-party liability. Includes building coverage, contents protection, and liability across various perils.",
        "what_covered": [
            "Structural damage and building materials protection",
            "Personal property and household contents coverage",
            "Third-party liability and bodily injury exposure",
            "Additional living expenses coverage",
        ],
        "what_not_covered": [
            "Flooding (requires separate flood insurance)",
            "Earthquakes (requires separate earthquake policy)",
            "Wear and tear or poor maintenance",
            "Business equipment or business use",
        ],
        "why_price_varies": [
            "**House value**: More expensive homes = higher premiums",
            "**Age of home**: Older homes cost more to insure",
            "**Location**: High-risk areas (wildfire, flood zones) cost more",
            "**Safety features**: Alarms and updated systems lower premiums",
            "**Claims history**: Previous claims increase your premium",
        ],
        "best_for": "Homeowners who want to protect their property investment and avoid financial disaster if something goes wrong.",
        "coverage_amount_guide": "Usually 80–100% of your home's rebuild value (not land value). E.g., if rebuilding costs ₹50 lakh, get ₹50 lakh coverage.",
    },
    "renters": {
        "what_is_it": "Renters insurance protects your belongings and covers liability if someone is injured in your rental apartment. Landlord's insurance doesn't cover your stuff.",
        "what_covered": [
            "Your personal belongings (furniture, clothes, electronics)",
            "Liability if you accidentally injure someone or damage their property",
            "Living expenses if your rental becomes unlivable (temporary housing)",
            "Medical payments for accidental injury to guests",
        ],
        "what_not_covered": [
            "Damage to the building itself (landlord's responsibility)",
            "Items of extremely high value without special riders",
            "Damage from riots or war",
            "Pets (unless you add a pet rider)",
        ],
        "why_price_varies": [
            "**Coverage amount**: Insuring ₹5 lakh of belongings costs less than ₹20 lakh",
            "**Deductible**: Higher deductible = lower premium (you pay more out-of-pocket)",
            "**Location**: High-crime areas have higher premiums",
            "**Number of roommates**: More people = more risk",
        ],
        "best_for": "Renters who want affordable protection for their belongings without paying for the building insurance.",
        "coverage_amount_guide": "List all your belongings (furniture, TV, laptop, clothes). Total it up—that's your coverage need. Usually ₹3–10 lakh for most renters.",
    },
    "auto": {
        "what_is_it": "Auto insurance protects you financially if your car is damaged, stolen, or if you injure someone in an accident.",
        "what_covered": [
            "Liability: You damage another car or injure someone (required by law)",
            "Collision: Your car hits something or is hit (covers repair cost minus deductible)",
            "Comprehensive: Theft, fire, flooding, natural disasters",
            "Uninsured motorist: Someone without insurance hits you",
        ],
        "what_not_covered": [
            "Wear and tear (tires, brakes, batteries)",
            "Mechanical breakdown",
            "Damage from racing or stunt driving",
            "Damage while driving for commercial purposes (Uber, taxi)",
        ],
        "why_price_varies": [
            "**Car age**: Older cars cost less to insure (lower repair costs)",
            "**Car model**: Sports cars = higher premiums; sedans = lower",
            "**Your driving record**: Accidents and tickets increase premium",
            "**Annual mileage**: More driving = more risk",
            "**Location**: Urban areas = higher premiums; rural = lower",
        ],
        "best_for": "Car owners who want protection from accidents, theft, and legal liability.",
        "coverage_amount_guide": "For liability, state minimums vary; ₹5–10 lakh is typical. For collision/comprehensive, match your car's value.",
    },
    "health": {
        "what_is_it": "Health insurance covers doctor visits, hospital stays, and medical treatments. It protects you from huge medical bills.",
        "what_covered": [
            "Doctor consultations and tests",
            "Hospital room and bed charges",
            "Surgery and anesthesia",
            "Medications and lab tests",
            "Pre- and post-hospitalization care",
        ],
        "what_not_covered": [
            "Cosmetic procedures (unless medically necessary)",
            "Routine wellness (unless plan specifies)",
            "Pre-existing conditions (waiting period applies)",
            "Alternative medicine (unless plan includes)",
        ],
        "why_price_varies": [
            "**Your age**: Younger = cheaper; older = more expensive",
            "**Health conditions**: Pre-existing conditions = higher premium",
            "**Coverage amount**: ₹3 lakh coverage < ₹10 lakh coverage",
            "**Deductible**: Higher deductible = lower premium",
            "**Network hospitals**: Plans with more hospitals = slightly higher premium",
        ],
        "best_for": "Anyone who wants financial protection against medical emergencies and doctor's fees.",
        "coverage_amount_guide": "For individuals: ₹3–5 lakh. For families: ₹10–15 lakh. High-income earners may want ₹20+ lakh.",
    },
    "fire": {
        "what_is_it": "Fire insurance specifically covers damage caused by fire, smoke, and sometimes explosions. Often combined with other policies.",
        "what_covered": [
            "Fire damage to the building and contents",
            "Smoke damage from fire",
            "Explosion or lightning damage",
            "Damage from attempts to extinguish fire",
        ],
        "what_not_covered": [
            "Damage from burning property yourself (intentional)",
            "Theft during or after fire",
            "Loss due to negligence",
            "Damage from war or civil unrest",
        ],
        "why_price_varies": [
            "**Building material**: Concrete building < Wooden building (risk difference)",
            "**Location**: High wildfire zones = higher premium",
            "**Building age**: Older buildings = higher premium",
            "**Safety measures**: Fire extinguishers, alarms = lower premium",
        ],
        "best_for": "Property owners in fire-risk areas (near forests, high-wildfire zones) or those wanting fire-specific coverage.",
        "coverage_amount_guide": "Usually the replacement cost of the property. For a ₹50-lakh house, get ₹50-lakh fire coverage.",
    },
}

COMMON_QUESTIONS = {
    "deductible": {
        "question": "What's a deductible?",
        "answer": "The amount YOU pay out of pocket before insurance kicks in. E.g., if deductible is ₹1,000 and repair costs ₹5,000, you pay ₹1,000 and insurance pays ₹4,000. Higher deductible = lower premium.",
    },
    "premium": {
        "question": "What's a premium?",
        "answer": "The amount you pay (monthly or yearly) to keep your insurance active. Like a subscription fee.",
    },
    "rider": {
        "question": "What's a rider?",
        "answer": "An add-on to your policy that adds extra coverage. E.g., 'Zero Depreciation' rider means your car's value isn't reduced after accidents. Riders cost extra.",
    },
    "coverage": {
        "question": "What's coverage amount?",
        "answer": "The maximum amount the insurance company will pay if something bad happens. E.g., if your home insurance has ₹50-lakh coverage and your house burns down with ₹75 lakh damage, insurance pays only ₹50 lakh.",
    },
    "claim": {
        "question": "What's a claim?",
        "answer": "When you ask the insurance company to pay for something covered by your policy. You file a claim with documents (photos, receipts, reports).",
    },
    "when_buy": {
        "question": "When should I buy insurance?",
        "answer": "ASAP. Insurance protects you from today onwards. The younger/healthier you are, the cheaper it is. Delays = higher premiums.",
    },
}

RIDER_EXPLANATIONS = {
    "zero_depreciation": {
        "name": "Zero Depreciation",
        "applies_to": ["auto"],
        "what_it_does": "Your car's value drops after accidents, but this rider covers the full repair cost without deducting depreciation.",
        "example": "Car damage = ₹1 lakh. Normally insurance pays ₹70,000 (after 30% depreciation). With zero depreciation, they pay full ₹1 lakh.",
        "cost_increase": "Usually 10–15% more expensive.",
    },
    "critical_illness": {
        "name": "Critical Illness Rider",
        "applies_to": ["health"],
        "what_it_does": "If you're diagnosed with a serious illness (cancer, heart attack, stroke), insurance pays a lump sum immediately—no waiting.",
        "example": "You get diagnosed with cancer. Insurance pays ₹10 lakh upfront, even if treatment costs more later.",
        "cost_increase": "Usually 8–12% more expensive.",
    },
    "accidental_cover": {
        "name": "Accidental Cover",
        "applies_to": ["health", "life"],
        "what_it_does": "Covers accidental injuries and death. Important if your job is risky or you travel frequently.",
        "example": "You slip and break your leg. Insurance covers hospital stay and surgery.",
        "cost_increase": "Usually 5–10% more expensive.",
    },
}

def get_policy_explanation(policy_type: str) -> dict:
    """Get plain-language explanation for a policy type."""
    return POLICY_EXPLANATIONS.get(policy_type.lower(), {})

def get_common_question(question_key: str) -> dict:
    """Get answer to a common insurance question."""
    return COMMON_QUESTIONS.get(question_key.lower(), {})

def get_rider_explanation(rider_key: str) -> dict:
    """Get explanation for a specific rider."""
    return RIDER_EXPLANATIONS.get(rider_key.lower(), {})

def format_coverage_checklist(policy_type: str) -> str:
    """Format 'what's covered' and 'what's not' as nice markdown."""
    exp = get_policy_explanation(policy_type)
    text = "### ✅ What's Covered\n"
    for item in exp.get("what_covered", []):
        text += f"- {item}\n"
    text += "\n### ❌ What's NOT Covered\n"
    for item in exp.get("what_not_covered", []):
        text += f"- {item}\n"
    return text
