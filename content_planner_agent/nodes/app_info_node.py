"""
App info node for the Content Planner Agent graph.
"""
import logging
import json
from langchain_core.messages import HumanMessage, AIMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_app_info_llm
from content_planner_agent.config.app_info import APP_INFO

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the LLM
app_info_llm = initialize_app_info_llm()

def process_app_info(state: ContentPlannerState) -> ContentPlannerState:
    """
    Process user questions about the application.
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with the agent's response
    """
    logger.info("Processing input in app_info node")
    
    # Get the last message (which should be from the user)
    last_message = state["messages"][-1]
    message_content = last_message.content
    
    # Prepare messages for the model
    messages = state["messages"].copy()
    
    # Add app info context to the message
    message_with_context = HumanMessage(
        content=f"""
Question: {message_content}

Application Information:
{json.dumps(APP_INFO, indent=2)}

Please answer the question based on the provided application information.
"""
    )
    
    # Replace the last message with the one containing context
    messages[-1] = message_with_context
    
    # Get response from the model
    logger.info("Calling LLM for app info response")
    response = app_info_llm.invoke(messages)
    
    # Handle response content which could be a string or AIMessage
    if hasattr(response, 'content'):
        content = response.content
    else:
        # If response is the message itself
        content = str(response)
    
    # Ensure we're dealing with a string
    if isinstance(content, list):
        # If content is a list (of messages), check if it's empty
        if len(content) > 0:
            content_str = str(content[0].content)
        else:
            # Handle empty list case
            logger.warning("Received empty list as response content")
            content_str = "I'm sorry, I don't have specific information about this app."
    else:
        # If content is already a string
        content_str = str(content)
    
    # Create AI message response
    ai_message = AIMessage(content=content_str)
    
    # Return the updated state with ONLY the AI message
    # This ensures we don't accumulate messages between nodes
    logger.info(f"App info response generated: {len(content_str)} chars")
    
    return {
        "messages": [ai_message],
        "guideline_draft": state.get("guideline_draft", ""),
        "current_task": "app_info",  # Keep the current task
        "posts_examples": state.get("posts_examples", []),
        "app_context": APP_INFO
    } 