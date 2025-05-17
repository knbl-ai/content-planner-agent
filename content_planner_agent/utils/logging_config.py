"""
Logging configuration for the Content Planner Agent.
"""
import logging
import sys
from content_planner_agent.config.settings import LOG_LEVEL

def configure_logging():
    """Configure logging for the application."""
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    root_logger.addHandler(console_handler)
    
    # Create loggers for specific components
    for name in ["router", "guidelines", "app_info", "post_examples", "agent"]:
        logger = logging.getLogger(f"content_planner_agent.{name}")
        logger.setLevel(log_level) 