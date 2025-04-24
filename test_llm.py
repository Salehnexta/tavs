"""
Test script to verify DeepSeek LLM integration.

This script directly tests if the DeepSeek LLM adapter is working properly
with the OpenAI SDK configuration.
"""

import os
import logging
from dotenv import load_dotenv
from pprint import pprint

# Add the current directory to PATH for imports
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import LLM adapter
from adk_travel_agent.llm_adapter import create_adk_model, CustomOpenAIModel

# Load environment variables and set up logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deepseek_connection():
    """Test direct connection to DeepSeek API."""
    print("\n----- Testing DeepSeek LLM Connection -----")
    
    try:
        # Create the model
        model = create_adk_model(model_type="chat")
        
        if model is None:
            print("❌ Failed to create LLM model. Check API keys and connectivity.")
            return False
            
        print(f"✅ Successfully created LLM model: {model.get_model_name()}")
        
        # Test with a simple travel-related query
        from google.adk.models import Request, Message
        
        # Create a simple request
        request = Request(
            messages=[
                Message(role="user", content="What are the best destinations to visit in April?")
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Generate content
        print("\nSending test query to LLM...")
        response = model.generate_content(request)
        
        # Print the response
        print("\n----- LLM Response -----")
        print(response.get("text", "No response received"))
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_deepseek_connection()
