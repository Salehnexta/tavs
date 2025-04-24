"""
Flight Search Tool for the Travel Assistant.
"""

import datetime
import logging
import json
import os
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

from google.adk import tools
from google.adk.tools import BaseTool
from google.adk.tools import ToolContext

from .utils import (
    logger, retry, validate_date_format, validate_required_fields,
    sanitize_input, ApiKeyError, ServiceUnavailableError, ValidationError
)

class FlightSearchTool(BaseTool):
    """Tool for searching flights between airports on specific dates."""
    
    def __init__(self):
        super().__init__(
            name="flight_search",
            description="Search for flights between airports on specific dates"
        )
        
    @property
    def function_schema(self):
        """Define the function schema for the flight search tool."""
        return {
            "name": "flight_search",
            "description": "Search for flights between airports on specific dates",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport code (e.g., JFK, LAX)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport code (e.g., LHR, CDG)"
                    },
                    "date": {
                        "type": "string",
                        "description": "Departure date in YYYY-MM-DD format"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date in YYYY-MM-DD format (for round trips)"
                    },
                    "num_passengers": {
                        "type": "integer",
                        "description": "Number of passengers"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort results by: 'price', 'duration', 'departure', or 'airline'"
                    },
                    "price_range": {
                        "type": "string",
                        "description": "Price range in format 'min-max' (e.g., '200-800')"
                    },
                    "cabin_class": {
                        "type": "string",
                        "description": "Preferred cabin class: 'economy', 'premium_economy', 'business', or 'first'"
                    }
                },
                "required": ["origin", "destination", "date"]
            }
        }
    
    @retry(max_tries=3, delay_seconds=2, exceptions=(ServiceUnavailableError,))
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a flight search between airports."""
        try:
            # Get parameters and sanitize inputs
            origin = sanitize_input(kwargs.get("origin", ""))
            destination = sanitize_input(kwargs.get("destination", ""))
            date = sanitize_input(kwargs.get("date", ""))
            return_date = sanitize_input(kwargs.get("return_date", ""))
            num_passengers = kwargs.get("num_passengers", 1)
            max_results = min(kwargs.get("max_results", 20), 30)  # Increased cap for more comprehensive results
            sort_by = sanitize_input(kwargs.get("sort_by", "price")).lower()
            price_range = sanitize_input(kwargs.get("price_range", ""))
            cabin_class = sanitize_input(kwargs.get("cabin_class", "economy")).lower()
            
            # Validate required fields
            missing_fields = validate_required_fields(
                {"origin": origin, "destination": destination, "date": date},
                ["origin", "destination", "date"]
            )
            
            if missing_fields:
                missing_str = ", ".join(missing_fields)
                logger.warning(f"Missing required fields: {missing_str}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": f"Missing required fields: {missing_str}",
                    "suggestion": "Please provide all required information for flight search."
                }
            
            # Validate date formats
            if not validate_date_format(date):
                logger.warning(f"Invalid date format: {date}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Invalid departure date format. Use YYYY-MM-DD.",
                    "suggestion": "Please provide the date in YYYY-MM-DD format (e.g., 2025-05-15)."
                }
                
            if return_date and not validate_date_format(return_date):
                logger.warning(f"Invalid return date format: {return_date}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Invalid return date format. Use YYYY-MM-DD.",
                    "suggestion": "Please provide the return date in YYYY-MM-DD format (e.g., 2025-05-22)."
                }
            
            # Log search parameters
            logger.info(
                f"Searching flights from {origin} to {destination} on {date}" + 
                (f", returning {return_date}" if return_date else "") + 
                f" for {num_passengers} passengers"
            )
            
            # In a real implementation, this would call a flight search API
            # For demo purposes, we'll just generate mock data
            try:
                flights = self._generate_mock_flights(
                    origin, destination, date, return_date, num_passengers, max_results,
                    sort_by=sort_by, price_range=price_range, cabin_class=cabin_class)
                
                logger.info(f"Found {len(flights)} flights from {origin} to {destination}")
                return {"status": "success", "flights": flights}
            except ServiceUnavailableError as e:
                # This specific error will trigger the retry mechanism
                logger.error(f"Service unavailable: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in FlightSearchTool: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "message": f"Failed to search flights: {str(e)}",
                "suggestion": "Please try again with different search criteria or try later."
            }
    
    def _generate_mock_flights(self, origin, destination, date, return_date=None, num_passengers=1, max_results=20, sort_by="price", price_range="", cabin_class="economy") -> List[Dict[str, Any]]:
        """Generate mock flight data for demonstration purposes."""
        # Simulate potential service outage (1% chance)
        if random.random() < 0.01:
            raise ServiceUnavailableError("Flight search service temporarily unavailable")
            
        airlines = ["Delta", "United", "American", "British Airways", "Emirates", "Lufthansa", "Qatar Airways"]
        aircraft = ["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380", "Boeing 787", "Airbus A350"]
        
        # Parse the date string
        try:
            departure_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            # This should be caught by the validation above, but just in case
            raise ValidationError(f"Invalid date format: {date}")
            
        flights = []
        for i in range(min(max_results, 10)):
            # Generate random departure and arrival times
            dep_hour = random.randint(6, 22)
            flight_duration = random.randint(1, 12)  # hours
            flight_duration_minutes = random.randint(0, 59)  # minutes
            total_minutes = dep_hour * 60 + flight_duration * 60 + flight_duration_minutes
            arr_hour = (total_minutes // 60) % 24
            arr_minute = total_minutes % 60
            
            # Calculate if arrival is next day
            next_day = total_minutes >= 24 * 60
            arrival_day_offset = "+1" if next_day else ""
            
            # Generate more realistic and varied prices based on the route, time, and demand
            route_factor = hash(f"{origin}{destination}") % 100 / 100 + 0.5  # 0.5 to 1.5 factor
            popularity_factor = 1 + (0.2 * flight_duration / 12)  # Longer flights cost more per hour
            time_factor = 1 + (0.3 * (abs(dep_hour - 12) / 12))  # Flights at convenient times cost more
            
            # Base price calculation with more variables
            base_price = int(random.randint(200, 1000) * route_factor * popularity_factor * time_factor)
            
            # Calculate different cabin classes with more realistic pricing ratios
            economy_price = base_price
            premium_economy_price = base_price * 1.8
            business_price = base_price * 3.2
            first_price = base_price * 6.5
            
            # Add some price variations for the same route (+/- 15%)
            random_variation = random.uniform(0.85, 1.15)
            economy_price = int(economy_price * random_variation)
            premium_economy_price = int(premium_economy_price * random_variation)
            business_price = int(business_price * random_variation)
            first_price = int(first_price * random_variation)
            
            flight = {
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(['DL', 'UA', 'AA', 'BA', 'EK', 'LH', 'QR'])}{random.randint(100, 999)}",
                "aircraft": random.choice(aircraft),
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": date,
                "departure_time": f"{dep_hour:02d}:{random.randint(0, 59):02d}",
                "arrival_time": f"{arr_hour:02d}:{arr_minute:02d}{arrival_day_offset}",
                "duration": f"{flight_duration}h {flight_duration_minutes}m",
                "stops": random.randint(0, 2),
                "prices": {
                    "economy": economy_price * num_passengers,
                    "premium_economy": premium_economy_price * num_passengers,
                    "business": business_price * num_passengers,
                    "first": first_price * num_passengers
                },
                "price_details": {
                    "base_fare": int(economy_price * 0.7),
                    "taxes_and_fees": int(economy_price * 0.3),
                    "per_passenger": economy_price,
                    "total": economy_price * num_passengers
                },
                "amenities": [
                    random.choice(["Wi-Fi", "No Wi-Fi"]),
                    random.choice(["Power outlets", "USB charging", "No power"]),
                    random.choice(["Seatback entertainment", "No entertainment"]),
                    random.choice(["Complimentary meal", "Meal for purchase", "No meal service"])
                ],
                "baggage_allowance": {
                    "carry_on": random.choice(["1 bag", "2 bags"]),
                    "checked": random.choice(["0 bags", "1 bag", "2 bags"])
                }
            }
            flights.append(flight)
            
        # Filter by price range if specified
        if price_range:
            try:
                min_price, max_price = map(int, price_range.split('-'))
                flights = [f for f in flights if min_price <= f["prices"][cabin_class] <= max_price]
            except (ValueError, IndexError):
                # If price range is invalid, ignore the filter
                logger.warning(f"Invalid price range format: {price_range}")
        
        # Sort flights based on sort_by parameter
        if sort_by == "price":
            flights.sort(key=lambda x: x["prices"][cabin_class])
        elif sort_by == "duration":
            flights.sort(key=lambda x: int(x["duration"].split('h')[0]) * 60 + int(x["duration"].split('h ')[1].split('m')[0]))
        elif sort_by == "departure":
            flights.sort(key=lambda x: x["departure_time"])
        elif sort_by == "airline":
            flights.sort(key=lambda x: x["airline"])
            
        # Add a summary section with statistics
        price_stats = {
            "lowest_price": min([f["prices"][cabin_class] for f in flights]) if flights else 0,
            "highest_price": max([f["prices"][cabin_class] for f in flights]) if flights else 0,
            "average_price": int(sum([f["prices"][cabin_class] for f in flights]) / len(flights)) if flights else 0
        }
        
        # Add summary to the first flight if there are flights
        if flights:
            flights[0]["search_summary"] = {
                "total_results": len(flights),
                "price_statistics": price_stats,
                "fastest_duration": min([f["duration"] for f in flights], key=lambda x: int(x.split('h')[0]) * 60 + int(x.split('h ')[1].split('m')[0])),
                "airlines_available": len(set([f["airline"] for f in flights]))
            }
            
        # For round trips, add return flights
        if return_date:
            try:
                return_date_obj = datetime.strptime(return_date, '%Y-%m-%d')
                # Ensure return date is after departure date
                if return_date_obj < departure_date:
                    raise ValidationError("Return date must be after departure date")
            except ValueError:
                # This should be caught by the validation above, but just in case
                raise ValidationError(f"Invalid return date format: {return_date}")
                
            return_flights = []
            for i in range(min(max_results, 10)):
                # Generate random departure and arrival times
                dep_hour = random.randint(6, 22)
                flight_duration = random.randint(1, 12)  # hours
                flight_duration_minutes = random.randint(0, 59)  # minutes
                total_minutes = dep_hour * 60 + flight_duration * 60 + flight_duration_minutes
                arr_hour = (total_minutes // 60) % 24
                arr_minute = total_minutes % 60
                
                # Calculate if arrival is next day
                next_day = total_minutes >= 24 * 60
                arrival_day_offset = "+1" if next_day else ""
                
                # Generate random prices with some route-based consistency
                route_factor = hash(f"{destination}{origin}") % 100 / 100 + 0.5  # 0.5 to 1.5 factor
                base_price = int(random.randint(200, 1000) * route_factor)
                economy_price = base_price
                business_price = base_price * 3
                first_price = base_price * 6
                
                flight = {
                    "airline": random.choice(airlines),
                    "flight_number": f"{random.choice(['DL', 'UA', 'AA', 'BA', 'EK', 'LH', 'QR'])}{random.randint(100, 999)}",
                    "aircraft": random.choice(aircraft),
                    "origin": destination.upper(),  # Swapped
                    "destination": origin.upper(),   # Swapped
                    "departure_date": return_date,
                    "departure_time": f"{dep_hour:02d}:{random.randint(0, 59):02d}",
                    "arrival_time": f"{arr_hour:02d}:{arr_minute:02d}{arrival_day_offset}",
                    "duration": f"{flight_duration}h {flight_duration_minutes}m",
                    "stops": random.randint(0, 2),
                    "prices": {
                        "economy": economy_price * num_passengers,
                        "business": business_price * num_passengers,
                        "first": first_price * num_passengers
                    }
                }
                
                return_flights.append(flight)
            
            return {"outbound": flights, "return": return_flights}
        
        return flights
