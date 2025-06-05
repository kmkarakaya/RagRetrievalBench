# Benchmarking Pipeline for Retrieval Performance

## Overview
The `benchmark.py` script provides a comprehensive benchmarking pipeline for evaluating retrieval performance of embedding models using multiple metrics including Mean Average Precision (MAP), Precision, Recall, NDCG, and MRR. It supports comparing different SentenceTransformer models against a corpus of documents using both ChromaDB for vector storage and direct tensor-based similarity calculations for consistent evaluation.

## Input Files
1. **`corpus.jsonl`**: Contains the corpus of documents in JSON Lines format. Each line represents a document chunk.
2. **`queries.jsonl`**: Contains the queries in JSON Lines format. Each line represents a query.
3. **`qrels.tsv`**: Contains the relevance mappings between queries and document chunks in TSV format. Each line specifies a query ID, document ID, and relevance score.

## Configuration
The script uses a configuration file (`benchmark_config.py`) to manage parameters such as:
- Paths to input files (`corpus_file`, `queries_file`, `qrels_file`)
- Model configurations (model names and corresponding collection names)
- Evaluation parameters:
  - `map_at_k`: Cutoff for MAP calculation
  - `mrr_at_k`: Cutoff for Mean Reciprocal Rank
  - `precision_recall_at_k`: Cutoff for Precision and Recall
  - `ndcg_at_k`: Cutoff for Normalized Discounted Cumulative Gain
- ChromaDB settings:
  - `reinitialize_collections`: Whether to rebuild ChromaDB collections
  - `show_progress_bar`: Display progress during evaluation
  - `batch_size`: Batch size for model inference

## Workflow
1. **Data Loading**:
   - Loads the corpus, queries, and relevance mappings from the specified input files.
2. **Embedding Generation**:
   - Generates embeddings for the corpus and queries using the specified models.
3. **Retrieval**:
   - Computes similarity scores between query embeddings and document embeddings.
   - Retrieves the top-k most relevant documents for each query.
4. **Evaluation**:
   - Calculates multiple metrics at specified cutoffs:
     - Mean Average Precision (MAP@k)
     - Precision and Recall@k
     - Normalized Discounted Cumulative Gain (NDCG@k)
     - Mean Reciprocal Rank (MRR@k)
   - Performs per-query performance analysis
   - Compares different MAP calculation methods
5. **Report Generation**:
   - Generates a detailed report including:
     - Summary metrics for each model
     - Statistical significance analysis
     - Per-query performance breakdown
     - Detailed MAP calculation methodology
   - Saves the report with timestamp in the `reports` folder

## Outputs
- A comprehensive report file in the `reports` folder, named with a timestamp (e.g., `report_2025_06_05_02_01.txt`).
- The report includes:
  - Summary metrics (MAP@k, Recall@k, Precision@k, NDCG@k, MRR@k) for each model
  - Statistical significance analysis of differences between models
  - Per-query performance analysis with detailed metrics
  - Comparison of different MAP calculation methods
  - Explanation of the evaluation methodology and ranking approach
  - Notes about potential differences between ChromaDB and evaluator rankings

## MAP Calculation Methodology
This project includes a detailed investigation into how Mean Average Precision (MAP) is calculated in the SentenceTransformer evaluator. Our key findings:

1. **Normalization Factor**: The evaluator divides the sum of precisions by min(k, len(relevant_docs)), not simply by len(relevant_docs)
2. **Ranking Method**: The evaluator uses tensor-based cosine similarity (util.pytorch_cos_sim) which may produce different rankings than ChromaDB's vector search
3. **Averaging Method**: The evaluator calculates MAP as the simple macro-average (mean) of per-query AP values, not weighted by the number of relevant docs for each query

We've consolidated all MAP calculation approaches into `benchmark.py`:
- Weighted average MAP calculation (traditional approach)
- Exact replica of the evaluator's calculation that matches its results
- Simple macro-average (the evaluator's method)

For a comprehensive explanation of our MAP calculation findings, see:
- [MAP_CALCULATION_SUMMARY.md](MAP_CALCULATION_SUMMARY.md): Detailed documentation of our findings

The benchmark.py script now includes all MAP calculation methods and ensures that per-query metrics use the same ranking method as the evaluator, providing consistency between summary and per-query metrics.

## How to Run
1. Ensure the input files (`corpus.jsonl`, `queries.jsonl`, `qrels.tsv`) are correctly formatted and placed in the appropriate directory.
2. Configure the parameters in `benchmark_config.py` as needed.
3. Run the script using the following command:
   ```bash
   python benchmark.py
   ```
4. Check the `reports` folder for the generated report.

## Dependencies
This project requires the following main dependencies:
- `sentence_transformers`: For embedding generation and evaluation
- `chromadb`: For vector storage and retrieval
- `numpy`: For numerical computations
- `torch`: For tensor operations

Install all dependencies by running:
```bash
pip install -r requirements.txt
```

## Notes
- The script ensures consistent evaluation by using the same tensor-based similarity calculations across all metrics
- All metrics use the evaluator's internal ranking method to maintain consistency between summary and per-query results
- The ChromaDB rankings in production may differ slightly from the evaluation results due to differences in similarity calculation methods
- The implementation supports both traditional weighted MAP and the evaluator's macro-average approach
- Each evaluated model gets its own ChromaDB collection for vector storage
- The code is modular and can be extended to support additional metrics or embedding models