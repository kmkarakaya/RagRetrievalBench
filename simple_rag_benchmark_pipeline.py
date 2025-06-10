import random
from sentence_transformers import SentenceTransformer, evaluation
import chromadb
from chromadb import Client
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
import json
import os
import time , datetime
import re
import numpy as np

from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import argparse


import benchmark_config as cfg
from utils.llm import generate_content

from utils.report_utils import  generate_benchmark_report, generate_visualizations, generate_corpus_statistics_viz

def prepare_corpus_from_pdfs():
    """
    Loads all PDFs from cfg.pdf_dir, splits them into chunks using the utility,
    and saves the chunks as JSONL to cfg.corpus_file.
    """
    print("Executing prepare_corpus_from_pdfs()...")

    # Import here to avoid circular imports
    import sys
    # Add the parent directory to sys.path if needed
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    try:
        from utils.text_splitter import split_pdfs_to_chunks
    except ImportError:
        print("Error: Could not import split_pdfs_to_chunks from utils.text_splitter")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        raise

    pdf_dir = cfg.pdf_dir
    chunk_size = cfg.chunk_size
    chunk_overlap = cfg.chunk_overlap
    corpus_file = cfg.corpus_file

    
    chunks = split_pdfs_to_chunks(pdf_dir, chunk_size, chunk_overlap)

    print(f"Saving {len(chunks)} chunks to {corpus_file}...")
    with open(corpus_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            # Each chunk should have at least 'doc_id' and 'text'
            f.write(json.dumps({"doc_id": chunk.doc_id, "text": chunk.page_content}) + "\n")
    print("Corpus preparation complete.")

    # Ensure the function is not called multiple times
    return



def generate_queries_from_corpus() -> dict[str,str]:

    print("Selecting seed chunks from corpus...")
    
    # Import here to avoid circular imports
    import sys
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    corpus = load_corpus()
    print(f"Loaded {len(corpus)} corpus chunks.")
    all_ids = list(corpus.keys())
    seed_ids = random.sample(all_ids, cfg.n_queries * cfg.chunks_per_query)
    print(f"Selected {len(seed_ids)} seed chunks for query generation ({cfg.n_queries,cfg.chunks_per_query}) .")
    
    
    # Generate and save queries in same loop
    print(f"Generating and saving queries to {cfg.queries_file}...")
    with open(cfg.queries_file, 'w', encoding='utf-8') as f:
        for i, seed_id in enumerate(seed_ids):
            prompt = f"Generate a search query for the following document:\n\n{corpus[seed_id]}\n\nQuery:"
            print(f"\nGenerating query {i+1}/{len(seed_ids)} for seed chunk {seed_id}...")
            
            # Generate query using the LLM
            generated_query = generate_content(cfg.generate_query_system_instruction,prompt)
            print(f"Generated query: {generated_query}")
            
            # Save query immediately
            query_id = f"q{i+1}_seedChunk_{seed_id}"
            f.write(json.dumps({"query_id": query_id, "text": generated_query}) + "\n")
            
    print("Query generation and saving complete. Queries saved to", cfg.queries_file)
 
def generate_qrels():
    corpus = load_corpus()
    # Initialize collection
    collection_name = "test_collection"
    initialize_collection(corpus, cfg.embedding_models[0]["model_name"], collection_name)
    # Use persistent client instead of chromadb.Client()
    client = get_chromadb_client()
    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error: Collection {collection_name} not found. Did you run initialization?")
        raise e
    print(f"Collection {collection_name} initialized successfully.")
    
    # Load queries
    queries = load_queries()
    print(f"Loaded {len(queries)} queries.")

    print("Generating qrels file...")
    # Create qrels file outside the loop
    with open(cfg.qrels_file, 'w', encoding='utf-8') as f:
        for query_id, query_text in queries.items():
            print(f"Query ID: {query_id}, Query Text: {query_text}")
            # Retrieve candidates for labeling related to a query from chromadb
            # Query ChromaDB directly with text - the embedding function will handle conversion
            results = collection.query(
                query_texts=[query_text],
                n_results=cfg.candidate_pool_size  # Get more results than needed to ensure we have enough
            )
            print(f"Retrieved {len(results['ids'][0])} documents for query {query_id}.")
            # Build prompt with query and retrieved chunks
            
            for i, (doc_id, text) in enumerate(zip(results['ids'][0], results['documents'][0])):
                prompt = f"Question: {query_text}\n"
                prompt += f"{i+1}. [{doc_id}] \"{text}\"\n\n"
                print(f"Generated prompt for query {query_id}:\n{prompt}")
                # Send prompt to LLM to get relevance judgments
                relevance = generate_content(cfg.generate_qrels_system_instruction, prompt)
                print(f"Relevance judgment for {doc_id}: {relevance}")
                try:
                    # Look for JSON pattern in the response
                    json_pattern = r'({[\s\S]*?})'
                    match = re.search(json_pattern, relevance)
                    if match:
                        json_str = match.group(1)
                        relevance_json = json.loads(json_str)
                        rel_score = relevance_json.get("relevance", 0)
                        print(f"Relevance score extracted: {rel_score}")
                    else:
                        # If no JSON pattern found, try direct parsing
                        relevance_json = json.loads(relevance)
                        rel_score = relevance_json.get("relevance", 0)
                        print(f"Relevance score extracted: {rel_score}")
                except json.JSONDecodeError:
                    print(f"*** Error parsing relevance JSON for {doc_id}, using default score of 0 ****")
                    rel_score = 0

                # Write results to qrels file
                if rel_score > 0:  # Only write relevant documents
                    print(f"Writing to qrels: {query_id}, {doc_id}, {rel_score}")
                    # Write in TREC format: query_id, doc_id, rel_score
                    f.write(f"{query_id}\t{doc_id}\t{rel_score}\n")
                # wait for a short time to avoid hitting API limits
                time.sleep(cfg.llm_timeout)

    print(f"Generated qrels file at {cfg.qrels_file} with {len(queries)} queries.")
    # Ensure the qrels file is created
    if not os.path.exists(cfg.qrels_file):
        print(f"Error: Qrels file {cfg.qrels_file} was not created.")
    else:
        print(f"Created qrels file: {cfg.qrels_file}")

    return

def load_corpus() -> dict[str,str]:
    corpus = {}
    with open(cfg.corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)
            corpus[j['doc_id']] = j['text']
    
    if not corpus:
        print(f"Warning: No documents found in {cfg.corpus_file}. Please check the file format.")
    else:
        print(f"Successfully loaded {len(corpus)} documents from {cfg.corpus_file}.")
        print(len(corpus), list(corpus.keys())[:5])
    return corpus

def load_queries() -> dict[str,str]:
    queries = {}
    with open(cfg.queries_file, 'r', encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)
            queries[j['query_id']] = j['text']
    if not queries:
        print(f"Warning: No queries found in {cfg.queries_file}. Please check the file format.")
    else:
        print(f"Successfully loaded {len(queries)} queries from {cfg.queries_file}.")
        print(len(queries), list(queries.keys())[:5])
    return queries

def load_ground_truth():
    """
    Load ground truth data files (corpus, queries, relevance judgments).
    
    Returns:
        tuple of (queries, corpus, relevant_docs)
    """
    print("Loading ground-truth files...")
    
    # Load queries
    with open(cfg.queries_file) as qf:
        queries = {j["query_id"]: j["text"] for j in map(json.loads, qf)}

    # Load corpus
    with open(cfg.corpus_file) as cf:
        corpus = {j["doc_id"]: j["text"] for j in map(json.loads, cf)}

    # Load relevance judgments
    relevant_docs = {}
    with open(cfg.qrels_file, 'r', encoding='utf-8') as rf:
        for line in rf:
            parts = line.strip().split()
            if len(parts) == 3:
                qid, doc_id, rel = parts
                try:
                    rel_int = int(rel)
                    if rel_int > 0:
                        relevant_docs.setdefault(qid, set()).add(doc_id)
                except ValueError:
                    continue
    
    print(f"Loaded {len(queries)} queries, {len(corpus)} corpus chunks, and {sum(len(v) for v in relevant_docs.values())} relevance mappings.")
    return queries, corpus, relevant_docs

def initialize_collection(corpus, model_name, collection_name):
    """Initialize a ChromaDB collection with document embeddings."""
    print(f"Initializing ChromaDB collection: {collection_name} with model: {model_name}...")
    
    # Check if collection exists and should be reinitialized
    client = Client()
    collection_exists = False
    
    try:
        client.get_collection(collection_name)
        collection_exists = True
    except:
        collection_exists = False
    
    if collection_exists and not cfg.reinitialize_collections:
        print(f"Collection {collection_name} already exists and reinitialize_collections=False. Skipping initialization.")
        return
    
    # Initialize SentenceTransformer embedding function
    from chromadb.utils import embedding_functions
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )
    
    # DEBUGGING: Test embedding output
    test_text = "This is a test sentence to verify embedding differences"
    test_embedding = sentence_transformer_ef([test_text])[0]
    print(f"DEBUG - First 5 dimensions of embedding for '{model_name}':")
    print(f"  {test_embedding[:5]}")
    
    # Get corpus IDs and texts
    corpus_ids = list(corpus.keys())
    corpus_texts = [corpus[doc_id] for doc_id in corpus_ids]
    
    # Delete collection if it exists
    if collection_exists:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    
    # Create new collection with the embedding function
    collection = client.create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    print(f"Created new collection: {collection_name}")
    
    # Add documents to collection
    batch_size = 32  # ChromaDB add batch size
    
    # Use tqdm if show_progress_bar is True
    iterator = tqdm(range(0, len(corpus_ids), batch_size)) if cfg.show_progress_bar else range(0, len(corpus_ids), batch_size)
    
    for i in iterator:
        # Get batch data
        batch_ids = corpus_ids[i:i+batch_size]
        batch_texts = corpus_texts[i:i+batch_size]
        
        # Add batch to collection - ChromaDB will handle embedding automatically
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=[{"text": text} for text in batch_texts]
        )
    
    print(f"Finished initializing collection: {collection_name}")

def evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name):
    """Evaluate retrieval performance using ChromaDB and SentenceTransformer evaluator."""
    print(f"\nEvaluating {model_name} using ChromaDB rankings...")
    
    # Get ChromaDB collection
    client = chromadb.Client()
    
    # Add debug info storage
    model_rankings = {}
    
    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error: Collection {collection_name} not found. Did you run initialization?")
        raise e
    
    # Set up evaluator with all config parameters
    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        mrr_at_k=cfg.mrr_at_k,
        ndcg_at_k=cfg.ndcg_at_k,
        accuracy_at_k=[cfg.k],  # Use k as a fallback if not in config
        precision_recall_at_k=cfg.precision_recall_at_k,
        map_at_k=cfg.map_at_k,
        show_progress_bar=cfg.show_progress_bar,
        batch_size=cfg.batch_size,
        name=f"{model_name}-chromadb"
    )
    
    # Get mapping from query ID to index
    query_id_to_idx = {qid: idx for idx, qid in enumerate(evaluator.queries_ids)}
    
    # Initialize results list for evaluator
    queries_result_list = [[] for _ in range(len(evaluator.queries_ids))]
    
    # Process each query
    query_iterator = tqdm(queries.items()) if cfg.show_progress_bar else queries.items()
    for qid, query_text in query_iterator:
        if qid not in relevant_docs or qid not in query_id_to_idx:
            continue
            
        # Get query index for evaluator
        query_idx = query_id_to_idx[qid]
        
        # Query ChromaDB directly with text - the embedding function will handle conversion
        results = collection.query(
            query_texts=[query_text],
            n_results=100  # Get more results than needed to ensure we have enough
        )
        
        # Store rankings for debugging
        model_rankings[qid] = results['ids'][0]
        
        # Store results in evaluator format
        for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
            # Convert distance to similarity score (higher is better)
            similarity = 1.0 / (1.0 + float(distance))
            queries_result_list[query_idx].append({
                "corpus_id": doc_id,
                "score": similarity
            })
        
        # Show top results for this query
        print(f"\nQuery {qid}: {query_text}")
        print(f"Relevant docs: {relevant_docs[qid]}")
        print(f"Top {cfg.k} retrieved docs:")
        for i, doc_score in enumerate(queries_result_list[query_idx][:cfg.k]):
            doc_id = doc_score["corpus_id"]
            is_relevant = doc_id in relevant_docs[qid]
            rel_marker = " (REL)" if is_relevant else ""
            print(f"  {i+1}. {doc_id} (score: {doc_score['score']:.4f}){rel_marker}")
    
    # Print detailed rankings for debugging
    print(f"\nDEBUG - Full rankings for {model_name}:")
    for qid, ranking in model_rankings.items():
        print(f"  Query {qid}:")
        print(f"    Top 5 docs: {ranking[:5]}")
    
    # Calculate metrics using ChromaDB rankings
    scores = evaluator.compute_metrics(queries_result_list)
    
    # Extract metrics based on config settings
    k = cfg.k
    metrics = {}
    
    if cfg.compute_map:
        metrics["map"] = scores["map@k"][k]
    else:
        metrics["map"] = 0.0
        
    if cfg.compute_recall:
        metrics["recall"] = scores["recall@k"][k]
    else:
        metrics["recall"] = 0.0
        
    if cfg.compute_precision:
        metrics["precision"] = scores["precision@k"][k]
    else:
        metrics["precision"] = 0.0
        
    if cfg.compute_ndcg:
        metrics["ndcg"] = scores["ndcg@k"][k]
    else:
        metrics["ndcg"] = 0.0
        
    if cfg.compute_mrr:
        metrics["mrr"] = scores["mrr@k"][k]
    else:
        metrics["mrr"] = 0.0
    
    # Print metrics
    print(f"\nMetrics for {model_name} using ChromaDB rankings:")
    if cfg.compute_map:
        print(f"MAP@{k}: {metrics['map']:.4f}")
    if cfg.compute_recall:
        print(f"Recall@{k}: {metrics['recall']:.4f}")
    if cfg.compute_precision:
        print(f"Precision@{k}: {metrics['precision']:.4f}")
    if cfg.compute_ndcg:
        print(f"NDCG@{k}: {metrics['ndcg']:.4f}")
    if cfg.compute_mrr:
        print(f"MRR@{k}: {metrics['mrr']:.4f}")
    
    return (
        metrics["map"],
        metrics["recall"],
        metrics["precision"],
        metrics["ndcg"],
        metrics["mrr"]
    )



