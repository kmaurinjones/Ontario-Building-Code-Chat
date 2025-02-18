# Changelog

## [0.2.3] - 20240320163000
### Added
- Comprehensive token counting system:
  - Total processed tokens tracking
  - Conversation tokens tracking (excluding RAG)
  - Document context tokens tracking
  - Separate input/output token tracking
- Local token counting implementation:
  - Query expansion token tracking
  - RAG context token tracking
  - Chat completion token tracking
- Enhanced cost estimation:
  - Real-time calculation
  - Separate input/output pricing
  - Cumulative session tracking
- Updated token display in sidebar:
  - Token usage breakdown
  - Cost breakdown by token type
  - Session total cost estimation

### Changed
- Removed dependency on OpenAI API token counting
- Improved token counting accuracy
- Enhanced cost estimation precision

### To Do
- Add token usage analytics over time
- Implement token usage optimization suggestions
- Add token usage limits and warnings

## [0.2.2] - 20240320153000
### Added
- Dual authentication system:
  - Support for app password authentication
  - Support for custom OpenAI API key authentication
- Dynamic API key management for cost allocation
- Validation system for OpenAI API keys
- Automatic API key switching mechanism

### Changed
- Updated authentication UI to support both password and API key input
- Modified OpenAI client initialization to use custom API keys when provided
- Enhanced error messaging for invalid credentials

### To Do
- Implement rate limiting
- Add user session analytics
- Enhance error handling for edge cases
- Add support for multiple building code versions

## [0.2.1] - 20240320143000
### Changed
- Optimized text chunking parameters:
  - Default chunk size reduced to 1000 tokens
  - Overlap increased to 500 tokens
- Upgraded to gpt-4o-mini model for improved performance
- Added cumulative session input/output token counting + price estimation and display in sidebar

## [0.2.0] - 20240319180000
### Added
- Password protection system with session persistence
- Secure password hashing using SHA-256
- Query expansion functionality
- Progress tracking for search operations
- Interactive UI elements:
  - Expandable search query display
  - Progress bars for operations
  - Word count for retrieved sections
- Source reference display
- Chat history management with clear functionality

### Changed
- Enhanced UI with modern design elements
- Improved error handling and user feedback
- Optimized chunk retrieval process

### To Do
- Implement rate limiting
- Add user session analytics
- Enhance error handling for edge cases
- Add support for multiple building code versions

## [0.1.0] - 20240319143000
### Added
- Initial project structure
- Project outline documentation
- Changelog initialization

### To Do
- Implement web scraping functionality
- Create text chunking system
- Set up ChromaDB integration
- Develop Streamlit interface

