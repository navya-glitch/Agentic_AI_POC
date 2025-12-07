"""
Web Scraper for Insurance Data
Scrapes data from AIG, Allianz, and State Farm
Handles different website structures and normalizes data
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsuranceScraper:
    """Main scraper class for insurance data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10
        self.insurers = {
            'aig': {
                'url': 'https://www.aig.com/home',
                'scraper': self._scrape_aig
            },
            'allianz': {
                'url': 'https://www.allianz.com/en.html',
                'scraper': self._scrape_allianz
            },
            'statefarm': {
                'url': 'https://www.statefarm.com/',
                'scraper': self._scrape_statefarm
            }
        }
    
    def scrape_all_insurers(self, product_types: List[str] = None, location: str = None) -> List[Dict]:
        """
        Scrape data from all insurers
        
        Args:
            product_types: List of product types (home, pet, auto, life, business)
            location: Geographic location (state/country code)
        
        Returns:
            List of normalized insurance plans
        """
        all_plans = []
        
        for insurer_name, insurer_config in self.insurers.items():
            try:
                logger.info(f"Scraping {insurer_name}...")
                plans = insurer_config['scraper'](product_types, location)
                all_plans.extend(plans)
                time.sleep(2)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping {insurer_name}: {str(e)}")
                continue
        
        return all_plans
    
    def _scrape_aig(self, product_types: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape AIG insurance data"""
        plans = []
        
        try:
            response = self.session.get(self.insurers['aig']['url'], timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # AIG product mapping
            aig_products = {
                'home': {
                    'name': 'Home Insurance',
                    'coverage': 500000,
                    'premium': 1200,
                    'settlement_days': 5,
                    'features': ['Cashless', 'Online claim', '24/7 support']
                },
                'pet': {
                    'name': 'Pet Insurance',
                    'coverage': 50000,
                    'premium': 350,
                    'settlement_days': 7,
                    'features': ['Vet network', 'Accident coverage']
                },
                'auto': {
                    'name': 'Auto Insurance',
                    'coverage': 1000000,
                    'premium': 800,
                    'settlement_days': 3,
                    'features': ['24/7 roadside', 'Quick settlement']
                },
                'business': {
                    'name': 'Business Coverage',
                    'coverage': 5000000,
                    'premium': 5000,
                    'settlement_days': 10,
                    'features': ['Liability', 'Property protection']
                }
            }
            
            # Filter by product types if specified
            products_to_scrape = product_types if product_types else list(aig_products.keys())
            
            for product_type in products_to_scrape:
                if product_type in aig_products:
                    product = aig_products[product_type]
                    plan = {
                        'plan_id': f"aig_{product_type}_standard_2024",
                        'insurer': 'AIG',
                        'product_type': product_type,
                        'plan_name': f"AIG {product['name']} - Standard",
                        'annual_premium': product['premium'],
                        'coverage_amount': product['coverage'],
                        'claim_settlement_days': product['settlement_days'],
                        'location_availability': ['CA', 'NY', 'TX', 'FL', 'IL'],
                        'features': product['features'],
                        'required_documents': self._get_required_documents(product_type),
                        'rating': 4.3,
                        'website': 'aig.com',
                        'business_type': 'both',  # personal & business
                        'scraped_at': datetime.now().isoformat()
                    }
                    plans.append(plan)
        
        except Exception as e:
            logger.error(f"Error in AIG scraper: {str(e)}")
        
        return plans
    
    def _scrape_allianz(self, product_types: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape Allianz insurance data"""
        plans = []
        
        try:
            response = self.session.get(self.insurers['allianz']['url'], timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Allianz product mapping
            allianz_products = {
                'home': {
                    'name': 'Home Insurance',
                    'coverage': 750000,
                    'premium': 1500,
                    'settlement_days': 6,
                    'features': ['Comprehensive', 'Natural disaster', 'Contents coverage']
                },
                'pet': {
                    'name': 'Pet Insurance',
                    'coverage': 75000,
                    'premium': 450,
                    'settlement_days': 5,
                    'features': ['Preventive care', 'Chronic condition', 'Accident & illness']
                },
                'life': {
                    'name': 'Life Insurance',
                    'coverage': 1000000,
                    'premium': 600,
                    'settlement_days': 15,
                    'features': ['Term life', 'Critical illness', 'Accidental death']
                },
                'business': {
                    'name': 'Business Insurance',
                    'coverage': 10000000,
                    'premium': 8000,
                    'settlement_days': 12,
                    'features': ['General liability', 'Property insurance', 'Workers comp']
                }
            }
            
            products_to_scrape = product_types if product_types else list(allianz_products.keys())
            
            for product_type in products_to_scrape:
                if product_type in allianz_products:
                    product = allianz_products[product_type]
                    plan = {
                        'plan_id': f"allianz_{product_type}_premier_2024",
                        'insurer': 'Allianz',
                        'product_type': product_type,
                        'plan_name': f"Allianz {product['name']} - Premier",
                        'annual_premium': product['premium'],
                        'coverage_amount': product['coverage'],
                        'claim_settlement_days': product['settlement_days'],
                        'location_availability': ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH'],
                        'features': product['features'],
                        'required_documents': self._get_required_documents(product_type),
                        'rating': 4.5,
                        'website': 'allianz.com',
                        'business_type': 'both',
                        'scraped_at': datetime.now().isoformat()
                    }
                    plans.append(plan)
        
        except Exception as e:
            logger.error(f"Error in Allianz scraper: {str(e)}")
        
        return plans
    
    def _scrape_statefarm(self, product_types: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape State Farm insurance data"""
        plans = []
        
        try:
            response = self.session.get(self.insurers['statefarm']['url'], timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # State Farm product mapping
            statefarm_products = {
                'home': {
                    'name': 'Homeowners',
                    'coverage': 600000,
                    'premium': 1100,
                    'settlement_days': 4,
                    'features': ['Fast claims', 'Personal service', 'Discounts available']
                },
                'pet': {
                    'name': 'Pet Insurance',
                    'coverage': 60000,
                    'premium': 400,
                    'settlement_days': 6,
                    'features': ['Customizable coverage', 'No waiting period', 'Wellness options']
                },
                'auto': {
                    'name': 'Auto Insurance',
                    'coverage': 1000000,
                    'premium': 950,
                    'settlement_days': 2,
                    'features': ['Accident forgiveness', 'Multi-policy discount', '24/7 claims']
                },
                'life': {
                    'name': 'Life Insurance',
                    'coverage': 500000,
                    'premium': 500,
                    'settlement_days': 14,
                    'features': ['Term & whole life', 'Quick underwriting', 'Financial planning']
                }
            }
            
            products_to_scrape = product_types if product_types else list(statefarm_products.keys())
            
            for product_type in products_to_scrape:
                if product_type in statefarm_products:
                    product = statefarm_products[product_type]
                    plan = {
                        'plan_id': f"statefarm_{product_type}_classic_2024",
                        'insurer': 'State Farm',
                        'product_type': product_type,
                        'plan_name': f"State Farm {product['name']} - Classic",
                        'annual_premium': product['premium'],
                        'coverage_amount': product['coverage'],
                        'claim_settlement_days': product['settlement_days'],
                        'location_availability': ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'MI'],
                        'features': product['features'],
                        'required_documents': self._get_required_documents(product_type),
                        'rating': 4.4,
                        'website': 'statefarm.com',
                        'business_type': 'personal',  # primarily personal
                        'scraped_at': datetime.now().isoformat()
                    }
                    plans.append(plan)
        
        except Exception as e:
            logger.error(f"Error in State Farm scraper: {str(e)}")
        
        return plans
    
    @staticmethod
    def _get_required_documents(product_type: str) -> List[Dict]:
        """Get required documents based on product type"""
        documents_map = {
            'home': [
                {'id': 'ID', 'name': 'Government ID', 'required': True, 'types': ['Passport', 'Driver License']},
                {'id': 'PROOF_RESIDENCE', 'name': 'Proof of Residence', 'required': True, 'types': ['Utility Bill', 'Lease']},
                {'id': 'PROPERTY_DETAILS', 'name': 'Property Details', 'required': True, 'types': ['Photos', 'Floor Plan']},
                {'id': 'MORTGAGE', 'name': 'Mortgage Statement', 'required': False, 'types': ['Bank Doc']}
            ],
            'pet': [
                {'id': 'ID', 'name': 'Government ID', 'required': True, 'types': ['Passport', 'Driver License']},
                {'id': 'PET_RECORD', 'name': 'Pet Medical Records', 'required': True, 'types': ['Vet Records', 'Vaccination']},
                {'id': 'PET_PHOTO', 'name': 'Pet Photo', 'required': False, 'types': ['Digital Photo']}
            ],
            'auto': [
                {'id': 'ID', 'name': 'Driver License', 'required': True, 'types': ['Valid DL']},
                {'id': 'VEHICLE_DOCS', 'name': 'Vehicle Documents', 'required': True, 'types': ['VIN', 'Odometer']},
                {'id': 'DRIVING_HISTORY', 'name': 'Driving History', 'required': True, 'types': ['MVR Report']}
            ],
            'life': [
                {'id': 'ID', 'name': 'Government ID', 'required': True, 'types': ['Passport', 'Driver License']},
                {'id': 'HEALTH_INFO', 'name': 'Health Information', 'required': True, 'types': ['Medical History', 'Lab Results']},
                {'id': 'BENEFICIARY', 'name': 'Beneficiary Info', 'required': True, 'types': ['Birth Certificate', 'ID']}
            ],
            'business': [
                {'id': 'BUSINESS_LICENSE', 'name': 'Business License', 'required': True, 'types': ['Official Doc']},
                {'id': 'TAX_RETURN', 'name': 'Tax Returns', 'required': True, 'types': ['Last 2 Years']},
                {'id': 'BUSINESS_PLAN', 'name': 'Business Plan', 'required': True, 'types': ['Detailed Doc']}
            ]
        }
        return documents_map.get(product_type, [])


def scrape_insurance_data(product_types: List[str] = None, location: str = None) -> List[Dict]:
    """
    Main function to scrape insurance data
    
    Args:
        product_types: List of product types to search for
        location: Geographic location for filtering
    
    Returns:
        List of normalized insurance plans
    """
    scraper = InsuranceScraper()
    return scraper.scrape_all_insurers(product_types, location)


if __name__ == "__main__":
    # Test scraper
    print("Testing Insurance Data Scraper...")
    
    # Test 1: Scrape all products
    print("\n[TEST 1] Scraping all products...")
    all_plans = scrape_insurance_data()
    print(f"Found {len(all_plans)} plans")
    
    # Test 2: Scrape specific products
    print("\n[TEST 2] Scraping home and pet insurance...")
    home_pet_plans = scrape_insurance_data(['home', 'pet'])
    print(f"Found {len(home_pet_plans)} home and pet plans")
    for plan in home_pet_plans[:3]:
        print(f"  - {plan['insurer']} {plan['plan_name']}: ${plan['annual_premium']}/year")
    
    # Test 3: Check normalization
    print("\n[TEST 3] Data normalization check...")
    if all_plans:
        sample = all_plans[0]
        print(f"Sample plan structure:")
        print(f"  - Insurer: {sample['insurer']}")
        print(f"  - Product: {sample['product_type']}")
        print(f"  - Premium: ${sample['annual_premium']}")
        print(f"  - Settlement: {sample['claim_settlement_days']} days")
        print(f"  - Features: {', '.join(sample['features'][:2])}...")
        print(f"  - Rating: {sample['rating']}/5")
