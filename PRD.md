# AI Docs Generator - Product Requirements Document

## Project Overview
AI Docs Generator is a DevRel-focused tool that leverages artificial intelligence to automatically generate comprehensive documentation from GitHub repositories. The tool aims to help developers quickly understand large codebases by providing auto-generated documentation, diagrams, and an interactive chat interface.

## Problem Statement
Developers often struggle with understanding large, unfamiliar codebases, which can be time-consuming and frustrating. Existing documentation is frequently outdated or incomplete. A tool that can automatically generate documentation and visualizations from code would save significant time and improve developer productivity.

## Target Users
- Developer Relations professionals
- New developers onboarding to existing projects
- Technical leads managing legacy codebases
- Open source contributors
- Technical documentation writers

## Core Features

### 1. GitHub Repository Input
- Accept public GitHub repository URLs
- Support repository upload functionality
- Allow selection of specific files or directories within the repository

### 2. Auto-generated Documentation
- Generate comprehensive markdown documentation
- Create architecture diagrams showing system components and relationships
- Produce flow diagrams illustrating process and data flows
- Generate entity-relationship diagrams for database schemas
- Provide service/API summaries with endpoints, parameters, and responses

### 3. Interactive Chat Interface
- Allow natural language queries about the codebase
- Support specific queries like "Explain file X" or "Draw the DB schema"
- Provide context-aware answers based on the analyzed codebase

### 4. Optional Features
- Voice input for queries
- Push generated documentation to a new GitHub repository
- Export documentation in various formats (PDF, HTML, etc.)
- Custom documentation templates

## Technical Requirements

### UI/Frontend
- Streamlit-based web interface
- Responsive design for desktop and tablet
- Clear visualization of generated diagrams
- Interactive file browser for repository exploration

### Backend Processing
- LLM integration via OpenRouter API (with Claude/Sonar/Ollama options)
- Agent framework implementation (CrewAI or LangGraph)
- Efficient code parsing system (Tree-sitter/AST/GitHub API)
- Diagram generation (Mermaid/Graphviz/diagrams Python library)
- GitHub integration via PyGitHub or gh CLI

### Performance Requirements
- Handle repositories up to 100MB in size
- Generate basic documentation within 5 minutes for medium-sized repos
- Support concurrent users on shared instances
- Implement caching for faster repeated analysis

## User Flow
1. User enters GitHub repository URL or uploads repository files
2. System analyzes the repository structure
3. User selects documentation scope (full repo or specific files/directories)
4. System generates initial documentation and diagrams
5. User can query the system about specific aspects of the code
6. User can export or publish the generated documentation

## Success Metrics
- Documentation accuracy (compared to human-written docs)
- Processing time (target: <5 minutes for medium repos)
- User satisfaction (measured via feedback)
- Adoption rate (number of unique repositories processed)
- Community engagement (GitHub stars, shares, feedback)

## Timeline and Milestones
- Phase 1: Core repository parsing and basic documentation generation
- Phase 2: Diagram generation and enhanced documentation
- Phase 3: Interactive chat interface
- Phase 4: Optional features (voice input, GitHub publishing)

## Constraints and Limitations
- LLM token usage costs for large repositories
- Processing time for very large codebases
- Complexity in handling diverse programming languages
- Accuracy limitations in inferring architecture from code alone

## Future Enhancements
- Support for private repositories with authentication
- Multi-language support for documentation
- Custom documentation templates
- Integration with CI/CD pipelines for automatic doc updates
- Specialized parsers for popular frameworks (React, Django, etc.) 