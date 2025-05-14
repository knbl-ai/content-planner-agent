"""
Simple script to test the Content Planner Agent API.
"""
import requests
import json
import uuid

# Generate a unique session ID
session_id = str(uuid.uuid4())
print(f"Using session ID: {session_id}")

# API endpoint
base_url = "http://localhost:5000/api"

# Test the chat endpoint
def test_chat():
    print("\n=== Testing /chat endpoint ===")
    
    # Send a message to the agent
    response = requests.post(
        f"{base_url}/chat",
        json={
            "message": "Hi, I need help creating content guidelines for my tech blog.",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response: {data['response'][:100]}...")  # Show first 100 chars
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Test the message endpoint (should be equivalent to chat)
def test_message():
    print("\n=== Testing /message endpoint ===")
    
    # Send a message to the agent
    response = requests.post(
        f"{base_url}/message",
        json={
            "message": "We focus on AI and machine learning topics.",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Response: {data['response'][:100]}...")  # Show first 100 chars
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Test saving a guideline
def test_save_guideline():
    print("\n=== Testing /guideline (POST) endpoint ===")
    
    # Save a guideline
    response = requests.post(
        f"{base_url}/guideline",
        json={
            "guideline": "# Tech Blog Content Guidelines\n\n## Topics\n- AI and ML\n- Web Development\n- Data Science",
            "session_id": session_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Test retrieving a guideline
def test_get_guideline():
    print("\n=== Testing /guideline/{session_id} (GET) endpoint ===")
    
    # Get the guideline
    response = requests.get(f"{base_url}/guideline/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Guideline: {data.get('guideline')[:100]}...")  # Show first 100 chars
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_chat()
    test_message()
    test_save_guideline()
    test_get_guideline() 