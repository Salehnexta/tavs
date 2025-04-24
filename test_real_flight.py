"""
Test script to demonstrate the real flight search functionality
"""

import json
import logging
from dotenv import load_dotenv
from adk_travel_agent.real_flight_tool import RealFlightSearchTool
from google.adk.tools import ToolContext
from google.adk.core.contexts import InvocationContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    print("Testing Real Flight Search from DMM to RUH for next week")
    print("-" * 70)
    
    # Create the tool
    real_flight_tool = RealFlightSearchTool()
    
    # Create invocation context and tool context (required for ADK 0.2.0)
    invocation_context = InvocationContext()
    tool_context = ToolContext(invocation_context)
    
    # Execute the tool with parameters
    result = real_flight_tool.execute(
        tool_context,
        origin="DMM",
        destination="RUH",
        date_period="next week",
        num_results=5,
        sort_by_price=True
    )
    
    # Print results in a readable format
    print(f"Status: {result.get('status')}")
    
    if result.get('status') == 'success':
        print(f"Found {len(result.get('flights', []))} flights")
        
        # Print summary if available
        first_flight = result.get('flights', [])[0] if result.get('flights') else {}
        summary = first_flight.get('summary', {})
        
        if summary:
            print("\nSUMMARY:")
            print(f"Total Results: {summary.get('total_results')}")
            print(f"Airlines Available: {summary.get('airlines_available')}")
            print(f"Airlines: {', '.join(summary.get('airlines', []))}")
            print(f"Lowest Price: {summary.get('lowest_price', 'N/A')}")
            print(f"Highest Price: {summary.get('highest_price', 'N/A')}")
            print(f"Average Price: {summary.get('average_price', 'N/A')}")
            print("-" * 70)
        
        # Print flight details
        print("\nFLIGHT DETAILS:")
        for i, flight in enumerate(result.get('flights', [])):
            if 'summary' in flight:  # Skip printing the summary entry again
                continue
                
            print(f"\nFlight Option {i+1}:")
            print(f"Route: {flight.get('origin')} → {flight.get('destination')}")
            
            if 'airlines' in flight:
                print(f"Airlines: {', '.join(flight.get('airlines', []))}")
            
            if 'price' in flight:
                print(f"Price: {flight.get('price')}")
            
            if 'duration' in flight:
                print(f"Duration: {flight.get('duration')}")
            
            if 'schedule' in flight:
                print(f"Schedule: {flight.get('schedule')}")
            
            if 'additional_info' in flight:
                print(f"Additional Info: {flight.get('additional_info')}")
            
            print(f"Source: {flight.get('source_title')}")
            print(f"Link: {flight.get('source_link')}")
            print("-" * 50)
    else:
        print(f"Message: {result.get('message')}")
        if 'suggestion' in result:
            print(f"Suggestion: {result.get('suggestion')}")

if __name__ == "__main__":
    main()
