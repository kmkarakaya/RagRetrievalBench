# RAG Retrieval Benchmark

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. This tool provides automated benchmarking of embedding models using real document collections, synthetic query generation, and standardized information retrieval metrics.

## 🚀 Features

- **Automated PDF Processing**: Extract and chunk documents from PDF files
- **LLM-Powered Query Generation**: Generate realistic queries using Gemini AI
- **Intelligent Relevance Assessment**: Automated qrels generation with LLM evaluation
- **Multi-Model Comparison**: Benchmark multiple embedding models simultaneously
- **Comprehensive Metrics**: MAP, Recall, Precision, NDCG, and MRR evaluation
- **Professional Reporting**: Automated generation of conference-ready reports with visualizations
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
# Using conda
conda create -n ragbenchmark python=3.8
conda activate ragbenchmark

# Using venv
python -m venv ragbenchmark
ragbenchmark\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

5. Configure your evaluation settings in `benchmark_config.py`

### Additional Requirements for PDF Report Generation

To generate reports in PDF format, you need to install the following tools:

1. **Pandoc**:
   - Pandoc is a universal document converter. You can download it from [Pandoc's official website](https://pandoc.org/installing.html).

2. **LaTeX Distribution**:
   - A LaTeX distribution like MikTeX is required for PDF generation. You can download MikTeX from [MikTeX's official website](https://miktex.org/download).

After installing these tools, the framework will be able to generate PDF reports seamlessly.

## ⚡ Quick Start

### Complete Pipeline (Recommended)
```bash
# Run the entire benchmark pipeline
python simple_rag_benchmark_pipeline.py --all
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

# 5. Run evaluation
python simple_rag_benchmark_pipeline.py --evaluate
```

## ⚙️ Configuration

Edit `benchmark_config.py` to customize your evaluation:

```python
# Embedding models to evaluate
embedding_models = [
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v1", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v2", "collection_name": "coll_v2"},
    # Add more models here
]

# Metrics toggles (enable/disable specific metrics)
compute_map = True       # Mean Average Precision (MAP)
compute_recall = True    # Recall@K
compute_precision = True # Precision@K
compute_mrr = True       # Mean Reciprocal Rank (MRR)
compute_ndcg = True      # Normalized Discounted Cumulative Gain (NDCG@K)

# Cutoff settings
k = 3
mrr_at_k = [k]
precision_recall_at_k = [k]
map_at_k = [k]
ndcg_at_k = [k]

# Embedding collection settings
show_progress_bar = True
document_batch_size = 32
reinitialize_collections = True

# Document processing
pdf_dir = "utils/pdfs"
chunk_size = 1000
chunk_overlap = 200

# Query generation
n_queries = 10
chunks_per_query = 1
candidate_pool_size = 10

# LLM settings
llm_model = "gemini-1.5-flash"
temperature = 0.1
llm_timeout = 4
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

1. **PDF Documents**: Place your PDF files in the `utils/pdfs/` directory
2. **API Key**: Set up your Google AI API key in `.env` file
3. **Configuration**: Adjust settings in `benchmark_config.py`

## 🔧 Pipeline Components

### 1. Document Processing (`--prepare-corpus`)
- **Input**: PDF files in specified directory
- **Process**: Text extraction using PyMuPDF, chunking with LangChain RecursiveCharacterTextSplitter
- **Output**: `corpus.jsonl` with document chunks
- **Features**: Configurable chunk size and overlap, metadata preservation

### 2. Query Generation (`--generate-queries`)
- **Input**: Document corpus
- **Process**: LLM-powered question generation from randomly sampled document chunks
- **Method**: Seed-chunk → Query generation using Gemini
- **Output**: `queries.jsonl` with evaluation queries
- **Quality Control**: Temperature-controlled generation for consistency

### 3. Relevance Assessment (`--generate-qrels`)
- **Input**: Queries and document corpus
- **Process**: 
  1. ChromaDB retrieval of candidate documents for each query
  2. LLM-based relevance labeling of candidates
  3. Structured JSON output parsing for binary relevance scores
- **Output**: `qrels.tsv` with relevance judgments in TREC format
- **Efficiency**: Rate-limited API calls to respect Gemini quotas

### 4. Collection Initialization (`--initialize`)
- **Input**: Document corpus and embedding models
- **Process**: 
  1. Generate embeddings using SentenceTransformers
  2. Store embeddings in ChromaDB collections with proper indexing
  3. Batch processing for memory efficiency
- **Output**: ChromaDB collections for each model
- **Options**: Configurable reinitialization and progress tracking

### 5. Embedding Evaluation (`--evaluate`)
- **Input**: Corpus, queries, qrels, and ChromaDB collections
- **Process**:
  1. Multi-model retrieval evaluation using SentenceTransformers framework
  2. Comprehensive metric calculation with statistical analysis
  3. Visualization generation for performance comparison
- **Output**: Performance metrics, detailed reports, and visualizations

### 6. Report Generation
- **Triggered by**: `--evaluate` (automatically generates reports)
- **Process**:
  1. Compile evaluation results and timing data into markdown
  2. Convert markdown to PDF via Pandoc and LaTeX
  3. Embed high-quality charts (performance, timing, corpus stats)
- **Output**: `reports/benchmark_report_*.md` and `*.pdf` in `reports/`

## 🛠️ System Utilities

- **Configuration Validation**: Ensures all config parameters are valid before pipeline execution
- **Progress Monitoring**: Displays progress bars and ETA for long-running tasks
- **Checkpointing & Resume**: Saves intermediate state to resume interrupted runs
- **Result Caching**: Avoids recomputation by caching embeddings and evaluations
- **Error Handling & Logging**: Comprehensive logs with per-query error tracking

## 📊 Evaluation Metrics

The framework computes standard information retrieval metrics:

- **MAP@k**: Mean Average Precision at rank k - measures ranking quality
- **Recall@k**: Proportion of relevant documents retrieved in top k - measures coverage
- **Precision@k**: Proportion of relevant documents among top k retrieved - measures accuracy
- **NDCG@k**: Normalized Discounted Cumulative Gain at rank k - measures ranking with position bias
- **MRR@k**: Mean Reciprocal Rank - measures rank of first relevant document
- **Time Metrics**: Embedding throughput (docs/sec), average time per document, end-to-end pipeline latency

All metrics are computed with configurable k values and include statistical significance testing.

## 📁 Output Files

### Generated Files
```
RagRetrievalBench/
├── corpus.jsonl              # Processed document chunks
├── queries.jsonl             # Generated evaluation queries
├── qrels.tsv                 # Relevance judgments (TREC format)
└── reports/
    ├── benchmark_report_*.md  # Comprehensive evaluation report
    ├── *_comparison_*.png     # Individual metric visualizations
    └── corpus_statistics_*.png # Dataset analysis charts
```

### Report Contents
- **Executive Summary**: Best performing model and key metrics
- **Methodology**: Detailed experimental setup and pipeline description
- **Dataset Statistics**: Corpus characteristics, query distributions, relevance patterns
- **Model Performance**: Comparative tables with statistical significance
- **Visualizations**: Performance charts and dataset analysis
- **Technical Details**: Implementation specifics for reproducibility
- **Discussion**: Findings, limitations, and future work

## 🏗️ Project Structure

```
RagRetrievalBench/
├── simple_rag_benchmark_pipeline.py  # Main pipeline script
├── benchmark_config.py               # Configuration settings
├── benchmark.py                      # Legacy evaluation script
├── utils/
│   ├── text_splitter.py             # Document processing utilities
│   ├── llm.py                       # LLM integration (Gemini)
│   ├── document_loader.py           # PDF loading utilities
│   └── chromadb_utils.py            # ChromaDB utilities
├── utils/pdfs/                      # Input PDF directory
├── reports/                         # Generated reports and visualizations
├── tests/                           # Unit tests
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables
└── README.md                       # This file
```

## 🔬 Research Applications

This framework is designed for:

- **Academic Research**: Systematic evaluation of embedding models for publications
- **Industry Applications**: Model selection for production RAG systems
- **Comparative Studies**: Benchmarking new embedding models against established baselines
- **Domain-Specific Evaluation**: Assessment of models on specialized document collections
- **Automated Benchmarking**: Continuous evaluation in ML pipelines

## 📝 Technical Implementation

### MAP Calculation Methodology
This project includes detailed investigation into Mean Average Precision (MAP) calculation methods:

1. **SentenceTransformers Evaluator**: Uses tensor-based cosine similarity with specific normalization
2. **ChromaDB Ranking**: Vector search with potential differences in similarity calculation
3. **Traditional MAP**: Weighted average based on relevant document counts

For detailed documentation, see [MAP_CALCULATION_SUMMARY.md](MAP_CALCULATION_SUMMARY.md).

### LLM Integration
- **Model**: Gemini 1.5 Flash for query generation and relevance assessment
- **Rate Limiting**: Configurable delays to respect API quotas
- **Error Handling**: Robust parsing of LLM outputs with fallback mechanisms
- **Prompt Engineering**: Structured system prompts for consistent outputs

### Vector Database
- **ChromaDB**: Efficient storage and retrieval with native embedding functions
- **Batch Processing**: Memory-efficient document ingestion
- **Collection Management**: Automatic initialization and reinitialization options

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code (if using black)
black .
```

### Testing
The project includes comprehensive unit tests for all major components:
- Document processing and chunking
- LLM integration and response parsing
- ChromaDB utilities and collection management
- Evaluation metrics and statistical analysis

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/yourusername/RagRetrievalBench/issues)
- **Documentation**: Detailed workflow documentation in [benchmark_workflow.md](benchmark_workflow.md)
- **Examples**: Check the `reports/` directory for example outputs

## 🔗 Related Projects

- [SentenceTransformers](https://github.com/UKPLab/sentence-transformers) - Embedding model framework
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector database
- [LangChain](https://github.com/langchain-ai/langchain) - Document processing utilities
- [Google Generative AI](https://github.com/google/generative-ai-python) - LLM integration

## 📊 Example Results

The framework generates comprehensive evaluation reports including:

- **Model Comparison Tables**: Performance across all metrics
- **Statistical Analysis**: Significance testing and confidence intervals
- **Per-Query Breakdown**: Detailed analysis of individual query performance
- **Dataset Characteristics**: Corpus statistics and query distributions
- **Visualization Charts**: Performance comparison and trend analysis

Example output from a recent benchmark:

| Model | MAP@3 | Recall@3 | Precision@3 | NDCG@3 | MRR@3 |
|-------|-------|----------|-------------|--------|-------|
| distiluse-base-multilingual-cased-v1 | 0.9056 | 0.4690 | 0.9000 | 0.9389 | 1.0000 |
| all-MiniLM-L6-v2 | 0.8889 | 0.4545 | 0.8667 | 0.9222 | 1.0000 |
| distiluse-base-multilingual-cased-v2 | 0.8778 | 0.4394 | 0.8333 | 0.9056 | 1.0000 |

## 🎯 Future Work

- **Multi-domain Evaluation**: Support for domain-specific benchmarking
- **Advanced Query Types**: Complex multi-turn and compositional queries
- **Real-time Evaluation**: Streaming evaluation for large document collections
- **Model Fine-tuning**: Integration with embedding model training pipelines
- **Cross-lingual Support**: Evaluation across multiple languages

---

**Made with ❤️ for the RAG research community**

*For detailed workflow documentation, see [benchmark_workflow.md](benchmark_workflow.md)*
*For MAP calculation methodology, see [MAP_CALCULATION_SUMMARY.md](MAP_CALCULATION_SUMMARY.md)*