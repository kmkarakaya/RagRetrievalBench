from sentence_transformers import SentenceTransformer, evaluation
import chromadb
from chromadb import Client
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
import json
import os
import datetime
import benchmark_config as cfg
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import argparse

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

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, output_dir="reports"):
    """Generate a comprehensive benchmark report suitable for a conference paper."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.md")
    
    # Sort models by MAP score for easier comparison
    sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp)
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write("# Embedding Model Benchmark for RAG Retrieval\n\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write executive summary
        f.write("## Executive Summary\n\n")
        f.write("This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used {len(corpus)} documents and {len(queries)} queries with {sum(len(v) for v in relevant_docs.values())} relevant document mappings.\n\n")
        
        # Best model highlight
        best_model = sorted_results[0]
        f.write(f"**Best performing model:** {best_model[0]}\n")
        if cfg.compute_map:
            f.write(f"* MAP@{cfg.k}: {best_model[1]:.4f}\n")
        if cfg.compute_recall:
            f.write(f"* Recall@{cfg.k}: {best_model[2]:.4f}\n")
        if cfg.compute_precision:
            f.write(f"* Precision@{cfg.k}: {best_model[3]:.4f}\n")
        if cfg.compute_ndcg:
            f.write(f"* NDCG@{cfg.k}: {best_model[4]:.4f}\n")
        if cfg.compute_mrr:
            f.write(f"* MRR@{cfg.k}: {best_model[5]:.4f}\n\n")
        
        # Benchmark configuration
        f.write("## Benchmark Configuration\n\n")
        f.write(f"* **k value:** {cfg.k}\n")
        f.write(f"* **Corpus size:** {len(corpus)} documents\n")
        f.write(f"* **Number of queries:** {len(queries)} queries\n")
        f.write(f"* **Number of relevance judgments:** {sum(len(v) for v in relevant_docs.values())}\n")
        f.write(f"* **Average relevant docs per query:** {sum(len(v) for v in relevant_docs.values()) / len(queries):.2f}\n\n")
        
        # Dataset details
        f.write("## Dataset\n\n")
        f.write("### Query Examples\n\n")
        
        # Display a few example queries (up to 5)
        query_sample = list(queries.items())[:5]
        query_table = []
        for qid, text in query_sample:
            rel_count = len(relevant_docs.get(qid, set()))
            query_table.append([qid, text[:100] + "..." if len(text) > 100 else text, rel_count])
        
        f.write(tabulate(query_table, headers=["Query ID", "Text", "# Relevant Docs"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Comparative results table
        f.write("## Comparative Results\n\n")
        
        # Prepare headers based on which metrics are computed
        headers = ["Model"]
        if cfg.compute_map:
            headers.append(f"MAP@{cfg.k}")
        if cfg.compute_recall:
            headers.append(f"Recall@{cfg.k}")
        if cfg.compute_precision:
            headers.append(f"Precision@{cfg.k}")
        if cfg.compute_ndcg:
            headers.append(f"NDCG@{cfg.k}")
        if cfg.compute_mrr:
            headers.append(f"MRR@{cfg.k}")
        
        # Prepare table data
        table_data = []
        for result in sorted_results:
            row = [result[0]]  # Model name
            idx = 1
            if cfg.compute_map:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_recall:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_precision:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_ndcg:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_mrr:
                row.append(f"{result[idx]:.4f}")
            
            table_data.append(row)
        
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("## Visualizations\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("### Model Performance Overview\n\n")
                f.write(f"![Model Comparison Across All Metrics]({os.path.basename(viz_files['overview'])})\n\n")
            
            # Add individual metric charts
            f.write("### Individual Metric Comparisons\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name != 'overview':
                    f.write(f"#### {metric_name.upper()} Comparison\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison Across Models]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis (if there are at least 2 models)
        if len(model_results) >= 2:
            f.write("## Statistical Significance Analysis\n\n")
            f.write("The table below shows the absolute difference between each model pair. ")
            f.write("Differences greater than 0.05 may be considered significant for practical applications.\n\n")
            
            # Create significance tables for each metric
            idx_map = {
                "map": 1 if cfg.compute_map else None,
                "recall": 2 if cfg.compute_recall else None,
                "precision": 3 if cfg.compute_precision else None,
                "ndcg": 4 if cfg.compute_ndcg else None,
                "mrr": 5 if cfg.compute_mrr else None
            }
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]  # Use shorter names
            
            for metric_name, metric_idx in idx_map.items():
                if metric_idx is None:
                    continue
                
                f.write(f"### {metric_name.upper()}@{cfg.k} Difference\n\n")
                
                # Create difference matrix
                diff_matrix = []
                for i, model1 in enumerate(sorted_results):
                    row = [model_names[i]]
                    for j, model2 in enumerate(sorted_results):
                        if i == j:
                            row.append("—")
                        else:
                            diff = abs(model1[metric_idx] - model2[metric_idx])
                            is_significant = diff > 0.05
                            row.append(f"{diff:.4f}{'*' if is_significant else ''}")
                    diff_matrix.append(row)
                
                f.write(tabulate(diff_matrix, headers=["Model"] + model_names, tablefmt="pipe"))
                f.write("\n\n")
                f.write("*Note: Values marked with * indicate potentially significant differences (>0.05).*\n\n")
        
        # Model details
        f.write("## Embedding Model Details\n\n")
        
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.models]:
            f.write(f"### {model_name}\n\n")
            f.write(f"* **Collection name:** {collection_name}\n")
            
            # Add additional model information if available
            try:
                model = SentenceTransformer(model_name)
                f.write(f"* **Model dimension:** {model.get_sentence_embedding_dimension()}\n")
                f.write(f"* **Model type:** {type(model).__name__}\n\n")
            except:
                f.write("* **Model information:** Not available\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        # Generate conclusion text based on results
        best_model_name = sorted_results[0][0]
        
        f.write(f"Based on the benchmark results, **{best_model_name}** demonstrated the strongest retrieval performance ")
        f.write(f"with the highest MAP@{cfg.k} score of {sorted_results[0][1]:.4f}. ")
        
        if len(sorted_results) > 1:
            second_best = sorted_results[1]
            map_diff = sorted_results[0][1] - second_best[1]
            
            if map_diff > 0.05:
                f.write(f"This model significantly outperformed the second-best model ({second_best[0]}) ")
                f.write(f"by a margin of {map_diff:.4f} in MAP@{cfg.k}. ")
            else:
                f.write(f"The performance was comparable to the second-best model ({second_best[0]}), ")
                f.write(f"with only a small difference of {map_diff:.4f} in MAP@{cfg.k}. ")
        
        f.write("\n\nThese results suggest that ")
        
        if len(sorted_results) > 1 and (sorted_results[0][1] - sorted_results[-1][1]) > 0.1:
            f.write("the choice of embedding model has a substantial impact on retrieval quality. ")
            f.write("Organizations implementing RAG systems should carefully consider their embedding model selection.")
        else:
            f.write("all tested models perform reasonably well for this particular dataset and use case. ")
            f.write("Other factors like inference speed, model size, and domain specificity might be more decisive factors for model selection.")
        
        f.write("\n\n---\n\n")
        f.write("*This report was automatically generated by the RAG Retrieval Benchmark tool.*\n")
    
    return report_file  # Return the path to the report file

def generate_visualizations(model_results, output_dir, timestamp):
    """Generate visualizations for the benchmark report."""
    # Dictionary to store paths to generated visualization files
    viz_files = {}
    
    # Set style
    plt.style.use('ggplot')  # Use a built-in matplotlib style
    
    # Prepare data
    model_names = [result[0].split('/')[-1] for result in model_results]  # Use shorter names
    metrics = {
        "MAP": [result[1] for result in model_results] if cfg.compute_map else None,
        "Recall": [result[2] for result in model_results] if cfg.compute_recall else None,
        "Precision": [result[3] for result in model_results] if cfg.compute_precision else None,
        "NDCG": [result[4] for result in model_results] if cfg.compute_ndcg else None,
        "MRR": [result[5] for result in model_results] if cfg.compute_mrr else None
    }
    
    # 1. Bar chart comparing all metrics across models
    plt.figure(figsize=(12, 8))
    
    # Set up positions for grouped bars
    x = np.arange(len(model_names))
    width = 0.15
    offset = 0
    
    # Create colormap without seaborn
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (metric_name, metric_values) in enumerate(metrics.items()):
        if metric_values is None:
            continue
        
        plt.bar(x + offset, metric_values, width, label=f"{metric_name}@{cfg.k}", 
                color=colors[i % len(colors)])
        offset += width
    
    plt.xlabel('Models', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title(f'Comparison of Embedding Models at k={cfg.k}', fontsize=14, weight='bold')
    plt.xticks(x + width*2, model_names, rotation=45, ha='right')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.ylim(0, 1)
    plt.tight_layout()
    
    # Save figure
    viz_file = os.path.join(output_dir, f"model_comparison_{timestamp}.png")
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    viz_files['overview'] = viz_file
    plt.close()
    
    # 2. Individual metric charts if there are multiple models
    if len(model_results) > 1:
        for j, (metric_name, metric_values) in enumerate(metrics.items()):
            if metric_values is None:
                continue
                
            plt.figure(figsize=(10, 6))
            color = colors[j % len(colors)]
            
            # Sort models by this metric
            sorted_indices = np.argsort(metric_values)[::-1]
            sorted_models = [model_names[i] for i in sorted_indices]
            sorted_values = [metric_values[i] for i in sorted_indices]
            
            bars = plt.bar(sorted_models, sorted_values, color=color)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.4f}',
                        ha='center', va='bottom', rotation=0)
            
            plt.xlabel('Models', fontsize=12)
            plt.ylabel(f'{metric_name} Score', fontsize=12)
            plt.title(f'{metric_name}@{cfg.k} Comparison', fontsize=14, weight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.ylim(0, max(metric_values) * 1.15)  # Add 15% headroom for labels
            plt.tight_layout()
            
            # Save figure
            viz_file = os.path.join(output_dir, f"{metric_name.lower()}_comparison_{timestamp}.png")
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            viz_files[metric_name.lower()] = viz_file
            plt.close()
    
    return viz_files



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

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, output_dir="reports"):
    """Generate a comprehensive benchmark report suitable for a conference paper."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.md")
    
    # Sort models by MAP score for easier comparison
    sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp)
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write("# Embedding Model Benchmark for RAG Retrieval\n\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write executive summary
        f.write("## Executive Summary\n\n")
        f.write("This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used {len(corpus)} documents and {len(queries)} queries with {sum(len(v) for v in relevant_docs.values())} relevant document mappings.\n\n")
        
        # Best model highlight
        best_model = sorted_results[0]
        f.write(f"**Best performing model:** {best_model[0]}\n")
        if cfg.compute_map:
            f.write(f"* MAP@{cfg.k}: {best_model[1]:.4f}\n")
        if cfg.compute_recall:
            f.write(f"* Recall@{cfg.k}: {best_model[2]:.4f}\n")
        if cfg.compute_precision:
            f.write(f"* Precision@{cfg.k}: {best_model[3]:.4f}\n")
        if cfg.compute_ndcg:
            f.write(f"* NDCG@{cfg.k}: {best_model[4]:.4f}\n")
        if cfg.compute_mrr:
            f.write(f"* MRR@{cfg.k}: {best_model[5]:.4f}\n\n")
        
        # Benchmark configuration
        f.write("## Benchmark Configuration\n\n")
        f.write(f"* **k value:** {cfg.k}\n")
        f.write(f"* **Corpus size:** {len(corpus)} documents\n")
        f.write(f"* **Number of queries:** {len(queries)} queries\n")
        f.write(f"* **Number of relevance judgments:** {sum(len(v) for v in relevant_docs.values())}\n")
        f.write(f"* **Average relevant docs per query:** {sum(len(v) for v in relevant_docs.values()) / len(queries):.2f}\n\n")
        
        # Dataset details
        f.write("## Dataset\n\n")
        f.write("### Query Examples\n\n")
        
        # Display a few example queries (up to 5)
        query_sample = list(queries.items())[:5]
        query_table = []
        for qid, text in query_sample:
            rel_count = len(relevant_docs.get(qid, set()))
            query_table.append([qid, text[:100] + "..." if len(text) > 100 else text, rel_count])
        
        f.write(tabulate(query_table, headers=["Query ID", "Text", "# Relevant Docs"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Comparative results table
        f.write("## Comparative Results\n\n")
        
        # Prepare headers based on which metrics are computed
        headers = ["Model"]
        if cfg.compute_map:
            headers.append(f"MAP@{cfg.k}")
        if cfg.compute_recall:
            headers.append(f"Recall@{cfg.k}")
        if cfg.compute_precision:
            headers.append(f"Precision@{cfg.k}")
        if cfg.compute_ndcg:
            headers.append(f"NDCG@{cfg.k}")
        if cfg.compute_mrr:
            headers.append(f"MRR@{cfg.k}")
        
        # Prepare table data
        table_data = []
        for result in sorted_results:
            row = [result[0]]  # Model name
            idx = 1
            if cfg.compute_map:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_recall:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_precision:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_ndcg:
                row.append(f"{result[idx]:.4f}")
                idx += 1
            if cfg.compute_mrr:
                row.append(f"{result[idx]:.4f}")
            
            table_data.append(row)
        
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("## Visualizations\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("### Model Performance Overview\n\n")
                f.write(f"![Model Comparison Across All Metrics]({os.path.basename(viz_files['overview'])})\n\n")
            
            # Add individual metric charts
            f.write("### Individual Metric Comparisons\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name != 'overview':
                    f.write(f"#### {metric_name.upper()} Comparison\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison Across Models]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis (if there are at least 2 models)
        if len(model_results) >= 2:
            f.write("## Statistical Significance Analysis\n\n")
            f.write("The table below shows the absolute difference between each model pair. ")
            f.write("Differences greater than 0.05 may be considered significant for practical applications.\n\n")
            
            # Create significance tables for each metric
            idx_map = {
                "map": 1 if cfg.compute_map else None,
                "recall": 2 if cfg.compute_recall else None,
                "precision": 3 if cfg.compute_precision else None,
                "ndcg": 4 if cfg.compute_ndcg else None,
                "mrr": 5 if cfg.compute_mrr else None
            }
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]  # Use shorter names
            
            for metric_name, metric_idx in idx_map.items():
                if metric_idx is None:
                    continue
                
                f.write(f"### {metric_name.upper()}@{cfg.k} Difference\n\n")
                
                # Create difference matrix
                diff_matrix = []
                for i, model1 in enumerate(sorted_results):
                    row = [model_names[i]]
                    for j, model2 in enumerate(sorted_results):
                        if i == j:
                            row.append("—")
                        else:
                            diff = abs(model1[metric_idx] - model2[metric_idx])
                            is_significant = diff > 0.05
                            row.append(f"{diff:.4f}{'*' if is_significant else ''}")
                    diff_matrix.append(row)
                
                f.write(tabulate(diff_matrix, headers=["Model"] + model_names, tablefmt="pipe"))
                f.write("\n\n")
                f.write("*Note: Values marked with * indicate potentially significant differences (>0.05).*\n\n")
        
        # Model details
        f.write("## Embedding Model Details\n\n")
        
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.models]:
            f.write(f"### {model_name}\n\n")
            f.write(f"* **Collection name:** {collection_name}\n")
            
            # Add additional model information if available
            try:
                model = SentenceTransformer(model_name)
                f.write(f"* **Model dimension:** {model.get_sentence_embedding_dimension()}\n")
                f.write(f"* **Model type:** {type(model).__name__}\n\n")
            except:
                f.write("* **Model information:** Not available\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        # Generate conclusion text based on results
        best_model_name = sorted_results[0][0]
        
        f.write(f"Based on the benchmark results, **{best_model_name}** demonstrated the strongest retrieval performance ")
        f.write(f"with the highest MAP@{cfg.k} score of {sorted_results[0][1]:.4f}. ")
        
        if len(sorted_results) > 1:
            second_best = sorted_results[1]
            map_diff = sorted_results[0][1] - second_best[1]
            
            if map_diff > 0.05:
                f.write(f"This model significantly outperformed the second-best model ({second_best[0]}) ")
                f.write(f"by a margin of {map_diff:.4f} in MAP@{cfg.k}. ")
            else:
                f.write(f"The performance was comparable to the second-best model ({second_best[0]}), ")
                f.write(f"with only a small difference of {map_diff:.4f} in MAP@{cfg.k}. ")
        
        f.write("\n\nThese results suggest that ")
        
        if len(sorted_results) > 1 and (sorted_results[0][1] - sorted_results[-1][1]) > 0.1:
            f.write("the choice of embedding model has a substantial impact on retrieval quality. ")
            f.write("Organizations implementing RAG systems should carefully consider their embedding model selection.")
        else:
            f.write("all tested models perform reasonably well for this particular dataset and use case. ")
            f.write("Other factors like inference speed, model size, and domain specificity might be more decisive factors for model selection.")
        
        f.write("\n\n---\n\n")
        f.write("*This report was automatically generated by the RAG Retrieval Benchmark tool.*\n")
    
    return report_file  # Return the path to the report file

def generate_visualizations(model_results, output_dir, timestamp):
    """Generate visualizations for the benchmark report."""
    # Dictionary to store paths to generated visualization files
    viz_files = {}
    
    # Set style
    plt.style.use('ggplot')  # Use a built-in matplotlib style
    
    # Prepare data
    model_names = [result[0].split('/')[-1] for result in model_results]  # Use shorter names
    metrics = {
        "MAP": [result[1] for result in model_results] if cfg.compute_map else None,
        "Recall": [result[2] for result in model_results] if cfg.compute_recall else None,
        "Precision": [result[3] for result in model_results] if cfg.compute_precision else None,
        "NDCG": [result[4] for result in model_results] if cfg.compute_ndcg else None,
        "MRR": [result[5] for result in model_results] if cfg.compute_mrr else None
    }
    
    # 1. Bar chart comparing all metrics across models
    plt.figure(figsize=(12, 8))
    
    # Set up positions for grouped bars
    x = np.arange(len(model_names))
    width = 0.15
    offset = 0
    
    # Create colormap without seaborn
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (metric_name, metric_values) in enumerate(metrics.items()):
        if metric_values is None:
            continue
        
        plt.bar(x + offset, metric_values, width, label=f"{metric_name}@{cfg.k}", 
                color=colors[i % len(colors)])
        offset += width
    
    plt.xlabel('Models', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title(f'Comparison of Embedding Models at k={cfg.k}', fontsize=14, weight='bold')
    plt.xticks(x + width*2, model_names, rotation=45, ha='right')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.ylim(0, 1)
    plt.tight_layout()
    
    # Save figure
    viz_file = os.path.join(output_dir, f"model_comparison_{timestamp}.png")
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    viz_files['overview'] = viz_file
    plt.close()
    
    # 2. Individual metric charts if there are multiple models
    if len(model_results) > 1:
        for j, (metric_name, metric_values) in enumerate(metrics.items()):
            if metric_values is None:
                continue
                
            plt.figure(figsize=(10, 6))
            color = colors[j % len(colors)]
            
            # Sort models by this metric
            sorted_indices = np.argsort(metric_values)[::-1]
            sorted_models = [model_names[i] for i in sorted_indices]
            sorted_values = [metric_values[i] for i in sorted_indices]
            
            bars = plt.bar(sorted_models, sorted_values, color=color)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.4f}',
                        ha='center', va='bottom', rotation=0)
            
            plt.xlabel('Models', fontsize=12)
            plt.ylabel(f'{metric_name} Score', fontsize=12)
            plt.title(f'{metric_name}@{cfg.k} Comparison', fontsize=14, weight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.ylim(0, max(metric_values) * 1.15)  # Add 15% headroom for labels
            plt.tight_layout()
            
            # Save figure
            viz_file = os.path.join(output_dir, f"{metric_name.lower()}_comparison_{timestamp}.png")
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            viz_files[metric_name.lower()] = viz_file
            plt.close()
    
    return viz_files
# Update main function to generate the report
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-corpus", action="store_true", help="Prepare corpus.jsonl from PDFs")
    args = parser.parse_args()

    if args.prepare_corpus:
        prepare_corpus_from_pdfs()
        return

    """Main function to run the benchmark."""
    # Validate existence of required files
    for file_path in [cfg.corpus_file, cfg.queries_file, cfg.qrels_file]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file not found: {file_path}")
    
    print("Starting simple RAG benchmark...")
    print(f"Configuration: k={cfg.k}, show_progress={cfg.show_progress_bar}, reinit_collections={cfg.reinitialize_collections}")
    
    # Load data
    queries, corpus, relevant_docs = load_ground_truth()
    
    # Process each model
    model_results = []
    
    for model_cfg in cfg.models:
        model_name = model_cfg["model_name"]
        collection_name = model_cfg["collection_name"]
        
        # Initialize collection
        initialize_collection(corpus, model_name, collection_name)
        
        # Evaluate model
        metrics = evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name)
        model_results.append((model_name, *metrics))
    
    # Print summary
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
    
    # After evaluating all models
    if model_results:
        # Generate detailed report
        report_file = generate_benchmark_report(model_results, queries, corpus, relevant_docs)
        print(f"\nDetailed benchmark report saved to: {report_file}")
    
    print("\nBenchmark completed!")

if __name__ == "__main__":
    main()

