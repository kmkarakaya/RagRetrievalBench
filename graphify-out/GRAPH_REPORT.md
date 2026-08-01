# Graph Report - c:/Codes/RagRetrievalBench  (2026-08-01)

## Corpus Check
- 29 files · ~2,793,102 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 734 nodes · 1182 edges · 50 communities (47 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.85)
- Token cost: 51,935 input · 2,087 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Journal Figure Generation|Journal Figure Generation]]
- [[_COMMUNITY_Reviewer-Driven Re-Analysis|Reviewer-Driven Re-Analysis]]
- [[_COMMUNITY_Related Work Bibliography|Related Work Bibliography]]
- [[_COMMUNITY_Report Generation Tests|Report Generation Tests]]
- [[_COMMUNITY_Benchmark CLI Pipeline|Benchmark CLI Pipeline]]
- [[_COMMUNITY_Dataset Report Utilities|Dataset Report Utilities]]
- [[_COMMUNITY_Query-Level Re-Evaluation|Query-Level Re-Evaluation]]
- [[_COMMUNITY_Metric Indexing Tests|Metric Indexing Tests]]
- [[_COMMUNITY_ChromaDB and Candidate Pooling|ChromaDB and Candidate Pooling]]
- [[_COMMUNITY_Model-Independent Pooled Qrels|Model-Independent Pooled Qrels]]
- [[_COMMUNITY_Bootstrap Uncertainty Tests|Bootstrap Uncertainty Tests]]
- [[_COMMUNITY_Springer Template Compliance|Springer Template Compliance]]
- [[_COMMUNITY_Re-Analysis Shared Helpers|Re-Analysis Shared Helpers]]
- [[_COMMUNITY_Aggregate Report Charts|Aggregate Report Charts]]
- [[_COMMUNITY_Gemini LLM Integration|Gemini LLM Integration]]
- [[_COMMUNITY_Corpora and Model Roster|Corpora and Model Roster]]
- [[_COMMUNITY_Manuscript Number Verification|Manuscript Number Verification]]
- [[_COMMUNITY_Report Integration Tests|Report Integration Tests]]
- [[_COMMUNITY_Research Questions and Evidence|Research Questions and Evidence]]
- [[_COMMUNITY_Aggregate Report Tests|Aggregate Report Tests]]
- [[_COMMUNITY_Cross-Dataset Aggregation|Cross-Dataset Aggregation]]
- [[_COMMUNITY_Bootstrap Interval Estimators|Bootstrap Interval Estimators]]
- [[_COMMUNITY_Metric Indexing Fixtures|Metric Indexing Fixtures]]
- [[_COMMUNITY_Local RAG Pipeline Concepts|Local RAG Pipeline Concepts]]
- [[_COMMUNITY_Query-Level Uncertainty Core|Query-Level Uncertainty Core]]
- [[_COMMUNITY_Visualization Tests|Visualization Tests]]
- [[_COMMUNITY_PDF Chunking and Splitting|PDF Chunking and Splitting]]
- [[_COMMUNITY_Qrels Generation Semantics Tests|Qrels Generation Semantics Tests]]
- [[_COMMUNITY_Report Print Utilities|Report Print Utilities]]
- [[_COMMUNITY_Metric Indexing in Reports|Metric Indexing in Reports]]
- [[_COMMUNITY_Report Edge-Case Handling|Report Edge-Case Handling]]
- [[_COMMUNITY_Console Output Tests|Console Output Tests]]
- [[_COMMUNITY_Statistical Significance Testing|Statistical Significance Testing]]
- [[_COMMUNITY_Performance Distribution Charts|Performance Distribution Charts]]
- [[_COMMUNITY_Bootstrap Artifact Persistence|Bootstrap Artifact Persistence]]
- [[_COMMUNITY_Dataset Configuration|Dataset Configuration]]
- [[_COMMUNITY_Frozen-Snapshot Bootstrap CLI|Frozen-Snapshot Bootstrap CLI]]
- [[_COMMUNITY_Language Sensitivity and Indexing|Language Sensitivity and Indexing]]
- [[_COMMUNITY_Effect Size and Aggregation|Effect Size and Aggregation]]
- [[_COMMUNITY_Model Alias Mapping|Model Alias Mapping]]
- [[_COMMUNITY_Metric Compatibility Validation|Metric Compatibility Validation]]
- [[_COMMUNITY_Raw Results Loading|Raw Results Loading]]
- [[_COMMUNITY_Citation Audit|Citation Audit]]
- [[_COMMUNITY_Pytest Configuration|Pytest Configuration]]
- [[_COMMUNITY_Retired CAS Bundle Manifest|Retired CAS Bundle Manifest]]

