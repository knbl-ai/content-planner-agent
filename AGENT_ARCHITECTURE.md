# Content Planner Agent Architecture

This document provides a detailed explanation of the Content Planner Agent's architecture, focusing on how the LangGraph-based agent works under the hood. This is intended as a learning resource for developers who want to understand how to build similar agents.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [State Management](#state-management)
4. [Graph Structure](#graph-structure)
5. [Memory and Persistence](#memory-and-persistence)
6. [Prompt Engineering](#prompt-engineering)
7. [Guideline Extraction](#guideline-extraction)
8. [Implementation Details](#implementation-details)
9. [Building Your Own Agent](#building-your-own-agent)

## Overview

The Content Planner Agent is built using LangGraph, a framework for creating stateful, graph-based AI agents. The agent helps users create content guidelines for social media posting through natural language conversation. It maintains state across conversation turns, extracts and updates content guidelines, and provides a way to save the final result.

At its core, the agent is a state machine that:
1. Processes user input
2. Updates an internal state (including conversation history and guideline draft)
3. Generates appropriate responses
4. Extracts guideline updates from those responses

## Core Components

The agent consists of several key components:

### 1. ContentPlannerAgent Class

This is the main class that orchestrates the agent's behavior. It:
- Initializes the language model
- Sets up the system prompt
- Builds the graph structure
- Provides methods for processing messages and saving guidelines

```python
class ContentPlannerAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Set up system prompt
        self.system_prompt = "..."
        
        # Initialize model with system prompt
        self.llm_with_prompt = self.llm.bind(system=self.system_prompt)
        
        # Set up memory
        self.memory = MemorySaver()
        
        # Build graph
        self.graph = self._build_graph()
        
        # In-memory storage for saved guidelines
        self.saved_guidelines = {}
```

### 2. ContentPlannerState TypedDict

This defines the structure of the state that flows through the graph:

```python
class ContentPlannerState(TypedDict):
    """State for the content planner agent."""
    messages: Annotated[List, add_messages]  # Conversation history
    guideline_draft: str  # Current guideline draft
```

The `Annotated[List, add_messages]` syntax is important - it tells LangGraph to use the `add_messages` function as a reducer for the messages field, which appends new messages instead of replacing the entire list.

### 3. Language Model (LLM)

We use the Claude model from Anthropic, specifically `claude-3-sonnet-20240229`. The model is initialized with:
- A temperature of 0.7 (balancing creativity and determinism)
- The API key from environment variables
- A system prompt that guides the model's behavior

### 4. System Prompt

The system prompt is crucial as it defines the agent's personality, goals, and behavior:

```python
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
```

### 5. Memory System

The `MemorySaver` from LangGraph provides in-memory persistence for conversation state, allowing the agent to remember previous interactions within a session.

## State Management

State management is a critical part of the agent. The state contains:

1. **messages**: The conversation history between the user and the agent
2. **guideline_draft**: The current draft of the content guideline being developed

The state flows through the graph and is updated at each step. The `add_messages` reducer ensures that new messages are appended to the existing ones rather than replacing them.

## Graph Structure

The agent uses a simple graph structure with a single processing node:

```python
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
```

Let's break down the graph structure:

1. We create a `StateGraph` with our `ContentPlannerState` schema
2. We define a `process_input` function that:
   - Takes the current state
   - Extracts the last message (from the user)
   - Gets the current guideline draft
   - Prepares context for the model by including the current draft
   - Invokes the LLM with the messages
   - Extracts guideline updates from the response
   - Returns an updated state with the new response and updated guideline
3. We add this function as a node named "process"
4. We add an edge from this node to the END node (terminating the graph execution)
5. We set this node as the entry point
6. We compile the graph with our memory checkpointer

This creates a simple linear workflow: User input → Process → Response → End

## Memory and Persistence

The agent uses LangGraph's `MemorySaver` for in-memory persistence:

```python
self.memory = MemorySaver()
```

This allows the agent to remember the conversation history and guideline draft across multiple interactions within a session. When processing a message, we retrieve the current draft using the session ID:

```python
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
```

When invoking the graph, we pass the session ID as part of the configuration:

```python
config = {"configurable": {"thread_id": session_id}}
result = self.graph.invoke(input_state, config)
```

This ensures that each session has its own independent state.

## Prompt Engineering

The system prompt is carefully designed to guide the model's behavior. Key aspects include:

1. **Role definition**: The model is instructed to be a helpful assistant specialized in content guidelines
2. **Goal setting**: Clear goals are provided (understanding brand voice, suggesting themes, etc.)
3. **Format instructions**: The model is told to use a specific format for guideline updates
4. **Markdown formatting**: Instructions for using markdown to structure responses
5. **Tone guidance**: The model is told to be concise and focus on actionable guidelines

This prompt engineering ensures that the model generates responses that are helpful, structured, and contain the necessary guideline updates.

## Guideline Extraction

A key part of the agent is extracting guideline updates from the model's responses. This is done using regex pattern matching:

```python
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
```

This function:
1. Looks for content between "GUIDELINE UPDATE:" and "END GUIDELINE UPDATE" markers
2. If found, extracts the latest update and appends it to the current draft
3. If no explicit update is found and there's no current draft, tries to extract potential guideline content from the response
4. Otherwise, returns the current draft unchanged

## Implementation Details

### Processing Messages

The `process_message` method is the main entry point for the agent:

```python
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
```

This method:
1. Creates a configuration with the session ID
2. Creates an input state with the user's message and the current guideline draft
3. Invokes the graph with this state and configuration
4. Returns the agent's response

### Saving Guidelines

The `save_guideline` method allows saving the final guideline:

```python
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
```

In the current implementation, this simply stores the guideline in an in-memory dictionary. In a production system, this would save to a database.

## Building Your Own Agent

To build a similar agent, follow these steps:

1. **Define your state schema**:
   ```python
   class YourAgentState(TypedDict):
       messages: Annotated[List, add_messages]
       # Add other state fields as needed
   ```

2. **Initialize the language model**:
   ```python
   llm = ChatAnthropic(
       model="claude-3-sonnet-20240229",
       temperature=0.7,
       anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
   )
   ```

3. **Create a system prompt**:
   ```python
   system_prompt = """
   Detailed instructions for the model...
   """
   llm_with_prompt = llm.bind(system=system_prompt)
   ```

4. **Set up memory**:
   ```python
   memory = MemorySaver()
   ```

5. **Build your graph**:
   ```python
   builder = StateGraph(YourAgentState)
   
   # Define your processing function
   def process(state: YourAgentState):
       # Process the state and return updates
       return updated_state
   
   # Add nodes and edges
   builder.add_node("process", process)
   builder.add_edge("process", END)
   builder.set_entry_point("process")
   
   # Compile the graph
   graph = builder.compile(checkpointer=memory)
   ```

6. **Create a method to process messages**:
   ```python
   def process_message(self, message: str, session_id: str):
       config = {"configurable": {"thread_id": session_id}}
       input_state = {...}
       result = self.graph.invoke(input_state, config)
       return result
   ```

7. **Add any additional utility methods** specific to your agent's functionality

By following this pattern, you can create agents for various purposes beyond content planning, such as:
- Customer support agents
- Research assistants
- Writing coaches
- Data analysis helpers
- And more!

The key is to define the right state schema, create an appropriate system prompt, and build a graph structure that handles the specific workflow you need.

## Conclusion

The Content Planner Agent demonstrates how to build a stateful, conversational agent using LangGraph. By understanding its architecture, you can create your own agents for different use cases.

The most important aspects to focus on are:
1. State management (defining what information needs to persist)
2. Prompt engineering (guiding the model's behavior)
3. Graph structure (defining the flow of information)
4. Memory persistence (ensuring continuity across interactions)

With these fundamentals in place, you can build sophisticated agents that maintain context, follow complex workflows, and provide valuable assistance to users. 