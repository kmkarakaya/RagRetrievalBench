# Results

Manuscript status: **Draft evidence complete, validation appendix pending**.

Positioning note:
- Results in this section are presented as evidence that the proposed pipeline enables practical, local embedding model selection. They are not presented as universal leaderboard claims.
- The evaluation is demonstrated with 3 datasets and 5 models in the frozen 2026-03-05 run. [Aggregate_Report_2026_03_05]

## Evidence Sources (Frozen Snapshot)

- Aggregate report: [Aggregate_Report_2026_03_05]
- Raw dataset results: [Raw_Education_Eng_2026_03_05], [Raw_Education_Tr_2026_03_05], [Raw_Law_Tr_2026_03_05]
- Dataset provenance sources: [TED_Regulations], [BDDK_Mevzuat]

## Pipeline Utility for Model Selection

The frozen outputs provide quality metrics (`MAP@10`, `Recall@10`, `Precision@10`, `NDCG@10`, `MRR@10`, `Success@10`) and runtime metrics (latency, throughput) for all 5 models on all 3 datasets. This supports cross-dataset comparison for dataset-specific model selection and enables users to choose the best suitable embedding model for user/application requirements. [Aggregate_Report_2026_03_05]

Dataset source provenance for this evaluation:
- Education datasets were curated from TED University regulations/guidelines source URL. [TED_Regulations]
- Law dataset was curated from BDDK regulations source URL. [BDDK_Mevzuat]
- Both sources were retrieved on `01/01/2026`. [TED_Regulations][BDDK_Mevzuat]

## RQ1: Language Effect (education_eng vs education_tr)

The top MAP model changes between English and Turkish education datasets: `sentence-transformers/all-MiniLM-L12-v2` is best on `education_eng` with `MAP@10=0.6121`, while `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` is best on `education_tr` with `MAP@10=0.5508`. [Aggregate_Report_2026_03_05][Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05]

Selected MAP evidence by dataset:

| Model | education_eng MAP@10 | education_tr MAP@10 |
|---|---:|---:|
| sentence-transformers/all-MiniLM-L12-v2 | 0.6121 | 0.1915 |
| sentence-transformers/paraphrase-multilingual-mpnet-base-v2 | 0.5404 | 0.5508 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 0.5020 | 0.4876 |

Interpretation: ranking and score profiles are language-sensitive under otherwise fixed evaluation settings. [Aggregate_Report_2026_03_05]

## RQ2: Domain Effect Within Turkish (education_tr vs law_tr)

For MAP ordering, the top-5 rank order is stable between `education_tr` and `law_tr` in this frozen run, with `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` ranked first in both datasets. [Aggregate_Report_2026_03_05][Raw_Education_Tr_2026_03_05][Raw_Law_Tr_2026_03_05]

Domain-related differences are still visible in absolute scores and dataset-level difficulty:
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`: `0.5508` (`education_tr`) vs `0.3659` (`law_tr`). [Aggregate_Report_2026_03_05]
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: `0.4876` vs `0.2948`. [Aggregate_Report_2026_03_05]
- Aggregate difficulty summary increases from `0.71` (`education_tr`) to `0.79` (`law_tr`). [Aggregate_Report_2026_03_05]

Interpretation: this run supports domain impact in performance level/difficulty, while MAP rank ordering remains stable across the two Turkish datasets. [Aggregate_Report_2026_03_05]

## Cross-Dataset Consistency

From the aggregate summary, `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` has the best overall average rank (`2.00`) and the lowest reported CV (`0.357`), with two dataset wins. [Aggregate_Report_2026_03_05]

| Model | Avg Rank | Mean MAP | CV | Datasets Won |
|---|---:|---:|---:|---:|
| sentence-transformers/paraphrase-multilingual-mpnet-base-v2 | 2.00 | 0.4857 | 0.357 | 2 |
| sentence-transformers/all-MiniLM-L12-v2 | 2.33 | 0.3299 | 0.608 | 1 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 3.00 | 0.4281 | 0.399 | 0 |

Source table: `Cross-Dataset Model Performance Summary`. [Aggregate_Report_2026_03_05]

## Quality-Speed Tradeoff

Latency and throughput evidence shows a clear operational tradeoff:
- Fastest weighted query latency: `sentence-transformers/all-MiniLM-L6-v2` at `28.54 ms/query`. [Aggregate_Report_2026_03_05]
- Slowest weighted query latency: `sentence-transformers/all-mpnet-base-v2` at `69.29 ms/query`. [Aggregate_Report_2026_03_05]
- Highest mean MAP across datasets: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` at `0.4857`, but with higher latency (`60.55 ms/query`) and lower throughput than MiniLM variants. [Aggregate_Report_2026_03_05]
- Embedding throughput examples (chunks/sec): `all-MiniLM-L6-v2` roughly `48-57`, `paraphrase-multilingual-mpnet-base-v2` roughly `14-15`, `all-mpnet-base-v2` roughly `3.9-8.6`. [Aggregate_Report_2026_03_05]

Interpretation: the best MAP model is not the fastest model; model choice depends on quality-vs-latency constraints. [Aggregate_Report_2026_03_05]

Practical implication:
- the pipeline's automatic benchmarking reports across various metrics make this tradeoff explicit for real deployment decisions. [Aggregate_Report_2026_03_05]

## Statistical Note

The aggregate report states that `paraphrase-multilingual-mpnet-base-v2` does not significantly differ from `all-MiniLM-L12-v2` on MAP (`p=0.339`). [Aggregate_Report_2026_03_05]

## Traceability Table

| Statement | Evidence |
|---|---|
| EN vs TR best-model switch | Aggregate MAP table + raw JSON MAP fields [Aggregate_Report_2026_03_05][Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05] |
| TR-domain MAP differences and difficulty shift | Aggregate MAP and dataset summary tables [Aggregate_Report_2026_03_05] |
| Consistency ranking and CV | Aggregate consistency tables [Aggregate_Report_2026_03_05] |
| Latency and throughput tradeoff | Aggregate timing tables [Aggregate_Report_2026_03_05] |
| Pipeline utility for fit-for-purpose model choice | Aggregate metrics + timing/report sections [Aggregate_Report_2026_03_05] |
| Dataset curation provenance and retrieval date | Dataset source references [TED_Regulations][BDDK_Mevzuat] |
