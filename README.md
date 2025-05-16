# AI Docs Generator

Generate comprehensive documentation from GitHub repositories using AI with CrewAI and Groq LLM integration.

## Features

- 🔍 **GitHub Repository Fetcher**: Fetch repositories from GitHub URLs
- 📂 **File Browser**: Browse and select files from repositories
- 📝 **Documentation Generation**: Generate comprehensive documentation using AI
- 📊 **Diagram Creation**: Automatically create architectural diagrams
- 💬 **Chat Interface**: Ask questions about the codebase

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-docs-generator.git
cd ai-docs-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```bash
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token  # Optional, for higher API rate limits
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Enter a GitHub repository URL in the sidebar.

3. Click "Fetch Repository" to retrieve the repository files.

4. Select files to include in the documentation.

5. Click "Generate Documentation" to create comprehensive documentation.

6. View the generated documentation, diagrams, and chat with the AI about the codebase.

## How It Works

AI Docs Generator uses a combination of technologies to generate documentation:

1. **CrewAI**: Utilizes a team of specialized AI agents to handle different aspects of documentation generation:
   - **Planner**: Analyzes repository structure and creates a documentation plan
   - **Code Analyzer**: Deeply understands code structure and functionality
   - **Documentation Writer**: Generates clear and comprehensive documentation
   - **Diagrammer**: Creates visual representations of the codebase

2. **Groq Integration**: Uses Groq's fast LLM API for responsive AI interactions.

3. **GitHub API**: Fetches repository files and metadata.

4. **Streamlit UI**: Provides an intuitive user interface for interacting with the application.

## Requirements

- Python 3.9+
- Groq API key
- GitHub token (optional)

## License

MIT 