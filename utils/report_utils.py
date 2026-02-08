import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

import matplotlib.pyplot as plt
import numpy as np
import config as cfg
import datetime
from tabulate import tabulate
import os
import textwrap
import json

# Import SentenceTransformer for model information
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    print("Warning: sentence-transformers not available. Model dimensions will show as 'N/A'")

import subprocess
import chromadb

METRIC_LABELS = {
    "map": "MAP",
    "recall": "Recall",
    "precision": "Precision",
    "ndcg": "NDCG",
    "mrr": "MRR",
    "hit_rate": "Success/Hit Rate",
}

METRIC_HEADERS = {
    "map": "MAP",
    "recall": "Recall",
    "precision": "Precision",
    "ndcg": "NDCG",
    "mrr": "MRR",
    "hit_rate": "Success",
}

METRIC_DOCS = {
    "map": ("Mean Average Precision at rank k", "Ranking quality"),
    "recall": ("Proportion of relevant docs in top k", "Coverage"),
    "precision": ("Proportion of relevant docs among retrieved", "Accuracy"),
    "ndcg": ("Normalized Discounted Cumulative Gain", "Ranking with position bias"),
    "mrr": ("Mean Reciprocal Rank", "First relevant position"),
    "hit_rate": ("Fraction of queries with at least one relevant doc in top k", "Query-level success"),
}


def get_enabled_metric_names():
    """Return enabled metric keys in evaluate_with_chromadb tuple order."""
    enabled = []
    if cfg.compute_map:
        enabled.append("map")
    if cfg.compute_recall:
        enabled.append("recall")
    if cfg.compute_precision:
        enabled.append("precision")
    if cfg.compute_ndcg:
        enabled.append("ndcg")
    if cfg.compute_mrr:
        enabled.append("mrr")
    if getattr(cfg, "compute_hit_rate", False):
        enabled.append("hit_rate")
    return enabled


def get_metric_indices():
    """Map metric key -> tuple index in model_results entries (index 0 is model name)."""
    return {metric: idx for idx, metric in enumerate(get_enabled_metric_names(), start=1)}


def get_primary_metric_key():
    """Pick primary metric for sorting/summary in priority order."""
    metric_indices = get_metric_indices()
    for metric in ("map", "ndcg", "mrr", "recall", "precision", "hit_rate"):
        if metric in metric_indices:
            return metric
    return None


