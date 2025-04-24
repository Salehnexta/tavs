"""
Web Search Tool for the Travel Assistant using Serper API.
"""

import os
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from google.adk import tools
from google.adk.tools import BaseTool, ToolContext

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")

# Configure requests with retry logic
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

# Cache configuration
CACHE_TTL = 3600  # Cache results for 1 hour (in seconds)

class WebSearchTool(BaseTool):
    """Tool for performing web searches for travel-related information using the Serper API."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for travel-related information"
        )
    
    @property
    def function_schema(self):
        """Define the function schema for the web search tool."""
        return {
            "name": "web_search",
            "description": "Search the web for travel-related information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (max 10)"
                    },
                    "search_type": {
                        "type": "string",
                        "description": "Type of search to perform: 'web', 'news', or 'places'.",
                        "enum": ["web", "news", "places"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional location context for the search (e.g., 'New York, USA')"
                    },
                    "language": {
                        "type": "string",
                        "description": "ISO language code (e.g., 'en' for English, 'fr' for French)"
                    },
                    "recent": {
                        "type": "boolean",
                        "description": "If true, prioritize recent results"
                    }
                },
                "required": ["query"]
            }
        }
    
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        """Execute a web search using Serper API."""
        try:
            # Extract and validate parameters
            query = kwargs.get("query")
            if not query or not isinstance(query, str) or len(query.strip()) == 0:
                return {
                    "status": "error",
                    "message": "A valid query is required for web search."
                }
                
            num_results = min(int(kwargs.get("num_results", 3)), 10)
            search_type = kwargs.get("search_type", "web").lower()
            location = kwargs.get("location")
            language = kwargs.get("language")
            recent = kwargs.get("recent", False)
            
            if not SERPER_API_KEY:
                return {
                    "status": "error",
                    "message": "Serper API key is not configured. Please set SERPER_API_KEY in your environment."
                }
            
            # Perform the search using Serper API with caching
            search_results = self._perform_search(
                query=query, 
                num_results=num_results,
                search_type=search_type,
                location=location,
                language=language,
                recent=recent
            )
            
            if not search_results or "error" in search_results[0]:
                return {
                    "status": "error",
                    "message": f"Search failed: {search_results[0].get('error', 'Unknown error') if search_results else 'No results'}"
                }
            
            return {
                "status": "success",
                "results": search_results
            }
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {
                "status": "error",
                "message": f"Failed to perform search: {str(e)}"
            }
    
    # Use LRU cache to avoid repeated identical queries
    @lru_cache(maxsize=100)
    def _cached_search(self, query_hash: str, search_type: str, timestamp_bucket: int) -> Tuple[List[Dict[str, Any]], float]:
        """Cached search result to avoid redundant API calls."""
        # This is just a wrapper function that can be cached
        # The timestamp_bucket parameter ensures cache entries expire
        # We don't actually use it in the function body
        return [], time.time()
    
    def _perform_search(self, query: str, num_results: int, search_type: str = "web", 
                        location: Optional[str] = None, language: Optional[str] = None, 
                        recent: bool = False) -> List[Dict[str, Any]]:
        """Perform a search using the Serper API with caching support."""
        try:
            # Add travel-related context to the query if it doesn't already have it
            if not any(term in query.lower() for term in ["travel", "trip", "vacation", "hotel", "flight", "destination"]):
                query = f"travel {query}"
            
            # Create a cache key based on all parameters
            cache_base = f"{query}|{num_results}|{search_type}|{location}|{language}|{recent}"
            query_hash = hashlib.md5(cache_base.encode()).hexdigest()
            
            # Create a timestamp bucket (e.g., current hour) for cache expiration
            timestamp_bucket = int(time.time() / CACHE_TTL)
            
            # Try to get results from cache
            try:
                cached_results, cache_time = self._cached_search(query_hash, search_type, timestamp_bucket)
                
                # If we have cached results and they're not too old, use them
                if cached_results and (time.time() - cache_time) < CACHE_TTL:
                    logger.info(f"Using cached results for query: {query}")
                    return cached_results
            except Exception as cache_error:
                logger.warning(f"Cache error (continuing with live search): {cache_error}")
            
            # Set up headers for API request
            headers = {
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Build the payload
            payload = {
                "q": query,
                "num": num_results
            }
            
            # Add optional parameters if provided
            if location:
                payload["gl"] = location
            if language:
                payload["hl"] = language
            
            # Adjust API endpoint based on search type
            api_url = SERPER_API_URL
            if search_type == "news":
                api_url = api_url.replace("search", "news")
            elif search_type == "places":
                api_url = api_url.replace("search", "places")
            
            # Perform the API request with retry logic
            response = http.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process results based on search type
            processed_results = []
            
            if search_type == "web":
                # Handle standard web search results
                if "organic" not in data:
                    return [{"title": "No results found", "snippet": "Try a different search query"}]
                
                organic_results = data["organic"]
                for result in organic_results[:num_results]:
                    processed_results.append({
                        "title": result.get("title", "No title"),
                        "link": result.get("link", "No link"),
                        "snippet": result.get("snippet", "No description available"),
                        "position": result.get("position"),
                        "source": "web"
                    })
                    
                # Add knowledge graph if available
                if "knowledgeGraph" in data and len(processed_results) < num_results:
                    kg = data["knowledgeGraph"]
                    kg_result = {
                        "title": kg.get("title", "Knowledge Graph Result"),
                        "link": kg.get("website", ""),
                        "snippet": kg.get("description", ""),
                        "source": "knowledge_graph"
                    }
                    processed_results.insert(0, kg_result)
                    
            elif search_type == "news":
                # Handle news search results
                if "news" not in data:
                    return [{"title": "No news results found", "snippet": "Try a different search query"}]
                
                news_results = data["news"]
                for result in news_results[:num_results]:
                    processed_results.append({
                        "title": result.get("title", "No title"),
                        "link": result.get("link", "No link"),
                        "snippet": result.get("snippet", "No description available"),
                        "date": result.get("date", "Unknown date"),
                        "source": result.get("source", "Unknown source"),
                        "type": "news"
                    })
                    
            elif search_type == "places":
                # Handle places search results
                if "places" not in data:
                    return [{"title": "No place results found", "snippet": "Try a different search query"}]
                
                places_results = data["places"]
                for result in places_results[:num_results]:
                    processed_results.append({
                        "title": result.get("title", "No title"),
                        "address": result.get("address", "No address available"),
                        "rating": result.get("rating", "Not rated"),
                        "reviews": result.get("reviews", "No reviews"),
                        "category": result.get("category", "Uncategorized"),
                        "phone": result.get("phone", ""),
                        "website": result.get("website", ""),
                        "snippet": result.get("description", "No description available"),
                        "type": "place"
                    })
            else:
                # Fallback to organic results for unrecognized types
                if "organic" not in data:
                    return [{"title": "No results found", "snippet": "Try a different search query"}]
                
                organic_results = data["organic"]
                for result in organic_results[:num_results]:
                    processed_results.append({
                        "title": result.get("title", "No title"),
                        "link": result.get("link", "No link"),
                        "snippet": result.get("snippet", "No description available"),
                        "source": "web"
                    })
            
            # Store results in cache
            try:
                # Clear the cache entry first to avoid collision
                self._cached_search.cache_clear()
                # Cache the new results
                self._cached_search(query_hash, search_type, timestamp_bucket)
                # Manually set the cached value
                self._cached_search.__wrapped__.__closure__[0].cell_contents[query_hash, search_type, timestamp_bucket] = (processed_results, time.time())
            except Exception as cache_error:
                logger.warning(f"Cache storage error: {cache_error}")
                
            return processed_results
            
        except requests.RequestException as e:
            logger.error(f"Request error in Serper search: {e}")
            return [{"error": f"Search API error: {str(e)}"}]
        except ValueError as e:
            logger.error(f"JSON parsing error in Serper search: {e}")
            return [{"error": f"Response parsing error: {str(e)}"}]
        except Exception as e:
            logger.error(f"Unexpected error in Serper search: {e}")
            return [{"error": f"Unexpected error: {str(e)}"}]
