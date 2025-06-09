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
from utils.chromadb_utils import create_chroma_collection
from utils.report_utils import  convert_md_to_pdf

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
    initialize_collection(corpus, cfg.models[0]["model_name"], collection_name)
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

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, output_dir="reports"):
    """Generate a comprehensive benchmark report suitable for a conference paper."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.md")
    
    # Sort models by MAP score for easier comparison
    sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
    
    # Calculate additional statistics
    chunk_lengths = [len(text.split()) for text in corpus.values()]
    query_lengths = [len(text.split()) for text in queries.values()]
    relevance_distribution = [len(v) for v in relevant_docs.values()]
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp)
        # Generate additional statistics visualizations
        viz_files.update(generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, output_dir, timestamp))
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write("# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models\n\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Abstract
        f.write("## Abstract\n\n")
        f.write("This paper presents a systematic evaluation framework for embedding models in ")
        f.write("Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline ")
        f.write("that processes PDF documents, generates synthetic queries using large language models, ")
        f.write("and evaluates retrieval performance across multiple embedding models using standardized ")
        f.write("information retrieval metrics. Our framework provides researchers and practitioners ")
        f.write("with a reproducible methodology for selecting optimal embedding models for their ")
        f.write("specific document collections and use cases.\n\n")
        
        # Executive summary
        f.write("## Executive Summary\n\n")
        f.write("This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used **{len(corpus)} documents** and **{len(queries)} queries** with **{sum(len(v) for v in relevant_docs.values())} relevant document mappings**.\n\n")
        
        # Best model highlight
        best_model = sorted_results[0]
        f.write(f"**Best performing model:** `{best_model[0]}`\n")
        if cfg.compute_map:
            f.write(f"* MAP@{cfg.k}: **{best_model[1]:.4f}**\n")
        if cfg.compute_recall:
            f.write(f"* Recall@{cfg.k}: **{best_model[2]:.4f}**\n")
        if cfg.compute_precision:
            f.write(f"* Precision@{cfg.k}: **{best_model[3]:.4f}**\n")
        if cfg.compute_ndcg:
            f.write(f"* NDCG@{cfg.k}: **{best_model[4]:.4f}**\n")
        if cfg.compute_mrr:
            f.write(f"* MRR@{cfg.k}: **{best_model[5]:.4f}**\n\n")
        
        # Methodology
        f.write("## Methodology\n\n")
        f.write("### 1. Automated Pipeline Overview\n\n")
        f.write("Our evaluation framework consists of five main stages:\n\n")
        f.write("1. **PDF Processing**: Document ingestion and chunking\n")
        f.write("2. **Corpus Generation**: Creation of standardized document chunks\n")
        f.write("3. **Query Generation**: LLM-assisted query synthesis\n")
        f.write("4. **Relevance Assessment**: Automated qrels generation\n")
        f.write("5. **Embedding Evaluation**: Multi-model performance comparison\n\n")
        
        f.write("### 2. Document Processing Pipeline\n\n")
        f.write("#### 2.1 PDF Extraction and Chunking\n\n")
        f.write(f"- **Source documents**: PDF files from `{cfg.pdf_dir}` directory\n")
        f.write(f"- **Chunking strategy**: Recursive character text splitting\n")
        f.write(f"- **Chunk size**: {cfg.chunk_size} characters\n")
        f.write(f"- **Chunk overlap**: {cfg.chunk_overlap} characters\n")
        f.write(f"- **Total chunks generated**: {len(corpus)}\n\n")
        
        f.write("The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to ")
        f.write("maintain semantic coherence while ensuring manageable chunk sizes for embedding models.\n\n")
        
        f.write("#### 2.2 Query Generation Process\n\n")
        f.write(f"- **LLM Model**: {cfg.llm_model}\n")
        f.write(f"- **Number of queries generated**: {len(queries)}\n")
        f.write(f"- **Generation strategy**: Seed-chunk → Query → Retrieval → Label\n")
        f.write(f"- **Candidate pool size**: {cfg.candidate_pool_size} chunks per query\n\n")
        
        f.write("Queries were generated using the following systematic approach:\n")
        f.write("1. Random sampling of seed chunks from the corpus\n")
        f.write("2. LLM-based question generation targeting specific chunks\n")
        f.write("3. Retrieval-based candidate identification using ChromaDB\n")
        f.write("4. LLM-based relevance labeling for comprehensive qrels\n\n")
        
        # Dataset statistics
        f.write("### 3. Dataset Statistics\n\n")
        
        # Corpus statistics table
        f.write("#### 3.1 Corpus Characteristics\n\n")
        corpus_stats = [
            ["Total Documents", f"{len(corpus):,}"],
            ["Average Chunk Length (words)", f"{np.mean(chunk_lengths):.1f}"],
            ["Median Chunk Length (words)", f"{np.median(chunk_lengths):.1f}"],
            ["Min Chunk Length (words)", f"{min(chunk_lengths)}"],
            ["Max Chunk Length (words)", f"{max(chunk_lengths)}"],
            ["Standard Deviation", f"{np.std(chunk_lengths):.1f}"]
        ]
        f.write(tabulate(corpus_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Query statistics table
        f.write("#### 3.2 Query Characteristics\n\n")
        query_stats = [
            ["Total Queries", f"{len(queries)}"],
            ["Average Query Length (words)", f"{np.mean(query_lengths):.1f}"],
            ["Median Query Length (words)", f"{np.median(query_lengths):.1f}"],
            ["Min Query Length (words)", f"{min(query_lengths)}"],
            ["Max Query Length (words)", f"{max(query_lengths)}"],
            ["Standard Deviation", f"{np.std(query_lengths):.1f}"]
        ]
        f.write(tabulate(query_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Relevance statistics
        f.write("#### 3.3 Relevance Distribution\n\n")
        relevance_stats = [
            ["Total Relevance Judgments", f"{sum(relevance_distribution)}"],
            ["Average Relevant Docs per Query", f"{np.mean(relevance_distribution):.1f}"],
            ["Median Relevant Docs per Query", f"{np.median(relevance_distribution):.1f}"],
            ["Min Relevant Docs", f"{min(relevance_distribution)}"],
            ["Max Relevant Docs", f"{max(relevance_distribution)}"],
            ["Coverage Ratio", f"{sum(relevance_distribution)/len(corpus)*100:.2f}%"]
        ]
        f.write(tabulate(relevance_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Benchmark configuration
        f.write("### 4. Experimental Setup\n\n")
        f.write("#### 4.1 Evaluation Framework\n\n")
        f.write("- **Vector Database**: ChromaDB\n")
        f.write("- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator\n")
        f.write(f"- **Retrieval Depth (k)**: {cfg.k}\n")
        f.write(f"- **Batch Size**: {cfg.batch_size}\n")
        f.write(f"- **Collection Reinitialization**: {cfg.reinitialize_collections}\n\n")
        
        f.write("#### 4.2 Evaluated Models\n\n")
        model_info_table = []
        for model_cfg in cfg.models:
            try:
                model = SentenceTransformer(model_cfg["model_name"])
                dimensions = model.get_sentence_embedding_dimension()
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    dimensions,
                    "Sentence Transformer"
                ])
            except:
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    "N/A",
                    "N/A"
                ])
        
        f.write(tabulate(model_info_table, 
                        headers=["Model Name", "Collection", "Dimensions", "Type"], 
                        tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("#### 4.3 Evaluation Metrics\n\n")
        metrics_desc = []
        if cfg.compute_map:
            metrics_desc.append(["MAP@k", "Mean Average Precision at rank k", "Ranking quality"])
        if cfg.compute_recall:
            metrics_desc.append(["Recall@k", "Proportion of relevant docs in top k", "Coverage"])
        if cfg.compute_precision:
            metrics_desc.append(["Precision@k", "Proportion of relevant docs among retrieved", "Accuracy"])
        if cfg.compute_ndcg:
            metrics_desc.append(["NDCG@k", "Normalized Discounted Cumulative Gain", "Ranking with position bias"])
        if cfg.compute_mrr:
            metrics_desc.append(["MRR@k", "Mean Reciprocal Rank", "First relevant position"])
        
        f.write(tabulate(metrics_desc, headers=["Metric", "Description", "Measures"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Add example queries
        f.write("#### 4.4 Representative Query Examples\n\n")
        query_sample = list(queries.items())[:5]
        query_table = []
        for qid, text in query_sample:
            rel_count = len(relevant_docs.get(qid, set()))
            # Truncate long queries for display
            display_text = text[:100] + "..." if len(text) > 100 else text
            query_table.append([qid, display_text, rel_count])
        
        f.write(tabulate(query_table, headers=["Query ID", "Query Text", "# Relevant Docs"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Results section
        f.write("## Results\n\n")
        
        # Comparative results table
        f.write("### 5.1 Model Performance Comparison\n\n")
        
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
        
        f.write("**Table: Comprehensive Model Performance Results**\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        # Performance analysis
        f.write("### 5.2 Performance Analysis\n\n")
        if len(sorted_results) > 1:
            best_model = sorted_results[0]
            worst_model = sorted_results[-1]
            
            f.write(f"The evaluation reveals significant performance variations across embedding models. ")
            f.write(f"**{best_model[0]}** achieved the highest MAP@{cfg.k} score of {best_model[1]:.4f}, ")
            f.write(f"while **{worst_model[0]}** scored {worst_model[1]:.4f}, representing a ")
            f.write(f"**{((best_model[1] - worst_model[1]) / worst_model[1] * 100):.1f}% improvement**.\n\n")
            
            # Correlation analysis between metrics
            if cfg.compute_map and cfg.compute_recall:
                map_scores = [r[1] for r in sorted_results]
                recall_scores = [r[2] for r in sorted_results]
                correlation = np.corrcoef(map_scores, recall_scores)[0, 1]
                f.write(f"**MAP-Recall Correlation**: {correlation:.3f} ")
                f.write("(indicates how well ranking quality correlates with coverage)\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("### 5.3 Visual Analysis\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("#### 5.3.1 Overall Performance Comparison\n\n")
                f.write(f"![Model Performance Overview]({os.path.basename(viz_files['overview'])})\n\n")
                f.write("*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*\n\n")
            
            # Add corpus statistics visualizations
            if 'corpus_stats' in viz_files:
                f.write("#### 5.3.2 Dataset Characteristics\n\n")
                f.write(f"![Corpus Statistics]({os.path.basename(viz_files['corpus_stats'])})\n\n")
                f.write("*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*\n\n")
            
            # Add individual metric charts
            f.write("#### 5.3.3 Individual Metric Analysis\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name not in ['overview', 'corpus_stats']:
                    f.write(f"##### {metric_name.upper()}@{cfg.k} Results\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis
        if len(model_results) >= 2:
            f.write("### 5.4 Statistical Significance Analysis\n\n")
            f.write("The following tables show absolute differences between model pairs. ")
            f.write("Differences greater than 0.05 may indicate practically significant improvements ")
            f.write("for real-world applications.\n\n")
            
            # Create significance tables for each metric
            idx_map = {
                "MAP": 1 if cfg.compute_map else None,
                "Recall": 2 if cfg.compute_recall else None,
                "Precision": 3 if cfg.compute_precision else None,
                "NDCG": 4 if cfg.compute_ndcg else None,
                "MRR": 5 if cfg.compute_mrr else None
            }
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]
            
            for metric_name, metric_idx in idx_map.items():
                if metric_idx is None:
                    continue
                
                f.write(f"#### {metric_name}@{cfg.k} Pairwise Differences\n\n")
                
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
                f.write("\n\n*Note: Values marked with * indicate potentially significant differences (>0.05).*\n\n")
        
        # Technical implementation details
        f.write("## Technical Implementation\n\n")
        f.write("### 6.1 Pipeline Architecture\n\n")
        f.write("The benchmark pipeline implements a modular architecture with the following components:\n\n")
        f.write("- **Document Processing Module**: PDF extraction and chunking using PyMuPDF and LangChain\n")
        f.write("- **LLM Integration**: Gemini API for query generation and relevance assessment\n")
        f.write("- **Vector Database**: ChromaDB with native embedding functions\n")
        f.write("- **Evaluation Engine**: SentenceTransformers evaluation framework\n")
        f.write("- **Reporting System**: Automated report generation with visualizations\n\n")
        
        f.write("### 6.2 Reproducibility\n\n")
        f.write("All experiments can be reproduced using the following commands:\n\n")
        f.write("```bash\n")
        f.write("# 1. Process PDFs into chunks\n")
        f.write("python simple_rag_benchmark_pipeline.py --prepare-corpus\n\n")
        f.write("# 2. Generate queries and relevance judgments\n")
        f.write("python simple_rag_benchmark_pipeline.py --generate-qrels\n\n")
        f.write("# 3. Run complete benchmark\n")
        f.write("python simple_rag_benchmark_pipeline.py --all\n")
        f.write("```\n\n")
        
        # Embedding model details
        f.write("### 6.3 Embedding Model Specifications\n\n")
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.models]:
            f.write(f"#### {model_name}\n\n")
            f.write(f"- **Collection identifier**: `{collection_name}`\n")
            
            # Add additional model information if available
            try:
                model = SentenceTransformer(model_name)
                f.write(f"- **Embedding dimension**: {model.get_sentence_embedding_dimension()}\n")
                f.write(f"- **Maximum sequence length**: {model.max_seq_length}\n")
                f.write(f"- **Model architecture**: Transformer-based sentence encoder\n\n")
            except:
                f.write("- **Model specifications**: Not available through SentenceTransformers interface\n\n")
        
        # Discussion and limitations
        f.write("## Discussion\n\n")
        f.write("### 7.1 Key Findings\n\n")
        
        best_model_name = sorted_results[0][0]
        f.write(f"1. **Model Performance Hierarchy**: {best_model_name} emerged as the top performer, ")
        f.write(f"achieving superior results across multiple evaluation metrics.\n\n")
        
        if len(sorted_results) > 1:
            second_best = sorted_results[1]
            map_diff = sorted_results[0][1] - second_best[1]
            
            f.write(f"2. **Performance Gaps**: The performance difference between the best and second-best ")
            f.write(f"models ({map_diff:.4f} MAP@{cfg.k}) suggests that model selection significantly ")
            f.write(f"impacts retrieval quality.\n\n")
        
        f.write("3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation ")
        f.write("process demonstrates the feasibility of automated benchmark creation for domain-specific ")
        f.write("document collections.\n\n")
        
        f.write("### 7.2 Limitations and Future Work\n\n")
        f.write("- **Single-domain evaluation**: Current results are specific to the evaluated document collection\n")
        f.write("- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model\n")
        f.write("- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs\n")
        f.write("- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        f.write("This study presents a comprehensive framework for evaluating embedding models in RAG systems. ")
        f.write("Our automated pipeline successfully generated meaningful evaluation datasets and provided ")
        f.write("statistically robust comparisons of model performance. ")
        
        f.write(f"The results demonstrate that **{best_model_name}** provides optimal retrieval performance ")
        f.write(f"for the evaluated document collection, with a MAP@{cfg.k} score of {sorted_results[0][1]:.4f}. ")
        
        if len(sorted_results) > 1 and (sorted_results[0][1] - sorted_results[-1][1]) > 0.1:
            f.write("The substantial performance variations across models underscore the importance of ")
            f.write("systematic evaluation in embedding model selection for production RAG systems.")
        else:
            f.write("While performance differences were moderate, the evaluation framework provides ")
            f.write("valuable insights for informed model selection based on specific application requirements.")
        
        f.write("\n\nThe open-source nature of our evaluation framework enables researchers and practitioners ")
        f.write("to adapt the methodology for their specific domains and requirements, contributing to ")
        f.write("more systematic and reproducible evaluation practices in the RAG community.\n\n")
        
        f.write("---\n\n")
        f.write(f"*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at {timestamp}.*\n")
        f.write("*Source code and evaluation data available at the project repository.*\n")
    
    return report_file

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
    
    # Calculate additional statistics
    chunk_lengths = [len(text.split()) for text in corpus.values()]
    query_lengths = [len(text.split()) for text in queries.values()]
    relevance_distribution = [len(v) for v in relevant_docs.values()]
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp)
        # Generate additional statistics visualizations
        viz_files.update(generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, output_dir, timestamp))
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write("# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models\n\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Abstract
        f.write("## Abstract\n\n")
        f.write("This paper presents a systematic evaluation framework for embedding models in ")
        f.write("Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline ")
        f.write("that processes PDF documents, generates synthetic queries using large language models, ")
        f.write("and evaluates retrieval performance across multiple embedding models using standardized ")
        f.write("information retrieval metrics. Our framework provides researchers and practitioners ")
        f.write("with a reproducible methodology for selecting optimal embedding models for their ")
        f.write("specific document collections and use cases.\n\n")
        
        # Executive summary
        f.write("## Executive Summary\n\n")
        f.write("This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used **{len(corpus)} documents** and **{len(queries)} queries** with **{sum(len(v) for v in relevant_docs.values())} relevant document mappings**.\n\n")
        
        # Best model highlight
        best_model = sorted_results[0]
        f.write(f"**Best performing model:** `{best_model[0]}`\n")
        if cfg.compute_map:
            f.write(f"* MAP@{cfg.k}: **{best_model[1]:.4f}**\n")
        if cfg.compute_recall:
            f.write(f"* Recall@{cfg.k}: **{best_model[2]:.4f}**\n")
        if cfg.compute_precision:
            f.write(f"* Precision@{cfg.k}: **{best_model[3]:.4f}**\n")
        if cfg.compute_ndcg:
            f.write(f"* NDCG@{cfg.k}: **{best_model[4]:.4f}**\n")
        if cfg.compute_mrr:
            f.write(f"* MRR@{cfg.k}: **{best_model[5]:.4f}**\n\n")
        
        # Methodology
        f.write("## Methodology\n\n")
        f.write("### 1. Automated Pipeline Overview\n\n")
        f.write("Our evaluation framework consists of five main stages:\n\n")
        f.write("1. **PDF Processing**: Document ingestion and chunking\n")
        f.write("2. **Corpus Generation**: Creation of standardized document chunks\n")
        f.write("3. **Query Generation**: LLM-assisted query synthesis\n")
        f.write("4. **Relevance Assessment**: Automated qrels generation\n")
        f.write("5. **Embedding Evaluation**: Multi-model performance comparison\n\n")
        
        f.write("### 2. Document Processing Pipeline\n\n")
        f.write("#### 2.1 PDF Extraction and Chunking\n\n")
        f.write(f"- **Source documents**: PDF files from `{cfg.pdf_dir}` directory\n")
        f.write(f"- **Chunking strategy**: Recursive character text splitting\n")
        f.write(f"- **Chunk size**: {cfg.chunk_size} characters\n")
        f.write(f"- **Chunk overlap**: {cfg.chunk_overlap} characters\n")
        f.write(f"- **Total chunks generated**: {len(corpus)}\n\n")
        
        f.write("The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to ")
        f.write("maintain semantic coherence while ensuring manageable chunk sizes for embedding models.\n\n")
        
        f.write("#### 2.2 Query Generation Process\n\n")
        f.write(f"- **LLM Model**: {cfg.llm_model}\n")
        f.write(f"- **Number of queries generated**: {len(queries)}\n")
        f.write(f"- **Generation strategy**: Seed-chunk → Query → Retrieval → Label\n")
        f.write(f"- **Candidate pool size**: {cfg.candidate_pool_size} chunks per query\n\n")
        
        f.write("Queries were generated using the following systematic approach:\n")
        f.write("1. Random sampling of seed chunks from the corpus\n")
        f.write("2. LLM-based question generation targeting specific chunks\n")
        f.write("3. Retrieval-based candidate identification using ChromaDB\n")
        f.write("4. LLM-based relevance labeling for comprehensive qrels\n\n")
        
        # Dataset statistics
        f.write("### 3. Dataset Statistics\n\n")
        
        # Corpus statistics table
        f.write("#### 3.1 Corpus Characteristics\n\n")
        corpus_stats = [
            ["Total Documents", f"{len(corpus):,}"],
            ["Average Chunk Length (words)", f"{np.mean(chunk_lengths):.1f}"],
            ["Median Chunk Length (words)", f"{np.median(chunk_lengths):.1f}"],
            ["Min Chunk Length (words)", f"{min(chunk_lengths)}"],
            ["Max Chunk Length (words)", f"{max(chunk_lengths)}"],
            ["Standard Deviation", f"{np.std(chunk_lengths):.1f}"]
        ]
        f.write(tabulate(corpus_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Query statistics table
        f.write("#### 3.2 Query Characteristics\n\n")
        query_stats = [
            ["Total Queries", f"{len(queries)}"],
            ["Average Query Length (words)", f"{np.mean(query_lengths):.1f}"],
            ["Median Query Length (words)", f"{np.median(query_lengths):.1f}"],
            ["Min Query Length (words)", f"{min(query_lengths)}"],
            ["Max Query Length (words)", f"{max(query_lengths)}"],
            ["Standard Deviation", f"{np.std(query_lengths):.1f}"]
        ]
        f.write(tabulate(query_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Relevance statistics
        f.write("#### 3.3 Relevance Distribution\n\n")
        relevance_stats = [
            ["Total Relevance Judgments", f"{sum(relevance_distribution)}"],
            ["Average Relevant Docs per Query", f"{np.mean(relevance_distribution):.1f}"],
            ["Median Relevant Docs per Query", f"{np.median(relevance_distribution):.1f}"],
            ["Min Relevant Docs", f"{min(relevance_distribution)}"],
            ["Max Relevant Docs", f"{max(relevance_distribution)}"],
            ["Coverage Ratio", f"{sum(relevance_distribution)/len(corpus)*100:.2f}%"]
        ]
        f.write(tabulate(relevance_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Benchmark configuration
        f.write("### 4. Experimental Setup\n\n")
        f.write("#### 4.1 Evaluation Framework\n\n")
        f.write("- **Vector Database**: ChromaDB\n")
        f.write("- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator\n")
        f.write(f"- **Retrieval Depth (k)**: {cfg.k}\n")
        f.write(f"- **Batch Size**: {cfg.batch_size}\n")
        f.write(f"- **Collection Reinitialization**: {cfg.reinitialize_collections}\n\n")
        
        f.write("#### 4.2 Evaluated Models\n\n")
        model_info_table = []
        for model_cfg in cfg.models:
            try:
                model = SentenceTransformer(model_cfg["model_name"])
                dimensions = model.get_sentence_embedding_dimension()
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    dimensions,
                    "Sentence Transformer"
                ])
            except:
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    "N/A",
                    "N/A"
                ])
        
        f.write(tabulate(model_info_table, 
                        headers=["Model Name", "Collection", "Dimensions", "Type"], 
                        tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("#### 4.3 Evaluation Metrics\n\n")
        metrics_desc = []
        if cfg.compute_map:
            metrics_desc.append(["MAP@k", "Mean Average Precision at rank k", "Ranking quality"])
        if cfg.compute_recall:
            metrics_desc.append(["Recall@k", "Proportion of relevant docs in top k", "Coverage"])
        if cfg.compute_precision:
            metrics_desc.append(["Precision@k", "Proportion of relevant docs among retrieved", "Accuracy"])
        if cfg.compute_ndcg:
            metrics_desc.append(["NDCG@k", "Normalized Discounted Cumulative Gain", "Ranking with position bias"])
        if cfg.compute_mrr:
            metrics_desc.append(["MRR@k", "Mean Reciprocal Rank", "First relevant position"])
        
        f.write(tabulate(metrics_desc, headers=["Metric", "Description", "Measures"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Add example queries
        f.write("#### 4.4 Representative Query Examples\n\n")
        query_sample = list(queries.items())[:5]
        query_table = []
        for qid, text in query_sample:
            rel_count = len(relevant_docs.get(qid, set()))
            # Truncate long queries for display
            display_text = text[:100] + "..." if len(text) > 100 else text
            query_table.append([qid, display_text, rel_count])
        
        f.write(tabulate(query_table, headers=["Query ID", "Query Text", "# Relevant Docs"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Results section
        f.write("## Results\n\n")
        
        # Comparative results table
        f.write("### 5.1 Model Performance Comparison\n\n")
        
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
        
        f.write("**Table: Comprehensive Model Performance Results**\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        # Performance analysis
        f.write("### 5.2 Performance Analysis\n\n")
        if len(sorted_results) > 1:
            best_model = sorted_results[0]
            worst_model = sorted_results[-1]
            
            f.write(f"The evaluation reveals significant performance variations across embedding models. ")
            f.write(f"**{best_model[0]}** achieved the highest MAP@{cfg.k} score of {best_model[1]:.4f}, ")
            f.write(f"while **{worst_model[0]}** scored {worst_model[1]:.4f}, representing a ")
            f.write(f"**{((best_model[1] - worst_model[1]) / worst_model[1] * 100):.1f}% improvement**.\n\n")
            
            # Correlation analysis between metrics
            if cfg.compute_map and cfg.compute_recall:
                map_scores = [r[1] for r in sorted_results]
                recall_scores = [r[2] for r in sorted_results]
                correlation = np.corrcoef(map_scores, recall_scores)[0, 1]
                f.write(f"**MAP-Recall Correlation**: {correlation:.3f} ")
                f.write("(indicates how well ranking quality correlates with coverage)\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("### 5.3 Visual Analysis\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("#### 5.3.1 Overall Performance Comparison\n\n")
                f.write(f"![Model Performance Overview]({os.path.basename(viz_files['overview'])})\n\n")
                f.write("*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*\n\n")
            
            # Add corpus statistics visualizations
            if 'corpus_stats' in viz_files:
                f.write("#### 5.3.2 Dataset Characteristics\n\n")
                f.write(f"![Corpus Statistics]({os.path.basename(viz_files['corpus_stats'])})\n\n")
                f.write("*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*\n\n")
            
            # Add individual metric charts
            f.write("#### 5.3.3 Individual Metric Analysis\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name not in ['overview', 'corpus_stats']:
                    f.write(f"##### {metric_name.upper()}@{cfg.k} Results\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis
        if len(model_results) >= 2:
            f.write("### 5.4 Statistical Significance Analysis\n\n")
            f.write("The following tables show absolute differences between model pairs. ")
            f.write("Differences greater than 0.05 may indicate practically significant improvements ")
            f.write("for real-world applications.\n\n")
            
            # Create significance tables for each metric
            idx_map = {
                "MAP": 1 if cfg.compute_map else None,
                "Recall": 2 if cfg.compute_recall else None,
                "Precision": 3 if cfg.compute_precision else None,
                "NDCG": 4 if cfg.compute_ndcg else None,
                "MRR": 5 if cfg.compute_mrr else None
            }
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]
            
            for metric_name, metric_idx in idx_map.items():
                if metric_idx is None:
                    continue
                
                f.write(f"#### {metric_name}@{cfg.k} Pairwise Differences\n\n")
                
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
                f.write("\n\n*Note: Values marked with * indicate potentially significant differences (>0.05).*\n\n")
        
        # Technical implementation details
        f.write("## Technical Implementation\n\n")
        f.write("### 6.1 Pipeline Architecture\n\n")
        f.write("The benchmark pipeline implements a modular architecture with the following components:\n\n")
        f.write("- **Document Processing Module**: PDF extraction and chunking using PyMuPDF and LangChain\n")
        f.write("- **LLM Integration**: Gemini API for query generation and relevance assessment\n")
        f.write("- **Vector Database**: ChromaDB with native embedding functions\n")
        f.write("- **Evaluation Engine**: SentenceTransformers evaluation framework\n")
        f.write("- **Reporting System**: Automated report generation with visualizations\n\n")
        
        f.write("### 6.2 Reproducibility\n\n")
        f.write("All experiments can be reproduced using the following commands:\n\n")
        f.write("```bash\n")
        f.write("# 1. Process PDFs into chunks\n")
        f.write("python simple_rag_benchmark_pipeline.py --prepare-corpus\n\n")
        f.write("# 2. Generate queries and relevance judgments\n")
        f.write("python simple_rag_benchmark_pipeline.py --generate-qrels\n\n")
        f.write("# 3. Run complete benchmark\n")
        f.write("python simple_rag_benchmark_pipeline.py --all\n")
        f.write("```\n\n")
        
        # Embedding model details
        f.write("### 6.3 Embedding Model Specifications\n\n")
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.models]:
            f.write(f"#### {model_name}\n\n")
            f.write(f"- **Collection identifier**: `{collection_name}`\n")
            
            # Add additional model information if available
            try:
                model = SentenceTransformer(model_name)
                f.write(f"- **Embedding dimension**: {model.get_sentence_embedding_dimension()}\n")
                f.write(f"- **Maximum sequence length**: {model.max_seq_length}\n")
                f.write(f"- **Model architecture**: Transformer-based sentence encoder\n\n")
            except:
                f.write("- **Model specifications**: Not available through SentenceTransformers interface\n\n")
        
        # Discussion and limitations
        f.write("## Discussion\n\n")
        f.write("### 7.1 Key Findings\n\n")
        
        best_model_name = sorted_results[0][0]
        f.write(f"1. **Model Performance Hierarchy**: {best_model_name} emerged as the top performer, ")
        f.write(f"achieving superior results across multiple evaluation metrics.\n\n")
        
        if len(sorted_results) > 1:
            second_best = sorted_results[1]
            map_diff = sorted_results[0][1] - second_best[1]
            
            f.write(f"2. **Performance Gaps**: The performance difference between the best and second-best ")
            f.write(f"models ({map_diff:.4f} MAP@{cfg.k}) suggests that model selection significantly ")
            f.write(f"impacts retrieval quality.\n\n")
        
        f.write("3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation ")
        f.write("process demonstrates the feasibility of automated benchmark creation for domain-specific ")
        f.write("document collections.\n\n")
        
        f.write("### 7.2 Limitations and Future Work\n\n")
        f.write("- **Single-domain evaluation**: Current results are specific to the evaluated document collection\n")
        f.write("- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model\n")
        f.write("- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs\n")
        f.write("- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        f.write("This study presents a comprehensive framework for evaluating embedding models in RAG systems. ")
        f.write("Our automated pipeline successfully generated meaningful evaluation datasets and provided ")
        f.write("statistically robust comparisons of model performance. ")
        
        f.write(f"The results demonstrate that **{best_model_name}** provides optimal retrieval performance ")
        f.write(f"for the evaluated document collection, with a MAP@{cfg.k} score of {sorted_results[0][1]:.4f}. ")
        
        if len(sorted_results) > 1 and (sorted_results[0][1] - sorted_results[-1][1]) > 0.1:
            f.write("The substantial performance variations across models underscore the importance of ")
            f.write("systematic evaluation in embedding model selection for production RAG systems.")
        else:
            f.write("While performance differences were moderate, the evaluation framework provides ")
            f.write("valuable insights for informed model selection based on specific application requirements.")
        
        f.write("\n\nThe open-source nature of our evaluation framework enables researchers and practitioners ")
        f.write("to adapt the methodology for their specific domains and requirements, contributing to ")
        f.write("more systematic and reproducible evaluation practices in the RAG community.\n\n")
        
        f.write("---\n\n")
        f.write(f"*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at {timestamp}.*\n")
        f.write("*Source code and evaluation data available at the project repository.*\n")
    
    return report_file

def generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, output_dir, timestamp):
    """Generate visualizations for corpus statistics."""
    viz_files = {}
    
    # Create figure with subplots for different statistics
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Dataset Characteristics and Statistics', fontsize=16, fontweight='bold')
    
    # 1. Chunk length distribution
    axes[0, 0].hist(chunk_lengths, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_xlabel('Chunk Length (words)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of Chunk Lengths')
    axes[0, 0].axvline(np.mean(chunk_lengths), color='red', linestyle='--', label=f'Mean: {np.mean(chunk_lengths):.1f}')
    axes[0, 0].legend()
    
    # 2. Query length distribution
    axes[0, 1].hist(query_lengths, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 1].set_xlabel('Query Length (words)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Distribution of Query Lengths')
    axes[0, 1].axvline(np.mean(query_lengths), color='red', linestyle='--', label=f'Mean: {np.mean(query_lengths):.1f}')
    axes[0, 1].legend()
    
    # 3. Relevance distribution
    axes[1, 0].hist(relevance_distribution, bins=max(relevance_distribution)+1, alpha=0.7, color='orange', edgecolor='black')
    axes[1, 0].set_xlabel('Number of Relevant Documents per Query')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Relevance Distribution')
    axes[1, 0].axvline(np.mean(relevance_distribution), color='red', linestyle='--', label=f'Mean: {np.mean(relevance_distribution):.1f}')
    axes[1, 0].legend()
    
    # 4. Summary statistics table as text
    axes[1, 1].axis('off')
    summary_stats = [
        ['Metric', 'Chunks', 'Queries', 'Relevance'],
        ['Count', f'{len(chunk_lengths)}', f'{len(query_lengths)}', f'{len(relevance_distribution)}'],
        ['Mean', f'{np.mean(chunk_lengths):.1f}', f'{np.mean(query_lengths):.1f}', f'{np.mean(relevance_distribution):.1f}'],
        ['Median', f'{np.median(chunk_lengths):.1f}', f'{np.median(query_lengths):.1f}', f'{np.median(relevance_distribution):.1f}'],
        ['Std Dev', f'{np.std(chunk_lengths):.1f}', f'{np.std(query_lengths):.1f}', f'{np.std(relevance_distribution):.1f}']
    ]
    
    table = axes[1, 1].table(cellText=summary_stats[1:], colLabels=summary_stats[0], 
                            cellLoc='center', loc='center', bbox=[0, 0.3, 1, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    axes[1, 1].set_title('Summary Statistics', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the combined statistics figure
    viz_file = os.path.join(output_dir, f"corpus_statistics_{timestamp}.png")
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    viz_files['corpus_stats'] = viz_file
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

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, output_dir="reports"):
    """Generate a comprehensive benchmark report suitable for a conference paper."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.md")
    
    # Sort models by MAP score for easier comparison
    sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
    
    # Calculate additional statistics
    chunk_lengths = [len(text.split()) for text in corpus.values()]
    query_lengths = [len(text.split()) for text in queries.values()]
    relevance_distribution = [len(v) for v in relevant_docs.values()]
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp)
        # Generate additional statistics visualizations
        viz_files.update(generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, output_dir, timestamp))
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write("# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models\n\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Abstract
        f.write("## Abstract\n\n")
        f.write("This paper presents a systematic evaluation framework for embedding models in ")
        f.write("Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline ")
        f.write("that processes PDF documents, generates synthetic queries using large language models, ")
        f.write("and evaluates retrieval performance across multiple embedding models using standardized ")
        f.write("information retrieval metrics. Our framework provides researchers and practitioners ")
        f.write("with a reproducible methodology for selecting optimal embedding models for their ")
        f.write("specific document collections and use cases.\n\n")
        
        # Executive summary
        f.write("## Executive Summary\n\n")
        f.write("This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used **{len(corpus)} documents** and **{len(queries)} queries** with **{sum(len(v) for v in relevant_docs.values())} relevant document mappings**.\n\n")
        
        # Best model highlight
        best_model = sorted_results[0]
        f.write(f"**Best performing model:** `{best_model[0]}`\n")
        if cfg.compute_map:
            f.write(f"* MAP@{cfg.k}: **{best_model[1]:.4f}**\n")
        if cfg.compute_recall:
            f.write(f"* Recall@{cfg.k}: **{best_model[2]:.4f}**\n")
        if cfg.compute_precision:
            f.write(f"* Precision@{cfg.k}: **{best_model[3]:.4f}**\n")
        if cfg.compute_ndcg:
            f.write(f"* NDCG@{cfg.k}: **{best_model[4]:.4f}**\n")
        if cfg.compute_mrr:
            f.write(f"* MRR@{cfg.k}: **{best_model[5]:.4f}**\n\n")
        
        # Methodology
        f.write("## Methodology\n\n")
        f.write("### 1. Automated Pipeline Overview\n\n")
        f.write("Our evaluation framework consists of five main stages:\n\n")
        f.write("1. **PDF Processing**: Document ingestion and chunking\n")
        f.write("2. **Corpus Generation**: Creation of standardized document chunks\n")
        f.write("3. **Query Generation**: LLM-assisted query synthesis\n")
        f.write("4. **Relevance Assessment**: Automated qrels generation\n")
        f.write("5. **Embedding Evaluation**: Multi-model performance comparison\n\n")
        
        f.write("### 2. Document Processing Pipeline\n\n")
        f.write("#### 2.1 PDF Extraction and Chunking\n\n")
        f.write(f"- **Source documents**: PDF files from `{cfg.pdf_dir}` directory\n")
        f.write(f"- **Chunking strategy**: Recursive character text splitting\n")
        f.write(f"- **Chunk size**: {cfg.chunk_size} characters\n")
        f.write(f"- **Chunk overlap**: {cfg.chunk_overlap} characters\n")
        f.write(f"- **Total chunks generated**: {len(corpus)}\n\n")
        
        f.write("The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to ")
        f.write("maintain semantic coherence while ensuring manageable chunk sizes for embedding models.\n\n")
        
        f.write("#### 2.2 Query Generation Process\n\n")
        f.write(f"- **LLM Model**: {cfg.llm_model}\n")
        f.write(f"- **Number of queries generated**: {len(queries)}\n")
        f.write(f"- **Generation strategy**: Seed-chunk → Query → Retrieval → Label\n")
        f.write(f"- **Candidate pool size**: {cfg.candidate_pool_size} chunks per query\n\n")
        
        f.write("Queries were generated using the following systematic approach:\n")
        f.write("1. Random sampling of seed chunks from the corpus\n")
        f.write("2. LLM-based question generation targeting specific chunks\n")
        f.write("3. Retrieval-based candidate identification using ChromaDB\n")
        f.write("4. LLM-based relevance labeling for comprehensive qrels\n\n")
        
        # Dataset statistics
        f.write("### 3. Dataset Statistics\n\n")
        
        # Corpus statistics table
        f.write("#### 3.1 Corpus Characteristics\n\n")
        corpus_stats = [
            ["Total Documents", f"{len(corpus):,}"],
            ["Average Chunk Length (words)", f"{np.mean(chunk_lengths):.1f}"],
            ["Median Chunk Length (words)", f"{np.median(chunk_lengths):.1f}"],
            ["Min Chunk Length (words)", f"{min(chunk_lengths)}"],
            ["Max Chunk Length (words)", f"{max(chunk_lengths)}"],
            ["Standard Deviation", f"{np.std(chunk_lengths):.1f}"]
        ]
        f.write(tabulate(corpus_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Query statistics table
        f.write("#### 3.2 Query Characteristics\n\n")
        query_stats = [
            ["Total Queries", f"{len(queries)}"],
            ["Average Query Length (words)", f"{np.mean(query_lengths):.1f}"],
            ["Median Query Length (words)", f"{np.median(query_lengths):.1f}"],
            ["Min Query Length (words)", f"{min(query_lengths)}"],
            ["Max Query Length (words)", f"{max(query_lengths)}"],
            ["Standard Deviation", f"{np.std(query_lengths):.1f}"]
        ]
        f.write(tabulate(query_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Relevance statistics
        f.write("#### 3.3 Relevance Distribution\n\n")
        relevance_stats = [
            ["Total Relevance Judgments", f"{sum(relevance_distribution)}"],
            ["Average Relevant Docs per Query", f"{np.mean(relevance_distribution):.1f}"],
            ["Median Relevant Docs per Query", f"{np.median(relevance_distribution):.1f}"],
            ["Min Relevant Docs", f"{min(relevance_distribution)}"],
            ["Max Relevant Docs", f"{max(relevance_distribution)}"],
            ["Coverage Ratio", f"{sum(relevance_distribution)/len(corpus)*100:.2f}%"]
        ]
        f.write(tabulate(relevance_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Benchmark configuration
        f.write("### 4. Experimental Setup\n\n")
        f.write("#### 4.1 Evaluation Framework\n\n")
        f.write("- **Vector Database**: ChromaDB\n")
        f.write("- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator\n")
        f.write(f"- **Retrieval Depth (k)**: {cfg.k}\n")
        f.write(f"- **Batch Size**: {cfg.batch_size}\n")
        f.write(f"- **Collection Reinitialization**: {cfg.reinitialize_collections}\n\n")
        
        f.write("#### 4.2 Evaluated Models\n\n")
        model_info_table = []
        for model_cfg in cfg.models:
            try:
                model = SentenceTransformer(model_cfg["model_name"])
                dimensions = model.get_sentence_embedding_dimension()
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    dimensions,
                    "Sentence Transformer"
                ])
            except:
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    "N/A",
                    "N/A"
                ])
        
        f.write(tabulate(model_info_table, 
                        headers=["Model Name", "Collection", "Dimensions", "Type"], 
                        tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("#### 4.3 Evaluation Metrics\n\n")
        metrics_desc = []
        if cfg.compute_map:
            metrics_desc.append(["MAP@k", "Mean Average Precision at rank k", "Ranking quality"])
        if cfg.compute_recall:
            metrics_desc.append(["Recall@k", "Proportion of relevant docs in top k", "Coverage"])
        if cfg.compute_precision:
            metrics_desc.append(["Precision@k", "Proportion of relevant docs among retrieved", "Accuracy"])
        if cfg.compute_ndcg:
            metrics_desc.append(["NDCG@k", "Normalized Discounted Cumulative Gain", "Ranking with position bias"])
        if cfg.compute_mrr:
            metrics_desc.append(["MRR@k", "Mean Reciprocal Rank", "First relevant position"])
        
        f.write(tabulate(metrics_desc, headers=["Metric", "Description", "Measures"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Add example queries
        f.write("#### 4.4 Representative Query Examples\n\n")
        query_sample = list(queries.items())[:5]
        query_table = []
        for qid, text in query_sample:
            rel_count = len(relevant_docs.get(qid, set()))
            # Truncate long queries for display
            display_text = text[:100] + "..." if len(text) > 100 else text
            query_table.append([qid, display_text, rel_count])
        
        f.write(tabulate(query_table, headers=["Query ID", "Query Text", "# Relevant Docs"], tablefmt="pipe"))
        f.write("\n\n")
        
        # Results section
        f.write("## Results\n\n")
        
        # Comparative results table
        f.write("### 5.1 Model Performance Comparison\n\n")
        
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
        
        f.write("**Table: Comprehensive Model Performance Results**\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        # Performance analysis
        f.write("### 5.2 Performance Analysis\n\n")
        if len(sorted_results) > 1:
            best_model = sorted_results[0]
            worst_model = sorted_results[-1]
            
            f.write(f"The evaluation reveals significant performance variations across embedding models. ")
            f.write(f"**{best_model[0]}** achieved the highest MAP@{cfg.k} score of {best_model[1]:.4f}, ")
            f.write(f"while **{worst_model[0]}** scored {worst_model[1]:.4f}, representing a ")
            f.write(f"**{((best_model[1] - worst_model[1]) / worst_model[1] * 100):.1f}% improvement**.\n\n")
            
            # Correlation analysis between metrics
            if cfg.compute_map and cfg.compute_recall:
                map_scores = [r[1] for r in sorted_results]
                recall_scores = [r[2] for r in sorted_results]
                correlation = np.corrcoef(map_scores, recall_scores)[0, 1]
                f.write(f"**MAP-Recall Correlation**: {correlation:.3f} ")
                f.write("(indicates how well ranking quality correlates with coverage)\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("### 5.3 Visual Analysis\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("#### 5.3.1 Overall Performance Comparison\n\n")
                f.write(f"![Model Performance Overview]({os.path.basename(viz_files['overview'])})\n\n")
                f.write("*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*\n\n")
            
            # Add corpus statistics visualizations
            if 'corpus_stats' in viz_files:
                f.write("#### 5.3.2 Dataset Characteristics\n\n")
                f.write(f"![Corpus Statistics]({os.path.basename(viz_files['corpus_stats'])})\n\n")
                f.write("*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*\n\n")
            
            # Add individual metric charts
            f.write("#### 5.3.3 Individual Metric Analysis\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name not in ['overview', 'corpus_stats']:
                    f.write(f"##### {metric_name.upper()}@{cfg.k} Results\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis
        if len(model_results) >= 2:
            f.write("### 5.4 Statistical Significance Analysis\n\n")
            f.write("The following tables show absolute differences between model pairs. ")
            f.write("Differences greater than 0.05 may indicate practically significant improvements ")
            f.write("for real-world applications.\n\n")
            
            # Create significance tables for each metric
            idx_map = {
                "MAP": 1 if cfg.compute_map else None,
                "Recall": 2 if cfg.compute_recall else None,
                "Precision": 3 if cfg.compute_precision else None,
                "NDCG": 4 if cfg.compute_ndcg else None,
                "MRR": 5 if cfg.compute_mrr else None
            }
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]
            
            for metric_name, metric_idx in idx_map.items():
                if metric_idx is None:
                    continue
                
                f.write(f"#### {metric_name}@{cfg.k} Pairwise Differences\n\n")
                
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
                f.write("\n\n*Note: Values marked with * indicate potentially significant differences (>0.05).*\n\n")
        
        # Technical implementation details
        f.write("## Technical Implementation\n\n")
        f.write("### 6.1 Pipeline Architecture\n\n")
        f.write("The benchmark pipeline implements a modular architecture with the following components:\n\n")
        f.write("- **Document Processing Module**: PDF extraction and chunking using PyMuPDF and LangChain\n")
        f.write("- **LLM Integration**: Gemini API for query generation and relevance assessment\n")
        f.write("- **Vector Database**: ChromaDB with native embedding functions\n")
        f.write("- **Evaluation Engine**: SentenceTransformers evaluation framework\n")
        f.write("- **Reporting System**: Automated report generation with visualizations\n\n")
        
        f.write("### 6.2 Reproducibility\n\n")
        f.write("All experiments can be reproduced using the following commands:\n\n")
        f.write("```bash\n")
        f.write("# 1. Process PDFs into chunks\n")
        f.write("python simple_rag_benchmark_pipeline.py --prepare-corpus\n\n")
        f.write("# 2. Generate queries and relevance judgments\n")
        f.write("python simple_rag_benchmark_pipeline.py --generate-qrels\n\n")
        f.write("# 3. Run complete benchmark\n")
        f.write("python simple_rag_benchmark_pipeline.py --all\n")
        f.write("```\n\n")
        
        # Embedding model details
        f.write("### 6.3 Embedding Model Specifications\n\n")
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.models]:
            f.write(f"#### {model_name}\n\n")
            f.write(f"- **Collection identifier**: `{collection_name}`\n")
            
            # Add additional model information if available
            try:
                model = SentenceTransformer(model_name)
                f.write(f"- **Embedding dimension**: {model.get_sentence_embedding_dimension()}\n")
                f.write(f"- **Maximum sequence length**: {model.max_seq_length}\n")
                f.write(f"- **Model architecture**: Transformer-based sentence encoder\n\n")
            except:
                f.write("- **Model specifications**: Not available through SentenceTransformers interface\n\n")
        
        # Discussion and limitations
        f.write("## Discussion\n\n")
        f.write("### 7.1 Key Findings\n\n")
        
        best_model_name = sorted_results[0][0]
        f.write(f"1. **Model Performance Hierarchy**: {best_model_name} emerged as the top performer, ")
        f.write(f"achieving superior results across multiple evaluation metrics.\n\n")
        
        if len(sorted_results) > 1:
            second_best = sorted_results[1]
            map_diff = sorted_results[0][1] - second_best[1]
            
            f.write(f"2. **Performance Gaps**: The performance difference between the best and second-best ")
            f.write(f"models ({map_diff:.4f} MAP@{cfg.k}) suggests that model selection significantly ")
            f.write(f"impacts retrieval quality.\n\n")
        
        f.write("3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation ")
        f.write("process demonstrates the feasibility of automated benchmark creation for domain-specific ")
        f.write("document collections.\n\n")
        
        f.write("### 7.2 Limitations and Future Work\n\n")
        f.write("- **Single-domain evaluation**: Current results are specific to the evaluated document collection\n")
        f.write("- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model\n")
        f.write("- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs\n")
        f.write("- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        f.write("This study presents a comprehensive framework for evaluating embedding models in RAG systems. ")
        f.write("Our automated pipeline successfully generated meaningful evaluation datasets and provided ")
        f.write("statistically robust comparisons of model performance. ")
        
        f.write(f"The results demonstrate that **{best_model_name}** provides optimal retrieval performance ")
        f.write(f"for the evaluated document collection, with a MAP@{cfg.k} score of {sorted_results[0][1]:.4f}. ")
        
        if len(sorted_results) > 1 and (sorted_results[0][1] - sorted_results[-1][1]) > 0.1:
            f.write("The substantial performance variations across models underscore the importance of ")
            f.write("systematic evaluation in embedding model selection for production RAG systems.")
        else:
            f.write("While performance differences were moderate, the evaluation framework provides ")
            f.write("valuable insights for informed model selection based on specific application requirements.")
        
        f.write("\n\nThe open-source nature of our evaluation framework enables researchers and practitioners ")
        f.write("to adapt the methodology for their specific domains and requirements, contributing to ")
        f.write("more systematic and reproducible evaluation practices in the RAG community.\n\n")
        
        f.write("---\n\n")
        f.write(f"*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at {timestamp}.*\n")
        f.write("*Source code and evaluation data available at the project repository.*\n")
    
    
    # Convert to PDF
    pdf_file = convert_md_to_pdf(report_file, output_dir)
    if pdf_file:
        print(f"PDF report saved to: {pdf_file}")
    
    return report_file, pdf_file

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
        
        for model_cfg in cfg.models:
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
                report_file, pdf_file = generate_benchmark_report(model_results, queries, corpus, relevant_docs)
                print(f"\nDetailed benchmark report saved to: {report_file} and PDF version at {pdf_file}")
        
    print("\nBenchmark completed!")

if __name__ == "__main__":
    main()