"""
Enhanced Streamlit frontend for the Travel Assistant.

This is a customized UI that works exclusively with the working travel agent.
"""

import os
import sys
import logging
import datetime
import json
from typing import List, Dict, Any, Tuple, Optional

import streamlit as st
from dotenv import load_dotenv
from google.adk.runners import Runner, InMemorySessionService, InvocationContext

# Add the current directory to PATH for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import our working travel agent
from working_agent.agent import root_agent

# Set up session service for ADK
session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "travel_assistant_app"

# Create a runner for the agent
travel_runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

print(f"Runner created for agent '{root_agent.name}'")

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page with enhanced styling
st.set_page_config(
    page_title="ADK Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .flight-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
    }
    .hotel-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .search-result {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #FF9800;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        position: relative;
    }
    .user-message {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .assistant-message {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state() -> None:
    """Initialize the Streamlit session state variables."""
    if "messages" not in st.session_state:
        # Start with a welcome message
        welcome_message = {
            "role": "assistant",
            "content": """
            # Welcome to the ADK Travel Assistant! 👋
            
            I can help you with:
            * ✈️ **Flight searches** between destinations
            * 🏨 **Hotel recommendations** for your stay
            * 🌍 **Travel information** like visa requirements, weather, etc.
            * 🔍 **Web searches** for travel-related information
            
            **Try asking me:**
            * "Find flights from New York to London next week"
            * "What are good hotels in Barcelona?"
            * "Tell me about visa requirements for Japan"
            * "What should I pack for a trip to Thailand in November?"
            """
        }
        st.session_state.messages = [welcome_message]
    
    # Store current date for reference
    if "current_date" not in st.session_state:
        st.session_state.current_date = datetime.datetime.now().strftime("%Y-%m-%d")

def display_sidebar() -> None:
    """Display and handle the sidebar UI elements."""
    with st.sidebar:
        st.image("https://storage.googleapis.com/gweb-cloudblog-publish/images/The_Agent_Development_Kit__Google_Cloud_Blo.max-1300x1300.png", width=250)
        
        st.markdown("## 🧭 Travel Assistant")
        st.markdown("*Powered by Google ADK*")
        
        st.markdown("---")
        
        st.markdown("### 📊 Session Info")
        st.markdown(f"**Date:** {st.session_state.current_date}")
        
        st.markdown("---")
        
        st.markdown("### 🔧 Features")
        st.markdown("✅ Flight Search")
        st.markdown("✅ Hotel Search")
        st.markdown("✅ Travel Information")
        st.markdown("✅ Google Search Integration")
        
        st.markdown("---")
        
        # Add helpful example queries
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "Find flights from London to Paris next week",
            "What are good hotels in Dubai?",
            "Tell me about visa requirements for USA",
            "What's the weather like in Tokyo in April?",
            "What are popular tourist attractions in Rome?",
        ]
        
        for query in example_queries:
            if st.button(query):
                # Use the query as user input
                process_user_message(query)
                # Force a rerun to update the UI
                st.rerun()

def format_agent_response(response: Dict[str, Any]) -> str:
    """
    Format the agent response for display with enhanced styling.
    
    Args:
        response: The agent response to format.
        
    Returns:
        Formatted response text.
    """
    if not response:
        return "I'm sorry, I couldn't generate a response."
    
    if isinstance(response, str):
        return response
    
    # Handle different response formats
    if "content" in response:
        return response["content"]
    
    # Special handling for tool responses
    if "tool_results" in response:
        tool_results = response["tool_results"]
        
        # Format flight search results
        if "flight_search" in tool_results:
            flight_data = tool_results["flight_search"]
            return format_flight_results(flight_data.get("flights", []))
        
        # Format hotel search results
        if "hotel_search" in tool_results:
            hotel_data = tool_results["hotel_search"]
            return format_hotel_results(hotel_data.get("hotels", []))
        
        # Format travel info results
        if "travel_info" in tool_results:
            return format_travel_info(tool_results["travel_info"])
        
        # Format web search results
        if "web_search" in tool_results:
            search_data = tool_results["web_search"]
            return format_search_results(search_data.get("results", []))
    
    # Generic handling for other response formats
    if "message" in response:
        return response["message"]
    
    # Fallback for unknown response format
    return str(response)

def format_flight_results(flights: List[Dict[str, Any]]) -> str:
    """Format flight search results for display with enhanced styling."""
    if not flights:
        return "No flights found matching your criteria."
    
    markdown = ""
    
    # Add summary if available in the first flight
    if "search_summary" in flights[0]:
        summary = flights[0]["search_summary"]
        markdown += f"""
        <div class="info-box">
            <h3>Flight Search Summary</h3>
            <p>Found {summary.get('total_results', len(flights))} flights</p>
            <p><strong>Lowest price:</strong> ${summary.get('price_statistics', {}).get('lowest_price', 'N/A')}</p>
            <p><strong>Fastest flight:</strong> {summary.get('fastest_duration', 'N/A')}</p>
            <p><strong>Airlines available:</strong> {summary.get('airlines_available', 'Multiple')}</p>
        </div>
        """
    
    # Format individual flights
    for i, flight in enumerate(flights[:10]):  # Limit to 10 flights
        price = flight.get("prices", {}).get("economy", "N/A")
        stops = flight.get("stops", 0)
        stops_text = "Non-stop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        
        markdown += f"""
        <div class="flight-card">
            <h4>{flight.get('airline', 'Airline')} - {flight.get('flight_number', '')}</h4>
            <p><strong>{flight.get('origin', '')} → {flight.get('destination', '')}</strong></p>
            <p>Date: {flight.get('departure_date', '')}</p>
            <p>Time: {flight.get('departure_time', '')} - {flight.get('arrival_time', '')}</p>
            <p>Duration: {flight.get('duration', 'N/A')} | {stops_text}</p>
            <p><strong>Price:</strong> ${price}</p>
            <p>Aircraft: {flight.get('aircraft', 'N/A')}</p>
        </div>
        """
    
    return markdown

def format_hotel_results(hotels: List[Dict[str, Any]]) -> str:
    """Format hotel search results for display with enhanced styling."""
    if not hotels:
        return "No hotels found matching your criteria."
    
    markdown = ""
    
    # Format individual hotels
    for hotel in hotels[:10]:  # Limit to 10 hotels
        price = hotel.get("price_per_night", "N/A")
        
        markdown += f"""
        <div class="hotel-card">
            <h4>{hotel.get('name', 'Hotel')}</h4>
            <p>{hotel.get('location', 'Location')}</p>
            <p><strong>Rating:</strong> {hotel.get('rating', 'N/A')}/5</p>
            <p><strong>Price:</strong> ${price}/night</p>
            <p><strong>Amenities:</strong> {', '.join(hotel.get('amenities', ['N/A']))}</p>
            <p>{hotel.get('description', '')}</p>
        </div>
        """
    
    return markdown

def format_travel_info(info_result: Dict[str, Any]) -> str:
    """Format travel information results for display with enhanced styling."""
    if not info_result or "status" in info_result and info_result["status"] == "error":
        return "Sorry, I couldn't retrieve travel information for your query."
    
    markdown = ""
    
    # Format destination information
    destination = info_result.get("destination", {})
    if destination:
        markdown += f"""
        <div class="info-box">
            <h3>{destination.get('name', 'Destination')}</h3>
            <p>{destination.get('description', '')}</p>
            <p><strong>Country:</strong> {destination.get('country', 'N/A')}</p>
            <p><strong>Language:</strong> {destination.get('language', 'N/A')}</p>
            <p><strong>Currency:</strong> {destination.get('currency', 'N/A')}</p>
        </div>
        """
    
    # Format travel requirements
    requirements = info_result.get("requirements", {})
    if requirements:
        markdown += f"""
        <div class="info-box">
            <h3>Travel Requirements</h3>
            <p><strong>Visa:</strong> {requirements.get('visa', 'N/A')}</p>
            <p><strong>Passport:</strong> {requirements.get('passport', 'N/A')}</p>
            <p><strong>Vaccinations:</strong> {requirements.get('vaccinations', 'N/A')}</p>
        </div>
        """
    
    # Format weather information
    weather = info_result.get("weather", {})
    if weather:
        markdown += f"""
        <div class="info-box">
            <h3>Weather Information</h3>
            <p><strong>Current:</strong> {weather.get('current', 'N/A')}</p>
            <p><strong>Forecast:</strong> {weather.get('forecast', 'N/A')}</p>
            <p><strong>Best time to visit:</strong> {weather.get('best_time', 'N/A')}</p>
        </div>
        """
    
    return markdown

def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """Format web search results for display with enhanced styling."""
    if not search_results:
        return "No search results found."
    
    markdown = ""
    
    for result in search_results:
        title = result.get("title", "No title")
        link = result.get("link", "#")
        snippet = result.get("snippet", "No description available")
        
        markdown += f"""
        <div class="search-result">
            <h4><a href="{link}" target="_blank">{title}</a></h4>
            <p><small>{link}</small></p>
            <p>{snippet}</p>
        </div>
        """
    
    return markdown

def process_user_message(user_input: str) -> None:
    """
    Process the user's message using our working travel agent.
    
    Args:
        user_input: The user's input message.
    """
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Add a placeholder for the assistant's response
    with st.chat_message("assistant", avatar="✈️"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
    
    try:
        # Get or create a unique session ID for this Streamlit session
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{id(st.session_state)}"
            
        # Get or create a unique user ID for this user
        if "user_id" not in st.session_state:
            st.session_state.user_id = f"user_{id(st.session_state)}"
        
        # Create an invocation context
        invocation_context = InvocationContext()
        
        # Use the runner to run the agent
        runner_response = travel_runner.run(
            user_message=user_input,
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            invocation_context=invocation_context
        )
        
        # Extract the text response
        response_text = ""
        if runner_response and hasattr(runner_response, "message") and runner_response.message:
            response_text = runner_response.message.content
        elif isinstance(runner_response, dict) and "content" in runner_response:
            response_text = runner_response["content"]
        else:
            response_text = "I apologize, but I'm having trouble processing your request."
        
        # Get any tool outputs
        tool_outputs = []
        if hasattr(runner_response, "tool_outputs") and runner_response.tool_outputs:
            tool_outputs = runner_response.tool_outputs
        
        # Extract the response content - handle various possible response formats
        response_content = ""
        if isinstance(response, dict) and "content" in response:
            response_content = response["content"]
        elif hasattr(response, "message") and hasattr(response.message, "content"):
            response_content = response.message.content
        elif isinstance(response, str):
            response_content = response
        else:
            response_content = "I'm sorry, I couldn't generate a response in the expected format."
        
        # Initialize tool result variables
        flight_results = None
        hotel_results = None
        travel_info = None
        search_results = None
        
        # Try to extract tool outputs from the response
        tool_outputs = []
        
        # Check if response has tool_outputs attribute
        if hasattr(response, 'tool_outputs') and response.tool_outputs:
            tool_outputs = response.tool_outputs
        # Check if response is a dict with tool_outputs key
        elif isinstance(response, dict) and 'tool_outputs' in response:
            tool_outputs = response['tool_outputs']
            
            # Process tool outputs
            for tool_output in tool_outputs:
                if tool_output.tool_name == "flight_search" or tool_output.tool_name == "real_flight_search":
                    try:
                        flight_data = tool_output.data
                        if isinstance(flight_data, dict) and 'flights' in flight_data:
                            flight_results = flight_data.get('flights', [])
                    except Exception as e:
                        logger.error(f"Error processing flight results: {e}")
                
                elif tool_output.tool_name == "hotel_search":
                    try:
                        hotel_data = tool_output.data
                        if isinstance(hotel_data, dict) and 'hotels' in hotel_data:
                            hotel_results = hotel_data.get('hotels', [])
                    except Exception as e:
                        logger.error(f"Error processing hotel results: {e}")
                
                elif tool_output.tool_name == "travel_info":
                    try:
                        travel_info = tool_output.data
                    except Exception as e:
                        logger.error(f"Error processing travel info: {e}")
                
                elif tool_output.tool_name == "web_search":
                    try:
                        search_data = tool_output.data
                        if isinstance(search_data, dict) and 'results' in search_data:
                            search_results = search_data.get('results', [])
                    except Exception as e:
                        logger.error(f"Error processing search results: {e}")
        
        # Format the response with any tool outputs
        formatted_response = f"<div class='agent-response'>{response_content}</div>"
        
        # Add any formatted tool outputs
        if flight_results:
            formatted_response += format_flight_results(flight_results)
        
        if hotel_results:
            formatted_response += format_hotel_results(hotel_results)
        
        if travel_info:
            formatted_response += format_travel_info(travel_info)
        
        if search_results:
            formatted_response += format_search_results(search_results)
        
        # Update the placeholder with the formatted response
        message_placeholder.markdown(formatted_response, unsafe_allow_html=True)
        
        # Add the assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        error_message = f"I'm sorry, I encountered an error: {str(e)}"
        message_placeholder.markdown(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

def main() -> None:
    """Main function for the enhanced Streamlit Travel Assistant app."""
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Display app header
    st.markdown('<h1 class="main-header">✈️ ADK Travel Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI-powered travel companion</p>', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        role_class = "user-message" if message["role"] == "user" else "assistant-message"
        avatar = "👤" if message["role"] == "user" else "✈️"
        
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(f'<div class="{role_class}">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("What travel assistance do you need?")
    if user_input:
        process_user_message(user_input)

if __name__ == "__main__":
    main()
