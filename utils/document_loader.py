"""
Document loading utilities for RagRetrievalBench.
Supports loading and processing PDF documents into corpus format.
"""
import json
import os
from typing import Dict, List, Tuple, Any

def prepare_corpus_from_pdfs(pdf_dir: str, chunk_size: int, chunk_overlap: int, corpus_file: str) -> Dict[str, Any]:
    """
    Loads all PDFs from pdf_dir, splits them into chunks, and saves as JSONL.
    
    Args:
        pdf_dir (str): Directory containing PDF files
        chunk_size (int): Size of text chunks
        chunk_overlap (int): Overlap between chunks  
        corpus_file (str): Path to save corpus JSONL file
        
    Returns:
        Dict[str, Any]: Statistics about corpus creation
        
    Raises:
        ImportError: If text_splitter module cannot be imported
        FileNotFoundError: If pdf_dir doesn't exist
    """
    print("Executing prepare_corpus_from_pdfs()...")
    
    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
    
    # Import text splitter
    try:
        from .text_splitter import split_pdfs_to_chunks
    except ImportError:
        print("Error: Could not import split_pdfs_to_chunks from utils.text_splitter")
        raise
    
    # Split PDFs into chunks
    chunks = split_pdfs_to_chunks(pdf_dir, chunk_size, chunk_overlap)
    
    # Save chunks as JSONL
    print(f"Saving {len(chunks)} chunks to {corpus_file}...")
    # Only create directory if corpus_file contains a directory path
    corpus_dir = os.path.dirname(corpus_file)
    if corpus_dir:  # Only create directory if there's actually a directory path
        os.makedirs(corpus_dir, exist_ok=True)
    
    with open(corpus_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps({
                "doc_id": chunk.doc_id, 
                "text": chunk.page_content
            }) + "\n")
    
    print("Corpus preparation complete.")
    
    return {
        "chunks_created": len(chunks),
        "output_file": corpus_file,
        "source_dir": pdf_dir
    }


def load_corpus(corpus_file: str) -> Dict[str, str]:
    """
    Load corpus from JSONL file.
    
    Args:
        corpus_file (str): Path to corpus JSONL file
        
    Returns:
        Dict[str, str]: Mapping of doc_id to text content
        
    Raises:
        FileNotFoundError: If corpus file doesn't exist
        ValueError: If corpus file is malformed
    """
    if not os.path.exists(corpus_file):
        raise FileNotFoundError(f"Corpus file not found: {corpus_file}")
    
    corpus = {}
    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if 'doc_id' not in data or 'text' not in data:
                        print(f"Warning: Line {line_num} missing required fields, skipping")
                        continue
                    corpus[data['doc_id']] = data['text']
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    except Exception as e:
        raise ValueError(f"Error reading corpus file {corpus_file}: {e}")
    
    if not corpus:
        print(f"Warning: No documents found in {corpus_file}. Please check the file format.")
    else:
        print(f"Successfully loaded {len(corpus)} documents from {corpus_file}.")
        print(f"First 5 document IDs: {list(corpus.keys())[:5]}")
    
    return corpus


def load_queries(queries_file: str) -> Dict[str, str]:
    """
    Load queries from JSONL file.
    
    Args:
        queries_file (str): Path to queries JSONL file
        
    Returns:
        Dict[str, str]: Mapping of query_id to text content
        
    Raises:
        FileNotFoundError: If queries file doesn't exist
        ValueError: If queries file is malformed
    """
    if not os.path.exists(queries_file):
        raise FileNotFoundError(f"Queries file not found: {queries_file}")
    
    queries = {}
    try:
        with open(queries_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if 'query_id' not in data or 'text' not in data:
                        print(f"Warning: Line {line_num} missing required fields, skipping")
                        continue
                    queries[data['query_id']] = data['text']
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    except Exception as e:
        raise ValueError(f"Error reading queries file {queries_file}: {e}")
    
    if not queries:
        print(f"Warning: No queries found in {queries_file}. Please check the file format.")
    else:
        print(f"Successfully loaded {len(queries)} queries from {queries_file}.")
        print(f"First 5 query IDs: {list(queries.keys())[:5]}")
    
    return queries


def load_ground_truth(corpus_file: str, queries_file: str, qrels_file: str) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, set]]:
    """
    Load all ground truth data files (corpus, queries, relevance judgments).
    
    Args:
        corpus_file (str): Path to corpus JSONL file
        queries_file (str): Path to queries JSONL file  
        qrels_file (str): Path to qrels TSV file
        
    Returns:
        Tuple[Dict[str, str], Dict[str, str], Dict[str, set]]: 
            (queries, corpus, relevant_docs)
            
    Raises:
        FileNotFoundError: If any required file doesn't exist
    """
    print("Loading ground-truth files...")
    
    # Load queries and corpus using existing functions
    queries = load_queries(queries_file)
    corpus = load_corpus(corpus_file)
    
    # Load relevance judgments
    if not os.path.exists(qrels_file):
        raise FileNotFoundError(f"Qrels file not found: {qrels_file}")
    
    relevant_docs = {}
    try:
        with open(qrels_file, 'r', encoding='utf-8') as rf:
            for line_num, line in enumerate(rf, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) != 3:
                    print(f"Warning: Line {line_num} in qrels file has {len(parts)} parts, expected 3")
                    continue
                
                qid, doc_id, rel = parts
                try:
                    rel_int = int(rel)
                    if rel_int > 0:
                        relevant_docs.setdefault(qid, set()).add(doc_id)
                except ValueError:
                    print(f"Warning: Invalid relevance score on line {line_num}: {rel}")
                    continue
    except Exception as e:
        raise ValueError(f"Error reading qrels file {qrels_file}: {e}")
    
    total_relevance_mappings = sum(len(v) for v in relevant_docs.values())
    print(f"Loaded {len(queries)} queries, {len(corpus)} corpus chunks, and {total_relevance_mappings} relevance mappings.")
    
    return queries, corpus, relevant_docs