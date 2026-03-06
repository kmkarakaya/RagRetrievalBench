# Introduction

This paper aims to create and test an embedding benchmarking pipeline that can evaluate different embedding model performances on local datasets so users can choose the best suitable embedding model for user/application requirements. The contribution is therefore not a universal ranking claim; it is a practical decision-support pipeline for developers and practitioners building Retrieval-Augmented Generation (RAG) systems. [Aggregate_Report_2026_03_05][Rag_Benchmark_Py]

RAG quality depends on retrieval quality, and retrieval quality depends on how well the embedding model matches the target corpus. Public benchmark leaderboards are useful references, but they are insufficient for direct deployment decisions on local documents. For practical engineering, the key question is: which embedding model is most suitable for this dataset and this application constraint profile? [Lewis_RAG_2021]

## Motivation

Teams deploying RAG systems usually need a repeatable and local workflow that can:
- evaluate multiple embedding models under one fixed setup,
- generate automatic benchmarking reports across various metrics,
- and compare models across multiple datasets before production selection.

The proposed pipeline addresses this gap by producing well-structured dynamic report outputs (timestamped markdown/pdf + visualizations) and by supporting cross-dataset comparison for dataset-specific model selection.

## Study Setup

The effectiveness of the pipeline is demonstrated with 3 datasets and 5 models in a frozen 2026-03-05 run family:
- Datasets: `education_eng`, `education_tr`, `law_tr`
- Embedding models: 5 sentence-transformer models configured in `config.py`
- Education datasets were curated from TED University regulations/guidelines source URL on `01/01/2026`.
- Law dataset was curated from BDDK regulations source URL on `01/01/2026`.
- Dataset evidence source keys: [Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05][Raw_Law_Tr_2026_03_05][TED_Regulations][BDDK_Mevzuat]

This setup enables controlled analysis of:
- language sensitivity within education (`education_eng` vs `education_tr`),
- domain sensitivity within Turkish (`education_tr` vs `law_tr`),
- and quality-speed tradeoffs relevant to deployment.

## Contributions

1. We present a reusable local embedding benchmarking pipeline for practical model selection.
2. We show that the pipeline produces automatic benchmarking reports across various metrics and runtime measurements.
3. We show that the same pipeline supports cross-dataset comparison for dataset-specific model selection.
4. We demonstrate the full workflow with 3 datasets and 5 models and provide traceable, timestamped artifacts.
5. We make the pipeline reusable by any developer through the public repository: `https://github.com/kmkarakaya/RagRetrievalBench.git`. [GitHub_RagRetrievalBench]

## Research Questions

- RQ1 (Pipeline Utility): Can the proposed pipeline provide actionable evidence for selecting embeddings on local datasets?
- RQ2 (Language Effect): Do model rankings and MAP outcomes change between English and Turkish education datasets under identical settings?
- RQ3 (Domain Effect): How do model performance profiles change between Turkish education and Turkish law datasets?
- RQ4 (Operational Tradeoff): How does the pipeline expose quality-speed tradeoffs (MAP, latency, throughput) for fit-for-purpose selection?

## Study Boundaries

- Claims are bounded to the frozen run and evaluated datasets.
- Results are used to demonstrate pipeline effectiveness and practical utility.
- We do not claim universal model superiority beyond this setup.
- Submission-quality validity additions (human qrels audit and compute environment) are tracked as pending in this draft; baseline dataset provenance is now documented.
