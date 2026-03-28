# Publication Plan (Canonical)

This file is the single planning source for paper-writing cycles in this repository.

## Purpose and Positioning

The paper contribution is an end-to-end embedding benchmarking workflow for local document collections, focused on practical model selection.

Positioning rule:
- This is a pipeline-utility paper, not a universal best-model paper.

Primary objective:
- Demonstrate a reusable local evaluation workflow.
- Generate automated benchmarking artifacts across quality and runtime metrics.
- Support dataset-specific model selection with cross-dataset comparison.

## Claims and Boundaries

Core claims:
1. Pipeline claim: the workflow enables reproducible, configurable local RAG retrieval benchmarking.
2. Language-effect claim: within the same domain, model rankings can change across languages.
3. Domain-effect claim: within the same language, model rankings can change across domains.

Boundary rules:
- Avoid universal superiority claims.
- Keep conclusions bounded to the current dataset setup and fixed protocol.
- Do not mix evidence from different run snapshots in one manuscript version.

## Frozen Snapshot and Evidence Constraints

Current baseline snapshot:
- Aggregate run id: `2026-03-05_11-32-49`
- Dataset runs:
  - `education_eng`: `2026-03-05_11-27-28`
  - `education_tr`: `2026-03-05_11-29-07`
  - `law_tr`: `2026-03-05_11-30-27`

Dataset provenance baseline:
- TED source (`education_eng`, `education_tr`): `https://www.tedu.edu.tr/en/regulations-and-guidelines-education`
- BDDK source (`law_tr`): `https://www.bddk.org.tr/Mevzuat/Liste/49`
- Retrieval date used in manuscript: `01/01/2026`

Consistency requirements:
- Manuscript states 3 datasets and 5 embedding models consistently.
- Citation keys resolve in `journal_paper/refs.bib`.
- Scope boundaries remain strict across Method, Experiments, and Results.

## Section Ownership Boundaries

- `method.tex`: proposed pipeline and workflow design, artifact construction, indexing/evaluation logic, reporting/reproducibility.
- `experiments.tex`: manuscript-specific setup, dataset context/provenance, model roster, controlled variables, limitations.
- `results.tex`: metric presentation, comparative evidence, findings, and tradeoff interpretation.

Do not move result interpretation into Method.

## Acceptance and Build Gates

Required gate:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File journal_paper/build.ps1 -CompilePdf
```

Acceptance criteria:
- Lint/template checks pass with 0 `ERROR`.
- PDF build completes successfully.
- Latest build folder and PDF path are reported.

## Step-1 Publication Planning Template (Use For New Cycles)

Fill this template before substantive section editing:

1. Working title:
2. Paper objective (1-2 sentences):
3. Decision-complete claims (A/B/C):
4. In-scope datasets and model roster:
5. Out-of-scope claims:
6. Evidence snapshot and provenance constraints:
7. Section-level responsibilities:
8. Planned validation checks:
9. Risks and mitigation:
10. Definition of done:

## Current Working Plan (Merged Legacy Content)

### Summary

Publish a compact yet defensible study showing that embedding model performance is dataset-dependent and language-sensitive. Use two education datasets (EN/TR) to isolate language effects and add one Turkish domain dataset (`law_tr`) to show domain effects within the same language. Generate consistent reports using the existing pipeline and include a light human audit for validity.

### Scope and Claims (Decision-Complete)

1. Claim A (Pipeline): We provide an end-to-end, LLM-assisted RAG retrieval benchmark pipeline that is reproducible and configurable for custom datasets.
2. Claim B (Language Effect): Within the same domain (education), model rankings change between EN and TR.
3. Claim C (Domain Effect): Within Turkish, model rankings differ across domains (`education_tr` vs `law_tr`).

Wording guidance:
- Avoid claims like "different from internet benchmark results" unless a public benchmark is explicitly included.
- Prefer: model rankings differ across language/domain in custom datasets, so model selection should be validated on target data.

### Datasets (Current Set)

- `education_eng` (English university regulations)
- `education_tr` (Turkish university regulations)
- `law_tr` (Turkish legal/regulation texts)

### Dataset Quality Requirements

1. Balance: keep total chunk counts within +/-10-15% across datasets.
2. Language purity: verify each dataset is single-language.
3. Document type: keep genre comparable (policy/regulation style).
4. Provenance: document source URLs and retrieval date for all PDFs.

### Pipeline Configuration Requirements

Set in `config.py` before running:
- `n_queries = 40`
- `candidate_pool_size = 20`
- `qrels_embedding_model_index` = multilingual model (for example, `paraphrase-multilingual-mpnet-base-v2`)
- Keep `chunk_size`, `chunk_overlap`, `k`, and `document_batch_size` fixed across datasets.

### Execution Steps (Per Dataset)

For each dataset (`education_eng`, `education_tr`, `law_tr`):
1. `python rag_benchmark.py --dataset <name> --prepare-corpus`
2. `python rag_benchmark.py --dataset <name> --generate-queries`
3. `python rag_benchmark.py --dataset <name> --generate-qrels`
4. `python rag_benchmark.py --dataset <name> --initialize`
5. `python rag_benchmark.py --dataset <name> --evaluate`

Then run:
- `python rag_benchmark.py --generate-aggregate-report --aggregate-datasets education_eng,education_tr,law_tr`

### Light Human Validation

- Randomly sample ~30 qrels per dataset.
- Manually label relevance (binary).
- Report agreement (simple accuracy or Cohen's kappa if two annotators).

### Report-Level Enhancements

Add a short appendix section (or dedicated paragraph) with:
- Dataset sizes (PDFs, chunks, queries)
- Query generation settings
- Qrels audit results
- Model list and embedding dimensions
- Compute environment (CPU/GPU, RAM)

### Suggested Enhancements (Optional but Strong)

1. Fix seed for sampling: add a random seed to query selection for reproducibility.
2. Store dataset metadata: language and source URLs in `raw_results`.
3. Qrels bias reduction: sample random negatives in addition to top-k retrieval candidates.

### Paper Structure (Decision-Complete)

1. Abstract
2. Introduction
3. Related Work
4. Pipeline and Methodology
5. Datasets
6. Experimental Setup
7. Results
8. Analysis
9. Validity and Limitations
10. Conclusion

### Tests and Acceptance Criteria

- All three datasets produce reports and `raw_results` JSON.
- Aggregate report renders with all tables and captions.
- At least one clear rank change between EN and TR.
- At least one rank change between Turkish domains.

### Assumptions

- Third Turkish dataset is `law_tr` (unless explicitly changed).
- 40 queries per dataset can be generated.
- Light qrels audit is performed.
