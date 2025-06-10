# Configuration file for benchmark.py

# Path to the corpus, queries, and qrels files
corpus_file = "corpus.jsonl"
queries_file = "queries.jsonl"
qrels_file = "qrels.tsv"

# ChromaDB collection/model pairs to benchmark
# for more info, visit https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
# Multilingual Models -  Semantic Similarity Models 
embedding_models = [ 
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v1", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v2", "collection_name": "coll_v2"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "collection_name": "coll_v3"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2", "collection_name": "coll_v4"},
    
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

# Creating collections and embedding settings for each embedding model
# Set to True to show progress bars during embedding and evaluation
show_progress_bar = True
# Batch size for embedding documents
document_batch_size = 32
# Add this line to your benchmark_config.py file
reinitialize_collections = True  # Set to False to skip re-embedding if collections exist

# Directory containing PDF files for embedding
pdf_dir = "utils/pdfs"  # Directory containing PDFs
chunk_size = 1000
chunk_overlap = 200

#QUERT GENERATION SETTINGS
# How many benchmark queries (seeds) to generate
n_queries = 10

# How many chunks to sample per seed (usually 1)
chunks_per_query = 1

# How many candidates to retrieve for labeling
candidate_pool_size = 10

# LLM settings
llm_model = "gemini-1.5-flash"

# Requests per minute (RPM) 
# Tokens per minute (TPM)
# Requests per day (RPD)
# Gemini 1.5 Flash	15 RPM    250,000 TPM   500 RPD
# Gemini 2.0 Flash	15 RPM 	1,000,000 TPM 1,500 RPD
llm_timeout = 4   #  wait for a short time in seconds to avoid hitting API limits



generate_query_system_instruction = """You are an expert in generating search queries. 
Given a document, generate a query that would retrieve this document 
from a vector database. The query should be concise and relevant to the content of 
the document. Do not include any personal opinions or irrelevant information. 
Focus on the main topics of the given document and prepare a query that is not just a replicate of the document.
The query should be in the form of a natural language question or statement that can be used
 to search for the document in a vector database. Determine the given document's language and 
 and generate the query in the same language.
Here is the document: 
"""

generate_qrels_system_instruction ="""
ou are an expert Information Retrieval judge. 
You will receive a user question and a candidate excerpt from a document.
Your task is to determine if the excerpt fully answers the question.:
Question: What are the key benefits of X?
 “Text excerpt from a document”
You will respond with a binary relevance label 0 or 1, where 0 means the excerpt does not relate to the question 
and 1 means it does have the complete or partial information.
just return 0 or 1, do not add any other text in JSON format:

{
    "relevance": 0 or 1
}
"""

temperature = 0.1  # Temperature for LLM generation