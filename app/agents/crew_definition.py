"""
CrewAI crew definition for the AI Docs Generator.
"""
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from typing import List, Dict, Any, Optional, Set
import os
import groq
from langchain.llms.base import LLM
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom LLM class to integrate direct Groq client
class GroqLLM(LLM):
    """LLM wrapper for Groq API."""
    
    client: Any = None
    model_name: str = "llama3-70b-8192"
    temperature: float = 0.2
    api_key: str = Field(default="")
    
    def __init__(self, model_name: str, temperature: float):
        """Initialize with model name and Groq API key."""
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = os.environ.get("GROQ_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = groq.Client(api_key=self.api_key)
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "groq"
    
    def _call(self, prompt: str, **kwargs) -> str:
        """Call the Groq API and return the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with Groq API: {str(e)}"

class DocsGeneratorCrew:
    """
    CrewAI crew for generating documentation from code repositories.
    
    The crew consists of these specialized agents:
    - Planner: Analyzes the repository structure and creates an execution plan
    - CodeAnalyzer: Parses and understands code files in detail
    - DocWriter: Generates comprehensive documentation from code analysis
    - Diagrammer: Creates visual representations of the codebase
    """
    
    def __init__(
        self, 
        model: str = "llama3-70b-8192",
        temperature: float = 0.2,
        verbose: bool = False,
        code_parser_tools: Optional[List[Tool]] = None,
        github_tools: Optional[List[Tool]] = None,
        diagram_tools: Optional[List[Tool]] = None,
    ):
        """
        Initialize the DocsGeneratorCrew.
        
        Args:
            model: LLM model to use for agents
            temperature: Temperature setting for LLM responses
            verbose: Whether to enable verbose logging
            code_parser_tools: Tools for parsing code
            github_tools: Tools for GitHub interactions
            diagram_tools: Tools for diagram generation
        """
        self.model_name = model
        self.temperature = temperature
        self.verbose = verbose
        self.code_parser_tools = code_parser_tools or []
        self.github_tools = github_tools or []
        self.diagram_tools = diagram_tools or []
        
        # Initialize Groq LLM
        self.groq_llm = GroqLLM(model_name=self.model_name, temperature=self.temperature)
        
        # Initialize agents
        self.planner = self._create_planner_agent()
        self.code_analyzer = self._create_code_analyzer_agent()
        self.doc_writer = self._create_doc_writer_agent()
        self.diagrammer = self._create_diagrammer_agent()
        
        # Create the crew with more limited, focused tasks to avoid timeouts
        try:
            self.crew = Crew(
                agents=[
                    self.planner,
                    self.code_analyzer,
                    self.doc_writer,
                    self.diagrammer
                ],
                tasks=self._create_tasks(),
                verbose=self.verbose,
                process=Process.sequential,  # Sequential is more reliable
                max_rpm=10,  # Limit requests per minute to avoid rate limits
                max_execution_time=300  # 5 minutes max per task
            )
        except TypeError:
            # Fallback to basic creation if those parameters aren't supported
            self.crew = Crew(
                agents=[
                    self.planner,
                    self.code_analyzer,
                    self.doc_writer,
                    self.diagrammer
                ],
                tasks=self._create_tasks(),
                verbose=self.verbose,
                process=Process.sequential  # Sequential is more reliable
            )
    
    def _create_planner_agent(self) -> Agent:
        """Create the Planner agent."""
        return Agent(
            role="Repository Planner",
            goal="Analyze repository structure and create an optimal documentation plan",
            backstory="""You are an expert software architect who can quickly understand 
            complex codebases and create efficient plans for documentation. You have
            years of experience working with different programming languages and frameworks,
            and you know how to identify important components and relationships.""",
            verbose=self.verbose,
            allow_delegation=True,
            tools=self.github_tools,
            llm=self.groq_llm
        )
    
    def _create_code_analyzer_agent(self) -> Agent:
        """Create the Code Analyzer agent."""
        return Agent(
            role="Code Analyzer",
            goal="Deeply understand code structure, patterns, and functionality",
            backstory="""You are a senior code analyst with expertise in multiple programming 
            languages. You can parse complex code, identify design patterns, understand class
            hierarchies, and extract the essential functionality. You're known for your 
            ability to simplify complex implementations and explain them clearly.""",
            verbose=self.verbose,
            allow_delegation=False,
            tools=self.code_parser_tools,
            llm=self.groq_llm
        )
    
    def _create_doc_writer_agent(self) -> Agent:
        """Create the Documentation Writer agent."""
        creativity_llm = GroqLLM(
            model_name=self.model_name,
            temperature=self.temperature + 0.1
        )
        
        return Agent(
            role="Documentation Writer",
            goal="Generate clear, comprehensive, and well-structured documentation",
            backstory="""You are a technical documentation expert who knows how to create
            documentation that's both comprehensive and easy to understand. You have a
            talent for explaining complex technical concepts in accessible ways, and you
            know how to structure documentation to make it easy to navigate and reference.""",
            verbose=self.verbose,
            allow_delegation=False,
            llm=creativity_llm
        )
    
    def _create_diagrammer_agent(self) -> Agent:
        """Create the Diagram Generator agent."""
        return Agent(
            role="Diagram Generator",
            goal="Create visual representations of code architecture and relationships",
            backstory="""You are a visualization expert who can translate complex code 
            structures into clear, informative diagrams. You have a deep understanding of
            various diagram types (UML, ER, flow, etc.) and know which type is most 
            appropriate for different aspects of a codebase. Your diagrams help developers
            quickly understand system architecture.""",
            verbose=self.verbose,
            allow_delegation=False,
            tools=self.diagram_tools,
            llm=self.groq_llm
        )
    
    def _create_tasks(self) -> List[Task]:
        """Create the tasks for the crew."""
        planning_task = Task(
            description="""
            Analyze the repository structure and create a comprehensive documentation plan.
            
            1. Identify the main components, modules, and services
            2. Determine important relationships between components
            3. Prioritize which parts need detailed documentation
            4. Create a documentation outline with sections and subsections
            5. Specify which diagrams would be most useful
            
            Your output should be a structured plan that other agents can follow to
            generate comprehensive documentation.
            """,
            agent=self.planner,
            expected_output="A structured documentation plan in JSON format"
        )
        
        code_analysis_task = Task(
            description="""
            Analyze the code files according to the documentation plan.
            
            For each component identified in the plan:
            1. Parse the code to understand its structure and functionality
            2. Identify key classes, functions, and methods
            3. Determine relationships with other components
            4. Note any design patterns or architectural approaches
            5. Extract API endpoints and parameters (if applicable)
            
            Your output should be a detailed analysis that the Documentation Writer
            can use to create accurate documentation.
            """,
            agent=self.code_analyzer,
            expected_output="A detailed code analysis in JSON format",
            context=[planning_task]
        )
        
        documentation_task = Task(
            description="""
            Create comprehensive documentation based on the code analysis.
            
            Follow the documentation plan and use the code analysis to:
            1. Write an overview of the project structure
            2. Document each component with clear explanations
            3. Describe key relationships between components
            4. Provide examples of usage where appropriate
            5. Include API references if applicable
            
            Format the documentation as markdown with clear sections and headers.
            """,
            agent=self.doc_writer,
            expected_output="Complete markdown documentation",
            context=[planning_task, code_analysis_task]
        )
        
        diagram_task = Task(
            description="""
            Create visual diagrams based on the code analysis and documentation plan.
            
            Generate the following types of diagrams as specified in the plan:
            1. Architecture diagrams showing high-level components
            2. Flow diagrams for key processes
            3. Entity-relationship diagrams if there's a database
            4. Class or component relationship diagrams
            
            Use the appropriate format (Mermaid or Graphviz) and ensure diagrams are
            clear, informative, and not too cluttered.
            """,
            agent=self.diagrammer,
            expected_output="Diagram specifications in Mermaid or Graphviz format",
            context=[planning_task, code_analysis_task]
        )
        
        return [planning_task, code_analysis_task, documentation_task, diagram_task]
    
    def run(self, repository_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the documentation generation process.
        
        Args:
            repository_data: Dictionary containing repository information and code content
            
        Returns:
            Dictionary containing generated documentation and diagrams
        """
        try:
            # Simplify task execution to avoid timeouts
            repository_url = repository_data.get("url", "")
            files = repository_data.get("files", [])
            
            # Create a simplified repository context
            repository_context = f"""
            Repository URL: {repository_url}
            
            Files to document:
            {', '.join(files)}
            """
            
            # Keep tasks more focused with smaller scopes
            simplified_tasks = self._create_simplified_tasks(repository_context)
            
            # Try to update crew with simplified tasks if method exists
            try:
                self.crew.tasks = simplified_tasks
            except (AttributeError, TypeError):
                # Fallback: create a new crew with the simplified tasks
                self.crew = Crew(
                    agents=[self.planner, self.code_analyzer, self.doc_writer, self.diagrammer],
                    tasks=simplified_tasks,
                    verbose=self.verbose,
                    process=Process.sequential
                )
            
            # Run without signal-based timeout (which doesn't work in Streamlit threads)
            try:
                # We'll just use a more direct, simplified approach instead
                result = self.crew.kickoff()
            except Exception as exec_error:
                # Handle execution errors
                error_str = str(exec_error)
                if "Agent stopped due to iteration limit" in error_str or "time limit" in error_str:
                    # For iteration limit errors, try to extract any partial results
                    # Look for content after the error message
                    # This is a best-effort attempt to salvage partial results
                    partial_content = error_str.split("Agent stopped due")[-1]
                    if len(partial_content) > 100:  # If we have meaningful content
                        return {
                            "documentation": f"Agent reached its limits while processing. Here's what was generated:\n\n{partial_content}",
                            "diagrams": "Incomplete due to agent limits.",
                            "plan": "Incomplete due to agent limits.",
                            "analysis": "Incomplete due to agent limits."
                        }
                    else:
                        return {
                            "documentation": f"Agent reached its limits without producing usable results. Please try with fewer files.",
                            "diagrams": "Not generated due to agent limits.",
                            "plan": "Not generated due to agent limits.",
                            "analysis": "Not generated due to agent limits."
                        }
                else:
                    # Re-raise for the outer exception handler
                    raise
            
            # Handle different return types from different CrewAI versions
            if isinstance(result, str):
                # Some versions return a string (likely the final task's output)
                documentation = result
                return {
                    "documentation": documentation,
                    "diagrams": "Diagrams not available in this CrewAI version.",
                    "plan": "Planning details not available in this CrewAI version.",
                    "analysis": "Code analysis not available in this CrewAI version."
                }
            elif isinstance(result, dict):
                # Extract the results from newer versions that return a dictionary
                planning_result = None
                analysis_result = None
                docs_result = None
                diagram_result = None
                
                for task_id, task_result in result.items():
                    if isinstance(task_result, dict):
                        # Structure from newer versions
                        if "planning" in task_id.lower():
                            planning_result = task_result.get("output", "")
                        elif "analysis" in task_id.lower() or "code" in task_id.lower():
                            analysis_result = task_result.get("output", "")
                        elif "documentation" in task_id.lower() or "doc" in task_id.lower():
                            docs_result = task_result.get("output", "")
                        elif "diagram" in task_id.lower():
                            diagram_result = task_result.get("output", "")
                    elif isinstance(task_result, str):
                        # Simple string result keyed by task ID
                        if "planning" in task_id.lower():
                            planning_result = task_result
                        elif "analysis" in task_id.lower() or "code" in task_id.lower():
                            analysis_result = task_result
                        elif "documentation" in task_id.lower() or "doc" in task_id.lower():
                            docs_result = task_result
                        elif "diagram" in task_id.lower():
                            diagram_result = task_result
                return {
                    "documentation": docs_result or "No documentation generated.",
                    "diagrams": diagram_result or "No diagrams generated.",
                    "plan": planning_result or "No plan generated.",
                    "analysis": analysis_result or "No analysis generated."
                }
            elif isinstance(result, list):
                # Some versions might return a list of results in order of tasks
                if len(result) >= 4:
                    return {
                        "documentation": result[2] or "No documentation generated.",  # Assuming doc writer is 3rd
                        "diagrams": result[3] or "No diagrams generated.",  # Assuming diagrammer is 4th
                        "plan": result[0] or "No plan generated.",  # Assuming planner is 1st
                        "analysis": result[1] or "No analysis generated."  # Assuming analyzer is 2nd
                    }
                else:
                    return {
                        "documentation": result[-1] if result else "No documentation generated.",
                        "diagrams": "No diagrams available in this CrewAI version.",
                        "plan": "No plan available in this CrewAI version.",
                        "analysis": "No analysis available in this CrewAI version."
                    }
            else:
                # Unknown return type, just convert to string for documentation
                documentation = str(result)
                return {
                    "documentation": documentation,
                    "diagrams": "Diagrams not available for this result type.",
                    "plan": "Planning details not available for this result type.",
                    "analysis": "Code analysis not available for this result type."
                }
        except Exception as e:
            # Fallback to direct documentation generation
            return {
                "documentation": f"Error generating documentation with CrewAI: {str(e)}",
                "diagrams": "Error generating diagrams.",
                "plan": "Error generating plan.",
                "analysis": "Error generating analysis."
            }

    def _create_simplified_tasks(self, repository_context: str) -> List[Task]:
        """
        Create simplified tasks with smaller scopes to avoid timeouts.
        
        Args:
            repository_context: Context about the repository
            
        Returns:
            List of simplified tasks
        """
        # Documentation task only - ultra simplified to avoid timeouts
        documentation_task = Task(
            description=f"""
            {repository_context}
            
            Generate basic documentation for the provided repository files. Keep your analysis brief and focused.
            
            For each main file:
            - What is its purpose?
            - What are its key functions/classes?
            - How does it connect to other components?
            
            Format as simple markdown. IMPORTANT: Keep your response brief and avoid deep analysis to prevent timeouts.
            Focus on generating a useful overview rather than comprehensive documentation.
            """,
            agent=self.doc_writer,
            expected_output="Basic markdown documentation focusing on the most important aspects of the codebase",
            max_iterations=3  # Limit iterations to avoid timeouts
        )
        
        return [documentation_task] 