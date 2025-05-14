"""
Node functions for the Content Planner Agent graph.
"""
from langchain_core.messages import HumanMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_llm
from content_planner_agent.utils.extractors import extract_guideline_updates

# Initialize the LLM
llm_with_prompt = initialize_llm()

def process_input(state: ContentPlannerState) -> ContentPlannerState:
    """
    Process user input and generate a response.
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with the agent's response and updated guideline draft
    """
    # Get the last message (which should be from the user)
    last_message = state["messages"][-1]
    
    # Get the current guideline draft
    current_draft = state.get("guideline_draft", "")
    
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
                break
    
    # Get response from the model
    response = llm_with_prompt.invoke(messages)
    
    # Extract any updates to the guideline from the response
    updated_draft = extract_guideline_updates(response.content, current_draft)
    
    # Return the updated state
    return {
        "messages": [response],
        "guideline_draft": updated_draft
    } 