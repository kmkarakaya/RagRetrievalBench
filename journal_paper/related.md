# Related Work

## RAG Retrieval Evaluation and Embedding Benchmarking

RAG systems combine retrieval and generation, so retrieval quality directly affects answer grounding and reliability. Prior work has shown that embedding choice and retrieval configuration strongly influence downstream performance. However, many benchmark studies are leaderboard-oriented and evaluated on standardized corpora, which may not reflect local enterprise or domain-specific collections. [Lewis_RAG_2021]

Recent work also highlights practical requirements beyond ranking quality: reproducibility, runtime efficiency, and task-aligned validation. This motivates reusable local benchmarking pipelines that can produce decision-ready outputs for developers. [SentenceTransformers_Pretrained][HuggingFace_SentenceTransformers][ChromaDB_Docs]

## Preliminary Conference Study (Short Context)

Our earlier conference paper (`publishedConferencePaper.pdf`) introduced a local automated benchmark pipeline and demonstrated it on a single technical English corpus. That preliminary work established feasibility for end-to-end automated evaluation with synthetic queries, LLM-based qrels, and multi-model retrieval metrics. [Karakaya_Conference_2025]

## Extension in the Current Journal Work

This journal manuscript extends the preliminary work in scope and practical selection value: it uses a frozen cross-dataset setup with `education_eng`, `education_tr`, and `law_tr`, and evaluates 5 embedding models under one consistent pipeline configuration. The dataset sources are explicitly documented (TED regulations/guidelines for education datasets and BDDK regulations for law dataset, retrieved on 01/01/2026). The extension adds aggregate cross-dataset ranking, consistency analysis, and quality-speed analysis, plus automatic benchmarking reports across various metrics, to support cross-dataset comparison for dataset-specific model selection. [Aggregate_Report_2026_03_05][Raw_Education_Eng_2026_03_05][Raw_Education_Tr_2026_03_05][Raw_Law_Tr_2026_03_05][TED_Regulations][BDDK_Mevzuat]

In short, the conference paper is context only; the journal evidence is driven by the current multi-dataset artifacts and emphasizes that the pipeline is reusable by any developer for choosing the best suitable embedding model for user/application requirements. [Karakaya_Conference_2025][GitHub_RagRetrievalBench]
