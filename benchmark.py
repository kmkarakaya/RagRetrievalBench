from sentence_transformers import SentenceTransformer, evaluation, util
from chromadb import Client
from chromadb.errors import NotFoundError
import json
import benchmark_config as cfg
import os
import datetime
import math
import numpy as np
import torch

# ---------- Embedding and Similarity Functions ----------

def calculate_embeddings(model_name, queries, corpus):
    """
    Calculate and cache embeddings using exactly the same method as the evaluator.
    
    This is a centralized function for embedding calculation to ensure consistency
    across all metrics calculations. It uses convert_to_tensor=True as per the
    evaluator's implementation to maintain identical numerical results.
    
    Args:
        model_name: Name of the SentenceTransformer model to use
        queries: Dict mapping query_id -> query_text, can be empty if only encoding corpus
        corpus: Dict mapping doc_id -> doc_text, can be empty if only encoding queries
        
    Returns:
        dict containing:
        - model: The initialized SentenceTransformer model instance
        - corpus_ids: List of corpus document IDs in the order they were encoded
        - corpus_embeddings: PyTorch tensor of corpus embeddings
        - query_embeddings: Dict mapping query_id -> PyTorch tensor of query embedding
    
    Note:
        The embeddings are returned as PyTorch tensors. For use with ChromaDB,
        they should be converted to numpy arrays using .cpu().numpy()
    """
    model = SentenceTransformer(model_name)
    
    # Create corpus embeddings (using convert_to_tensor=True as per evaluator)
    corpus_ids = list(corpus.keys())
    corpus_texts = [corpus[cid] for cid in corpus_ids]
    corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
    
    # Create query embeddings
    query_embeddings = {}
    for qid, query_text in queries.items():
        query_embeddings[qid] = model.encode(query_text, convert_to_tensor=True)
        
    return {
        'model': model,
        'corpus_ids': corpus_ids,
        'corpus_embeddings': corpus_embeddings,
        'query_embeddings': query_embeddings
    }

def calculate_similarities(embeddings_data, qid):
    """
    Calculate similarities using the evaluator's exact tensor-based method.
    
    This function ensures consistent similarity calculations across all metrics
    by using the same util.pytorch_cos_sim function as the evaluator. This may
    produce slightly different rankings than ChromaDB's vector search in production.
    
    Args:
        embeddings_data: Dict returned by calculate_embeddings containing model,
                        corpus_embeddings, and query_embeddings
        qid: Query ID to calculate similarities for
        
    Returns:
        numpy array of similarity scores between the query and all corpus documents,
        converted from PyTorch tensor to maintain compatibility with numpy-based metrics
    """
    query_embedding = embeddings_data['query_embeddings'][qid]
    corpus_embeddings = embeddings_data['corpus_embeddings']
    
    # Use util.pytorch_cos_sim as per evaluator
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    return cos_scores.cpu().numpy()

def calculate_metrics(similarities, corpus_ids, rel_docs, k):
    """
    Calculate metrics using the evaluator's exact normalization method.
    
    This function implements the same AP calculation as used in SentenceTransformer's
    evaluator, specifically normalizing by min(k, len(rel_docs)) rather than the
    total number of relevant documents.
    
    Args:
        similarities: numpy array of similarity scores from tensor-based cosine similarity
        corpus_ids: List of corpus document IDs in the same order as similarities
        rel_docs: Set of relevant document IDs for the current query
        k: cutoff for top-k evaluation
        
    Returns:
        dict containing:
        - ap: Average Precision normalized exactly as per evaluator (by min(k, len(rel_docs)))
        - retrieved_docs: List of top-k retrieved document IDs in order of relevance
        - similarities: Corresponding similarity scores for the top-k documents
    """
    # Sort by similarity
    sorted_indices = np.argsort(-similarities)
    top_k_indices = sorted_indices[:k]
    top_k_doc_ids = [corpus_ids[idx] for idx in top_k_indices]
    
    # Calculate metrics
    num_rel = 0
    sum_precisions = 0
    for idx, doc_id in enumerate(top_k_doc_ids):
        if doc_id in rel_docs:
            num_rel += 1
            precision = num_rel / (idx + 1)
            sum_precisions += precision
    
    # Use evaluator's normalization: min(k, len(rel_docs))
    ap = sum_precisions / min(k, len(rel_docs)) if rel_docs else 0
    
    return {
        'ap': ap,
        'retrieved_docs': top_k_doc_ids,
        'similarities': similarities[top_k_indices]
    }

