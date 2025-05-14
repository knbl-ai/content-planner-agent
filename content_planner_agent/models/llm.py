"""
LLM initialization and configuration.
"""
from langchain_anthropic import ChatAnthropic
from content_planner_agent.config.settings import MODEL_NAME, TEMPERATURE, ANTHROPIC_API_KEY, SYSTEM_PROMPT

def initialize_llm():
    """
    Initialize the language model with the appropriate configuration.
    
    Returns:
        A configured ChatAnthropic instance
    """
    # Initialize the LLM
    llm = ChatAnthropic(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        anthropic_api_key=ANTHROPIC_API_KEY
    )
    
    # Bind the system prompt
    llm_with_prompt = llm.bind(system=SYSTEM_PROMPT)
    
    return llm_with_prompt 