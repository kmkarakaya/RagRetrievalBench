# RAG Retrieval Benchmark: Education Dataset Evaluation

**Dataset:** Education
**Generated:** 2026-02-07 15:14:40

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

**Table: Corpus Characteristics Summary**

**Column Explanations:**
- **Source PDF Documents**: Number of original PDF files processed
- **Total Document Chunks**: Number of text chunks created from PDFs
- **Average Chunk Length**: Mean number of words per chunk
- **Median Chunk Length**: Middle value of chunk lengths (resistant to outliers)
- **Min/Max Chunk Length**: Range of chunk sizes
- **Standard Deviation**: Variability in chunk lengths

**How to interpret:**
- **High variability** (large std dev) indicates inconsistent chunking
- **Very short chunks** may lose context, very long chunks may be noisy
- **Chunk count** affects retrieval efficiency and memory usage

#### Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |     5   |
| Average Query Length (words) |    12.8 |
| Median Query Length (words)  |    12   |
| Min Query Length (words)     |     7   |
| Max Query Length (words)     |    19   |
| Standard Deviation           |     3.9 |

**Table: Query Characteristics Summary**

**Column Explanations:**
- **Total Queries**: Number of evaluation queries generated
- **Average Query Length**: Mean number of words per query
- **Median Query Length**: Middle value of query lengths
- **Min/Max Query Length**: Range of query lengths
- **Standard Deviation**: Variability in query lengths

**How to interpret:**
- **Query length** affects retrieval difficulty (longer = more specific)
- **High variability** indicates diverse query types
- **Query count** determines statistical power of evaluation

#### Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 21      |
| Average Relevant Docs per Query | 4.2     |
| Median Relevant Docs per Query  | 4.0     |
| Min Relevant Docs               | 2       |
| Max Relevant Docs               | 9       |
| Coverage Ratio                  | 11.11%  |

**Table: Relevance Distribution Summary**

**Column Explanations:**
- **Total Relevance Judgments**: Total number of relevant document-query pairs
- **Average Relevant Docs per Query**: Mean number of relevant documents per query
- **Median Relevant Docs per Query**: Middle value of relevant docs per query
- **Min/Max Relevant Docs**: Range of relevant documents per query
- **Coverage Ratio**: Percentage of corpus that is relevant to queries

**How to interpret:**
- **High average relevant docs** = easier retrieval task
- **Low coverage ratio** = sparse relevance (harder evaluation)
- **High variability** indicates inconsistent query difficulty

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

**Table: Evaluated Embedding Models**

**Column Explanations:**
- **Model Name**: Full model identifier from Hugging Face or provider
- **Collection**: ChromaDB collection name for this model
- **Dimensions**: Embedding vector dimensionality
- **Type**: Model architecture or framework

**How to interpret:**
- **Higher dimensions** generally capture more semantic nuance
- **Different architectures** have different strengths/weaknesses
- **Collection names** ensure isolated evaluation per model

### Evaluation Metrics

| Metric      | Description                                 | Measures                   |
|:------------|:--------------------------------------------|:---------------------------|
| MAP@k       | Mean Average Precision at rank k            | Ranking quality            |
| Recall@k    | Proportion of relevant docs in top k        | Coverage                   |
| Precision@k | Proportion of relevant docs among retrieved | Accuracy                   |
| NDCG@k      | Normalized Discounted Cumulative Gain       | Ranking with position bias |
| MRR@k       | Mean Reciprocal Rank                        | First relevant position    |

**Table: Evaluation Metrics Overview**

**Metric Details:**
- **MAP@k**: Mean Average Precision - balances precision and recall across ranks
- **Recall@k**: Coverage - fraction of relevant docs retrieved in top k
- **Precision@k**: Accuracy - fraction of retrieved docs that are relevant
- **NDCG@k**: Position-aware ranking quality with logarithmic discounting
- **MRR@k**: First relevant position - emphasizes finding relevant docs early

**When to use each metric:**
- **MAP**: Overall ranking quality for information retrieval
- **Recall**: Ensuring comprehensive coverage of relevant content
- **Precision**: Minimizing irrelevant results in recommendations
- **NDCG**: Search engine ranking with position bias
- **MRR**: Question-answering where first relevant result matters

### Representative Query Examples