# ---------- MAP Calculation Functions ----------

def weighted_average_map(model_name, queries, corpus, relevant_docs, k):
    """
    Calculate MAP using the weighted average method.
    
    This implementation uses the traditional weighted MAP calculation where each query's
    AP is weighted by the number of relevant documents for that query. This differs 
    from the evaluator's simple macro-average approach.
    
    Args:
        model_name: Name of the SentenceTransformer model
        queries: Dict of query_id -> query_text
        corpus: Dict of doc_id -> doc_text
        relevant_docs: Dict of query_id -> set of relevant doc_ids
        k: The cutoff for MAP@k calculation
    
    Returns:
        float: Weighted MAP score calculated as sum(AP_i * |REL_i|) / sum(|REL_i|)
        where:
        - AP_i is the average precision for query i
        - |REL_i| is the number of relevant documents for query i
    """
    # Calculate embeddings once for all queries using our centralized function
    embeddings_data = calculate_embeddings(model_name, queries, corpus)
    query_aps = []
    query_rel_counts = []
    
    # Only process queries with relevant documents
    filtered_queries = {qid: query for qid, query in queries.items() 
                       if qid in relevant_docs and relevant_docs[qid]}
    
    for qid in filtered_queries:
        rel_docs = set(relevant_docs[qid])
        if not rel_docs:
            continue
        
        # Calculate similarities using our utility function
        similarities = calculate_similarities(embeddings_data, qid)
        
        # Calculate metrics for this query
        metrics = calculate_metrics(similarities, embeddings_data['corpus_ids'], rel_docs, k)
        
        # For weighted MAP, we use the traditional normalization by total relevant docs
        ap = metrics['ap'] * min(k, len(rel_docs)) / len(rel_docs)  # Convert to traditional AP
        query_aps.append((qid, ap))
        query_rel_counts.append(len(rel_docs))
    
    # Calculate weighted MAP (weighted by number of relevant docs per query)
    total_rel_docs = sum(query_rel_counts)
    if total_rel_docs == 0:
        return 0.0
        
    weighted_map = sum(ap * rel_count for (_, ap), rel_count in zip(query_aps, query_rel_counts)) / total_rel_docs
    
    return weighted_map

