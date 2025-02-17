# Ontario Building Code Chat Assistant

## Project Goals
1. Create a Streamlit-based conversational interface for the Ontario Building Code
2. Implement efficient text extraction and processing from the specified webpage
3. Utilize vector database (ChromaDB) for storing and retrieving relevant information
4. Provide real-time chat interactions using GPT-4-mini
5. Implement basic security measures to control access

## Components
1. Web Scraping
   - Extract text from Ontario Building Code webpage (currently from https://www.ontario.ca/laws/regulation/120332/v25)
   - Parse all text content from the webpage

2. Text Processing
   - Chunk text into 20k character segments with 1k overlap
   - Prepare text for embedding
   - Query expansion for improved search relevance

3. Vector Database
   - Implement ChromaDB for storing embeddings
   - Cache text content alongside embeddings
   - Store in data/vector_db directory
   - Efficient chunk retrieval with progress tracking

4. Chat Interface
   - Streamlit-based UI with modern design
   - OpenAI integration with gpt-4o-mini
   - Streaming response implementation
   - Interactive query expansion display
   - Progress bars for search operations
   - Chat history context size management, to mitigate chat context window issues
   - Source reference display

5. Security Features
   - Password-protected access
   - Session-based authentication
   - Secure password hashing
   - Persistent authentication across page reloads
