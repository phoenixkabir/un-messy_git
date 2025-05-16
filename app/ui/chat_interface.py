"""
Chat interface for interacting with codebase documentation.
"""
import streamlit as st
import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def ask_llm(prompt, context="", model_name="llama3-70b-8192", temperature=0.2):
    """
    Ask a question to the LLM.
    
    Args:
        prompt: User's question
        context: Additional context for the question
        model_name: LLM model to use
        temperature: Temperature setting for LLM responses
        
    Returns:
        LLM response
    """
    try:
        # Initialize Groq client
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return "Error: GROQ_API_KEY not found in environment variables"
        
        groq_client = groq.Client(api_key=groq_api_key)
        
        # Create system message with context if provided
        system_message = """You are a helpful AI assistant specialized in explaining code and documentation.
        Answer questions about the codebase based on the provided context and documentation."""
        
        if context:
            system_message += f"\n\nContext about the codebase:\n{context}"
        
        # Call the Groq API
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with Groq API: {str(e)}"

def chat_interface():
    """
    Display chat interface for interacting with the documentation.
    """
    st.header("Chat with your Codebase")
    st.write("Ask questions about the code and documentation.")
    
    # Initialize chat history in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about your code...", key="chat_input")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get context from session state
        context = ""
        if "documentation" in st.session_state and st.session_state.documentation:
            context += f"Documentation:\n{st.session_state.documentation}\n\n"
        
        if "plan" in st.session_state and st.session_state.plan:
            context += f"Plan:\n{st.session_state.plan}\n\n"
        
        if "analysis" in st.session_state and st.session_state.analysis:
            context += f"Analysis:\n{st.session_state.analysis}\n\n"
        
        # Display assistant thinking
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                model_name = "llama3-70b-8192"  # Default model
                if "model_name" in st.session_state:
                    model_name = st.session_state.model_name
                
                response = ask_llm(
                    user_input, 
                    context=context,
                    model_name=model_name,
                    temperature=0.2
                )
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response}) 