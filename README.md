# Content Planner Agent

A LangGraph-based agent that helps users create content guidelines for social media posting.

## Features

- **Multi-node Architecture**: Uses specialized nodes for different tasks:
  - Content Guidelines Creation
  - Application Information
  - Social Media Post Examples Generation
- **Context-aware Conversations**: Maintains state and context across multiple interactions
- **Task-specific AI Responses**: Uses specialized prompts for different tasks
- **Parallel Execution Support**: Handles concurrent node updates with proper state management

## Project Structure

```
content_planner_agent/
├── api/                 # API-related code
│   ├── app.py           # Flask application
│   └── routes.py        # API endpoints
├── config/              # Configuration settings
│   └── settings.py      # Environment variables and system prompts
├── db/                  # Database interaction
│   └── database.py      # Database interface (in-memory for now)
├── models/              # LLM models
│   └── llm.py           # LLM initialization
├── nodes/               # Graph nodes
│   ├── router_node.py   # Intent detection and routing
│   ├── guidelines_node.py # Guidelines creation node
│   ├── app_info_node.py # App information node
│   └── post_examples_node.py # Post examples generation node
├── state/               # State definitions
│   └── state.py         # State TypedDict for the graph
├── tests/               # Test scripts and utilities
│   ├── test_agent.py    # Comprehensive agent testing
│   ├── test_api.py      # API endpoint testing
│   └── test_agent_simple.py # Simple agent test script
├── utils/               # Utility functions
│   ├── extractors.py    # Functions for extracting data from responses
│   └── logging_config.py # Logging configuration
└── agent.py             # Main agent implementation
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DB_CONNECTION_STRING=your_mongodb_connection_string
   ```

## Development Guidelines

### Cursor Rules

This project uses Cursor Rules to maintain consistent development practices. The rules are located in the `.cursor/rules` directory and include:

1. **Test Organization**: Guidelines for organizing and structuring tests
2. **Agent Architecture**: Best practices for the Content Planner Agent structure
3. **LangGraph Best Practices**: Guidelines for working with LangGraph
4. **Code Style**: Conventions for code formatting and style

These rules are automatically applied when working with the codebase in Cursor IDE.

### Running Tests

All tests are located in the `tests` directory. To run tests:

```
# Run a specific test
python -m tests.test_agent

# Run API tests
python -m tests.test_api

# Run a simple agent test
python -m tests.test_agent_simple
```

## Testing

For testing the agent, refer to [TESTING.md](TESTING.md).

## Usage

Run the application:

```
python main.py
```

The API will be available at `http://localhost:5000`.

### API Endpoints

- `POST /api/message` - Process a message
  ```json
  {
    "message": "Help me create content guidelines for my tech blog",
    "session_id": "unique-session-id"
  }
  ```

- `POST /api/guideline` - Save a finalized guideline
  ```json
  {
    "guideline": "# Content Guidelines for Tech Blog\n\n...",
    "session_id": "unique-session-id"
  }
  ```

- `GET /api/guideline/<session_id>` - Get a saved guideline

- `GET /api/post-examples/<session_id>` - Get generated post examples

## Detailed Architecture

### LangGraph Implementation

The agent uses LangGraph 0.4.3 to orchestrate a multi-node workflow with state management. The core architecture follows these principles:

1. **StateGraph**: The entire agent is built around a `StateGraph` with a defined state type (`ContentPlannerState`).

2. **Node Structure**: 
   - **Router Node**: Entry point that determines user intent and routes to specialized nodes
   - **Specialized Nodes**: Task-specific nodes (guidelines, app_info, post_examples)
   - Each node has a clearly defined responsibility and doesn't interfere with other nodes' tasks

3. **Flow Control**:
   - The router node processes incoming messages and determines intent
   - Conditional edges direct flow to specialized nodes based on the detected intent
   - Each specialized node returns to the router after processing
   - Processing stops when an AI message is detected in the router

4. **Memory Management**:
   - Uses `MemorySaver` for checkpointing conversation state
   - Session-based persistence via database storage

### State Management

The state management is a critical component properly handling concurrent updates:

```python
class ContentPlannerState(TypedDict):
    """State for the Content Planner Agent."""
    messages: Annotated[List[BaseMessage], operator.add]
    guideline_draft: str
    current_task: str  # "guidelines", "app_info", "post_examples"
    posts_examples: List[str]
    app_context: Dict[str, Any]
```

Key aspects:

1. **Annotated Types with Reducers**: 
   - The `messages` field uses `Annotated[List[BaseMessage], operator.add]`
   - This enables proper handling of concurrent updates during parallel execution
   - When multiple nodes update the same list concurrently, the `operator.add` reducer combines them properly

2. **Type Safety**:
   - TypedDict ensures type safety across the graph
   - Each field has a clearly defined type to prevent type errors

### Edge Cases and Solutions

During development, we encountered and solved several edge cases:

1. **Concurrent Graph Updates**:
   - **Problem**: The `INVALID_CONCURRENT_GRAPH_UPDATE` error occurred when multiple nodes tried to update the same state fields during parallel execution
   - **Solution**: Implemented `Annotated[List[BaseMessage], operator.add]` for the messages field to properly handle concurrent updates with a reducer

2. **Message Format Handling**:
   - **Problem**: After implementing the state with reducers, nodes expecting `response.content` to be a string were receiving a list
   - **Solution**: Updated node handlers (router_node.py, app_info_node.py) to properly handle content that could be either a string or a list:
   ```python
   # Handle response content which could be a string or AIMessage
   if hasattr(response, 'content'):
       content = response.content
   else:
       # If response is the message itself
       content = str(response)
   
   # Ensure we're dealing with a string
   if isinstance(content, list):
       # If content is a list (of messages), check if it's empty
       if len(content) > 0:
           content_str = str(content[0].content)
       else:
           # Handle empty list case
           logger.warning("Received empty list as response content")
           content_str = "I'm sorry, I don't have specific information about this."
   else:
       # If content is already a string
       content_str = str(content)
   ```

3. **Loop Prevention**:
   - **Problem**: Risk of infinite loops between nodes
   - **Solution**: Proper loop detection in the router function that checks if the last message is from the AI, ending processing if so:
   ```python
   if state["messages"] and isinstance(state["messages"][-1], AIMessage):
       logger.info("Last message was from AI, ending processing")
       return END
   ```

4. **Session State Persistence**:
   - **Problem**: Maintaining conversation context across API calls
   - **Solution**: Database-backed session management with proper state merging

### Best Practices

When working with this codebase, follow these best practices:

1. **State Handling**:
   - Always use proper reducers (`operator.add`) for list fields that might be updated concurrently
   - When processing state, handle all possible data formats (strings, lists, etc.)

2. **Node Implementation**:
   - Each node should return a complete state object with all required fields
   - Nodes should only update their own relevant fields and preserve others

3. **Error Handling**:
   - Use proper error handling in node functions to prevent graph execution failures
   - Log all errors with sufficient context for debugging

4. **Content Handling**:
   - Always check the type of content returned from LLM calls (string vs list vs message object)
   - Implement proper type conversion and validation

5. **Testing**:
   - Use debug mode for initial testing to avoid excessive API calls
   - Test each node individually before integrating into the graph

## Debug Mode

For testing without making API calls, use debug mode:

```python
agent = ContentPlannerAgent(debug_mode=True)
```

## Future Enhancements

- Additional graph nodes for specialized processing
- Integration with more LLM providers
- Enhanced error handling and logging
- User authentication and authorization
- Improved database schema and indexing
- Dynamic node creation based on context
- Advanced parallelization strategies for complex workflows
