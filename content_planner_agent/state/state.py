"""
State definitions for the Content Planner Agent.
"""
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class ContentPlannerState(TypedDict):
    """State for the content planner agent."""
    messages: Annotated[List, add_messages]
    guideline_draft: str 