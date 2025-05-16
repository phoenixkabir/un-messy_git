"""
GitHub repository fetcher for AI Docs Generator.
"""
import os
import tempfile
from typing import Dict, Any, Optional, List, Tuple
import re
import git
from github import Github, Repository, GithubException
from pathlib import Path


class RepoFetcher:
    """
    Handles fetching GitHub repositories for analysis.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the repository fetcher.
        
        Args:
            github_token: GitHub API token (optional but recommended for higher rate limits)
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.github = Github(self.github_token) if self.github_token else Github()
        self.clone_path = None
    
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repo name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple containing (owner, repo_name)
            
        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        # Handle multiple URL formats
        patterns = [
            r"github\.com/([^/]+)/([^/]+)/?.*",  # github.com/owner/repo
            r"github\.com:([^/]+)/([^/]+)\.git",  # github.com:owner/repo.git (SSH)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo_name = match.groups()
                # Remove .git suffix if present
                repo_name = repo_name.replace(".git", "")
                return owner, repo_name
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def fetch_repository_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetch repository metadata from GitHub API.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dictionary containing repository metadata
            
        Raises:
            ValueError: If repository cannot be found or accessed
        """
        try:
            owner, repo_name = self._parse_github_url(url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "default_branch": repo.default_branch,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "owner": owner,
                "repo_name": repo_name,
                "size_kb": repo.size,
            }
        except GithubException as e:
            raise ValueError(f"Error fetching repository: {e}")
    
    def clone_repository(self, url: str, branch: Optional[str] = None) -> str:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            url: GitHub repository URL
            branch: Branch to clone (defaults to the default branch)
            
        Returns:
            Path to the cloned repository
            
        Raises:
            ValueError: If repository cannot be cloned
        """
        try:
            # Create a temporary directory
            self.clone_path = tempfile.mkdtemp(prefix="ai_docs_generator_")
            
            # Get metadata to determine default branch if needed
            metadata = self.fetch_repository_metadata(url)
            branch = branch or metadata["default_branch"]
            
            # Clone the repository
            git.Repo.clone_from(
                url,
                self.clone_path,
                branch=branch,
                depth=1  # Shallow clone for faster download
            )
            
            return self.clone_path
        except Exception as e:
            raise ValueError(f"Error cloning repository: {e}")
    
    def get_file_list(self, repo_path: str, ignore_patterns: Optional[List[str]] = None) -> List[str]:
        """
        Get a list of all files in the repository.
        
        Args:
            repo_path: Path to the cloned repository
            ignore_patterns: List of glob patterns to ignore
            
        Returns:
            List of file paths relative to repo_path
        """
        ignore_patterns = ignore_patterns or [
            ".git/*", "node_modules/*", "__pycache__/*", "*.pyc",
            "*.log", "*.lock", ".DS_Store", "venv/*", "env/*",
            "dist/*", "build/*", "*.min.js", "*.min.css"
        ]
        
        all_files = []
        repo_path = Path(repo_path)
        
        for root, _, files in os.walk(repo_path):
            rel_root = Path(root).relative_to(repo_path)
            for file in files:
                file_path = str(rel_root / file)
                
                # Skip files matching ignore patterns
                if any(Path(file_path).match(pattern) for pattern in ignore_patterns):
                    continue
                
                all_files.append(file_path)
        
        return all_files
    
    def read_file(self, repo_path: str, file_path: str) -> str:
        """
        Read a file from the repository.
        
        Args:
            repo_path: Path to the cloned repository
            file_path: Path to the file, relative to repo_path
            
        Returns:
            File contents as a string
            
        Raises:
            FileNotFoundError: If file cannot be found
            UnicodeDecodeError: If file cannot be decoded as text
        """
        full_path = os.path.join(repo_path, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a more lenient encoding for binary files
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                return "[Binary file not shown]"
    
    def get_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Get a complete representation of the repository structure.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Dictionary containing repository structure and file contents
        """
        file_list = self.get_file_list(repo_path)
        
        # Build file tree
        file_tree = {}
        for file_path in file_list:
            content = self.read_file(repo_path, file_path)
            file_tree[file_path] = {
                "path": file_path,
                "content": content,
                "size": len(content),
                "extension": os.path.splitext(file_path)[1][1:] if os.path.splitext(file_path)[1] else "",
            }
        
        return file_tree
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.clone_path and os.path.exists(self.clone_path):
            import shutil
            shutil.rmtree(self.clone_path, ignore_errors=True)


def fetch_repository(url: str) -> Dict[str, Any]:
    """
    Fetch a GitHub repository for documentation generation.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Dictionary containing repository data
    """
    fetcher = RepoFetcher()
    
    try:
        # Get repository metadata
        metadata = fetcher.fetch_repository_metadata(url)
        
        # Clone the repository
        repo_path = fetcher.clone_repository(url)
        
        # Get repository structure
        file_tree = fetcher.get_repository_structure(repo_path)
        
        return {
            "metadata": metadata,
            "files": file_tree,
            "path": repo_path,
        }
    except Exception as e:
        print(f"Error fetching repository: {e}")
        return None
    finally:
        fetcher.cleanup() 