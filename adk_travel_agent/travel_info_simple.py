"""
Travel Information Tool for the Travel Assistant (Simplified version).
"""

import json
import os
import random
from typing import Dict, Any, List

from google.adk.tools import BaseTool
from google.adk.tools import ToolContext

# Simple logging setup
import logging
logger = logging.getLogger(__name__)

# Define cache
class SimpleCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value

travel_info_cache = SimpleCache()

# Custom exceptions
class ServiceUnavailableError(Exception):
    """Exception raised when a service is unavailable."""
    pass

class ValidationError(Exception):
    """Exception raised for input validation errors."""
    pass

# Utility functions
def retry(max_tries=3, delay_seconds=1):
    """Simple retry decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except ServiceUnavailableError as e:
                    tries += 1
                    if tries == max_tries:
                        logger.error(f"Failed after {max_tries} tries: {str(e)}")
                        raise
                    
                    logger.warning(f"Retry {tries}/{max_tries} after error: {str(e)}")
                    import time
                    time.sleep(delay_seconds)
            
        return wrapper
    return decorator

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
                        "description": "Destination to get information about (e.g., 'Paris')"
                    },
                    "info_type": {
                        "type": "string",
                        "description": "Type of information to retrieve (general, visa, weather, safety, attractions, transportation, culture)"
                    }
                },
                "required": ["destination"]
            }
        }
    
    @retry(max_tries=3)
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a travel info query for a destination."""
        try:
            # Get parameters
            destination = kwargs.get("destination", "")
            info_type = kwargs.get("info_type", "general")
            
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
            
            # Generate mock data
            try:
                travel_info = self._generate_mock_travel_info(destination, info_type)
                
                # Cache the results
                travel_info_cache.set(cache_key, travel_info)
                
                logger.info(f"Generated travel information for {destination}")
                return {"status": "success", "information": travel_info}
            except ServiceUnavailableError as e:
                logger.error(f"Service unavailable: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in TravelInfoTool: {str(e)}")
            return {
                "status": "error",
                "error_type": str(type(e).__name__),
                "message": f"Failed to get travel information: {str(e)}",
                "suggestion": "Please try again later or try a different destination."
            }
    
    def _generate_mock_travel_info(self, destination, info_type="general") -> Dict[str, Any]:
        """Generate mock travel information for demonstration purposes."""
        # Simulate potential service outage (1% chance)
        if random.random() < 0.01:
            raise ServiceUnavailableError("Travel information service temporarily unavailable")

        result = {
            "destination": destination,
            "info_type": info_type,
            "last_updated": "2025-04-20",
            "disclaimer": "This information is for demonstration purposes only."
        }

        # General information
        if info_type == "general":
            overview_options = [
                "is a popular travel destination known for its beautiful scenery.",
                "is a popular travel destination known for its rich culture.",
                "is a popular travel destination known for its historical sites.",
                "is a popular travel destination known for its vibrant nightlife.",
                "is a popular travel destination known for its delicious cuisine."
            ]
            best_time_options = [
                "The best time to visit is during spring (March-May).",
                "The best time to visit is during summer (June-August).",
                "The best time to visit is during fall (September-November).",
                "The best time to visit is during winter (December-February)."
            ]
            language_options = [
                "The primary language spoken is English, and it is widely understood.",
                "The primary language spoken is Spanish, but many locals speak English.",
                "The primary language spoken is French, but English is commonly spoken in tourist areas.",
                "The primary language spoken is German, and English is also widely spoken."
            ]
            
            result["overview"] = destination + " " + random.choice(overview_options)
            result["best_time_to_visit"] = random.choice(best_time_options)
            result["language"] = random.choice(language_options)
            
        # Visa information
        elif info_type == "visa":
            visa_options = [
                "A visa is required for most tourists.",
                "A visa is not required for stays under 90 days.",
                "An electronic visa (e-visa) can be obtained online."
            ]
            processing_options = [
                "Visa processing typically takes 3-5 business days.",
                "Visa processing typically takes 1-2 weeks.",
                "Visa processing typically takes 24-48 hours with express service."
            ]
            document_options = [
                "Required documents include a valid passport, visa application form, and passport photos.",
                "Required documents include a valid passport with at least 6 months validity, proof of accommodation, and return flight ticket.",
                "Required documents include a valid passport, travel insurance, and bank statements."
            ]
            
            result["requirements"] = random.choice(visa_options)
            result["processing_time"] = random.choice(processing_options)
            result["documentation"] = random.choice(document_options)
            
        # Weather information
        elif info_type == "weather":
            climate_options = [
                "has a tropical climate.",
                "has a mediterranean climate.",
                "has a continental climate.",
                "has a temperate climate."
            ]
            season_options = [
                "The seasons are well-defined with four distinct seasons.",
                "The seasons are primarily wet and dry seasons.",
                "The seasons are mild with little temperature variation throughout the year."
            ]
            min_temp = random.randint(0, 20)
            max_temp = random.randint(20, 40)
            
            result["climate"] = destination + " " + random.choice(climate_options)
            result["seasons"] = random.choice(season_options)
            result["temperature"] = f"Average temperatures range from {min_temp}°C in winter to {max_temp}°C in summer."
            
        # Safety information
        elif info_type == "safety":
            safety_options = [
                "is generally considered very safe for tourists.",
                "is generally considered safe for tourists.",
                "is generally considered moderately safe for tourists."
            ]
            area_options = [
                "Travelers are advised to exercise normal precautions.",
                "Travelers are advised to avoid certain neighborhoods after dark.",
                "Travelers are advised to be vigilant in tourist areas where pickpocketing can occur."
            ]
            emergency_options = [
                "In case of emergency, dial 911.",
                "In case of emergency, dial 112.",
                "In case of emergency, dial 999."
            ]
            
            result["overall"] = destination + " " + random.choice(safety_options)
            result["areas_to_avoid"] = random.choice(area_options)
            result["emergency_contacts"] = random.choice(emergency_options)
            
        # Attractions information
        elif info_type == "attractions":
            attraction_items = [
                f"The {destination} Museum",
                f"The {destination} Castle",
                f"The {destination} Park",
                f"The {destination} Cathedral",
                f"The {destination} Beach",
                f"The {destination} Old Town"
            ]
            random.shuffle(attraction_items)
            
            hidden_items = [
                f"The Local {destination} Market",
                f"The {destination} Botanical Garden",
                f"The {destination} Historical Cafe",
                f"The {destination} Viewpoint"
            ]
            random.shuffle(hidden_items)
            
            day_trip_options = [
                f"Popular day trips from {destination} include visits to nearby islands and countryside vineyards.",
                f"Popular day trips from {destination} include visits to mountain villages and archaeological sites.",
                f"Popular day trips from {destination} include visits to national parks and neighboring cities."
            ]
            
            result["top_sights"] = attraction_items[:3]
            result["hidden_gems"] = hidden_items[:2]
            result["day_trips"] = random.choice(day_trip_options)
            
        # Transportation information
        elif info_type == "transportation":
            transport_options = [
                f"In {destination}, the main transportation options include public buses, subway/metro, and taxis.",
                f"In {destination}, the main transportation options include trams, rental cars, and bicycles.",
                f"In {destination}, the main transportation options include ferries, ride-sharing services, and walking."
            ]
            airport_options = [
                f"From the airport to the city center, options include airport express train and taxis (approx. $30).",
                f"From the airport to the city center, options include shuttle bus and public bus.",
                f"From the airport to the city center, options include ride-sharing services and rental car."
            ]
            public_options = [
                "Public transportation is extensive and runs until midnight.",
                "Public transportation is limited but reliable.",
                "Public transportation can be crowded during rush hours."
            ]
            
            result["getting_around"] = random.choice(transport_options)
            result["from_airport"] = random.choice(airport_options)
            result["public_transport"] = random.choice(public_options)
            
        # Culture information
        elif info_type == "culture":
            etiquette_options = [
                f"Important cultural etiquette in {destination} includes removing shoes before entering homes and greeting with a bow.",
                f"Important cultural etiquette in {destination} includes covering shoulders when visiting religious sites and tipping for services.",
                f"Important cultural etiquette in {destination} includes avoiding public displays of affection and eating with your right hand only."
            ]
            custom_options = [
                "Unique local customs include traditional greetings and tea ceremonies.",
                "Unique local customs include afternoon siestas and removing shoes indoors.",
                "Unique local customs include specific dining etiquette and festival celebrations."
            ]
            cuisine_options = [
                "The local cuisine features spicy dishes, fresh seafood, and vegetarian options.",
                "The local cuisine features street food, traditional breads, and rice-based meals.",
                "The local cuisine features exotic fruits, grilled meats, and unique desserts."
            ]
            
            result["etiquette"] = random.choice(etiquette_options)
            result["customs"] = random.choice(custom_options)
            result["cuisine"] = random.choice(cuisine_options)
            
        # Default to general information
        else:
            return self._generate_mock_travel_info(destination, "general")
            
        return result