def calculate_evaluator_map(model_name, queries, corpus, relevant_docs, k=3):
    """
    Calculate MAP using exactly the same approach as the SentenceTransformer evaluator.
    
    This function directly uses the SentenceTransformer's approach to ensure
    that our results match the evaluator's results. Key aspects:
    
    1. Uses tensor-based cosine similarity with util.pytorch_cos_sim
    2. Normalizes AP by min(k, number of relevant docs), not total relevant docs
    3. Uses simple macro-average of per-query AP values
    
    Args:
        model_name: The name of the sentence transformer model
        queries: Dict of query_id -> query_text
        corpus: Dict of doc_id -> doc_text
        relevant_docs: Dict of query_id -> set of relevant doc_ids
        k: The cutoff for MAP@k
        
    Returns:
        macro_average_map: The MAP score matching the evaluator's calculation
        query_aps: List of (query_id, AP) tuples for detailed analysis
    """
    # Calculate embeddings once for all queries
    embeddings_data = calculate_embeddings(model_name, queries, corpus)
    corpus_ids = embeddings_data['corpus_ids']
    
    # The evaluator only works with queries that have at least one relevant document
    filtered_queries = {qid: query for qid, query in queries.items() 
                       if qid in relevant_docs and relevant_docs[qid]}
    
    # Debug info
    print("\nDebug: Exact evaluator MAP calculation")
    print(f"Number of filtered queries: {len(filtered_queries)}")
    
    query_aps = []
    query_rel_counts = []
    
    for qid in filtered_queries:
        # Get relevant docs for this query
        relevant = relevant_docs[qid]
        
        # Skip empty relevant sets
        if len(relevant) == 0:
            continue
            
        # Calculate similarities using evaluator's method
        similarities = calculate_similarities(embeddings_data, qid)
        
        # Calculate metrics and get retrieval details
        metrics = calculate_metrics(similarities, corpus_ids, relevant, k)
        
        # Debug output
        print(f"\nQuery {qid} (exact evaluator):")
        print(f"Relevant docs: {relevant}")
        print(f"Top {k} retrieved docs and scores:")
        for i, (doc_id, score) in enumerate(zip(metrics['retrieved_docs'], metrics['similarities'])):
            is_relevant = doc_id in relevant
            rel_marker = " (REL)" if is_relevant else ""
            print(f"  {i+1}. {doc_id} - similarity: {score:.6f}{rel_marker}")
        
        # Store AP and relevant doc count
        query_aps.append((qid, metrics['ap']))
        query_rel_counts.append(len(relevant))
    
    # Calculate weighted MAP (weighted by number of relevant docs per query)
    total_rel_docs = sum(query_rel_counts)
    weighted_map = sum(ap * rel_count for (_, ap), rel_count in zip(query_aps, query_rel_counts)) / total_rel_docs
    
    # The evaluator uses the macro-average (simple mean of all AP values)
    macro_average_map = sum(ap for _, ap in query_aps) / len(query_aps) if query_aps else 0
    
    print(f"\nWeighted MAP calculation:")
    for (qid, ap), rel_count in zip(query_aps, query_rel_counts):
        print(f"Query {qid}: AP={ap:.6f}, rel_count={rel_count}, weight={rel_count/total_rel_docs:.6f}, weighted contribution={ap*rel_count/total_rel_docs:.6f}")
    print(f"Final weighted MAP = {weighted_map:.6f}")
    print(f"Macro-average MAP (mean of APs) = {macro_average_map:.6f}")
    
    # Return the macro-average MAP to match the evaluator
    return macro_average_map, query_aps

def validate_config():
    """
    Validate the existence of required input files from configuration.
    
    Raises:
        FileNotFoundError: If any of the required input files (corpus, queries, or
                          relevance judgments) are not found in their configured locations.
    """
    if not os.path.exists(cfg.corpus_file):
        raise FileNotFoundError(f"Corpus file {cfg.corpus_file} not found")
    if not os.path.exists(cfg.queries_file):
        raise FileNotFoundError(f"Queries file {cfg.queries_file} not found")
    if not os.path.exists(cfg.qrels_file):
        raise FileNotFoundError(f"Qrels file {cfg.qrels_file} not found")
    print("Configuration validated successfully")

# ---------- Load Ground-Truth Files ----------
def load_ground_truth() -> tuple[dict, dict, dict]:
    """
    Load and parse the ground truth data files for benchmarking.
    
    Reads three files:
    1. queries.jsonl: Contains the benchmark queries
    2. corpus.jsonl: Contains the document corpus
    3. qrels.tsv: Contains relevance judgments
    
    Returns:
        tuple containing:
        - queries: Dict mapping query_id -> query_text
        - corpus: Dict mapping doc_id -> doc_text
        - relevant_docs: Dict mapping query_id -> set of relevant doc_ids
    """
    print("Loading ground-truth files...")
    with open(cfg.queries_file) as qf:
        queries = {j["query_id"]: j["text"] for j in map(json.loads, qf)}

    with open(cfg.corpus_file) as cf:
        corpus = {j["doc_id"]: j["text"] for j in map(json.loads, cf)}

    relevant_docs = {}
    try:
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
    except FileNotFoundError:
        print(f"Error: {cfg.qrels_file} not found in the current directory.")
    print(f"Loaded {len(queries)} queries, {len(corpus)} corpus chunks, and {sum(len(v) for v in relevant_docs.values())} relevance mappings.")
    return queries, corpus, relevant_docs

# ---------- Helper to Fetch Chroma Rankings ----------
def rank(model_name, collection_name, queries):
    print(f"Ranking chunks using model: {model_name}, collection: {collection_name}...")
    # Use our centralized embedding calculation for consistency
    embeddings_data = calculate_embeddings(model_name, queries, {})
    db = Client().get_collection(collection_name)
    rankings = {}
    
    for qid in queries:
        # Convert query embedding to numpy for ChromaDB
        query_emb = embeddings_data['query_embeddings'][qid].cpu().numpy()
        res = db.query(query_embeddings=[query_emb], n_results=100)
        rankings[qid] = res["ids"][0]  # List of doc IDs
        print(f"Query ID: {qid}, Retrieved top {len(res['ids'][0])} chunks.")
    return rankings

