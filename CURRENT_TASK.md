# Content Planner Agent Expansion Roadmap

## Current Architecture

The Content Planner Agent currently has a simple architecture:
- One state definition (`ContentPlannerState`)
- Single node (`process_input`) that handles all interactions
- One graph that routes all messages through this node
- Single system prompt focused on content guidelines

## Proposed Architecture

To handle multiple functionalities (guidelines creation, app questions, post examples), we'll implement a multi-node architecture with conditional routing.

### 1. Enhanced State Management

Expand the state to include:
- `current_task`: Tracks which functionality the user is currently engaging with (e.g., "guidelines", "app_info", "post_examples")
- `posts_examples`: Store generated post examples
- `app_context`: Store information about the parent application

```python
class ContentPlannerState(TypedDict):
    messages: List[BaseMessage]
    guideline_draft: str
    current_task: str  # "guidelines", "app_info", "post_examples"
    posts_examples: List[str]
    app_context: Dict[str, Any]
```

### 2. Multi-Node Graph Structure

Create specialized nodes for each functionality:

1. **Router Node**
   - Analyzes user input to determine intent
   - Routes to the appropriate specialized node
   - Returns to this node after each interaction

2. **Guidelines Node**
   - Focused on creating and refining content guidelines
   - Uses the existing functionality

3. **App Info Node**
   - Answers questions about the parent application
   - Requires context about the application

4. **Post Examples Node**
   - Generates examples based on existing guidelines
   - References the guideline_draft to ensure consistency

### 3. Conditional Routing Logic

Implement a decision-making function to determine which node to route to:

```python
def router_function(state: ContentPlannerState) -> Literal["guidelines", "app_info", "post_examples", END]:
    """
    Determine which node to route to based on the user's message.
    
    Args:
        state: Current state of the conversation
        
    Returns:
        String indicating the next node to call
    """
    # Get the last message from the user
    last_message = state["messages"][-1]
    message_content = last_message.content.lower()
    
    # Use the router LLM to classify the intent
    intent = router_llm.invoke(
        [SystemMessage(content="Classify the user's intent as one of: guidelines, app_info, post_examples"),
        last_message]
    ).content
    
    # Update the current task based on intent
    if "guideline" in intent:
        return "guidelines"
    elif "app" in intent or "application" in intent:
        return "app_info"
    elif "post" in intent or "example" in intent:
        return "post_examples"
    else:
        # Default to guidelines if intent is unclear
        return "guidelines"
```

Example graph construction:

```python
def _build_graph(self) -> StateGraph:
    """
    Build the LangGraph workflow with multiple nodes.
    
    Returns:
        The compiled StateGraph
    """
    # Create the graph builder
    builder = StateGraph(ContentPlannerState)
    
    # Add nodes to the graph
    builder.add_node("router", route_message)
    builder.add_node("guidelines", process_guidelines)
    builder.add_node("app_info", process_app_info)
    builder.add_node("post_examples", process_post_examples)
    
    # Set router as entry point
    builder.set_entry_point("router")
    
    # Add conditional edges from router
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
    
    # After each specialized node, return to router
    builder.add_edge("guidelines", "router")
    builder.add_edge("app_info", "router")
    builder.add_edge("post_examples", "router")
    
    # Compile the graph with memory
    return builder.compile(checkpointer=self.memory)
```

### 4. Task-Specific System Prompts

Create specialized system prompts for each node:

```python
# Router prompt
ROUTER_PROMPT = """
You are a content planning assistant that can help with:
1. Creating content guidelines for social media
2. Answering questions about the parent application
3. Generating example posts based on content guidelines

Your task is to understand which of these services the user is requesting.
"""

# App info prompt
APP_INFO_PROMPT = """
You are a helpful assistant that provides information about the parent application.
The application is a content planning tool that helps users create and manage content strategies.

Answer questions accurately based on the app's context and functionality.
"""

# Post examples prompt
POST_EXAMPLES_PROMPT = """
You are a social media content creation expert. Your task is to generate example posts
based on the content guidelines the user has developed.

When generating examples:
- Follow the tone, style and themes specified in the guidelines
- Create diverse examples across different platforms
- Make each example authentic and engaging
- Include any relevant hashtags, emojis or formatting
"""
```

## Implementation Steps

### Step 1: Enhance State Definition
- Update `ContentPlannerState` with new fields
- Add utility functions to manage state transitions

### Step 2: Create Specialized Nodes

1. Create `router_node.py`:

```python
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from content_planner_agent.state.state import ContentPlannerState
from content_planner_agent.models.llm import initialize_router_llm

# Initialize router LLM
router_llm = initialize_router_llm()

def route_message(state: ContentPlannerState) -> ContentPlannerState:
    """
    Route user input to the appropriate specialized node.
    
    Args:
        state: Current state including messages and current task
        
    Returns:
        Updated state with routing decision
    """
    # Get the last message (from the user)
    last_message = state["messages"][-1]
    
    # Determine intent using the LLM
    response = router_llm.invoke([last_message])
    
    # Extract and save the detected intent/task
    current_task = state.get("current_task", "guidelines")
    
    # Return updated state with routing decision
    return {
        "messages": state["messages"],
        "guideline_draft": state.get("guideline_draft", ""),
        "current_task": current_task,
        "posts_examples": state.get("posts_examples", []),
        "app_context": state.get("app_context", {})
    }
```

2. Update `process_node.py` to become `guidelines_node.py`
3. Create `app_info_node.py` and `post_examples_node.py`

### Step 3: Define Task-Specific System Prompts
- Add new prompt templates in `settings.py`
- Initialize separate LLM instances for each node

### Step 4: Update Graph Structure
- Implement the multi-node graph in `_build_graph()`
- Add conditional edges for routing between nodes

### Step 5: Enhance API Endpoints
- Update existing endpoints to support the expanded functionality
- Add new endpoints if necessary (e.g., for retrieving post examples)

## First Implementation Step

Begin by implementing the router node and updating the state definition:

1. Update `state.py` with the expanded `ContentPlannerState`:

```python
"""
State definitions for the Content Planner Agent.
"""
from typing import Dict, List, Any, TypedDict
from langchain_core.messages import BaseMessage

class ContentPlannerState(TypedDict):
    """State for the Content Planner Agent."""
    messages: List[BaseMessage]
    guideline_draft: str
    current_task: str  # "guidelines", "app_info", "post_examples"
    posts_examples: List[str]
    app_context: Dict[str, Any]
```

2. Create `router_node.py` with intent classification logic
3. Update `settings.py` with task-specific system prompts
4. Modify `agent.py` to include the new routing logic in the graph

## Future Enhancements

- Add memory for cross-task context (remember discussions from other tasks)
- Implement node-specific memory to specialize in different aspects
- Add a feedback mechanism to improve node routing accuracy
- Support for hybrid tasks (e.g., generating posts while refining guidelines)
- Add visualization of the current task to help users understand context
- Implement fallback mechanisms for unclear intents 