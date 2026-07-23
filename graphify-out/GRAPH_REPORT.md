# Graph Report - .  (2026-07-23)

## Corpus Check
- Large corpus: 88 files · ~858,408 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 665 nodes · 1052 edges · 52 communities (46 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.83)
- Token cost: 158,632 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Pipeline Orchestration & Config|Pipeline Orchestration & Config]]
- [[_COMMUNITY_Related Work & Citations|Related Work & Citations]]
- [[_COMMUNITY_Report Generation Tests|Report Generation Tests]]
- [[_COMMUNITY_Metric Indexing & Tests|Metric Indexing & Tests]]
- [[_COMMUNITY_Pooled Qrels & Batch API|Pooled Qrels & Batch API]]
- [[_COMMUNITY_Task Runner (make.py)|Task Runner (make.py)]]
- [[_COMMUNITY_ChromaDB Retrieval & Eval|ChromaDB Retrieval & Eval]]
- [[_COMMUNITY_Analysis Common Helpers|Analysis Common Helpers]]
- [[_COMMUNITY_Journal Figure Generation|Journal Figure Generation]]
- [[_COMMUNITY_Benchmark CLI & Qrels Generation|Benchmark CLI & Qrels Generation]]
- [[_COMMUNITY_Document Loading & Tests|Document Loading & Tests]]
- [[_COMMUNITY_Query-Level Eval & Bootstrap|Query-Level Eval & Bootstrap]]
- [[_COMMUNITY_Report Utils Integration|Report Utils Integration]]
- [[_COMMUNITY_Manuscript & Data Provenance|Manuscript & Data Provenance]]
- [[_COMMUNITY_Report Utilities|Report Utilities]]
- [[_COMMUNITY_LLM & Batch Config|LLM & Batch Config]]
- [[_COMMUNITY_Results & Core Findings|Results & Core Findings]]
- [[_COMMUNITY_Negative-Judgment Reconstruction|Negative-Judgment Reconstruction]]
- [[_COMMUNITY_Aggregate Statistics|Aggregate Statistics]]
- [[_COMMUNITY_Aggregate Report Charts|Aggregate Report Charts]]
- [[_COMMUNITY_LaTeX Template Compliance|LaTeX Template Compliance]]
- [[_COMMUNITY_Aggregate Report Tests|Aggregate Report Tests]]
- [[_COMMUNITY_LLM Judge & Retry|LLM Judge & Retry]]
- [[_COMMUNITY_Metric-Indexing Test Suite|Metric-Indexing Test Suite]]
- [[_COMMUNITY_Qrels Construction Method|Qrels Construction Method]]
- [[_COMMUNITY_Report Utility Tests|Report Utility Tests]]
- [[_COMMUNITY_Corpus Loading & NFC|Corpus Loading & NFC]]
- [[_COMMUNITY_Visualization Tests|Visualization Tests]]
- [[_COMMUNITY_Text Chunking|Text Chunking]]
- [[_COMMUNITY_Qrels Generation Tests|Qrels Generation Tests]]
- [[_COMMUNITY_Report Integration Tests|Report Integration Tests]]
- [[_COMMUNITY_Report Metric-Indexing Tests|Report Metric-Indexing Tests]]
- [[_COMMUNITY_Edge-Case Error Tests|Edge-Case Error Tests]]
- [[_COMMUNITY_Statistical Significance Tests|Statistical Significance Tests]]
- [[_COMMUNITY_Performance Distribution Charts|Performance Distribution Charts]]
- [[_COMMUNITY_Language Effect & Models|Language Effect & Models]]
- [[_COMMUNITY_Cross-Dataset Aggregation|Cross-Dataset Aggregation]]
- [[_COMMUNITY_Markdown Report & Radar Chart|Markdown Report & Radar Chart]]
- [[_COMMUNITY_Speed & Latency Heatmaps|Speed & Latency Heatmaps]]
- [[_COMMUNITY_Dataset Configuration|Dataset Configuration]]
- [[_COMMUNITY_Corpus Statistics Viz|Corpus Statistics Viz]]
- [[_COMMUNITY_Citation Audit|Citation Audit]]
- [[_COMMUNITY_Bootstrap Forest Plot|Bootstrap Forest Plot]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]