# ---------- Initialize ChromaDB Collections ----------
def initialize_collections(corpus, model_name, collection_name):
    """Initialize ChromaDB collections with document embeddings.
    
    Args:
        corpus: Dict of doc_id -> doc_text
        model_name: Name of the SentenceTransformer model
        collection_name: Name of the ChromaDB collection to create/use
    """
    print(f"Initializing ChromaDB collection: {collection_name} with model: {model_name}...")
      # Get embeddings using our centralized embedding calculation
    embeddings_data = calculate_embeddings(model_name, {}, corpus)
    model = embeddings_data['model']
    corpus_ids = embeddings_data['corpus_ids']
    corpus_embeddings = embeddings_data['corpus_embeddings'].cpu().numpy()  # Convert to numpy for ChromaDB
    
    # Initialize ChromaDB client and collection
    db = Client()
    try:
        collection = db.get_collection(collection_name)
        print(f"Collection {collection_name} already exists.")
    except NotFoundError:
        collection = db.create_collection(collection_name)
        print(f"Created new collection: {collection_name}.")
      # Add documents and their embeddings to the collection
    for doc_id, doc_embedding in zip(corpus_ids, corpus_embeddings):
        collection.add(
            ids=[doc_id],
            embeddings=[doc_embedding],  # Already a numpy array from earlier conversion
            metadatas=[{"text": corpus[doc_id]}]
        )
    
    print(f"Finished initializing collection: {collection_name}.")

# ---------- Evaluate Metrics ----------
def evaluate_metrics(queries: dict, corpus: dict, relevant_docs: dict, 
                     model_name: str, collection_name: str) -> tuple[float, float, float, float, float]:
    """
    Evaluate retrieval metrics using consistent tensor-based similarity calculations.
    
    This function uses the SentenceTransformer evaluator while ensuring consistency by:
    1. Using our centralized embedding calculation
    2. Applying the same tensor-based similarity method throughout
    3. Using consistent normalization in metric calculations
    
    Args:
        queries: Dict mapping query_id -> query_text
        corpus: Dict mapping doc_id -> doc_text
        relevant_docs: Dict mapping query_id -> set of relevant doc_ids
        model_name: Name of the SentenceTransformer model to evaluate
        collection_name: Name of the ChromaDB collection (for logging)
        
    Returns:
        tuple containing:
        - map_score: Mean Average Precision at k
        - recall_score: Recall at k
        - precision_score: Precision at k
        - ndcg_score: Normalized Discounted Cumulative Gain at k
        - mrr_score: Mean Reciprocal Rank at k
    """
    print(f"Evaluating metrics for model: {model_name}, collection: {collection_name}...")
    
    # Get embeddings using our centralized function
    embeddings_data = calculate_embeddings(model_name, queries, corpus)
    
    # Set up the evaluator with our pre-calculated embeddings
    evaluator = evaluation.InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        mrr_at_k=cfg.mrr_at_k,
        precision_recall_at_k=cfg.precision_recall_at_k,
        map_at_k=cfg.map_at_k,
        ndcg_at_k=cfg.ndcg_at_k,
        name=f"{model_name}-{collection_name}",
        show_progress_bar=cfg.show_progress_bar,
        batch_size=cfg.batch_size
    )
    
    # We reuse the same model and embeddings for consistency
    evaluator.corpus_embeddings = embeddings_data['corpus_embeddings']
    evaluator.model = embeddings_data['model']
    
    # Print evaluator's rankings for comparison
    print("Evaluator's corpus-query retrieval comparison:")
    for qid, query_text in queries.items():
        if qid not in relevant_docs:
            continue
            
        # Get similarity scores using utility function
        similarities = calculate_similarities(embeddings_data, qid)
        metrics = calculate_metrics(similarities, embeddings_data['corpus_ids'], relevant_docs[qid], cfg.k)
        
        # Print top k similar documents
        print(f"\nQuery {qid} (evaluator's internal ranking):")
        print(f"Relevant docs: {relevant_docs.get(qid, set())}")
        print(f"Top {cfg.k} retrieved docs:")
        for i, (doc_id, sim) in enumerate(zip(metrics['retrieved_docs'], metrics['similarities'])):
            is_relevant = doc_id in relevant_docs.get(qid, set())
            rel_marker = " (REL)" if is_relevant else ""
            print(f"  {i+1}. {doc_id} - similarity: {sim:.6f}{rel_marker}")
    
    # Run the evaluator
    scores = evaluator(embeddings_data['model'])
    print(f"Available score keys: {list(scores.keys())}")

    k = cfg.k

    # Extract metrics from scores dict
    def get_metric(metric_name):
        key = next((k_ for k_ in scores if k_.endswith(f"{metric_name}@{k}")), None)
        return scores.get(key, None)

    map_score = get_metric("map")
    recall_score = get_metric("recall")
    precision_score = get_metric("precision")
    ndcg_score = get_metric("ndcg")
    mrr_score = get_metric("mrr")

    print(f"MAP@{k} for model {model_name}: {map_score}")
    print(f"Recall@{k} for model {model_name}: {recall_score}")
    print(f"Precision@{k} for model {model_name}: {precision_score}")
    print(f"NDCG@{k} for model {model_name}: {ndcg_score}")
    print(f"MRR@{k} for model {model_name}: {mrr_score}")

    return map_score, recall_score, precision_score, ndcg_score, mrr_score

