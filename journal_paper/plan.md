# Reusable Journal Writing Plan

## Purpose and Positioning
The central contribution of this manuscript is an end-to-end embedding benchmarking pipeline that enables users to evaluate embedding model performance on local datasets and select the best suitable embedding model for user/application requirements.

This paper is positioned as a pipeline design plus demonstrated utility paper, not as a universal model winner paper.

Primary objective:
- Create and test a reusable pipeline for local embedding evaluation.
- Generate automatic benchmarking reports across various metrics.
- Provide well-structured dynamic report outputs (timestamped markdown/pdf + visualizations).
- Support cross-dataset comparison for dataset-specific model selection.
- Demonstrate effectiveness with 3 datasets and 5 models.
- Publish the pipeline as reusable tooling for developers.

## Scope and Canonical Sources
- Aggregate report (frozen run): `aggregated_reports/2026-03-05_11-32-49/aggregate_report.md` [Aggregate_Report_2026_03_05]
- Dataset raw results (frozen run):
  - `datasets/education_eng/reports/raw_results_2026-03-05_11-27-28.json` [Raw_Education_Eng_2026_03_05]
  - `datasets/education_tr/reports/raw_results_2026-03-05_11-29-07.json` [Raw_Education_Tr_2026_03_05]
  - `datasets/law_tr/reports/raw_results_2026-03-05_11-30-27.json` [Raw_Law_Tr_2026_03_05]
- Pipeline/config baseline:
  - `config.py` [Config_Py]
  - `rag_benchmark.py` [Rag_Benchmark_Py]
- Dataset provenance (curation sources, retrieved on 01/01/2026):
  - Education datasets (`education_eng`, `education_tr`): TED University Regulations and Guidelines for Education  
    `https://www.tedu.edu.tr/en/regulations-and-guidelines-education` [TED_Regulations]
  - Law dataset (`law_tr`): Bankacilik Duzenleme ve Denetleme Kurumu (BDDK) Mevzuat listesi  
    `https://www.bddk.org.tr/Mevzuat/Liste/49` [BDDK_Mevzuat]
- Public code repository:
  - `https://github.com/kmkarakaya/RagRetrievalBench.git` [GitHub_RagRetrievalBench]
- Prior conference paper (related work context only):
  - `publishedConferencePaper.pdf` [Karakaya_Conference_2025]

Scope rules:
- Keep conference-paper coverage brief in `related.md`.
- Ground all quantitative claims in the frozen cross-dataset run.
- State clearly that results demonstrate pipeline effectiveness, not universal superiority of a single embedding model.

## Citation and Reference Contract
- `refs.md` is the mandatory and only canonical reference metadata file for all manuscript sections.
- Every in-text citation must use semantic key labels (square-bracketed in text) that are defined exactly once in `refs.md`.
- The writing agent must add all possible references with complete citation metadata to `refs.md` before citing them.
- Every citation key used in `abstract.md`, `intro.md`, `method.md`, `experiments.md`, `results.md`, `related.md`, `conculusion.md`, and `plan.md` must resolve to an entry in `refs.md`.
- Prohibited citation styles in manuscript sections:
  - A-number style (for example `A1`)
  - E-number evidence-tag style (for example `E1`)
  - standalone numeric citation style (for example `1`)
- Key format rule:
  - `FirstMeaningfulWord_Qualifier`, ASCII only, letters/numbers/underscore, starts with a letter
  - Collision handling via short suffix (domain/year/source acronym)
  - Keep keys stable once introduced

## Experiment Snapshot (Frozen Baseline)
- Aggregate run id: `2026-03-05_11-32-49`
- Dataset run ids:
  - `education_eng`: `2026-03-05_11-27-28`
  - `education_tr`: `2026-03-05_11-29-07`
  - `law_tr`: `2026-03-05_11-30-27`

### Fixed Settings for This Manuscript
- `n_queries = 50` (evidenced by `total_queries` in all three raw JSON files)
- `candidate_pool_size = 20`
- `k = 10`
- `chunk_size = 1000`
- `chunk_overlap = 200`
- `qrels_embedding_model_index = 4`

Configuration evidence:
- `config.py`
- Raw JSON `config` blocks (except `n_queries` and `qrels_embedding_model_index`, which are read from `config.py`)

### Rule: Do Not Mix Runs
No numeric table or figure in the manuscript may combine values from different timestamps. If a new run is introduced, update the snapshot block first and revalidate all derived statements.

## Model Naming Standard (Use Everywhere)
Use exact names as they appear in `config.py` and raw JSON:
- `sentence-transformers/all-MiniLM-L6-v2`
- `sentence-transformers/all-mpnet-base-v2`
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- `sentence-transformers/all-MiniLM-L12-v2`
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

