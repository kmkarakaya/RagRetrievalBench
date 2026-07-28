# RAG Retrieval Benchmark: Education_Tr_Rerun Dataset Evaluation

**Dataset:** Education_Tr_Rerun
**Generated:** 2026-07-28 10:27:24

## Abstract

This paper presents a systematic evaluation of embedding models on the education_tr_rerun dataset within Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes documents (PDFs), generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG) on the education_tr_rerun dataset. The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **29 document(s) (PDFs)** that were processed into **619 chunks** and **50 queries** with **354 relevant document mappings**.

**Best performing model:** `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
* MAP@10: **0.3606**
* Recall@10: **0.4876**
* Precision@10: **0.3080**
* NDCG@10: **0.5067**
* MRR@10: **0.7590**
* Success/Hit Rate@10: **0.9600**

## Methodology

### Automated Pipeline Overview

Our evaluation framework consists of five main stages:

1. **Document (PDF) Processing**: Document ingestion and chunking
2. **Corpus Generation**: Creation of standardized chunks
3. **Query Generation**: LLM-assisted query synthesis
4. **Relevance Assessment**: Automated qrels generation
5. **Embedding Evaluation**: Multi-model performance comparison

### Document Processing Pipeline

#### PDF Extraction and Chunking

- **Source documents (PDFs)**: 29 file(s) from `datasets\education_tr\pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 619

The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence while ensuring manageable chunk sizes for embedding models.

#### Query Generation Process

- **LLM Model**: models/gemini-2.5-flash-lite
- **Number of queries generated**: 50
- **Generation strategy**: Seed-chunk → Query → Retrieval → Label
- **Candidate pool size**: 20 chunks per query

Queries were generated using the following systematic approach:
1. Random sampling of seed chunks from the corpus
2. LLM-based question generation targeting specific chunks
3. Retrieval-based candidate identification using ChromaDB
4. LLM-based relevance labeling for comprehensive qrels

## Education_Tr_Rerun Dataset Statistics

#### Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Source Documents (PDFs)      |    29   |
| Total Chunks                 |   619   |
| Average Chunk Length (words) |   116   |
| Median Chunk Length (words)  |   119   |
| Min Chunk Length (words)     |    16   |
| Max Chunk Length (words)     |   144   |
| Standard Deviation           |    15.8 |

**Table: Corpus Characteristics Summary**

**Column Explanations:**
- **Source Documents (PDFs)**: Number of source documents (PDF files) processed
- **Total Chunks**: Number of text chunks created from documents (PDFs)
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
| Total Queries                |    50   |
| Average Query Length (words) |     9.4 |
| Median Query Length (words)  |     9   |
| Min Query Length (words)     |     5   |
| Max Query Length (words)     |    23   |
| Standard Deviation           |     3.1 |

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

| Metric                               | Value   |
|:-------------------------------------|:--------|
| Total Relevance Judgments            | 354     |
| Average Relevant Documents per Query | 7.1     |
| Median Relevant Documents per Query  | 6.0     |
| Min Relevant Documents               | 2       |
| Max Relevant Documents               | 20      |
| Coverage Ratio                       | 57.19%  |

**Table: Relevance Distribution Summary**

**Column Explanations:**
- **Total Relevance Judgments**: Total number of relevant document-query pairs
- **Average Relevant Documents per Query**: Mean number of relevant documents per query
- **Median Relevant Documents per Query**: Middle value of relevant documents per query
- **Min/Max Relevant Documents**: Range of relevant documents per query
- **Coverage Ratio**: Percentage of corpus that is relevant to queries

**How to interpret:**
- **High average relevant documents** = easier retrieval task
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

| Model Name                                                  | Collection           |   Dimensions | Type                 |
|:------------------------------------------------------------|:---------------------|-------------:|:---------------------|
| sentence-transformers/all-MiniLM-L6-v2                      | education_tr_coll_v1 |          384 | Sentence Transformer |
| sentence-transformers/all-mpnet-base-v2                     | education_tr_coll_v2 |          768 | Sentence Transformer |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | education_tr_coll_v3 |          384 | Sentence Transformer |
| sentence-transformers/all-MiniLM-L12-v2                     | education_tr_coll_v4 |          384 | Sentence Transformer |
| sentence-transformers/paraphrase-multilingual-mpnet-base-v2 | education_tr_coll_v5 |          768 | Sentence Transformer |

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