## God Nodes (most connected - your core abstractions)
1. `Related Work Section` - 47 edges
2. `generate_aggregate_report()` - 31 edges
3. `generate_benchmark_report()` - 25 edges
4. `generate()` - 17 edges
5. `Experiments Section` - 15 edges
6. `generate_figures()` - 15 edges
7. `TestMetricIndexingLogic` - 13 edges
8. `main()` - 13 edges
9. `generate_benchmark_report()` - 12 edges
10. `metric_value()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Pinned Environment Version Snapshot` --semantically_similar_to--> `Python Dependency Manifest (requirements.txt)`  [INFERRED] [semantically similar]
  current_versions.txt → requirements.txt
- `Springer Front Matter Contract` --semantically_similar_to--> `Springer Front Matter Contract (SN001-SN008)`  [INFERRED] [semantically similar]
  codex_skills/latex-template-compliance/references/template_rules.md → AGENTS.md
- `Declarations Rules` --semantically_similar_to--> `Springer Declarations Contract (SN013-SN014)`  [INFERRED] [semantically similar]
  codex_skills/latex-template-compliance/SKILL.md → AGENTS.md
- `test_split_text_basic()` --calls--> `split_text()`  [EXTRACTED]
  tests/test_text_splitter.py → utils/text_splitter.py
- `test_split_text_overlap()` --calls--> `split_text()`  [EXTRACTED]
  tests/test_text_splitter.py → utils/text_splitter.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **RAG Evaluation Pipeline Stages** — utils_document_loader, utils_llm, utils_chromadb_utils, utils_bootstrap_utils, utils_report_utils [EXTRACTED 1.00]
- **Manuscript Artifact Automation** — rag_benchmark_py, utils_paper_artifacts, journal_paper_manuscript [EXTRACTED 0.95]
- **Springer sn-jnl Template Contract** — agents_sn_template, agents_sn_front_matter, agents_forbidden_preamble, agents_sn_declarations, references_template_rules_front_matter_contract, references_template_rules_bibliography_contract, references_template_rules_lint_rule_map [EXTRACTED 1.00]
- **Template Compliance Enforcement Chain** — agents_codex_project_rules, latex_template_compliance_skill_skill, references_checklist_latex_compliance_checklist, agents_build_ps1 [EXTRACTED 1.00]

## Communities (50 total, 3 thin omitted)

### Community 0 - "Journal Figure Generation"
Cohesion: 0.10
Nodes (54): Any, Manuscript (sn-jnl), Path, build_alias_map(), build_metadata(), configure_matplotlib(), _figure_datasets(), generate_figures() (+46 more)

### Community 1 - "Reviewer-Driven Re-Analysis"
Cohesion: 0.06
Nodes (45): bootstrap_ci.py, ChromaDB Native Index Segfault Caveat, common.py Shared Helpers, Reconstruction Consistency Gate, Exact Squared-L2 kNN Reconstruction, pooled_qrels.py, query_level_eval.py, Reviewer-Driven Re-Analysis Layer (+37 more)

### Community 2 - "Related Work Bibliography"
Cohesion: 0.05
Nodes (43): Abdallah et al. 2025 (RerankArena), Abimbola et al. 2026 (Open-Source Embedding Survey), Ali et al. 2024 (RAG+LLM Traceability), Bassani & Pasi 2021 (Synthetic Query Labeling), Baysan & Gungor 2025 (TR-MTEB), Bellard et al. 2025 (Agentic RAG LLM-Judge), Caferoglu et al. 2025 (Sing-SQL), Cohen et al. 2025 (WixQA) (+35 more)

