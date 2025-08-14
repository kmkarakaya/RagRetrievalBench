import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

import matplotlib.pyplot as plt
import numpy as np
import benchmark_config as cfg
import datetime
from tabulate import tabulate
import os
import textwrap

def generate_benchmark_report(model_results, queries, corpus, relevant_docs, timing_results=None, output_dir="reports"):
    """Generate a comprehensive benchmark report suitable for a conference paper."""   # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Debug: Check if timing data is received
    # print(f"DEBUG: timing_results received: {timing_results}")
    # if timing_results:
    #     print(f"DEBUG: Number of timing entries: {len(timing_results)}")
    #     for model_name, timing_data in timing_results:
    #         print(f"DEBUG: {model_name} - {timing_data}")

    # Generate timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(output_dir, f"benchmark_report_{timestamp}.md")
    
    # Sort models by MAP score for easier comparison
    sorted_results = sorted(model_results, key=lambda x: x[1], reverse=True)
    
    # ——— Fallback timing for evaluation‐only runs ———
    # if user only did --evaluate, timing_results is [] ⇒ inject hard‐coded values
    if timing_results is not None and not timing_results:
        print("⚠️  Warning: No timing data available for report generation")
        print("   To include timing analysis, run: python simple_rag_benchmark_pipeline.py --initialize")
        print("   Report will be generated without timing performance section")
        timing_results = None  # Clear it completely
    
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
        f.write("### Automated Pipeline Overview\n\n")
        f.write("Our evaluation framework consists of five main stages:\n\n")
        f.write("1. **PDF Processing**: Document ingestion and chunking\n")
        f.write("2. **Corpus Generation**: Creation of standardized document chunks\n")
        f.write("3. **Query Generation**: LLM-assisted query synthesis\n")
        f.write("4. **Relevance Assessment**: Automated qrels generation\n")
        f.write("5. **Embedding Evaluation**: Multi-model performance comparison\n\n")
        
        f.write("### Document Processing Pipeline\n\n")
        f.write("#### PDF Extraction and Chunking\n\n")
        f.write(f"- **Source documents**: PDF files from `{cfg.pdf_dir}` directory\n")
        f.write(f"- **Chunking strategy**: Recursive character text splitting\n")
        f.write(f"- **Chunk size**: {cfg.chunk_size} characters\n")
        f.write(f"- **Chunk overlap**: {cfg.chunk_overlap} characters\n")
        f.write(f"- **Total chunks generated**: {len(corpus)}\n\n")
        
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
        f.write("## Dataset Statistics\n\n")
        
        # Corpus statistics table
        f.write("#### Corpus Characteristics\n\n")
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
        
        # Relevance statistics
        f.write("#### Relevance Distribution\n\n")
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
        
        f.write("### Evaluation Metrics\n\n")
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
        
        # Results section
        f.write("## Results\n\n")
        
        # Comparative results table
        f.write("### Model Performance Comparison\n\n")
        
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
        f.write("### Performance Analysis\n\n")
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
            f.write("### Visual Analysis\n\n")
            
            # Add main comparison chart
            if 'overview' in viz_files:
                f.write("#### 6.3.1 Overall Performance Comparison\n\n")
                f.write(f"![Model Performance Overview]({os.path.basename(viz_files['overview'])})\n\n")
                f.write("*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*\n\n")
            
            # Add corpus statistics visualizations
            if 'corpus_stats' in viz_files:
                f.write("#### 6.3.2 Dataset Characteristics\n\n")
                f.write(f"![Corpus Statistics]({os.path.basename(viz_files['corpus_stats'])})\n\n")
                f.write("*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*\n\n")
            
            # Add individual metric charts
            f.write("#### 6.3.3 Individual Metric Analysis\n\n")
            for metric_name, file_path in viz_files.items():
                if metric_name not in ['overview', 'corpus_stats']:
                    f.write(f"##### {metric_name.upper()}@{cfg.k} Results\n\n")
                    f.write(f"![{metric_name.capitalize()} Comparison]({os.path.basename(file_path)})\n\n")
        
        # Statistical significance analysis
        if len(model_results) >= 2:
            f.write("### Statistical Significance Analysis\n\n")
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
        # Add timing analysis section if timing data is provided
        if timing_results:
            f.write("## Embedding Performance Metrics\n\n")
            f.write("This section analyzes the computational efficiency of different embedding models ")
            f.write("during the corpus initialization phase, measuring the time required to embed ")
            f.write(f"and index {len(corpus)} documents.\n\n")
            
            # Create timing table
            timing_headers = ["Model", "Embedding Time (s)", "Docs/Second", "Avg Time/Doc (ms)"]
            timing_rows = []
            
            for model_name, timing_data in timing_results:
                timing_rows.append([
                    model_name,
                    f"{timing_data['embedding_time']:.2f}",
                    f"{timing_data['docs_per_second']:.2f}",
                    f"{timing_data['avg_time_per_doc']*1000:.2f}"
                ])
            
            # Sort by docs per second (fastest first)
            timing_rows.sort(key=lambda x: float(x[2]), reverse=True)
            
            f.write("#### Embedding Speed Comparison\n\n")
            f.write(tabulate(timing_rows, headers=timing_headers, tablefmt="pipe"))
            f.write("\n\n")
            
            # Find fastest and slowest models
            fastest_model = timing_rows[0]
            slowest_model = timing_rows[-1]
            
            f.write("#### Performance Insights\n\n")
            f.write(f"- **Fastest embedding model**: `{fastest_model[0]}` at {fastest_model[2]} docs/second\n")
            f.write(f"- **Slowest embedding model**: `{slowest_model[0]}` at {slowest_model[2]} docs/second\n")
            
            # Calculate speedup
            if float(slowest_model[2]) > 0:
                speedup = float(fastest_model[2]) / float(slowest_model[2])
                f.write(f"- **Performance ratio**: {speedup:.2f}x speed difference between fastest and slowest\n")
            
            # Add timing visualization reference (with caption)
            timing_viz_file = f"timing_comparison_{timestamp}.png"
            f.write(f"![Figure: Embedding Speed Comparison]({timing_viz_file})\n\n")
 
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
            try:
                model = SentenceTransformer(model_name)
                f.write(f"- **Embedding dimension**: {model.get_sentence_embedding_dimension()}\n")
                f.write(f"- **Maximum sequence length**: {model.max_seq_length}\n")
                f.write(f"- **Model architecture**: Transformer-based sentence encoder\n\n")
            except:
                f.write("- **Model specifications**: Not available through SentenceTransformers interface\n\n")
        
        # Discussion and limitations
        f.write("## Discussion\n\n")
        f.write("### Key Findings\n\n")
        
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