| Metric      | Description                                                      | Measures                   |
|:------------|:-----------------------------------------------------------------|:---------------------------|
| MAP@k       | Mean Average Precision at rank k                                 | Ranking quality            |
| Recall@k    | Proportion of relevant documents in top k                        | Coverage                   |
| Precision@k | Proportion of relevant documents among retrieved                 | Accuracy                   |
| NDCG@k      | Normalized Discounted Cumulative Gain                            | Ranking with position bias |
| MRR@k       | Mean Reciprocal Rank                                             | First relevant position    |
| Success@k   | Fraction of queries with at least one relevant document in top k | Query-level success        |

**Table: Evaluation Metrics Overview**

**Metric Details:**
- **MAP@k**: Mean Average Precision - balances precision and recall across ranks
- **Recall@k**: Coverage - fraction of relevant documents retrieved in top k
- **Precision@k**: Accuracy - fraction of retrieved documents that are relevant
- **NDCG@k**: Position-aware ranking quality with logarithmic discounting
- **MRR@k**: First relevant position - emphasizes finding relevant documents early
- **Success@k**: Success@k / Hit Rate@k - fraction of queries with at least one relevant hit in top k

**When to use each metric:**
- **MAP**: Overall ranking quality for information retrieval
- **Recall**: Ensuring comprehensive coverage of relevant content
- **Precision**: Minimizing irrelevant results in recommendations
- **NDCG**: Search engine ranking with position bias
- **MRR**: Question-answering where first relevant result matters
- **Success**: Measuring query-level success rate when at least one relevant hit is enough

### Representative Query Examples

| Query ID                         | Query Text                                                               |   # Relevant Documents |
|:---------------------------------|:-------------------------------------------------------------------------|-----------------------:|
| q1_for_Bütçe_chunk2              | TED Üniversitesi bütçe ve muhasebe esasları nelerdir?                    |                      6 |
| q2_for_Atama_chunk26             | TEDÜ doçentlik atama kriterleri nelerdir?                                |                     11 |
| q3_for_Kaf_chunk15               | Yönerge güncellemeleri ve revizyonları hakkında bilgi.                   |                     20 |
| q4_for_hareketlilik_<br/>chunk26 | Yeşil seyahat ve Erasmus+ ikili anlaşmaları hakkında bilgi.              |                      8 |
| q5_for_hareketlilik_<br/>chunk4  | Erasmus+ öğrenim hareketliliği başvuru süreci ve takvimi hakkında bilgi. |                      9 |

**Table: Representative Query Examples**

**Column Explanations:**
- **Query ID**: Unique identifier for each query
- **Query Text**: The actual query text used for retrieval
- **# Relevant Documents**: Number of ground truth relevant documents

**How to interpret:**
- **Query diversity** shows the range of information needs tested
- **Relevant document count** indicates query specificity (fewer = more specific)
- **Query length** may correlate with retrieval difficulty

## Results

### Model Performance Comparison

**Table: Comprehensive Model Performance Results**

| Model                                 |   MAP@10 |   Recall@10 |   Precision@10 |   NDCG@10 |   MRR@10 |   Success@10 |
|:--------------------------------------|---------:|------------:|---------------:|----------:|---------:|-------------:|
| paraphrase-multilingual-mpnet-base-v2 |   0.3606 |      0.4876 |          0.308 |    0.5067 |   0.759  |         0.96 |
| paraphrase-multilingual-MiniLM-L12-v2 |   0.2972 |      0.3953 |          0.256 |    0.4259 |   0.6369 |         0.88 |
| all-MiniLM-L12-v2                     |   0.1854 |      0.2579 |          0.168 |    0.2951 |   0.5345 |         0.72 |
| all-MiniLM-L6-v2                      |   0.1231 |      0.1897 |          0.146 |    0.1956 |   0.2788 |         0.58 |
| all-mpnet-base-v2                     |   0.094  |      0.1913 |          0.136 |    0.1766 |   0.2561 |         0.58 |

**Table: Model Performance Results Explanation**

**Column Explanations:**
- **Model**: Embedding model name (shortened for readability)
- **MAP@10**: Mean Average Precision at rank 10
- **Recall@10**: Fraction of relevant documents retrieved in top 10
- **Precision@10**: Fraction of retrieved documents that are relevant
- **NDCG@10**: Normalized Discounted Cumulative Gain at rank 10
- **MRR@10**: Mean Reciprocal Rank at rank 10
- **Success@10**: Success@10 / Hit Rate@10: fraction of queries with >=1 relevant retrieved

