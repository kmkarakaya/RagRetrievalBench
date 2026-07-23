import random
import json
import os
import time
import re
import sys
import unicodedata
import numpy as np
import argparse

import config as cfg
from utils.llm import generate_content
from utils.batch_manager import BatchManager
from utils.chromadb_utils import get_chromadb_client, initialize_collection, evaluate_with_chromadb
from utils.report_utils import generate_benchmark_report, print_results_summary, print_report_info
from utils.document_loader import prepare_corpus_from_pdfs
from utils.document_loader import load_corpus as load_corpus_from_file
from utils.document_loader import load_queries as load_queries_from_file  
from utils.document_loader import load_ground_truth

def configure_utf8_stdio() -> None:
    """
    Force UTF-8 console output when possible.
    Prevents garbled Turkish text in Windows terminals with legacy code pages.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

def normalize_unicode_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    return unicodedata.normalize("NFC", text)

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

def extract_response_text(batch_result):
    """Helper to extract text from a Batch API result object."""
    try:
        # Check for candidates directly in response
        response = batch_result.get("response", {})
        candidates = response.get("candidates", [])
        
        # Fallback: check for body (sometimes SDK wrappers might use this)
        if not candidates:
            candidates = response.get("body", {}).get("candidates", [])
            
        if candidates:
            return candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
    except Exception:
        pass
    return ""

def parse_source_chunk_id(query_id: str) -> str | None:
    """Extract source chunk id from query ids like q12_for_DocName_chunk7."""
    if not query_id or "_for_" not in query_id:
        return None

    _, source_part = query_id.split("_for_", 1)
    if not source_part:
        return None

    # Use last _chunkN suffix so doc names containing "_chunk" remain parseable.
    match = re.match(r"^(.+)_chunk(\d+)$", source_part)
    if not match:
        return None

    doc_name, chunk_num = match.groups()
    if not doc_name:
        return None
    return f"{doc_name}_chunk{chunk_num}"

def add_forced_source_qrel(query_id: str, qrel_map: dict[str, dict[str, int]]) -> bool:
    """Force-add source chunk as relevant for a query. Returns False if query_id is unparseable."""
    source_chunk_id = parse_source_chunk_id(query_id)
    if source_chunk_id is None:
        print(f"WARNING: Could not parse source chunk from query_id: {query_id}")
        return False

    qrel_map.setdefault(query_id, {})[source_chunk_id] = 1
    return True

def parse_relevance_score(text: str) -> int:
    """Parse LLM relevance response; return positive integer or 0."""
    if not text:
        return 0

    try:
        json_pattern = r'({[\s\S]*?})'
        match = re.search(json_pattern, text)
        if match:
            relevance_json = json.loads(match.group(1))
        else:
            relevance_json = json.loads(text)

        score = int(relevance_json.get("relevance", 0))
        return score if score > 0 else 0
    except Exception:
        return 0

def apply_source_chunk_coverage(query_ids: list[str], qrel_map: dict[str, set[str]]) -> dict:
    """Apply forced source qrels for all queries and return coverage stats."""
    forced_count = 0
    unparseable_query_ids = []

    for query_id in query_ids:
        if add_forced_source_qrel(query_id, qrel_map):
            forced_count += 1
        else:
            unparseable_query_ids.append(query_id)

    queries_without_any_positive_after_merge = [
        query_id for query_id in query_ids
        if not any(int(v) > 0 for v in qrel_map.get(query_id, {}).values())
    ]

    coverage = {
        "forced_count": forced_count,
        "unparseable_count": len(unparseable_query_ids),
        "queries_without_any_positive_after_merge": queries_without_any_positive_after_merge,
    }

    print("Qrels coverage summary:")
    print(f"  forced_count: {coverage['forced_count']}")
    print(f"  unparseable_count: {coverage['unparseable_count']}")
    print(
        "  queries_without_any_positive_after_merge: "
        f"{len(coverage['queries_without_any_positive_after_merge'])}"
    )

    if unparseable_query_ids:
        print("  unparseable_query_ids: " + ", ".join(sorted(unparseable_query_ids)))
    if queries_without_any_positive_after_merge:
        print(
            "  queries_without_any_positive_after_merge_ids: "
            + ", ".join(sorted(queries_without_any_positive_after_merge))
        )

    return coverage

def write_qrels_tsv(qrel_map: dict[str, dict[str, int]], qrels_file: str, store_negatives: bool = True) -> int:
    """Write deterministic qrels.tsv (query_id<TAB>doc_id<TAB>label) from a
    {query_id: {doc_id: label}} map. Negative rows (label 0) are written only when
    store_negatives is True; the loader ignores 0-rows for evaluation but keeping
    them makes non-relevant decisions auditable."""
    total_rows = 0
    with open(qrels_file, 'w', encoding='utf-8') as f:
        for query_id in sorted(qrel_map.keys()):
            for doc_id in sorted(qrel_map[query_id].keys()):
                label = int(qrel_map[query_id][doc_id])
                if label <= 0 and not store_negatives:
                    continue
                f.write(f"{query_id}\t{doc_id}\t{label}\n")
                total_rows += 1
    return total_rows


def build_qrels_candidate_pool(corpus: dict, queries: dict) -> dict:
    """Return {query_id: [(doc_id, text), ...]} candidate pool for LLM judging.

    When cfg.qrels_pooling is True, the pool for each query is the deduplicated
    union of the top cfg.candidate_pool_size chunks retrieved by EVERY model in
    cfg.embedding_models, so the constructed ground truth does not privilege any
    single evaluated model. When False, it uses only cfg.qrels_embedding_model_index
    (legacy single-model pool). Collections are (re)built via initialize_collection
    under their real names so the evaluation stage can reuse them.
    """
    if getattr(cfg, "qrels_pooling", True):
        models = cfg.embedding_models
    else:
        models = [cfg.embedding_models[cfg.qrels_embedding_model_index]]

    client = get_chromadb_client()
    pool: dict[str, dict[str, str]] = {qid: {} for qid in queries}
    for model_cfg in models:
        initialize_collection(corpus, model_cfg["model_name"], model_cfg["collection_name"])
        collection = client.get_collection(model_cfg["collection_name"])
        for query_id, query_text in queries.items():
            results = collection.query(query_texts=[query_text], n_results=cfg.candidate_pool_size)
            for doc_id, text in zip(results["ids"][0], results["documents"][0]):
                if doc_id not in pool[query_id]:
                    pool[query_id][doc_id] = text
    return {qid: list(docs.items()) for qid, docs in pool.items()}



def generate_queries_from_corpus(batch_submit=False, batch_fetch_id=None) -> bool:
    # --- Batch Fetch Mode ---
    if batch_fetch_id:
        print(f"Fetching QUERY results for batch {batch_fetch_id}...")
        bm = BatchManager()
        results = bm.download_results(batch_fetch_id)
        if not results:
            return

        print(f"Writing {len(results)} queries to {cfg.queries_file}...")
        with open(cfg.queries_file, 'w', encoding='utf-8') as f:
            for res in results:
                # Key maps to query_id
                key = res.get("custom_id") or res.get("key")
                text = extract_response_text(res)
                
                if key and text:
                    normalized_key = normalize_unicode_text(key)
                    normalized_text = normalize_unicode_text(text)
                    f.write(json.dumps({"query_id": normalized_key, "text": normalized_text}, ensure_ascii=False) + "\n")
        
        # Update batch history to indicate successful fetch
        bm.update_batch_status(batch_fetch_id, "FETCHED_SUCCESSFULLY")
        print("Done.")
        return True

    # --- Normal / Submit Mode ---
    print("Selecting seed chunks from corpus...")
    
    # Use the refactored load_corpus function
    corpus = load_corpus_from_file(cfg.corpus_file)
    print(f"Loaded {len(corpus)} corpus chunks.")
    
    if len(corpus) == 0:
        print("ERROR: Corpus is empty. Cannot generate queries. Please ensure PDFs are present in the pdf_dir and run --prepare-corpus first.")
        return False
    
    all_ids = list(corpus.keys())
    needed_chunks = cfg.n_queries * cfg.chunks_per_query
    if len(all_ids) < needed_chunks:
        print(f"ERROR: Not enough corpus chunks ({len(all_ids)}) to generate {cfg.n_queries} queries with {cfg.chunks_per_query} chunks each. Need at least {needed_chunks} chunks.")
        return False
    
    # Seed the RNG for reproducible seed-chunk selection (see config.random_seed).
    if getattr(cfg, "random_seed", None) is not None:
        random.seed(cfg.random_seed)
    seed_ids = random.sample(all_ids, needed_chunks)
    print(f"Selected {len(seed_ids)} seed chunks for query generation ({cfg.n_queries} queries, {cfg.chunks_per_query} chunks per query).")

    # Batch Submission
    if batch_submit:
        print("Preparing batch request for Queries...")
        bm = BatchManager()
        requests = []
        for i, seed_id in enumerate(seed_ids):
             query_id = f"q{i+1}_for_{seed_id}"
             # Pass just the document chunk as the user message
             req = bm.prepare_request(query_id, corpus[seed_id], cfg.generate_query_system_instruction, cfg.temperature)
             requests.append(req)
        
        bm.submit_batch(requests, "query_gen")
        print("Batch processing started. Please note the Job Name above for fetching results.")
        return True
    
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
            query_id = normalize_unicode_text(f"q{i+1}_for_{seed_id}")
            normalized_query = normalize_unicode_text(generated_query)
            f.write(json.dumps({"query_id": query_id, "text": normalized_query}, ensure_ascii=False) + "\n")
            
    print("Query generation and saving complete. Queries saved to", cfg.queries_file)
    return True
 
def generate_qrels(batch_submit=False, batch_fetch_id=None) -> bool:
    # --- Batch Fetch Mode ---
    if batch_fetch_id:
        print(f"Fetching QRELS results for batch {batch_fetch_id}...")
        bm = BatchManager()
        results = bm.download_results(batch_fetch_id)
        if not results:
            return False

        try:
            queries = load_queries_from_file(cfg.queries_file)
        except Exception as e:
            print(f"ERROR: Could not load queries file for qrels merge: {e}")
            return False

        qrel_map: dict[str, dict[str, int]] = {}
        for res in results:
            key = res.get("custom_id") or res.get("key")
            text = extract_response_text(res)
            if not key:
                continue

            # Parse key format: query_id|||doc_id
            try:
                query_id, doc_id = key.split("|||", 1)
            except ValueError:
                print(f"Skipping invalid key format: {key}")
                continue

            label = 1 if parse_relevance_score(text) > 0 else 0
            qrel_map.setdefault(query_id, {})[doc_id] = label

        if getattr(cfg, "force_source_chunk_relevant", False):
            apply_source_chunk_coverage(sorted(queries.keys()), qrel_map)
        rows_written = write_qrels_tsv(qrel_map, cfg.qrels_file, getattr(cfg, "qrels_store_negatives", True))
        print(f"Wrote qrels to {cfg.qrels_file} ({rows_written} rows).")

        # Update batch history to indicate successful fetch
        bm.update_batch_status(batch_fetch_id, "FETCHED_SUCCESSFULLY")
        print("Done.")
        return True

    # Use refactored load_corpus function
    corpus = load_corpus_from_file(cfg.corpus_file)

    if len(corpus) == 0:
        print("ERROR: Corpus is empty. Cannot generate qrels. Please ensure PDFs are present and run --prepare-corpus first.")
        return False

    # Load queries using refactored function
    queries = load_queries_from_file(cfg.queries_file)
    print(f"Loaded {len(queries)} queries.")

    if len(queries) == 0:
        print("ERROR: No queries found. Cannot generate qrels. Please run --generate-queries first.")
        return False

    # Build the candidate pool for judging. With cfg.qrels_pooling this is the
    # model-independent union of every model's top candidates; otherwise it is a
    # single-model pool (legacy). See build_qrels_candidate_pool.
    pooling = getattr(cfg, "qrels_pooling", True)
    force = getattr(cfg, "force_source_chunk_relevant", False)
    store_negatives = getattr(cfg, "qrels_store_negatives", True)
    print(f"Building qrels candidate pool (pooling={'all models' if pooling else 'single model'}, "
          f"pool size={cfg.candidate_pool_size} per model)...")
    candidate_pool = build_qrels_candidate_pool(corpus, queries)

    # Batch Submission
    if batch_submit:
        print("Preparing batch request for Qrels...")
        bm = BatchManager()
        requests = []
        for query_id, query_text in queries.items():
            source_chunk_id = parse_source_chunk_id(query_id)
            for i, (doc_id, text) in enumerate(candidate_pool.get(query_id, [])):
                if force and source_chunk_id and doc_id == source_chunk_id:
                    continue  # forced relevant without judging
                prompt = f"Question: {query_text}\n{i+1}. [{doc_id}] \"{text}\"\n\n"
                key = f"{query_id}|||{doc_id}"
                req = bm.prepare_request(key, prompt, cfg.generate_qrels_system_instruction, cfg.temperature)
                requests.append(req)

        bm.submit_batch(requests, "qrels_gen")
        print(f"Submitted {len(requests)} judgments.")
        return True

    print("Generating qrels file...")
    qrel_map: dict[str, dict[str, int]] = {}
    for query_id, query_text in queries.items():
        source_chunk_id = parse_source_chunk_id(query_id)
        candidates = candidate_pool.get(query_id, [])
        print(f"Query {query_id}: judging {len(candidates)} pooled candidates.")
        for i, (doc_id, text) in enumerate(candidates):
            if force and source_chunk_id and doc_id == source_chunk_id:
                continue  # forced relevant without judging
            prompt = f"Question: {query_text}\n{i+1}. [{doc_id}] \"{text}\"\n\n"
            relevance = generate_content(cfg.generate_qrels_system_instruction, prompt)
            label = 1 if parse_relevance_score(relevance) > 0 else 0
            qrel_map.setdefault(query_id, {})[doc_id] = label
            time.sleep(cfg.llm_timeout)  # wait to avoid hitting API limits

    if force:
        apply_source_chunk_coverage(sorted(queries.keys()), qrel_map)
    rows_written = write_qrels_tsv(qrel_map, cfg.qrels_file, store_negatives)
    print(f"Generated qrels file at {cfg.qrels_file} with {len(queries)} queries and {rows_written} rows.")
    if not os.path.exists(cfg.qrels_file):
        print(f"Error: Qrels file {cfg.qrels_file} was not created.")
    else:
        print(f"Created qrels file: {cfg.qrels_file}")

    return True

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
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="RAG Benchmark Pipeline")
    parser.add_argument("--prepare-corpus", action="store_true", help="Prepare corpus.jsonl from PDFs")
    parser.add_argument("--generate-queries", action="store_true", help="Generate queries from corpus")
    parser.add_argument("--generate-qrels", action="store_true", help="Generate qrels file")
    parser.add_argument("--initialize", action="store_true", help="Initialize collections")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate models")
    parser.add_argument("--all", action="store_true", help="Run complete pipeline")
    
    # New Batch Arguments
    parser.add_argument("--batch-submit", action="store_true", help="Submit tasks to Gemini Batch API instead of running locally")
    parser.add_argument("--batch-fetch", type=str, help="Fetch results for a specific Batch Job Name (ID)")
    parser.add_argument("--batch_status", action="store_true", help="List all batch jobs and their statuses")
    parser.add_argument("--batch-cancel", type=str, help="Cancel a specific Batch Job Name (ID)")
    parser.add_argument("--dataset", type=str, help="Dataset name to run benchmark on")
    
    # Aggregate Reporting Arguments
    parser.add_argument("--generate-aggregate-report", action="store_true", 
                       help="Generate cross-dataset aggregate performance report")
    parser.add_argument("--aggregate-datasets", type=str, default=None,
                       help="Comma-separated list of datasets to include (e.g., education,finance). Default: all available")
    parser.add_argument("--aggregate-output-dir", type=str, default=None,
                       help="Custom output directory for aggregate report. Default: reports/aggregate")
    parser.add_argument("--aggregate-metrics", type=str, default=None,
                       help="Comma-separated metrics to analyze (e.g., map,ndcg). Default: common metrics across datasets")
    
    args = parser.parse_args()

    if (args.initialize or args.evaluate or args.all) and not args.dataset:
        parser.error("--dataset is required when using --initialize, --evaluate, or --all")

    if args.dataset:
        cfg.configure_for_dataset(args.dataset)

    # Create necessary directories
    os.makedirs(cfg.reports_dir, exist_ok=True)
    os.makedirs(cfg.pdf_dir, exist_ok=True)
    
    # Handle aggregate report generation
    if args.generate_aggregate_report:
        print("=" * 80)
        print("GENERATING AGGREGATE CROSS-DATASET REPORT")
        print("=" * 80)
        
        # Parse dataset list
        dataset_names = None
        if args.aggregate_datasets:
            dataset_names = [d.strip() for d in args.aggregate_datasets.split(',')]
            print(f"\nDatasets to include: {', '.join(dataset_names)}")
        else:
            dataset_names = cfg.discover_available_datasets()
            print(f"\nAuto-discovered datasets: {', '.join(dataset_names)}")
        
        # Validate minimum datasets
        if len(dataset_names) < cfg.aggregate_min_datasets:
            print(f"\nERROR: Need at least {cfg.aggregate_min_datasets} datasets for aggregation.")
            print(f"Found: {len(dataset_names)} datasets")
            print(f"\nAvailable datasets:")
            for ds in cfg.discover_available_datasets():
                raw_path = cfg.get_latest_raw_results(ds)
                status = "✓ Has raw results" if raw_path else "✗ Missing raw results (run --evaluate first)"
                print(f"  - {ds}: {status}")
            return
        
        # Parse metrics
        metrics = None
        if args.aggregate_metrics:
            metrics = [m.strip() for m in args.aggregate_metrics.split(',')]
        
        # Generate report
        try:
            from utils.aggregate_report_utils import generate_aggregate_report
            
            report_path = generate_aggregate_report(
                dataset_names=dataset_names,
                output_dir=args.aggregate_output_dir,
                metrics=metrics,
                generate_pdf=True
            )
            
            print(f"\n{'='*80}")
            print(f"[Success] Aggregate report generated: {report_path}")
            pdf_path = report_path.replace('.md', '.pdf')
            if os.path.exists(pdf_path):
                print(f"[Success] PDF report: {pdf_path}")
            print(f"{'='*80}\n")
        
        except Exception as e:
            print(f"\n❌ ERROR generating aggregate report: {e}")
            import traceback
            traceback.print_exc()
        
        return  # Exit after generation
    
    # Handle individual pipeline steps - EXIT after each
    if args.prepare_corpus:
        prepare_corpus_from_pdfs_wrapper()
        return
        
    if args.generate_queries:
        generate_queries_from_corpus(batch_submit=args.batch_submit, batch_fetch_id=args.batch_fetch)
        return
        
    if args.generate_qrels:
        generate_qrels(batch_submit=args.batch_submit, batch_fetch_id=args.batch_fetch)
        return
        
    if args.batch_status:
        bm = BatchManager()
        
        # If no dataset specified, show all datasets
        if not hasattr(args, 'dataset') or not args.dataset:
            datasets_dir = os.path.join(os.path.dirname(cfg.reports_dir), 'datasets')
            if os.path.exists(datasets_dir):
                print("Batch Job History Across All Datasets (refreshed from API):")
                dataset_dirs = [d for d in os.listdir(datasets_dir) if os.path.isdir(os.path.join(datasets_dir, d))]
                all_jobs = []
                
                # Check default reports directory
                default_history = os.path.join(os.path.dirname(cfg.reports_dir), 'reports', 'batch_history.jsonl')
                if os.path.exists(default_history):
                    with open(default_history, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = json.loads(line.strip())
                            entry['_dataset'] = 'default'
                            all_jobs.append(entry)
                
                # Check each dataset directory
                for dataset_name in dataset_dirs:
                    dataset_reports_dir = os.path.join(datasets_dir, dataset_name, 'reports')
                    history_file = os.path.join(dataset_reports_dir, 'batch_history.jsonl')
                    if os.path.exists(history_file):
                        with open(history_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                entry = json.loads(line.strip())
                                entry['_dataset'] = dataset_name
                                all_jobs.append(entry)
                
                # Sort by timestamp and display
                all_jobs.sort(key=lambda x: x['timestamp'], reverse=True)
                for entry in all_jobs:
                    dataset_label = f" [{entry['_dataset']}]" if entry['_dataset'] != 'default' else ""
                    current_status = bm.check_status(entry['batch_id'])
                    if current_status != entry['status']:
                        entry['status'] = current_status
                        print(f"- {entry['batch_id']}: {entry['status']} ({entry['type']}) - {entry['timestamp']}{dataset_label} [UPDATED]")
                    else:
                        print(f"- {entry['batch_id']}: {entry['status']} ({entry['type']}) - {entry['timestamp']}{dataset_label}")
                
                # Update all history files with refreshed statuses
                for entry in all_jobs:
                    dataset_name = entry['_dataset']
                    if dataset_name == 'default':
                        history_file = os.path.join(os.path.dirname(cfg.reports_dir), 'reports', 'batch_history.jsonl')
                    else:
                        history_file = os.path.join(datasets_dir, dataset_name, 'reports', 'batch_history.jsonl')
                    
                    # Read current entries for this dataset
                    current_entries = []
                    if os.path.exists(history_file):
                        with open(history_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                current_entries.append(json.loads(line.strip()))
                    
                    # Update the matching entry
                    for i, current_entry in enumerate(current_entries):
                        if current_entry['batch_id'] == entry['batch_id']:
                            current_entries[i]['status'] = entry['status']
                            break
                    
                    # Write back
                    with open(history_file, 'w', encoding='utf-8') as f:
                        for current_entry in current_entries:
                            f.write(json.dumps(current_entry) + "\n")
            else:
                print("No datasets found.")
        else:
            # Dataset-specific batch status (existing logic)
            history_file = os.path.join(cfg.reports_dir, "batch_history.jsonl")
            if os.path.exists(history_file):
                print("Batch Job History (refreshed from API):")
                updated_entries = []
                with open(history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        # Refresh status from API
                        current_status = bm.check_status(entry['batch_id'])
                        if current_status != entry['status']:
                            entry['status'] = current_status
                            print(f"- {entry['batch_id']}: {entry['status']} ({entry['type']}) - {entry['timestamp']} [UPDATED]")
                        else:
                            print(f"- {entry['batch_id']}: {entry['status']} ({entry['type']}) - {entry['timestamp']}")
                        updated_entries.append(entry)
                
                # Update the history file with refreshed statuses
                with open(history_file, 'w', encoding='utf-8') as f:
                    for entry in updated_entries:
                        f.write(json.dumps(entry) + "\n")
            else:
                print("No batch history found.")
        return

    if args.batch_cancel:
        bm = BatchManager()
        success = bm.cancel_batch(args.batch_cancel)
        if success:
            print(f"Successfully cancelled batch job: {args.batch_cancel}")
        else:
            print(f"Failed to cancel batch job: {args.batch_cancel}")
        return

    if args.batch_fetch:
        bm = BatchManager()
        # Get job details to determine type
        try:
            job = bm.client.batches.get(name=args.batch_fetch)
            # Check batch history to determine job type
            job_type = None
            history_file = bm.history_file
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("batch_id") == args.batch_fetch:
                                job_type = entry.get("type")
                                break
                        except:
                            continue
            
            if job_type == "query_gen":
                generate_queries_from_corpus(batch_fetch_id=args.batch_fetch)
            elif job_type == "qrels_gen":
                generate_qrels(batch_fetch_id=args.batch_fetch)
            else:
                print(f"Unknown job type '{job_type}' for batch {args.batch_fetch}")
                print("Please specify the operation type explicitly:")
                print("  --generate-queries --batch-fetch <id>")
                print("  --generate-qrels --batch-fetch <id>")
        except Exception as e:
            print(f"Error fetching batch job {args.batch_fetch}: {e}")
        return
    if args.all:
        if args.batch_submit or args.batch_fetch:
            print("Error: --all cannot be used with batch modes. Please run steps individually.")
            return

        print("Starting complete RAG benchmark pipeline...")
        result = prepare_corpus_from_pdfs_wrapper()
        if result['chunks_created'] == 0:
            print("ERROR: No chunks created from PDFs. Please ensure PDFs are present in the pdf_dir.")
            return
        if not generate_queries_from_corpus():
            return
        if not generate_qrels():
            return
        # Continue to evaluation section below
        
    # Handle initialization and evaluation
    if args.initialize or args.evaluate or args.all:
        
        # --- PATH 1: Initialization Only ---
        # If we are ONLY initializing, we just need the corpus.
        if args.initialize and not args.evaluate and not args.all:
            if not os.path.exists(cfg.corpus_file):
                raise FileNotFoundError(f"Corpus file not found: {cfg.corpus_file}")
            
            print("Loading corpus for initialization...")
            corpus = load_corpus_from_file(cfg.corpus_file)
            
            # Initialize collections and collect timing data
            timing_results = []
            for model_cfg in cfg.embedding_models:
                model_name = model_cfg["model_name"]
                collection_name = model_cfg["collection_name"]
                timing_data = initialize_collection(corpus, model_name, collection_name)
                if timing_data and isinstance(timing_data, dict):
                    timing_results.append((model_name, timing_data))
            
            # Save timing data to file for later use
            if timing_results:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                timing_file = os.path.join(cfg.reports_dir, f"timing_data_{timestamp}.json")
                
                with open(timing_file, 'w', encoding='utf-8') as f:
                    # Convert to dict format for JSON
                    timing_dict = {model_name: timing_data for model_name, timing_data in timing_results}
                    json.dump(timing_dict, f, indent=2)
                print(f"Timing data saved to {timing_file}")
            
            print("\nInitialization completed successfully.")
            return

        # --- PATH 2: Evaluation (or All) ---
        # Requires all files (Corpus, Queries, Qrels)
        
        # Validate required files
        for file_path in [cfg.corpus_file, cfg.queries_file, cfg.qrels_file]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        print("Starting embedding model evaluation...")
        print(f"Configuration: k={cfg.k}, show_progress={cfg.show_progress_bar}, reinit_collections={cfg.reinitialize_collections}")
        
        # Load ground truth data ONCE using refactored function
        queries, corpus, relevant_docs = load_ground_truth(cfg.corpus_file, cfg.queries_file, cfg.qrels_file)
        
        # Load existing timing data if available
        timing_results = []
        timing_by_model = {}
        # Find the most recent timing data file
        import glob
        timing_files = glob.glob(os.path.join(cfg.reports_dir, "timing_data_*.json"))
        if timing_files:
            # Sort by modification time, get the most recent
            latest_timing_file = max(timing_files, key=os.path.getmtime)
            try:
                with open(latest_timing_file, 'r', encoding='utf-8') as f:
                    timing_dict = json.load(f)
                    timing_results = [(model_name, timing_data) for model_name, timing_data in timing_dict.items()]
                    timing_by_model = {
                        model_name: timing_data if isinstance(timing_data, dict) else {}
                        for model_name, timing_data in timing_dict.items()
                    }
                print(f"Loaded timing data from {latest_timing_file}")
            except Exception as e:
                print(f"Warning: Could not load timing data from {latest_timing_file}: {e}")
        else:
            print("No timing data files found.")
        
        # Initialize containers (timing_results may already have data)
        model_results = []
        
        # Process each model ONCE
        for model_cfg in cfg.embedding_models:
            model_name = model_cfg["model_name"]
            collection_name = model_cfg["collection_name"]
            
            # Initialize if requested (args.all or (args.initialize AND args.evaluate))
            # Note: Pure args.initialize is handled in PATH 1 above
            if args.initialize or args.all:
                timing_data = initialize_collection(corpus, model_name, collection_name)
                if timing_data and isinstance(timing_data, dict):
                    merged_timing = timing_by_model.get(model_name, {})
                    merged_timing.update(timing_data)
                    timing_by_model[model_name] = merged_timing
            
            # Evaluate if requested
            if args.evaluate or args.all:
                # Evaluate model
                metrics, retrieval_timing = evaluate_with_chromadb(
                    queries, corpus, relevant_docs, model_name, collection_name
                )
                model_results.append((model_name, *metrics))
                merged_timing = timing_by_model.get(model_name, {})
                merged_timing.update(retrieval_timing)
                merged_timing.setdefault("docs_processed", len(corpus))
                timing_by_model[model_name] = merged_timing

        timing_results = [(model_name, timing_data) for model_name, timing_data in timing_by_model.items()]
        
        # Save updated timing data to file (including any empty entries added during evaluation)
        if timing_results:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timing_file = os.path.join(cfg.reports_dir, f"timing_data_{timestamp}.json")
            
            with open(timing_file, 'w', encoding='utf-8') as f:
                json.dump(timing_by_model, f, indent=2)
            print(f"Updated timing data saved to {timing_file}")
        
        # Display and generate report ONLY ONCE
        if model_results:
            print_results_summary(
                model_results=model_results,
                queries=queries,
                corpus=corpus,
                relevant_docs=relevant_docs,
                timing_results=timing_results,
                dataset_name=cfg.current_dataset,
                output_dir=cfg.reports_dir,
                save_raw_results=True
            )
            report_files = generate_benchmark_report(model_results, queries, corpus, relevant_docs, timing_results, output_dir=cfg.reports_dir)
            print_report_info(report_files)
    
    print("\nBenchmark completed!")


if __name__ == "__main__":
    main()
