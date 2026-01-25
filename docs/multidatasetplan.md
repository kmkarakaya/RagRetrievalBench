# Multi-Dataset Support Implementation Plan

## Overview
Implement multi-dataset support in RagRetrievalBench to allow running the RAG benchmark pipeline on multiple document sets without file or collection conflicts. This will be achieved by adding a `--dataset` flag that isolates data, collections, and outputs per dataset.

## Requirements
- Add `--dataset <name>` command-line argument to `rag_benchmark.py`
  - The `<name>` value (e.g., `dataset1`) indicates the dataset directory: `C:\Codes\RagRetrievalBench\datasets\dataset1`
  - This directory will contain the PDFs for that dataset directly
- Dynamically configure file paths and collection names based on dataset name
- Ensure isolation between datasets (no overwriting of corpus.jsonl, queries.jsonl, qrels.tsv, ChromaDB collections, reports, etc.)
- Support dataset-specific PDF directories

## Implementation Steps

### 1. Update `config.py`
- Add `reports_dir = "reports"` to default configuration
- Add `configure_for_dataset(dataset_name)` function:
  - Update global variables in `config` module directly (in-place modification)
  - Modify path constants:
    - `corpus_file` -> `datasets/{dataset_name}/corpus.jsonl`
    - `queries_file` -> `datasets/{dataset_name}/queries.jsonl`
    - `qrels_file` -> `datasets/{dataset_name}/qrels.tsv`
    - `pdf_dir` -> `datasets/{dataset_name}/`
    - `reports_dir` -> `datasets/{dataset_name}/reports/`
  - Update `embedding_models` list:
    - Prefix each `collection_name` with `{dataset_name}_`
- Ensure `configure_for_dataset` is called before any other module caches these values (though most usage is runtime attribute access, which is safe)

### 2. Update `rag_benchmark.py`
- Add `--dataset` argument parser (default not set, meaning standard non-dataset mode?)
  - *Correction based on requirements:* If no backward compatibility is needed, maybe enforce `--dataset` or default to `datasets/default`? 
  - Decision: Default to `datasets/default` if not provided, to keep usage simple.
- Call `cfg.configure_for_dataset(args.dataset)` immediately after parsing args and BEFORE imports that might potentially resolve paths (though lazy import is better).
- Pass `output_dir=cfg.reports_dir` to `generate_benchmark_report()`.

### 3. Update `utils/document_loader.py`
- No changes needed to function signatures (functions already accept paths).
- `rag_benchmark.py` responsibility to pass the new `cfg.pdf_dir`, etc.

### 4. Update `utils/batch_manager.py`
- Refactor `HISTORY_FILE`:
  - Currently hardcoded as module constant `reports/batch_history.jsonl` (resolved at import time).
  - Change to resolve `HISTORY_FILE` inside `__init__` or methods using `cfg.reports_dir`.
  - Ensure batch request/result files are saved to `cfg.reports_dir` or a subprocess `batches/` folder.

### 5. Update `utils/chromadb_utils.py`
- No changes needed if it uses `cfg.embedding_models` at runtime (which it does).
- `initialize_collection` and `evaluate_with_chromadb` will automatically use the prefixed collection names from `cfg`.

### 6. Update `utils/report_utils.py`
- Ensure `generate_benchmark_report` uses the `output_dir` argument (it already does, but callers must pass `cfg.reports_dir`).
- Verify visualization saving logic uses the passed `output_dir`.

### 7. Update `README.md`
- Document the new `--dataset` flag
- Provide examples of multi-dataset usage

## Directory Structure
```
RagRetrievalBench/
├── datasets/
│   ├── default/  # Default dataset
│   │   ├── corpus.jsonl
│   │   ├── queries.jsonl
│   │   ├── qrels.tsv
│   │   ├── *.pdf  # PDFs directly in dataset directory
│   │   ├── reports/
│   │   └── chromadb_collections/
│   └── dataset1/
│       ├── corpus.jsonl
│       ├── queries.jsonl
│       ├── qrels.tsv
│       ├── *.pdf  # PDFs directly in dataset directory
│       ├── reports/
│       └── chromadb_collections/
```

## Testing Plan
1. Test with `--dataset default` - create default dataset directory structure
2. Test with `--dataset test1` - create new dataset directory structure
3. Run full pipeline on multiple datasets simultaneously
4. Verify no file conflicts between datasets
5. Test collection isolation in ChromaDB

## Future Enhancements
- Dataset metadata storage
- Dataset comparison features
- Batch processing across multiple datasets
