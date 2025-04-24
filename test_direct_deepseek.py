"""
Direct test of DeepSeek API integration using OpenAI SDK.

This script directly tests the DeepSeek API using the OpenAI SDK without
the ADK layer to verify basic connectivity and authentication.
"""

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys and base URL from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")

def test_deepseek_direct():
    """Test direct connection to DeepSeek API using OpenAI SDK."""
    print("\n----- Testing Direct DeepSeek Integration with OpenAI SDK -----")
    
    try:
        # Initialize OpenAI client with DeepSeek configuration
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        
        print(f"✅ Initialized OpenAI client with DeepSeek API at {DEEPSEEK_API_BASE}")
        
        # Test with a simple travel-related query
        print("\nSending test query to DeepSeek...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": "What are the best destinations to visit in Japan during spring?"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        # Print the response
        print("\n----- DeepSeek Response -----")
        print(response.choices[0].message.content)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_deepseek_direct()
