#!/usr/bin/env python3
"""
Run script for the AI Docs Generator Streamlit application.

This script provides a simple way to run the Streamlit app with the correct
configuration and environment variables.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Run the Streamlit application."""
    print("Starting AI Docs Generator...")
    
    # Get Streamlit server port from environment or use default
    port = os.environ.get("STREAMLIT_SERVER_PORT", "8501")
    
    # Check for required environment variables
    missing_vars = []
    required_vars = ["GROQ_API_KEY", "GITHUB_TOKEN"]
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: The following required environment variables are not set: {', '.join(missing_vars)}")
        print("The application may not function correctly without them.")
        print("Please create a .env file with these variables or set them in your environment.")
        
        # Ask user if they want to continue
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting.")
            sys.exit(1)
    
    # Run Streamlit
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", port,
        "--browser.serverAddress", "localhost",
        "--server.headless", "false",
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping AI Docs Generator...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 