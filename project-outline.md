# Ontario Building Code Chat Assistant

## Project Goals
1. Create a Streamlit-based conversational interface for the Ontario Building Code
2. Implement efficient text extraction and processing from the specified webpage
3. Utilize vector database (ChromaDB) for storing and retrieving relevant information
4. Provide real-time chat interactions using gpt-4o-mini
5. Implement basic security measures to control access
6. Maintain accurate token usage tracking and cost estimation

## Components
1. Web Scraping
   - Extract text from Ontario Building Code webpage (currently from https://www.ontario.ca/laws/regulation/120332/v25)
   - Parse all text content from the webpage

2. Text Processing
   - Chunk text into 1000 token segments with 500 token overlap
   - Prepare text for embedding
   - Enhanced query expansion (10 queries per user input)
   - Optimized context window management

3. Vector Database
   - Implement persistent ChromaDB for storing embeddings
   - Cache text content alongside embeddings
   - Store in data/vector_db directory
   - Efficient chunk retrieval with progress tracking
   - Persistent storage across application restarts

4. Chat Interface
   - Streamlit-based UI with modern design
   - OpenAI integration with gpt-4o-mini
   - Streaming response implementation
   - Interactive query expansion display
   - Progress bars for search operations
   - Chat history context size management
   - Source reference display
   - Real-time token usage tracking and cost estimation

5. Security Features
   - Dual authentication system:
     - Password-protected access with app password
     - OpenAI API key authentication for custom keys
   - Session-based authentication
   - Secure password hashing
   - Persistent authentication across page reloads
   - Dynamic API key management
   - API key validation system

6. Monitoring
   - Comprehensive Token Tracking:
     - Total processed tokens across all operations
     - Conversation tokens (excluding RAG context)
     - Document context tokens from RAG retrieval
     - Separate input/output token tracking
   - Token Counting Implementation:
     - Local token counting using tiktoken
     - Query expansion token tracking
     - RAG context token tracking
     - Chat completion token tracking
   - Cost Estimation:
     - Real-time cost calculation
     - Separate input/output token pricing
     - Cumulative session cost tracking
   - Display Features:
     - Token usage breakdown in sidebar
     - Cost breakdown by token type
     - Session total cost estimation
   - Performance Metrics:
     - Query expansion effectiveness
     - Context window optimization
     - API key usage tracking
