"""
Hotel Search Tool for the Travel Assistant.
"""

import datetime
from typing import Dict, Any, List, Optional
import logging
import json
import os
import random
from datetime import datetime, timedelta

from google.adk import tools
from google.adk.tools import BaseTool
from google.adk.tools import ToolContext

from .utils import (
    logger, retry, validate_date_format, validate_required_fields,
    sanitize_input, travel_info_cache, ApiKeyError, ServiceUnavailableError, ValidationError
)

# Logging is already set up in utils

class HotelSearchTool(BaseTool):
    """Tool for searching hotels at specific destinations."""
    
    def __init__(self):
        super().__init__(
            name="hotel_search",
            description="Search for hotels at a specific destination with filters"
        )
        
    @property
    def function_schema(self):
        """Define the function schema for the hotel search tool."""
        return {
            "name": "hotel_search",
            "description": "Search for hotels at a specific destination with filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Hotel location or city (e.g., 'Paris')"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date in YYYY-MM-DD format"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date in YYYY-MM-DD format"
                    },
                    "guests": {
                        "type": "integer",
                        "description": "Number of guests"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price per night (USD)"
                    },
                    "amenities": {
                        "type": "string",
                        "description": "Comma-separated list of required amenities (e.g., 'pool,wifi,breakfast')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    }
                },
                "required": ["destination", "check_in", "check_out"]
            }
        }
    
    @retry(max_tries=3, delay_seconds=2, exceptions=(ServiceUnavailableError,))
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a hotel search at a destination."""
        try:
            # Get parameters and sanitize inputs
            destination = sanitize_input(kwargs.get("destination", ""))
            check_in = sanitize_input(kwargs.get("check_in", ""))
            check_out = sanitize_input(kwargs.get("check_out", ""))
            guests = kwargs.get("guests", 2)
            max_price = kwargs.get("max_price")
            amenities = kwargs.get("amenities", [])
            max_results = min(kwargs.get("max_results", 5), 10)  # Cap at 10 for performance
            
            # Validate required fields
            missing_fields = validate_required_fields(
                {"destination": destination, "check_in": check_in, "check_out": check_out},
                ["destination", "check_in", "check_out"]
            )
            
            if missing_fields:
                missing_str = ", ".join(missing_fields)
                logger.warning(f"Missing required fields: {missing_str}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": f"Missing required fields: {missing_str}",
                    "suggestion": "Please provide all required information for hotel search."
                }
            
            # Validate date formats
            if not validate_date_format(check_in):
                logger.warning(f"Invalid check-in date format: {check_in}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Invalid check-in date format. Use YYYY-MM-DD.",
                    "suggestion": "Please provide the check-in date in YYYY-MM-DD format (e.g., 2025-05-15)."
                }
                
            if not validate_date_format(check_out):
                logger.warning(f"Invalid check-out date format: {check_out}")
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Invalid check-out date format. Use YYYY-MM-DD.",
                    "suggestion": "Please provide the check-out date in YYYY-MM-DD format (e.g., 2025-05-22)."
                }
                
            # Validate date logic
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
                
                if check_out_date <= check_in_date:
                    logger.warning(f"Check-out date must be after check-in date: {check_in} to {check_out}")
                    return {
                        "status": "error",
                        "error_type": "ValidationError",
                        "message": "Check-out date must be after check-in date.",
                        "suggestion": "Please ensure your check-out date is at least one day after your check-in date."
                    }
            except ValueError:
                # This should be caught by the validation above, but just in case
                return {
                    "status": "error",
                    "error_type": "ValidationError",
                    "message": "Invalid date format.",
                    "suggestion": "Please provide dates in YYYY-MM-DD format."
                }
            
            # Handle amenities validation if provided
            if amenities and not isinstance(amenities, list):
                try:
                    # Try to convert to list if it's a string
                    if isinstance(amenities, str):
                        amenities = [a.strip() for a in amenities.split(',')]
                    else:
                        amenities = list(amenities)
                except Exception:
                    logger.warning(f"Invalid amenities format: {amenities}")
                    return {
                        "status": "error",
                        "error_type": "ValidationError",
                        "message": "Invalid amenities format.",
                        "suggestion": "Please provide amenities as a list or comma-separated string."
                    }
            
            # Log search parameters
            logger.info(
                f"Searching hotels in {destination} from {check_in} to {check_out} " + 
                f"for {guests} guests" +
                (f", max price: ${max_price}" if max_price else "")
            )
            
            # Try to get from cache first
            cache_key = f"hotel_search:{destination}:{check_in}:{check_out}:{guests}:{max_price}"
            cached_result = travel_info_cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached hotel results for {destination}")
                return {"status": "success", "hotels": cached_result, "cached": True}
            
            # In a real implementation, this would call a hotel search API
            # For demo purposes, we'll just generate mock data
            try:
                hotels = self._generate_mock_hotels(
                    destination, check_in, check_out, guests, max_price, amenities, max_results)
                
                # Cache the results
                travel_info_cache.set(cache_key, hotels)
                
                logger.info(f"Found {len(hotels)} hotels in {destination}")
                return {"status": "success", "hotels": hotels}
            except ServiceUnavailableError as e:
                # This specific error will trigger the retry mechanism
                logger.error(f"Service unavailable: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error in HotelSearchTool: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to search hotels: {str(e)}"
            }
    
    def _validate_dates(self, check_in: str, check_out: str) -> bool:
        """Validate date formats and logic."""
        try:
            check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
            today = datetime.date.today()
            
            if check_in_date < today:
                return False
                
            if check_out_date <= check_in_date:
                return False
                    
            return True
        except ValueError:
            return False
    
    def _simulate_hotel_search(
        self, location: str, check_in: str, check_out: str, guests: int,
        price_min: Optional[float], price_max: Optional[float],
        amenities: List[str], star_rating: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Simulate hotel search results for demonstration purposes."""
        hotels = [
            {
                "name": f"Grand Hotel {location}",
                "address": f"123 Main Street, {location}",
                "star_rating": 5,
                "price_per_night": 299.99,
                "total_price": self._calculate_total(299.99, check_in, check_out),
                "amenities": ["pool", "wifi", "spa", "restaurant", "gym", "breakfast"],
                "available_rooms": 3,
                "image_url": "https://example.com/hotel1.jpg",
                "cancellation_policy": "Free cancellation until 48 hours before check-in"
            },
            {
                "name": f"Boutique Stay {location}",
                "address": f"456 High Street, {location}",
                "star_rating": 4,
                "price_per_night": 189.99,
                "total_price": self._calculate_total(189.99, check_in, check_out),
                "amenities": ["wifi", "breakfast", "bar"],
                "available_rooms": 5,
                "image_url": "https://example.com/hotel2.jpg",
                "cancellation_policy": "Free cancellation until 24 hours before check-in"
            },
            {
                "name": f"Budget Inn {location}",
                "address": f"789 Low Road, {location}",
                "star_rating": 3,
                "price_per_night": 99.99,
                "total_price": self._calculate_total(99.99, check_in, check_out),
                "amenities": ["wifi", "parking"],
                "available_rooms": 8,
                "image_url": "https://example.com/hotel3.jpg",
                "cancellation_policy": "Non-refundable"
            }
        ]
        
        # Apply filters
        filtered_hotels = hotels
        
        if price_min is not None:
            filtered_hotels = [h for h in filtered_hotels if h["price_per_night"] >= price_min]
            
        if price_max is not None:
            filtered_hotels = [h for h in filtered_hotels if h["price_per_night"] <= price_max]
            
        if star_rating is not None:
            filtered_hotels = [h for h in filtered_hotels if h["star_rating"] >= star_rating]
            
        if amenities:
            filtered_hotels = [
                h for h in filtered_hotels 
                if all(amenity.strip() in h["amenities"] for amenity in amenities if amenity.strip())
            ]
        
        return filtered_hotels
    
    def _calculate_total(self, price_per_night: float, check_in: str, check_out: str) -> float:
        """Calculate the total price based on number of nights."""
        check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
        nights = (check_out_date - check_in_date).days
        return round(price_per_night * nights, 2)
