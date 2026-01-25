# GitHub Copilot Instructions for RagRetrievalBench

This repository hosts a RAG (Retrieval-Augmented Generation) benchmarking pipeline. It evaluates the performance of various embedding models and retrieval strategies using a modular, step-by-step approach.

## 🏗 Project Architecture

### Core Components

- **`rag_benchmark.py`**: The entry point and orchestrator. It handles CLI arguments and executes pipeline steps sequentially or individually.
- **`config.py`**: Central configuration hub. Defines file paths, model lists (`embedding_models`), and tunable hyperparameters (chunk size, `k` values). **Always reference `cfg` variables instead of hardcoding values.**
- **`utils/`**: specialized modules:
  - `chromadb_utils.py`: Manages vector database interactions (embeddings, retrieval) and calculates metrics using `sentence-transformers`.
  - `llm.py` & `batch_manager.py`: Interfaces for the Google Gemini API. `batch_manager.py` handles async Batch API jobs for cost-effective synthetic data generation (Queries/Qrels).
  - `document_loader.py`: Handles PDF parsing (via `pypdf` or similar) and JSONL I/O.
  - `report_utils.py`: Generates Markdown reports and visualizations (`matplotlib`) from benchmark results.

### Data Flow

1. **Corpus Preparation**: PDFs $\rightarrow$ `prepare_corpus_from_pdfs` $\rightarrow$ `corpus.jsonl`
2. **Query Generation**: `corpus.jsonl` $\rightarrow$ LLM (Batch/Direct) $\rightarrow$ `queries.jsonl`
3. **Ground Truth (Qrels)**: `corpus.jsonl` + `queries.jsonl` $\rightarrow$ LLM (Batch/Direct) $\rightarrow$ `qrels.tsv`
4. **Vector Store Initialization**: `corpus.jsonl` $\rightarrow$ Embedding Models $\rightarrow$ ChromaDB Collections
5. **Evaluation**: `queries.jsonl` $\rightarrow$ ChromaDB Retrieval $\rightarrow$ Metrics (MAP, Recall, NDCG) $\rightarrow$ Reports

## 🛠 Critical Workflows

### 1. Running the Benchmark

The pipeline is flag-driven. Common patterns:

- **Full Run**: `python rag_benchmark.py --all`
- **Setup Only**: `python rag_benchmark.py --prepare-corpus --generate-queries --generate-qrels`
- **Evaluation Loop**: `python rag_benchmark.py --initialize --evaluate` (Initialize is required if models change).
- **Batch Processing**:
  - Submit jobs: `--batch_submit` with step flags (e.g., `--generate-queries`).
  - Check status: `--batch_status`.
  - Fetch results: `--batch_fetch <job_id>`.

### 2. Multi-Dataset Support (Upcoming)

- We are transitioning to a multi-dataset structure (`datasets/<name>/`).
- **Do not assume flat file paths.** Use `config.configure_for_dataset(name)` (once implemented) or respect `cfg.*_file` variables which may change dynamically.

### 3. Testing

- Run all tests: `pytest`
- Tests are located in `tests/`.
- `conftest.py` handles fixtures.
- When refactoring, ensure `test_report_utils.py` and `test_metric_indexing.py` pass, as reporting logic is sensitive to metric tuple ordering.

## 🧩 conventions & Patterns

### Configuration First

- **Never hardcode paths** like `"corpus.jsonl"`. Use `config.corpus_file`.
- **Never hardcode model names**. Iterate over `config.embedding_models`.

### Batch Processing

- Prefer `BatchManager` for LLM tasks over direct `generate_content` calls for large datasets.
- Batch history is stored in a JSONL file (ensure paths are dynamic/config-aware).

### Metric Handling

- **Strict Tuple Ordering**: `evaluate_with_chromadb` returns metrics in a specific order: `(map_score, recall_score, precision_score, ndcg_score, mrr_score)`.
- `report_utils.py` relies on this exact unpacking order. If you add a metric, update *both* files.

### Error Handling

- Use `try/except` blocks in `llm.py` to handle API rate limits and timeouts gracefully.
- Validate file existence using `os.path.exists` before attempting load operations in `documents_loader.py`.

## 📦 Dependencies

- **Core**: `chromadb`, `sentence-transformers`, `google-genai`, `matplotlib`, `tabulate`, `numpy`.
- **Environment**: Conda environment `ragbenchmark` - **Always activate this environment before running any Python commands** (`conda activate ragbenchmark`).
  - **Windows Path Format**: When using PowerShell in VS Code, always use Windows-style paths (e.g., `cd C:\Codes\RagRetrievalBench`) instead of Unix-style paths (`/c/Codes/RagRetrievalBench`).

## ⚠️ Common Pitfalls

**Dynamic Indexing**: Avoid accessing metrics by raw indices if possible (though currently legacy code does this). When modifying report logic, verify indices against the tuple definition in `chromadb_utils.py`.
