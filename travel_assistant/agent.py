"""
Travel Assistant agent implementation.

This file creates and exports the travel assistant agent for the ADK web interface.
"""

import os
import logging
from dotenv import load_dotenv

# Import ADK components
from google.adk.agents import LlmAgent
from google.adk import Runner

# Import custom LLM adapter for DeepSeek
from adk_travel_agent.llm_adapter import create_adk_model

# Import our travel agent tools
from adk_travel_agent.flight_tool import FlightSearchTool
from adk_travel_agent.hotel_tool import HotelSearchTool
from adk_travel_agent.travel_info_simple import TravelInfoTool
from adk_travel_agent.web_search_tool import WebSearchTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The instruction prompt for the travel assistant
TRAVEL_AGENT_INSTRUCTION = """
You are a helpful AI travel assistant. Your goal is to help users with travel planning by providing
information about destinations, flight and hotel options, and answering travel-related questions.

Use the available tools to:
1. Search for flights between destinations
2. Find hotels at specific locations
3. Provide travel information about destinations (visa requirements, weather, etc.)
4. Search the web for travel-related information

Always be courteous, professional, and provide accurate information. If you don't know something or 
can't find the requested information, be honest about it and suggest alternatives.
"""

def create_agent(model_type: str = "chat", debug: bool = False):
    """
    Create the travel assistant agent.
    
    Args:
        model_type: Type of model to use (chat or coder)
        debug: Whether to enable debug mode
        
    Returns:
        LlmAgent: The configured travel assistant agent.
    """
    # Create the tools
    flight_tool = FlightSearchTool()
    hotel_tool = HotelSearchTool()
    travel_info_tool = TravelInfoTool()
    web_search_tool = WebSearchTool()
    
    # Use DeepSeek model with OpenAI SDK
    model = create_adk_model(model_type="chat")
    
    # Fallback to a default model if the DeepSeek model creation fails
    if model is None:
        logger.warning("Failed to create DeepSeek model. Check API keys and connectivity.")
        from google.adk.llms import GeminiModel
        model = GeminiModel(name="gemini-1.0-pro")
        logger.info("Using Gemini model as fallback")
    
    # Create the travel agent with the tools
    travel_agent = LlmAgent(
        name="travel_assistant",
        instruction=TRAVEL_AGENT_INSTRUCTION,
        model=model,
        tools=[flight_tool, hotel_tool, travel_info_tool, web_search_tool],
        description="An AI assistant that helps with travel planning and information."
    )
    
    logger.info("Travel Assistant agent created successfully")
    return travel_agent

# Create and export the agent for ADK web interface
travel_assistant = create_agent(model_type="chat")

# Create interactive runner for testing
def create_interactive_runner(agent=None):
    """
    Create an interactive runner for the Travel Assistant agent.
    
    Args:
        agent: An existing agent instance or None to create a new one.
        
    Returns:
        A Runner for the Travel Assistant agent.
    """
    if agent is None:
        agent = travel_assistant
        
    return Runner(agent=agent)
