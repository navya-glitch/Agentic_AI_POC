"""
Insurance Agentic POC - Version Information
"""

__version__ = "1.0.0"
__app_name__ = "Insurance Agentic POC"
__release_date__ = "2025-12-05"
__author__ = "Insurance Team"
__description__ = "AI-powered insurance search and comparison platform with multi-agent architecture"

VERSION_INFO = {
    "version": __version__,
    "app_name": __app_name__,
    "release_date": __release_date__,
    "author": __author__,
    "description": __description__,
    "features": [
        "Natural language insurance search",
        "Multi-agent orchestration",
        "Real-time plan comparison",
        "Coverage details display",
        "Claim approval timelines",
        "AI-powered recommendations",
        "Support for 5 insurance types",
        "Streamlit web UI",
        "Ollama LLM integration",
    ],
    "python_version": "3.8+",
    "components": {
        "ui": "Streamlit (port 8501)",
        "agents": "LangChain + LanGraph",
        "llm": "Ollama (gemma3:1b)",
        "data": "Dummy plans database",
    },
    "changes": {
        "1.0.0": [
            "Initial release",
            "Streamlit UI with search",
            "Multi-agent architecture",
            "Coverage details",
            "Claim timelines",
            "Premium quotes",
            "Plan comparison",
            "Data export (JSON)",
        ],
    },
}


def get_version():
    """Get the current version string."""
    return __version__


def get_info():
    """Get full version information."""
    return VERSION_INFO


if __name__ == "__main__":
    print(f"{__app_name__} v{__version__}")
    print(f"Release Date: {__release_date__}")
    print(f"Author: {__author__}")
    print(f"\n{__description__}")
