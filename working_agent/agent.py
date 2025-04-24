"""
Working Travel Assistant Agent implementation for current ADK version.

This agent uses the direct string model approach as shown in the official
Google Developer blog examples.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Import our travel agent tools
from adk_travel_agent.real_flight_tool import RealFlightSearchTool  # New real flight search tool
from adk_travel_agent.flight_tool import FlightSearchTool  # Keep as fallback
from adk_travel_agent.hotel_tool import HotelSearchTool
from adk_travel_agent.travel_info_simple import TravelInfoTool
from adk_travel_agent.web_search_tool import WebSearchTool

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE")

# Validate environment variables
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Travel agent instruction template
TRAVEL_AGENT_INSTRUCTION = """
You are an AI-powered Travel Assistant that helps users plan trips through natural language interaction. 

You can assist with various travel-related tasks:
- Find real flights between destinations using actual flight data from Google search
- Search for hotels and accommodations
- Provide travel information about destinations (visa requirements, weather, attractions, etc.)
- Search the web for travel-related data and recommendations

When searching for flights, ALWAYS use the real_flight_search tool first to get actual flight data. Only use the regular flight_search as a fallback if real flight data is unavailable.

Always be helpful, accurate, and professional. If you don't know something or can't find
the requested information, be honest about it and suggest alternatives if possible.
"""

# Create the tools
real_flight_tool = RealFlightSearchTool()  # Real flight search using Serper API
flight_tool = FlightSearchTool()  # Keep mock flight search as fallback
hotel_tool = HotelSearchTool()
travel_info_tool = TravelInfoTool()
web_search_tool = WebSearchTool()

def create_fallback_model():
    """
    Create a LiteLLM model with fallback mechanism.
    First try DeepSeek, then fall back to Groq if DeepSeek is unavailable.
    
    Returns:
        A LiteLLM model instance configured for either DeepSeek or Groq.
    """
    # Try DeepSeek first (primary model)
    if DEEPSEEK_API_KEY and DEEPSEEK_API_BASE:
        try:
            logger.info(f"Attempting to use DeepSeek as primary model with API base: {DEEPSEEK_API_BASE}")
            
            # Configure environment for DeepSeek
            os.environ["OPENAI_API_KEY"] = DEEPSEEK_API_KEY
            os.environ["OPENAI_API_BASE"] = DEEPSEEK_API_BASE
            
            # Return DeepSeek model via LiteLLM
            return LiteLlm(model="deepseek/deepseek-chat")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek model: {str(e)}")
            logger.info("Falling back to Groq model...")
    else:
        logger.warning("DeepSeek API key or base URL not configured. Falling back to Groq.")
    
    # Fall back to Groq if DeepSeek failed or is not configured
    if GROQ_API_KEY and GROQ_API_BASE:
        try:
            logger.info(f"Attempting to use Groq as fallback model with API base: {GROQ_API_BASE}")
            
            # Configure environment for Groq
            os.environ["OPENAI_API_KEY"] = GROQ_API_KEY
            os.environ["OPENAI_API_BASE"] = GROQ_API_BASE
            
            # Return Groq model via LiteLLM
            return LiteLlm(model="groq/llama3-70b-8192")
        except Exception as e:
            logger.error(f"Failed to initialize Groq model: {str(e)}")
    else:
        logger.warning("Groq API key or base URL not configured.")
    
    # If both DeepSeek and Groq fail, raise an exception
    raise ValueError("Failed to initialize DeepSeek or Groq models. Check API keys and base URLs.")

# Create the travel assistant agent with fallback model mechanism
# IMPORTANT: ADK web interface expects the agent variable to be named 'root_agent'
try:
    fallback_model = create_fallback_model()
    logger.info(f"Successfully created model: {fallback_model}")
    
    root_agent = LlmAgent(
        name="working_travel_assistant",
        model=fallback_model,  # Use fallback model (DeepSeek or Groq)
        instruction=TRAVEL_AGENT_INSTRUCTION,
        tools=[real_flight_tool, flight_tool, hotel_tool, travel_info_tool, web_search_tool],
        description="AI-powered Travel Assistant that helps with flights, hotels, and travel information."
    )
    logger.info("Successfully created travel assistant agent")
except Exception as e:
    logger.error(f"Failed to create travel assistant agent: {str(e)}")
    raise
