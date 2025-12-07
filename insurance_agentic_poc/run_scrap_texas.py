"""Run scrap.py with Texas as location"""
import sys
from io import StringIO
from scrap import InsuranceScraperAgent

# Simulate user input
sys.stdin = StringIO("Texas\n")

# Run the agent
agent = InsuranceScraperAgent()
agent.run()

