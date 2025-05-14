from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import our agent
from app.api.agent import ContentPlannerAgent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the agent
agent = ContentPlannerAgent()

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint to chat with the content planner agent
    """
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', 'default_session')
    
    # Process the message through our agent
    response = agent.process_message(user_input, session_id)
    
    return jsonify({
        'response': response,
        'session_id': session_id
    })

@app.route('/api/save', methods=['POST'])
def save_guideline():
    """
    Endpoint to save the final content guideline
    """
    data = request.json
    guideline = data.get('guideline', '')
    session_id = data.get('session_id', 'default_session')
    
    # Mock saving the guideline (will be implemented with DB in future phases)
    success = agent.save_guideline(guideline, session_id)
    
    return jsonify({
        'success': success,
        'message': 'Guideline saved successfully' if success else 'Failed to save guideline'
    })

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=5000) 