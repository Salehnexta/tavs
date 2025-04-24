"""
Real Flight Search Tool that uses Serper API to get actual flight data.
This tool provides real flight information from Google search results.
"""

import os
import re
import json
import logging
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from google.adk.tools import BaseTool, ToolContext

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")

# Configure requests with retry logic
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

# Cache for search results
CACHE_TTL = 1800  # 30 minutes in seconds
flight_cache = {}

class RealFlightSearchTool(BaseTool):
    """Tool for searching real flight information using the Serper API to query Google."""
    
    def __init__(self):
        super().__init__(
            name="real_flight_search",
            description="Search for real flight information between airports on specific dates"
        )
    
    @property
    def function_schema(self):
        """Define the function schema for the real flight search tool."""
        return {
            "name": "real_flight_search",
            "description": "Search for real flight information between airports on specific dates",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code (e.g., DMM, JFK)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code (e.g., RUH, LHR)"
                    },
                    "date_period": {
                        "type": "string",
                        "description": "When to travel (e.g., 'next week', 'tomorrow', 'May 15')"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    },
                    "sort_by_price": {
                        "type": "boolean",
                        "description": "If true, prioritize showing pricing information"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a real flight search between airports using Serper API."""
        try:
            # Get and validate parameters
            origin = kwargs.get("origin", "").strip().upper()
            destination = kwargs.get("destination", "").strip().upper()
            date_period = kwargs.get("date_period", "next week")
            num_results = min(kwargs.get("num_results", 5), 10)
            sort_by_price = kwargs.get("sort_by_price", True)
            
            # Validate required fields
            if not origin or not destination:
                return {
                    "status": "error",
                    "message": "Both origin and destination airport codes are required."
                }
            
            # Check for API key
            if not SERPER_API_KEY:
                return {
                    "status": "error",
                    "message": "Serper API key is not configured. Please set SERPER_API_KEY in your environment."
                }
            
            logger.info(f"Searching for real flights from {origin} to {destination} for {date_period}")
            
            # Get flight data from Serper API
            try:
                flight_data = self._search_flights(origin, destination, date_period, num_results)
                
                if not flight_data or len(flight_data) == 0:
                    return {
                        "status": "info",
                        "message": f"No flights found from {origin} to {destination} for {date_period}.",
                        "suggestion": "Try different dates or airports."
                    }
                
                # Process and structure the flight data
                structured_flights = self._structure_flight_data(flight_data, origin, destination, sort_by_price)
                
                # Return the structured data
                return {
                    "status": "success",
                    "flights": structured_flights,
                    "source": "Real flight data from Google via Serper API"
                }
                
            except Exception as e:
                logger.error(f"Error in flight search: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to retrieve flight information: {str(e)}"
                }
            
        except Exception as e:
            logger.error(f"Error in RealFlightSearchTool: {str(e)}")
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }
    
    def _search_flights(self, origin: str, destination: str, date_period: str, num_results: int) -> List[Dict[str, Any]]:
        """Search for flights using the Serper API."""
        # Create a unique cache key
        cache_key = f"{origin}-{destination}-{date_period}-{num_results}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check if we have cached results
        current_time = time.time()
        if cache_key in flight_cache and current_time - flight_cache[cache_key]["timestamp"] < CACHE_TTL:
            logger.info(f"Using cached flight results for {origin} to {destination}")
            return flight_cache[cache_key]["data"]
        
        # Construct the search query
        query = f"flights from {origin} to {destination} {date_period}"
        
        # Set up headers for API request
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Build the payload
        payload = {
            "q": query,
            "num": max(num_results * 2, 10)  # Request more results than needed to improve extraction chances
        }
        
        # Make the request to Serper API
        response = http.post(SERPER_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant flight data from organic search results
        organic_results = data.get("organic", [])
        if not organic_results:
            return []
        
        # Cache the results
        flight_cache[cache_key] = {
            "timestamp": current_time,
            "data": organic_results
        }
        
        return organic_results
    
    def _structure_flight_data(self, organic_results: List[Dict[str, Any]], 
                              origin: str, destination: str, sort_by_price: bool) -> List[Dict[str, Any]]:
        """
        Extract and structure flight information from organic search results.
        """
        flights = []
        airlines_found = set()
        prices = []
        
        # Process each search result
        for result in organic_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            price = result.get("price")
            
            # Skip irrelevant results
            if not any(keyword in title.lower() for keyword in ["flight", "cheap", "air"]):
                continue
                
            flight_info = {
                "origin": origin,
                "destination": destination,
                "source_link": link,
                "source_title": title
            }
            
            # Extract airlines
            airlines = self._extract_airlines(title, snippet)
            if airlines:
                flight_info["airlines"] = airlines
                airlines_found.update(airlines)
            
            # Extract price information
            if price:
                flight_info["price"] = f"${price}"
                prices.append(price)
            else:
                extracted_price = self._extract_price(title, snippet)
                if extracted_price:
                    flight_info["price"] = extracted_price
                    try:
                        # Extract numeric value for sorting
                        numeric_price = float(re.sub(r'[^\d.]', '', extracted_price))
                        prices.append(numeric_price)
                    except:
                        pass
            
            # Extract flight duration
            duration = self._extract_duration(snippet)
            if duration:
                flight_info["duration"] = duration
            
            # Extract flight schedule information
            schedule = self._extract_schedule(snippet)
            if schedule:
                flight_info["schedule"] = schedule
            
            # Extract additional information
            additional_info = self._extract_additional_info(snippet)
            if additional_info:
                flight_info["additional_info"] = additional_info
            
            flights.append(flight_info)
        
        # Add summary statistics
        if flights:
            summary = {
                "summary": {
                    "total_results": len(flights),
                    "airlines_available": len(airlines_found),
                    "airlines": list(airlines_found)
                }
            }
            
            if prices:
                summary["summary"]["lowest_price"] = f"${min(prices)}"
                summary["summary"]["highest_price"] = f"${max(prices)}"
                summary["summary"]["average_price"] = f"${sum(prices) / len(prices):.2f}"
            
            flights[0].update(summary)
        
        # Sort flights by price if requested and possible
        if sort_by_price:
            flights.sort(key=lambda x: float(re.sub(r'[^\d.]', '', x.get("price", "$999999"))) 
                        if isinstance(x.get("price"), str) and "$" in x.get("price", "") 
                        else 999999)
        
        return flights
    
    def _extract_airlines(self, title: str, snippet: str) -> List[str]:
        """Extract airline information from search results."""
        common_airlines = ["Saudia", "Saudi Airlines", "SV", "Flynas", "flyadeal", "Emirates", 
                          "Etihad", "Qatar Airways", "Turkish Airlines", "EgyptAir", "Gulf Air"]
        
        airlines = []
        combined_text = (title + " " + snippet).lower()
        
        for airline in common_airlines:
            if airline.lower() in combined_text:
                airlines.append(airline)
        
        return list(set(airlines))
    
    def _extract_price(self, title: str, snippet: str) -> Optional[str]:
        """Extract price information from search results."""
        combined_text = title + " " + snippet
        
        # Look for price patterns like $99, USD 99, 99 USD, etc.
        price_patterns = [
            r'\$\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*\$',
            r'USD\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*USD',
            r'from\s*\$\s*(\d+(?:\.\d+)?)',
            r'from\s*(\d+(?:\.\d+)?)\s*\$',
            r'starting at\s*\$\s*(\d+(?:\.\d+)?)',
            r'as low as\s*\$\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*dollars'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        
        return None
    
    def _extract_duration(self, snippet: str) -> Optional[str]:
        """Extract flight duration information."""
        # Look for patterns like "1h 30m", "1 hour 30 minutes", etc.
        duration_patterns = [
            r'(\d+)\s*h(?:rs?)?(?:\s*(\d+)\s*m(?:in)?)?',
            r'(\d+)\s*hours?(?:\s*(\d+)\s*minutes?)?',
            r'(\d+)\s*hour\s*(\d+)\s*minute',
            r'duration:?\s*(\d+):(\d+)',
            r'flight\s*time:?\s*(\d+)(?::|\s*h)(\d+)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                hours = match.group(1)
                minutes = match.group(2) if match.group(2) else "0"
                return f"{hours}h {minutes}m"
        
        return None
    
    def _extract_schedule(self, snippet: str) -> Optional[str]:
        """Extract flight schedule information."""
        schedule_info = []
        
        # Look for departure/arrival times
        time_pattern = r'(\d{1,2}):(\d{2})(?:\s*(AM|PM))?'
        times = re.findall(time_pattern, snippet, re.IGNORECASE)
        
        if times and len(times) >= 2:
            schedule_info.append(f"Dep: {times[0][0]}:{times[0][1]} {times[0][2] if times[0][2] else ''}")
            schedule_info.append(f"Arr: {times[1][0]}:{times[1][1]} {times[1][2] if times[1][2] else ''}")
        
        # Look for weekly flight patterns
        weekly_pattern = r'(\d+)\s*weekly\s*(?:flights|nonstop)'
        weekly_match = re.search(weekly_pattern, snippet, re.IGNORECASE)
        if weekly_match:
            schedule_info.append(f"{weekly_match.group(1)} weekly flights")
        
        # Look for flight days
        days_pattern = r'(MTWTFSS|[MTWTFSS]{1,7})'
        days_match = re.search(days_pattern, snippet)
        if days_match:
            schedule_info.append(f"Days: {days_match.group(1)}")
        
        return ", ".join(schedule_info) if schedule_info else None
    
    def _extract_additional_info(self, snippet: str) -> Optional[str]:
        """Extract additional flight information."""
        additional = []
        
        # Check for nonstop flights
        if re.search(r'non-?stop|direct', snippet, re.IGNORECASE):
            additional.append("Nonstop flight")
        
        # Check for connection information
        connection_match = re.search(r'(\d+)\s*stops?', snippet, re.IGNORECASE)
        if connection_match:
            additional.append(f"{connection_match.group(1)} stop{'s' if connection_match.group(1) != '1' else ''}")
        
        # Check for baggage information
        if re.search(r'baggage|luggage', snippet, re.IGNORECASE):
            bag_match = re.search(r'(\d+)\s*(?:free)?\s*(?:bags?|luggage|baggage)', snippet, re.IGNORECASE)
            if bag_match:
                additional.append(f"{bag_match.group(1)} free bags")
        
        return ", ".join(additional) if additional else None
