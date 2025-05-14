"""
API routes for the Content Planner Agent.
"""
from flask import Blueprint, request, jsonify
from content_planner_agent.agent import ContentPlannerAgent

# Create a Flask Blueprint for the API routes
api_bp = Blueprint('api', __name__)

# Initialize the agent
agent = ContentPlannerAgent()

@api_bp.route('/message', methods=['POST', 'OPTIONS'])
def process_message():
    """
    Process a message from the user.
    
    Expected JSON payload:
    {
        "message": "User message text",
        "session_id": "unique-session-identifier"
    }
    
    Returns:
        JSON response with the agent's reply
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    
    if not data or 'message' not in data or 'session_id' not in data:
        return jsonify({
            'error': 'Invalid request. Must include "message" and "session_id".'
        }), 400
    
    message = data['message']
    session_id = data['session_id']
    
    # Process the message with the agent
    response = agent.process_message(message, session_id)
    
    return jsonify({
        'response': response,
        'session_id': session_id
    })

# Add a /chat route that's equivalent to /message for backward compatibility
@api_bp.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Alias for process_message to maintain compatibility with existing clients.
    """
    return process_message()

@api_bp.route('/guideline', methods=['POST', 'OPTIONS'])
def save_guideline():
    """
    Save a finalized guideline.
    
    Expected JSON payload:
    {
        "guideline": "Guideline text content",
        "session_id": "unique-session-identifier"
    }
    
    Returns:
        JSON response indicating success or failure
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    
    if not data or 'guideline' not in data or 'session_id' not in data:
        return jsonify({
            'error': 'Invalid request. Must include "guideline" and "session_id".'
        }), 400
    
    guideline = data['guideline']
    session_id = data['session_id']
    
    # Save the guideline
    success = agent.save_guideline(guideline, session_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Guideline saved successfully.',
            'session_id': session_id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to save guideline.',
            'session_id': session_id
        }), 500

@api_bp.route('/guideline/<session_id>', methods=['GET', 'OPTIONS'])
def get_guideline(session_id):
    """
    Get a saved guideline.
    
    Args:
        session_id: The session ID in the URL path
    
    Returns:
        JSON response with the guideline content
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 200
        
    guideline = agent.get_guideline(session_id)
    
    if guideline:
        return jsonify({
            'guideline': guideline,
            'session_id': session_id
        })
    else:
        return jsonify({
            'error': 'Guideline not found.',
            'session_id': session_id
        }), 404 