## God Nodes (most connected - your core abstractions)
1. `Related Work Section` - 48 edges
2. `generate_aggregate_report()` - 30 edges
3. `generate_benchmark_report()` - 21 edges
4. `BatchManager` - 19 edges
5. `load_corpus()` - 17 edges
6. `Experiments Section` - 17 edges
7. `load_queries()` - 15 edges
8. `main()` - 14 edges
9. `TestMetricIndexingLogic` - 13 edges
10. `generate_content()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Pinned Environment Version Snapshot` --semantically_similar_to--> `Python Dependency Manifest (requirements.txt)`  [INFERRED] [semantically similar]
  current_versions.txt → requirements.txt
- `build_union()` --calls--> `load_corpus()`  [EXTRACTED]
  analysis/pooled_qrels.py → utils/document_loader.py
- `build_union()` --calls--> `load_queries()`  [EXTRACTED]
  analysis/pooled_qrels.py → utils/document_loader.py
- `_rank_all()` --calls--> `load_corpus()`  [EXTRACTED]
  analysis/query_level_eval.py → utils/document_loader.py
- `_rank_all()` --calls--> `load_queries()`  [EXTRACTED]
  analysis/query_level_eval.py → utils/document_loader.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Synthetic Query and Pooled-Qrels Construction Workflow** — journal_paper_method_synthetic_query_generation, journal_paper_method_query_generator, journal_paper_method_model_independent_candidate_pool, journal_paper_method_relevance_judge, journal_paper_method_qrels_construction [EXTRACTED 1.00]
- **The Four Research Questions RQ1-RQ4** — journal_paper_intro_rq1, journal_paper_intro_rq2, journal_paper_intro_rq3, journal_paper_intro_rq4 [EXTRACTED 1.00]
- **End-to-End Benchmarking Pipeline Stage Flow** — journal_paper_method_corpus_preparation, journal_paper_method_synthetic_query_generation, journal_paper_method_qrels_construction, journal_paper_method_embedding_index_construction, journal_paper_method_retrieval_evaluation_workflow, journal_paper_method_automated_reporting [EXTRACTED 1.00]
- **RAG Benchmark CLI Pipeline Stages** — readme_prepare_corpus, readme_generate_queries, readme_generate_qrels, readme_initialize, readme_evaluate, readme_generate_aggregate_report [EXTRACTED 1.00]
- **Reviewer Re-Analysis Scripts** — analysis_readme_query_level_eval, analysis_readme_pooled_qrels, analysis_readme_bootstrap_ci, analysis_readme_reconstruct_negatives, analysis_readme_common [EXTRACTED 1.00]
- **CAS LaTeX Compliance Guidance Set** — latex_template_compliance_skill, template_rules_cas_template_rules, checklist_latex_compliance_checklist, agents_codex_project_rules [EXTRACTED 1.00]

## Communities (52 total, 6 thin omitted)

### Community 0 - "Pipeline Orchestration & Config"
Cohesion: 0.06
Nodes (45): bootstrap_ci.py, ChromaDB Native Index Segfault Caveat, common.py Shared Helpers, Reconstruction Consistency Gate, Exact Squared-L2 kNN Reconstruction, pooled_qrels.py, query_level_eval.py, Reviewer-Driven Re-Analysis Layer (+37 more)

### Community 1 - "Related Work & Citations"
Cohesion: 0.05
Nodes (43): Abdallah et al. 2025 (RerankArena), Abimbola et al. 2026 (Open-Source Embedding Survey), Ali et al. 2024 (RAG+LLM Traceability), Bassani & Pasi 2021 (Synthetic Query Labeling), Baysan & Gungor 2025 (TR-MTEB), Bellard et al. 2025 (Agentic RAG LLM-Judge), Caferoglu et al. 2025 (Sing-SQL), Cohen et al. 2025 (WixQA) (+35 more)

