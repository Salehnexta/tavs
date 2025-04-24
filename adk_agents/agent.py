"""
ADK Travel Assistant Agent implementation for ADK 0.2.0.

This file creates and exports a properly structured travel assistant agent
that follows ADK 0.2.0 conventions for discovery and deployment.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import GeminiModel

# Import our travel agent tools
from adk_travel_agent.flight_tool import FlightSearchTool
from adk_travel_agent.hotel_tool import HotelSearchTool
from adk_travel_agent.travel_info_simple import TravelInfoTool
from adk_travel_agent.web_search_tool import WebSearchTool

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Travel agent instruction template
TRAVEL_AGENT_INSTRUCTION = """
You are an AI-powered Travel Assistant that helps users plan trips through natural language interaction. 

You can assist with various travel-related tasks:
- Find flights between destinations
- Search for hotels and accommodations
- Provide travel information about destinations (visa requirements, weather, attractions, etc.)
- Search the web for travel-related data and recommendations

Always be helpful, accurate, and professional. If you don't know something or can't find
the requested information, be honest about it and suggest alternatives if possible.
"""

# Create the tools
flight_tool = FlightSearchTool()
hotel_tool = HotelSearchTool()
travel_info_tool = TravelInfoTool()
web_search_tool = WebSearchTool()

def create_model():
    """
    Create the LLM model for the travel assistant.
    
    This function tries to use DeepSeek via our custom adapter if available,
    otherwise falls back to using Gemini.
    
    Returns:
        A configured model for the travel assistant
    """
    try:
        # First try to use our custom DeepSeek integration
        from adk_travel_agent.llm_adapter import create_adk_model
        model = create_adk_model(model_type="chat")
        
        if model is not None:
            logger.info("Using DeepSeek model via custom adapter")
            return model
    except Exception as e:
        logger.warning(f"Failed to load custom DeepSeek model: {e}")
    
    # Fall back to Gemini model
    logger.info("Using Gemini model as fallback")
    return GeminiModel(name="gemini-1.0-pro")

# Create the travel assistant agent with the proper ADK 0.2.0 structure
travel_assistant = LlmAgent(
    name="travel_assistant",
    model=create_model(),
    instruction=TRAVEL_AGENT_INSTRUCTION,
    tools=[flight_tool, hotel_tool, travel_info_tool, web_search_tool],
    description="AI-powered Travel Assistant that helps with flights, hotels, and travel information."
)
