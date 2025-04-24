"""
Test script to verify the ADK agent with DeepSeek LLM integration.

This script tests the Travel Assistant agent to verify if the LLM integration
is working properly.
"""

import os
import logging
import sys
from dotenv import load_dotenv

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the travel assistant agent
from travel_assistant.agent import travel_assistant

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_travel_assistant():
    """Test the travel assistant agent with a simple query."""
    print("\n----- Testing Travel Assistant Agent with DeepSeek LLM -----")
    
    try:
        # Get the model name
        model_name = travel_assistant.model.get_model_name()
        print(f"Agent is using model: {model_name}")
        
        # Test with a simple travel query
        print("\nSending test query to agent...")
        response = travel_assistant.generate_response("What are popular destinations to visit in France?")
        
        # Print the response
        print("\n----- Agent Response -----")
        print(response.text)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_travel_assistant()
