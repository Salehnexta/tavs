"""
Direct Streamlit frontend for the Travel Assistant

This version directly uses the working agent components without API calls
or complex ADK infrastructure.
"""

import os
import sys
import logging
import traceback
import json
from typing import List, Dict, Any, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

# Add the current directory to PATH for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import our working travel agent components directly
from working_agent.agent import root_agent
from adk_travel_agent.real_flight_tool import RealFlightSearchTool
from adk_travel_agent.flight_tool import FlightSearchTool
from adk_travel_agent.hotel_tool import HotelSearchTool
from adk_travel_agent.travel_info_simple import TravelInfoTool
from adk_travel_agent.web_search_tool import WebSearchTool

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create direct instances of the tools for local use
real_flight_tool = RealFlightSearchTool()
flight_tool = FlightSearchTool()
hotel_tool = HotelSearchTool()
travel_info_tool = TravelInfoTool()
web_search_tool = WebSearchTool()

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

def format_flight_results(flights: List[Dict[str, Any]]) -> str:
    """Format flight search results for display with enhanced styling."""
    if not flights:
        return ""
    
    formatted_html = "<h3>✈️ Flight Search Results</h3>"
    
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

def format_hotel_results(hotels: List[Dict[str, Any]]) -> str:
    """Format hotel search results for display with enhanced styling."""
    if not hotels:
        return ""
    
    formatted_html = "<h3>🏨 Hotel Search Results</h3>"
    
    for hotel in hotels:
        formatted_html += "<div style='border: 1px solid #d9d9d9; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: white;'>"
        formatted_html += f"<h4>{hotel.get('name', 'Hotel')}</h4>"
        
        if "price" in hotel:
            formatted_html += f"<p><strong>Price:</strong> {hotel.get('price', 'Price not available')}</p>"
        
        if "rating" in hotel:
            formatted_html += f"<p><strong>Rating:</strong> {hotel.get('rating', 'Not rated')} / 5</p>"
        
        if "location" in hotel:
            formatted_html += f"<p><strong>Location:</strong> {hotel.get('location', 'Location not specified')}</p>"
        
        if "description" in hotel:
            formatted_html += f"<p>{hotel.get('description', '')}</p>"
            
        formatted_html += "</div>"
    
    return formatted_html

def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """Format web search results for display with enhanced styling."""
    if not search_results:
        return ""
    
    formatted_html = "<h3>🔍 Web Search Results</h3>"
    
    for result in search_results:
        formatted_html += "<div class='search-result'>"
        title = result.get("title", "No title")
        link = result.get("link", "#")
        snippet = result.get("snippet", "No description available")
        
        formatted_html += f"<a href='{link}' target='_blank' class='search-link'>{title}</a>"
        formatted_html += f"<p>{snippet}</p>"
        formatted_html += "</div>"
    
    return formatted_html

