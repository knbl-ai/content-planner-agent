"""
Main entry point for the Content Planner Agent application.
"""
import os
import logging
import uuid
from flask import Flask
from content_planner_agent.api.app import create_app
from content_planner_agent.utils.logging_config import configure_logging
from content_planner_agent.agent import ContentPlannerAgent

def test_routing_logic():
    """
    Test the routing logic of the agent with different queries.
    """
    agent = ContentPlannerAgent()
    session_id = str(uuid.uuid4())
    logger = logging.getLogger(__name__)
    
    logger.info("==== TESTING ROUTING LOGIC ====")
    
    # Test guidelines intent
    logger.info("\n\n==== TESTING GUIDELINES INTENT ====")
    response = agent.process_message("Can you help me create content guidelines for my tech blog?", session_id)
    logger.info(f"Response: {response[:100]}...")
    
    # Test app info intent
    logger.info("\n\n==== TESTING APP INFO INTENT ====")
    response = agent.process_message("What features does this application have?", session_id)
    logger.info(f"Response: {response[:100]}...")
    
    # Test post examples intent
    logger.info("\n\n==== TESTING POST EXAMPLES INTENT ====")
    response = agent.process_message("Can you generate some example posts based on my guidelines?", session_id)
    logger.info(f"Response: {response[:100]}...")
    
    logger.info("==== TESTING COMPLETE ====")

if __name__ == "__main__":
    # Configure logging
    os.environ["LOG_LEVEL"] = "DEBUG"
    configure_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Content Planner Agent application")
    
    # Run routing logic tests
    test_routing_logic()
    
    # Create and run the Flask app
    app = create_app()
    
    # Set debug mode based on environment
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    logger.info(f"Running Flask app with debug={debug}")
    app.run(host="0.0.0.0", port=5000, debug=debug) 