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
from src.utils.token_counter import count_tokens
from openai import OpenAI

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
    """Returns `True` if the user had the correct password or provided a valid OpenAI API key."""
    
    def make_hash(password: str) -> str:
        """Create a hash of the password."""
        return hashlib.sha256(str.encode(password)).hexdigest()
    
    def validate_openai_key(api_key: str) -> bool:
        """Validate an OpenAI API key by attempting to create a client."""
        try:
            client = OpenAI(api_key=api_key)
            # Try a minimal API call to verify the key
            client.models.list()
            return True
        except:
            return False
    
    def password_entered():
        """Checks whether a password entered by the user is correct or if it's a valid OpenAI API key."""
        input_text = st.session_state["password"]
        
        # First check if it's the app password
        if make_hash(input_text) == make_hash(os.getenv("APP_PASSWORD")):
            st.session_state["password_correct"] = True
            st.session_state["password_hash"] = make_hash(input_text)
            del st.session_state["password"]
            return
        
        # If not the password, try validating as OpenAI API key
        if validate_openai_key(input_text):
            st.session_state["password_correct"] = True
            st.session_state["using_custom_api_key"] = True
            st.session_state["custom_api_key"] = input_text
            del st.session_state["password"]
            # Update the OpenAI client with the new API key
            os.environ["OPENAI_API_KEY"] = input_text
            return
        
        # If neither password nor valid API key
        st.session_state["password_correct"] = False
        if "password_hash" in st.session_state:
            del st.session_state["password_hash"]
        st.error("❌ Invalid input. Please enter either the app password or a valid OpenAI API key.")

    # Check if the user has already authenticated
    if "password_hash" in st.session_state:
        if st.session_state["password_hash"] == make_hash(os.getenv("APP_PASSWORD")):
            return True
        else:
            del st.session_state["password_hash"]
    
    # If not authenticated, show the password input
    if "password_correct" not in st.session_state:
        st.text_input(
            "Please enter the app password or your OpenAI API key", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Please enter the app password or your OpenAI API key", 
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
    
# Initialize token counters
if "total_prompt_tokens" not in st.session_state:
    st.session_state.total_prompt_tokens = 0
if "total_completion_tokens" not in st.session_state:
    st.session_state.total_completion_tokens = 0
if "total_processed_tokens" not in st.session_state:
    st.session_state.total_processed_tokens = 0
if "current_conversation_tokens" not in st.session_state:
    st.session_state.current_conversation_tokens = 0

# Initialize token display placeholder in session state
if "token_display" not in st.session_state:
    st.session_state.token_display = None

# Initialize vector store first
if "vector_store" not in st.session_state:
    with st.spinner("Initializing vector database..."):
        st.session_state.vector_store = initialize_vector_store()

# Initialize chatbot with vector store
if "chatbot" not in st.session_state:
    with st.spinner("Initializing chatbot (this may take a few minutes on first run)..."):
        st.session_state.chatbot = initialize_chatbot(st.session_state.vector_store)

# Initialize query expander
if "query_expander" not in st.session_state:
    with st.spinner("Setting up query expansion..."):
        st.session_state.query_expander = initialize_query_expander()

def update_token_display():
    """Update the token usage display in the sidebar."""
    # Calculate costs
    prompt_cost = (st.session_state.total_prompt_tokens / 1_000_000) * 0.15
    completion_cost = (st.session_state.total_completion_tokens / 1_000_000) * 0.60
    total_cost = prompt_cost + completion_cost
    
    # Update the token display
    if st.session_state.token_display is not None:
        st.session_state.token_display.empty()  # Clear previous content
        st.session_state.token_display.markdown(f"""
        ### Token Usage
        
        **Total Processed Tokens:** {st.session_state.total_processed_tokens:,}  
        **Current Conversation Tokens:** {st.session_state.current_conversation_tokens:,}  
        
        **Input Tokens:** {st.session_state.total_prompt_tokens:,}  
        **Output Tokens:** {st.session_state.total_completion_tokens:,}  
        **Total Tokens:** {st.session_state.total_prompt_tokens + st.session_state.total_completion_tokens:,}
        
        **Estimated Cost:** ${total_cost:.4f} USD
        - Input: ${prompt_cost:.4f}
        - Output: ${completion_cost:.4f}
        """)

# Initialize the sidebar
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
        st.session_state.total_prompt_tokens = 0
        st.session_state.total_completion_tokens = 0
        st.session_state.total_processed_tokens = 0
        st.session_state.current_conversation_tokens = 0
        st.rerun()
    
    st.divider()
    # Create a single empty element for token display
    st.session_state.token_display = st.empty()
    # Initial token display
    update_token_display()

def get_relevant_chunks(query: str, expanded_queries: List[str], k: int = 2) -> List[str]:
    """
    Get relevant chunks from vector store using multiple queries.
    
    Parameters
    ----------
    query : str
        Original user query
    expanded_queries : List[str]
        List of expanded queries
    k : int, default=2
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
    
    # Maximum tokens for context (leaving room for the rest of the prompt)
    MAX_CONTEXT_TOKENS = 100000  # This leaves ~28k tokens for the rest of the conversation
    current_tokens = 0
    
    # Search with all queries
    for i, q in enumerate([query] + expanded_queries):
        results = st.session_state.vector_store.query(
            query_texts=[q],
            n_results=k
        )
        
        # Add chunks while respecting token limit
        for chunk in results['documents'][0]:
            # Skip if we've already seen this chunk
            if chunk in all_chunks:
                continue
                
            # Check token count
            chunk_tokens = count_tokens(chunk)
            if current_tokens + chunk_tokens > MAX_CONTEXT_TOKENS:
                # Stop adding chunks if we'd exceed the limit
                progress_bar.empty()
                return all_chunks
                
            all_chunks.append(chunk)
            current_tokens += chunk_tokens
        
        # Update progress
        progress = (i + 1) / total_queries
        progress_bar.progress(progress, text=f"{progress_text} ({i + 1}/{total_queries} queries)")
    
    # Clear the progress bar
    progress_bar.empty()
    
    return all_chunks

def process_message(query: str):
    """Process user message and generate response."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get conversation history (excluding the current query)
        conversation_history = st.session_state.messages[:-1] if len(st.session_state.messages) > 0 else None
        
        # Query expansion with spinner
        with st.spinner("Expanding your query into targeted search terms..."):
            expanded_queries, query_tokens = st.session_state.query_expander.generate(
                query=query,
                conversation_history=conversation_history,
                n_queries=4  # Reduced from 9 to 4 to prevent context overload
            )
            # Update token counts
            st.session_state.total_prompt_tokens += query_tokens["prompt_tokens"]
            st.session_state.total_completion_tokens += query_tokens["completion_tokens"]
            st.session_state.total_processed_tokens += query_tokens["total_tokens"]
            update_token_display()  # Update display after query expansion
        
        # Check if we got meaningful search queries (more than just the original query)
        has_meaningful_queries = len(expanded_queries) > 1 and expanded_queries != [query]
        
        if has_meaningful_queries:
            # Show expanded queries in a neat container
            with st.expander("🔍 Generated search queries", expanded=False):
                st.write("I've expanded your query into these specific search terms:")
                for i, q in enumerate(expanded_queries, 1):
                    st.markdown(f"**{i}.** {q}")
            
            # Get relevant chunks with progress bar (handled inside function)
            chunks = get_relevant_chunks(
                query=query, 
                expanded_queries=expanded_queries, 
                k=3 # get top 5 chunks per query (before deduplication)
            )
            
            if chunks:  # Only show if we found relevant sections
                # Calculate total words in chunks
                total_words = sum(len(chunk.split()) for chunk in chunks)
                
                # Count tokens in chunks and add to total processed
                chunk_tokens = sum(count_tokens(chunk) for chunk in chunks)
                st.session_state.total_processed_tokens += chunk_tokens
                
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
                chunk_tokens = 0
        else:
            # No meaningful queries generated, skip search
            chunks = []
            context = ""
            chunk_tokens = 0
        
        # Prepare messages for chat
        messages = [
            {"role": "system", "content": st.session_state.chatbot.generate_system_prompt(context)},
            {"role": "user", "content": query}
        ]
        
        # Calculate current conversation tokens (excluding RAG context)
        conversation_tokens = sum(count_tokens(msg["content"]) for msg in st.session_state.messages)
        conversation_tokens += count_tokens(query)  # Add current query
        st.session_state.current_conversation_tokens = conversation_tokens
        
        # Stream response
        with st.spinner("💭 Generating response..."):
            response = ""
            message_placeholder = st.empty()
            last_chunk = None
            
            # Create a list to store all chunks
            chunks = []
            for chunk in st.session_state.chatbot.chat_stream(messages):
                chunks.append(chunk)
                if isinstance(chunk, dict):  # This is the token usage info
                    last_chunk = chunk
                    print(f"Token usage received: {chunk}")  # Debug log
                else:  # This is a text chunk
                    response += chunk
                    message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response)
            
            # Update token counts if we got usage info
            if last_chunk and isinstance(last_chunk, dict):
                print(f"Before update - Prompt tokens: {st.session_state.total_prompt_tokens}, Completion tokens: {st.session_state.total_completion_tokens}")  # Debug log
                st.session_state.total_prompt_tokens += last_chunk["prompt_tokens"]
                st.session_state.total_completion_tokens += last_chunk["completion_tokens"]
                st.session_state.total_processed_tokens += last_chunk["total_tokens"]
                
                # Update current conversation tokens with the response
                st.session_state.current_conversation_tokens += count_tokens(response)
                
                print(f"After update - Prompt tokens: {st.session_state.total_prompt_tokens}, Completion tokens: {st.session_state.total_completion_tokens}")  # Debug log
                update_token_display()  # Update display after chat response

    # Update chat history
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "assistant", "content": response})

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
print()
