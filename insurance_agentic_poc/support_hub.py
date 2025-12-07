# support_hub.py
"""
Customer support utilities: FAQ, chatbot prompts, support channels, etc.
"""

FAQ_TOPICS = {
    "buying": [
        {
            "q": "How do I compare two policies?",
            "a": "Use the 'Compare' tab. Select two plans to see side-by-side premium, coverage, features, and benefits.",
        },
        {
            "q": "Can I customize my policy?",
            "a": "Yes! Add or remove riders (add-ons), increase coverage, change deductibles—all on the checkout page.",
        },
        {
            "q": "How fast can I buy?",
            "a": "You can get a quote instantly and buy in minutes. No lengthy form-filling needed.",
        },
        {
            "q": "Do I need to upload documents?",
            "a": "We auto-fill from uploaded ID/documents where possible. KYC upload is optional for faster verification.",
        },
    ],
    "pricing": [
        {
            "q": "Why did my premium go up?",
            "a": "Premiums increase due to: age, claims history, new risk factors (e.g., high-traffic location), or inflation adjustments.",
        },
        {
            "q": "Can I get a discount?",
            "a": "Yes—bundling policies (home + auto), safety features, claim-free years, and loyalty discounts all help reduce premiums.",
        },
        {
            "q": "What's a deductible?",
            "a": "The amount you pay out-of-pocket before insurance covers the rest. Higher deductible = lower premium.",
        },
    ],
    "claims": [
        {
            "q": "How do I file a claim?",
            "a": "1. Go to 'My Claims' in your wallet. 2. Upload photos/documents. 3. Describe the incident. 4. We'll contact you within 24 hours.",
        },
        {
            "q": "How long does a claim take?",
            "a": "Simple claims: 3–5 days. Complex claims: 1–2 weeks. You can track status in real-time on your dashboard.",
        },
        {
            "q": "What documents do I need?",
            "a": "Depends on claim type. Photos of damage, receipts, police report (if theft), medical reports (if health), etc.",
        },
        {
            "q": "Can I track my claim?",
            "a": "Yes! Real-time status updates are available in your wallet. You'll also get WhatsApp/SMS updates.",
        },
    ],
    "renewal": [
        {
            "q": "When does my policy renew?",
            "a": "Check your policy details or wallet. You'll get a reminder 30 days before expiry.",
        },
        {
            "q": "Can I renew in one click?",
            "a": "Yes! Use 'One-Click Renewal' button. If enabled, auto-renewal happens automatically.",
        },
        {
            "q": "What if I want to change my plan at renewal?",
            "a": "You can upgrade/downgrade coverage or switch to a different plan during renewal. No penalty.",
        },
    ],
    "general": [
        {
            "q": "Is my data secure?",
            "a": "Yes, all data is encrypted. We follow banking-grade security standards and comply with data protection laws.",
        },
        {
            "q": "Can I cancel my policy?",
            "a": "Yes, within the first 30 days for a full refund. After that, you can cancel anytime with notice.",
        },
        {
            "q": "How do I contact support?",
            "a": "Chatbot (24/7), live agent (9 AM–9 PM), WhatsApp, email, or phone. All available on this platform.",
        },
    ],
}

CHATBOT_CONTEXT = """
You are a friendly, knowledgeable insurance support assistant. 
- Be concise and clear (no jargon, explain in simple terms).
- If you don't know, offer to connect with a live agent.
- Provide step-by-step instructions for common tasks.
- Be empathetic, especially for claims-related questions.
"""

SUPPORT_CHANNELS = {
    "chatbot": {
        "name": "Chatbot",
        "hours": "24/7",
        "response_time": "Instant",
        "icon": "🤖",
        "description": "Quick answers to common questions.",
    },
    "live_agent": {
        "name": "Live Agent",
        "hours": "9 AM - 9 PM IST",
        "response_time": "< 2 minutes",
        "icon": "👤",
        "description": "Talk to a real person for complex issues.",
    },
    "whatsapp": {
        "name": "WhatsApp",
        "hours": "24/7",
        "response_time": "< 5 minutes",
        "icon": "💬",
        "description": "Chat with us on WhatsApp for quick help.",
    },
    "email": {
        "name": "Email",
        "hours": "Monday–Friday",
        "response_time": "< 24 hours",
        "icon": "📧",
        "description": "Send detailed inquiries via email.",
    },
    "phone": {
        "name": "Phone",
        "hours": "9 AM - 9 PM IST",
        "response_time": "Direct connection",
        "icon": "📞",
        "description": "Call our support line for immediate help.",
    },
}

def get_faq_section(topic: str) -> list:
    """Get FAQ items for a topic."""
    return FAQ_TOPICS.get(topic, [])

def get_all_faq() -> dict:
    """Get all FAQ topics."""
    return FAQ_TOPICS

def search_faq(query: str) -> list:
    """Search FAQ for matching questions/answers."""
    results = []
    query_lower = query.lower()
    for topic, items in FAQ_TOPICS.items():
        for item in items:
            if query_lower in item["q"].lower() or query_lower in item["a"].lower():
                results.append({"topic": topic, **item})
    return results

def get_support_channels() -> dict:
    """Get all support channels info."""
    return SUPPORT_CHANNELS

def format_chatbot_response(response_text: str) -> str:
    """Format chatbot response with friendly markdown."""
    return f"🤖 **Assistant:** {response_text}"
