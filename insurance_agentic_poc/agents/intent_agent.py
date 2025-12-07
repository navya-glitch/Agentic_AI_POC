# agents/intent_agent.py
import json
import re
from typing import Dict, Any, List

from ollama_client import chat_ollama

SUPPORTED_TYPES = ["home", "fire", "renters", "auto", "health"]

US_STATE_CODES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY",
}

RISK_KEYWORDS = {
    "pet": ["pet", "pets", "dog", "dogs", "cat", "cats"],
    "swimming_pool": ["swimming pool", "pool"],
}


def _heuristic_policy_type(text: str) -> str:
    t = text.lower()
    for p in SUPPORTED_TYPES:
        if p in t:
            return p
    # simple synonyms
    if any(w in t for w in ["house", "home insurance", "villa", "apartment", "flat"]):
        return "home"
    if "tenant" in t or "renter" in t:
        return "renters"
    return "home"


def _heuristic_risk_factors(text: str) -> List[str]:
    text_low = text.lower()
    risks = set()
    for risk, kws in RISK_KEYWORDS.items():
        for kw in kws:
            if kw in text_low:
                risks.add(risk)
                break
    return list(risks)


def _find_state_codes_in_text(text: str) -> List[str]:
    """
    Find all 2-letter US state codes that appear as separate words
    in the query (e.g. 'in CA', 'NY', 'TX').
    """
    codes = []
    upper = text.upper()
    for code in US_STATE_CODES:
        pattern = r"\b" + re.escape(code) + r"\b"
        if re.search(pattern, upper):
            codes.append(code)
    return codes


def extract_intent(user_query: str) -> Dict[str, Any]:
    """
    Intent Understanding Agent:
    1) Ask LLM to extract structured intent.
    2) Apply deterministic heuristics to FIX / FILL:
       - policyType
       - riskFactors (pet, swimming pool)
       - location (prefer state codes present in user query)
    """

    system_prompt = f"""
You are an Intent Understanding Agent for an insurance e-commerce search system.

Your job:
1. Read the user's natural language query.
2. Infer:
   - policyType: one of {SUPPORTED_TYPES}
   - riskFactors: list of short strings, e.g. ["pet", "swimming_pool"]
   - location: city or state if mentioned, else "Unknown"
   - intent: one of ["Explore", "Comparison", "Buy"]

Very important:
- If the query mentions pets, animals, dogs, or cats, include "pet" in riskFactors.
- If the query mentions pool or swimming pool, include "swimming_pool" in riskFactors.
- If the query includes a 2-letter US state code (like CA, NY, TX), set location to that code.

Respond ONLY as strict JSON, no extra text, with this schema:
{{
  "policyType": "<one of: {', '.join(SUPPORTED_TYPES)}>",
  "riskFactors": ["<risk1>", "<risk2>"],
  "location": "<string or 'Unknown'>",
  "intent": "<Explore|Comparison|Buy>",
  "rawQueryEcho": "<echo original query>"
}}
"""

    # ---- 1) LLM extraction ----
    content = chat_ollama(system_prompt, user_query).strip()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "policyType": _heuristic_policy_type(user_query),
            "riskFactors": [],
            "location": "Unknown",
            "intent": "Comparison",
            "rawQueryEcho": user_query,
        }

    # ---- 2) Heuristic correction/augmentation ----

    # policyType
    policy = parsed.get("policyType") or _heuristic_policy_type(user_query)
    if policy not in SUPPORTED_TYPES:
        policy = _heuristic_policy_type(user_query)
    parsed["policyType"] = policy

    # riskFactors: merge LLM output + heuristics
    rf_llm = parsed.get("riskFactors")
    if not isinstance(rf_llm, list):
        rf_llm = []
    rf_llm = [str(x).strip().lower() for x in rf_llm if str(x).strip()]

    rf_heuristic = _heuristic_risk_factors(user_query)
    merged_risks = sorted(set(rf_llm) | set(rf_heuristic))
    parsed["riskFactors"] = merged_risks

    # location: prefer explicit state codes in query
    loc_llm = (parsed.get("location") or "Unknown").upper()
    codes_in_query = _find_state_codes_in_text(user_query)

    if codes_in_query:
        # If the LLM-picked location is one of the explicit codes, keep it,
        # otherwise use the first code detected in the query.
        if loc_llm in codes_in_query:
            loc_final = loc_llm
        else:
            loc_final = codes_in_query[0]
    else:
        # Fall back to LLM if it's at least a valid US state; otherwise Unknown.
        loc_final = loc_llm if loc_llm in US_STATE_CODES else "Unknown"

    parsed["location"] = loc_final

    # intent
    intent = parsed.get("intent", "Comparison")
    if intent not in ["Explore", "Comparison", "Buy"]:
        intent = "Comparison"
    parsed["intent"] = intent

    parsed["rawQueryEcho"] = user_query
    return parsed
