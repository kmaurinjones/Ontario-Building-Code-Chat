"""
Streamlit app for the Ontario Building Code Chat interface.
"""
import streamlit as st
from src.chat import ChatBot
from src.query_expander import QueryExpander
from src.database import VectorStore
import time
from typing import List, Dict
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Ontario Building Code Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def make_hash(password: str) -> str:
        """Create a hash of the password."""
        return hashlib.sha256(str.encode(password)).hexdigest()
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if make_hash(st.session_state["password"]) == make_hash(os.getenv("APP_PASSWORD")):
            st.session_state["password_correct"] = True
            # Save the hashed password in a cookie that expires in 7 days
            st.session_state["password_hash"] = make_hash(st.session_state["password"])
            del st.session_state["password"]  # Don't store the raw password
        else:
            st.session_state["password_correct"] = False
            if "password_hash" in st.session_state:
                del st.session_state["password_hash"]
            st.error("❌ Incorrect password. Please try again.")

    # Check if the user has already authenticated
    if "password_hash" in st.session_state:
        if st.session_state["password_hash"] == make_hash(os.getenv("APP_PASSWORD")):
            return True
        else:
            del st.session_state["password_hash"]
    
    # If not authenticated, show the password input
    if "password_correct" not in st.session_state:
        st.text_input(
            "Please enter the app password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Please enter the app password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    else:
        return True

if not check_password():
    st.stop()

@st.cache_resource
def initialize_vector_store():
    """Initialize and cache the vector store."""
    return VectorStore()

@st.cache_resource
def initialize_query_expander():
    """Initialize and cache the query expander."""
    return QueryExpander()

@st.cache_resource
def initialize_chatbot(_vector_store):
    """Initialize and cache the chatbot instance."""
    return ChatBot(vector_store=_vector_store)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize vector store first
if "vector_store" not in st.session_state:
    with st.spinner("Initializing vector database..."):
        st.session_state.vector_store = initialize_vector_store()

# Initialize chatbot with vector store
if "chatbot" not in st.session_state:
    with st.spinner("Initializing chatbot (this may take a few minutes on first run)..."):
        st.session_state.chatbot = initialize_chatbot(st.session_state.vector_store)

if "query_expander" not in st.session_state:
    with st.spinner("Setting up query expansion..."):
        st.session_state.query_expander = initialize_query_expander()

def get_relevant_chunks(query: str, expanded_queries: List[str], k: int = 3) -> List[str]:
    """
    Get relevant chunks from vector store using multiple queries.
    
    Parameters
    ----------
    query : str
        Original user query
    expanded_queries : List[str]
        List of expanded queries
    k : int, default=3
        Number of chunks to retrieve per query
        
    Returns
    -------
    List[str]
        List of relevant text chunks
    """
    all_chunks = []
    progress_text = "Searching through building code sections..."
    
    # Create a progress bar for search operations
    progress_bar = st.progress(0, text=progress_text)
    total_queries = len(expanded_queries) + 1  # +1 for original query
    
    # Search with all queries
    for i, q in enumerate([query] + expanded_queries):
        results = st.session_state.vector_store.query(
            query_texts=[q],
            n_results=k
        )
        all_chunks.extend(results['documents'][0])
        
        # Update progress
        progress = (i + 1) / total_queries
        progress_bar.progress(progress, text=f"{progress_text} ({i + 1}/{total_queries} queries)")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_chunks = []
    
    # Create a spinner for deduplication
    with st.spinner("Removing duplicate sections..."):
        for chunk in all_chunks:
            if chunk not in seen:
                seen.add(chunk)
                unique_chunks.append(chunk)
    
    # Clear the progress bar
    progress_bar.empty()
    
    return unique_chunks

def process_message(query: str):
    """Process user message and generate response."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Query expansion with spinner
        with st.spinner("Expanding your query into targeted search terms..."):
            expanded_queries = st.session_state.query_expander.generate(query)
        
        # Check if we got meaningful search queries (more than just the original query)
        has_meaningful_queries = len(expanded_queries) > 1 and expanded_queries != [query]
        
        if has_meaningful_queries:
            # Show expanded queries in a neat container
            with st.expander("🔍 Generated search queries", expanded=False):
                st.write("I've expanded your query into these specific search terms:")
                for i, q in enumerate(expanded_queries, 1):
                    st.markdown(f"**{i}.** {q}")
            
            # Get relevant chunks with progress bar (handled inside function)
            chunks = get_relevant_chunks(query, expanded_queries)
            
            if chunks:  # Only show if we found relevant sections
                # Calculate total words in chunks
                total_words = sum(len(chunk.split()) for chunk in chunks)
                
                # Show found sections
                with st.expander(f"📚 Relevant building code information ({total_words} words)", expanded=False):
                    for i, chunk in enumerate(chunks, 1):
                        st.markdown(f"**Section {i}**")
                        st.markdown(chunk)
                        if i < len(chunks):
                            st.divider()
                
                # Use chunks as context if we have them
                context = "\n\n".join(chunks)
            else:
                context = ""
        else:
            # No meaningful queries generated, skip search
            chunks = []
            context = ""
        
        # Prepare messages for chat
        messages = [
            {"role": "system", "content": st.session_state.chatbot.generate_system_prompt(context)},
            {"role": "user", "content": query}
        ]
        
        # Stream response
        with st.spinner("💭 Generating response..."):
            response = ""
            message_placeholder = st.empty()
            for chunk in st.session_state.chatbot.chat_stream(messages):
                response += chunk
                message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response)
    
    # Update chat history
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.markdown("# About")
    st.markdown(
        "This assistant helps you navigate the **Ontario Building Code (v25)**. "
        "Ask any question about building regulations, and I'll find relevant "
        "information from the official code. "
        "Currently, all information referenced can be found at this link:\n\n"
        "[Ontario Building Code](https://www.ontario.ca/laws/regulation/120332/v25)"
    )
    st.divider()
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Main content area
st.title("🏗️ Ontario Building Code Assistant")
st.markdown(
    "Ask questions about the Ontario Building Code, and I'll help you find the relevant information. "
    "I'll search through the code and provide accurate, sourced answers. \n\n"
    "*Always check the official code to verify the answer provided here.*"
)
st.divider()

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if query := st.chat_input("Ask about building regulations...", key="user_input"):
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        process_message(query)

print()