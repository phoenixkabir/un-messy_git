"""
AI Docs Generator - Main Application
"""
import streamlit as st
import os
from dotenv import load_dotenv
import groq
import time
from app.agents.crew_definition import DocsGeneratorCrew
from app.ui.chat_interface import chat_interface
from app.github.github_utils import GithubRepositoryFetcher
from app.utils.file_browser import FileBrowser

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_api_key = os.environ.get("GROQ_API_KEY")
if groq_api_key:
    groq_client = groq.Client(api_key=groq_api_key)
else:
    st.error("GROQ_API_KEY not found in environment variables")

def generate_documentation(repo_url, selected_files, model_name, temperature):
    """
    Generate documentation using CrewAI or fallback to direct API calls.
    
    Args:
        repo_url: GitHub repository URL
        selected_files: List of files to include in documentation
        model_name: LLM model to use
        temperature: Temperature setting for LLM responses
        
    Returns:
        Generated documentation and diagrams
    """
    # Validate inputs
    if not selected_files:
        st.error("No files selected for documentation generation.")
        return {
            "documentation": "Error: No files were selected for documentation generation.",
            "diagrams": "No diagrams generated.",
            "plan": "No plan generated.",
            "analysis": "No analysis generated."
        }
    
    try:
        # Create crew
        crew = DocsGeneratorCrew(
            model=model_name,
            temperature=temperature,
            verbose=True
        )
        
        # Prepare repository data
        repository_data = {
            "url": repo_url,
            "files": selected_files
        }
        
        # Run the crew
        st.info("Generating documentation with CrewAI... This may take a few minutes.")
        result = crew.run(repository_data)
        return result
    except Exception as e:
        st.error(f"Error with CrewAI: {str(e)}")
        st.info("Falling back to direct documentation generation...")
        
        # Fallback to direct documentation generation using Groq API
        try:
            # Basic prompt for documentation
            prompt = f"""
            Generate documentation for the following GitHub repository: {repo_url}
            
            Files to include:
            {', '.join(selected_files)}
            
            Please include:
            1. Overview of the project
            2. Key components and their interactions
            3. API documentation (if applicable)
            4. Usage examples
            """
            
            response = groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            
            return {
                "documentation": response.choices[0].message.content,
                "diagrams": "No diagrams available in fallback mode.",
                "plan": "No plan available in fallback mode.",
                "analysis": "No detailed analysis available in fallback mode."
            }
        except Exception as fallback_error:
            return {
                "documentation": f"Error generating documentation: {str(fallback_error)}",
                "diagrams": "Error generating diagrams.",
                "plan": "Error generating plan.",
                "analysis": "Error generating analysis."
            }

def main():
    """Main application function."""
    st.set_page_config(page_title="AI Docs Generator", layout="wide")
    
    st.title("AI Docs Generator")
    st.write("Generate comprehensive documentation from your GitHub repositories.")
    
    # Initialize session state
    if "repository_fetcher" not in st.session_state:
        st.session_state.repository_fetcher = GithubRepositoryFetcher()
    
    if "file_browser" not in st.session_state:
        st.session_state.file_browser = FileBrowser()
    
    if "repo_files" not in st.session_state:
        st.session_state.repo_files = []
    
    if "documentation" not in st.session_state:
        st.session_state.documentation = ""
    
    if "diagrams" not in st.session_state:
        st.session_state.diagrams = ""
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("Repository Settings")
        
        # GitHub repository URL input
        repo_url = st.text_input("GitHub Repository URL", 
                                placeholder="https://github.com/username/repo",
                                key="repo_url_input")
        
        # Fetch repository button
        if st.button("Fetch Repository", key="fetch_repo_btn"):
            if repo_url:
                with st.spinner("Fetching repository..."):
                    try:
                        st.session_state.repo_files = st.session_state.repository_fetcher.fetch_repository(repo_url)
                        if st.session_state.repo_files:
                            st.success("Repository fetched successfully!")
                        else:
                            st.warning("No files found in the repository.")
                    except Exception as e:
                        st.error(f"Error fetching repository: {str(e)}")
            else:
                st.warning("Please enter a GitHub repository URL.")
        
        # File browser
        if st.session_state.repo_files:
            st.subheader("Select Files")
            # Display the file browser - selected files are stored in session state
            st.session_state.file_browser.display_file_browser(
                st.session_state.repo_files
            )
        
        # Model settings
        st.header("Model Settings")
        model_name = st.selectbox(
            "Model",
            ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            key="model_selectbox"
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1, key="temperature_slider")
        
        # Generate documentation button
        if st.button("Generate Documentation", key="generate_docs_btn"):
            selected_files = st.session_state.get("selected_file_paths", [])
            if repo_url and selected_files:
                with st.spinner("Generating documentation... This may take a few minutes."):
                    result = generate_documentation(
                        repo_url, 
                        selected_files,
                        model_name,
                        temperature
                    )
                    
                    st.session_state.documentation = result["documentation"]
                    st.session_state.diagrams = result["diagrams"]
                    st.session_state.plan = result.get("plan", "")
                    st.session_state.analysis = result.get("analysis", "")
                    
                    st.success("Documentation generated successfully!")
            else:
                if not repo_url:
                    st.warning("Please enter a GitHub repository URL.")
                if not selected_files:
                    st.warning("Please select at least one file to generate documentation.")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Documentation", "Diagrams", "Chat", "Plan", "Analysis"
    ])
    
    with tab1:
        if st.session_state.documentation:
            st.markdown(st.session_state.documentation)
        else:
            st.info("Documentation will appear here after generation.")
    
    with tab2:
        if st.session_state.diagrams:
            st.markdown(st.session_state.diagrams)
        else:
            st.info("Diagrams will appear here after generation.")
    
    with tab3:
        chat_interface()
    
    with tab4:
        if "plan" in st.session_state and st.session_state.plan:
            st.markdown(st.session_state.plan)
        else:
            st.info("Planning details will appear here after generation.")
    
    with tab5:
        if "analysis" in st.session_state and st.session_state.analysis:
            st.markdown(st.session_state.analysis)
        else:
            st.info("Code analysis will appear here after generation.")

if __name__ == "__main__":
    main() 