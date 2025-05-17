"""
Test script for the Content Planner Agent in debug mode.
"""
import uuid
import logging
from content_planner_agent.agent import ContentPlannerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

def run_debug_test():
    """Run tests in debug mode to verify routing logic."""
    print("\n===== TESTING CONTENT PLANNER AGENT (DEBUG MODE) =====\n")
    
    # Create agent in debug mode
    agent = ContentPlannerAgent(debug_mode=True)
    session_id = str(uuid.uuid4())
    
    print(f"Created agent with session ID: {session_id[:8]}...\n")
    
    # Test messages for different intents
    test_messages = [
        {
            "intent": "guidelines",
            "message": "I need help creating content guidelines for my tech blog"
        },
        {
            "intent": "app_info",
            "message": "What features does this application have?"
        },
        {
            "intent": "app_info",
            "message": "How do I save my guidelines?"
        },
        {
            "intent": "post_examples",
            "message": "Can you generate some example posts based on my guidelines?"
        },
        {
            "intent": "guidelines",
            "message": "I want to refine my content guidelines"
        }
    ]
    
    # Process each message and check the result
    for i, test in enumerate(test_messages):
        print(f"\n----- Test {i+1}: {test['intent']} intent -----")
        print(f"Message: {test['message']}")
        
        # Process the message
        response = agent.process_message(test["message"], session_id)
        
        # Get the current task from the session state
        state = agent.db_manager.in_memory_sessions.get(session_id, {})
        current_task = state.get("current_task", "unknown")
        
        print(f"Response: {response}")
        print(f"Current task: {current_task}")
        
        # Verify the task matches the expected intent
        if current_task == test["intent"]:
            print(f"✓ Test passed: Task is '{current_task}' as expected")
        else:
            print(f"✗ Test failed: Expected '{test['intent']}' but got '{current_task}'")
    
    print("\n===== ALL TESTS COMPLETED =====")

def test_app_info_functionality():
    """Test the app info functionality with specific questions."""
    print("\n===== TESTING APP INFO FUNCTIONALITY =====\n")
    
    # Create agent in debug mode
    agent = ContentPlannerAgent(debug_mode=True)
    session_id = str(uuid.uuid4())
    
    # List of specific app info questions
    app_info_questions = [
        "What API endpoints are available in this application?",
        "How do I save my guidelines?",
        "What features does the Content Planner have?",
        "Can I generate examples for specific platforms?",
        "What's the basic flow for using this application?"
    ]
    
    for i, question in enumerate(app_info_questions):
        print(f"\n----- App Info Question {i+1} -----")
        print(f"Question: {question}")
        
        # Process the question
        response = agent.process_message(question, session_id)
        
        # Get the current task from the session state
        state = agent.db_manager.in_memory_sessions.get(session_id, {})
        current_task = state.get("current_task", "unknown")
        
        print(f"Response snippet: {response[:100]}...")
        print(f"Current task: {current_task}")
        
        # Verify the task is app_info
        if current_task == "app_info":
            print(f"✓ Task is correctly set to 'app_info'")
        else:
            print(f"✗ Task is incorrectly set to '{current_task}', should be 'app_info'")
    
    print("\n===== APP INFO TESTING COMPLETED =====")

if __name__ == "__main__":
    run_debug_test()
    test_app_info_functionality() 