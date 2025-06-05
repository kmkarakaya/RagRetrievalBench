# RAG Retrieval Benchmark Workflow

## Overview
This document outlines the workflow for benchmarking different embedding models for retrieval augmented generation (RAG) systems. This workflow allows you to systematically evaluate which embedding models perform best with your specific documents and queries.

## Workflow Steps

### 1. PDF Processing
- Import PDFs from your document collection
- Split PDFs into chunks using text splitters
  - Consider chunk size (e.g., 1000 characters) and overlap (e.g., 200 characters)
  - Maintain document metadata and context during splitting
- Store processed chunks with unique IDs for later reference

### 2. Embedding Model Benchmark
- **For each embedding model to test:**
  1. Create a ChromaDB collection with a unique name
  2. Configure the collection with the model's embedding function:
     ```python
     sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
     collection = client.create_collection(name=collection_name, embedding_function=sentence_transformer_ef)
     ```
  3. Add document chunks to the collection in batches
  4. The collection now contains chunks embedded by the specified model
  5. Repeat for all embedding models to be tested (embed2, embed3, etc.)
  6. Verify collection creation with sample queries

### 3. Test Data Preparation
- Create a representative test dataset:
  - **Corpus selection:**
    - Select diverse chunks that represent your document collection
    - Save to `corpus.jsonl` with document IDs and text content
  - **Query generation:**
    - Create realistic queries your users might ask
    - Use LLMs to generate diverse query types (factoid, exploratory, comparative)
    - Save to `queries.jsonl` with query IDs and text
  - **Relevance judgments:**
    - Establish which documents are relevant to each query
    - Use subject matter experts or LLM assistance
    - Save relevance mappings to `qrels.tsv` in the format `query_id doc_id relevance_score`

### 4. Evaluation
- **For each embedding model:**
  1. Load the corresponding ChromaDB collection
  2. For each query in `queries.jsonl`:
     - Submit the query to ChromaDB to get ranked results
     - Format results for the evaluator:
       ```python
       queries_result_list[query_idx].append({
           "corpus_id": doc_id,
           "score": similarity_score
       })
       ```
  3. Provide the SentenceTransformers `InformationRetrievalEvaluator` with:
     - The queries
     - Expected relevant chunks list
     - The received chunk list from ChromaDB
  4. Calculate metrics using `InformationRetrievalEvaluator.compute_metrics()`:
     - MAP (Mean Average Precision)
     - Recall@k
     - Precision@k
     - NDCG@k (Normalized Discounted Cumulative Gain)
     - MRR@k (Mean Reciprocal Rank)

### 5. Debugging and Validation
- Verify the evaluation is working correctly:
  - Print top k results for sample queries
  - Check if relevant documents appear in results
  - Ensure different models produce different rankings
  - Compare embedding dimension outputs across models
- If models produce identical metrics:
  - Test with larger/more diverse query sets
  - Try models with more significant architectural differences
  - Increase k values for evaluation

### 6. Results Analysis and Reporting
- Generate comprehensive reports with:
  - Summary tables comparing all models across metrics
  - Visualizations of performance differences
  - Statistical significance analysis between models
  - Per-query performance analysis
- Consider specialized performance aspects:
  - Domain-specific retrieval quality
  - Multilingual capabilities if relevant
  - Performance on different query types
  - Computational efficiency and embedding size

### 7. Model Selection Decision
- Select the best model based on:
  - Primary metric performance (usually MAP@k)
  - Balanced performance across all metrics
  - Specific requirements of your RAG application
  - Deployment considerations (model size, inference speed)

## Implementation Notes
- Use ChromaDB's native embedding functions for efficiency
- Batch process documents during collection creation
- Ensure collections are properly reinitialized between benchmark runs
- Convert distance scores to similarity scores for the evaluator:

  ```python
  # ChromaDB returns distance; convert to similarity for IR evaluation
  similarity = 1.0 / (1.0 + float(distance))
  ```
- Always use ChromaDB's returned ranking for evaluation, not the evaluator's internal reranking
- Ensure all configuration (paths, models, metrics, etc.) is handled via `benchmark_config.py`
- Save all reports and plots to the `reports/` directory for reproducibility
- Remove or avoid legacy/testing code in the main pipeline for clarity
- Document all steps and results for transparency and reproducibility