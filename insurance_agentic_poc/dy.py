import json
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import os
from urllib.parse import quote_plus

class InsuranceScraperAgent:
    def __init__(self):
        self.static_data_file = "insurance_static_data.json"
        self.output_file = "insurance_scraped_data.json"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.initialize_static_data()
        
    def initialize_static_data(self):
        """Create static data file with pre-populated information"""
        if not os.path.exists(self.static_data_file):
            static_data = {
                "State Farm": {
                    "company_name": "State Farm Insurance",
                    "logo_url": "https://www.statefarm.com/content/dam/sf-www/images/sf-logo.svg",
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
                    "logo_url": "https://www.aig.com/content/dam/aig/america-canada/us/images/logo/aig-logo.svg",
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
            
            with open(self.static_data_file, 'w') as f:
                json.dump(static_data, f, indent=4)
            print(f"✓ Static data file created: {self.static_data_file}")
        else:
            print(f"✓ Static data file already exists: {self.static_data_file}")
    
    def load_static_data(self):
        """Load static data from file"""
        with open(self.static_data_file, 'r') as f:
            return json.load(f)
    
    def query_ollama(self, prompt, model="gemma3:1b"):
        """Query Ollama with Gemma model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()['response']
            else:
                print(f"✗ Ollama error: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Ollama connection error: {e}")
            return None
    
    def generate_search_query(self, company, data_point, location=None):
        """Use Ollama to generate optimized search query"""
        location_context = f" in {location}" if location else ""
        prompt = f"""Generate a concise Google search query to find: {data_point} for {company}{location_context}.
        Return only the search query, no explanation. Make it specific and likely to return official data.
        Examples: 'State Farm claims paid 2024', 'AIG customer statistics 2023'
        Query:"""
        
        query = self.query_ollama(prompt)
        if query:
            query = query.strip().replace('"', '')
            return query
        return f"{company} {data_point}{location_context}"
    
    def google_search(self, query, num_results=5):
        """Perform Google search and return URLs"""
        print(f"   🔍 Searching: {query}")
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
        
        try:
            time.sleep(2)  # Rate limiting
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            urls = []
            for g in soup.find_all('div', class_='g'):
                link = g.find('a', href=True)
                if link and link['href'].startswith('http'):
                    urls.append(link['href'])
            
            return urls[:num_results]
        except Exception as e:
            print(f"   ✗ Search error: {e}")
            return []
    
    def scrape_page(self, url):
        """Scrape content from a URL"""
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            # Limit text size for Ollama
            return text[:5000]
        except Exception as e:
            print(f"   ✗ Scraping error for {url}: {e}")
            return ""
    
    def extract_information(self, text, data_point, company):
        """Use Ollama to extract specific information from scraped text"""
        prompt = f"""From the following text, extract information about: {data_point} for {company}.
        Be specific and cite numbers if available. If information is not found, say "NOT FOUND".
        Keep response under 100 words and factual.
        
        Text: {text[:3000]}
        
        Answer:"""
        
        result = self.query_ollama(prompt)
        return result if result else "Unable to extract information"
    
    def scrape_dynamic_data(self, company, location):
        """Scrape all dynamic data points"""
        print(f"\n📊 Scraping dynamic data for {company}...")
        
        dynamic_queries = {
            "claims_settled_recent": f"claims settled 2024",
            "customers_past_5_years": f"number of customers past 5 years statistics",
            "products_sold_location": f"products sold {location}",
            "active_policyholders_location": f"active policyholders {location}",
            "coverage_trends_location": f"most popular coverage {location}",
            "recommended_coverage_location": f"recommended insurance coverage {location} climate risks",
            "current_deductibles": f"typical deductibles 2024"
        }
        
        results = {}
        
        for key, query_base in dynamic_queries.items():
            print(f"\n   📋 {key.replace('_', ' ').title()}:")
            
            # Generate optimized query using Ollama
            search_query = self.generate_search_query(company, query_base, location)
            
            # Google search
            urls = self.google_search(search_query)
            
            if not urls:
                results[key] = "No search results found"
                continue
            
            # Scrape and extract from first few results
            extracted_info = []
            for url in urls[:3]:  # Check first 3 results
                print(f"   📄 Analyzing: {url[:60]}...")
                content = self.scrape_page(url)
                if content:
                    info = self.extract_information(content, query_base, company)
                    if info and "NOT FOUND" not in info.upper():
                        extracted_info.append({
                            "source": url,
                            "information": info
                        })
                        break  # Found relevant info, move to next query
            
            results[key] = extracted_info if extracted_info else "Information not found in search results"
        
        return results
    
    def run(self):
        """Main execution flow"""
        print("=" * 70)
        print("🏢 INSURANCE DATA SCRAPING AGENT")
        print("=" * 70)
        
        # Check Ollama connection
        print("\n🤖 Checking Ollama connection...")
        test_response = self.query_ollama("Say 'ready' if you can respond.", model="gemma3:1b")
        if not test_response:
            print("✗ Cannot connect to Ollama. Make sure it's running on http://localhost:11434")
            print("  Run: ollama serve")
            return
        print("✓ Ollama is ready!")
        
        # Load static data
        static_data = self.load_static_data()
        
        # Interactive prompts
        print("\n" + "=" * 70)
        print("📍 Location-based Analysis")
        location = input("Enter location (e.g., California, New York, Texas): ").strip()
        if not location:
            location = "United States"
        
        print(f"\n✓ Analyzing for location: {location}")
        
        # Process both companies
        final_results = {
            "scrape_date": datetime.now().isoformat(),
            "location": location,
            "companies": {}
        }
        
        for company in ["State Farm", "AIG"]:
            print(f"\n{'=' * 70}")
            print(f"Processing: {company}")
            print(f"{'=' * 70}")
            
            company_data = {
                "static_data": static_data[company],
                "dynamic_data": self.scrape_dynamic_data(company, location)
            }
            
            final_results["companies"][company] = company_data
        
        # Save results
        with open(self.output_file, 'w') as f:
            json.dump(final_results, f, indent=4)
        
        print(f"\n{'=' * 70}")
        print(f"✓ Scraping complete! Results saved to: {self.output_file}")
        print(f"{'=' * 70}")
        
        # Display summary
        self.display_summary(final_results)
    
    def display_summary(self, results):
        """Display a summary of results"""
        print("\n📊 SUMMARY:")
        print(f"Location: {results['location']}")
        print(f"Scrape Date: {results['scrape_date']}")
        
        for company, data in results['companies'].items():
            print(f"\n{company}:")
            print(f"  Founded: {data['static_data']['founded_year']}")
            print(f"  Products: {len(data['static_data']['product_types'])} types")
            print(f"  Partners: {len(data['static_data']['third_party_partners'])} companies")
            # Print the actual dynamic data (pretty JSON) instead of just the length
            try:
                pretty = json.dumps(data['dynamic_data'], indent=2, ensure_ascii=False)
            except Exception:
                pretty = str(data['dynamic_data'])
            print(f"  Dynamic data points collected: {pretty}")

if __name__ == "__main__":
    agent = InsuranceScraperAgent()
    agent.run()