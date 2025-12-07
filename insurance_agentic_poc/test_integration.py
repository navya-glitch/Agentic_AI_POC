"""Test script to verify the integration of scrap.py and data_scraper.py"""

from data_scraper import InsuranceScraper, InsuranceScraperAgent, scrape_insurance_data

print("=" * 70)
print("TESTING INTEGRATED SCRAPERS")
print("=" * 70)

# Test 1: InsuranceScraperAgent initialization
print("\n[TEST 1] Testing InsuranceScraperAgent...")
try:
    agent = InsuranceScraperAgent()
    print("✓ InsuranceScraperAgent initialized successfully")
    
    # Test static data loading
    static_data = agent.load_static_data()
    print(f"✓ Static data loaded: {list(static_data.keys())}")
    
    # Test getting company data
    state_farm_data = agent.get_company_static_data("State Farm")
    if state_farm_data:
        print(f"✓ State Farm data retrieved:")
        print(f"  - Company: {state_farm_data.get('company_name')}")
        print(f"  - Founded: {state_farm_data.get('founded_year')}")
        print(f"  - Headquarters: {state_farm_data.get('headquarters')}")
        print(f"  - Product Types: {len(state_farm_data.get('product_types', []))}")
        print(f"  - Covered Items: {len(state_farm_data.get('standard_coverage', {}).get('covered', []))}")
        print(f"  - Not Covered Items: {len(state_farm_data.get('standard_coverage', {}).get('not_covered', []))}")
        print(f"  - Third-Party Partners: {len(state_farm_data.get('third_party_partners', []))}")
        # Verify logo_url is NOT in the data (should be excluded from UI)
        if 'logo_url' in state_farm_data:
            print("  ⚠️  WARNING: logo_url found in data (should be excluded from UI)")
        else:
            print("  ✓ logo_url not exposed (correct)")
    else:
        print("✗ Could not retrieve State Farm data")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: InsuranceScraper (original scraper)
print("\n[TEST 2] Testing InsuranceScraper...")
try:
    scraper = InsuranceScraper()
    print("✓ InsuranceScraper initialized successfully")
    
    # Test scraping
    plans = scrape_insurance_data(['home'], 'CA')
    print(f"✓ Scraped {len(plans)} plans")
    
    if plans:
        sample = plans[0]
        print(f"✓ Sample plan structure:")
        print(f"  - Insurer: {sample.get('insurer')}")
        print(f"  - Plan Name: {sample.get('plan_name')}")
        print(f"  - Premium: ${sample.get('annual_premium')}")
        print(f"  - Coverage: ${sample.get('coverage_amount')}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Integration - Both scrapers working together
print("\n[TEST 3] Testing Integration...")
try:
    # Get plans from InsuranceScraper
    plans = scrape_insurance_data(['home'], 'CA')
    
    if plans:
        plan = plans[0]
        company_name = plan.get('insurer')
        
        # Get company details from InsuranceScraperAgent
        company_data = agent.get_company_static_data(company_name)
        
        if company_data:
            print(f"✓ Integration successful!")
            print(f"  - Plan from InsuranceScraper: {plan.get('plan_name')}")
            print(f"  - Company data from InsuranceScraperAgent: {company_data.get('company_name')}")
            print(f"  - Can combine both data sources ✓")
        else:
            print(f"⚠️  Plan found but no company data for {company_name}")
    else:
        print("⚠️  No plans found to test integration")
        
except Exception as e:
    print(f"✗ Integration error: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)