### Community 3 - "Report Generation Tests"
Cohesion: 0.07
Nodes (19): generate_benchmark_report(), Test report generation functionality, Setup test data and config, Test successful report generation, Test report generation without timing data, Test report generation with empty model results, Test report generation with only some metrics enabled, Test report renders Success@k / Hit Rate@k when enabled. (+11 more)

### Community 4 - "Benchmark CLI Pipeline"
Cohesion: 0.10
Nodes (32): add_forced_source_qrel(), apply_source_chunk_coverage(), configure_utf8_stdio(), extract_response_text(), generate_qrels(), generate_queries_from_corpus(), main(), normalize_unicode_text() (+24 more)

### Community 5 - "Dataset Report Utilities"
Cohesion: 0.12
Nodes (29): mock_chromadb_client_for_reports(), Avoid real ChromaDB calls in report tests., _capture_environment(), _discover_existing_visuals(), generate_benchmark_report(), generate_corpus_statistics_viz(), generate_timing_visualization(), generate_visualizations() (+21 more)

### Community 6 - "Query-Level Re-Evaluation"
Cohesion: 0.08
Nodes (28): main(), probe(), _rank_all(), Query-level re-evaluation via corpus re-embedding + exact squared-L2 kNN.  Why r, Return list of {query_id, ranked_ids, distances} for one model via     re-embedd, Faithful-reconstruction check: recomputed frozen-qrels aggregates vs published., retrieve_dataset(), run_gate() (+20 more)

### Community 7 - "Metric Indexing Tests"
Cohesion: 0.09
Nodes (18): Test metric indexing logic for report_utils.py This tests the core fix for dyna, Test when only recall is enabled, Test with only recall and precision enabled, Test the core metric indexing logic that was fixed in report_utils.py, Test when no metrics are enabled, Store original config values before each test, Test that metric order doesn't matter when some are disabled, Test edge case where middle metrics are disabled (+10 more)

### Community 8 - "ChromaDB and Candidate Pooling"
Cohesion: 0.11
Nodes (23): ChromaDB, build_qrels_candidate_pool(), Return {query_id: [(doc_id, text), ...]} candidate pool for LLM judging.      Wh, Test collection initialization when collection already exists, Hit-rate metric should default to 0.0 when accuracy@k is missing., Test that ChromaDB client is created successfully, Test collection initialization with mock data, Test the evaluation function with mock data (+15 more)

### Community 9 - "Model-Independent Pooled Qrels"
Cohesion: 0.14
Nodes (24): build_union(), fetch(), _job_for(), main(), plan(), Build model-INDEPENDENT pooled qrels to correct the M5 candidate-pool bias.  Pro, Return (corpus, queries, pool) where pool[qid][docid] = best rank across models., (qid, docid, best_rank) ordered by query then ascending best rank. (+16 more)

### Community 10 - "Bootstrap Uncertainty Tests"
Cohesion: 0.09
Nodes (13): Tests for the query-level uncertainty stage.  The property worth protecting is d, A relevant document past the cutoff must not count., AP is normalised by min(k, |R|), matching InformationRetrievalEvaluator., Same corpus, computed twice with unrelated work in between., Consuming one cell's stream must not shift another's.      This is the guarantee, The reason the paired column is the one that discriminates.      Two models with, _scored(), test_cell_rng_is_independent_of_draw_order() (+5 more)

### Community 11 - "Springer Template Compliance"
Cohesion: 0.13
Nodes (21): journal_paper/build.ps1 Lint/Build Gate, Codex Project Rules, Flat Folder Policy, Forbidden Preamble Constructs (SN010-SN012), TeX-First Manuscript Workflow, Manuscript Section Boundaries, Springer Declarations Contract (SN013-SN014), Springer Front Matter Contract (SN001-SN008) (+13 more)

### Community 12 - "Re-Analysis Shared Helpers"
Cohesion: 0.10
Nodes (18): embed_texts(), extract_response_text(), get_st_model(), judge_with_retry(), knn_rank(), load_expected_means(), open_collection(), parse_relevance_score() (+10 more)

