"""
Repository input section UI component.
"""
import streamlit as st
import re
from typing import Optional


def validate_github_url(url: str) -> bool:
    """
    Validate a GitHub repository URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check if URL is empty
    if not url:
        return False
    
    # Check if URL matches GitHub pattern
    github_pattern = r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+"
    return bool(re.match(github_pattern, url))


def repo_input_section() -> Optional[str]:
    """
    Display the repository input section.
    
    Returns:
        Repository URL if entered and valid, None otherwise
    """
    st.subheader("GitHub Repository")
    
    # Option to input GitHub URL
    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        help="Enter the URL of a public GitHub repository"
    )
    
    # Option to upload ZIP file
    st.text("OR")
    uploaded_file = st.file_uploader(
        "Upload Repository ZIP",
        type=["zip"],
        help="Upload a ZIP file containing the repository"
    )
    
    # Display additional options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            branch = st.text_input(
                "Branch",
                placeholder="main",
                help="Specify a branch (defaults to the repository's default branch)"
            )
        
        with col2:
            max_files = st.number_input(
                "Max Files",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                help="Maximum number of files to process"
            )
        
        ignore_patterns = st.text_area(
            "Ignore Patterns",
            placeholder=".git/*\nnode_modules/*\n*.min.js",
            help="Enter glob patterns to ignore, one per line"
        )
        
        if ignore_patterns:
            st.session_state.ignore_patterns = ignore_patterns.split('\n')
        else:
            st.session_state.ignore_patterns = None
    
    # Validate input and return URL
    if github_url and validate_github_url(github_url):
        # Store branch in session state if specified
        if branch:
            st.session_state.branch = branch
        else:
            st.session_state.branch = None
        
        # Store max files in session state
        st.session_state.max_files = max_files
        
        # Extract and store repository name for later reference
        match = re.search(r"github\.com/[a-zA-Z0-9_-]+/([a-zA-Z0-9_-]+)", github_url)
        if match:
            st.session_state.repository_name = match.group(1)
        
        return github_url
    elif uploaded_file:
        # Handle uploaded ZIP file
        # For now, we'll just return None as we haven't implemented this functionality yet
        st.warning("ZIP file upload is not yet implemented. Please use a GitHub URL.")
        return None
    else:
        return None 