#!/usr/bin/env python
"""
Simple test script for the Content Planner Agent.
"""
import sys
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add the current directory to the path
import os
sys.path.insert(0, os.path.abspath("."))

from content_planner_agent.agent import ContentPlannerAgent

def main():
    """Main function to test the agent."""
    print("Initializing agent...")
    
    # Set debug_mode=True to avoid API calls during testing
    # Change to False for real API calls
    debug_mode = False
    agent = ContentPlannerAgent(debug_mode=debug_mode)
    
    print("\nProcessing message...")
    response = agent.process_message("Tell me about this app", "test_session")
    
    print("\nResponse:")
    print(response)

if __name__ == "__main__":
    main() 