def load_ground_truth():
    """
    Load ground truth data files (corpus, queries, relevance judgments).
    
    Returns:
        tuple of (queries, corpus, relevant_docs)
    """
    print("Loading ground-truth files...")
    
    # Load queries
    with open(cfg.queries_file) as qf:
        queries = {j["query_id"]: j["text"] for j in map(json.loads, qf)}

    # Load corpus
    with open(cfg.corpus_file) as cf:
        corpus = {j["doc_id"]: j["text"] for j in map(json.loads, cf)}

    # Load relevance judgments
    relevant_docs = {}
    with open(cfg.qrels_file, 'r', encoding='utf-8') as rf:
        for line in rf:
            parts = line.strip().split()
            if len(parts) == 3:
                qid, doc_id, rel = parts
                try:
                    rel_int = int(rel)
                    if rel_int > 0:
                        relevant_docs.setdefault(qid, set()).add(doc_id)
                except ValueError:
                    continue
    
    print(f"Loaded {len(queries)} queries, {len(corpus)} corpus chunks, and {sum(len(v) for v in relevant_docs.values())} relevance mappings.")
    return queries, corpus, relevant_docs

def initialize_collection(corpus, model_name, collection_name):
    """Initialize a ChromaDB collection with document embeddings."""
    print(f"Initializing ChromaDB collection: {collection_name} with model: {model_name}...")
    
    # Check if collection exists and should be reinitialized
    client = Client()
    collection_exists = False
    
    try:
        client.get_collection(collection_name)
        collection_exists = True
    except:
        collection_exists = False
    
    if collection_exists and not cfg.reinitialize_collections:
        print(f"Collection {collection_name} already exists and reinitialize_collections=False. Skipping initialization.")
        return
    
    # Initialize SentenceTransformer embedding function
    from chromadb.utils import embedding_functions

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )
    
    # DEBUGGING: Test embedding output
    test_text = "This is a test sentence to verify embedding differences"
    test_embedding = sentence_transformer_ef([test_text])[0]
    print(f"DEBUG - First 5 dimensions of embedding for '{model_name}':")
    print(f"  {test_embedding[:5]}")
    
    # Get corpus IDs and texts
    corpus_ids = list(corpus.keys())
    corpus_texts = [corpus[doc_id] for doc_id in corpus_ids]
    
    # Delete collection if it exists
    if collection_exists:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    
    # Create new collection with the embedding function
    collection = client.create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    print(f"Created new collection: {collection_name}")
    
    # Add documents to collection
    batch_size = 32  # ChromaDB add batch size
    
    # Use tqdm if show_progress_bar is True
    iterator = tqdm(range(0, len(corpus_ids), batch_size)) if cfg.show_progress_bar else range(0, len(corpus_ids), batch_size)
    
    for i in iterator:
        # Get batch data
        batch_ids = corpus_ids[i:i+batch_size]
        batch_texts = corpus_texts[i:i+batch_size]
        
        # Add batch to collection - ChromaDB will handle embedding automatically
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=[{"text": text} for text in batch_texts]
        )
    
    print(f"Finished initializing collection: {collection_name}")

def evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name):
    """Evaluate retrieval performance using ChromaDB and SentenceTransformer evaluator."""
    print(f"\nEvaluating {model_name} using ChromaDB rankings...")
    
    # Get ChromaDB collection
    client = chromadb.Client()
    
    # Add debug info storage
    model_rankings = {}
    
    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error: Collection {collection_name} not found. Did you run initialization?")
        raise e
    
    # Set up evaluator with all config parameters
    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        mrr_at_k=cfg.mrr_at_k,
        ndcg_at_k=cfg.ndcg_at_k,
        accuracy_at_k=[cfg.k],  # Use k as a fallback if not in config
        precision_recall_at_k=cfg.precision_recall_at_k,
        map_at_k=cfg.map_at_k,
        show_progress_bar=cfg.show_progress_bar,
        batch_size=cfg.batch_size,
        name=f"{model_name}-chromadb"
    )
    
    # Get mapping from query ID to index
    query_id_to_idx = {qid: idx for idx, qid in enumerate(evaluator.queries_ids)}
    
    # Initialize results list for evaluator
    queries_result_list = [[] for _ in range(len(evaluator.queries_ids))]
    
    # Process each query
    query_iterator = tqdm(queries.items()) if cfg.show_progress_bar else queries.items()
    for qid, query_text in query_iterator:
        if qid not in relevant_docs or qid not in query_id_to_idx:
            continue
            
        # Get query index for evaluator
        query_idx = query_id_to_idx[qid]
        
        # Query ChromaDB directly with text - the embedding function will handle conversion
        results = collection.query(
            query_texts=[query_text],
            n_results=100  # Get more results than needed to ensure we have enough
        )
        
        # Store rankings for debugging
        model_rankings[qid] = results['ids'][0]
        
        # Store results in evaluator format
        for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
            # Convert distance to similarity score (higher is better)
            similarity = 1.0 / (1.0 + float(distance))
            queries_result_list[query_idx].append({
                "corpus_id": doc_id,
                "score": similarity
            })
        
        # Show top results for this query
        print(f"\nQuery {qid}: {query_text}")
        print(f"Relevant docs: {relevant_docs[qid]}")
        print(f"Top {cfg.k} retrieved docs:")
        for i, doc_score in enumerate(queries_result_list[query_idx][:cfg.k]):
            doc_id = doc_score["corpus_id"]
            is_relevant = doc_id in relevant_docs[qid]
            rel_marker = " (REL)" if is_relevant else ""
            print(f"  {i+1}. {doc_id} (score: {doc_score['score']:.4f}){rel_marker}")
    
    # Print detailed rankings for debugging
    print(f"\nDEBUG - Full rankings for {model_name}:")
    for qid, ranking in model_rankings.items():
        print(f"  Query {qid}:")
        print(f"    Top 5 docs: {ranking[:5]}")
    
    # Calculate metrics using ChromaDB rankings
    scores = evaluator.compute_metrics(queries_result_list)
    
    # Extract metrics based on config settings
    k = cfg.k
    metrics = {}
    
    if cfg.compute_map:
        metrics["map"] = scores["map@k"][k]
    else:
        metrics["map"] = 0.0
        
    if cfg.compute_recall:
        metrics["recall"] = scores["recall@k"][k]
    else:
        metrics["recall"] = 0.0
        
    if cfg.compute_precision:
        metrics["precision"] = scores["precision@k"][k]
    else:
        metrics["precision"] = 0.0
        
    if cfg.compute_ndcg:
        metrics["ndcg"] = scores["ndcg@k"][k]
    else:
        metrics["ndcg"] = 0.0
        
    if cfg.compute_mrr:
        metrics["mrr"] = scores["mrr@k"][k]
    else:
        metrics["mrr"] = 0.0
    
    # Print metrics
    print(f"\nMetrics for {model_name} using ChromaDB rankings:")
    if cfg.compute_map:
        print(f"MAP@{k}: {metrics['map']:.4f}")
    if cfg.compute_recall:
        print(f"Recall@{k}: {metrics['recall']:.4f}")
    if cfg.compute_precision:
        print(f"Precision@{k}: {metrics['precision']:.4f}")
    if cfg.compute_ndcg:
        print(f"NDCG@{k}: {metrics['ndcg']:.4f}")
    if cfg.compute_mrr:
        print(f"MRR@{k}: {metrics['mrr']:.4f}")
    
    return (
        metrics["map"],
        metrics["recall"],
        metrics["precision"],
        metrics["ndcg"],
        metrics["mrr"]
    )



