"""
Direct test of Groq API integration using OpenAI SDK.

This script directly tests the Groq API using the OpenAI SDK without
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

def test_groq_direct():
    """Test direct connection to Groq API using OpenAI SDK."""
    print("\n----- Testing Direct Groq Integration with OpenAI SDK -----")
    
    try:
        # Initialize OpenAI client with Groq configuration
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_API_BASE
        )
        
        print(f"✅ Initialized OpenAI client with Groq API at {GROQ_API_BASE}")
        
        # List available models
        print("\nFetching available Groq models...")
        models = client.models.list()
        print(f"Available models: {[model.id for model in models.data]}")
        
        # Test with a simple travel-related query
        print("\nSending test query to Groq...")
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Using Llama 3 model from Groq
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": "What are the top 3 must-visit attractions in Paris?"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        # Print the response
        print("\n----- Groq Response -----")
        print(response.choices[0].message.content)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_groq_direct()