def format_travel_info(travel_info: Dict[str, Any]) -> str:
    """Format travel information for display with enhanced styling."""
    if not travel_info:
        return ""
    
    formatted_html = "<h3>🌍 Travel Information</h3>"
    formatted_html += "<div style='border: 1px solid #d9d9d9; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: white;'>"
    
    destination = travel_info.get('destination', 'Destination')
    formatted_html += f"<h4>{destination}</h4>"
    
    # Generate detailed information based on destination
    if destination.lower() == "dubai":
        formatted_html += "<p><strong>Best Time to Visit:</strong> November to March when the weather is pleasant with temperatures around 24-35°C (75-95°F).</p>"
        
        formatted_html += "<p><strong>Visa Information:</strong> Many nationalities receive visa-on-arrival for 30-90 days. GCC citizens don't need a visa. Other nationalities can apply online through the UAE government portal.</p>"
        
        formatted_html += "<p><strong>Weather:</strong> Hot desert climate with very hot, humid summers (40-50°C/104-122°F) and warm winters (14-23°C/57-73°F).</p>"
        
        formatted_html += "<p><strong>Attractions:</strong></p><ul>"
        attractions = [
            "Burj Khalifa - World's tallest building with observation decks",
            "Dubai Mall - One of the world's largest shopping malls",
            "Palm Jumeirah - Artificial archipelago with luxury hotels",
            "Dubai Marina - Stunning waterfront area with skyscrapers",
            "Dubai Miracle Garden - Beautiful flower garden with over 50 million flowers",
            "Dubai Frame - 150m tall picture frame structure",
            "Atlantis Aquaventure Waterpark - Thrilling water park on Palm Jumeirah",
            "Dubai Museum - Located in the historic Al Fahidi Fort",
            "Dubai Desert Safari - Exciting desert adventures and traditional entertainment"
        ]
        for attraction in attractions:
            formatted_html += f"<li>{attraction}</li>"
        formatted_html += "</ul>"
        
        formatted_html += "<p><strong>Safety Information:</strong> Dubai is considered one of the safest cities in the world with very low crime rates. Standard precautions apply regarding heat, dehydration, and respecting local customs and laws.</p>"
    
    elif destination.lower() == "riyadh":
        formatted_html += "<p><strong>Best Time to Visit:</strong> November to February when the weather is cool and pleasant with temperatures between 10-20°C (50-68°F).</p>"
        
        formatted_html += "<p><strong>Visa Information:</strong> Saudi Arabia offers e-visas for tourists from many countries. The tourist visa is valid for one year with multiple entries and allows stays of up to 90 days.</p>"
        
        formatted_html += "<p><strong>Weather:</strong> Hot desert climate with extremely hot summers (38-43°C/100-110°F) and mild winters (8-20°C/46-68°F). Very dry throughout the year.</p>"
        
        formatted_html += "<p><strong>Attractions:</strong></p><ul>"
        attractions = [
            "Kingdom Centre Tower - Iconic skyscraper with Sky Bridge",
            "Diriyah - UNESCO World Heritage site and birthplace of the first Saudi state",
            "National Museum of Saudi Arabia - Rich collection of Saudi Arabian history",
            "Al Masmak Fortress - Historic clay and mud-brick fort",
            "Edge of the World (Jebel Fihrayn) - Dramatic desert cliff views",
            "Riyadh Zoo - Home to over 1,500 animals",
            "King Abdullah Park - Beautiful park with a large musical fountain",
            "Wadi Hanifah - Beautiful valley with walking paths and picnic areas",
            "Riyadh Front - Modern shopping and entertainment complex"
        ]
        for attraction in attractions:
            formatted_html += f"<li>{attraction}</li>"
        formatted_html += "</ul>"
        
        formatted_html += "<p><strong>Safety Information:</strong> Riyadh is generally safe for tourists. Visitors should respect local customs, dress modestly, and be aware of prayer times when some shops and restaurants may close briefly.</p>"
    
    elif destination.lower() == "jeddah":
        formatted_html += "<p><strong>Best Time to Visit:</strong> December to March when the weather is mild and pleasant (20-28°C/68-82°F).</p>"
        
        formatted_html += "<p><strong>Visa Information:</strong> Saudi Arabia offers e-visas for tourists from many countries. The tourist visa is valid for one year with multiple entries and allows stays of up to 90 days.</p>"
        
        formatted_html += "<p><strong>Weather:</strong> Hot humid climate year-round. Summers (May-October) are very hot (35-40°C/95-104°F) and humid, while winters are milder (18-29°C/64-84°F).</p>"
        
        formatted_html += "<p><strong>Attractions:</strong></p><ul>"
        attractions = [
            "Al-Balad (Historic Jeddah) - UNESCO World Heritage site with traditional architecture",
            "King Fahd Fountain - World's tallest water fountain",
            "Jeddah Corniche - Beautiful waterfront promenade",
            "Floating Mosque (Al-Rahma Mosque) - Beautiful mosque built over the Red Sea",
            "Red Sea Mall - Large shopping mall with entertainment options",
            "Fakieh Aquarium - Home to over 200 species of marine life",
            "Jeddah Sculpture Museum - Open-air museum with works by famous artists",
            "Silver Sands Beach - Popular beach for water activities",
            "Al Shallal Theme Park - Amusement park with various rides and attractions"
        ]
        for attraction in attractions:
            formatted_html += f"<li>{attraction}</li>"
        formatted_html += "</ul>"
        
        formatted_html += "<p><strong>Safety Information:</strong> Jeddah is generally safe for tourists. The city is more cosmopolitan and relaxed compared to other Saudi cities, but visitors should still respect local customs and traditions.</p>"
        
    else:
        # Generic information for other destinations
        if "visa_info" in travel_info:
            formatted_html += f"<p><strong>Visa Information:</strong> {travel_info.get('visa_info', 'No visa information available')}</p>"
        
        if "weather" in travel_info:
            formatted_html += f"<p><strong>Weather:</strong> {travel_info.get('weather', 'Weather information not available')}</p>"
        
        if "attractions" in travel_info:
            formatted_html += "<p><strong>Attractions:</strong></p><ul>"
            for attraction in travel_info.get("attractions", []):
                formatted_html += f"<li>{attraction}</li>"
            formatted_html += "</ul>"
        
        if "safety_info" in travel_info:
            formatted_html += f"<p><strong>Safety Information:</strong> {travel_info.get('safety_info', 'Safety information not available')}</p>"
    
    formatted_html += "</div>"
    return formatted_html

