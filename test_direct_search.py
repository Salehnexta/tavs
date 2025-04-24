"""
Direct test of Serper API to show real search results.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Serper API configuration
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")

# Query for DMM to Cairo trip
query = "trip from dmm to cairo next week"

# Set up headers for API request
headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

# Build the payload
payload = {
    "q": f"travel {query}",
    "num": 5  # Number of results
}

# Make the API request
try:
    print(f"Sending search request for: '{query}'")
    response = requests.post(SERPER_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    # Get the search results
    results = response.json()
    
    # Process and display the results
    print("\nActual Search Results from Serper API:")
    print("-" * 60)
    
    if "organic" in results:
        for i, result in enumerate(results["organic"][:5], 1):
            print(f"Result {i}:")
            print(f"Title: {result.get('title', 'No title')}")
            print(f"Link: {result.get('link', 'No link')}")
            print(f"Snippet: {result.get('snippet', 'No description')[:150]}...")
            print("-" * 60)
    else:
        print("No organic results found.")
        
    # Save full results to file for review
    with open("search_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Full results saved to search_results.json")
    
except Exception as e:
    print(f"Error: {e}")
