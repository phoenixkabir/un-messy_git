"""
Sidebar component for the Streamlit application.
"""
import streamlit as st
import os

def sidebar():
    """Display sidebar with settings and options."""
    with st.sidebar:
        st.header("Settings")
        
        # Model settings
        st.subheader("LLM Settings")
        model_options = [
            "anthropic/claude-3-opus-20240229",
            "anthropic/claude-3-sonnet-20240229",
            "anthropic/claude-3-haiku-20240307",
            "openai/gpt-4-turbo-preview",
            "openai/gpt-4o",
            "openai/gpt-3.5-turbo",
        ]
        selected_model = st.selectbox(
            "LLM Model",
            options=model_options,
            index=1  # Default to Claude 3 Sonnet
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.1,
            help="Higher values make output more creative, lower values make it more deterministic."
        )
        
        # Diagram settings
        st.subheader("Diagram Settings")
        diagram_format = st.radio(
            "Diagram Format",
            options=["Mermaid", "Graphviz"],
            index=0,
            help="Select the format for generated diagrams."
        )
        
        max_diagram_elements = st.number_input(
            "Max Diagram Elements",
            min_value=10,
            max_value=500,
            value=100,
            step=10,
            help="Maximum number of elements to include in a diagram. Lower values create simpler diagrams."
        )
        
        # Documentation settings
        st.subheader("Documentation Settings")
        docs_format = st.radio(
            "Documentation Format",
            options=["Markdown", "HTML"],
            index=0,
            help="Select the format for generated documentation."
        )
        
        include_code_snippets = st.checkbox(
            "Include Code Snippets",
            value=True,
            help="Include relevant code snippets in the documentation."
        )
        
        # GitHub publishing
        st.subheader("GitHub Publishing")
        enable_github_push = st.checkbox(
            "Enable GitHub Publishing",
            value=False,
            help="Allow pushing generated documentation to a GitHub repository."
        )
        
        if enable_github_push:
            github_token_provided = os.environ.get("GITHUB_TOKEN", "") != ""
            if not github_token_provided:
                st.warning("GitHub token not found. Add it to your .env file to enable publishing.")
            
            github_repo_name = st.text_input(
                "Target Repository Name",
                value="docs-" + st.session_state.get("repository_name", "repo"),
                help="Name of the GitHub repository to push documentation to."
            )
        
        # About section
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            """
            AI Docs Generator creates comprehensive documentation and diagrams from GitHub repositories using AI.
            
            [View Source Code](https://github.com/yourusername/ai-docs-generator)
            """
        )
        
    # Return settings as a dictionary
    return {
        "model": selected_model,
        "temperature": temperature,
        "diagram_format": diagram_format.lower(),
        "max_diagram_elements": max_diagram_elements,
        "docs_format": docs_format.lower(),
        "include_code_snippets": include_code_snippets,
        "enable_github_push": enable_github_push,
        "github_repo_name": github_repo_name if enable_github_push else None,
    } 