"""
Main entry point for the ADK Travel Assistant.

This module provides the CLI interface for running the Travel Assistant agent
in different modes (interactive, web) and with various configuration options.

Usage:
    # Run in interactive mode (CLI)
    python -m adk_travel_agent.main

    # Run with web interface
    python -m adk_travel_agent.main --web

    # Run with debug logging
    python -m adk_travel_agent.main --debug

    # Specify a different LLM model type
    python -m adk_travel_agent.main --model-type coder
"""

import argparse
import logging
import sys
from typing import Optional, List, Union

from google.adk import Runner

# Import our travel agent
from .agent import create_travel_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the Travel Assistant.
    
    Args:
        args: Command-line arguments to parse, or None to use sys.argv.
        
    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="ADK Travel Assistant")
    
    parser.add_argument(
        "--model-type",
        type=str,
        default="chat",
        choices=["chat", "coder"],
        help="Type of LLM model to use (chat or coder)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Run with web interface instead of CLI"
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the Travel Assistant.
    
    Args:
        args: Command-line arguments, or None to use sys.argv.
    """
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Set up logging based on debug flag
    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Create the travel agent
        logger.info(f"Creating Travel Assistant with model type: {parsed_args.model_type}")
        travel_agent = create_travel_agent(
            model_type=parsed_args.model_type,
            debug=parsed_args.debug
        )
        
        # Run the agent
        if parsed_args.web:
            logger.info("Starting Travel Assistant with web interface")
            # Note: ADK web interface is started using the CLI command:
            # adk web
            # This is handled automatically when running via the ADK CLI
            print("\nTo start the web interface, run:")
            print("adk web\n")
            sys.exit(0)
        else:
            # Run in interactive mode
            logger.info("Starting Travel Assistant in interactive mode")
            runner = Runner(agent=travel_agent)
            runner.run()
    
    except Exception as e:
        logger.error(f"Error running Travel Assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
