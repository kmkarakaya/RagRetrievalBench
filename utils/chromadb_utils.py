import chromadb
from chromadb.utils import embedding_functions
import random
import os
from tqdm import tqdm
from sentence_transformers import evaluation
import time


import benchmark_config as cfg


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
    
    # Get ChromaDB client
    client = get_chromadb_client()
    
    # Check if collection exists
    try:
        collection = client.get_collection(collection_name)
        if not cfg.reinitialize_collections:
            print(f"Collection {collection_name} already exists and reinitialize_collections=False. Skipping initialization.")
            return 0.0  # Return 0 time if skipped
        # Delete existing collection if reinitialization is enabled
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        print(f"Collection {collection_name} does not exist. Creating a new one...")
    
    # Initialize SentenceTransformer embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )
    
    # Create new collection
    collection = client.create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    print(f"Created new collection: {collection_name}")
    
    # Start timing for embedding process only
    embedding_start_time = time.time()
    
    # Add documents to collection in batches
    batch_size = cfg.document_batch_size  # Use document_batch_size from benchmark_config
    corpus_ids = list(corpus.keys())
    corpus_texts = list(corpus.values())
    
    # Fixed (shorter, cleaner description):
    short_model_name = model_name.split('/')[-1]  # Get just the model name part
    iterator = tqdm(range(0, len(corpus_ids), batch_size), desc=f"Embedding with {short_model_name}") if cfg.show_progress_bar else range(0, len(corpus_ids), batch_size)
    for i in iterator:
        batch_ids = corpus_ids[i:i+batch_size]
        batch_texts = corpus_texts[i:i+batch_size]
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=[{"text": text} for text in batch_texts]
        )
    
    # Calculate embedding time and performance metrics
    embedding_time = time.time() - embedding_start_time
    docs_per_second = len(corpus_ids) / embedding_time
    avg_time_per_doc = embedding_time / len(corpus_ids)
    
    print(f"Finished initializing collection: {collection_name}")
    print(f"Embedding performance:")
    print(f"  Embedding time: {embedding_time:.2f} seconds")
    print(f"  Documents processed: {len(corpus_ids)}")
    print(f"  Documents per second: {docs_per_second:.2f}")
    print(f"  Average time per document: {avg_time_per_doc:.4f} seconds")
    
    timing_data = {
        "embedding_time": embedding_time,
        "docs_processed": len(corpus_ids),
        "docs_per_second": docs_per_second,
        "avg_time_per_doc": avg_time_per_doc
    }
    

    
    return timing_data




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
        batch_size=cfg.document_batch_size,
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
    # print(f"\nDEBUG - Full rankings for {model_name}:")
    # for qid, ranking in model_rankings.items():
    #     print(f"  Query {qid}:")
    #     print(f"    Top 5 docs: {ranking[:5]}")
    
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


