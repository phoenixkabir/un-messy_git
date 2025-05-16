"""
Diagram generation for AI Docs Generator.
Supports Mermaid and Graphviz formats.
"""
from typing import Dict, Any, List, Optional
import os
import re
from collections import defaultdict


class DiagramGenerator:
    """
    Generates diagrams from parsed repository data.
    Supports Mermaid and Graphviz formats.
    """
    
    def __init__(self, format: str = "mermaid", max_elements: int = 100):
        """
        Initialize the diagram generator.
        
        Args:
            format: Output format ("mermaid" or "graphviz")
            max_elements: Maximum number of elements in a diagram
        """
        self.format = format.lower()
        self.max_elements = max_elements
        
        if self.format not in ["mermaid", "graphviz"]:
            raise ValueError(f"Unsupported diagram format: {format}")
    
    def _create_architecture_diagram_mermaid(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Mermaid architecture diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Mermaid diagram code
        """
        # Extract main components and their relationships
        files = parsed_data['parsed_files']
        dependencies = parsed_data['dependencies']
        
        # Group files by directory for modules
        modules = defaultdict(list)
        for file_path in files:
            directory = os.path.dirname(file_path)
            if not directory:
                directory = "root"
            modules[directory].append(file_path)
        
        # Filter to stay within max_elements
        if len(modules) > self.max_elements:
            # Sort by number of files
            sorted_modules = sorted(modules.items(), key=lambda x: len(x[1]), reverse=True)
            # Take top modules
            modules = dict(sorted_modules[:self.max_elements])
        
        # Generate diagram
        diagram = "```mermaid\ngraph TD\n"
        
        # Add modules as nodes
        for module, files in modules.items():
            module_id = re.sub(r'[^\w]', '_', module)
            file_count = len(files)
            diagram += f"    {module_id}[{module}<br/>({file_count} files)]\n"
        
        # Add dependencies between modules
        module_dependencies = defaultdict(set)
        for source, targets in dependencies.items():
            source_module = os.path.dirname(source) or "root"
            for target in targets:
                target_module = os.path.dirname(target) or "root"
                if source_module != target_module:
                    module_dependencies[source_module].add(target_module)
        
        for source, targets in module_dependencies.items():
            source_id = re.sub(r'[^\w]', '_', source)
            for target in targets:
                target_id = re.sub(r'[^\w]', '_', target)
                diagram += f"    {source_id} --> {target_id}\n"
        
        diagram += "```"
        return diagram
    
    def _create_architecture_diagram_graphviz(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Graphviz architecture diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Graphviz diagram code
        """
        # Extract main components and their relationships
        files = parsed_data['parsed_files']
        dependencies = parsed_data['dependencies']
        
        # Group files by directory for modules
        modules = defaultdict(list)
        for file_path in files:
            directory = os.path.dirname(file_path)
            if not directory:
                directory = "root"
            modules[directory].append(file_path)
        
        # Filter to stay within max_elements
        if len(modules) > self.max_elements:
            # Sort by number of files
            sorted_modules = sorted(modules.items(), key=lambda x: len(x[1]), reverse=True)
            # Take top modules
            modules = dict(sorted_modules[:self.max_elements])
        
        # Generate diagram
        diagram = "digraph G {\n"
        diagram += "    rankdir=TB;\n"
        diagram += "    node [shape=box, style=filled, fillcolor=lightblue];\n"
        
        # Add modules as nodes
        for module, files in modules.items():
            module_id = re.sub(r'[^\w]', '_', module)
            file_count = len(files)
            diagram += f'    {module_id} [label="{module}\\n({file_count} files)"];\n'
        
        # Add dependencies between modules
        module_dependencies = defaultdict(set)
        for source, targets in dependencies.items():
            source_module = os.path.dirname(source) or "root"
            for target in targets:
                target_module = os.path.dirname(target) or "root"
                if source_module != target_module:
                    module_dependencies[source_module].add(target_module)
        
        for source, targets in module_dependencies.items():
            source_id = re.sub(r'[^\w]', '_', source)
            for target in targets:
                target_id = re.sub(r'[^\w]', '_', target)
                diagram += f"    {source_id} -> {target_id};\n"
        
        diagram += "}"
        return diagram
    
    def create_architecture_diagram(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create an architecture diagram showing high-level components and their relationships.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Diagram code in the specified format
        """
        if self.format == "mermaid":
            return self._create_architecture_diagram_mermaid(parsed_data)
        else:
            return self._create_architecture_diagram_graphviz(parsed_data)
    
    def _create_class_diagram_mermaid(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Mermaid class diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Mermaid diagram code
        """
        files = parsed_data['parsed_files']
        
        # Extract classes and their relationships
        classes = {}
        for file_path, file_info in files.items():
            file_classes = file_info.get('classes', [])
            for cls in file_classes:
                class_name = cls['name']
                classes[class_name] = {
                    'file': file_path,
                    'parent_classes': cls.get('parent_classes', []),
                }
        
        # Filter to stay within max_elements
        if len(classes) > self.max_elements:
            # Just take the first N classes
            classes = dict(list(classes.items())[:self.max_elements])
        
        # Generate diagram
        diagram = "```mermaid\nclassDiagram\n"
        
        # Add inheritance relationships
        for class_name, info in classes.items():
            for parent in info.get('parent_classes', []):
                if parent in classes:  # Only include parents that we have in our filtered set
                    diagram += f"    {parent} <|-- {class_name}\n"
        
        # Add classes
        for class_name, info in classes.items():
            file_path = info['file']
            diagram += f"    class {class_name} {\n"
            
            # Add filename
            diagram += f"        +{os.path.basename(file_path)}\n"
                        
            # Add functions from file
            file_info = files[file_path]
            if 'functions' in file_info:
                for func in file_info['functions']:
                    if len(func.get('name', '')) > 0:
                        diagram += f"        +{func['name']}()\n"
            
            diagram += "    }\n"
        
        diagram += "```"
        return diagram
    
    def _create_class_diagram_graphviz(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Graphviz class diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Graphviz diagram code
        """
        files = parsed_data['parsed_files']
        
        # Extract classes and their relationships
        classes = {}
        for file_path, file_info in files.items():
            file_classes = file_info.get('classes', [])
            for cls in file_classes:
                class_name = cls['name']
                classes[class_name] = {
                    'file': file_path,
                    'parent_classes': cls.get('parent_classes', []),
                }
        
        # Filter to stay within max_elements
        if len(classes) > self.max_elements:
            # Just take the first N classes
            classes = dict(list(classes.items())[:self.max_elements])
        
        # Generate diagram
        diagram = "digraph G {\n"
        diagram += "    rankdir=BT;\n"  # Bottom to top for inheritance
        diagram += "    node [shape=record, style=filled, fillcolor=lightblue];\n"
        
        # Add classes
        for class_name, info in classes.items():
            file_path = info['file']
            file_basename = os.path.basename(file_path)
            
            # Get functions for this class from the file
            functions = []
            file_info = files[file_path]
            if 'functions' in file_info:
                for func in file_info['functions']:
                    if len(func.get('name', '')) > 0:
                        functions.append(func['name'] + "()")
            
            # Create the class node with HTML-like label
            diagram += f'    {class_name} [label="{{{{ {class_name} | + {file_basename} '
            if functions:
                diagram += ' | '
                diagram += '\\l+ '.join(functions) + '\\l'
            diagram += '}}}}"];\n'
        
        # Add inheritance relationships
        for class_name, info in classes.items():
            for parent in info.get('parent_classes', []):
                if parent in classes:  # Only include parents that we have in our filtered set
                    diagram += f"    {class_name} -> {parent} [arrowhead=empty];\n"
        
        diagram += "}"
        return diagram
    
    def create_class_diagram(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a class diagram showing class hierarchies and relationships.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Diagram code in the specified format
        """
        if self.format == "mermaid":
            return self._create_class_diagram_mermaid(parsed_data)
        else:
            return self._create_class_diagram_graphviz(parsed_data)
    
    def _create_dependency_diagram_mermaid(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Mermaid dependency diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Mermaid diagram code
        """
        dependencies = parsed_data['dependencies']
        
        # Filter to most important files and dependencies
        if len(dependencies) > self.max_elements:
            # Sort by number of dependencies
            sorted_deps = sorted(dependencies.items(), key=lambda x: len(x[1]), reverse=True)
            # Take top files
            dependencies = dict(sorted_deps[:self.max_elements])
        
        # Generate diagram
        diagram = "```mermaid\ngraph LR\n"
        
        # Add files as nodes
        added_nodes = set()
        for source, targets in dependencies.items():
            source_id = re.sub(r'[^\w]', '_', source)
            if source_id not in added_nodes:
                diagram += f"    {source_id}[{os.path.basename(source)}]\n"
                added_nodes.add(source_id)
            
            for target in targets:
                target_id = re.sub(r'[^\w]', '_', target)
                if target_id not in added_nodes:
                    diagram += f"    {target_id}[{os.path.basename(target)}]\n"
                    added_nodes.add(target_id)
                
                diagram += f"    {source_id} --> {target_id}\n"
        
        diagram += "```"
        return diagram
    
    def _create_dependency_diagram_graphviz(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Graphviz dependency diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Graphviz diagram code
        """
        dependencies = parsed_data['dependencies']
        
        # Filter to most important files and dependencies
        if len(dependencies) > self.max_elements:
            # Sort by number of dependencies
            sorted_deps = sorted(dependencies.items(), key=lambda x: len(x[1]), reverse=True)
            # Take top files
            dependencies = dict(sorted_deps[:self.max_elements])
        
        # Generate diagram
        diagram = "digraph G {\n"
        diagram += "    rankdir=LR;\n"
        diagram += "    node [shape=box, style=filled, fillcolor=lightblue];\n"
        
        # Add files as nodes
        added_nodes = set()
        for source, targets in dependencies.items():
            source_id = re.sub(r'[^\w]', '_', source)
            if source_id not in added_nodes:
                diagram += f'    {source_id} [label="{os.path.basename(source)}"];\n'
                added_nodes.add(source_id)
            
            for target in targets:
                target_id = re.sub(r'[^\w]', '_', target)
                if target_id not in added_nodes:
                    diagram += f'    {target_id} [label="{os.path.basename(target)}"];\n'
                    added_nodes.add(target_id)
                
                diagram += f"    {source_id} -> {target_id};\n"
        
        diagram += "}"
        return diagram
    
    def create_dependency_diagram(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a dependency diagram showing file dependencies.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Diagram code in the specified format
        """
        if self.format == "mermaid":
            return self._create_dependency_diagram_mermaid(parsed_data)
        else:
            return self._create_dependency_diagram_graphviz(parsed_data)
    
    def _create_api_diagram_mermaid(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Mermaid API diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Mermaid diagram code
        """
        # Collect all API endpoints
        endpoints = []
        files = parsed_data['parsed_files']
        
        for file_path, file_info in files.items():
            file_endpoints = file_info.get('endpoints', [])
            for endpoint in file_endpoints:
                endpoints.append({
                    'file': file_path,
                    'path': endpoint['path'],
                    'methods': endpoint['methods'],
                    'type': endpoint['type'],
                })
        
        # Filter to max_elements
        if len(endpoints) > self.max_elements:
            endpoints = endpoints[:self.max_elements]
        
        if not endpoints:
            return "```mermaid\ngraph TD\n    A[No API endpoints detected]\n```"
        
        # Generate diagram
        diagram = "```mermaid\nclassDiagram\n"
        
        # Group endpoints by file
        endpoints_by_file = defaultdict(list)
        for endpoint in endpoints:
            endpoints_by_file[endpoint['file']].append(endpoint)
        
        # Add classes for files
        for file_path, file_endpoints in endpoints_by_file.items():
            file_id = re.sub(r'[^\w]', '_', file_path)
            file_name = os.path.basename(file_path)
            
            diagram += f"    class {file_id} {{\n"
            diagram += f"        +{file_name}\n"
            
            for endpoint in file_endpoints:
                methods = ', '.join(endpoint['methods'])
                diagram += f"        +{methods} {endpoint['path']}\n"
            
            diagram += "    }\n"
        
        diagram += "```"
        return diagram
    
    def _create_api_diagram_graphviz(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create a Graphviz API diagram.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Graphviz diagram code
        """
        # Collect all API endpoints
        endpoints = []
        files = parsed_data['parsed_files']
        
        for file_path, file_info in files.items():
            file_endpoints = file_info.get('endpoints', [])
            for endpoint in file_endpoints:
                endpoints.append({
                    'file': file_path,
                    'path': endpoint['path'],
                    'methods': endpoint['methods'],
                    'type': endpoint['type'],
                })
        
        # Filter to max_elements
        if len(endpoints) > self.max_elements:
            endpoints = endpoints[:self.max_elements]
        
        if not endpoints:
            return "digraph G {\n    A [label=\"No API endpoints detected\"];\n}"
        
        # Generate diagram
        diagram = "digraph G {\n"
        diagram += "    rankdir=TB;\n"
        diagram += "    node [shape=record, style=filled, fillcolor=lightblue];\n"
        
        # Group endpoints by file
        endpoints_by_file = defaultdict(list)
        for endpoint in endpoints:
            endpoints_by_file[endpoint['file']].append(endpoint)
        
        # Add nodes for files
        for file_path, file_endpoints in endpoints_by_file.items():
            file_id = re.sub(r'[^\w]', '_', file_path)
            file_name = os.path.basename(file_path)
            
            # Create the label with endpoints
            label = f"{file_name}|"
            endpoint_labels = []
            for endpoint in file_endpoints:
                methods = ', '.join(endpoint['methods'])
                endpoint_labels.append(f"+ {methods} {endpoint['path']}")
            
            label += "\\l".join(endpoint_labels) + "\\l"
            
            diagram += f'    {file_id} [label="{{ {label} }}"];\n'
        
        # Add relationships based on framework type
        framework_groups = defaultdict(list)
        for file_path, file_endpoints in endpoints_by_file.items():
            framework = file_endpoints[0]['type'] if file_endpoints else "Unknown"
            framework_groups[framework].append(file_path)
        
        for framework, files in framework_groups.items():
            if len(files) > 1:
                for i in range(len(files) - 1):
                    source_id = re.sub(r'[^\w]', '_', files[i])
                    target_id = re.sub(r'[^\w]', '_', files[i + 1])
                    diagram += f"    {source_id} -> {target_id} [style=dashed, label=\"{framework}\"];\n"
        
        diagram += "}"
        return diagram
    
    def create_api_diagram(self, parsed_data: Dict[str, Any]) -> str:
        """
        Create an API diagram showing endpoints and routes.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Diagram code in the specified format
        """
        if self.format == "mermaid":
            return self._create_api_diagram_mermaid(parsed_data)
        else:
            return self._create_api_diagram_graphviz(parsed_data)
    
    def generate_diagrams(self, parsed_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all diagrams for the repository.
        
        Args:
            parsed_data: Parsed repository data
            
        Returns:
            Dictionary mapping diagram types to diagram code
        """
        return {
            "architecture": self.create_architecture_diagram(parsed_data),
            "class": self.create_class_diagram(parsed_data),
            "dependency": self.create_dependency_diagram(parsed_data),
            "api": self.create_api_diagram(parsed_data),
        }


def generate_diagrams(parsed_data: Dict[str, Any], format: str = "mermaid", max_elements: int = 100) -> Dict[str, str]:
    """
    Generate diagrams for documentation.
    
    Args:
        parsed_data: Parsed repository data
        format: Output format ("mermaid" or "graphviz")
        max_elements: Maximum number of elements in a diagram
        
    Returns:
        Dictionary mapping diagram types to diagram code
    """
    generator = DiagramGenerator(format=format, max_elements=max_elements)
    return generator.generate_diagrams(parsed_data) 