def load_ground_truth():
    """
    Load ground truth data files (corpus, queries, relevance judgments).
    
    Returns:
        tuple of (queries, corpus, relevant_docs)
    """
    print("Loading ground-truth files...")
    
    # Load queries
    with open(cfg.queries_file) as qf:
        queries = {j["query_id"]: j["text"] for j in map(json.loads, qf)}

    # Load corpus
    with open(cfg.corpus_file) as cf:
        corpus = {j["doc_id"]: j["text"] for j in map(json.loads, cf)}

    # Load relevance judgments
    relevant_docs = {}
    with open(cfg.qrels_file, 'r', encoding='utf-8') as rf:
        for line in rf:
            parts = line.strip().split()
            if len(parts) == 3:
                qid, doc_id, rel = parts
                try:
                    rel_int = int(rel)
                    if rel_int > 0:
                        relevant_docs.setdefault(qid, set()).add(doc_id)
                except ValueError:
                    continue
    
    print(f"Loaded {len(queries)} queries, {len(corpus)} corpus chunks, and {sum(len(v) for v in relevant_docs.values())} relevance mappings.")
    return queries, corpus, relevant_docs

def get_chromadb_client():
    """Get a persistent ChromaDB client that saves data to disk"""
    import chromadb
    import os
    
    # Ensure the directory exists (same path as your chromadb_utils)
    os.makedirs(os.path.join("utils", "chromadb_collections"), exist_ok=True)
    
    # Create persistent client
    client = chromadb.PersistentClient(path=os.path.join("utils", "chromadb_collections"))
    return client