**How to interpret the results:**
- **Higher scores** = better retrieval performance
- **MAP**: MAP balances ranking quality and coverage
- **Recall**: Recall shows how comprehensive the retrieval is
- **Precision**: Precision shows how accurate the retrieval is
- **NDCG**: NDCG rewards relevant documents appearing early
- **MRR**: MRR emphasizes finding the first relevant result
- **Success**: Success/Hit Rate captures whether queries get at least one relevant hit

### Performance Analysis

The evaluation reveals observable performance differences across embedding models. **sentence-transformers/paraphrase-multilingual-mpnet-base-v2** achieved the highest MAP@10 score of 0.3606, while **sentence-transformers/all-mpnet-base-v2** scored 0.0940, representing a **283.5% relative improvement**.

**MAP-Recall Correlation**: 0.992 (indicates how well ranking quality correlates with coverage)

### Visual Analysis

#### 6.3.1 Overall Performance Comparison

![Model Performance Overview](education_tr_rerun_model_comparison_2026-07-23_17-57-53.png)

**Figure: Comprehensive Model Performance Comparison**

This bar chart compares all embedding models across all evaluation metrics at k=10. Each model has a group of bars showing its performance on different metrics.

**How to interpret:**
- **Taller bars** indicate better performance on that metric
- **Consistent height across metrics** shows well-rounded models
- **Spiky patterns** reveal specialized models (good at some metrics, poor at others)
- **Model grouping** allows direct comparison between models

**Why it matters:** Identifies models with balanced capabilities vs. specialized models, helping you choose based on your specific requirements.

#### 6.3.2 Dataset Characteristics

![Corpus Statistics](education_tr_rerun_corpus_statistics_2026-07-23_17-57-53.png)

**Figure: Dataset Characteristics and Distributions**

This figure contains four subplots showing the statistical properties of your evaluation dataset:

**Top-left: Chunk Length Distribution**
- Shows how chunk sizes vary across the corpus
- **Normal distribution** indicates consistent chunking
- **Skewed distribution** suggests chunking strategy issues

**Top-right: Query Length Distribution**
- Shows the diversity of query lengths in your evaluation set
- **Wide range** indicates varied information needs
- **Narrow range** suggests similar query complexity

**Bottom-left: Relevance Distribution**
- Shows how many relevant documents exist per query
- **Right-skewed** = most queries have few relevant documents (harder task)
- **Left-skewed** = most queries have many relevant documents (easier task)

**Bottom-right: Summary Statistics Table**
- Key metrics for chunk lengths, query lengths, and relevance
- Helps assess dataset quality and evaluation difficulty

**Why it matters:** Understanding your dataset characteristics helps interpret model performance results and identify potential evaluation biases.

#### 6.3.3 Individual Metric Analysis

The following charts provide detailed performance breakdowns for each evaluation metric. Each chart focuses on a single metric to enable precise model comparisons.

##### MAP@10 Performance

![MAP Comparison](education_tr_rerun_map_comparison_2026-07-23_17-57-53.png)

**MAP@k (Mean Average Precision)**: Measures ranking quality by averaging precision at each relevant document position. Rewards models that rank relevant documents highly.

**Interpretation**: Higher values indicate better overall ranking performance. Useful for general information retrieval tasks.

##### Recall@10 Performance

![Recall Comparison](education_tr_rerun_recall_comparison_2026-07-23_17-57-53.png)

**Recall@k**: Measures the fraction of relevant documents that are successfully retrieved in the top k results. Focuses on coverage of relevant content.

**Interpretation**: Higher values indicate more comprehensive retrieval. Important when missing relevant information is costly.

##### Precision@10 Performance

![Precision Comparison](education_tr_rerun_precision_comparison_2026-07-23_17-57-53.png)

**Precision@k**: Measures the fraction of retrieved documents that are actually relevant. Focuses on accuracy of the retrieved results.

**Interpretation**: Higher values indicate fewer irrelevant results. Important when irrelevant information reduces user satisfaction.

##### NDCG@10 Performance

![NDCG Comparison](education_tr_rerun_ndcg_comparison_2026-07-23_17-57-53.png)