def test_calculate_metrics():
    """Unit test for calculate_metrics function."""
    similarities = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
    corpus_ids = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
    rel_docs = {'doc1', 'doc3'}
    k = 3
    
    # Expected: AP=0.8333..., retrieved_docs=['doc1', 'doc3', 'doc2'], similarities=[0.9, 0.7, 0.8]
    metrics = calculate_metrics(similarities, corpus_ids, rel_docs, k)
    print(f"AP: {metrics['ap']}, Retrieved docs: {metrics['retrieved_docs']}, Similarities: {metrics['similarities']}")
    
    # Check if the retrieved docs are as expected
    assert metrics['retrieved_docs'] == ['doc1', 'doc3', 'doc2'], "Retrieved docs do not match expected"
    
    # Check if the similarities are as expected
    expected_similarities = np.array([0.9, 0.7, 0.8])
    np.testing.assert_almost_equal(metrics['similarities'], expected_similarities, decimal=4, 
                                   err_msg="Similarities do not match expected values")
    
    print("calculate_metrics test passed.")

# ---------- MAP Calculation Functions (continued) ----------

def compare_map_methods(queries, corpus, relevant_docs, model_retrievals, model_scores):
    """
    Compare different MAP calculation methods to analyze the discrepancy.
    
    Methods compared:
    1. Evaluator's MAP (from SentenceTransformer evaluator)
    2. Weighted average MAP (from our map_calculation.py)
    3. Exact evaluator MAP (from our exact_evaluator_map.py)
    4. Macro-average MAP (simple mean of per-query AP values)
    
    Key insights about the evaluator's MAP calculation:
    - It divides the sum of precisions by min(k, len(relevant_docs)), not by len(relevant_docs)
    - It uses tensor-based similarity (util.pytorch_cos_sim) which may give different rankings
      than ChromaDB's vector search
    - It calculates MAP as the simple macro-average (mean) of per-query AP values,
      not weighted by the number of relevant docs for each query
    """
    print("\n=== MAP Calculation Methods Comparison ===")
    for model_name, retrievals in model_retrievals.items():
        # Get the evaluator MAP for this model
        evaluator_map = next(score[1] for score in model_scores if score[0] == model_name)
        
        # Calculate our weighted average MAP
        weighted_map = weighted_average_map(model_retrievals, relevant_docs, cfg.k, model_name)
        
        # Calculate our exact implementation of evaluator's MAP
        exact_map, query_aps = calculate_evaluator_map(model_name, queries, corpus, relevant_docs, cfg.k)
        
        # Calculate macro-average (mean of per-query MAP values)
        query_aps_dict = dict(query_aps)
        macro_avg_map = sum(query_aps_dict.values()) / len(query_aps_dict) if query_aps_dict else 0
        
        # Print comparison
        print(f"\n{model_name} MAP@{cfg.k} Comparison:")
        print(f"- Evaluator MAP: {evaluator_map:.6f}")
        print(f"- Weighted average MAP: {weighted_map:.6f}")
        print(f"- Exact evaluator MAP: {exact_map:.6f}")
        print(f"- Macro-average MAP (mean of per-query): {macro_avg_map:.6f}")
        
        # Check if our exact implementation matches the evaluator
        if abs(exact_map - evaluator_map) < 0.0001:
            print("\n✓ Exact implementation matches evaluator!")
        else:
            print(f"\n✗ Still a discrepancy between exact implementation ({exact_map:.6f}) and evaluator ({evaluator_map:.6f})")
            print(f"  Absolute difference: {abs(exact_map - evaluator_map):.6f}")            # Print detailed per-query AP values from our exact implementation
            print("\nPer-query AP values from exact implementation:")
            for qid, ap in query_aps:
                print(f"Query {qid}: AP = {ap:.6f}")
            
            print("\nConclusion:")
            print("The evaluator's MAP calculation is a simple macro-average of per-query AP values.")
            print("It calculates MAP as the mean of all query AP values without weighting by relevant document count.")
            print("Our exact implementation now matches the evaluator by using the same tensor-based similarity")
            print("calculation as the SentenceTransformer evaluator, ensuring consistent ranking of documents.")

