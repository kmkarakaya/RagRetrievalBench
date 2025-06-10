# RAG Retrieval Benchmark: A Comprehensive Evaluation of Embedding Models

**Generated:** 2025-06-10 18:10:55

## Abstract

This paper presents a systematic evaluation framework for embedding models in Retrieval Augmented Generation (RAG) systems. We developed an automated pipeline that processes PDF documents, generates synthetic queries using large language models, and evaluates retrieval performance across multiple embedding models using standardized information retrieval metrics. Our framework provides researchers and practitioners with a reproducible methodology for selecting optimal embedding models for their specific document collections and use cases.

## Executive Summary

This report presents a comparative analysis of embedding models for retrieval augmented generation (RAG). The models were evaluated on their ability to retrieve relevant documents using ChromaDB as the vector database. The benchmark used **232 documents** and **10 queries** with **49 relevant document mappings**.

**Best performing model:** `sentence-transformers/distiluse-base-multilingual-cased-v1`
* MAP@3: **0.6111**
* Recall@3: **0.3445**
* Precision@3: **0.6667**
* NDCG@3: **0.6531**
* MRR@3: **0.7000**

## Methodology

### 1. Automated Pipeline Overview

Our evaluation framework consists of five main stages:

1. **PDF Processing**: Document ingestion and chunking
2. **Corpus Generation**: Creation of standardized document chunks
3. **Query Generation**: LLM-assisted query synthesis
4. **Relevance Assessment**: Automated qrels generation
5. **Embedding Evaluation**: Multi-model performance comparison

### 2. Document Processing Pipeline

#### 2.1 PDF Extraction and Chunking

- **Source documents**: PDF files from `utils/pdfs` directory
- **Chunking strategy**: Recursive character text splitting
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters
- **Total chunks generated**: 232

The chunking process uses LangChain's `RecursiveCharacterTextSplitter` to maintain semantic coherence while ensuring manageable chunk sizes for embedding models.

#### 2.2 Query Generation Process

- **LLM Model**: gemini-1.5-flash
- **Number of queries generated**: 10
- **Generation strategy**: Seed-chunk → Query → Retrieval → Label
- **Candidate pool size**: 10 chunks per query

Queries were generated using the following systematic approach:
1. Random sampling of seed chunks from the corpus
2. LLM-based question generation targeting specific chunks
3. Retrieval-based candidate identification using ChromaDB
4. LLM-based relevance labeling for comprehensive qrels

### 3. Dataset Statistics

#### 3.1 Corpus Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Documents              |   232   |
| Average Chunk Length (words) |   124.5 |
| Median Chunk Length (words)  |   121   |
| Min Chunk Length (words)     |    91   |
| Max Chunk Length (words)     |   179   |
| Standard Deviation           |    17   |

#### 3.2 Query Characteristics

| Metric                       |   Value |
|:-----------------------------|--------:|
| Total Queries                |    10   |
| Average Query Length (words) |    19.7 |
| Median Query Length (words)  |    20.5 |
| Min Query Length (words)     |    12   |
| Max Query Length (words)     |    27   |
| Standard Deviation           |     5.2 |

#### 3.3 Relevance Distribution

| Metric                          | Value   |
|:--------------------------------|:--------|
| Total Relevance Judgments       | 49      |
| Average Relevant Docs per Query | 4.9     |
| Median Relevant Docs per Query  | 5.0     |
| Min Relevant Docs               | 1       |
| Max Relevant Docs               | 9       |
| Coverage Ratio                  | 21.12%  |

### 4. Experimental Setup

#### 4.1 Evaluation Framework

- **Vector Database**: ChromaDB
- **Evaluation Library**: SentenceTransformers InformationRetrievalEvaluator
- **Retrieval Depth (k)**: 3
