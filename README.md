# RagRetrievalBench

A Python-based RAG (Retrieval Augmented Generation) benchmarking toolkit that provides utilities for document processing, text chunking, and vector storage operations.

## Features

- PDF document loading and text extraction with smart whitespace handling
- Intelligent text chunking with configurable size and overlap
- Vector storage using ChromaDB with sentence transformer embeddings
- Google's Gemini API integration for language model capabilities

## Installation

See [setup.md](setup.md) for detailed setup instructions.

Quick start:
```bash
conda create -n ragbenchmark python=3.10
conda activate ragbenchmark
pip install -r requirements.txt
```

## Environment Configuration

1. Create a `.env` file in the project root directory
2. Add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

## Core Components

### Document Loading
- Supports PDF document loading with improved text extraction
- Handles whitespace and formatting cleanup
- Uses PyMuPDF for reliable PDF processing

### Text Splitting
- Implements recursive character text splitting
- Configurable chunk size and overlap
- Optimized for RAG applications

### Vector Storage
- ChromaDB integration for efficient vector storage
- Sentence Transformer embedding support
- Collection management with add/delete capabilities

### LLM Integration
- Google's Gemini API integration
- Configurable generation parameters
- Environment-based API key management

## Development

### Project Structure
```
RagRetrievalBench/
├── backend/           # Core RAG implementation
├── utils/            # Utility functions and helpers
├── tests/           # Test suite
└── requirements.txt # Project dependencies
```

### Testing

The project uses pytest for testing. To run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_document_loader.py

# Run integration tests only
pytest -m integration

# Run unit tests only
pytest -m "not integration"
```

Test categories:
- Unit tests for core components
- Integration tests for ChromaDB operations
- Integration tests for Gemini API
- Text processing validation tests

### Dependencies

Core dependencies:
- chromadb
- google-genai
- sentence_transformers
- pymupdf
- langchain-text-splitters
- python-dotenv

Development dependencies:
- pytest
- black (code formatting)
- isort (import sorting)

## Basic Usage

```python
from utils.document_loader import load_document
from utils.text_spitter import split_text
from utils.chromadb_utils import create_chroma_collection
from utils.llm import generate_content

# Load and process a document
doc = load_document("path/to/your/document.pdf")
chunks = split_text(doc, chunk_size=1000, chunk_overlap=200)

# Create a vector store
collection = create_chroma_collection(
    "my_collection",
    "all-MiniLM-L6-v2",
    [chunks],
    from_scratch=True
)

# Generate content using Gemini
response = generate_content("Your prompt here", max_output_tokens=500)
print(response)
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[Add your license information here]