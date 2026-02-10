**Plan**

# Journal Publication Plan for RAG Embedding Benchmark (Education EN/TR + One TR Domain)

## Summary

Publish a compact yet defensible study showing that **embedding model performance is dataset‑dependent** and  **language‑sensitive** . Use two education datasets (EN/TR) to isolate language effects and add one **Turkish domain dataset** (e.g., **law_tr**) to show domain effects within the same language. Generate consistent reports using the existing pipeline and add a light human audit for validity.

## Scope & Claims (Decision‑Complete)

1. **Claim A (Pipeline)** : We provide an end‑to‑end, LLM‑assisted RAG retrieval benchmark pipeline that is reproducible and configurable for custom datasets.
2. **Claim B (Language Effect)** : Within the same domain (education), model rankings change between EN and TR.
3. **Claim C (Domain Effect)** : Within Turkish, model rankings differ across domains (education_tr vs law_tr).

Wording guidance:

* Avoid “different from internet benchmark results” unless you add a public benchmark.
* Use: “model rankings differ across language/domain in custom datasets, so model selection should be validated on target data.”

## Datasets (Final Set)

* **education_eng** (English university regulations)
* **education_tr** (Turkish university regulations)
* **law_tr** (Turkish legal/regulation texts)

If you prefer **finance_tr** instead of **law_tr**, swap it now. All steps remain identical.

## Dataset Quality Requirements (Must‑Do)

1. **Balance** : Keep total chunk counts within ±10–15% across datasets.
2. **Language purity** : Verify each dataset is single‑language.
3. **Document type** : Keep genre comparable (policy/regulation style).
4. **Provenance** : Document source URLs and retrieval date for all PDFs.

## Pipeline Configuration (Must‑Do)

Set the following in [config.py](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/KMK/.vscode/extensions/openai.chatgpt-0.4.71-win32-x64/webview/# "config.py") before running:

* **n_queries = 40**
* **candidate_pool_size = 20**
* **qrels_embedding_model_index = multilingual model** (e.g., **paraphrase-multilingual-mpnet-base-v2**)
* Keep **chunk_size**, **chunk_overlap**, **k**, and **document_batch_size** fixed across datasets.

## Execution Steps (Per Dataset)

For each dataset (**education_eng**, **education_tr**, **law_tr**):

1. **python rag_benchmark.py --dataset `<name>` --prepare-corpus**
2. **python rag_benchmark.py --dataset `<name>` --generate-queries**
3. **python rag_benchmark.py --dataset `<name>` --generate-qrels**
4. **python rag_benchmark.py --dataset `<name>` --initialize**
5. **python rag_benchmark.py --dataset `<name>` --evaluate**

Then run:

* **python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education_eng,education_tr,law_tr**

## Light Human Validation (Must‑Do)

* Randomly sample  **~30 qrels per dataset** .
* Manually label relevance (binary).
* Report agreement (simple accuracy or Cohen’s kappa if two annotators).

## Report‑Level Enhancements (Must‑Do)

Add a short appendix section (or dedicated paragraph) with:

* Dataset sizes (PDFs, chunks, queries).
* Query generation settings.
* Qrels audit results.
* Model list and embedding dimensions.
* Compute environment (CPU/GPU, RAM).

## Suggested Pipeline Enhancements (Optional but Strong)

1. **Fix seed for sampling** : add a random seed to query selection for reproducibility.
2. **Store dataset metadata** : language and source URLs in **raw_results**.
3. **Qrels bias reduction** : sample random negatives in addition to top‑k retrieval candidates.

## Paper Structure (Decision‑Complete)

1. **Abstract**
2. **Introduction**

   * Motivation: model selection is dataset‑specific and language‑sensitive.
3. **Related Work**

   * RAG evaluation, embedding benchmarks, multilingual retrieval.
4. **Pipeline & Methodology**

   * PDF → chunking → query gen → qrels → evaluation.
5. **Datasets**

   * EN/TR education + TR law; sizes and sources.
6. **Experimental Setup**

   * Models, metrics, k, chunk params, qrels model.
7. **Results**

   * Per‑dataset reports + aggregate comparison.
8. **Analysis**

   * Language effect (education_en vs education_tr).
   * Domain effect (education_tr vs law_tr).
9. **Validity & Limitations**

   * LLM‑based qrels, dataset size, single institution.
10. **Conclusion**

    * Model choice must be validated on target dataset.

## Tests & Acceptance Criteria

* All three datasets produce reports and raw_results JSON.
* Aggregate report renders with all tables and captions.
* At least one clear **rank change** between EN and TR.
* At least one **rank change** between TR domains.

## API/Interface Changes

None required. Optional: add seed and dataset metadata to raw_results.

## Assumptions

* You will add a third Turkish dataset (**law_tr**) unless you explicitly prefer **finance_tr**.
* You can generate 40 queries per dataset.
* You will perform a light qrels audit.
