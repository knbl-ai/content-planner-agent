import os
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

class Database:
    """
    Utility class for database operations.
    This is a simple implementation that will be expanded in future phases.
    """
    
    def __init__(self):
        """Initialize the database connection."""
        self.client = None
        self.db = None
        
        # In the MVP, we'll mock the database operations
        self.mock_db = {
            "guidelines": {},
            "sessions": {}
        }
        
        # Try to connect to MongoDB if URI is provided
        mongodb_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB_NAME")
        
        if mongodb_uri and db_name:
            try:
                self.client = MongoClient(mongodb_uri)
                self.db = self.client[db_name]
                print(f"Connected to MongoDB: {db_name}")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
                print("Using mock database instead")
    
    def save_guideline(self, guideline: str, session_id: str) -> bool:
        """
        Save a content guideline.
        
        Args:
            guideline: The guideline text
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If we have a real database connection, use it
            if self.db:
                self.db.guidelines.update_one(
                    {"session_id": session_id},
                    {"$set": {"guideline": guideline}},
                    upsert=True
                )
            # Otherwise use the mock database
            else:
                self.mock_db["guidelines"][session_id] = guideline
                
            return True
        except Exception as e:
            print(f"Error saving guideline: {e}")
            return False
    
    def get_guideline(self, session_id: str) -> Optional[str]:
        """
        Get a saved guideline.
        
        Args:
            session_id: The session ID
            
        Returns:
            The guideline text, or None if not found
        """
        try:
            # If we have a real database connection, use it
            if self.db:
                result = self.db.guidelines.find_one({"session_id": session_id})
                return result["guideline"] if result else None
            # Otherwise use the mock database
            else:
                return self.mock_db["guidelines"].get(session_id)
        except Exception as e:
            print(f"Error getting guideline: {e}")
            return None
    
    def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Save session data.
        
        Args:
            session_id: The session ID
            data: The session data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If we have a real database connection, use it
            if self.db:
                self.db.sessions.update_one(
                    {"session_id": session_id},
                    {"$set": data},
                    upsert=True
                )
            # Otherwise use the mock database
            else:
                self.mock_db["sessions"][session_id] = data
                
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: The session ID
            
        Returns:
            The session data, or None if not found
        """
        try:
            # If we have a real database connection, use it
            if self.db:
                result = self.db.sessions.find_one({"session_id": session_id})
                return result if result else None
            # Otherwise use the mock database
            else:
                return self.mock_db["sessions"].get(session_id)
        except Exception as e:
            print(f"Error getting session: {e}")
            return None 