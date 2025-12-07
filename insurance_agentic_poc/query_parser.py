"""
Natural Language Query Parser for Insurance Search
Extracts product types, location, and other parameters from user queries
"""

import re
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryParser:
    """Parse natural language insurance queries"""
    
    def __init__(self):
        """Initialize query parser with product and location mappings"""
        
        # Product type keywords
        self.product_keywords = {
            'home': ['home', 'house', 'homeowners', 'property', 'house insurance', 'dwelling'],
            'pet': ['pet', 'dog', 'cat', 'animal', 'vet', 'veterinary', 'puppy', 'kitten'],
            'auto': ['auto', 'car', 'vehicle', 'car insurance', 'driving', 'driver', 'motorcycle'],
            'life': ['life', 'term life', 'whole life', 'death benefit', 'beneficiary'],
            'business': ['business', 'commercial', 'liability', 'property damage', 'workers comp', 'employer'],
            'health': ['health', 'medical', 'hospital', 'coverage', 'illness', 'doctor']
        }
        
        # US States mapping
        self.us_states = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        # Business vs Personal indicators
        self.business_keywords = ['business', 'commercial', 'company', 'enterprise', 'startup', 'corporate']
        self.personal_keywords = ['personal', 'individual', 'family', 'myself', 'my family']
        
        # Coverage amount keywords
        self.coverage_keywords = {
            'low': (100000, 300000),
            'medium': (300000, 750000),
            'high': (750000, 2000000),
            'premium': (2000000, 10000000)
        }
    
    def parse_query(self, query: str) -> Dict:
        """
        Parse natural language query into structured parameters
        
        Args:
            query: User's natural language query
        
        Returns:
            Dictionary with extracted parameters
        """
        query_lower = query.lower()
        
        result = {
            'original_query': query,
            'product_types': self._extract_products(query_lower),
            'location': self._extract_location(query_lower),
            'business_type': self._determine_business_type(query_lower),
            'coverage_level': self._extract_coverage_level(query_lower),
            'keywords': self._extract_keywords(query_lower),
            'intent': self._determine_intent(query_lower)
        }
        
        logger.info(f"Parsed query: {result}")
        return result
    
    def _extract_products(self, query: str) -> List[str]:
        """Extract product types from query"""
        products = []
        
        for product_type, keywords in self.product_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', query):
                    if product_type not in products:
                        products.append(product_type)
                    break
        
        return products if products else ['health']  # Default to health if none found
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        # Check for state names
        for state_name, state_code in self.us_states.items():
            if re.search(r'\b' + state_name + r'\b', query):
                return state_code
        
        # Check for state codes
        state_codes = list(self.us_states.values())
        for code in state_codes:
            if re.search(r'\b' + code + r'\b', query):
                return code
        
        # Check for common city/area names
        if 'california' in query or 'ca' in query or 'los angeles' in query or 'sf' in query:
            return 'CA'
        if 'texas' in query or 'tx' in query or 'dallas' in query or 'houston' in query:
            return 'TX'
        if 'florida' in query or 'fl' in query or 'miami' in query or 'orlando' in query:
            return 'FL'
        if 'new york' in query or 'ny' in query or 'nyc' in query or 'manhattan' in query:
            return 'NY'
        
        return None
    
    def _determine_business_type(self, query: str) -> str:
        """Determine if query is for business or personal insurance"""
        business_score = sum(1 for kw in self.business_keywords if kw in query)
        personal_score = sum(1 for kw in self.personal_keywords if kw in query)
        
        if business_score > personal_score:
            return 'business'
        elif personal_score > business_score:
            return 'personal'
        else:
            return 'both'
    
    def _extract_coverage_level(self, query: str) -> Optional[str]:
        """Extract desired coverage level from query"""
        coverage_patterns = {
            'low': r'\b(low|basic|minimal|budget)\b',
            'medium': r'\b(medium|moderate|standard|normal)\b',
            'high': r'\b(high|comprehensive|premium|full|maximum)\b',
            'premium': r'\b(premium|elite|luxury|unlimited|top-tier)\b'
        }
        
        for level, pattern in coverage_patterns.items():
            if re.search(pattern, query):
                return level
        
        return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'are', 'for', 'in', 'to', 'i', 'me', 'my'}
        
        # Split query and filter
        words = query.split()
        keywords = [
            word.strip('.,!?;:') 
            for word in words 
            if len(word) > 3 and word.lower() not in stop_words
        ]
        
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def _determine_intent(self, query: str) -> str:
        """Determine user's intent from query"""
        if any(word in query for word in ['compare', 'comparison', 'vs', 'versus', 'which', 'better']):
            return 'comparison'
        elif any(word in query for word in ['recommend', 'recommendation', 'suggest', 'best']):
            return 'recommendation'
        elif any(word in query for word in ['cost', 'price', 'premium', 'how much', 'quote']):
            return 'pricing'
        elif any(word in query for word in ['document', 'requirement', 'need', 'what do i need']):
            return 'document_requirement'
        elif any(word in query for word in ['claim', 'settle', 'timeline', 'how long']):
            return 'claim_info'
        else:
            return 'search'


