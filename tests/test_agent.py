"""
Test script for the Content Planner Agent.
"""
import uuid
from content_planner_agent.agent import ContentPlannerAgent

def main():
    """Run a simple test conversation with the agent."""
    # Initialize the agent
    agent = ContentPlannerAgent()
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    
    # Start a conversation
    messages = [
        "Hi, I need help creating content guidelines for my company's social media.",
        "We're a tech startup focused on AI products for small businesses.",
        "Our target audience is small business owners who want to use AI but don't have technical expertise.",
        "We want to post 3-4 times per week across Twitter, LinkedIn, and Instagram.",
        "What kind of content themes would you recommend?",
        "Those sound good. Can you also suggest a content calendar structure?",
        "Great! Can you summarize all this into a comprehensive guideline?"
    ]
    
    # Process each message
    for message in messages:
        print("\nUser:", message)
        response = agent.process_message(message, session_id)
        print("\nAgent:", response)
    
    # Get the final guideline draft
    print("\n\n--- FINAL GUIDELINE DRAFT ---\n")
    checkpoints = agent.memory.list({"configurable": {"thread_id": session_id}})
    if checkpoints:
        last_checkpoint = agent.memory.get(checkpoints[-1])
        guideline_draft = last_checkpoint.get("guideline_draft", "")
        print(guideline_draft)
    
    # Save the guideline
    success = agent.save_guideline(guideline_draft, session_id)
    print(f"\nGuideline saved: {success}")
    
    # Retrieve the saved guideline
    retrieved_guideline = agent.get_guideline(session_id)
    print("\nRetrieved guideline length:", len(retrieved_guideline))

if __name__ == "__main__":
    main() 