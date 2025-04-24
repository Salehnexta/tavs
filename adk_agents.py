"""
ADK Agents configuration file.

This file exports only the working travel agent for the ADK web interface.
All other agent implementations have been removed.
"""

from working_agent.agent import root_agent

# Export the working travel assistant agent - this is the only one that works properly
# The variable name here needs to be root_agent for ADK to discover it correctly
root_agent = root_agent
