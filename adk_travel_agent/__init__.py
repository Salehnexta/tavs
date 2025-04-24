"""
ADK Travel Agent package initialization.
"""

__version__ = "1.0.0"

# Expose the agent module for discovery by ADK web interface
from . import agent
from .agent import create_travel_agent
