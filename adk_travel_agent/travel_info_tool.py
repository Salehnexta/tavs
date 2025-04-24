"""
Travel Information Tool for the Travel Assistant.
"""

import json
import os
import random
from typing import Dict, Any, List

from google.adk.tools import BaseTool
from google.adk.tools import ToolContext

from .utils import (
    logger, retry, validate_date_format, validate_required_fields,
    sanitize_input, travel_info_cache, ApiKeyError, ServiceUnavailableError, ValidationError
)

# Logging is already set up in utils

class TravelInfoTool(BaseTool):
    """Tool for retrieving travel information about destinations."""
    
    def __init__(self):
        super().__init__(
            name="travel_info",
            description="Get information about travel destinations like visa requirements, weather, attractions, etc."
        )
    
    @property
    def function_schema(self):
        """Define the function schema for the travel info tool."""
        return {
            "name": "travel_info",
            "description": "Get information about travel destinations like visa requirements, weather, attractions, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination city or country"
                    },
                    "info_type": {
                        "type": "string",
                        "description": "Type of information needed (visa, weather, attractions, transportation, safety, food, currency)"
                    }
                },
                "required": ["destination"]
            }
        }
    
    @retry(max_tries=3, delay_seconds=2, exceptions=(ServiceUnavailableError,))
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a travel info query for a destination."""
        try:
            # Get parameters and sanitize inputs
            destination = sanitize_input(kwargs.get("destination", ""))
            info_type = sanitize_input(kwargs.get("info_type", "general"))
            
            # Validate required fields
            if not destination:
                logger.warning("Missing required destination parameter")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Missing destination parameter",
                    "suggestion": "Please specify a destination to get travel information about."
                }
            
            # Validate info_type if provided
            valid_info_types = ["general", "visa", "weather", "safety", "attractions", "transportation", "culture"]
            if info_type and info_type not in valid_info_types:
                logger.warning(f"Invalid info_type: {info_type}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": f"Invalid info_type: {info_type}",
                    "suggestion": f"Please use one of the following info types: {', '.join(valid_info_types)}"
                }
            
            # Log query parameters
            logger.info(f"Getting {info_type} information about {destination}")
            
            # Try to get from cache first
            cache_key = f"travel_info:{destination}:{info_type}"
            cached_result = travel_info_cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached travel information for {destination}")
                return {"status": "success", "information": cached_result, "cached": True}
            
            # In a real implementation, this would call a travel info API
            # For demo purposes, we'll just generate mock data
            try:
                travel_info = self._generate_mock_travel_info(destination, info_type)
                
                # Cache the results
                travel_info_cache.set(cache_key, travel_info)
                
                logger.info(f"Generated travel information for {destination}")
                return {"status": "success", "information": travel_info}
            except ServiceUnavailableError as e:
                # This specific error will trigger the retry mechanism
                logger.error(f"Service unavailable: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in TravelInfoTool: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "message": f"Failed to get travel information: {str(e)}",
                "suggestion": "Please try again later or try a different destination."
            }
    
    def _generate_mock_travel_info(self, destination, info_type="general") -> Dict[str, Any]:
        """Generate mock travel information for demonstration purposes."""
        # Simulate potential service outage (1% chance)
        if random.random() < 0.01:
            raise ServiceUnavailableError("Travel information service temporarily unavailable")

        # More extensive dictionary of sample travel information by type
        travel_info_templates = {
            "general": {
                "overview": f"{destination} is a popular travel destination known for its {random.choice(['beautiful scenery', 'rich culture', 'historical sites', 'vibrant nightlife', 'delicious cuisine', 'friendly locals', 'architectural wonders', 'stunning beaches'])}. It attracts millions of visitors each year.",
                "best_time_to_visit": f"The best time to visit {destination} is during {random.choice(['spring (March-May)', 'summer (June-August)', 'fall (September-November)', 'winter (December-February)'])} when the weather is {random.choice(['warm and pleasant', 'cool and comfortable', 'mild with occasional rain', 'sunny and dry'])}.",
                "language": f"The primary language spoken in {destination} is {random.choice(['English', 'Spanish', 'French', 'German', 'Italian', 'Mandarin', 'Japanese', 'Arabic'])}, but {random.choice(['English is widely understood', 'many locals speak English', 'English is not commonly spoken'])}."            
            },
            "visa": {
                "requirements": f"For tourists from most countries, {random.choice(['a visa is required', 'a visa is not required for stays under 90 days', 'an electronic visa (e-visa) can be obtained online', 'a visa-on-arrival is available'])} to visit {destination}.",
                "processing_time": f"Visa processing typically takes {random.randint(1, 14)} {random.choice(['business days', 'days', 'weeks'])}.",
                "documentation": f"Required documents include {', '.join(random.sample(['a valid passport with at least 6 months validity', 'visa application form', 'passport photos', 'proof of accommodation', 'return flight ticket', 'travel insurance', 'bank statements', 'proof of sufficient funds', 'itinerary'], random.randint(3, 6)))}."            
            },
            "weather": {
                "climate": f"{destination} has a {random.choice(['tropical', 'mediterranean', 'continental', 'temperate', 'arid', 'polar', 'subtropical', 'oceanic', 'monsoon'])} climate.",
                "seasons": f"The seasons in {destination} are {random.choice(['well-defined with four distinct seasons', 'primarily wet and dry seasons', 'mild with little temperature variation throughout the year', 'characterized by a rainy and dry period', 'influenced by monsoon patterns'])}." + f" {random.choice(['The rainy season typically runs from May to October.', 'Hurricanes/typhoons are possible between June and November.', 'Snowfall is common from December to February.', 'The driest months are typically January to March.', ''])}",
                "temperature": f"Average temperatures range from {random.randint(0, 20)}°C ({random.randint(32, 68)}°F) in winter to {random.randint(20, 40)}°C ({random.randint(68, 104)}°F) in summer.",
                "what_to_pack": f"Travelers are advised to pack {', '.join(random.sample(['light clothing', 'layers', 'a rain jacket', 'comfortable walking shoes', 'sunscreen', 'a hat', 'winter clothing', 'an umbrella', 'insect repellent'], random.randint(3, 5)))}."            
            },
            "safety": {
                "overall": f"{destination} is generally considered {random.choice(['very safe', 'safe', 'moderately safe', 'safe for tourists with normal precautions'])} for tourists.",
                "areas_to_avoid": f"Travelers are advised to {random.choice(['exercise normal precautions', 'avoid certain neighborhoods after dark', 'be vigilant in tourist areas where pickpocketing can occur', 'stick to well-lit and populated areas at night', 'research local areas before visiting'])}." + f" {random.choice(['Petty theft can be common in crowded tourist areas.', 'Scams targeting tourists have been reported.', 'Road safety can be a concern in some areas.', 'Natural disasters such as earthquakes/floods may occur.', ''])}",
                "emergency_contacts": f"In case of emergency, dial {random.choice(['911', '112', '999', '000'])}. The tourist police can be reached at {random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}.",
                "health": f"Travelers {random.choice(['should drink bottled water', 'can generally drink tap water', 'should avoid raw street food', 'should have travel insurance with medical coverage', 'may need vaccinations before travel'])}."            
            },
            "attractions": {
                "top_sights": f"Top attractions in {destination} include {', '.join([f'the {place}' for place in random.sample(['Grand Museum', 'National Park', 'Old Town', 'Cathedral', 'Castle', 'Beach', 'Mountain', 'River', 'Shopping District', 'Theater', 'Royal Palace', 'Ancient Temple', 'Modern Art Gallery', 'Safari Park', 'Cultural Center'], random.randint(3, 6))])}.",
                "hidden_gems": f"Lesser-known attractions worth visiting are {', '.join([f'the {place}' for place in random.sample(['Local Market', 'Botanical Garden', 'Historical Cafe', 'Viewpoint', 'Art Gallery', 'Ancient Ruins', 'Nature Trail', 'Local Brewery', 'Underground Caves', 'Artisan Workshops', 'Abandoned Village'], random.randint(2, 4))])}.",
                "day_trips": f"Popular day trips from {destination} include visits to {', '.join(random.sample(['nearby islands', 'countryside vineyards', 'mountain villages', 'archaeological sites', 'national parks', 'neighboring cities', 'coastal towns', 'historic battlefields', 'wildlife sanctuaries'], random.randint(2, 4)))}."            
            },
            "transportation": {
                "getting_around": f"In {destination}, the main transportation options include {', '.join(random.sample(['public buses', 'subway/metro', 'taxis', 'ride-sharing services', 'tuk-tuks/rickshaws', 'rental cars', 'ferries', 'bicycles', 'trams', 'high-speed trains'], random.randint(3, 5)))}." + f" {random.choice(['Public transportation is efficient and affordable.', 'Taxis are plentiful but negotiate fares in advance.', 'Renting a car is recommended for exploring the countryside.', 'Walking is the best way to explore the city center.', 'Bicycle rentals are widely available and popular.'])}",
                "from_airport": f"From the airport to the city center, options include {', '.join(random.sample(['airport express train', 'shuttle bus', 'taxi (approx. $' + str(random.randint(15, 50)) + ')', 'ride-sharing services', 'public bus', 'rental car'], random.randint(2, 4)))}." + f" The journey typically takes {random.randint(15, 90)} minutes depending on traffic.",
                "public_transport": f"Public transportation {random.choice(['is extensive and runs until midnight', 'is limited but reliable', 'can be crowded during rush hours', 'offers tourist passes for unlimited travel', 'accepts contactless payment methods'])}."
            },
            "culture": {
                "etiquette": f"Important cultural etiquette in {destination} includes {', '.join(random.sample(['removing shoes before entering homes or temples', 'greeting with a bow', 'covering shoulders and knees when visiting religious sites', 'tipping for services', 'not pointing with your finger', 'avoiding public displays of affection', 'not touching people\'s heads'.replace('\'', "'"), 'eating with your right hand only'], random.randint(2, 4)))}." + f" {random.choice(['Locals appreciate visitors who learn a few basic phrases.', 'Punctuality is highly valued.', 'Haggling is expected in markets.', 'Gift-giving is an important cultural practice.', ''])}",
                "customs": f"Unique local customs include {', '.join(random.sample(['traditional greetings', 'tea ceremonies', 'afternoon siestas', 'removing shoes indoors', 'specific dining etiquette', 'festival celebrations', 'religious observances'], random.randint(2, 3)))}." + f" Visitors should be respectful of local traditions and customs.",
                "cuisine": f"The local cuisine features {', '.join(random.sample(['spicy dishes', 'fresh seafood', 'vegetarian options', 'street food', 'traditional breads', 'rice-based meals', 'exotic fruits', 'grilled meats', 'unique desserts'], random.randint(3, 5)))}." + f" {random.choice(['Do not miss trying the local specialty dish.', 'Food tours are a great way to experience local cuisine.', 'Restaurants typically open late for dinner.', 'Street food is delicious but choose vendors carefully.', 'Markets offer the freshest local ingredients.'])}"
            }
        }
        
        # If the requested info type is not in our templates, return general info
        if info_type not in travel_info_templates:
            info_type = "general"
        
        result = travel_info_templates[info_type].copy()
        result["destination"] = destination
        result["info_type"] = info_type
        result["last_updated"] = "2025-04-20"  # Mock date for demonstration
        
        # Add a disclaimer
        result["disclaimer"] = "This information is for demonstration purposes only. Always verify travel information with official sources before making travel plans."
        
        return result