Metric labels:
- `MAP@10`, `Recall@10`, `Precision@10`, `NDCG@10`, `MRR@10`, `Success@10`

Dataset ids:
- `education_eng`, `education_tr`, `law_tr`

Demonstration setup statement (use consistently):
- This journal paper demonstrates the pipeline with 3 datasets and 5 embedding models.

## Claim-to-Evidence Matrix (Build Before Prose)
| Claim | Evidence Objects | Numeric Anchors (Frozen Run) | Interpretation Rule |
|---|---|---|---|
| Pipeline supports practical model selection | `aggregate_report.md` method + ranking + timing sections; dataset raw JSON metrics/timing fields | Quality and speed metrics jointly available (`MAP@10`, latency, throughput) for each model | Use multi-metric evidence to map model choice to user requirements |
| Language effect (education EN vs TR rank change) | Aggregate table `Model Performance by Dataset (MAP@10)` and `Dataset Performance Summary`; raw JSON MAP fields for `education_eng` and `education_tr` | `education_eng` best: `all-MiniLM-L12-v2` (`0.6121`), `education_tr` best: `paraphrase-multilingual-mpnet-base-v2` (`0.5508`) | Claim supported if best model differs between EN and TR within education domain |
| Domain effect within Turkish (education_tr vs law_tr) | Aggregate table `Model Performance by Dataset (MAP@10)`; dataset difficulty section; raw JSON MAP fields for both TR datasets | Top model remains `paraphrase-multilingual-mpnet-base-v2` in both; absolute MAP shifts by model (example: `all-MiniLM-L12-v2` `0.1915` -> `0.1863`) and mean dataset difficulty changes | Report domain effect in score profile/difficulty; explicitly state ranking stability for MAP in this run |
| Cross-dataset consistency | Aggregate table `Cross-Dataset Model Performance Summary`; `Detailed Consistency Metrics` | Best consistency according to report: `paraphrase-multilingual-mpnet-base-v2` (`CV=0.357`, avg rank `2.00`) | Use report-level CV/avg-rank values as canonical consistency summary |
| Automatic report generation quality | Aggregate directory artifacts + dataset report folders | Markdown/pdf reports and visualization png outputs are generated with timestamps | Describe the reports as well-structured dynamic report outputs |

## Drafting Workflow and Deliverables
Draft in this order and keep each file evidence-linked and pipeline-first.

1. `journal_paper/abstract.md`
- One-paragraph structured abstract (problem, method, setup, key findings, practical utility)
- Keep claims bounded to frozen-run evidence
- Include semantic citations when needed

2. `journal_paper/intro.md`
- Pipeline purpose for developer decision support
- Local-data suitability and application-specific selection framing
- Contributions and explicit research questions
- Include reusable-by-developers statement

3. `journal_paper/method.md`
- End-to-end pipeline: PDF -> chunking -> query generation -> qrels -> retrieval eval -> structured report generation
- Frozen config values only
- Model set and metric definitions
- Statistical analysis methods as implemented by aggregate report
- Reproducibility and public code availability

4. `journal_paper/experiments.md`
- Demonstration setup: 3 datasets and 5 embedding models
- Dataset construction and per-dataset sizes
- Experimental controls shared across datasets
- Notes on comparability limits (`law_tr` has 2 PDFs)

5. `journal_paper/results.md`
- Core quantitative findings with source tags to frozen files
- Use findings to show the pipeline can expose differences by language/domain and runtime constraints
- Include practical model selection guidance based on user needs
- Keep significance notes from aggregate report

6. `journal_paper/related.md`
- Core retrieval/RAG benchmark literature
- Short conference-paper summary
- One concise extension paragraph: from preliminary single-corpus study to cross-dataset practical selection workflow

7. `journal_paper/conculusion.md`
- Restate pipeline utility and reusability
- Supported findings only
- Pending validation items separated clearly
- Future work

8. `journal_paper/refs.md`
- Consolidated references used across all sections
- Include literature, frozen artifacts, and the GitHub repository citation as first-class reference

9. `journal_paper/main.md`
- Canonical manuscript entrypoint with section order manifest (build-generated style)
- Do not duplicate full section body content in `main.md`

10. `journal_paper/md_to_latex.md`
- Operational conversion pipeline spec (markdown -> latex -> optional pdf)
- Includes citation conversion (`[Key]` -> `[@Key]`), bib generation, and build verification

