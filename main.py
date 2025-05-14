"""
Main entry point for the Content Planner Agent application.
"""
import argparse
import sys

def main():
    """
    Main function to run the Content Planner Agent application.
    Provides CLI options for different modes of operation.
    """
    parser = argparse.ArgumentParser(description='Content Planner Agent')
    parser.add_argument('--api', action='store_true', help='Run the API server')
    parser.add_argument('--test', action='store_true', help='Run a test conversation')
    
    args = parser.parse_args()
    
    if args.api:
        # Run the API server
        from content_planner_agent.api.app import app
        print("Starting Content Planner Agent API server...")
        print("API will be available at http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    
    elif args.test:
        # Run a test conversation
        print("Running test conversation...")
        import test_agent
        test_agent.main()
    
    else:
        # Show help if no arguments provided
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 