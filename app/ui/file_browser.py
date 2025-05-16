"""
File browser UI component.
"""
import streamlit as st
import os
from typing import Dict, Any, List
import re


def group_files_by_directory(files: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Group files by directory.
    
    Args:
        files: Dictionary mapping file paths to file info
        
    Returns:
        Dictionary mapping directories to lists of file paths
    """
    directories = {}
    
    for file_path in files:
        directory = os.path.dirname(file_path)
        if not directory:
            directory = "root"
        
        if directory not in directories:
            directories[directory] = []
        
        directories[directory].append(file_path)
    
    return directories


def determine_file_icon(file_path: str) -> str:
    """
    Determine an icon for a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Icon string
    """
    extension = os.path.splitext(file_path)[1].lower()
    
    # Map extensions to icons
    if extension in ['.py']:
        return "🐍"  # Python
    elif extension in ['.js', '.jsx', '.ts', '.tsx']:
        return "⚛️"  # JavaScript/TypeScript
    elif extension in ['.html', '.htm']:
        return "🌐"  # HTML
    elif extension in ['.css', '.scss', '.sass', '.less']:
        return "🎨"  # CSS
    elif extension in ['.json', '.yaml', '.yml', '.toml', '.xml']:
        return "📋"  # Config files
    elif extension in ['.md', '.txt', '.rst']:
        return "📝"  # Documentation
    elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
        return "🖼️"  # Images
    else:
        return "📄"  # Default file icon


def get_file_language(file_path: str) -> str:
    """
    Get the programming language for a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Programming language
    """
    extension = os.path.splitext(file_path)[1].lower()
    
    # Map extensions to languages
    if extension == '.py':
        return "Python"
    elif extension == '.js':
        return "JavaScript"
    elif extension == '.jsx':
        return "React"
    elif extension == '.ts':
        return "TypeScript"
    elif extension == '.tsx':
        return "TypeScript React"
    elif extension == '.html':
        return "HTML"
    elif extension == '.css':
        return "CSS"
    elif extension == '.md':
        return "Markdown"
    elif extension == '.json':
        return "JSON"
    elif extension == '.yaml' or extension == '.yml':
        return "YAML"
    else:
        return "Plain Text"


def file_browser(repository: Dict[str, Any]) -> List[str]:
    """
    Display a file browser for repository files.
    
    Args:
        repository: Repository information from fetch_repository
        
    Returns:
        List of selected file paths
    """
    st.subheader("File Browser")
    
    if not repository or not repository.get('files'):
        st.warning("No repository data available.")
        return []
    
    # Get repository files
    files = repository['files']
    
    # Group files by directory
    directories = group_files_by_directory(files)
    
    # Sort directories
    sorted_directories = sorted(directories.keys())
    
    # File search
    search_query = st.text_input("Search Files", placeholder="Enter filename or extension")
    
    # Filter files by search query if provided
    if search_query:
        filtered_files = {}
        for dir_name, file_paths in directories.items():
            filtered_paths = [
                path for path in file_paths 
                if search_query.lower() in path.lower()
            ]
            if filtered_paths:
                filtered_files[dir_name] = filtered_paths
        
        directories = filtered_files
        sorted_directories = sorted(directories.keys())
    
    # Display file counts
    total_files = sum(len(files) for files in directories.values())
    st.info(f"Total files: {total_files}")
    
    # File selection options
    col1, col2 = st.columns(2)
    
    with col1:
        select_all = st.button("Select All")
    
    with col2:
        deselect_all = st.button("Deselect All")
    
    # Initialize selected files if not in session state
    if "selected_files" not in st.session_state:
        st.session_state.selected_files = []
    
    # Handle select/deselect actions
    if select_all:
        st.session_state.selected_files = [path for paths in directories.values() for path in paths]
    elif deselect_all:
        st.session_state.selected_files = []
    
    # Display files by directory
    selected_files = []
    
    for directory in sorted_directories:
        # Directory expander
        with st.expander(f"📂 {directory} ({len(directories[directory])} files)", expanded=directory == "root"):
            # Sort files in this directory
            sorted_files = sorted(directories[directory])
            
            # Display files with checkboxes
            for file_path in sorted_files:
                file_name = os.path.basename(file_path)
                icon = determine_file_icon(file_path)
                language = get_file_language(file_path)
                
                # File size in KB
                file_size = files[file_path]['size'] / 1024
                size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                
                # Checkbox label with file info
                label = f"{icon} {file_name} ({language}, {size_str})"
                
                # Checkbox for file selection
                is_selected = st.checkbox(
                    label, 
                    value=file_path in st.session_state.selected_files,
                    key=f"file_{file_path}"
                )
                
                if is_selected:
                    selected_files.append(file_path)
    
    # Update session state
    st.session_state.selected_files = selected_files
    
    # Display selected file count
    if selected_files:
        st.success(f"Selected {len(selected_files)} files")
    else:
        st.warning("No files selected")
    
    return selected_files 