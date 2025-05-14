"""
Mock database interface for the Content Planner Agent.
This is a temporary implementation that stores data in memory.
"""
from typing import Dict, Optional

class DatabaseManager:
    """
    Mock database manager that stores data in memory.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        # In-memory storage for guidelines and session states
        self.guidelines = {}
        self.sessions = {}
        print("Using mock database implementation")
    
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
            self.guidelines[session_id] = guideline
            print(f"Saved guideline for session {session_id}")
            return True
        except Exception as e:
            print(f"Error saving guideline: {e}")
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
            return self.guidelines.get(session_id)
        except Exception as e:
            print(f"Error retrieving guideline: {e}")
            return None
    
    def save_session_state(self, session_id: str, guideline_draft: str) -> bool:
        """
        Save the current session state to in-memory storage.
        
        Args:
            session_id: The session ID
            guideline_draft: The current guideline draft
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.sessions[session_id] = guideline_draft
            return True
        except Exception as e:
            print(f"Error saving session state: {e}")
            return False
    
    def get_session_state(self, session_id: str) -> Optional[str]:
        """
        Get the current session state from in-memory storage.
        
        Args:
            session_id: The session ID
            
        Returns:
            The guideline draft, or None if not found
        """
        try:
            return self.sessions.get(session_id)
        except Exception as e:
            print(f"Error retrieving session state: {e}")
            return None 