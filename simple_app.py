"""
Simple Streamlit frontend for the Travel Assistant that works with ADK 0.2.0

This version doesn't try to use ADK's internal Runner/InvocationContext and instead
focuses on direct interaction with the agent via API calls.
"""

import os
import sys
import logging
import json
import requests
from typing import List, Dict, Any

import streamlit as st
from dotenv import load_dotenv

# Add the current directory to PATH for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #e6f7ff;
    }
    .chat-message.assistant {
        background-color: #f0f2f5;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex-grow: 1;
    }
    .flight-result {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: white;
    }
    .flight-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    .flight-details {
        display: flex;
        justify-content: space-between;
    }
    .price {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1a73e8;
    }
    .airline {
        color: #555;
    }
    .search-result {
        margin-bottom: 15px;
        padding: 10px;
        border-left: 3px solid #1a73e8;
        background-color: #f8f9fa;
    }
    .search-link {
        color: #1a73e8;
        text-decoration: none;
        font-weight: 500;
    }
    .agent-response {
        background-color: #f0f2f5;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize the Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"conv_{id(st.session_state)}"
        
    if "adk_api_url" not in st.session_state:
        # Default to local ADK server URL
        st.session_state.adk_api_url = "http://localhost:8000"

def display_sidebar():
    """Display and handle the sidebar UI elements."""
    with st.sidebar:
        st.title("✈️ Travel Assistant")
        st.markdown("An AI-powered assistant to help plan your trips")
        
        st.subheader("About")
        st.markdown("""
        This AI Travel Assistant can help you with:
        - Finding flights between destinations
        - Searching for hotels and accommodations
        - Providing travel information
        - Answering general travel questions
        """)
        
        st.subheader("Settings")
        api_url = st.text_input(
            "ADK API URL",
            value=st.session_state.adk_api_url,
            help="The URL of the ADK server API"
        )
        
        if api_url != st.session_state.adk_api_url:
            st.session_state.adk_api_url = api_url
            st.success(f"API URL updated to: {api_url}")
            
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_id = f"conv_{id(st.session_state)}"
            st.success("Conversation cleared!")
        
        st.subheader("Examples")
        example_queries = [
            "Find flights from DMM to RUH next week",
            "What are popular tourist attractions in Dubai?",
            "I need a hotel in Jeddah near the waterfront",
            "What's the best time to visit Riyadh?",
            "Tell me about visa requirements for Saudis visiting Japan"
        ]
        
        for query in example_queries:
            if st.button(query):
                process_user_message(query)
                st.experimental_rerun()

def format_agent_response(response: Dict[str, Any]) -> str:
    """Format the agent response for display."""
    if isinstance(response, str):
        return f"<div class='agent-response'>{response}</div>"
        
    formatted_response = "<div class='agent-response'>"
    
    # Extract text content - handle ADK response format
    if "response" in response and "text" in response["response"]:
        formatted_response += response["response"]["text"]
    elif "content" in response:
        formatted_response += response["content"]
    elif "text" in response:
        formatted_response += response["text"]
    else:
        formatted_response += "I'm sorry, I couldn't process your request properly."
    
    formatted_response += "</div>"
    return formatted_response

def format_flight_results(flights: List[Dict[str, Any]]) -> str:
    """Format flight search results for display with enhanced styling."""
    if not flights:
        return ""
    
    formatted_html = "<h3>Flight Search Results</h3>"
    
    # Add summary information if available
    summary = None
    for flight in flights:
        if "summary" in flight:
            summary = flight["summary"]
            break
    
    if summary:
        formatted_html += "<div style='background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>"
        formatted_html += f"<p><strong>Airlines available:</strong> {', '.join(summary.get('airlines', []))}</p>"
        if "lowest_price" in summary:
            formatted_html += f"<p><strong>Price range:</strong> {summary.get('lowest_price', '')} - {summary.get('highest_price', '')}</p>"
        formatted_html += "</div>"
    
    # Add each flight
    for i, flight in enumerate(flights):
        if "summary" in flight:  # Skip the summary entry
            continue
            
        formatted_html += f"<div class='flight-result'>"
        
        # Flight header
        formatted_html += "<div class='flight-header'>"
        airline_info = ", ".join(flight.get("airlines", ["Airline information unavailable"]))
        formatted_html += f"<div class='airline'>{airline_info}</div>"
        
        if "price" in flight:
            formatted_html += f"<div class='price'>{flight.get('price', '')}</div>"
        formatted_html += "</div>"
        
        # Flight details
        formatted_html += "<div class='flight-details'>"
        formatted_html += f"<div><strong>{flight.get('origin', '')}</strong> → <strong>{flight.get('destination', '')}</strong></div>"
        
        if "duration" in flight:
            formatted_html += f"<div><strong>Duration:</strong> {flight.get('duration', '')}</div>"
        formatted_html += "</div>"
        
        # Additional info
        if "schedule" in flight:
            formatted_html += f"<div><strong>Schedule:</strong> {flight.get('schedule', '')}</div>"
        
        if "additional_info" in flight:
            formatted_html += f"<div><strong>Additional info:</strong> {flight.get('additional_info', '')}</div>"
            
        # Source link if available
        if "source_link" in flight:
            formatted_html += f"<div><a href='{flight.get('source_link', '')}' target='_blank'>View booking options</a></div>"
            
        formatted_html += "</div>"
    
    return formatted_html

def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """Format web search results for display with enhanced styling."""
    if not search_results:
        return ""
    
    formatted_html = "<h3>Web Search Results</h3>"
    
    for result in search_results:
        formatted_html += "<div class='search-result'>"
        title = result.get("title", "No title")
        link = result.get("link", "#")
        snippet = result.get("snippet", "No description available")
        
        formatted_html += f"<a href='{link}' target='_blank' class='search-link'>{title}</a>"
        formatted_html += f"<p>{snippet}</p>"
        formatted_html += "</div>"
    
    return formatted_html

def call_adk_api(user_input: str) -> Dict[str, Any]:
    """Call the ADK API to process the user's message."""
    try:
        # Use the ADK web interface endpoint for agents
        api_url = f"{st.session_state.adk_api_url}/api/agents/working_travel_assistant/run"
        logger.info(f"Calling ADK API at {api_url}")
        
        # Format payload for ADK web interface
        payload = {
            "user_id": "streamlit_user",
            "session_id": st.session_state.conversation_id,
            "message": {
                "role": "user",
                "content": user_input
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling ADK API: {str(e)}")
        return {"error": f"Failed to communicate with the Travel Assistant API: {str(e)}"}

def process_user_message(user_input: str) -> None:
    """Process the user's message by calling the ADK API."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Add a placeholder for the assistant's response
    with st.chat_message("assistant", avatar="✈️"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
    
    try:
        # Call the ADK API
        response = call_adk_api(user_input)
        
        if "error" in response:
            # Handle error response
            error_message = response["error"]
            message_placeholder.markdown(f"Error: {error_message}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_message}"})
            return
        
        # Format the response
        formatted_response = format_agent_response(response)
        
        # Check for any tool outputs in ADK response format
        tool_outputs = []
        if "response" in response and "tool_outputs" in response["response"]:
            tool_outputs = response["response"]["tool_outputs"]
        elif "tool_outputs" in response:
            tool_outputs = response["tool_outputs"]
            
            # Process flight search results
            flight_results = next((output["data"]["flights"] 
                                for output in tool_outputs 
                                if output["tool_name"] in ["flight_search", "real_flight_search"] 
                                and "flights" in output["data"]), None)
            if flight_results:
                formatted_response += format_flight_results(flight_results)
            
            # Process web search results
            search_results = next((output["data"]["results"] 
                                 for output in tool_outputs 
                                 if output["tool_name"] == "web_search" 
                                 and "results" in output["data"]), None)
            if search_results:
                formatted_response += format_search_results(search_results)
        
        # Update the placeholder with the formatted response
        message_placeholder.markdown(formatted_response, unsafe_allow_html=True)
        
        # Add the assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        error_message = f"I'm sorry, I encountered an error: {str(e)}"
        message_placeholder.markdown(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

def main():
    """Main function for the Streamlit Travel Assistant app."""
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Display chat header
    st.header("AI Travel Assistant 🌎✈️🏨")
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role, avatar="👤" if role == "user" else "✈️"):
            st.markdown(content, unsafe_allow_html=True)
    
    # Chat input
    if user_input := st.chat_input("How can I assist with your travel plans today?"):
        process_user_message(user_input)

if __name__ == "__main__":
    main()