### Community 13 - "Aggregate Report Charts"
Cohesion: 0.11
Nodes (18): calculate_average_ranks(), calculate_consistency_scores(), generate_aggregate_report(), generate_dataset_characteristics_chart(), generate_embedding_speed_heatmap(), generate_pairwise_significance_heatmap(), get_common_models(), Overview chart for dataset sizes (Documents (PDFs), chunks, queries, qrels). (+10 more)

### Community 14 - "Gemini LLM Integration"
Cohesion: 0.13
Nodes (16): Google Gemini AI, Test error handling when trying to generate content with an invalid API key, Test content generation succeeds with valid API response (using mocked client), Test client initialization when API key exists in .env file but not in system en, Test that API key from .env file is used even when a different key exists in sys, Integration test: Generate content using API key from .env file, ensuring system, Test behavior when API key is not found in either .env file or system environmen, test_api_error_with_invalid_key() (+8 more)

### Community 15 - "Corpora and Model Roster"
Cohesion: 0.17
Nodes (16): Conclusion Section, Dataset education_tr, Dataset law_tr, M2 all-mpnet-base-v2 (English), M3 paraphrase-multilingual-MiniLM-L12-v2, M4 all-MiniLM-L12-v2 (English), Experiments Section, Method Section (+8 more)

### Community 16 - "Manuscript Number Verification"
Cohesion: 0.17
Nodes (14): check_dataset_result_summary(), check_generated_fragments_present(), check_inline_paired_intervals(), check_scored_query_counts(), check_worked_example(), _load_raw(), Check the manuscript's hand-written numbers against the pipeline's artifacts., Paired intervals quoted in the results prose must match the bootstrap blocks. (+6 more)

