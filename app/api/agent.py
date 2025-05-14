from typing import Annotated, Dict, List, TypedDict
import os
import re
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Define the state for our graph
class ContentPlannerState(TypedDict):
    """State for the content planner agent."""
    messages: Annotated[List, add_messages]
    guideline_draft: str

class ContentPlannerAgent:
    """
    Agent that helps users create content guidelines for social media posting.
    Uses LangGraph to maintain conversation state and memory.
    """
    
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Set up system prompt for the agent
        self.system_prompt = """
        You are a helpful assistant specialized in creating content guidelines for automated social media posting.
        
        Your goal is to help the user create a comprehensive content guideline by:
        1. Understanding their brand voice, audience, and goals
        2. Suggesting content themes and topics
        3. Recommending posting frequency and best practices
        4. Providing examples of effective posts
        5. Iteratively refining the guideline based on user feedback
        
        As you work with the user, maintain a draft of the content guideline that gets more detailed over time.
        When the user is satisfied with the guideline, they can save the final version.
        
        When you have new information to add to the guideline, include a section in your response like this:
        
        GUIDELINE UPDATE:
        [Your updated guideline content here]
        END GUIDELINE UPDATE
        
        Format your responses using Markdown:
        - Use **bold** for emphasis
        - Use bullet points and numbered lists for structured information
        - Use headings (## and ###) for sections
        - Use code blocks for examples when appropriate
        
        Be concise, helpful, and focus on creating practical, actionable guidelines.
        """
        
        # Initialize the model with the system prompt
        self.llm_with_prompt = self.llm.bind(system=self.system_prompt)
        
        # Set up memory for conversation history
        self.memory = MemorySaver()
        
        # Build the graph
        self.graph = self._build_graph()
        
        # In-memory storage for saved guidelines (mock DB)
        self.saved_guidelines = {}
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create the graph builder
        builder = StateGraph(ContentPlannerState)
        
        # Define the main node that processes messages and updates the guideline
        def process_input(state: ContentPlannerState):
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
            response = self.llm_with_prompt.invoke(messages)
            
            # Extract any updates to the guideline from the response
            updated_draft = self._extract_guideline_updates(response.content, current_draft)
            
            # Return the updated state
            return {
                "messages": [response],
                "guideline_draft": updated_draft
            }
        
        # Add the node to the graph
        builder.add_node("process", process_input)
        
        # Add edges
        builder.add_edge("process", END)
        builder.set_entry_point("process")
        
        # Compile the graph with memory
        return builder.compile(checkpointer=self.memory)
    
    def _extract_guideline_updates(self, response: str, current_draft: str) -> str:
        """
        Extract updates to the guideline from the model's response.
        Looks for content between "GUIDELINE UPDATE:" and "END GUIDELINE UPDATE" markers.
        """
        # If there's no current draft, start with an empty one
        if not current_draft:
            current_draft = ""
        
        # Look for guideline updates in the response
        pattern = r"GUIDELINE UPDATE:(.*?)END GUIDELINE UPDATE"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            # Extract the latest update
            latest_update = matches[-1].strip()
            
            # If we already have a draft, append the new content
            if current_draft:
                return current_draft + "\n\n" + latest_update
            else:
                return latest_update
        
        # If we can't find an explicit update but don't have a draft yet,
        # try to extract something useful from the response
        if not current_draft:
            # Look for any structured content that might be guideline-like
            sections = re.split(r'\n\s*\n', response)
            
            # Filter out very short sections and join the rest
            potential_guideline = "\n\n".join([s for s in sections if len(s.strip()) > 50])
            
            if potential_guideline:
                return potential_guideline
        
        # If no updates found or we already have a draft, return the current draft
        return current_draft
    
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
        
        # Create the input state
        input_state = {
            "messages": [HumanMessage(content=message)],
            "guideline_draft": self._get_current_draft(session_id)
        }
        
        # Invoke the graph
        result = self.graph.invoke(input_state, config)
        
        # Return the agent's response
        return result["messages"][-1].content
    
    def _get_current_draft(self, session_id: str) -> str:
        """
        Get the current guideline draft for a session.
        In a real implementation, this would fetch from a database.
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
        Save the final guideline.
        In a real implementation, this would save to a database.
        
        Args:
            guideline: The final guideline text
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would save to a database
            self.saved_guidelines[session_id] = guideline
            print(f"Saved guideline for session {session_id}")
            return True
        except Exception as e:
            print(f"Error saving guideline: {e}")
            return False 