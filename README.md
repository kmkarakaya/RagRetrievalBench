# RAG Retrieval Benchmark

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Owner: Murat Karakaya**
- Website: [www.muratkarakaya.net](https://www.muratkarakaya.net)
- YouTube: [Murat Karakaya Akademi](https://www.youtube.com/@MuratKarakayaAkademi)

A comprehensive evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. This tool provides automated benchmarking of embedding models using real document collections, synthetic query generation, and standardized information retrieval metrics.

## 🚀 Features

- **Automated PDF Processing**: Extract and chunk documents from PDF files
- **LLM-Powered Query Generation**: Generate realistic queries using Google Gemini AI
- **Intelligent Relevance Assessment**: Automated qrels generation with LLM evaluation
- **Multi-Model Comparison**: Benchmark multiple embedding models simultaneously
- **Comprehensive Metrics**: MAP, Recall, Precision, NDCG, and MRR evaluation
- **Professional Reporting**: Automated generation of markdown and PDF reports with visualizations
- **ChromaDB Integration**: Efficient vector storage and retrieval
- **Modular Pipeline**: Run individual components or complete end-to-end evaluation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline Components](#pipeline-components)
- [Evaluation Metrics](#evaluation-metrics)
- [Output Files](#output-files)
- [Development Tools](#development-tools)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Google AI API key (for Gemini integration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RagRetrievalBench.git
cd RagRetrievalBench
```

2. Create and activate a virtual environment:
```bash
# Using conda (recommended)
conda create -n ragbenchmark python=3.8
conda activate ragbenchmark

# Using venv
python -m venv ragbenchmark
ragbenchmark\Scripts\activate  # Windows
source ragbenchmark/bin/activate  # Linux/macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the template
cp .env.template .env

# Edit .env with your editor and replace 'your_api_key_here'
notepad .env  # Windows
nano .env     # Linux/macOS
```

5. Configure your evaluation settings in `config.py`

### Additional Requirements for PDF Report Generation

To generate reports in PDF format, you need to install:

1. **Pandoc**: Download from [Pandoc's official website](https://pandoc.org/installing.html)
2. **LaTeX Distribution**: Download MikTeX from [MikTeX's official website](https://miktex.org/download)

After installing these tools, the framework will generate PDF reports automatically.

## ⚡ Quick Start

### Complete Pipeline (Recommended)
```bash
# Activate environment
conda activate ragbenchmark

# Run the entire benchmark pipeline
python rag_benchmark.py --all
```

### Step-by-Step Execution
```bash
# 1. Process PDFs into document chunks
python simple_rag_benchmark_pipeline.py --prepare-corpus

# 2. Generate evaluation queries
python simple_rag_benchmark_pipeline.py --generate-queries

# 3. Create relevance judgments
python simple_rag_benchmark_pipeline.py --generate-qrels

# 4. Initialize embedding collections
python simple_rag_benchmark_pipeline.py --initialize

# 5. Run evaluation and generate reports
python simple_rag_benchmark_pipeline.py --evaluate
```

## ⚙️ Configuration

Edit `config.py` to customize your evaluation:

```python
# Embedding models to evaluate
embedding_models = [
    {"model_name": "sentence-transformers/all-MiniLM-L6-v2", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/all-mpnet-base-v2", "collection_name": "coll_v2"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "collection_name": "coll_v3"},
    {"model_name": "sentence-transformers/all-MiniLM-L12-v2", "collection_name": "coll_v4"}
]

# Metrics configuration
compute_map = True       # Mean Average Precision
compute_recall = True    # Recall@K
compute_precision = True # Precision@K
compute_mrr = True       # Mean Reciprocal Rank
compute_ndcg = True      # Normalized Discounted Cumulative Gain

# Evaluation settings
k = 10
mrr_at_k = [k]
precision_recall_at_k = [k]
map_at_k = [k]
ndcg_at_k = [k]

# Document processing
pdf_dir = "utils/pdfs"
chunk_size = 1000
chunk_overlap = 200

# Query generation
n_queries = 5
chunks_per_query = 1
candidate_pool_size = 10

# LLM settings
llm_model = "gemini-2.5-flash-lite"
temperature = 0.1
llm_timeout = (60/15) + 1  # Rate limiting for API calls

# ChromaDB settings
show_progress_bar = True
document_batch_size = 32
reinitialize_collections = True
```

## 📖 Usage

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--prepare-corpus` | Extract and chunk PDF documents |
| `--generate-queries` | Generate evaluation queries from corpus |
| `--generate-qrels` | Create relevance judgments using LLM |
| `--initialize` | Build embedding collections in ChromaDB |
| `--evaluate` | Run retrieval evaluation and generate reports |
| `--all` | Execute complete pipeline end-to-end |

### Input Requirements

1. **PDF Documents**: Place your PDF files in `utils/pdfs/` directory
2. **API Key**: Set up your Google AI API key in `.env` file
3. **Configuration**: Adjust settings in `config.py`

## 🔧 Pipeline Components

### 1. Document Processing (`--prepare-corpus`)
- **Input**: PDF files in `utils/pdfs/`
- **Process**: Text extraction and chunking using RecursiveCharacterTextSplitter
- **Output**: `corpus.jsonl` with structured document chunks
- **Features**: Configurable chunk size/overlap, automatic text cleaning

### 2. Query Generation (`--generate-queries`)
- **Input**: Document corpus
- **Process**: LLM-powered question generation from random document chunks
- **Output**: `queries.jsonl` with realistic evaluation queries
- **Quality**: Temperature-controlled generation for consistency

### 3. Relevance Assessment (`--generate-qrels`)
- **Input**: Queries and document corpus
- **Process**: 
  1. Retrieve candidate documents using first embedding model
  2. LLM-based relevance evaluation with structured JSON parsing
  3. Rate-limited API calls with configurable timeout
- **Output**: `qrels.tsv` in TREC format

### 4. Collection Initialization (`--initialize`)
- **Input**: Document corpus and embedding models
- **Process**: 
  1. Generate embeddings using SentenceTransformers
  2. Store in ChromaDB collections with batch processing
  3. Performance timing and throughput measurement
- **Output**: ChromaDB collections in `utils/chromadb_collections/`

### 5. Evaluation & Reporting (`--evaluate`)
- **Input**: Corpus, queries, qrels, and ChromaDB collections
- **Process**: Multi-model retrieval evaluation with comprehensive metrics
- **Output**: 
  - Performance reports (markdown and PDF)
  - Visualization charts (PNG format)
  - Detailed timing analysis

## 📊 Evaluation Metrics

The framework computes standard information retrieval metrics:

- **MAP@k**: Mean Average Precision - ranking quality assessment
- **Recall@k**: Coverage of relevant documents in top-k results
- **Precision@k**: Accuracy of top-k retrieved documents
- **NDCG@k**: Position-aware ranking quality with discounting
- **MRR@k**: Mean reciprocal rank of first relevant document
- **Timing Metrics**: Embedding speed, throughput, processing time

## 📁 Output Files

### Generated Files Structure
```
RagRetrievalBench/
├── corpus.jsonl                    # Processed document chunks
├── queries.jsonl                   # Generated evaluation queries
├── qrels.tsv                       # Relevance judgments (TREC format)
├── reports/
│   ├── benchmark_report_*.md       # Comprehensive evaluation report
│   ├── benchmark_report_*.pdf      # PDF version (if Pandoc installed)
│   ├── timing_comparison_*.png     # Performance comparison charts
│   ├── model_comparison_*.png      # Model performance visualization
│   └── corpus_statistics_*.png    # Dataset analysis charts
└── utils/chromadb_collections/     # Vector database storage
    ├── chroma.sqlite3              # ChromaDB metadata
    └── [collection_directories]/   # Individual model collections
```

### Report Contents
- **Executive Summary**: Best performing models and key insights
- **Methodology**: Experimental setup and evaluation procedure
- **Dataset Statistics**: Corpus analysis and query characteristics
- **Model Performance**: Comparative tables with statistical analysis
- **Timing Analysis**: Embedding performance and throughput comparison
- **Visualizations**: Charts for performance, timing, and dataset statistics
- **Technical Details**: Configuration and reproducibility information

## 🛠️ Development Tools

### Python Task Runner (`make.py`)
```bash
# Format code
python make.py format

# Run tests
python make.py test
python make.py test-cov  # With coverage

# Clean generated files
python make.py clean

# Check code quality
python make.py lint

# Show help
python make.py help
```

### Cleanup Operations
The `make.py clean` command removes:
- Python cache files (`__pycache__/`, `*.pyc`)
- Test artifacts (`.pytest_cache`, coverage reports)
- Generated reports (`reports/` contents)
- ChromaDB collections (`utils/chromadb_collections/` contents)

## 🧪 Testing

### Running Tests
```bash
# Activate environment
conda activate ragbenchmark

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test files
pytest tests/test_llm.py
pytest tests/test_document_loader.py
```

### Test Coverage
Current test coverage includes:
- **utils/chromadb_utils.py**: 90% coverage (excellent)
- **utils/document_loader.py**: 70% coverage (good)
- **utils/llm.py**: 79% coverage (good)
- **utils/report_utils.py**: 76% coverage (excellent)
- **utils/text_splitter.py**: 26% coverage (needs improvement)
- **Overall Coverage**: 71% (excellent progress)

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                    # Test configuration and fixtures
├── test_chromadb_utils.py         # ChromaDB functionality tests
├── test_document_loader.py        # Document processing tests
├── test_llm.py                   # LLM integration tests
├── test_text_splitter.py         # Text chunking tests
├── test_report_utils.py          # Report generation tests
├── test_report_integration.py    # Integration tests
└── test_metric_indexing.py       # Metric calculation tests
```

### Test Quality
- **58 total tests** with **100% pass rate** ✅
- **Comprehensive mocking** for external dependencies
- **Integration tests** for complex workflows
- **Error handling tests** for robust code
- **Professional test documentation** in `docs/test_plan.md`

## 🎯 Project Structure

```
RagRetrievalBench/
├── simple_rag_benchmark_pipeline.py  # Main pipeline script
├── rag_benchmark.py                  # Alternative pipeline interface
├── config.py                         # Configuration settings (renamed from benchmark_config.py)
├── make.py                          # Development task runner
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Test configuration
├── .env                            # Environment variables (create this)
├── .gitignore                      # Git ignore rules
├── docs/                           # Documentation
│   ├── test_plan.md               # Comprehensive testing strategy (540+ lines)
│   └── todolist.md                # Development roadmap
├── utils/                          # Core utilities package
│   ├── __init__.py               # Package initialization
│   ├── chromadb_utils.py         # Vector database operations
│   ├── document_loader.py        # PDF processing and corpus loading
│   ├── llm.py                    # Google Gemini LLM integration
│   ├── report_utils.py           # Report generation and visualization
│   ├── text_splitter.py          # Document chunking utilities
│   └── pdfs/                     # Input PDF documents directory
├── tests/                         # Comprehensive test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Shared test configuration
│   └── test_*.py               # Individual test modules
└── reports/                       # Generated evaluation reports
```

## 🚀 API Rate Limits & Best Practices

### Google Gemini API Limits
- **Gemini 2.5 Flash-Lite**: 15 RPM, 250,000 TPM, 1,000 RPD
- **Rate Limiting**: Built-in delays between API calls (configurable)
- **Error Handling**: Graceful quota exhaustion handling with helpful messages

### Performance Optimization
- **Batch Processing**: Documents processed in configurable batches (default: 32)
- **Progress Tracking**: Real-time progress bars for long-running operations
- **Caching**: ChromaDB collections persist between runs
- **Memory Management**: Efficient handling of large document collections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python make.py test-cov`
5. Format code: `python make.py format`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a pull request

### Development Standards
- **Test Coverage**: Maintain >70% coverage for new code
- **Code Quality**: Follow PEP 8 and use black formatting
- **Documentation**: Update relevant docs for significant changes
- **Testing**: Add comprehensive tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SentenceTransformers**: For embedding model integration
- **ChromaDB**: For efficient vector storage and retrieval
- **Google AI**: For Gemini API access
- **LangChain**: For document processing utilities

---

**Made with ❤️ for the RAG research community**

*For questions or support, please open an issue on GitHub.*