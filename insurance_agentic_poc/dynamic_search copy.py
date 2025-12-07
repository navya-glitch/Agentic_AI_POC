"""
Integration Module for Dynamic Data Search
Connects web scraper, cache, query parser, and agents
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from data_scraper import scrape_insurance_data
from cache_manager import get_cache_manager, CachedDataSource
from query_parser import parse_insurance_query, enhance_insurance_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicInsuranceSearchEngine:
    """
    Main search engine integrating scraping, caching, parsing, and agents
    Handles dynamic data fetching based on user queries
    """
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize search engine
        
        Args:
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.cache_manager = get_cache_manager(ttl_hours=cache_ttl_hours)
        self.cached_data_source = CachedDataSource(self.cache_manager)
        self.search_history = []
    
    def search(self, user_query: str, user_profile: Optional[Dict] = None) -> Dict:
        """
        Perform intelligent search based on natural language query
        
        Args:
            user_query: User's natural language query
            user_profile: Optional user profile for filtering
        
        Returns:
            Search results with recommendations
        """
        logger.info(f"Starting search for: {user_query}")
        
        # Parse query
        parsed = enhance_insurance_query(user_query)
        logger.info(f"Parsed query: {parsed['filter_criteria']}")
        
        # Fetch data (with caching)
        plans = self._fetch_plans(
            parsed['filter_criteria']['product_types'],
            parsed['filter_criteria']['location']
        )
        
        # Filter and sort results
        filtered_plans = self._filter_results(plans, parsed['filter_criteria'], user_profile)
        
        # Build response
        response = {
            'query': user_query,
            'parsed_query': parsed,
            'total_results': len(filtered_plans),
            'plans': filtered_plans,
            'recommendations': self._get_recommendations(filtered_plans, user_profile),
            'timestamp': datetime.now().isoformat(),
            'cache_info': self.cache_manager.get_cache_stats()
        }
        
        # Track search
        self.search_history.append({
            'query': user_query,
            'results_count': len(filtered_plans),
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def _fetch_plans(self, product_types: Optional[List[str]] = None, 
                     location: Optional[str] = None) -> List[Dict]:
        """
        Fetch insurance plans (with caching)
        
        Args:
            product_types: List of product types
            location: Geographic location
        
        Returns:
            List of insurance plans
        """
        # Try cache first
        cached = self.cache_manager.get(product_types, location)
        if cached:
            logger.info(f"Retrieved {len(cached)} plans from cache")
            return cached
        
        # Fetch from scrapers
        logger.info("Cache miss, fetching from sources...")
        plans = scrape_insurance_data(product_types, location)
        
        # Cache results
        if plans:
            self.cache_manager.set(plans, product_types, location)
            logger.info(f"Cached {len(plans)} plans")
        
        return plans
    
    def _filter_results(self, plans: List[Dict], 
                       filter_criteria: Dict, 
                       user_profile: Optional[Dict] = None) -> List[Dict]:
        """
        Filter and sort plans based on criteria
        
        Args:
            plans: List of plans to filter
            filter_criteria: Filtering parameters
            user_profile: Optional user profile
        
        Returns:
            Filtered and sorted plans
        """
        filtered = plans.copy()
        
        # Filter by location if specified
        if filter_criteria['location']:
            location = filter_criteria['location']
            filtered = [
                p for p in filtered 
                if location in p.get('location_availability', [])
            ]
            logger.info(f"After location filter: {len(filtered)} plans")
        
        # Filter by business type
        if filter_criteria['business_type'] != 'both':
            business_type = filter_criteria['business_type']
            filtered = [
                p for p in filtered 
                if p.get('business_type') in [business_type, 'both']
            ]
            logger.info(f"After business type filter: {len(filtered)} plans")
        
        # Filter by coverage level
        if filter_criteria['coverage_level']:
            coverage_level = filter_criteria['coverage_level']
            coverage_map = {
                'low': (0, 300000),
                'medium': (300000, 750000),
                'high': (750000, 2000000),
                'premium': (2000000, float('inf'))
            }
            
            if coverage_level in coverage_map:
                min_cov, max_cov = coverage_map[coverage_level]
                filtered = [
                    p for p in filtered 
                    if min_cov <= p.get('coverage_amount', 0) <= max_cov
                ]
                logger.info(f"After coverage filter: {len(filtered)} plans")
        
        # Sort by rating and premium
        filtered.sort(
            key=lambda p: (
                -p.get('rating', 0),
                p.get('annual_premium', float('inf'))
            )
        )
        
        return filtered
    
    def _get_recommendations(self, plans: List[Dict], 
                            user_profile: Optional[Dict] = None) -> List[Dict]:
        """
        Generate recommendations from plans
        
        Args:
            plans: List of filtered plans
            user_profile: Optional user profile
        
        Returns:
            List of recommendations
        """
        if not plans:
            return []
        
        recommendations = []
        
        # Top rated plan
        top_rated = max(plans, key=lambda p: p.get('rating', 0))
        recommendations.append({
            'title': 'Best Rated',
            'plan': top_rated['plan_name'],
            'insurer': top_rated['insurer'],
            'reason': f"Highest customer rating: {top_rated['rating']}/5",
            'plan_id': top_rated['plan_id']
        })
        
        # Most affordable
        most_affordable = min(plans, key=lambda p: p.get('annual_premium', float('inf')))
        recommendations.append({
            'title': 'Most Affordable',
            'plan': most_affordable['plan_name'],
            'insurer': most_affordable['insurer'],
            'reason': f"Lowest premium: ${most_affordable['annual_premium']}/year",
            'plan_id': most_affordable['plan_id']
        })
        
        # Fastest claims
        fastest_claims = min(plans, key=lambda p: p.get('claim_settlement_days', 365))
        recommendations.append({
            'title': 'Fastest Claims',
            'plan': fastest_claims['plan_name'],
            'insurer': fastest_claims['insurer'],
            'reason': f"Quickest settlement: {fastest_claims['claim_settlement_days']} days",
            'plan_id': fastest_claims['plan_id']
        })
        
        return recommendations
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific plan
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Plan details or None
        """
        # Search in cache and all sources
        all_cache_entries = []
        if self.cache_manager.in_memory_cache:
            for cached_data in self.cache_manager.in_memory_cache.values():
                all_cache_entries.extend(cached_data)
        
        for plan in all_cache_entries:
            if plan.get('plan_id') == plan_id:
                return plan
        
        return None
    
    def get_comparison(self, plan_ids: List[str]) -> Dict:
        """
        Get comparison of multiple plans
        
        Args:
            plan_ids: List of plan IDs to compare
        
        Returns:
            Comparison data
        """
        plans = []
        for plan_id in plan_ids:
            plan = self.get_plan_details(plan_id)
            if plan:
                plans.append(plan)
        
        if not plans:
            return {'error': 'No plans found for comparison'}
        
        # Build comparison matrix
        comparison = {
            'plans': plans,
            'comparison_fields': [
                'insurer',
                'plan_name',
                'annual_premium',
                'coverage_amount',
                'claim_settlement_days',
                'rating'
            ],
            'best_by_field': {}
        }
        
        # Calculate best by field
        for field in ['annual_premium', 'coverage_amount', 'rating']:
            if field == 'annual_premium':
                best = min(plans, key=lambda p: p.get(field, float('inf')))
            else:
                best = max(plans, key=lambda p: p.get(field, 0))
            
            comparison['best_by_field'][field] = {
                'plan_id': best['plan_id'],
                'value': best.get(field)
            }
        
        return comparison
    
    def clear_cache(self) -> Dict:
        """Clear all cached data"""
        self.cache_manager.clear_all()
        return {
            'status': 'success',
            'message': 'All cache cleared'
        }
    
    def get_search_history(self) -> List[Dict]:
        """Get search history"""
        return self.search_history
    
    def get_status(self) -> Dict:
        """Get search engine status"""
        return {
            'status': 'active',
            'cache_stats': self.cache_manager.get_cache_stats(),
            'searches_performed': len(self.search_history),
            'timestamp': datetime.now().isoformat()
        }


# Global search engine instance
_search_engine = None


def get_search_engine(cache_ttl_hours: int = 24) -> DynamicInsuranceSearchEngine:
    """Get or create global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = DynamicInsuranceSearchEngine(cache_ttl_hours)
    return _search_engine


if __name__ == "__main__":
    # Test search engine
    print("Testing Dynamic Insurance Search Engine...")
    
    engine = DynamicInsuranceSearchEngine()
    
    # Test 1: Simple search
    print("\n[TEST 1] Simple search for home insurance in California")
    results = engine.search("I need home insurance in California")
    print(f"Found {results['total_results']} plans")
    print(f"Recommendations:")
    for rec in results['recommendations']:
        print(f"  - {rec['title']}: {rec['reason']}")
    
    # Test 2: Complex query
    print("\n[TEST 2] Complex query - home and pet for California")
    results = engine.search("I'm looking for home and pet insurance for my family in California")
    print(f"Found {results['total_results']} plans")
    print(f"Parsed intent: {results['parsed_query']['intent']}")
    
    # Test 3: Status check
    print("\n[TEST 3] Engine status")
    status = engine.get_status()
    print(f"Searches: {status['searches_performed']}")
    print(f"Cache entries: {status['cache_stats']['file_cache_entries']}")
