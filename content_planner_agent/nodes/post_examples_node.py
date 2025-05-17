"""
Post examples node for the Content Planner Agent graph.
"""
import logging
import re
from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_post_examples_llm

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the LLM
post_examples_llm = initialize_post_examples_llm()

def extract_post_examples(content: str) -> List[str]:
    """
    Extract post examples from the LLM response.
    
    Args:
        content: The LLM response content
        
    Returns:
        List of extracted post examples
    """
    pattern = r"POST EXAMPLE:\s*(.*?)\s*END POST EXAMPLE"
    examples = re.findall(pattern, content, re.DOTALL)
    logger.info(f"Extracted {len(examples)} post examples")
    return examples

def process_post_examples(state: ContentPlannerState) -> ContentPlannerState:
    """
    Generate example posts based on content guidelines.
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with the agent's response and post examples
    """
    logger.info("Processing input in post_examples node")
    
    # Get the last message (which should be from the user)
    last_message = state["messages"][-1]
    
    # Get the current guideline draft
    current_draft = state.get("guideline_draft", "")
    
    if not current_draft:
        logger.warning("No guideline draft available for post examples")
        response_content = "I don't have any content guidelines to base examples on. Let's create some guidelines first."
        ai_message = AIMessage(content=response_content)
        return {
            "messages": [ai_message],
            "guideline_draft": "",
            "current_task": "post_examples",
            "posts_examples": state.get("posts_examples", []),
            "app_context": state.get("app_context", {})
        }
    
    # Create context with the current draft
    context = f"Generate post examples based on these content guidelines:\n{current_draft}\n\n"
    
    # Prepare messages for the model
    messages = state["messages"].copy()
    
    # Add guideline context to the last human message
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            content = context + messages[i].content
            messages[i] = HumanMessage(content=content)
            logger.info("Added guideline context to user message")
            break
    
    # Get response from the model
    logger.info("Calling LLM for post examples generation")
    response = post_examples_llm.invoke(messages)
    
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
            content_str = "Here are some example posts based on your guidelines."
    else:
        # If content is already a string
        content_str = str(content)
    
    # Extract post examples
    new_examples = extract_post_examples(content_str)
    
    # Get existing examples
    existing_examples = state.get("posts_examples", [])
    
    # Combine examples (adding only new ones)
    all_examples = existing_examples.copy()
    for example in new_examples:
        if example not in all_examples:
            all_examples.append(example)
    
    logger.info(f"Added {len(new_examples)} new post examples, total: {len(all_examples)}")
    
    # Create AI message response
    ai_message = AIMessage(content=content_str)
    
    # Return the updated state
    return {
        "messages": [ai_message],
        "guideline_draft": current_draft,
        "current_task": "post_examples",
        "posts_examples": all_examples,
        "app_context": state.get("app_context", {})
    } 