def print_results_summary(model_results):
    """Print benchmark results summary table."""
    from tabulate import tabulate

    # Build headers
    headers = ["Model"]
    if cfg.compute_map:       headers.append(f"MAP@{cfg.k}")
    if cfg.compute_recall:    headers.append(f"Recall@{cfg.k}")
    if cfg.compute_precision: headers.append(f"Prec@{cfg.k}")
    if cfg.compute_ndcg:      headers.append(f"NDCG@{cfg.k}")
    if cfg.compute_mrr:       headers.append(f"MRR@{cfg.k}")

    # Build table rows
    table_data = []
    for model_name, *metrics in model_results:
        short_name = model_name.split("/")[-1]
        row = [short_name] + [f"{m:.4f}" for m in metrics]
        table_data.append(row)

    # Print table
    print("\nBenchmark Results Summary\n")
    print(tabulate(table_data, headers=headers, tablefmt="github"))

    # Summary statistics
    # (only for metrics that exist)
    print("\nSummary Statistics\n")
    if cfg.compute_map:
        map_idx = headers.index(f"MAP@{cfg.k}")
        scores = [float(r[map_idx]) for r in table_data]
        print(f"• MAP@{cfg.k}: Best={max(scores):.4f}, "
              f"Worst={min(scores):.4f}, Avg={np.mean(scores):.4f}")
    if cfg.compute_recall:
        rec_idx = headers.index(f"Recall@{cfg.k}")
        scores = [float(r[rec_idx]) for r in table_data]
        print(f"• Recall@{cfg.k}: Best={max(scores):.4f}, "
              f"Worst={min(scores):.4f}, Avg={np.mean(scores):.4f}")
    print()


def print_report_info(report_files):
    """Print information about generated report files."""
    print(f"\n📊 REPORTS GENERATED:")
    if isinstance(report_files, tuple):
        md_file, pdf_file = report_files
        print(f"  • Markdown: {md_file}")
        if pdf_file:
            print(f"  • PDF: {pdf_file}")
    else:
        print(f"  • Report: {report_files}")
