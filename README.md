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
- **Multi-Model Comparison**: Benchmark multiple SentenceTransformers embedding models simultaneously
- **Cross-Dataset Analysis**: Compare embedding model performance across multiple datasets with statistical significance testing
- **Comprehensive Metrics**: MAP, Recall, Precision, NDCG, MRR, and Success/Hit Rate evaluation
- **Statistical Analysis**: Paired t-tests, Cohen's d effect sizes, Friedman test, and consistency metrics
- **Batch Processing Support**: Cost-effective asynchronous processing for large datasets
- **Persistent Timing Data**: Timing metrics saved between pipeline runs for accurate performance tracking
- **Professional Reporting**: Automated generation of markdown and PDF reports with visualizations
- **Aggregate Reporting**: Cross-dataset comparison reports with 14+ statistical visualizations
- **ChromaDB Integration**: Efficient vector storage and retrieval
- **Modular Pipeline**: Run individual components or complete end-to-end evaluation
- **Multi-Dataset Support**: Run benchmarks on multiple datasets with complete isolation

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

1. **Pandoc**: Download from [Pandoc&#39;s official website](https://pandoc.org/installing.html)
2. **LaTeX Distribution**: Download MikTeX from [MikTeX&#39;s official website](https://miktex.org/download)

After installing these tools, the framework will generate PDF reports automatically.

## ⚡ Quick Start

### Complete Pipeline with Batch Processing (Recommended for Large Datasets)

```bash
# Activate environment
conda activate ragbenchmark

# Full pipeline with batch processing on a dataset
python rag_benchmark.py --dataset finance --prepare-corpus
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
python rag_benchmark.py --dataset finance --generate-qrels --batch-submit
python rag_benchmark.py --dataset finance --generate-qrels --batch-fetch <BATCH_ID>
python rag_benchmark.py --dataset finance --initialize
python rag_benchmark.py --dataset finance --evaluate
```

### Step-by-Step Execution

```bash
# For a specific dataset (e.g., legal_docs)
python rag_benchmark.py --dataset legal_docs --prepare-corpus
python rag_benchmark.py --dataset legal_docs --generate-queries
python rag_benchmark.py --dataset legal_docs --generate-qrels
python rag_benchmark.py --dataset legal_docs --initialize
python rag_benchmark.py --dataset legal_docs --evaluate

# Combined initialization and evaluation (recommended for convenience)
python rag_benchmark.py --dataset finance --initialize --evaluate
```

**Note**: `--initialize`, `--evaluate`, and `--all` require `--dataset` to avoid ambiguity in multi-dataset setups.

**Note**: Steps 4 and 5 can be run separately - timing data from initialization is automatically saved and loaded for accurate performance reporting.

**💡 Tip**: For datasets with more than 10 queries, consider using [Batch Processing](#batch-processing-optional) to reduce costs and avoid rate limits.

### Cross-Dataset Aggregate Reporting

Compare embedding model performance across multiple datasets with statistical analysis:

```bash
# Run evaluations on multiple datasets
python rag_benchmark.py --dataset education --all
python rag_benchmark.py --dataset finance --all
python rag_benchmark.py --dataset legal --all

# Generate aggregate comparison report
python rag_benchmark.py --generate-aggregate-report

# Generate aggregate report for specific datasets
python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education finance

# Save aggregate report to custom location
python rag_benchmark.py --generate-aggregate-report --aggregate-output-dir ./my_reports
```

### ⚡ Batch Processing (Optional)

For large datasets, use the Gemini Batch API to reduce costs (50% cheaper) and avoid rate limits. Batch processing is recommended when:

- You have more than 10 queries to generate
- You want to minimize API costs
- You need to process large amounts of data asynchronously
- You want to avoid hitting rate limits during peak hours

**How Batch Processing Works:**

1. **Submit Phase**: Upload your requests to Google's Batch API and get a job ID
2. **Processing Phase**: Google processes your requests asynchronously (can take minutes to hours)
3. **Fetch Phase**: Download the results when processing is complete

**Important Notes:**

- Batch jobs are processed asynchronously - you can check status anytime
- Results are saved to your dataset's `reports/` directory
- Use `--batch_status` to monitor job progress (shows all datasets when no --dataset specified)
- Batch processing costs ~50% less than real-time API calls

**Phase 1: Query Generation (Batch Mode)**

```bash
# Submit batch job for query generation (specify dataset for isolation)
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
# Output: "Batch submitted successfully! Job Name: projects/.../locations/.../batchJobs/.../<BATCH_ID>"

# Check status (optional, shows all datasets if no --dataset specified)
python rag_benchmark.py --batch_status

# Fetch results when ready (use the BATCH_ID from submit output)
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
```

**Phase 2: Relevance Judgments (Batch Mode)**

```bash
# Submit batch job for qrels generation (specify dataset for isolation)
python rag_benchmark.py --dataset finance --generate-qrels --batch-submit

# Check status (optional)
python rag_benchmark.py --batch_status

# Fetch results when ready
python rag_benchmark.py --dataset finance --generate-qrels --batch-fetch <BATCH_ID>
```

**Cancelling Batch Jobs**
If you need to cancel a running batch job:

```bash
# Cancel a specific batch job
python rag_benchmark.py --batch-cancel <BATCH_ID>
```

**For Specific Datasets:**

```bash
# All batch commands work with --dataset flag
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
python rag_benchmark.py --dataset finance --batch_status
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
python rag_benchmark.py --dataset finance --batch-cancel <BATCH_ID>

# Check all datasets (run without --dataset)
python rag_benchmark.py --batch_status
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
compute_hit_rate = True  # Success@K / Hit Rate@K

# Evaluation settings
k = 10
mrr_at_k = [k]
precision_recall_at_k = [k]
map_at_k = [k]
ndcg_at_k = [k]

# Document processing
pdf_dir = "utils/pdfs"  # Default PDF directory (used when no --dataset specified)
chunk_size = 1000
chunk_overlap = 200

# Query generation
n_queries = 5
chunks_per_query = 1
candidate_pool_size = 10
qrels_embedding_model_index = 4  # Which embedding model to use for qrels candidate retrieval

# LLM settings
llm_model = "models/gemini-2.5-flash-lite"
temperature = 0.1
llm_timeout = 0.01  # Adjust to avoid rate limits for your API tier

# ChromaDB settings
show_progress_bar = True
document_batch_size = 32
reinitialize_collections = True
```

**Note**: Currently, only SentenceTransformers models are supported. Ensure model names follow the format 'sentence-transformers/model-name'.

### Aggregate Reporting Settings

These settings control cross-dataset reporting (see `config.py` for full list):

```python
aggregate_results_dir = "aggregated_reports"
aggregate_statistical_tests = True
aggregate_generate_visualizations = True
aggregate_significance_level = 0.05
aggregate_min_datasets = 2
aggregate_require_identical_metrics = False
```

### Dataset-Specific Paths

When running with `--dataset <name>`, `configure_for_dataset()` updates:

- `pdf_dir` → `datasets/<name>/pdfs/`
- `reports_dir` → `datasets/<name>/reports/`
- `chroma_db_path` → `datasets/<name>/chromadb_collections/`
- Collection names are prefixed with the dataset name to avoid collisions

### Multi-Dataset Support

The framework supports running benchmarks on multiple datasets with complete isolation:

- Use `--dataset <name>` to specify a dataset (e.g., `--dataset finance`)
- Each dataset gets its own directory under `datasets/<name>/`
- Place PDF files in `datasets/<name>/pdfs/`
- All outputs (corpus, queries, qrels, reports, ChromaDB collections) are isolated per dataset
- If no `--dataset` is specified, only `--prepare-corpus`, `--generate-queries`, `--generate-qrels`, and batch status use default paths; `--initialize`, `--evaluate`, and `--all` require `--dataset`

## 📖 Usage

### Command Line Arguments

| Argument                          | Description                                                                            |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| `--prepare-corpus`              | Extract and chunk PDF documents                                                        |
| `--generate-queries`            | Generate evaluation queries from corpus                                                |
| `--generate-qrels`              | Create relevance judgments using LLM                                                   |
| `--initialize`                  | Build embedding collections in ChromaDB (requires `--dataset`)                       |
| `--evaluate`                    | Run retrieval evaluation and generate reports (requires `--dataset`)                 |
| `--all`                         | Execute complete pipeline end-to-end (requires `--dataset`)                          |
| `--dataset <name>`              | Run benchmark on specified dataset (required for initialize/evaluate/all)              |
| `--generate-aggregate-report`   | Generate cross-dataset comparison report with statistical analysis (includes PDF)      |
| `--aggregate-datasets <list>`   | Specify datasets for aggregate analysis (default: auto-discover)                       |
| `--aggregate-output-dir <path>` | Custom output directory for aggregate reports (default: aggregated_reports/)            |
| `--aggregate-metrics <list>`    | Metrics to include in aggregate analysis (default: all enabled)                        |
| `--batch-submit`                | Submit tasks to Gemini Batch API                                                       |
| `--batch-fetch <ID>`            | Fetch results from Batch API job                                                       |
| `--batch_status`                | List all batch jobs and their statuses (across all datasets if no --dataset specified) |
| `--batch-cancel <ID>`           | Cancel a specific Batch Job                                                            |

### Input Requirements

1. **PDF Documents**: Place your PDF files in `datasets/<name>/pdfs/` directory (when using `--dataset`) or `utils/pdfs/` (default for corpus/query/qrels generation)
2. **API Key**: Set up your Google AI API key in `.env` file
3. **Configuration**: Adjust settings in `config.py`

## 🔧 Pipeline Components

### 1. Document Processing (`--prepare-corpus`)

- **Input**: PDF files in `datasets/<name>/pdfs/` when using `--dataset`, or `utils/pdfs/` for default paths
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

- **Input**: Document corpus and embedding models (requires `--dataset`)
- **Process**:
  1. Generate embeddings using SentenceTransformers (currently the only supported embedding library)
  2. Store in ChromaDB collections with batch processing
  3. Performance timing and throughput measurement
- **Output**: ChromaDB collections in `datasets/<name>/chromadb_collections/`

### 5. Evaluation & Reporting (`--evaluate`)

- **Input**: Corpus, queries, qrels, and ChromaDB collections (requires `--dataset`)
- **Process**:
  1. Load persisted timing data from previous initialization runs
  2. Multi-model retrieval evaluation with comprehensive metrics
  3. Generate timing data for any missing models
  4. Save updated timing data for future runs
  5. Save structured raw results JSON for aggregate analysis
- **Output**:
  - Performance reports (markdown and PDF) named `<dataset>_benchmark_report_*.md/.pdf`
  - Visualization charts (PNG format)
  - Detailed timing analysis
  - Raw results JSON for cross-dataset comparison
- **Features**: Persistent timing data allows running `--initialize` and `--evaluate` separately

### 6. Aggregate Analysis (`--generate-aggregate-report`)

- **Input**: Raw results JSON from multiple dataset evaluations
- **Process**:
  1. Load and validate results from multiple datasets
  2. Perform statistical analysis (paired t-tests, Cohen's d, Friedman test)
  3. Calculate model rankings and consistency metrics
  4. Generate 14+ statistical visualizations
  5. Create comprehensive cross-dataset comparison report
- **Output**:
  - Aggregate comparison report (markdown and PDF)
  - Statistical analysis visualizations
  - Model ranking heatmaps and radar charts
  - Dataset difficulty analysis
- **Features**: Automated dataset discovery, statistical significance testing, publication-ready analysis

## 📊 Evaluation Metrics

The framework computes standard information retrieval metrics:

- **MAP@k**: Mean Average Precision - ranking quality assessment
- **Recall@k**: Coverage of relevant documents in top-k results
- **Precision@k**: Accuracy of top-k retrieved documents
- **NDCG@k**: Position-aware ranking quality with discounting
- **MRR@k**: Mean reciprocal rank of first relevant document
- **Success@k**: Fraction of queries with at least one relevant hit
- **Timing Metrics**: Embedding speed, throughput, processing time, and query latency

### Statistical Analysis Methods (Aggregate Reporting)

For cross-dataset comparison and statistical significance testing:

- **Paired t-tests**: Compare model performance across datasets (α=0.05)
- **Cohen's d**: Measure effect sizes for practical significance
- **Friedman Test**: Non-parametric test for multiple model comparison
- **Consistency Metrics**: Coefficient of variation, worst-case performance drop
- **Dataset Difficulty Scoring**: Relative hardness assessment across datasets

## 📁 Output Files

### Generated Files Structure

```
RagRetrievalBench/
├── corpus.jsonl                    # Processed document chunks (default dataset)
├── queries.jsonl                   # Generated evaluation queries (default)
├── qrels.tsv                       # Relevance judgments (default)
├── aggregated_reports/             # Cross-dataset comparison reports
│   └── <timestamp>/                # Timestamped subdirectory for each run
│       ├── aggregate_report.md     # Comprehensive cross-dataset analysis
│       ├── aggregate_report.pdf    # PDF version (if Pandoc installed)
│       ├── cross_dataset_radar_chart_*.png
│       ├── model_ranking_heatmap_*.png
│       ├── pairwise_significance_heatmap_*.png
│       ├── consistency_comparison_*.png
│       └── [additional statistical visualizations]
├── datasets/                       # Multi-dataset support
│   └── <dataset_name>/             # Per-dataset isolated storage
│       ├── corpus.jsonl            # Dataset-specific corpus
│       ├── queries.jsonl           # Dataset-specific queries
│       ├── qrels.tsv               # Dataset-specific relevance judgments
│       ├── pdfs/                   # Input PDF documents for this dataset
│       ├── reports/                # Dataset-specific reports
│       │   ├── <dataset>_benchmark_report_*.md
│       │   ├── <dataset>_benchmark_report_*.pdf
│       │   ├── raw_results_*.json  # Dataset-specific raw results
│       │   ├── timing_data_*.json
│       │   ├── batch_history.jsonl # Dataset-specific batch history
│       │   └── *.png               # Dataset-specific visualizations
│       └── chromadb_collections/   # Dataset-specific vector database
│           ├── chroma.sqlite3      # ChromaDB metadata
│           └── [collection_directories]/ # Individual model collections
└── utils/chromadb_collections/     # Vector database storage (default)
    ├── chroma.sqlite3              # ChromaDB metadata
    └── [collection_directories]/   # Individual model collections
```

### Report Contents

#### Individual Dataset Reports

- **Executive Summary**: Best performing models and key insights
- **Methodology**: Experimental setup and evaluation procedure
- **Dataset Statistics**: Corpus analysis and query characteristics
- **Model Performance**: Comparative tables with statistical analysis
- **Timing Analysis**: Embedding performance and throughput comparison (uses persisted timing data)
- **Visualizations**: Charts for performance, timing, and dataset statistics
- **Technical Details**: Configuration and reproducibility information

#### Aggregate Cross-Dataset Reports

- **Executive Summary**: Overall best performers across datasets with consistency metrics
- **Datasets Analyzed**: Summary of all included datasets (PDFs → chunks breakdown)
- **Cross-Dataset Model Comparison**: Statistical rankings with significance testing
- **Dataset-Specific Analysis**: Individual dataset performance and difficulty assessment
- **Model Consistency**: Performance variability analysis across datasets
- **Statistical Analysis**: Paired t-tests, effect sizes, Friedman test results
- **Visualizations**: 14+ statistical charts including radar plots, heatmaps, and significance matrices
- **Recommendations**: Production deployment guidance based on aggregate analysis

## 🛠️ Development Tools

### Python Task Runner (`make.py`)

```bash
# Format code
python make.py format

# Run tests
python make.py test
python make.py test-cov  # With coverage

# Run pipeline helpers
python make.py prepare <dataset>   # Prepare corpus, queries, qrels
python make.py init <dataset>      # Initialize ChromaDB collections
python make.py evaluate <dataset>  # Evaluate models
python make.py all <dataset>       # Full pipeline (prepare + init + evaluate)
python make.py aggregate [args]    # Aggregate report (pass-through args supported)

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
- Aggregate reports (`aggregated_reports/` contents)
- ChromaDB collections (`utils/chromadb_collections/` contents)
- Dataset-specific reports and collections under `datasets/<name>/`

## 🧪 Testing

### Running Tests

```bash
# Activate environment
conda activate ragbenchmark

# Run all tests (recommended)
python make.py test

# Run with coverage (defaults to utils coverage)
python make.py test-cov

# Run specific test files
pytest tests/test_llm.py
pytest tests/test_document_loader.py

# Full-project coverage (optional)
pytest --cov=. --cov-report=html --cov-report=term
```

### Test Coverage

Coverage varies by module and changes over time. To generate current numbers:

```bash
python make.py test-cov
```

For full-project coverage, use:

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

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

- **Unit + integration tests** across core utilities and reporting
- **Comprehensive mocking** for external dependencies
- **Integration tests** for complex workflows (marked `integration` in `pytest.ini`)
- **Error handling tests** for robust code paths
- **Test plan** in `docs/test_plan.md`

## 🎯 Project Structure

```
RagRetrievalBench/
├── rag_benchmark.py                  # Main pipeline script
├── config.py                         # Configuration settings
├── make.py                          # Development task runner
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Test configuration
├── .env                            # Environment variables (create this)
├── .env.template                   # Environment variables template
├── .gitignore                      # Git ignore rules
├── current_versions.txt            # Version tracking
├── test_plan.md                    # Placeholder (see docs/test_plan.md)
├── test_report_issues.py           # Test issue reporting script
├── backend/                        # Backend-related files
├── datasets/                       # Multi-dataset storage (created dynamically)
│   └── <dataset_name>/             # Per-dataset isolated directories
│       ├── corpus.jsonl            # Dataset-specific corpus
│       ├── queries.jsonl           # Dataset-specific queries
│       ├── qrels.tsv               # Dataset-specific qrels
│       ├── pdfs/                   # Input PDFs for this dataset
│       ├── reports/                # Dataset-specific reports and data
│       └── chromadb_collections/   # Dataset-specific vector DB
├── docs/                           # Documentation
│   ├── benchmark_workflow.md      # Benchmark workflow documentation
│   ├── MAP_CALCULATION_SUMMARY.md # MAP calculation summary
│   ├── test_plan.md               # Comprehensive testing strategy (540+ lines)
│   └── todolist.md                # Development roadmap
├── utils/                          # Core utilities package
│   ├── __init__.py               # Package initialization
│   ├── aggregate_report_utils.py # Cross-dataset statistical analysis
│   ├── chromadb_utils.py         # Vector database operations
│   ├── document_loader.py        # PDF processing and corpus loading
│   ├── llm.py                    # Google Gemini LLM integration
│   ├── report_utils.py           # Report generation and visualization
│   ├── text_splitter.py          # Document chunking utilities
│   ├── chromadb_collections/     # ChromaDB collections storage (default)
│   └── pdfs/                     # Input PDF documents directory (default)
├── tests/                         # Comprehensive test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Shared test configuration
│   └── test_*.py               # Individual test modules
├── reports/                       # Generated evaluation reports (default dataset)
├── aggregated_reports/            # Cross-dataset aggregate reports
│   └── <timestamp>/               # Timestamped report run
│       ├── aggregate_report.md    # Statistical comparison report
│       ├── aggregate_report.pdf   # PDF version (if Pandoc installed)
│       └── *.png                  # Aggregate visualizations
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