## Section Writing Rules
- Avoid universal superiority claims for any embedding model.
- Keep claims bounded to evaluated datasets and setup.
- Every quantitative statement in `results.md` must carry an evidence tag mapped to a concrete file and run timestamp.
- Keep these phrases consistent across sections:
  - `best suitable embedding model for user/application requirements`
  - `automatic benchmarking reports across various metrics`
  - `well-structured dynamic report outputs (timestamped markdown/pdf + visualizations)`
  - `cross-dataset comparison for dataset-specific model selection`
  - `demonstrated with 3 datasets and 5 models`
  - `pipeline reusable by any developer`
- Related work conference paragraph must remain short and factual:
  - preliminary study scope
  - this journal extension scope
- Mark manuscript state if validity appendices are missing:
  - `Draft evidence complete, validation appendix pending`

## Mandatory Validity Items (Submission-Quality)
These are required before final submission lock:
1. Data provenance table:
   - source URLs per PDF set
   - retrieval date per source
   - current status: baseline sources for education and law datasets are documented (01/01/2026)
2. Light qrels human audit:
   - sample size
   - labeling protocol
   - agreement metric (accuracy and/or Cohen kappa)
3. Compute environment table:
   - CPU/GPU/RAM
   - OS
   - package/runtime versions

If any item is not ready, keep them in a pending subsection and do not overstate validity.

## Figure and Table Policy
- Use primary figures from:
  - `aggregated_reports/2026-03-05_11-32-49/*.png`
- Use primary numeric values from:
  - aggregate markdown tables
  - raw JSON metrics/timing fields
- Do not transcribe numbers from memory.
- Keep model order/naming consistent with `config.py`.

## Reusable Update Workflow (Future Reruns)
When a new run is produced:
1. Update `Experiment Snapshot` block first (aggregate id + dataset ids).
2. Update fixed settings if config changed.
3. Recompute the claim-to-evidence matrix from new frozen files.
4. Update `results.md` quantitative statements and evidence tags.
5. Re-run quality gates checklist.
6. Add a changelog entry with date and changed run ids.

## Quality Gates Checklist
1. Message consistency gate:
   - each main section (`plan`, `abstract`, `intro`, `method`, `experiments`, `results`, `related`, `conculusion`) keeps pipeline-first framing and developer utility language
2. Numerical consistency gate:
   - all sections consistently state `3 datasets` and `5 embedding models`
3. Scope gate:
   - no universal best-model claims
   - conclusions remain dataset/setup-bounded
4. Artifact gate:
   - GitHub URL appears and matches `https://github.com/kmkarakaya/RagRetrievalBench.git`
5. Provenance gate:
   - education datasets are tied to TED source URL and retrieval date 01/01/2026
   - law dataset is tied to BDDK source URL and retrieval date 01/01/2026
6. Citation format gate:
   - no A-number, E-number, or standalone numeric citation styles
   - all citations use semantic key format and resolve in `refs.md`
7. Traceability gate:
   - frozen-run evidence tags/paths remain intact
8. Completeness gate:
   - all core manuscript files are non-empty and mutually consistent:
     `abstract.md`, `intro.md`, `related.md`, `method.md`, `experiments.md`, `results.md`, `conculusion.md`, `refs.md`, `main.md`, `md_to_latex.md`

## Practical Commands (Verification)
Use these checks before each drafting revision:

```powershell
rg --line-number "2026-03-05_11-32-49|2026-03-05_11-27-28|2026-03-05_11-29-07|2026-03-05_11-30-27" journal_paper
rg --line-number "best suitable embedding model for user/application requirements|automatic benchmarking reports across various metrics|well-structured dynamic report outputs|cross-dataset comparison for dataset-specific model selection|demonstrated with 3 datasets and 5 models|pipeline reusable by any developer" journal_paper
rg --line-number "https://github.com/kmkarakaya/RagRetrievalBench.git" journal_paper
rg --line-number "tedu.edu.tr/en/regulations-and-guidelines-education|bddk.org.tr/Mevzuat/Liste/49|01/01/2026" journal_paper
rg --line-number "\bA[0-9]+\b|\bE[0-9]+\b|\[[0-9]+\]" journal_paper
```

## Changelog
| Date | Change | Run IDs |
|---|---|---|
| 2026-03-06 | Initialized reusable journal writing plan; froze baseline evidence and drafting workflow | Aggregate: `2026-03-05_11-32-49`; Datasets: `11-27-28`, `11-29-07`, `11-30-27` |
| 2026-03-06 | Reframed manuscript to pipeline-first positioning and practical model-selection utility; added GitHub artifact reference | Same frozen run IDs |
| 2026-03-06 | Added dataset provenance for TED education regulations and BDDK law regulations with retrieval date 01/01/2026 | Same frozen run IDs |
| 2026-03-06 | Standardized citation model to semantic keys in `refs.md` and enforced key-based citations across manuscript sections | Same frozen run IDs |
