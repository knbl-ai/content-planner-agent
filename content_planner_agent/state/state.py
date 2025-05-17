"""
State definitions for the Content Planner Agent.
"""
from typing import Dict, List, Any, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class ContentPlannerState(TypedDict):
    """State for the Content Planner Agent."""
    messages: Annotated[List[BaseMessage], operator.add]
    guideline_draft: str
    current_task: str  # "guidelines", "app_info", "post_examples"
    posts_examples: List[str]
    app_context: Dict[str, Any] 