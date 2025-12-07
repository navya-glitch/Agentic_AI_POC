"""
Helpers to read the output JSON produced by `scrap.py` (insurance_scraped_data.json).
This file provides safe accessors so the UI can render scrape metadata and
per-company dynamic findings if the scraping job was run locally.
"""
import json
import os
from typing import Optional, Dict, Any

SCRAP_OUTPUT_FILE = "insurance_scraped_data.json"


def _load_output() -> Optional[Dict[str, Any]]:
    if not os.path.exists(SCRAP_OUTPUT_FILE):
        return None
    try:
        with open(SCRAP_OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_scrape_metadata() -> Optional[Dict[str, Any]]:
    """Return top-level metadata from the scrape output (scrape_date, location).

    Returns None if file missing or invalid.
    """
    data = _load_output()
    if not data:
        return None
    return {"scrape_date": data.get("scrape_date"), "location": data.get("location")}


def get_company_scrape(company_name: str) -> Optional[Dict[str, Any]]:
    """Return the scraped data for a specific company (static_data + dynamic_data).

    Performs case-insensitive lookup. Returns None if not present.
    """
    data = _load_output()
    if not data:
        return None
    companies = data.get("companies", {})
    if not companies:
        return None

    # Direct lookup
    if company_name in companies:
        return companies[company_name]

    # Case-insensitive / partial matches
    for key in companies:
        if key.lower() == company_name.lower() or key.lower() in company_name.lower() or company_name.lower() in key.lower():
            return companies[key]

    return None
