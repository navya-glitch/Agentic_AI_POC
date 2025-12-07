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
from policy_explanations import get_policy_explanation, format_coverage_checklist
from policy_manager import get_all_policies, save_policy, get_renewal_reminders
from support_hub import search_faq, FAQ_TOPICS
# Optional imports — provide light fallbacks if modules are missing or raise
try:
    from recommendation_engine import rank_plans_for_user
except Exception:
    def rank_plans_for_user(plans, user_profile):
        # Simple fallback: return up to three plans with categories set
        out = []
        for i, p in enumerate(plans[:3]):
            cat = ["🏆 Best Value", "⭐ Ideal Coverage", "💡 Alternative"][i] if i < 3 else ""
            item = {"category": cat, **(p or {})}
            out.append(item)
        return out

try:
    from company_profiles import get_company_profile
except Exception:
    def get_company_profile(name: str):
        return {"company_name": name or "Unknown", "description": "No profile available."}

try:
    from service_center_locator import find_nearest_service_center, format_service_center_info
except Exception:
    def find_nearest_service_center(*a, **k):
        return []
    def format_service_center_info(info):
        return "No service centers available."

try:
    from comparison_charts import create_premium_comparison_chart, create_coverage_vs_premium_chart
except Exception:
    def create_premium_comparison_chart(df):
        return None
    def create_coverage_vs_premium_chart(df):
        return None

try:
    from area_eligibility import AREA_ELIGIBILITY
except Exception:
    AREA_ELIGIBILITY = {}
from scrap_fields import get_scrap_fields_for_company
from scrap_output_reader import get_company_scrape, get_scrape_metadata

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

# ====== INITIALIZE SESSION STATE ======
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_search_results" not in st.session_state:
    st.session_state.current_search_results = []
if "selected_plans" not in st.session_state:
    st.session_state.selected_plans = []
if "cache_stats" not in st.session_state:
    st.session_state.cache_stats = {"hits": 0, "misses": 0}

# ====== USER PROFILE SESSION STATE ======
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Guest User",
        "email": "",
        "budget_preference": "Balanced",
        "coverage_preference": "Standard",
        "risk_tolerance": "Moderate",
        "insurance_types": ["Home"],
        "preferred_locations": ["California"],
        "savings_profile": False,
        "contact_method": "Email"
    }

# ====== HEADER ======
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    with st.popover("👤 Profile", use_container_width=True):
        st.subheader("👤 User Profile")
        st.write(f"**Name:** {st.session_state.user_profile['name']}")
        st.write(f"**Budget Preference:** {st.session_state.user_profile['budget_preference']}")
        st.write(f"**Coverage Level:** {st.session_state.user_profile['coverage_preference']}")
        st.markdown("---")
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.show_profile_editor = True

with col2:
    st.markdown("<div class='main-title'>🏆 InsureAI Pro</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Smart Insurance Solutions Powered by AI</div>", unsafe_allow_html=True)

with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.show_settings = True

