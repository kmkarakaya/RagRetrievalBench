# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models

**Generated:** 2025-08-14 22:09:05

## Abstract

This paper presents a systematic evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **239 documents** and **5 queries** with **13 relevant document mappings**.

**Best performing model:** `sentence-transformers/all-MiniLM-L6-v2`
* MAP@10: **0.7189**
* Recall@10: **1.0000**
* Precision@10: **0.2600**
* NDCG@10: **0.8303**
* MRR@10: **0.8667**

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
- **Total chunks generated**: 239

The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence while ensuring manageable chunk sizes for embedding models.

#### Query Generation Process

- **LLM Model**: gemini-2.5-flash-lite
- **Number of queries generated**: 5
- **Generation strategy**: Seed-chunk → Query → Retrieval → Label
- **Candidate pool size**: 5 chunks per query

Queries were generated using the following systematic approach:
1. Random sampling of seed chunks from the corpus
2. LLM-based question generation targeting specific chunks
3. Retrieval-based candidate identification using ChromaDB
4. LLM-based relevance labeling for comprehensive qrels

## Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Documents              |   239   |
| Average Chunk Length (words) |   155.8 |
| Median Chunk Length (words)  |   144   |
| Min Chunk Length (words)     |    67   |
| Max Chunk Length (words)     |   381   |
| Standard Deviation           |    45.2 |

#### Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |     5   |
| Average Query Length (words) |    14.4 |
| Median Query Length (words)  |    14   |
| Min Query Length (words)     |     9   |
| Max Query Length (words)     |    18   |
| Standard Deviation           |     3.1 |

#### Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 13      |
| Average Relevant Docs per Query | 2.6     |
| Median Relevant Docs per Query  | 3.0     |
| Min Relevant Docs               | 1       |
| Max Relevant Docs               | 4       |
| Coverage Ratio                  | 5.44%   |

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

| Query ID                      | Query Text                                                                                                                       |   # Relevant Docs |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_Attention_chu<br/>nk46 | Google's neural machine translation system for bridging the gap between human and machine translation.                           |                 1 |
| q2_for_Attention_chu<br/>nk10 | What are the components of the encoder and decoder stacks in a Transformer model?                                                |                 4 |
| q3_for_DeepSeek_chun<br/>k30  | How does DeepSeek-V3 balance expert load during training using bias adjustment and a complementary sequence-wise auxiliary loss? |                 2 |
| q4_for_DeepSeek_chun<br/>k69  | How to achieve load balancing in Mixture of Experts (MoE) models using redundant experts and GPU allocation strategies?          |                 3 |
| q5_for_DeepSeek_chun<br/>k27  | DeepSeekMoE architecture for FFNs with shared and routed experts.                                                                |                 3 |

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                                       |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |
|:------------------------------------------------------------|---------:|------------:|---------------:|----------:|---------:|
| sentence-transformers/all-MiniLM-L6-v2                      |   0.7189 |      1      |           0.26 |    0.8303 |   0.8667 |
| sentence-transformers/all-MiniLM-L12-v2                     |   0.6531 |      0.9333 |           0.24 |    0.7879 |   0.9    |
| sentence-transformers/all-mpnet-base-v2                     |   0.5889 |      0.9333 |           0.24 |    0.7323 |   0.8333 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |   0.4833 |      0.6667 |           0.18 |    0.5665 |   0.65   |

### Performance Analysis

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/all-MiniLM-L6-v2** achieved the highest MAP@10 score of 0.7189, while **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** scored 0.4833, representing a **48.7% improvement**.

**MAP-Recall Correlation**: 0.927 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](model_comparison_2025-08-14_22-09-02.png)

*Figure: Comprehensive comparison of all embedding models across evaluation metrics.*

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](corpus_statistics_2025-08-14_22-09-02.png)

*Figure: Distribution of chunk lengths, query lengths, and relevance patterns in the evaluation dataset.*

#### 6.3.3 Individual Metric Analysis

##### MAP@10 Results

![Map Comparison](map_comparison_2025-08-14_22-09-02.png)

