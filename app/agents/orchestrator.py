"""
Orchestrator for AI Docs Generator agent crew.
Manages the execution of CrewAI agents to generate documentation.
"""
import os
from typing import Dict, Any, List, Optional
from app.agents.crew_definition import DocsGeneratorCrew
from langchain.tools import Tool
from dotenv import load_dotenv
import groq
import json
import tempfile

# Load environment variables
load_dotenv()

# Configure Groq client
groq_client = groq.Client(api_key=os.environ.get("GROQ_API_KEY", ""))


class GithubTools:
    """Tools for GitHub repository interaction."""
    
    @staticmethod
    def create_github_tools() -> List[Tool]:
        """Create tools for GitHub repository interaction."""
        return [
            Tool(
                name="search_repository_files",
                func=GithubTools.search_repository_files,
                description="Search for files in a repository by name or extension",
            ),
            Tool(
                name="read_repository_file",
                func=GithubTools.read_repository_file,
                description="Read the contents of a file in the repository",
            ),
        ]
    
    @staticmethod
    def search_repository_files(repository_data: Dict[str, Any], query: str) -> str:
        """
        Search for files in a repository.
        
        Args:
            repository_data: Repository data
            query: Search query (name or extension)
            
        Returns:
            List of matching files
        """
        files = repository_data.get("files", {})
        
        # Filter files based on query
        matching_files = []
        for file_path in files.keys():
            if query.lower() in file_path.lower():
                matching_files.append(file_path)
        
        return json.dumps(matching_files)
    
    @staticmethod
    def read_repository_file(repository_data: Dict[str, Any], file_path: str) -> str:
        """
        Read the contents of a file in the repository.
        
        Args:
            repository_data: Repository data
            file_path: Path to the file
            
        Returns:
            File contents
        """
        files = repository_data.get("files", {})
        file_info = files.get(file_path)
        
        if not file_info:
            return f"File not found: {file_path}"
        
        return file_info.get("content", "")


class CodeParserTools:
    """Tools for code parsing and analysis."""
    
    @staticmethod
    def create_code_parser_tools() -> List[Tool]:
        """Create tools for code parsing and analysis."""
        return [
            Tool(
                name="get_file_info",
                func=CodeParserTools.get_file_info,
                description="Get information about a file in the repository",
            ),
            Tool(
                name="find_dependencies",
                func=CodeParserTools.find_dependencies,
                description="Find dependencies for a file in the repository",
            ),
            Tool(
                name="find_references",
                func=CodeParserTools.find_references,
                description="Find references to a class or function in the repository",
            ),
        ]
    
    @staticmethod
    def get_file_info(parsed_data: Dict[str, Any], file_path: str) -> str:
        """
        Get information about a file in the repository.
        
        Args:
            parsed_data: Parsed repository data
            file_path: Path to the file
            
        Returns:
            File information as JSON string
        """
        parsed_files = parsed_data.get("parsed_files", {})
        file_info = parsed_files.get(file_path)
        
        if not file_info:
            return f"File not found: {file_path}"
        
        return json.dumps(file_info)
    
    @staticmethod
    def find_dependencies(parsed_data: Dict[str, Any], file_path: str) -> str:
        """
        Find dependencies for a file in the repository.
        
        Args:
            parsed_data: Parsed repository data
            file_path: Path to the file
            
        Returns:
            Dependencies as JSON string
        """
        dependencies = parsed_data.get("dependencies", {})
        file_dependencies = dependencies.get(file_path, [])
        
        return json.dumps(file_dependencies)
    
    @staticmethod
    def find_references(parsed_data: Dict[str, Any], symbol: str) -> str:
        """
        Find references to a class or function in the repository.
        
        Args:
            parsed_data: Parsed repository data
            symbol: Class or function name
            
        Returns:
            References as JSON string
        """
        parsed_files = parsed_data.get("parsed_files", {})
        references = []
        
        for file_path, file_info in parsed_files.items():
            # Check if symbol is defined in this file
            classes = file_info.get("classes", [])
            functions = file_info.get("functions", [])
            
            if any(cls["name"] == symbol for cls in classes) or any(func["name"] == symbol for func in functions):
                references.append({
                    "file": file_path,
                    "type": "definition",
                })
            
            # Check if symbol is referenced in this file
            if symbol in file_info.get("imports", []):
                references.append({
                    "file": file_path,
                    "type": "import",
                })
        
        return json.dumps(references)