# ====== USER PROFILE EDITOR MODAL ======
if st.session_state.get("show_profile_editor"):
    st.markdown("---")
    st.subheader("✏️ Edit Your Profile")
    
    profile_col1, profile_col2 = st.columns(2)
    
    with profile_col1:
        st.session_state.user_profile["name"] = st.text_input(
            "Full Name",
            value=st.session_state.user_profile.get("name", "Guest User")
        )
        
        st.session_state.user_profile["email"] = st.text_input(
            "Email Address",
            value=st.session_state.user_profile.get("email", ""),
            placeholder="your@email.com"
        )
        
        st.session_state.user_profile["contact_method"] = st.selectbox(
            "Preferred Contact Method",
            ["Email", "Phone", "SMS"],
            index=["Email", "Phone", "SMS"].index(st.session_state.user_profile.get("contact_method", "Email"))
        )
    
    with profile_col2:
        st.session_state.user_profile["budget_preference"] = st.selectbox(
            "Budget Preference",
            ["LowPremium", "Balanced", "HighCoverage"],
            index=["LowPremium", "Balanced", "HighCoverage"].index(st.session_state.user_profile.get("budget_preference", "Balanced"))
        )
        
        st.session_state.user_profile["coverage_preference"] = st.selectbox(
            "Coverage Level",
            ["Minimum", "Standard", "Premium"],
            index=["Minimum", "Standard", "Premium"].index(st.session_state.user_profile.get("coverage_preference", "Standard"))
        )
        
        st.session_state.user_profile["risk_tolerance"] = st.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"],
            index=["Conservative", "Moderate", "Aggressive"].index(st.session_state.user_profile.get("risk_tolerance", "Moderate"))
        )
    
    st.session_state.user_profile["insurance_types"] = st.multiselect(
        "Insurance Types Interested In",
        ["Home", "Auto", "Pet", "Health", "Life", "Business"],
        default=st.session_state.user_profile.get("insurance_types", ["Home"])
    )
    
    st.session_state.user_profile["preferred_locations"] = st.multiselect(
        "Preferred Locations (States)",
        ["California", "Texas", "Florida", "New York", "Pennsylvania", "Arizona", "Georgia", "Illinois"],
        default=st.session_state.user_profile.get("preferred_locations", ["California"])
    )
    
    st.session_state.user_profile["savings_profile"] = st.checkbox(
        "📁 Save this profile for future sessions",
        value=st.session_state.user_profile.get("savings_profile", False)
    )
    
    profile_col1, profile_col2, profile_col3 = st.columns(3)
    with profile_col1:
        if st.button("✅ Save Profile", use_container_width=True):
            st.session_state.show_profile_editor = False
            st.success("✅ Profile saved successfully!")
            st.rerun()
    
    with profile_col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.session_state.user_profile = {
                "name": "Guest User",
                "email": "",
                "budget_preference": "Balanced",
                "coverage_preference": "Standard",
                "risk_tolerance": "Moderate",
                "insurance_types": ["Home"],
                "preferred_locations": ["California"],
                "savings_profile": False,
                "contact_method": "Email"
            }
            st.success("✅ Profile reset to defaults!")
            st.rerun()
    
    with profile_col3:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_profile_editor = False
            st.rerun()
    
    st.markdown("---")

