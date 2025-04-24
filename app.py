"""
Streamlit frontend for the Travel Assistant.

This provides an alternative UI to the built-in ADK web interface.
It integrates with the ADK Travel Assistant agent and tools.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Tuple, Optional

import streamlit as st
from dotenv import load_dotenv

# Add the current directory to PATH for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import our travel agent
from adk_travel_agent.agent import create_travel_agent

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state() -> None:
    """Initialize the Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "travel_agent" not in st.session_state:
        try:
            # Create the ADK travel agent
            st.session_state.travel_agent = create_travel_agent(
                model_type="chat",
                debug=False
            )
            logger.info("Travel agent created successfully")
        except Exception as e:
            logger.error(f"Error creating travel agent: {e}")
            st.error(f"Failed to initialize travel agent: {str(e)}")
            st.session_state.travel_agent = None
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = os.urandom(16).hex()

def display_sidebar() -> Tuple[str, bool]:
    """
    Display and handle the sidebar UI elements.
    
    Returns:
        Tuple of (selected_model, debug_mode)
    """
    st.sidebar.title("✈️ Travel Assistant")
    st.sidebar.markdown("---")
    
    # Model selection
    model_type = st.sidebar.selectbox(
        "Select LLM Model:",
        options=["chat", "coder"],
        index=0,
        help="Select which LLM model type to use"
    )
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox(
        "Debug Mode",
        value=False,
        help="Enable detailed logging for debugging"
    )
    
    # Add info about the tools
    st.sidebar.markdown("---")
    st.sidebar.subheader("Available Tools")
    
    tools_info = {
        "Flight Search": "Search for flights between destinations",
        "Hotel Search": "Find hotels at a specific location",
        "Travel Info": "Get information about destinations",
        "Web Search": "Search the web for travel information"
    }
    
    for tool, description in tools_info.items():
        st.sidebar.markdown(f"**{tool}**: {description}")
    
    # Example queries
    st.sidebar.markdown("---")
    st.sidebar.subheader("Example Queries")
    example_queries = [
        "Find flights from New York to Tokyo for next Tuesday",
        "What are good hotels in Paris near the Eiffel Tower?",
        "Tell me about visa requirements for Japan",
        "What's the best time to visit Thailand?",
        "What should I pack for a trip to Barcelona in summer?"
    ]
    
    for query in example_queries:
        if st.sidebar.button(query, key=f"example_{hash(query)}"):
            # Add example query to input
            st.session_state.messages.append({"role": "user", "content": query})
            process_user_message(query)
    
    # Reset conversation button
    st.sidebar.markdown("---")
    if st.sidebar.button("Reset Conversation", key="reset_conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = os.urandom(16).hex()
        
        # Recreate the agent with selected settings
        try:
            st.session_state.travel_agent = create_travel_agent(
                model_type=model_type,
                debug=debug_mode
            )
            st.sidebar.success("Conversation reset successfully!")
        except Exception as e:
            st.sidebar.error(f"Error resetting agent: {str(e)}")
    
    return model_type, debug_mode

def format_agent_response(response: Dict[str, Any]) -> str:
    """
    Format the agent response for display.
    
    Args:
        response: The agent response to format.
        
    Returns:
        Formatted response text.
    """
    if isinstance(response, str):
        return response
    
    if isinstance(response, dict):
        # Handle tool outputs
        if "tool_outputs" in response:
            tool_outputs = response["tool_outputs"]
            result_text = ""
            
            for tool_output in tool_outputs:
                tool_name = tool_output.get("tool_name", "Unknown Tool")
                tool_result = tool_output.get("output", {})
                
                if tool_name == "flight_search" and tool_result.get("status") == "success":
                    result_text += format_flight_results(tool_result.get("flights", []))
                elif tool_name == "hotel_search" and tool_result.get("status") == "success":
                    result_text += format_hotel_results(tool_result.get("hotels", []))
                elif tool_name == "travel_info" and tool_result.get("status") == "success":
                    result_text += format_travel_info(tool_result)
                elif tool_name == "web_search" and tool_result.get("status") == "success":
                    result_text += format_search_results(tool_result.get("results", []))
                else:
                    # Generic formatting for any other tool output
                    result_text += f"**{tool_name} Results:**\n\n"
                    result_text += f"```json\n{tool_result}\n```\n\n"
            
            return result_text
        
        # Return the text content if available
        if "text" in response:
            return response["text"]
    
    # Fall back to string representation
    return str(response)

def format_flight_results(flights: List[Dict[str, Any]]) -> str:
    """Format flight search results for display."""
    if not flights:
        return "No flights found matching your criteria."
    
    result = "### 🛫 Flight Search Results\n\n"
    
    for i, flight in enumerate(flights):
        airline = flight.get("airline", "Unknown Airline")
        flight_number = flight.get("flight_number", "")
        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})
        price = flight.get("price", 0)
        duration = flight.get("duration", "")
        
        result += f"**Option {i+1}:** {airline} ({flight_number}) - **${price:.2f}**\n\n"
        result += f"✈️ **From:** {departure.get('airport', 'Unknown')} at {departure.get('time', '').split('T')[1]}\n\n"
        result += f"🛬 **To:** {arrival.get('airport', 'Unknown')} at {arrival.get('time', '').split('T')[1]}\n\n"
        result += f"⏱️ **Duration:** {duration}\n\n"
        result += "---\n\n"
    
    return result

