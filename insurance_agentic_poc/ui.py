import streamlit as st
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Insurance Search & Comparison",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        color: #1f77d4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .plan-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .plan-name {
        font-size: 1.3em;
        font-weight: bold;
        color: #1f77d4;
    }
    .plan-company {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    .plan-premium {
        font-size: 1.5em;
        font-weight: bold;
        color: #27ae60;
    }
    .plan-rating {
        color: #f39c12;
        font-weight: bold;
    }
    .recommendation-box {
        background-color: #e8f4f8;
        border-left: 4px solid #1f77d4;
        padding: 20px;
        border-radius: 4px;
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-title">🛡️ Insurance Search & Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find the best insurance plans tailored to your needs</div>', unsafe_allow_html=True)

# Sidebar with examples
with st.sidebar:
    st.header("📋 Example Queries")
    st.markdown("""
    Try these examples:
    - "Home insurance with pet and swimming pool in CA"
    - "Best health insurance in TX for family"
    - "Cheap renters insurance in NY"
    - "Auto insurance in Florida"
    """)
    
    st.divider()
    
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. **Intent Analysis** - Understands what you're looking for
    2. **Query Enhancement** - Adds context and defaults
    3. **Plan Fetching** - Searches matching plans
    4. **Recommendations** - AI-powered comparison & insights
    """)

# Main search section
col1, col2 = st.columns([4, 1])

with col1:
    user_query = st.text_input(
        "📝 Describe what insurance you're looking for:",
        placeholder="e.g., Home insurance with pet and swimming pool in CA",
        label_visibility="collapsed",
    )

with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Process the query
if search_button and user_query:
    # Import agents only when needed
    from agents.intent_agent import extract_intent
    from agents.query_enhancement_agent import enhance_query
    from agents.connectors_agent import fetch_and_score_plans
    from agents.recommendation_agent import generate_recommendation
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Results", "Intent Analysis", "Enhanced Query", "Detailed Plans"])
    
    try:
        with st.spinner("🔄 Processing your request..."):
            # Step 1: Extract Intent
            st.info("📊 Analyzing your search intent...")
            intent = extract_intent(user_query)
            
            # Step 2: Enhance Query
            st.info("✨ Enhancing your query with smart defaults...")
            enhanced = enhance_query(intent)
            
            # Step 3: Fetch and Score Plans
            st.info("🔍 Searching for matching insurance plans...")
            plans = fetch_and_score_plans(enhanced)
            
        if not plans:
            st.warning("⚠️ No plans found matching your criteria. Try different keywords or locations.")
            st.info("💡 For demo, try: 'home insurance in CA' or 'health plan in TX'")
        else:
            # Step 4: Generate Recommendation
            recommendation_text = None
            with st.spinner("🤖 Generating personalized recommendations..."):
                try:
                    recommendation_text = generate_recommendation(enhanced, plans)
                except Exception as e:
                    st.warning(f"⚠️ Could not generate AI recommendation (Ollama may be busy): {str(e)[:100]}")
                    recommendation_text = f"Found {len(plans)} matching plans. Review the details in the tabs below."
            
            # Tab 1: Results
            with tab1:
                st.success(f"✅ Found {len(plans)} matching plans")
                
                st.markdown("### 🏆 Top Recommendations")
                
                # Display top 3 plans
                for idx, plan in enumerate(plans[:3], 1):
                    with st.container():
                        st.markdown(f'<div class="plan-card">', unsafe_allow_html=True)
                        
                        # Header with rank
                        col1_plan, col2_plan = st.columns([3, 1])
                        
                        with col1_plan:
                            st.markdown(
                                f'<div class="plan-name">#{idx} {plan["plan_name"]}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="plan-company">by {plan["company_name"]}</div>',
                                unsafe_allow_html=True,
                            )
                        
                        with col2_plan:
                            st.markdown(
                                f'<div class="plan-premium">${plan["adjusted_annual_premium_usd"]:,.0f}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(f'<small>per year</small>', unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # Premium Quote Section
                        st.markdown("#### 💰 **Quote Details**")
                        quote_col1, quote_col2, quote_col3 = st.columns(3)
                        with quote_col1:
                            st.metric("Annual Premium", f"${plan['adjusted_annual_premium_usd']:,.0f}")
                        with quote_col2:
                            monthly = plan.get('monthly_premium_usd', plan['adjusted_annual_premium_usd'] / 12)
                            st.metric("Monthly Premium", f"${monthly:,.2f}")
                        with quote_col3:
                            st.metric("Deductible", f"${plan['deductible_usd']:,.0f}")
                        
                        st.divider()
                        
                        # Key metrics
                        st.markdown("#### 📊 **Plan Ratings**")
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            st.metric("Coverage", f"${plan['coverage_amount_usd']:,.0f}")
                        
                        with metric_col2:
                            rating_text = f"{plan['customer_rating']:.1f} ⭐"
                            st.metric("Rating", rating_text)
                        
                        with metric_col3:
                            st.metric("Reviews", f"{plan['number_of_reviews']}")
                        
                        with metric_col4:
                            value_score = plan.get("valueScore", 0)
                            st.metric("Value Score", f"{value_score:.1f}/100")
                        
                        st.divider()
                        
                        # Coverage Details
                        if 'coverage_details' in plan:
                            st.markdown("#### 🏛️ **Coverage Breakdown**")
                            coverage_cols = st.columns(len(plan['coverage_details']))
                            for col_idx, (coverage_type, coverage_amount) in enumerate(plan['coverage_details'].items()):
                                with coverage_cols[col_idx]:
                                    st.metric(coverage_type, coverage_amount)
                        
                        st.divider()
                        
                        # Claim Information
                        if 'claim_approval_timeline' in plan:
                            st.markdown("#### ⚡ **Claim Information**")
                            claim_col1, claim_col2 = st.columns(2)
                            with claim_col1:
                                st.info(f"**Approval Timeline:** {plan['claim_approval_timeline']}")
                            with claim_col2:
                                st.info(f"**Claim Process:** {plan['claim_process']}")
                        
                        st.divider()
                        
                        # Features & Limitations
                        feature_col1, feature_col2 = st.columns(2)
                        
                        with feature_col1:
                            with st.expander("✅ Features & Benefits"):
                                for feature in plan.get("features", []):
                                    st.markdown(f"• {feature}")
                        
                        with feature_col2:
                            with st.expander("⚠️ Limitations & Exclusions"):
                                for limitation in plan.get("limitations", []):
                                    st.markdown(f"• {limitation}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # AI Recommendation
                if recommendation_text:
                    st.markdown("### 🤖 AI-Powered Recommendation")
                    st.markdown(
                        f'<div class="recommendation-box">{recommendation_text}</div>',
                        unsafe_allow_html=True,
                    )
            
            # Tab 2: Intent Analysis
            with tab2:
                st.markdown("### 📊 Extracted Intent")
                st.json(intent)
            
            # Tab 3: Enhanced Query
            with tab3:
                st.markdown("### ✨ Enhanced Query")
                st.json(enhanced)
            
            # Tab 4: All Plans
            with tab4:
                st.markdown(f"### 📋 All {len(plans)} Plans")
                
                # Create tabs for different views of the data
                sub_tab1, sub_tab2 = st.tabs(["Comparison Table", "Detailed Breakdown"])
                
                with sub_tab1:
                    # Create a comparison table
                    plan_data = []
                    for plan in plans:
                        monthly = plan.get('monthly_premium_usd', plan['adjusted_annual_premium_usd'] / 12)
                        plan_data.append({
                            "Company": plan["company_name"],
                            "Plan Name": plan["plan_name"],
                            "Annual Premium": f"${plan['adjusted_annual_premium_usd']:,.0f}",
                            "Monthly Premium": f"${monthly:,.2f}",
                            "Deductible": f"${plan['deductible_usd']:,.0f}",
                            "Rating": f"{plan['customer_rating']:.1f}⭐",
                            "Reviews": plan['number_of_reviews'],
                            "Claim Approval": plan.get('claim_approval_timeline', 'N/A'),
                        })
                    
                    st.dataframe(plan_data, use_container_width=True)
                
                with sub_tab2:
                    # Detailed breakdown with coverage and claims
                    for plan in plans:
                        with st.expander(f"🔍 {plan['company_name']} - {plan['plan_name']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Pricing**")
                                monthly = plan.get('monthly_premium_usd', plan['adjusted_annual_premium_usd'] / 12)
                                st.markdown(f"- **Annual:** ${plan['adjusted_annual_premium_usd']:,.0f}")
                                st.markdown(f"- **Monthly:** ${monthly:,.2f}")
                                st.markdown(f"- **Deductible:** ${plan['deductible_usd']:,.0f}")
                            
                            with col2:
                                st.markdown("**Claims & Support**")
                                st.markdown(f"- **Approval Time:** {plan.get('claim_approval_timeline', 'N/A')}")
                                st.markdown(f"- **Process:** {plan.get('claim_process', 'N/A')}")
                            
                            if 'coverage_details' in plan:
                                st.markdown("**Coverage Details**")
                                coverage_info = " | ".join([f"{k}: {v}" for k, v in plan['coverage_details'].items()])
                                st.markdown(coverage_info)
                
                st.divider()
                
                # Download options
                col1_down, col2_down = st.columns(2)
                
                with col1_down:
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json.dumps(plan_data, indent=2),
                        file_name="insurance_plans.json",
                        mime="application/json",
                    )
    
    except Exception as e:
        st.error(f"❌ Error processing your request: {str(e)}")
        st.info("💡 Troubleshooting:")
        st.info("• Make sure Ollama is running: `ollama serve`")
        st.info("• Check that the agents are properly configured")
        st.info("• Try a different search query")

else:
    # Empty state
    if not user_query and search_button:
        st.warning("⚠️ Please enter a search query")
    else:
        # Show welcome message
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("🏠 **Home Insurance**\nProtect your property")
        
        with col2:
            st.info("🚗 **Auto Insurance**\nCover your vehicle")
        
        with col3:
            st.info("💊 **Health Insurance**\nProtect your health")
        
        st.markdown("---")
        
        st.markdown("""
        ### 🎯 Getting Started
        
        1. **Enter your query** in the search box above
        2. **Our AI agents analyze** your needs
        3. **Find matching plans** from our database
        4. **Get personalized recommendations** based on value and fit
        
        ### 🔧 Supported Insurance Types
        - Home Insurance
        - Renters Insurance
        - Auto Insurance
        - Fire Insurance
        - Health Insurance
        
        ### 💡 Need Help?
        - Make sure Ollama is running (`ollama serve`)
        - Try example queries from the sidebar
        - Check that all dependencies are installed
        """)
