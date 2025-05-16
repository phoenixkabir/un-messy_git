"""
Output section UI component.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_markdown(content: str) -> None:
    """
    Render markdown content with proper formatting.
    
    Args:
        content: Markdown content to render
    """
    st.markdown(content)


def render_diagram(diagram_code: str) -> None:
    """
    Render a diagram (Mermaid or Graphviz).
    
    Args:
        diagram_code: Diagram code in Mermaid or Graphviz format
    """
    if diagram_code.startswith("```mermaid"):
        # Extract just the mermaid code
        diagram_code = diagram_code.replace("```mermaid", "").replace("```", "").strip()
        st.markdown(f"```mermaid\n{diagram_code}\n```")
    elif "digraph G" in diagram_code:
        # Graphviz diagram
        from graphviz import Source
        st.graphviz_chart(diagram_code)
    else:
        # Just render as code
        st.code(diagram_code)


def render_statistics(statistics: Dict[str, Any]) -> None:
    """
    Render repository statistics.
    
    Args:
        statistics: Repository statistics
    """
    if not statistics:
        return
    
    st.subheader("Repository Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files", statistics.get("total_files", 0))
    
    with col2:
        st.metric("Lines of Code", statistics.get("total_loc", 0))
    
    with col3:
        languages = statistics.get("languages", {})
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
        st.metric("Primary Language", primary_language)
    
    # Languages breakdown
    if languages:
        st.subheader("Languages")
        
        # Convert to DataFrame for display
        language_data = [{"Language": lang, "Files": count} for lang, count in languages.items()]
        language_df = pd.DataFrame(language_data)
        
        # Sort by file count descending
        language_df = language_df.sort_values("Files", ascending=False).reset_index(drop=True)
        
        # Display as chart
        st.bar_chart(language_df.set_index("Language"))
    
    # File types breakdown
    file_types = statistics.get("file_types", {})
    if file_types:
        st.subheader("File Types")
        
        # Convert to DataFrame for display
        file_type_data = [{"Type": ftype, "Count": count} for ftype, count in file_types.items()]
        file_type_df = pd.DataFrame(file_type_data)
        
        # Sort by count descending
        file_type_df = file_type_df.sort_values("Count", ascending=False).reset_index(drop=True)
        
        # Display as chart
        st.bar_chart(file_type_df.set_index("Type"))


def output_section(documentation: Dict[str, Any], diagrams: Dict[str, str]) -> None:
    """
    Display documentation and diagrams.
    
    Args:
        documentation: Generated documentation
        diagrams: Generated diagrams
    """
    # Handle plan, if present
    if "plan" in documentation:
        with st.expander("Documentation Plan", expanded=False):
            st.json(documentation["plan"])
    
    # Display repository statistics if available
    if "statistics" in documentation:
        render_statistics(documentation["statistics"])
    
    # Display diagrams
    if diagrams:
        st.header("Diagrams")
        
        # Create tabs for different diagram types
        diagram_tabs = st.tabs([
            "Architecture", 
            "Class Hierarchy", 
            "Dependencies", 
            "API"
        ])
        
        # Architecture diagram
        with diagram_tabs[0]:
            if "architecture" in diagrams:
                render_diagram(diagrams["architecture"])
            else:
                st.info("No architecture diagram generated.")
        
        # Class diagram
        with diagram_tabs[1]:
            if "class" in diagrams:
                render_diagram(diagrams["class"])
            else:
                st.info("No class diagram generated.")
        
        # Dependency diagram
        with diagram_tabs[2]:
            if "dependency" in diagrams:
                render_diagram(diagrams["dependency"])
            else:
                st.info("No dependency diagram generated.")
        
        # API diagram
        with diagram_tabs[3]:
            if "api" in diagrams:
                render_diagram(diagrams["api"])
            else:
                st.info("No API diagram generated.")
    
    # Display documentation
    st.header("Documentation")
    
    # Extract the main documentation content
    if isinstance(documentation, str):
        # If documentation is a string, render it as markdown
        render_markdown(documentation)
    elif isinstance(documentation, dict):
        # If documentation has sections, create tabs
        if "overview" in documentation or "sections" in documentation:
            # Display overview first
            if "overview" in documentation:
                st.subheader("Overview")
                render_markdown(documentation["overview"])
            
            # Display sections
            if "sections" in documentation:
                sections = documentation["sections"]
                
                if isinstance(sections, dict):
                    # If sections is a dictionary, create tabs for each section
                    section_titles = list(sections.keys())
                    section_tabs = st.tabs(section_titles)
                    
                    for i, title in enumerate(section_titles):
                        with section_tabs[i]:
                            render_markdown(sections[title])
                elif isinstance(sections, list):
                    # If sections is a list, display each section with its title
                    for section in sections:
                        if isinstance(section, dict) and "title" in section and "content" in section:
                            st.subheader(section["title"])
                            render_markdown(section["content"])
        else:
            # If no specific structure, just render the documentation
            render_markdown(str(documentation))
    else:
        st.warning("No documentation generated.")
    
    # Download options
    st.header("Download")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "Download Documentation (Markdown)",
            data=str(documentation),
            file_name="documentation.md",
            mime="text/markdown",
        )
    
    with col2:
        # Combine diagrams into a single file
        diagrams_text = "\n\n".join([f"# {name.capitalize()} Diagram\n\n{code}" for name, code in diagrams.items()])
        st.download_button(
            "Download Diagrams",
            data=diagrams_text,
            file_name="diagrams.md",
            mime="text/markdown",
        ) 