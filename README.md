# Ontario Building Code Chat Assistant

An interactive AI-powered chat interface for navigating and understanding the Ontario Building Code (v25). This application uses advanced natural language processing and vector search to provide accurate, context-aware responses to questions about building regulations in Ontario.

## 🌟 Features

- **Interactive Chat Interface**: Modern Streamlit-based UI with real-time response streaming
- **Smart Search**: 
  - Query expansion for improved search relevance
  - Vector-based semantic search using ChromaDB
  - Progress tracking for search operations
- **Context-Aware Responses**: Utilizes gpt-4o-mini for generating accurate, contextual answers
- **Flexible Authentication**:
  - Password-protected access with app password
  - OpenAI API key authentication for custom billing
  - Session persistence for both methods
- **Source References**: Displays relevant sections from the building code
- **User-Friendly Features**:
  - Expandable search query display
  - Progress bars for operations
  - Word count for retrieved sections
  - Chat history management
  - Token usage and cost tracking

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kmaurinjones/Ontario-Building-Code-Chat.git
cd Ontario-Building-Code-Chat
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies using UV:
```bash
uv pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration:
- `OPENAI_API_KEY`: Your OpenAI API key (default key for app password users)
- `APP_PASSWORD`: Password for accessing the application

### Running the Application

Start the Streamlit app:
```bash
uv run streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

## 🔒 Security

- Dual authentication system:
  - App password authentication (uses default API key)
  - OpenAI API key authentication (uses user's API key)
- Session-based authentication
- Secure password hashing
- Persistent authentication across page reloads
- Dynamic API key management
- API key validation

## 📚 Data Source

Currently references Ontario Building Code v25 from:
[https://www.ontario.ca/laws/regulation/120332/v25](https://www.ontario.ca/laws/regulation/120332/v25)

## 🛠️ Project Structure

```
Ontario-Building-Code-Chat/
├── app.py              # Main Streamlit application
├── src/               # Source code modules
├── data/              # Vector database and data storage
├── setup/             # Setup and initialization scripts
├── requirements.txt   # Project dependencies
└── .env              # Environment variables
```

## ⚠️ Disclaimer

This tool is designed to assist in navigating the Ontario Building Code. Always verify information with the official building code documentation for critical decisions.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Changelog

See [changelog.md](changelog.md) for a detailed history of changes and updates.