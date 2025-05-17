"""
Application information configuration for the Content Planner Agent.
"""

# Application information used by the App Info node
APP_INFO = {
    "name": "Content Planner",
    "version": "1.0.0",
    "description": "A powerful tool for creating and managing content guidelines for social media posting.",
    
    "features": {
        "guidelines_creation": {
            "name": "Content Guidelines Creation",
            "description": "Create comprehensive content guidelines for your social media strategy.",
            "capabilities": [
                "Brand voice definition",
                "Content theme suggestions",
                "Posting frequency recommendations",
                "Audience targeting guidance"
            ]
        },
        "post_examples": {
            "name": "Post Examples Generation",
            "description": "Generate example posts based on your content guidelines.",
            "capabilities": [
                "Platform-specific content (LinkedIn, Twitter/X, Instagram, etc.)",
                "Different content formats (promotional, educational, engagement)",
                "Customized to match brand voice",
                "Hashtag suggestions"
            ]
        },
        "storage": {
            "name": "Guidelines Storage",
            "description": "Save and retrieve your guidelines for later use.",
            "capabilities": [
                "Persistent storage of guidelines",
                "Retrieval by session ID",
                "Version history (planned feature)"
            ]
        }
    },
    
    "api_endpoints": {
        "message": {
            "path": "/api/message",
            "method": "POST",
            "description": "Process a message from the user",
            "parameters": {
                "message": "The user's message",
                "session_id": "A unique identifier for the conversation session"
            }
        },
        "save_guideline": {
            "path": "/api/guideline",
            "method": "POST",
            "description": "Save a finalized guideline",
            "parameters": {
                "guideline": "The guideline text content",
                "session_id": "A unique identifier for the conversation session"
            }
        },
        "get_guideline": {
            "path": "/api/guideline/<session_id>",
            "method": "GET",
            "description": "Get a saved guideline",
            "parameters": {
                "session_id": "The session ID in the URL path"
            }
        },
        "get_post_examples": {
            "path": "/api/post-examples/<session_id>",
            "method": "GET",
            "description": "Get generated post examples",
            "parameters": {
                "session_id": "The session ID in the URL path"
            }
        }
    },
    
    "faqs": [
        {
            "question": "How do I save my guidelines?",
            "answer": "You can save your guidelines by making a POST request to /api/guideline with your guideline content and session ID."
        },
        {
            "question": "Can I generate examples for specific platforms?",
            "answer": "Yes, you can ask for platform-specific examples like 'Generate LinkedIn post examples' or 'Create Instagram post examples'."
        },
        {
            "question": "How do I start creating guidelines?",
            "answer": "Start by describing your brand, target audience, and content goals. The agent will guide you through the process."
        },
        {
            "question": "Can I retrieve my guidelines later?",
            "answer": "Yes, you can retrieve your guidelines by making a GET request to /api/guideline/<your_session_id>."
        }
    ],
    
    "usage": {
        "basic_flow": [
            "Start a conversation with a session ID",
            "Describe your brand and content needs",
            "Refine the guidelines with the agent's assistance",
            "Save the final guidelines",
            "Generate post examples based on the guidelines"
        ],
        "tips": [
            "Be specific about your brand voice and target audience",
            "Ask for specific examples when needed",
            "You can always return to refining your guidelines after generating examples",
            "Save your session ID to retrieve your guidelines later"
        ]
    }
}


# "iGentity is an app for automating social media content creation.\n\nIt allows users to generate social media content in a semi-automated way. All you need to do is write a clear content guideline, and the app takes care of the rest.\n\niGentity will break down your guideline into specific post ideas, generate matching images, and prepare your posts for automatic publishing.\n\nCurrently, video generation is manual:\nClick on a post in the dashboard below → switch to Video → click the image icon → enter your prompt.\n\niGentity uses state-of-the-art AI models for both image and video generation.\n\nOnce created, your content will be published automatically to selected social platforms.\n\nOn the left side of the chat, you'll find the Settings panel, where you can:\n- Choose the publication dates and times\n- Set the language and text length\n- Toggle manual approval before publishing\n\nOn the right side, you can:\n- Select which platforms to publish to\n- Choose which image and video models you want to use\n\nImage Models:\n- Flux – Ideal for general-purpose content (photorealistic or animated)\n- GPT-Image-1 – Also suitable for general use, but offers more advanced capabilities like infographics, text in images, product shots, and image editing\n\nVideo Models:\n- Kling – Cost-effective, good quality\n- Veo 2 – Top-tier video quality, but higher cost"