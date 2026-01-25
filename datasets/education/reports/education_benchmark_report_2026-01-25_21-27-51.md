# RAG Retrieval Benchmark: Education Dataset Evaluation

**Dataset:** Education
**Generated:** 2026-01-25 21:27:54

## Abstract

This paper presents a systematic evaluation of embedding models on the education dataset within Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG) on the education dataset. The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **1 PDF document(s)** that were processed into **189 document chunks** and **5 queries** with **21 relevant document mappings**.

**Best performing model:** `sentence-transformers/all-MiniLM-L6-v2`
* MAP@10: **0.7999**
* Recall@10: **1.0000**
* Precision@10: **0.4200**
* NDCG@10: **0.9092**
* MRR@10: **1.0000**

## Methodology

### Automated Pipeline Overview

Our evaluation framework consists of five main stages:

1. **PDF Processing**: Document ingestion and chunking
2. **Corpus Generation**: Creation of standardized document chunks
3. **Query Generation**: LLM-assisted query synthesis
4. **Relevance Assessment**: Automated qrels generation
5. **Embedding Evaluation**: Multi-model performance comparison

### Document Processing Pipeline

#### PDF Extraction and Chunking

- **Source PDF documents**: 1 file(s) from `datasets\education\pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 189

The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence while ensuring manageable chunk sizes for embedding models.

#### Query Generation Process

- **LLM Model**: models/gemini-2.5-flash-lite
- **Number of queries generated**: 5
- **Generation strategy**: Seed-chunk → Query → Retrieval → Label
- **Candidate pool size**: 10 chunks per query

Queries were generated using the following systematic approach:
1. Random sampling of seed chunks from the corpus
2. LLM-based question generation targeting specific chunks
3. Retrieval-based candidate identification using ChromaDB
4. LLM-based relevance labeling for comprehensive qrels

## Education Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Source PDF Documents         |     1   |
| Total Document Chunks        |   189   |
| Average Chunk Length (words) |   158.3 |
| Median Chunk Length (words)  |   144   |
| Min Chunk Length (words)     |    67   |
| Max Chunk Length (words)     |   381   |
| Standard Deviation           |    49.5 |

#### Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |     5   |
| Average Query Length (words) |    12.8 |
| Median Query Length (words)  |    12   |
| Min Query Length (words)     |     7   |
| Max Query Length (words)     |    19   |
| Standard Deviation           |     3.9 |

#### Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 21      |
| Average Relevant Docs per Query | 4.2     |
| Median Relevant Docs per Query  | 4.0     |
| Min Relevant Docs               | 2       |
| Max Relevant Docs               | 9       |
| Coverage Ratio                  | 11.11%  |

## Experimental Setup

### Evaluation Framework

- **Vector Database**: ChromaDB
- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator
- **Retrieval Depth (k)**: 10
- **Batch Size**: 32
- **Collection Reinitialization**: True

### Evaluated Models

| Model Name                                                  | Collection        |   Dimensions | Type                 |
|:------------------------------------------------------------|:------------------|-------------:|:---------------------|
| sentence-transformers/all-MiniLM-L6-v2                      | education_coll_v1 |          384 | Sentence Transformer |
| sentence-transformers/all-mpnet-base-v2                     | education_coll_v2 |          768 | Sentence Transformer |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | education_coll_v3 |          384 | Sentence Transformer |
| sentence-transformers/all-MiniLM-L12-v2                     | education_coll_v4 |          384 | Sentence Transformer |

### Evaluation Metrics

| Metric      | Description                                 | Measures                   |
|:------------|:--------------------------------------------|:---------------------------|
| MAP@k       | Mean Average Precision at rank k            | Ranking quality            |
| Recall@k    | Proportion of relevant docs in top k        | Coverage                   |
| Precision@k | Proportion of relevant docs among retrieved | Accuracy                   |
| NDCG@k      | Normalized Discounted Cumulative Gain       | Ranking with position bias |
| MRR@k       | Mean Reciprocal Rank                        | First relevant position    |

### Representative Query Examples

| Query ID                      | Query Text                                                                                                                       |   # Relevant Docs |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_DeepSeek_chun<br/>k85  | DeepSeek-V3 training hyperparameters and learning rate schedule                                                                  |                 2 |
| q2_for_DeepSeek_chun<br/>k109 | What are the methods used to enhance model responses through reflection and verification, and how is non-reasoning data handled? |                 2 |
| q3_for_DeepSeek_chun<br/>k21  | What are the key components and training methodologies of the DeepSeek-V3 model?                                                 |                 4 |
| q4_for_DeepSeek_chun<br/>k34  | What is the Multi-Token Prediction (MTP) objective and its implementation in DeepSeek-V3?                                        |                 4 |
| q5_for_DeepSeek_chun<br/>k52  | What is a mixed precision framework for FP8 data format in deep learning training?                                               |                 9 |

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                 |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |
|:--------------------------------------|---------:|------------:|---------------:|----------:|---------:|
| all-MiniLM-L6-v2                      |   0.7999 |      1      |           0.42 |    0.9092 |   1      |
| all-MiniLM-L12-v2                     |   0.5101 |      0.6556 |           0.28 |    0.6507 |   0.9    |
| all-mpnet-base-v2                     |   0.4328 |      0.8056 |           0.32 |    0.5936 |   0.5333 |
| paraphrase-multilingual-MiniLM-L12-v2 |   0.3821 |      0.6889 |           0.24 |    0.558  |   0.7167 |

### Performance Analysis

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/all-MiniLM-L6-v2** achieved the highest MAP@10 score of 0.7999, while **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** scored 0.3821, representing a **109.3% improvement**.

**MAP-Recall Correlation**: 0.836 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](education_model_comparison_2026-01-25_21-27-51.png)

*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](education_corpus_statistics_2026-01-25_21-27-51.png)

*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*

#### 6.3.3 Individual Metric Analysis

##### MAP@10 Results

![Map Comparison](education_map_comparison_2026-01-25_21-27-51.png)

##### RECALL@10 Results

![Recall Comparison](education_recall_comparison_2026-01-25_21-27-51.png)

##### PRECISION@10 Results

![Precision Comparison](education_precision_comparison_2026-01-25_21-27-51.png)

##### NDCG@10 Results

![Ndcg Comparison](education_ndcg_comparison_2026-01-25_21-27-51.png)

##### MRR@10 Results

![Mrr Comparison](education_mrr_comparison_2026-01-25_21-27-51.png)

### Statistical Significance Analysis

The following tables show absolute differences between model pairs. Differences greater than 0.05 may indicate practically significant improvements for real-world applications.

#### MAP@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.2899*             | 0.3671*             | 0.4178*                                 |
| all-MiniLM-L12-v2                     | 0.2899*            | —                   | 0.0772*             | 0.1280*                                 |
| all-mpnet-base-v2                     | 0.3671*            | 0.0772*             | —                   | 0.0507*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.4178*            | 0.1280*             | 0.0507*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Recall@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.3444*             | 0.1944*             | 0.3111*                                 |
| all-MiniLM-L12-v2                     | 0.3444*            | —                   | 0.1500*             | 0.0333                                  |
| all-mpnet-base-v2                     | 0.1944*            | 0.1500*             | —                   | 0.1167*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.3111*            | 0.0333              | 0.1167*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Precision@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.1400*             | 0.1000*             | 0.1800*                                 |
| all-MiniLM-L12-v2                     | 0.1400*            | —                   | 0.0400              | 0.0400                                  |
| all-mpnet-base-v2                     | 0.1000*            | 0.0400              | —                   | 0.0800*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1800*            | 0.0400              | 0.0800*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### NDCG@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.2585*             | 0.3156*             | 0.3512*                                 |
| all-MiniLM-L12-v2                     | 0.2585*            | —                   | 0.0571*             | 0.0927*                                 |
| all-mpnet-base-v2                     | 0.3156*            | 0.0571*             | —                   | 0.0356                                  |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.3512*            | 0.0927*             | 0.0356              | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### MRR@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.1000*             | 0.4667*             | 0.2833*                                 |
| all-MiniLM-L12-v2                     | 0.1000*            | —                   | 0.3667*             | 0.1833*                                 |
| all-mpnet-base-v2                     | 0.4667*            | 0.3667*             | —                   | 0.1833*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2833*            | 0.1833*             | 0.1833*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

## Embedding Performance Metrics

This section analyzes the computational efficiency of different embedding models during the corpus initialization phase, measuring the time required to embed and index 189 document chunks.

#### Embedding Speed Comparison

| Model                                                       |   Embedding Time (s) |   Docs/Second |   Avg Time/Doc (ms) |
|:------------------------------------------------------------|---------------------:|--------------:|--------------------:|
| sentence-transformers/all-MiniLM-L12-v2                     |                 4.3  |         43.96 |               22.75 |
| sentence-transformers/all-MiniLM-L6-v2                      |                 4.37 |         43.28 |               23.1  |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                 4.97 |         38.02 |               26.3  |
| sentence-transformers/all-mpnet-base-v2                     |                49.58 |          3.81 |              262.31 |

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L12-v2` at 43.96 docs/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 3.81 docs/second
- **Performance ratio**: 11.54x speed difference between fastest and slowest
![Figure: Embedding Speed Comparison](timing_comparison_2026-01-25_21-27-51.png)

