# RagRetrievalBench

A Python-based RAG (Retrieval Augmented Generation) benchmarking toolkit that provides utilities for document processing, text chunking, and vector storage operations.

## Features

- PDF document loading and text extraction with smart whitespace handling
- Intelligent text chunking with configurable size and overlap
- Vector storage using ChromaDB with sentence transformer embeddings
- Google's Gemini API integration for language model capabilities

## Project Structure

```
RagRetrievalBench/
├── backend/
│   ├── config.py          # Configuration settings
│   ├── create_KB.py       # Knowledge base creation utilities
│   └── rag_kmk.py         # RAG implementation
├── utils/
│   ├── chromadb_utils.py  # ChromaDB helper functions
│   ├── document_loader.py # Document loading utilities
│   └── text_spitter.py   # Text chunking functionality
└── requirements.txt      # Project dependencies
```

## Setup

1. Create a Conda environment:
```bash
conda create -n ragbenchmark python=3.10
conda activate ragbenchmark
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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

### Environment Configuration
- Supports `.env` file for API key management
- Configurable embedding models
- Flexible collection naming and management

## Dependencies

- chromadb
- google-genai
- sentence_transformers
- pymupdf
- langchain-text-splitters

## Usage

Basic example of document processing:

```python
from utils.document_loader import load_document
from utils.text_spitter import split_text

# Load a PDF document
doc = load_document("path/to/your/document.pdf")

# Split into chunks
chunks = split_text(doc, chunk_size=1000, chunk_overlap=200)
```