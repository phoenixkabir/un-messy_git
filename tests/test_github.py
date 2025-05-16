"""
Unit tests for GitHub repository fetcher functionality.
"""
import os
import unittest
from unittest.mock import patch, MagicMock

import pytest

from app.github.repo_fetcher import RepoFetcher


class TestRepoFetcher(unittest.TestCase):
    """Test cases for RepoFetcher class."""

    def setUp(self):
        """Set up test environment."""
        self.repo_fetcher = RepoFetcher()
        self.test_url = "https://github.com/username/repo"
        
    def test_parse_github_url_valid(self):
        """Test parsing valid GitHub URLs."""
        owner, repo = self.repo_fetcher.parse_github_url(self.test_url)
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")
        
        # Test with trailing slash
        owner, repo = self.repo_fetcher.parse_github_url(self.test_url + "/")
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")
        
        # Test with .git extension
        owner, repo = self.repo_fetcher.parse_github_url(self.test_url + ".git")
        self.assertEqual(owner, "username")
        self.assertEqual(repo, "repo")

    def test_parse_github_url_invalid(self):
        """Test parsing invalid GitHub URLs."""
        invalid_urls = [
            "https://gitlab.com/username/repo",
            "https://github.com",
            "https://github.com/username",
            "invalid_url",
        ]
        
        for url in invalid_urls:
            with self.assertRaises(ValueError):
                self.repo_fetcher.parse_github_url(url)
    
    @patch('app.github.repo_fetcher.requests.get')
    def test_fetch_repo_metadata(self, mock_get):
        """Test fetching repository metadata."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "repo",
            "description": "Test repository",
            "stargazers_count": 100,
            "forks_count": 20,
            "language": "Python",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-31T00:00:00Z",
            "owner": {
                "login": "username",
                "avatar_url": "https://github.com/avatar.png"
            }
        }
        mock_get.return_value = mock_response
        
        metadata = self.repo_fetcher.fetch_repo_metadata("username", "repo")
        
        self.assertEqual(metadata["name"], "repo")
        self.assertEqual(metadata["description"], "Test repository")
        self.assertEqual(metadata["stars"], 100)
        self.assertEqual(metadata["forks"], 20)
        self.assertEqual(metadata["language"], "Python")
        self.assertEqual(metadata["owner"], "username")
        
        # Assert that requests.get was called with the correct URL
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/username/repo",
            headers=self.repo_fetcher.headers
        )
    
    @patch('app.github.repo_fetcher.subprocess.run')
    def test_clone_repository(self, mock_run):
        """Test cloning a repository."""
        # Mock the subprocess.run response
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Patch os.path.exists to always return False (directory doesn't exist)
        with patch('os.path.exists', return_value=False):
            # Patch os.makedirs to avoid actually creating directories
            with patch('os.makedirs'):
                result = self.repo_fetcher.clone_repository("username", "repo")
                
                self.assertTrue(result)
                
                # Assert that git clone was called with the correct arguments
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                self.assertEqual(args[0][0], "git")
                self.assertEqual(args[0][1], "clone")
                self.assertEqual(args[0][2], "https://github.com/username/repo.git")
    
    @patch('os.walk')
    def test_get_file_structure(self, mock_walk):
        """Test getting file structure from a repository."""
        # Mock the os.walk response
        mock_walk.return_value = [
            ('/tmp/repo', ['dir1', 'dir2'], ['file1.py', 'file2.py']),
            ('/tmp/repo/dir1', [], ['file3.py']),
            ('/tmp/repo/dir2', [], ['file4.py'])
        ]
        
        # Patch the os.path.getsize to always return 1024
        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.isdir', return_value=True):
                structure = self.repo_fetcher.get_file_structure("/tmp/repo")
                
                # Check that the structure contains the expected files and directories
                self.assertEqual(len(structure), 6)  # 4 files + 2 directories
                
                # Check that each file has the correct properties
                for item in structure:
                    if item["type"] == "file":
                        self.assertIn("size", item)
                        self.assertIn("path", item)
                    elif item["type"] == "directory":
                        self.assertIn("path", item)


if __name__ == '__main__':
    unittest.main() 