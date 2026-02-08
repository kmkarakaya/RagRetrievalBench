# RAG Retrieval Benchmark: Law Dataset Evaluation

**Dataset:** Law
**Generated:** 2026-02-07 21:10:53

## Abstract

This paper presents a systematic evaluation of embedding models on the law dataset within Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG) on the law dataset. The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **1 PDF document(s)** that were processed into **306 document chunks** and **5 queries** with **14 relevant document mappings**.

**Best performing model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
* MAP@10: **0.6389**
* Recall@10: **0.9667**
* Precision@10: **0.2600**
* NDCG@10: **0.7668**
* MRR@10: **0.7500**

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

- **Source PDF documents**: 1 file(s) from `datasets\law\pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 306

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

## Law Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Source PDF Documents         |     1   |
| Total Document Chunks        |   306   |
| Average Chunk Length (words) |   120.2 |
| Median Chunk Length (words)  |   120   |
| Min Chunk Length (words)     |    56   |
| Max Chunk Length (words)     |   214   |
| Standard Deviation           |    12.3 |

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
| Average Query Length (words) |     8.6 |
| Median Query Length (words)  |     7   |
| Min Query Length (words)     |     5   |
| Max Query Length (words)     |    15   |
| Standard Deviation           |     3.4 |

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
| Total Relevance Judgments       | 14      |
| Average Relevant Docs per Query | 2.8     |
| Median Relevant Docs per Query  | 3.0     |
| Min Relevant Docs               | 1       |
| Max Relevant Docs               | 6       |
| Coverage Ratio                  | 4.58%   |

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

| Model Name                                                  | Collection   |   Dimensions | Type                 |
|:------------------------------------------------------------|:-------------|-------------:|:---------------------|
| sentence-transformers/all-MiniLM-L6-v2                      | law_coll_v1  |          384 | Sentence Transformer |
| sentence-transformers/all-mpnet-base-v2                     | law_coll_v2  |          768 | Sentence Transformer |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | law_coll_v3  |          384 | Sentence Transformer |
| sentence-transformers/all-MiniLM-L12-v2                     | law_coll_v4  |          384 | Sentence Transformer |

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

| Query ID                                                    | Query Text                                                                                                                                  |   # Relevant Docs |
|:------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------|------------------:|
| q1_for_6362 sayılı<br/>Sermaye Piyasası<br/>Kanunu_chunk160 | Merkezi Kayıt Kuruluşu'nun görevleri ve yetkileri nelerdir?                                                                                 |                 1 |
| q2_for_6362 sayılı<br/>Sermaye Piyasası<br/>Kanunu_chunk144 | Değerleme uzmanları ve kuruluşlarının Türkiye Değerleme Uzmanları Birliğine üyelik yükümlülükleri ve uyulmaması halinde sonuçları nelerdir? |                 3 |
| q3_for_6362 sayılı<br/>Sermaye Piyasası<br/>Kanunu_chunk71  | Faaliyet izninin iptali ve sonuçları                                                                                                        |                 1 |
| q4_for_6362 sayılı<br/>Sermaye Piyasası<br/>Kanunu_chunk200 | İzinsiz sermaye piyasası faaliyetlerinin internet üzerinden yürütülmesi ve engellenmesi.                                                    |                 3 |
| q5_for_6362 sayılı<br/>Sermaye Piyasası<br/>Kanunu_chunk21  | Sermaye piyasası araçlarının kaydileştirilmesi ve ihraç süreçleri                                                                           |                 6 |

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
| paraphrase-multilingual-MiniLM-L12-v2 |   0.6389 |      0.9667 |           0.26 |    0.7668 |   0.75   |
| all-MiniLM-L12-v2                     |   0.2    |      0.2    |           0.06 |    0.2469 |   0.4    |
| all-mpnet-base-v2                     |   0.1476 |      0.3667 |           0.08 |    0.2523 |   0.4286 |
| all-MiniLM-L6-v2                      |   0.0889 |      0.2667 |           0.08 |    0.1508 |   0.1067 |

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

The evaluation reveals significant performance variations across embedding models. **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** achieved the highest MAP@10 score of 0.6389, while **sentence-transformers/all-MiniLM-L6-v2** scored 0.0889, representing a **618.8% improvement**.

**MAP-Recall Correlation**: 0.952 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](law_model_comparison_2026-02-07_21-10-50.png)

**Figure: Comprehensive Model Performance Comparison**

This bar chart compares all embedding models across all evaluation metrics at k=10. Each model has a group of bars showing its performance on different metrics.

**How to interpret:**
- **Taller bars** indicate better performance on that metric
- **Consistent height across metrics** shows well-rounded models
- **Spiky patterns** reveal specialized models (good at some metrics, poor at others)
- **Model grouping** allows direct comparison between models

**Why it matters:** Identifies models with balanced capabilities vs. specialized models, helping you choose based on your specific requirements.

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](law_corpus_statistics_2026-02-07_21-10-50.png)

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

![Map Comparison](law_map_comparison_2026-02-07_21-10-50.png)

**MAP@k (Mean Average Precision)**: Measures ranking quality by averaging precision at each relevant document position. Rewards models that rank relevant documents highly.

**Interpretation**: Higher values indicate better overall ranking performance. Useful for general information retrieval tasks.

##### RECALL@10 Performance

![Recall Comparison](law_recall_comparison_2026-02-07_21-10-50.png)

**Recall@k**: Measures the fraction of relevant documents that are successfully retrieved in the top k results. Focuses on coverage of relevant content.

**Interpretation**: Higher values indicate more comprehensive retrieval. Important when missing relevant information is costly.

##### PRECISION@10 Performance

![Precision Comparison](law_precision_comparison_2026-02-07_21-10-50.png)

**Precision@k**: Measures the fraction of retrieved documents that are actually relevant. Focuses on accuracy of the retrieved results.

**Interpretation**: Higher values indicate fewer irrelevant results. Important when irrelevant information reduces user satisfaction.

##### NDCG@10 Performance

![Ndcg Comparison](law_ndcg_comparison_2026-02-07_21-10-50.png)

**NDCG@k (Normalized Discounted Cumulative Gain)**: Measures ranking quality with position-based discounting. Relevant documents are more valuable when ranked higher.

**Interpretation**: Higher values indicate better ranking with proper position weighting. Standard metric for search engine evaluation.

##### MRR@10 Performance

![Mrr Comparison](law_mrr_comparison_2026-02-07_21-10-50.png)

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

| Model                                 | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | all-MiniLM-L6-v2   |
|:--------------------------------------|:----------------------------------------|:--------------------|:--------------------|:-------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | —                                       | 0.4389*             | 0.4913*             | 0.5501*            |
| all-MiniLM-L12-v2                     | 0.4389*                                 | —                   | 0.0524*             | 0.1111*            |
| all-mpnet-base-v2                     | 0.4913*                                 | 0.0524*             | —                   | 0.0587*            |
| all-MiniLM-L6-v2                      | 0.5501*                                 | 0.1111*             | 0.0587*             | —                  |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Recall@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | all-MiniLM-L6-v2   |
|:--------------------------------------|:----------------------------------------|:--------------------|:--------------------|:-------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | —                                       | 0.7667*             | 0.6000*             | 0.7000*            |
| all-MiniLM-L12-v2                     | 0.7667*                                 | —                   | 0.1667*             | 0.0667*            |
| all-mpnet-base-v2                     | 0.6000*                                 | 0.1667*             | —                   | 0.1000*            |
| all-MiniLM-L6-v2                      | 0.7000*                                 | 0.0667*             | 0.1000*             | —                  |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### Precision@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | all-MiniLM-L6-v2   |
|:--------------------------------------|:----------------------------------------|:--------------------|:--------------------|:-------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | —                                       | 0.2000*             | 0.1800*             | 0.1800*            |
| all-MiniLM-L12-v2                     | 0.2000*                                 | —                   | 0.0200              | 0.0200             |
| all-mpnet-base-v2                     | 0.1800*                                 | 0.0200              | —                   | 0.0000             |
| all-MiniLM-L6-v2                      | 0.1800*                                 | 0.0200              | 0.0000              | —                  |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### NDCG@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | all-MiniLM-L6-v2   |
|:--------------------------------------|:----------------------------------------|:--------------------|:--------------------|:-------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | —                                       | 0.5199*             | 0.5145*             | 0.6160*            |
| all-MiniLM-L12-v2                     | 0.5199*                                 | —                   | 0.0054              | 0.0961*            |
| all-mpnet-base-v2                     | 0.5145*                                 | 0.0054              | —                   | 0.1015*            |
| all-MiniLM-L6-v2                      | 0.6160*                                 | 0.0961*             | 0.1015*             | —                  |

*Note: Values marked with * indicate potentially significant differences (>0.05).*

#### MRR@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-mpnet-base-v2   | all-MiniLM-L6-v2   |
|:--------------------------------------|:----------------------------------------|:--------------------|:--------------------|:-------------------|
| paraphrase-multilingual-MiniLM-L12-v2 | —                                       | 0.3500*             | 0.3214*             | 0.6433*            |
| all-MiniLM-L12-v2                     | 0.3500*                                 | —                   | 0.0286              | 0.2933*            |
| all-mpnet-base-v2                     | 0.3214*                                 | 0.0286              | —                   | 0.3219*            |
| all-MiniLM-L6-v2                      | 0.6433*                                 | 0.2933*             | 0.3219*             | —                  |

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
| sentence-transformers/all-MiniLM-L6-v2                      |                 6.52 |         46.95 |               21.3  |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                 6.57 |         46.57 |               21.47 |
| sentence-transformers/all-MiniLM-L12-v2                     |                 6.69 |         45.72 |               21.87 |
| sentence-transformers/all-mpnet-base-v2                     |                78.44 |          3.9  |              256.34 |

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

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L6-v2` at 46.95 docs/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 3.90 docs/second
- **Performance ratio**: 12.04x speed difference between fastest and slowest
![Figure: Embedding Speed Comparison](timing_comparison_2026-02-07_21-10-50.png)

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

- **Collection identifier**: `law_coll_v1`
- **Embedding dimension**: 384
- **Maximum sequence length**: 256
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-mpnet-base-v2

- **Collection identifier**: `law_coll_v2`
- **Embedding dimension**: 768
- **Maximum sequence length**: 384
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

- **Collection identifier**: `law_coll_v3`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-MiniLM-L12-v2

- **Collection identifier**: `law_coll_v4`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

## Discussion

### Key Findings

1. **Model Performance Hierarchy**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 emerged as the top performer, achieving superior results across multiple evaluation metrics.

2. **Performance Gaps**: The performance difference between the best and second-best models (0.4389 MAP@10) suggests that model selection significantly impacts retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided statistically robust comparisons of model performance. The results demonstrate that **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.6389. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2026-02-07_21-10-50.*
*Source code and evaluation data available at the project repository.*
