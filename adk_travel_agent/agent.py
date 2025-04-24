"""
Travel Agent implementation using Google's Agent Development Kit (ADK).

This module defines the travel assistant agent with specialized tools for:
- Flight searches
- Hotel searches
- Travel information retrieval
- General web searches for travel data

The agent uses DeepSeek (via OpenAI SDK) as the primary LLM with Groq as fallback.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk import Runner

# Import tools
from .flight_tool import FlightSearchTool
from .hotel_tool import HotelSearchTool
from .travel_info_simple import TravelInfoTool
from .web_search_tool import WebSearchTool

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Travel agent instruction template
TRAVEL_AGENT_INSTRUCTION = """
You are an AI-powered Travel Assistant that helps users plan trips through natural language interaction. 

You can assist with various travel-related tasks:
- Find flights between destinations
- Search for hotels and accommodations
- Provide travel information about destinations (visa requirements, weather, attractions, etc.)
- Search the web for travel-related information

Tools available to you:
- flight_search: Search for flights between airports on specific dates
- hotel_search: Find hotels at a specific location with various criteria
- travel_info: Get information about travel destinations (visa, weather, attractions, etc.)
- web_search: Search the web for travel-related information

When providing recommendations, consider factors like price, convenience, user preferences, 
and availability. Always present options rather than making decisions for the user.
"""

def create_travel_agent(model_type: str = "chat", debug: bool = False) -> LlmAgent:
    """
    Create and return a Travel Assistant agent with specialized tools.
    
    Args:
        model_type: Type of model to use (chat or coder)
        debug: Whether to enable debug mode
        
    Returns:
        A fully configured Travel Assistant agent
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create the specialized travel tools
    flight_tool = FlightSearchTool()
    hotel_tool = HotelSearchTool()
    travel_info_tool = TravelInfoTool()
    web_search_tool = WebSearchTool()
    
    # For demo purposes, use a standard model - in production, this would be replaced with DeepSeek
    # The actual DeepSeek integration would be done through an environment variable config
    model = "gemini-1.5-flash"
    if model_type == "coder":
        model = "gemini-1.5-pro"
    
    # Create the travel agent
    travel_agent = LlmAgent(
        name="travel_assistant",
        instruction=TRAVEL_AGENT_INSTRUCTION,
        model=model,  # Using a standard model for demo purposes
        tools=[flight_tool, hotel_tool, travel_info_tool, web_search_tool],
        description="An AI assistant that helps with travel planning and information."
    )
    
    logger.info("Travel Assistant agent created successfully")
    return travel_agent

def create_interactive_runner(agent: Optional[LlmAgent] = None) -> Runner:
    """
    Create an interactive runner for the Travel Assistant agent.
    
    Args:
        agent: An existing agent instance or None to create a new one.
        
    Returns:
        A Runner for the Travel Assistant agent.
    """
    if agent is None:
        agent = create_travel_agent()
    
    return Runner(agent=agent)
