# Content Planner Agent

An intelligent agent that helps users generate content guidelines for automated social media posting. Built with LangGraph, Flask, and React.

## Features

- Natural language conversation with the agent
- Memory persistence across conversation turns
- Iterative content guideline creation
- Save finalized guidelines

## Project Structure

```
content_planner_agent/
├── app/                    # Backend Python code
│   ├── api/                # API endpoints and agent logic
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   ├── components/         # Reusable components
│   ├── static/             # Static assets
│   └── templates/          # HTML templates
├── frontend/               # React frontend
│   ├── public/
│   └── src/
│       ├── components/     # React components
│       ├── App.jsx         # Main React component
│       └── ...
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not in repo)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 14+
- MongoDB (optional, mock DB is used by default)

### Backend Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd content_planner_agent
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv content_planner_env
   source content_planner_env/bin/activate  # On Windows: content_planner_env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB_NAME=content_planner
   FLASK_ENV=development
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Usage

1. Start a conversation with the agent by typing in the chat input
2. The agent will help you create a content guideline through conversation
3. View the current guideline draft by clicking "Show Guideline"
4. Save the finalized guideline by clicking "Save Guideline"

## Future Enhancements

- RAG integration for fetching content best practices
- Web search tool for real-time information
- Structured JSON schema for guidelines
- PostgreSQL or Redis for session storage
- Vector store (FAISS or PGVector) for long-term context

## License

MIT # content-planner-agent