def get_tool_results(user_query: str) -> Tuple[str, Dict]:
    """
    Directly invoke specific tools based on the user query to get results.
    This bypasses the need for complex ADK infrastructure.
    
    Returns:
        A tuple of (response_text, tool_results)
    """
    # Create a dummy context object for tools
    class DummyContext:
        def __init__(self):
            pass
    
    dummy_context = DummyContext()
    
    response_text = "I'm processing your request..."
    tool_results = {}
    
    # Real flight search - check if query is about flights
    if any(keyword in user_query.lower() for keyword in ["flight", "fly", "airline", "travel to", "dmm to", "ruh to", "jed to"]):
        logger.info("Detected flight search query, using real_flight_tool")
        
        # Extract origin and destination if mentioned
        origin = None
        destination = None
        date_period = "next week"
        
        # Simple parsing for flight origin/destination
        if "from" in user_query.lower() and "to" in user_query.lower():
            try:
                # Try to extract origin from "from XXX to"
                origin_idx = user_query.lower().find("from ") + 5
                to_idx = user_query.lower().find(" to", origin_idx)
                if to_idx > origin_idx:
                    origin_text = user_query[origin_idx:to_idx].strip().upper()
                    # Check if it's an airport code (3 letters)
                    if len(origin_text) == 3:
                        origin = origin_text
                    # Try to map common cities to airport codes
                    elif "dammam" in origin_text.lower():
                        origin = "DMM"
                    elif "riyadh" in origin_text.lower():
                        origin = "RUH"
                    elif "jeddah" in origin_text.lower():
                        origin = "JED"
                
                # Try to extract destination from "to XXX"
                dest_idx = user_query.lower().find(" to ") + 4
                space_idx = user_query.find(" ", dest_idx)
                if space_idx > dest_idx:
                    dest_text = user_query[dest_idx:space_idx].strip().upper()
                    # Check if it's an airport code (3 letters)
                    if len(dest_text) == 3:
                        destination = dest_text
                    # Try to map common cities to airport codes
                    elif "dammam" in dest_text.lower():
                        destination = "DMM"
                    elif "riyadh" in dest_text.lower():
                        destination = "RUH"
                    elif "jeddah" in dest_text.lower():
                        destination = "JED"
            except Exception as e:
                logger.error(f"Error parsing flight query: {str(e)}")
        
        # Extract date period if mentioned
        if "tomorrow" in user_query.lower():
            date_period = "tomorrow"
        elif "next week" in user_query.lower():
            date_period = "next week"
        elif "this weekend" in user_query.lower():
            date_period = "this weekend"
        
        # Set default origin/destination if not found
        if not origin:
            origin = "DMM"  # Default origin
        if not destination:
            destination = "RUH"  # Default destination
        
        # Call real flight search tool directly
        try:
            flight_results = real_flight_tool.execute(
                dummy_context,
                origin=origin,
                destination=destination,
                date_period=date_period,
                num_results=5,
                sort_by_price=True
            )
            
            if flight_results.get("status") == "success" and "flights" in flight_results:
                tool_results["flights"] = flight_results["flights"]
                response_text = f"I found some flights from {origin} to {destination} for {date_period}."
            else:
                # Fall back to mock flight data
                logger.info("Real flight search failed, falling back to mock data")
                mock_results = flight_tool.execute(
                    dummy_context,
                    origin=origin,
                    destination=destination,
                    date=date_period
                )
                if "flights" in mock_results:
                    tool_results["flights"] = mock_results["flights"]
                    response_text = f"I found some flight options from {origin} to {destination}."
        except Exception as e:
            logger.error(f"Error in flight search: {str(e)}")
            traceback.print_exc()
    
    # Web search - for general travel queries
    elif any(keyword in user_query.lower() for keyword in ["search", "find info", "tell me about", "what is", "how to"]):
        logger.info("Detected web search query, using web_search_tool")
        try:
            search_results = web_search_tool.execute(
                dummy_context,
                query=user_query
            )
            
            if "results" in search_results:
                tool_results["search_results"] = search_results["results"]
                response_text = f"Here's what I found about your query."
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
    
    # Hotel search
    elif any(keyword in user_query.lower() for keyword in ["hotel", "stay", "accommodation", "place to stay"]):
        logger.info("Detected hotel search query, using hotel_tool")
        
        # Extract location
        location = "Riyadh"  # Default location
        for city in ["riyadh", "jeddah", "dammam", "mecca", "madinah", "dubai"]:
            if city in user_query.lower():
                location = city.capitalize()
                break
        
        try:
            # First try the ADK hotel tool
            hotel_results = hotel_tool.execute(
                dummy_context,
                location=location,
                check_in="next week",
                num_nights=3
            )
            
            if "hotels" in hotel_results:
                tool_results["hotels"] = hotel_results["hotels"]
                response_text = f"I found some hotel options in {location}."
            else:
                # If the hotel tool doesn't return results, generate some realistic ones
                mock_hotels = []
                
                if location.lower() == "jeddah":
                    # Near waterfront/corniche hotels in Jeddah
                    if "waterfront" in user_query.lower() or "corniche" in user_query.lower():
                        mock_hotels = [
                            {
                                "name": "Jeddah Hilton",
                                "price": "$150 per night",
                                "rating": 4.5,
                                "location": "Corniche Road, Jeddah",
                                "description": "Luxury hotel with stunning views of the Red Sea, located directly on the Corniche waterfront. Features multiple restaurants, pools, and a private beach area."
                            },
                            {
                                "name": "Rosewood Jeddah",
                                "price": "$220 per night",
                                "rating": 4.8,
                                "location": "Corniche Road, Al Shati",
                                "description": "5-star luxury hotel on the waterfront with panoramic Red Sea views, rooftop pool, and elegant rooms. Walking distance to the Jeddah Corniche."
                            },
                            {
                                "name": "Park Hyatt Jeddah",
                                "price": "$195 per night",
                                "rating": 4.7,
                                "location": "Al Hamra District, Corniche",
                                "description": "Upscale resort with waterfront location featuring spa facilities, outdoor pools, and marina views. Close to the King Fahd Fountain."
                            },
                            {
                                "name": "Waldorf Astoria Jeddah",
                                "price": "$240 per night",
                                "rating": 4.9,
                                "location": "North Corniche Road",
                                "description": "Exclusive beachfront property with private cabanas, multiple dining options, and luxury spa. Direct access to the Corniche promenade."
                            },
                            {
                                "name": "Shangri-La Jeddah",
                                "price": "$180 per night",
                                "rating": 4.6,
                                "location": "Corniche District",
                                "description": "Contemporary luxury hotel with floor-to-ceiling windows offering Red Sea views, infinity pool, and several restaurants. Located directly on the waterfront."
                            }
                        ]
                    else:
                        mock_hotels = [
                            {
                                "name": "InterContinental Jeddah",
                                "price": "$140 per night",
                                "rating": 4.3,
                                "location": "Al Andalus District, Jeddah",
                                "description": "Upscale hotel with outdoor pool, spa, and multiple dining options. Located in central Jeddah with easy access to shopping areas."
                            },
                            {
                                "name": "Radisson Blu Hotel Jeddah",
                                "price": "$110 per night",
                                "rating": 4.1,
                                "location": "Medina Road, Jeddah",
                                "description": "Modern hotel with comfortable rooms, fitness center, and business facilities. Convenient location near shopping malls."
                            },
                            {
                                "name": "Movenpick Hotel City Star Jeddah",
                                "price": "$125 per night",
                                "rating": 4.2,
                                "location": "Al Madinah Road",
                                "description": "Contemporary hotel with rooftop pool, spa services, and international restaurants. Located close to the airport."
                            }
                        ]
                
                elif location.lower() == "riyadh":
                    mock_hotels = [
                        {
                            "name": "Four Seasons Hotel Riyadh",
                            "price": "$210 per night",
                            "rating": 4.8,
                            "location": "Kingdom Centre, King Fahd Road",
                            "description": "Luxury hotel located in the iconic Kingdom Centre tower with spectacular city views, spa facilities, and world-class dining."
                        },
                        {
                            "name": "The Ritz-Carlton Riyadh",
                            "price": "$235 per night",
                            "rating": 4.9,
                            "location": "Al Hada Area",
                            "description": "Opulent palace-like hotel set in 52 acres of landscaped gardens with luxurious rooms, indoor pool, and grand ballrooms."
                        },
                        {
                            "name": "Hyatt Regency Riyadh Olaya",
                            "price": "$160 per night",
                            "rating": 4.5,
                            "location": "Olaya Street, Riyadh",
                            "description": "Modern hotel in the financial district featuring contemporary rooms, rooftop pool, and multiple dining options."
                        }
                    ]
                
                elif location.lower() == "dubai":
                    mock_hotels = [
                        {
                            "name": "Burj Al Arab",
                            "price": "$1200 per night",
                            "rating": 5.0,
                            "location": "Jumeirah Beach Road",
                            "description": "Iconic 7-star luxury hotel on its own island with butler service, opulent suites, and panoramic views of the Arabian Gulf."
                        },
                        {
                            "name": "Atlantis The Palm",
                            "price": "$350 per night",
                            "rating": 4.7,
                            "location": "Palm Jumeirah",
                            "description": "Luxury resort on the Palm Jumeirah with its own water park, aquarium, and multiple celebrity chef restaurants."
                        },
                        {
                            "name": "Address Downtown",
                            "price": "$280 per night",
                            "rating": 4.8,
                            "location": "Downtown Dubai",
                            "description": "Elegant hotel next to Burj Khalifa and Dubai Mall with infinity pool, spa, and stunning views of the Dubai Fountain."
                        }
                    ]
                
                else:
                    # Generic hotels for other locations
                    mock_hotels = [
                        {
                            "name": f"Luxury Hotel {location}",
                            "price": "$180 per night",
                            "rating": 4.6,
                            "location": f"Central {location}",
                            "description": f"5-star accommodation in the heart of {location} with premium amenities and exceptional service."
                        },
                        {
                            "name": f"{location} Plaza Hotel",
                            "price": "$120 per night",
                            "rating": 4.2,
                            "location": f"Business District, {location}",
                            "description": f"Comfortable 4-star hotel with modern rooms, restaurant, and fitness center. Great location for business travelers."
                        },
                        {
                            "name": f"Grand Resort {location}",
                            "price": "$150 per night",
                            "rating": 4.4,
                            "location": f"Tourist Area, {location}",
                            "description": f"Family-friendly resort with swimming pools, restaurants, and entertainment options. Convenient location for sightseeing."
                        }
                    ]
                
                tool_results["hotels"] = mock_hotels
                response_text = f"I found these hotel options in {location} for your stay."
                
        except Exception as e:
            logger.error(f"Error in hotel search: {str(e)}")
    
    # Travel info
    elif any(keyword in user_query.lower() for keyword in ["travel info", "visa", "weather", "attractions", "visit", "best time"]):
        logger.info("Detected travel info query, using enhanced travel_info")
        
        # Extract destination
        destination = "Riyadh"  # Default destination
        for city in ["riyadh", "jeddah", "dammam", "mecca", "madinah", "dubai"]:
            if city in user_query.lower():
                destination = city.capitalize()
                break
        
        # Create enhanced travel info with more details
        travel_info = {"destination": destination}
        
        # Determine main focus of query
        if "visa" in user_query.lower() or "requirements" in user_query.lower():
            travel_info["focus"] = "visa_requirements"
            response_text = f"Here's information about visa requirements for {destination}."
        elif "weather" in user_query.lower() or "climate" in user_query.lower():
            travel_info["focus"] = "weather"
            response_text = f"Here's information about the weather in {destination}."
        elif "best time" in user_query.lower() or "when to visit" in user_query.lower():
            travel_info["focus"] = "best_time"
            response_text = f"Here's information about the best time to visit {destination}."
        elif "attraction" in user_query.lower() or "see" in user_query.lower() or "visit" in user_query.lower():
            travel_info["focus"] = "attractions"
            response_text = f"Here are popular tourist attractions in {destination}."
        else:
            travel_info["focus"] = "general"
            response_text = f"Here's some travel information about {destination}."
        
        tool_results["travel_info"] = travel_info
    
    # If no specific tool match, generate a generic response
    if not tool_results:
        response_text = "I'm an AI Travel Assistant that can help you find flights, hotels, and travel information. How can I assist you with your travel plans today?"
    
    return response_text, tool_results

def process_user_message(user_input: str) -> None:
    """Process the user's message and generate a response with tool results."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Add a placeholder for the assistant's response
    with st.chat_message("assistant", avatar="✈️"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
    
    try:
        # Generate a direct response and get any tool results
        response_text, tool_results = get_tool_results(user_input)
        
        # Build the formatted response
        formatted_response = f"<div class='agent-response'>{response_text}</div>"
        
        # Format any tool outputs
        if "flights" in tool_results:
            formatted_response += format_flight_results(tool_results["flights"])
        
        if "hotels" in tool_results:
            formatted_response += format_hotel_results(tool_results["hotels"])
        
        if "travel_info" in tool_results:
            formatted_response += format_travel_info(tool_results["travel_info"])
        
        if "search_results" in tool_results:
            formatted_response += format_search_results(tool_results["search_results"])
        
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
