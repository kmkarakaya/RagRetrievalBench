# Method

## Pipeline

The benchmark follows the repository pipeline implemented in `rag_benchmark.py` and is designed as tooling for developer decision support. [Rag_Benchmark_Py]
1. Prepare corpus from dataset PDFs.
2. Generate synthetic queries from sampled chunks.
3. Generate qrels via LLM-based relevance judgments over retrieved candidates.
4. Initialize per-model vector collections.
5. Evaluate retrieval metrics and timing.
6. Generate per-dataset benchmark reports (markdown/pdf + visualizations).
7. Generate aggregate cross-dataset comparison reports.

Datasets are isolated by `--dataset` routing and `configure_for_dataset()` in `config.py`.
[Config_Py]

Pipeline purpose statement:
- enable selection of the best suitable embedding model for user/application requirements using local data and operational constraints.

## Frozen Configuration Used in This Manuscript

The manuscript uses one fixed snapshot from 2026-03-05 and does not mix run timestamps.

Primary settings:
- `k = 10`
- `chunk_size = 1000`
- `chunk_overlap = 200`
- `candidate_pool_size = 20`
- `document_batch_size = 32`
- `reinitialize_collections = True`
- `n_queries = 50`
- `qrels_embedding_model_index = 4` (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`)
- `llm_model = models/gemini-2.5-flash-lite`

Evidence sources:
- `config.py` [Config_Py]
- Raw JSON `config` blocks:
  - `datasets/education_eng/reports/raw_results_2026-03-05_11-27-28.json` [Raw_Education_Eng_2026_03_05]
  - `datasets/education_tr/reports/raw_results_2026-03-05_11-29-07.json` [Raw_Education_Tr_2026_03_05]
  - `datasets/law_tr/reports/raw_results_2026-03-05_11-30-27.json` [Raw_Law_Tr_2026_03_05]

## Evaluated Embedding Models

Model list (exact naming as configured):
1. `sentence-transformers/all-MiniLM-L6-v2`
2. `sentence-transformers/all-mpnet-base-v2`
3. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
4. `sentence-transformers/all-MiniLM-L12-v2`
5. `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

Demonstration setup statement:
- this journal paper is demonstrated with 3 datasets and 5 models.

## Metrics and Operational Measurements

Retrieval metrics:
- `MAP@10`
- `Recall@10`
- `Precision@10`
- `NDCG@10`
- `MRR@10`
- `Success@10`

Operational measurements:
- Embedding time and throughput (`chunks/sec`)
- Average query retrieval latency (`ms/query`)

These outputs are intended to support cross-dataset comparison for dataset-specific model selection.

## Statistical and Aggregate Analysis

The aggregate report includes:
- Cross-dataset ranking by MAP
- Coefficient of variation (CV) and stability summaries
- Paired t-tests and effect-size reporting
- Friedman test
- Cross-dataset visual summaries (heatmaps, radar chart, consistency chart)

Canonical aggregate artifact:
- `aggregated_reports/2026-03-05_11-32-49/aggregate_report.md` [Aggregate_Report_2026_03_05]

Reporting utility statement:
- the pipeline produces automatic benchmarking reports across various metrics and well-structured dynamic report outputs (timestamped markdown/pdf + visualizations).

## Reproducibility Controls

- Fixed frozen run IDs are documented in `journal_paper/plan.md`.
- Numeric values in manuscript sections must be taken from frozen aggregate/raw artifacts.
- If new runs are introduced, snapshot IDs and all dependent numeric statements must be updated before manuscript edits continue.
- Dataset curation provenance is fixed for this draft:
  - Education datasets source: `https://www.tedu.edu.tr/en/regulations-and-guidelines-education` (retrieved 01/01/2026) [TED_Regulations]
  - Law dataset source: `https://www.bddk.org.tr/Mevzuat/Liste/49` (retrieved 01/01/2026) [BDDK_Mevzuat]
- The implementation is publicly available and pipeline reusable by any developer: `https://github.com/kmkarakaya/RagRetrievalBench.git`. [GitHub_RagRetrievalBench]
