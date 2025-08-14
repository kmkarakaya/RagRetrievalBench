# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models

**Generated:** 2025-06-11 01:04:51

## Abstract

This paper presents a systematic evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **588 documents** and **50 queries** with **220 relevant document mappings**.

**Best performing model:** `sentence-transformers/all-MiniLM-L6-v2`
* MAP@10: **0.8264**
* Recall@10: **1.0000**
* Precision@10: **0.4889**
* NDCG@10: **0.9059**
* MRR@10: **0.9259**

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

- **Source documents**: PDF files from `utils/pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 588

The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence while ensuring manageable chunk sizes for embedding models.

#### Query Generation Process

- **LLM Model**: gemini-2.0-flash
- **Number of queries generated**: 50
- **Generation strategy**: Seed-chunk → Query → Retrieval → Label
- **Candidate pool size**: 10 chunks per query

Queries were generated using the following systematic approach:
1. Random sampling of seed chunks from the corpus
2. LLM-based question generation targeting specific chunks
3. Retrieval-based candidate identification using ChromaDB
4. LLM-based relevance labeling for comprehensive qrels

## Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Documents              |   588   |
| Average Chunk Length (words) |   151.9 |
| Median Chunk Length (words)  |   147   |
| Min Chunk Length (words)     |    33   |
| Max Chunk Length (words)     |   381   |
| Standard Deviation           |    32.5 |

#### Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |    50   |
| Average Query Length (words) |    19.7 |
| Median Query Length (words)  |    19   |
| Min Query Length (words)     |    10   |
| Max Query Length (words)     |    33   |
| Standard Deviation           |     4.9 |

#### Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 220     |
| Average Relevant Docs per Query | 4.9     |
| Median Relevant Docs per Query  | 5.0     |
| Min Relevant Docs               | 1       |
| Max Relevant Docs               | 10      |
| Coverage Ratio                  | 37.41%  |

## Experimental Setup

### Evaluation Framework

- **Vector Database**: ChromaDB
- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator
- **Retrieval Depth (k)**: 10
- **Batch Size**: 32
- **Collection Reinitialization**: True

### Evaluated Models

| Model Name                                                  | Collection   | Dimensions   | Type   |
|:------------------------------------------------------------|:-------------|:-------------|:-------|
| sentence-transformers/all-MiniLM-L6-v2                      | coll_v1      | N/A          | N/A    |
| sentence-transformers/all-mpnet-base-v2                     | coll_v2      | N/A          | N/A    |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | coll_v3      | N/A          | N/A    |
| sentence-transformers/all-MiniLM-L12-v2                     | coll_v4      | N/A          | N/A    |

### Evaluation Metrics

| Metric      | Description                                 | Measures                   |
|:------------|:--------------------------------------------|:---------------------------|
| MAP@k       | Mean Average Precision at rank k            | Ranking quality            |
| Recall@k    | Proportion of relevant docs in top k        | Coverage                   |
| Precision@k | Proportion of relevant docs among retrieved | Accuracy                   |
| NDCG@k      | Normalized Discounted Cumulative Gain       | Ranking with position bias |
| MRR@k       | Mean Reciprocal Rank                        | First relevant position    |

### Representative Query Examples

| Query ID                      | Query Text                                                                                                                                                  |   # Relevant Docs |
|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_Attention_chu<br/>nk31 | What are the effects of varying Transformer architecture parameters on English-to-German translation performance (BLEU score and perplexity)?               |                 3 |
| q2_for_Gemma_chunk8           | What is the architecture and training of the Gemma vision encoder, including its handling of non-square aspect ratios and high-resolution images?           |                 5 |
| q3_for_DeepSeek_chun<br/>k69  | How does redundant expert deployment achieve load balancing in Mixture of Experts (MoE) models, and what considerations are involved in its implementation? |                 2 |
| q4_for_Qwen_chunk83           | What is the Phi-3 technical report about a language model for phones?                                                                                       |                 2 |
| q5_for_DeepSeek_chun<br/>k75  | GPU co-processor for offloading communication tasks between InfiniBand and NVLink.                                                                          |                 2 |

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                                       |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |
|:------------------------------------------------------------|---------:|------------:|---------------:|----------:|---------:|
| sentence-transformers/all-MiniLM-L6-v2                      |   0.8264 |      1      |         0.4889 |    0.9059 |   0.9259 |
| sentence-transformers/all-mpnet-base-v2                     |   0.4829 |      0.6522 |         0.2933 |    0.6137 |   0.7867 |
| sentence-transformers/all-MiniLM-L12-v2                     |   0.4353 |      0.6033 |         0.28   |    0.5744 |   0.7699 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |   0.3823 |      0.55   |         0.24   |    0.5275 |   0.7788 |

### Performance Analysis

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/all-MiniLM-L6-v2** achieved the highest MAP@10 score of 0.8264, while **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** scored 0.3823, representing a **116.2% improvement**.

**MAP-Recall Correlation**: 1.000 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](model_comparison_2025-06-11_01-04-48.png)

*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](corpus_statistics_2025-06-11_01-04-48.png)

*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*

#### 6.3.3 Individual Metric Analysis

##### MAP@10 Results

![Map Comparison](map_comparison_2025-06-11_01-04-48.png)

##### RECALL@10 Results

![Recall Comparison](recall_comparison_2025-06-11_01-04-48.png)

##### PRECISION@10 Results

![Precision Comparison](precision_comparison_2025-06-11_01-04-48.png)

##### NDCG@10 Results

![Ndcg Comparison](ndcg_comparison_2025-06-11_01-04-48.png)

##### MRR@10 Results

![Mrr Comparison](mrr_comparison_2025-06-11_01-04-48.png)

### Statistical Significance Analysis

The following tables show absolute differences between model pairs. Differences greater than 0.05 may indicate practically significant improvements for real-world applications.

#### MAP@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-mpnet-base-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.3435*             | 0.3911*             | 0.4441*                                 |
| all-mpnet-base-v2                     | 0.3435*            | —                   | 0.0476              | 0.1006*                                 |
| all-MiniLM-L12-v2                     | 0.3911*            | 0.0476              | —                   | 0.0530*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.4441*            | 0.1006*             | 0.0530*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Recall@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-mpnet-base-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.3478*             | 0.3967*             | 0.4500*                                 |
| all-mpnet-base-v2                     | 0.3478*            | —                   | 0.0489              | 0.1021*                                 |
| all-MiniLM-L12-v2                     | 0.3967*            | 0.0489              | —                   | 0.0532*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.4500*            | 0.1021*             | 0.0532*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Precision@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-mpnet-base-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.1956*             | 0.2089*             | 0.2489*                                 |
| all-mpnet-base-v2                     | 0.1956*            | —                   | 0.0133              | 0.0533*                                 |
| all-MiniLM-L12-v2                     | 0.2089*            | 0.0133              | —                   | 0.0400                                  |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2489*            | 0.0533*             | 0.0400              | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### NDCG@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-mpnet-base-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.2922*             | 0.3316*             | 0.3784*                                 |
| all-mpnet-base-v2                     | 0.2922*            | —                   | 0.0394              | 0.0862*                                 |
| all-MiniLM-L12-v2                     | 0.3316*            | 0.0394              | —                   | 0.0469                                  |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.3784*            | 0.0862*             | 0.0469              | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### MRR@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-mpnet-base-v2   | all-MiniLM-L12-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.1393*             | 0.1560*             | 0.1471*                                 |
| all-mpnet-base-v2                     | 0.1393*            | —                   | 0.0167              | 0.0079                                  |
| all-MiniLM-L12-v2                     | 0.1560*            | 0.0167              | —                   | 0.0089                                  |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1471*            | 0.0079              | 0.0089              | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

## Embedding Performance Metrics

This section analyzes the computational efficiency of different embedding models during the corpus initialization phase, measuring the time required to embed and index 588 documents.

#### Embedding Speed Comparison

| Model                                                       |   Embedding Time (s) |   Docs/Second |   Avg Time/Doc (ms) |
|:------------------------------------------------------------|---------------------:|--------------:|--------------------:|
| sentence-transformers/all-MiniLM-L12-v2                     |                14.29 |         41.15 |               24.3  |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                14.37 |         40.92 |               24.44 |
| sentence-transformers/all-MiniLM-L6-v2                      |                14.53 |         40.47 |               24.71 |
| sentence-transformers/all-mpnet-base-v2                     |               143.48 |          4.1  |              244.01 |

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L12-v2` at 41.15 docs/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 4.10 docs/second
- **Performance ratio**: 10.04x speed difference between fastest and slowest
![Figure: Embedding Speed Comparison](timing_comparison_2025-06-11_01-04-48.png)

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

- **Collection identifier**: `coll_v1`
- **Model specifications**: Not available through SentenceTransformers interface

#### sentence-transformers/all-mpnet-base-v2

- **Collection identifier**: `coll_v2`
- **Model specifications**: Not available through SentenceTransformers interface

#### sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

- **Collection identifier**: `coll_v3`
- **Model specifications**: Not available through SentenceTransformers interface

#### sentence-transformers/all-MiniLM-L12-v2

- **Collection identifier**: `coll_v4`
- **Model specifications**: Not available through SentenceTransformers interface

## Discussion

### Key Findings

1. **Model Performance Hierarchy**: sentence-transformers/all-MiniLM-L6-v2 emerged as the top performer, achieving superior results across multiple evaluation metrics.

2. **Performance Gaps**: The performance difference between the best and second-best models (0.3435 MAP@10) suggests that model selection significantly impacts retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided statistically robust comparisons of model performance. The results demonstrate that **sentence-transformers/all-MiniLM-L6-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.8264. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2025-06-11_01-04-48.*
*Source code and evaluation data available at the project repository.*
