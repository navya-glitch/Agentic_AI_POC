# Insurance Agentic UI

A modern web interface for the Insurance Search & Comparison PoC built with Streamlit.

## Features

✨ **Modern Web Interface**
- Clean, intuitive search interface
- Real-time plan comparison
- Interactive plan cards with detailed information
- Beautiful data visualization

🔍 **Smart Search**
- Natural language query support
- Intent analysis and extraction
- Query enhancement with smart defaults
- Automatic state and insurance type detection

📊 **Comprehensive Results**
- Top plan recommendations with AI explanations
- Plan comparison table
- Detailed metrics (premium, coverage, deductible, ratings, reviews)
- Value scoring system

🤖 **AI-Powered**
- Intent extraction to understand user needs
- Query enhancement with contextual defaults
- Plan fetching and scoring
- Natural language recommendations and explanations

## Installation

### 1. Install Dependencies

```bash
cd insurance_agentic_poc
pip install -r agents/requirements.txt
```

### 2. Setup (if not already done)

Make sure you have:
- Python 3.8+
- Ollama running locally (for the LLM integration)

## Running the UI

### Start the Streamlit App

```bash
streamlit run ui.py
```

The application will open in your default browser at `http://localhost:8501`

### Alternative: Run in a specific port

```bash
streamlit run ui.py --server.port 8000
```

## Usage

1. **Enter Your Query**: Type what insurance you're looking for
   - Example: "Home insurance with pet and swimming pool in CA"
   - Example: "Best health insurance in TX for family"
   - Example: "Cheap renters insurance in NY"

2. **Review Results**: The app will show you:
   - Top 3 recommended plans with full details
   - AI-powered explanation of recommendations
   - Side-by-side comparison with all matching plans

3. **Explore Details**: Use the tabs to view:
   - **Results**: Top recommendations with AI explanation
   - **Intent Analysis**: How the system understood your query
   - **Enhanced Query**: Query with smart defaults added
   - **Detailed Plans**: Full table of all matching plans

4. **Download**: Export plan data as JSON for further analysis

## Example Queries

- "Home insurance with pet and swimming pool in CA"
- "Best health insurance in TX for family"
- "Cheap renters insurance in NY"
- "Auto insurance in Florida"
- "Fire insurance in Oregon"

## Supported Insurance Types

- 🏠 Home Insurance
- 🚨 Renters Insurance
- 🚗 Auto Insurance
- 🔥 Fire Insurance
- 💊 Health Insurance

## File Structure

```
insurance_agentic_poc/
├── ui.py                          # Main Streamlit application
├── main.py                        # CLI version (original)
├── ollama_client.py               # Ollama integration
├── data_plans.py                  # Dummy insurance plans data
├── web_scrapper.py                # Web scraping utilities
├── agents/
│   ├── __init__.py
│   ├── intent_agent.py            # Intent extraction agent
│   ├── query_enhancement_agent.py # Query enhancement agent
│   ├── connectors_agent.py        # Plan fetching and scoring
│   ├── recommendation_agent.py    # Recommendation engine
│   └── requirements.txt           # Python dependencies
```

## How It Works

The application follows a multi-agent architecture:

1. **Intent Agent** → Extracts structured intent from natural language
2. **Query Enhancement Agent** → Adds defaults and context
3. **Connectors Agent** → Fetches and scores matching plans
4. **Recommendation Agent** → Generates personalized recommendations

## Troubleshooting

### Port Already in Use
```bash
streamlit run ui.py --server.port 8002
```

### Ollama Not Running
Make sure Ollama is running locally:
```bash
ollama serve
```

### No Plans Found
Try different keywords or supported insurance types (home, health, auto, fire, renters)

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **LLM**: Ollama (local)
- **AI Framework**: LangChain
- **Graph Computing**: LanGraph

## Notes

- This is a PoC (Proof of Concept)
- Plans are dummy/demo data for testing
- Streamlit automatically reloads when code changes
