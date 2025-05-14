# Content Planner Agent

A LangGraph-based agent that helps users create content guidelines for social media posting.

## Project Structure

```
content_planner_agent/
├── api/                 # API-related code
│   ├── app.py           # Flask application
│   └── routes.py        # API endpoints
├── config/              # Configuration settings
│   └── settings.py      # Environment variables and constants
├── db/                  # Database interaction
│   └── database.py      # MongoDB interface
├── models/              # LLM models
│   └── llm.py           # LLM initialization
├── nodes/               # Graph nodes
│   └── process_node.py  # Processing node for the graph
├── state/               # State definitions
│   └── state.py         # State TypedDict for the graph
├── utils/               # Utility functions
│   └── extractors.py    # Functions for extracting data from responses
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
   pip install -e .
   ```

3. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DB_CONNECTION_STRING=your_mongodb_connection_string
   ```

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

## Future Enhancements

- Additional graph nodes for specialized processing
- Integration with more LLM providers
- Enhanced error handling and logging
- User authentication and authorization
- Improved database schema and indexing
