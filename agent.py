"""
ADK Travel Assistant Agent - Direct export for ADK web interface.

This file creates and directly exports the travel assistant agent 
for discovery by the ADK web interface.
"""

from adk_travel_agent.agent import create_travel_agent

# Create and export the travel assistant agent
# This needs to be a top-level variable named the same as the intended agent name
travel_assistant = create_travel_agent(model_type="chat", debug=True)
