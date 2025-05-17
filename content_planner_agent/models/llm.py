"""
LLM initialization for the Content Planner Agent.
"""
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from content_planner_agent.config.settings import (
    ANTHROPIC_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    GUIDELINES_PROMPT,
    ROUTER_PROMPT,
    APP_INFO_PROMPT,
    POST_EXAMPLES_PROMPT
)

# Set up logger
logger = logging.getLogger(__name__)

def initialize_llm(system_prompt=None):
    """
    Initialize an LLM with a system prompt.
    
    Args:
        system_prompt (str, optional): System prompt to use. Defaults to GUIDELINES_PROMPT.
        
    Returns:
        A prompt-wrapped LLM
    """
    if system_prompt is None:
        system_prompt = GUIDELINES_PROMPT
        
    logger.info(f"Initializing LLM with system prompt: {system_prompt[:50]}...")
    
    # Create the LLM
    llm = ChatAnthropic(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        anthropic_api_key=ANTHROPIC_API_KEY
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    # Create the prompt-wrapped LLM
    return prompt | llm

def initialize_guidelines_llm():
    """Initialize LLM for guidelines node."""
    logger.info("Initializing guidelines LLM")
    return initialize_llm(GUIDELINES_PROMPT)

def initialize_router_llm():
    """Initialize LLM for router node."""
    logger.info("Initializing router LLM")
    return initialize_llm(ROUTER_PROMPT)

def initialize_app_info_llm():
    """Initialize LLM for app info node."""
    logger.info("Initializing app info LLM")
    return initialize_llm(APP_INFO_PROMPT)

def initialize_post_examples_llm():
    """Initialize LLM for post examples node."""
    logger.info("Initializing post examples LLM")
    return initialize_llm(POST_EXAMPLES_PROMPT) 