| Query ID                      | Query Text                                                                                                                       |   # Relevant Docs |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_DeepSeek_chun<br/>k85  | DeepSeek-V3 training hyperparameters and learning rate schedule                                                                  |                 2 |
| q2_for_DeepSeek_chun<br/>k109 | What are the methods used to enhance model responses through reflection and verification, and how is non-reasoning data handled? |                 2 |
| q3_for_DeepSeek_chun<br/>k21  | What are the key components and training methodologies of the DeepSeek-V3 model?                                                 |                 4 |
| q4_for_DeepSeek_chun<br/>k34  | What is the Multi-Token Prediction (MTP) objective and its implementation in DeepSeek-V3?                                        |                 4 |
| q5_for_DeepSeek_chun<br/>k52  | What is a mixed precision framework for FP8 data format in deep learning training?                                               |                 9 |

**Table: Representative Query Examples**

**Column Explanations:**
- **Query ID**: Unique identifier for each query
- **Query Text**: The actual query text used for retrieval
- **# Relevant Docs**: Number of ground truth relevant documents

**How to interpret:**
- **Query diversity** shows the range of information needs tested
- **Relevant docs count** indicates query specificity (fewer = more specific)
- **Query length** may correlate with retrieval difficulty

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                 |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |
|:--------------------------------------|---------:|------------:|---------------:|----------:|---------:|
| all-MiniLM-L6-v2                      |   0.7999 |      1      |           0.42 |    0.9092 |   1      |
| all-MiniLM-L12-v2                     |   0.5101 |      0.6556 |           0.28 |    0.6507 |   0.9    |
| all-mpnet-base-v2                     |   0.4328 |      0.8056 |           0.32 |    0.5936 |   0.5333 |
| paraphrase-multilingual-MiniLM-L12-v2 |   0.3821 |      0.6889 |           0.24 |    0.558  |   0.7167 |

**Table: Model Performance Results Explanation**

**Column Explanations:**
- **Model**: Embedding model name (shortened for readability)
- **MAP@10**: Mean Average Precision at rank 10
- **Recall@10**: Fraction of relevant documents retrieved in top 10
- **Precision@10**: Fraction of retrieved documents that are relevant
- **NDCG@10**: Normalized Discounted Cumulative Gain at rank 10
- **MRR@10**: Mean Reciprocal Rank at rank 10

**How to interpret the results:**
- **Higher scores** = better retrieval performance
- **MAP** balances ranking quality and coverage
- **Recall** shows how comprehensive the retrieval is
- **Precision** shows how accurate the retrieval is
- **NDCG** rewards relevant documents appearing early
- **MRR** emphasizes finding the first relevant result

### Performance Analysis

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/all-MiniLM-L6-v2** achieved the highest MAP@10 score of 0.7999, while **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** scored 0.3821, representing a **109.3% improvement**.

**MAP-Recall Correlation**: 0.836 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](education_model_comparison_2026-02-07_15-14-37.png)

**Figure: Comprehensive Model Performance Comparison**

This bar chart compares all embedding models across all evaluation metrics at k=10. Each model has a group of bars showing its performance on different metrics.

**How to interpret:**
- **Taller bars** indicate better performance on that metric
- **Consistent height across metrics** shows well-rounded models
- **Spiky patterns** reveal specialized models (good at some metrics, poor at others)
- **Model grouping** allows direct comparison between models

**Why it matters:** Identifies models with balanced capabilities vs. specialized models, helping you choose based on your specific requirements.

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](education_corpus_statistics_2026-02-07_15-14-37.png)

**Figure: Dataset Characteristics and Distributions**

This figure contains four subplots showing the statistical properties of your evaluation dataset:

**Top-left: Chunk Length Distribution**
- Shows how document chunk sizes vary across the corpus
- **Normal distribution** indicates consistent chunking
- **Skewed distribution** suggests chunking strategy issues

**Top-right: Query Length Distribution**
- Shows the diversity of query lengths in your evaluation set
- **Wide range** indicates varied information needs
- **Narrow range** suggests similar query complexity

**Bottom-left: Relevance Distribution**
- Shows how many relevant documents exist per query
- **Right-skewed** = most queries have few relevant docs (harder task)
- **Left-skewed** = most queries have many relevant docs (easier task)

**Bottom-right: Summary Statistics Table**
- Key metrics for chunk lengths, query lengths, and relevance
- Helps assess dataset quality and evaluation difficulty

**Why it matters:** Understanding your dataset characteristics helps interpret model performance results and identify potential evaluation biases.

#### 6.3.3 Individual Metric Analysis