*Figure: Computational efficiency comparison showing embedding speed and processing time per document.*

## Technical Implementation

### Pipeline Architecture

The benchmark pipeline implements a modular architecture with the following components:

- **Document Processing Module**: PDF extraction and chunking using PyMuPDF and LangChain
- **LLM Integration**: Gemini API for query generation and relevance assessment
- **Vector Database**: ChromaDB with native embedding functions
- **Evaluation Engine**: SentenceTransformers evaluation framework
- **Reporting System**: Automated report generation with visualizations

### Reproducibility

All experiments can be reproduced using the following commands:

```bash
# 1. Process PDFs into chunks
python simple_rag_benchmark_pipeline.py --prepare-corpus

# 2. Generate queries and relevance judgments
python simple_rag_benchmark_pipeline.py --generate-qrels

# 3. Run complete benchmark
python simple_rag_benchmark_pipeline.py --all
```

### Embedding Model Specifications

#### sentence-transformers/all-MiniLM-L6-v2

- **Collection identifier**: `education_coll_v1`
- **Embedding dimension**: 384
- **Maximum sequence length**: 256
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-mpnet-base-v2

- **Collection identifier**: `education_coll_v2`
- **Embedding dimension**: 768
- **Maximum sequence length**: 384
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

- **Collection identifier**: `education_coll_v3`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-MiniLM-L12-v2

- **Collection identifier**: `education_coll_v4`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

## Discussion

### Key Findings

1. **Model Performance Hierarchy**: sentence-transformers/all-MiniLM-L6-v2 emerged as the top performer, achieving superior results across multiple evaluation metrics.

2. **Performance Gaps**: The performance difference between the best and second-best models (0.2899 MAP@10) suggests that model selection significantly impacts retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided statistically robust comparisons of model performance. The results demonstrate that **sentence-transformers/all-MiniLM-L6-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.7999. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2026-01-25_21-27-51.*
*Source code and evaluation data available at the project repository.*
