import streamlit as st
import json
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import altair as alt
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import dynamic search components
try:
    from cache_manager import CacheManager
    from query_parser import QueryParser, QueryEnhancer
    from dynamic_search import DynamicInsuranceSearchEngine
    from dynamic_agents_integration import DynamicAgentsController
    DYNAMIC_SEARCH_AVAILABLE = True
except ImportError as e:
    DYNAMIC_SEARCH_AVAILABLE = False
    print(f"Warning: Dynamic search not available: {e}")

# Import existing utilities
from agents.intent_agent import extract_intent
from agents.query_enhancement_agent import enhance_query
from agents.connectors_agent import fetch_and_score_plans
from agents.recommendation_agent import generate_recommendation
try:
    from policy_explanations import get_policy_explanation, format_coverage_checklist
except ImportError:
    # Fallback if policy_explanations is not available
    def get_policy_explanation(*args, **kwargs):
        return {}
    def format_coverage_checklist(*args, **kwargs):
        return ""
try:
    from policy_manager import get_all_policies, save_policy, get_renewal_reminders
except ImportError:
    # Fallback if policy_manager is not available
    def get_all_policies(*args, **kwargs):
        return []
    def save_policy(*args, **kwargs):
        return None
    def get_renewal_reminders(*args, **kwargs):
        return []

try:
    from support_hub import search_faq, FAQ_TOPICS
except ImportError:
    # Fallback if support_hub is not available
    def search_faq(*args, **kwargs):
        return []
    FAQ_TOPICS = {}
try:
    from recommendation_engine import rank_plans_for_user
except ImportError:
    def rank_plans_for_user(*args, **kwargs):
        return []

try:
    from company_profiles import get_company_profile
except ImportError:
    def get_company_profile(*args, **kwargs):
        return {}

try:
    from service_center_locator import find_nearest_service_center, format_service_center_info
except ImportError:
    def find_nearest_service_center(*args, **kwargs):
        return None
    def format_service_center_info(*args, **kwargs):
        return ""

try:
    from comparison_charts import create_premium_comparison_chart, create_coverage_vs_premium_chart
except ImportError:
    def create_premium_comparison_chart(*args, **kwargs):
        return None
    def create_coverage_vs_premium_chart(*args, **kwargs):
        return None

try:
    from area_eligibility import AREA_ELIGIBILITY
except ImportError:
    AREA_ELIGIBILITY = {}

from data_scraper import InsuranceScraperAgent

# Helper: render company metadata for a plan (excludes logo_url)
def render_company_fields(plan):
    try:
        company = plan.get("company") or get_company_profile(plan.get("insurer"))
    except Exception:
        company = plan.get("company") or {}
    company = company or {}

    founded = company.get("founded_year") or company.get("founded")
    hq = company.get("headquarters") or company.get("head_office") or company.get("headquarter")
    partners = company.get("third_party_partners") or company.get("partners") or []
    coverage = company.get("standard_coverage") or company.get("standard_coverage_items") or []

    if not (founded or hq or partners or coverage):
        return

    st.markdown("**Company Info**")
    if founded:
        st.write(f"**Founded:** {founded}")
    if hq:
        st.write(f"**Headquarters:** {hq}")
    if partners:
        if isinstance(partners, (list, tuple)):
            st.write("**Partners:** " + ", ".join(str(p) for p in partners))
        else:
            st.write(f"**Partners:** {partners}")
    if coverage:
        st.write("**Standard Coverage:**")
        if isinstance(coverage, (list, tuple)):
            for c in coverage:
                st.write(f"- {c}")
        else:
            st.write(f"- {coverage}")

