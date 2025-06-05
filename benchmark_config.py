# Configuration file for benchmark.py

# Path to the corpus, queries, and qrels files
corpus_file = "corpus.jsonl"
queries_file = "queries.jsonl"
qrels_file = "qrels.tsv"

# ChromaDB collection/model pairs to benchmark
models = [ 
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v1", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/all-MiniLM-L6-v2", "collection_name": "coll_v3"},
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v2", "collection_name": "coll_v2"},
    
]

# Evaluation metrics to compute (set to True to enable)
# These flags control which metrics are reported in the final output and report.

compute_map = True         # Mean Average Precision (MAP)
compute_recall = True      # Recall@K
compute_precision = True   # Precision@K
compute_mrr = True         # Mean Reciprocal Rank (MRR)
compute_ndcg = True        # Normalized Discounted Cumulative Gain (NDCG@K)

# Single cutoff value for all metrics
k = 3  # Use the same k for all metrics

# Evaluation parameters (all metrics use the same k)
# Note: precision_recall_at_k is a parameter that sets the cutoff k for both Precision@K and Recall@K.
mrr_at_k = [k]
precision_recall_at_k = [k]
map_at_k = [k]
ndcg_at_k = [k]

# Other options
show_progress_bar = True
batch_size = 32

# Add this line to your benchmark_config.py file
reinitialize_collections = True  # Set to False to skip re-embedding if collections exist

# Directory containing PDF files for embedding
pdf_dir = "utils/pdfs"  # Directory containing PDFs
chunk_size = 1000
chunk_overlap = 200
