# RAG Retrieval Benchmark

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](<https://img.shields.io/badge/code%20style-black-000000.svg>)](https://github.com/psf/black)

**Owner: Murat Karakaya**

- Website: [www.muratkarakaya.net](https://www.muratkarakaya.net)
- YouTube: [Murat Karakaya Akademi](https://www.youtube.com/@MuratKarakayaAkademi)

A comprehensive evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. This tool provides automated benchmarking of embedding models using real document collections, synthetic query generation, and standardized information retrieval metrics.

## 🚀 Features

- **Automated PDF Processing**: Extract and chunk documents from PDF files
- **LLM-Powered Query Generation**: Generate realistic queries using Google Gemini AI
- **Intelligent Relevance Assessment**: Automated qrels generation with LLM evaluation
- **Multi-Model Comparison**: Benchmark multiple SentenceTransformers embedding models simultaneously
- **Cross-Dataset Analysis**: Compare embedding model performance across multiple datasets with statistical significance testing
- **Comprehensive Metrics**: MAP, Recall, Precision, NDCG, MRR, and Success/Hit Rate evaluation
- **Query-Level Uncertainty**: Per-corpus bootstrap confidence intervals, with paired intervals against each corpus's leading model, so you can tell which parts of a ranking the data actually resolves
- **Statistical Analysis**: Paired t-tests, Cohen's d effect sizes, Friedman test, and consistency metrics
- **Batch Processing Support**: Cost-effective asynchronous processing for large datasets
- **Persistent Timing Data**: Timing metrics saved between pipeline runs for accurate performance tracking
- **Professional Reporting**: Automated generation of markdown and PDF reports with visualizations
- **Aggregate Reporting**: Cross-dataset comparison reports with 14+ statistical visualizations
- **Publication Artifacts**: Manuscript figures and LaTeX data tables generated from run outputs rather than transcribed
- **One-Command Builds**: `--build-all` runs every stage in order and skips whatever is already done
- **ChromaDB Integration**: Efficient vector storage and retrieval
- **Modular Pipeline**: Run individual components or complete end-to-end evaluation
- **Multi-Dataset Support**: Run benchmarks on multiple datasets with complete isolation

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Pipeline Components](#-pipeline-components)
- [Evaluation Metrics](#-evaluation-metrics)
- [Output Files](#-output-files)
- [Development Tools](#-development-tools)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🛠 Installation

### Prerequisites

- Python 3.10+
- Google AI API key (for Gemini integration)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/RagRetrievalBench.git
cd RagRetrievalBench
```

2. Create and activate a virtual environment:

```bash
# Using conda (recommended)
conda create -n ragbenchmark python=3.10
conda activate ragbenchmark

# Using venv
python -m venv ragbenchmark
ragbenchmark\Scripts\activate  # Windows
source ragbenchmark/bin/activate  # Linux/macOS
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Copy the template
cp .env.template .env

# Edit .env with your editor and replace 'your_api_key_here'
notepad .env  # Windows
nano .env     # Linux/macOS
```

5. Configure your evaluation settings in `config.py`

### Additional Requirements for PDF Report Generation

To generate reports in PDF format, you need to install:

1. **Pandoc**: Download from [Pandoc&#39;s official website](https://pandoc.org/installing.html)
2. **LaTeX Distribution**: Download MikTeX from [MikTeX&#39;s official website](https://miktex.org/download)

After installing these tools, the framework generates PDF reports automatically alongside the markdown ones. Without them the markdown reports are still produced; only the PDF step is skipped.

Conversion goes through `utils/pandoc_header.tex`, a small LaTeX preamble injected into every pandoc run. It works around a `longtable` bug that otherwise aborts the build on any report containing a table that spans a page break, and declares the Unicode characters the reports use. Do not remove it.

## ⚡ Quick Start

### 🧭 Bring Your Own Dataset (end-to-end)

Run the whole pipeline on **your own documents** and get a per-dataset report, a cross-dataset aggregate report, and publication-ready figures and tables. Replace `mydata` with any name you like.

**One command.** `--build-all` runs every stage in order and skips whatever is already done, so it is safe to re-run:

```bash
conda activate ragbenchmark          # ChromaDB's native index requires this env (see note below)

mkdir -p datasets/mydata/pdfs
cp /path/to/your/*.pdf datasets/mydata/pdfs/

python rag_benchmark.py --dataset mydata --build-all --batch-submit
```

The two LLM stages (query generation and relevance judging) submit Gemini Batch jobs and cannot finish in one pass. `--build-all` stops at each one and prints the command to resume with once the job completes:

```bash
python rag_benchmark.py --dataset mydata --build-all --batch-fetch <BATCH_ID>
```

After the second batch completes, the remaining stages — indexing, evaluation, uncertainty estimation, the dataset report, the aggregate report, and the manuscript figures and tables — all run in one shot.

**Or run the stages yourself**, which is the same sequence `--build-all` performs:

```bash
# 1) Chunk the PDFs into a corpus (no LLM, fast)
python rag_benchmark.py --dataset mydata --prepare-corpus

# 2) Generate synthetic queries (LLM; batch recommended for >10 queries)
python rag_benchmark.py --dataset mydata --generate-queries --batch-submit
#    ...wait for the job, then fetch with the printed BATCH_ID:
python rag_benchmark.py --dataset mydata --generate-queries --batch-fetch <BATCH_ID>

# 3) Build model-independent pooled relevance judgments (LLM; batch recommended)
#    Unions each model's top candidates, LLM-judges the union, stores 0/1 labels.
python rag_benchmark.py --dataset mydata --generate-qrels --batch-submit
python rag_benchmark.py --dataset mydata --generate-qrels --batch-fetch <BATCH_ID>

# 4) Embed all models, evaluate, estimate uncertainty, write the report and figures
python rag_benchmark.py --dataset mydata --initialize --evaluate
```

**Step 4 produces**, under `datasets/mydata/reports/`:

- `raw_results_<ts>.json` — machine-readable results (metrics, timing, full config, environment snapshot)
- `mydata_benchmark_report_<ts>.md` and `.pdf` — the human-readable dataset report, including a **Query-Level Uncertainty** section
- per-metric PNG charts (MAP, Recall, Precision, NDCG, MRR, Success, timing, corpus stats)

and under `datasets/mydata/analysis/`:

- `rankings_<Mn>.jsonl` — each model's per-query ranked list, kept so the statistics can be recomputed without re-embedding
- `bootstrap_frozen.json` — per-corpus confidence intervals

**About the uncertainty section.** Point estimates alone do not say whether your corpus actually separates two models. The report gives each model a *marginal* interval and, against the corpus's own leading model, a *paired* interval. The paired one is what decides: two marginal intervals can overlap heavily while the paired difference still excludes zero. When a model is **not** separated from the leader, choose on latency instead of quality. Resampling is seeded per (corpus, model, metric), so evaluating one dataset gives exactly the same intervals as evaluating all of them. Turn it off with `compute_bootstrap = False`, or recompute it alone with:

```bash
python rag_benchmark.py --dataset mydata --bootstrap
```

**Compare several datasets.** Repeat the steps for each dataset (`mydata2`, `mydata3`, …), then:

```bash
python rag_benchmark.py --generate-aggregate-report
```

This writes a cross-dataset comparison report + ~20 comparison figures (radar chart, ranking/performance heatmaps, dataset-difficulty, consistency, per-metric distributions) to `aggregated_reports/<timestamp>/`, together with the pooled aggregate uncertainty layer.

**Paper artifacts.** The manuscript's figures and data tables are generated from these same run outputs rather than typed by hand:

```bash
python rag_benchmark.py --journal-figures   # results_*.png into journal_paper/
python rag_benchmark.py --paper-tables      # tbl_*.tex fragments the manuscript \inputs
python rag_benchmark.py --verify-paper      # check remaining hand-written numbers; non-zero on drift
```

**Small corpus / no batch access?** Drop the `--batch-*` flags to run synchronously, or run everything at once:

```bash
python rag_benchmark.py --dataset mydata --all      # prepare → queries → qrels → init → evaluate (synchronous LLM)
```

> `--all` uses **synchronous** LLM calls, which the Gemini free tier throttles after a few requests. For anything beyond a tiny corpus, use the batch steps above with a **billing-enabled** key (the free tier disables the Batch API).

> **Run in the `ragbenchmark` conda environment.** ChromaDB's native index (`add`/`query`) works there. Do not run the pipeline from a plain `base` environment: on some machines it can crash while loading the persisted native index; if a run segfaults, first confirm the active env (`python -c "import sys; print(sys.executable)"`).

### The Full Stage Sequence

`--build-all` runs exactly this order. Run the stages yourself when you want to inspect or repeat one of them:

| # | Stage | Command | LLM? |
|---|---|---|---|
| 1 | Corpus | `--prepare-corpus` | no |
| 2 | Queries | `--generate-queries` | **yes** |
| 3 | Qrels | `--generate-qrels` | **yes** |
| 4 | Index | `--initialize` | no |
| 5 | Evaluate | `--evaluate` | no |
| 6 | Uncertainty | runs inside `--evaluate`; alone with `--bootstrap` | no |
| 7 | Dataset report | runs inside `--evaluate`; alone with `--regenerate-report` | no |
| 8 | Aggregate report | `--generate-aggregate-report` | no |
| 9 | Paper artifacts | `--journal-figures`, `--paper-tables` | no |

```bash
conda activate ragbenchmark

# Stages 1-3 with the Batch API (recommended for anything beyond a tiny corpus)
python rag_benchmark.py --dataset finance --prepare-corpus
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
python rag_benchmark.py --dataset finance --generate-qrels --batch-submit
python rag_benchmark.py --dataset finance --generate-qrels --batch-fetch <BATCH_ID>

# Stages 4-7 in one go: index, evaluate, uncertainty, dataset report
python rag_benchmark.py --dataset finance --initialize --evaluate
```

Drop `--batch-submit` / `--batch-fetch` to run stages 2-3 synchronously. That is fine for a handful of queries and needs no billing-enabled key, but the Gemini free tier throttles it quickly.

`--initialize` and `--evaluate` can also be run separately; timing data from initialization is saved and reloaded so the report stays accurate:

```bash
python rag_benchmark.py --dataset finance --initialize
python rag_benchmark.py --dataset finance --evaluate
```

**Note**: `--initialize`, `--evaluate`, `--all`, `--build-all`, `--bootstrap`, and `--regenerate-report` all require `--dataset`.

### Re-running Stages Without Re-embedding

Indexing and evaluation are the expensive stages. These three rebuild downstream outputs from artifacts already on disk, so none of them re-embeds the corpus or calls an LLM:

```bash
# Recompute the confidence intervals only
python rag_benchmark.py --dataset finance --bootstrap

# Rebuild the dataset report in place, keeping its original filename, timestamp and
# figures, and writing no new raw_results file. Use it to pick up report changes
# without disturbing a completed run.
python rag_benchmark.py --dataset finance --regenerate-report
```

### Cross-Dataset Aggregate Reporting

Compare embedding model performance across multiple datasets with statistical analysis. Needs at least `aggregate_min_datasets` evaluated datasets:

```bash
# Evaluate several datasets first
python rag_benchmark.py --dataset education --initialize --evaluate
python rag_benchmark.py --dataset finance --initialize --evaluate
python rag_benchmark.py --dataset legal --initialize --evaluate

# Generate the aggregate comparison report over all discovered datasets
python rag_benchmark.py --generate-aggregate-report

# Restrict to specific datasets (COMMA-separated, no spaces)
python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education,finance

# Restrict to specific metrics, and choose the output location
python rag_benchmark.py --generate-aggregate-report --aggregate-metrics map,ndcg
python rag_benchmark.py --generate-aggregate-report --aggregate-output-dir ./my_reports
```

Output lands in `aggregated_reports/<timestamp>/`: a comparison report, ~20 figures, and the pooled query-level uncertainty layer.

### Publication Artifacts

The manuscript in `journal_paper/` takes its figures and data tables from the pipeline rather than from hand-typed numbers. Regenerate them after any evaluation:

```bash
python rag_benchmark.py --journal-figures   # results_*.png into journal_paper/
python rag_benchmark.py --paper-tables      # tbl_*.tex fragments the manuscript \inputs
python rag_benchmark.py --verify-paper      # check remaining hand-written numbers; non-zero on drift
```

`--paper-tables` writes one `tbl_<name>.tex` per data table, containing only a `tabular` environment; captions and labels stay in the hand-authored `.tex` sections. `--verify-paper` is a release gate: it exits non-zero if any number still typed by hand disagrees with the run artifacts.

### Your Datasets vs. the Manuscript's Datasets

There are two independent selections, and confusing them is the easiest mistake to make:

| Selection | Set where | Controls |
|---|---|---|
| `--dataset <name>` | per command | Which corpus a pipeline stage runs on. Always explicit. |
| `paper_datasets` | `config.py`, once | Which corpora the **manuscript** artifacts are built from. |

`paper_datasets` governs **only** `--journal-figures` and `--paper-tables` — the `results_*.png` and `tbl_*.tex` files the paper `\input`s, including its per-corpus and pooled confidence-interval tables. It does **not** restrict anything else: every dataset still gets its own report, and the standalone aggregate report covers whatever you point it at with `--aggregate-datasets` (or everything evaluated).

That separation is what lets you add corpora freely without disturbing a paper build.

**Benchmarking your own corpora, not writing this paper.** Set `paper_datasets = None`. The manuscript stages then cover everything you have evaluated — or simply never run them; they exist only to build the paper.

```python
paper_datasets = None      # config.py
```

```bash
python rag_benchmark.py --dataset mydata --build-all --batch-submit
python rag_benchmark.py --generate-aggregate-report     # all your datasets
```

**Reproducing or extending the published results.** Leave `paper_datasets` at the three published corpora. Add as many of your own datasets as you like: each gets a full report, and they appear in the aggregate report, but they can never leak into the manuscript.

```python
paper_datasets = ["education_eng", "education_tr", "law_tr"]   # unchanged
```

```bash
python rag_benchmark.py --dataset mydata --build-all --batch-submit   # safe
python rag_benchmark.py --paper-tables                                # still exactly 13 fragments
```

**Writing a paper about your own corpora.** Point both settings at your datasets. `paper_comparisons` names the corpus pairs you want side-by-side comparison tables for; empty the list if no pair isolates a factor you care about.

```python
paper_datasets = ["legal_tr", "legal_eng"]
paper_comparisons = [
    ("language_effect_comparison", "legal_eng", "legal_tr", r"eng $\to$ tr", False),
]
```

If `paper_datasets` names a dataset that has not been evaluated, the artifact stages stop with an explicit error rather than silently producing a partial paper.

### ⚡ Batch Processing (Optional)

For large datasets, use the Gemini Batch API to reduce costs (50% cheaper) and avoid rate limits. Batch processing is recommended when:

- You have more than 10 queries to generate
- You want to minimize API costs
- You need to process large amounts of data asynchronously
- You want to avoid hitting rate limits during peak hours

**How Batch Processing Works:**

1. **Submit Phase**: Upload your requests to Google's Batch API and get a job ID
2. **Processing Phase**: Google processes your requests asynchronously (can take minutes to hours)
3. **Fetch Phase**: Download the results when processing is complete

**Important Notes:**

- Batch jobs are processed asynchronously - you can check status anytime
- Results are saved to your dataset's `reports/` directory
- Use `--batch_status` to monitor job progress (shows all datasets when no --dataset specified)
- Batch processing costs ~50% less than real-time API calls
- The Batch API requires a **billing-enabled** Google AI key; it is disabled on the free tier (which also throttles synchronous calls after a few requests)

**Phase 1: Query Generation (Batch Mode)**

```bash
# Submit batch job for query generation (specify dataset for isolation)
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
# Output: "Batch submitted successfully! Job Name: projects/.../locations/.../batchJobs/.../<BATCH_ID>"

# Check status (optional, shows all datasets if no --dataset specified)
python rag_benchmark.py --batch_status

# Fetch results when ready (use the BATCH_ID from submit output)
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
```

**Phase 2: Relevance Judgments (Batch Mode)**

```bash
# Submit batch job for qrels generation (specify dataset for isolation)
python rag_benchmark.py --dataset finance --generate-qrels --batch-submit

# Check status (optional)
python rag_benchmark.py --batch_status

# Fetch results when ready
python rag_benchmark.py --dataset finance --generate-qrels --batch-fetch <BATCH_ID>
```

**Cancelling Batch Jobs**
If you need to cancel a running batch job:

```bash
# Cancel a specific batch job
python rag_benchmark.py --batch-cancel <BATCH_ID>
```

**For Specific Datasets:**

```bash
# All batch commands work with --dataset flag
python rag_benchmark.py --dataset finance --generate-queries --batch-submit
python rag_benchmark.py --dataset finance --batch_status
python rag_benchmark.py --dataset finance --generate-queries --batch-fetch <BATCH_ID>
python rag_benchmark.py --dataset finance --batch-cancel <BATCH_ID>

# Check all datasets (run without --dataset)
python rag_benchmark.py --batch_status
```

## ⚙ Configuration

Edit `config.py` to customize your evaluation:

```python
# Embedding models to evaluate
embedding_models = [
    {"model_name": "sentence-transformers/all-MiniLM-L6-v2", "collection_name": "coll_v1"},
    {"model_name": "sentence-transformers/all-mpnet-base-v2", "collection_name": "coll_v2"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "collection_name": "coll_v3"},
    {"model_name": "sentence-transformers/all-MiniLM-L12-v2", "collection_name": "coll_v4"},
    {"model_name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2", "collection_name": "coll_v5"}
]

# Metrics configuration
compute_map = True       # Mean Average Precision
compute_recall = True    # Recall@K
compute_precision = True # Precision@K
compute_mrr = True       # Mean Reciprocal Rank
compute_ndcg = True      # Normalized Discounted Cumulative Gain
compute_hit_rate = True  # Success@K / Hit Rate@K

# Evaluation settings
k = 10
mrr_at_k = [k]
precision_recall_at_k = [k]
map_at_k = [k]
ndcg_at_k = [k]

# Document processing
pdf_dir = "utils/pdfs"  # Default PDF directory (used when no --dataset specified)
chunk_size = 1000
chunk_overlap = 200

# Query generation
n_queries = 50            # synthetic queries per dataset
chunks_per_query = 1
candidate_pool_size = 20  # top-k retrieved per model for the judged candidate pool

# Benchmark-construction controls
random_seed = 42                    # reproducible seed-chunk sampling and bootstrap (None disables)
qrels_pooling = True                # True: union candidates across ALL models (model-independent, unbiased)
                                    # False: legacy single-model pool via qrels_embedding_model_index
qrels_store_negatives = True        # store explicit 0 (non-relevant) rows alongside 1s (auditable)
force_source_chunk_relevant = False # False: judge each query's seed chunk like any other candidate
qrels_embedding_model_index = 4     # only used when qrels_pooling = False (0-based)

# Query-level uncertainty stage
compute_bootstrap = True            # emit per-corpus confidence intervals with the dataset report
bootstrap_resamples = 10000         # B: number of bootstrap resamples
bootstrap_confidence = 0.95         # interval coverage

# Which datasets feed the manuscript artifacts (--journal-figures, --paper-tables).
# Pinning them keeps a paper build deterministic. None/[] = use every evaluated dataset.
paper_datasets = ["education_eng", "education_tr", "law_tr"]

# Corpus pairs to emit as manuscript comparison tables (--paper-tables).
# Empty by default: a pairwise comparison only means something once you have decided
# which two corpora isolate the factor you care about.
paper_comparisons = [
    ("language_effect_comparison", "education_eng", "education_tr", r"eng $\to$ tr", False),
    ("turkish_domain_comparison",  "education_tr",  "law_tr", r"law $\!-\!$ education", True),
]

# LLM settings
llm_model = "models/gemini-2.5-flash-lite"
temperature = 0.1
llm_timeout = 0.01  # Adjust to avoid rate limits for your API tier

# ChromaDB settings
show_progress_bar = True
document_batch_size = 32
reinitialize_collections = True
hnsw_space = "l2"        # ChromaDB distance space ("l2" default, or "cosine")
log_environment = True   # record Python/library/device snapshot in raw_results JSON
```

**Note**: Currently, only SentenceTransformers models are supported. Ensure model names follow the format 'sentence-transformers/model-name'.

### Aggregate Reporting Settings

These settings control cross-dataset reporting (see `config.py` for full list):

```python
aggregate_results_dir = "aggregated_reports"
aggregate_statistical_tests = True
aggregate_generate_visualizations = True
aggregate_significance_level = 0.05
aggregate_min_datasets = 2
aggregate_require_identical_metrics = False
```

### Dataset-Specific Paths

When running with `--dataset <name>`, `configure_for_dataset()` updates:

- `pdf_dir` → `datasets/<name>/pdfs/`
- `reports_dir` → `datasets/<name>/reports/`
- `chroma_db_path` → `datasets/<name>/chromadb_collections/`
- Collection names are prefixed with the dataset name to avoid collisions

### Multi-Dataset Support

The framework supports running benchmarks on multiple datasets with complete isolation:

- Use `--dataset <name>` to specify a dataset (e.g., `--dataset finance`)
- Each dataset gets its own directory under `datasets/<name>/`
- Place PDF files in `datasets/<name>/pdfs/`
- All outputs (corpus, queries, qrels, reports, ChromaDB collections) are isolated per dataset
- If no `--dataset` is specified, only `--prepare-corpus`, `--generate-queries`, `--generate-qrels`, and batch status use default paths; `--initialize`, `--evaluate`, and `--all` require `--dataset`

## 📖 Usage

### Command Line Arguments

| Argument                          | Description                                                                            |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| `--dataset <name>`              | Target dataset. Required for every stage flag below except the aggregate and paper-artifact ones |
| `--build-all`                   | Run every stage in order, skipping what is already done; pauses at each Batch API stage with a resume command |
| `--prepare-corpus`              | Extract and chunk PDF documents                                                        |
| `--generate-queries`            | Generate evaluation queries from corpus                                                |
| `--generate-qrels`              | Create relevance judgments using LLM                                                   |
| `--initialize`                  | Build embedding collections in ChromaDB                                                |
| `--evaluate`                    | Run retrieval evaluation, uncertainty estimation, and the dataset report               |
| `--all`                         | Execute the pipeline end-to-end using **synchronous** LLM calls (no Batch API)         |
| `--bootstrap`                   | Recompute per-corpus confidence intervals from stored rankings only                    |
| `--regenerate-report`           | Rebuild the dataset report in place from stored results; writes no new raw_results file |
| `--generate-aggregate-report`   | Generate cross-dataset comparison report with statistical analysis (includes PDF)      |
| `--aggregate-datasets <list>`   | Comma-separated datasets for aggregate analysis, e.g. `education,finance` (default: auto-discover) |
| `--aggregate-output-dir <path>` | Custom output directory for aggregate reports (default: aggregated_reports/)           |
| `--aggregate-metrics <list>`    | Comma-separated metrics for aggregate analysis, e.g. `map,ndcg` (default: all enabled) |
| `--journal-figures`             | Regenerate the manuscript figures into `journal_paper/`                                |
| `--paper-tables`                | Regenerate the manuscript data tables as `tbl_*.tex` fragments                         |
| `--verify-paper`                | Check hand-written manuscript numbers against run artifacts; exits non-zero on drift   |
| `--batch-submit`                | Submit tasks to Gemini Batch API                                                       |
| `--batch-fetch <ID>`            | Fetch results from Batch API job                                                       |
| `--batch_status`                | List all batch jobs and their statuses (across all datasets if no --dataset specified) |
| `--batch-cancel <ID>`           | Cancel a specific Batch Job                                                            |

### Input Requirements

1. **PDF Documents**: Place your PDF files in `datasets/<name>/pdfs/` directory (when using `--dataset`) or `utils/pdfs/` (default for corpus/query/qrels generation)
2. **API Key**: Set up your Google AI API key in `.env` file
3. **Configuration**: Adjust settings in `config.py`

## 🔧 Pipeline Components

### 1. Document Processing (`--prepare-corpus`)

- **Input**: PDF files in `datasets/<name>/pdfs/` when using `--dataset`, or `utils/pdfs/` for default paths
- **Process**: Text extraction and chunking using RecursiveCharacterTextSplitter
- **Output**: `corpus.jsonl` with structured document chunks
- **Features**: Configurable chunk size/overlap, automatic text cleaning

### 2. Query Generation (`--generate-queries`)

- **Input**: Document corpus
- **Process**: LLM-powered question generation from random document chunks
- **Output**: `queries.jsonl` with realistic evaluation queries
- **Quality**: Temperature-controlled generation for consistency

### 3. Relevance Assessment (`--generate-qrels`)

- **Input**: Queries and document corpus
- **Process**:
  1. **Model-independent pooling** — for each query, union the top-`candidate_pool_size` chunks retrieved by *every* embedding model (deduplicated), so the ground truth does not privilege any single evaluated model. Set `qrels_pooling = False` for the legacy single-model pool (`qrels_embedding_model_index`).
  2. LLM binary relevance judging over the pooled candidates, with structured JSON parsing
  3. Rate-limited synchronous calls or the Gemini Batch API; the query's own seed chunk is judged normally unless `force_source_chunk_relevant = True`
- **Output**: `qrels.tsv` as `query_id <TAB> doc_id <TAB> label`, with positive (`1`) and, when `qrels_store_negatives = True`, explicit negative (`0`) judgments. The evaluator scores against the positives; negatives are retained so non-relevant decisions are auditable.

### 4. Collection Initialization (`--initialize`)

- **Input**: Document corpus and embedding models (requires `--dataset`)
- **Process**:
  1. Generate embeddings using SentenceTransformers (currently the only supported embedding library)
  2. Store in ChromaDB collections with batch processing
  3. Performance timing and throughput measurement
- **Output**: ChromaDB collections in `datasets/<name>/chromadb_collections/`

### 5. Evaluation & Reporting (`--evaluate`)

- **Input**: Corpus, queries, qrels, and ChromaDB collections (requires `--dataset`)
- **Process**:
  1. Load persisted timing data from previous initialization runs
  2. Multi-model retrieval evaluation with comprehensive metrics
  3. Persist each model's per-query ranked list to `datasets/<name>/analysis/rankings_<Mn>.jsonl`
  4. Generate timing data for any missing models
  5. Save updated timing data for future runs
  6. Save structured raw results JSON for aggregate analysis
- **Output**:
  - Performance reports (markdown and PDF) named `<dataset>_benchmark_report_*.md/.pdf`
  - Visualization charts (PNG format)
  - Detailed timing analysis
  - Raw results JSON for cross-dataset comparison
  - Per-query ranking files, which make stage 6 possible without re-embedding
- **Features**: Persistent timing data allows running `--initialize` and `--evaluate` separately

### 6. Query-Level Uncertainty (runs inside `--evaluate`; alone via `--bootstrap`)

- **Input**: The per-query ranking files from stage 5, plus `qrels.tsv`
- **Process**:
  1. Recompute per-query metric values from the stored rankings (no re-embedding, no LLM)
  2. **Marginal** interval per model per metric — a percentile bootstrap over the corpus's queries
  3. **Paired** interval against the corpus's own leading model, resampling the per-query *differences*
  4. Each `(corpus, model, metric)` cell draws from an independently derived random stream
- **Output**: `datasets/<name>/analysis/bootstrap_frozen.json`, and a **Query-Level Uncertainty** section in the dataset report
- **Why both intervals**: marginal intervals carry the corpus's shared query difficulty, so they are wide and overlap between models. The paired interval cancels that shared component and is the one that discriminates — two marginal intervals can overlap heavily while the paired difference still excludes zero. A model that is *not* separated from the leader should be chosen on operational cost, not quality.
- **Determinism**: because the streams are seeded per cell rather than consumed in traversal order, evaluating one dataset yields exactly the same intervals as evaluating all of them, and disabling a metric does not shift the others
- **Config**: `compute_bootstrap`, `bootstrap_resamples`, `bootstrap_confidence`, seeded from `random_seed`

### 7. Aggregate Analysis (`--generate-aggregate-report`)

- **Input**: Raw results JSON from multiple dataset evaluations
- **Process**:
  1. Load and validate results from multiple datasets
  2. Perform statistical analysis (paired t-tests, Cohen's d, Friedman test)
  3. Calculate model rankings and consistency metrics
  4. Compute the pooled query-level uncertainty layer across all corpora
  5. Generate 14+ statistical visualizations
  6. Create comprehensive cross-dataset comparison report
- **Output**:
  - Aggregate comparison report (markdown and PDF)
  - Statistical analysis visualizations
  - Model ranking heatmaps and radar charts
  - Dataset difficulty analysis
  - Pooled confidence intervals over every scored query
- **Note on the pooled estimator**: it is a query-weighted mean over all corpora, not the unweighted macro mean of the per-corpus means reported elsewhere in the same document, so the two aggregate figures for one model differ slightly. It is also **unstratified** — resampling does not preserve each corpus's share of the queries, so composition variance widens the intervals. Because a deployment targets one corpus at a time, the **per-corpus report remains the primary artifact** for model selection.
- **Features**: Automated dataset discovery, statistical significance testing, publication-ready analysis

### 8. Publication Artifacts (`--journal-figures`, `--paper-tables`, `--verify-paper`)

- **Input**: the latest `raw_results_*.json` per dataset, the qrels, and the uncertainty blocks — all auto-discovered
- **Process**:
  1. `--journal-figures` rebuilds the paper-ready figures (cross-dataset MAP@10, per-dataset metric profiles, quality–speed tradeoff, bootstrap forest plot) with consistent styling and anonymized `M1`–`M5` labels
  2. `--paper-tables` emits each manuscript data table as a `tabular`-only LaTeX fragment
  3. `--verify-paper` re-checks every number still typed by hand against the artifacts
- **Output**: `results_*.png` and `tbl_*.tex` in `journal_paper/`
- **Why**: hand-transcribing results into LaTeX is the largest source of silent error in a paper. Generating them means a number cannot drift from the run that produced it, and `--verify-paper` catches drift in whatever remains manual.
- **Editorial control is preserved**: fragments contain only the `tabular`; the `table` float, `\caption` and `\label` stay in the hand-authored section files. Fragments are written flat into `journal_paper/` because the manuscript build enforces flat sources.
- **Configure** which corpus pairs get comparison tables with `paper_comparisons` in `config.py`

## 📊 Evaluation Metrics

The framework computes standard information retrieval metrics:

- **MAP@k**: Mean Average Precision - ranking quality assessment
- **Recall@k**: Coverage of relevant documents in top-k results
- **Precision@k**: Accuracy of top-k retrieved documents
- **NDCG@k**: Position-aware ranking quality with discounting
- **MRR@k**: Mean reciprocal rank of first relevant document
- **Success@k**: Fraction of queries with at least one relevant hit
- **Timing Metrics**: Embedding speed, throughput, processing time, and query latency

### Statistical Analysis Methods (Aggregate Reporting)

For cross-dataset comparison and statistical significance testing:

- **Paired t-tests**: Compare model performance across datasets (α=0.05)
- **Cohen's d**: Measure effect sizes for practical significance
- **Friedman Test**: Non-parametric test for multiple model comparison
- **Consistency Metrics**: Coefficient of variation, worst-case performance drop
- **Dataset Difficulty Scoring**: Relative hardness assessment across datasets

## 📁 Output Files

### Generated Files Structure

```
RagRetrievalBench/
├── corpus.jsonl                    # Processed document chunks (default dataset)
├── queries.jsonl                   # Generated evaluation queries (default)
├── qrels.tsv                       # Relevance judgments (default)
├── aggregated_reports/             # Cross-dataset comparison reports
│   └── <timestamp>/                # Timestamped subdirectory for each run
│       ├── aggregate_report.md     # Comprehensive cross-dataset analysis
│       ├── aggregate_report.pdf    # PDF version (needs Pandoc + LaTeX)
│       ├── cross_dataset_radar_chart_*.png
│       ├── model_ranking_heatmap_*.png
│       ├── pairwise_significance_heatmap_*.png
│       ├── consistency_comparison_*.png
│       └── [additional statistical visualizations]
├── datasets/                       # Multi-dataset support
│   └── <dataset_name>/             # Per-dataset isolated storage
│       ├── corpus.jsonl            # Dataset-specific corpus
│       ├── queries.jsonl           # Dataset-specific queries
│       ├── qrels.tsv               # Dataset-specific relevance judgments
│       ├── pdfs/                   # Input PDF documents for this dataset
│       ├── reports/                # Dataset-specific reports
│       │   ├── <dataset>_benchmark_report_*.md
│       │   ├── <dataset>_benchmark_report_*.pdf
│       │   ├── raw_results_*.json  # Dataset-specific raw results
│       │   ├── timing_data_*.json
│       │   ├── batch_history.jsonl # Dataset-specific batch history
│       │   └── *.png               # Dataset-specific visualizations
│       ├── analysis/               # Query-level artifacts
│       │   ├── rankings_M*.jsonl   # Per-query ranked lists, one file per model
│       │   └── bootstrap_frozen.json # Per-corpus confidence intervals
│       └── chromadb_collections/   # Dataset-specific vector database
│           ├── chroma.sqlite3      # ChromaDB metadata
│           └── [collection_directories]/ # Individual model collections
├── journal_paper/                  # Manuscript sources and generated artifacts
│   ├── results_*.png               # Figures from --journal-figures
│   └── tbl_*.tex                   # Data tables from --paper-tables
└── utils/chromadb_collections/     # Vector database storage (default)
    ├── chroma.sqlite3              # ChromaDB metadata
    └── [collection_directories]/   # Individual model collections
```

The files under `analysis/` are what make the statistics reproducible without re-embedding: keeping each model's ranked list means confidence intervals, alternative relevance judgments, and report changes can all be recomputed from disk.

### Report Contents

#### Individual Dataset Reports

- **Executive Summary**: Best performing models and key insights
- **Methodology**: Experimental setup and evaluation procedure
- **Dataset Statistics**: Corpus analysis and query characteristics
- **Model Performance**: Comparative tables with statistical analysis
- **Query-Level Uncertainty**: Marginal and paired bootstrap intervals per model, with a `Separated?` column saying whether the corpus actually distinguishes each model from the leader
- **Pairwise Differences**: Raw gaps between point estimates, kept as descriptive context below the intervals
- **Timing Analysis**: Embedding performance and throughput comparison (uses persisted timing data)
- **Visualizations**: Charts for performance, timing, and dataset statistics
- **Technical Details**: Configuration and reproducibility information

#### Aggregate Cross-Dataset Reports

- **Executive Summary**: Overall best performers across datasets with consistency metrics
- **Datasets Analyzed**: Summary of all included datasets (PDFs → chunks breakdown)
- **Cross-Dataset Model Comparison**: Statistical rankings with significance testing
- **Dataset-Specific Analysis**: Individual dataset performance and difficulty assessment
- **Model Consistency**: Performance variability analysis across datasets
- **Statistical Analysis**: Paired t-tests, effect sizes, Friedman test results
- **Visualizations**: 14+ statistical charts including radar plots, heatmaps, and significance matrices
- **Recommendations**: Production deployment guidance based on aggregate analysis

## 🛠 Development Tools

### Python Task Runner (`make.py`)

```bash
# Format code
python make.py format

# Run tests
python make.py test
python make.py test-cov  # With coverage

# Run pipeline helpers
python make.py prepare <dataset>   # Prepare corpus, queries, qrels
python make.py init <dataset>      # Initialize ChromaDB collections
python make.py evaluate <dataset>  # Evaluate models
python make.py all <dataset>       # Full pipeline (prepare + init + evaluate)
python make.py aggregate [args]    # Aggregate report (pass-through args supported)

# Clean generated files
python make.py clean

# Check code quality
python make.py lint

# Show help
python make.py help
```

### Cleanup Operations

The `make.py clean` command removes:

- Python cache files (`__pycache__/`, `*.pyc`)
- Test artifacts (`.pytest_cache`, coverage reports)
- Generated reports (`reports/` contents)
- Aggregate reports (`aggregated_reports/` contents)
- ChromaDB collections (`utils/chromadb_collections/` contents)
- Dataset-specific reports and collections under `datasets/<name>/`

## 🧪 Testing

### Running Tests

```bash
# Activate environment
conda activate ragbenchmark

# Run all tests (recommended)
python make.py test

# Run with coverage (defaults to utils coverage)
python make.py test-cov

# Run specific test files
pytest tests/test_llm.py
pytest tests/test_document_loader.py

# Full-project coverage (optional)
pytest --cov=. --cov-report=html --cov-report=term
```

### Test Coverage

Coverage varies by module and changes over time. To generate current numbers:

```bash
python make.py test-cov
```

For full-project coverage, use:

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Test configuration and fixtures
├── test_aggregate_report_utils.py # Aggregate report tests
├── test_chromadb_utils.py         # ChromaDB functionality tests
├── test_document_loader.py        # Document processing tests
├── test_llm.py                   # LLM integration tests
├── test_text_splitter.py         # Text chunking tests
├── test_report_utils.py          # Report generation tests
├── test_report_integration.py    # Integration tests
└── test_metric_indexing.py       # Metric calculation tests
```

### Test Quality

- **Unit + integration tests** across core utilities and reporting
- **Comprehensive mocking** for external dependencies
- **Integration tests** for complex workflows (marked `integration` in `pytest.ini`)
- **Error handling tests** for robust code paths

## 🎯 Project Structure

```
RagRetrievalBench/
├── rag_benchmark.py                  # Main pipeline script
├── config.py                         # Configuration settings
├── make.py                          # Development task runner
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Test configuration
├── .env                            # Environment variables (create this)
├── .env.template                   # Environment variables template
├── .gitignore                      # Git ignore rules
├── current_versions.txt            # Version tracking
├── datasets/                       # Multi-dataset storage (created dynamically)
│   └── <dataset_name>/             # Per-dataset isolated directories
│       ├── corpus.jsonl            # Dataset-specific corpus
│       ├── queries.jsonl           # Dataset-specific queries
│       ├── qrels.tsv               # Dataset-specific qrels
│       ├── pdfs/                   # Input PDFs for this dataset
│       ├── reports/                # Dataset-specific reports and data
│       ├── analysis/               # Per-query rankings and uncertainty blocks
│       └── chromadb_collections/   # Dataset-specific vector DB
├── utils/                          # Core utilities package
│   ├── __init__.py               # Package initialization
│   ├── aggregate_report_utils.py # Cross-dataset statistical analysis
│   ├── batch_manager.py         # Gemini Batch API helpers
│   ├── bootstrap_utils.py        # Query-level uncertainty stage
│   ├── chromadb_utils.py         # Vector database operations
│   ├── document_loader.py        # PDF processing and corpus loading
│   ├── generate_journal_results_figures.py # Manuscript figures
│   ├── llm.py                    # Google Gemini LLM integration
│   ├── pandoc_header.tex         # LaTeX preamble for markdown -> PDF conversion
│   ├── paper_artifacts.py        # Manuscript LaTeX data tables
│   ├── report_utils.py           # Report generation and visualization
│   ├── text_splitter.py          # Document chunking utilities
│   ├── verify_paper_numbers.py   # Manuscript number drift check
│   ├── chromadb_collections/     # ChromaDB collections storage (default)
│   └── pdfs/                     # Input PDF documents directory (default)
├── analysis/                      # Frozen-snapshot provenance (not a pipeline stage)
├── journal_paper/                 # Manuscript sources + generated figures/tables
├── tests/                         # Comprehensive test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Shared test configuration
│   └── test_*.py               # Individual test modules
├── reports/                       # Generated evaluation reports (default dataset)
├── aggregated_reports/            # Cross-dataset aggregate reports
│   └── <timestamp>/               # Timestamped report run
│       ├── aggregate_report.md    # Statistical comparison report
│       ├── aggregate_report.pdf   # PDF version (needs Pandoc + LaTeX)
│       └── *.png                  # Aggregate visualizations
```

## 🚀 API Rate Limits & Best Practices

### Google Gemini API Limits

- **Limits vary by plan and model version**. Check current values in Google AI Studio for your account before large runs.
- **Rate Limiting**: Built-in delays between API calls (configurable)
- **Error Handling**: Graceful quota exhaustion handling with helpful messages

### Performance Optimization

- **Batch Processing**: Documents processed in configurable batches (default: 32)
- **Progress Tracking**: Real-time progress bars for long-running operations
- **Caching**: ChromaDB collections persist between runs
- **Memory Management**: Efficient handling of large document collections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python make.py test-cov`
5. Format code: `python make.py format`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a pull request

### Development Standards

- **Test Coverage**: Maintain >70% coverage for new code
- **Code Quality**: Follow PEP 8 and use black formatting
- **Documentation**: Update relevant docs for significant changes
- **Testing**: Add comprehensive tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SentenceTransformers**: For embedding model integration
- **ChromaDB**: For efficient vector storage and retrieval
- **Google AI**: For Gemini API access
- **LangChain**: For document processing utilities

---

**Made with ❤ for the RAG research community**

*For questions or support, please open an issue on GitHub.*
