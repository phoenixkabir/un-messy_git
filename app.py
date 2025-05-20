__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

"""
AI Docs Generator - Main application entry point.

This script runs the Streamlit app for generating documentation from GitHub repositories.
Compatible with Python 3.9.1.
"""
import os
from dotenv import load_dotenv
from app.main import main

# Load environment variables
load_dotenv()

# Run the application
if __name__ == "__main__":
    main() 