def initialize_collection(corpus, model_name, collection_name):
    """Initialize a ChromaDB collection with document embeddings."""
    print(f"Initializing ChromaDB collection: {collection_name} with model: {model_name}...")
    
    # Check if collection exists and should be reinitialized
    client = get_chromadb_client()
    collection_exists = False
    
    try:
        client.get_collection(collection_name)
        collection_exists = True
    except:
        collection_exists = False
    
    if collection_exists and not cfg.reinitialize_collections:
        print(f"Collection {collection_name} already exists and reinitialize_collections=False. Skipping initialization.")
        return
    
    # Initialize SentenceTransformer embedding function
    from chromadb.utils import embedding_functions

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )
    
    # DEBUGGING: Test embedding output
    test_text = "This is a test sentence to verify embedding differences"
    test_embedding = sentence_transformer_ef([test_text])[0]
    print(f"DEBUG - First 5 dimensions of embedding for '{model_name}':")
    print(f"  {test_embedding[:5]}")
    
    # Get corpus IDs and texts
    corpus_ids = list(corpus.keys())
    corpus_texts = [corpus[doc_id] for doc_id in corpus_ids]
    
    # Delete collection if it exists
    if collection_exists:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    
    # Create new collection with the embedding function
    collection = client.create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    print(f"Created new collection: {collection_name}")
    
    # Add documents to collection
    batch_size = 32  # ChromaDB add batch size
    
    # Use tqdm if show_progress_bar is True
    iterator = tqdm(range(0, len(corpus_ids), batch_size)) if cfg.show_progress_bar else range(0, len(corpus_ids), batch_size)
    
    for i in iterator:
        # Get batch data
        batch_ids = corpus_ids[i:i+batch_size]
        batch_texts = corpus_texts[i:i+batch_size]
        
        # Add batch to collection - ChromaDB will handle embedding automatically
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=[{"text": text} for text in batch_texts]
        )
    
    print(f"Finished initializing collection: {collection_name}")

def evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name):
    """Evaluate retrieval performance using ChromaDB and SentenceTransformer evaluator."""
    print(f"\nEvaluating {model_name} using ChromaDB rankings...")
    
    # Use persistent client instead of chromadb.Client()
    client = get_chromadb_client()
    
    # Add debug info storage
    model_rankings = {}
    
    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error: Collection {collection_name} not found. Did you run initialization?")
        raise e
    
    # Set up evaluator with all config parameters
    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        mrr_at_k=cfg.mrr_at_k,
        ndcg_at_k=cfg.ndcg_at_k,
        accuracy_at_k=[cfg.k],  # Use k as a fallback if not in config
        precision_recall_at_k=cfg.precision_recall_at_k,
        map_at_k=cfg.map_at_k,
        show_progress_bar=cfg.show_progress_bar,
        batch_size=cfg.batch_size,
        name=f"{model_name}-chromadb"
    )
    
    # Get mapping from query ID to index
    query_id_to_idx = {qid: idx for idx, qid in enumerate(evaluator.queries_ids)}
    
    # Initialize results list for evaluator
    queries_result_list = [[] for _ in range(len(evaluator.queries_ids))]
    
    # Process each query
    query_iterator = tqdm(queries.items()) if cfg.show_progress_bar else queries.items()
    for qid, query_text in query_iterator:
        if qid not in relevant_docs or qid not in query_id_to_idx:
            continue
            
        # Get query index for evaluator
        query_idx = query_id_to_idx[qid]
        
        # Query ChromaDB directly with text - the embedding function will handle conversion
        results = collection.query(
            query_texts=[query_text],
            n_results=100  # Get more results than needed to ensure we have enough
        )
        
        # Store rankings for debugging
        model_rankings[qid] = results['ids'][0]
        
        # Store results in evaluator format
        for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
            # Convert distance to similarity score (higher is better)
            similarity = 1.0 / (1.0 + float(distance))
            queries_result_list[query_idx].append({
                "corpus_id": doc_id,
                "score": similarity
            })
        
        # Show top results for this query
        print(f"\nQuery {qid}: {query_text}")
        print(f"Relevant docs: {relevant_docs[qid]}")
        print(f"Top {cfg.k} retrieved docs:")
        for i, doc_score in enumerate(queries_result_list[query_idx][:cfg.k]):
            doc_id = doc_score["corpus_id"]
            is_relevant = doc_id in relevant_docs[qid]
            rel_marker = " (REL)" if is_relevant else ""
            print(f"  {i+1}. {doc_id} (score: {doc_score['score']:.4f}){rel_marker}")
    
    # Print detailed rankings for debugging
    print(f"\nDEBUG - Full rankings for {model_name}:")
    for qid, ranking in model_rankings.items():
        print(f"  Query {qid}:")
        print(f"    Top 5 docs: {ranking[:5]}")
    
    # Calculate metrics using ChromaDB rankings
    scores = evaluator.compute_metrics(queries_result_list)
    
    # Extract metrics based on config settings
    k = cfg.k
    metrics = {}
    
    if cfg.compute_map:
        metrics["map"] = scores["map@k"][k]
    else:
        metrics["map"] = 0.0
        
    if cfg.compute_recall:
        metrics["recall"] = scores["recall@k"][k]
    else:
        metrics["recall"] = 0.0
        
    if cfg.compute_precision:
        metrics["precision"] = scores["precision@k"][k]
    else:
        metrics["precision"] = 0.0
        
    if cfg.compute_ndcg:
        metrics["ndcg"] = scores["ndcg@k"][k]
    else:
        metrics["ndcg"] = 0.0
        
    if cfg.compute_mrr:
        metrics["mrr"] = scores["mrr@k"][k]
    else:
        metrics["mrr"] = 0.0
    
    # Print metrics
    print(f"\nMetrics for {model_name} using ChromaDB rankings:")
    if cfg.compute_map:
        print(f"MAP@{k}: {metrics['map']:.4f}")
    if cfg.compute_recall:
        print(f"Recall@{k}: {metrics['recall']:.4f}")
    if cfg.compute_precision:
        print(f"Precision@{k}: {metrics['precision']:.4f}")
    if cfg.compute_ndcg:
        print(f"NDCG@{k}: {metrics['ndcg']:.4f}")
    if cfg.compute_mrr:
        print(f"MRR@{k}: {metrics['mrr']:.4f}")
    
    return (
        metrics["map"],
        metrics["recall"],
        metrics["precision"],
        metrics["ndcg"],
        metrics["mrr"]
    )