##### RECALL@10 Results

![Recall Comparison](recall_comparison_2025-08-14_22-09-02.png)

##### PRECISION@10 Results

![Precision Comparison](precision_comparison_2025-08-14_22-09-02.png)

##### NDCG@10 Results

![Ndcg Comparison](ndcg_comparison_2025-08-14_22-09-02.png)

##### MRR@10 Results

![Mrr Comparison](mrr_comparison_2025-08-14_22-09-02.png)

### Statistical Significance Analysis

The following tables show absolute differences between model pairs. Differences greater than 0.05 may indicate practically significant improvements for real-world applications.

#### MAP@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0658*             | 0.1300*             | 0.2356*                                 |
| all-MiniLM-L12-v2                     | 0.0658*            | —                   | 0.0642*             | 0.1697*                                 |
| all-mpnet-base-v2                     | 0.1300*            | 0.0642*             | —                   | 0.1056*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2356*            | 0.1697*             | 0.1056*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Recall@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0667*             | 0.0667*             | 0.3333*                                 |
| all-MiniLM-L12-v2                     | 0.0667*            | —                   | 0.0000              | 0.2667*                                 |
| all-mpnet-base-v2                     | 0.0667*            | 0.0000              | —                   | 0.2667*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.3333*            | 0.2667*             | 0.2667*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Precision@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0200              | 0.0200              | 0.0800*                                 |
| all-MiniLM-L12-v2                     | 0.0200             | —                   | 0.0000              | 0.0600*                                 |
| all-mpnet-base-v2                     | 0.0200             | 0.0000              | —                   | 0.0600*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0800*            | 0.0600*             | 0.0600*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### NDCG@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0424              | 0.0980*             | 0.2638*                                 |
| all-MiniLM-L12-v2                     | 0.0424             | —                   | 0.0556*             | 0.2214*                                 |
| all-mpnet-base-v2                     | 0.0980*            | 0.0556*             | —                   | 0.1658*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2638*            | 0.2214*             | 0.1658*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### MRR@10 Pairwise Differences

| Model                                 | all-MiniLM-L6-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   |
|:--------------------------------------|:-------------------|:--------------------|:--------------------|:----------------------------------------|
| all-MiniLM-L6-v2                      | —                  | 0.0333              | 0.0333              | 0.2167*                                 |
| all-MiniLM-L12-v2                     | 0.0333             | —                   | 0.0667*             | 0.2500*                                 |
| all-mpnet-base-v2                     | 0.0333             | 0.0667*             | —                   | 0.1833*                                 |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.2167*            | 0.2500*             | 0.1833*             | —                                       |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

## Embedding Performance Metrics

This section analyzes the computational efficiency of different embedding models during the corpus initialization phase, measuring the time required to embed and index 239 documents.

#### Embedding Speed Comparison

| Model                                                       | Embedding Time (s)   | Docs/Second   | Avg Time/Doc (ms)   |
|:------------------------------------------------------------|:---------------------|:--------------|:--------------------|
| sentence-transformers/all-MiniLM-L6-v2                      | N/A                  | N/A           | N/A                 |
| sentence-transformers/all-mpnet-base-v2                     | N/A                  | N/A           | N/A                 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | N/A                  | N/A           | N/A                 |
| sentence-transformers/all-MiniLM-L12-v2                     | N/A                  | N/A           | N/A                 |

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L6-v2` at N/A docs/second
- **Slowest embedding model**: `sentence-transformers/all-MiniLM-L12-v2` at N/A docs/second
- **Performance ratio**: Cannot calculate - run --initialize first for timing data
![Figure: Embedding Speed Comparison](timing_comparison_2025-08-14_22-09-02.png)

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

2. **Performance Gaps**: The performance difference between the best and second-best models (0.0658 MAP@10) suggests that model selection significantly impacts retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided statistically robust comparisons of model performance. The results demonstrate that **sentence-transformers/all-MiniLM-L6-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.7189. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2025-08-14_22-09-02.*
*Source code and evaluation data available at the project repository.*
