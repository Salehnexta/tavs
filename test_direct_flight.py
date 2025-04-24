"""
Test script that directly calls the Serper API to demonstrate real flight search results.
"""

import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")

def search_flights(origin, destination, date_period):
    """Search for flights using the Serper API directly."""
    
    # Construct the search query
    query = f"flights from {origin} to {destination} {date_period}"
    print(f"Searching for: {query}")
    
    # Set up headers for API request
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Build the payload
    payload = {
        "q": query,
        "num": 10  # Request 10 results
    }
    
    # Make the request to Serper API
    response = requests.post(SERPER_API_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

def format_flight_results(data):
    """Format the flight search results in a readable way."""
    
    if not data or "organic" not in data:
        print("No results found or invalid response")
        return
    
    organic_results = data.get("organic", [])
    
    # Print search statistics
    print(f"\nFound {len(organic_results)} search results")
    print("-" * 70)
    
    # Extract and display flight information
    print("\nFLIGHT INFORMATION:\n")
    
    for i, result in enumerate(organic_results[:5]):  # Show first 5 results
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        
        print(f"Result {i+1}:")
        print(f"Title: {title}")
        print(f"Snippet: {snippet}")
        print(f"Link: {link}")
        
        # Check for price in the result
        if "price" in result:
            print(f"Price: ${result['price']}")
            
        print("-" * 70)
    
    # Look for price patterns in snippets
    print("\nPRICE INFORMATION EXTRACTED:")
    price_found = False
    
    for result in organic_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        
        # Simple price extraction based on common patterns
        if "$" in snippet:
            price_idx = snippet.find("$")
            price_end = min(price_idx + 20, len(snippet))
            price_snippet = snippet[price_idx:price_end]
            print(f"Price mention: {price_snippet}")
            price_found = True
            
        if "$" in title:
            price_idx = title.find("$")
            price_end = min(price_idx + 20, len(title))
            price_snippet = title[price_idx:price_end]
            print(f"Price in title: {price_snippet}")
            price_found = True
    
    if not price_found:
        print("No specific price information found in the results")
        
    # Extract airline information
    print("\nAIRLINE INFORMATION:")
    airlines = set()
    airline_keywords = ["Saudia", "flynas", "flyadeal", "SV", "Saudi Airlines"]
    
    for result in organic_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        
        for airline in airline_keywords:
            if airline.lower() in title or airline.lower() in snippet:
                airlines.add(airline)
    
    if airlines:
        print(f"Airlines mentioned: {', '.join(airlines)}")
    else:
        print("No specific airlines mentioned in the results")

def main():
    """Main function to run the flight search test."""
    print("Testing Direct Flight Search from DMM to RUH for next week")
    print("=" * 70)
    
    origin = "DMM"
    destination = "RUH" 
    date_period = "next week"
    
    try:
        # Perform the search
        results = search_flights(origin, destination, date_period)
        
        # Format and display results
        format_flight_results(results)
        
        # Save raw results to file for debugging
        with open("flight_search_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\nRaw results saved to flight_search_results.json")
        
    except Exception as e:
        logger.error(f"Error in flight search: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