**NDCG@k (Normalized Discounted Cumulative Gain)**: Measures ranking quality with position-based discounting. Relevant documents are more valuable when ranked higher.

**Interpretation**: Higher values indicate better ranking with proper position weighting. Standard metric for search engine evaluation.

##### MRR@10 Performance

![MRR Comparison](education_tr_rerun_mrr_comparison_2026-07-23_17-57-53.png)

**MRR@k (Mean Reciprocal Rank)**: Measures how early the first relevant document appears in the ranked results. Emphasizes finding relevant information quickly.

**Interpretation**: Higher values indicate faster discovery of relevant content. Critical for question-answering and single-answer scenarios.

##### Success/Hit Rate@10 Performance

![Success/Hit Rate Comparison](education_tr_rerun_hit_rate_comparison_2026-07-23_17-57-53.png)

**Success@k / Hit Rate@k**: Measures the fraction of queries where at least one relevant document appears in top-k results.

**Interpretation**: Higher values indicate more queries are successfully served. Useful when any relevant hit is sufficient for a good user experience.

### Query-Level Uncertainty (Descriptive)

Point estimates alone do not show whether this corpus actually separates the candidate models. The table below reports a percentile bootstrap 95% confidence interval for each model's MAP@10 over the 50 scored queries of this corpus, together with the **paired** difference against `M5`, the MAP@10-leading candidate here.

| Model                                        | MAP@10 [95% CI]         | `M5` - model diff [95% CI]   | Separated?   |
|:---------------------------------------------|:------------------------|:-----------------------------|:-------------|
| paraphrase-multilingual-mpnet-base-v2 (`M5`) | 0.3606 [0.2935, 0.4301] | -                            | -            |
| paraphrase-multilingual-MiniLM-L12-v2 (`M3`) | 0.2972 [0.2326, 0.3646] | +0.0634 [+0.0165, +0.1119]   | yes          |
| all-MiniLM-L12-v2 (`M4`)                     | 0.1854 [0.1366, 0.2371] | +0.1752 [+0.0886, +0.2638]   | yes          |
| all-MiniLM-L6-v2 (`M1`)                      | 0.1231 [0.0738, 0.1773] | +0.2376 [+0.1548, +0.3193]   | yes          |
| all-mpnet-base-v2 (`M2`)                     | 0.0940 [0.0607, 0.1305] | +0.2666 [+0.1951, +0.3429]   | yes          |

**Table: Per-corpus bootstrap intervals for MAP@10 (B=10,000 resamples over the 50 scored queries)**

**How to read this:**
- The **paired** column is the column that decides. It resamples the per-query differences, so it cancels the shared query-difficulty variation that inflates each model's own interval.
- Two marginal intervals can overlap heavily while the paired difference still excludes zero. Do **not** read overlap in the middle column as evidence of no difference.
- **Separated? = no** means this corpus does not distinguish that model from the leader on MAP@10. When that happens, the choice should be made on operational cost (see the timing section) rather than on retrieval quality.
- Intervals are descriptive and conditional on this snapshot: queries are generated from corpus chunks, documents contribute related chunks, and relevance labels are LLM-judged. They are computed within this corpus only and are not population-level inference.

### Pairwise Difference Analysis (Descriptive)

Absolute differences between model point estimates, for reference. These are raw gaps, not tests; where a bootstrap interval is available above, that is the evidence to use.

#### MAP@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.0634                                  | 0.1752              | 0.2376             | 0.2666              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0634                                  | -                                       | 0.1118              | 0.1741             | 0.2032              |
| all-MiniLM-L12-v2                     | 0.1752                                  | 0.1118                                  | -                   | 0.0624             | 0.0914              |
| all-MiniLM-L6-v2                      | 0.2376                                  | 0.1741                                  | 0.0624              | -                  | 0.0290              |
| all-mpnet-base-v2                     | 0.2666                                  | 0.2032                                  | 0.0914              | 0.0290             | -                   |

#### Recall@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.0923                                  | 0.2297              | 0.2978             | 0.2963              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0923                                  | -                                       | 0.1373              | 0.2055             | 0.2040              |
| all-MiniLM-L12-v2                     | 0.2297                                  | 0.1373                                  | -                   | 0.0682             | 0.0666              |
| all-MiniLM-L6-v2                      | 0.2978                                  | 0.2055                                  | 0.0682              | -                  | 0.0016              |
| all-mpnet-base-v2                     | 0.2963                                  | 0.2040                                  | 0.0666              | 0.0016             | -                   |

