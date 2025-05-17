"""
Guidelines node for the Content Planner Agent graph.
"""
import logging
from langchain_core.messages import HumanMessage, AIMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_guidelines_llm
from content_planner_agent.utils.extractors import extract_guideline_updates

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the LLM
llm_with_prompt = initialize_guidelines_llm()

def process_guidelines(state: ContentPlannerState) -> ContentPlannerState:
    """
    Process user input for guidelines creation and generate a response.
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with the agent's response and updated guideline draft
    """
    logger.info("Processing input in guidelines node")
    
    # Get the last message (which should be from the user)
    last_message = state["messages"][-1]
    
    # Get the current guideline draft
    current_draft = state.get("guideline_draft", "")
    
    logger.info(f"Current draft length: {len(current_draft)} characters")
    
    # Create context with the current draft
    context = f"Current guideline draft:\n{current_draft}\n\n"
    
    # Prepare messages for the model
    messages = state["messages"].copy()
    
    # If we have a draft, include it in the context
    if current_draft:
        # Find the last human message and update it with context
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                content = context + messages[i].content
                messages[i] = HumanMessage(content=content)
                logger.info("Added guideline draft context to user message")
                break
    
    # Get response from the model
    logger.info("Calling LLM for guidelines response")
    response = llm_with_prompt.invoke(messages)
    
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
            content_str = "Let me help you create effective content guidelines."
    else:
        # If content is already a string
        content_str = str(content)
    
    # Extract any updates to the guideline from the response
    updated_draft = extract_guideline_updates(content_str, current_draft)
    
    if updated_draft != current_draft:
        logger.info("Guideline draft was updated")
    else:
        logger.info("No changes to guideline draft")
    
    # Create AI message response
    ai_message = AIMessage(content=content_str)
    
    # Return the updated state
    return {
        "messages": [ai_message],
        "guideline_draft": updated_draft,
        "current_task": "guidelines",
        "posts_examples": state.get("posts_examples", []),
        "app_context": state.get("app_context", {})
    } 