The following charts provide detailed performance breakdowns for each evaluation metric. Each chart focuses on a single metric to enable precise model comparisons.

##### MAP@10 Performance

![Map Comparison](education_map_comparison_2026-02-07_15-14-37.png)

**MAP@k (Mean Average Precision)**: Measures ranking quality by averaging precision at each relevant document position. Rewards models that rank relevant documents highly.

**Interpretation**: Higher values indicate better overall ranking performance. Useful for general information retrieval tasks.

##### RECALL@10 Performance

![Recall Comparison](education_recall_comparison_2026-02-07_15-14-37.png)

**Recall@k**: Measures the fraction of relevant documents that are successfully retrieved in the top k results. Focuses on coverage of relevant content.

**Interpretation**: Higher values indicate more comprehensive retrieval. Important when missing relevant information is costly.

##### PRECISION@10 Performance

![Precision Comparison](education_precision_comparison_2026-02-07_15-14-37.png)

**Precision@k**: Measures the fraction of retrieved documents that are actually relevant. Focuses on accuracy of the retrieved results.

**Interpretation**: Higher values indicate fewer irrelevant results. Important when irrelevant information reduces user satisfaction.

##### NDCG@10 Performance

![Ndcg Comparison](education_ndcg_comparison_2026-02-07_15-14-37.png)

**NDCG@k (Normalized Discounted Cumulative Gain)**: Measures ranking quality with position-based discounting. Relevant documents are more valuable when ranked higher.

**Interpretation**: Higher values indicate better ranking with proper position weighting. Standard metric for search engine evaluation.

##### MRR@10 Performance

![Mrr Comparison](education_mrr_comparison_2026-02-07_15-14-37.png)

**MRR@k (Mean Reciprocal Rank)**: Measures how early the first relevant document appears in the ranked results. Emphasizes finding relevant information quickly.

**Interpretation**: Higher values indicate faster discovery of relevant content. Critical for question-answering and single-answer scenarios.

### Statistical Significance Analysis

This section helps determine whether observed performance differences between models are meaningful or could occur by random chance. While formal statistical tests require larger sample sizes, these tables show practical significance thresholds.

**Understanding the Results:**
- **Difference > 0.05**: Potentially meaningful improvement for real applications
- **Difference > 0.10**: Clearly significant performance gap
- **Difference < 0.02**: Likely negligible for most use cases
- **Values marked with *** indicate differences above the 0.05 threshold

**Important Caveats:**
- These are absolute differences, not statistical significance tests
- True significance requires larger datasets and proper statistical methods
- Consider practical importance alongside statistical significance

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

This section analyzes the computational efficiency of different embedding models during the corpus initialization phase. Understanding embedding speed is crucial for production deployment decisions.

**Why embedding speed matters:**
- **Initial setup time**: How long to embed your entire corpus
- **Update frequency**: How often you can refresh embeddings
- **Scalability**: Performance with larger document collections
- **Cost**: Computational resources required for deployment

#### Embedding Speed Comparison

| Model                                                       |   Embedding Time (s) |   Docs/Second |   Avg Time/Doc (ms) |
|:------------------------------------------------------------|---------------------:|--------------:|--------------------:|
| sentence-transformers/all-MiniLM-L12-v2                     |                 3.96 |         47.78 |               20.93 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                 4    |         47.31 |               21.14 |
| sentence-transformers/all-MiniLM-L6-v2                      |                 4.19 |         45.08 |               22.18 |
| sentence-transformers/all-mpnet-base-v2                     |                45.92 |          4.12 |              242.96 |

**Table: Embedding Performance Metrics**

**Column Explanations:**
- **Model**: Embedding model name
- **Embedding Time (s)**: Total time to embed all document chunks
- **Docs/Second**: Processing throughput (higher = faster)
- **Avg Time/Doc (ms)**: Average time per document chunk

**How to interpret:**
- **Higher Docs/Second** = more efficient processing
- **Lower Avg Time/Doc** = faster individual document handling
- **Trade-offs**: Speed often correlates with model size/complexity
- **Production considerations**: Balance speed with retrieval quality

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L12-v2` at 47.78 docs/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 4.12 docs/second
- **Performance ratio**: 11.60x speed difference between fastest and slowest
![Figure: Embedding Speed Comparison](timing_comparison_2026-02-07_15-14-37.png)

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

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2026-02-07_15-14-37.*
*Source code and evaluation data available at the project repository.*
