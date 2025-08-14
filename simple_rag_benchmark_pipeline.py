import random
import json
import os
import time
import re
import numpy as np
import argparse

import benchmark_config as cfg
from utils.llm import generate_content
from utils.chromadb_utils import get_chromadb_client, initialize_collection, evaluate_with_chromadb
from utils.report_utils import generate_benchmark_report, print_results_summary, print_report_info
from utils.document_loader import prepare_corpus_from_pdfs
from utils.document_loader import load_corpus as load_corpus_from_file
from utils.document_loader import load_queries as load_queries_from_file  
from utils.document_loader import load_ground_truth

def prepare_corpus_from_pdfs_wrapper():
    """
    Wrapper function that calls the refactored prepare_corpus_from_pdfs with config values.
    This maintains backward compatibility with the pipeline interface.
    """
    result = prepare_corpus_from_pdfs(
        pdf_dir=cfg.pdf_dir,
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        corpus_file=cfg.corpus_file
    )
    print(f"Corpus preparation complete: {result['chunks_created']} chunks created")
    return result



def generate_queries_from_corpus() -> dict[str,str]:
    print("Selecting seed chunks from corpus...")
    
    # Use the refactored load_corpus function
    corpus = load_corpus_from_file(cfg.corpus_file)
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
            time.sleep(cfg.llm_timeout)  # Wait to avoid hitting API limits
            # Generate query using the LLM
            generated_query = generate_content(cfg.generate_query_system_instruction,prompt)
            print(f"Generated query: {generated_query}")
            
            # Save query immediately
            query_id = f"q{i+1}_for_{seed_id}"
            f.write(json.dumps({"query_id": query_id, "text": generated_query}) + "\n")
            
    print("Query generation and saving complete. Queries saved to", cfg.queries_file)
 
def generate_qrels():
    # Use refactored load_corpus function
    corpus = load_corpus_from_file(cfg.corpus_file)
    # Use the first configured model and collection for qrels generation
    first_model = cfg.embedding_models[0]
    model_name = first_model["model_name"]
    collection_name = first_model["collection_name"] + "_qrels"  # Avoid conflict with benchmark collections
    
    print(f"Generating qrels using model: {model_name}")
    print(f"Using temporary collection: {collection_name}")
    
    initialize_collection(corpus, model_name, collection_name)
    # Use persistent client instead of chromadb.Client()
    client = get_chromadb_client()
    try:
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error: Collection {collection_name} not found. Did you run initialization?")
        raise e
    print(f"Collection {collection_name} initialized successfully.")
    
    # Load queries using refactored function
    queries = load_queries_from_file(cfg.queries_file)
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

def load_queries() -> dict[str,str]:
    """
    DEPRECATED: Use utils.document_loader.load_queries() instead.
    Kept for backward compatibility.
    """
    print("Warning: Using deprecated load_queries(). Use utils.document_loader.load_queries() instead.")
    from utils.document_loader import load_queries as new_load_queries
    return new_load_queries(cfg.queries_file)

def load_corpus() -> dict[str,str]:
    """
    DEPRECATED: Use utils.document_loader.load_corpus() instead.
    Kept for backward compatibility.
    """
    print("Warning: Using deprecated load_corpus(). Use utils.document_loader.load_corpus() instead.")
    from utils.document_loader import load_corpus as new_load_corpus
    return new_load_corpus(cfg.corpus_file)
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
    
    # Handle individual pipeline steps - EXIT after each
    if args.prepare_corpus:
        prepare_corpus_from_pdfs_wrapper()
        return
        
    if args.generate_queries:
        generate_queries_from_corpus()
        return
        
    if args.generate_qrels:
        generate_qrels()
        return
        
    # Handle complete pipeline
    if args.all:
        print("Starting complete RAG benchmark pipeline...")
        prepare_corpus_from_pdfs_wrapper()
        generate_queries_from_corpus()
        generate_qrels()
        # Continue to evaluation section below
        
    # Handle initialization and evaluation
    if args.initialize or args.evaluate or args.all:
        # Validate required files
        for file_path in [cfg.corpus_file, cfg.queries_file, cfg.qrels_file]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        print("Starting embedding model evaluation...")
        print(f"Configuration: k={cfg.k}, show_progress={cfg.show_progress_bar}, reinit_collections={cfg.reinitialize_collections}")
        
        # Load ground truth data ONCE using refactored function
        queries, corpus, relevant_docs = load_ground_truth(cfg.corpus_file, cfg.queries_file, cfg.qrels_file)
        
        # Initialize containers ONCE
        model_results = []
        timing_results = []
        
        # Process each model ONCE
        for model_cfg in cfg.embedding_models:
            model_name = model_cfg["model_name"]
            collection_name = model_cfg["collection_name"]
            
            # Initialize if requested
            if args.initialize or args.all:
                timing_data = initialize_collection(corpus, model_name, collection_name)
                if timing_data and isinstance(timing_data, dict):
                    timing_results.append((model_name, timing_data))
            
            # Evaluate if requested
            if args.evaluate or args.all:
                # If no timing data exists, we need to initialize first or skip timing in report
                if not any(t[0] == model_name for t in timing_results):
                    print(f"⚠️  Warning: No timing data available for {model_name}")
                    print(f"   Run with --initialize first to get accurate timing metrics")
                    # Add empty timing data to indicate missing measurements
                    timing_results.append((model_name, {
                        "embedding_time": None, 
                        "docs_processed": len(corpus),
                        "docs_per_second": None, 
                        "avg_time_per_doc": None,
                        "note": "Timing data unavailable - run --initialize first"
                    }))
                
                # Evaluate model
                metrics = evaluate_with_chromadb(queries, corpus, relevant_docs, model_name, collection_name)
                model_results.append((model_name, *metrics))
        
        # Display and generate report ONLY ONCE
        if model_results:
            print_results_summary(model_results)
            report_files = generate_benchmark_report(model_results, queries, corpus, relevant_docs, timing_results)
            print_report_info(report_files)
    
    print("\nBenchmark completed!")


if __name__ == "__main__":
    main()