def save_raw_results_json(dataset_name, model_results, timing_data, corpus, queries, relevant_docs, output_path):
    """
    Save structured evaluation results for aggregate analysis.
    
    Args:
        dataset_name: Name of the dataset
        model_results: List of tuples (model_name, enabled_metrics...) where enabled_metrics
                      are in order: MAP, Recall, Precision, NDCG, MRR (only enabled ones included)
        timing_data: Dict with timing information per model
        corpus: Dict of document chunks
        queries: Dict of queries
        relevant_docs: Dict of relevance judgments
        output_path: Path to save JSON file
    """
    # Compute corpus/query/relevance statistics
    chunk_lengths = [len(text.split()) for text in corpus.values()]
    query_lengths = [len(text.split()) for text in queries.values()]
    relevance_distribution = [len(v) for v in relevant_docs.values()]

    total_chunks = len(corpus)
    total_queries = len(queries)
    total_qrels = sum(relevance_distribution)

    pdf_files = [f for f in os.listdir(cfg.pdf_dir) if f.lower().endswith('.pdf')] if os.path.exists(cfg.pdf_dir) else []
    pdf_count = len(pdf_files)

    avg_chunks_per_pdf = round(total_chunks / pdf_count, 1) if pdf_count > 0 else 0
    avg_qrels_per_query = round(total_qrels / total_queries, 2) if total_queries > 0 else 0

    coverage_ratio = (total_qrels / total_chunks * 100) if total_chunks > 0 else 0.0

    def _safe_stat(values, func, default=0.0):
        return float(func(values)) if values else float(default)
    
    # Build results structure
    results_dict = {
        "dataset": dataset_name,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "config": {
            "k": cfg.k,
            "chunk_size": cfg.chunk_size,
            "chunk_overlap": cfg.chunk_overlap,
            "llm_model": cfg.llm_model,
            "candidate_pool_size": cfg.candidate_pool_size,
            "document_batch_size": cfg.document_batch_size,
            "reinitialize_collections": cfg.reinitialize_collections,
            "embedding_models": [
                {
                    "model_name": model_cfg["model_name"],
                    "collection_name": model_cfg["collection_name"]
                }
                for model_cfg in cfg.embedding_models
            ],
            "metric_flags": {
                "compute_map": cfg.compute_map,
                "compute_recall": cfg.compute_recall,
                "compute_precision": cfg.compute_precision,
                "compute_ndcg": cfg.compute_ndcg,
                "compute_mrr": cfg.compute_mrr,
                "compute_hit_rate": getattr(cfg, "compute_hit_rate", False)
            }
        },
        "models": {},
        "corpus_stats": {
            "total_pdfs": pdf_count,
            "total_chunks": total_chunks,
            "avg_chunks_per_pdf": avg_chunks_per_pdf,
            "total_queries": total_queries,
            "total_qrels": total_qrels,
            "avg_qrels_per_query": avg_qrels_per_query
        },
        "corpus_characteristics": {
            "avg_chunk_length": _safe_stat(chunk_lengths, np.mean),
            "median_chunk_length": _safe_stat(chunk_lengths, np.median),
            "min_chunk_length": _safe_stat(chunk_lengths, min),
            "max_chunk_length": _safe_stat(chunk_lengths, max),
            "std_chunk_length": _safe_stat(chunk_lengths, np.std)
        },
        "query_characteristics": {
            "total_queries": total_queries,
            "avg_query_length": _safe_stat(query_lengths, np.mean),
            "median_query_length": _safe_stat(query_lengths, np.median),
            "min_query_length": _safe_stat(query_lengths, min),
            "max_query_length": _safe_stat(query_lengths, max),
            "std_query_length": _safe_stat(query_lengths, np.std)
        },
        "relevance_characteristics": {
            "total_relevance_judgments": total_qrels,
            "avg_relevant_docs_per_query": _safe_stat(relevance_distribution, np.mean),
            "median_relevant_docs_per_query": _safe_stat(relevance_distribution, np.median),
            "min_relevant_docs_per_query": _safe_stat(relevance_distribution, min),
            "max_relevant_docs_per_query": _safe_stat(relevance_distribution, max),
            "coverage_ratio": float(coverage_ratio)
        },
        "representative_queries": [
            {
                "query_id": qid,
                "query_text": qtext,
                "relevant_docs": len(relevant_docs.get(qid, []))
            }
            for qid, qtext in list(queries.items())[:5]
        ]
    }
    
    # Build metric index mapping based on enabled metrics
    metric_indices = get_metric_indices()

    # Process model results
    for result in model_results:
        model_name = result[0]
        metrics = {
            metric_name: float(result[metric_indices[metric_name]])
            for metric_name in get_enabled_metric_names()
        }
        
        # Get timing data if available
        timing = {}
        if timing_data and model_name in timing_data:
            timing = timing_data[model_name]
        
        results_dict["models"][model_name] = {
            "metrics": metrics,
            "timing": timing
        }
    
    # Save to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Raw Results] Saved to: {output_path}")

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, timing_results=None, output_dir="reports", dataset_name=None, save_raw_results=True):
    """Generate a comprehensive benchmark report suitable for a conference paper."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract dataset name from output_dir if not provided
    if dataset_name is None:
        # Extract dataset name from path like "datasets/education/reports"
        if "datasets" in output_dir:
            path_parts = output_dir.split(os.sep)
            datasets_idx = path_parts.index("datasets") if "datasets" in path_parts else -1
            if datasets_idx >= 0 and datasets_idx + 1 < len(path_parts):
                dataset_name = path_parts[datasets_idx + 1]
            else:
                dataset_name = "unknown"
        else:
            dataset_name = "default"

    # Check if model_results is empty
    if not model_results:
        raise ValueError("No model results provided")
    
    # Debug: Check if timing data is received
    # print(f"DEBUG: timing_results received: {timing_results}")
    # if timing_results:
    #     print(f"DEBUG: Number of timing entries: {len(timing_results)}")
    #     for model_name, timing_data in timing_results:
    #         print(f"DEBUG: {model_name} - {timing_data}")

    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"{dataset_name}_benchmark_report_{timestamp}.md")
    
    # Sort models by primary metric for easier comparison (if any results exist)
    metric_indices = get_metric_indices()
    primary_metric = get_primary_metric_key()
    if model_results and primary_metric:
        sort_idx = metric_indices[primary_metric]
        sorted_results = sorted(model_results, key=lambda x: x[sort_idx], reverse=True)
    else:
        sorted_results = model_results
    
    # Fallback timing for evaluation-only runs
    # If user only did --evaluate, timing_results is [], so timing is omitted.
    if timing_results is not None and not timing_results:
        print("[Warning] No timing data available for report generation")
        print("   To include timing analysis, run: python simple_rag_benchmark_pipeline.py --initialize")
        print("   Report will be generated without timing performance section")
        timing_results = None  # Clear it completely
    
    # Calculate additional statistics
    chunk_lengths = [len(text.split()) for text in corpus.values()]
    query_lengths = [len(text.split()) for text in queries.values()]
    relevance_distribution = [len(v) for v in relevant_docs.values()]
    
    # Count source PDF documents
    pdf_count = 0
    if os.path.exists(cfg.pdf_dir):
        pdf_count = len([f for f in os.listdir(cfg.pdf_dir) if f.lower().endswith('.pdf')])
    
    # Count document chunks from ChromaDB
    chunk_count = 0
    try:
        client = chromadb.PersistentClient(path=cfg.chroma_db_path)
        collection_name = cfg.embedding_models[0]["collection_name"]
        collection = client.get_collection(collection_name)
        chunk_count = collection.count()
    except Exception as e:
        print(f"Warning: Could not get chunk count from ChromaDB: {e}. Using corpus length.")
        chunk_count = len(corpus)
    
    # Generate visualizations first so we can reference them in the report
    viz_files = {}
    try:
        viz_files = generate_visualizations(sorted_results, output_dir, timestamp, dataset_name)
        # Generate additional statistics visualizations
        viz_files.update(generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, chunk_count, output_dir, timestamp, dataset_name))
        print(f"Generated {len(viz_files)} visualizations")
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Start writing the report
    with open(report_file, "w", encoding="utf-8") as f:
        # Write report header
        f.write(f"# RAG Retrieval Benchmark: {dataset_name.title()} Dataset Evaluation\n\n")
        f.write(f"**Dataset:** {dataset_name.title()}\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Abstract
        f.write("## Abstract\n\n")
        f.write(f"This paper presents a systematic evaluation of embedding models on the {dataset_name} dataset ")
        f.write("within Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline ")
        f.write("that processes PDF documents, generates synthetic queries using large language models, ")
        f.write("and evaluates retrieval performance across multiple embedding models using standardized ")
        f.write("information retrieval metrics. Our framework provides researchers and practitioners ")
        f.write("with a reproducible methodology for selecting optimal embedding models for their ")
        f.write("specific document collections and use cases.\n\n")
        
        # Executive summary
        f.write("## Executive Summary\n\n")
        f.write(f"This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG) on the {dataset_name} dataset. ")
        f.write("The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. ")
        f.write(f"The benchmark used **{pdf_count} PDF document(s)** that were processed into **{chunk_count} document chunks** and **{len(queries)} queries** with **{sum(len(v) for v in relevant_docs.values())} relevant document mappings**.\n\n")
        
        # Best model highlight
        if sorted_results:  # Check if there are any results
            best_model = sorted_results[0]
            f.write(f"**Best performing model:** `{best_model[0]}`\n")
            
            # Use dynamic indexing based on enabled metrics
            for metric_name in get_enabled_metric_names():
                metric_label = METRIC_LABELS[metric_name]
                f.write(f"* {metric_label}@{cfg.k}: **{best_model[metric_indices[metric_name]]:.4f}**\n")
            f.write("\n")
        else:
            f.write("**No model results available for comparison.**\n\n")
        
        # Methodology
        f.write("## Methodology\n\n")
        f.write("### Automated Pipeline Overview\n\n")
        f.write("Our evaluation framework consists of five main stages:\n\n")
        f.write("1. **PDF Processing**: Document ingestion and chunking\n")
        f.write("2. **Corpus Generation**: Creation of standardized document chunks\n")
        f.write("3. **Query Generation**: LLM-assisted query synthesis\n")
        f.write("4. **Relevance Assessment**: Automated qrels generation\n")
        f.write("5. **Embedding Evaluation**: Multi-model performance comparison\n\n")
        
        f.write("### Document Processing Pipeline\n\n")
        f.write("#### PDF Extraction and Chunking\n\n")
        f.write(f"- **Source PDF documents**: {pdf_count} file(s) from `{cfg.pdf_dir}` directory\n")
        f.write(f"- **Chunking strategy**: Recursive character text splitting\n")
        f.write(f"- **Chunk size**: {cfg.chunk_size} characters\n")
        f.write(f"- **Chunk overlap**: {cfg.chunk_overlap} characters\n")
        f.write(f"- **Total chunks generated**: {chunk_count}\n\n")
        
        f.write("The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to ")
        f.write("maintain semantic coherence while ensuring manageable chunk sizes for embedding models.\n\n")
        
        f.write("#### Query Generation Process\n\n")
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
        f.write(f"## {dataset_name.title()} Dataset Statistics\n\n")
        
        # Corpus statistics table
        f.write("#### Corpus Characteristics\n\n")
        corpus_stats = [
            ["Source PDF Documents", f"{pdf_count}"],
            ["Total Document Chunks", f"{chunk_count:,}"],
            ["Average Chunk Length (words)", f"{np.mean(chunk_lengths):.1f}"],
            ["Median Chunk Length (words)", f"{np.median(chunk_lengths):.1f}"],
            ["Min Chunk Length (words)", f"{min(chunk_lengths)}"],
            ["Max Chunk Length (words)", f"{max(chunk_lengths)}"],
            ["Standard Deviation", f"{np.std(chunk_lengths):.1f}"]
        ]
        f.write(tabulate(corpus_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Corpus Characteristics Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Source PDF Documents**: Number of original PDF files processed\n")
        f.write("- **Total Document Chunks**: Number of text chunks created from PDFs\n")
        f.write("- **Average Chunk Length**: Mean number of words per chunk\n")
        f.write("- **Median Chunk Length**: Middle value of chunk lengths (resistant to outliers)\n")
        f.write("- **Min/Max Chunk Length**: Range of chunk sizes\n")
        f.write("- **Standard Deviation**: Variability in chunk lengths\n\n")
        
        f.write("**How to interpret:**\n")
        f.write("- **High variability** (large std dev) indicates inconsistent chunking\n")
        f.write("- **Very short chunks** may lose context, very long chunks may be noisy\n")
        f.write("- **Chunk count** affects retrieval efficiency and memory usage\n\n")
        
        # Query statistics table
        f.write("#### Query Characteristics\n\n")
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
        
        f.write("**Table: Query Characteristics Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Total Queries**: Number of evaluation queries generated\n")
        f.write("- **Average Query Length**: Mean number of words per query\n")
        f.write("- **Median Query Length**: Middle value of query lengths\n")
        f.write("- **Min/Max Query Length**: Range of query lengths\n")
        f.write("- **Standard Deviation**: Variability in query lengths\n\n")
        
        f.write("**How to interpret:**\n")
        f.write("- **Query length** affects retrieval difficulty (longer = more specific)\n")
        f.write("- **High variability** indicates diverse query types\n")
        f.write("- **Query count** determines statistical power of evaluation\n\n")
        
        # Relevance statistics
        f.write("#### Relevance Distribution\n\n")
        relevance_stats = [
            ["Total Relevance Judgments", f"{sum(relevance_distribution)}"],
            ["Average Relevant Docs per Query", f"{np.mean(relevance_distribution):.1f}"],
            ["Median Relevant Docs per Query", f"{np.median(relevance_distribution):.1f}"],
            ["Min Relevant Docs", f"{min(relevance_distribution)}"],
            ["Max Relevant Docs", f"{max(relevance_distribution)}"],
            ["Coverage Ratio", f"{sum(relevance_distribution)/chunk_count*100:.2f}%"]
        ]
        f.write(tabulate(relevance_stats, headers=["Metric", "Value"], tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Relevance Distribution Summary**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Total Relevance Judgments**: Total number of relevant document-query pairs\n")
        f.write("- **Average Relevant Docs per Query**: Mean number of relevant documents per query\n")
        f.write("- **Median Relevant Docs per Query**: Middle value of relevant docs per query\n")
        f.write("- **Min/Max Relevant Docs**: Range of relevant documents per query\n")
        f.write("- **Coverage Ratio**: Percentage of corpus that is relevant to queries\n\n")
        
        f.write("**How to interpret:**\n")
        f.write("- **High average relevant docs** = easier retrieval task\n")
        f.write("- **Low coverage ratio** = sparse relevance (harder evaluation)\n")
        f.write("- **High variability** indicates inconsistent query difficulty\n\n")
        
        # Benchmark configuration
        f.write("## Experimental Setup\n\n")
        f.write("### Evaluation Framework\n\n")
        f.write("- **Vector Database**: ChromaDB\n")
        f.write("- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator\n")
        f.write(f"- **Retrieval Depth (k)**: {cfg.k}\n")
        f.write(f"- **Batch Size**: {cfg.document_batch_size}\n")
        f.write(f"- **Collection Reinitialization**: {cfg.reinitialize_collections}\n\n")
        
        f.write("### Evaluated Models\n\n")
        model_info_table = []
        for model_cfg in cfg.embedding_models:
            if SENTENCE_TRANSFORMER_AVAILABLE:
                try:
                    model = SentenceTransformer(model_cfg["model_name"])
                    dimensions = model.get_sentence_embedding_dimension()
                    max_seq_length = getattr(model, 'max_seq_length', 'N/A')
                    model_info_table.append([
                        model_cfg["model_name"],
                        model_cfg["collection_name"],
                        str(dimensions),
                        "Sentence Transformer"
                    ])
                except Exception as e:
                    print(f"Warning: Could not load model info for {model_cfg['model_name']}: {e}")
                    model_info_table.append([
                        model_cfg["model_name"],
                        model_cfg["collection_name"],
                        "Error loading",
                        "N/A"
                    ])
            else:
                model_info_table.append([
                    model_cfg["model_name"],
                    model_cfg["collection_name"],
                    "N/A (import failed)",
                    "N/A"
                ])
        
        f.write(tabulate(model_info_table, 
                        headers=["Model Name", "Collection", "Dimensions", "Type"], 
                        tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Evaluated Embedding Models**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Model Name**: Full model identifier from Hugging Face or provider\n")
        f.write("- **Collection**: ChromaDB collection name for this model\n")
        f.write("- **Dimensions**: Embedding vector dimensionality\n")
        f.write("- **Type**: Model architecture or framework\n\n")
        
        f.write("**How to interpret:**\n")
        f.write("- **Higher dimensions** generally capture more semantic nuance\n")
        f.write("- **Different architectures** have different strengths/weaknesses\n")
        f.write("- **Collection names** ensure isolated evaluation per model\n\n")
        
        f.write("### Evaluation Metrics\n\n")
        metrics_desc = []
        for metric_name in get_enabled_metric_names():
            metric_header = METRIC_HEADERS[metric_name]
            desc, measures = METRIC_DOCS[metric_name]
            metrics_desc.append([f"{metric_header}@k", desc, measures])
        
        f.write(tabulate(metrics_desc, headers=["Metric", "Description", "Measures"], tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Evaluation Metrics Overview**\n\n")
        f.write("**Metric Details:**\n")
        metric_details = {
            "map": "Mean Average Precision - balances precision and recall across ranks",
            "recall": "Coverage - fraction of relevant docs retrieved in top k",
            "precision": "Accuracy - fraction of retrieved docs that are relevant",
            "ndcg": "Position-aware ranking quality with logarithmic discounting",
            "mrr": "First relevant position - emphasizes finding relevant docs early",
            "hit_rate": "Success@k / Hit Rate@k - fraction of queries with at least one relevant hit in top k",
        }
        for metric_name in get_enabled_metric_names():
            f.write(f"- **{METRIC_HEADERS[metric_name]}@k**: {metric_details[metric_name]}\n")
        f.write("\n")
        
        f.write("**When to use each metric:**\n")
        metric_use_cases = {
            "map": "Overall ranking quality for information retrieval",
            "recall": "Ensuring comprehensive coverage of relevant content",
            "precision": "Minimizing irrelevant results in recommendations",
            "ndcg": "Search engine ranking with position bias",
            "mrr": "Question-answering where first relevant result matters",
            "hit_rate": "Measuring query-level success rate when at least one relevant hit is enough",
        }
        for metric_name in get_enabled_metric_names():
            f.write(f"- **{METRIC_HEADERS[metric_name]}**: {metric_use_cases[metric_name]}\n")
        f.write("\n")
        
        # Representative Query Examples
        f.write("### Representative Query Examples\n\n")
        headers = ["Query ID", "Query Text", "# Relevant Docs"]
        rep_rows = []
        for qid in list(queries)[:5]:
            # wrap long IDs at ~20 chars with HTML line breaks for clean table layout
            wrapped_qid = "<br/>".join(textwrap.wrap(qid, width=20))
            rep_rows.append([wrapped_qid, queries[qid], len(relevant_docs[qid])])
        f.write(tabulate(rep_rows, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Representative Query Examples**\n\n")
        f.write("**Column Explanations:**\n")
        f.write("- **Query ID**: Unique identifier for each query\n")
        f.write("- **Query Text**: The actual query text used for retrieval\n")
        f.write("- **# Relevant Docs**: Number of ground truth relevant documents\n\n")
        
        f.write("**How to interpret:**\n")
        f.write("- **Query diversity** shows the range of information needs tested\n")
        f.write("- **Relevant docs count** indicates query specificity (fewer = more specific)\n")
        f.write("- **Query length** may correlate with retrieval difficulty\n\n")
        
        # Results section
        f.write("## Results\n\n")
        
        # Comparative results table
        f.write("### Model Performance Comparison\n\n")
        
        # Prepare headers based on which metrics are computed
        headers = ["Model"]
        for metric_name in get_enabled_metric_names():
            headers.append(f"{METRIC_HEADERS[metric_name]}@{cfg.k}")
        
        # Prepare table data
        table_data = []
        for result in sorted_results:
            short_name = result[0].split('/')[-1]  # Use short name for better table formatting
            row = [short_name]  # Model name
            for metric_name in get_enabled_metric_names():
                row.append(f"{result[metric_indices[metric_name]]:.4f}")
            
            table_data.append(row)
        
        f.write("**Table: Comprehensive Model Performance Results**\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt="pipe"))
        f.write("\n\n")
        
        f.write("**Table: Model Performance Results Explanation**\n\n")
        f.write("**Column Explanations:**\n")
        f.write(f"- **Model**: Embedding model name (shortened for readability)\n")
        column_explanations = {
            "map": f"Mean Average Precision at rank {cfg.k}",
            "recall": f"Fraction of relevant documents retrieved in top {cfg.k}",
            "precision": "Fraction of retrieved documents that are relevant",
            "ndcg": f"Normalized Discounted Cumulative Gain at rank {cfg.k}",
            "mrr": f"Mean Reciprocal Rank at rank {cfg.k}",
            "hit_rate": f"Success@{cfg.k} / Hit Rate@{cfg.k}: fraction of queries with >=1 relevant retrieved",
        }
        for metric_name in get_enabled_metric_names():
            f.write(f"- **{METRIC_HEADERS[metric_name]}@{cfg.k}**: {column_explanations[metric_name]}\n")
        f.write("\n")
        
        f.write("**How to interpret the results:**\n")
        f.write("- **Higher scores** = better retrieval performance\n")
        interpret_bullets = {
            "map": "MAP balances ranking quality and coverage",
            "recall": "Recall shows how comprehensive the retrieval is",
            "precision": "Precision shows how accurate the retrieval is",
            "ndcg": "NDCG rewards relevant documents appearing early",
            "mrr": "MRR emphasizes finding the first relevant result",
            "hit_rate": "Success/Hit Rate captures whether queries get at least one relevant hit",
        }
        for metric_name in get_enabled_metric_names():
            f.write(f"- **{METRIC_HEADERS[metric_name]}**: {interpret_bullets[metric_name]}\n")
        f.write("\n")
        
        # Performance analysis
        f.write("### Performance Analysis\n\n")
        if len(sorted_results) > 1:
            best_model = sorted_results[0]
            worst_model = sorted_results[-1]
            
            # Get the primary metric name and value dynamically
            primary_metric_name = None
            primary_metric_value_best = None
            primary_metric_value_worst = None
            
            if primary_metric:
                primary_metric_name = f"{METRIC_LABELS[primary_metric]}@{cfg.k}"
                primary_metric_idx = metric_indices[primary_metric]
                primary_metric_value_best = best_model[primary_metric_idx]
                primary_metric_value_worst = worst_model[primary_metric_idx]
            
            if primary_metric_name and primary_metric_value_best is not None:
                f.write(f"The evaluation reveals significant performance variations across embedding models. ")
                f.write(f"**{best_model[0]}** achieved the highest {primary_metric_name} score of {primary_metric_value_best:.4f}, ")
                f.write(f"while **{worst_model[0]}** scored {primary_metric_value_worst:.4f}, representing a ")
                f.write(f"**{((primary_metric_value_best - primary_metric_value_worst) / primary_metric_value_worst * 100):.1f}% improvement**.\n\n")
            
            # Correlation analysis between metrics - only if both MAP and Recall are enabled
            if "map" in metric_indices and "recall" in metric_indices and len(sorted_results) > 0:
                map_index = metric_indices["map"]
                recall_index = metric_indices["recall"]
                if all(len(result) > max(map_index, recall_index) for result in sorted_results):
                    map_scores = [r[map_index] for r in sorted_results]
                    recall_scores = [r[recall_index] for r in sorted_results]
                    correlation = np.corrcoef(map_scores, recall_scores)[0, 1]
                    f.write(f"**MAP-Recall Correlation**: {correlation:.3f} ")
                    f.write("(indicates how well ranking quality correlates with coverage)\n\n")
        
        # Add visualizations section if there are any
        if viz_files:
            f.write("### Visual Analysis\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("#### 6.3.1 Overall Performance Comparison\n\n")
                f.write(f"![Model Performance Overview]({os.path.basename(viz_files['overview'])})\n\n")
                f.write("**Figure: Comprehensive Model Performance Comparison**\n\n")
                f.write(f"This bar chart compares all embedding models across all evaluation metrics at k={cfg.k}. ")
                f.write("Each model has a group of bars showing its performance on different metrics.\n\n")
                f.write("**How to interpret:**\n")
                f.write("- **Taller bars** indicate better performance on that metric\n")
                f.write("- **Consistent height across metrics** shows well-rounded models\n")
                f.write("- **Spiky patterns** reveal specialized models (good at some metrics, poor at others)\n")
                f.write("- **Model grouping** allows direct comparison between models\n\n")
                f.write("**Why it matters:** Identifies models with balanced capabilities vs. specialized models, ")
                f.write("helping you choose based on your specific requirements.\n\n")
            
            # Add corpus statistics visualizations
            if 'corpus_stats' in viz_files:
                f.write("#### 6.3.2 Dataset Characteristics\n\n")
                f.write(f"![Corpus Statistics]({os.path.basename(viz_files['corpus_stats'])})\n\n")
                f.write("**Figure: Dataset Characteristics and Distributions**\n\n")
                f.write("This figure contains four subplots showing the statistical properties of your evaluation dataset:\n\n")
                f.write("**Top-left: Chunk Length Distribution**\n")
                f.write("- Shows how document chunk sizes vary across the corpus\n")
                f.write("- **Normal distribution** indicates consistent chunking\n")
                f.write("- **Skewed distribution** suggests chunking strategy issues\n\n")
                
                f.write("**Top-right: Query Length Distribution**\n")
                f.write("- Shows the diversity of query lengths in your evaluation set\n")
                f.write("- **Wide range** indicates varied information needs\n")
                f.write("- **Narrow range** suggests similar query complexity\n\n")
                
                f.write("**Bottom-left: Relevance Distribution**\n")
                f.write("- Shows how many relevant documents exist per query\n")
                f.write("- **Right-skewed** = most queries have few relevant docs (harder task)\n")
                f.write("- **Left-skewed** = most queries have many relevant docs (easier task)\n\n")
                
                f.write("**Bottom-right: Summary Statistics Table**\n")
                f.write("- Key metrics for chunk lengths, query lengths, and relevance\n")
                f.write("- Helps assess dataset quality and evaluation difficulty\n\n")
                
                f.write("**Why it matters:** Understanding your dataset characteristics helps interpret ")
                f.write("model performance results and identify potential evaluation biases.\n\n")
            
            # Add individual metric charts
            f.write("#### 6.3.3 Individual Metric Analysis\n\n")
            f.write("The following charts provide detailed performance breakdowns for each evaluation metric. ")
            f.write("Each chart focuses on a single metric to enable precise model comparisons.\n\n")
            
            for metric_name, file_path in viz_files.items():
                if metric_name not in ['overview', 'corpus_stats']:
                    metric_label = METRIC_LABELS.get(metric_name, metric_name)
                    f.write(f"##### {metric_label}@{cfg.k} Performance\n\n")
                    f.write(f"![{metric_label} Comparison]({os.path.basename(file_path)})\n\n")
                    
                    # Add metric-specific explanations
                    if metric_name.lower() == 'map':
                        f.write("**MAP@k (Mean Average Precision)**: Measures ranking quality by averaging precision ")
                        f.write("at each relevant document position. Rewards models that rank relevant documents highly.\n\n")
                        f.write("**Interpretation**: Higher values indicate better overall ranking performance. ")
                        f.write("Useful for general information retrieval tasks.\n\n")
                    
                    elif metric_name.lower() == 'recall':
                        f.write("**Recall@k**: Measures the fraction of relevant documents that are successfully retrieved ")
                        f.write("in the top k results. Focuses on coverage of relevant content.\n\n")
                        f.write("**Interpretation**: Higher values indicate more comprehensive retrieval. ")
                        f.write("Important when missing relevant information is costly.\n\n")
                    
                    elif metric_name.lower() == 'precision':
                        f.write("**Precision@k**: Measures the fraction of retrieved documents that are actually relevant. ")
                        f.write("Focuses on accuracy of the retrieved results.\n\n")
                        f.write("**Interpretation**: Higher values indicate fewer irrelevant results. ")
                        f.write("Important when irrelevant information reduces user satisfaction.\n\n")
                    
                    elif metric_name.lower() == 'ndcg':
                        f.write("**NDCG@k (Normalized Discounted Cumulative Gain)**: Measures ranking quality with ")
                        f.write("position-based discounting. Relevant documents are more valuable when ranked higher.\n\n")
                        f.write("**Interpretation**: Higher values indicate better ranking with proper position weighting. ")
                        f.write("Standard metric for search engine evaluation.\n\n")
                    
                    elif metric_name.lower() == 'mrr':
                        f.write("**MRR@k (Mean Reciprocal Rank)**: Measures how early the first relevant document ")
                        f.write("appears in the ranked results. Emphasizes finding relevant information quickly.\n\n")
                        f.write("**Interpretation**: Higher values indicate faster discovery of relevant content. ")
                        f.write("Critical for question-answering and single-answer scenarios.\n\n")
                    
                    elif metric_name.lower() == 'hit_rate':
                        f.write("**Success@k / Hit Rate@k**: Measures the fraction of queries where at least one ")
                        f.write("relevant document appears in top-k results.\n\n")
                        f.write("**Interpretation**: Higher values indicate more queries are successfully served. ")
                        f.write("Useful when any relevant hit is sufficient for a good user experience.\n\n")
        
        # Statistical significance analysis
        if len(model_results) >= 2:
            f.write("### Statistical Significance Analysis\n\n")
            f.write("This section helps determine whether observed performance differences between models ")
            f.write("are meaningful or could occur by random chance. While formal statistical tests ")
            f.write("require larger sample sizes, these tables show practical significance thresholds.\n\n")
            
            f.write("**Understanding the Results:**\n")
            f.write("- **Difference > 0.05**: Potentially meaningful improvement for real applications\n")
            f.write("- **Difference > 0.10**: Clearly significant performance gap\n")
            f.write("- **Difference < 0.02**: Likely negligible for most use cases\n")
            f.write("- **Values marked with *** indicate differences above the 0.05 threshold\n\n")
            
            f.write("**Important Caveats:**\n")
            f.write("- These are absolute differences, not statistical significance tests\n")
            f.write("- True significance requires larger datasets and proper statistical methods\n")
            f.write("- Consider practical importance alongside statistical significance\n\n")
            
            # Create significance tables for each metric - using dynamic indices
            idx_map = {METRIC_LABELS[k]: v for k, v in metric_indices.items()}
            
            # Get model names for significance table
            model_names = [result[0].split('/')[-1] for result in sorted_results]
            
            for metric_name, metric_idx in idx_map.items():
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
        # Add timing analysis section if timing data is provided
        if timing_results:
            f.write("## Compute And Retrieval Performance Metrics\n\n")
            f.write("This section analyzes the computational efficiency of different embedding models ")
            f.write("during corpus initialization and retrieval. Understanding speed and latency is crucial ")
            f.write("for production deployment decisions.\n\n")
            
            f.write("**Why timing metrics matter:**\n")
            f.write("- **Initial setup time**: How long to embed your entire corpus\n")
            f.write("- **Update frequency**: How often you can refresh embeddings\n")
            f.write("- **Query responsiveness**: How fast retrieval returns results at runtime\n")
            f.write("- **Scalability**: Performance with larger document collections\n")
            f.write("- **Cost**: Computational resources required for deployment\n\n")
            
            # Create timing table
            timing_headers = [
                "Model",
                "Embedding Time (s)",
                "Docs/Second",
                "Avg Time/Doc (ms)",
                "Avg Query Latency (ms/query)",
                "Queries Timed",
            ]
            timing_records = []
            
            for model_name, timing_data in timing_results:
                try:
                    # Validate timing_data structure
                    if not isinstance(timing_data, dict):
                        continue  # Skip invalid data

                    embedding_time = timing_data.get("embedding_time")
                    docs_per_second = timing_data.get("docs_per_second")
                    avg_time_per_doc = timing_data.get("avg_time_per_doc")
                    avg_query_latency_ms = timing_data.get("avg_query_latency_ms")
                    queries_timed = timing_data.get("queries_timed")

                    has_embedding_data = all(
                        isinstance(value, (int, float))
                        for value in (embedding_time, docs_per_second, avg_time_per_doc)
                    )
                    has_latency_data = isinstance(avg_query_latency_ms, (int, float)) and isinstance(queries_timed, int)

                    # Keep row if we have either embedding timing or retrieval latency
                    if not (has_embedding_data or has_latency_data):
                        continue

                    timing_records.append({
                        "model": model_name,
                        "embedding_time": embedding_time if has_embedding_data else None,
                        "docs_per_second": docs_per_second if has_embedding_data else None,
                        "avg_time_per_doc_ms": (avg_time_per_doc * 1000.0) if has_embedding_data else None,
                        "avg_query_latency_ms": avg_query_latency_ms if has_latency_data else None,
                        "queries_timed": queries_timed if has_latency_data else None,
                    })
                except (TypeError, KeyError, ValueError) as e:
                    print(f"Warning: Invalid timing data for {model_name}: {e}")
                    continue

            # Sort by retrieval latency (lower is better), then by docs/sec (higher is better)
            timing_records.sort(
                key=lambda rec: (
                    rec["avg_query_latency_ms"] if isinstance(rec["avg_query_latency_ms"], (int, float)) else float("inf"),
                    -(rec["docs_per_second"] if isinstance(rec["docs_per_second"], (int, float)) else 0.0),
                )
            )

            timing_rows = []
            for rec in timing_records:
                timing_rows.append([
                    rec["model"],
                    f"{rec['embedding_time']:.2f}" if isinstance(rec["embedding_time"], (int, float)) else "N/A",
                    f"{rec['docs_per_second']:.2f}" if isinstance(rec["docs_per_second"], (int, float)) else "N/A",
                    f"{rec['avg_time_per_doc_ms']:.2f}" if isinstance(rec["avg_time_per_doc_ms"], (int, float)) else "N/A",
                    f"{rec['avg_query_latency_ms']:.2f}" if isinstance(rec["avg_query_latency_ms"], (int, float)) else "N/A",
                    f"{rec['queries_timed']}" if isinstance(rec["queries_timed"], int) else "N/A",
                ])
            
            f.write("#### Embedding Speed And Query Latency Comparison\n\n")
            f.write(tabulate(timing_rows, headers=timing_headers, tablefmt="pipe"))
            f.write("\n\n")
            
            f.write("**Table: Compute And Retrieval Performance Metrics**\n\n")
            f.write("**Column Explanations:**\n")
            f.write("- **Model**: Embedding model name\n")
            f.write("- **Embedding Time (s)**: Total time to embed all document chunks\n")
            f.write("- **Docs/Second**: Processing throughput (higher = faster)\n")
            f.write("- **Avg Time/Doc (ms)**: Average time per document chunk\n")
            f.write("- **Avg Query Latency (ms/query)**: Average DB retrieval time per query (lower = faster)\n")
            f.write("- **Queries Timed**: Number of queries included in retrieval latency measurement\n\n")
            
            f.write("**How to interpret:**\n")
            f.write("- **Higher Docs/Second** = more efficient processing\n")
            f.write("- **Lower Avg Time/Doc** = faster embedding of individual chunks\n")
            f.write("- **Lower Avg Query Latency** = faster retrieval responsiveness at runtime\n")
            f.write("- **Trade-offs**: Speed often correlates with model size/complexity\n")
            f.write("- **Production considerations**: Balance speed with retrieval quality\n\n")
            
            # Find fastest/slowest models for embedding throughput and retrieval latency
            if timing_records:  # Only proceed if there are valid timing rows
                f.write("#### Performance Insights\n\n")

                embedding_records = [rec for rec in timing_records if isinstance(rec["docs_per_second"], (int, float))]
                if embedding_records:
                    fastest_embed = max(embedding_records, key=lambda rec: rec["docs_per_second"])
                    slowest_embed = min(embedding_records, key=lambda rec: rec["docs_per_second"])
                    f.write(
                        f"- **Fastest embedding model**: `{fastest_embed['model']}` "
                        f"at {fastest_embed['docs_per_second']:.2f} docs/second\n"
                    )
                    f.write(
                        f"- **Slowest embedding model**: `{slowest_embed['model']}` "
                        f"at {slowest_embed['docs_per_second']:.2f} docs/second\n"
                    )
                    if slowest_embed["docs_per_second"] > 0:
                        speedup = fastest_embed["docs_per_second"] / slowest_embed["docs_per_second"]
                        f.write(f"- **Embedding performance ratio**: {speedup:.2f}x (fastest vs slowest)\n")

                latency_records = [rec for rec in timing_records if isinstance(rec["avg_query_latency_ms"], (int, float))]
                if latency_records:
                    lowest_latency = min(latency_records, key=lambda rec: rec["avg_query_latency_ms"])
                    highest_latency = max(latency_records, key=lambda rec: rec["avg_query_latency_ms"])
                    f.write(
                        f"- **Lowest retrieval latency**: `{lowest_latency['model']}` "
                        f"at {lowest_latency['avg_query_latency_ms']:.2f} ms/query\n"
                    )
                    f.write(
                        f"- **Highest retrieval latency**: `{highest_latency['model']}` "
                        f"at {highest_latency['avg_query_latency_ms']:.2f} ms/query\n"
                    )
                    if lowest_latency["avg_query_latency_ms"] > 0:
                        latency_ratio = highest_latency["avg_query_latency_ms"] / lowest_latency["avg_query_latency_ms"]
                        f.write(f"- **Retrieval latency spread**: {latency_ratio:.2f}x (highest vs lowest)\n")
            else:
                f.write("#### Performance Insights\n\n")
                f.write("- **No valid timing data available for analysis**\n")
            
            # Add timing visualization reference (with caption)
            timing_viz_file = f"{dataset_name}_timing_comparison_{timestamp}.png"
            
            # Generate timing visualization if timing data exists
            try:
                generate_timing_visualization(timing_results, output_dir, timestamp, dataset_name)
                f.write(f"![Figure: Compute and Retrieval Timing Comparison]({timing_viz_file})\n\n")
                f.write("*Figure: Embedding speed and query retrieval latency comparison across models.*\n\n")
            except Exception as e:
                f.write(f"*Timing visualization could not be generated: {e}*\n\n")
 
         # Technical implementation details
        f.write("## Technical Implementation\n\n")
        f.write("### Pipeline Architecture\n\n")
        f.write("The benchmark pipeline implements a modular architecture with the following components:\n\n")
        f.write("- **Document Processing Module**: PDF extraction and chunking using PyMuPDF and LangChain\n")
        f.write("- **LLM Integration**: Gemini API for query generation and relevance assessment\n")
        f.write("- **Vector Database**: ChromaDB with native embedding functions\n")
        f.write("- **Evaluation Engine**: SentenceTransformers evaluation framework\n")
        f.write("- **Reporting System**: Automated report generation with visualizations\n\n")
        
        f.write("### Reproducibility\n\n")
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
        f.write("### Embedding Model Specifications\n\n")
        for model_name, collection_name in [(m["model_name"], m["collection_name"]) for m in cfg.embedding_models]:
            f.write(f"#### {model_name}\n\n")
            f.write(f"- **Collection identifier**: `{collection_name}`\n")
            
            # Add additional model information if available
            if SENTENCE_TRANSFORMER_AVAILABLE:
                try:
                    model = SentenceTransformer(model_name)
                    f.write(f"- **Embedding dimension**: {model.get_sentence_embedding_dimension()}\n")
                    max_seq_len = getattr(model, 'max_seq_length', 'Not available')
                    f.write(f"- **Maximum sequence length**: {max_seq_len}\n")
                    f.write(f"- **Model architecture**: Transformer-based sentence encoder\n\n")
                except Exception as e:
                    f.write(f"- **Model specifications**: Error loading model ({str(e)})\n\n")
            else:
                f.write("- **Model specifications**: SentenceTransformers library not available\n\n")
        
        # Discussion and limitations
        f.write("## Discussion\n\n")
        f.write("### Key Findings\n\n")
        
        if sorted_results:
            best_model_name = sorted_results[0][0]
            f.write(f"1. **Model Performance Hierarchy**: {best_model_name} emerged as the top performer, ")
            f.write(f"achieving superior results across multiple evaluation metrics.\n\n")
            
            if len(sorted_results) > 1:
                second_best = sorted_results[1]
                # Use dynamic metric detection based on enabled metric order
                primary_metric_name = None
                primary_diff = None
                
                if primary_metric:
                    metric_idx = metric_indices[primary_metric]
                    primary_metric_name = f"{METRIC_LABELS[primary_metric]}@{cfg.k}"
                    primary_diff = sorted_results[0][metric_idx] - second_best[metric_idx]
                
                if primary_metric_name and primary_diff is not None:
                    f.write(f"2. **Performance Gaps**: The performance difference between the best and second-best ")
                    f.write(f"models ({primary_diff:.4f} {primary_metric_name}) suggests that model selection significantly ")
                    f.write(f"impacts retrieval quality.\n\n")
            
            f.write("3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation ")
            f.write("process demonstrates the feasibility of automated benchmark creation for domain-specific ")
            f.write("document collections.\n\n")
        else:
            f.write("1. **No Model Results**: This report was generated without model evaluation results.\n\n")
        
        f.write("### Limitations and Future Work\n\n")
        f.write("- **Single-domain evaluation**: Current results are specific to the evaluated document collection\n")
        f.write("- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model\n")
        f.write("- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs\n")
        f.write("- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        
        f.write("This study presents a comprehensive framework for evaluating embedding models in RAG systems. ")
        f.write("Our automated pipeline successfully generated meaningful evaluation datasets and provided ")
        f.write("statistically robust comparisons of model performance. ")
        
        if sorted_results:
            best_model_name = sorted_results[0][0]
            
            # Get the primary metric name and score dynamically
            primary_metric_name = None
            primary_score = None
            
            if primary_metric:
                metric_idx = metric_indices[primary_metric]
                primary_metric_name = f"{METRIC_LABELS[primary_metric]}@{cfg.k}"
                primary_score = sorted_results[0][metric_idx]
            
            if primary_metric_name and primary_score is not None:
                f.write(f"The results demonstrate that **{best_model_name}** provides optimal retrieval performance ")
                f.write(f"for the evaluated document collection, with a {primary_metric_name} score of {primary_score:.4f}. ")
            else:
                f.write(f"The results demonstrate that **{best_model_name}** provides optimal retrieval performance ")
                f.write(f"for the evaluated document collection. ")
            
            if len(sorted_results) > 1 and primary_metric:
                metric_idx = metric_indices[primary_metric]
                performance_gap = sorted_results[0][metric_idx] - sorted_results[-1][metric_idx]
                if performance_gap > 0.1:
                    f.write("The substantial performance variations across models underscore the importance of ")
                    f.write("systematic evaluation in embedding model selection for production RAG systems.")
                else:
                    f.write("While performance differences were moderate, the evaluation framework provides ")
                    f.write("valuable insights for informed model selection based on specific application requirements.")
            else:
                f.write("The evaluation framework provides valuable insights for informed model selection ")
                f.write("based on specific application requirements.")
        else:
            f.write("The framework demonstrates the potential for automated benchmarking, though specific ")
            f.write("performance conclusions require model evaluation results.")
        
        f.write("\n\nThe open-source nature of our evaluation framework enables researchers and practitioners ")
        f.write("to adapt the methodology for their specific domains and requirements, contributing to ")
        f.write("more systematic and reproducible evaluation practices in the RAG community.\n\n")
        
        f.write("---\n\n")
        f.write(f"*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at {timestamp}.*\n")
        f.write("*Source code and evaluation data available at the project repository.*\n")
    
    
    # Convert to PDF
    try:
        pdf_file = convert_md_to_pdf(report_file, output_dir)
        if pdf_file:
            print(f"PDF report saved to: {pdf_file}")
            return report_file, pdf_file
        else:
            print("PDF conversion failed, but markdown report is available")
            return report_file, None
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return report_file, None


def generate_visualizations(model_results, output_dir, timestamp, dataset_name="default"):
    """Generate visualizations for the benchmark report."""
    # Dictionary to store paths to generated visualization files
    viz_files = {}
    
    # Set style
    plt.style.use('ggplot')  # Use a built-in matplotlib style
    
    # Prepare data - Dynamic metric extraction based on config
    model_names = [result[0].split('/')[-1] for result in model_results]  # Use shorter names
    
    # Build metrics dictionary using dynamic enabled-metric indices
    metrics = {}
    metric_indices = get_metric_indices()
    for metric_name in get_enabled_metric_names():
        metrics[metric_name] = {
            "label": METRIC_LABELS[metric_name],
            "values": [result[metric_indices[metric_name]] for result in model_results],
        }
    
    # 1. Bar chart comparing all metrics across models
    plt.figure(figsize=(12, 8))
    
    # Set up positions for grouped bars
    x = np.arange(len(model_names))
    width = 0.15
    offset = 0
    
    # Create colormap without seaborn
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (metric_key, metric_info) in enumerate(metrics.items()):
        metric_label = metric_info["label"]
        metric_values = metric_info["values"]
        plt.bar(x + offset, metric_values, width, label=f"{metric_label}@{cfg.k}", 
                color=colors[i % len(colors)])
        offset += width
    
    plt.xlabel('Models', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title(f'Comparison of Embedding Models at k={cfg.k}', fontsize=14, weight='bold')
    metric_count = max(len(metrics), 1)
    center_offset = width * (metric_count - 1) / 2
    plt.xticks(x + center_offset, model_names, rotation=45, ha='right')
    if metrics:
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.ylim(0, 1)
    plt.tight_layout()
    
    # Save figure
    viz_file = os.path.join(output_dir, f"{dataset_name}_model_comparison_{timestamp}.png")
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    viz_files['overview'] = viz_file
    plt.close()
    
    # 2. Individual metric charts if there are multiple models
    if len(model_results) > 1:
        for j, (metric_key, metric_info) in enumerate(metrics.items()):
            metric_label = metric_info["label"]
            metric_values = metric_info["values"]
            plt.figure(figsize=(10, 6))
            # Use consistent blue color for all individual metric charts
            color = '#1f77b4'  # Blue color
            
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
            plt.ylabel(f'{metric_label} Score', fontsize=12)
            plt.title(f'{metric_label}@{cfg.k} Comparison', fontsize=14, weight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.ylim(0, max(metric_values) * 1.15)  # Add 15% headroom for labels
            plt.tight_layout()
            
            # Save figure
            viz_file = os.path.join(output_dir, f"{dataset_name}_{metric_key}_comparison_{timestamp}.png")
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            viz_files[metric_key] = viz_file
            plt.close()
    
    return viz_files


def generate_timing_visualization(timing_results, output_dir, timestamp, dataset_name="default"):
    """Generate timing performance visualization."""
    if not timing_results:
        return {}
    
    try:
        records = []
        for model_name, timing_data in timing_results:
            if not isinstance(timing_data, dict):
                continue
            short_name = model_name.split('/')[-1]
            avg_time_per_doc = timing_data.get('avg_time_per_doc')
            records.append({
                "model": short_name,
                "docs_per_second": timing_data.get('docs_per_second'),
                "avg_time_per_doc_ms": (avg_time_per_doc * 1000.0) if isinstance(avg_time_per_doc, (int, float)) else None,
                "avg_query_latency_ms": timing_data.get('avg_query_latency_ms'),
            })

        throughput_records = [r for r in records if isinstance(r["docs_per_second"], (int, float))]
        per_doc_records = [r for r in records if isinstance(r["avg_time_per_doc_ms"], (int, float))]
        latency_records = [r for r in records if isinstance(r["avg_query_latency_ms"], (int, float))]

        panels = []
        if throughput_records:
            panels.append(("Embedding Throughput", "Documents per Second", throughput_records, "docs_per_second", "skyblue", "{:.1f}"))
        if per_doc_records:
            panels.append(("Embedding Time per Document", "Average Time per Document (ms)", per_doc_records, "avg_time_per_doc_ms", "lightcoral", "{:.1f} ms"))
        if latency_records:
            panels.append(("Query Retrieval Latency", "Average Query Latency (ms/query)", latency_records, "avg_query_latency_ms", "mediumseagreen", "{:.2f} ms"))

        if not panels:
            return {}

        fig, axes = plt.subplots(1, len(panels), figsize=(7 * len(panels), 6))
        if len(panels) == 1:
            axes = [axes]

        for ax, (title, ylabel, panel_records, value_key, color, label_fmt) in zip(axes, panels):
            panel_models = [rec["model"] for rec in panel_records]
            panel_values = [rec[value_key] for rec in panel_records]

            bars = ax.bar(panel_models, panel_values, color=color, alpha=0.8)
            ax.set_xlabel('Models', fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, weight='bold')
            ax.tick_params(axis='x', rotation=45)

            max_val = max(panel_values) if panel_values else 0
            offset = max_val * 0.02 if max_val > 0 else 0.02
            for bar, value in zip(bars, panel_values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    value + offset,
                    label_fmt.format(value),
                    ha='center',
                    va='bottom'
                )

        plt.tight_layout()
        
        # Save figure
        timing_viz_file = os.path.join(output_dir, f"{dataset_name}_timing_comparison_{timestamp}.png")
        plt.savefig(timing_viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {"timing": timing_viz_file}
        
    except Exception as e:
        print(f"Error generating timing visualization: {e}")
        return {}


def generate_corpus_statistics_viz(chunk_lengths, query_lengths, relevance_distribution, chunk_count, output_dir, timestamp, dataset_name="default"):
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
        ['Count', f'{chunk_count}', f'{len(query_lengths)}', f'{len(relevance_distribution)}'],
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
    viz_file = os.path.join(output_dir, f"{dataset_name}_corpus_statistics_{timestamp}.png")
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    viz_files['corpus_stats'] = viz_file
    plt.close()
    
    return viz_files



def convert_md_to_pdf(md_file_path, output_dir="reports"):
    """Convert markdown report to PDF using pandoc with MiKTeX/pdflatex"""
    import subprocess
    import os
    
    # Get absolute paths to avoid path issues
    md_file_path = os.path.abspath(md_file_path)
    base_name = os.path.splitext(os.path.basename(md_file_path))[0]
    md_dir = os.path.dirname(md_file_path)
    
    # Calculate output path
    if os.path.isabs(output_dir):
        pdf_file_path = os.path.join(output_dir, f"{base_name}.pdf")
    else:
        project_root = os.path.dirname(os.path.dirname(__file__))
        pdf_file_path = os.path.join(project_root, output_dir, f"{base_name}.pdf")
    
    # Ensure the PDF path is also absolute
    pdf_file_path = os.path.abspath(pdf_file_path)
    
    try:
        # Enhanced pandoc command with absolute paths
        cmd = [
            "pandoc", 
            md_file_path,  # Now using absolute path
            "-o", pdf_file_path,  # Also absolute path
            "--pdf-engine=pdflatex",
            "--standalone",
            "--from=markdown",
            "--to=pdf",
            "--variable=geometry:margin=1in",
            "--variable=fontsize:11pt",
            "--toc",
            "--number-sections"
        ]
        
        print(f"Converting {md_file_path} to PDF using pandoc + MiKTeX...")
        print(f"Command: {' '.join(cmd)}")
        print(f"Working directory: {md_dir}")
        
        # Run pandoc from the markdown directory (where images are located)
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True, 
            cwd=md_dir  # This is crucial for finding images
        )
        
        if result.stdout:
            print(f"Pandoc output: {result.stdout}")
        
        print(f"✓ PDF with images generated successfully: {pdf_file_path}")
        
        # Verify the PDF was created and has reasonable size
        if os.path.exists(pdf_file_path):
            file_size = os.path.getsize(pdf_file_path)
            print(f"✓ PDF file confirmed - Size: {file_size:,} bytes")
            return pdf_file_path
        else:
            print("✗ PDF file was not created despite success message")
            return None
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Pandoc conversion failed:")
        print(f"  Return code: {e.returncode}")
        print(f"  Command: {' '.join(cmd)}")
        if e.stdout:
            print(f"  Stdout: {e.stdout}")
        if e.stderr:
            print(f"  Stderr: {e.stderr}")
        
        # Try a simpler command without advanced options
        try:
            simple_cmd = [
                "pandoc", 
                md_file_path,  # Absolute path
                "-o", pdf_file_path,  # Absolute path
                "--pdf-engine=pdflatex",
                "--standalone"
            ]
            print("\nTrying simplified pandoc command...")
            subprocess.run(simple_cmd, check=True, capture_output=True, text=True, cwd=md_dir)
            print(f"✓ PDF generated with simplified options: {pdf_file_path}")
            return pdf_file_path
        except subprocess.CalledProcessError as e2:
            print(f"✗ Simplified pandoc also failed: {e2.stderr}")
            return None
    
    except FileNotFoundError:
        print("✗ Pandoc not found in PATH")
        print("  Make sure pandoc is installed and added to your system PATH")
        return None
    
    except Exception as e:
        print(f"✗ Unexpected error during PDF conversion: {e}")
        return None

if __name__ == "__main__":
    """Manual test for PDF conversion"""
    import os
    
    # Test with the specific markdown file
    test_md_file = r"C:\Codes\RagRetrievalBench\reports\benchmark_report_2025-06-10_00-28-26.md"
    
    print("=== Manual PDF Conversion Test ===")
    print(f"Testing conversion of: {test_md_file}")
    
    # Check if the file exists
    if not os.path.exists(test_md_file):
        print(f"ERROR: Test file does not exist: {test_md_file}")
        print("Available files in reports directory:")
        reports_dir = r"C:\Codes\RagRetrievalBench\reports"
        if os.path.exists(reports_dir):
            for file in os.listdir(reports_dir):
                if file.endswith('.md'):
                    print(f"  - {file}")
        else:
            print("  Reports directory does not exist")
    else:
        print("✓ Test file found")
        
        # Test the conversion
        result = convert_md_to_pdf(test_md_file)
        
        if result:
            print(f"✓ PDF conversion successful!")
            print(f"✓ PDF saved to: {result}")
            
            # Check if PDF was actually created
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"✓ PDF file confirmed - Size: {file_size:,} bytes")
            else:
                print("✗ PDF file was not created despite success message")
        else:
            print("✗ PDF conversion failed")
    
    print("=== Test Complete ===")




def print_results_summary(model_results, queries=None, corpus=None, relevant_docs=None, 
                         timing_results=None, dataset_name=None, output_dir=None, save_raw_results=False):
    """Print benchmark results summary table and optionally save raw results JSON."""
    from tabulate import tabulate

    metric_indices = get_metric_indices()
    enabled_metrics = get_enabled_metric_names()

    # Build headers dynamically
    headers = ["Model"]
    for metric_name in enabled_metrics:
        if metric_name == "precision":
            short_label = "Prec"
        elif metric_name == "hit_rate":
            short_label = "Success"
        else:
            short_label = METRIC_LABELS[metric_name]
        headers.append(f"{short_label}@{cfg.k}")

    # Build table rows using dynamic metric indices
    table_data = []
    for result in model_results:
        model_name = result[0]
        row_values = [result[metric_indices[m]] for m in enabled_metrics]
        short_name = model_name.split("/")[-1]
        row = [short_name] + [f"{m:.4f}" for m in row_values]
        table_data.append(row)

    # Print table
    print("\nBenchmark Results Summary\n")
    print(tabulate(table_data, headers=headers, tablefmt="github"))

    # Summary statistics
    print("\nSummary Statistics\n")
    for metric_name in enabled_metrics:
        scores = [result[metric_indices[metric_name]] for result in model_results]
        print(f"- {METRIC_LABELS[metric_name]}@{cfg.k}: Best={max(scores):.4f}, "
              f"Worst={min(scores):.4f}, Avg={np.mean(scores):.4f}")
    print()

    # Save raw results JSON for aggregate analysis
    if save_raw_results and output_dir:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        raw_results_path = os.path.join(output_dir, f"raw_results_{timestamp}.json")
        # Load timing data from file if timing_results was provided
        timing_dict = {}
        if timing_results:
            # Convert timing_results list to dict
            timing_dict = {model: timing for model, timing in timing_results}
        
        save_raw_results_json(
            dataset_name=dataset_name or "unknown",
            model_results=model_results,
            timing_data=timing_dict,
            corpus=corpus or [],
            queries=queries or [],
            relevant_docs=relevant_docs or {},
            output_path=raw_results_path
        )

def print_report_info(report_files):
    """Print information about generated report files."""
    print(f"\n[Reports] Generated:")
    if isinstance(report_files, tuple):
        md_file, pdf_file = report_files
        print(f"  • Markdown: {md_file}")
        if pdf_file:
            print(f"  • PDF: {pdf_file}")
    else:
        print(f"  • Report: {report_files}")