# ====== SETTINGS MODAL ======
if st.session_state.get("show_settings"):
    st.markdown("---")
    st.subheader("⚙️ Application Settings")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        st.write("**Search Settings**")
        st.checkbox("🔐 Use web scraper for real data", value=True)
        st.checkbox("📊 Show detailed analytics", value=True)
        st.checkbox("🤖 Use AI recommendations", value=True)
        st.checkbox("💾 Auto-save comparisons", value=False)
    
    with settings_col2:
        st.write("**Display Settings**")
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.selectbox("Results per page", [5, 10, 15, 20])
        st.checkbox("📱 Mobile-friendly layout", value=True)
        st.checkbox("⚡ Fast mode (less animations)", value=False)
    
    if st.button("✅ Save Settings", use_container_width=True):
        st.session_state.show_settings = False
        st.success("✅ Settings saved!")
        st.rerun()
    
    st.markdown("---")
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
                    col1, col2, col3, col4 = st.columns(4)
                    
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

                    st.markdown(f"<div class='info-box'>✅ Found {len(search_results)} insurance plans matching your criteria!</div>", unsafe_allow_html=True)
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
                    
                    with col2:
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>${plan.get('annual_premium', 0)/12:.0f}</div><div class='metric-label'>Monthly Premium</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{plan.get('rating', 0):.1f}⭐</div><div class='metric-label'>Customer Rating</div></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-box'><div class='metric-value'>{plan.get('claim_settlement_days', 0)}d</div><div class='metric-label'>Claim Cycle Tim</div></div>", unsafe_allow_html=True)
                    
                    st.markdown("---")

                    # Display additional company metadata (from scrap.py static fields)
                    try:
                        scrap_meta = get_scrap_fields_for_company(plan.get('insurer'))
                    except Exception:
                        scrap_meta = None

                    if scrap_meta:
                        st.markdown("**Company Info:**")
                        st.write(f"Founded: {scrap_meta.get('founded_year', 'N/A')}")
                        st.write(f"Headquarters: {scrap_meta.get('headquarters', 'N/A')}")

                        partners = scrap_meta.get('third_party_partners') or []
                        if partners:
                            with st.expander("Third-party partners", expanded=False):
                                for p in partners:
                                    st.write(f"- {p}")

                        std_cov = scrap_meta.get('standard_coverage', {})
                        if std_cov:
                            with st.expander("Standard Coverage - Covered", expanded=False):
                                for c in std_cov.get('covered', []):
                                    st.write(f"- {c}")
                            with st.expander("Standard Coverage - Not Covered", expanded=False):
                                for c in std_cov.get('not_covered', []):
                                    st.write(f"- {c}")

                        # Render any dynamic scraped data if available (from insurance_scraped_data.json)
                        dyn = scrap_meta.get('dynamic_data') if isinstance(scrap_meta, dict) else None
                        if dyn:
                            with st.expander("Available Product & Claim & Coverage insights", expanded=False):
                                for key, val in dyn.items():
                                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                                    # If the value is a list of sources/info dicts, show them nicely
                                    if isinstance(val, list):
                                        for item in val:
                                            if isinstance(item, dict):
                                                info = item.get('information') or item.get('info') or str(item)
                                                src = item.get('source')
                                                if src:
                                                    st.write(f"- {info}  —  [{src}]({src})")
                                                else:
                                                    st.write(f"- {info}")
                                            else:
                                                st.write(f"- {item}")
                                    else:
                                        st.write(str(val))

                    # Show scraped dynamic outputs if available (from running scrap.py)
                    try:
                        scraped = get_company_scrape(plan.get('insurer'))
                    except Exception:
                        scraped = None

                    if scraped:
                        # scraped contains {"static_data":..., "dynamic_data":{...}}
                        dyn = scraped.get('dynamic_data', {})
                        if dyn:
                            with st.expander("Details of Product,Claim & Coverage Insights", expanded=False):
                                for key, value in dyn.items():
                                    # value could be a list of dicts or a string
                                    display_key = key.replace('_', ' ').title()
                                    if isinstance(value, str):
                                        st.write(f"**{display_key}:** {value}")
                                    elif isinstance(value, list):
                                        # show first found item summary
                                        if len(value) == 0:
                                            st.write(f"**{display_key}:** No information found")
                                        else:
                                            first = value[0]
                                            info = first.get('information') if isinstance(first, dict) else str(first)
                                            src = first.get('source') if isinstance(first, dict) else None
                                            st.write(f"**{display_key}:** {info}")
                                            if src:
                                                st.markdown(f"*Source:* {src}")

                    if st.button(f"View Full Details", key=f"btn_{idx}"):
                        st.session_state.selected_plans.append(plan)
                        st.success(f"✅ Added to comparison!")

        with tab2:
            # Comparison view
            if len(st.session_state.current_search_results) >= 2:
                st.subheader("⚖️ Policy Comparison")
                
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
                            comparison_data.append({
                                "Plan": plan.get('plan_name', 'N/A'),
                                "Insurer": plan.get('insurer', 'N/A'),
                                "Monthly": f"${plan.get('annual_premium', 0)/12:.0f}",
                                "Coverage": f"${plan.get('coverage_amount', 0):,.0f}",
                                "Rating": f"{plan.get('rating', 0):.1f}⭐",
                                "Claim Days": plan.get('claim_settlement_days', 0)
                            })
                    
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

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
                
                # Show recommendations based on user profile
                st.info(f"""
                💡 **Personalized for your profile:**
                - Budget Preference: {st.session_state.user_profile['budget_preference']}
                - Coverage Level: {st.session_state.user_profile['coverage_preference']}
                - Risk Tolerance: {st.session_state.user_profile['risk_tolerance']}
                """)
                
                try:
                    if st.session_state.agents_controller:
                        with st.spinner("Analyzing plans with AI based on your profile..."):
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
                
                # Additional personalized tips
                with st.expander("💡 Personalized Tips for You"):
                    if st.session_state.user_profile['budget_preference'] == 'LowPremium':
                        st.write("💡 You prefer low premiums. Consider higher deductibles to reduce monthly costs.")
                    elif st.session_state.user_profile['budget_preference'] == 'HighCoverage':
                        st.write("💡 You prefer comprehensive coverage. Look for plans with higher coverage limits and lower deductibles.")
                    else:
                        st.write("💡 You prefer balanced coverage. These plans offer good protection at reasonable premiums.")
                    
                    if st.session_state.user_profile['risk_tolerance'] == 'Conservative':
                        st.write("🛡️ You have conservative risk tolerance. These plans include more comprehensive protections.")
                    elif st.session_state.user_profile['risk_tolerance'] == 'Aggressive':
                        st.write("⚡ You have aggressive risk tolerance. Consider plans with lower premiums and higher deductibles.")
                    
                    st.write(f"📍 Showing recommendations for: {', '.join(st.session_state.user_profile['preferred_locations'])}")

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
                        for doc in docs:
                            st.markdown(f"• {doc}")

                        # Additional company metadata (from scrap.py static fields)
                        try:
                            scrap_meta = get_scrap_fields_for_company(selected_plan.get('insurer'))
                        except Exception:
                            scrap_meta = None

                        if scrap_meta:
                            st.subheader("🏢 Company Information")
                            st.markdown(f"**Founded:** {scrap_meta.get('founded_year','N/A')}")
                            st.markdown(f"**Headquarters:** {scrap_meta.get('headquarters','N/A')}")

                            partners = scrap_meta.get('third_party_partners') or []
                            if partners:
                                with st.expander("Third-party partners", expanded=False):
                                    for p in partners:
                                        st.write(f"- {p}")

                            std_cov = scrap_meta.get('standard_coverage', {})
                            if std_cov:
                                with st.expander("Standard Coverage — Covered", expanded=False):
                                    for c in std_cov.get('covered', []):
                                        st.write(f"- {c}")
                                with st.expander("Standard Coverage — Not Covered", expanded=False):
                                    for c in std_cov.get('not_covered', []):
                                        st.write(f"- {c}")

                        # Show scraped dynamic data if present
                        dyn = scrap_meta.get('dynamic_data') if isinstance(scrap_meta, dict) else None
                        if dyn:
                            st.subheader("📈 Latest Scraped Data")
                            for key, val in dyn.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                                if isinstance(val, list):
                                    for item in val:
                                        if isinstance(item, dict):
                                            info = item.get('information') or item.get('info') or str(item)
                                            src = item.get('source')
                                            if src:
                                                st.write(f"- {info}  —  [{src}]({src})")
                                            else:
                                                st.write(f"- {info}")
                                        else:
                                            st.write(f"- {item}")
                                else:
                                    st.write(str(val))

                        # Global scrape metadata (scrape_date, location)
                        try:
                            meta = get_scrape_metadata()
                        except Exception:
                            meta = None

                        if meta:
                            st.subheader("🕒 Scrape Metadata")
                            st.markdown(f"**Scrape Date:** {meta.get('scrape_date', 'N/A')}")
                            st.markdown(f"**Scrape Location:** {meta.get('location', 'N/A')}")

                        # Company-specific dynamic data
                        try:
                            scraped = get_company_scrape(selected_plan.get('insurer'))
                        except Exception:
                            scraped = None

                        if scraped:
                            dyn = scraped.get('dynamic_data', {})
                            if dyn:
                                st.subheader("🔎 Scraped Insights")
                                for key, value in dyn.items():
                                    display_key = key.replace('_', ' ').title()
                                    with st.expander(display_key, expanded=False):
                                        if isinstance(value, str):
                                            st.write(value)
                                        elif isinstance(value, list) and len(value) > 0:
                                            for item in value:
                                                if isinstance(item, dict):
                                                    st.markdown(f"- **Source:** {item.get('source', 'N/A')}")
                                                    st.write(item.get('information', ''))
                                                else:
                                                    st.write(str(item))
                                        else:
                                            st.write("No scraped information available")
                    
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
    st.error("⚠️ Dynamic search system not available")
    st.info("Ensure all packages are installed: pip install -r requirements.txt")

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("---")
    
    # User profile summary in sidebar
    st.subheader("👤 Your Profile")
    profile_info = f"""
    **Name:** {st.session_state.user_profile['name']}
    
    **Preferences:**
    - 💰 Budget: {st.session_state.user_profile['budget_preference']}
    - 🛡️ Coverage: {st.session_state.user_profile['coverage_preference']}
    - ⚠️ Risk: {st.session_state.user_profile['risk_tolerance']}
    - 📍 Locations: {', '.join(st.session_state.user_profile['preferred_locations'][:2])}
    """
    st.markdown(profile_info)
    
    if st.button("✏️ Edit Profile", use_container_width=True):
        st.session_state.show_profile_editor = True
        st.rerun()
    
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