def main():
    parser = argparse.ArgumentParser(description="RAG Benchmark Pipeline")
    parser.add_argument("--prepare-corpus", action="store_true", help="Prepare corpus.jsonl from PDFs")
    parser.add_argument("--generate-queries", action="store_true", help="Generate queries from corpus")
    parser.add_argument("--generate-qrels", action="store_true", help="Generate qrels file")
    parser.add_argument("--initialize", action="store_true", help="Initialize collections")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate models")
    parser.add_argument("--all", action="store_true", help="Run complete pipeline")
    args = parser.parse_args()

    # Create necessary directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs(cfg.pdf_dir, exist_ok=True)
    
    if args.prepare_corpus:
        prepare_corpus_from_pdfs()
        return
        
    if args.generate_queries:
        generate_queries_from_corpus()
        return
        
    if args.generate_qrels:
        generate_qrels()
        return
        
    if args.all:
        # Run complete pipeline
        print("Starting complete RAG benchmark pipeline...")
        
        # Step 1: Prepare corpus
        prepare_corpus_from_pdfs()
        
        # Step 2: Generate queries
        generate_queries_from_corpus()
        
        # Step 3: Generate qrels
        generate_qrels()
        
        # Continue with evaluation...
        
    # Validate existence of required files for evaluation
    if args.initialize or args.evaluate or args.all:
        for file_path in [cfg.corpus_file, cfg.queries_file, cfg.qrels_file]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        print("Starting embedding model evaluation...")
        print(f"Configuration: k={cfg.k}, show_progress={cfg.show_progress_bar}, reinit_collections={cfg.reinitialize_collections}")
        
        # Load data
        queries, corpus, relevant_docs = load_ground_truth()
        
        # Process each model
        model_results = []
        
        for model_cfg in cfg.embedding_models:
            model_name = model_cfg["model_name"]
            collection_name = model_cfg["collection_name"]
            
            # Initialize collection
            if args.initialize or args.all:
                initialize_collection(corpus, model_name, collection_name)
            
            # Evaluate model
            if args.evaluate or args.all:
                metrics = evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name)
                model_results.append((model_name, *metrics))
        
        # Print summary
        if model_results:
            print("\n=== Benchmark Results Summary ===")
            header = f"{'Model':<60}"
            if cfg.compute_map:
                header += f" | {'MAP@' + str(cfg.k):<8}"
            if cfg.compute_recall:
                header += f" | {'Recall@' + str(cfg.k):<8}"
            if cfg.compute_precision:
                header += f" | {'Prec@' + str(cfg.k):<8}"
            if cfg.compute_ndcg:
                header += f" | {'NDCG@' + str(cfg.k):<8}"
            if cfg.compute_mrr:
                header += f" | {'MRR@' + str(cfg.k):<8}"
            
            print(header)
            print("-" * len(header))
            
            for result in model_results:
                model_name = result[0]
                metrics = result[1:]
                
                line = f"{model_name:<60}"
                idx = 0
                
                if cfg.compute_map:
                    line += f" | {metrics[idx]:<8.4f}"
                    idx += 1
                if cfg.compute_recall:
                    line += f" | {metrics[idx]:<8.4f}"
                    idx += 1
                if cfg.compute_precision:
                    line += f" | {metrics[idx]:<8.4f}"
                    idx += 1
                if cfg.compute_ndcg:
                    line += f" | {metrics[idx]:<8.4f}"
                    idx += 1
                if cfg.compute_mrr:
                    line += f" | {metrics[idx]:<8.4f}"
                
                print(line)
        
            # Generate detailed report
            if model_results:
                report_files = generate_benchmark_report(model_results, queries, corpus, relevant_docs)
                if isinstance(report_files, tuple):
                    md_file, pdf_file = report_files
                    print(f"\nDetailed benchmark report saved:")
                    print(f"  Markdown: {md_file}")
                    if pdf_file:
                        print(f"  PDF: {pdf_file}")
                else:
                    # Backward compatibility if function returns single file
                    print(f"\nDetailed benchmark report saved to: {report_files}")
    print("\nBenchmark completed!")

if __name__ == "__main__":
    main()