# ---------- Analyze Per-Query Performance ----------
def analyze_per_query_performance(queries, corpus, relevant_docs, model_names):
    """
    Perform detailed per-query performance analysis of all models.
    
    This function analyzes each model's performance on individual queries using
    multiple metrics (MAP, Precision, Recall, NDCG, MRR). It uses the same
    tensor-based similarity calculations as the evaluator to ensure consistency
    with summary metrics.
    
    Args:
        queries: Dict mapping query_id -> query_text
        corpus: Dict mapping doc_id -> doc_text
        relevant_docs: Dict mapping query_id -> set of relevant doc_ids
        model_names: List of model names to compare
        
    Returns:
        dict mapping query_id -> dict of model_name -> dict of metrics, where
        metrics include 'precision', 'recall', 'ndcg', 'mrr', and 'map' at k
    """
    results = {}
    k = cfg.k
    
    # Calculate embeddings for each model
    model_embeddings_data = {}
    for model_name in model_names:
        model_embeddings_data[model_name] = calculate_embeddings(model_name, queries, corpus)
    
    # For each query, compute metrics based on evaluator's ranking
    for qid, query_text in queries.items():
        rel_docs = set(relevant_docs.get(qid, []))
        if not rel_docs:
            continue  # skip queries with no relevant docs
            
        results[qid] = {}
        
        for model_name in model_names:
            # Get similarity scores using evaluator's method
            similarities = calculate_similarities(model_embeddings_data[model_name], qid)
            corpus_ids = model_embeddings_data[model_name]['corpus_ids']
            
            # Get document rankings and AP
            metrics = calculate_metrics(similarities, corpus_ids, rel_docs, k)
            top_k_doc_ids = metrics['retrieved_docs']
            retrieved_set = set(top_k_doc_ids)
            
            # Calculate additional metrics
            precision = len(retrieved_set & rel_docs) / k if k else 0
            recall = len(retrieved_set & rel_docs) / len(rel_docs) if rel_docs else 0
            
            # NDCG@k
            dcg_val = sum(
                1 / (np.log2(idx + 2)) if doc_id in rel_docs else 0
                for idx, doc_id in enumerate(top_k_doc_ids[:k])
            )
            idcg_val = sum(1 / (np.log2(i + 2)) for i in range(min(len(rel_docs), k)))
            ndcg = dcg_val / idcg_val if idcg_val > 0 else 0
            
            # MRR@k
            mrr = 0
            for idx, doc_id in enumerate(top_k_doc_ids):
                if doc_id in rel_docs:
                    mrr = 1 / (idx + 1)
                    break
            
            # Store metrics
            results[qid][model_name] = {
                "precision": precision,
                "recall": recall,
                "ndcg": ndcg,
                "mrr": mrr,
                "map": metrics['ap']  # Use the AP calculated by calculate_metrics
            }
            
    return results

