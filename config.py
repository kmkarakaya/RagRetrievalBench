import os

# Configuration file for benchmark.py

# Path to the corpus, queries, and qrels files
corpus_file = "corpus.jsonl"
queries_file = "queries.jsonl"
qrels_file = "qrels.tsv"
reports_dir = "reports"
chroma_db_path = os.path.join("utils", "chromadb_collections")

def configure_for_dataset(dataset_name):
    """
    Configures paths and variables for a specific dataset.
    Args:
        dataset_name (str): Name of the dataset (folder name under datasets/).
    """
    global corpus_file, queries_file, qrels_file, pdf_dir, reports_dir, chroma_db_path, embedding_models
    
    # Define dataset root
    dataset_root = os.path.join("datasets", dataset_name)
    
    # Ensure dataset directory exists
    if not os.path.exists(dataset_root):
        os.makedirs(dataset_root, exist_ok=True)
        print(f"Created new dataset directory: {dataset_root}")
        
    # Update paths
    corpus_file = os.path.join(dataset_root, "corpus.jsonl")
    queries_file = os.path.join(dataset_root, "queries.jsonl")
    qrels_file = os.path.join(dataset_root, "qrels.tsv")
    
    # PDFs are expected in a 'pdfs' subdirectory or directly in root? 
    # Plan v2 decided on 'datasets/{dataset_name}/' for direct isolation or 'pdfs' folder.
    # Let's use a 'pdfs' subfolder for cleanliness and to avoid scanning jsonl files as pdfs accidentally if loader is loose.
    pdf_dir = os.path.join(dataset_root, "pdfs")
    
    # Reports
    reports_dir = os.path.join(dataset_root, "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
        
    # ChromaDB
    chroma_db_path = os.path.join(dataset_root, "chromadb_collections")
    if not os.path.exists(chroma_db_path):
        os.makedirs(chroma_db_path, exist_ok=True)
        
    # Update collection names in embedding_models to avoid collisions if using shared resources
    # (Though with separate chroma_db_path, this is less critical, but strict separation is good)
    # We create a new list to avoid mutating the original one multiple times if called repeatedly (though unlikely)
    new_embedding_models = []
    for model in embedding_models:
        new_model = model.copy()
        # Prefix collection name with dataset name
        # sanitize dataset name for collection name (alphanumeric, underscores, hyphens)
        clean_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in dataset_name)
        if not new_model["collection_name"].startswith(f"{clean_name}_"):
             new_model["collection_name"] = f"{clean_name}_{new_model['collection_name']}"
        new_embedding_models.append(new_model)
    embedding_models = new_embedding_models
    
    print(f"Configuration updated for dataset: {dataset_name}")
    print(f"  Corpus: {corpus_file}")
    print(f"  PDFs: {pdf_dir}")
    print(f"  DB Path: {chroma_db_path}")



# ChromaDB collection/model pairs to benchmark
# for more info, visit https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
# Multilingual Models -  Semantic Similarity Models 
# embedding_models = [ 
#     {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v1", "collection_name": "coll_v1"},
#     {"model_name": "sentence-transformers/distiluse-base-multilingual-cased-v2", "collection_name": "coll_v2"},
#     {"model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "collection_name": "coll_v3"},
#     {"model_name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2", "collection_name": "coll_v4"},
    
# ]

# Most downloaded models from https://huggingface.co/sentence-transformers
embedding_models = [
    {"model_name": "sentence-transformers/all-MiniLM-L6-v2", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/all-mpnet-base-v2", "collection_name": "coll_v2"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "collection_name": "coll_v3"},
    {"model_name": "sentence-transformers/all-MiniLM-L12-v2", "collection_name": "coll_v4"},

]

# Evaluation metrics to compute (set to True to enable)
# These flags control which metrics are reported in the final output and report.

compute_map = True         # Mean Average Precision (MAP)
compute_recall = True      # Recall@K
compute_precision = True   # Precision@K
compute_mrr = True         # Mean Reciprocal Rank (MRR)
compute_ndcg = True        # Normalized Discounted Cumulative Gain (NDCG@K)

# Single cutoff value for all metrics
k = 10  # Use the same k for all metrics

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

#QUERY GENERATION SETTINGS
# How many benchmark queries (seeds) to generate
n_queries = 5

# How many chunks to sample per seed (usually 1)
chunks_per_query = 1

# How many candidates to retrieve for labeling
candidate_pool_size = 10

# LLM settings
llm_model = "models/gemini-2.5-flash-lite"

# Requests per minute (RPM) 
# Tokens per minute (TPM)
# Requests per day (RPD)
# Gemini 2.0 Flash-Lite	30 RPM	1,000,000 TPM	200 RPD
# Gemini 2.0 Flash	    15 RPM 	1,000,000 TPM   200 RPD
# Gemini 2.5 Flash-Lite	15 RPM	  250,000 TPM 1,000 RPD
llm_timeout = (60/10) + 1    #  wait for a short time in seconds to avoid hitting API limits



generate_query_system_instruction = """You are an expert in generating search queries. 
Given a document, generate a query that would retrieve this document 
from a vector database. The query should be concise and relevant to the content of 
the document. Do not include any personal opinions or irrelevant information. 
Focus on the main topics of the given document and prepare a query that is not just a replicate of the document.
The query should be in the form of a natural language question or statement that can be used
 to search for the document in a vector database. Determine the given document's language and 
 generate the query in the same language."""

generate_qrels_system_instruction ="""
You are an expert Information Retrieval judge. 
You will receive a user question and a candidate excerpt from a document.
Your task is to determine if the excerpt fully answers the question.
Example:
Question: What are the key benefits of X?
"Text excerpt from a document"
Respond with a binary relevance label 0 or 1, where 0 means the excerpt does not relate to the question 
and 1 means it does have the complete or partial information.
Return only a JSON object in this format:

{
    "relevance": 0 or 1
}
"""

temperature = 0.1  # Temperature for LLM generation