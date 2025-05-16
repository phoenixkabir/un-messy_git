"""
Code parser for AI Docs Generator.
"""
from typing import Dict, Any, List, Optional
import os
from collections import defaultdict
import re


class CodeParser:
    """
    Parses code files to extract structure and relationships.
    """
    
    def __init__(self):
        """Initialize the code parser."""
        # File extension to language mapping
        self.language_map = {
            "py": "Python",
            "js": "JavaScript",
            "jsx": "JavaScript (React)",
            "ts": "TypeScript",
            "tsx": "TypeScript (React)",
            "java": "Java",
            "c": "C",
            "cpp": "C++",
            "cs": "C#",
            "go": "Go",
            "rb": "Ruby",
            "php": "PHP",
            "swift": "Swift",
            "kt": "Kotlin",
            "rs": "Rust",
            "html": "HTML",
            "css": "CSS",
            "scss": "SCSS",
            "md": "Markdown",
            "json": "JSON",
            "yaml": "YAML",
            "yml": "YAML",
            "sql": "SQL",
            "sh": "Shell",
            "bat": "Batch",
            "ps1": "PowerShell",
        }
        
        # Patterns for detecting imports and dependencies
        self.import_patterns = {
            "Python": [
                r"import\s+([a-zA-Z0-9_.,\s]+)",
                r"from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_.,\s*]+)",
            ],
            "JavaScript": [
                r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]",
                r"import\s+['\"]([^'\"]+)['\"]",
            ],
            "TypeScript": [
                r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]",
                r"import\s+['\"]([^'\"]+)['\"]",
            ],
            "Java": [
                r"import\s+([a-zA-Z0-9_.]+\*?);",
            ],
        }
        
        # Patterns for detecting classes and functions
        self.class_patterns = {
            "Python": r"class\s+([a-zA-Z0-9_]+)(?:\(([a-zA-Z0-9_.,\s]+)\))?:",
            "JavaScript": r"class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?",
            "TypeScript": r"(?:export\s+)?class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?(?:\s+implements\s+([a-zA-Z0-9_,\s]+))?",
            "Java": r"(?:public|private|protected)?\s*(?:static)?\s*class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?(?:\s+implements\s+([a-zA-Z0-9_,\s]+))?",
        }
        
        self.function_patterns = {
            "Python": r"def\s+([a-zA-Z0-9_]+)\s*\(",
            "JavaScript": r"(?:function\s+([a-zA-Z0-9_]+)\s*\(|(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|([a-zA-Z0-9_]+)\s*:\s*(?:async\s*)?\([^)]*\)\s*=>)",
            "TypeScript": r"(?:function\s+([a-zA-Z0-9_]+)\s*\(|(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|([a-zA-Z0-9_]+)\s*(?::\s*[a-zA-Z0-9_<>[\],\s|]+)?\s*\([^)]*\))",
            "Java": r"(?:public|private|protected)?\s*(?:static)?\s*(?:[a-zA-Z0-9_<>[\],\s]+)\s+([a-zA-Z0-9_]+)\s*\(",
        }
    
    def detect_language(self, file_path: str, content: str) -> str:
        """
        Detect the programming language of a file.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Detected language
        """
        extension = os.path.splitext(file_path)[1][1:].lower()
        
        # Check if extension is in our map
        if extension in self.language_map:
            return self.language_map[extension]
        
        # Try to guess based on content for files without clear extensions
        if "def " in content and "import " in content:
            return "Python"
        if "function " in content or "const " in content or "let " in content:
            return "JavaScript"
        if "public class " in content or "private class " in content:
            return "Java"
            
        return "Unknown"
    
    def parse_imports(self, content: str, language: str) -> List[str]:
        """
        Parse imports and dependencies from code.
        
        Args:
            content: File content
            language: Programming language
            
        Returns:
            List of imported modules/packages
        """
        imports = []
        
        if language in self.import_patterns:
            for pattern in self.import_patterns[language]:
                for match in re.finditer(pattern, content):
                    if match.groups():
                        imports.append(match.group(1).strip())
        
        return imports
    
    def parse_classes(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Parse class definitions from code.
        
        Args:
            content: File content
            language: Programming language
            
        Returns:
            List of class information
        """
        classes = []
        
        if language in self.class_patterns:
            pattern = self.class_patterns[language]
            for match in re.finditer(pattern, content):
                class_info = {
                    "name": match.group(1),
                    "parent_classes": [],
                }
                
                # Check for inheritance
                if len(match.groups()) > 1 and match.group(2):
                    parent_classes = match.group(2).split(',')
                    class_info["parent_classes"] = [p.strip() for p in parent_classes]
                
                classes.append(class_info)
        
        return classes
    
    def parse_functions(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Parse function definitions from code.
        
        Args:
            content: File content
            language: Programming language
            
        Returns:
            List of function information
        """
        functions = []
        
        if language in self.function_patterns:
            pattern = self.function_patterns[language]
            for match in re.finditer(pattern, content):
                # Use the first non-None capturing group as the function name
                for group in match.groups():
                    if group:
                        function_name = group
                        break
                else:
                    continue  # Skip if no function name found
                
                functions.append({
                    "name": function_name,
                })
        
        return functions
    
    def extract_api_endpoints(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract API endpoints from code (e.g., Flask/Express routes).
        
        Args:
            content: File content
            language: Programming language
            
        Returns:
            List of API endpoint information
        """
        endpoints = []
        
        # Extract Flask routes (Python)
        if language == "Python":
            # Look for @app.route or @blueprint.route decorators
            route_pattern = r"@(?:[a-zA-Z0-9_]+\.)?route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?"
            for match in re.finditer(route_pattern, content):
                route_path = match.group(1)
                methods = []
                if match.group(2):
                    methods_str = match.group(2)
                    methods = [m.strip(" '\"") for m in methods_str.split(',')]
                
                endpoints.append({
                    "path": route_path,
                    "methods": methods if methods else ["GET"],
                    "type": "Flask",
                })
        
        # Extract Express routes (JavaScript/TypeScript)
        if language in ["JavaScript", "TypeScript"]:
            # Look for app.get/post/put/delete patterns
            route_pattern = r"(?:app|router)\.([a-z]+)\s*\(['\"]([^'\"]+)['\"]"
            for match in re.finditer(route_pattern, content):
                method = match.group(1).upper()
                route_path = match.group(2)
                
                endpoints.append({
                    "path": route_path,
                    "methods": [method],
                    "type": "Express",
                })
        
        return endpoints
    
    def parse_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a single file to extract its structure and content.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Dictionary containing parsed information
        """
        language = self.detect_language(file_path, content)
        
        # Skip parsing binary files or files with unknown language
        if content == "[Binary file not shown]" or language == "Unknown":
            return {
                "path": file_path,
                "language": language,
                "summary": "Binary file or unknown format",
                "type": "binary" if content == "[Binary file not shown]" else "unknown",
            }
        
        # Parse the file
        imports = self.parse_imports(content, language)
        classes = self.parse_classes(content, language)
        functions = self.parse_functions(content, language)
        endpoints = self.extract_api_endpoints(content, language)
        
        # Determine file type based on content
        file_type = "source"
        if any(file_path.endswith(ext) for ext in [".md", ".txt"]):
            file_type = "documentation"
        elif any(file_path.endswith(ext) for ext in [".json", ".yaml", ".yml", ".xml", ".toml"]):
            file_type = "config"
        elif any(file_path.endswith(ext) for ext in [".html", ".css", ".scss", ".less"]):
            file_type = "frontend"
        elif "test" in file_path.lower() or file_path.endswith("spec.js") or file_path.endswith("spec.ts"):
            file_type = "test"
        
        # Extract file summary
        loc = len(content.split('\n'))
        
        return {
            "path": file_path,
            "language": language,
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "endpoints": endpoints,
            "loc": loc,
            "type": file_type,
        }
    
    def build_dependency_graph(self, parsed_files: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Build a dependency graph between files.
        
        Args:
            parsed_files: Dictionary of parsed file information
            
        Returns:
            Dictionary mapping files to their dependencies
        """
        # Map from module/package names to files
        module_to_file = {}
        
        # First pass: map modules to files
        for file_path, file_info in parsed_files.items():
            # Extract module name from file path
            if file_info['language'] == "Python":
                # Convert path to module notation
                module_path = os.path.splitext(file_path)[0].replace('/', '.')
                module_parts = module_path.split('.')
                
                # Register all possible import paths for this file
                for i in range(len(module_parts)):
                    module_name = '.'.join(module_parts[i:])
                    if module_name:
                        module_to_file[module_name] = file_path
            
            # For JavaScript/TypeScript, use path-based mapping
            elif file_info['language'] in ["JavaScript", "TypeScript"]:
                base_name = os.path.splitext(file_path)[0]
                module_to_file[base_name] = file_path
                module_to_file['./' + base_name] = file_path
        
        # Second pass: build dependency graph
        dependencies = defaultdict(list)
        
        for file_path, file_info in parsed_files.items():
            for imported in file_info.get('imports', []):
                # Try to find the file that provides this import
                target_file = module_to_file.get(imported)
                
                if target_file and target_file != file_path:  # Avoid self-dependencies
                    dependencies[file_path].append(target_file)
        
        return dict(dependencies)
    
    def parse_repository(self, repository: Dict[str, Any], selected_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Parse a repository to extract its structure and content.
        
        Args:
            repository: Repository information from fetch_repository
            selected_files: List of files to parse (if None, parse all files)
            
        Returns:
            Dictionary containing parsed repository information
        """
        files = repository['files']
        
        # Filter files if selected_files is provided
        if selected_files:
            files = {path: info for path, info in files.items() if path in selected_files}
        
        # Parse each file
        parsed_files = {}
        for file_path, file_info in files.items():
            parsed_files[file_path] = self.parse_file(file_path, file_info['content'])
        
        # Build dependency graph
        dependencies = self.build_dependency_graph(parsed_files)
        
        # Collect statistics
        language_count = defaultdict(int)
        file_type_count = defaultdict(int)
        total_loc = 0
        
        for file_info in parsed_files.values():
            language_count[file_info['language']] += 1
            file_type_count[file_info['type']] += 1
            total_loc += file_info.get('loc', 0)
        
        return {
            "metadata": repository['metadata'],
            "parsed_files": parsed_files,
            "dependencies": dependencies,
            "statistics": {
                "total_files": len(parsed_files),
                "languages": dict(language_count),
                "file_types": dict(file_type_count),
                "total_loc": total_loc,
            },
            "repository_path": repository['path'],
        }


def parse_repository(repository: Dict[str, Any], selected_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse a repository for documentation generation.
    
    Args:
        repository: Repository information from fetch_repository
        selected_files: List of files to parse (if None, parse all files)
        
    Returns:
        Dictionary containing parsed repository information
    """
    parser = CodeParser()
    return parser.parse_repository(repository, selected_files) 