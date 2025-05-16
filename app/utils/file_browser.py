"""
File browser utility for displaying and selecting repository files.
"""
import streamlit as st
from typing import List, Dict, Any
import uuid

class FileBrowser:
    """
    Utility class for browsing and selecting files from repositories.
    """
    
    def __init__(self):
        """Initialize the file browser."""
        # Initialize selection tracking
        if "selected_file_paths" not in st.session_state:
            st.session_state.selected_file_paths = []
            
        # Initialize button action flags
        if "select_all_clicked" not in st.session_state:
            st.session_state.select_all_clicked = False
        if "deselect_all_clicked" not in st.session_state:
            st.session_state.deselect_all_clicked = False
    
    def _make_stable_key(self, prefix: str, path: str) -> str:
        """
        Create a stable key for UI elements based on prefix and path.
        Using hash to avoid characters that might cause issues in keys.
        
        Args:
            prefix: Prefix for the key
            path: Path to use for the key
            
        Returns:
            A stable unique key
        """
        # Use hash to create a stable identifier from the path
        # This ensures keys remain consistent between renders
        path_hash = str(hash(path) % 10000000)
        return f"{prefix}_{path_hash}"
    
    def _handle_select_all(self):
        """Handle the 'Select All' button click."""
        st.session_state.select_all_clicked = True
        
    def _handle_deselect_all(self):
        """Handle the 'Deselect All' button click."""
        st.session_state.deselect_all_clicked = True
        st.session_state.selected_file_paths = []
    
    def display_file_browser(self, files: List[Dict[str, Any]], indent_level: int = 0) -> List[str]:
        """
        Display a file browser with checkboxes for selecting files.
        
        Args:
            files: List of file information dictionaries
            indent_level: Level of indentation for display (used for subdirectories)
            
        Returns:
            List of selected file paths
        """
        # Process select all/deselect all logic before rendering any UI
        if indent_level == 0:
            # Reset flags after handling them
            if st.session_state.deselect_all_clicked:
                st.session_state.deselect_all_clicked = False
                # No need to clear selected_file_paths again, already done in handler
                
            code_files = [f for f in files if f.get("type") == "file" and self._is_code_file(f.get("name", ""))]
            if st.session_state.select_all_clicked:
                st.session_state.select_all_clicked = False
                # Pre-select all code files for this render cycle
                for file in code_files:
                    file_path = file.get("path", "")
                    if file_path not in st.session_state.selected_file_paths:
                        st.session_state.selected_file_paths.append(file_path)
        
        # Group files by type
        dirs = [f for f in files if f.get("type") == "dir"]
        code_files = [f for f in files if f.get("type") == "file" and self._is_code_file(f.get("name", ""))]
        other_files = [f for f in files if f.get("type") == "file" and not self._is_code_file(f.get("name", ""))]
        
        # Sort files by name
        dirs.sort(key=lambda x: x.get("name", "").lower())
        code_files.sort(key=lambda x: x.get("name", "").lower())
        other_files.sort(key=lambda x: x.get("name", "").lower())
        
        # Create indentation prefix
        indent = "│  " * indent_level
        
        # Display directories
        if dirs and indent_level == 0:
            st.markdown("##### Directories")
        
        for directory in dirs:
            dir_path = directory.get("path", "")
            dir_name = directory.get('name', '')
            
            # Create a stable key for this directory
            dir_key = self._make_stable_key("dir", dir_path)
            
            # Use indentation in the label to show hierarchy
            dir_label = f"{indent}📁 {dir_name}"
            
            if st.checkbox(dir_label, key=dir_key):
                # Fetch and display subdirectory contents
                repo_info = directory.get("repo_info", {})
                path = directory.get("path", "")
                
                # Import here to avoid circular imports
                from app.github.github_utils import GithubRepositoryFetcher
                
                # Create a new GithubRepositoryFetcher instance
                fetcher = GithubRepositoryFetcher()
                
                try:
                    # Fetch subdirectory contents
                    subdirectory_files = fetcher.fetch_repository_contents(repo_info, path)
                    
                    # Process subdirectory files
                    for item in subdirectory_files:
                        item["full_path"] = item["path"]
                        item["repo_info"] = repo_info
                    
                    # Display subdirectory browser with increased indentation
                    st.markdown(f"**{indent}└─ Contents of {dir_name}:**")
                    
                    # Recursively display subdirectory contents with increased indentation
                    self.display_file_browser(
                        subdirectory_files, 
                        indent_level=indent_level + 1
                    )
                    
                except Exception as e:
                    st.error(f"Error fetching subdirectory: {str(e)}")
        
        # Display code files
        if code_files:
            if indent_level == 0:
                st.markdown("##### Code Files")
            
            for file in code_files:
                file_path = file.get("path", "")
                file_name = file.get('name', '')
                
                # Create a stable key for this file
                file_key = self._make_stable_key("file", file_path)
                
                # Use indentation in the label to show hierarchy
                file_label = f"{indent}📄 {file_name}"
                
                # Check if file is already selected (for initialization of checkbox)
                default_value = file_path in st.session_state.selected_file_paths
                
                # Display checkbox and update selected files based on interaction
                is_selected = st.checkbox(file_label, value=default_value, key=file_key)
                
                # Update our list of selected files
                if is_selected and file_path not in st.session_state.selected_file_paths:
                    st.session_state.selected_file_paths.append(file_path)
                elif not is_selected and file_path in st.session_state.selected_file_paths:
                    st.session_state.selected_file_paths.remove(file_path)
                
                # Display file preview if small enough and at root level
                if file.get("size", 0) < 20000 and indent_level == 0 and is_selected:  
                    preview_key = self._make_stable_key("preview", file_path)
                    with st.expander(f"Preview: {file_name}", expanded=False, key=preview_key):
                        try:
                            # Import here to avoid circular imports
                            from app.github.github_utils import GithubRepositoryFetcher
                            
                            # Create a new GithubRepositoryFetcher instance
                            fetcher = GithubRepositoryFetcher()
                            
                            # Fetch file content
                            content = fetcher.fetch_file_content(file.get("repo_info", {}), file_path)
                            st.code(content, language=self._get_language(file_name))
                        except Exception as e:
                            st.error(f"Error fetching file content: {str(e)}")
        
        # Display other files
        if other_files:
            if indent_level == 0:
                st.markdown("##### Other Files")
            
            for file in other_files:
                file_path = file.get("path", "")
                file_name = file.get('name', '')
                
                # Create a stable key for this file
                file_key = self._make_stable_key("file", file_path)
                
                # Use indentation in the label to show hierarchy
                file_label = f"{indent}📄 {file_name}"
                
                # Check if file is already selected (for initialization of checkbox)
                default_value = file_path in st.session_state.selected_file_paths
                
                # Display checkbox and update selected files based on interaction
                is_selected = st.checkbox(file_label, value=default_value, key=file_key)
                
                # Update our list of selected files
                if is_selected and file_path not in st.session_state.selected_file_paths:
                    st.session_state.selected_file_paths.append(file_path)
                elif not is_selected and file_path in st.session_state.selected_file_paths:
                    st.session_state.selected_file_paths.remove(file_path)
        
        # File selection options - only show at root level
        if files and indent_level == 0:
            st.markdown("---")
            
            # Generate stable keys for buttons
            select_all_key = "select_all_code_files_btn"
            deselect_all_key = "deselect_all_files_btn"
            
            # Select/deselect all buttons on the same row
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "Select All Code Files", 
                    key=select_all_key, 
                    on_click=self._handle_select_all
                )
            
            with col2:
                st.button(
                    "Deselect All", 
                    key=deselect_all_key, 
                    on_click=self._handle_deselect_all
                )
            
            # Display selected files count
            st.markdown(f"**Selected: {len(st.session_state.selected_file_paths)} files**")
        
        # Return the selected files
        return st.session_state.selected_file_paths
    
    def _is_code_file(self, filename: str) -> bool:
        """
        Check if a file is a code file based on its extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if the file is a code file, False otherwise
        """
        code_extensions = [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss", ".java", 
            ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs", ".sh", 
            ".swift", ".kt", ".kts", ".scala", ".dart", ".ex", ".exs", ".erl", ".fs", 
            ".fsx", ".lua", ".pl", ".pm", ".sql", ".r", ".json", ".yml", ".yaml", 
            ".toml", ".md", ".markdown", ".dockerfile", ".vue"
        ]
        
        return any(filename.lower().endswith(ext) for ext in code_extensions)
    
    def _get_language(self, filename: str) -> str:
        """
        Get the language of a file based on its extension for syntax highlighting.
        
        Args:
            filename: Name of the file
            
        Returns:
            Language string for syntax highlighting
        """
        extension_to_language = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".sh": "bash",
            ".swift": "swift",
            ".kt": "kotlin",
            ".kts": "kotlin",
            ".scala": "scala",
            ".dart": "dart",
            ".ex": "elixir",
            ".exs": "elixir",
            ".erl": "erlang",
            ".fs": "fsharp",
            ".fsx": "fsharp",
            ".lua": "lua",
            ".pl": "perl",
            ".pm": "perl",
            ".sql": "sql",
            ".r": "r",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
            ".markdown": "markdown",
            ".dockerfile": "dockerfile",
            ".vue": "vue"
        }
        
        for ext, lang in extension_to_language.items():
            if filename.lower().endswith(ext):
                return lang
        
        return "text" 