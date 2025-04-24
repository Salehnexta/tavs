"""
LLM Adapter for integrating DeepSeek with Google ADK using OpenAI SDK.

This module configures the OpenAI SDK to work with DeepSeek LLM:
- DeepSeek Chat as primary LLM accessed via OpenAI SDK
- Groq as fallback option (uses LiteLLM)

The adapter integrates with Google ADK's LlmAgent framework.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, cast

from dotenv import load_dotenv
import openai
import litellm
from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define DeepSeek API base URL
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# DeepSeek model configurations
DEEPSEEK_MODELS = {
    "chat": "deepseek-chat",
    "coder": "deepseek-coder"
}

# Fallback model configurations
FALLBACK_MODELS = {
    "groq": "groq/llama3-8b-8192",
    "openai": "gpt-3.5-turbo"
}

def configure_openai_for_deepseek() -> bool:
    """
    Configure the OpenAI SDK to use DeepSeek's API.
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if not DEEPSEEK_API_KEY:
        logger.error("DeepSeek API key not found in environment variables")
        return False
    
    # Configure the OpenAI client to use DeepSeek's API
    openai.api_key = DEEPSEEK_API_KEY
    openai.base_url = DEEPSEEK_API_BASE
    
    logger.info(f"OpenAI SDK configured to use DeepSeek API at {DEEPSEEK_API_BASE}")
    return True

class CustomOpenAIModel(BaseLlm):
    """Custom implementation of BaseLlm using OpenAI SDK with DeepSeek."""
    
    def __init__(self):
        super().__init__()
        self._model_name = DEEPSEEK_MODELS["chat"]
        self._client = None
        self._setup_success = self._setup_client()
        
    def get_model_name(self):
        return self._model_name
        
    def set_model_name(self, model_name: str):
        self._model_name = model_name
        
    def _setup_client(self) -> bool:
        """Set up the OpenAI client for DeepSeek."""
        if not configure_openai_for_deepseek():
            logger.warning("Failed to configure OpenAI SDK for DeepSeek")
            return False
            
        try:
            self._client = openai.OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_API_BASE
            )
            return True
        except Exception as e:
            logger.error(f"Error setting up OpenAI client: {e}")
            return False
    
    async def generate_content_async(self, request):
        """Generate content using the OpenAI client asynchronously."""
        if not self._setup_success or not self._client:
            raise ValueError("Client not properly initialized")
            
        try:
            # Convert ADK request to OpenAI format
            messages = []
            for message in request.messages:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
                
            # Call the OpenAI API
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1024
            )
            
            # Return the response text
            return {"text": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
            
    def generate_content(self, request):
        """Generate content using the OpenAI client."""
        if not self._setup_success or not self._client:
            raise ValueError("Client not properly initialized")
            
        try:
            # Convert ADK request to OpenAI format
            messages = []
            for message in request.messages:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
                
            # Call the OpenAI API
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1024
            )
            
            # Return the response text
            return {"text": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

class CustomLiteLLMModel(BaseLlm):
    """Custom implementation of BaseLlm using LiteLLM."""
    
    def __init__(self):
        super().__init__()
        self._model_name = FALLBACK_MODELS["groq"]
        self._setup_success = self._setup_client()
        
    def get_model_name(self):
        return self._model_name
        
    def set_model_name(self, model_name: str):
        self._model_name = model_name
        self._setup_success = self._setup_client()
        
    def _setup_client(self) -> bool:
        """Set up LiteLLM with the appropriate API key."""
        try:
            if "groq" in self._model_name.lower() and GROQ_API_KEY:
                litellm.api_key = GROQ_API_KEY
                return True
            elif "openai" in self._model_name.lower() and OPENAI_API_KEY:
                litellm.api_key = OPENAI_API_KEY
                return True
            else:
                logger.error(f"No API key found for model {self._model_name}")
                return False
        except Exception as e:
            logger.error(f"Error setting up LiteLLM client: {e}")
            return False
    
    async def generate_content_async(self, request):
        """Generate content using LiteLLM asynchronously."""
        if not self._setup_success:
            raise ValueError("LiteLLM not properly initialized")
            
        try:
            # Convert ADK request to LiteLLM format
            messages = []
            for message in request.messages:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
                
            # Call LiteLLM
            response = await litellm.acompletion(
                model=self._model_name,
                messages=messages,
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1024
            )
            
            # Return the response text
            return {"text": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error generating content with LiteLLM: {e}")
            raise
            
    def generate_content(self, request):
        """Generate content using LiteLLM."""
        if not self._setup_success:
            raise ValueError("LiteLLM not properly initialized")
            
        try:
            # Convert ADK request to LiteLLM format
            messages = []
            for message in request.messages:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
                
            # Call LiteLLM
            response = litellm.completion(
                model=self._model_name,
                messages=messages,
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1024
            )
            
            # Return the response text
            return {"text": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error generating content with LiteLLM: {e}")
            raise

def create_adk_model(model_type: str = "chat") -> Optional[BaseLlm]:
    """
    Create and return an ADK-compatible model.
    
    Args:
        model_type: The type of DeepSeek model to use (chat or coder)
        
    Returns:
        A configured model instance for ADK or None if setup fails
    """
    if model_type not in DEEPSEEK_MODELS:
        logger.warning(f"Unknown model type {model_type}, falling back to 'chat'")
        model_type = "chat"
    
    # Try to create OpenAI model for DeepSeek
    model = CustomOpenAIModel()
    model.set_model_name(DEEPSEEK_MODELS[model_type])
    if model._setup_success:
        return model
    
    # If DeepSeek setup fails, try fallback models
    logger.warning("DeepSeek setup failed, trying fallback models")
    
    # Try Groq as fallback
    if GROQ_API_KEY:
        logger.info("Falling back to Groq via LiteLLM")
        groq_model = CustomLiteLLMModel()
        groq_model.set_model_name(FALLBACK_MODELS["groq"])
        if groq_model._setup_success:
            return groq_model
    
    # Try OpenAI as last resort
    if OPENAI_API_KEY:
        logger.info("Falling back to OpenAI")
        openai_model = CustomLiteLLMModel()
        openai_model.set_model_name(FALLBACK_MODELS["openai"])
        if openai_model._setup_success:
            return openai_model
    
    logger.error("Failed to create any LLM model. Check API keys and connectivity.")
    return None
