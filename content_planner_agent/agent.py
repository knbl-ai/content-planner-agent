"""
Content Planner Agent implementation using LangGraph.
"""
import logging
from typing import Dict, List, Any, Literal, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.nodes.router_node import route_message
from content_planner_agent.nodes.guidelines_node import process_guidelines
from content_planner_agent.nodes.app_info_node import process_app_info
from content_planner_agent.nodes.post_examples_node import process_post_examples
from content_planner_agent.utils.logging_config import configure_logging
from content_planner_agent.db.database import DatabaseManager

# Set up logger
logger = logging.getLogger(__name__)

# Debug mode responses
DEBUG_RESPONSES = {
    "router": {
        "guidelines": "guidelines",
        "app_info": "app_info",
        "post_examples": "post_examples"
    },
    "guidelines": "I'll help you create comprehensive content guidelines for your platform.",
    "app_info": "This application is a content planning tool that helps users create and manage social media content strategies.",
    "post_examples": "Here are some example posts based on your guidelines:\n\nPOST EXAMPLE:\nLinkedIn: Just released our new feature for content creators!\nEND POST EXAMPLE"
}

class ContentPlannerAgent:
    """
    Agent that helps users create content guidelines for social media posting.
    Uses LangGraph to maintain conversation state and memory.
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the Content Planner Agent.
        
        Args:
            debug_mode: If True, use predefined responses instead of calling LLMs
        """
        # Configure logging
        configure_logging()
        logger.info("Initializing Content Planner Agent")
        
        # Set debug mode
        self.debug_mode = debug_mode
        if debug_mode:
            logger.info("Running in DEBUG MODE - using predefined responses")
        
        # Set up memory for conversation history
        self.memory = MemorySaver()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("Content Planner Agent initialized")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with multiple specialized nodes.
        
        Returns:
            The compiled StateGraph
        """
        logger.info("Building graph")
        
        # Create the graph builder
        builder = StateGraph(ContentPlannerState)
        
        # Set the entry point
        builder.set_entry_point("router")
        
        # Add nodes to the graph
        builder.add_node("router", route_message)
        builder.add_node("guidelines", process_guidelines)
        builder.add_node("app_info", process_app_info)
        builder.add_node("post_examples", process_post_examples)
        
        logger.info("Added nodes to graph")
        
        # Define the routing function
        def router_function(state: ContentPlannerState) -> Literal["guidelines", "app_info", "post_examples", END]:
            # Get the current task
            current_task = state.get("current_task", "guidelines")
            logger.info(f"Router function called with current task: {current_task}")
            
            # Check if the last message is from AI - if so, end the processing
            if state["messages"] and isinstance(state["messages"][-1], AIMessage):
                logger.info("Last message was from AI, ending processing")
                return END
                
            # If we're in the middle of a conversation, keep routing to the same node
            if current_task in ["guidelines", "app_info", "post_examples"]:
                logger.info(f"Routing to {current_task}")
                return current_task
            else:
                # Default to guidelines
                logger.info(f"Unknown task '{current_task}', defaulting to guidelines")
                return "guidelines"
        
        # Add conditional edges from router to each specialized node
        builder.add_conditional_edges(
            "router",
            router_function,
            {
                "guidelines": "guidelines",
                "app_info": "app_info",
                "post_examples": "post_examples",
                END: END
            }
        )
        
        # Add edges from specialized nodes back to router
        builder.add_edge("guidelines", "router")
        builder.add_edge("app_info", "router")
        builder.add_edge("post_examples", "router")
        
        logger.info("Added conditional edges")
        
        # Compile the graph with memory
        graph = builder.compile(checkpointer=self.memory)
        logger.info("Graph compiled")
        return graph
    
    def process_message(self, message: str, session_id: str) -> str:
        """
        Process a message from the user and return the agent's response.
        
        Args:
            message: The user's message
            session_id: A unique identifier for the conversation session
            
        Returns:
            The agent's response
        """
        logger.info(f"Processing message for session {session_id[:8]}...")
        
        # If in debug mode, use a simplified approach
        if self.debug_mode:
            return self._debug_process_message(message, session_id)
        
        # Create config with session ID for memory persistence
        config = {"configurable": {"thread_id": session_id}}
        
        # Try to get existing state from the database
        existing_state = self.db_manager.get_session_state(session_id) or {}
        
        # Create the input state
        # Using a list for messages to work with our Annotated[List] state definition
        input_state = {
            "messages": [HumanMessage(content=message)],
            "guideline_draft": existing_state.get("guideline_draft", ""),
            "current_task": existing_state.get("current_task", "guidelines"),
            "posts_examples": existing_state.get("posts_examples", []),
            "app_context": existing_state.get("app_context", {})
        }
        
        logger.info(f"Input state created with task: {input_state['current_task']}")
        
        # Invoke the graph
        try:
            logger.info("Invoking graph...")
            result = self.graph.invoke(input_state, config)
            logger.info(f"Graph invocation complete. Current task: {result.get('current_task')}")
        except Exception as e:
            logger.error(f"Error invoking graph: {str(e)}", exc_info=True)
            return f"I'm sorry, I encountered an error: {str(e)}"
        
        # Save the updated state to the database
        self.db_manager.save_session_state(session_id, result)
        logger.info(f"Updated state saved to database for session {session_id[:8]}")
        
        # Return the agent's response
        return result["messages"][-1].content
    
    def _debug_process_message(self, message: str, session_id: str) -> str:
        """
        Process a message in debug mode without calling LLMs.
        
        Args:
            message: The user's message
            session_id: A unique identifier for the conversation session
            
        Returns:
            A predefined response based on detected intent
        """
        logger.info("Processing message in DEBUG MODE")
        
        # Get existing state
        existing_state = self.db_manager.get_session_state(session_id) or {}
        current_task = existing_state.get("current_task", "guidelines")
        
        # Simple intent detection for testing
        message_lower = message.lower()
        if "app" in message_lower or "feature" in message_lower:
            detected_intent = "app_info"
        elif "post" in message_lower or "example" in message_lower:
            detected_intent = "post_examples"
        else:
            detected_intent = "guidelines"
        
        logger.info(f"Debug mode detected intent: {detected_intent}")
        
        # Update state based on intent
        response_content = DEBUG_RESPONSES[detected_intent]
        
        # Create AI message for response
        ai_message = AIMessage(content=response_content)
        
        # Create updated state - making sure messages is a list
        updated_state = {
            "messages": [ai_message],
            "guideline_draft": existing_state.get("guideline_draft", ""),
            "current_task": detected_intent,
            "posts_examples": existing_state.get("posts_examples", []),
            "app_context": existing_state.get("app_context", {})
        }
        
        # Save the updated state
        self.db_manager.save_session_state(session_id, updated_state)
        
        return response_content
        
    def save_guideline(self, guideline: str, session_id: str) -> bool:
        """
        Save the final guideline to the database.
        
        Args:
            guideline: The final guideline text
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving guideline for session {session_id[:8]}")
        return self.db_manager.save_guideline(session_id, guideline)
    
    def get_guideline(self, session_id: str) -> str:
        """
        Get a saved guideline from the database.
        
        Args:
            session_id: The session ID
            
        Returns:
            The guideline text, or an empty string if not found
        """
        logger.info(f"Getting guideline for session {session_id[:8]}")
        return self.db_manager.get_guideline(session_id) or ""
        
    def get_post_examples(self, session_id: str) -> List[str]:
        """
        Get generated post examples for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of post examples, or empty list if none found
        """
        logger.info(f"Getting post examples for session {session_id[:8]}")
        state = self.db_manager.get_session_state(session_id)
        return state.get("posts_examples", []) if state else [] 