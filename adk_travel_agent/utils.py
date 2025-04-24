"""
Utility functions and classes for the ADK Travel Assistant.

This module contains error handling utilities, retry mechanisms, validation functions,
and other common functionality used across the travel assistant components.
"""

import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("travel_assistant.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Custom exception types
class ApiKeyError(Exception):
    """Exception raised for API key issues."""
    pass

class ServiceUnavailableError(Exception):
    """Exception raised when a service is unavailable."""
    pass

class ValidationError(Exception):
    """Exception raised for input validation errors."""
    pass

# Retry decorator
def retry(max_tries: int = 3, delay_seconds: int = 1, 
          exceptions: tuple = (Exception,), logger = None):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_tries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries (doubles with each retry)
        exceptions: Tuple of exceptions to catch and retry on
        logger: Logger instance to use for logging retries
    
    Returns:
        The decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_logger = logger or logging.getLogger(func.__module__)
            tries = 0
            current_delay = delay_seconds
            
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries == max_tries:
                        local_logger.error(
                            f"Failed after {max_tries} tries: {str(e)}", 
                            exc_info=True
                        )
                        raise
                    
                    local_logger.warning(
                        f"Retry {tries}/{max_tries} after error: {str(e)}. "
                        f"Waiting {current_delay}s before retry."
                    )
                    time.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff
                    
        return wrapper
    return decorator

# Input validation functions
def validate_date_format(date_string: str) -> bool:
    """
    Validate if a string is in YYYY-MM-DD format.
    
    Args:
        date_string: The date string to validate
        
    Returns:
        True if the date is valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Dictionary containing the fields to validate
        required_fields: List of field names that are required
        
    Returns:
        List of missing field names, empty if all required fields are present
    """
    missing = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing.append(field)
    return missing

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Basic sanitization - remove potentially harmful characters
    # This is a simple example; more sophisticated sanitization might be needed
    import re
    sanitized = re.sub(r'[^\w\s\-\.,?!]', '', text)
    return sanitized

# Cache with expiration
class ExpiringCache:
    """A cache with expiration for storing API responses."""
    
    def __init__(self, expiry_seconds: int = 3600):
        """
        Initialize the cache.
        
        Args:
            expiry_seconds: Number of seconds after which cache entries expire
        """
        self.cache = {}
        self.expiry = {}
        self.expiry_seconds = expiry_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        now = time.time()
        if key in self.cache and now < self.expiry.get(key, 0):
            return self.cache[key]
        
        # Clean up expired entry if it exists
        if key in self.cache:
            del self.cache[key]
            del self.expiry[key]
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache with expiration.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        self.expiry[key] = time.time() + self.expiry_seconds
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.expiry.clear()
        
# Create a shared cache instance for travel info
travel_info_cache = ExpiringCache(expiry_seconds=86400)  # 24 hours

# API key validation
def validate_api_key(api_key: str, api_name: str) -> None:
    """
    Validate that an API key is present.
    
    Args:
        api_key: The API key to validate
        api_name: Name of the API for error messages
        
    Raises:
        ApiKeyError: If the API key is missing or invalid
    """
    if not api_key:
        raise ApiKeyError(f"{api_name} API key is missing. Check your .env file.")
    
    # Additional validation could be added here, e.g., key format checking
