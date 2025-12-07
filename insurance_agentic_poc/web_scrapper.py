#!/usr/bin/env python3
"""
BeautifulSoup + Ollama Insurance Scraper PoC

This is a standalone script to test LLM-powered scraping without ScrapeGraphAI.

What it does:
1) Asks you for a REAL URL (insurance listing / product page you are allowed to scrape).
2) Fetches the webpage using requests + parses with BeautifulSoup.
3) Extracts text content and sends it to Ollama for LLM-based extraction.
4) Returns insurance plans as structured JSON.

Requirements:
    pip install requests beautifulsoup4

    # Also: Ollama running and a model pulled (e.g. llama3.1)
    ollama run llama3.1   # first time to pull
"""

import json
import requests
from typing import Any, Dict
from bs4 import BeautifulSoup

from .ollama_client import chat_ollama


def fetch_and_parse_url(url: str) -> str:
    """
    Fetch a URL and extract text content using BeautifulSoup.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # Remove script and style tags
    for tag in soup(["script", "style", "meta", "noscript"]):
        tag.decompose()

    # Get text
    text = soup.get_text(separator="\n", strip=True)
    return text


def extract_plans_with_ollama(page_text: str) -> list[Dict[str, Any]]:
    """
    Send the page text to Ollama and ask it to extract insurance plans as JSON.
    """
    system_prompt = """
You are an expert at extracting insurance product information from webpage text.

From the given webpage text, identify all insurance products/plans and return them as JSON.
For each plan, extract (if present):

- companyName: Company offering the plan
- planName: Name of the insurance plan
- insuranceType: Type of insurance (e.g. "home", "auto", "health", "renters", "fire")
- location: Geographic region/state if mentioned (else null)
- priceText: Premium/price as shown on the page
- coverageText: Coverage amount or limit description
- keyBenefits: List of 2-5 key benefits from the page
- keyLimitations: List of 2-5 key exclusions/limitations from the page

Rules:
- ONLY extract information that is explicitly stated on the page.
- Do NOT make up or infer numeric values.
- If a field is not present, set it to null or an empty list.
- Return STRICT JSON only, no extra text or markdown.

Output format:
[
  {
    "companyName": "...",
    "planName": "...",
    "insuranceType": "...",
    "location": null,
    "priceText": "...",
    "coverageText": "...",
    "keyBenefits": ["...", "..."],
    "keyLimitations": ["...", "..."]
  }
]

If no insurance plans found, return an empty array: []
""".strip()

    # Send to Ollama
    response = chat_ollama(system_prompt, page_text)

    # Try to extract JSON from the response
    try:
        # Try direct JSON parsing
        plans = json.loads(response.strip())
    except json.JSONDecodeError:
        # Try to find JSON in the response (in case there's extra text)
        import re
        json_match = re.search(r"\[.*\]", response, re.DOTALL)
        if json_match:
            try:
                plans = json.loads(json_match.group())
            except json.JSONDecodeError:
                plans = []
        else:
            plans = []

    return plans if isinstance(plans, list) else []


def main():
    print("=== BeautifulSoup + Ollama Insurance Scraper PoC ===\n")
    print("Give me a REAL URL (insurance-related) that you're allowed to scrape.\n")

    url = input("Enter URL (must start with http:// or https://): ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return

    if not (url.startswith("http://") or url.startswith("https://")):
        print("Invalid URL. It must start with http:// or https://")
        return

    print("\nFetching and parsing webpage...\n")

    try:
        page_text = fetch_and_parse_url(url)
        print(f"✓ Fetched {len(page_text)} characters of text.\n")
    except requests.RequestException as e:
        print(f"✗ Error fetching URL: {e}\n")
        return

    # Truncate if too long (Ollama can struggle with very long contexts)
    max_chars = 8000
    if len(page_text) > max_chars:
        print(f"Page text is {len(page_text)} chars; truncating to {max_chars}...\n")
        page_text = page_text[:max_chars]

    print("Sending to Ollama for LLM-based extraction...\n")

    try:
        plans = extract_plans_with_ollama(page_text)
    except Exception as e:
        print(f"✗ Error calling Ollama: {e}\n")
        print("Make sure Ollama is running: ollama serve\n")
        return

    print("=== Extracted Insurance Plans ===\n")

    if not plans:
        print("No insurance plans found on this page.")
    else:
        print(json.dumps(plans, indent=2))

    print("\n" + "=" * 50)
    print("Note:")
    print("- Make sure this URL is allowed to be scraped (check robots.txt / ToS).")
    print("- Ollama must be running with a model available (e.g., ollama run llama3.1)")
    print("- Results quality depends on the page structure and Ollama model.\n")


if __name__ == "__main__":
    main()
