"""
Content Planner Agent implementation using LangGraph.
"""
from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.nodes.process_node import process_input
from content_planner_agent.db.database import DatabaseManager

class ContentPlannerAgent:
    """
    Agent that helps users create content guidelines for social media posting.
    Uses LangGraph to maintain conversation state and memory.
    """
    
    def __init__(self):
        """Initialize the Content Planner Agent."""
        # Set up memory for conversation history
        self.memory = MemorySaver()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            The compiled StateGraph
        """
        # Create the graph builder
        builder = StateGraph(ContentPlannerState)
        
        # Add the process node to the graph
        builder.add_node("process", process_input)
        
        # Add edges
        builder.add_edge("process", END)
        builder.set_entry_point("process")
        
        # Compile the graph with memory
        return builder.compile(checkpointer=self.memory)
    
    def process_message(self, message: str, session_id: str) -> str:
        """
        Process a message from the user and return the agent's response.
        
        Args:
            message: The user's message
            session_id: A unique identifier for the conversation session
            
        Returns:
            The agent's response
        """
        # Create config with session ID for memory persistence
        config = {"configurable": {"thread_id": session_id}}
        
        # Try to get the current draft from the database
        guideline_draft = self.db_manager.get_session_state(session_id) or self._get_current_draft(session_id)
        
        # Create the input state
        input_state = {
            "messages": [HumanMessage(content=message)],
            "guideline_draft": guideline_draft
        }
        
        # Invoke the graph
        result = self.graph.invoke(input_state, config)
        
        # Save the updated guideline draft to the database
        self.db_manager.save_session_state(session_id, result["guideline_draft"])
        
        # Return the agent's response
        return result["messages"][-1].content
    
    def _get_current_draft(self, session_id: str) -> str:
        """
        Get the current guideline draft for a session from memory.
        
        Args:
            session_id: The session ID
            
        Returns:
            The current guideline draft
        """
        # Try to get the draft from the last checkpoint
        try:
            # Get the last checkpoint for this session
            checkpoints = self.memory.list({"configurable": {"thread_id": session_id}})
            if checkpoints:
                last_checkpoint = self.memory.get(checkpoints[-1])
                return last_checkpoint.get("guideline_draft", "")
        except Exception:
            # If there's an error, start with an empty draft
            pass
        
        return ""
    
    def save_guideline(self, guideline: str, session_id: str) -> bool:
        """
        Save the final guideline to the database.
        
        Args:
            guideline: The final guideline text
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        return self.db_manager.save_guideline(session_id, guideline)
    
    def get_guideline(self, session_id: str) -> str:
        """
        Get a saved guideline from the database.
        
        Args:
            session_id: The session ID
            
        Returns:
            The guideline text, or an empty string if not found
        """
        return self.db_manager.get_guideline(session_id) or "" 