#### Precision@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.0520                                  | 0.1400              | 0.1620             | 0.1720              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0520                                  | -                                       | 0.0880              | 0.1100             | 0.1200              |
| all-MiniLM-L12-v2                     | 0.1400                                  | 0.0880                                  | -                   | 0.0220             | 0.0320              |
| all-MiniLM-L6-v2                      | 0.1620                                  | 0.1100                                  | 0.0220              | -                  | 0.0100              |
| all-mpnet-base-v2                     | 0.1720                                  | 0.1200                                  | 0.0320              | 0.0100             | -                   |

#### NDCG@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.0808                                  | 0.2116              | 0.3111             | 0.3301              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0808                                  | -                                       | 0.1308              | 0.2303             | 0.2493              |
| all-MiniLM-L12-v2                     | 0.2116                                  | 0.1308                                  | -                   | 0.0994             | 0.1185              |
| all-MiniLM-L6-v2                      | 0.3111                                  | 0.2303                                  | 0.0994              | -                  | 0.0191              |
| all-mpnet-base-v2                     | 0.3301                                  | 0.2493                                  | 0.1185              | 0.0191             | -                   |

#### MRR@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.1221                                  | 0.2245              | 0.4802             | 0.5029              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.1221                                  | -                                       | 0.1024              | 0.3581             | 0.3808              |
| all-MiniLM-L12-v2                     | 0.2245                                  | 0.1024                                  | -                   | 0.2557             | 0.2784              |
| all-MiniLM-L6-v2                      | 0.4802                                  | 0.3581                                  | 0.2557              | -                  | 0.0227              |
| all-mpnet-base-v2                     | 0.5029                                  | 0.3808                                  | 0.2784              | 0.0227             | -                   |

#### Success/Hit Rate@10 Pairwise Differences

| Model                                 | paraphrase-multilingual-mpnet-base-v2   | paraphrase-multilingual-MiniLM-L12-v2   | all-MiniLM-L12-v2   | all-MiniLM-L6-v2   | all-mpnet-base-v2   |
|:--------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|:-------------------|:--------------------|
| paraphrase-multilingual-mpnet-base-v2 | -                                       | 0.0800                                  | 0.2400              | 0.3800             | 0.3800              |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.0800                                  | -                                       | 0.1600              | 0.3000             | 0.3000              |
| all-MiniLM-L12-v2                     | 0.2400                                  | 0.1600                                  | -                   | 0.1400             | 0.1400              |
| all-MiniLM-L6-v2                      | 0.3800                                  | 0.3000                                  | 0.1400              | -                  | 0.0000              |
| all-mpnet-base-v2                     | 0.3800                                  | 0.3000                                  | 0.1400              | 0.0000             | -                   |

## Compute And Retrieval Performance Metrics

This section analyzes the computational efficiency of different embedding models during corpus initialization and retrieval. Understanding speed and latency is crucial for production deployment decisions.

**Why timing metrics matter:**
- **Initial setup time**: How long to embed your entire corpus
- **Update frequency**: How often you can refresh embeddings
- **Query responsiveness**: How fast retrieval returns results at runtime
- **Scalability**: Performance with larger document collections
- **Cost**: Computational resources required for deployment

#### Embedding Speed And Query Latency Comparison

| Model                                                       |   Embedding Time (s) |   Chunks/Second |   Avg Time/Chunk (ms) |   Avg Query Latency (ms/query) |   Queries Timed |
|:------------------------------------------------------------|---------------------:|----------------:|----------------------:|-------------------------------:|----------------:|
| sentence-transformers/all-MiniLM-L6-v2                      |                14.24 |           43.47 |                 23    |                          16.87 |              50 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |                14.97 |           41.34 |                 24.19 |                          25.63 |              50 |
| sentence-transformers/all-MiniLM-L12-v2                     |                14.76 |           41.94 |                 23.84 |                          28.53 |              50 |
| sentence-transformers/paraphrase-multilingual-mpnet-base-v2 |                46.63 |           13.27 |                 75.33 |                          42.72 |              50 |
| sentence-transformers/all-mpnet-base-v2                     |               172.18 |            3.6  |                278.16 |                          49.86 |              50 |

**Table: Compute And Retrieval Performance Metrics**

