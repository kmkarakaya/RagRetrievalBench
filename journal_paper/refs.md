# References (Canonical Source: `refs.md`)

This file is the single source of truth for citation metadata and keys used in all journal markdown sections.

## Citation Key Rules
- Key format: `FirstMeaningfulWord_Qualifier`
- Allowed chars: ASCII letters, numbers, underscore
- First char: letter
- No spaces, hyphens, punctuation
- Keys are stable once introduced

## Reference Entries

[Aggregate_Report_2026_03_05]
- type: dataset-artifact-report
- authors_or_org: RagRetrievalBench Aggregate Reporting System
- title: Cross-Dataset Embedding Model Comparison Report
- venue_or_publisher: Local pipeline output
- year: 2026
- path_or_url: `aggregated_reports/2026-03-05_11-32-49/aggregate_report.md`
- accessed_or_retrieved: 2026-03-05
- note: Frozen baseline aggregate report used for cross-dataset analysis

[Raw_Education_Eng_2026_03_05]
- type: dataset-artifact-raw-results
- authors_or_org: RagRetrievalBench Evaluation Pipeline
- title: Raw Results for education_eng
- venue_or_publisher: Local pipeline output
- year: 2026
- path_or_url: `datasets/education_eng/reports/raw_results_2026-03-05_11-27-28.json`
- accessed_or_retrieved: 2026-03-05
- note: Primary quantitative source for education_eng metrics/timing

[Raw_Education_Tr_2026_03_05]
- type: dataset-artifact-raw-results
- authors_or_org: RagRetrievalBench Evaluation Pipeline
- title: Raw Results for education_tr
- venue_or_publisher: Local pipeline output
- year: 2026
- path_or_url: `datasets/education_tr/reports/raw_results_2026-03-05_11-29-07.json`
- accessed_or_retrieved: 2026-03-05
- note: Primary quantitative source for education_tr metrics/timing

[Raw_Law_Tr_2026_03_05]
- type: dataset-artifact-raw-results
- authors_or_org: RagRetrievalBench Evaluation Pipeline
- title: Raw Results for law_tr
- venue_or_publisher: Local pipeline output
- year: 2026
- path_or_url: `datasets/law_tr/reports/raw_results_2026-03-05_11-30-27.json`
- accessed_or_retrieved: 2026-03-05
- note: Primary quantitative source for law_tr metrics/timing

[Config_Py]
- type: software-config
- authors_or_org: RagRetrievalBench Project
- title: Benchmark Configuration File (`config.py`)
- venue_or_publisher: Repository source file
- year: 2026
- path_or_url: `config.py`
- accessed_or_retrieved: 2026-03-06
- note: Defines pipeline parameters, model list, and metric settings

[Rag_Benchmark_Py]
- type: software-pipeline
- authors_or_org: RagRetrievalBench Project
- title: Main Benchmark Pipeline (`rag_benchmark.py`)
- venue_or_publisher: Repository source file
- year: 2026
- path_or_url: `rag_benchmark.py`
- accessed_or_retrieved: 2026-03-06
- note: Implements end-to-end benchmark workflow and report generation

[GitHub_RagRetrievalBench]
- type: software-repository
- authors_or_org: Karakaya, Murat
- title: RagRetrievalBench GitHub Repository
- venue_or_publisher: GitHub
- year: 2026
- path_or_url: `https://github.com/kmkarakaya/RagRetrievalBench.git`
- accessed_or_retrieved: 2026-03-06
- note: Public code release for pipeline reproducibility and reuse

[TED_Regulations]
- type: web-dataset-source
- authors_or_org: TED University
- title: Regulations and Guidelines for Education
- venue_or_publisher: TED University Official Website
- year: 2026
- path_or_url: `https://www.tedu.edu.tr/en/regulations-and-guidelines-education`
- accessed_or_retrieved: 2026-01-01
- note: Source used to curate `education_eng` and `education_tr` datasets

[BDDK_Mevzuat]
- type: web-dataset-source
- authors_or_org: Bankacilik Duzenleme ve Denetleme Kurumu (BDDK)
- title: Mevzuat Listesi
- venue_or_publisher: BDDK Official Website
- year: 2026
- path_or_url: `https://www.bddk.org.tr/Mevzuat/Liste/49`
- accessed_or_retrieved: 2026-01-01
- note: Source used to curate `law_tr` dataset

[Lewis_RAG_2021]
- type: article-preprint
- authors_or_org: Lewis, Patrick et al.
- title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- venue_or_publisher: arXiv
- year: 2021
- path_or_url: `https://arxiv.org/abs/2005.11401`
- accessed_or_retrieved: 2026-03-06
- note: Foundational RAG reference

[Karakaya_Conference_2025]
- type: conference-paper
- authors_or_org: Karakaya, Murat
- title: Local Benchmarking of Sentence Embedding Models for Retrieval-Augmented Generation
- venue_or_publisher: TheIIER International Conference, Madrid, Spain
- year: 2025
- path_or_url: `publishedConferencePaper.pdf`
- accessed_or_retrieved: 2026-03-06
- note: Preliminary study referenced briefly in related work

[SentenceTransformers_Pretrained]
- type: documentation
- authors_or_org: Sentence Transformers Project
- title: Pretrained Models Documentation
- venue_or_publisher: Sentence Transformers Documentation
- year: 2026
- path_or_url: `https://www.sbert.net/docs/sentence_transformer/pretrained_models.html`
- accessed_or_retrieved: 2026-03-06
- note: Embedding model catalog and model details

[HuggingFace_SentenceTransformers]
- type: model-hub
- authors_or_org: Hugging Face
- title: Sentence-Transformers Model Hub
- venue_or_publisher: Hugging Face
- year: 2026
- path_or_url: `https://huggingface.co/sentence-transformers`
- accessed_or_retrieved: 2026-03-06
- note: Popularity/download context for model selection

[ChromaDB_Docs]
- type: documentation
- authors_or_org: Chroma
- title: ChromaDB Documentation
- venue_or_publisher: Chroma Documentation
- year: 2026
- path_or_url: `https://docs.trychroma.com`
- accessed_or_retrieved: 2026-03-06
- note: Vector store and retrieval backend reference

## Citation Usage Notes
- Use only key citations from this file in all manuscript sections.
- Use citation format `key_word` wrapped in square brackets in prose/tables/figure notes.
- Do not use numeric or evidence-tag citation styles.