### Community 2 - "Report Generation Tests"
Cohesion: 0.07
Nodes (19): generate_benchmark_report(), Test report generation functionality, Setup test data and config, Test successful report generation, Test report generation without timing data, Test report generation with empty model results, Test report generation with only some metrics enabled, Test report renders Success@k / Hit Rate@k when enabled. (+11 more)

### Community 3 - "Metric Indexing & Tests"
Cohesion: 0.09
Nodes (18): Test metric indexing logic for report_utils.py This tests the core fix for dyna, Test when only recall is enabled, Test with only recall and precision enabled, Test the core metric indexing logic that was fixed in report_utils.py, Test when no metrics are enabled, Store original config values before each test, Test that metric order doesn't matter when some are disabled, Test edge case where middle metrics are disabled (+10 more)

### Community 4 - "Pooled Qrels & Batch API"
Cohesion: 0.13
Nodes (15): build_union(), fetch(), _job_for(), main(), plan(), Build model-INDEPENDENT pooled qrels to correct the M5 candidate-pool bias.  Pro, Return (corpus, queries, pool) where pool[qid][docid] = best rank across models., (qid, docid, best_rank) ordered by query then ascending best rank. (+7 more)

### Community 5 - "Task Runner (make.py)"
Cohesion: 0.11
Nodes (25): aggregate_report(), all_steps(), benchmark(), clean(), evaluate(), format(), help(), init_collections() (+17 more)

### Community 6 - "ChromaDB Retrieval & Eval"
Cohesion: 0.12
Nodes (22): build_qrels_candidate_pool(), Return {query_id: [(doc_id, text), ...]} candidate pool for LLM judging.      Wh, Test collection initialization when collection already exists, Hit-rate metric should default to 0.0 when accuracy@k is missing., Test that ChromaDB client is created successfully, Test collection initialization with mock data, Test the evaluation function with mock data, test_evaluate_with_chromadb() (+14 more)

### Community 7 - "Analysis Common Helpers"
Cohesion: 0.09
Nodes (19): analysis_dir(), embed_texts(), extract_response_text(), get_st_model(), knn_rank(), label_for(), load_expected_means(), parse_relevance_score() (+11 more)

### Community 8 - "Journal Figure Generation"
Cohesion: 0.31
Nodes (20): Any, Path, build_alias_map(), build_metadata(), configure_matplotlib(), generate_figures(), latency_ms(), latest_raw_result_path() (+12 more)

### Community 9 - "Benchmark CLI & Qrels Generation"
Cohesion: 0.16
Nodes (20): add_forced_source_qrel(), apply_source_chunk_coverage(), configure_utf8_stdio(), extract_response_text(), generate_qrels(), generate_queries_from_corpus(), main(), normalize_unicode_text() (+12 more)

### Community 10 - "Document Loading & Tests"
Cohesion: 0.15
Nodes (19): Test loading all ground truth files together, Query ids/text should be normalized to NFC when loading., Test successful queries loading, Test queries loading with non-existent file, Test corpus preparation from PDFs, test_load_ground_truth(), test_load_queries_file_not_found(), test_load_queries_normalizes_unicode_nfc() (+11 more)

