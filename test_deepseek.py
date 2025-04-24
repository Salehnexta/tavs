"""
Test script for DeepSeek LLM integration with Travel Assistant.

This script tests if the DeepSeek LLM is properly configured and working with our Travel Assistant.
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
from travel_assistant.agent import travel_assistant, create_interactive_runner

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm_integration():
    """Test the Travel Assistant with DeepSeek LLM integration."""
    print("\n----- Testing Travel Assistant with DeepSeek LLM -----")
    
    try:
        # Create an interactive runner for testing
        runner = create_interactive_runner(travel_assistant)
        
        # Send a test query
        print("\nSending test query to agent...")
        response = runner.run("What are some good travel destinations in Japan?")
        
        # Print the response
        print("\n----- Agent Response -----")
        print(response)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_llm_integration()
