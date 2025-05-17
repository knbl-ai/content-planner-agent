"""
Router node for the Content Planner Agent graph.
"""
import logging
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_router_llm

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the router LLM
router_llm = initialize_router_llm()

def route_message(state: ContentPlannerState) -> ContentPlannerState:
    """
    Determine user intent and update the current task in the state.
    
    Args:
        state: Current state of the conversation
        
    Returns:
        Updated state with current_task set based on intent
    """
    # Get the last message from the user
    last_message = state["messages"][-1]
    
    # Check if the last message is from AI - if so, we should end the processing loop
    if isinstance(last_message, AIMessage):
        logger.info("Last message was from AI, maintaining current task without routing")
        # Return the state as-is to avoid re-routing AI responses
        return state
    
    message_content = last_message.content
    
    logger.info(f"Routing message: '{message_content[:50]}...'")
    
    # Use the router LLM to classify the intent
    response = router_llm.invoke([last_message])
    
    # Handle response content which could be a string or AIMessage
    if hasattr(response, 'content'):
        intent_content = response.content
    else:
        # If response is the message itself
        intent_content = str(response)
    
    # Ensure we're dealing with a string
    if isinstance(intent_content, list):
        # If content is a list (of messages), check if it's empty
        if len(intent_content) > 0:
            intent = str(intent_content[0].content).strip().lower()
        else:
            # Handle empty list case
            logger.warning("Received empty list as response content")
            intent = "guidelines"  # Default to guidelines as fallback
    else:
        # If content is already a string
        intent = str(intent_content).strip().lower()
    
    logger.info(f"Router detected intent: '{intent}'")
    
    # Determine the task based on intent
    if "guidelines" in intent:
        current_task = "guidelines"
        logger.info("Setting task to guidelines")
    elif "app_info" in intent:
        current_task = "app_info"
        logger.info("Setting task to app_info")
    elif "post_examples" in intent:
        current_task = "post_examples"
        logger.info("Setting task to post_examples")
    else:
        # Default to guidelines if intent is unclear
        current_task = "guidelines"
        logger.info(f"Intent '{intent}' unclear, defaulting to guidelines task")
    
    # Return updated state with current_task
    return {
        "messages": state["messages"],
        "guideline_draft": state.get("guideline_draft", ""),
        "current_task": current_task,
        "posts_examples": state.get("posts_examples", []),
        "app_context": state.get("app_context", {})
    } 