# RAG Retrieval Benchmark: Finance Dataset Evaluation

**Dataset:** Finance
**Generated:** 2026-01-25 21:31:33

## Abstract

This paper presents a systematic evaluation of embedding models on the finance dataset within Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG) on the finance dataset. The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **1 PDF document(s)** that were processed into **50 document chunks** and **5 queries** with **17 relevant document mappings**.

**Best performing model:** `sentence-transformers/all-MiniLM-L6-v2`
* MAP@10: **0.8419**
* Recall@10: **1.0000**
* Precision@10: **0.3400**
* NDCG@10: **0.9252**
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

- **Source PDF documents**: 1 file(s) from `datasets\finance\pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 50

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

## Finance Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Source PDF Documents         |     1   |
| Total Document Chunks        |    50   |
| Average Chunk Length (words) |   146.2 |
| Median Chunk Length (words)  |   145   |
| Min Chunk Length (words)     |    67   |
| Max Chunk Length (words)     |   193   |
| Standard Deviation           |    19.8 |

#### Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |     5   |
| Average Query Length (words) |    11.8 |
| Median Query Length (words)  |    12   |
| Min Query Length (words)     |     6   |
| Max Query Length (words)     |    18   |
| Standard Deviation           |     4.7 |

#### Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 17      |
| Average Relevant Docs per Query | 3.4     |
| Median Relevant Docs per Query  | 2.0     |
| Min Relevant Docs               | 1       |
| Max Relevant Docs               | 8       |
| Coverage Ratio                  | 34.00%  |

## Experimental Setup

### Evaluation Framework

- **Vector Database**: ChromaDB
- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator
- **Retrieval Depth (k)**: 10
- **Batch Size**: 32
- **Collection Reinitialization**: True

### Evaluated Models

| Model Name                                                  | Collection      |   Dimensions | Type                 |
|:------------------------------------------------------------|:----------------|-------------:|:---------------------|
| sentence-transformers/all-MiniLM-L6-v2                      | finance_coll_v1 |          384 | Sentence Transformer |
| sentence-transformers/all-mpnet-base-v2                     | finance_coll_v2 |          768 | Sentence Transformer |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | finance_coll_v3 |          384 | Sentence Transformer |
| sentence-transformers/all-MiniLM-L12-v2                     | finance_coll_v4 |          384 | Sentence Transformer |

### Evaluation Metrics

| Metric      | Description                                 | Measures                   |
|:------------|:--------------------------------------------|:---------------------------|
| MAP@k       | Mean Average Precision at rank k            | Ranking quality            |
| Recall@k    | Proportion of relevant docs in top k        | Coverage                   |
| Precision@k | Proportion of relevant docs among retrieved | Accuracy                   |
| NDCG@k      | Normalized Discounted Cumulative Gain       | Ranking with position bias |
| MRR@k       | Mean Reciprocal Rank                        | First relevant position    |

### Representative Query Examples

| Query ID                      | Query Text                                                                                                      |   # Relevant Docs |
|:------------------------------|:----------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_Attention_chu<br/>nk40 | What are some key papers in sequence learning and deep learning, including work on LSTMs and residual networks? |                 4 |
| q2_for_Attention_chu<br/>nk9  | Transformer model architecture for sequence transduction                                                        |                 8 |
| q3_for_Attention_chu<br/>nk25 | What are the training data, hardware, and schedule used for language models?                                    |                 1 |
| q4_for_Attention_chu<br/>nk28 | What are the dropout and label smoothing techniques used in the Transformer model for machine translation?      |                 2 |
| q5_for_Attention_chu<br/>nk49 | What is the ideal application of law?                                                                           |                 2 |

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                 |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |
|:--------------------------------------|---------:|------------:|---------------:|----------:|---------:|
| all-MiniLM-L6-v2                      |   0.8419 |       1     |           0.34 |    0.9252 |   1      |
| all-MiniLM-L12-v2                     |   0.7474 |       0.925 |           0.28 |    0.8627 |   1      |
| paraphrase-multilingual-MiniLM-L12-v2 |   0.558  |       0.85  |           0.24 |    0.705  |   0.8333 |
| all-mpnet-base-v2                     |   0.5417 |       0.75  |           0.24 |    0.6742 |   0.85   |

### Performance Analysis

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/all-MiniLM-L6-v2** achieved the highest MAP@10 score of 0.8419, while **sentence-transformers/all-mpnet-base-v2** scored 0.5417, representing a **55.4% improvement**.

**MAP-Recall Correlation**: 0.939 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](finance_model_comparison_2026-01-25_21-31-30.png)

*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](finance_corpus_statistics_2026-01-25_21-31-30.png)

*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*

#### 6.3.3 Individual Metric Analysis

##### MAP@10 Results

![Map Comparison](finance_map_comparison_2026-01-25_21-31-30.png)

##### RECALL@10 Results

![Recall Comparison](finance_recall_comparison_2026-01-25_21-31-30.png)

##### PRECISION@10 Results

![Precision Comparison](finance_precision_comparison_2026-01-25_21-31-30.png)

##### NDCG@10 Results

![Ndcg Comparison](finance_ndcg_comparison_2026-01-25_21-31-30.png)

##### MRR@10 Results

![Mrr Comparison](finance_mrr_comparison_2026-01-25_21-31-30.png)

### Statistical Significance Analysis

The following tables show absolute differences between model pairs. Differences greater than 0.05 may indicate practically significant improvements for real-world applications.

#### MAP@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:-------------------|:--------------------|:----------------------------------------|:--------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0945*             | 0.2839*                                 | 0.3002*             |
| all-MiniLM-L12-v2                     | 0.0945*            | —                   | 0.1894*                                 | 0.2057*             |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2839*            | 0.1894*             | —                                       | 0.0163              |
| all-mpnet-base-v2                     | 0.3002*            | 0.2057*             | 0.0163                                  | —                   |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Recall@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:-------------------|:--------------------|:----------------------------------------|:--------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0750*             | 0.1500*                                 | 0.2500*             |
| all-MiniLM-L12-v2                     | 0.0750*            | —                   | 0.0750*                                 | 0.1750*             |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1500*            | 0.0750*             | —                                       | 0.1000*             |
| all-mpnet-base-v2                     | 0.2500*            | 0.1750*             | 0.1000*                                 | —                   |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Precision@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:-------------------|:--------------------|:----------------------------------------|:--------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0600*             | 0.1000*                                 | 0.1000*             |
| all-MiniLM-L12-v2                     | 0.0600*            | —                   | 0.0400                                  | 0.0400              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1000*            | 0.0400              | —                                       | 0.0000              |
| all-mpnet-base-v2                     | 0.1000*            | 0.0400              | 0.0000                                  | —                   |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### NDCG@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:-------------------|:--------------------|:----------------------------------------|:--------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0625*             | 0.2202*                                 | 0.2510*             |
| all-MiniLM-L12-v2                     | 0.0625*            | —                   | 0.1577*                                 | 0.1885*             |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2202*            | 0.1577*             | —                                       | 0.0308              |
| all-mpnet-base-v2                     | 0.2510*            | 0.1885*             | 0.0308                                  | —                   |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### MRR@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:-------------------|:--------------------|:----------------------------------------|:--------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0000              | 0.1667*                                 | 0.1500*             |
| all-MiniLM-L12-v2                     | 0.0000             | —                   | 0.1667*                                 | 0.1500*             |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1667*            | 0.1667*             | —                                       | 0.0167              |
| all-mpnet-base-v2                     | 0.1500*            | 0.1500*             | 0.0167                                  | —                   |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

## Embedding Performance Metrics

This section analyzes the computational efficiency of different embedding models during the corpus initialization phase, measuring the time required to embed and index 50 document chunks.

#### Embedding Speed Comparison

| Model                                                       |   Embedding Time (s) |   Docs/Second |   Avg Time/Doc (ms) |
|:------------------------------------------------------------|---------------------:|--------------:|--------------------:|
| sentence-transformers/all-MiniLM-L6-v2                      |                 1.42 |         35.22 |               28.4  |
| sentence-transformers/all-MiniLM-L12-v2                     |                 1.45 |         34.43 |               29.05 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                 1.55 |         32.16 |               31.1  |
| sentence-transformers/all-mpnet-base-v2                     |                11.73 |          4.26 |              234.68 |

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L6-v2` at 35.22 docs/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 4.26 docs/second
- **Performance ratio**: 8.27x speed difference between fastest and slowest
![Figure: Embedding Speed Comparison](timing_comparison_2026-01-25_21-31-30.png)

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

- **Collection identifier**: `finance_coll_v1`
- **Embedding dimension**: 384
- **Maximum sequence length**: 256
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-mpnet-base-v2

- **Collection identifier**: `finance_coll_v2`
- **Embedding dimension**: 768
- **Maximum sequence length**: 384
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

- **Collection identifier**: `finance_coll_v3`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-MiniLM-L12-v2

- **Collection identifier**: `finance_coll_v4`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

## Discussion

### Key Findings

1. **Model Performance Hierarchy**: sentence-transformers/all-MiniLM-L6-v2 emerged as the top performer, achieving superior results across multiple evaluation metrics.

2. **Performance Gaps**: The performance difference between the best and second-best models (0.0945 MAP@10) suggests that model selection significantly impacts retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided statistically robust comparisons of model performance. The results demonstrate that **sentence-transformers/all-MiniLM-L6-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.8419. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2026-01-25_21-31-30.*
*Source code and evaluation data available at the project repository.*
