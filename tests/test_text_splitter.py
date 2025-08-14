import pytest
from utils.text_splitter import split_text

def test_split_text_basic():
    text = "This is a test document. " * 50  # Create text longer than chunk size
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= 100 for chunk in chunks)

def test_split_text_overlap():
    text = "This is a test document. " * 10
    chunks = split_text(text, chunk_size=50, chunk_overlap=25)
    # Check that consecutive chunks have overlapping content
    for i in range(len(chunks) - 1):
        assert any(phrase in chunks[i+1] for phrase in chunks[i].split() if len(phrase) > 3)

def test_split_text_empty():
    chunks = split_text("", chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 0

def test_split_text_small_input():
    text = "Small text"
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == text