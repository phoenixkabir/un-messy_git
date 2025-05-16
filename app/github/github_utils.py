"""
GitHub repository fetcher utility.
"""
import streamlit as st
import requests
import os
import base64
from typing import Dict, List, Any
from urllib.parse import urlparse

class GithubRepositoryFetcher:
    """
    Utility class for fetching GitHub repositories.
    """
    
    def __init__(self):
        """Initialize the GitHub repository fetcher."""
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.headers = {}
        if self.github_token:
            self.headers = {"Authorization": f"token {self.github_token}"}
    
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """
        Parse a GitHub URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dictionary containing owner and repo name
        """
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        return {
            "owner": path_parts[0],
            "repo": path_parts[1],
            "url": url
        }
    
    def fetch_repository_metadata(self, repo_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Fetch repository metadata from GitHub API.
        
        Args:
            repo_info: Dictionary containing owner and repo name
            
        Returns:
            Repository metadata
        """
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(api_url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repository: {response.status_code} - {response.text}")
        
        repo_data = response.json()
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description", ""),
            "url": repo_data["html_url"],
            "default_branch": repo_data["default_branch"],
            "language": repo_data.get("language", ""),
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "owner": owner,
            "repo": repo
        }
    
    def fetch_repository_contents(self, repo_info: Dict[str, str], path: str = "") -> List[Dict[str, Any]]:
        """
        Fetch repository contents from GitHub API.
        
        Args:
            repo_info: Dictionary containing owner and repo name
            path: Path within the repository to fetch
            
        Returns:
            List of repository contents
        """
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(api_url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repository contents: {response.status_code} - {response.text}")
        
        contents = response.json()
        
        if not isinstance(contents, list):
            # Handle single file response
            contents = [contents]
        
        return contents
    
    def fetch_file_content(self, repo_info: Dict[str, str], path: str) -> str:
        """
        Fetch file content from GitHub API.
        
        Args:
            repo_info: Dictionary containing owner and repo name
            path: Path to the file within the repository
            
        Returns:
            File content
        """
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(api_url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch file content: {response.status_code} - {response.text}")
        
        file_data = response.json()
        
        if file_data.get("type") != "file":
            raise Exception(f"Path does not point to a file: {path}")
        
        content = file_data.get("content", "")
        encoding = file_data.get("encoding", "base64")
        
        if encoding == "base64":
            content = base64.b64decode(content).decode("utf-8")
        
        return content
    
    def fetch_repository(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch a GitHub repository including metadata and contents.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            List of repository contents
        """
        try:
            # Parse the GitHub URL
            repo_info = self.parse_github_url(url)
            
            # Fetch repository metadata
            metadata = self.fetch_repository_metadata(repo_info)
            
            # Fetch repository contents
            contents = self.fetch_repository_contents(repo_info)
            
            # Process contents to include full path
            for item in contents:
                item["full_path"] = item["path"]
                item["repo_info"] = repo_info
                item["metadata"] = metadata
            
            return contents
        except Exception as e:
            st.error(f"Error fetching repository: {str(e)}")
            return []
    
    def get_file_contents_recursive(self, repo_info: Dict[str, str], path: str = "") -> List[Dict[str, Any]]:
        """
        Recursively fetch all files in a repository.
        
        Args:
            repo_info: Dictionary containing owner and repo name
            path: Path within the repository to start fetching from
            
        Returns:
            List of file information dictionaries
        """
        all_files = []
        contents = self.fetch_repository_contents(repo_info, path)
        
        for item in contents:
            if item["type"] == "file":
                all_files.append({
                    "name": item["name"],
                    "path": item["path"],
                    "size": item["size"],
                    "type": "file",
                    "download_url": item["download_url"],
                    "repo_info": repo_info
                })
            elif item["type"] == "dir":
                all_files.extend(self.get_file_contents_recursive(repo_info, item["path"]))
        
        return all_files 