### Community 17 - "Report Integration Tests"
Cohesion: 0.13
Nodes (8): Test report generation with all metrics enabled, Test report generation with only some metrics enabled (critical test for indexin, Test report with only recall enabled (edge case), Test that empty model results raise appropriate error, Test timing data validation handles invalid data gracefully, Test report_utils.py integration with proper metric indexing, Setup test data and config, TestReportUtilsIntegration

### Community 18 - "Research Questions and Evidence"
Cohesion: 0.18
Nodes (14): RQ1: Pipeline Utility, RQ3: Domain Sensitivity, RQ4: Operational Decision Support, Introduction Section, Model-Independent Pooled Qrels, Lewis et al. 2021 (RAG), Thakur et al. 2025 (TREC RAG Human vs LLM Judges), Query-Level Bootstrap Confidence Intervals (+6 more)

### Community 19 - "Aggregate Report Tests"
Cohesion: 0.22
Nodes (13): _build_datasets_fixture(), test_compute_weighted_query_latency_summary(), test_extract_query_latency_matrix(), compute_weighted_query_latency_summary(), extract_query_latency_matrix(), generate_query_latency_heatmap(), get_all_models(), Heatmap of query retrieval latency (ms/query) by model and dataset.     Lower v (+5 more)

### Community 20 - "Cross-Dataset Aggregation"
Cohesion: 0.15
Nodes (13): calculate_model_rankings(), generate_consistency_comparison_chart(), generate_cross_dataset_radar_chart(), generate_model_ranking_heatmap(), metric_header_name(), normalize_model_names(), Aggregate reporting utilities for cross-dataset performance comparison. Impleme, Grouped bar chart comparing consistency metrics across models.     Groups: coef (+5 more)

### Community 21 - "Bootstrap Interval Estimators"
Cohesion: 0.19
Nodes (14): cell_rng(), compute_dataset_bootstrap(), compute_pooled_bootstrap(), _dataset_key(), _metric_key(), _model_key(), paired_ci(), percentile_ci() (+6 more)

### Community 22 - "Metric Indexing Fixtures"
Cohesion: 0.17
Nodes (7): Test metric indexing with only some metrics enabled, Test when only recall is enabled, Test metric indexing fixes, Store original config values before each test, Restore original config values after each test, Test metric indexing when all metrics are enabled, TestMetricIndexing

### Community 23 - "Local RAG Pipeline Concepts"
Cohesion: 0.20
Nodes (11): Gemini 2.5 Flash-Lite, Automated Two-Layer Reporting, Local RAG Benchmarking Pipeline, ChromaDB Vector Store, Corpus Preparation (Chunking), Qrels (Relevance Judgment) Construction, LLM Query Generator Role, LLM-as-Judge (Relevance Judge Role) (+3 more)

### Community 24 - "Query-Level Uncertainty Core"
Cohesion: 0.29
Nodes (10): load_rankings(), per_query_metrics(), pooled_over_datasets(), rankings_path(), Query-level uncertainty estimation: the pipeline's statistical decision-support, Binary-relevance IR metrics for ONE query at cutoff k.      ranked_ids   : doc_i, Per-query and aggregate metrics for each model, from stored rankings + qrels., Score each dataset from its stored rankings, then pool. Returns (block, vectors) (+2 more)

### Community 25 - "Visualization Tests"
Cohesion: 0.20
Nodes (5): Test visualization generation functions, Test visualization generation, Test timing visualization generation, Test corpus statistics visualization, TestVisualizationFunctions

### Community 26 - "PDF Chunking and Splitting"
Cohesion: 0.33
Nodes (8): test_split_text_basic(), test_split_text_empty(), test_split_text_overlap(), test_split_text_small_input(), Loads all PDFs from a directory, splits their text into chunks, and returns a li, Split the text into smaller chunks for processing.          Args:         tex, split_pdfs_to_chunks(), split_text()

### Community 27 - "Qrels Generation Semantics Tests"
Cohesion: 0.50
Nodes (7): _batch_result(), _read_qrels_lines(), test_batch_fetch_adds_source_for_queries_missing_in_batch_results(), test_batch_fetch_deduplicates_when_source_already_positive(), test_batch_fetch_forces_source_even_when_all_llm_labels_zero(), test_non_batch_forces_source_and_deduplicates_candidates(), _write_queries_jsonl()

### Community 28 - "Report Print Utilities"
Cohesion: 0.25
Nodes (6): mock_chromadb_client_for_reports(), Test report_utils.py functionality, focusing on the metric indexing fixes and in, Test utility print functions work correctly, Avoid real ChromaDB calls in report tests., print_report_info(), Print information about generated report files.

### Community 29 - "Metric Indexing in Reports"
Cohesion: 0.25
Nodes (4): Test metric indexing within report generation context, Test the sorting logic used in report generation, Test various metric configuration scenarios, TestMetricIndexingInReportContext

### Community 30 - "Report Edge-Case Handling"
Cohesion: 0.25
Nodes (4): Test edge cases and error handling, Test with only one model result, Test with empty timing results list (not None), TestEdgeCasesAndErrorHandling

### Community 31 - "Console Output Tests"
Cohesion: 0.25
Nodes (6): print_report_info(), print_results_summary(), Test utility functions, Test results summary printing, Test report info printing, TestUtilityFunctions

### Community 32 - "Statistical Significance Testing"
Cohesion: 0.25
Nodes (8): check_aggregate_dependencies(), generate_win_tie_loss_matrix(), perform_friedman_test(), perform_pairwise_significance_tests(), Paired t-test for all model pairs across datasets.     Each dataset provides on, Win-Tie-Loss analysis across datasets.          Returns DataFrame showing wins, Friedman test for overall differences across multiple models and datasets., Check if required dependencies for aggregate reporting are installed.     Raise

### Community 33 - "Performance Distribution Charts"
Cohesion: 0.25
Nodes (8): generate_dataset_difficulty_chart(), generate_model_performance_heatmap(), generate_performance_distribution_plots(), metric_display_name(), Bar chart showing mean model performance per dataset.     Datasets sorted by me, Heatmap of model performance by dataset for a single metric.      Returns: Pat, Human-readable metric name for narrative text and titles., Box plot for score distributions across datasets.     One subplot per model sho

### Community 34 - "Bootstrap Artifact Persistence"
Cohesion: 0.25
Nodes (8): analysis_dir(), bootstrap_output_path(), excludes_zero(), datasets/<dataset>/analysis/ (created if missing). Never reports/., datasets/<dataset>/analysis/bootstrap_<variant>.json.      `variant` names the q, Compute and persist the per-corpus uncertainty block. Returns the block., run_dataset_stage(), _settings()

### Community 35 - "Dataset Configuration"
Cohesion: 0.29
Nodes (6): configure_for_dataset(), discover_available_datasets(), get_latest_raw_results(), Configures paths and variables for a specific dataset.     Args:         datas, Auto-discover datasets in datasets/ directory.     Returns list of dataset name, Find the most recent raw_results_{timestamp}.json for a dataset.     Returns ab

### Community 36 - "Frozen-Snapshot Bootstrap CLI"
Cohesion: 0.53
Nodes (5): main(), qrels_path(), Frozen-snapshot bootstrap CLI for the alternative qrels variants.  The uncertain, run(), zero_marker()

### Community 37 - "Language Sensitivity and Indexing"
Cohesion: 0.40
Nodes (6): M1 all-MiniLM-L6-v2 (English), M5 paraphrase-multilingual-mpnet-base-v2, RQ2: Language Sensitivity, Per-Model Embedding Index Construction, Language Effect, SentenceTransformers

### Community 38 - "Effect Size and Aggregation"
Cohesion: 0.33
Nodes (6): aggregate_model_performance(), calculate_effect_sizes(), extract_model_scores_across_datasets(), Extract scores for one model/metric across all datasets.     Returns: {"educati, Compute aggregate statistics per model across datasets.          Returns struc, Cohen's d effect size for model comparison.          Returns:     {

### Community 39 - "Model Alias Mapping"
Cohesion: 0.33
Nodes (6): label_for(), label_map(), model_names(), Full sentence-transformers model names in configured order., Return the M1..M5 label for a full sentence-transformers model name., {full model name: M1..M5}.

### Community 40 - "Metric Compatibility Validation"
Cohesion: 0.50
Nodes (5): test_metric_compatibility_includes_hit_rate(), get_common_metrics(), Check metric flag consistency across datasets.     Returns validation report wi, Identify metrics enabled in ALL datasets.     Returns: ["map", "recall", "ndcg", validate_metric_compatibility()

### Community 41 - "Raw Results Loading"
Cohesion: 0.50
Nodes (4): load_dataset_results(), load_multiple_datasets(), Load most recent raw_results JSON for a dataset.     Returns None if not found, Load results for multiple datasets.     Uses config.discover_available_datasets

## Knowledge Gaps
- **69 isolated node(s):** `Corpus Preparation (Chunking)`, `Automated Two-Layer Reporting`, `Reproducibility (Frozen Artifacts)`, `Consistency Diagnostics (CV, Worst Drop, Score Range)`, `M2 all-mpnet-base-v2 (English)` (+64 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Experiments Section` connect `Corpora and Model Roster` to `Language Sensitivity and Indexing`, `Local RAG Pipeline Concepts`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `Related Work Section` connect `Related Work Bibliography` to `Research Questions and Evidence`, `Corpora and Model Roster`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `M1 all-MiniLM-L6-v2 (English)` connect `Language Sensitivity and Indexing` to `Corpora and Model Roster`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **What connects `Citation audit (A24): cited keys vs refs.bib entries; missing/unused/incomplete.`, `Build model-INDEPENDENT pooled qrels to correct the M5 candidate-pool bias.  Pro`, `Return (corpus, queries, pool) where pool[qid][docid] = best rank across models.` to the rest of the system?**
  _290 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Journal Figure Generation` be split into smaller, more focused modules?**
  _Cohesion score 0.1025974025974026 - nodes in this community are weakly interconnected._
- **Should `Reviewer-Driven Re-Analysis` be split into smaller, more focused modules?**
  _Cohesion score 0.06161616161616162 - nodes in this community are weakly interconnected._
- **Should `Related Work Bibliography` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._