class DiagramTools:
    """Tools for diagram generation."""
    
    @staticmethod
    def create_diagram_tools() -> List[Tool]:
        """Create tools for diagram generation."""
        return [
            Tool(
                name="generate_architecture_diagram",
                func=DiagramTools.generate_architecture_diagram,
                description="Generate an architecture diagram for the repository",
            ),
            Tool(
                name="generate_class_diagram",
                func=DiagramTools.generate_class_diagram,
                description="Generate a class diagram for specified classes",
            ),
            Tool(
                name="generate_sequence_diagram",
                func=DiagramTools.generate_sequence_diagram,
                description="Generate a sequence diagram for a specific flow",
            ),
        ]
    
    @staticmethod
    def generate_architecture_diagram(parsed_data: Dict[str, Any], format: str = "mermaid") -> str:
        """
        Generate an architecture diagram for the repository.
        
        Args:
            parsed_data: Parsed repository data
            format: Diagram format ("mermaid" or "graphviz")
            
        Returns:
            Diagram code
        """
        from app.diagrams.generator import DiagramGenerator
        generator = DiagramGenerator(format=format)
        return generator.create_architecture_diagram(parsed_data)
    
    @staticmethod
    def generate_class_diagram(parsed_data: Dict[str, Any], class_names: List[str], format: str = "mermaid") -> str:
        """
        Generate a class diagram for specified classes.
        
        Args:
            parsed_data: Parsed repository data
            class_names: List of class names to include in the diagram
            format: Diagram format ("mermaid" or "graphviz")
            
        Returns:
            Diagram code
        """
        from app.diagrams.generator import DiagramGenerator
        # For simplicity, we currently just generate the full class diagram
        # A more sophisticated implementation would filter to the specified classes
        generator = DiagramGenerator(format=format)
        return generator.create_class_diagram(parsed_data)
    
    @staticmethod
    def generate_sequence_diagram(parsed_data: Dict[str, Any], description: str) -> str:
        """
        Generate a sequence diagram for a specific flow.
        
        Args:
            parsed_data: Parsed repository data
            description: Description of the flow to diagram
            
        Returns:
            Mermaid sequence diagram code
        """
        # This is a placeholder that would be implemented with LLM-driven sequence diagram generation
        actors = []
        components = []
        
        # Extract potential actors and components from the repository
        parsed_files = parsed_data.get("parsed_files", {})
        for file_info in parsed_files.values():
            for cls in file_info.get("classes", []):
                components.append(cls["name"])
        
        # Use Groq to generate a sequence diagram based on the components and description
        prompt = f"""
        Generate a Mermaid sequence diagram for the following scenario:
        {description}
        
        Based on the available components: {', '.join(components[:20])}
        
        The diagram should follow this format:
        ```mermaid
        sequenceDiagram
            Actor1->>Component1: Action
            Component1->>Component2: Action
            Component2-->>Component1: Response
            Component1-->>Actor1: Response
        ```
        
        Generate only the diagram code, no explanations.
        """
        
        try:
            response = groq_client.chat.completions.create(
                model=os.environ.get("DEFAULT_MODEL", "llama3-70b-8192"),
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "You are a technical diagram generator that creates sequence diagrams based on code components."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            diagram_code = response.choices[0].message.content
            
            # Extract just the mermaid code
            if "```mermaid" in diagram_code:
                diagram_code = diagram_code.split("```mermaid")[1]
                if "```" in diagram_code:
                    diagram_code = diagram_code.split("```")[0]
            
            return f"```mermaid\n{diagram_code.strip()}\n```"
        except Exception as e:
            return f"```mermaid\nsequenceDiagram\n    participant User\n    participant System\n    Note over User,System: Error generating diagram: {str(e)}\n```"


def run_documentation_generation(parsed_data: Dict[str, Any], model: str = None, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Run the documentation generation process using CrewAI.
    
    Args:
        parsed_data: Parsed repository data
        model: LLM model to use
        temperature: Temperature setting for LLM responses
        
    Returns:
        Generated documentation and diagrams
    """
    # Use specified model or default from environment
    model = model or os.environ.get("DEFAULT_MODEL", "llama3-70b-8192")
    
    # Create tools
    github_tools = GithubTools.create_github_tools()
    code_parser_tools = CodeParserTools.create_code_parser_tools()
    diagram_tools = DiagramTools.create_diagram_tools()
    
    # Create crew
    crew = DocsGeneratorCrew(
        model=model,
        temperature=temperature,
        verbose=True,
        github_tools=github_tools,
        code_parser_tools=code_parser_tools,
        diagram_tools=diagram_tools,
    )
    
    # Run documentation generation
    result = crew.run(parsed_data)
    
    return result 