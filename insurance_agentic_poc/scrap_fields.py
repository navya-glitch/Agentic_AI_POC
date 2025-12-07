"""
Lightweight static fields extracted from `scrap.py` for UI consumption.
This module purposely excludes `logo_url` and heavy/sensitive logic so the UI
can import it without requiring Ollama or network access.
"""
from typing import Dict, Any

SCRAP_STATIC_DATA: Dict[str, Dict[str, Any]] = {
    "State Farm": {
        "company_name": "State Farm Insurance",
        "founded_year": 1922,
        "headquarters": "Bloomington, Illinois, USA",
        "third_party_partners": [
            "CARSTAR",
            "Service Master",
            "1-800-WATER-DAMAGE",
            "Paul Davis Restoration",
            "Rainbow International",
            "Glass America"
        ],
        "standard_coverage": {
            "covered": [
                "Auto collision and comprehensive",
                "Property damage liability",
                "Bodily injury liability",
                "Home fire and theft",
                "Personal liability",
                "Medical payments"
            ],
            "not_covered": [
                "Flood damage (requires separate policy)",
                "Earthquake damage (requires separate policy)",
                "Normal wear and tear",
                "Intentional damage",
                "War or nuclear hazard"
            ]
        },
        "product_types": [
            "Auto Insurance",
            "Home Insurance",
            "Renters Insurance",
            "Life Insurance",
            "Health Insurance",
            "Business Insurance"
        ]
    },
    "AIG": {
        "company_name": "American International Group (AIG)",
        "founded_year": 1919,
        "headquarters": "New York City, New York, USA",
        "third_party_partners": [
            "Crawford & Company",
            "Sedgwick",
            "Gallagher Bassett",
            "Cunningham Lindsey",
            "ESIS (AIG owned)",
            "Vidal (Health Network Partner)"
        ],
        "standard_coverage": {
            "covered": [
                "Commercial property and liability",
                "Auto physical damage",
                "Travel insurance",
                "Accident and health",
                "Workers compensation",
                "Professional liability"
            ],
            "not_covered": [
                "Flood without rider",
                "Earthquake without rider",
                "Acts of war",
                "Nuclear incidents",
                "Intentional acts",
                "Prior known losses"
            ]
        },
        "product_types": [
            "Commercial Insurance",
            "Personal Auto Insurance",
            "Travel Insurance",
            "Accident & Health Insurance",
            "Life Insurance",
            "Homeowners Insurance"
        ]
    }
}


def get_scrap_fields_for_company(company_name: str):
    """Return the static scrap fields for a given company name.

    Performs a case-insensitive lookup and simple normalization.
    Returns None if no metadata is found.
    """
    if not company_name:
        return None

    # Direct match
    if company_name in SCRAP_STATIC_DATA:
        return SCRAP_STATIC_DATA[company_name]

    # Case-insensitive match
    for key in SCRAP_STATIC_DATA:
        if key.lower() == company_name.lower():
            return SCRAP_STATIC_DATA[key]

    # Partial match (e.g., 'State Farm Insurance' -> 'State Farm')
    for key in SCRAP_STATIC_DATA:
        if key.lower() in company_name.lower() or company_name.lower() in key.lower():
            return SCRAP_STATIC_DATA[key]

    return None


def _load_scraped_json() -> dict:
    """Load the JSON file produced by `scrap.py` if present.

    Expected structure (from `scrap.py`):
    {
      "scrape_date": "...",
      "location": "...",
      "companies": {
          "State Farm": {"static_data": {...}, "dynamic_data": {...}},
          "AIG": { ... }
      }
    }
    """
    import os, json

    base = os.path.dirname(__file__)
    path = os.path.join(base, "insurance_scraped_data.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_scrap_fields_for_company(company_name: str):
    """Return merged static fields and scraped JSON fields for a company.

    - Keeps the original static data behavior (case-insensitive matching).
    - Merges in any `dynamic_data` found in `insurance_scraped_data.json` under
      the `companies` key.
    - Excludes `logo_url`.
    """
    if not company_name:
        return None

    # Find static entry using previous logic
    static = None
    if company_name in SCRAP_STATIC_DATA:
        static = SCRAP_STATIC_DATA[company_name]
    else:
        for key in SCRAP_STATIC_DATA:
            if key.lower() == company_name.lower() or key.lower() in company_name.lower() or company_name.lower() in key.lower():
                static = SCRAP_STATIC_DATA[key]
                break

    # Start with a copy of static (without logo_url)
    merged = {}
    if static:
        for k, v in static.items():
            if k == "logo_url":
                continue
            merged[k] = v

    # Load scraped JSON and merge dynamic_data if present
    scraped = _load_scraped_json()
    companies = scraped.get("companies") if isinstance(scraped, dict) else {}
    if isinstance(companies, dict):
        # Try direct match first
        company_scraped = companies.get(company_name)
        if not company_scraped:
            # Try case-insensitive / partial match
            for key in companies:
                if key.lower() == company_name.lower() or key.lower() in company_name.lower() or company_name.lower() in key.lower():
                    company_scraped = companies.get(key)
                    break

        if company_scraped and isinstance(company_scraped, dict):
            dyn = company_scraped.get("dynamic_data")
            if dyn:
                merged["dynamic_data"] = dyn

    # Add top-level scrape metadata if available
    if isinstance(scraped, dict):
        if scraped.get("scrape_date"):
            merged["scrape_date"] = scraped.get("scrape_date")
        if scraped.get("location"):
            merged["scrape_location"] = scraped.get("location")

    return merged if merged else None
