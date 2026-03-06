# Experiments

## Experimental Snapshot

This draft uses the frozen 2026-03-05 run family:
- Aggregate report: `aggregated_reports/2026-03-05_11-32-49/aggregate_report.md` [Aggregate_Report_2026_03_05]
- Dataset raw results:
  - `education_eng`: `raw_results_2026-03-05_11-27-28.json` [Raw_Education_Eng_2026_03_05]
  - `education_tr`: `raw_results_2026-03-05_11-29-07.json` [Raw_Education_Tr_2026_03_05]
  - `law_tr`: `raw_results_2026-03-05_11-30-27.json` [Raw_Law_Tr_2026_03_05]

Primary evaluation intent:
- demonstrate pipeline effectiveness for practical model selection, not to claim a universal best model.

## Datasets

| Dataset | Documents (PDFs) | Chunks | Queries | Qrels |
|---|---:|---:|---:|---:|
| education_eng | 29 | 572 | 50 | 215 |
| education_tr | 29 | 619 | 50 | 199 |
| law_tr | 2 | 723 | 50 | 210 |
| Total | 60 | 1914 | 150 | 624 |

Source:
- Aggregate table `Dataset Statistics Summary` in `aggregated_reports/2026-03-05_11-32-49/aggregate_report.md` [Aggregate_Report_2026_03_05]

Demonstration scope:
- demonstrated with 3 datasets and 5 models.

## Dataset Provenance

| Dataset Group | Source | URL | Retrieval Date |
|---|---|---|---|
| `education_eng`, `education_tr` | TED University Regulations and Guidelines for Education | `https://www.tedu.edu.tr/en/regulations-and-guidelines-education` | `01/01/2026` |
| `law_tr` | Bankacilik Duzenleme ve Denetleme Kurumu (BDDK) Mevzuat listesi | `https://www.bddk.org.tr/Mevzuat/Liste/49` | `01/01/2026` |

Provenance note:
- The education datasets were curated from the TED University regulations/guidelines source above.
- The law dataset was curated from the BDDK regulations source above.
[TED_Regulations][BDDK_Mevzuat]

## Shared Evaluation Setup

- Retrieval backend: ChromaDB vector search with cosine similarity.
- Cutoff: `k=10` for all metrics.
- Chunking: `1000` size, `200` overlap.
- Query count: `50` per dataset.
- Candidate pool for qrels labeling: `20`.
- Same five embedding models evaluated on each dataset.

Sources:
- `config.py` [Config_Py]
- Aggregate section `Methodology` and dataset raw-result `config` blocks. [Aggregate_Report_2026_03_05][Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05][Raw_Law_Tr_2026_03_05]

Decision-support framing:
- this setup is intentionally fixed so users can compare retrieval quality and operational metrics to choose the best suitable embedding model for user/application requirements.
- the workflow is designed for developers/practitioners and is pipeline reusable by any developer.

## Controlled Variables

Held constant across datasets:
- Metric definitions and cutoff
- Embedding model list
- Candidate pool size
- Chunking parameters
- Reporting pipeline and aggregate analysis procedure

Varied by dataset:
- Corpus language/domain
- Corpus size and document composition

## Known Comparability Limitation

`law_tr` has only 2 source PDFs but 723 chunks, while education datasets each have 29 PDFs. This structural imbalance can influence retrieval behavior and should be interpreted as a limitation when comparing cross-domain outcomes.

Sources:
- Aggregate `Dataset Statistics Summary`
- Dataset sections under `Dataset-Specific Analysis` in aggregate report
[Aggregate_Report_2026_03_05]

## Report Outputs and Utility

For each run, the pipeline emits:
- per-dataset benchmark reports (markdown/pdf),
- aggregate cross-dataset report (markdown/pdf),
- visualization assets for metrics, ranking, consistency, and timing.

These outputs are treated as automatic benchmarking reports across various metrics and as well-structured dynamic report outputs (timestamped markdown/pdf + visualizations) used for cross-dataset comparison for dataset-specific model selection.

## Pending Submission-Quality Additions

The following are intentionally tracked as pending in this draft stage:
1. Light human qrels audit (sample, protocol, agreement metric)
2. Compute environment table (CPU/GPU/RAM/software versions)