# ====== PAGE CONFIG ======
st.set_page_config(
    page_title="InsureAI Pro | Smart Insurance Solutions",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ====== CUSTOM CSS ======
st.markdown("""
<style>
.main-title {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3em;
    font-weight: bold;
    margin-bottom: 5px;
    letter-spacing: 1px;
}

.subtitle {
    text-align: center;
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.2em;
    margin-bottom: 30px;
    font-weight: 500;
}

.search-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 35px;
    border-radius: 15px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.search-title {
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 15px;
}

.plan-card {
    border: 2px solid #667eea;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    background-color: #ffffff;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    transition: all 0.3s ease;
}

.plan-card:hover {
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
    transform: translateY(-2px);
    border-color: #764ba2;
}

.plan-header {
    font-size: 1.3em;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
}

.plan-details {
    color: #333;
    line-height: 1.6;
}

.badge-premium {
    display: inline-block;
    background-color: #667eea;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    margin-right: 5px;
    font-weight: 600;
}

.badge-popular {
    display: inline-block;
    background-color: #764ba2;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    margin-right: 5px;
    font-weight: 600;
}

.badge-recommended {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    margin-right: 5px;
    font-weight: 600;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

.comparison-table th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px;
    text-align: left;
    border: 1px solid #ddd;
    font-weight: 600;
}

.comparison-table td {
    padding: 12px;
    border: 1px solid #ddd;
}

.comparison-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.agent-response {
    background-color: #f3f1ff;
    border-left: 4px solid #667eea;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}

.info-box {
    background-color: #f3f1ff;
    border-left: 4px solid #667eea;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}

.success-box {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}

.warning-box {
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
}

.tab-content {
    padding: 20px 0;
}

.filter-section {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #667eea;
}

.metric-box {
    background: linear-gradient(135deg, #f3f1ff 0%, #f9f7ff 100%);
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    border: 2px solid #667eea;
}

.metric-value {
    font-size: 2em;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ====== HELPER FUNCTIONS ======
def get_company_info(company_name):
    """Helper function to get company static data"""
    if "scraper_agent" not in st.session_state:
        st.session_state.scraper_agent = InsuranceScraperAgent()
    return st.session_state.scraper_agent.get_company_static_data(company_name)

def display_company_static_info(company_data, compact=False):
    """Display company static information"""
    if not company_data:
        return
    
    if compact:
        # Compact display for list views
        if company_data.get('founded_year'):
            st.caption(f"📅 Founded: {company_data.get('founded_year')} | 📍 {company_data.get('headquarters', 'N/A')}")
        if company_data.get('product_types'):
            st.caption(f"📦 Products: {len(company_data.get('product_types', []))} types")
        if company_data.get('third_party_partners'):
            st.caption(f"🤝 Partners: {len(company_data.get('third_party_partners', []))} companies")
    else:
        # Full display
        if company_data.get('founded_year'):
            st.markdown(f"**Founded:** {company_data.get('founded_year')}")
        if company_data.get('headquarters'):
            st.markdown(f"**Headquarters:** {company_data.get('headquarters')}")
        if company_data.get('product_types'):
            st.markdown(f"**Product Types:** {len(company_data.get('product_types', []))} types offered")
        if company_data.get('third_party_partners'):
            st.markdown(f"**Partners:** {len(company_data.get('third_party_partners', []))} third-party companies")

def display_company_coverage_summary(company_data):
    """Display coverage summary in compact format"""
    if not company_data or not company_data.get('standard_coverage'):
        return
    
    coverage = company_data.get('standard_coverage', {})
    covered_count = len(coverage.get('covered', []))
    not_covered_count = len(coverage.get('not_covered', []))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Covered Items", covered_count)
    with col2:
        st.metric("Exclusions", not_covered_count)

# ====== INITIALIZE SESSION STATE ======
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_search_results" not in st.session_state:
    st.session_state.current_search_results = []
if "selected_plans" not in st.session_state:
    st.session_state.selected_plans = []
if "cache_stats" not in st.session_state:
    st.session_state.cache_stats = {"hits": 0, "misses": 0}
if "scraper_agent" not in st.session_state:
    st.session_state.scraper_agent = InsuranceScraperAgent()

# ====== HEADER ======
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='main-title'>🏆 InsureAI Pro</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Smart Insurance Solutions Powered by AI</div>", unsafe_allow_html=True)

# ====== MAIN SEARCH INTERFACE ======
st.markdown("<div class='search-container'>", unsafe_allow_html=True)
st.markdown("<div class='search-title'>🔍 Find Your Perfect Insurance Plan</div>", unsafe_allow_html=True)

if DYNAMIC_SEARCH_AVAILABLE:
    # Initialize components
    if "cache_manager" not in st.session_state:
        st.session_state.cache_manager = CacheManager()
    if "query_parser" not in st.session_state:
        st.session_state.query_parser = QueryParser()
    if "search_engine" not in st.session_state:
        try:
            st.session_state.search_engine = DynamicInsuranceSearchEngine()
        except Exception as e:
            st.warning(f"Search engine: {str(e)}")
            st.session_state.search_engine = None
    if "agents_controller" not in st.session_state:
        try:
            st.session_state.agents_controller = DynamicAgentsController()
        except Exception as e:
            st.warning(f"Agent controller: {str(e)}")
            st.session_state.agents_controller = None

    # Natural language search input
    search_query = st.text_input(
        "💬 What insurance do you need?",
        placeholder="e.g., 'Home and pet insurance in California' or 'Best auto insurance for young drivers'",
        key="main_search"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        search_button = st.button("🔍 Search Plans", use_container_width=True)
    with col2:
        show_filters = st.checkbox("⚙️ Filters", value=False)
    with col3:
        show_recommendations = st.checkbox("💡 AI Tips", value=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ====== FILTERS SECTION ======
    if show_filters:
        st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
        st.subheader("📋 Refine Your Search")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            selected_products = st.multiselect(
                "Insurance Types:",
                ["Home", "Auto", "Pet", "Health", "Life", "Business"],
                default=["Home"]
            )
        
        with filter_col2:
            selected_locations = st.multiselect(
                "States:",
                ["California", "Texas", "Florida", "New York", "Pennsylvania"],
                default=["California"]
            )
        
        with filter_col3:
            max_premium = st.slider(
                "Max Monthly Premium ($):",
                min_value=0,
                max_value=500,
                value=300,
                step=10
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

    # ====== SEARCH EXECUTION ======
    if search_button and search_query:
        with st.spinner("🔄 Searching for best plans..."):
            try:
                # Parse query
                parsed_query = st.session_state.query_parser.parse_query(search_query)
                
                # Add to history
                st.session_state.search_history.append({
                    "query": search_query,
                    "timestamp": datetime.now(),
                    "parsed": parsed_query
                })

                # Perform search
                if st.session_state.search_engine:
                    search_response = st.session_state.search_engine.search(
                        user_query=search_query
                    )
                    search_results = search_response.get('plans', [])
                    st.session_state.current_search_results = search_results
                else:
                    st.error("Search engine not initialized")
                    search_results = []

                # Display results summary
                if search_results:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{len(search_results)}</div><div class='metric-label'>Plans Found</div></div>", unsafe_allow_html=True)
                    
                    with col2:
                        avg_rating = sum(p.get("rating", 0) for p in search_results) / len(search_results)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{avg_rating:.1f}</div><div class='metric-label'>Avg Rating</div></div>", unsafe_allow_html=True)
                    
                    with col3:
                        min_premium = min(p.get("annual_premium", 0) for p in search_results)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${min_premium/12:.0f}</div><div class='metric-label'>Min Monthly</div></div>", unsafe_allow_html=True)
                    
                    with col4:
                        max_coverage = max(p.get("coverage_amount", 0) for p in search_results)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${max_coverage/1000:.0f}K</div><div class='metric-label'>Max Coverage</div></div>", unsafe_allow_html=True)
                    
                    with col5:
                        # Get unique companies and show company count
                        unique_companies = set(p.get('insurer', '') for p in search_results)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{len(unique_companies)}</div><div class='metric-label'>Companies</div></div>", unsafe_allow_html=True)

                    st.markdown(f"<div class='info-box'>✅ Found {len(search_results)} insurance plans from {len(unique_companies)} companies matching your criteria!</div>", unsafe_allow_html=True)
                    
                    # Show company badges with static info
                    st.markdown("---")
                    st.markdown("**🏢 Companies in Results:**")
                    company_cols = st.columns(min(len(unique_companies), 5))
                    for idx, company_name in enumerate(list(unique_companies)[:5]):
                        with company_cols[idx]:
                            company_data = get_company_info(company_name)
                            if company_data:
                                st.markdown(f"**{company_name}**")
                                if company_data.get('founded_year'):
                                    years_old = datetime.now().year - company_data.get('founded_year')
                                    st.caption(f"Est. {company_data.get('founded_year')} ({years_old} yrs)")
                                if company_data.get('product_types'):
                                    st.caption(f"{len(company_data.get('product_types', []))} product types")
                            else:
                                st.markdown(f"**{company_name}**")
                else:
                    st.warning("No plans found. Try different search terms.")

            except Exception as e:
                st.error(f"Search error: {str(e)}")

    # ====== SEARCH RESULTS DISPLAY ======
    if st.session_state.current_search_results:
        st.subheader("📋 Available Plans")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["List View", "Comparison", "Recommendations", "Details"])

        with tab1:
            # List view of plans
            for idx, plan in enumerate(st.session_state.current_search_results[:5]):
                with st.expander(
                    f"{'⭐' if plan.get('rating', 0) >= 4.5 else '📌'} {plan.get('plan_name', 'Unknown Plan')} - {plan.get('insurer', 'Unknown')}",
                    expanded=(idx == 0)
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Insurer:** {plan.get('insurer', 'N/A')}")
                        st.markdown(f"**Type:** {plan.get('product_type', 'N/A')}")
                        st.markdown(f"**Coverage:** ${plan.get('coverage_amount', 0):,.0f}")
                        st.markdown(f"**Features:** {', '.join(plan.get('features', [])[:3])}")
                        st.markdown(f"**Available in:** {', '.join(plan.get('location_availability', [])[:2])}")
                        
                        # Add company static information
                        st.markdown("---")
                        company_name = plan.get('insurer', '')
                        company_data = get_company_info(company_name)
                        if company_data:
                            st.markdown("**🏢 Company Info:**")
                            display_company_static_info(company_data, compact=True)
                            
                            # Coverage summary
                            if company_data.get('standard_coverage'):
                                with st.expander("📋 Coverage Summary", expanded=False):
                                    display_company_coverage_summary(company_data)
                    
                    with col2:
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${plan.get('annual_premium', 0)/12:.0f}</div><div class='metric-label'>Monthly</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{plan.get('rating', 0):.1f}⭐</div><div class='metric-label'>Rating</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{plan.get('claim_settlement_days', 0)}d</div><div class='metric-label'>Claim Days</div></div>", unsafe_allow_html=True)
                        
                        # Company metrics
                        if company_data:
                            if company_data.get('founded_year'):
                                years_old = datetime.now().year - company_data.get('founded_year')
                                st.markdown(f"<div class='metric-box'><div class='metric-value'>{years_old}</div><div class='metric-label'>Years in Business</div></div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    if st.button(f"View Full Details", key=f"btn_{idx}"):
                        st.session_state.selected_plans.append(plan)
                        st.success(f"✅ Added to comparison!")

        with tab2:
            # Comparison view
            if len(st.session_state.current_search_results) >= 2:
                st.subheader("⚖️ Compare Plans Side by Side")
                
                selected_plans = st.multiselect(
                    "Select plans to compare (up to 4):",
                    [p.get('plan_name', 'Unknown') for p in st.session_state.current_search_results],
                    default=[st.session_state.current_search_results[0].get('plan_name', 'Unknown'),
                             st.session_state.current_search_results[1].get('plan_name', 'Unknown')] if len(st.session_state.current_search_results) >= 2 else [],
                    max_selections=4
                )

                if selected_plans:
                    comparison_data = []
                    for plan in st.session_state.current_search_results:
                        if plan.get('plan_name') in selected_plans:
                            company_name = plan.get('insurer', '')
                            company_data = get_company_info(company_name)
                            
                            # Calculate company age
                            company_age = "N/A"
                            if company_data and company_data.get('founded_year'):
                                company_age = f"{datetime.now().year - company_data.get('founded_year')} years"
                            
                            # Get product types count
                            product_count = "N/A"
                            if company_data and company_data.get('product_types'):
                                product_count = len(company_data.get('product_types', []))
                            
                            # Get partners count
                            partners_count = "N/A"
                            if company_data and company_data.get('third_party_partners'):
                                partners_count = len(company_data.get('third_party_partners', []))
                            
                            comparison_data.append({
                                "Plan": plan.get('plan_name', 'N/A'),
                                "Insurer": plan.get('insurer', 'N/A'),
                                "Monthly": f"${plan.get('annual_premium', 0)/12:.0f}",
                                "Coverage": f"${plan.get('coverage_amount', 0):,.0f}",
                                "Rating": f"{plan.get('rating', 0):.1f}⭐",
                                "Claim Days": plan.get('claim_settlement_days', 0),
                                "Company Age": company_age,
                                "Product Types": product_count,
                                "Partners": partners_count
                            })
                    
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Display company details for each selected plan
                    st.markdown("---")
                    st.subheader("🏢 Company Details Comparison")
                    comp_cols = st.columns(len(selected_plans))
                    
                    for idx, plan_name in enumerate(selected_plans):
                        plan = next((p for p in st.session_state.current_search_results if p.get('plan_name') == plan_name), None)
                        if plan:
                            with comp_cols[idx]:
                                company_name = plan.get('insurer', '')
                                company_data = get_company_info(company_name)
                                if company_data:
                                    st.markdown(f"**{company_name}**")
                                    if company_data.get('founded_year'):
                                        st.caption(f"Founded: {company_data.get('founded_year')}")
                                    if company_data.get('headquarters'):
                                        st.caption(f"HQ: {company_data.get('headquarters')}")
                                    if company_data.get('product_types'):
                                        st.caption(f"Products: {len(company_data.get('product_types', []))} types")
                                    if company_data.get('third_party_partners'):
                                        st.caption(f"Partners: {len(company_data.get('third_party_partners', []))}")
                                    
                                    # Coverage quick view
                                    if company_data.get('standard_coverage'):
                                        coverage = company_data.get('standard_coverage', {})
                                        with st.expander("Coverage", expanded=False):
                                            st.caption(f"✅ {len(coverage.get('covered', []))} covered")
                                            st.caption(f"❌ {len(coverage.get('not_covered', []))} exclusions")

                    # Create comparison charts
                    if len(comparison_data) >= 2:
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            premium_data = pd.DataFrame({
                                "Plan": [p['Plan'] for p in comparison_data],
                                "Monthly": [float(p['Monthly'].replace('$', '')) for p in comparison_data]
                            })
                            
                            chart = alt.Chart(premium_data).mark_bar().encode(
                                x='Plan',
                                y='Monthly',
                                color=alt.value('#667eea')
                            ).properties(
                                title="💰 Premium Comparison",
                                height=300
                            )
                            st.altair_chart(chart, use_container_width=True)
                        
                        with chart_col2:
                            rating_data = pd.DataFrame({
                                "Plan": [p['Plan'] for p in comparison_data],
                                "Rating": [float(p['Rating'].replace('⭐', '')) for p in comparison_data]
                            })
                            
                            chart = alt.Chart(rating_data).mark_bar().encode(
                                x='Plan',
                                y=alt.Y('Rating', scale=alt.Scale(domain=[0, 5])),
                                color=alt.value('#764ba2')
                            ).properties(
                                title="⭐ Customer Ratings",
                                height=300
                            )
                            st.altair_chart(chart, use_container_width=True)
            else:
                st.info("📌 Need at least 2 plans to compare. Refine your search to find more options.")

        with tab3:
            # AI Recommendations
            if show_recommendations and st.session_state.current_search_results:
                st.subheader("🤖 AI-Powered Recommendations")
                
                try:
                    if st.session_state.agents_controller:
                        with st.spinner("Analyzing plans with AI..."):
                            recommendations = st.session_state.agents_controller.search_and_compare(
                                search_query,
                                st.session_state.current_search_results
                            )
                            
                            st.markdown("<div class='agent-response'>", unsafe_allow_html=True)
                            st.markdown(f"**🎯 Top Recommendation:** {recommendations.get('top_recommendation', 'N/A')}")
                            st.markdown(f"**💡 Why:** {recommendations.get('recommendation', 'N/A')}")
                            if recommendations.get('reasons'):
                                st.markdown("**Key Reasons:**")
                                for reason in recommendations.get('reasons', []):
                                    st.markdown(f"✓ {reason}")
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Agent controller not available")
                except Exception as e:
                    st.info(f"AI analysis: {str(e)}")
                
                # Add company statistics for top plans
                st.markdown("---")
                st.subheader("📊 Company Statistics")
                
                top_plans = st.session_state.current_search_results[:3]
                stat_cols = st.columns(len(top_plans))
                
                for idx, plan in enumerate(top_plans):
                    with stat_cols[idx]:
                        company_name = plan.get('insurer', '')
                        company_data = get_company_info(company_name)
                        
                        st.markdown(f"**{company_name}**")
                        if company_data:
                            # Static fields
                            if company_data.get('founded_year'):
                                years_old = datetime.now().year - company_data.get('founded_year')
                                st.metric("Years in Business", years_old)
                            
                            if company_data.get('product_types'):
                                st.metric("Product Types", len(company_data.get('product_types', [])))
                            
                            if company_data.get('third_party_partners'):
                                st.metric("Partners", len(company_data.get('third_party_partners', [])))
                            
                            if company_data.get('standard_coverage'):
                                coverage = company_data.get('standard_coverage', {})
                                covered = len(coverage.get('covered', []))
                                not_covered = len(coverage.get('not_covered', []))
                                st.metric("Coverage Items", f"{covered} covered, {not_covered} exclusions")
                            
                            # Dynamic data placeholder (if available)
                            if "dynamic_data" in st.session_state and company_name in st.session_state.dynamic_data:
                                dynamic = st.session_state.dynamic_data[company_name]
                                if dynamic.get('claims_settled_recent'):
                                    st.caption("📈 Recent claims data available")
                                if dynamic.get('customers_past_5_years'):
                                    st.caption("👥 Customer growth data available")

        with tab4:
            # Detailed plan information
            if st.session_state.current_search_results:
                selected_plan_name = st.selectbox(
                    "Select a plan for detailed information:",
                    [p.get('plan_name', 'Unknown') for p in st.session_state.current_search_results]
                )
                
                selected_plan = next(
                    (p for p in st.session_state.current_search_results if p.get('plan_name') == selected_plan_name),
                    None
                )
                
                if selected_plan:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader(f"📄 {selected_plan.get('plan_name', 'Plan Details')}")
                        
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.markdown(f"**Insurance Company:** {selected_plan.get('insurer', 'N/A')}")
                            st.markdown(f"**Plan Type:** {selected_plan.get('product_type', 'N/A')}")
                            st.markdown(f"**Annual Premium:** ${selected_plan.get('annual_premium', 0):,.0f}")
                            st.markdown(f"**Monthly Payment:** ${selected_plan.get('annual_premium', 0)/12:,.0f}")
                        
                        with detail_col2:
                            st.markdown(f"**Coverage Limit:** ${selected_plan.get('coverage_amount', 0):,.0f}")
                            st.markdown(f"**Claim Settlement:** {selected_plan.get('claim_settlement_days', 0)} days")
                            st.markdown(f"**Customer Rating:** {'⭐' * int(selected_plan.get('rating', 0))} ({selected_plan.get('rating', 0)})")
                        
                        st.markdown("---")
                        
                        # Features
                        st.subheader("✨ Key Features")
                        features = selected_plan.get('features', [])
                        feature_col1, feature_col2 = st.columns(2)
                        for i, feature in enumerate(features):
                            if i % 2 == 0:
                                feature_col1.markdown(f"✓ {feature}")
                            else:
                                feature_col2.markdown(f"✓ {feature}")
                        
                        # Location availability
                        st.subheader("📍 Location Availability")
                        st.write(", ".join(selected_plan.get('location_availability', [])))
                        
                        # Documents required
                        st.subheader("📋 Documents Needed")
                        docs = selected_plan.get('required_documents', [])
                        if isinstance(docs, list) and len(docs) > 0:
                            if isinstance(docs[0], dict):
                                for doc in docs:
                                    req_text = "Required" if doc.get('required', False) else "Optional"
                                    st.markdown(f"• **{doc.get('name', 'Document')}** ({req_text})")
                                    if doc.get('types'):
                                        st.caption(f"  Types: {', '.join(doc.get('types', []))}")
                            else:
                                for doc in docs:
                                    st.markdown(f"• {doc}")
                        
                        st.markdown("---")
                        
                        # Company Information from scrap.py
                        st.subheader("🏢 Company Information")
                        company_name = selected_plan.get('insurer', '')
                        
                        # Get static company data
                        company_static_data = get_company_info(company_name)
                        
                        if company_static_data:
                            # Company Name
                            st.markdown(f"**Company Name:** {company_static_data.get('company_name', company_name)}")
                            
                            # Founded Year
                            if company_static_data.get('founded_year'):
                                st.markdown(f"**Founded:** {company_static_data.get('founded_year')}")
                            
                            # Headquarters
                            if company_static_data.get('headquarters'):
                                st.markdown(f"**Headquarters:** {company_static_data.get('headquarters')}")
                            
                            # Product Types
                            if company_static_data.get('product_types'):
                                st.markdown("**Product Types Offered:**")
                                product_types_list = company_static_data.get('product_types', [])
                                for ptype in product_types_list:
                                    st.markdown(f"• {ptype}")
                            
                            st.markdown("---")
                            
                            # Standard Coverage - Expandable Sections
                            if company_static_data.get('standard_coverage'):
                                coverage = company_static_data.get('standard_coverage', {})
                                
                                # What's Covered - Expandable
                                with st.expander("✅ What's Covered", expanded=False):
                                    covered_items = coverage.get('covered', [])
                                    if covered_items:
                                        for item in covered_items:
                                            st.markdown(f"✓ {item}")
                                    else:
                                        st.info("No coverage information available")
                                
                                # What's NOT Covered - Expandable
                                with st.expander("❌ What's NOT Covered", expanded=False):
                                    not_covered_items = coverage.get('not_covered', [])
                                    if not_covered_items:
                                        for item in not_covered_items:
                                            st.markdown(f"✗ {item}")
                                    else:
                                        st.info("No exclusions information available")
                            
                            # Third Party Partners
                            if company_static_data.get('third_party_partners'):
                                st.markdown("---")
                                st.subheader("🤝 Third-Party Partners")
                                partners = company_static_data.get('third_party_partners', [])
                                for partner in partners:
                                    st.markdown(f"• {partner}")
                        
                        # Dynamic Data Section (optional, requires Ollama)
                        st.markdown("---")
                        st.subheader("📊 Dynamic Company Data (Requires Ollama)")
                        st.info("This section fetches real-time data about the company's performance, customer base, and market trends.")
                        
                        location_input = st.text_input(
                            "Enter location for dynamic data:",
                            placeholder="e.g., California, New York, Texas",
                            key="dynamic_location_input"
                        )
                        
                        col_fetch1, col_fetch2 = st.columns([1, 1])
                        with col_fetch1:
                            if st.button("🔄 Fetch All Dynamic Data", key="fetch_dynamic_btn", use_container_width=True):
                                if location_input:
                                    with st.spinner("Fetching dynamic data (this may take a while)..."):
                                        try:
                                            dynamic_data = st.session_state.scraper_agent.get_company_dynamic_data(
                                                company_name, 
                                                location_input
                                            )
                                            
                                            # Store in session state
                                            if "dynamic_data" not in st.session_state:
                                                st.session_state.dynamic_data = {}
                                            st.session_state.dynamic_data[company_name] = dynamic_data
                                            
                                            if dynamic_data:
                                                st.success("✅ Dynamic data fetched successfully!")
                                        except Exception as e:
                                            st.warning(f"Could not fetch dynamic data: {str(e)}")
                                            st.info("Make sure Ollama is running on http://localhost:11434")
                                else:
                                    st.warning("Please enter a location to fetch dynamic data")
                        
                        with col_fetch2:
                            if st.button("📋 View Cached Data", key="view_cached_btn", use_container_width=True):
                                if "dynamic_data" in st.session_state and company_name in st.session_state.dynamic_data:
                                    dynamic_data = st.session_state.dynamic_data[company_name]
                                else:
                                    st.info("No cached dynamic data. Please fetch data first.")
                                    dynamic_data = None
                        
                        # Display dynamic data
                        dynamic_data_to_show = None
                        if "dynamic_data" in st.session_state and company_name in st.session_state.dynamic_data:
                            dynamic_data_to_show = st.session_state.dynamic_data[company_name]
                        
                        if dynamic_data_to_show:
                            st.markdown("---")
                            st.markdown("**Dynamic Data Points:**")
                            
                            # Organize dynamic fields
                            dynamic_fields = {
                                "claims_settled_recent": "📋 Claims Settled (Recent)",
                                "customers_past_5_years": "👥 Customers (Past 5 Years)",
                                "products_sold_location": "📦 Products Sold (Location)",
                                "active_policyholders_location": "📊 Active Policyholders (Location)",
                                "coverage_trends_location": "📈 Coverage Trends (Location)",
                                "recommended_coverage_location": "💡 Recommended Coverage (Location)",
                                "current_deductibles": "💰 Current Deductibles"
                            }
                            
                            for key, label in dynamic_fields.items():
                                if key in dynamic_data_to_show:
                                    with st.expander(label, expanded=False):
                                        value = dynamic_data_to_show[key]
                                        if isinstance(value, list):
                                            for item in value:
                                                if isinstance(item, dict):
                                                    st.markdown(f"**Information:** {item.get('information', 'N/A')}")
                                                    if item.get('source'):
                                                        st.caption(f"Source: {item.get('source', 'N/A')[:80]}...")
                                                else:
                                                    st.markdown(f"• {item}")
                                        else:
                                            st.markdown(f"{value}")
                    
                    with col2:
                        st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-value'>${selected_plan.get('annual_premium', 0)/12:.0f}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='metric-label'>Monthly Cost</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        if st.button("Get AI-Powered Quote", use_container_width=True):
                            try:
                                if st.session_state.agents_controller:
                                    quote = st.session_state.agents_controller.get_quote_for_search(
                                        search_query,
                                        selected_plan
                                    )
                                    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                                    st.markdown(f"✅ **Quote Generated:** {quote}")
                                    st.markdown("</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.info(f"Quote generation: {str(e)}")

else:
    # Fallback to basic search using agents when dynamic search is not available
    st.info("💡 Using basic search mode (dynamic search components not available)")
    
    # Basic search interface
    search_query = st.text_input(
        "💬 What insurance do you need?",
        placeholder="e.g., 'Home and pet insurance in California' or 'Best auto insurance for young drivers'",
        key="basic_search"
    )
    
    search_button = st.button("🔍 Search Plans", use_container_width=True, type="primary")
    
    if search_button and search_query:
        with st.spinner("🔄 Searching for best plans..."):
            try:
                # Use basic agents for search
                intent = extract_intent(search_query)
                enhanced = enhance_query(intent)
                plans = fetch_and_score_plans(enhanced)
                
                if plans:
                    st.session_state.current_search_results = plans
                    st.success(f"✅ Found {len(plans)} insurance plans!")
                    
                    # Display results summary with company info
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{len(plans)}</div><div class='metric-label'>Plans Found</div></div>", unsafe_allow_html=True)
                    
                    with col2:
                        avg_rating = sum(p.get("rating", 0) for p in plans) / len(plans)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{avg_rating:.1f}</div><div class='metric-label'>Avg Rating</div></div>", unsafe_allow_html=True)
                    
                    with col3:
                        min_premium = min(p.get("annual_premium", 0) for p in plans)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${min_premium/12:.0f}</div><div class='metric-label'>Min Monthly</div></div>", unsafe_allow_html=True)
                    
                    with col4:
                        max_coverage = max(p.get("coverage_amount", 0) for p in plans)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${max_coverage/1000:.0f}K</div><div class='metric-label'>Max Coverage</div></div>", unsafe_allow_html=True)
                    
                    with col5:
                        unique_companies = set(p.get('insurer', '') for p in plans)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{len(unique_companies)}</div><div class='metric-label'>Companies</div></div>", unsafe_allow_html=True)
                    
                    # Show company badges
                    st.markdown("---")
                    st.markdown("**🏢 Companies in Results:**")
                    company_cols = st.columns(min(len(unique_companies), 5))
                    for idx, company_name in enumerate(list(unique_companies)[:5]):
                        with company_cols[idx]:
                            company_data = get_company_info(company_name)
                            if company_data:
                                st.markdown(f"**{company_name}**")
                                if company_data.get('founded_year'):
                                    years_old = datetime.now().year - company_data.get('founded_year')
                                    st.caption(f"Est. {company_data.get('founded_year')} ({years_old} yrs)")
                                if company_data.get('product_types'):
                                    st.caption(f"{len(company_data.get('product_types', []))} product types")
                            else:
                                st.markdown(f"**{company_name}**")
                    
                    # Display results
                    st.subheader("📋 Available Plans")
                    tab1, tab2, tab3, tab4 = st.tabs(["List View", "Comparison", "Recommendations", "Details"])
                    
                    # List View
                    with tab1:
                        for idx, plan in enumerate(plans[:5]):
                            with st.expander(
                                f"{'⭐' if plan.get('rating', 0) >= 4.5 else '📌'} {plan.get('plan_name', 'Unknown Plan')} - {plan.get('insurer', 'Unknown')}",
                                expanded=(idx == 0)
                            ):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"**Insurer:** {plan.get('insurer', 'N/A')}")
                                    st.markdown(f"**Type:** {plan.get('product_type', 'N/A')}")
                                    st.markdown(f"**Coverage:** ${plan.get('coverage_amount', 0):,.0f}")
                                    st.markdown(f"**Features:** {', '.join(plan.get('features', [])[:3])}")
                                    
                                    # Add company static information
                                    st.markdown("---")
                                    company_name = plan.get('insurer', '')
                                    company_data = get_company_info(company_name)
                                    if company_data:
                                        st.markdown("**🏢 Company Info:**")
                                        display_company_static_info(company_data, compact=True)
                                        
                                        # Coverage summary
                                        if company_data.get('standard_coverage'):
                                            with st.expander("📋 Coverage Summary", expanded=False):
                                                display_company_coverage_summary(company_data)
                                
                                with col2:
                                    st.markdown(f"**Monthly:** ${plan.get('annual_premium', 0)/12:.0f}")
                                    st.markdown(f"**Rating:** {plan.get('rating', 0):.1f}⭐")
                                    
                                    # Company metrics
                                    if company_data:
                                        if company_data.get('founded_year'):
                                            years_old = datetime.now().year - company_data.get('founded_year')
                                            st.markdown(f"<div class='metric-box'><div class='metric-value'>{years_old}</div><div class='metric-label'>Years in Business</div></div>", unsafe_allow_html=True)
                    
                    # Details tab with company information
                    with tab4:
                        if plans:
                            selected_plan_name = st.selectbox(
                                "Select a plan for detailed information:",
                                [p.get('plan_name', 'Unknown') for p in plans],
                                key="basic_plan_select"
                            )
                            
                            selected_plan = next(
                                (p for p in plans if p.get('plan_name') == selected_plan_name),
                                None
                            )
                            
                            if selected_plan:
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.subheader(f"📄 {selected_plan.get('plan_name', 'Plan Details')}")
                                    
                                    detail_col1, detail_col2 = st.columns(2)
                                    
                                    with detail_col1:
                                        st.markdown(f"**Insurance Company:** {selected_plan.get('insurer', 'N/A')}")
                                        st.markdown(f"**Plan Type:** {selected_plan.get('product_type', 'N/A')}")
                                        st.markdown(f"**Annual Premium:** ${selected_plan.get('annual_premium', 0):,.0f}")
                                        st.markdown(f"**Monthly Payment:** ${selected_plan.get('annual_premium', 0)/12:,.0f}")
                                    
                                    with detail_col2:
                                        st.markdown(f"**Coverage Limit:** ${selected_plan.get('coverage_amount', 0):,.0f}")
                                        st.markdown(f"**Claim Settlement:** {selected_plan.get('claim_settlement_days', 0)} days")
                                        st.markdown(f"**Customer Rating:** {'⭐' * int(selected_plan.get('rating', 0))} ({selected_plan.get('rating', 0)})")
                                    
                                    st.markdown("---")
                                    
                                    # Features
                                    st.subheader("✨ Key Features")
                                    features = selected_plan.get('features', [])
                                    feature_col1, feature_col2 = st.columns(2)
                                    for i, feature in enumerate(features):
                                        if i % 2 == 0:
                                            feature_col1.markdown(f"✓ {feature}")
                                        else:
                                            feature_col2.markdown(f"✓ {feature}")
                                    
                                    # Location availability
                                    st.subheader("📍 Location Availability")
                                    st.write(", ".join(selected_plan.get('location_availability', [])))
                                    
                                    # Documents required
                                    st.subheader("📋 Documents Needed")
                                    docs = selected_plan.get('required_documents', [])
                                    if isinstance(docs, list) and len(docs) > 0:
                                        if isinstance(docs[0], dict):
                                            for doc in docs:
                                                req_text = "Required" if doc.get('required', False) else "Optional"
                                                st.markdown(f"• **{doc.get('name', 'Document')}** ({req_text})")
                                                if doc.get('types'):
                                                    st.caption(f"  Types: {', '.join(doc.get('types', []))}")
                                        else:
                                            for doc in docs:
                                                st.markdown(f"• {doc}")
                                    
                                    st.markdown("---")
                                    
                                    # Company Information from scrap.py
                                    st.subheader("🏢 Company Information")
                                    company_name = selected_plan.get('insurer', '')
                                    
                                    # Get static company data
                                    company_static_data = get_company_info(company_name)
                                    
                                    if company_static_data:
                                        # Company Name
                                        st.markdown(f"**Company Name:** {company_static_data.get('company_name', company_name)}")
                                        
                                        # Founded Year
                                        if company_static_data.get('founded_year'):
                                            st.markdown(f"**Founded:** {company_static_data.get('founded_year')}")
                                        
                                        # Headquarters
                                        if company_static_data.get('headquarters'):
                                            st.markdown(f"**Headquarters:** {company_static_data.get('headquarters')}")
                                        
                                        # Product Types
                                        if company_static_data.get('product_types'):
                                            st.markdown("**Product Types Offered:**")
                                            product_types_list = company_static_data.get('product_types', [])
                                            for ptype in product_types_list:
                                                st.markdown(f"• {ptype}")
                                        
                                        st.markdown("---")
                                        
                                        # Standard Coverage - Expandable Sections
                                        if company_static_data.get('standard_coverage'):
                                            coverage = company_static_data.get('standard_coverage', {})
                                            
                                            # What's Covered - Expandable
                                            with st.expander("✅ What's Covered", expanded=False):
                                                covered_items = coverage.get('covered', [])
                                                if covered_items:
                                                    for item in covered_items:
                                                        st.markdown(f"✓ {item}")
                                                else:
                                                    st.info("No coverage information available")
                                            
                                            # What's NOT Covered - Expandable
                                            with st.expander("❌ What's NOT Covered", expanded=False):
                                                not_covered_items = coverage.get('not_covered', [])
                                                if not_covered_items:
                                                    for item in not_covered_items:
                                                        st.markdown(f"✗ {item}")
                                                else:
                                                    st.info("No exclusions information available")
                                        
                                        # Third Party Partners
                                        if company_static_data.get('third_party_partners'):
                                            st.markdown("---")
                                            st.subheader("🤝 Third-Party Partners")
                                            partners = company_static_data.get('third_party_partners', [])
                                            for partner in partners:
                                                st.markdown(f"• {partner}")
                                    
                                    # Dynamic Data Section (optional, requires Ollama)
                                    st.markdown("---")
                                    st.subheader("📊 Dynamic Company Data (Requires Ollama)")
                                    st.info("This section fetches real-time data about the company's performance, customer base, and market trends.")
                                    
                                    location_input = st.text_input(
                                        "Enter location for dynamic data:",
                                        placeholder="e.g., California, New York, Texas",
                                        key="dynamic_location_input_basic"
                                    )
                                    
                                    col_fetch1, col_fetch2 = st.columns([1, 1])
                                    with col_fetch1:
                                        if st.button("🔄 Fetch All Dynamic Data", key="fetch_dynamic_btn_basic", use_container_width=True):
                                            if location_input:
                                                with st.spinner("Fetching dynamic data (this may take a while)..."):
                                                    try:
                                                        dynamic_data = st.session_state.scraper_agent.get_company_dynamic_data(
                                                            company_name, 
                                                            location_input
                                                        )
                                                        
                                                        # Store in session state
                                                        if "dynamic_data" not in st.session_state:
                                                            st.session_state.dynamic_data = {}
                                                        st.session_state.dynamic_data[company_name] = dynamic_data
                                                        
                                                        if dynamic_data:
                                                            st.success("✅ Dynamic data fetched successfully!")
                                                    except Exception as e:
                                                        st.warning(f"Could not fetch dynamic data: {str(e)}")
                                                        st.info("Make sure Ollama is running on http://localhost:11434")
                                            else:
                                                st.warning("Please enter a location to fetch dynamic data")
                                    
                                    with col_fetch2:
                                        if st.button("📋 View Cached Data", key="view_cached_btn_basic", use_container_width=True):
                                            if "dynamic_data" in st.session_state and company_name in st.session_state.dynamic_data:
                                                dynamic_data = st.session_state.dynamic_data[company_name]
                                            else:
                                                st.info("No cached dynamic data. Please fetch data first.")
                                                dynamic_data = None
                                    
                                    # Display dynamic data
                                    dynamic_data_to_show = None
                                    if "dynamic_data" in st.session_state and company_name in st.session_state.dynamic_data:
                                        dynamic_data_to_show = st.session_state.dynamic_data[company_name]
                                    
                                    if dynamic_data_to_show:
                                        st.markdown("---")
                                        st.markdown("**Dynamic Data Points:**")
                                        
                                        # Organize dynamic fields
                                        dynamic_fields = {
                                            "claims_settled_recent": "📋 Claims Settled (Recent)",
                                            "customers_past_5_years": "👥 Customers (Past 5 Years)",
                                            "products_sold_location": "📦 Products Sold (Location)",
                                            "active_policyholders_location": "📊 Active Policyholders (Location)",
                                            "coverage_trends_location": "📈 Coverage Trends (Location)",
                                            "recommended_coverage_location": "💡 Recommended Coverage (Location)",
                                            "current_deductibles": "💰 Current Deductibles"
                                        }
                                        
                                        for key, label in dynamic_fields.items():
                                            if key in dynamic_data_to_show:
                                                with st.expander(label, expanded=False):
                                                    value = dynamic_data_to_show[key]
                                                    if isinstance(value, list):
                                                        for item in value:
                                                            if isinstance(item, dict):
                                                                st.markdown(f"**Information:** {item.get('information', 'N/A')}")
                                                                if item.get('source'):
                                                                    st.caption(f"Source: {item.get('source', 'N/A')[:80]}...")
                                                            else:
                                                                st.markdown(f"• {item}")
                                                    else:
                                                        st.markdown(f"{value}")
                                
                                with col2:
                                    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='metric-value'>${selected_plan.get('annual_premium', 0)/12:.0f}</div>", unsafe_allow_html=True)
                                    st.markdown("<div class='metric-label'>Monthly Cost</div>", unsafe_allow_html=True)
                                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No plans found. Try different search terms.")
                    
            except Exception as e:
                st.error(f"Search error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Search Statistics")
    
    if st.session_state.search_history:
        st.write(f"🔍 Total Searches: {len(st.session_state.search_history)}")
        st.write(f"⏰ Last Search: {st.session_state.search_history[-1]['timestamp'].strftime('%H:%M:%S')}")
        
        with st.expander("📜 Recent Searches"):
            for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
                st.write(f"{i+1}. {search['query'][:40]}...")
    else:
        st.write("Start searching to build history!")
    
    st.markdown("---")
    st.subheader("🛠️ Tools")
    
    if st.button("🔄 Clear Cache", use_container_width=True):
        if "cache_manager" in st.session_state:
            st.session_state.cache_manager.clear_all()
            st.success("✅ Cache cleared!")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.search_history = []
        st.success("✅ History cleared!")
    
    st.markdown("---")
    st.subheader("❓ Help")
    
    help_tabs = st.tabs(["FAQ", "About", "Tips"])
    
    with help_tabs[0]:
        st.markdown("""
        **Q: How do I search?**
        Use natural language like "Home insurance in California"
        
        **Q: Can I compare plans?**
        Yes! Use the Comparison tab.
        
        **Q: How are recommendations made?**
        Our AI analyzes your needs and matches plans.
        """)
    
    with help_tabs[1]:
        st.markdown("""
        **InsureAI Pro v2.0**
        
        ✨ AI-powered search
        💰 Real-time quotes
        📊 Smart comparisons
        🚀 Fast & reliable
        """)
    
    with help_tabs[2]:
        st.markdown("""
        **Best practices:**
        1. Be specific in searches
        2. Use filters wisely
        3. Compare 2-3 plans
        4. Review AI tips
        5. Check documents needed
        """)

# ====== FOOTER ======
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9em;'>
    <p>🏆 InsureAI Pro | Smart Insurance Solutions</p>
    <p>Powered by AI Agents & Dynamic Search</p>
    <p style='font-size: 0.8em;'>Always review terms before purchasing.</p>
</div>
""", unsafe_allow_html=True)