class QueryEnhancer:
    """Enhance parsed queries with additional context"""
    
    def __init__(self, parser: QueryParser):
        """Initialize query enhancer"""
        self.parser = parser
    
    def enhance(self, query: str) -> Dict:
        """
        Parse and enhance query with recommendations
        
        Args:
            query: User's natural language query
        
        Returns:
            Enhanced query with parsed parameters and suggestions
        """
        parsed = self.parser.parse_query(query)
        
        # Add enhancement suggestions
        parsed['suggestions'] = self._get_suggestions(parsed)
        parsed['filter_criteria'] = self._build_filter_criteria(parsed)
        
        return parsed
    
    def _get_suggestions(self, parsed_query: Dict) -> List[str]:
        """Get suggestions based on parsed query"""
        suggestions = []
        
        if not parsed_query['location']:
            suggestions.append("Specify your location for better recommendations")
        
        if len(parsed_query['product_types']) == 1:
            suggestions.append("Consider comparing multiple product types for better coverage")
        
        if parsed_query['coverage_level'] is None:
            suggestions.append("Specify coverage level (low, medium, high, premium)")
        
        if parsed_query['business_type'] == 'both':
            suggestions.append("Clarify if you need personal or business insurance")
        
        return suggestions
    
    def _build_filter_criteria(self, parsed_query: Dict) -> Dict:
        """Build filter criteria for database queries"""
        return {
            'product_types': parsed_query['product_types'],
            'location': parsed_query['location'],
            'business_type': parsed_query['business_type'],
            'coverage_level': parsed_query['coverage_level'],
            'keywords': parsed_query['keywords']
        }


def parse_insurance_query(query: str) -> Dict:
    """Parse an insurance search query"""
    parser = QueryParser()
    return parser.parse_query(query)


def enhance_insurance_query(query: str) -> Dict:
    """Parse and enhance an insurance search query"""
    parser = QueryParser()
    enhancer = QueryEnhancer(parser)
    return enhancer.enhance(query)


if __name__ == "__main__":
    # Test query parser
    print("Testing Query Parser...")
    
    test_queries = [
        "I need home and pet insurance for California",
        "Compare auto insurance plans in Texas",
        "What's the best health coverage for my family in New York?",
        "Business liability insurance for my startup in Florida",
        "I'm looking for life insurance with premium coverage",
    ]
    
    parser = QueryParser()
    
    for query in test_queries:
        print(f"\n[QUERY] {query}")
        parsed = parser.parse_query(query)
        print(f"  Products: {parsed['product_types']}")
        print(f"  Location: {parsed['location']}")
        print(f"  Type: {parsed['business_type']}")
        print(f"  Intent: {parsed['intent']}")
        print(f"  Coverage: {parsed['coverage_level']}")
    
    print("\n[ENHANCED QUERIES]")
    enhancer = QueryEnhancer(parser)
    for query in test_queries[:2]:
        print(f"\n[QUERY] {query}")
        enhanced = enhancer.enhance(query)
        print(f"  Suggestions: {enhanced['suggestions']}")