**Column Explanations:**
- **Model**: Embedding model name
- **Embedding Time (s)**: Total time to embed all chunks
- **Chunks/Second**: Processing throughput (higher = faster)
- **Avg Time/Chunk (ms)**: Average time per chunk
- **Avg Query Latency (ms/query)**: Average DB retrieval time per query (lower = faster)
- **Queries Timed**: Number of queries included in retrieval latency measurement

**How to interpret:**
- **Higher Chunks/Second** = more efficient processing
- **Lower Avg Time/Chunk** = faster embedding of individual chunks
- **Lower Avg Query Latency** = faster retrieval responsiveness at runtime
- **Trade-offs**: Speed often correlates with model size/complexity
- **Production considerations**: Balance speed with retrieval quality

#### Performance Insights

- **Fastest embedding model**: `sentence-transformers/all-MiniLM-L6-v2` at 43.47 chunks/second
- **Slowest embedding model**: `sentence-transformers/all-mpnet-base-v2` at 3.60 chunks/second
- **Embedding performance ratio**: 12.09x (fastest vs slowest)
- **Lowest retrieval latency**: `sentence-transformers/all-MiniLM-L6-v2` at 16.87 ms/query
- **Highest retrieval latency**: `sentence-transformers/all-mpnet-base-v2` at 49.86 ms/query
- **Retrieval latency spread**: 2.95x (highest vs lowest)
![Figure: Compute and Retrieval Timing Comparison](education_tr_rerun_timing_comparison_2026-07-23_17-57-53.png)

*Figure: Embedding speed and query retrieval latency comparison across models.*

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
python rag_benchmark.py --dataset education_tr_rerun --prepare-corpus

# 2. Generate queries
python rag_benchmark.py --dataset education_tr_rerun --generate-queries

# 3. Generate relevance judgments
python rag_benchmark.py --dataset education_tr_rerun --generate-qrels

# 4. Run complete benchmark
python rag_benchmark.py --dataset education_tr_rerun --all
```

### Embedding Model Specifications

#### sentence-transformers/all-MiniLM-L6-v2

- **Collection identifier**: `education_tr_coll_v1`
- **Embedding dimension**: 384
- **Maximum sequence length**: 256
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-mpnet-base-v2

- **Collection identifier**: `education_tr_coll_v2`
- **Embedding dimension**: 768
- **Maximum sequence length**: 384
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

- **Collection identifier**: `education_tr_coll_v3`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/all-MiniLM-L12-v2

- **Collection identifier**: `education_tr_coll_v4`
- **Embedding dimension**: 384
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

#### sentence-transformers/paraphrase-multilingual-mpnet-base-v2

- **Collection identifier**: `education_tr_coll_v5`
- **Embedding dimension**: 768
- **Maximum sequence length**: 128
- **Model architecture**: Transformer-based sentence encoder

## Discussion

### Key Findings

1. **Model Performance Hierarchy**: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 emerged as the top performer, achieving superior results across multiple evaluation metrics.

2. **Performance Gaps**: The performance difference between the best and second-best models (0.0634 MAP@10) is large, suggesting model choice can materially affect retrieval quality.

3. **Automated Evaluation Viability**: The LLM-assisted query and relevance generation process demonstrates the feasibility of automated benchmark creation for domain-specific document collections.

### Limitations and Future Work

- **Single-domain evaluation**: Current results are specific to the evaluated document collection
- **LLM bias**: Query generation and relevance judgments may reflect biases of the generative model
- **Limited query diversity**: Future work should explore multi-turn queries and complex information needs
- **Scalability**: Evaluation should be extended to larger document collections and more diverse domains

## Conclusion

This study presents a comprehensive framework for evaluating embedding models in RAG systems. Our automated pipeline successfully generated meaningful evaluation datasets and provided structured comparative analysis of model performance. The results demonstrate that **sentence-transformers/paraphrase-multilingual-mpnet-base-v2** provides optimal retrieval performance for the evaluated document collection, with a MAP@10 score of 0.3606. The substantial performance variations across models underscore the importance of systematic evaluation in embedding model selection for production RAG systems.

The open-source nature of our evaluation framework enables researchers and practitioners to adapt the methodology for their specific domains and requirements, contributing to more systematic and reproducible evaluation practices in the RAG community.

---

*This report was automatically generated by the RAG Retrieval Benchmark Pipeline at 2026-07-23_17-57-53.*
*Source code and evaluation data available at the project repository.*
