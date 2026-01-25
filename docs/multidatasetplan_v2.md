# Multi-Dataset Support Implementation Plan (Refined)

## Overview
Implement multi-dataset support in RagRetrievalBench to allow running the RAG benchmark pipeline on multiple document sets without file or collection conflicts.

## Requirements
- Add `--dataset <name>` command-line argument to `rag_benchmark.py`.
- Isolate inputs (PDFs) and outputs (corpus, queries, qrels, ChromaDB, reports) per dataset.
- Dynamically configure paths based on the dataset name.
- Prefix collection names to prevent collisions if using a shared DB, or use separate DB paths.

## Implementation Steps

### 1. Update `config.py`
- **New Variables**: 
  - `chroma_db_path`: Default to `utils/chromadb_collections` (current behavior).
  - `reports_dir`: Default to `reports` (current behavior).
- **`configure_for_dataset(dataset_name)`**:
  - Accepts `dataset_name` string.
  - Updates paths to:
    - `pdf_dir` -> `datasets/{dataset_name}/pdfs` (Note: Plan v1 said `datasets/{dataset_name}/`, but a `pdfs` subdir keeps it cleaner) or directly `datasets/{dataset_name}/`. **Decision**: `datasets/{dataset_name}/`.
    - `corpus_file` -> `datasets/{dataset_name}/corpus.jsonl`
    - `queries_file` -> `datasets/{dataset_name}/queries.jsonl`
    - `qrels_file` -> `datasets/{dataset_name}/qrels.tsv`
    - `chroma_db_path` -> `datasets/{dataset_name}/chromadb_collections`
    - `reports_dir` -> `datasets/{dataset_name}/reports`
  - **Directory Creation**: Ensure these directories exist (except pdfs source).
  - **Collection Names**: Re-construct `embedding_models` list, prefixing `collection_name` with `{dataset_name}_`.

### 2. Refactor `utils/chromadb_utils.py`
- **Issue**: `get_chromadb_client` has hardcoded path `utils/chromadb_collections`.
- **Fix**: Change to usage of `cfg.chroma_db_path`. This allows true isolation of vector databases per dataset.

### 3. Refactor `utils/batch_manager.py`
- **Issue**: `HISTORY_FILE` is defined as a module-level constant using `__file__` relative path.
- **Fix**: Move `HISTORY_FILE` resolution into `BatchManager.__init__` or use a property. It should point to `{cfg.reports_dir}/batch_history.jsonl` or `{cfg.reports_dir}/../batch_history.jsonl` if we want a shared history per dataset.
- **Decision**: Per-dataset batch history seems safer to avoid locking issues, so `{cfg.reports_dir}/batch_history.jsonl`.

### 4. Update `rag_benchmark.py`
- Add `--dataset` argument to `argparse`.
- If `--dataset` is provided:
  - Call `cfg.configure_for_dataset(args.dataset)`.
  - Print confirmation of active dataset and paths.
- Ensure `generate_queries_from_corpus` uses the updated `cfg` paths.

### 5. Update `utils/report_utils.py`
- Verify `generate_benchmark_report` uses `cfg.reports_dir` for saving Markdown reports and JSON timing data.
- Ensure `save_plot` functions use the passed reference or config.

## Directory Structure Target
```
RagRetrievalBench/
├── config.py
├── datasets/
│   ├── finance_docs/
│   │   ├── corpus.jsonl
│   │   ├── queries.jsonl
│   │   ├── qrels.tsv
│   │   ├── report_2023-10-xx.md (inside reports/)
│   │   ├── chromadb_collections/ (sqlite3 db)
│   │   └── *.pdf
│   └── legal_docs/
│       └── ...
```

## Migration Note
- Existing users/runs without `--dataset` will use the default paths defined in `config.py` (backward compatibility). 
