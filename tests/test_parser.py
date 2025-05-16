"""
Unit tests for code parser functionality.
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open

from app.parsers.code_parser import CodeParser


class TestCodeParser(unittest.TestCase):
    """Test cases for CodeParser class."""

    def setUp(self):
        """Set up test environment."""
        self.code_parser = CodeParser()
        
    def test_detect_language_by_extension(self):
        """Test language detection by file extension."""
        test_cases = [
            ("file.py", "python"),
            ("file.js", "javascript"),
            ("file.ts", "typescript"),
            ("file.java", "java"),
            ("file.cpp", "cpp"),
            ("file.c", "c"),
            ("file.go", "go"),
            ("file.rb", "ruby"),
            ("file.php", "php"),
            ("file.html", "html"),
            ("file.css", "css"),
            ("file.unknown", "unknown")
        ]
        
        for filename, expected_language in test_cases:
            detected_language = self.code_parser.detect_language(filename)
            self.assertEqual(detected_language, expected_language)
    
    @patch('builtins.open', new_callable=mock_open, read_data="import os\n\ndef main():\n    print('Hello')")
    def test_parse_python_file(self, mock_file):
        """Test parsing a Python file."""
        result = self.code_parser.parse_file("example.py")
        
        # Check that the result contains the expected keys
        self.assertIn("imports", result)
        self.assertIn("functions", result)
        self.assertIn("classes", result)
        self.assertIn("language", result)
        
        # Check that the language is correctly identified
        self.assertEqual(result["language"], "python")
        
        # Check that imports were detected
        self.assertIn("os", result["imports"])
        
        # Check that functions were detected
        self.assertIn("main", result["functions"])
    
    @patch('builtins.open', new_callable=mock_open, read_data="class Example {\n  constructor() {}\n  method() {}\n}")
    def test_parse_javascript_file(self, mock_file):
        """Test parsing a JavaScript file."""
        result = self.code_parser.parse_file("example.js")
        
        # Check language detection
        self.assertEqual(result["language"], "javascript")
        
        # Check that classes were detected
        self.assertIn("Example", result["classes"])
        
        # Check that methods were detected
        self.assertIn("method", result["methods"])
        self.assertIn("constructor", result["methods"])
    
    def test_build_dependency_graph_simple(self):
        """Test building a simple dependency graph."""
        # Mock file parse results
        parsed_files = {
            "module1.py": {
                "imports": ["module2", "module3"],
                "language": "python"
            },
            "module2.py": {
                "imports": ["module3"],
                "language": "python"
            },
            "module3.py": {
                "imports": [],
                "language": "python"
            }
        }
        
        # Build dependency graph
        with patch.object(self.code_parser, 'parse_file', side_effect=lambda f: parsed_files.get(f, {})):
            graph = self.code_parser.build_dependency_graph(list(parsed_files.keys()))
            
            # Check that the graph has the correct nodes
            self.assertEqual(len(graph), 3)
            
            # Check that dependencies are correctly mapped
            self.assertIn("module2", graph["module1.py"]["depends_on"])
            self.assertIn("module3", graph["module1.py"]["depends_on"])
            self.assertIn("module3", graph["module2.py"]["depends_on"])
            self.assertEqual(len(graph["module3.py"]["depends_on"]), 0)
            
            # Check reverse dependencies
            self.assertIn("module1.py", graph["module2.py"]["used_by"])
            self.assertIn("module1.py", graph["module3.py"]["used_by"])
            self.assertIn("module2.py", graph["module3.py"]["used_by"])
            self.assertEqual(len(graph["module1.py"]["used_by"]), 0)


if __name__ == '__main__':
    unittest.main() 