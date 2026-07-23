# `analysis/` — reviewer-driven re-analysis and pipeline notes

This folder contains the re-analysis used to answer the journal reviewer's
methodological concerns, plus notes on the benchmark-construction controls that
were added to the **main** pipeline (`config.py`, `rag_benchmark.py`, `utils/`).

The main pipeline is the source of truth for future runs. The scripts here are a
**read-only re-analysis layer**: they never modify the frozen snapshot and were
needed because this machine's persisted ChromaDB segments crash on cross-process
reload (see "ChromaDB caveat" below).

---

## 1. New benchmark-construction controls (in `config.py`)

These make the pipeline implement the protocol described in the paper's Method.
All default to the paper-aligned behavior; legacy behavior is available by flipping
the flag.

| Flag | Default | Meaning |
|------|---------|---------|
| `random_seed` | `42` | Seeds seed-chunk sampling so query selection is reproducible (`None` disables). |
| `qrels_pooling` | `True` | Build the LLM-judge candidate pool as the **model-independent union** of every model's top-`candidate_pool_size` chunks. `False` = legacy single-model pool via `qrels_embedding_model_index`. |
| `qrels_store_negatives` | `True` | Write explicit `0` (non-relevant) rows to `qrels.tsv` in addition to `1`. The loader ignores `0` rows for scoring, but they make judgments auditable. |
| `force_source_chunk_relevant` | `False` | If `True`, each query's seed chunk is marked relevant without judging (legacy bias). Default `False` judges it like any other candidate. |
| `hnsw_space` | `"l2"` | ChromaDB distance space set explicitly at collection creation (`"l2"` = ChromaDB default squared-Euclidean; `"cosine"` also valid). |
| `log_environment` | `True` | Record a Python/library/device snapshot in each `raw_results_*.json`. |

The raw-result JSON now also records these settings under `config` and an
`environment` block, so a run is self-describing.

---

## 2. Reproducing the paper's pipeline on a dataset

Place a dataset under `datasets/<name>/pdfs/`, then run the stages. Use **batch
mode** for the LLM stages (query generation and pooled judging); the free-tier
synchronous quota is too small for thousands of judgments, and `--all` forces
synchronous mode.

```bash
# 1. Corpus (no LLM)
python rag_benchmark.py --prepare-corpus --dataset <name>

# 2. Queries (LLM; batch recommended)
python rag_benchmark.py --generate-queries --dataset <name> --batch-submit
python rag_benchmark.py --generate-queries --dataset <name> --batch-fetch <job_id>

# 3. Pooled qrels across all models (LLM; batch recommended)
#    Builds each model's collection, unions top-k candidates, judges the union,
#    and stores 0/1 labels.
python rag_benchmark.py --generate-qrels --dataset <name> --batch-submit
python rag_benchmark.py --generate-qrels --dataset <name> --batch-fetch <job_id>

# 4. Build indexes + evaluate + dataset report/figures
python rag_benchmark.py --all --dataset <name>          # small corpora, synchronous
#    or, once queries+qrels exist, just:
python rag_benchmark.py --initialize --evaluate --dataset <name>

# 5. Aggregate cross-dataset report + figures (needs >= 2 evaluated datasets)
python rag_benchmark.py --generate-aggregate-report
```

Artifacts land in `datasets/<name>/reports/` (raw-result JSON, benchmark report,
per-metric PNGs) and `aggregated_reports/<timestamp>/` (cross-dataset report + PNGs).
Journal figures are (re)built by `utils/generate_journal_results_figures.py`.

The `GEMINI_API_KEY` is read from the environment or a project `.env`. Batch mode
requires a billing-enabled key (the free tier disables the Batch API).

---

## 3. Re-analysis scripts (used for the current paper's evidence)

These regenerate rankings by **re-embedding `corpus.jsonl` and doing exact
squared-L2 kNN in NumPy**, bypassing the persisted ChromaDB index. A consistency
gate confirms this reproduces the published dataset means (14/15 model-dataset
pairs bit-exactly; Turkish M1 within 0.003). Outputs go to `datasets/*/analysis/`
and `results_reanalysis/`; frozen `reports/` are never touched.

```bash
python analysis/query_level_eval.py --retrieve   # persist per-query top-100 ranked lists
python analysis/query_level_eval.py --gate        # reconstruction vs published means
python analysis/reconstruct_negatives.py          # recover discarded 0-judgments from batch files
python analysis/pooled_qrels.py --plan            # size the model-independent pooled union (no LLM)
python analysis/pooled_qrels.py --submit          # judge the union via Batch API (needs billing key)
python analysis/pooled_qrels.py --status          # poll batch jobs
python analysis/pooled_qrels.py --fetch           # write qrels_pooled.tsv / qrels_pooled_forced.tsv
python analysis/bootstrap_ci.py --variant frozen  # query-level bootstrap CIs (also: pooled, pooled_forced)
```

- `common.py` — shared helpers: `SEED`, ST embedding + exact-L2 kNN, ST-matching
  per-query IR metrics, judge parsing, retry wrapper.
- `query_level_eval.py` — re-embed/retrieve + per-query metrics + consistency gate.
- `reconstruct_negatives.py` — implicit negatives from `reports/batches/batch_req_qrels_gen_*.jsonl`.
- `pooled_qrels.py` — model-independent pooled qrels rebuild via Batch API.
- `bootstrap_ci.py` — percentile + paired bootstrap CIs over queries (replaces the n=3 tests).

---

## 4. Run in the `ragbenchmark` conda environment

Use the project's conda environment (per the top-level `README.md`):

```bash
conda activate ragbenchmark        # or: conda run -n ragbenchmark <cmd>
python rag_benchmark.py --all --dataset <name>
```

ChromaDB's native index (`add`/`query`) works in `ragbenchmark`. It does **not**
work in the miniconda `base` environment on this machine: a fresh
`collection.add(...)` segfaults there (a broken/incompatible ChromaDB build in
`base`), so always run the pipeline under `ragbenchmark`. If a run ever segfaults,
first confirm the active env is `ragbenchmark` (`python -c "import sys; print(sys.executable)"`).

The re-analysis scripts in this folder re-embed from `corpus.jsonl` (exact-L2 kNN)
instead of reading the persisted ChromaDB index, so they are environment-independent
and were validated to reproduce the published metrics regardless of which env runs them.