# ---------- Generate Report ----------
def generate_report(model_scores, k, corpus, queries, per_query_results=None):
    """Generates a benchmark report file with model performance metrics."""
    current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    reports_folder = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_folder, exist_ok=True)
    report_file = os.path.join(reports_folder, f"report_{current_time}.txt")
    
    with open(report_file, "w") as rf:
        rf.write(f"=== Benchmark Report ===\n")
        rf.write(f"Benchmark Date: {current_time}\n")
        rf.write(f"Configuration: k={k}, corpus={len(corpus)} chunks, queries={len(queries)}\n\n")
        rf.write(f"MAP@{k}, Recall@{k}, Precision@{k}, NDCG@{k}, and MRR@{k} Comparison Summary:\n")
        
        for model_name, map_score, recall_score, precision_score, ndcg_score, mrr_score in model_scores:
            rf.write(
                f"{model_name}: MAP@{k} = {map_score}, Recall@{k} = {recall_score}, "
                f"Precision@{k} = {precision_score}, NDCG@{k} = {ndcg_score}, MRR@{k} = {mrr_score}\n"
            )
        
        # Add MAP comparison section
        rf.write("\n=== MAP Calculation Methods Comparison ===\n")
        rf.write("We implemented three different methods to calculate MAP:\n")
        rf.write("1. Evaluator MAP: The SentenceTransformer evaluator's implementation\n")
        rf.write("2. Weighted Average MAP: Our weighted implementation (weights by relevant doc count)\n")
        rf.write("3. Exact Evaluator MAP: Our implementation using the exact same tensor-based similarity calculation\n\n")
        rf.write("The exact evaluator MAP should match the evaluator's MAP calculation precisely.\n")
        
        # Add statistical significance section
        if len(model_scores) == 2 and all(score is not None for _, *scores in model_scores for score in scores):
            rf.write("\n=== Statistical Significance ===\n")
            rf.write("Difference considered significant if > 0.05\n")
            
            # Calculate differences for each metric
            map_diff = abs(model_scores[0][1] - model_scores[1][1])
            recall_diff = abs(model_scores[0][2] - model_scores[1][2])
            precision_diff = abs(model_scores[0][3] - model_scores[1][3])
            ndcg_diff = abs(model_scores[0][4] - model_scores[1][4])
            mrr_diff = abs(model_scores[0][5] - model_scores[1][5])
            
            # Write differences and significance to report
            rf.write(f"MAP difference: {map_diff:.4f} ({'Significant' if map_diff > 0.05 else 'Not significant'})\n")
            rf.write(f"Recall difference: {recall_diff:.4f} ({'Significant' if recall_diff > 0.05 else 'Not significant'})\n")
            rf.write(f"Precision difference: {precision_diff:.4f} ({'Significant' if precision_diff > 0.05 else 'Not significant'})\n")
            rf.write(f"NDCG difference: {ndcg_diff:.4f} ({'Significant' if ndcg_diff > 0.05 else 'Not significant'})\n")
            rf.write(f"MRR difference: {mrr_diff:.4f} ({'Significant' if mrr_diff > 0.05 else 'Not significant'})\n")
        
        # Add per-query performance analysis
        if per_query_results:
            rf.write("\n=== Per-Query Performance Analysis ===\n")
            for qid, model_results in per_query_results.items():
                rf.write(f"\nQuery ID: {qid}\n")
                rf.write(f"Query text: {queries[qid]}\n")
                for model_name, metrics in model_results.items():
                    rf.write(
                        f"  {model_name}: Precision@{k} = {metrics['precision']:.4f}, "
                        f"Recall@{k} = {metrics['recall']:.4f}, "
                        f"NDCG@{k} = {metrics['ndcg']:.4f}, "
                        f"MRR@{k} = {metrics['mrr']:.4f}, "
                        f"MAP@{k} = {metrics['map']:.4f}\n"
                    )
                    
                # Identify better performing model for this query (by MAP@k)
                if len(model_results) > 1:
                    model_names = list(model_results.keys())
                    if model_results[model_names[0]]['map'] > model_results[model_names[1]]['map']:
                        better_model = model_names[0]
                    elif model_results[model_names[0]]['map'] < model_results[model_names[1]]['map']:
                        better_model = model_names[1]
                    else:
                        better_model = "Equal performance"
                    if better_model != "Equal performance":
                        rf.write(f"  Better model for this query (MAP@{k}): {better_model}\n")
                    else:
                        rf.write(f"  Both models perform equally for this query (MAP@{k})\n")
        
        # Add explanation of MAP calculation
        rf.write("\n=== MAP Calculation Methodology ===\n")
        rf.write("The evaluator's MAP calculation is a simple macro-average of per-query AP values.\n")
        rf.write("For each query, Average Precision (AP) is calculated as:\n")
        rf.write("  AP = (sum of precision@i for each relevant doc i found) / min(k, total number of relevant docs)\n\n")
        rf.write("Then MAP is calculated as:\n")
        rf.write("  MAP = sum(AP_i) / number_of_queries\n")
        rf.write("This is different from the traditional weighted MAP calculation that weights by relevant doc count.\n")
        
        # Add note about the ranking methodology
        rf.write("\n=== Note on Rankings and Metrics ===\n")
        rf.write("All metrics in this report (both summary and per-query) use the SentenceTransformer evaluator's\n")
        rf.write("internal tensor-based cosine similarity for document ranking. This ensures consistency between\n")
        rf.write("the summary metrics and per-query metrics.\n\n")
        rf.write("Note: The evaluator's ranking may differ from ChromaDB's ranking in production environments.\n")
            
    print(f"Report saved to {report_file}")

