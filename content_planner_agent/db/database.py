"""
Database interaction for the Content Planner Agent.
"""
import logging
from typing import Dict, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Handles database interactions for the Content Planner Agent.
    Uses in-memory storage for testing purposes.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        # For testing, we'll use in-memory storage
        self.in_memory_guidelines = {}
        self.in_memory_sessions = {}
        logger.info("Using in-memory storage for testing")
    
    def save_guideline(self, session_id: str, guideline: str) -> bool:
        """
        Save a guideline to in-memory storage.
        
        Args:
            session_id: The session ID
            guideline: The guideline text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.in_memory_guidelines[session_id] = guideline
            logger.info(f"Saved guideline for session {session_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"Error saving guideline: {str(e)}")
            return False
    
    def get_guideline(self, session_id: str) -> Optional[str]:
        """
        Get a guideline from in-memory storage.
        
        Args:
            session_id: The session ID
            
        Returns:
            The guideline text, or None if not found
        """
        try:
            guideline = self.in_memory_guidelines.get(session_id)
            if guideline:
                logger.info(f"Retrieved guideline for session {session_id[:8]}")
            else:
                logger.info(f"No guideline found for session {session_id[:8]}")
            return guideline
        except Exception as e:
            logger.error(f"Error retrieving guideline: {str(e)}")
            return None
    
    def save_session_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save the session state to in-memory storage.
        
        Args:
            session_id: The session ID
            state: The session state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract serializable data from the state
            serializable_state = {
                "guideline_draft": state.get("guideline_draft", ""),
                "current_task": state.get("current_task", "guidelines"),
                "posts_examples": state.get("posts_examples", []),
                "app_context": state.get("app_context", {})
            }
            
            self.in_memory_sessions[session_id] = serializable_state
            logger.info(f"Session state saved for session {session_id[:8]}: task={serializable_state['current_task']}")
            return True
        except Exception as e:
            logger.error(f"Error saving session state: {str(e)}")
            return False
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the session state from in-memory storage.
        
        Args:
            session_id: The session ID
            
        Returns:
            The session state, or None if not found
        """
        try:
            state = self.in_memory_sessions.get(session_id)
            
            if state:
                logger.info(f"Retrieved state for session {session_id[:8]}: task={state.get('current_task', 'unknown')}")
            else:
                logger.info(f"No state found for session {session_id[:8]}")
            return state
        except Exception as e:
            logger.error(f"Error retrieving session state: {str(e)}")
            return None 