### Community 11 - "Query-Level Eval & Bootstrap"
Cohesion: 0.17
Nodes (17): ci(), main(), paired(), qrels_path(), Query-level bootstrap confidence intervals (replaces the underpowered n=3 Friedm, run(), load_rankings(), main() (+9 more)

### Community 12 - "Report Utils Integration"
Cohesion: 0.13
Nodes (12): Test report generation with all metrics enabled, Test report generation with only some metrics enabled (critical test for indexin, Test report with only recall enabled (edge case), Test that empty model results raise appropriate error, Test timing data validation handles invalid data gracefully, Test report_utils.py integration with proper metric indexing, Setup test data and config, TestReportUtilsIntegration (+4 more)

### Community 13 - "Manuscript & Data Provenance"
Cohesion: 0.16
Nodes (18): Conclusion Section, Dataset education_eng, Dataset education_tr, Dataset law_tr, M2 all-mpnet-base-v2 (English), M3 paraphrase-multilingual-MiniLM-L12-v2, M4 all-MiniLM-L12-v2 (English), Experiments Section (+10 more)

### Community 14 - "Report Utilities"
Cohesion: 0.22
Nodes (15): _capture_environment(), generate_visualizations(), get_enabled_metric_names(), get_metric_indices(), get_primary_metric_key(), normalize_unicode_text(), print_results_summary(), Generate visualizations for the benchmark report. (+7 more)

### Community 15 - "LLM & Batch Config"
Cohesion: 0.20
Nodes (11): get_latest_raw_results(), Find the most recent raw_results_{timestamp}.json for a dataset.     Returns ab, Test client initialization when API key exists in .env file but not in system en, Test client initialization when API key exists in system environment but not in, Test that API key from .env file is used even when a different key exists in sys, Test behavior when API key is not found in either .env file or system environmen, test_api_key_env_file_priority_over_system(), test_api_key_found_in_env_file() (+3 more)

### Community 16 - "Results & Core Findings"
Cohesion: 0.16
Nodes (15): Six Retrieval Metrics, RQ1: Pipeline Utility, RQ3: Domain Sensitivity, RQ4: Operational Decision Support, Introduction Section, Model-Independent Pooled Qrels, Lewis et al. 2021 (RAG), Thakur et al. 2025 (TREC RAG Human vs LLM Judges) (+7 more)

### Community 17 - "Negative-Judgment Reconstruction"
Cohesion: 0.24
Nodes (13): build(), _dataset_file(), frozen_judged_labels(), judged_pairs(), latest_qrels_batch(), main(), positives(), Reconstruct the implicit NEGATIVE relevance judgments that the frozen pipeline d (+5 more)

### Community 18 - "Aggregate Statistics"
Cohesion: 0.15
Nodes (13): calculate_consistency_scores(), calculate_model_rankings(), generate_consistency_comparison_chart(), load_dataset_results(), load_multiple_datasets(), normalize_model_names(), Aggregate reporting utilities for cross-dataset performance comparison. Impleme, Load most recent raw_results JSON for a dataset.     Returns None if not found (+5 more)

### Community 19 - "Aggregate Report Charts"
Cohesion: 0.14
Nodes (14): calculate_average_ranks(), generate_aggregate_report(), generate_dataset_characteristics_chart(), generate_model_ranking_heatmap(), generate_pairwise_significance_heatmap(), get_common_models(), Overview chart for dataset sizes (Documents (PDFs), chunks, queries, qrels)., Heatmap of p-values with significance indicators.     Color: White (p>0.05) to (+6 more)

### Community 20 - "LaTeX Template Compliance"
Cohesion: 0.21
Nodes (13): journal_paper/build.ps1 Lint/Build Gate, Elsevier CAS Template Conventions, Codex Project Rules, Flat Folder Policy, TeX-First Manuscript Workflow, Manuscript Section Boundaries, LaTeX Compliance Checklist, CAS Abstract verbatimwrite Handling (+5 more)

### Community 21 - "Aggregate Report Tests"
Cohesion: 0.24
Nodes (12): _build_datasets_fixture(), test_compute_weighted_query_latency_summary(), test_extract_query_latency_matrix(), test_metric_compatibility_includes_hit_rate(), compute_weighted_query_latency_summary(), extract_query_latency_matrix(), get_common_metrics(), Check metric flag consistency across datasets.     Returns validation report wi (+4 more)

### Community 22 - "LLM Judge & Retry"
Cohesion: 0.17
Nodes (12): judge_with_retry(), Synchronous LLM judge with exponential backoff.      Fallback for the Batch API, Test error handling when trying to generate content with an invalid API key, Test content generation succeeds with valid API response (using mocked client), Integration test: Generate content using API key from .env file, ensuring system, Integration test: Generate content using API key from system environment, when n, test_api_error_with_invalid_key(), test_generate_content_successful_response() (+4 more)

### Community 23 - "Metric-Indexing Test Suite"
Cohesion: 0.17
Nodes (7): Test metric indexing with only some metrics enabled, Test when only recall is enabled, Test metric indexing fixes, Store original config values before each test, Restore original config values after each test, Test metric indexing when all metrics are enabled, TestMetricIndexing

### Community 24 - "Qrels Construction Method"
Cohesion: 0.20
Nodes (11): Gemini 2.5 Flash-Lite, Automated Two-Layer Reporting, Local RAG Benchmarking Pipeline, ChromaDB Vector Store, Corpus Preparation (Chunking), Qrels (Relevance Judgment) Construction, LLM Query Generator Role, LLM-as-Judge (Relevance Judge Role) (+3 more)

### Community 25 - "Report Utility Tests"
Cohesion: 0.22
Nodes (8): mock_chromadb_client_for_reports(), print_report_info(), print_results_summary(), Avoid real ChromaDB calls in report tests., Test utility functions, Test results summary printing, Test report info printing, TestUtilityFunctions

### Community 26 - "Corpus Loading & NFC"
Cohesion: 0.20
Nodes (10): load_corpus(), DEPRECATED: Use utils.document_loader.load_corpus() instead.     Kept for backwa, Test successful corpus loading, Corpus doc ids/text should be normalized to NFC when loading., Test corpus loading with non-existent file, test_load_corpus_file_not_found(), test_load_corpus_normalizes_unicode_nfc(), test_load_corpus_success() (+2 more)

### Community 27 - "Visualization Tests"
Cohesion: 0.20
Nodes (6): Test visualization generation functions, Test visualization generation, Test timing visualization generation, TestVisualizationFunctions, generate_timing_visualization(), Generate timing performance visualization.

### Community 28 - "Text Chunking"
Cohesion: 0.33
Nodes (8): test_split_text_basic(), test_split_text_empty(), test_split_text_overlap(), test_split_text_small_input(), Loads all PDFs from a directory, splits their text into chunks, and returns a li, Split the text into smaller chunks for processing.          Args:         tex, split_pdfs_to_chunks(), split_text()

### Community 29 - "Qrels Generation Tests"
Cohesion: 0.50
Nodes (7): _batch_result(), _read_qrels_lines(), test_batch_fetch_adds_source_for_queries_missing_in_batch_results(), test_batch_fetch_deduplicates_when_source_already_positive(), test_batch_fetch_forces_source_even_when_all_llm_labels_zero(), test_non_batch_forces_source_and_deduplicates_candidates(), _write_queries_jsonl()

### Community 30 - "Report Integration Tests"
Cohesion: 0.25
Nodes (6): mock_chromadb_client_for_reports(), Test report_utils.py functionality, focusing on the metric indexing fixes and in, Test utility print functions work correctly, Avoid real ChromaDB calls in report tests., print_report_info(), Print information about generated report files.

### Community 31 - "Report Metric-Indexing Tests"
Cohesion: 0.25
Nodes (4): Test metric indexing within report generation context, Test the sorting logic used in report generation, Test various metric configuration scenarios, TestMetricIndexingInReportContext

### Community 32 - "Edge-Case Error Tests"
Cohesion: 0.25
Nodes (4): Test edge cases and error handling, Test with only one model result, Test with empty timing results list (not None), TestEdgeCasesAndErrorHandling

### Community 33 - "Statistical Significance Tests"
Cohesion: 0.25
Nodes (8): check_aggregate_dependencies(), generate_win_tie_loss_matrix(), perform_friedman_test(), perform_pairwise_significance_tests(), Paired t-test for all model pairs across datasets.     Each dataset provides on, Win-Tie-Loss analysis across datasets.          Returns DataFrame showing wins, Friedman test for overall differences across multiple models and datasets., Check if required dependencies for aggregate reporting are installed.     Raise

### Community 34 - "Performance Distribution Charts"
Cohesion: 0.25
Nodes (8): generate_dataset_difficulty_chart(), generate_model_performance_heatmap(), generate_performance_distribution_plots(), metric_display_name(), Bar chart showing mean model performance per dataset.     Datasets sorted by me, Heatmap of model performance by dataset for a single metric.      Returns: Pat, Human-readable metric name for narrative text and titles., Box plot for score distributions across datasets.     One subplot per model sho

### Community 35 - "Language Effect & Models"
Cohesion: 0.40
Nodes (6): M1 all-MiniLM-L6-v2 (English), M5 paraphrase-multilingual-mpnet-base-v2, RQ2: Language Sensitivity, Per-Model Embedding Index Construction, Sentence Transformers, Language Effect

### Community 36 - "Cross-Dataset Aggregation"
Cohesion: 0.33
Nodes (6): aggregate_model_performance(), calculate_effect_sizes(), extract_model_scores_across_datasets(), Extract scores for one model/metric across all datasets.     Returns: {"educati, Compute aggregate statistics per model across datasets.          Returns struc, Cohen's d effect size for model comparison.          Returns:     {

### Community 37 - "Markdown Report & Radar Chart"
Cohesion: 0.33
Nodes (6): generate_cross_dataset_radar_chart(), metric_header_name(), Write the actual Markdown report content., Short metric name for table headers., Multi-axis radar chart comparing top models across metrics.     Each metric axi, _write_markdown_report()

### Community 38 - "Speed & Latency Heatmaps"
Cohesion: 0.33
Nodes (6): generate_embedding_speed_heatmap(), generate_query_latency_heatmap(), get_all_models(), Heatmap of embedding throughput (chunks/sec) by model and dataset.      Return, Heatmap of query retrieval latency (ms/query) by model and dataset.     Lower v, Get all unique models across datasets.

### Community 39 - "Dataset Configuration"
Cohesion: 0.33
Nodes (4): configure_for_dataset(), discover_available_datasets(), Configures paths and variables for a specific dataset.     Args:         datas, Auto-discover datasets in datasets/ directory.     Returns list of dataset name

### Community 40 - "Corpus Statistics Viz"
Cohesion: 0.50
Nodes (3): Test corpus statistics visualization, generate_corpus_statistics_viz(), Generate visualizations for corpus statistics.

## Knowledge Gaps
- **69 isolated node(s):** `Abstract`, `Corpus Preparation (Chunking)`, `Automated Two-Layer Reporting`, `Reproducibility (Frozen Artifacts)`, `Six Retrieval Metrics` (+64 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `generate_benchmark_report()` connect `Report Utils Integration` to `Edge-Case Error Tests`, `Corpus Statistics Viz`, `Benchmark CLI & Qrels Generation`, `Report Utilities`, `Report Utility Tests`, `Visualization Tests`, `Report Integration Tests`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `generate_aggregate_report()` connect `Aggregate Report Charts` to `Statistical Significance Tests`, `Performance Distribution Charts`, `Cross-Dataset Aggregation`, `Markdown Report & Radar Chart`, `Speed & Latency Heatmaps`, `Benchmark CLI & Qrels Generation`, `Report Utils Integration`, `Aggregate Statistics`, `Aggregate Report Tests`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **What connects `Query-level bootstrap confidence intervals (replaces the underpowered n=3 Friedm`, `Citation audit (A24): cited keys vs refs.bib entries; missing/unused/incomplete.`, `Shared helpers for the re-analysis workstream (reviewer-driven revision).  Desig` to the rest of the system?**
  _273 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pipeline Orchestration & Config` be split into smaller, more focused modules?**
  _Cohesion score 0.06161616161616162 - nodes in this community are weakly interconnected._
- **Should `Related Work & Citations` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._
- **Should `Report Generation Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06825396825396825 - nodes in this community are weakly interconnected._
- **Should `Metric Indexing & Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.08505747126436781 - nodes in this community are weakly interconnected._