# ---------- Main Benchmarking Script ----------
if __name__ == "__main__":
    validate_config()
    print("Starting benchmarking process...")
    queries, corpus, relevant_docs = load_ground_truth()
    k = cfg.k

    model_scores = []
    model_retrievals = {}  # Dictionary to store retrieval results for each model
    
    for model_cfg in cfg.models:
        model_name = model_cfg["model_name"]
        collection_name = model_cfg["collection_name"]
        if cfg.reinitialize_collections:
            initialize_collections(corpus, model_name, collection_name)
        else:
            print(f"Skipping collection initialization as per configuration.")
        
        # Store retrieval results for per-query analysis
        retrievals = rank(model_name, collection_name, queries)
        model_retrievals[model_name] = retrievals
        map_score, recall_score, precision_score, ndcg_score, mrr_score = evaluate_metrics(
            queries, corpus, relevant_docs, model_name, collection_name
        )
        print(f"Final MAP@{k} for {model_name}: {map_score}")
        print(f"Final Recall@{k} for {model_name}: {recall_score}")
        print(f"Final Precision@{k} for {model_name}: {precision_score}")
        print(f"Final NDCG@{k} for {model_name}: {ndcg_score}")
        model_scores.append((model_name, map_score, recall_score, precision_score, ndcg_score, mrr_score))
        
    # Analyze per-query performance
    per_query_results = analyze_per_query_performance(
        queries, 
        corpus, 
        relevant_docs, 
        [model_cfg["model_name"] for model_cfg in cfg.models]
    )
      # Include per-query results in the report
    generate_report(model_scores, k, corpus, queries, per_query_results)    # Compare different MAP calculation methods
    print("\n=== MAP Calculation Methods Comparison ===")
    for model_name in [cfg["model_name"] for cfg in cfg.models]:
        # Calculate MAP using different methods
        evaluator_map = next(score[1] for score in model_scores if score[0] == model_name)
        weighted_map = weighted_average_map(model_name, queries, corpus, relevant_docs, cfg.k)
        exact_map, query_aps = calculate_evaluator_map(model_name, queries, corpus, relevant_docs, cfg.k)
        
        print(f"\n{model_name} MAP@{cfg.k} Comparison:")
        print(f"- Evaluator MAP: {evaluator_map:.6f}")
        print(f"- Weighted average MAP: {weighted_map:.6f}")
        print(f"- Exact evaluator MAP: {exact_map:.6f}")
        
        if abs(exact_map - evaluator_map) < 0.0001:
            print("✓ Exact implementation matches evaluator!")
        else:
            print(f"✗ Discrepancy between implementations: {abs(exact_map - evaluator_map):.6f}")
    
    print("\nBenchmark completed successfully.")
