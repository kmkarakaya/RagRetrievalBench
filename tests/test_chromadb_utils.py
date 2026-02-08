import pytest
import chromadb
from utils.chromadb_utils import get_chromadb_client, initialize_collection, evaluate_with_chromadb
import tempfile
import shutil
import os
import time
from unittest.mock import patch, MagicMock

@pytest.fixture
def temp_chroma_dir():
    # Create a temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Wait a bit for ChromaDB to release files
    time.sleep(1)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        print(f"Warning: Could not remove temp directory {temp_dir}")

@pytest.fixture
def chroma_client(temp_chroma_dir):
    client = chromadb.PersistentClient(path=temp_chroma_dir)
    yield client
    # Close any open connections
    try:
        client.reset()
    except:
        pass

def test_get_chromadb_client():
    """Test that ChromaDB client is created successfully"""
    with patch('os.makedirs') as mock_makedirs:
        client = get_chromadb_client()
        assert client is not None
        # Verify that the directory creation was attempted
        mock_makedirs.assert_called_once_with(os.path.join("utils", "chromadb_collections"), exist_ok=True)

def test_initialize_collection():
    """Test collection initialization with mock data"""
    # Mock corpus data
    test_corpus = {
        "doc1": "This is the first test document",
        "doc2": "This is the second test document", 
        "doc3": "This is the third test document"
    }
    
    # Mock the ChromaDB client and collection
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("Collection does not exist")
    mock_client.create_collection.return_value = mock_collection
    
    # Mock the embedding function to avoid model loading
    mock_embedding_function = MagicMock()
    
    with patch('utils.chromadb_utils.get_chromadb_client', return_value=mock_client), \
         patch('utils.chromadb_utils.cfg') as mock_cfg, \
         patch('utils.chromadb_utils.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_embedding_function), \
         patch('time.time', side_effect=[0.0, 2.5]):  # Start time 0.0, end time 2.5
        
        # Configure mock settings
        mock_cfg.reinitialize_collections = True
        mock_cfg.document_batch_size = 100
        mock_cfg.show_progress_bar = False
        
        # Call the function
        result = initialize_collection(test_corpus, "test-model", "test-collection")
        
        # Verify the function behavior
        mock_client.create_collection.assert_called_once()
        mock_collection.add.assert_called_once()
        
        # Verify timing data is returned
        assert isinstance(result, dict)
        assert "embedding_time" in result
        assert "docs_processed" in result
        assert result["docs_processed"] == len(test_corpus)
        assert result["embedding_time"] == 2.5  # Should be end_time - start_time

def test_evaluate_with_chromadb():
    """Test the evaluation function with mock data"""
    # Mock test data
    queries = {"q1": "test query", "q2": "another query"}
    corpus = {"doc1": "document one", "doc2": "document two"}
    relevant_docs = {"q1": ["doc1"], "q2": ["doc2"]}
    
    # Mock ChromaDB query results
    mock_results = {
        'ids': [['doc1', 'doc2']],
        'distances': [[0.1, 0.9]]
    }
    
    # Mock collection and client
    mock_collection = MagicMock()
    mock_collection.query.return_value = mock_results
    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    
    # Mock evaluator
    mock_evaluator = MagicMock()
    mock_scores = {
        "map@k": {10: 0.85},
        "recall@k": {10: 0.75},
        "precision@k": {10: 0.80},
        "ndcg@k": {10: 0.82},
        "mrr@k": {10: 0.78},
        "accuracy@k": {10: 0.90}
    }
    mock_evaluator.compute_metrics.return_value = mock_scores
    mock_evaluator.queries_ids = list(queries.keys())
    
    with patch('utils.chromadb_utils.get_chromadb_client', return_value=mock_client), \
         patch('utils.chromadb_utils.cfg') as mock_cfg, \
         patch('sentence_transformers.evaluation.InformationRetrievalEvaluator', return_value=mock_evaluator), \
         patch('utils.chromadb_utils.time.perf_counter', side_effect=[0.0, 0.01, 0.02, 0.05]):
        
        # Configure mock settings
        mock_cfg.k = 10
        mock_cfg.compute_map = True
        mock_cfg.compute_recall = True
        mock_cfg.compute_precision = True
        mock_cfg.compute_ndcg = True
        mock_cfg.compute_mrr = True
        mock_cfg.compute_hit_rate = True
        mock_cfg.show_progress_bar = False
        
        # Call the function
        metrics, retrieval_timing = evaluate_with_chromadb(
            queries, corpus, relevant_docs, "test-model", "test-collection"
        )
        map_score, recall, precision, ndcg, mrr, hit_rate = metrics
        
        # Verify results
        assert map_score == 0.85
        assert recall == 0.75
        assert precision == 0.80
        assert ndcg == 0.82
        assert mrr == 0.78
        assert hit_rate == 0.90

        assert retrieval_timing["queries_timed"] == 2
        assert retrieval_timing["total_query_retrieval_time_s"] == pytest.approx(0.04)
        assert retrieval_timing["avg_query_latency_s"] == pytest.approx(0.02)
        assert retrieval_timing["avg_query_latency_ms"] == pytest.approx(20.0)
        
        # Verify ChromaDB interactions
        mock_client.get_collection.assert_called_once_with("test-collection")
        assert mock_collection.query.call_count == len(queries)

def test_initialize_collection_existing():
    """Test collection initialization when collection already exists"""
    test_corpus = {"doc1": "test document"}
    
    # Mock existing collection
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection  # Collection exists
    
    with patch('utils.chromadb_utils.get_chromadb_client', return_value=mock_client), \
         patch('utils.chromadb_utils.cfg') as mock_cfg:
        
        # Test when reinitialize_collections is False
        mock_cfg.reinitialize_collections = False
        
        result = initialize_collection(test_corpus, "test-model", "existing-collection")
        
        # Should return 0.0 when skipping initialization
        assert result == 0.0
        
        # Should not create a new collection
        mock_client.create_collection.assert_not_called()


def test_evaluate_with_chromadb_hit_rate_only_and_missing_accuracy():
    """Hit-rate metric should default to 0.0 when accuracy@k is missing."""
    queries = {"q1": "test query"}
    corpus = {"doc1": "document one"}
    relevant_docs = {"q1": ["doc1"]}

    mock_results = {
        'ids': [['doc1']],
        'distances': [[0.1]]
    }

    mock_collection = MagicMock()
    mock_collection.query.return_value = mock_results
    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection

    mock_evaluator = MagicMock()
    mock_evaluator.compute_metrics.return_value = {
        # intentionally missing accuracy@k
        "map@k": {10: 0.5}
    }
    mock_evaluator.queries_ids = list(queries.keys())

    with patch('utils.chromadb_utils.get_chromadb_client', return_value=mock_client), \
         patch('utils.chromadb_utils.cfg') as mock_cfg, \
         patch('sentence_transformers.evaluation.InformationRetrievalEvaluator', return_value=mock_evaluator), \
         patch('utils.chromadb_utils.time.perf_counter', side_effect=[0.0, 0.01]):

        mock_cfg.k = 10
        mock_cfg.compute_map = False
        mock_cfg.compute_recall = False
        mock_cfg.compute_precision = False
        mock_cfg.compute_ndcg = False
        mock_cfg.compute_mrr = False
        mock_cfg.compute_hit_rate = True
        mock_cfg.show_progress_bar = False
        mock_cfg.mrr_at_k = [10]
        mock_cfg.ndcg_at_k = [10]
        mock_cfg.precision_recall_at_k = [10]
        mock_cfg.map_at_k = [10]
        mock_cfg.document_batch_size = 8

        metrics, _ = evaluate_with_chromadb(
            queries, corpus, relevant_docs, "test-model", "test-collection"
        )

        assert metrics == (0.0,)
