import pytest
from utils.document_loader import load_corpus, load_queries, load_ground_truth, prepare_corpus_from_pdfs
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

def test_load_corpus_success():
    """Test successful corpus loading"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write test corpus data
        test_data = [
            {"doc_id": "doc1", "text": "First document content"},
            {"doc_id": "doc2", "text": "Second document content"},
            {"doc_id": "doc3", "text": "Third document content"}
        ]
        for item in test_data:
            f.write(json.dumps(item) + "\n")
        corpus_file = f.name
    
    try:
        corpus = load_corpus(corpus_file)
        assert len(corpus) == 3
        assert corpus["doc1"] == "First document content"
        assert corpus["doc2"] == "Second document content"
        assert corpus["doc3"] == "Third document content"
    finally:
        os.unlink(corpus_file)


def test_load_corpus_file_not_found():
    """Test corpus loading with non-existent file"""
    with pytest.raises(FileNotFoundError, match="Corpus file not found"):
        load_corpus("nonexistent_corpus.jsonl")


def test_load_queries_success():
    """Test successful queries loading"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write test query data
        test_queries = [
            {"query_id": "q1", "text": "What is machine learning?"},
            {"query_id": "q2", "text": "How does neural network work?"}
        ]
        for query in test_queries:
            f.write(json.dumps(query) + "\n")
        queries_file = f.name
    
    try:
        queries = load_queries(queries_file)
        assert len(queries) == 2
        assert queries["q1"] == "What is machine learning?"
        assert queries["q2"] == "How does neural network work?"
    finally:
        os.unlink(queries_file)


def test_load_queries_file_not_found():
    """Test queries loading with non-existent file"""
    with pytest.raises(FileNotFoundError, match="Queries file not found"):
        load_queries("nonexistent_queries.jsonl")


def test_prepare_corpus_from_pdfs():
    """Test corpus preparation from PDFs"""
    # Create mock chunks
    mock_chunk1 = MagicMock()
    mock_chunk1.doc_id = "doc1"
    mock_chunk1.page_content = "First chunk content"
    
    mock_chunk2 = MagicMock()
    mock_chunk2.doc_id = "doc2"  
    mock_chunk2.page_content = "Second chunk content"
    
    mock_chunks = [mock_chunk1, mock_chunk2]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_dir = os.path.join(temp_dir, "pdfs")
        os.makedirs(pdf_dir)
        corpus_file = os.path.join(temp_dir, "corpus.jsonl")
        
        # Mock the text_splitter function that gets imported inside prepare_corpus_from_pdfs
        with patch('utils.text_splitter.split_pdfs_to_chunks', return_value=mock_chunks):
            result = prepare_corpus_from_pdfs(pdf_dir, 1000, 100, corpus_file)
            
            # Check return value
            assert result["chunks_created"] == 2
            assert result["output_file"] == corpus_file
            assert result["source_dir"] == pdf_dir
            
            # Check file was created
            assert os.path.exists(corpus_file)
            
            # Check file content
            with open(corpus_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 2
                
                doc1 = json.loads(lines[0])
                assert doc1["doc_id"] == "doc1"
                assert doc1["text"] == "First chunk content"
                
                doc2 = json.loads(lines[1])
                assert doc2["doc_id"] == "doc2"
                assert doc2["text"] == "Second chunk content"


def test_load_ground_truth():
    """Test loading all ground truth files together"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        corpus_file = os.path.join(temp_dir, "corpus.jsonl")
        queries_file = os.path.join(temp_dir, "queries.jsonl")
        qrels_file = os.path.join(temp_dir, "qrels.tsv")
        
        # Write corpus
        with open(corpus_file, 'w') as f:
            f.write(json.dumps({"doc_id": "doc1", "text": "Document 1"}) + "\n")
            f.write(json.dumps({"doc_id": "doc2", "text": "Document 2"}) + "\n")
        
        # Write queries  
        with open(queries_file, 'w') as f:
            f.write(json.dumps({"query_id": "q1", "text": "Query 1"}) + "\n")
            f.write(json.dumps({"query_id": "q2", "text": "Query 2"}) + "\n")
        
        # Write qrels
        with open(qrels_file, 'w') as f:
            f.write("q1\tdoc1\t1\n")
            f.write("q1\tdoc2\t0\n")  # Will be ignored (relevance = 0)
            f.write("q2\tdoc2\t2\n")
        
        # Load ground truth
        queries, corpus, relevant_docs = load_ground_truth(corpus_file, queries_file, qrels_file)
        
        # Verify results
        assert len(queries) == 2
        assert len(corpus) == 2
        assert len(relevant_docs) == 2
        assert "doc1" in relevant_docs["q1"]
        assert "doc2" in relevant_docs["q2"]
        assert len(relevant_docs["q1"]) == 1  # Only relevance > 0