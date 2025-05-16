#!/usr/bin/env python3
"""
AI Docs Generator - Entry point (Simplified)

This script runs the Streamlit app for generating documentation from GitHub repositories.
Compatible with Python 3.9.1.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the Streamlit application."""
    try:
        # Check required environment variables
        required_vars = ["GROQ_API_KEY", "GITHUB_TOKEN"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print("⚠️  WARNING: The following required environment variables are not set:")
            for var in missing_vars:
                print(f"   - {var}")
            
            response = input("Do you want to continue anyway? (y/n): ")
            if response.lower() != "y":
                print("Exiting application.")
                sys.exit(1)
        
        # Run the Streamlit app
        port = os.environ.get("STREAMLIT_SERVER_PORT", "8501")
        print(f"🚀 Starting Streamlit server on port {port}...")
        subprocess.run(
            [
                "streamlit", 
                "run", 
                "app.py", 
                "--server.port", 
                port, 
                "--server.headless", 
                "true"
            ],
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 