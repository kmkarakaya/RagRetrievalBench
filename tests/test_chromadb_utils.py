import pytest
import chromadb
from utils.chromadb_utils import create_chroma_collection, list_collections, get_random_chunks
import tempfile
import shutil
import os
import time

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

def test_create_chroma_collection(temp_chroma_dir):
    test_sentences = [["Hello world", "Test document"], ["Another test", "Final test"]]
    collection = create_chroma_collection(
        "test_collection",
        "all-MiniLM-L6-v2",
        test_sentences,
        from_scratch=True
    )
    assert collection is not None
    assert collection.count() == len([item for sublist in test_sentences for item in sublist])

def test_list_collections(chroma_client):
    # Create a few test collections
    collections_to_create = ["test1", "test2", "test3"]
    for name in collections_to_create:
        chroma_client.create_collection(name=name)
    
    collections = list_collections(chroma_client)
    assert len(collections) == len(collections_to_create)
    collection_names = [c.name for c in collections]
    assert all(name in collection_names for name in collections_to_create)

def test_get_random_chunks(chroma_client):
    # Create a test collection with known data
    collection = chroma_client.create_collection(name="test_random")
    test_docs = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    collection.add(
        documents=test_docs,
        ids=[str(i) for i in range(len(test_docs))]
    )
    
    # Test getting random chunks
    n_chunks = 3
    random_chunks = get_random_chunks(chroma_client, "test_random", n_chunks)
    assert len(random_chunks) == n_chunks
    assert all(chunk in test_docs for chunk in random_chunks)

def test_get_random_chunks_error_handling(chroma_client):
    # Test requesting more chunks than available
    collection = chroma_client.create_collection(name="test_error")
    collection.add(
        documents=["single doc"],
        ids=["0"]
    )
    
    with pytest.raises(ValueError):
        get_random_chunks(chroma_client, "test_error", n_chunks=2)