def format_hotel_results(hotels: List[Dict[str, Any]]) -> str:
    """Format hotel search results for display."""
    if not hotels:
        return "No hotels found matching your criteria."
    
    result = "### 🏨 Hotel Search Results\n\n"
    
    for i, hotel in enumerate(hotels):
        name = hotel.get("name", "Unknown Hotel")
        address = hotel.get("address", "")
        star_rating = hotel.get("star_rating", 0)
        price = hotel.get("price_per_night", 0)
        total_price = hotel.get("total_price", 0)
        amenities = hotel.get("amenities", [])
        
        stars = "⭐" * star_rating
        
        result += f"**Option {i+1}:** {name} {stars}\n\n"
        result += f"📍 **Address:** {address}\n\n"
        result += f"💰 **Price:** ${price:.2f} per night (Total: ${total_price:.2f})\n\n"
        
        if amenities:
            result += f"🛎️ **Amenities:** {', '.join(amenities)}\n\n"
        
        result += "---\n\n"
    
    return result

def format_travel_info(info_result: Dict[str, Any]) -> str:
    """Format travel information results for display."""
    destination = info_result.get("destination", "the destination")
    info = info_result.get("info", {})
    
    result = f"### 🌍 Travel Information: {destination}\n\n"
    
    if "overview" in info:
        result += f"**Overview:** {info['overview']}\n\n"
    
    if "best_time_to_visit" in info:
        result += f"**Best Time to Visit:** {info['best_time_to_visit']}\n\n"
    
    if "popular_attractions" in info and isinstance(info["popular_attractions"], list):
        result += "**Popular Attractions:**\n\n"
        for attraction in info["popular_attractions"]:
            result += f"- {attraction}\n"
        result += "\n"
    
    # Add other information if available
    for key, value in info.items():
        if key not in ["overview", "best_time_to_visit", "popular_attractions", "note"]:
            if isinstance(value, str):
                result += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
    
    if "note" in info:
        result += f"*Note: {info['note']}*\n\n"
    
    return result

def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """Format web search results for display."""
    if not search_results:
        return "No search results found."
    
    result = "### 🔍 Search Results\n\n"
    
    for i, item in enumerate(search_results):
        title = item.get("title", "No Title")
        link = item.get("link", "#")
        snippet = item.get("snippet", "No description available")
        
        result += f"**{i+1}. [{title}]({link})**\n\n"
        result += f"{snippet}\n\n"
        result += "---\n\n"
    
    return result

def process_user_message(user_input: str) -> None:
    """
    Process the user's message using the ADK travel agent.
    
    Args:
        user_input: The user's input message.
    """
    if not st.session_state.travel_agent:
        st.error("Travel agent not initialized. Please check the logs and try again.")
        return
    
    # Add a placeholder for the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
    
    try:
        # Directly use the travel agent without the Runner
        # This avoids issues with the Runner class requiring additional parameters in newer ADK versions
        
        # Simple implementation to get a response from the travel agent
        # We'll use a dummy invocation ID for this interaction
        invocation_id = "streamlit-session-" + str(id(st.session_state))
        
        # Handle the user message directly with the agent
        agent_response = st.session_state.travel_agent.handle_user_message(invocation_id, user_input)
        
        # Format the response
        formatted_response = format_agent_response(agent_response)
        
        # Update the placeholder with the formatted response
        message_placeholder.markdown(formatted_response)
        
        # Add the assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        message_placeholder.markdown(f"I'm sorry, I encountered an error: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": f"I'm sorry, I encountered an error: {str(e)}"})

def main() -> None:
    """Main function for the Streamlit Travel Assistant app."""
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar and get settings
    model_type, debug_mode = display_sidebar()
    
    # Set up the main chat interface
    st.title("✈️ Travel Assistant")
    st.write("Ask me about flights, hotels, destinations, or any travel-related questions!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    user_input = st.chat_input("What travel plans can I help you with today?")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process the message
        process_user_message(user_input)

if __name__ == "__main__":
    main()
