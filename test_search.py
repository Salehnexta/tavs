"""
Test script to demonstrate real search results from the WebSearchTool.
"""

import os
import json
from dotenv import load_dotenv
from adk_travel_agent.web_search_tool import WebSearchTool
from google.adk.tools import ToolContext

# Load environment variables
load_dotenv()

# Create the web search tool
web_search_tool = WebSearchTool()

# Create a dummy tool context
# For ADK 0.2.0, ToolContext doesn't need conversation_id or user_id
tool_context = ToolContext()

# Perform a search for DMM to Cairo trip
query = "trip from dmm to cairo next week"
search_results = web_search_tool.execute(
    tool_context=tool_context,
    query=query,
    num_results=5,
    search_type="web"
)

# Pretty print the results
print(f"Search query: '{query}'")
print(f"Results: {json.dumps(search_results, indent=2)}")
